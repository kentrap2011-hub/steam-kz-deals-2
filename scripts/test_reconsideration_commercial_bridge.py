import copy
import json

import commercial_reconsideration_bridge as bridge
import play_priority_context
import refine_visual_ranking as refiner
from taste_evidence_contract import current_evidence_contract_sha


def evidence_entry(state, reason='exclude_insufficient'):
    common = {
        'evidence_contract_sha': current_evidence_contract_sha(),
        'verdict': 'EXCLUDE',
        'fit_level': 'below_moderate',
        'reason_code': reason,
        'fit_evidence_state': state,
        'fit_evidence_confidence': 'medium',
        'fit_evidence_basis': ['candidate_information_insufficient'],
        'historical_negative_context': None,
        'candidate_quality_findings': [],
        'negative_analysis_status': 'complete_no_confirmed_negative',
        'negative_findings': [],
    }
    if state == 'reconsiderable':
        common.update({
            'fit_evidence_confidence': 'medium',
            'fit_evidence_basis': ['historical_user_experience', 'later_quality_reputation_reopened_interest'],
            'historical_negative_context': {
                'exposure_depth': 'brief',
                'recency': 'old',
                'reaction': 'non_engagement',
                'later_reopening_evidence': 'quality_reputation',
            },
        })
    if state == 'confirmed_negative':
        common.update({
            'reason_code': 'exclude_direct_conflict',
            'fit_evidence_confidence': 'high',
            'fit_evidence_basis': ['direct_user_current_reaction'],
            'negative_analysis_status': 'complete_with_confirmed_negative',
            'negative_findings': [{
                'evidence_strength': 'strong',
                'personal_relevance': 'confirmed',
                'evidence_origin': 'direct_user_current_reaction',
            }],
        })
    return common


def scenario(decision='БРАТЬ СЕЙЧАС', disposition='INCLUDE', bucket=3):
    return {'disposition': disposition, 'purchase_decision': decision, 'priority_bucket': bucket}


def package_evidence(strict=True):
    return {
        'package_key': 'Sub_42',
        'strict_current_price_savings': strict,
        'comparison_source_aligned': True,
        'covered_visible_game_count': 2,
        'requires_multi_game_intent': True,
        'savings_kzt': 500.0,
    }


