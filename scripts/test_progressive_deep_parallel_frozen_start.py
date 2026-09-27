import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path

import ingest_progressive_pass2
import progressive_pass2
import progressive_work_authority
import test_progressive_async_traversal as async_regression
import test_progressive_pass2 as pass2_core


def blob_at(repo, commit, path):
    return async_regression.git(repo, 'rev-parse', f'{commit}:{path}')


def write_active_authority(repo, item, manifest, dossier, when, message):
    async_regression.write_json(
        repo / 'config/progressive_pass2_contract.json',
        {'contract': 'PROGRESSIVE-PASS2-V1', 'implemented': True, 'active': True},
    )
    async_regression.write_json(
        repo / 'data/production/pre_ai/progressive_pass2_work.json',
        manifest,
    )
    async_regression.write_json(repo / item['dossier_path'], dossier)
    async_regression.git(repo, 'add', '.')
    return async_regression.commit(repo, message, when)


def v2_marker(repo, observed, nonce):
    contract_blob = blob_at(repo, observed, 'config/progressive_pass2_contract.json')
    work_blob = blob_at(repo, observed, 'data/production/pre_ai/progressive_pass2_work.json')
    path = (
        repo / 'data/ai_inbox/progressive_pass2/run_starts'
        / f'{observed}--{nonce}.json'
    )
    doc = {
        'schema_version': 2,
        'contract': 'PROGRESSIVE-PASS2-RUN-START-MARKER-V2',
        'observed_main_commit': observed,
        'run_start_nonce': nonce,
        'progressive_pass2_contract_blob_sha': contract_blob,
        'progressive_pass2_work_blob_sha': work_blob,
    }
    async_regression.write_json(path, doc)
    return path, doc


def persist_confirmation(repo, when):
    async_regression.set_git_identity(
        repo, 'steam-kz-bot', 'steam-kz-bot@users.noreply.github.com'
    )
    async_regression.git(repo, 'add', '-A')
    return async_regression.commit(repo, 'Persist Deep frozen start confirmation', when)


def process_markers(repo):
    old = Path.cwd()
    try:
        os.chdir(repo)
        return ingest_progressive_pass2.process_run_start_markers()
    finally:
        os.chdir(old)


def resolve(repo, item, doc, persisted_work):
    old = Path.cwd()
    try:
        os.chdir(repo)
        return ingest_progressive_pass2.resolve_candidate_authority(
            Path(item['result_submission_path']),
            'result_submission_path',
            doc,
            persisted_work,
        )
    finally:
        os.chdir(old)


