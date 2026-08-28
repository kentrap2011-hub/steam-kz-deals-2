import json
import math
import subprocess
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

POLICY = Path('config/mailing_policy.json')
CONTRACT = Path('config/deal_quality_contract.json')
TASTE_INDEX = Path('data/cache/taste_fit.index.json')
TASTE_LEDGER = Path('data/cache/taste_fit.ledger_validation.json')
CHECKPOINT = Path('data/cache/taste_fit.checkpoint_validation.json')
FAMILIES = Path('data/cache/offer_family.validation.json')
STORE = Path('data/cache/store_state.validation.json')
STEAMDB = Path('data/cache/steamdb_cache.validation.json')
OUT = Path('data/cache/deal_quality.validation.json')


def sha(path):
    return subprocess.check_output(['git', 'rev-parse', f'HEAD:{path}'], text=True).strip()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


policy = load(POLICY)
contract = load(CONTRACT)
taste = load(TASTE_INDEX)
ledger = load(TASTE_LEDGER)
checkpoint = load(CHECKPOINT)
families = load(FAMILIES)
store = load(STORE)
steamdb = load(STEAMDB)

if policy.get('status') != 'canonical':
    raise SystemExit('Policy not canonical')
if float(policy['pricing']['target_rub']) != float(contract['authority']['requires_canonical_target_rub']):
    raise SystemExit('Deal contract base target disagrees with canonical policy')
if contract.get('contract') != 'DEAL-QUALITY-AND-SORT-V1':
    raise SystemExit('Unexpected deal contract')
if ledger.get('status') != 'complete' or not ledger.get('complete_ledger'):
    raise SystemExit('Taste ledger incomplete')
if checkpoint.get('status') != 'complete' or not checkpoint.get('checkpoint_complete'):
    raise SystemExit('Taste checkpoint incomplete')
if families.get('status') != 'complete' or not families.get('complete_coverage'):
    raise SystemExit('Offer families incomplete')
if store.get('status') != 'complete' or int(store.get('missing_count') or 0) != 0:
    raise SystemExit('Store state incomplete')
if steamdb.get('status') != 'complete' or not steamdb.get('complete_coverage'):
    raise SystemExit('SteamDB classification incomplete')
if int(steamdb.get('true_lookup_miss_count') or 0) != 0:
    raise SystemExit('Stage 18 cannot run while SteamDB true misses remain')
if int(steamdb.get('invalid_cache_entry_count') or 0) != 0:
    raise SystemExit('SteamDB classification has invalid entries')

policy_sha = sha('config/mailing_policy.json')
taste_index_sha = sha('data/cache/taste_fit.index.json')
ledger_sha = sha('data/cache/taste_fit.ledger_validation.json')
family_sha = sha('data/cache/offer_family.validation.json')
store_sha = sha('data/cache/store_state.validation.json')
steamdb_sha = sha('data/cache/steamdb_cache.validation.json')

if ledger['bindings'].get('policy_blob_sha') != policy_sha:
    raise SystemExit('Taste ledger stale versus policy')
if ledger['bindings'].get('taste_index_blob_sha') != taste_index_sha:
    raise SystemExit('Taste ledger stale versus taste index')
if checkpoint['bindings'].get('policy_blob_sha') != policy_sha:
    raise SystemExit('Taste checkpoint stale versus policy')
if checkpoint['bindings'].get('ledger_validation_blob_sha') != ledger_sha:
    raise SystemExit('Taste checkpoint stale versus taste ledger')
if families['bindings'].get('policy_blob_sha') != policy_sha:
    raise SystemExit('Offer families stale versus policy')
if store['bindings'].get('policy_blob_sha') != policy_sha:
    raise SystemExit('Store validation stale versus policy')
if store['bindings'].get('offer_family_blob_sha') != family_sha:
    raise SystemExit('Store validation stale versus families')
if steamdb['bindings'].get('policy_blob_sha') != policy_sha:
    raise SystemExit('SteamDB classification stale versus policy')
if steamdb['bindings'].get('store_state_validation_blob_sha') != store_sha:
    raise SystemExit('SteamDB classification stale versus store')
if steamdb['bindings'].get('offer_family_blob_sha') != family_sha:
    raise SystemExit('SteamDB classification stale versus families')

# One FX lookup for the whole stage. Never silently use a guessed rate.
fx_url = contract['fx']['source_url']
req = urllib.request.Request(fx_url, headers={'User-Agent': 'steam-kz-deals/1.0', 'Accept': 'application/json'})
with urllib.request.urlopen(req, timeout=15) as resp:
    fx = json.loads(resp.read().decode('utf-8'))
if fx.get('result') != 'success' or fx.get('base_code') != 'RUB':
    raise SystemExit('FX provider returned invalid result')
