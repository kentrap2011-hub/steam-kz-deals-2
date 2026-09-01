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
            },
        },
    }


def legal_retained_base_support_case():
    checks, retained, invalid, expected_queue = build_transactional_proof_checks(
        all_keys=['App_1'],
        total_results=1,
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
        family_graph={
            'families': [{
                'family_id': 'addon:App_1',
                'taste_subject_key': 'App_1',
                'requires_ai_base_support': True,
            }],
        },
    )
    assert all(checks.values()), checks
    assert retained == {'App_1'}
    assert invalid == {}
    assert expected_queue == 1
    return checks


def illegal_retained_taste_work_case():
    checks, retained, invalid, expected_queue = build_transactional_proof_checks(
        all_keys=['App_1'],
        total_results=1,
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
        family_graph={
            'families': [{
                'family_id': 'game:1',
                'taste_subject_key': 'App_1',
                'requires_ai_base_support': False,
            }],
        },
    )
    assert retained == set()
    assert 'App_1' in invalid
    assert expected_queue == 0
    assert checks['retained_ingest_keys_are_base_support_only'] is False
    assert checks['ai_queue_decrement_exact'] is False
    assert checks['queue_file_count_exact'] is False
    assert checks['all_ingested_keys_removed_from_queue'] is False
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
