import copy
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import build_progressive_pass1_work
import progressive_pass1
import progressive_pass2
import progressive_personalization


NOW = datetime(2026, 9, 22, 12, 0, 0, tzinfo=timezone.utc)
FACTOR_VALUES = {
    'gameplay_mastery': 80,
    'development_variety': 75,
    'structure_pacing_direction': 70,
    'identity_hooks': 65,
    'breadth_of_match': 72,
}


def projection(profile='profile-A'):
    return {
        'schema_version': 3,
        'status': 'complete',
        'source_mailing_updated_at_utc': 'commercial-A',
        'current_profile': {'blob_sha': profile},
        'current_binding': {
            'taste_model_version': 'taste-v3',
            'taste_semantics_sha256': 'semantics-sha',
            'candidate_context_contract_blob_sha': 'context-contract-blob',
        },
        'entries': {
            'App_1': {'status': 'ai_required', 'taste_fingerprint': 'fp-1', 'candidate_context_sha256': 'ctx-1'},
            'App_2': {'status': 'ai_required', 'taste_fingerprint': 'fp-2', 'candidate_context_sha256': 'ctx-2'},
        },
    }


def contexts():
    return [
        {
            'family_id': f'game:{index}',
            'taste_subject_key': f'App_{index}',
            'purchase': {
                'key': f'App_{index}',
                'title': f'Game {index}',
                'current_price_rub_display': 100,
                'original_price_rub_display': 200,
                'discount_percent': 50,
                'sale_end_utc': '2099-01-01T00:00:00+00:00',
            },
            'history': {'quality': 'unverified', 'minimum_rub_display': None},
            'deal_if_strong': {'disposition': 'INCLUDE'},
            'deal_if_moderate': {'disposition': 'INCLUDE'},
            'context_only': {'wishlist': False},
            'semantic_condition': {
                'ai_condition': 'taste_subject_include_controls_purchase_family',
                'requires_ai_base_support': False,
                'base_appids': [str(index)],
            },
        }
        for index in (1, 2)
    ]


def queue():
    return [
        {
            'family_id': f'game:{index}',
            'taste_subject_key': f'App_{index}',
            'appid': str(index),
            'title': f'Game {index}',
            'taste_fingerprint': f'fp-{index}',
            'candidate_context_sha256': f'ctx-{index}',
            'short_description': f'Candidate-specific description {index}',
            'bundle_members': [],
            'fit_tags': ['Action'],
            'core_fit_count': 1,
            'release_date': '1 Jan, 2026',
            'semantic_condition': {
                'ai_condition': 'taste_subject_include_controls_purchase_family',
                'requires_ai_base_support': False,
                'base_appids': [str(index)],
            },
        }
        for index in (1, 2)
    ]


def empty_pass1_state():
    return {'schema_version': 1, 'contract': 'PROGRESSIVE-PASS1-STATE-V1', 'entries': {}}


def pass1_entry(binding, outcome='analyzed_fit'):
    row = {
        **{field: binding[field] for field in progressive_pass1.IDENTITY_FIELDS},
        'pass1_attempted': True,
        'outcome': outcome,
        'analysis_issue_code': None,
        'accepted_at_utc': '2026-09-21T00:00:00+00:00',
    }
    if outcome == 'analyzed_fit':
        row.update({
            'fit_level': 'strong',
            'confidence': 'high',
            'positive_evidence': ['candidate-specific Fast fit'],
            'taste_factors': copy.deepcopy(FACTOR_VALUES),
        })
    elif outcome == 'analysis_incomplete':
        row['analysis_issue_code'] = 'insufficient_evidence'
    return row


def empty_pass2_state():
    return {'schema_version': 2, 'contract': 'PROGRESSIVE-PASS2-STATE-V2', 'entries': {}}


def dossier_record(appid, title, binding, *, digest=None, expires='2026-10-01T00:00:00Z', resolved=True):
    return {
        'path': f'data/cache/taste_steam_review_dossiers/App_{appid}.json',
        'content_sha256': digest or (str(appid)[-1] * 64),
        'doc': {
            'schema': 'TASTE-STEAM-REVIEW-DOSSIER-V2',
            'schema_version': 2,
            'appid': str(appid),
            'generated_at_utc': '2026-09-21T00:00:00Z',
            'expires_at_utc': expires,
            'game_identity': {
                'work_title': title,
                'release_year': 2026,
                'resolution_status': 'resolved' if resolved else 'ambiguous',
            },
            'web_evidence_contract_binding': copy.deepcopy(binding),
        },
    }


