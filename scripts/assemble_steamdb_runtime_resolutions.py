#!/usr/bin/env python3
import glob
import json
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = Path('data/cache/steamdb_miss_manifest.json')
PROGRESS = Path('data/cache/steamdb_runtime_progress.json')
BATCH_GLOB = 'data/cache/steamdb_runtime_batches/*.json'
OUT = Path('data/cache/steamdb_web_resolutions.json')

manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
source_sha = manifest['source_validation_blob_sha']
expected = [x['key'] for x in manifest['misses']]
expected_set = set(expected)
if len(expected) != manifest['count'] or len(expected_set) != len(expected):
    raise SystemExit('Invalid SteamDB miss manifest')

confirmed = {}
previously_free = set()
unavailable = {}
special = {}
attempted = set()
transients = {}


def add_source(path: Path):
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('source_validation_blob_sha') != source_sha:
        return
    local_confirmed = data.get('confirmed_min_kzt') or {}
    local_free = set(data.get('previously_free') or [])
    local_unavailable = data.get('unavailable_exact_history') or {}
    local_special = data.get('special_evidence') or {}
    local_transients = data.get('transient_failures') or {}
    local_attempted = set(data.get('attempted_keys') or [])
    if not local_attempted:
        local_attempted = set(local_confirmed) | local_free | set(local_unavailable) | set(local_transients)
    attempted.update(local_attempted)

    for key, value in local_confirmed.items():
        if key not in expected_set:
            raise SystemExit(f'Unexpected confirmed key {key} in {path}')
        if key in confirmed and confirmed[key] != value:
            raise SystemExit(f'Conflicting confirmed minimum for {key}')
        confirmed[key] = value
    for key in local_free:
        if key not in expected_set:
            raise SystemExit(f'Unexpected free key {key} in {path}')
        previously_free.add(key)
    for key, code in local_unavailable.items():
        if key not in expected_set:
            raise SystemExit(f'Unexpected unavailable key {key} in {path}')
        if key in unavailable and unavailable[key] != code:
            raise SystemExit(f'Conflicting unavailable evidence for {key}')
        unavailable[key] = code
    for key, evidence in local_special.items():
        if key in special and special[key] != evidence:
            raise SystemExit(f'Conflicting special evidence for {key}')
        special[key] = evidence
    for key, reason in local_transients.items():
        transients[key] = reason


if PROGRESS.exists():
    add_source(PROGRESS)
for name in sorted(glob.glob(BATCH_GLOB)):
    add_source(Path(name))

resolved = set(confirmed) | previously_free | set(unavailable)
if (set(confirmed) & previously_free) or (set(confirmed) & set(unavailable)) or (previously_free & set(unavailable)):
    raise SystemExit('SteamDB outcome sets overlap')

missing = [key for key in expected if key not in resolved]
if missing:
    print(json.dumps({
        'status': 'waiting_for_runtime',
        'resolved_count': len(resolved),
        'expected_count': len(expected),
        'missing_count': len(missing),
        'transient_count': len([k for k in missing if k in transients]),
        'next_missing': missing[:10],
    }, ensure_ascii=False, indent=2))
    raise SystemExit(0)

out = {
    'schema_version': 1,
    'source_validation_blob_sha': source_sha,
    'runtime_attempted_count': len(attempted | resolved),
    'checked_at_utc': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    'confirmed_min_kzt': {k: confirmed[k] for k in expected if k in confirmed},
    'previously_free': [k for k in expected if k in previously_free],
    'unavailable_exact_history': {k: unavailable[k] for k in expected if k in unavailable},
    'special_evidence': {k: special[k] for k in expected if k in special},
}
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({
    'status': 'complete',
    'resolved_count': len(resolved),
    'expected_count': len(expected),
    'confirmed_min_count': len(confirmed),
    'previously_free_count': len(previously_free),
    'unavailable_count': len(unavailable),
}, ensure_ascii=False, indent=2))
