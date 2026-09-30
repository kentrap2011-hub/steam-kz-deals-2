import copy
import json
from datetime import datetime, timezone
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

    # Pinned production reconciliation: the three proven 2026-09-30 contract
    # failures are consumed once and may continue only as explicitly authorized
    # recovery work. They must never reappear as fresh normal first-pass work.
    pinned = {
        'game:1353270': {
            'appid': '1353270',
            'work_id': '1379906886119f0bcd8b2d764fa7ce663140ada66a7da03ec1dd08176679773b',
            'recovery_authorization_id': '78a3660c5930d60c03f6b71d97bea1b9575aac496c684ebccd69143b97a18814',
            'prior_result_commit': '6919dcb927526f716e4448d3013eb2c74736e3bb',
        },
        'game:1296770': {
            'appid': '1296770',
            'work_id': 'a349c27f3663446a76886e22218455525bc43a2428278ca450257ad916f6239a',
            'recovery_authorization_id': 'd330d77dcc3803008332a0291baafdf7f842ee878c5e377bf3527f4e77df00f4',
            'prior_result_commit': '57a31a9789673b6e10464c02938b76c4991a6e40',
        },
        'game:1158940': {
            'appid': '1158940',
            'work_id': 'ddb33cb3665250557120ce1deaa1af3f23fe213fd96119e7335f5d17a9c01fe9',
            'recovery_authorization_id': 'c2ef1322b725a4551341e7e013f2949ecba572bc636b313a1e64e64c3950cc19',
            'prior_result_commit': '911e1b1e00fdc5dbed1bff3d9e3f0148a18c58ac',
        },
    }
    production_state = progressive_pass2.load_state()
    for family_id, expected in pinned.items():
        pinned_entry = production_state['entries'][family_id]
        assert pinned_entry['appid'] == expected['appid']
        assert pinned_entry['work_id'] == expected['work_id']
        assert pinned_entry['normal_first_pass_attempted'] is True
        assert pinned_entry['outcome'] == 'analysis_incomplete'
        assert pinned_entry['analysis_issue_code'] == 'terminal_execution_failure'
        assert pinned_entry['attempt_consumption_source'] == 'github_derived_semantic_contract_failure'
        assert pinned_entry['recovery_owned'] is True
        first = pinned_entry['normal_first_pass']
        assert first['semantic_contract_failure_reason'] == 'confirmed personal negative requires high confidence'
        assert first['historical_reconciliation_proof']['prior_result_commit'] == expected['prior_result_commit']
        assert first['historical_reconciliation_proof']['prior_ingest_rejection_commit'] == (
            '5651782bb91a18aaaedc1b26b5973159e3e021d0'
        )
        auth = pinned_entry['recovery_authorization']
        assert auth['status'] == 'authorized'
        assert auth['recovery_authorization_id'] == expected['recovery_authorization_id']
        assert auth['recovery_reason'] == (
            'corrected_runtime_or_validation_defect_material_to_the_prior_failure'
        )
        assert auth['recovery_condition_binding']['defect_fix_binding']['validated_fix_commit'] == (
            'b21bdfd773162e9856c1b12015b1b497b4999363'
        )

    production = progressive_pass2.recompute_eligibility(
        context_rows=progressive_pass1.load_jsonl(progressive_pass1.PROGRESSIVE_CONTEXT),
        projection_doc=progressive_pass2.load_json(progressive_pass1.TASTE_PROJECTION),
        queue_rows=progressive_pass1.load_jsonl(progressive_pass1.TASTE_QUEUE),
        pass1_state_doc=progressive_pass1.load_state(),
        pass2_state_doc=production_state,
        current_binding=progressive_pass2.current_dossier_binding(),
        now=datetime(2026, 9, 30, 6, 50, tzinfo=timezone.utc),
    )
    production_items = {row['family_id']: row for row in production['items']}
    for family_id, expected in pinned.items():
        row = production_items[family_id]
        assert row['work_id'] == expected['work_id']
        assert row['work_mode'] == 'recovery'
        assert row['recovery_authorization_id'] == expected['recovery_authorization_id']
        assert row['recovery_reason'] == (
            'corrected_runtime_or_validation_defect_material_to_the_prior_failure'
        )
        assert production['reasons'][family_id] == 'eligible_recovery_authorization'
    assert not any(
        row['family_id'] in pinned and row['work_mode'] == 'normal_first_pass'
        for row in production['items']
    )

    traversal = contract['invocation_traversal']
    assert traversal['prior_sibling_ingest_required'] is False
    assert traversal['prior_sibling_attempt_advancement_required'] is False
    assert 'do not wait for GitHub ingest' in prompt
    assert 'canonical acceptance is **pending/unverified**' in prompt
    assert 'never block sibling semantic traversal' in prompt

    print('DEEP_INVALID_NOT_FIT_CONTRACT_LOOP=PASS')


if __name__ == '__main__':
    main()