def work_doc(items):
    return {
        'schema_version': 2,
        'contract': 'PROGRESSIVE-PASS2-WORK-V1',
        'implemented': True,
        'pass2_active': False,
        'items': items,
    }


def result_doc(item, outcome='analyzed_fit', **extra):
    doc = {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS2-RESULT-V1',
        **{field: item.get(field) for field in progressive_pass2.IMMUTABLE_RESULT_FIELDS},
        'dossier_compatibility_binding': copy.deepcopy(item['dossier_compatibility_binding']),
        'recovery_condition_binding': copy.deepcopy(item.get('recovery_condition_binding')),
        'outcome': outcome,
    }
    doc.update(extra)
    return doc


def terminal_doc(item, reason='worker_failure'):
    return {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS2-EXECUTION-RECEIPT-V1',
        **{field: item.get(field) for field in progressive_pass2.IMMUTABLE_RESULT_FIELDS},
        'dossier_compatibility_binding': copy.deepcopy(item['dossier_compatibility_binding']),
        'recovery_condition_binding': copy.deepcopy(item.get('recovery_condition_binding')),
        'execution_status': 'executed_no_accepted_result',
        'execution_started_at_utc': '2026-09-22T10:00:00Z',
        'execution_finished_at_utc': '2026-09-22T10:01:00Z',
        'terminal_reason': reason,
    }


def recompute(bindings, p1, p2, dossiers, current_binding, *, proj=None):
    del bindings
    return progressive_pass2.recompute_eligibility(
        context_rows=contexts(),
        projection_doc=proj or projection(),
        queue_rows=queue(),
        pass1_state_doc=p1,
        pass2_state_doc=p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: dossiers.get(str(appid)),
        now=NOW,
    )


def fit_result(item):
    return result_doc(
        item,
        fit_level='strong',
        confidence='high',
        positive_evidence=['candidate-specific dossier-supported gameplay fit'],
        taste_factors=FACTOR_VALUES,
    )


