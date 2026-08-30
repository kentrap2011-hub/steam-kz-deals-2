import json
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import build_final_visual_payload
import priority_ranking

EXPECTED_ORDER = [
    'sale_expiry_urgency_asc',
    'total_score_desc',
    'title_asc',
]

NOW = datetime(2026, 8, 30, 6, 0, tzinfo=timezone.utc)  # 10:00 Europe/Samara


def game(title, **overrides):
    row = {
        'id': title,
        'title': title,
        'fit': 'strong',
        'source_fit': 'strong',
        'risk_level': 'low',
        'risk_codes': [],
        'wishlist': False,
        'history_quality': 'record',
        'discount_percent': 70,
        'original_price_rub': 1000,
        'current_price_rub': 300,
        'duration_tiebreak_penalty': 0,
        'duration_preference_band': 'unknown',
        'estimated_duration_hours': None,
        'sale_end_utc': '2026-09-05T12:00:00Z',
        'direct_user_evidence': {'level': 'none'},
        'practical': {
            'modern_windows_friction': 'unknown',
            'steam_achievements': True,
            'achievement_quality': 3,
        },
    }
    for key, value in overrides.items():
        if key == 'practical':
            row['practical'].update(value)
        else:
            row[key] = value
    return row


def ranked(rows, policy_path=priority_ranking.POLICY):
    rows = deepcopy(rows)
    rows, order = priority_ranking.apply_final_priority_order(rows, now=NOW, policy_path=policy_path)
    assert order == EXPECTED_ORDER, (order, EXPECTED_ORDER)
    return rows


def titles(rows):
    return [row['title'] for row in rows]


def component(row, section, component_id):
    return next(x for x in row['score_breakdown'][section] if x['id'] == component_id)


