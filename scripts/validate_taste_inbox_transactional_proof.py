import json

from process_taste_inbox import build_transactional_proof_checks


def valid_manifest(ai_queue_count):
    return {
        'source_family_count': 1,
        'sale_end_coverage': 1.0,
        'sale_end_missing_count': 0,
        'sale_end_missing_primary_keys': [],
        'complete_family_partition': True,
        'ai_queue_count': ai_queue_count,
        'contract': {
            'missing_sale_end_does_not_exclude_candidate': True,
        },
    }


def base_projection():
    return {
        'complete_coverage': True,
        'safe_cache_hit_count': 6,
        'ai_required_count': 0,
        'entries': {
            'App_1': {
                'status': 'cache_hit',
                'cached_taste': {
                    'verdict': 'INCLUDE',
                },
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
        after_projection=base_projection(),
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
        after_projection=base_projection(),
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
    assert checks['ingested_key_retention_matches_negative_and_base_support_state'] is False
    assert checks['ai_queue_count_exact'] is False
    assert checks['queue_file_count_exact'] is False
    failed = [name for name, ok in checks.items() if not ok]
    assert failed, 'illegal retained taste-required row must fail closed'
    return failed


def main():
    legal = legal_retained_base_support_case()
    illegal_failed = illegal_retained_taste_work_case()
    print(json.dumps({
        'status': 'PASS',
        'legal_retained_base_support_case': all(legal.values()),
        'illegal_retained_taste_work_failed_checks': illegal_failed,
    }, indent=2))
    print('TASTE_INBOX_TRANSACTIONAL_PROOF_VALIDATION=PASS')


if __name__ == '__main__':
    main()