rate = float((fx.get('rates') or {}).get('KZT') or 0)
if not math.isfinite(rate) or rate <= 0:
    raise SystemExit('Invalid RUB/KZT rate')
fx_time = datetime.fromtimestamp(int(fx['time_last_update_unix']), tz=timezone.utc)
age_hours = (datetime.now(timezone.utc) - fx_time).total_seconds() / 3600
if age_hours < -1 or age_hours > float(contract['fx']['max_rate_age_hours']):
    raise SystemExit(f'FX rate stale: {age_hours:.2f}h')

# The compact taste index intentionally stores entries as positional arrays.
taste_entries = taste.get('entries') or {}
taste_fields = taste.get('entry_fields') or []
if int(taste.get('index_entry_count') or -1) != len(taste_entries):
    raise SystemExit('Taste compact index entry count mismatch')
if taste_fields != ['appid', 'taste_fingerprint', 'verdict', 'fit_level', 'reason_code']:
    raise SystemExit(f'Unexpected compact taste entry shape: {taste_fields!r}')


def taste_entry(key):
    raw = taste_entries.get(key)
    if raw is None:
        return None
    if not isinstance(raw, list) or len(raw) != len(taste_fields):
        raise SystemExit(f'Malformed compact taste entry for {key}')
    return dict(zip(taste_fields, raw))


fit_rank = {'strong': 0, 'moderate': 1}
store_by_key = {x['primary_key']: x for x in store['current_state']}
if len(store_by_key) != int(store.get('primary_count') or -1):
    raise SystemExit('Store primary count mismatch')

history = {}
for x in steamdb.get('confirmed_min_hits') or []:
    history[x['key']] = {'status': 'confirmed_min', 'historical_min_kzt': float(x['historical_min_kzt'])}
for x in steamdb.get('previously_free_hits') or []:
    history[x['key']] = {'status': 'previously_free', 'historical_min_kzt': 0.0}
for x in steamdb.get('negative_cache_hits') or []:
    history[x['key']] = {'status': 'unavailable_exact_history', 'historical_min_kzt': None}
if len(history) != int(steamdb.get('primary_count') or -1):
    raise SystemExit('SteamDB primary coverage map mismatch')


def family_fit(fam):
    keys = []
    for key in [fam.get('primary_key'), *(fam.get('all_member_keys') or [])]:
        if key and key not in keys:
            keys.append(key)
    levels = []
    for key in keys:
        entry = taste_entry(key)
        if entry and entry.get('verdict') == 'INCLUDE' and entry.get('fit_level') in fit_rank:
            levels.append(entry['fit_level'])
    if not levels:
        raise SystemExit(f'No final included taste fit for family {fam.get("family_id")}')
    return min(levels, key=lambda x: fit_rank[x])


def history_quality(current_kzt, hist_entry):
    status = hist_entry['status']
    if status == 'previously_free':
        return 'previously_free', None
    if status == 'unavailable_exact_history':
        return 'unverified', None
    hist = float(hist_entry['historical_min_kzt'])
    if hist <= 0:
        raise SystemExit('Nonpositive paid historical minimum')
    delta = current_kzt / hist - 1.0
    if current_kzt <= hist:
        return 'record', delta
    if delta <= 0.10 + 1e-12:
        return 'near_record', delta
    if delta <= 0.25 + 1e-12:
        return 'good_vs_history', delta
    return 'well_above_history', delta


def price_gate(fit, price_rub, quality):
    if price_rub <= 500 + 1e-12:
        return True, 500, 'base_target'
    if fit == 'strong':
        if price_rub > 750 + 1e-12:
            return False, 750, 'strong_absolute_ceiling'
        if price_rub <= 650 + 1e-12:
            ok = quality in {'record', 'near_record', 'good_vs_history'}
            return ok, 650, 'strong_standard_overage_requires_good_history'
        ok = quality in {'record', 'near_record'}
        return ok, 750, 'strong_high_overage_requires_record_or_near_record'
    if fit == 'moderate':
        if price_rub > 550 + 1e-12:
            return False, 550, 'moderate_absolute_ceiling'
        ok = quality in {'record', 'near_record'}
        return ok, 550, 'moderate_overage_requires_record_or_near_record'
    return False, 500, 'unsupported_or_below_moderate_fit'


decision_by_quality = {
    'record': 'БРАТЬ СЕЙЧАС',
    'near_record': 'БРАТЬ СЕЙЧАС',
    'good_vs_history': 'МОЖНО БРАТЬ',
    'previously_free': 'МОЖНО БРАТЬ',
    'unverified': 'МОЖНО БРАТЬ',
    'well_above_history': 'ЛУЧШЕ ЖДАТЬ',
}
decision_rank = {x: i for i, x in enumerate(contract['sorting']['purchase_decision_order'])}
quality_rank = {x: i for i, x in enumerate(contract['sorting']['price_quality_order'])}

