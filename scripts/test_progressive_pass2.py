import copy
import json
from datetime import datetime, timezone
from pathlib import Path

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
        'entries': {},
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
            'context_only': {'wishlist': False},
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


def incomplete_pass1_entry(binding):
    return {
        **{field: binding[field] for field in progressive_pass1.IDENTITY_FIELDS},
        'pass1_attempted': True,
        'outcome': 'analysis_incomplete',
        'analysis_issue_code': 'insufficient_evidence',
        'accepted_at_utc': '2026-09-21T00:00:00+00:00',
    }


def pass1_state(bindings, families=('game:1', 'game:2')):
    return {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS1-STATE-V1',
        'entries': {
            family: incomplete_pass1_entry(bindings[family])
            for family in families
        },
    }


def empty_pass2_state():
    return {'schema_version': 1, 'contract': 'PROGRESSIVE-PASS2-STATE-V1', 'entries': {}}


def dossier_record(appid, title, binding, *, expires='2026-10-01T00:00:00Z', resolved=True):
    return {
        'path': f'data/cache/taste_steam_review_dossiers/App_{appid}.json',
        'content_sha256': (str(appid)[-1] or 'a') * 64,
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
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS2-WORK-V1',
        'implemented': True,
        'pass2_active': False,
        'items': items,
    }


def result_doc(item, outcome='analyzed_fit', **extra):
    doc = {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS2-RESULT-V1',
        **{field: item[field] for field in progressive_pass2.IMMUTABLE_RESULT_FIELDS},
        'dossier_compatibility_binding': copy.deepcopy(item['dossier_compatibility_binding']),
        'outcome': outcome,
    }
    doc.update(extra)
    return doc


def terminal_doc(item, reason='worker_failure'):
    return {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS2-EXECUTION-RECEIPT-V1',
        **{field: item[field] for field in progressive_pass2.IMMUTABLE_RESULT_FIELDS},
        'dossier_compatibility_binding': copy.deepcopy(item['dossier_compatibility_binding']),
        'execution_status': 'executed_no_accepted_result',
        'execution_started_at_utc': '2026-09-22T10:00:00Z',
        'execution_finished_at_utc': '2026-09-22T10:01:00Z',
        'terminal_reason': reason,
    }


def recompute(bindings, p1_state, p2_state, dossier_map, *, proj=None, ctx=None, q=None):
    proj = proj or projection()
    ctx = ctx or contexts()
    q = q or queue()
    current_binding = {'binding': 'current-v1', 'schema': 'Dossier-V2'}
    return progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=proj,
        queue_rows=q,
        pass1_state_doc=p1_state,
        pass2_state_doc=p2_state,
        current_binding=current_binding,
        dossier_loader=lambda appid: dossier_map.get(str(appid)),
        now=NOW,
    ), current_binding


