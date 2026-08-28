import json
import math
import time
from collections import Counter
from pathlib import Path

FAMILIES = Path('data/production/pre_ai/family_graph.json')
STORE = Path('data/production/pre_ai/store_snapshot.json')
HISTORY_CACHE = Path('data/cache/steamdb_history.json')
CONTROL = Path('data/cache/deal_quality.validation.json')
OUT = Path('data/production/pre_ai/history_snapshot.json')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def history_quality(current_kzt, cache_entry):
    if cache_entry is None:
        return {
            'cache_status': 'missing',
            'history_quality': 'unverified',
            'historical_min_kzt': None,
            'delta_vs_paid_historical_minimum': None,
            'evidence': 'no_persistent_exact_history_cache_entry',
        }

    status = cache_entry.get('status')
    if status == 'previously_free':
        return {
            'cache_status': status,
            'history_quality': 'previously_free',
            'historical_min_kzt': 0.0,
            'delta_vs_paid_historical_minimum': None,
            'evidence': 'persistent_cache_previously_free',
        }
    if status == 'unavailable_exact_history':
        return {
            'cache_status': status,
            'history_quality': 'unverified',
            'historical_min_kzt': None,
            'delta_vs_paid_historical_minimum': None,
            'evidence': 'persistent_cache_exact_history_unavailable',
        }
    if status != 'confirmed_min':
        raise SystemExit(f'Unsupported persistent history status: {status!r}')

    hist = float(cache_entry.get('historical_min_kzt'))
    if not math.isfinite(hist) or hist <= 0:
        raise SystemExit('Confirmed paid historical minimum must be finite and positive')

    delta = current_kzt / hist - 1.0
    if current_kzt <= hist + 1e-12:
        quality = 'record'
        evidence = (
            'current_store_price_below_confirmed_cached_minimum'
            if current_kzt < hist - 1e-12
            else 'current_store_price_equals_confirmed_cached_minimum'
        )
    elif delta <= 0.10 + 1e-12:
        quality = 'near_record'
        evidence = 'confirmed_cached_minimum_within_10_percent'
    elif delta <= 0.25 + 1e-12:
        quality = 'good_vs_history'
        evidence = 'confirmed_cached_minimum_within_25_percent'
    else:
        quality = 'well_above_history'
        evidence = 'confirmed_cached_minimum_more_than_25_percent_lower'

    return {
        'cache_status': status,
        'history_quality': quality,
        'historical_min_kzt': hist,
        'delta_vs_paid_historical_minimum': delta,
        'evidence': evidence,
    }


def compare_control(rows):
    if not CONTROL.exists():
        return {'control_available': False}

    control = load(CONTROL)
    old_rows = {}
    for row in (control.get('sorted_recommendations') or []) + (control.get('price_exclusions') or []):
        key = row.get('primary_key')
        if key:
            old_rows[key] = row

    comparable = []
    mismatches = []
    for key, new in rows.items():
        old = old_rows.get(key)
        if not old:
            continue
        old_current = old.get('current_kzt')
        if old_current is None or not math.isclose(float(old_current), float(new['current_kzt']), rel_tol=0, abs_tol=1e-12):
            continue
        comparable.append(key)
        if old.get('history_quality') != new.get('history_quality'):
            mismatches.append({
                'primary_key': key,
                'old_history_quality': old.get('history_quality'),
                'new_history_quality': new.get('history_quality'),
            })

    if mismatches:
        raise SystemExit(f'History quality differs from unchanged-price validated control: {mismatches[:5]}')

    return {
        'control_available': True,
        'control_row_count': len(old_rows),
        'comparable_unchanged_price_count': len(comparable),
        'match_count': len(comparable),
        'mismatch_count': 0,
        'match_ratio': 1.0 if comparable else None,
    }


def main():
    started = time.monotonic()
    family_doc = load(FAMILIES)
    store_doc = load(STORE)
    cache_doc = load(HISTORY_CACHE)

    if family_doc.get('status') != 'complete':
        raise SystemExit('Pre-AI family graph incomplete')
    if not family_doc.get('complete_coverage_of_nonexcluded_candidates'):
        raise SystemExit('Pre-AI family graph lacks complete candidate coverage')
    if store_doc.get('status') != 'complete':
        raise SystemExit('Pre-AI Store snapshot incomplete')
    if cache_doc.get('country_code') != 'kz' or cache_doc.get('currency') != 'KZT':
        raise SystemExit('Persistent history cache is not Kazakhstan/KZT')

    families = family_doc.get('families') or []
    store = store_doc.get('entries') or {}
    cache = cache_doc.get('entries') or {}
    primaries = [x['primary_key'] for x in families]
    if len(primaries) != int(family_doc.get('family_count') or -1):
        raise SystemExit('Family primary count mismatch')
    if len(primaries) != len(set(primaries)):
        raise SystemExit('Duplicate family primary key')

    rows = {}
    for family in families:
        key = family['primary_key']
        state = store.get(key)
        if state is None:
            raise SystemExit(f'Missing current Store state for primary {key}')
        current_kzt = float(state['final_kzt'])
        if not math.isfinite(current_kzt) or current_kzt < 0:
            raise SystemExit(f'Invalid current KZT price for {key}')

        classified = history_quality(current_kzt, cache.get(key))
        rows[key] = {
            'family_id': family['family_id'],
            'primary_key': key,
            'title': family['primary_title'],
            'current_kzt': current_kzt,
            **classified,
        }

    if set(rows) != set(primaries):
        raise SystemExit('History classification primary coverage mismatch')

    cache_status_counts = Counter(row['cache_status'] for row in rows.values())
    quality_counts = Counter(row['history_quality'] for row in rows.values())
    below_count = sum(
        1 for row in rows.values()
        if row['evidence'] == 'current_store_price_below_confirmed_cached_minimum'
    )
    control = compare_control(rows)

    out = {
        'schema_version': 1,
        'purpose': 'pre_ai_nonblocking_price_history_classification',
        'status': 'complete',
        'source_family_count': len(families),
        'persistent_cache_path': str(HISTORY_CACHE),
        'persistent_cache_updated_at_utc': cache_doc.get('updated_at_utc'),
        'persistent_cache_entry_count': len(cache),
        'primary_count': len(rows),
        'classified_count': len(rows),
        'complete_coverage': True,
        'external_calls': 0,
        'cache_status_counts': dict(sorted(cache_status_counts.items())),
        'history_quality_counts': dict(sorted(quality_counts.items())),
        'confirmed_current_below_cached_min_count': below_count,
        'validated_control_comparison': control,
        'entries': rows,
        'elapsed_seconds': round(time.monotonic() - started, 3),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')

    print(json.dumps({
        'status': out['status'],
        'primary_count': out['primary_count'],
        'classified_count': out['classified_count'],
        'complete_coverage': out['complete_coverage'],
        'external_calls': out['external_calls'],
        'cache_status_counts': out['cache_status_counts'],
        'history_quality_counts': out['history_quality_counts'],
        'confirmed_current_below_cached_min_count': below_count,
        'control': control,
        'elapsed_seconds': out['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
