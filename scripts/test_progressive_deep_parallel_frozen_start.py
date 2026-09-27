import copy
import hashlib
import json
import os
import tempfile
from pathlib import Path

import ingest_progressive_pass2
import progressive_pass2
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


def v2_marker(repo, nonce):
    path = repo / 'data/ai_inbox/progressive_pass2/run_starts' / f'{nonce}.json'
    doc = {
        'schema_version': 2,
        'contract': 'PROGRESSIVE-PASS2-RUN-START-MARKER-V2',
        'run_start_nonce': nonce,
    }
    async_regression.write_json(path, doc)
    return path, doc


def process_markers(repo):
    old = Path.cwd()
    try:
        os.chdir(repo)
        return ingest_progressive_pass2.process_run_start_markers()
    finally:
        os.chdir(old)


def persist_confirmation(repo, when):
    async_regression.set_git_identity(
        repo, 'steam-kz-bot', 'steam-kz-bot@users.noreply.github.com'
    )
    async_regression.git(repo, 'add', '-A')
    return async_regression.commit(repo, 'Persist Deep run-start confirmation', when)


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
            '2026-09-27T10:00:00+00:00', 'prepare Deep authority A',
        )
        frozen_contract_blob = blob_at(
            repo, authority_a, 'config/progressive_pass2_contract.json'
        )
        frozen_work_blob = blob_at(
            repo, authority_a, 'data/production/pre_ai/progressive_pass2_work.json'
        )

        # The marker itself establishes the immutable boundary. GitHub chooses A
        # because A is the marker commit's actual parent.
        marker_path, _ = v2_marker(repo, 'a' * 32)
        async_regression.git(repo, 'add', marker_path.relative_to(repo).as_posix())
        anchor = async_regression.commit(
            repo, 'Deep V2 run-start marker on A',
            '2026-09-27T10:01:00+00:00',
        )

        # Dossier/work advances after the marker but before confirmation is durable.
        dossier_b = copy.deepcopy(dossier_a)
        dossier_b['generated_at_utc'] = '2026-09-27T10:01:30Z'
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
            '2026-09-27T10:02:00+00:00',
        )

        receipts = process_markers(repo)
        assert len(receipts) == 1
        receipt = receipts[0]
        assert receipt['status'] == 'confirmed', receipt
        assert receipt['run_start_anchor_commit'] == anchor
        assert receipt['run_start_authority_commit'] == authority_a
        assert receipt['run_start_marker_parent_commit'] == authority_a
        assert receipt['progressive_pass2_contract_blob_sha'] == frozen_contract_blob
        assert receipt['progressive_pass2_work_blob_sha'] == frozen_work_blob
        assert authority_b != authority_a
        persist_confirmation(repo, '2026-09-27T10:03:00+00:00')

        # A result remains bound to A; B's newer Dossier is not substituted.
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
            '2026-09-27T10:04:00+00:00',
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
            accepted_at_utc='2026-09-27T10:05:00+00:00',
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
        marker_path, _ = v2_marker(repo, 'b' * 32)
        async_regression.git(repo, 'add', marker_path.relative_to(repo).as_posix())
        async_regression.commit(
            repo, 'Deep marker before unrelated write',
            '2026-09-27T11:01:00+00:00',
        )
        (repo / 'UNRELATED_CANONICAL_NOTE.txt').write_text(
            'parallel write\n', encoding='utf-8'
        )
        async_regression.git(repo, 'add', 'UNRELATED_CANONICAL_NOTE.txt')
        async_regression.commit(
            repo, 'unrelated canonical repository write',
            '2026-09-27T11:02:00+00:00',
        )
        receipt = process_markers(repo)[0]
        assert receipt['status'] == 'confirmed', receipt
        assert receipt['run_start_authority_commit'] == authority_a
        assert receipt['run_start_marker_parent_commit'] == authority_a


def material_result_binding_mismatch_rejected():
    item, manifest, dossier = async_regression.deep_fixture()
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        async_regression.init_repo(repo)
        authority = write_active_authority(
            repo, item, manifest, dossier,
            '2026-09-27T12:00:00+00:00', 'prepare exact Deep authority',
        )
        marker_path, _ = v2_marker(repo, 'c' * 32)
        async_regression.git(repo, 'add', marker_path.relative_to(repo).as_posix())
        anchor = async_regression.commit(
            repo, 'Deep V2 marker',
            '2026-09-27T12:01:00+00:00',
        )
        receipt = process_markers(repo)[0]
        assert receipt['status'] == 'confirmed', receipt
        persist_confirmation(repo, '2026-09-27T12:02:00+00:00')

        bad = pass2_core.fit_result(item)
        bad.update({
            'authorization_id': '0' * 64,
            'run_start_anchor_commit': anchor,
            'run_start_authority_commit': authority,
            'run_started_at_utc': receipt['run_started_at_utc'],
        })
        path = repo / item['result_submission_path']
        async_regression.write_json(path, bad)
        async_regression.set_git_identity(
            repo, 'scheduled-worker', 'scheduled-worker@example.invalid'
        )
        async_regression.git(repo, 'add', path.relative_to(repo).as_posix())
        async_regression.commit(
            repo, 'forged material result binding',
            '2026-09-27T12:03:00+00:00',
        )
        resolved, error = resolve(repo, item, bad, manifest)
        assert error is None
        state, receipts = progressive_pass2.process_result_documents(
            pass2_core.work_doc([resolved]),
            pass2_core.empty_pass2_state(),
            [(path.name, bad, None)],
            accepted_at_utc='2026-09-27T12:04:00+00:00',
        )
        assert state['entries'] == {}
        assert receipts[0]['status'].startswith('rejected')


