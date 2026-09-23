import copy
import json
from datetime import timedelta
from pathlib import Path

import progressive_pass1
import progressive_pass2
import test_progressive_pass2 as core


ROOT = Path('.')
WRITER_GROUP = 'group: taste-steam-review-dossier-canonical-writer'


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def main():
    ctx = core.contexts()
    queue = core.queue()
    projection = core.projection()
    _generation, bindings, _queue_by_family = progressive_pass1.current_bindings(
        ctx, projection, queue
    )
    empty_p1 = core.empty_pass1_state()
    empty_p2 = core.empty_pass2_state()
    current_binding = {'binding': 'current-v1', 'schema': 'Dossier-V2'}
    d1 = core.dossier_record('1', 'Game 1', current_binding)
    d2 = core.dossier_record('2', 'Game 2', current_binding)

    # DEEP-INT-01: accepted Dossier alone is enough for normal Deep first-pass
    # eligibility. Fast/PASS 1 can remain completely untouched.
    normal = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=empty_p1,
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1}.get(str(appid)),
        now=core.NOW,
    )
    assert [item['family_id'] for item in normal['items']] == ['game:1']
    assert normal['items'][0]['work_mode'] == 'normal_first_pass'
    assert normal['reasons']['game:2'] == 'no_canonically_accepted_dossier'

    # DEEP-INT-02: unrelated Fast results, including successful Fast, do not
    # suppress normal Deep work for an identity without authoritative Deep.
    fast_state = {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS1-STATE-V1',
        'entries': {
            'game:1': core.pass1_entry(bindings['game:1'], 'analyzed_fit'),
            'game:2': core.pass1_entry(bindings['game:2'], 'analyzed_not_fit'),
        },
    }
    with_fast = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=fast_state,
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1, '2': d2}.get(str(appid)),
        now=core.NOW,
    )
    assert {item['family_id'] for item in with_fast['items']} == {'game:1', 'game:2'}

    # DEEP-INT-03: transport/buffer presence has no authority; only canonical
    # accepted Dossier truth can unlock work.
    buffered_only = {'1': {'schema': 'transport-only-candidate'}}
    locked = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=fast_state,
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda _appid: None,
        now=core.NOW,
    )
    assert buffered_only
    assert locked['items'] == []
    assert locked['counts']['deep_waiting_for_dossier_count'] == 2

    # DEEP-INT-04: stale/expired/binding-mismatched Dossier truth removes normal
    # authorization without consuming an attempt.
    expired = copy.deepcopy(d1)
    expired['doc']['expires_at_utc'] = (
        core.NOW - timedelta(seconds=1)
    ).isoformat().replace('+00:00', 'Z')
    expiry_result = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=empty_p1,
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': expired}.get(str(appid)),
        now=core.NOW,
    )
    assert expiry_result['items'] == []
    assert expiry_result['reasons']['game:1'] == 'dossier_expired_or_missing_expiry'
    assert empty_p2['entries'] == {}

    wrong_binding = core.dossier_record('1', 'Game 1', {'binding': 'old'})
    compatibility_result = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=empty_p1,
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': wrong_binding}.get(str(appid)),
        now=core.NOW,
    )
    assert compatibility_result['items'] == []
    assert compatibility_result['reasons']['game:1'] == 'dossier_compatibility_binding_mismatch'

    # DEEP-INT-05: exact identity rebinding invalidates old consumed Deep state and
    # establishes a new normal first-pass identity; no retry budget is reused.
    item1 = next(item for item in with_fast['items'] if item['family_id'] == 'game:1')
    completed, receipts = progressive_pass2.process_result_documents(
        core.work_doc([item1]),
        empty_p2,
        [(Path(item1['result_submission_path']).name, core.fit_result(item1), None)],
        accepted_at_utc='2026-09-22T12:10:00+00:00',
    )
    assert receipts[0]['status'] == 'accepted'
    same_identity = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=empty_p1,
        pass2_state_doc=completed,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1, '2': d2}.get(str(appid)),
        now=core.NOW,
    )
    assert 'game:1' not in {item['family_id'] for item in same_identity['items']}
    assert same_identity['reasons']['game:1'] == 'deep_authoritative_completed'

    rebound_projection = core.projection('profile-B')
    rebound = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=rebound_projection,
        queue_rows=queue,
        pass1_state_doc=empty_p1,
        pass2_state_doc=completed,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1, '2': d2}.get(str(appid)),
        now=core.NOW,
    )
    assert any(
        item['family_id'] == 'game:1' and item['work_mode'] == 'normal_first_pass'
        for item in rebound['items']
    )

    # DEEP-INT-06: unresolved consumed Deep leaves the identity recovery-owned;
    # recomputation never emits a blind retry merely because time passes or work
    # is projected again.
    item2 = next(item for item in with_fast['items'] if item['family_id'] == 'game:2')
    unresolved_doc = core.result_doc(
        item2, outcome='analysis_incomplete', issue_code='insufficient_evidence'
    )
    unresolved, unresolved_receipts = progressive_pass2.process_result_documents(
        core.work_doc([item2]),
        empty_p2,
        [(Path(item2['result_submission_path']).name, unresolved_doc, None)],
        accepted_at_utc='2026-09-22T12:11:00+00:00',
    )
    assert unresolved_receipts[0]['status'] == 'accepted'
    first = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=empty_p1,
        pass2_state_doc=unresolved,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1, '2': d2}.get(str(appid)),
        now=core.NOW,
    )
    later = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=empty_p1,
        pass2_state_doc=unresolved,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1, '2': d2}.get(str(appid)),
        now=core.NOW + timedelta(hours=12),
    )
    assert not any(item['family_id'] == 'game:2' for item in first['items'])
    assert not any(item['family_id'] == 'game:2' for item in later['items'])
    assert first['reasons']['game:2'] == 'recovery_owned_fresh_authorization_required'
    assert later['reasons']['game:2'] == 'recovery_owned_fresh_authorization_required'

    # DEEP-INT-07: explicit fresh GitHub recovery authorization is the only route
    # back to recovery work and is one-shot by authorization ID.
    d2_changed = core.dossier_record('2', 'Game 2', current_binding, digest='8' * 64)
    condition = {
        'kind': 'material_dossier_or_evidence_change',
        'value': f"dossier_sha256:{d2_changed['content_sha256']}",
        'semantic_input': progressive_pass2._semantic_input(queue[1]),
    }
    authorized, auth = progressive_pass2.authorize_recovery(
        binding=bindings['game:2'],
        state_doc=unresolved,
        dossier_record=d2_changed,
        current_binding=current_binding,
        recovery_reason='materially_changed_canonically_accepted_dossier_or_evidence',
        recovery_condition_binding=condition,
        authorized_at_utc='2026-09-22T12:12:00+00:00',
    )
    recovery_work = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=empty_p1,
        pass2_state_doc=authorized,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1, '2': d2_changed}.get(str(appid)),
        now=core.NOW,
    )
    recovery_item = next(item for item in recovery_work['items'] if item['family_id'] == 'game:2')
    assert recovery_item['work_mode'] == 'recovery'
    assert recovery_item['recovery_authorization_id'] == auth['recovery_authorization_id']

    recovery_incomplete = core.result_doc(
        recovery_item, outcome='analysis_incomplete', issue_code='evidence_unavailable'
    )
    after_recovery, recovery_receipts = progressive_pass2.process_result_documents(
        core.work_doc([recovery_item]),
        authorized,
        [(Path(recovery_item['result_submission_path']).name, recovery_incomplete, None)],
        accepted_at_utc='2026-09-22T12:13:00+00:00',
    )
    assert recovery_receipts[0]['status'] == 'accepted'
    no_blind_second_recovery = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=empty_p1,
        pass2_state_doc=after_recovery,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1, '2': d2_changed}.get(str(appid)),
        now=core.NOW,
    )
    assert not any(item['family_id'] == 'game:2' for item in no_blind_second_recovery['items'])
    assert no_blind_second_recovery['reasons']['game:2'] == (
        'recovery_owned_fresh_authorization_required'
    )

    # DEEP-INT-08: every canonical eligibility/state writer remains serialized
    # through one GitHub-owned boundary; recovery authorization joins that boundary.
    pass1_workflow = read('.github/workflows/ingest-progressive-pass1.yml')
    dossier_workflow = read('.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml')
    daily_workflow = read('.github/workflows/build-pre-ai-store-snapshot.yml')
    pass2_workflow = read('.github/workflows/ingest-progressive-pass2.yml')
    recovery_workflow = read('.github/workflows/authorize-progressive-pass2-recovery.yml')
    for workflow in (pass1_workflow, dossier_workflow, daily_workflow):
        assert 'python scripts/build_progressive_pass2_work.py' in workflow
        assert 'data/production/pre_ai/progressive_pass2_work.json' in workflow
    for workflow in (
        pass1_workflow, dossier_workflow, daily_workflow, pass2_workflow, recovery_workflow
    ):
        assert WRITER_GROUP in workflow
        assert 'cancel-in-progress: false' in workflow
    assert 'workflow_dispatch:' in recovery_workflow
    assert 'schedule:' not in recovery_workflow

    # DEEP-INT-09: ingest always recomputes current authorization immediately before
    # persistence; worker-supplied work is never treated as control-plane truth.
    pass2_ingest = read('scripts/ingest_progressive_pass2.py')
    assert (
        pass2_ingest.index('work = build_progressive_pass2_work.build_work_document()')
        < pass2_ingest.index('progressive_pass2.process_result_documents(')
    )

    # DEEP-INT-10: repository activation is consistent everywhere while live
    # production state remains allowed to advance after accepted Deep ingest.
    pass2_contract = json.loads(read('config/progressive_pass2_contract.json'))
    pass1_contract = json.loads(read('config/progressive_pass1_contract.json'))
    personalization = json.loads(read('config/progressive_personalization_contract.json'))
    ownership = json.loads(read('config/execution_ownership_contract.json'))
    daily = json.loads(read('config/daily_execution_contract.json'))
    pass2_state = json.loads(read('data/cache/progressive_pass2_state.json'))
    pass2_work = json.loads(read('data/production/pre_ai/progressive_pass2_work.json'))
    assert pass2_contract['active'] is True
    assert pass2_contract['activation_guard']['pass2_active'] is True
    assert pass2_contract['activation_guard']['deep_active'] is True
    assert pass2_contract['activation_guard']['production_execution_authorized'] is True
    assert pass2_contract['activation_guard']['real_backlog_processing_allowed'] is True
    assert pass2_contract['runtime_architecture']['production_execution_authorized'] is True
    assert pass1_contract['pass2']['active'] is True
    assert personalization['phase_b_execution']['pass2_active'] is True
    assert personalization['phase_c_pass2_design']['active'] is True
    assert ownership['progressive_personalization_phase_c_pass2_core']['pass2_active'] is True
    assert ownership['progressive_personalization_phase_c_pass2_core']['production_execution_authorized'] is True
    assert daily['progressive_personalization_phase_a']['pass2_active'] is True
    assert daily['progressive_personalization_phase_b_pass1']['pass2_active'] is True
    assert daily['progressive_personalization_phase_c_pass2']['pass2_active'] is True
    assert pass2_contract['scheduler']['canonical_title'] == 'Progressive Deep Worker'
    assert pass2_contract['scheduler']['matching_task_cardinality'] == 1
    core.assert_persisted_projection_invariants(
        pass2_state,
        pass2_work.get('scope') or {},
        pass2_work.get('items') or [],
    )
    # A consumed unresolved first pass is a legitimate non-empty production state.
    # Regression validation must accept it instead of pinning production to activation-era zero.
    assert unresolved['entries']
    core.assert_persisted_projection_invariants(unresolved, first['counts'], first['items'])

    print('progressive Deep FAST-DOSSIER-DEEP integration regression: ok')


if __name__ == '__main__':
    main()
