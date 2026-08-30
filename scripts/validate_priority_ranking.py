from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import priority_ranking

EXPECTED_ORDER = [
    'sale_expiry_urgency_asc',
    'priority_bucket_asc',
    'practical_or_personal_risk_asc',
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
    assert priority_ranking.load_final_priority_order() == EXPECTED_ORDER

    # Expiring today/tomorrow overrides every automatic recommendation factor.
    urgent_today = game('today', priority_bucket=6, sale_end_utc='2026-08-30T18:00:00Z')
    urgent_tomorrow = game('tomorrow', priority_bucket=1, sale_end_utc='2026-08-31T18:00:00Z')
    later = game('later', priority_bucket=1, sale_end_utc='2026-09-05T18:00:00Z')
    assert titles(ranked([later, urgent_tomorrow, urgent_today])) == ['today', 'tomorrow', 'later']

    # Within the same expiry urgency, the qualitative taste+deal bucket remains first.
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
    assert titles(ranked([stronger_deal, wishlist])) == ['wishlist', 'stronger-deal']

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