def concurrent_dossier_success_and_no_substitution():
    item, manifest_a, dossier_a = async_regression.deep_fixture()
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        async_regression.init_repo(repo)
        authority_a = write_active_authority(
            repo, item, manifest_a, dossier_a,
            '2026-09-27T10:00:00+00:00', 'prepare frozen Deep authority A',
        )
        frozen_contract_blob = blob_at(
            repo, authority_a, 'config/progressive_pass2_contract.json'
        )
        frozen_work_blob = blob_at(
            repo, authority_a, 'data/production/pre_ai/progressive_pass2_work.json'
        )

        # Canonical Dossier/work progress advances after A was frozen.
        dossier_b = copy.deepcopy(dossier_a)
        dossier_b['generated_at_utc'] = '2026-09-27T10:01:00Z'
        raw_b = (
            json.dumps(
                dossier_b, ensure_ascii=False, sort_keys=True, separators=(',', ':')
            ) + '\n'
        ).encode('utf-8')
        manifest_b = copy.deepcopy(manifest_a)
        manifest_b['items'][0]['dossier_content_sha256'] = hashlib.sha256(raw_b).hexdigest()
        async_regression.write_json(repo / item['dossier_path'], dossier_b)
        async_regression.write_json(
            repo / 'data/production/pre_ai/progressive_pass2_work.json', manifest_b
        )
        async_regression.git(repo, 'add', '.')
        authority_b = async_regression.commit(
            repo, 'parallel canonical Dossier/work advance B',
            '2026-09-27T10:01:00+00:00',
        )

        marker_path, marker_doc = v2_marker(repo, authority_a, 'a' * 32)
        assert marker_doc['progressive_pass2_contract_blob_sha'] == frozen_contract_blob
        assert marker_doc['progressive_pass2_work_blob_sha'] == frozen_work_blob
        async_regression.git(repo, 'add', marker_path.relative_to(repo).as_posix())
        anchor = async_regression.commit(
            repo, 'Deep V2 run-start marker after parallel Dossier write',
            '2026-09-27T10:02:00+00:00',
        )

        receipts = process_markers(repo)
        assert len(receipts) == 1
        receipt = receipts[0]
        assert receipt['status'] == 'confirmed'
        assert receipt['run_start_authority_commit'] == authority_a
        assert receipt['run_start_marker_parent_commit'] == authority_b
        assert receipt['progressive_pass2_work_blob_sha'] == frozen_work_blob
        assert receipt['progressive_pass2_contract_blob_sha'] == frozen_contract_blob
        persist_confirmation(repo, '2026-09-27T10:02:05+00:00')

        # Result is bound to frozen A even though B already exists.
        result = pass2_core.fit_result(item)
        result.update({
            'run_start_anchor_commit': anchor,
            'run_start_authority_commit': authority_a,
            'run_started_at_utc': receipt['run_started_at_utc'],
        })
        result_path = repo / item['result_submission_path']
        async_regression.write_json(result_path, result)
        async_regression.set_git_identity(
            repo, 'scheduled-worker', 'scheduled-worker@example.invalid'
        )
        async_regression.git(repo, 'add', result_path.relative_to(repo).as_posix())
        async_regression.commit(
            repo, 'publish result from frozen A',
            '2026-09-27T10:03:00+00:00',
        )
        resolved, error = resolve(repo, item, result, manifest_b)
        assert error is None
        assert resolved['_run_start_authority_commit'] == authority_a
        assert resolved['dossier_content_sha256'] == item['dossier_content_sha256']
        assert (
            resolved['dossier_content_sha256']
            != manifest_b['items'][0]['dossier_content_sha256']
        )
        state, accepted = progressive_pass2.process_result_documents(
            pass2_core.work_doc([resolved]),
            pass2_core.empty_pass2_state(),
            [(result_path.name, result, None)],
            accepted_at_utc='2026-09-27T10:04:00+00:00',
        )
        assert accepted[0]['status'] == 'accepted'
        assert state['entries'][item['family_id']]['normal_first_pass_attempted'] is True


def unrelated_write_success():
    item, manifest, dossier = async_regression.deep_fixture()
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        async_regression.init_repo(repo)
        authority_a = write_active_authority(
            repo, item, manifest, dossier,
            '2026-09-27T11:00:00+00:00', 'prepare Deep authority A',
        )
        (repo / 'UNRELATED_CANONICAL_NOTE.txt').write_text('parallel write\n', encoding='utf-8')
        async_regression.git(repo, 'add', 'UNRELATED_CANONICAL_NOTE.txt')
        authority_b = async_regression.commit(
            repo, 'unrelated canonical repository write',
            '2026-09-27T11:01:00+00:00',
        )
        marker_path, _ = v2_marker(repo, authority_a, 'b' * 32)
        async_regression.git(repo, 'add', marker_path.relative_to(repo).as_posix())
        async_regression.commit(
            repo, 'Deep marker after unrelated write',
            '2026-09-27T11:02:00+00:00',
        )
        receipt = process_markers(repo)[0]
        assert receipt['status'] == 'confirmed'
        assert receipt['run_start_authority_commit'] == authority_a
        assert receipt['run_start_marker_parent_commit'] == authority_b


def material_binding_mismatch_rejected():
    item, manifest, dossier = async_regression.deep_fixture()
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        async_regression.init_repo(repo)
        authority_a = write_active_authority(
            repo, item, manifest, dossier,
            '2026-09-27T12:00:00+00:00', 'prepare Deep authority A',
        )
        marker_path, doc = v2_marker(repo, authority_a, 'c' * 32)
        doc['progressive_pass2_work_blob_sha'] = '0' * 40
        async_regression.write_json(marker_path, doc)
        async_regression.git(repo, 'add', marker_path.relative_to(repo).as_posix())
        async_regression.commit(
            repo, 'forged material Deep binding',
            '2026-09-27T12:01:00+00:00',
        )
        receipt = process_markers(repo)[0]
        assert receipt['status'] == 'rejected'
        assert 'work blob mismatch' in receipt['reason']


