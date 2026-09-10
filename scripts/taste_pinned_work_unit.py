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
BINDING_FIELDS = (
    'profile_blob_sha',
    'taste_model_version',
    'taste_semantics_sha256',
    'source_mailing_updated_at_utc',
)
PROFILE_IDENTITY_FIELDS = (
    'repository',
    'path',
    'resolved_commit_sha',
    'blob_sha',
    'content_sha256',
    'bytes',
)

# Narrow grandfathering authority for the already-produced 10-result package.
# This is intentionally path+commit exact and is not a general historical-profile fallback.
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


def _canonical_sha256(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def read_jsonl(path):
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding='utf-8').splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f'Invalid JSONL at {path}:{number}: {exc}') from exc
    return rows


def _bindings_from_projection(projection):
    current_profile = projection.get('current_profile') or {}
    current_binding = projection.get('current_binding') or {}
    bindings = {
        'profile_blob_sha': current_profile.get('blob_sha'),
        'taste_model_version': current_binding.get('taste_model_version'),
        'taste_semantics_sha256': current_binding.get('taste_semantics_sha256'),
        'source_mailing_updated_at_utc': projection.get('source_mailing_updated_at_utc'),
    }
    missing = [field for field, value in bindings.items() if value in (None, '')]
    if missing:
        raise ValueError(f'Pinned work-unit projection missing bindings: {missing}')
    return bindings


def _normalized_profile_identity(projection, profile_binding):
    projection_profile = projection.get('current_profile') or {}
    profile_binding = dict(profile_binding or {})
    identity = {
        'repository': profile_binding.get('repository') or projection_profile.get('repository'),
        'path': profile_binding.get('path') or projection_profile.get('path'),
        'resolved_commit_sha': profile_binding.get('resolved_commit_sha') or profile_binding.get('commit_sha'),
        'blob_sha': profile_binding.get('blob_sha') or projection_profile.get('blob_sha'),
        'content_sha256': profile_binding.get('content_sha256'),
        'bytes': profile_binding.get('bytes') if profile_binding.get('bytes') is not None else projection_profile.get('bytes'),
    }
    if identity['blob_sha'] != projection_profile.get('blob_sha'):
        raise ValueError('Frozen profile blob does not match prepared Taste projection')
    missing = [field for field in PROFILE_IDENTITY_FIELDS if identity.get(field) in (None, '')]
    if missing:
        raise ValueError(f'Pinned work-unit lacks immutable profile identity fields: {missing}')
    if not isinstance(identity['bytes'], int) or identity['bytes'] <= 0:
        raise ValueError('Pinned profile byte count must be a positive integer')
    if len(str(identity['resolved_commit_sha'])) != 40 or len(str(identity['blob_sha'])) != 40:
        raise ValueError('Pinned profile commit/blob SHA must be 40 hex characters')
    if len(str(identity['content_sha256'])) != 64:
        raise ValueError('Pinned profile content SHA256 must be 64 hex characters')
    return identity


def _pin_row(queue_row):
    work_required = queue_row.get('work_required')
    if not isinstance(work_required, list) or not work_required:
        raise ValueError(f"Pinned queue row has no work_required: {queue_row.get('taste_subject_key')!r}")
    row = {
        'key': queue_row.get('taste_subject_key'),
        'appid': str(queue_row.get('appid')),
        'taste_fingerprint': queue_row.get('taste_fingerprint'),
        'candidate_context_sha256': queue_row.get('candidate_context_sha256'),
        'work_required': list(work_required),
    }
    if not isinstance(row['key'], str) or not row['key']:
        raise ValueError('Pinned queue row requires taste_subject_key')
    for field in ('taste_fingerprint', 'candidate_context_sha256'):
        value = row[field]
        if not isinstance(value, str) or len(value) != 64:
            raise ValueError(f"Pinned queue row has invalid {field}: {row['key']}")
    return row


def _pin_hash_payload(pin):
    return {
        'schema': pin.get('schema'),
        'producer_id': pin.get('producer_id'),
        'producer_generation': pin.get('producer_generation'),
        'profile_identity': pin.get('profile_identity'),
        'bindings': pin.get('bindings'),
        'ordered_rows': pin.get('ordered_rows'),
    }


