import json
from copy import deepcopy

import ingest_taste_results
import refine_visual_ranking
from taste_evidence_contract import evidence_readiness, validate_fit_evidence_fields
from taste_negative_contract import structured_grounded_risks, validate_negative_analysis


def expect_error(fn, contains):
    try:
        fn()
    except ValueError as exc:
        assert contains in str(exc), (contains, str(exc))
        return
    raise AssertionError(f'Expected ValueError containing {contains!r}')


def base_result(state, confidence, basis, *, reason='exclude_insufficient'):
    return {
        'key': 'App_1', 'appid': '1', 'taste_fingerprint': '1' * 64,
        'candidate_context_sha256': '2' * 64, 'verdict': 'EXCLUDE',
        'fit_level': 'below_moderate', 'reason_code': reason,
        'positive_evidence': [], 'negative_analysis_status': 'incomplete_no_confirmed_negative',
        'negative_findings': [], 'negative_evidence': [],
        'fit_evidence_state': state, 'fit_evidence_confidence': confidence,
        'fit_evidence_basis': basis, 'historical_negative_context': None,
        'candidate_quality_findings': [],
    }


def quality_finding():
    return {
        'category': 'navigation_feedback', 'code': 'opaque_navigation_feedback',
        'evidence': 'Recurring player reports describe unclear action feedback and repeated backtracking.',
        'source': 'recurring_player_complaints', 'recurrence': 'recurring_pattern',
        'personal_relevance': 'unresolved',
        'risk_text_ru': 'Игроки регулярно отмечают непрозрачную обратную связь и возвраты; это требует дополнительной проверки, но не доказывает личный минус.',
    }


def strong_negative(code='felt_technical_burden', category='felt_burden', origin='title_specific_inspection'):
    return {
        'category': category, 'code': code,
        'evidence': 'Direct title-specific inspection produced a strong dry, technical and tedious reaction.',
        'risk_text_ru': 'После прямого просмотра игра ощущается сухой, чрезмерно технической и утомительной.',
        'evidence_origin': origin, 'evidence_strength': 'strong', 'personal_relevance': 'confirmed',
    }


def main():
    haven = base_result('insufficient', 'low', ['candidate_information_insufficient'])
    haven['candidate_quality_findings'] = [quality_finding()]
    validate_fit_evidence_fields(haven)
    assert structured_grounded_risks(haven) == {}

    bioshock = base_result(
        'reconsiderable', 'medium',
        ['historical_user_experience', 'later_quality_reputation_reopened_interest'],
        reason='exclude_direct_conflict',
    )
    bioshock['historical_negative_context'] = {
        'exposure_depth': 'brief', 'recency': 'old', 'reaction': 'non_engagement',
        'later_reopening_evidence': 'quality_reputation',
    }
    validate_fit_evidence_fields(bioshock)
    fit, reason = refine_visual_ranking.direct_fit_cap('strong', {'rating': 3.0}, 'reconsiderable')
    assert fit == 'strong' and 'does_not_hard_cap' in reason

    highfleet = base_result(
        'confirmed_negative', 'high',
        ['direct_user_current_reaction', 'title_specific_inspection'],
        reason='exclude_direct_conflict',
    )
    highfleet['negative_analysis_status'] = 'complete_with_confirmed_negative'
    highfleet['negative_findings'] = [strong_negative()]
    highfleet['negative_evidence'] = [highfleet['negative_findings'][0]['evidence']]
    validate_negative_analysis(highfleet['negative_analysis_status'], highfleet['negative_findings'], highfleet['negative_evidence'], require_v5=True)
    validate_fit_evidence_fields(highfleet)
    risks = structured_grounded_risks(highfleet)
    assert risks['felt_technical_burden']['score'] == 4
    assert refine_visual_ranking.risk_summary(risks)[3] == 'high'

    generic = deepcopy(highfleet['negative_findings'])
    generic[0]['evidence_origin'] = 'generic_feature_hypothesis'
    expect_error(
        lambda: validate_negative_analysis('complete_with_confirmed_negative', generic, [generic[0]['evidence']], require_v5=True),
        'invalid personal-negative evidence origin',
    )

    old_hard = deepcopy(highfleet)
    old_hard['fit_evidence_basis'] = ['historical_user_experience']
    old_hard['negative_findings'][0]['evidence_origin'] = 'historical_user_experience'
    old_hard['historical_negative_context'] = {
        'exposure_depth': 'brief', 'recency': 'old', 'reaction': 'non_engagement',
        'later_reopening_evidence': 'none',
    }
    expect_error(lambda: validate_fit_evidence_fields(old_hard), 'substantial/complete explicit dislike')

    informed = deepcopy(old_hard)
    informed['historical_negative_context'] = {
        'exposure_depth': 'substantial', 'recency': 'recent', 'reaction': 'explicit_dislike',
        'later_reopening_evidence': 'none',
    }
    validate_fit_evidence_fields(informed)

    quality_only = deepcopy(haven)
    validate_fit_evidence_fields(quality_only)
    assert quality_only['candidate_quality_findings']
    assert structured_grounded_risks(quality_only) == {}

    expect_error(
        lambda: ingest_taste_results.validate_noncommercial_quality_text('quality', 'Great only because the discount is 90%'),
        'forbidden commercial evidence fragment',
    )

    legacy_include = {'verdict': 'INCLUDE', 'fit_level': 'moderate', 'reason_code': 'include_moderate', 'negative_evidence': []}
    assert evidence_readiness(legacy_include)['fit_evidence_state'] == 'sufficient'
    legacy_insufficient = {'verdict': 'EXCLUDE', 'fit_level': 'below_moderate', 'reason_code': 'exclude_insufficient', 'negative_evidence': []}
    assert evidence_readiness(legacy_insufficient)['fit_evidence_state'] == 'insufficient'
    legacy_bioshock = {'verdict': 'EXCLUDE', 'fit_level': 'below_moderate', 'reason_code': 'exclude_direct_conflict', 'negative_evidence': ['old attempt']}
    assert evidence_readiness(legacy_bioshock)['fit_evidence_backfill_required'] is True
    legacy_risk = {'verdict': 'INCLUDE', 'fit_level': 'moderate', 'reason_code': 'include_moderate', 'negative_evidence': ['direction unclear']}
    assert evidence_readiness(legacy_risk)['fit_evidence_backfill_required'] is True

    print(json.dumps({
        'status': 'PASS', 'insufficient_not_confirmed_negative': True,
        'reconsiderable_not_confirmed_negative': True,
        'old_shallow_weaker_than_informed_rejection': True,
        'generic_feature_cannot_create_strong_personal_negative': True,
        'candidate_quality_risk_without_personal_dislike': True,
        'highfleet_strong_negative_score': risks['felt_technical_burden']['score'],
        'bioshock_reconsiderable_supported': True, 'haven_moon_insufficient_supported': True,
        'commercial_signals_rejected_from_evidence_state': True,
        'legacy_ambiguous_backfill_required': True,
    }, ensure_ascii=False, indent=2))
    print('TASTE_EVIDENCE_STATE_TEST=PASS')


if __name__ == '__main__':
    main()