def main():
    contract = progressive_pass2.load_contract()
    assert contract['active'] is False
    assert contract['runtime_architecture']['target_architecture_runtime_adapted'] is True
    assert contract['attempt_budget']['normal_first_pass_attempts_per_deep_identity'] == 1
    assert contract['attempt_budget']['recovery_attempts_share_normal_first_pass_budget'] is False

    ctx, q, proj = contexts(), queue(), projection()
    generation, bindings, _ = progressive_pass1.current_bindings(ctx, proj, q)
    current_binding = {'binding': 'current-v1', 'schema': 'Dossier-V2'}
    d1 = dossier_record('1', 'Game 1', current_binding)
    d2 = dossier_record('2', 'Game 2', current_binding)
    dossiers = {'1': d1, '2': d2}

    # DEEP-01: normal first-pass eligibility does not require any Fast/PASS 1 attempt.
    ready = recompute(bindings, empty_pass1_state(), empty_pass2_state(), dossiers, current_binding)
    assert {x['family_id'] for x in ready['items']} == {'game:1', 'game:2'}
    assert all(x['work_mode'] == 'normal_first_pass' for x in ready['items'])
    assert ready['counts']['deep_total_current_coverage_target'] == 2
    assert ready['counts']['deep_first_pass_attempted_count'] == 0
    item1 = next(x for x in ready['items'] if x['family_id'] == 'game:1')
    item2 = next(x for x in ready['items'] if x['family_id'] == 'game:2')

    # DEEP-02: generation/work rebinding creates a new exact current identity.
    new_proj = projection('profile-B')
    _new_generation, new_bindings, _ = progressive_pass1.current_bindings(ctx, new_proj, q)
    assert new_bindings['game:1']['work_id'] != bindings['game:1']['work_id']
    assert generation['semantic_generation_id'] != _new_generation['semantic_generation_id']

    # DEEP-03: exact accepted, fresh, compatible Dossier is still mandatory.
    missing = recompute(bindings, empty_pass1_state(), empty_pass2_state(), {}, current_binding)
    assert missing['items'] == []
    assert missing['counts']['deep_waiting_for_dossier_count'] == 2
    wrong = dossier_record('9', 'Game 1', current_binding)
    ok, reason = progressive_pass2.dossier_is_eligible(
        binding=bindings['game:1'],
        semantic_input=progressive_pass2._semantic_input(q[0]),
        dossier_record=wrong,
        current_binding=current_binding,
        now=NOW,
    )
    assert ok is False and reason == 'dossier_wrong_appid'

    # DEEP-04/06: invalid artifacts consume no attempt; a consumed unresolved normal
    # first pass is accounted but never re-enters normal first-pass work.
    bad = fit_result(item1)
    bad['dossier_content_sha256'] = 'f' * 64
    unchanged, receipts = progressive_pass2.process_result_documents(
        work_doc([item1]),
        empty_pass2_state(),
        [(Path(item1['result_submission_path']).name, bad, None)],
        accepted_at_utc='2026-09-22T12:01:00+00:00',
    )
    assert unchanged['entries'] == {}
    assert receipts[0]['status'] == 'rejected_invalid_result_no_attempt'

    incomplete = result_doc(item1, outcome='analysis_incomplete', issue_code='insufficient_evidence')
    unresolved, receipts = progressive_pass2.process_result_documents(
        work_doc([item1]),
        empty_pass2_state(),
        [(Path(item1['result_submission_path']).name, incomplete, None)],
        accepted_at_utc='2026-09-22T12:02:00+00:00',
    )
    e1 = unresolved['entries']['game:1']
    assert e1['normal_first_pass_attempted'] is True
    assert e1['authoritative_completed'] is False
    assert e1['recovery_owned'] is True
    again = recompute(bindings, empty_pass1_state(), unresolved, dossiers, current_binding)
    assert not any(x['family_id'] == 'game:1' for x in again['items'])
    assert again['reasons']['game:1'] == 'recovery_owned_fresh_authorization_required'

    # DEEP-07: a valid exact-bound terminal receipt also consumes normal first pass
    # into recovery ownership; no accepted result is fabricated.
    after_terminal, terminal_receipts, canonical = progressive_pass2.process_terminal_execution_documents(
        work_doc([item2]),
        empty_pass2_state(),
        [(Path(item2['terminal_execution_submission_path']).name, terminal_doc(item2), None)],
        accepted_at_utc='2026-09-22T12:03:00+00:00',
        source_sha256_by_name={Path(item2['terminal_execution_submission_path']).name: 'a' * 64},
    )
    assert terminal_receipts[0]['status'] == 'accepted_terminal_execution_receipt'
    assert after_terminal['entries']['game:2']['recovery_owned'] is True
    assert after_terminal['entries']['game:2']['authoritative_completed'] is False
    assert len(canonical) == 1

    # DEEP-08: old consumed state does not block a genuinely new current identity.
    new_ready = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=new_proj,
        queue_rows=q,
        pass1_state_doc=empty_pass1_state(),
        pass2_state_doc=unresolved,
        current_binding=current_binding,
        dossier_loader=lambda appid: dossiers.get(str(appid)),
        now=NOW,
    )
    assert any(x['family_id'] == 'game:1' and x['work_mode'] == 'normal_first_pass' for x in new_ready['items'])

    # DEEP-05/09: materially changed canonical Dossier authorizes exactly one fresh
    # recovery attempt with separate immutable recovery identity.
    d1_new = dossier_record('1', 'Game 1', current_binding, digest='9' * 64)
    condition = {
        'kind': 'material_dossier_or_evidence_change',
        'value': f"dossier_sha256:{d1_new['content_sha256']}",
        'semantic_input': progressive_pass2._semantic_input(q[0]),
    }
    authorized, auth = progressive_pass2.authorize_recovery(
        binding=bindings['game:1'],
        state_doc=unresolved,
        dossier_record=d1_new,
        current_binding=current_binding,
        recovery_reason='materially_changed_canonically_accepted_dossier_or_evidence',
        recovery_condition_binding=condition,
        authorized_at_utc='2026-09-22T12:04:00+00:00',
    )
    recovery_projection = recompute(
        bindings, empty_pass1_state(), authorized, {'1': d1_new, '2': d2}, current_binding
    )
    recovery_item = next(x for x in recovery_projection['items'] if x['family_id'] == 'game:1')
    assert recovery_item['work_mode'] == 'recovery'
    assert recovery_item['recovery_authorization_id'] == auth['recovery_authorization_id']
    assert recovery_projection['counts']['recovery_pending_count'] == 1

    recovery_fit = fit_result(recovery_item)
    completed, receipts = progressive_pass2.process_result_documents(
        work_doc([recovery_item]),
        authorized,
        [(Path(recovery_item['result_submission_path']).name, recovery_fit, None)],
        accepted_at_utc='2026-09-22T12:05:00+00:00',
    )
    assert receipts[0]['status'] == 'accepted'
    assert completed['entries']['game:1']['authoritative_completed'] is True
    assert completed['entries']['game:1']['outcome'] == 'analyzed_fit'
    assert len(completed['entries']['game:1']['recovery_attempts']) == 1

    # DEEP-10: a corrected runtime/validation defect can authorize recovery without
    # pretending that the Dossier changed, but it must carry a concrete defect binding.
    condition2 = {
        'kind': 'explicit_operator_condition',
        'value': 'fix:validator-2026-09-22',
        'semantic_input': progressive_pass2._semantic_input(q[1]),
    }
    technical_auth, technical = progressive_pass2.authorize_recovery(
        binding=bindings['game:2'],
        state_doc=after_terminal,
        dossier_record=d2,
        current_binding=current_binding,
        recovery_reason='corrected_runtime_or_validation_defect_material_to_the_prior_failure',
        recovery_condition_binding=condition2,
        authorized_at_utc='2026-09-22T12:06:00+00:00',
    )
    assert technical['recovery_condition_binding']['value'] == 'fix:validator-2026-09-22'
    technical_work = recompute(
        bindings, empty_pass1_state(), technical_auth, dossiers, current_binding
    )
    assert next(x for x in technical_work['items'] if x['family_id'] == 'game:2')['work_mode'] == 'recovery'

    # DEEP-17: normal-first-pass completeness is distinct from all-authoritative.
    both_consumed = copy.deepcopy(unresolved)
    both_consumed['entries']['game:2'] = copy.deepcopy(after_terminal['entries']['game:2'])
    coverage = recompute(bindings, empty_pass1_state(), both_consumed, dossiers, current_binding)
    assert coverage['counts']['deep_normal_first_pass_complete'] is True
    assert coverage['counts']['deep_all_current_authoritative_complete'] is False
    assert coverage['counts']['deep_normal_first_pass_remaining_count'] == 0
    assert coverage['counts']['deep_remaining_until_all_authoritative_count'] == 2

    # DEEP-11/15: bounded operator recovery entrypoint exists and recomputation hooks
    # remain GitHub-owned/serialized, including recovery authorization persistence.
    auth_script = Path('scripts/authorize_progressive_pass2_recovery.py').read_text(encoding='utf-8')
    auth_workflow = Path('.github/workflows/authorize-progressive-pass2-recovery.yml').read_text(encoding='utf-8')
    assert 'workflow_dispatch:' in auth_workflow
    assert 'group: taste-steam-review-dossier-canonical-writer' in auth_workflow
    assert 'schedule:' not in auth_workflow
    assert 'authorize_recovery(' in auth_script
    for workflow_path in (
        '.github/workflows/ingest-progressive-pass1.yml',
        '.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml',
        '.github/workflows/build-pre-ai-store-snapshot.yml',
        '.github/workflows/ingest-progressive-pass2.yml',
    ):
        text = Path(workflow_path).read_text(encoding='utf-8')
        assert 'python scripts/build_progressive_pass2_work.py' in text or workflow_path.endswith('ingest-progressive-pass2.yml')
        assert 'group: taste-steam-review-dossier-canonical-writer' in text

    # DEEP-16: Dossier statistics observability is non-blocking when its artifact
    # cannot be read.
    original_dossier_work = progressive_pass2.DOSSIER_WORK
    try:
        progressive_pass2.DOSSIER_WORK = Path('/definitely/missing/dossier-work.json')
        metrics = progressive_personalization._dossier_processing_metrics()
        assert metrics['dossier_total_current_scope'] is None
        assert metrics['dossier_observability'].startswith('unavailable:')
    finally:
        progressive_pass2.DOSSIER_WORK = original_dossier_work

    # DEEP-13/14/19 and DEEP-12: producer precedence/stage fields and Fast suppression
    # are validated with exact synthetic current states.
    fast_state = {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS1-STATE-V1',
        'entries': {
            'game:1': pass1_entry(bindings['game:1'], 'analyzed_fit'),
            'game:2': pass1_entry(bindings['game:2'], 'analyzed_fit'),
        },
    }
    deep_not_fit_doc = result_doc(
        item1,
        outcome='analyzed_not_fit',
        confidence='high',
        not_fit_basis='completed_below_threshold',
        not_fit_evidence=['candidate-specific accepted Dossier contradicts durable fit'],
    )
    deep_authoritative_state, _ = progressive_pass2.process_result_documents(
        work_doc([item1]), empty_pass2_state(),
        [(Path(item1['result_submission_path']).name, deep_not_fit_doc, None)],
        accepted_at_utc='2026-09-22T12:07:00+00:00',
    )
    combined_deep = copy.deepcopy(deep_authoritative_state)
    combined_deep['entries']['game:2'] = copy.deepcopy(unresolved['entries']['game:1'])
    # Rebind the unresolved entry to game:2 exact identity.
    for field in progressive_pass1.IDENTITY_FIELDS:
        combined_deep['entries']['game:2'][field] = bindings['game:2'][field]
        combined_deep['entries']['game:2']['normal_first_pass'][field] = bindings['game:2'][field]

    original_paths = {
        'p1_state': progressive_pass1.STATE,
        'p1_queue': progressive_pass1.TASTE_QUEUE,
        'p1_context': progressive_pass1.PROGRESSIVE_CONTEXT,
        'p1_projection': progressive_pass1.TASTE_PROJECTION,
        'p2_state': progressive_pass2.STATE,
        'dossier_work': progressive_pass2.DOSSIER_WORK,
        'deep_work': progressive_pass2.WORK,
    }
    original_binding_loader = progressive_pass2.current_dossier_binding
    original_dossier_loader = progressive_pass2.canonical_dossier_loader
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            p1_state_path = tmp / 'p1.json'
            queue_path = tmp / 'queue.jsonl'
            context_path = tmp / 'context.jsonl'
            projection_path = tmp / 'projection.json'
            p2_state_path = tmp / 'p2.json'
            dossier_work_path = tmp / 'dossier-work.json'
            deep_work_path = tmp / 'deep-work.json'
            p1_state_path.write_text(json.dumps(fast_state), encoding='utf-8')
            queue_path.write_text(''.join(json.dumps(row) + '\n' for row in q), encoding='utf-8')
            context_path.write_text(''.join(json.dumps(row) + '\n' for row in ctx), encoding='utf-8')
            projection_path.write_text(json.dumps(proj), encoding='utf-8')
            p2_state_path.write_text(json.dumps(combined_deep), encoding='utf-8')
            dossier_work_path.write_text(json.dumps({'submission_group_plan': {'groups': []}, 'group_progress': {'groups': []}}), encoding='utf-8')
            deep_work_path.write_text(json.dumps({'items': []}), encoding='utf-8')
            progressive_pass1.STATE = p1_state_path
            progressive_pass1.TASTE_QUEUE = queue_path
            progressive_pass1.PROGRESSIVE_CONTEXT = context_path
            progressive_pass1.TASTE_PROJECTION = projection_path
            progressive_pass2.STATE = p2_state_path
            progressive_pass2.DOSSIER_WORK = dossier_work_path
            progressive_pass2.WORK = deep_work_path
            progressive_pass2.current_dossier_binding = lambda: current_binding
            progressive_pass2.canonical_dossier_loader = lambda appid: dossiers.get(str(appid))

            index = progressive_personalization.build_state_index(
                context_rows=ctx,
                projection_doc=proj,
                taste_entries={},
            )
            assert index['game:1']['analysis_state'] == 'analyzed_not_fit'
            assert index['game:1']['effective_analysis_source'] == 'deep'
            assert index['game:1']['deep_stage_state'] == 'completed'
            assert index['game:2']['analysis_state'] == 'analyzed_fit'
            assert index['game:2']['analysis_semantic_source'] == 'progressive_pass1'
            assert index['game:2']['effective_analysis_source'] == 'fast'
            assert index['game:2']['deep_stage_state'] == 'incomplete_or_recovery'

            # Only authoritative Deep suppresses future Fast; unresolved Deep does not.
            # Remove existing Fast attempts to exercise future work projection.
            p1_state_path.write_text(json.dumps(empty_pass1_state()), encoding='utf-8')
            pass1_work = build_progressive_pass1_work.build_work_document(now=NOW)
            assert pass1_work['scope']['fast_skipped_due_to_authoritative_deep_count'] == 1
            assert {x['family_id'] for x in pass1_work['items']} == {'game:2'}

            game = {}
            progressive_personalization.apply_state_fields(game, index['game:2'])
            for field in (
                'fast_stage_state', 'fast_stage_outcome', 'dossier_stage_state',
                'deep_stage_state', 'deep_stage_outcome', 'deep_recovery_state',
                'effective_analysis_source',
            ):
                assert field in game
    finally:
        progressive_pass1.STATE = original_paths['p1_state']
        progressive_pass1.TASTE_QUEUE = original_paths['p1_queue']
        progressive_pass1.PROGRESSIVE_CONTEXT = original_paths['p1_context']
        progressive_pass1.TASTE_PROJECTION = original_paths['p1_projection']
        progressive_pass2.STATE = original_paths['p2_state']
        progressive_pass2.DOSSIER_WORK = original_paths['dossier_work']
        progressive_pass2.WORK = original_paths['deep_work']
        progressive_pass2.current_dossier_binding = original_binding_loader
        progressive_pass2.canonical_dossier_loader = original_dossier_loader

    # DEEP-18: stage statistics reconcile independently.
    visible = [
        {'id': 'game:2', 'analysis_state': 'analyzed_fit', 'analysis_tier': 1},
    ]
    status = progressive_personalization.build_processing_status(
        index, visible, business_excluded_family_ids={'game:1'}
    )
    progressive_personalization.validate_processing_status(status)
    assert status['fast_total_current_scope'] == 1
    assert status['fast_attempted_count'] == 1
    assert status['deep_total_current_coverage_target'] == 1
    assert status['deep_first_pass_attempted_count'] == 1
    assert status['deep_authoritative_completed_count'] == 0

    # DEEP-20/21: inactive migration/projection state has zero attempts and every
    # activation guard remains off. Work may contain projected items, but projection
    # itself consumes no attempt.
    persisted_state = json.loads(Path('data/cache/progressive_pass2_state.json').read_text(encoding='utf-8'))
    persisted_work = json.loads(Path('data/production/pre_ai/progressive_pass2_work.json').read_text(encoding='utf-8'))
    personalization = json.loads(Path('config/progressive_personalization_contract.json').read_text(encoding='utf-8'))
    ownership = json.loads(Path('config/execution_ownership_contract.json').read_text(encoding='utf-8'))
    assert persisted_state == empty_pass2_state()
    assert persisted_work.get('pass2_active') is False
    assert persisted_work.get('scope', {}).get('deep_first_pass_attempted_count', 0) == 0
    assert contract['active'] is False
    assert personalization['phase_b_execution']['pass2_active'] is False
    assert personalization['phase_c_pass2_design']['active'] is False
    assert ownership['progressive_personalization_phase_c_pass2_core']['pass2_active'] is False

    # DEEP-22: this runtime adaptation does not implement the user-facing stage UI.
    changed_ui_guard = Path('web/progressive-personalization-ui.js').read_text(encoding='utf-8')
    assert 'deep_stage_state' not in changed_ui_guard

    json.loads(Path('config/progressive_pass2_result_schema.json').read_text(encoding='utf-8'))
    json.loads(Path('config/progressive_pass2_execution_receipt_schema.json').read_text(encoding='utf-8'))
    print('progressive Deep runtime adaptation DEEP-01..22: ok')


if __name__ == '__main__':
    main()
