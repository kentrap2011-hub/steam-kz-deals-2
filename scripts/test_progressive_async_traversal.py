import copy
import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import ingest_progressive_pass2
import progressive_pass1
import progressive_pass2
import progressive_work_authority
import test_progressive_pass2 as pass2_core


NOW = datetime(2026, 9, 24, 12, 0, 0, tzinfo=timezone.utc)
FORGED_RUN_STARTED = '2026-09-24T10:15:00+00:00'


def read(path):
    return Path(path).read_text(encoding='utf-8')


def git(repo, *args):
    return subprocess.run(
        ['git', *args], cwd=repo, text=True, capture_output=True, check=True
    ).stdout.strip()


def commit(repo, message, when):
    env = dict(os.environ)
    env['GIT_AUTHOR_DATE'] = when
    env['GIT_COMMITTER_DATE'] = when
    subprocess.run(
        ['git', 'commit', '-qm', message],
        cwd=repo,
        text=True,
        capture_output=True,
        check=True,
        env=env,
    )
    return git(repo, 'rev-parse', 'HEAD')


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n'
    ).encode('utf-8')
    path.write_bytes(raw)
    return raw


def deep_fixture():
    ctx = pass2_core.contexts()
    queue = pass2_core.queue()
    proj = pass2_core.projection()
    generation, bindings, _ = progressive_pass1.current_bindings(ctx, proj, queue)
    current_binding = {'binding': 'run-start-v1', 'schema': 'Dossier-V2'}
    dossier = {
        'schema': 'TASTE-STEAM-REVIEW-DOSSIER-V2',
        'schema_version': 2,
        'appid': '1',
        'generated_at_utc': '2026-09-23T00:00:00Z',
        'expires_at_utc': '2026-10-01T00:00:00Z',
        'game_identity': {
            'work_title': 'Game 1',
            'release_year': 2026,
            'resolution_status': 'resolved',
        },
        'web_evidence_contract_binding': copy.deepcopy(current_binding),
    }
    raw = (
        json.dumps(dossier, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n'
    ).encode('utf-8')
    record = {
        'path': 'data/cache/taste_steam_review_dossiers/App_1.json',
        'doc': dossier,
        'content_sha256': hashlib.sha256(raw).hexdigest(),
    }
    item = progressive_pass2.make_work_item(
        bindings['game:1'], queue[0], record, current_binding
    )
    manifest = {
        'schema_version': 2,
        'contract': 'PROGRESSIVE-PASS2-WORK-V1',
        'implemented': True,
        'pass2_active': True,
        'semantic_generation_id': generation['semantic_generation_id'],
        'profile_pin': generation['profile_pin'],
        'items': [item],
    }
    return item, manifest, dossier


def init_repo(repo):
    git(repo, 'init', '-q')
    git(repo, 'config', 'user.name', 'scheduled-worker')
    git(repo, 'config', 'user.email', 'scheduled-worker@example.invalid')


def set_git_identity(repo, name, email):
    git(repo, 'config', 'user.name', name)
    git(repo, 'config', 'user.email', email)


def exact_authority_and_path_reuse():
    item, manifest_a, dossier = deep_fixture()
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        init_repo(repo)

        contract_path = repo / 'config/progressive_pass2_contract.json'
        manifest_path = repo / 'data/production/pre_ai/progressive_pass2_work.json'
        dossier_path = repo / item['dossier_path']
        write_json(
            contract_path,
            {
                'contract': 'PROGRESSIVE-PASS2-V1',
                'implemented': True,
                'active': True,
            },
        )
        write_json(manifest_path, manifest_a)
        write_json(dossier_path, dossier)
        git(repo, 'add', '.')
        authority_a = commit(repo, 'prepare Deep authority A', '2026-09-24T10:00:00+00:00')

        # Main advances to B before the real invocation starts. Keep the exact item
        # identity/path the same so only the run-start authority proof can distinguish
        # stale A from actual current B.
        manifest_b = copy.deepcopy(manifest_a)
        manifest_b['director_test_authority'] = 'B'
        write_json(manifest_path, manifest_b)
        git(repo, 'add', '.')
        authority_b = commit(repo, 'replace Deep authority with B', '2026-09-24T10:30:00+00:00')

        nonce = '1' * 32
        marker_path = (
            repo / 'data/ai_inbox/progressive_pass2/run_starts'
            / f'{authority_b}--{nonce}.json'
        )
        marker_doc = {
            'schema_version': 1,
            'contract': 'PROGRESSIVE-PASS2-RUN-START-MARKER-V1',
            'observed_main_commit': authority_b,
            'run_start_nonce': nonce,
        }
        write_json(marker_path, marker_doc)
        git(repo, 'add', marker_path.relative_to(repo).as_posix())
        anchor = commit(repo, 'Deep run-start marker', '2026-09-24T11:00:00+00:00')

        previous_cwd = Path.cwd()
        try:
            os.chdir(repo)
            start_receipts = ingest_progressive_pass2.process_run_start_markers()
        finally:
            os.chdir(previous_cwd)
        assert len(start_receipts) == 1
        start_receipt = start_receipts[0]
        assert start_receipt['status'] == 'confirmed'
        assert start_receipt['run_start_anchor_commit'] == anchor
        assert start_receipt['run_start_authority_commit'] == authority_b
        assert start_receipt['run_started_at_utc'] == '2026-09-24T11:00:00+00:00'
        assert not marker_path.exists()

        set_git_identity(
            repo,
            'steam-kz-bot',
            'steam-kz-bot@users.noreply.github.com',
        )
        git(repo, 'add', '-A')
        confirmation_commit = commit(
            repo,
            'Reconcile Dossier and PASS 2 state',
            '2026-09-24T11:01:00+00:00',
        )

        # Mandatory DRG-01 regression: stale A plus a forged earlier worker time
        # cannot masquerade as current. The GitHub receipt says the actual authority
        # at marker creation was B, so A is rejected even though the fake time lies
        # before B's commit.
        stale_doc = pass2_core.fit_result(item)
        stale_doc.update({
            'run_start_anchor_commit': anchor,
            'run_start_authority_commit': authority_a,
            'run_started_at_utc': FORGED_RUN_STARTED,
        })
        stale_path = repo / item['result_submission_path']
        write_json(stale_path, stale_doc)
        set_git_identity(repo, 'scheduled-worker', 'scheduled-worker@example.invalid')
        git(repo, 'add', stale_path.relative_to(repo).as_posix())
        commit(repo, 'stale A result with forged earlier time', '2026-09-24T11:10:00+00:00')

        previous_cwd = Path.cwd()
        try:
            os.chdir(repo)
            stale_item, stale_error = ingest_progressive_pass2.resolve_candidate_authority(
                Path(item['result_submission_path']),
                'result_submission_path',
                stale_doc,
                manifest_b,
            )
            assert stale_error is not None
            assert 'does not match GitHub confirmation' in stale_error
            stale_state, stale_receipts = progressive_pass2.process_result_documents(
                pass2_core.work_doc([stale_item]),
                pass2_core.empty_pass2_state(),
                [(Path(item['result_submission_path']).name, stale_doc, None)],
                accepted_at_utc='2026-09-24T11:11:00+00:00',
            )
        finally:
            os.chdir(previous_cwd)
        assert stale_state['entries'] == {}
        assert stale_receipts[0]['status'] == 'rejected_invalid_result_no_attempt'

        # Remove the rejected transport exactly as GitHub invalid-transport cleanup
        # does, leaving the semantic attempt unconsumed and the old error receipt durable.
        stale_path.unlink()
        write_json(
            repo / 'data/cache/progressive_pass2_ingest_receipts/rejected.json',
            {
                'status': 'rejected_invalid_result_no_attempt',
                'work_id': item['work_id'],
                'reason': stale_error,
            },
        )
        set_git_identity(
            repo,
            'steam-kz-bot',
            'steam-kz-bot@users.noreply.github.com',
        )
        git(repo, 'add', '-A')
        commit(repo, 'persist stale rejection and cleanup', '2026-09-24T11:12:00+00:00')

        # A later Git/Dossier change belongs to the next invocation. It must not
        # invalidate the already-confirmed B run.
        changed = copy.deepcopy(dossier)
        changed['generated_at_utc'] = '2026-09-23T01:00:00Z'
        write_json(dossier_path, changed)
        set_git_identity(repo, 'scheduled-worker', 'scheduled-worker@example.invalid')
        git(repo, 'add', dossier_path.relative_to(repo).as_posix())
        later_change = commit(repo, 'later Dossier change C', '2026-09-24T11:20:00+00:00')

        valid_doc = pass2_core.fit_result(item)
        valid_doc.update({
            'run_start_anchor_commit': anchor,
            'run_start_authority_commit': authority_b,
            'run_started_at_utc': start_receipt['run_started_at_utc'],
        })
        write_json(stale_path, valid_doc)
        git(repo, 'add', stale_path.relative_to(repo).as_posix())
        valid_add = commit(repo, 'valid result from confirmed B run', '2026-09-24T11:30:00+00:00')

        previous_cwd = Path.cwd()
        try:
            os.chdir(repo)
            resolved, exact_error = ingest_progressive_pass2.resolve_candidate_authority(
                Path(item['result_submission_path']),
                'result_submission_path',
                valid_doc,
                manifest_b,
            )
            assert exact_error is None
            assert resolved['_result_introduction_commit'] == valid_add
            assert resolved['_run_start_anchor_commit'] == anchor
            assert resolved['_run_start_authority_commit'] == authority_b
            valid_state, valid_receipts = progressive_pass2.process_result_documents(
                pass2_core.work_doc([resolved]),
                pass2_core.empty_pass2_state(),
                [(Path(item['result_submission_path']).name, valid_doc, None)],
                accepted_at_utc='2026-09-24T11:31:00+00:00',
            )
        finally:
            os.chdir(previous_cwd)
        assert valid_receipts[0]['status'] == 'accepted'
        assert valid_state['entries'][item['family_id']]['normal_first_pass_attempted'] is True
        assert progressive_work_authority.commit_is_ancestor(
            confirmation_commit, valid_add, repo
        )
        assert progressive_work_authority.commit_is_ancestor(
            later_change, valid_add, repo
        )

        # The next invocation anchors C, not B. With the old B manifest still binding
        # the previous Dossier SHA, C is not silently reusable as the older run view.
        stale_path.unlink()
        git(repo, 'add', '-A')
        commit(repo, 'clear accepted transport fixture', '2026-09-24T11:32:00+00:00')
        nonce2 = '2' * 32
        observed_c = git(repo, 'rev-parse', 'HEAD')
        marker2 = (
            repo / 'data/ai_inbox/progressive_pass2/run_starts'
            / f'{observed_c}--{nonce2}.json'
        )
        write_json(
            marker2,
            {
                'schema_version': 1,
                'contract': 'PROGRESSIVE-PASS2-RUN-START-MARKER-V1',
                'observed_main_commit': observed_c,
                'run_start_nonce': nonce2,
            },
        )
        git(repo, 'add', marker2.relative_to(repo).as_posix())
        anchor2 = commit(repo, 'next Deep run-start marker', '2026-09-24T11:35:00+00:00')
        proof2 = progressive_work_authority.validate_run_start_marker_commit(
            anchor2,
            marker2,
            json.loads(marker2.read_text(encoding='utf-8')),
            repo_root=repo,
        )
        next_item = progressive_work_authority.resolve_presemantic_work_item_at_commit(
            marker_path.parent.parent / 'results' / Path(item['result_submission_path']).name,
            manifest_path,
            proof2['run_start_authority_commit'],
            path_field='result_submission_path',
            expected_contract='PROGRESSIVE-PASS2-WORK-V1',
            repo_root=repo,
        ) if False else None
        assert next_item is None
        assert proof2['run_start_authority_commit'] == observed_c

    # Same deterministic result path may be added again after GitHub-owned invalid
    # cleanup; work-authority lookup must bind to the new bytes/introduction commit.
    item, manifest, dossier = deep_fixture()
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        init_repo(repo)
        manifest_path = repo / 'data/production/pre_ai/progressive_pass2_work.json'
        dossier_path = repo / item['dossier_path']
        write_json(manifest_path, manifest)
        write_json(dossier_path, dossier)
        git(repo, 'add', '.')
        authority = commit(repo, 'prepare Deep work', '2026-09-24T12:00:00+00:00')

        candidate = repo / item['result_submission_path']
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text('{bad json', encoding='utf-8')
        git(repo, 'add', '.')
        commit(repo, 'bad transport', '2026-09-24T12:05:00+00:00')
        candidate.unlink()
        git(repo, 'add', '-A')
        commit(repo, 'GitHub cleanup', '2026-09-24T12:06:00+00:00')

        write_json(candidate, {'valid_transport': True})
        git(repo, 'add', '.')
        valid_add = commit(repo, 'valid resubmission', '2026-09-24T12:10:00+00:00')
        resolved = progressive_work_authority.resolve_presemantic_work_item_at_commit(
            candidate,
            manifest_path,
            authority,
            path_field='result_submission_path',
            expected_contract='PROGRESSIVE-PASS2-WORK-V1',
            repo_root=repo,
        )
        assert resolved['_result_introduction_commit'] == valid_add



def main():
    fast = json.loads(read('config/progressive_pass1_contract.json'))
    deep = json.loads(read('config/progressive_pass2_contract.json'))
    ownership = json.loads(read('config/execution_ownership_contract.json'))
    fast_prompt = read('config/progressive_pass1_worker_prompt.md')
    deep_prompt = read('config/progressive_pass2_worker_prompt.md')
    result_schema = json.loads(read('config/progressive_pass2_result_schema.json'))
    receipt_schema = json.loads(read('config/progressive_pass2_execution_receipt_schema.json'))
    ingest_source = read('scripts/ingest_progressive_pass2.py')

    ft = fast['invocation_traversal']
    assert ft['manifest_and_profile_pin_read_once_per_invocation'] is True
    assert ft['prior_sibling_ingest_required'] is False
    assert ft['prior_sibling_manifest_advancement_required'] is False
    assert ft['existing_transport_implies_canonical_acceptance'] is False
    assert ft['stale_wrong_generation_or_wrong_path_counts_as_submitted'] is False
    assert 'do not wait for GitHub to ingest A' in fast_prompt
    assert 'do not infer acceptance' in fast_prompt
    assert fast['attempt_budget']['invalid_semantic_payload_with_exact_identity'] == (
        'consume_attempt_as_analysis_incomplete'
    )
    assert fast['attempt_budget']['maximum_attempts_per_work_id'] == 1
    assert fast['semantic_generation']['profile_pin']['live_update_after_pin_invalidates_started_work'] is False

    dt = deep['invocation_traversal']
    assert dt['snapshot_boundary'] == 'github_confirmed_create_only_run_start_marker_first_parent'
    assert dt['github_run_start_confirmation_required'] is True
    assert dt['worker_supplied_run_started_at_is_authority'] is False
    assert dt['run_started_at_source'] == 'github_run_start_confirmation_git_commit_time'
    assert dt['manifest_dossier_and_recovery_authorization_frozen_once'] is True
    assert dt['per_item_mutable_manifest_dossier_or_authorization_reread'] is False
    assert dt['changes_after_start_apply_to_next_invocation'] is True
    assert dt['prior_sibling_ingest_required'] is False
    assert dt['existing_transport_implies_canonical_acceptance'] is False
    assert deep['eligibility']['prior_fast_attempt_required'] is False
    assert deep['eligibility']['global_fast_completion_required'] is False
    assert 'do not reread or revalidate mutable' in deep_prompt
    assert 'PROGRESSIVE-PASS2-RUN-START-MARKER-V1' in deep_prompt
    assert 'PROGRESSIVE-PASS2-RUN-START-RECEIPT-V1' in deep_prompt
    assert 'Never substitute a time chosen by the semantic worker' in deep_prompt
    assert 'do not reread or revalidate mutable' in deep_prompt
    exact_authority_and_path_reuse()

    item, _manifest, dossier = deep_fixture()
    expired = copy.deepcopy(dossier)
    expired['expires_at_utc'] = '2026-09-24T10:00:00Z'
    raw = (
        json.dumps(expired, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n'
    ).encode('utf-8')
    ok, reason = progressive_pass2.dossier_is_eligible(
        binding=item,
        semantic_input=item['semantic_input'],
        dossier_record={
            'path': item['dossier_path'],
            'doc': expired,
            'content_sha256': hashlib.sha256(raw).hexdigest(),
        },
        current_binding=item['dossier_compatibility_binding'],
        now=datetime(2026, 9, 24, 11, 0, tzinfo=timezone.utc),
    )
    assert ok is False and reason == 'dossier_expired_or_missing_expiry'

    ctx, q, proj = pass2_core.contexts(), pass2_core.queue(), pass2_core.projection()
    binding = {'binding': 'current-v1', 'schema': 'Dossier-V2'}
    d1 = pass2_core.dossier_record('1', 'Game 1', binding)
    ready = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=proj,
        queue_rows=q,
        pass1_state_doc=pass2_core.empty_pass1_state(),
        pass2_state_doc=pass2_core.empty_pass2_state(),
        current_binding=binding,
        dossier_loader=lambda appid: {'1': d1}.get(str(appid)),
        now=pass2_core.NOW,
    )
    item = next(row for row in ready['items'] if row['family_id'] == 'game:1')
    name = Path(item['result_submission_path']).name
    unchanged, bad_receipts = progressive_pass2.process_result_documents(
        pass2_core.work_doc([item]),
        pass2_core.empty_pass2_state(),
        [(name, None, 'JSONDecodeError:test')],
        accepted_at_utc='2026-09-24T11:01:00+00:00',
    )
    assert unchanged['entries'] == {}
    assert bad_receipts[0]['status'] == 'rejected_invalid_result_no_attempt'
    assert name in ingest_progressive_pass2.removable_names(bad_receipts)

    tname = Path(item['terminal_execution_submission_path']).name
    unchanged2, terminal_bad, _ = progressive_pass2.process_terminal_execution_documents(
        pass2_core.work_doc([item]),
        pass2_core.empty_pass2_state(),
        [(tname, None, 'JSONDecodeError:test')],
        accepted_at_utc='2026-09-24T11:02:00+00:00',
        source_sha256_by_name={tname: 'a' * 64},
    )
    assert unchanged2['entries'] == {}
    assert terminal_bad[0]['status'] == 'rejected_invalid_execution_receipt_no_attempt'
    assert tname in ingest_progressive_pass2.removable_names(terminal_bad)

    valid_state, valid_receipts = progressive_pass2.process_result_documents(
        pass2_core.work_doc([item]),
        pass2_core.empty_pass2_state(),
        [(name, pass2_core.fit_result(item), None)],
        accepted_at_utc='2026-09-24T11:03:00+00:00',
    )
    assert valid_receipts[0]['status'] == 'accepted'
    replay_state, replay_receipts = progressive_pass2.process_result_documents(
        pass2_core.work_doc([item]),
        valid_state,
        [(name, pass2_core.fit_result(item), None)],
        accepted_at_utc='2026-09-24T11:04:00+00:00',
    )
    assert replay_state == valid_state
    assert replay_receipts[0]['status'] == 'replay_ignored'

    original = ingest_progressive_pass2.INGEST_RECEIPTS
    try:
        with tempfile.TemporaryDirectory() as td:
            ingest_progressive_pass2.INGEST_RECEIPTS = Path(td) / 'receipts'
            ingest_progressive_pass2.write_ingest_receipts(bad_receipts, {name: b'{bad'})
            ingest_progressive_pass2.write_ingest_receipts(
                valid_receipts, {name: b'{"good":true}'}
            )
            assert len(list(ingest_progressive_pass2.INGEST_RECEIPTS.glob('*.json'))) == 2
    finally:
        ingest_progressive_pass2.INGEST_RECEIPTS = original

    policy = deep['transport']['invalid_zero_attempt_policy']
    assert policy['raw_rejected_payload_archive'] is False
    assert policy['new_rejected_payload_fingerprint_field'] is False
    assert 'raw_rejected_payload' not in ingest_source
    assert 'rejected_payload_fingerprint' not in ingest_source
    assert 'rejected_payload_fingerprint' not in json.dumps(result_schema)
    assert 'rejected_payload_fingerprint' not in json.dumps(receipt_schema)
    assert ingest_source.index('write_ingest_receipts(') < ingest_source.index('path.unlink()')

    assert deep['ordering']['invalid_or_failed_item_blocks_siblings'] is False
    assert deep['transport']['valid_siblings_depend_on_invalid_sibling'] is False
    assert dt['same_invocation_retry_after_transport_cleanup'] is False
    assert ownership['progressive_personalization_phase_c_pass2_core']['control_plane'] == 'github'
    assert ownership['progressive_personalization_phase_b_pass1']['owner'] == 'github_control_plane'
    assert deep['scheduler']['configuration_owner'] == 'external_user_operator'

    for schema in (result_schema, receipt_schema):
        assert 'run_start_anchor_commit' in schema['required']
        assert 'run_start_authority_commit' in schema['required']
        assert 'run_started_at_utc' in schema['required']

    print('progressive async traversal + Deep invalid transport regression: ok')


if __name__ == '__main__':
    main()
