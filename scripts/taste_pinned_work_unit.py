import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PIN_SCHEMA = 'TASTE-PINNED-WORK-UNIT-V1'
CANONICAL_BATCH_SIZE = 10
ACTIVE_PIN = Path('data/production/pre_ai/taste_active_work_unit.json')
DEFAULT_PROJECTION = Path('data/production/pre_ai/taste_projection.json')
DEFAULT_QUEUE = Path('data/production/pre_ai/chatgpt_taste_queue.jsonl')
ACTIVE_PRODUCER_ID = 'chatgpt_scheduled_task:6aa032f37e688191a5c9a1a83f91c5d9'
ACTIVE_PRODUCER_GENERATION = 2
BINDING_FIELDS = ('profile_blob_sha', 'taste_model_version', 'taste_semantics_sha256', 'source_mailing_updated_at_utc')
PROFILE_IDENTITY_FIELDS = ('repository', 'path', 'resolved_commit_sha', 'blob_sha', 'content_sha256', 'bytes')
LEGACY_RESULT_PATH = 'data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json'
LEGACY_RESULT_COMMIT = 'f138d5216248c999fde588c47ca5088ff9c076ee'
LEGACY_PIN_COMMIT = '0ec1ed0ec10e8950f86e6f600bc360325481ae9b'
LEGACY_PROFILE_IDENTITY = {
    'repository': 'kentrap2011-hub/stopgame-ratings-data',
    'path': 'gaming_taste_live.json',
    'resolved_commit_sha': 'c8a915d1ecad2bfd4f22d83182542925f73b1e54',
    'blob_sha': 'b487e62b3fec9f413fb001d96b4894f8ac43e5d5',
    'content_sha256': '6ed2adb975860783abf402ed74446eb257b1e78af69c332590dc27718a663cc4',
    'bytes': 243058,
}


def _sha(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(path):
    rows = []
    for n, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f'Invalid JSONL at {path}:{n}: {exc}') from exc
    return rows


def _bindings(projection):
    p = projection.get('current_profile') or {}
    b = projection.get('current_binding') or {}
    out = {
        'profile_blob_sha': p.get('blob_sha'),
        'taste_model_version': b.get('taste_model_version'),
        'taste_semantics_sha256': b.get('taste_semantics_sha256'),
        'source_mailing_updated_at_utc': projection.get('source_mailing_updated_at_utc'),
    }
    missing = [k for k, v in out.items() if v in (None, '')]
    if missing:
        raise ValueError(f'Pinned work-unit projection missing bindings: {missing}')
    return out


def _profile(projection, frozen):
    p = projection.get('current_profile') or {}
    frozen = dict(frozen or {})
    out = {
        'repository': frozen.get('repository') or p.get('repository'),
        'path': frozen.get('path') or p.get('path'),
        'resolved_commit_sha': frozen.get('resolved_commit_sha') or frozen.get('commit_sha'),
        'blob_sha': frozen.get('blob_sha') or p.get('blob_sha'),
        'content_sha256': frozen.get('content_sha256'),
        'bytes': frozen.get('bytes') if frozen.get('bytes') is not None else p.get('bytes'),
    }
    if out['blob_sha'] != p.get('blob_sha'):
        raise ValueError('Frozen profile blob does not match prepared Taste projection')
    missing = [k for k in PROFILE_IDENTITY_FIELDS if out.get(k) in (None, '')]
    if missing:
        raise ValueError(f'Pinned work-unit lacks immutable profile identity fields: {missing}')
    if not isinstance(out['bytes'], int) or out['bytes'] <= 0:
        raise ValueError('Pinned profile byte count must be positive')
    return out