def validate_pin_authority(pin):
    if not isinstance(pin, dict) or pin.get('schema') != PIN_SCHEMA:
        raise ValueError('No valid durable pinned Taste work-unit authority')
    if pin.get('status') != 'active':
        raise ValueError('Pinned Taste work-unit is not active')
    if pin.get('producer_id') != ACTIVE_PRODUCER_ID:
        raise ValueError('Pinned Taste work-unit producer_id is not canonical')
    if pin.get('producer_generation') != ACTIVE_PRODUCER_GENERATION:
        raise ValueError('Pinned Taste work-unit producer_generation is not canonical')
    profile = pin.get('profile_identity') or {}
    missing_profile = [field for field in PROFILE_IDENTITY_FIELDS if profile.get(field) in (None, '')]
    if missing_profile:
        raise ValueError(f'Pinned Taste work-unit profile identity incomplete: {missing_profile}')
    bindings = pin.get('bindings') or {}
    missing_bindings = [field for field in BINDING_FIELDS if bindings.get(field) in (None, '')]
    if missing_bindings:
        raise ValueError(f'Pinned Taste work-unit bindings incomplete: {missing_bindings}')
    if bindings.get('profile_blob_sha') != profile.get('blob_sha'):
        raise ValueError('Pinned profile blob differs between identity and semantic bindings')
    rows = pin.get('ordered_rows')
    if not isinstance(rows, list) or not rows or len(rows) > CANONICAL_BATCH_SIZE:
        raise ValueError('Pinned Taste work-unit ordered_rows cardinality is invalid')
    normalized = []
    for row in rows:
        normalized.append(_pin_row({
            'taste_subject_key': row.get('key'),
            'appid': row.get('appid'),
            'taste_fingerprint': row.get('taste_fingerprint'),
            'candidate_context_sha256': row.get('candidate_context_sha256'),
            'work_required': row.get('work_required'),
        }))
    if normalized != rows:
        raise ValueError('Pinned Taste work-unit rows are not canonical')
    if len({row['key'] for row in rows}) != len(rows):
        raise ValueError('Pinned Taste work-unit contains duplicate taste_subject_key values')
    expected_hash = _canonical_sha256(_pin_hash_payload(pin))
    if pin.get('ordered_work_unit_sha256') != expected_hash:
        raise ValueError('Pinned Taste work-unit SHA256 does not match its exact contents')
    return pin


def build_pinned_work_unit(
    projection,
    queue_rows,
    profile_binding,
    *,
    prepared_at_utc=None,
    authority='canonical_git_pre_semantic_work_unit_pin',
):
    """Build the exact next Taste work-unit after the live profile has been immutably frozen."""
    if projection.get('status') != 'complete' or not projection.get('complete_coverage'):
        raise ValueError('Pinned taste projection is incomplete')
    if not isinstance(queue_rows, list) or not queue_rows:
        raise ValueError('Pinned ChatGPT taste queue is empty')

    batch_count = min(CANONICAL_BATCH_SIZE, len(queue_rows))
    rows = [_pin_row(row) for row in queue_rows[:batch_count]]
    if len({row['key'] for row in rows}) != len(rows):
        raise ValueError('Pinned work-unit contains duplicate taste_subject_key values')

    pin = {
        'schema': PIN_SCHEMA,
        'status': 'active',
        'authority': authority,
        'prepared_at_utc': prepared_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        'producer_id': ACTIVE_PRODUCER_ID,
        'producer_generation': ACTIVE_PRODUCER_GENERATION,
        'profile_identity': _normalized_profile_identity(projection, profile_binding),
        'bindings': _bindings_from_projection(projection),
        'ordered_rows': rows,
    }
    pin['ordered_work_unit_sha256'] = _canonical_sha256(_pin_hash_payload(pin))
    return validate_pin_authority(pin)


def pin_queue_rows(pin):
    validate_pin_authority(pin)
    return [{
        'taste_subject_key': row['key'],
        'appid': row['appid'],
        'taste_fingerprint': row['taste_fingerprint'],
        'candidate_context_sha256': row['candidate_context_sha256'],
        'work_required': list(row['work_required']),
    } for row in pin['ordered_rows']]


def pin_projection(pin):
    validate_pin_authority(pin)
    identity = pin['profile_identity']
    bindings = pin['bindings']
    return {
        'status': 'complete',
        'complete_coverage': True,
        'source_mailing_updated_at_utc': bindings['source_mailing_updated_at_utc'],
        'current_profile': {
            'repository': identity['repository'],
            'path': identity['path'],
            'blob_sha': identity['blob_sha'],
            'bytes': identity['bytes'],
        },
        'current_binding': {
            'taste_model_version': bindings['taste_model_version'],
            'taste_semantics_sha256': bindings['taste_semantics_sha256'],
        },
    }


