import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGER = ROOT / 'scripts/stage_progressive_pass1_canonical_writer.sh'
WORKFLOW = ROOT / '.github/workflows/ingest-progressive-pass1.yml'

REQUIRED_FILES = [
    'data/ai_inbox/progressive_pass1/result.json',
    'data/cache/progressive_pass1_state.json',
    'data/cache/progressive_pass1_receipts/receipt.json',
    'data/production/pre_ai/progressive_pass1_work.json',
    'data/production/pre_ai/progressive_pass2_work.json',
    'data/cache/taste_steam_review_dossiers/dossier.json',
    'data/production/pre_ai/taste_steam_review_dossier_work.json',
    'data/production/pre_ai/taste_steam_review_dossier_worker_index.json',
    'data/production/pre_ai/taste_steam_review_dossier_validation_status.json',
    'data/production/pre_ai/taste_steam_review_dossier_worker_groups/g000001.json',
]

OPTIONAL_FILES = [
    'data/ai_inbox/taste_steam_review_dossiers/candidate.json',
    'data/quarantine/taste_steam_review_dossier_inbox/rejected.json',
    'data/audit/taste_steam_review_dossier_group_failures.jsonl',
]

OPTIONAL_ROOTS = [
    'data/ai_inbox/taste_steam_review_dossiers',
    'data/quarantine/taste_steam_review_dossier_inbox',
    'data/audit/taste_steam_review_dossier_group_failures.jsonl',
]


def run(cwd, *args):
    return subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=True)


def write(root, relative, content='x\n'):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def init_repo(root, include_optional=False):
    run(root, 'git', 'init', '-q')
    run(root, 'git', 'config', 'user.name', 'test')
    run(root, 'git', 'config', 'user.email', 'test@example.com')
    for path in REQUIRED_FILES:
        write(root, path)
    if include_optional:
        for path in OPTIONAL_FILES:
            write(root, path)
    run(root, 'git', 'add', '-A')
    run(root, 'git', 'commit', '-qm', 'baseline')


def run_stager(root):
    run(root, 'bash', str(STAGER))
    run(root, 'git', 'diff', '--cached', '--check')


def staged(root):
    return run(root, 'git', 'diff', '--cached', '--name-status').stdout


def assert_production_workflow_uses_stager():
    workflow = WORKFLOW.read_text(encoding='utf-8')
    marker = '- name: Commit PASS 1 state and remaining work'
    assert marker in workflow
    commit_block = workflow.split(marker, 1)[1]
    assert 'bash scripts/stage_progressive_pass1_canonical_writer.sh' in commit_block
    for path in OPTIONAL_ROOTS:
        assert path not in commit_block


def main():
    assert_production_workflow_uses_stager()

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        init_repo(root)
        write(root, 'data/cache/progressive_pass1_state.json', 'changed\n')
        run_stager(root)
        assert 'data/cache/progressive_pass1_state.json' in staged(root)
        run(root, 'git', 'commit', '-qm', 'commit without optional dossier paths')

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        init_repo(root, include_optional=True)
        for path in OPTIONAL_FILES:
            (root / path).unlink()
        for directory in (
            'data/ai_inbox/taste_steam_review_dossiers',
            'data/quarantine/taste_steam_review_dossier_inbox',
        ):
            try:
                (root / directory).rmdir()
            except OSError:
                pass
        run_stager(root)
        status = staged(root)
        for path in OPTIONAL_FILES:
            assert f'D\t{path}' in status, (path, status)
        run(root, 'git', 'commit', '-qm', 'stage optional deletions')

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        init_repo(root)
        for path in OPTIONAL_FILES:
            write(root, path, 'new\n')
        run_stager(root)
        status = staged(root)
        for path in OPTIONAL_FILES:
            assert f'A\t{path}' in status, (path, status)
        run(root, 'git', 'commit', '-qm', 'stage optional additions')

    print('progressive PASS 1 workflow staging regression: ok')


if __name__ == '__main__':
    main()