def _row(row):
    work = row.get('work_required')
    out = {
        'key': row.get('taste_subject_key') if 'taste_subject_key' in row else row.get('key'),
        'appid': str(row.get('appid')),
        'taste_fingerprint': row.get('taste_fingerprint'),
        'candidate_context_sha256': row.get('candidate_context_sha256'),
        'work_required': list(work) if isinstance(work, list) else work,
    }
    if not out['key'] or not isinstance(out['work_required'], list) or not out['work_required']:
        raise ValueError('Pinned queue row identity/work_required is incomplete')
    for field in ('taste_fingerprint', 'candidate_context_sha256'):
        if not isinstance(out[field], str) or len(out[field]) != 64:
            raise ValueError(f'Pinned queue row has invalid {field}: {out["key"]}')
    return out


def _hash_payload(pin):
    return {k: pin.get(k) for k in ('schema', 'producer_id', 'producer_generation', 'profile_identity', 'bindings', 'ordered_rows')}


def validate_pin_authority(pin):
    if not isinstance(pin, dict) or pin.get('schema') != PIN_SCHEMA or pin.get('status') != 'active':
        raise ValueError('No valid active pinned Taste work-unit authority')
    if pin.get('producer_id') != ACTIVE_PRODUCER_ID or pin.get('producer_generation') != ACTIVE_PRODUCER_GENERATION:
        raise ValueError('Pinned Taste work-unit producer fence mismatch')
    profile = pin.get('profile_identity') or {}
    if any(profile.get(k) in (None, '') for k in PROFILE_IDENTITY_FIELDS):
        raise ValueError('Pinned Taste work-unit profile identity incomplete')
    bindings = pin.get('bindings') or {}
    if any(bindings.get(k) in (None, '') for k in BINDING_FIELDS) or bindings.get('profile_blob_sha') != profile.get('blob_sha'):
        raise ValueError('Pinned Taste semantic bindings incomplete or inconsistent')
    rows = pin.get('ordered_rows')
    if not isinstance(rows, list) or not 1 <= len(rows) <= CANONICAL_BATCH_SIZE:
        raise ValueError('Pinned Taste ordered work-unit cardinality invalid')
    if [_row(r) for r in rows] != rows or len({r['key'] for r in rows}) != len(rows):
        raise ValueError('Pinned Taste ordered rows are noncanonical or duplicated')
    if pin.get('ordered_work_unit_sha256') != _sha(_hash_payload(pin)):
        raise ValueError('Pinned Taste work-unit SHA256 mismatch')
    return pin


def build_pinned_work_unit(projection, queue_rows, profile_binding, *, prepared_at_utc=None, authority='canonical_git_pre_semantic_work_unit_pin'):
    if projection.get('status') != 'complete' or not projection.get('complete_coverage'):
        raise ValueError('Pinned taste projection is incomplete')
    if not isinstance(queue_rows, list) or not queue_rows:
        raise ValueError('Pinned ChatGPT taste queue is empty')
    rows = [_row(r) for r in queue_rows[:CANONICAL_BATCH_SIZE]]
    if len({r['key'] for r in rows}) != len(rows):
        raise ValueError('Pinned work-unit contains duplicate keys')
    pin = {
        'schema': PIN_SCHEMA,
        'status': 'active',
        'authority': authority,
        'prepared_at_utc': prepared_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        'producer_id': ACTIVE_PRODUCER_ID,
        'producer_generation': ACTIVE_PRODUCER_GENERATION,
        'profile_identity': _profile(projection, profile_binding),
        'bindings': _bindings(projection),
        'ordered_rows': rows,
    }
    pin['ordered_work_unit_sha256'] = _sha(_hash_payload(pin))
    return validate_pin_authority(pin)


def pin_queue_rows(pin):
    validate_pin_authority(pin)
    return [{
        'taste_subject_key': r['key'], 'appid': r['appid'], 'taste_fingerprint': r['taste_fingerprint'],
        'candidate_context_sha256': r['candidate_context_sha256'], 'work_required': list(r['work_required']),
    } for r in pin['ordered_rows']]