def validate_document_against_pin(doc, pin, *, authority_commit=None, legacy=False):
    validate_pin_authority(pin)
    if doc.get('schema_version') != 1:
        raise ValueError('Unexpected ingest schema_version')
    bindings = doc.get('bindings')
    if not isinstance(bindings, dict):
        raise ValueError('Ingest bindings must be an object')

    expected_bindings = pin['bindings']
    for field in BINDING_FIELDS:
        if bindings.get(field) != expected_bindings.get(field):
            raise ValueError(
                f'Ingest binding mismatch for pinned {field}: '
                f"input={bindings.get(field)!r} pinned={expected_bindings.get(field)!r}"
            )

    if not legacy:
        if not authority_commit or len(authority_commit) != 40:
            raise ValueError('Canonical pinned work-unit authority commit is missing')
        if bindings.get('pinned_work_unit_sha256') != pin['ordered_work_unit_sha256']:
            raise ValueError('Ingest result is not bound to the exact pinned work-unit SHA256')
        if bindings.get('pin_authority_commit') != authority_commit:
            raise ValueError('Ingest result is not bound to the exact pre-semantic pin commit')

    results = doc.get('results')
    if not isinstance(results, list) or not results:
        raise ValueError('Ingest results must be a non-empty array')
    if len(results) > 100:
        raise ValueError('A single taste ingest batch may contain at most 100 results')
    rows = pin['ordered_rows']
    if len(results) != len(rows):
        raise ValueError(
            f'Ingest result count does not match pinned work-unit: input={len(results)} pinned={len(rows)}'
        )

    seen = set()
    for index, (result, row) in enumerate(zip(results, rows)):
        if not isinstance(result, dict):
            raise ValueError('Every ingest result must be an object')
        key = result.get('key')
        if key in seen:
            raise ValueError(f'Duplicate ingest key: {key}')
        seen.add(key)
        if key != row['key']:
            raise ValueError(
                f'Ingest ordered work-unit mismatch at index {index}: input={key!r} pinned={row["key"]!r}'
            )
        if str(result.get('appid')) != row['appid']:
            raise ValueError(f'Appid mismatch for pinned work-unit row {key}')
        if result.get('taste_fingerprint') != row['taste_fingerprint']:
            raise ValueError(f'Taste fingerprint mismatch for pinned work-unit row {key}')
        if result.get('candidate_context_sha256') != row['candidate_context_sha256']:
            raise ValueError(f'Candidate context mismatch for pinned work-unit row {key}')
    return bindings


def _git(repo_root, *args, check=True):
    proc = subprocess.run(['git', *args], cwd=repo_root, text=True, capture_output=True, check=False)
    if check and proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise ValueError(f'Git pinned-work-unit proof failed: {detail}')
    return proc


def _git_text(repo_root, *args):
    return _git(repo_root, *args).stdout.strip()


def _git_bytes(repo_root, commit, path):
    proc = subprocess.run(['git', 'show', f'{commit}:{path}'], cwd=repo_root, capture_output=True, check=False)
    if proc.returncode != 0:
        detail = proc.stderr.decode('utf-8', errors='replace').strip()
        raise ValueError(f'Git pinned-work-unit snapshot missing {path} at {commit}: {detail}')
    return proc.stdout


def _result_introduction_commit(repo_root, rel_input, current_bytes):
    additions = [line.strip() for line in _git_text(
        repo_root, 'log', '--diff-filter=A', '--format=%H', '--', rel_input,
    ).splitlines() if line.strip()]
    if not additions:
        raise ValueError('Ingest result has no durable Git introduction commit')
    result_commit = additions[0]
    if _git_bytes(repo_root, result_commit, rel_input) != current_bytes:
        raise ValueError('Ingest result changed after its durable introduction commit')
    return result_commit


def _legacy_pin(repo_root, rel_projection, rel_queue):
    projection = json.loads(_git_bytes(repo_root, LEGACY_PIN_COMMIT, rel_projection).decode('utf-8'))
    queue_rows = []
    for number, line in enumerate(_git_bytes(repo_root, LEGACY_PIN_COMMIT, rel_queue).decode('utf-8').splitlines(), start=1):
        if not line.strip():
            continue
        try:
            queue_rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f'Invalid legacy pinned queue JSONL at line {number}: {exc}') from exc
    pin = build_pinned_work_unit(
        projection,
        queue_rows,
        LEGACY_PROFILE_IDENTITY,
        prepared_at_utc='2026-09-10T08:14:03+00:00',
        authority='grandfathered_git_pre_semantic_checkpoint',
    )
    return pin, projection, queue_rows[:len(pin['ordered_rows'])]


