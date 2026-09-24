import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


COMMIT_SHA_RE = re.compile(r'^[0-9a-f]{40}$')


def _git(repo, *args, check=True):
    proc = subprocess.run(
        ['git', *args], cwd=repo, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if check and proc.returncode:
        raise ValueError(
            f"Progressive Git authority proof failed: git {' '.join(args)}: "
            f"{(proc.stderr or proc.stdout).strip()}"
        )
    return proc


def _text(repo, *args):
    return _git(repo, *args).stdout.strip()


def _relative(repo, path):
    try:
        return Path(path).resolve().relative_to(Path(repo).resolve()).as_posix()
    except ValueError as exc:
        raise ValueError('Progressive authority paths must be inside the canonical checkout') from exc


def _bytes_at(repo, commit, relative_path):
    proc = subprocess.run(
        ['git', 'show', f'{commit}:{relative_path}'], cwd=repo,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if proc.returncode:
        raise ValueError(f'Progressive authority snapshot missing {relative_path} at {commit}')
    return proc.stdout


def file_bytes_at_commit(commit, relative_path, repo_root=Path('.')):
    repo = Path(repo_root).resolve()
    relative = _relative(repo, repo / Path(relative_path))
    return _bytes_at(repo, str(commit), relative)


def result_introduction_commit(artifact_path, repo_root=Path('.')):
    repo = Path(repo_root).resolve()
    artifact = Path(artifact_path).resolve()
    relative = _relative(repo, artifact)
    raw = artifact.read_bytes()
    commits = [
        value for value in
        _text(repo, 'log', '--diff-filter=A', '--format=%H', '--', relative).splitlines()
        if value
    ]
    for commit in commits:
        try:
            if _bytes_at(repo, commit, relative) == raw:
                return commit
        except ValueError:
            continue
    raise ValueError('Progressive result lacks a durable immutable Git introduction commit')


def _resolve_from_manifest_doc(
    doc,
    *,
    artifact_relative,
    path_field,
    expected_contract,
    authority_commit,
    result_commit,
):
    if doc.get('contract') != expected_contract:
        raise ValueError('Progressive authority manifest contract mismatch')
    profile_pin = doc.get('profile_pin')
    if not isinstance(profile_pin, dict) or not profile_pin.get('pin_sha256'):
        raise ValueError('Progressive authority manifest profile pin is missing')
    for item in doc.get('items') or []:
        if not isinstance(item, dict):
            continue
        prepared_path = Path(str(item.get(path_field) or '')).as_posix()
        if prepared_path != artifact_relative:
            continue
        if item.get('profile_pin_sha256') != profile_pin.get('pin_sha256'):
            raise ValueError('Prepared work/profile pin binding is inconsistent')
        resolved = dict(item)
        resolved['_work_authority_commit'] = authority_commit
        resolved['_result_introduction_commit'] = result_commit
        resolved['_profile_pin'] = profile_pin
        return resolved
    raise ValueError('No exact Git-prepared pre-semantic work authority exists for artifact')


def resolve_presemantic_work_item_at_commit(
    artifact_path,
    manifest_path,
    authority_commit,
    *,
    path_field,
    expected_contract,
    repo_root=Path('.'),
):
    repo = Path(repo_root).resolve()
    artifact = Path(artifact_path).resolve()
    manifest = Path(manifest_path).resolve()
    authority_commit = str(authority_commit or '').lower()
    if not COMMIT_SHA_RE.fullmatch(authority_commit):
        raise ValueError('Progressive run-start authority commit is invalid')
    if _text(repo, 'rev-parse', f'{authority_commit}^{{commit}}') != authority_commit:
        raise ValueError('Progressive run-start authority commit does not resolve exactly')

    result_commit = result_introduction_commit(artifact, repo)
    parent = _text(repo, 'rev-parse', f'{result_commit}^')
    if not commit_is_ancestor(authority_commit, parent, repo):
        raise ValueError('Progressive run-start authority does not predate artifact transport')

    relative_manifest = _relative(repo, manifest)
    artifact_relative = _relative(repo, artifact)
    try:
        doc = json.loads(_bytes_at(repo, authority_commit, relative_manifest).decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('Progressive run-start manifest is not valid JSON') from exc
    return _resolve_from_manifest_doc(
        doc,
        artifact_relative=artifact_relative,
        path_field=path_field,
        expected_contract=expected_contract,
        authority_commit=authority_commit,
        result_commit=result_commit,
    )


def resolve_presemantic_work_item(
    artifact_path,
    manifest_path,
    *,
    path_field,
    expected_contract,
    repo_root=Path('.'),
):
    repo = Path(repo_root).resolve()
    artifact = Path(artifact_path).resolve()
    manifest = Path(manifest_path).resolve()
    artifact_name = artifact.name
    relative_manifest = _relative(repo, manifest)
    result_commit = result_introduction_commit(artifact, repo)
    parent = _text(repo, 'rev-parse', f'{result_commit}^')
    commits = [
        value for value in
        _text(repo, 'log', '--format=%H', parent, '--', relative_manifest).splitlines()
        if value
    ]
    for authority_commit in commits:
        try:
            doc = json.loads(_bytes_at(repo, authority_commit, relative_manifest).decode('utf-8'))
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if doc.get('contract') != expected_contract:
            continue
        profile_pin = doc.get('profile_pin')
        if not isinstance(profile_pin, dict) or not profile_pin.get('pin_sha256'):
            continue
        for item in doc.get('items') or []:
            if not isinstance(item, dict):
                continue
            if Path(str(item.get(path_field) or '')).name != artifact_name:
                continue
            if item.get('profile_pin_sha256') != profile_pin.get('pin_sha256'):
                raise ValueError('Prepared work/profile pin binding is inconsistent')
            resolved = dict(item)
            resolved['_work_authority_commit'] = authority_commit
            resolved['_result_introduction_commit'] = result_commit
            resolved['_profile_pin'] = profile_pin
            return resolved
    raise ValueError('No exact Git-prepared pre-semantic work authority exists for artifact')




def commit_parent(commit, repo_root=Path('.')):
    repo = Path(repo_root).resolve()
    commit = str(commit or '').lower()
    if not COMMIT_SHA_RE.fullmatch(commit):
        raise ValueError('Progressive commit identity is invalid')
    parts = _text(repo, 'rev-list', '--parents', '-n', '1', commit).split()
    if len(parts) != 2 or parts[0] != commit:
        raise ValueError('Progressive run-start anchor must be a single-parent Git commit')
    return parts[1]


def commit_committer_time_utc(commit, repo_root=Path('.')):
    repo = Path(repo_root).resolve()
    raw = _text(repo, 'show', '-s', '--format=%cI', str(commit))
    try:
        parsed = datetime.fromisoformat(raw.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('Progressive Git commit time is invalid') from exc
    if parsed.tzinfo is None:
        raise ValueError('Progressive Git commit time must be timezone-aware')
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def validate_run_start_marker_commit(
    anchor_commit,
    marker_path,
    marker_doc,
    *,
    repo_root=Path('.'),
):
    """Prove one create-only marker anchored the actual main parent at run start."""
    repo = Path(repo_root).resolve()
    anchor = str(anchor_commit or '').lower()
    if not COMMIT_SHA_RE.fullmatch(anchor):
        raise ValueError('Progressive run-start anchor commit is invalid')
    if _text(repo, 'rev-parse', f'{anchor}^{{commit}}') != anchor:
        raise ValueError('Progressive run-start anchor commit does not resolve exactly')
    if not isinstance(marker_doc, dict):
        raise ValueError('Progressive run-start marker must be a JSON object')
    required = {
        'schema_version',
        'contract',
        'observed_main_commit',
        'run_start_nonce',
    }
    if set(marker_doc) != required:
        raise ValueError('Progressive run-start marker fields are invalid')
    if marker_doc.get('schema_version') != 1:
        raise ValueError('Progressive run-start marker schema mismatch')
    if marker_doc.get('contract') != 'PROGRESSIVE-PASS2-RUN-START-MARKER-V1':
        raise ValueError('Progressive run-start marker contract mismatch')
    observed = str(marker_doc.get('observed_main_commit') or '').lower()
    nonce = str(marker_doc.get('run_start_nonce') or '').lower()
    if not COMMIT_SHA_RE.fullmatch(observed):
        raise ValueError('Progressive run-start marker observed main is invalid')
    if not re.fullmatch(r'[0-9a-f]{32}', nonce):
        raise ValueError('Progressive run-start marker nonce is invalid')

    relative_marker = _relative(repo, repo / Path(marker_path))
    expected_path = (
        'data/ai_inbox/progressive_pass2/run_starts/'
        f'{observed}--{nonce}.json'
    )
    if relative_marker != expected_path:
        raise ValueError('Progressive run-start marker path does not match its identity')

    parent = commit_parent(anchor, repo)
    if parent != observed:
        raise ValueError(
            'Progressive observed main was superseded before the actual run-start marker'
        )

    changes = [
        value for value in
        _text(repo, 'diff-tree', '--no-commit-id', '--name-status', '-r', anchor).splitlines()
        if value
    ]
    if changes != [f'A\t{relative_marker}']:
        raise ValueError('Progressive run-start anchor commit is not marker-only create-only transport')

    try:
        durable_doc = json.loads(_bytes_at(repo, anchor, relative_marker).decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('Progressive durable run-start marker is not valid JSON') from exc
    if durable_doc != marker_doc:
        raise ValueError('Progressive durable run-start marker content mismatch')

    return {
        'run_start_anchor_commit': anchor,
        'run_start_authority_commit': parent,
        'run_started_at_utc': commit_committer_time_utc(anchor, repo),
        'run_start_nonce': nonce,
        'marker_path': relative_marker,
    }


def _file_introduction_commit_with_bytes(
    relative_path,
    raw,
    *,
    before_commit,
    repo_root=Path('.'),
):
    repo = Path(repo_root).resolve()
    commits = [
        value for value in
        _text(
            repo,
            'log',
            '--diff-filter=A',
            '--format=%H',
            str(before_commit),
            '--',
            str(relative_path),
        ).splitlines()
        if value
    ]
    for commit in commits:
        try:
            if _bytes_at(repo, commit, str(relative_path)) == raw:
                return commit
        except ValueError:
            continue
    raise ValueError('Progressive durable GitHub confirmation receipt has no introduction commit')


def load_confirmed_run_start_receipt_for_artifact(
    artifact_path,
    anchor_commit,
    *,
    receipt_root='data/cache/progressive_pass2_run_start_receipts',
    repo_root=Path('.'),
):
    """Load the GitHub-owned start confirmation that existed before result transport."""
    repo = Path(repo_root).resolve()
    artifact = Path(artifact_path).resolve()
    anchor = str(anchor_commit or '').lower()
    if not COMMIT_SHA_RE.fullmatch(anchor):
        raise ValueError('Progressive run-start anchor commit is invalid')

    result_commit = result_introduction_commit(artifact, repo)
    result_parent = commit_parent(result_commit, repo)
    if not commit_is_ancestor(anchor, result_parent, repo):
        raise ValueError('Progressive run-start anchor does not predate result transport')

    receipt_path = f"{str(receipt_root).rstrip('/')}/{anchor}.json"
    try:
        raw = _bytes_at(repo, result_parent, receipt_path)
        receipt = json.loads(raw.decode('utf-8'))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('Progressive GitHub run-start confirmation receipt is missing') from exc
    if not isinstance(receipt, dict):
        raise ValueError('Progressive GitHub run-start confirmation receipt is invalid')
    if receipt.get('schema_version') != 1:
        raise ValueError('Progressive GitHub run-start confirmation schema mismatch')
    if receipt.get('contract') != 'PROGRESSIVE-PASS2-RUN-START-RECEIPT-V1':
        raise ValueError('Progressive GitHub run-start confirmation contract mismatch')
    if receipt.get('status') != 'confirmed':
        raise ValueError('Progressive GitHub run-start confirmation is not confirmed')
    if receipt.get('run_start_anchor_commit') != anchor:
        raise ValueError('Progressive GitHub run-start confirmation anchor mismatch')

    marker_path = receipt.get('marker_path')
    if not isinstance(marker_path, str) or not marker_path:
        raise ValueError('Progressive GitHub run-start confirmation marker path is missing')
    try:
        marker_raw = _bytes_at(repo, anchor, marker_path)
        marker_doc = json.loads(marker_raw.decode('utf-8'))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError('Progressive anchored run-start marker is unavailable') from exc
    proof = validate_run_start_marker_commit(
        anchor,
        marker_path,
        marker_doc,
        repo_root=repo,
    )
    for field in (
        'run_start_authority_commit',
        'run_started_at_utc',
        'run_start_nonce',
        'marker_path',
    ):
        if receipt.get(field) != proof[field]:
            raise ValueError(f'Progressive GitHub run-start confirmation {field} mismatch')

    receipt_commit = _file_introduction_commit_with_bytes(
        receipt_path,
        raw,
        before_commit=result_parent,
        repo_root=repo,
    )
    if not commit_is_ancestor(anchor, receipt_commit, repo):
        raise ValueError('Progressive GitHub run-start confirmation predates its marker')
    if not commit_is_ancestor(receipt_commit, result_parent, repo):
        raise ValueError('Progressive GitHub run-start confirmation was not durable before result')
    author_name = _text(repo, 'show', '-s', '--format=%an', receipt_commit)
    author_email = _text(repo, 'show', '-s', '--format=%ae', receipt_commit)
    if (
        author_name != 'steam-kz-bot'
        or author_email != 'steam-kz-bot@users.noreply.github.com'
    ):
        raise ValueError('Progressive run-start confirmation was not persisted by GitHub control plane')

    result = dict(receipt)
    result['_receipt_introduction_commit'] = receipt_commit
    result['_result_introduction_commit'] = result_commit
    return result

def consumed_work_ids(receipt_dir):
    consumed = set()
    root = Path(receipt_dir)
    if not root.exists():
        return consumed
    for path in root.glob('*.json'):
        try:
            receipt = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            continue
        status = str(receipt.get('status') or '')
        work_id = receipt.get('work_id')
        if work_id and (status.startswith('accepted') or status == 'replay_ignored'):
            consumed.add(str(work_id))
    return consumed


def commit_is_ancestor(older, newer, repo_root=Path('.')):
    if not older or not newer:
        return False
    if older == newer:
        return True
    return _git(
        Path(repo_root).resolve(), 'merge-base', '--is-ancestor',
        str(older), str(newer), check=False,
    ).returncode == 0


def authority_rank(commit, repo_root=Path('.')):
    return int(_text(Path(repo_root).resolve(), 'rev-list', '--count', str(commit)))