def pin_projection(pin):
    validate_pin_authority(pin)
    p, b = pin['profile_identity'], pin['bindings']
    return {
        'status': 'complete', 'complete_coverage': True,
        'source_mailing_updated_at_utc': b['source_mailing_updated_at_utc'],
        'current_profile': {'repository': p['repository'], 'path': p['path'], 'blob_sha': p['blob_sha'], 'bytes': p['bytes']},
        'current_binding': {'taste_model_version': b['taste_model_version'], 'taste_semantics_sha256': b['taste_semantics_sha256']},
    }


def validate_document_against_pin(doc, pin, *, authority_commit=None, legacy=None):
    validate_pin_authority(pin)
    if authority_commit is None:
        authority_commit = pin.get('authority_commit')
    if legacy is None:
        legacy = bool(pin.get('grandfathered_legacy_package'))
    if doc.get('schema_version') != 1 or not isinstance(doc.get('bindings'), dict):
        raise ValueError('Unexpected ingest schema or missing bindings')
    bindings = doc['bindings']
    for field in BINDING_FIELDS:
        if bindings.get(field) != pin['bindings'].get(field):
            raise ValueError(f'Ingest binding mismatch for pinned {field}')
    if not legacy:
        if not authority_commit or len(authority_commit) != 40:
            raise ValueError('Canonical pinned work-unit authority commit is missing')
        if bindings.get('pinned_work_unit_sha256') != pin['ordered_work_unit_sha256']:
            raise ValueError('Ingest result is not bound to exact pinned work-unit SHA256')
        if bindings.get('pin_authority_commit') != authority_commit:
            raise ValueError('Ingest result is not bound to exact pre-semantic pin commit')
    results = doc.get('results')
    rows = pin['ordered_rows']
    if not isinstance(results, list) or not results or len(results) > 100:
        raise ValueError('Ingest results cardinality invalid')
    if len(results) != len(rows):
        raise ValueError(f'Ingest result count does not match pinned work-unit: input={len(results)} pinned={len(rows)}')
    seen = set()
    for i, (result, row) in enumerate(zip(results, rows)):
        if not isinstance(result, dict):
            raise ValueError('Every ingest result must be an object')
        key = result.get('key')
        if key in seen:
            raise ValueError(f'Duplicate ingest key: {key}')
        seen.add(key)
        if key != row['key']:
            raise ValueError(f'Ingest ordered work-unit mismatch at index {i}')
        if str(result.get('appid')) != row['appid']:
            raise ValueError(f'Appid mismatch for pinned row {key}')
        if result.get('taste_fingerprint') != row['taste_fingerprint']:
            raise ValueError(f'Taste fingerprint mismatch for pinned row {key}')
        if result.get('candidate_context_sha256') != row['candidate_context_sha256']:
            raise ValueError(f'Candidate context mismatch for pinned row {key}')
    return bindings


def _git(repo, *args, check=True):
    proc = subprocess.run(['git', *args], cwd=repo, text=True, capture_output=True, check=False)
    if check and proc.returncode:
        raise ValueError(f'Git pinned-work-unit proof failed: {(proc.stderr or proc.stdout).strip()}')
    return proc


def _text(repo, *args):
    return _git(repo, *args).stdout.strip()


def _bytes(repo, commit, path):
    proc = subprocess.run(['git', 'show', f'{commit}:{path}'], cwd=repo, capture_output=True, check=False)
    if proc.returncode:
        raise ValueError(f'Git pinned-work-unit snapshot missing {path} at {commit}')
    return proc.stdout


def _result_commit(repo, path, raw):
    commits = [x for x in _text(repo, 'log', '--diff-filter=A', '--format=%H', '--', path).splitlines() if x]
    if not commits:
        raise ValueError('Ingest result has no durable Git introduction commit')
    commit = commits[0]
    if _bytes(repo, commit, path) != raw:
        raise ValueError('Ingest result changed after its durable introduction commit')
    return commit


