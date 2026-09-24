import json
import re
import subprocess
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
