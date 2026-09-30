import copy
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import progressive_pass1
import progressive_pass2
import progressive_work_authority
import test_progressive_pass2 as core


def confirmed_negative_result(item, confidence):
    return core.result_doc(
        item,
        outcome='analyzed_not_fit',
        confidence=confidence,
        not_fit_basis='confirmed_personal_negative',
        not_fit_evidence=['candidate-specific personal negative supported by the frozen Dossier'],
        negative_assessment={
            'status': 'completed',
            'evaluated_candidate_refs': [{'kind': 'observation', 'index': 0}],
            'findings': [
                {
                    'disposition': 'confirmed_personal_risk',
                    'risk_code': 'low_active_gameplay',
                    'text_ru': 'Замороженное досье подтверждает персонально значимый риск.',
                    'evidence_refs': [{'kind': 'observation', 'index': 0}],
                },
            ],
        },
    )


def schema_invariant(schema):
    for rule in schema.get('allOf') or []:
        condition = rule.get('if') or {}
        props = condition.get('properties') or {}
        then = rule.get('then') or {}
        then_props = then.get('properties') or {}
        if (
            (props.get('outcome') or {}).get('const') == 'analyzed_not_fit'
            and (props.get('not_fit_basis') or {}).get('const') == 'confirmed_personal_negative'
            and set(condition.get('required') or []) >= {'outcome', 'not_fit_basis'}
            and (then_props.get('confidence') or {}).get('const') == 'high'
            and 'confidence' in (then.get('required') or [])
        ):
            return True
    return False


