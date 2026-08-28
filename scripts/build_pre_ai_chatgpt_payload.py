import hashlib
import json
import math
import time
import urllib.request
from collections import Counter
from pathlib import Path

MAILING = Path('data/production/mailing/index.json')
STORE = Path('data/production/pre_ai/store_snapshot.json')
FX = Path('data/production/pre_ai/fx_snapshot.json')
FAMILIES = Path('data/production/pre_ai/family_graph.json')
TASTE = Path('data/production/pre_ai/taste_projection.json')
HISTORY = Path('data/production/pre_ai/history_snapshot.json')
DEALS = Path('data/production/pre_ai/deal_scenarios.json')
OUT = Path('data/production/pre_ai/chatgpt_payload.json')

PREREQUISITES = [STORE, FX, FAMILIES, TASTE, HISTORY, DEALS]
WISHLIST_URL = 'https://raw.githubusercontent.com/kentrap2011-hub/stopgame-ratings-data/main/steam_wishlist.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def git_blob_sha_bytes(raw):
    return hashlib.sha1(f'blob {len(raw)}\0'.encode('ascii') + raw).hexdigest()


def nullable_float(value):
    if value in (None, ''):
        return None
    return float(value)


def nullable_int(value):
    if value in (None, ''):
        return None
    return int(float(value))


def load_feed(index):
    cols = index['columns']
    ci = {name: i for i, name in enumerate(cols)}
    feed = {}
    for n in range(1, int(index['chunk_count']) + 1):
        path = Path(index['chunk_pattern'].replace('NNN', f'{n:03d}'))
        for line in path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            cells = line.split('\t')
            if len(cells) != len(cols):
                raise SystemExit(f'Column mismatch in {path}')
            key = cells[ci['key']]
            feed[key] = {
                'appid': cells[ci['appid']],
                'title': cells[ci['title']],
                'global_review_positive': nullable_float(cells[ci['global_review_positive']]),
                'global_review_count': nullable_int(cells[ci['global_review_count']]),
                'russian_review_positive': nullable_float(cells[ci['russian_review_positive']]),
                'russian_review_count': nullable_int(cells[ci['russian_review_count']]),
                'reasons': [] if cells[ci['reasons']] == '' else cells[ci['reasons']].split('|'),
            }
    if len(feed) != int(index['item_count']):
        raise SystemExit('Mailing item_count mismatch')
    return feed


def load_wishlist():
    req = urllib.request.Request(WISHLIST_URL, headers={'User-Agent': 'steam-kz-deals/1.0'})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
    doc = json.loads(raw.decode('utf-8'))
    games = doc.get('games') or []
    appids = {str(game['appid']) for game in games if game.get('appid') is not None}
    if int(doc.get('count') or -1) != len(games):
        raise SystemExit('Wishlist count metadata mismatch')
    return {
        'blob_sha': git_blob_sha_bytes(raw),
        'entry_count': len(games),
        'appids': appids,
    }


def compact_scenario(scenario):
    out = {
        'disposition': scenario['final_disposition'],
        'price_gate_reason': scenario['price_gate_reason'],
        'active_price_ceiling_rub': scenario['active_price_ceiling_rub'],
    }
    if scenario['final_disposition'] == 'INCLUDE':
        out['purchase_decision'] = scenario['purchase_decision']
    else:
        out['exclusion_reason_code'] = scenario['exclusion_reason_code']
    return out