def arbitrary_historical_authority_rejected():
    old_item, manifest_old, dossier_old = async_regression.deep_fixture()
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        async_regression.init_repo(repo)
        historical = write_active_authority(
            repo, old_item, manifest_old, dossier_old,
            '2026-09-27T13:00:00+00:00', 'prepare historical Deep authority H',
        )

        dossier_current = copy.deepcopy(dossier_old)
        dossier_current['generated_at_utc'] = '2026-09-27T13:01:00Z'
        raw_current = (
            json.dumps(
                dossier_current,
                ensure_ascii=False,
                sort_keys=True,
                separators=(',', ':'),
            ) + '\n'
        ).encode('utf-8')
        manifest_current = copy.deepcopy(manifest_old)
        current_item = manifest_current['items'][0]
        current_digest = hashlib.sha256(raw_current).hexdigest()
        current_item['dossier_content_sha256'] = current_digest
        current_item['authorization_id'] = progressive_pass2.authorization_id(
            current_item,
            current_digest,
            current_item['dossier_compatibility_binding'],
            work_mode=current_item['work_mode'],
            recovery_authorization_id=current_item['recovery_authorization_id'],
        )
        current_prefix = (
            f"{current_item['semantic_generation_id'][:16]}--"
            f"{current_item['work_id']}--{current_item['authorization_id']}"
        )
        current_item['result_submission_path'] = (
            f'data/ai_inbox/progressive_pass2/results/{current_prefix}.json'
        )
        current_item['terminal_execution_submission_path'] = (
            f'data/ai_inbox/progressive_pass2/execution_receipts/{current_prefix}.json'
        )
        async_regression.write_json(repo / old_item['dossier_path'], dossier_current)
        async_regression.write_json(
            repo / 'data/production/pre_ai/progressive_pass2_work.json',
            manifest_current,
        )
        async_regression.git(repo, 'add', '.')
        current = async_regression.commit(
            repo, 'prepare current Deep authority C',
            '2026-09-27T13:01:00+00:00',
        )

        # V2 has no authority field: GitHub selects C because C is the marker parent.
        marker_path, marker_doc = v2_marker(repo, 'd' * 32)
        assert 'observed_main_commit' not in marker_doc
        assert 'progressive_pass2_work_blob_sha' not in marker_doc
        async_regression.git(repo, 'add', marker_path.relative_to(repo).as_posix())
        anchor = async_regression.commit(
            repo, 'Deep V2 marker selects current C',
            '2026-09-27T13:02:00+00:00',
        )
        receipt = process_markers(repo)[0]
        assert receipt['status'] == 'confirmed', receipt
        assert receipt['run_start_authority_commit'] == current
        assert receipt['run_start_authority_commit'] != historical
        persist_confirmation(repo, '2026-09-27T13:03:00+00:00')

        # An old valid-looking H item cannot be revived under C's marker/receipt.
        stale = pass2_core.fit_result(old_item)
        stale.update({
            'run_start_anchor_commit': anchor,
            'run_start_authority_commit': historical,
            'run_started_at_utc': receipt['run_started_at_utc'],
        })
        stale_path = repo / old_item['result_submission_path']
        async_regression.write_json(stale_path, stale)
        async_regression.set_git_identity(
            repo, 'scheduled-worker', 'scheduled-worker@example.invalid'
        )
        async_regression.git(repo, 'add', stale_path.relative_to(repo).as_posix())
        async_regression.commit(
            repo, 'attempt historical Deep authority revival',
            '2026-09-27T13:04:00+00:00',
        )
        try:
            resolve(repo, old_item, stale, manifest_current)
        except ValueError as exc:
            assert (
                'does not match GitHub confirmation' in str(exc)
                or 'does not match exact work item' in str(exc)
                or 'not found' in str(exc)
            )
        else:
            raise AssertionError('historical Deep authority must fail closed')


def missing_confirmation_zero_attempt():
    item, manifest, dossier = async_regression.deep_fixture()
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        async_regression.init_repo(repo)
        authority = write_active_authority(
            repo, item, manifest, dossier,
            '2026-09-27T14:00:00+00:00', 'prepare Deep authority',
        )
        marker_path, _ = v2_marker(repo, 'e' * 32)
        async_regression.git(repo, 'add', marker_path.relative_to(repo).as_posix())
        anchor = async_regression.commit(
            repo, 'Deep V2 marker without confirmation',
            '2026-09-27T14:01:00+00:00',
        )
        result = pass2_core.fit_result(item)
        result.update({
            'run_start_anchor_commit': anchor,
            'run_start_authority_commit': authority,
            'run_started_at_utc': '2026-09-27T14:01:00+00:00',
        })
        path = repo / item['result_submission_path']
        async_regression.write_json(path, result)
        async_regression.git(repo, 'add', path.relative_to(repo).as_posix())
        async_regression.commit(
            repo, 'forbidden pre-confirmation result',
            '2026-09-27T14:02:00+00:00',
        )
        try:
            resolve(repo, item, result, manifest)
        except ValueError as exc:
            assert 'confirmation receipt is missing' in str(exc)
        else:
            raise AssertionError('missing confirmation must not authorize result')
        state, receipts = progressive_pass2.process_result_documents(
            pass2_core.work_doc([]),
            pass2_core.empty_pass2_state(),
            [(path.name, result, None)],
            accepted_at_utc='2026-09-27T14:03:00+00:00',
        )
        assert state['entries'] == {}
        assert receipts[0]['status'] == 'rejected_stale_or_mismatched'


def main():
    concurrent_dossier_success_and_no_substitution()
    unrelated_write_success()
    material_result_binding_mismatch_rejected()
    arbitrary_historical_authority_rejected()
    missing_confirmation_zero_attempt()
    print('progressive Deep parallel frozen start authority regression: ok')


if __name__ == '__main__':
    main()
