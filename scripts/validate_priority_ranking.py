from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import build_final_visual_payload
import priority_ranking

EXPECTED_ORDER = [
    'sale_expiry_urgency_asc',
    'practical_or_personal_risk_asc',
    'priority_bucket_asc',
    'wishlist_desc',
    'discount_percent_desc',
    'price_quality_vs_history_desc',
    'current_price_rub_asc',
    'achievement_quality_desc',
    'duration_tiebreak_asc',
    'title_asc',
]

NOW = datetime(2026, 8, 30, 6, 0, tzinfo=timezone.utc)  # 10:00 Europe/Samara


def game(title, **overrides):
    row = {
        'id': title,
        'title': title,
        'priority_bucket': 1,
        'risk_level': 'low',
        'wishlist': False,
        'history_quality': 'record',
        'discount_percent': 80,
        'current_price_rub': 300,
        'duration_tiebreak_penalty': 0,
        'duration_preference_band': 'unknown',
        'sale_end_utc': '2026-09-05T12:00:00Z',
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


def ranked(rows):
    rows = deepcopy(rows)
    rows, order = priority_ranking.apply_final_priority_order(rows, now=NOW)
    assert order == EXPECTED_ORDER, (order, EXPECTED_ORDER)
    return rows


def titles(rows):
    return [row['title'] for row in rows]


def main():
    assert callable(build_final_visual_payload.main)
    assert priority_ranking.load_final_priority_order() == EXPECTED_ORDER

    # Expiring today/tomorrow overrides every automatic recommendation factor.
    urgent_today = game('today', priority_bucket=6, risk_level='high', sale_end_utc='2026-08-30T18:00:00Z')
    urgent_tomorrow = game('tomorrow', priority_bucket=1, sale_end_utc='2026-08-31T18:00:00Z')
    later = game('later', priority_bucket=1, sale_end_utc='2026-09-05T18:00:00Z')
    assert titles(ranked([later, urgent_tomorrow, urgent_today])) == ['today', 'tomorrow', 'later']

    # Medium/low heuristic risks are descriptive context only at this early layer;
    # only high/serious risk may demote before the mixed taste+deal bucket.
    medium = game('a-medium', risk_level='medium')
    low = game('b-low', risk_level='low')
    assert priority_ranking.practical_risk_rank(medium) == priority_ranking.practical_risk_rank(low) == 0
    high = game('a-high', risk_level='high')
    assert titles(ranked([high, low])) == ['b-low', 'a-high']

    # Regression for the Seraph's Last Stand / High On Life structure: a very cheap candidate
    # with a commercially better bucket must not beat a clearly safer wishlist candidate merely
    # because its current price is close to historical lows.
    cheap_high_risk = game(
        'cheap-high-risk',
        priority_bucket=5,
        risk_level='high',
        wishlist=False,
        discount_percent=30,
        history_quality='good_vs_history',
        current_price_rub=39,
    )
    interesting_wait = game(
        'interesting-wishlist-wait',
        priority_bucket=6,
        risk_level='low',
        wishlist=True,
        discount_percent=65,
        history_quality='well_above_history',
        current_price_rub=460,
    )
    risk_pair = ranked([cheap_high_risk, interesting_wait])
    assert titles(risk_pair) == ['interesting-wishlist-wait', 'cheap-high-risk']
    assert (risk_pair[0].get('priority_vs_next') or {}).get('deciding_factor_id') == 'practical_or_personal_risk_asc'

    # With the same urgency and serious-risk layer, the qualitative taste+deal bucket remains first.
    assert titles(ranked([game('bucket2', priority_bucket=2), game('bucket1', priority_bucket=1)])) == ['bucket1', 'bucket2']

    # A bare legacy Steam requirement label is neutral without confirmed modern-Windows friction.
    bare_legacy = game('a-bare-legacy', practical={'legacy_windows_requirement_label': 'legacy', 'modern_windows_friction': 'unknown'})
    normal = game('b-normal', practical={'modern_windows_friction': 'likely_none'})
    assert priority_ranking.practical_risk_rank(bare_legacy) == priority_ranking.practical_risk_rank(normal) == 0

    # Confirmed pre-Windows-10 targeting/fixes must demote the otherwise equal candidate.
    confirmed_old = game('a-confirmed-old', practical={'modern_windows_friction': 'confirmed_pre_windows_10_target'})
    assert titles(ranked([confirmed_old, normal])) == ['b-normal', 'a-confirmed-old']

    # Wishlist is meaningful inside the same bucket/risk layer and comes before commercial tie-breaks.
    wishlist = game('wishlist', wishlist=True, discount_percent=20, history_quality='well_above_history')
    stronger_deal = game('stronger-deal', wishlist=False, discount_percent=90, history_quality='record')
    wishlist_pair = ranked([stronger_deal, wishlist])
    assert titles(wishlist_pair) == ['wishlist', 'stronger-deal']

    # Per-game diagnostics must be producer-owned and follow the exact canonical factor order.
    for row in wishlist_pair:
        assert [factor['id'] for factor in row.get('priority_factors') or []] == EXPECTED_ORDER
        assert all('label' in factor and 'value' in factor and 'sort_value' in factor for factor in row['priority_factors'])
        visible_text = ' '.join(f"{factor.get('label', '')} {factor.get('value', '')}" for factor in row['priority_factors']).casefold()
        assert 'bucket' not in visible_text
        assert 'tie-break' not in visible_text
    first_vs_next = wishlist_pair[0].get('priority_vs_next') or {}
    assert first_vs_next.get('next_game_id') == 'stronger-deal'
    assert first_vs_next.get('deciding_factor_id') == 'wishlist_desc'
    assert first_vs_next.get('current_value') == 'да'
    assert first_vs_next.get('next_value') == 'нет'
    assert wishlist_pair[-1].get('priority_vs_next') is None

    # Discount comes before historical-minimum quality: a short price history must not make a routine
    # new-game 20% record beat a genuinely strong old-game discount.
    new_game_record = game('new-game-record', discount_percent=20, history_quality='record')
    old_game_strong_discount = game('old-game-strong-discount', discount_percent=70, history_quality='good_vs_history')
    assert titles(ranked([new_game_record, old_game_strong_discount])) == ['old-game-strong-discount', 'new-game-record']

    # Commercial value precedes achievements: achievements are a late close-candidate factor.
    cheap_no_ach = game('cheap-no-ach', current_price_rub=200, practical={'steam_achievements': False, 'achievement_quality': None})
    expensive_best_ach = game('expensive-best-ach', current_price_rub=400, practical={'steam_achievements': True, 'achievement_quality': 5})
    assert titles(ranked([expensive_best_ach, cheap_no_ach])) == ['cheap-no-ach', 'expensive-best-ach']

    # Direct user evidence is intentionally not a separate final factor; it already changes fit/bucket upstream.
    assert not any('direct_user' in factor for factor in EXPECTED_ORDER)

    # UI manual end-of-queue override must stay above automatic priority, including expiry urgency.
    app = Path('web/app.js').read_text(encoding='utf-8')
    required_ui_fragments = [
        "if(r.manual_end_at)manual.push(g.id);else normal.push(g.id);",
        "return [...normal,...manual];",
        "r.manual_end_at=Date.now();",
        "state.queue.ids.push(g.id);",
    ]
    for fragment in required_ui_fragments:
        assert fragment in app, f'missing manual queue override invariant: {fragment}'

    print('PRIORITY_RANKING_VALIDATION=PASS')


if __name__ == '__main__':
    main()