def main():
    insufficient = evidence_entry('insufficient')
    wishlist_good = bridge.resolve_bridge(
        taste_entry=insufficient,
        wishlist=True,
        moderate_scenario=scenario(),
    )
    assert wishlist_good and wishlist_good['kind'] == bridge.WISHLIST_GOOD_DEAL
    assert wishlist_good['taste_state_preserved'] is True

    ordinary = bridge.resolve_bridge(
        taste_entry=insufficient,
        wishlist=True,
        moderate_scenario=scenario('МОЖНО БРАТЬ', 'INCLUDE', 5),
    )
    assert ordinary is None

    confirmed = evidence_entry('confirmed_negative', 'exclude_direct_conflict')
    huge_discount = bridge.resolve_bridge(
        taste_entry=confirmed,
        wishlist=True,
        moderate_scenario=scenario(),
        package_evidence=package_evidence(),
    )
    assert huge_discount is None

    nonwishlist = bridge.resolve_bridge(
        taste_entry=insufficient,
        wishlist=False,
        moderate_scenario=scenario(),
    )
    assert nonwishlist is None

    reconsiderable = evidence_entry('reconsiderable', 'exclude_audited_below')
    package_bridge = bridge.resolve_bridge(
        taste_entry=reconsiderable,
        wishlist=False,
        moderate_scenario=scenario('ЛУЧШЕ ЖДАТЬ', 'INCLUDE', 6),
        package_evidence=package_evidence(),
    )
    assert package_bridge and package_bridge['kind'] == bridge.RECONSIDERABLE_FIXED_PACKAGE
    decision, bucket = bridge.effective_purchase_fields(package_bridge, scenario('ЛУЧШЕ ЖДАТЬ', 'INCLUDE', 6))
    assert decision == 'МОЖНО БРАТЬ' and bucket == 5

    package_bad = bridge.resolve_bridge(
        taste_entry=reconsiderable,
        wishlist=False,
        moderate_scenario=scenario('ЛУЧШЕ ЖДАТЬ', 'INCLUDE', 6),
        package_evidence=package_evidence(False),
    )
    assert package_bad is None
    package_commercial_exclude = bridge.resolve_bridge(
        taste_entry=reconsiderable,
        wishlist=False,
        moderate_scenario=scenario('БРАТЬ СЕЙЧАС', 'EXCLUDE', 3),
        package_evidence=package_evidence(True),
    )
    assert package_commercial_exclude is None

    bioshock = evidence_entry('reconsiderable', 'exclude_direct_conflict')
    bioshock_bridge = bridge.resolve_bridge(
        taste_entry=bioshock,
        wishlist=False,
        moderate_scenario=scenario('ЛУЧШЕ ЖДАТЬ', 'INCLUDE', 6),
        package_evidence=package_evidence(True),
    )
    assert bioshock_bridge and bioshock_bridge['kind'] == bridge.RECONSIDERABLE_FIXED_PACKAGE

    highfleet = bridge.resolve_bridge(
        taste_entry=confirmed,
        wishlist=True,
        moderate_scenario=scenario(),
        package_evidence=package_evidence(),
    )
    assert highfleet is None

    positive = copy.deepcopy(insufficient)
    positive.update({'verdict': 'INCLUDE', 'fit_level': 'strong', 'reason_code': 'include_strong', 'fit_evidence_state': 'sufficient', 'fit_evidence_confidence': 'high', 'fit_evidence_basis': ['normalized_taste_factors']})
    assert bridge.resolve_bridge(taste_entry=positive, wishlist=True, moderate_scenario=scenario(), package_evidence=package_evidence()) is None

    # Step-2 role/start is invariant to commercial inputs.
    base_game = {'title': 'High On Life'}
    before = play_priority_context.context_for_game(base_game, {})
    commercial_game = {'title': 'High On Life', 'wishlist': True, 'discount_percent': 99, 'decision': 'БРАТЬ СЕЙЧАС', 'commercial_eligibility_bridge': wishlist_good}
    after = play_priority_context.context_for_game(commercial_game, {})
    assert before == after
    assert after['play_role'] == 'main_full' and after['relative_start_priority'] == 'ordinary'

    # Risks/warnings are data carried beside the bridge, not replaced by it.
    row = {
        'taste_subject_key': 'App_test',
        'context_only': {'wishlist': True},
        'deal_if_moderate': scenario(),
        'commercial_eligibility_bridge': wishlist_good,
        'risks': ['confirmed practical warning'],
    }
    validated = bridge.validate_visual_bridge(row, insufficient)
    assert validated and row['risks'] == ['confirmed practical warning']

    package_row = {
        'taste_subject_key': 'App_bioshock',
        'context_only': {'wishlist': False},
        'deal_if_moderate': scenario('ЛУЧШЕ ЖДАТЬ', 'INCLUDE', 6),
        'commercial_eligibility_bridge': bioshock_bridge,
        'risks': ['package route warning must survive'],
        'risk_provenance': [{'source': 'confirmed_practical'}],
    }
    validated_package = bridge.validate_visual_bridge(package_row, bioshock)
    assert validated_package and package_row['risks'] == ['package route warning must survive']
    assert package_row['risk_provenance'] == [{'source': 'confirmed_practical'}]

    final_game = {
        'fit': 'below_moderate',
        'decision': 'ЛУЧШЕ ЖДАТЬ',
        'priority_bucket': 6,
        'risks': list(package_row['risks']),
        'risk_provenance': list(package_row['risk_provenance']),
    }
    final_bridge = refiner.validated_commercial_bridge(package_row, bioshock)
    assert final_bridge and final_bridge['kind'] == bridge.RECONSIDERABLE_FIXED_PACKAGE
    refiner.apply_fit_adjustment(
        final_game,
        {'rating': 5.0, 'level': 'positive'},
        {},
        bioshock,
        {},
        final_bridge,
    )
    assert final_game['fit'] == 'below_moderate'
    assert refiner.apply_commercial_branch(final_game, package_row, final_bridge) is True
    assert final_game['decision'] == 'МОЖНО БРАТЬ' and final_game['priority_bucket'] == 5
    assert final_game['risks'] == ['package route warning must survive']
    assert final_game['risk_provenance'] == [{'source': 'confirmed_practical'}]

    print(json.dumps({
        'status': 'PASS',
        'wishlist_good_deal_insufficient': True,
        'wishlist_ordinary_insufficient_blocked': True,
        'confirmed_negative_huge_discount_blocked': True,
        'nonwishlist_weak_unchanged': True,
        'reconsiderable_package_purchase_worthy': True,
        'package_without_strict_savings_blocked': True,
        'package_commercial_exclusion_preserved': True,
        'bioshock_v5_reconsiderable_over_legacy_reason': True,
        'highfleet_non_rescuable': True,
        'strong_positive_unchanged': True,
        'role_start_priority_invariant': True,
        'wishlist_risks_preserved': True,
        'package_risk_provenance_preserved': True,
        'final_refinement_preserves_bridge_fit_and_purchase_value': True,
    }, ensure_ascii=False, indent=2))
    print('RECONSIDERATION_COMMERCIAL_BRIDGE_TEST=PASS')


if __name__ == '__main__':
    main()
