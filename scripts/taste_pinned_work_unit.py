import hashlib
import json
import subprocess
from pathlib import Path

PIN_SCHEMA = 'TASTE-PINNED-WORK-UNIT-V1'
CANONICAL_BATCH_SIZE = 10
BINDING_FIELDS = (
    'profile_blob_sha',
    'taste_model_version',
    'taste_semantics_sha256',
    'source_mailing_updated_at_utc',
)


def _canonical_sha256(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


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


def build_pinned_work_unit(projection, queue_rows, authority_commit=None, result_commit=None):
    """Build the exact deterministic next Taste work-unit from an immutable pre-result snapshot."""
    if projection.get('status') != 'complete' or not projection.get('complete_coverage'):
        raise ValueError('Pinned taste projection is incomplete')
    if not isinstance(queue_rows, list) or not queue_rows:
        raise ValueError('Pinned ChatGPT taste queue is empty')

    batch_count = min(CANONICAL_BATCH_SIZE, len(queue_rows))
    rows = [_pin_row(row) for row in queue_rows[:batch_count]]
    keys = [row['key'] for row in rows]
    if len(set(keys)) != len(keys):
        raise ValueError('Pinned work-unit contains duplicate taste_subject_key values')

    profile = projection.get('current_profile') or {}
    pin = {
        'schema': PIN_SCHEMA,
        'authority': 'git_pre_result_parent_snapshot',
        'authority_commit': authority_commit,
        'result_commit': result_commit,
        'profile_identity': {
            'repository': profile.get('repository'),
            'path': profile.get('path'),
            'blob_sha': profile.get('blob_sha'),
            'bytes': profile.get('bytes'),
        },
        'bindings': _bindings_from_projection(projection),
        'ordered_rows': rows,
    }
    pin['ordered_work_unit_sha256'] = _canonical_sha256({
        'bindings': pin['bindings'],
        'profile_identity': pin['profile_identity'],
        'ordered_rows': rows,
    })
    return pin


def validate_document_against_pin(doc, pin):
    if not isinstance(pin, dict) or pin.get('schema') != PIN_SCHEMA:
        raise ValueError('No valid durable pinned Taste work-unit authority')
    if doc.get('schema_version') != 1:
        raise ValueError('Unexpected ingest schema_version')
    bindings = doc.get('bindings')
    if not isinstance(bindings, dict):
        raise ValueError('Ingest bindings must be an object')

    expected_bindings = pin.get('bindings') or {}
    for field in BINDING_FIELDS:
        if bindings.get(field) != expected_bindings.get(field):
            raise ValueError(
                f'Ingest binding mismatch for pinned {field}: '
                f"input={bindings.get(field)!r} pinned={expected_bindings.get(field)!r}"
            )

    results = doc.get('results')
    if not isinstance(results, list) or not results:
        raise ValueError('Ingest results must be a non-empty array')
    if len(results) > 100:
        raise ValueError('A single taste ingest batch may contain at most 100 results')

    rows = pin.get('ordered_rows')
    if not isinstance(rows, list) or not rows:
        raise ValueError('Pinned Taste work-unit has no ordered rows')
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


def _git(repo_root, *args):
    proc = subprocess.run(
        ['git', *args], cwd=repo_root, text=True, capture_output=True, check=False,
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        raise ValueError(f'Git pinned-work-unit proof failed: {detail}')
    return proc.stdout


def _git_bytes(repo_root, commit, path):
    proc = subprocess.run(
        ['git', 'show', f'{commit}:{path}'], cwd=repo_root, capture_output=True, check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.decode('utf-8', errors='replace').strip()
        raise ValueError(f'Git pinned-work-unit snapshot missing {path} at {commit}: {detail}')
    return proc.stdout


def resolve_pinned_work_unit(input_path, projection_path, queue_path, repo_root=Path('.')):
    """
    Resolve authority from the commit immediately before the immutable inbox file was introduced.

    The current inbox bytes must still equal the bytes at their introducing commit. Copying an old
    result into a new commit therefore binds it to that new commit's parent, not to arbitrary history.
    """
    repo_root = Path(repo_root).resolve()
    input_path = Path(input_path).resolve()
    try:
        rel_input = input_path.relative_to(repo_root).as_posix()
        rel_projection = Path(projection_path).resolve().relative_to(repo_root).as_posix()
        rel_queue = Path(queue_path).resolve().relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise ValueError('Pinned Taste paths must be inside the canonical Git checkout') from exc

    additions = [line.strip() for line in _git(
        repo_root, 'log', '--diff-filter=A', '--format=%H', '--', rel_input,
    ).splitlines() if line.strip()]
    if not additions:
        raise ValueError('Ingest result has no durable Git introduction commit')

    result_commit = additions[0]
    committed_input = _git_bytes(repo_root, result_commit, rel_input)
    if committed_input != input_path.read_bytes():
        raise ValueError('Ingest result changed after its durable introduction commit')

    parent = _git(repo_root, 'rev-parse', f'{result_commit}^').strip()
    if not parent:
        raise ValueError('Ingest result introduction commit has no pre-result parent snapshot')

    projection = json.loads(_git_bytes(repo_root, parent, rel_projection).decode('utf-8'))
    queue_rows = []
    for number, line in enumerate(_git_bytes(repo_root, parent, rel_queue).decode('utf-8').splitlines(), start=1):
        if not line.strip():
            continue
        try:
            queue_rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f'Invalid pinned queue JSONL at line {number}: {exc}') from exc

    pin = build_pinned_work_unit(
        projection,
        queue_rows,
        authority_commit=parent,
        result_commit=result_commit,
    )
    return pin, projection, queue_rows[:len(pin['ordered_rows'])]
