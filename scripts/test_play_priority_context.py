import copy
import json
from pathlib import Path

import build_ranking_lookup
import play_priority_context as context
from taste_evidence_contract import current_evidence_contract_sha


def assert_context(title, role, start, taste_entry=None, **extra):
    game = {'title': title, **extra}
    resolved = context.context_for_game(game, taste_entry or {})
    assert resolved['play_role'] == role, (title, resolved)
    assert resolved['relative_start_priority'] == start, (title, resolved)
    return resolved


def confirmed_negative_entry():
    return {
        'evidence_contract_sha': current_evidence_contract_sha(),
        'verdict': 'EXCLUDE',
        'fit_level': 'below_moderate',
        'reason_code': 'exclude_direct_conflict',
        'fit_evidence_state': 'confirmed_negative',
        'fit_evidence_confidence': 'high',
        'fit_evidence_basis': ['direct_user_current_reaction'],
        'historical_negative_context': None,
        'candidate_quality_findings': [],
        'negative_analysis_status': 'complete_with_confirmed_negative',
        'negative_findings': [{
            'evidence_strength': 'strong',
            'personal_relevance': 'confirmed',
            'evidence_origin': 'direct_user_current_reaction',
        }],
    }


def main():
    contract = context.load_contract()
    expected = contract['control_expectations']

    sifu = assert_context('Sifu', 'main_full', 'high')
    high_on_life = assert_context('High On Life', 'main_full', 'ordinary', wishlist=True)
    amnesia = assert_context('Amnesia: The Bunker', 'main_full', 'ordinary')
    terminator = assert_context('Terminator: Resistance', 'main_full', 'ordinary', sale_expiry_urgency='today')
    tails = assert_context('Tails of Iron 2: Whiskers of Winter', 'secondary_palate_cleanser', 'ordinary', fit='strong')
    trine = assert_context('Trine 4: The Nightmare Prince', 'family_coop', 'ordinary')
    tmnt = assert_context('TMNT: Splintered Fate', 'unresolved', 'unresolved')
    highfleet = assert_context('HighFleet', 'unresolved', 'low', confirmed_negative_entry())

    for title, exp in expected.items():
        if title == 'HighFleet':
            got = context.context_for_game({'title': title}, confirmed_negative_entry())
        else:
            got = context.context_for_game({'title': title}, {})
        assert got['play_role'] == exp['play_role'], (title, got, exp)
        assert got['relative_start_priority'] == exp['relative_start_priority'], (title, got, exp)

    # Commercial urgency and wishlist are deliberately invisible to the resolver.
    commercial_variants = [
        {'title': 'High On Life', 'wishlist': False, 'sale_expiry_urgency': 'today', 'discount_percent': 90, 'current_price_rub': 1, 'decision': 'БРАТЬ СЕЙЧАС'},
        {'title': 'High On Life', 'wishlist': True, 'sale_expiry_urgency': 'later_or_unknown', 'discount_percent': 0, 'current_price_rub': 9999, 'decision': 'ЛУЧШЕ ЖДАТЬ'},
    ]
    commercial_results = [context.context_for_game(row, {}) for row in commercial_variants]
    assert commercial_results[0] == commercial_results[1]
    assert commercial_results[0]['relative_start_priority'] == 'ordinary'

    terminator_today = context.context_for_game({'title': 'Terminator: Resistance', 'sale_expiry_urgency': 'today'}, {})
    terminator_later = context.context_for_game({'title': 'Terminator: Resistance', 'sale_expiry_urgency': 'later_or_unknown'}, {})
    assert terminator_today == terminator_later
    assert terminator_today['relative_start_priority'] == 'ordinary'

    # Strong fit can remain a secondary role; role is not a renamed fit score.
    assert tails['play_role'] == 'secondary_palate_cleanser'
    assert tails['relative_start_priority'] == 'ordinary'

    # Family role survives downstream and is not rewritten to a solo/main role.
    visual_game = {
        'title': 'Trine 4',
        'fit': 'strong',
        'priority_rank': 11,
        'total_score': 77.5,
        'personal_score': 44.0,
        'purchase_score': 33.5,
        'score_breakdown': {},
    }
    before_rank_fields = {key: copy.deepcopy(visual_game.get(key)) for key in ('fit', 'priority_rank', 'total_score', 'personal_score', 'purchase_score')}
    assert context.apply_to_game(visual_game, {}) is True
    for key, before in before_rank_fields.items():
        assert visual_game.get(key) == before, (key, before, visual_game.get(key))
    compact = build_ranking_lookup.compact_row(visual_game)
    assert compact['play_role'] == 'family_coop'
    assert compact['relative_start_priority'] == 'ordinary'

    # Franchise history alone stays unresolved, but title-specific evidence can resolve
    # either main or secondary independently; it is a prior, not a hard cap.
    assert tmnt['play_priority_context_source'] == 'weak_prior_only'
    title_specific_main = {
        'title_specific_evidence': True,
        'play_role': 'main_full',
        'play_role_confidence': 'medium',
        'relative_start_priority': 'ordinary',
        'relative_start_priority_confidence': 'medium',
        'provenance': ['title_specific_followup_evidence', 'franchise_history_weak_prior'],
    }
    title_specific_secondary = dict(title_specific_main, play_role='secondary_palate_cleanser')
    assert context.resolve_from_hint(title_specific_main)['play_role'] == 'main_full'
    assert context.resolve_from_hint(title_specific_secondary)['play_role'] == 'secondary_palate_cleanser'

    # Step-1 confirmed negative always wins over any hypothetical high/main hint.
    aggressive_hint = {
        'title_specific_evidence': True,
        'play_role': 'main_full',
        'play_role_confidence': 'high',
        'relative_start_priority': 'high',
        'relative_start_priority_confidence': 'high',
        'provenance': ['hypothetical_title_specific_interest'],
    }
    guarded = context.resolve_from_hint(aggressive_hint, confirmed_negative=True)
    assert guarded['play_role'] == 'unresolved'
    assert guarded['relative_start_priority'] == 'low'
    assert highfleet['relative_start_priority'] != 'high'

    # Uncalibrated candidates stay unresolved instead of being inferred from genre/score.
    unknown = context.context_for_game({'title': 'Unknown Control', 'fit': 'strong', 'total_score': 99, 'wishlist': True}, {})
    assert unknown['play_role'] == 'unresolved'
    assert unknown['relative_start_priority'] == 'unresolved'

    result = {
        'status': 'PASS',
        'contract': contract['contract_id'],
        'controls': {
            'Sifu': [sifu['play_role'], sifu['relative_start_priority']],
            'High On Life': [high_on_life['play_role'], high_on_life['relative_start_priority']],
            'Amnesia: The Bunker': [amnesia['play_role'], amnesia['relative_start_priority']],
            'Terminator: Resistance': [terminator['play_role'], terminator['relative_start_priority']],
            'Tails of Iron 2': [tails['play_role'], tails['relative_start_priority']],
            'Trine 4': [trine['play_role'], trine['relative_start_priority']],
            'TMNT: Splintered Fate': [tmnt['play_role'], tmnt['relative_start_priority']],
            'HighFleet': [highfleet['play_role'], highfleet['relative_start_priority']],
        },
        'wishlist_invariance': True,
        'sale_urgency_invariance': True,
        'strong_fit_secondary_supported': True,
        'family_role_downstream_supported': True,
        'franchise_prior_not_hard_cap': True,
        'confirmed_negative_cannot_be_high': True,
        'ranking_fields_immutable': True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print('PLAY_PRIORITY_CONTEXT_TEST=PASS')


if __name__ == '__main__':
    main()
