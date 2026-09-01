from copy import deepcopy
from datetime import datetime, timezone

import apply_fixed_package_purchase_options as package_options
import priority_ranking
import refresh_visual_commercial_fields as commercial_refresh


NOW = datetime(2026, 9, 1, 8, 0, tzinfo=timezone.utc)
RATE = 5.0
SOURCE = '2026-09-01T00:00:00+00:00'


def payload():
    return {
        'source_mailing_updated_at_utc': SOURCE,
        'fx_binding': {'kzt_per_rub': RATE},
    }


def store_snapshot():
    return {
        'status': 'complete',
        'discovery_source_updated_at_utc': SOURCE,
        'observed_at_utc': '2026-09-01T07:00:00+00:00',
        'entries': {
            'App_1': {
                'key': 'App_1',
                'appid': '1',
                'title': 'One',
                'purchase_option_name': 'One',
                'discount_percent': 50,
                'final_kzt': 500.0,
                'original_kzt': 1000.0,
                'discount_end_utc': '2026-09-05T17:00:00+00:00',
            },
            'App_2': {
                'key': 'App_2',
                'appid': '2',
                'title': 'Two',
                'purchase_option_name': 'Two',
                'discount_percent': 50,
                'final_kzt': 500.0,
                'original_kzt': 1000.0,
                'discount_end_utc': '2026-09-05T17:00:00+00:00',
            },
        },
    }


def family_graph():
    return {
        'status': 'complete',
        'source_updated_at_utc': SOURCE,
        'families': [
            {
                'family_id': 'game:1',
                'family_type': 'base_game',
                'base_appids': ['1'],
                'primary_key': 'App_1',
                'primary_title': 'One',
                'primary_final_kzt': 9999.0,
                'alternative_purchase_keys': [],
                'all_member_keys': ['App_1'],
            },
            {
                'family_id': 'game:2',
                'family_type': 'base_game',
                'base_appids': ['2'],
                'primary_key': 'App_2',
                'primary_title': 'Two',
                'primary_final_kzt': 9999.0,
                'alternative_purchase_keys': [],
                'all_member_keys': ['App_2'],
            },
        ],
    }


def history_snapshot():
    return {
        'status': 'complete',
        'entries': {
            'App_1': {
                'history_quality': 'record',
                'historical_min_kzt': 500.0,
                'cache_status': 'confirmed_min',
            },
            'App_2': {
                'history_quality': 'near_record',
                'historical_min_kzt': 450.0,
                'cache_status': 'confirmed_min',
            },
        },
    }


def semantic_game(fid, title, appid):
    return {
        'id': fid,
        'title': title,
        'base_appids': [appid],
        'fit': 'strong',
        'source_fit': 'strong',
        'taste_factors': {
            'gameplay_mastery': 80,
            'development_variety': 70,
            'structure_pacing_direction': 75,
            'identity_hooks': 60,
            'breadth_of_match': 70,
        },
        'why_fit': ['semantic reason must survive'],
        'risks': ['semantic risk must survive'],
        'risk_codes': [],
        'risk_level': 'low',
        'wishlist': False,
        'history_quality': 'unverified',
        'current_price_rub': 999,
        'original_price_rub': 1999,
        'discount_percent': 10,
        'sale_end_utc': '2026-09-02T00:00:00+00:00',
        'duration_preference_band': 'unknown',
        'estimated_duration_hours': None,
        'direct_user_evidence': {'level': 'none'},
        'practical': {
            'modern_windows_friction': 'unknown',
            'steam_achievements': True,
            'achievement_quality': 3,
        },
        'offers': [],
    }


def test_commercial_refresh_changes_only_commercial_state():
    visual = {
        'source_mailing_updated_at_utc': 'old-semantic-source',
        'items': [semantic_game('game:1', 'One', '1')],
    }
    before = deepcopy(visual['items'][0])
    stats = commercial_refresh.refresh_visual_commercial_fields(
        visual,
        payload=payload(),
        store_snapshot=store_snapshot(),
        family_graph=family_graph(),
        history_snapshot=history_snapshot(),
        now=NOW,
    )
    game = visual['items'][0]

    assert visual['source_mailing_updated_at_utc'] == 'old-semantic-source'
    assert visual['commercial_source_mailing_updated_at_utc'] == SOURCE
    assert stats['taste_recalculated'] is False
    assert stats['semantic_fields_rewritten'] is False
    assert game['fit'] == before['fit']
    assert game['taste_factors'] == before['taste_factors']
    assert game['why_fit'] == before['why_fit']
    assert game['risks'] == before['risks']

    assert game['current_price_kzt'] == 500.0
    assert game['current_price_rub'] == 100
    assert game['original_price_rub'] == 200
    assert game['discount_percent'] == 50
    assert game['historical_minimum_rub'] == 100
    assert game['history_quality'] == 'record'
    assert game['sale_end_utc'] == '2026-09-05T17:00:00+00:00'


def test_package_comparison_uses_refreshed_current_prices_not_stale_family_price():
    visual = {
        'source_mailing_updated_at_utc': 'old-semantic-source',
        'items': [
            semantic_game('game:1', 'One', '1'),
            semantic_game('game:2', 'Two', '2'),
        ],
    }
    commercial_refresh.refresh_visual_commercial_fields(
        visual,
        payload=payload(),
        store_snapshot=store_snapshot(),
        family_graph=family_graph(),
        history_snapshot=history_snapshot(),
        now=NOW,
    )

    packages = {
        'source_mailing_updated_at_utc': SOURCE,
        'packages': {
            'Sub_10': {
                'key': 'Sub_10',
                'packageid': 10,
                'entity_kind': 'sub',
                'fixed_price_semantics': True,
                'personalized_price': False,
                'title': 'Two Game Pack',
                'final_kzt': 700.0,
                'original_kzt': 1400.0,
                'discount_percent': 50,
                'included_appids': ['1', '2'],
                'web_url': 'https://store.steampowered.com/sub/10/',
            }
        },
    }
    stats = package_options.apply_to_visual(
        visual,
        packages,
        family_graph(),
        RATE,
        purchase_equivalence={},
    )

    assert stats['source_binding_aligned'] is True
    assert stats['display_only_due_source_mismatch'] is False
    assert stats['visible_game_count_with_better_package'] == 2
    rec = visual['items'][0]['better_purchase_option']
    assert rec['standalone_total_kzt'] == 1000.0
    assert rec['savings_kzt'] == 300.0
    assert rec['strict_current_price_savings'] is True
    assert rec['comparison_source_aligned'] is True

    ranked, _ = priority_ranking.apply_final_priority_order(visual['items'])
    assert all(row['score_breakdown']['purchase_route'] == 'fixed_package' for row in ranked)
    assert all(row['package_value_points'] > 0 for row in ranked)


def main():
    tests = [
        test_commercial_refresh_changes_only_commercial_state,
        test_package_comparison_uses_refreshed_current_prices_not_stale_family_price,
    ]
    for test in tests:
        test()
    print(f'commercial refresh tests: {len(tests)} passed')


if __name__ == '__main__':
    main()