def main():
    assert callable(build_final_visual_payload.main)
    policy = priority_ranking.load_final_policy()
    assert priority_ranking.load_final_priority_order() == EXPECTED_ORDER
    assert policy['contract'] == 'FINAL-PRIORITY-RANKING-V2'

    model = policy['score_model']
    assert model['total_max'] == 100
    assert model['personal']['max'] == 60
    assert model['purchase']['max'] == 40
    assert sum(x['max_points'] for x in model['personal']['taste']['normalized_factor_weights'].values()) == 50
    assert model['personal']['wishlist']['max'] == 4
    assert model['personal']['achievements']['max'] == 3
    assert model['personal']['duration']['max'] == 3
    assert model['purchase']['savings']['max'] == 20
    assert model['purchase']['price']['max'] == 12
    assert model['purchase']['history']['max'] == 8

    # Existing cache entries without a factor vector work immediately, but the score is explicitly coarse.
    coarse = ranked([game('coarse')])[0]
    assert coarse['score_breakdown']['precision']['code'] == 'legacy_coarse_fit'
    assert coarse['score_breakdown']['precision']['is_coarse_legacy'] is True
    assert component(coarse, 'personal_components', 'taste')['points'] == 42

    moderate = ranked([game('moderate', fit='moderate', source_fit='moderate')])[0]
    assert component(moderate, 'personal_components', 'taste')['points'] == 34
    assert coarse['total_score'] > moderate['total_score']

    # Exact user rating is the strongest taste-score source and is not double-counted.
    direct = ranked([game('direct', direct_user_evidence={'level': 'positive', 'rating': 4.5})])[0]
    direct_taste = component(direct, 'personal_components', 'taste')
    assert direct_taste['source'] == 'direct_user_rating'
    assert direct_taste['points'] == 45

    # New normalized semantic factors are weight-independent inputs; GitHub applies the configured maxima.
    factor_ids = list(model['personal']['taste']['normalized_factor_weights'])
    perfect_factors = {factor_id: 100 for factor_id in factor_ids}
    detailed = ranked([game('detailed', taste_factors=perfect_factors)])[0]
    detailed_taste = component(detailed, 'personal_components', 'taste')
    assert detailed_taste['source'] == 'normalized_taste_factors'
    assert detailed_taste['points'] == 50
    assert sum(x['points'] for x in detailed_taste['factor_breakdown']) == 50

    # Score breakdown is internally exact and bounded.
    for row in (coarse, moderate, direct, detailed):
        breakdown = row['score_breakdown']
        personal_sum = sum(float(x['points']) for x in breakdown['personal_components'])
        purchase_sum = sum(float(x['points']) for x in breakdown['purchase_components'])
        assert breakdown['personal_score'] == max(0, min(60, round(personal_sum, 1)))
        assert breakdown['purchase_score'] == max(0, min(40, round(purchase_sum, 1)))
        assert breakdown['total_score'] == round(breakdown['personal_score'] + breakdown['purchase_score'], 1)
        assert 0 <= breakdown['total_score'] <= 100
        assert row['total_score'] == breakdown['total_score']

    # Urgency remains outside 100 points and has absolute automatic precedence.
    urgent_low = game(
        'today-low-score',
        fit='moderate',
        source_fit='moderate',
        wishlist=False,
        original_price_rub=730,
        current_price_rub=700,
        history_quality='well_above_history',
        practical={'steam_achievements': False, 'achievement_quality': None},
        duration_preference_band='extreme_length',
        risk_level='high',
        risk_codes=['unchanged_repetition'],
        sale_end_utc='2026-08-30T18:00:00Z',
    )
    later_high = game(
        'later-high-score',
        taste_factors=perfect_factors,
        wishlist=True,
        original_price_rub=6050,
        current_price_rub=50,
        history_quality='record',
        practical={'steam_achievements': True, 'achievement_quality': 5},
        duration_preference_band='preferred_medium',
        sale_end_utc='2026-09-05T18:00:00Z',
    )
    urgency_pair = ranked([later_high, urgent_low])
    assert titles(urgency_pair) == ['today-low-score', 'later-high-score']
    assert urgency_pair[0]['total_score'] < urgency_pair[1]['total_score']
    assert (urgency_pair[0]['priority_vs_next'] or {}).get('deciding_factor_id') == 'sale_expiry_urgency_asc'

    # Inside the same urgency, the visible total score is the real ordering rule.
    same_urgency = ranked([moderate, coarse])
    assert titles(same_urgency) == ['coarse', 'moderate']
    assert (same_urgency[0]['priority_vs_next'] or {}).get('deciding_factor_id') == 'total_score_desc'

    # Wishlist is exactly the configured bounded +4 bonus.
    no_wishlist = ranked([game('no-wishlist')])[0]
    wishlist = ranked([game('wishlist', wishlist=True)])[0]
    assert component(no_wishlist, 'personal_components', 'wishlist')['points'] == 0
    assert component(wishlist, 'personal_components', 'wishlist')['points'] == 4
    assert wishlist['total_score'] - no_wishlist['total_score'] == 4

    # Descriptive risks are small; serious personal and confirmed Windows risks use configured penalties.
    low_risk = ranked([game('low-risk', risk_level='low', risk_codes=['old_design_friction'])])[0]
    medium_risk = ranked([game('medium-risk', risk_level='medium', risk_codes=['management_routine'])])[0]
    high_risk = ranked([game('high-risk', risk_level='high', risk_codes=['unchanged_repetition'])])[0]
    windows_risk = ranked([game('windows-risk', practical={'modern_windows_friction': 'serious_problem'})])[0]
    assert component(low_risk, 'personal_components', 'risk')['points'] == -1
    assert component(medium_risk, 'personal_components', 'risk')['points'] == -3
    assert component(high_risk, 'personal_components', 'risk')['points'] == -10
    assert component(windows_risk, 'personal_components', 'risk')['points'] == -12
    assert high_risk['risk_status']['code'] == 'serious_risk'
    assert high_risk['risk_status']['affects_score'] is True
    assert high_risk['risk_status']['score_penalty'] == 10

    # Lack of achievements is already scored in its own component and must not be counted again as risk.
    no_ach = ranked([game(
        'no-ach',
        risk_level='low',
        risk_codes=['no_steam_achievements'],
        practical={'steam_achievements': False, 'achievement_quality': None},
    )])[0]
    assert component(no_ach, 'personal_components', 'achievements')['points'] == 0
    assert component(no_ach, 'personal_components', 'risk')['points'] == 0

    # Current-price table stays separate from promotional savings.
    cheap = ranked([game('cheap', original_price_rub=1000, current_price_rub=39)])[0]
    normal_price = ranked([game('normal-price', original_price_rub=1000, current_price_rub=460)])[0]
    assert component(cheap, 'purchase_components', 'price')['points'] == 12
    assert component(normal_price, 'purchase_components', 'price')['points'] == 9
    assert component(cheap, 'purchase_components', 'price')['points'] - component(normal_price, 'purchase_components', 'price')['points'] == 3

    # Discount value is absolute rubles saved, not the displayed percentage.
    tiny_fifty_percent = ranked([game(
        'tiny-50-percent',
        original_price_rub=60,
        current_price_rub=30,
        discount_percent=50,
    )])[0]
    large_fifty_percent = ranked([game(
        'large-50-percent',
        original_price_rub=6000,
        current_price_rub=3000,
        discount_percent=50,
    )])[0]
    tiny_savings = component(tiny_fifty_percent, 'purchase_components', 'savings')
    large_savings = component(large_fifty_percent, 'purchase_components', 'savings')
    assert tiny_savings['savings_rub'] == 30
    assert tiny_savings['points'] == 0
    assert large_savings['savings_rub'] == 3000
    assert large_savings['points'] == 19

    # Percentage itself cannot change V2 score when actual prices are identical.
    percent_a = ranked([game('percent-a', original_price_rub=1000, current_price_rub=500, discount_percent=10)])[0]
    percent_b = ranked([game('percent-b', original_price_rub=1000, current_price_rub=500, discount_percent=90)])[0]
    assert percent_a['total_score'] == percent_b['total_score']
    assert component(percent_a, 'purchase_components', 'savings')['points'] == 10
    assert component(percent_b, 'purchase_components', 'savings')['points'] == 10

    # A short-history technical record must not overpower a much larger real saving.
    new_game_record = ranked([game(
        'new-game-record',
        original_price_rub=500,
        current_price_rub=400,
        history_quality='record',
    )])[0]
    old_game_big_saving = ranked([game(
        'old-game-big-saving',
        original_price_rub=1400,
        current_price_rub=400,
        history_quality='good_vs_history',
    )])[0]
    assert component(new_game_record, 'purchase_components', 'savings')['points'] == 3
    assert component(new_game_record, 'purchase_components', 'history')['points'] == 8
    assert component(old_game_big_saving, 'purchase_components', 'savings')['points'] == 14
    assert component(old_game_big_saving, 'purchase_components', 'history')['points'] == 5
    assert old_game_big_saving['purchase_score'] > new_game_record['purchase_score']

    unverified = ranked([game('unverified', history_quality='unverified')])[0]
    previously_free = ranked([game('previously-free', history_quality='previously_free')])[0]
    weak_history = ranked([game('weak-history', history_quality='well_above_history')])[0]
    assert component(unverified, 'purchase_components', 'history')['points'] == 3
    assert component(previously_free, 'purchase_components', 'history')['points'] == 2
    assert component(weak_history, 'purchase_components', 'history')['points'] == 0

    # Regression for the High On Life / Seraph's Last Stand structure: a tiny cheap-game saving and serious
    # personal risk should not beat a wishlist candidate with a materially larger real saving.
    cheap_high_risk = game(
        'cheap-high-risk',
        fit='moderate',
        source_fit='moderate',
        risk_level='high',
        risk_codes=['unchanged_repetition'],
        wishlist=False,
        original_price_rub=55,
        current_price_rub=39,
        history_quality='good_vs_history',
    )
    interesting_wait = game(
        'interesting-wishlist-wait',
        fit='moderate',
        source_fit='moderate',
        risk_level='low',
        risk_codes=[],
        wishlist=True,
        original_price_rub=1350,
        current_price_rub=460,
        history_quality='well_above_history',
    )
    risk_pair = ranked([cheap_high_risk, interesting_wait])
    assert titles(risk_pair) == ['interesting-wishlist-wait', 'cheap-high-risk']
    assert risk_pair[0]['total_score'] > risk_pair[1]['total_score']
    assert (risk_pair[0]['priority_vs_next'] or {}).get('deciding_factor_id') == 'total_score_desc'

    # Central-config tuning proof: changing only JSON changes the score; no Python or taste re-evaluation is needed.
    tuned = deepcopy(policy)
    tuned['score_model']['purchase']['savings']['bands'] = deepcopy(
        tuned['score_model']['purchase']['savings']['bands']
    )
    for band in tuned['score_model']['purchase']['savings']['bands']:
        if band['min'] <= 700 <= band['max']:
            band['points'] = 4
    with tempfile.NamedTemporaryFile('w', suffix='.json', encoding='utf-8', delete=False) as fh:
        json.dump(tuned, fh, ensure_ascii=False)
        tuned_path = Path(fh.name)
    try:
        before = ranked([game('weight-test', original_price_rub=1000, current_price_rub=300)])[0]
        after = ranked([game('weight-test', original_price_rub=1000, current_price_rub=300)], policy_path=tuned_path)[0]
        assert component(before, 'purchase_components', 'savings')['points'] == 10
        assert component(after, 'purchase_components', 'savings')['points'] == 4
        assert before['total_score'] - after['total_score'] == 6
        assert component(before, 'personal_components', 'taste')['points'] == component(after, 'personal_components', 'taste')['points']
    finally:
        tuned_path.unlink(missing_ok=True)

    # Per-game ranking diagnostics now contain only urgency, visible score and deterministic title fallback.
    diagnostic_pair = ranked([game('B'), game('A', wishlist=True)])
    for row in diagnostic_pair:
        assert [factor['id'] for factor in row.get('priority_factors') or []] == EXPECTED_ORDER
        assert all('label' in factor and 'value' in factor and 'sort_value' in factor for factor in row['priority_factors'])
        visible_text = ' '.join(f"{factor.get('label', '')} {factor.get('value', '')}" for factor in row['priority_factors']).casefold()
        assert 'bucket' not in visible_text
        assert 'tie-break' not in visible_text
        assert 'production' not in visible_text

    # UI manual end-of-queue override must stay above automatic priority.
    app = Path('web/app.js').read_text(encoding='utf-8')
    required_ui_fragments = [
        "if(r.manual_end_at)manual.push(g.id);else normal.push(g.id);",
        "return [...normal,...manual];",
        "r.manual_end_at=Date.now();",
        "state.queue.ids.push(g.id);",
        "g.risk_status",
        "Экономия по акции",
    ]
    for fragment in required_ui_fragments:
        assert fragment in app, f'missing UI invariant: {fragment}'

    print('PRIORITY_RANKING_VALIDATION=PASS')


if __name__ == '__main__':
    main()
