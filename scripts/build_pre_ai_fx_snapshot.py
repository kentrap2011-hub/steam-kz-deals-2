import json
import math
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STORE = Path('data/production/pre_ai/store_snapshot.json')
CONTRACT = Path('config/deal_quality_contract.json')
OUT = Path('data/production/pre_ai/fx_snapshot.json')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


started = time.monotonic()
store = load(STORE)
contract = load(CONTRACT)

if store.get('status') != 'complete':
    raise SystemExit('Pre-AI Store snapshot is not complete')
if contract.get('contract') != 'DEAL-QUALITY-AND-SORT-V1':
    raise SystemExit('Unexpected deal quality contract')

entries = store.get('entries') or {}
if len(entries) != int(store.get('entry_count') or -1):
    raise SystemExit('Pre-AI Store entry count mismatch')

fx_contract = contract.get('fx') or {}
if fx_contract.get('base') != 'RUB' or fx_contract.get('quote') != 'KZT':
    raise SystemExit('Unexpected FX base/quote contract')
if fx_contract.get('rub_value_formula') != 'kzt / kzt_per_rub':
    raise SystemExit('Unexpected FX formula contract')

fx_url = fx_contract['source_url']
req = urllib.request.Request(
    fx_url,
    headers={'User-Agent': 'steam-kz-deals/1.0', 'Accept': 'application/json'},
)
with urllib.request.urlopen(req, timeout=15) as resp:
    fx = json.loads(resp.read().decode('utf-8'))

if fx.get('result') != 'success' or fx.get('base_code') != 'RUB':
    raise SystemExit('FX provider returned invalid result')
rate = float((fx.get('rates') or {}).get('KZT') or 0)
if not math.isfinite(rate) or rate <= 0:
    raise SystemExit('Invalid RUB/KZT rate')

fx_time = datetime.fromtimestamp(int(fx['time_last_update_unix']), tz=timezone.utc)
now = datetime.now(timezone.utc)
age_hours = (now - fx_time).total_seconds() / 3600
max_age_hours = float(fx_contract['max_rate_age_hours'])
if age_hours < -1 or age_hours > max_age_hours:
    raise SystemExit(f'FX rate stale: {age_hours:.2f}h')

converted = {}
for key, row in entries.items():
    final_kzt = float(row['final_kzt'])
    original_kzt = float(row['original_kzt'])
    if not math.isfinite(final_kzt) or final_kzt < 0:
        raise SystemExit(f'Invalid final_kzt for {key}')
    if not math.isfinite(original_kzt) or original_kzt < 0:
        raise SystemExit(f'Invalid original_kzt for {key}')
    if original_kzt + 1e-12 < final_kzt:
        raise SystemExit(f'original_kzt below final_kzt for {key}')

    final_rub = final_kzt / rate
    original_rub = original_kzt / rate
    if not math.isfinite(final_rub) or not math.isfinite(original_rub):
        raise SystemExit(f'Non-finite RUB conversion for {key}')

    converted[key] = {
        'key': key,
        'final_kzt': final_kzt,
        'original_kzt': original_kzt,
        'final_rub_unrounded': final_rub,
        'final_rub_display': int(round(final_rub)),
        'original_rub_unrounded': original_rub,
        'original_rub_display': int(round(original_rub)),
    }

if set(converted) != set(entries):
    raise SystemExit('FX conversion key coverage mismatch')

# Full-map arithmetic regression: every stored RUB value must reproduce the
# canonical KZT/rate formula within floating-point tolerance.
for key, row in converted.items():
    expected_final = row['final_kzt'] / rate
    expected_original = row['original_kzt'] / rate
    if not math.isclose(row['final_rub_unrounded'], expected_final, rel_tol=0, abs_tol=1e-12):
        raise SystemExit(f'Final RUB formula mismatch for {key}')
    if not math.isclose(row['original_rub_unrounded'], expected_original, rel_tol=0, abs_tol=1e-12):
        raise SystemExit(f'Original RUB formula mismatch for {key}')

out = {
    'schema_version': 1,
    'purpose': 'pre_ai_deterministic_fx_snapshot',
    'status': 'complete',
    'authoritative_for': [
        'kzt_per_rub',
        'current_price_rub',
        'original_price_rub',
    ],
    'source_store_observed_at_utc': store.get('observed_at_utc'),
    'source_store_entry_count': int(store['entry_count']),
    'observed_at_utc': now.isoformat(),
    'fx': {
        'provider': fx_url,
        'base': 'RUB',
        'quote': 'KZT',
        'kzt_per_rub': rate,
        'provider_updated_at_utc': fx_time.isoformat(),
        'rate_age_hours': age_hours,
        'max_rate_age_hours': max_age_hours,
        'external_calls': 1,
        'formula': 'kzt / kzt_per_rub',
    },
    'entry_count': len(converted),
    'complete_coverage': True,
    'entries': converted,
    'elapsed_seconds': round(time.monotonic() - started, 3),
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(
    json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n',
    encoding='utf-8',
)

print(json.dumps({
    'status': out['status'],
    'source_store_entry_count': out['source_store_entry_count'],
    'entry_count': out['entry_count'],
    'complete_coverage': out['complete_coverage'],
    'fx_kzt_per_rub': rate,
    'fx_provider_updated_at_utc': fx_time.isoformat(),
    'fx_age_hours': round(age_hours, 3),
    'external_calls': 1,
    'elapsed_seconds': out['elapsed_seconds'],
}, ensure_ascii=False, indent=2))
