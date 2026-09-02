import json
from copy import deepcopy

import priority_ranking
from ingest_taste_results import (
    build_full_entry,
    build_negative_only_entry,
    validate_input,
)
from taste_cache_common import (
    ENTRY_CONTRACT,
    TASTE_FACTOR_IDS,
    load_json,
    validate_cache_entry,
)
from taste_negative_contract import (
    negative_readiness,
    structured_grounded_risks,
    validate_negative_analysis,
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
            'taste_model_version': 'taste-v4-test',
            'taste_semantics_sha256': '4' * 64,
        },
        'source_mailing_updated_at_utc': '2026-09-02T00:00:00+00:00',
    }
    queue_row = {
        'taste_subject_key': key,
        'appid': '999999',
        'taste_fingerprint': fingerprint,
        'candidate_context_sha256': context_sha,
        'work_required': [
            'evaluate_taste_fit',
            'evaluate_normalized_taste_factors',
            'resolve_grounded_negative_analysis',
        ],
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
        'negative_analysis_status': 'complete_with_confirmed_negative',
        'negative_findings': [
            {
                'category': 'other_grounded',
                'code': 'other_grounded_taste_risk',
                'evidence': 'A confirmed candidate-specific downside that does not fit the initial taxonomy.',
                'risk_text_ru': 'У игры есть подтверждённый персональный минус, который пока не относится к отдельной категории риска.',
            }
        ],
        'negative_evidence': [
            'A confirmed candidate-specific downside that does not fit the initial taxonomy.'
        ],
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

    validated_bindings, validated_rows = validate_input(doc, queue_by_key, projection, {})
    assert validated_bindings == bindings
    assert len(validated_rows) == 1 and validated_rows[0]['full_eval'] is True
    assert tuple(result['taste_factors']) == TASTE_FACTOR_IDS

    entry = build_full_entry(result, bindings, '2026-09-02T00:01:00+00:00')
    contract = load_json(ENTRY_CONTRACT)
    required = contract['schema_v4_required_entry_fields']
    assert validate_cache_entry(
        entry,
        result['key'],
        required,
        require_taste_factors=True,
        require_v4_negative_fields=True,
    )
    assert negative_readiness(entry)['negative_analysis_ready'] is True

    # Unfamiliar grounded evidence survives because admission uses code/category,
    # not English keyword matching. The escape hatch remains ranking-neutral.
    mapped = structured_grounded_risks(entry)
    assert mapped['other_grounded_taste_risk']['score'] == 0
    assert mapped['other_grounded_taste_risk']['source'] == 'taste_negative_evidence'
    assert mapped['other_grounded_taste_risk']['text'] == result['negative_findings'][0]['risk_text_ru']

    # Legacy free text alone never upgrades negative readiness.
    legacy = deepcopy(entry)
    legacy.pop('negative_analysis_status')
    legacy.pop('negative_findings')
    legacy['negative_evidence'] = ['repetition exists in legacy prose']
    assert negative_readiness(legacy)['negative_analysis_ready'] is False

    expect_value_error(
        lambda: validate_negative_analysis('complete_with_confirmed_negative', [], []),
        'requires at least one',
    )
    expect_value_error(
        lambda: validate_negative_analysis(
            'incomplete_no_confirmed_negative',
            result['negative_findings'],
            result['negative_evidence'],
        ),
        'requires empty findings and evidence',
    )
    invalid_pair = deepcopy(result['negative_findings'])
    invalid_pair[0]['category'] = 'direction'
    expect_value_error(
        lambda: validate_negative_analysis(
            'complete_with_confirmed_negative',
            invalid_pair,
            result['negative_evidence'],
        ),
        'category/code mismatch',
    )
    empty_evidence = deepcopy(result['negative_findings'])
    empty_evidence[0]['evidence'] = '   '
    expect_value_error(
        lambda: validate_negative_analysis(
            'complete_with_confirmed_negative',
            empty_evidence,
            ['   '],
        ),
        'must be a non-empty string',
    )
    empty_risk = deepcopy(result['negative_findings'])
    empty_risk[0]['risk_text_ru'] = ''
    expect_value_error(
        lambda: validate_negative_analysis(
            'complete_with_confirmed_negative',
            empty_risk,
            result['negative_evidence'],
        ),
        'must be a non-empty string',
    )

    incomplete = deepcopy(result)
    incomplete['negative_analysis_status'] = 'incomplete_no_confirmed_negative'
    incomplete['negative_findings'] = []
    incomplete['negative_evidence'] = []
    incomplete_doc = {'schema_version': 1, 'bindings': bindings, 'results': [incomplete]}
    _, incomplete_rows = validate_input(incomplete_doc, queue_by_key, projection, {})
    assert incomplete_rows[0]['result']['negative_analysis_status'] == 'incomplete_no_confirmed_negative'

    # Negative-only work returns only identity + negative fields. Therefore an
    # attempted fit rewrite is rejected before merge; the accepted entry is the base.
    negative_queue = deepcopy(queue_row)
    negative_queue['work_required'] = ['resolve_grounded_negative_analysis']
    negative_result = {
        field: deepcopy(result[field])
        for field in [
            'key', 'appid', 'taste_fingerprint', 'candidate_context_sha256',
            'negative_analysis_status', 'negative_findings', 'negative_evidence',
        ]
    }
    negative_doc = {'schema_version': 1, 'bindings': bindings, 'results': [negative_result]}
    _, negative_rows = validate_input(
        negative_doc,
        {negative_queue['taste_subject_key']: negative_queue},
        projection,
        {result['key']: entry},
    )
    merged = build_negative_only_entry(negative_result, negative_rows[0]['base_entry'])
    for field in [
        'verdict', 'fit_level', 'reason_code', 'positive_evidence', 'taste_factors',
        'profile_blob_sha', 'taste_model_version', 'taste_semantics_sha256',
        'taste_fingerprint', 'candidate_context_sha256', 'evaluated_at_utc',
    ]:
        assert merged[field] == entry[field], field

    attempted_rewrite = deepcopy(negative_doc)
    attempted_rewrite['results'][0]['verdict'] = 'EXCLUDE'
    expect_value_error(
        lambda: validate_input(
            attempted_rewrite,
            {negative_queue['taste_subject_key']: negative_queue},
            projection,
            {result['key']: entry},
        ),
        'attempted to rewrite accepted Taste semantics',
    )

    # Existing normalized-factor scoring remains unchanged.
    policy = priority_ranking.load_final_policy()
    taste_cfg = policy['score_model']['personal']['taste']
    scored = priority_ranking._taste_component(
        {'fit': result['fit_level'], 'taste_factors': result['taste_factors']},
        policy,
    )
    expected_points = round(sum(
        result['taste_factors'][factor_id] / taste_cfg['normalized_scale_max'] * factor_cfg['max_points']
        for factor_id, factor_cfg in taste_cfg['normalized_factor_weights'].items()
    ), policy['score_model']['round_digits'])
    assert scored['source'] == 'normalized_taste_factors'
    assert scored['points'] == expected_points

    missing_vector = deepcopy(doc)
    missing_vector['results'][0].pop('taste_factors')
    expect_value_error(
        lambda: validate_input(missing_vector, queue_by_key, projection, {}),
        'requires taste_factors',
    )

    print(json.dumps({
        'status': 'PASS',
        'contract': 'TASTE-SEMANTIC-RESULT-V4',
        'factor_ids': list(TASTE_FACTOR_IDS),
        'valid_vector_persists': True,
        'configured_score_points': scored['points'],
        'negative_contract_consistency_rejected_when_invalid': True,
        'legacy_fit_reuse_negative_unresolved': True,
        'negative_only_fit_semantics_immutable': True,
        'unfamiliar_structured_finding_survives': True,
        'other_grounded_taste_risk_score': 0,
    }, ensure_ascii=False, indent=2))
    print('TASTE_V4_CONTRACT_VALIDATION=PASS')


if __name__ == '__main__':
    main()