def _legacy_pin(repo, projection_path, queue_path):
    projection = json.loads(_bytes(repo, LEGACY_PIN_COMMIT, projection_path).decode())
    rows = [json.loads(line) for line in _bytes(repo, LEGACY_PIN_COMMIT, queue_path).decode().splitlines() if line.strip()]
    pin = build_pinned_work_unit(projection, rows, LEGACY_PROFILE_IDENTITY, prepared_at_utc='2026-09-10T08:14:03+00:00', authority='grandfathered_git_pre_semantic_checkpoint')
    return pin, projection, rows[:len(pin['ordered_rows'])]


def resolve_pinned_work_unit(input_path, projection_path=DEFAULT_PROJECTION, queue_path=DEFAULT_QUEUE, active_pin_path=ACTIVE_PIN, repo_root=Path('.')):
    repo = Path(repo_root).resolve(); inp = Path(input_path).resolve(); active = Path(active_pin_path).resolve()
    try:
        rel_inp = inp.relative_to(repo).as_posix(); rel_proj = Path(projection_path).resolve().relative_to(repo).as_posix()
        rel_queue = Path(queue_path).resolve().relative_to(repo).as_posix(); rel_pin = active.relative_to(repo).as_posix()
    except ValueError as exc:
        raise ValueError('Pinned Taste paths must be inside canonical Git checkout') from exc
    raw = inp.read_bytes(); result_commit = _result_commit(repo, rel_inp, raw); doc = json.loads(raw.decode())
    if rel_inp == LEGACY_RESULT_PATH:
        if result_commit != LEGACY_RESULT_COMMIT or _text(repo, 'rev-parse', f'{result_commit}^') != LEGACY_PIN_COMMIT:
            raise ValueError('Grandfathered Taste package provenance mismatch')
        pin, projection, rows = _legacy_pin(repo, rel_proj, rel_queue)
        validate_document_against_pin(doc, pin, legacy=True)
        pin = dict(pin, authority_commit=LEGACY_PIN_COMMIT, result_commit=result_commit, grandfathered_legacy_package=True)
        return pin, projection, rows
    if not active.exists():
        raise ValueError('No durable active pinned Taste work-unit exists for this result')
    pin_raw = active.read_bytes(); pin_commit = _text(repo, 'log', '-1', '--format=%H', '--', rel_pin)
    if not pin_commit or _bytes(repo, pin_commit, rel_pin) != pin_raw:
        raise ValueError('Active Taste pin lacks immutable durable Git authority')
    if _git(repo, 'merge-base', '--is-ancestor', pin_commit, result_commit, check=False).returncode:
        raise ValueError('Result does not descend from claimed pre-semantic pin commit')
    pin = json.loads(pin_raw.decode())
    validate_document_against_pin(doc, pin, authority_commit=pin_commit, legacy=False)
    pin = dict(pin, authority_commit=pin_commit, result_commit=result_commit, grandfathered_legacy_package=False)
    return pin, pin_projection(pin), pin_queue_rows(pin)


def prepare_pin(projection_path, queue_path, profile_binding_path, output_path):
    output = Path(output_path)
    if output.exists():
        raise ValueError(f'Active Taste work-unit already exists: {output}')
    pin = build_pinned_work_unit(json.loads(Path(projection_path).read_text()), read_jsonl(queue_path), json.loads(Path(profile_binding_path).read_text()))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(pin, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return pin


def main():
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare'); p.add_argument('--projection', type=Path, default=DEFAULT_PROJECTION); p.add_argument('--queue', type=Path, default=DEFAULT_QUEUE)
    p.add_argument('--profile-binding', required=True, type=Path); p.add_argument('--output', type=Path, default=ACTIVE_PIN)
    args = parser.parse_args()
    try:
        pin = prepare_pin(args.projection, args.queue, args.profile_binding, args.output)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps({'status': 'prepared_not_yet_durable', 'path': str(args.output), 'ordered_work_unit_sha256': pin['ordered_work_unit_sha256'], 'profile_blob_sha': pin['bindings']['profile_blob_sha']}, indent=2))


if __name__ == '__main__':
    main()