def main():
    contract = json.loads(Path('config/progressive_pass2_contract.json').read_text(encoding='utf-8'))
    schema = json.loads(Path('config/progressive_pass2_result_schema.json').read_text(encoding='utf-8'))
    prompt = Path('config/progressive_pass2_worker_prompt.md').read_text(encoding='utf-8')

    # LOOP-01/02/03/04: one explicit canonical confidence invariant and no auto-upgrade.
    assert schema_invariant(schema)
    not_fit = contract['outcomes']['analyzed_not_fit']
    assert not_fit['confirmed_personal_negative_requires_confidence'] == 'high'
    assert not_fit['medium_confidence_confirmed_personal_negative_forbidden'] is True
    assert 'never mechanically rewrite or promote `medium` to `high`' in prompt
    assert 'result object against the canonical result contract' in prompt

    ctx, q, proj = core.contexts(), core.queue(), core.projection()
    _generation, bindings, _queue_by_family = progressive_pass1.current_bindings(ctx, proj, q)
    current_binding = {'binding': 'current-v1', 'schema': 'Dossier-V2'}
    d1 = core.dossier_record('1', 'Game 1', current_binding)
    d2 = core.dossier_record('2', 'Game 2', current_binding)
    d1['doc']['observations'] = [{
        'sentiment': 'negative',
        'summary': 'Candidate-specific low active gameplay evidence.',
    }]
    dossiers = {'1': d1, '2': d2}

    ready = core.recompute(
        bindings,
        core.empty_pass1_state(),
        core.empty_pass2_state(),
        dossiers,
        current_binding,
    )
    item = next(row for row in ready['items'] if row['family_id'] == 'game:1')
    name = Path(item['result_submission_path']).name

    # High is valid when the rest of the evidence contract is satisfied.
    high = confirmed_negative_result(item, 'high')
    high_state, high_receipts = progressive_pass2.process_result_documents(
        core.work_doc([item]),
        core.empty_pass2_state(),
        [(name, high, None)],
        accepted_at_utc='2026-09-30T06:00:00+00:00',
    )
    assert high_receipts[0]['status'] == 'accepted', high_receipts[0]
    assert high_state['entries']['game:1']['confidence'] == 'high'
    assert high_state['entries']['game:1']['outcome'] == 'analyzed_not_fit'

    # Medium is not rewritten to high. Exact-bound semantic execution is consumed
    # as terminal incomplete and enters existing recovery ownership.
    medium = confirmed_negative_result(item, 'medium')
    medium_before = copy.deepcopy(medium)
    failed_state, failed_receipts = progressive_pass2.process_result_documents(
        core.work_doc([item]),
        core.empty_pass2_state(),
        [(name, medium, None)],
        accepted_at_utc='2026-09-30T06:01:00+00:00',
    )
    receipt = failed_receipts[0]
    assert receipt['status'] == 'rejected_semantic_contract_result_attempt_consumed', receipt
    assert receipt['attempt_consumed'] is True
    assert receipt['reason'] == 'confirmed personal negative requires high confidence'
    assert medium == medium_before
    assert medium['confidence'] == 'medium'
    entry = failed_state['entries']['game:1']
    assert entry['normal_first_pass_attempted'] is True
    assert entry['authoritative_completed'] is False
    assert entry['outcome'] == 'analysis_incomplete'
    assert entry['analysis_issue_code'] == 'terminal_execution_failure'
    assert entry['attempt_consumption_source'] == 'github_derived_semantic_contract_failure'
    assert entry['normal_first_pass']['semantic_contract_failure_reason'] == receipt['reason']
    assert entry['recovery_owned'] is True
    assert 'confidence' not in entry

    # The exact work cannot reappear as ordinary first-pass merely because its
    # semantic result was rejected.
    after = core.recompute(
        bindings,
        core.empty_pass1_state(),
        failed_state,
        dossiers,
        current_binding,
    )
    assert not any(row['family_id'] == 'game:1' and row['work_mode'] == 'normal_first_pass' for row in after['items'])
    assert after['reasons']['game:1'] == 'recovery_owned_fresh_authorization_required'

    # Recovery remains GitHub-owned and requires a fresh explicit authorization
    # using the corrected-runtime/validation-defect reason.
    condition = {
        'semantic_input': progressive_pass2._semantic_input(q[0]),
        'defect_fix_binding': 'deep-invalid-not-fit-contract-loop-fix-01-test',
    }
    try:
        progressive_pass2.authorize_recovery(
            binding=bindings['game:1'],
            state_doc=failed_state,
            dossier_record=d1,
            current_binding=current_binding,
            recovery_reason='unsupported_reason',
            recovery_condition_binding=condition,
            authorized_at_utc='2026-09-30T06:02:00+00:00',
        )
        raise AssertionError('unsupported recovery reason was accepted')
    except ValueError as exc:
        assert 'unsupported Deep recovery reason' in str(exc)

    authorized_state, auth = progressive_pass2.authorize_recovery(
        binding=bindings['game:1'],
        state_doc=failed_state,
        dossier_record=d1,
        current_binding=current_binding,
        recovery_reason='corrected_runtime_or_validation_defect_material_to_the_prior_failure',
        recovery_condition_binding=condition,
        authorized_at_utc='2026-09-30T06:02:00+00:00',
    )
    assert auth['status'] == 'authorized'
    recovery_work = core.recompute(
        bindings,
        core.empty_pass1_state(),
        authorized_state,
        dossiers,
        current_binding,
    )
    recovered_item = next(row for row in recovery_work['items'] if row['family_id'] == 'game:1')
    assert recovered_item['work_mode'] == 'recovery'
    assert recovered_item['recovery_authorization_id'] == auth['recovery_authorization_id']
    assert recovered_item['recovery_reason'] == 'corrected_runtime_or_validation_defect_material_to_the_prior_failure'

    # Malformed and wrong-identity transport remains non-attempting.
    malformed_state, malformed_receipts = progressive_pass2.process_result_documents(
        core.work_doc([item]),
        core.empty_pass2_state(),
        [(name, None, 'JSONDecodeError:test')],
        accepted_at_utc='2026-09-30T06:03:00+00:00',
    )
    assert malformed_state['entries'] == {}
    assert malformed_receipts[0]['status'] == 'rejected_invalid_result_no_attempt'
    assert malformed_receipts[0]['attempt_consumed'] is False

    wrong = confirmed_negative_result(item, 'medium')
    wrong['work_id'] = 'f' * 64
    wrong_state, wrong_receipts = progressive_pass2.process_result_documents(
        core.work_doc([item]),
        core.empty_pass2_state(),
        [(name, wrong, None)],
        accepted_at_utc='2026-09-30T06:04:00+00:00',
    )
    assert wrong_state['entries'] == {}
    assert wrong_receipts[0]['status'] == 'rejected_invalid_result_no_attempt'
    assert wrong_receipts[0]['attempt_consumed'] is False

    # Persisted ingest receipts with explicit attempt_consumed protect the same
    # work identity from being authorized as fresh normal work in one ingest pass.
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / 'receipt.json'
        p.write_text(json.dumps({
            'status': 'rejected_semantic_contract_result_attempt_consumed',
            'work_id': item['work_id'],
            'attempt_consumed': True,
        }), encoding='utf-8')
        assert item['work_id'] in progressive_work_authority.consumed_work_ids(Path(tmp))

    traversal = contract['invocation_traversal']
    assert traversal['prior_sibling_ingest_required'] is False
    assert traversal['prior_sibling_attempt_advancement_required'] is False
    assert 'do not wait for GitHub ingest' in prompt
    assert 'canonical acceptance is **pending/unverified**' in prompt
    assert 'never block sibling semantic traversal' in prompt

    print('DEEP_INVALID_NOT_FIT_CONTRACT_LOOP=PASS')


if __name__ == '__main__':
    main()