def main():
    started = time.monotonic()
    mailing = load(MAILING)
    store_doc = load(STORE)
    fx_doc = load(FX)
    family_doc = load(FAMILIES)
    taste_doc = load(TASTE)
    history_doc = load(HISTORY)
    deals_doc = load(DEALS)

    docs = [store_doc, fx_doc, family_doc, taste_doc, history_doc, deals_doc]
    if any(doc.get('status') != 'complete' for doc in docs):
        raise SystemExit('A pre-AI prerequisite is incomplete')
    if not all([
        fx_doc.get('complete_coverage'),
        family_doc.get('complete_coverage_of_nonexcluded_candidates'),
        taste_doc.get('complete_coverage'),
        history_doc.get('complete_coverage'),
        deals_doc.get('complete_coverage'),
    ]):
        raise SystemExit('A pre-AI prerequisite lacks complete coverage')

    source_stamp = mailing.get('source_updated_at_utc')
    if family_doc.get('source_updated_at_utc') != source_stamp:
        raise SystemExit('Family graph stale versus mailing feed')
    if taste_doc.get('source_mailing_updated_at_utc') != source_stamp:
        raise SystemExit('Taste projection stale versus mailing feed')

    feed = load_feed(mailing)
    wishlist = load_wishlist()
    store = store_doc['entries']
    fx = fx_doc['entries']
    taste = taste_doc['entries']
    history = history_doc['entries']
    deals = deals_doc['entries']
    families = family_doc['families']
    rate = float(fx_doc['fx']['kzt_per_rub'])
    if not math.isfinite(rate) or rate <= 0:
        raise SystemExit('Invalid FX rate in pre-AI snapshot')

    if len(families) != int(family_doc['family_count']):
        raise SystemExit('Family count mismatch')

    queue = []
    ready = []
    excluded_keys = []
    exclusion_counts = Counter()
    sale_end_missing = []

    for family in families:
        primary_key = family['primary_key']
        taste_key = family['taste_subject_key']
        if primary_key not in store or primary_key not in fx or primary_key not in history or primary_key not in deals:
            raise SystemExit(f'Missing primary prerequisite for {primary_key}')
        if taste_key not in taste or taste_key not in feed:
            raise SystemExit(f'Missing taste prerequisite for {taste_key}')

        store_row = store[primary_key]
        fx_row = fx[primary_key]
        taste_row = taste[taste_key]
        history_row = history[primary_key]
        deal_row = deals[primary_key]
        feed_row = feed[taste_key]

        sale_end_utc = store_row.get('discount_end_utc')
        sale_end_local = store_row.get('discount_end_europe_berlin')
        if not sale_end_utc or not sale_end_local:
            sale_end_missing.append(primary_key)

        hist_min_kzt = history_row.get('historical_min_kzt')
        hist_min_rub = None if hist_min_kzt is None else float(hist_min_kzt) / rate
        delta = history_row.get('delta_vs_paid_historical_minimum')
        history_compact = {
            'quality': history_row['history_quality'],
            'minimum_rub_display': None if hist_min_rub is None else int(round(hist_min_rub)),
            'delta_vs_paid_minimum_percent': None if delta is None else round(float(delta) * 100.0, 1),
            'previously_free': history_row['history_quality'] == 'previously_free',
        }

        candidate = {
            'family_id': family['family_id'],
            'family_type': family['family_type'],
            'taste_subject': {
                'key': taste_key,
                'appid': taste_row['appid'],
                'title': taste_row['taste_subject_title'],
                'taste_fingerprint': taste_row['taste_fingerprint'],
                'fit_tags': taste_row['fit_tags'],
                'core_fit_count': taste_row['core_fit_count'],
                'release_date': taste_row['release_date'],
                'cache_status': taste_row['status'],
                'ai_required_reason': taste_row.get('ai_required_reason'),
                'wishlist': str(taste_row['appid']) in wishlist['appids'],
                'reviews': {
                    'global_positive_percent': feed_row['global_review_positive'],
                    'global_count': feed_row['global_review_count'],
                    'russian_positive_percent': feed_row['russian_review_positive'],
                    'russian_count': feed_row['russian_review_count'],
                },
                'recall_context_only': feed_row['reasons'],
            },
            'purchase': {
                'key': primary_key,
                'title': family['primary_title'],
                'discount_percent': store_row['discount_percent'],
                'current_price_rub_display': int(fx_row['final_rub_display']),
                'current_price_rub_unrounded': fx_row['final_rub_unrounded'],
                'original_price_rub_display': int(fx_row['original_rub_display']),
                'sale_end_utc': sale_end_utc,
                'sale_end_europe_berlin': sale_end_local,
                'store_changed_since_discovery': bool(store_row.get('changed_since_discovery')),
                'selection_reason': family['primary_selection_reason'],
            },
            'history': history_compact,
            'deal_if_strong': compact_scenario(deal_row['decision_if_strong']),
            'deal_if_moderate': compact_scenario(deal_row['decision_if_moderate']),
            'semantic_condition': {
                'ai_condition': family['ai_condition'],
                'requires_ai_base_support': bool(family.get('requires_ai_base_support')),
                'base_appids': family.get('base_appids') or [],
            },
        }

        strong_ok = candidate['deal_if_strong']['disposition'] == 'INCLUDE'
        moderate_ok = candidate['deal_if_moderate']['disposition'] == 'INCLUDE'
        cache_hit = taste_row['status'] == 'cache_hit'
        cached_taste = taste_row.get('cached_taste') if cache_hit else None

        if not strong_ok and not moderate_ok:
            excluded_keys.append(primary_key)
            exclusion_counts['deal_excludes_even_if_strong'] += 1
            continue

        if cache_hit:
            candidate['taste_subject']['cached_taste'] = cached_taste
            if cached_taste['verdict'] != 'INCLUDE':
                excluded_keys.append(primary_key)
                exclusion_counts['valid_cached_taste_below_moderate'] += 1
                continue
            fit = cached_taste['fit_level']
            selected = candidate['deal_if_strong'] if fit == 'strong' else candidate['deal_if_moderate']
            if selected['disposition'] != 'INCLUDE':
                excluded_keys.append(primary_key)
                exclusion_counts['deal_excludes_for_valid_cached_fit'] += 1
                continue
            if family.get('requires_ai_base_support'):
                candidate['work_required'] = ['resolve_base_support_condition']
                queue.append(candidate)
            else:
                candidate['resolved_taste_fit'] = fit
                candidate['final_purchase_decision'] = selected['purchase_decision']
                ready.append(candidate)
            continue

        work = ['evaluate_taste_fit']
        if family.get('requires_ai_base_support'):
            work.append('resolve_base_support_condition')
        candidate['work_required'] = work
        queue.append(candidate)

    if sale_end_missing:
        raise SystemExit(f'Mandatory sale-end missing for paid family primaries: {sale_end_missing[:10]}')

    partition_count = len(queue) + len(ready) + len(excluded_keys)
    if partition_count != len(families):
        raise SystemExit('Compact payload family partition mismatch')
    if len(set(excluded_keys)) != len(excluded_keys):
        raise SystemExit('Duplicate deterministic exclusion key')

    source_bytes = sum(path.stat().st_size for path in PREREQUISITES)
    out = {
        'schema_version': 1,
        'purpose': 'single_compact_pre_ai_payload_for_chatgpt_taste_and_semantic_only_work',
        'status': 'complete',
        'source_mailing_updated_at_utc': source_stamp,
        'profile_binding': {
            'canonical_profile_blob_sha': taste_doc['current_profile']['blob_sha'],
            'taste_model_version': taste_doc['cache_binding']['current_taste_model_version'],
        },
        'wishlist_binding': {
            'blob_sha': wishlist['blob_sha'],
            'entry_count': wishlist['entry_count'],
            'is_context_only_not_taste_proof': True,
        },
        'fx_binding': {
            'kzt_per_rub': rate,
            'provider_updated_at_utc': fx_doc['fx']['provider_updated_at_utc'],
        },
        'contract': {
            'minimum_taste_fit': 'moderate',
            'chatgpt_must_not_recalculate_prices_history_or_deal_gates': True,
            'chatgpt_selects_precomputed_deal_scenario_from_final_taste_fit': True,
            'every_visible_paid_recommendation_requires_sale_end': True,
            'wishlist_is_context_only': True,
            'reviews_and_recall_flags_are_not_positive_taste_proof': True,
        },
        'source_family_count': len(families),
        'ai_queue_count': len(queue),
        'ready_without_ai_count': len(ready),
        'deterministically_excluded_without_ai_count': len(excluded_keys),
        'deterministic_exclusion_counts': dict(sorted(exclusion_counts.items())),
        'complete_family_partition': partition_count == len(families),
        'mandatory_sale_end_coverage': 1.0,
        'source_pre_ai_artifact_bytes': source_bytes,
        'ai_queue': queue,
        'ready_without_ai': ready,
        'deterministically_excluded_primary_keys': excluded_keys,
        'elapsed_seconds': round(time.monotonic() - started, 3),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(out, ensure_ascii=False, separators=(',', ':')).encode('utf-8') + b'\n'
    OUT.write_bytes(raw)

    print(json.dumps({
        'status': out['status'],
        'source_family_count': out['source_family_count'],
        'ai_queue_count': out['ai_queue_count'],
        'ready_without_ai_count': out['ready_without_ai_count'],
        'deterministically_excluded_without_ai_count': out['deterministically_excluded_without_ai_count'],
        'deterministic_exclusion_counts': out['deterministic_exclusion_counts'],
        'complete_family_partition': out['complete_family_partition'],
        'mandatory_sale_end_coverage': out['mandatory_sale_end_coverage'],
        'wishlist_entry_count': wishlist['entry_count'],
        'source_pre_ai_artifact_bytes': source_bytes,
        'compact_payload_bytes': len(raw),
        'size_ratio_vs_joined_sources': round(len(raw) / source_bytes, 4) if source_bytes else None,
        'external_calls': 1,
        'elapsed_seconds': out['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