def main():
    contract = progressive_pass2.load_contract()
    assert contract['implemented'] is True
    assert contract['active'] is False
    assert contract['attempt_budget']['maximum_automatic_attempts_per_semantic_generation_and_work_id'] == 1
    assert contract['attempt_budget']['new_dossier_same_budget_key_resets_attempt'] is False

    ctx = contexts()
    q = queue()
    proj = projection()
    generation, bindings, _ = progressive_pass1.current_bindings(ctx, proj, q)
    p1 = pass1_state(bindings)
    p2 = empty_pass2_state()
    current_binding = {'binding': 'current-v1', 'schema': 'Dossier-V2'}

    # P2CORE-01: without an accepted canonical Dossier, current incomplete items wait
    # and no attempt is consumed.
    none_result = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=proj,
        queue_rows=q,
        pass1_state_doc=p1,
        pass2_state_doc=p2,
        current_binding=current_binding,
        dossier_loader=lambda _appid: None,
        now=NOW,
    )
    assert none_result['counts']['current_analysis_incomplete_count'] == 2
    assert none_result['counts']['dossier_waiting_count'] == 2
    assert none_result['counts']['pass2_eligible_count'] == 0
    assert p2['entries'] == {}

    d1 = dossier_record('1', 'Game 1', current_binding)
    d2 = dossier_record('2', 'Game 2', current_binding)
    dossiers = {'1': d1, '2': d2}

    # P2CORE-02: exact accepted, fresh, compatible Dossier unlocks only the matching
    # current incomplete work identity.
    ready = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=proj,
        queue_rows=q,
        pass1_state_doc=p1,
        pass2_state_doc=p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: dossiers.get(str(appid)),
        now=NOW,
    )
    assert ready['counts']['pass2_eligible_count'] == 2
    assert {item['family_id'] for item in ready['items']} == {'game:1', 'game:2'}
    item1 = next(x for x in ready['items'] if x['family_id'] == 'game:1')
    item2 = next(x for x in ready['items'] if x['family_id'] == 'game:2')
    assert item1['semantic_generation_id'] == generation['semantic_generation_id']
    assert item1['work_id'] == bindings['game:1']['work_id']
    assert item1['appid'] == '1'
    assert item1['dossier_content_sha256'] == d1['content_sha256']
    assert item1['dossier_compatibility_binding'] == current_binding
    assert item1['dossier_expires_at_utc'] == d1['doc']['expires_at_utc']
    assert len(item1['authorization_id']) == 64

    # P2CORE-03: stale, wrong-app, wrong-work, ambiguous/cross-release and binding
    # mismatches all fail closed and consume zero attempts.
    bad_cases = []
    expired = dossier_record('1', 'Game 1', current_binding, expires='2026-09-22T11:00:00Z')
    bad_cases.append(expired)
    wrong_app = dossier_record('9', 'Game 1', current_binding)
    bad_cases.append(wrong_app)
    wrong_title = dossier_record('1', 'Other Game', current_binding)
    bad_cases.append(wrong_title)
    ambiguous = dossier_record('1', 'Game 1', current_binding, resolved=False)
    bad_cases.append(ambiguous)
    wrong_binding = dossier_record('1', 'Game 1', {'binding': 'old', 'schema': 'Dossier-V2'})
    bad_cases.append(wrong_binding)
    wrong_year = dossier_record('1', 'Game 1', current_binding)
    wrong_year['doc']['game_identity']['release_year'] = 2025
    bad_cases.append(wrong_year)
    for bad in bad_cases:
        eligible, _reason = progressive_pass2.dossier_is_eligible(
            binding=bindings['game:1'],
            pass1_entry=p1['entries']['game:1'],
            semantic_input=progressive_pass2._semantic_input(q[0]),
            dossier_record=bad,
            current_binding=current_binding,
            pass2_state_doc=p2,
            now=NOW,
        )
        assert eligible is False
    assert p2['entries'] == {}

    # P2CORE-04/05: work/result identity is exact-bound to generation/work/appid and
    # Dossier SHA/binding. Projection by itself consumes zero attempts.
    assert p2['entries'] == {}
    good_fit = result_doc(
        item1,
        fit_level='strong',
        confidence='high',
        positive_evidence=['candidate-specific dossier-supported gameplay fit'],
        taste_factors=FACTOR_VALUES,
    )
    wrong_hash = copy.deepcopy(good_fit)
    wrong_hash['dossier_content_sha256'] = 'f' * 64
    unchanged, bad_receipts = progressive_pass2.process_result_documents(
        work_doc([item1]),
        p2,
        [(Path(item1['result_submission_path']).name, wrong_hash, None)],
        accepted_at_utc='2026-09-22T12:05:00+00:00',
    )
    assert unchanged == p2
    assert bad_receipts[0]['status'] == 'rejected_invalid_result_no_attempt'

    # P2CORE-06: one accepted exact-bound result consumes exactly one attempt.
    pass2_after_fit, fit_receipts = progressive_pass2.process_result_documents(
        work_doc([item1]),
        p2,
        [(Path(item1['result_submission_path']).name, good_fit, None)],
        accepted_at_utc='2026-09-22T12:06:00+00:00',
    )
    assert fit_receipts[0]['status'] == 'accepted'
    assert pass2_after_fit['entries']['game:1']['pass2_attempted'] is True
    assert pass2_after_fit['entries']['game:1']['attempt_consumption_source'] == 'accepted_result'
    replay_state, replay_receipts = progressive_pass2.process_result_documents(
        work_doc([item1]),
        pass2_after_fit,
        [(Path(item1['result_submission_path']).name, good_fit, None)],
        accepted_at_utc='2026-09-22T12:07:00+00:00',
    )
    assert replay_state == pass2_after_fit
    assert replay_receipts[0]['status'] == 'replay_ignored'

    # P2CORE-07: only a valid exact-bound terminal execution receipt can consume the
    # attempt when no accepted semantic result exists.
    terminal = terminal_doc(item2, 'worker_failure')
    pass2_after_terminal, terminal_receipts, canonical = (
        progressive_pass2.process_terminal_execution_documents(
            work_doc([item2]),
            p2,
            [(Path(item2['terminal_execution_submission_path']).name, terminal, None)],
            accepted_at_utc='2026-09-22T12:08:00+00:00',
            source_sha256_by_name={Path(item2['terminal_execution_submission_path']).name: 'a' * 64},
        )
    )
    assert terminal_receipts[0]['status'] == 'accepted_terminal_execution_receipt'
    assert pass2_after_terminal['entries']['game:2']['pass2_attempted'] is True
    assert pass2_after_terminal['entries']['game:2']['outcome'] == 'analysis_incomplete'
    assert pass2_after_terminal['entries']['game:2']['attempt_consumption_source'] == 'terminal_execution_receipt'
    assert len(canonical) == 1

    invalid_terminal = terminal_doc(item2)
    invalid_terminal['authorization_id'] = '0' * 64
    still_empty, invalid_terminal_receipts, _ = progressive_pass2.process_terminal_execution_documents(
        work_doc([item2]),
        p2,
        [(Path(item2['terminal_execution_submission_path']).name, invalid_terminal, None)],
        accepted_at_utc='2026-09-22T12:08:30+00:00',
    )
    assert still_empty == p2
    assert invalid_terminal_receipts[0]['status'] == 'rejected_invalid_execution_receipt_no_attempt'

    # P2CORE-08: consumed budget prevents automatic re-eligibility even with a new
    # Dossier for the same semantic_generation_id/work_id.
    d1_new = dossier_record('1', 'Game 1', current_binding)
    d1_new['content_sha256'] = '9' * 64
    after_consumed = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=proj,
        queue_rows=q,
        pass1_state_doc=p1,
        pass2_state_doc=pass2_after_fit,
        current_binding=current_binding,
        dossier_loader=lambda appid: {'1': d1_new, '2': d2}.get(str(appid)),
        now=NOW,
    )
    assert 'game:1' not in {x['family_id'] for x in after_consumed['items']}
    assert after_consumed['reasons']['game:1'] == 'pass2_attempt_already_consumed'

    # P2CORE-09: a genuinely new semantic generation/work identity creates a new
    # budget; old PASS 2 state is non-current and does not block it.
    new_proj = projection('profile-B')
    _new_gen, new_bindings, _ = progressive_pass1.current_bindings(ctx, new_proj, q)
    new_p1 = pass1_state(new_bindings)
    new_ready = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=new_proj,
        queue_rows=q,
        pass1_state_doc=new_p1,
        pass2_state_doc=pass2_after_fit,
        current_binding=current_binding,
        dossier_loader=lambda appid: dossiers.get(str(appid)),
        now=NOW,
    )
    assert any(x['family_id'] == 'game:1' for x in new_ready['items'])
    assert new_bindings['game:1']['work_id'] != bindings['game:1']['work_id']

    # P2CORE-10: one invalid item does not roll back or block a valid sibling.
    valid2 = result_doc(
        item2,
        fit_level='moderate',
        confidence='medium',
        positive_evidence=['second candidate has sufficient dossier-supported fit'],
        taste_factors=FACTOR_VALUES,
    )
    malformed1 = copy.deepcopy(good_fit)
    malformed1.pop('authorization_id')
    sibling_state, sibling_receipts = progressive_pass2.process_result_documents(
        work_doc([item1, item2]),
        p2,
        [
            (Path(item1['result_submission_path']).name, malformed1, None),
            (Path(item2['result_submission_path']).name, valid2, None),
        ],
        accepted_at_utc='2026-09-22T12:09:00+00:00',
    )
    assert 'game:1' not in sibling_state['entries']
    assert sibling_state['entries']['game:2']['outcome'] == 'analyzed_fit'
    assert [r['status'] for r in sibling_receipts] == [
        'rejected_invalid_result_no_attempt',
        'accepted',
    ]

    # P2CORE-11: PASS 2 recovery is independent from unrelated PASS 1 not_analyzed
    # work; there is no global PASS 1 completion gate.
    p1_only_first = pass1_state(bindings, families=('game:1',))
    parallel = progressive_pass2.recompute_eligibility(
        context_rows=ctx,
        projection_doc=proj,
        queue_rows=q,
        pass1_state_doc=p1_only_first,
        pass2_state_doc=p2,
        current_binding=current_binding,
        dossier_loader=lambda appid: dossiers.get(str(appid)),
        now=NOW,
    )
    assert [x['family_id'] for x in parallel['items']] == ['game:1']

    # P2CORE-12/13: PASS 1 history is immutable; accepted PASS 2 projection becomes
    # the current state with explicit machine provenance for the read-only UI.
    p1_before = copy.deepcopy(p1)
    projected = progressive_pass2.project_state(bindings['game:1'], pass2_after_fit)
    assert p1 == p1_before
    assert projected['analysis_state'] == 'analyzed_fit'
    assert projected['analysis_resolution_pass'] == 'pass2'
    game = {}
    progressive_personalization.apply_state_fields(game, projected)
    assert game['analysis_resolution_pass'] == 'pass2'
    assert game['pass2_attempted'] is True

    # P2CORE-14: repository activation guards remain off and no production attempt
    # exists in the initialized PASS 2 state/work artifacts.
    persisted_state = json.loads(Path('data/cache/progressive_pass2_state.json').read_text(encoding='utf-8'))
    persisted_work = json.loads(Path('data/production/pre_ai/progressive_pass2_work.json').read_text(encoding='utf-8'))
    personalization_contract = json.loads(
        Path('config/progressive_personalization_contract.json').read_text(encoding='utf-8')
    )
    assert persisted_state['entries'] == {}
    assert persisted_work['pass2_active'] is False
    assert len(persisted_work.get('items') or []) == int(
        (persisted_work.get('scope') or {}).get('pass2_eligible_count') or 0
    )
    assert personalization_contract['phase_b_execution']['pass2_active'] is False
    assert personalization_contract['phase_b_execution']['pass2_implemented'] is True
    assert personalization_contract['phase_c_pass2_design']['active'] is False
    assert personalization_contract['phase_c_pass2_design']['implemented'] is True

    # P2CORE-15: Dossier evidence semantics remain read-only to PASS 2 while the
    # GitHub-owned canonical persistence boundary now invokes the existing Progressive
    # eligibility projection.
    assert contract['eligibility']['canonical_dossier_store'] == 'data/cache/taste_steam_review_dossiers'
    assert contract['eligibility']['buffered_or_worker_candidate_is_accepted_truth'] is False
    assert contract['dossier_integration']['automatic_recompute_after_canonical_dossier_persistence'] == 'active_github_owned'
    assert contract['dossier_integration']['dossier_owned_workflow_modification_in_this_implementation'] is True
    assert contract['dossier_integration']['projection_is_attempt_consumption'] is False

    json.loads(Path('config/progressive_pass2_result_schema.json').read_text(encoding='utf-8'))
    json.loads(Path('config/progressive_pass2_execution_receipt_schema.json').read_text(encoding='utf-8'))
    print('progressive PASS 2 Phase C core regression: ok')


if __name__ == '__main__':
    main()
