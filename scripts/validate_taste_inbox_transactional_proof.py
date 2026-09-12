import json

from process_taste_inbox import build_transactional_proof_checks


def valid_manifest(ai_queue_count, deterministically_excluded_primary_keys=None):
    return {
        'source_family_count': 1,
        'sale_end_coverage': 1.0,
        'sale_end_missing_count': 0,
        'sale_end_missing_primary_keys': [],
        'complete_family_partition': True,
        'ai_queue_count': ai_queue_count,
        'deterministically_excluded_primary_keys': deterministically_excluded_primary_keys or [],
        'contract': {
            'missing_sale_end_does_not_exclude_candidate': True,
        },
    }


def projection_for(key='App_1', verdict='INCLUDE', fit_level=None):
    cached_taste = {
        'verdict': verdict,
    }
    if fit_level is not None:
        cached_taste['fit_level'] = fit_level
    return {
        'complete_coverage': True,
        'safe_cache_hit_count': 6,
        'ai_required_count': 0,
        'entries': {
            key: {
                'status': 'cache_hit',
                'cached_taste': cached_taste,
            },
        },
    }


def legal_retained_base_support_case():
    checks, retained, mismatches, expected_queue, full_eval_count = build_transactional_proof_checks(
        all_keys=['App_1'],
        result_by_key={'App_1': {}},
        baseline_queue_by_key={
            'App_1': {
                'taste_subject_key': 'App_1',
                'work_required': ['evaluate_taste_fit', 'resolve_base_support_condition'],
            },
        },
        baseline_safe_hits=5,
        baseline_ai_required=1,
        baseline_ai_queue=1,
        after_projection=projection_for(),
        after_manifest=valid_manifest(1),
        after_queue=[{
            'family_id': 'addon:App_1',
            'taste_subject_key': 'App_1',
            'work_required': ['resolve_base_support_condition'],
        }],
    )
    assert all(checks.values()), checks
    assert retained == {'App_1': ['resolve_base_support_condition']}
    assert mismatches == {}
    assert expected_queue == 1
    assert full_eval_count == 1
    return checks


def final_taste_exclude_drops_stale_base_support_case():
    key = 'App_2336880'
    checks, retained, mismatches, expected_queue, full_eval_count = build_transactional_proof_checks(
        all_keys=[key],
        result_by_key={key: {}},
        baseline_queue_by_key={
            key: {
                'taste_subject_key': key,
                'work_required': ['evaluate_taste_fit', 'resolve_base_support_condition'],
            },
        },
        baseline_safe_hits=5,
        baseline_ai_required=1,
        baseline_ai_queue=1,
        after_projection=projection_for(key=key, verdict='EXCLUDE', fit_level='below_moderate'),
        after_manifest=valid_manifest(0, deterministically_excluded_primary_keys=[key]),
        after_queue=[],
        after_family_graph={
            'families': [{
                'family_id': f'addon:{key}',
                'taste_subject_key': key,
                'primary_key': key,
                'requires_ai_base_support': True,
            }],
        },
        after_deals={
            'entries': {
                key: {
                    'decision_if_strong': {'final_disposition': 'INCLUDE'},
                    'decision_if_moderate': {'final_disposition': 'INCLUDE'},
                },
            },
        },
    )
    assert all(checks.values()), checks
    assert retained == {}
    assert mismatches == {}
    assert expected_queue == 0
    assert full_eval_count == 1
    assert checks['ai_queue_count_exact'] is True
    assert checks['queue_file_count_exact'] is True
    return checks


def post_fit_deal_exclude_drops_negative_case():
    key = 'Sub_87601'
    checks, retained, mismatches, expected_queue, full_eval_count = build_transactional_proof_checks(
        all_keys=[key],
        result_by_key={
            key: {
                'negative_analysis_status': 'incomplete_no_confirmed_negative',
            },
        },
        baseline_queue_by_key={
            key: {
                'taste_subject_key': key,
                'work_required': ['evaluate_taste_fit', 'resolve_grounded_negative_analysis'],
            },
        },
        baseline_safe_hits=5,
        baseline_ai_required=1,
        baseline_ai_queue=1,
        after_projection=projection_for(key=key, verdict='INCLUDE', fit_level='moderate'),
        after_manifest=valid_manifest(0, deterministically_excluded_primary_keys=[key]),
        after_queue=[],
        after_family_graph={
            'families': [{
                'family_id': f'bundle:{key}',
                'taste_subject_key': key,
                'primary_key': key,
                'requires_ai_base_support': False,
            }],
        },
        after_deals={
            'entries': {
                key: {
                    'decision_if_strong': {
                        'final_disposition': 'INCLUDE',
                    },
                    'decision_if_moderate': {
                        'final_disposition': 'EXCLUDE',
                        'price_gate_reason': 'moderate_absolute_budget_ceiling',
                        'exclusion_reason_code': 'price_clearly_unreasonable_after_soft_target_evaluation',
                    },
                },
            },
        },
    )
    assert all(checks.values()), checks
    assert retained == {}
    assert mismatches == {}
    assert expected_queue == 0
    assert full_eval_count == 1
    assert checks['ai_queue_count_exact'] is True
    assert checks['queue_file_count_exact'] is True
    return checks


