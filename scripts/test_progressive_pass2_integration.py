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
    empty_p2 = core.empty_pass2_state()
    current_binding = {'binding': 'current-v1', 'schema': 'Dossier-V2'}
    d1 = core.dossier_record('1', 'Game 1', current_binding)
    d2 = core.dossier_record('2', 'Game 2', current_binding)

    # P2INT-01 / P2INT-03: canonical accepted Dossier + a newly persisted exact
    # PASS 1 incomplete state is sufficient to derive eligible work automatically.
    no_pass1 = core.pass1_state(bindings, families=())
    before = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=no_pass1,
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1}.get(str(appid)),
        now=core.NOW,
    )
    assert before['items'] == []
    after = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=core.pass1_state(bindings, families=('game:1',)),
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1}.get(str(appid)),
        now=core.NOW,
    )
    assert [item['family_id'] for item in after['items']] == ['game:1']

    # P2INT-02: transport/buffer presence has no authority. Only the canonical
    # Dossier loader result can unlock work; failed/unaccepted groups therefore
    # cannot be substituted as accepted truth.
    buffered_only = {'1': {'schema': 'transport-only-candidate'}}
    locked = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=core.pass1_state(bindings, families=('game:1',)),
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda _appid: None,
        now=core.NOW,
    )
    assert buffered_only
    assert locked['items'] == []
    assert locked['reasons']['game:1'] == 'no_canonically_accepted_dossier'

    # P2INT-04: leaving incomplete or changing generation/work identity removes
    # stale authorization instead of carrying it forward.
    analyzed_state = core.pass1_state(bindings, families=('game:1',))
    analyzed_state['entries']['game:1']['outcome'] = 'analyzed_fit'
    analyzed_state['entries']['game:1']['analysis_issue_code'] = None
    left_incomplete = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=analyzed_state,
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1}.get(str(appid)),
        now=core.NOW,
    )
    assert left_incomplete['items'] == []

    new_projection = core.projection('profile-B')
    changed_generation = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=new_projection,
        queue_rows=queue,
        pass1_state_doc=core.pass1_state(bindings, families=('game:1',)),
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1}.get(str(appid)),
        now=core.NOW,
    )
    assert changed_generation['items'] == []

    # P2INT-05: expiry or compatibility changes invalidate authorization. Work
    # also carries exact expiry so the semantic worker can fail closed before run.
    expired = copy.deepcopy(d1)
    expired['doc']['expires_at_utc'] = (
        core.NOW - timedelta(seconds=1)
    ).isoformat().replace('+00:00', 'Z')
    expiry_result = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=core.pass1_state(bindings, families=('game:1',)),
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': expired}.get(str(appid)),
        now=core.NOW,
    )
    assert expiry_result['items'] == []
    assert expiry_result['reasons']['game:1'] == 'dossier_expired_or_missing_expiry'

    wrong_binding = core.dossier_record('1', 'Game 1', {'binding': 'old'})
    compatibility_result = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=core.pass1_state(bindings, families=('game:1',)),
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': wrong_binding}.get(str(appid)),
        now=core.NOW,
    )
    assert compatibility_result['items'] == []
    assert compatibility_result['reasons']['game:1'] == 'dossier_compatibility_binding_mismatch'

    # P2INT-06 / P2INT-07: projection is idempotent, consumes zero attempts, and
    # one invalid sibling does not block another valid sibling.
    p1_both = core.pass1_state(bindings)
    p2_before = copy.deepcopy(empty_p2)
    mixed = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=p1_both,
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': expired, '2': d2}.get(str(appid)),
        now=core.NOW,
    )
    mixed_again = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=projection,
        queue_rows=queue,
        pass1_state_doc=p1_both,
        pass2_state_doc=empty_p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': expired, '2': d2}.get(str(appid)),
        now=core.NOW,
    )
    assert mixed == mixed_again
    assert empty_p2 == p2_before
    assert [item['family_id'] for item in mixed['items']] == ['game:2']
    assert mixed['items'][0]['dossier_expires_at_utc'] == d2['doc']['expires_at_utc']

    # P2INT-08: integration wiring does not alter PASS 1/Dossier semantic state.
    pass1_contract = json.loads(read('config/progressive_pass1_contract.json'))
    dossier_contract = json.loads(read('config/taste_steam_review_dossier_contract.json'))
    assert pass1_contract['worker_strategy']['deep_recovery_allowed'] is False
    assert pass1_contract['attempt_budget']['automatic_pass1_retry'] is False
    assert dossier_contract['checkpointing']['failure_rule'].startswith(
        'invalid_or_failed_group_is_classified_failed'
    )

    # P2INT-09 is an acceptance-time production-state check, not a permanent
    # regression fixture: current group numbers legitimately change on daily rollover.

    # P2INT-10: activation remains off and no attempt exists.
    pass2_contract = json.loads(read('config/progressive_pass2_contract.json'))
    personalization = json.loads(read('config/progressive_personalization_contract.json'))
    ownership = json.loads(read('config/execution_ownership_contract.json'))
    pass2_state = json.loads(read('data/cache/progressive_pass2_state.json'))
    assert pass2_contract['active'] is False
    assert personalization['phase_b_execution']['pass2_active'] is False
    assert personalization['phase_c_pass2_design']['active'] is False
    assert ownership['progressive_personalization_phase_c_pass2_core']['pass2_active'] is False
    assert pass2_state['entries'] == {}

    # P2INT-03/P2INT-05 control-plane proof: every canonical eligibility writer
    # calls the same builder and all eligibility/attempt writers share one
    # serialized boundary. No polling scheduler or second queue owner is added.
    pass1_workflow = read('.github/workflows/ingest-progressive-pass1.yml')
    dossier_workflow = read('.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml')
    daily_workflow = read('.github/workflows/build-pre-ai-store-snapshot.yml')
    pass2_workflow = read('.github/workflows/ingest-progressive-pass2.yml')
    for workflow in (pass1_workflow, dossier_workflow, daily_workflow):
        assert 'python scripts/build_progressive_pass2_work.py' in workflow
        assert 'data/production/pre_ai/progressive_pass2_work.json' in workflow
    for workflow in (pass1_workflow, dossier_workflow, daily_workflow, pass2_workflow):
        assert WRITER_GROUP in workflow
    assert (
        pass1_workflow.index('python scripts/ingest_progressive_pass1.py')
        < pass1_workflow.index('python scripts/build_progressive_pass2_work.py')
    )
    assert (
        dossier_workflow.index('python scripts/ingest_taste_steam_review_dossier_inbox.py')
        < dossier_workflow.index('python scripts/build_progressive_pass2_work.py')
    )
    assert (
        daily_workflow.index('python scripts/build_progressive_pass1_work.py')
        < daily_workflow.index('python scripts/build_progressive_pass2_work.py')
    )

    # P2INT-05 ingest proof: GitHub recomputes authorization from current truth
    # before it accepts submitted result/receipt documents.
    pass2_ingest = read('scripts/ingest_progressive_pass2.py')
    assert (
        pass2_ingest.index('work = build_progressive_pass2_work.build_work_document()')
        < pass2_ingest.index('progressive_pass2.process_result_documents(')
    )

    print('progressive PASS 2 dossier integration regression: ok')


if __name__ == '__main__':
    main()