def resolve_pinned_work_unit(
    input_path,
    projection_path=DEFAULT_PROJECTION,
    queue_path=DEFAULT_QUEUE,
    active_pin_path=ACTIVE_PIN,
    repo_root=Path('.'),
):
    """Resolve only a proven pre-semantic active pin or the exact grandfathered 10-result package."""
    repo_root = Path(repo_root).resolve()
    input_path = Path(input_path).resolve()
    active_pin_path = Path(active_pin_path).resolve()
    try:
        rel_input = input_path.relative_to(repo_root).as_posix()
        rel_projection = Path(projection_path).resolve().relative_to(repo_root).as_posix()
        rel_queue = Path(queue_path).resolve().relative_to(repo_root).as_posix()
        rel_pin = active_pin_path.relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise ValueError('Pinned Taste paths must be inside the canonical Git checkout') from exc

    current_bytes = input_path.read_bytes()
    result_commit = _result_introduction_commit(repo_root, rel_input, current_bytes)

    if rel_input == LEGACY_RESULT_PATH:
        if result_commit != LEGACY_RESULT_COMMIT:
            raise ValueError('Grandfathered Taste result path was reintroduced and is no longer grandfatherable')
        parent = _git_text(repo_root, 'rev-parse', f'{result_commit}^')
        if parent != LEGACY_PIN_COMMIT:
            raise ValueError('Grandfathered Taste result no longer has the proven pre-semantic checkpoint parent')
        pin, projection, rows = _legacy_pin(repo_root, rel_projection, rel_queue)
        validate_document_against_pin(json.loads(current_bytes.decode('utf-8')), pin, legacy=True)
        pin = dict(pin)
        pin['authority_commit'] = LEGACY_PIN_COMMIT
        pin['result_commit'] = result_commit
        pin['grandfathered_legacy_package'] = True
        return pin, projection, rows

    if not active_pin_path.exists():
        raise ValueError('No durable active pinned Taste work-unit exists for this result')
    pin_bytes = active_pin_path.read_bytes()
    pin_commit = _git_text(repo_root, 'log', '-1', '--format=%H', '--', rel_pin)
    if not pin_commit:
        raise ValueError('Active Taste work-unit pin has no durable Git commit')
    if _git_bytes(repo_root, pin_commit, rel_pin) != pin_bytes:
        raise ValueError('Active Taste work-unit pin changed after its durable authority commit')
    ancestor = _git(repo_root, 'merge-base', '--is-ancestor', pin_commit, result_commit, check=False)
    if ancestor.returncode != 0:
        raise ValueError('Result introduction commit does not descend from its claimed pre-semantic pin commit')

    pin = json.loads(pin_bytes.decode('utf-8'))
    validate_document_against_pin(
        json.loads(current_bytes.decode('utf-8')),
        pin,
        authority_commit=pin_commit,
        legacy=False,
    )
    resolved_pin = dict(pin)
    resolved_pin['authority_commit'] = pin_commit
    resolved_pin['result_commit'] = result_commit
    resolved_pin['grandfathered_legacy_package'] = False
    return resolved_pin, pin_projection(pin), pin_queue_rows(pin)


def prepare_pin(projection_path, queue_path, profile_binding_path, output_path):
    output_path = Path(output_path)
    if output_path.exists():
        raise ValueError(f'Active Taste work-unit already exists: {output_path}')
    projection = json.loads(Path(projection_path).read_text(encoding='utf-8'))
    queue_rows = read_jsonl(queue_path)
    profile_binding = json.loads(Path(profile_binding_path).read_text(encoding='utf-8'))
    pin = build_pinned_work_unit(projection, queue_rows, profile_binding)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(pin, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return pin


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    prepare = sub.add_parser('prepare')
    prepare.add_argument('--projection', type=Path, default=DEFAULT_PROJECTION)
    prepare.add_argument('--queue', type=Path, default=DEFAULT_QUEUE)
    prepare.add_argument('--profile-binding', required=True, type=Path)
    prepare.add_argument('--output', type=Path, default=ACTIVE_PIN)
    args = parser.parse_args()
    if args.command == 'prepare':
        try:
            pin = prepare_pin(args.projection, args.queue, args.profile_binding, args.output)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        print(json.dumps({
            'status': 'prepared_not_yet_durable',
            'path': str(args.output),
            'ordered_work_unit_sha256': pin['ordered_work_unit_sha256'],
            'profile_blob_sha': pin['bindings']['profile_blob_sha'],
            'result_binding_requirement': 'commit this pin before semantics; bind result to pin SHA256 + authority commit',
        }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
