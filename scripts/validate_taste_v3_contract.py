import json
from copy import deepcopy

from ingest_taste_results import build_entry, validate_input
from taste_cache_common import (
    ENTRY_CONTRACT,
    TASTE_FACTOR_IDS,
    load_json,
    validate_cache_entry,
)


def expect_value_error(fn, contains):
    try:
        fn()
    except ValueError as exc:
        assert contains in str(exc), (contains, str(exc))
        return
    raise AssertionError(f'Expected ValueError containing {contains!r}')


def fixture():
    key = 'App_999999'
    fingerprint = '1' * 64
    context_sha = '2' * 64
    projection = {
        'current_profile': {'blob_sha': '3' * 40},
        'current_binding': {
            'taste_model_version': 'taste-v3-test',
            'taste_semantics_sha256': '4' * 64,
        },
        'source_mailing_updated_at_utc': '2026-08-30T00:00:00+00:00',
    }
    queue_row = {
        'taste_subject_key': key,
        'appid': '999999',
        'taste_fingerprint': fingerprint,
        'candidate_context_sha256': context_sha,
        'work_required': ['evaluate_taste_fit', 'evaluate_normalized_taste_factors'],
    }
    bindings = {
        'profile_blob_sha': projection['current_profile']['blob_sha'],
        'taste_model_version': projection['current_binding']['taste_model_version'],
        'taste_semantics_sha256': projection['current_binding']['taste_semantics_sha256'],
        'source_mailing_updated_at_utc': projection['source_mailing_updated_at_utc'],
    }
    result = {
        'key': key,
        'appid': '999999',
        'taste_fingerprint': fingerprint,
        'candidate_context_sha256': context_sha,
        'verdict': 'INCLUDE',
        'fit_level': 'strong',
        'reason_code': 'include_strong',
        'positive_evidence': [
            'Active decisions and learnable mastery match the profile.',
            'Progression changes the available play rather than repeating one static loop.',
        ],
        'negative_evidence': [],
        'taste_factors': {
            'gameplay_mastery': 80,
            'development_variety': 65,
            'structure_pacing_direction': 70,
            'identity_hooks': 55,
            'breadth_of_match': 60,
        },
    }
    return projection, queue_row, bindings, result


def main():
    projection, queue_row, bindings, result = fixture()
    queue_by_key = {queue_row['taste_subject_key']: queue_row}
    doc = {'schema_version': 1, 'bindings': bindings, 'results': [result]}

    validated_bindings, validated_results = validate_input(doc, queue_by_key, projection)
    assert validated_bindings == bindings
    assert validated_results == [result]
    assert tuple(result['taste_factors']) == TASTE_FACTOR_IDS

    entry = build_entry(result, bindings, '2026-08-30T00:01:00+00:00')
    contract = load_json(ENTRY_CONTRACT)
    required = contract.get('schema_v3_required_entry_fields') or contract['base_required_entry_fields']
    assert validate_cache_entry(entry, result['key'], required, require_taste_factors=True)
    assert entry['taste_factors'] == result['taste_factors']

    missing_vector = deepcopy(doc)
    missing_vector['results'][0].pop('taste_factors')
    expect_value_error(
        lambda: validate_input(missing_vector, queue_by_key, projection),
        'requires taste_factors',
    )

    missing_factor = deepcopy(doc)
    missing_factor['results'][0]['taste_factors'].pop('breadth_of_match')
    expect_value_error(
        lambda: validate_input(missing_factor, queue_by_key, projection),
        'must contain exactly',
    )

    extra_factor = deepcopy(doc)
    extra_factor['results'][0]['taste_factors']['commercial_value'] = 100
    expect_value_error(
        lambda: validate_input(extra_factor, queue_by_key, projection),
        'must contain exactly',
    )

    out_of_range = deepcopy(doc)
    out_of_range['results'][0]['taste_factors']['gameplay_mastery'] = 101
    expect_value_error(
        lambda: validate_input(out_of_range, queue_by_key, projection),
        'within 0..100',
    )

    # Migration safety: legacy queue rows that do not request normalized factors may
    # still be ingested without the V3 vector until the scheduled migration reaches them.
    legacy_queue = deepcopy(queue_row)
    legacy_queue['work_required'] = ['evaluate_taste_fit']
    legacy_result = deepcopy(result)
    legacy_result.pop('taste_factors')
    legacy_doc = {'schema_version': 1, 'bindings': bindings, 'results': [legacy_result]}
    _, legacy_validated = validate_input(
        legacy_doc,
        {legacy_queue['taste_subject_key']: legacy_queue},
        projection,
    )
    assert legacy_validated == [legacy_result]

    print(json.dumps({
        'status': 'PASS',
        'contract': 'TASTE-SEMANTIC-RESULT-V3',
        'factor_ids': list(TASTE_FACTOR_IDS),
        'valid_vector_persists': True,
        'missing_vector_rejected_when_requested': True,
        'malformed_vector_rejected': True,
        'legacy_migration_fallback_preserved': True,
    }, ensure_ascii=False, indent=2))
    print('TASTE_V3_CONTRACT_VALIDATION=PASS')


if __name__ == '__main__':
    main()