def pinned_key_removed_from_live_queue_case():
    key = 'App_stale_pinned'
    pinned_row = {
        'taste_subject_key': key,
        'appid': '123',
        'taste_fingerprint': 'a' * 64,
        'candidate_context_sha256': 'b' * 64,
        'work_required': ['evaluate_taste_fit', 'resolve_grounded_negative_analysis'],
    }
    baseline_projection = {
        'complete_coverage': True,
        'safe_cache_hit_count': 5,
        'ai_required_count': 3,
        'entries': {key: {'status': 'not_current_live_work'}},
    }
    after_projection = {
        'complete_coverage': True,
        'safe_cache_hit_count': 5,
        'ai_required_count': 3,
        'entries': {key: {'status': 'not_current_live_work'}},
    }
    after_queue = [
        {'taste_subject_key': 'App_live_1'},
        {'taste_subject_key': 'App_live_2'},
        {'taste_subject_key': 'App_live_3'},
    ]
    checks, retained, mismatches, expected_queue, full_eval_count = build_transactional_proof_checks(
        all_keys=[key],
        result_by_key={key: {}},
        baseline_queue_by_key={key: pinned_row},
        baseline_current_queue_by_key={},
        baseline_safe_hits=5,
        baseline_ai_required=3,
        baseline_ai_queue=3,
        after_projection=after_projection,
        after_manifest=valid_manifest(3),
        after_queue=after_queue,
        baseline_projection=baseline_projection,
        current_reusable_by_key={key: False},
    )
    assert all(checks.values()), checks
    assert retained == {}
    assert mismatches == {}
    assert expected_queue == 3
    assert full_eval_count == 1
    assert checks['older_pinned_result_does_not_become_current_live_cache_hit'] is True
    assert checks['newer_live_work_remains_exact_for_next_work_unit'] is True
    return checks


def illegal_retained_taste_work_case():
    checks, retained, mismatches, expected_queue, full_eval_count = build_transactional_proof_checks(
        all_keys=['App_1'],
        result_by_key={'App_1': {}},
        baseline_queue_by_key={
            'App_1': {
                'taste_subject_key': 'App_1',
                'work_required': ['evaluate_taste_fit'],
            },
        },
        baseline_safe_hits=5,
        baseline_ai_required=1,
        baseline_ai_queue=1,
        after_projection=projection_for(),
        after_manifest=valid_manifest(1),
        after_queue=[{
            'family_id': 'game:1',
            'taste_subject_key': 'App_1',
            'work_required': ['evaluate_taste_fit', 'evaluate_normalized_taste_factors'],
        }],
    )
    assert retained == {}
    assert 'App_1' in mismatches
    assert expected_queue == 0
    assert full_eval_count == 1
    assert checks['ingested_key_retention_matches_negative_base_support_or_newer_live_state'] is False
    assert checks['ai_queue_count_exact'] is False
    assert checks['queue_file_count_exact'] is False
    failed = [name for name, ok in checks.items() if not ok]
    assert failed, 'illegal retained taste-required row must fail closed'
    return failed


def main():
    legal = legal_retained_base_support_case()
    final_exclude = final_taste_exclude_drops_stale_base_support_case()
    deal_exclude = post_fit_deal_exclude_drops_negative_case()
    stale_removed = pinned_key_removed_from_live_queue_case()
    illegal_failed = illegal_retained_taste_work_case()
    print(json.dumps({
        'status': 'PASS',
        'legal_retained_base_support_case': all(legal.values()),
        'final_taste_exclude_drops_stale_base_support_case': all(final_exclude.values()),
        'post_fit_deal_exclude_drops_negative_case': all(deal_exclude.values()),
        'pinned_key_removed_from_live_queue_case': all(stale_removed.values()),
        'illegal_retained_taste_work_failed_checks': illegal_failed,
    }, indent=2))
    print('TASTE_INBOX_TRANSACTIONAL_PROOF_VALIDATION=PASS')


if __name__ == '__main__':
    main()