def arbitrary_historical_binding_rejected():
    item, manifest_a, dossier = async_regression.deep_fixture()
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        async_regression.init_repo(repo)
        historical_a = write_active_authority(
            repo, item, manifest_a, dossier,
            '2026-09-27T13:00:00+00:00', 'prepare historical authority A',
        )
        manifest_b = copy.deepcopy(manifest_a)
        manifest_b['items'][0]['authorization_id'] = 'f' * 64
        async_regression.write_json(
            repo / 'data/production/pre_ai/progressive_pass2_work.json', manifest_b
        )
        async_regression.git(repo, 'add', '.')
        current_b = async_regression.commit(
            repo, 'replace prepared Deep authorization with B',
            '2026-09-27T13:01:00+00:00',
        )

        # A historical commit plus current-looking bindings is not a valid freeze.
        marker_path, doc = v2_marker(repo, historical_a, 'd' * 32)
        doc['progressive_pass2_work_blob_sha'] = blob_at(
            repo, current_b, 'data/production/pre_ai/progressive_pass2_work.json'
        )
        async_regression.write_json(marker_path, doc)
        async_regression.git(repo, 'add', marker_path.relative_to(repo).as_posix())
        async_regression.commit(
            repo, 'attempt historical Deep authority revival',
            '2026-09-27T13:02:00+00:00',
        )
        receipt = process_markers(repo)[0]
        assert receipt['status'] == 'rejected'
        assert 'work blob mismatch' in receipt['reason']


def non_ancestor_history_rejected():
    item, manifest, dossier = async_regression.deep_fixture()
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        async_regression.init_repo(repo)
        base = write_active_authority(
            repo, item, manifest, dossier,
            '2026-09-27T14:00:00+00:00', 'base authority',
        )
        async_regression.git(repo, 'checkout', '-qb', 'other', base)
        (repo / 'other.txt').write_text('other branch\n', encoding='utf-8')
        async_regression.git(repo, 'add', 'other.txt')
        other = async_regression.commit(
            repo, 'unrelated historical branch authority',
            '2026-09-27T14:01:00+00:00',
        )
        async_regression.git(repo, 'checkout', '-q', 'master')
        (repo / 'main.txt').write_text('main line\n', encoding='utf-8')
        async_regression.git(repo, 'add', 'main.txt')
        async_regression.commit(
            repo, 'advance canonical line',
            '2026-09-27T14:02:00+00:00',
        )

        # Build a syntactically exact marker for a commit that is not in marker-parent lineage.
        contract_blob = blob_at(repo, other, 'config/progressive_pass2_contract.json')
        work_blob = blob_at(repo, other, 'data/production/pre_ai/progressive_pass2_work.json')
        path = (
            repo / 'data/ai_inbox/progressive_pass2/run_starts'
            / f'{other}--{"e" * 32}.json'
        )
        async_regression.write_json(path, {
            'schema_version': 2,
            'contract': 'PROGRESSIVE-PASS2-RUN-START-MARKER-V2',
            'observed_main_commit': other,
            'run_start_nonce': 'e' * 32,
            'progressive_pass2_contract_blob_sha': contract_blob,
            'progressive_pass2_work_blob_sha': work_blob,
        })
        async_regression.git(repo, 'add', path.relative_to(repo).as_posix())
        async_regression.commit(
            repo, 'attempt non-ancestor historical authority',
            '2026-09-27T14:03:00+00:00',
        )
        receipt = process_markers(repo)[0]
        assert receipt['status'] == 'rejected'
        assert 'not an ancestor' in receipt['reason']


def main():
    concurrent_dossier_success_and_no_substitution()
    unrelated_write_success()
    material_binding_mismatch_rejected()
    arbitrary_historical_binding_rejected()
    non_ancestor_history_rejected()
    print('progressive Deep parallel frozen start authority regression: ok')


if __name__ == '__main__':
    main()
