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
MANIFEST_OUT = Path('data/production/pre_ai/chatgpt_payload.json')
TASTE_QUEUE_OUT = Path('data/production/pre_ai/chatgpt_taste_queue.jsonl')
PURCHASE_CONTEXT_OUT = Path('data/production/pre_ai/chatgpt_purchase_context.jsonl')

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


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='\n') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')))
            f.write('\n')


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

    ai_queue = []
    ai_context = []
    ready_context = []
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
        strong_scenario = compact_scenario(deal_row['decision_if_strong'])
        moderate_scenario = compact_scenario(deal_row['decision_if_moderate'])

        strong_ok = strong_scenario['disposition'] == 'INCLUDE'
        moderate_ok = moderate_scenario['disposition'] == 'INCLUDE'
        if not strong_ok and not moderate_ok:
            excluded_keys.append(primary_key)
            exclusion_counts['deal_excludes_even_if_strong'] += 1
            continue

        semantic_condition = {
            'ai_condition': family['ai_condition'],
            'requires_ai_base_support': bool(family.get('requires_ai_base_support')),
            'base_appids': family.get('base_appids') or [],
        }
        context = {
            'family_id': family['family_id'],
            'family_type': family['family_type'],
            'taste_subject_key': taste_key,
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
            'deal_if_strong': strong_scenario,
            'deal_if_moderate': moderate_scenario,
            'context_only': {
                'wishlist': str(taste_row['appid']) in wishlist['appids'],
                'reviews': {
                    'global_positive_percent': feed_row['global_review_positive'],
                    'global_count': feed_row['global_review_count'],
                    'russian_positive_percent': feed_row['russian_review_positive'],
                    'russian_count': feed_row['russian_review_count'],
                },
                'discovery_reasons': feed_row['reasons'],
            },
            'semantic_condition': semantic_condition,
        }

        cache_hit = taste_row['status'] == 'cache_hit'
        cached_taste = taste_row.get('cached_taste') if cache_hit else None
        if cache_hit:
            if cached_taste['verdict'] != 'INCLUDE':
                excluded_keys.append(primary_key)
                exclusion_counts['valid_cached_taste_below_moderate'] += 1
                continue
            fit = cached_taste['fit_level']
            selected = strong_scenario if fit == 'strong' else moderate_scenario
            if selected['disposition'] != 'INCLUDE':
                excluded_keys.append(primary_key)
                exclusion_counts['deal_excludes_for_valid_cached_fit'] += 1
                continue
            if family.get('requires_ai_base_support'):
                work = ['resolve_base_support_condition']
                ai_queue.append({
                    'family_id': family['family_id'],
                    'taste_subject_key': taste_key,
                    'appid': taste_row['appid'],
                    'title': taste_row['taste_subject_title'],
                    'taste_fingerprint': taste_row['taste_fingerprint'],
                    'candidate_context_sha256': taste_row['candidate_context_sha256'],
                    'short_description': taste_row.get('short_description'),
                    'bundle_members': taste_row.get('bundle_members') or [],
                    'resolved_taste_fit': fit,
                    'work_required': work,
                    'semantic_condition': semantic_condition,
                })
                ai_context.append(context)
            else:
                context['resolved_taste_fit'] = fit
                context['final_purchase_decision'] = selected['purchase_decision']
                ready_context.append(context)
            continue

        work = ['evaluate_taste_fit']
        if family.get('requires_ai_base_support'):
            work.append('resolve_base_support_condition')
        # Strictly price-blind AI input. Do not add prices, discount, reviews,
        # wishlist, popularity, or any deal/history signal here.
        ai_queue.append({
            'family_id': family['family_id'],
            'taste_subject_key': taste_key,
            'appid': taste_row['appid'],
            'title': taste_row['taste_subject_title'],
            'taste_fingerprint': taste_row['taste_fingerprint'],
            'candidate_context_sha256': taste_row['candidate_context_sha256'],
            'short_description': taste_row.get('short_description'),
            'bundle_members': taste_row.get('bundle_members') or [],
            'fit_tags': taste_row['fit_tags'],
            'core_fit_count': taste_row['core_fit_count'],
            'release_date': taste_row['release_date'],
            'ai_required_reason': taste_row.get('ai_required_reason'),
            'work_required': work,
            'semantic_condition': semantic_condition,
        })
        ai_context.append(context)

    sale_end_coverage = round((len(families) - len(sale_end_missing)) / len(families), 4) if families else 1.0
    if len(ai_queue) != len(ai_context):
        raise SystemExit('AI queue/context alignment mismatch')
    for i, (work, context) in enumerate(zip(ai_queue, ai_context), start=1):
        if work['family_id'] != context['family_id'] or work['taste_subject_key'] != context['taste_subject_key']:
            raise SystemExit(f'AI queue/context row alignment mismatch at line {i}')

    partition_count = len(ai_queue) + len(ready_context) + len(excluded_keys)
    if partition_count != len(families):
        raise SystemExit('Consumer payload family partition mismatch')
    if len(set(excluded_keys)) != len(excluded_keys):
        raise SystemExit('Duplicate deterministic exclusion key')

    write_jsonl(TASTE_QUEUE_OUT, ai_queue)
    # First N lines are intentionally one-to-one with taste queue lines.
    # Fully ready cached rows follow after them.
    purchase_context = ai_context + ready_context
    write_jsonl(PURCHASE_CONTEXT_OUT, purchase_context)

    source_bytes = sum(path.stat().st_size for path in PREREQUISITES)
    manifest = {
        'schema_version': 3,
        'purpose': 'chatgpt_consumer_bundle_with_context_bound_strict_price_blind_taste_phase',
        'status': 'complete',
        'source_mailing_updated_at_utc': source_stamp,
        'profile_binding': {
            'canonical_profile_blob_sha': taste_doc['current_profile']['blob_sha'],
            'taste_model_version': taste_doc['current_binding']['taste_model_version'],
            'candidate_context_contract_blob_sha': taste_doc['current_binding']['candidate_context_contract_blob_sha'],
            'content_metadata_blob_sha': taste_doc['current_binding']['content_metadata_blob_sha'],
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
            'taste_phase_is_strictly_price_blind': True,
            'candidate_context_digest_required_for_persisted_taste_verdict': True,
            'steam_short_description_is_price_blind_candidate_evidence_not_profile_evidence': True,
            'taste_queue_forbids': ['price', 'discount', 'history', 'reviews', 'wishlist', 'popularity', 'deal_quality'],
            'chatgpt_must_fix_taste_verdict_before_reading_matching_purchase_context': True,
            'chatgpt_must_not_recalculate_prices_history_or_deal_gates': True,
            'chatgpt_selects_precomputed_deal_scenario_from_final_taste_fit': True,
            'every_visible_paid_recommendation_requires_sale_end': False,
            'missing_sale_end_does_not_exclude_candidate': True,
            'known_sale_end_at_or_before_consumer_time_is_inactive': True,
            'current_offer_state_must_not_be_reused_past_known_sale_end': True,
            'wishlist_is_context_only': True,
            'reviews_and_discovery_flags_are_not_positive_taste_proof': True,
        },
        'files': {
            'taste_queue_jsonl': str(TASTE_QUEUE_OUT),
            'purchase_context_jsonl': str(PURCHASE_CONTEXT_OUT),
            'line_alignment': 'taste_queue line N == purchase_context line N for 1..ai_queue_count',
            'ready_context_start_line': len(ai_queue) + 1 if ready_context else None,
        },
        'source_family_count': len(families),
        'candidate_description_known_count': taste_doc['candidate_context']['description_known_count'],
        'candidate_description_missing_count': taste_doc['candidate_context']['description_missing_count'],
        'candidate_description_coverage': taste_doc['candidate_context']['description_coverage'],
        'ai_queue_count': len(ai_queue),
        'ready_without_ai_count': len(ready_context),
        'purchase_context_line_count': len(purchase_context),
        'deterministically_excluded_without_ai_count': len(excluded_keys),
        'deterministic_exclusion_counts': dict(sorted(exclusion_counts.items())),
        'complete_family_partition': partition_count == len(families),
        'sale_end_coverage': sale_end_coverage,
        'sale_end_missing_count': len(sale_end_missing),
        'sale_end_missing_primary_keys': sale_end_missing,
        'source_pre_ai_artifact_bytes': source_bytes,
        'deterministically_excluded_primary_keys': excluded_keys,
        'elapsed_seconds': round(time.monotonic() - started, 3),
    }
    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    taste_bytes = TASTE_QUEUE_OUT.stat().st_size
    context_bytes = PURCHASE_CONTEXT_OUT.stat().st_size
    manifest_bytes = MANIFEST_OUT.stat().st_size
    consumer_bytes = taste_bytes + context_bytes + manifest_bytes
    print(json.dumps({
        'status': manifest['status'],
        'source_family_count': manifest['source_family_count'],
        'ai_queue_count': manifest['ai_queue_count'],
        'ready_without_ai_count': manifest['ready_without_ai_count'],
        'deterministically_excluded_without_ai_count': manifest['deterministically_excluded_without_ai_count'],
        'deterministic_exclusion_counts': manifest['deterministic_exclusion_counts'],
        'complete_family_partition': manifest['complete_family_partition'],
        'sale_end_coverage': manifest['sale_end_coverage'],
        'sale_end_missing_count': manifest['sale_end_missing_count'],
        'wishlist_entry_count': wishlist['entry_count'],
        'source_pre_ai_artifact_bytes': source_bytes,
        'manifest_bytes': manifest_bytes,
        'taste_queue_bytes': taste_bytes,
        'purchase_context_bytes': context_bytes,
        'consumer_bundle_bytes': consumer_bytes,
        'taste_queue_ratio_vs_previous_monolithic_payload': round(taste_bytes / 895322, 4),
        'consumer_bundle_ratio_vs_joined_sources': round(consumer_bytes / source_bytes, 4) if source_bytes else None,
        'external_calls': 1,
        'elapsed_seconds': manifest['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