rows = []
excluded = []
seen_primary = set()
for fam in families['families']:
    primary = fam['primary_key']
    if primary in seen_primary:
        raise SystemExit(f'Duplicate primary family key: {primary}')
    seen_primary.add(primary)
    state = store_by_key.get(primary)
    hist_entry = history.get(primary)
    if state is None or hist_entry is None:
        raise SystemExit(f'Missing stage prerequisite row for {primary}')
    fit = family_fit(fam)
    current_kzt = float(state['final_kzt'])
    current_rub = current_kzt / rate
    quality, delta = history_quality(current_kzt, hist_entry)
    allowed, ceiling_rub, gate_reason = price_gate(fit, current_rub, quality)
    common = {
        'family_id': fam['family_id'],
        'primary_key': primary,
        'title': state['title'],
        'fit_level': fit,
        'discount_percent': state.get('discount_percent'),
        'current_kzt': current_kzt,
        'current_price_rub_unrounded': current_rub,
        'current_price_rub_display': int(round(current_rub)),
        'history_quality': quality,
        'historical_min_kzt': hist_entry['historical_min_kzt'],
        'delta_vs_paid_historical_minimum': delta,
        'active_price_ceiling_rub': ceiling_rub,
        'price_gate_reason': gate_reason,
    }
    if not allowed:
        common.update({
            'final_disposition': 'EXCLUDE',
            'exclusion_reason_code': 'price_clearly_unreasonable_after_soft_target_evaluation',
        })
        excluded.append(common)
        continue
    decision = decision_by_quality[quality]
    common.update({
        'final_disposition': 'INCLUDE',
        'purchase_decision': decision,
        'best_variant_value_score': 0,
    })
    rows.append(common)

if len(seen_primary) != int(families.get('primary_count') or -1):
    raise SystemExit('Family primary coverage mismatch')
if len(rows) + len(excluded) != len(seen_primary):
    raise SystemExit('Deal disposition coverage mismatch')


def sort_key(row):
    discount = int(row['discount_percent']) if row['discount_percent'] is not None else -1
    return (
        decision_rank[row['purchase_decision']],
        fit_rank[row['fit_level']],
        quality_rank[row['history_quality']],
        -int(row['best_variant_value_score']),
        -discount,
        row['current_price_rub_unrounded'],
        row['title'].casefold(),
        row['primary_key'],
    )


rows.sort(key=sort_key)
if [x['primary_key'] for x in rows] != [x['primary_key'] for x in sorted(rows, key=sort_key)]:
    raise SystemExit('Non-deterministic sort')

out = {
    'schema_version': 1,
    'purpose': 'deal_quality_and_deterministic_sort_validation',
    'status': 'complete',
    'bindings': {
        'policy_blob_sha': policy_sha,
        'deal_quality_contract_blob_sha': sha('config/deal_quality_contract.json'),
        'taste_index_blob_sha': taste_index_sha,
        'taste_ledger_blob_sha': ledger_sha,
        'taste_checkpoint_blob_sha': sha('data/cache/taste_fit.checkpoint_validation.json'),
        'offer_family_blob_sha': family_sha,
        'store_state_blob_sha': store_sha,
        'steamdb_cache_classification_blob_sha': steamdb_sha,
    },
    'fx': {
        'provider': fx_url,
        'base': 'RUB',
        'quote': 'KZT',
        'kzt_per_rub': rate,
        'provider_updated_at_utc': fx_time.isoformat(),
        'rate_age_hours': age_hours,
        'external_calls': 1,
    },
    'input_primary_count': len(seen_primary),
    'recommendation_count': len(rows),
    'price_excluded_count': len(excluded),
    'classified_count': len(rows) + len(excluded),
    'complete_coverage': True,
    'decision_counts': {d: sum(1 for x in rows if x['purchase_decision'] == d) for d in decision_rank},
    'history_quality_counts': {q: sum(1 for x in rows if x['history_quality'] == q) for q in quality_rank},
    'fit_counts': {f: sum(1 for x in rows if x['fit_level'] == f) for f in fit_rank},
    'price_exclusion_reason_count': sum(
        1 for x in excluded
        if x['exclusion_reason_code'] == 'price_clearly_unreasonable_after_soft_target_evaluation'
    ),
    'sorted_recommendations': rows,
    'price_exclusions': excluded,
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({
    'status': out['status'],
    'input_primary_count': out['input_primary_count'],
    'recommendation_count': out['recommendation_count'],
    'price_excluded_count': out['price_excluded_count'],
    'decision_counts': out['decision_counts'],
    'fit_counts': out['fit_counts'],
    'fx_kzt_per_rub': rate,
    'fx_age_hours': round(age_hours, 2),
}, ensure_ascii=False, indent=2))
