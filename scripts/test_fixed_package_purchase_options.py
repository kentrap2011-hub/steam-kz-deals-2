from copy import deepcopy
from pathlib import Path

import priority_ranking
from apply_fixed_package_purchase_options import build_recommendations
from build_fixed_package_purchase_options import classify_package, packageid_for_returned_item


RATE = 5.396789


def family(fid, appid, price, title):
    return {
        'family_id': fid,
        'family_type': 'base_game',
        'base_appids': [str(appid)],
        'primary_final_kzt': price,
        'primary_title': title,
    }


def visible(fid, title):
    return {'id': fid, 'title': title}


def package(pid, price, appids, title='Package'):
    return {
        'key': f'Sub_{pid}',
        'packageid': pid,
        'entity_kind': 'sub',
        'fixed_price_semantics': True,
        'personalized_price': False,
        'title': title,
        'final_kzt': price,
        'original_kzt': price * 2,
        'discount_percent': 50,
        'included_appids': [str(x) for x in appids],
        'web_url': f'https://store.steampowered.com/sub/{pid}/',
    }


def run(packages, families, items):
    artifact = {'packages': {row['key']: row for row in packages}}
    graph = {'families': families}
    return build_recommendations(artifact, graph, items, RATE)


def ranking_game(title, **overrides):
    row = {
        'id': f'game:{title}',
        'title': title,
        'fit': 'strong',
        'source_fit': 'strong',
        'risk_level': 'low',
        'risk_codes': [],
        'wishlist': False,
        'history_quality': 'record',
        'discount_percent': 50,
        'original_price_rub': 300,
        'current_price_rub': 150,
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
    row.update(overrides)
    return row


def strong_four_game_package(price=300):
    return {
        'package_key': 'Sub_400',
        'packageid': 400,
        'package_title': 'Four Game Pack',
        'package_price_rub': price,
        'package_price_per_visible_game_rub': round(price / 4, 1),
        'covered_visible_game_count': 4,
        'covered_visible_titles': ['One', 'Two', 'Three', 'Four'],
        'standalone_total_rub': 600,
        'savings_rub': 600 - price,
        'savings_percent_vs_standalone': round(((600 - price) / 600) * 100, 1),
        'web_url': 'https://store.steampowered.com/sub/400/',
    }


def test_bioshock_collection_actual_member_regression():
    families = [
        family('game:409710', 409710, 662, 'BioShock Remastered'),
        family('game:409720', 409720, 397, 'BioShock 2 Remastered'),
        family('game:8870', 8870, 975, 'BioShock Infinite'),
    ]
    items = [
        visible('game:409710', 'BioShock Remastered'),
        visible('game:409720', 'BioShock 2 Remastered'),
        visible('game:8870', 'BioShock Infinite'),
    ]
    packages = [package(127633, 1420, [409710, 409720, 8870], 'BioShock: The Collection')]
    recs, best = run(packages, families, items)
    assert len(recs) == 1
    rec = recs[0]
    assert rec['standalone_total_kzt'] == 2034
    assert rec['savings_kzt'] == 614
    assert rec['covered_visible_game_count'] == 3
    assert rec['package_price_per_visible_game_rub'] == round(rec['package_price_rub'] / 3, 1)
    assert set(best) == {'game:409710', 'game:409720', 'game:8870'}


def test_package_does_not_guess_original_remaster_equivalence():
    families = [
        family('game:7670', 7670, 662, 'BioShock'),
        family('game:8850', 8850, 397, 'BioShock 2'),
        family('game:8870', 8870, 975, 'BioShock Infinite'),
    ]
    items = [visible('game:7670', 'BioShock'), visible('game:8850', 'BioShock 2'), visible('game:8870', 'BioShock Infinite')]
    packages = [package(127633, 1420, [409710, 409720, 8870], 'BioShock: The Collection')]
    recs, best = run(packages, families, items)
    assert recs == []
    assert best == {}


def test_more_expensive_package_is_not_recommended():
    families = [family('game:1', 1, 500, 'One'), family('game:2', 2, 500, 'Two')]
    items = [visible('game:1', 'One'), visible('game:2', 'Two')]
    recs, best = run([package(10, 1100, [1, 2])], families, items)
    assert recs == []
    assert best == {}


def test_single_visible_game_does_not_trigger_multi_game_advice():
    families = [family('game:1', 1, 500, 'One'), family('game:2', 2, 500, 'Two')]
    items = [visible('game:1', 'One')]
    recs, best = run([package(10, 400, [1, 2])], families, items)
    assert recs == []
    assert best == {}


def test_unknown_extra_content_adds_no_assumed_value():
    families = [family('game:1', 1, 500, 'One'), family('game:2', 2, 500, 'Two')]
    items = [visible('game:1', 'One'), visible('game:2', 'Two')]
    recs, _ = run([package(10, 900, [1, 2, 999999])], families, items)
    assert recs[0]['standalone_total_kzt'] == 1000
    assert recs[0]['savings_kzt'] == 100
    assert recs[0]['unknown_extra_content_value_assumed_kzt'] == 0


def test_family_is_counted_once_when_multiple_appids_map_to_same_family():
    families = [{
        'family_id': 'game:1', 'family_type': 'base_game', 'base_appids': ['1', '11'],
        'primary_final_kzt': 500, 'primary_title': 'Edition Family',
    }, family('game:2', 2, 500, 'Two')]
    items = [visible('game:1', 'Edition Family'), visible('game:2', 'Two')]
    recs, _ = run([package(10, 800, [1, 11, 2])], families, items)
    assert recs[0]['covered_visible_game_count'] == 2
    assert recs[0]['standalone_total_kzt'] == 1000
    assert recs[0]['savings_kzt'] == 200


def test_best_package_prefers_larger_absolute_savings():
    families = [family('game:1', 1, 500, 'One'), family('game:2', 2, 500, 'Two')]
    items = [visible('game:1', 'One'), visible('game:2', 'Two')]
    recs, best = run([package(10, 800, [1, 2]), package(11, 700, [1, 2])], families, items)
    assert len(recs) == 2
    assert best['game:1']['packageid'] == 11
    assert best['game:2']['packageid'] == 11


def test_returned_package_can_be_matched_by_exact_option():
    item = {'id': 999999, 'purchase_options': [{'packageid': 127633}]}
    assert packageid_for_returned_item(item, {127633}) == 127633


def test_package_classification_requires_two_current_apps():
    item = {
        'id': 127633,
        'name': 'BioShock: The Collection',
        'included_appids': [409710, 409720, 8870],
        'purchase_options': [{
            'packageid': 127633,
            'final_price_in_cents': 142000,
            'original_price_in_cents': 710000,
            'discount_pct': 80,
            'active_discounts': [],
        }],
    }
    entry, reason = classify_package(127633, item, {409710}, {409710}, 1)
    assert entry is None
    assert reason == 'fewer_than_two_current_app_candidates'


def test_four_game_package_materially_improves_purchase_score_without_changing_taste():
    standalone = ranking_game('Standalone')
    bundled = ranking_game('Bundled', better_purchase_option=strong_four_game_package())
    ranked, _ = priority_ranking.apply_final_priority_order([deepcopy(standalone), deepcopy(bundled)])
    by_title = {row['title']: row for row in ranked}
    solo = by_title['Standalone']
    pack = by_title['Bundled']

    assert solo['score_breakdown']['purchase_route'] == 'standalone'
    assert solo['purchase_score'] == 22
    assert pack['score_breakdown']['purchase_route'] == 'fixed_package'
    assert pack['purchase_score'] == 40
    assert pack['package_value_points'] == 18
    assert pack['personal_score'] == solo['personal_score']
    assert pack['total_score'] - solo['total_score'] == 18
    assert [row['id'] for row in pack['score_breakdown']['purchase_components']] == [
        'package_savings_percent',
        'package_effective_price',
        'package_coverage',
    ]
    assert ranked[0]['title'] == 'Bundled'


def test_package_over_practical_price_ceiling_is_visible_but_does_not_boost_score():
    row = ranking_game('Over budget', better_purchase_option=strong_four_game_package(price=800))
    ranked, _ = priority_ranking.apply_final_priority_order([row])
    game = ranked[0]
    breakdown = game['score_breakdown']
    assert breakdown['purchase_route'] == 'standalone'
    assert breakdown['package_route']['available'] is True
    assert breakdown['package_route']['eligible_for_score'] is False
    assert breakdown['package_route']['status'] == 'package_over_practical_price_ceiling'
    assert game['package_value_points'] == 0


def test_ui_has_explicit_package_block_contract():
    app = Path('web/app.js').read_text(encoding='utf-8')
    required = [
        'function renderPackageDeal(g)',
        'better_purchase_option',
        '🎁 Выгодный набор Steam',
        'package_price_per_visible_game_rub',
        'standalone_total_rub',
        'savings_rub',
        "purchase_route==='fixed_package'",
    ]
    for fragment in required:
        assert fragment in app, f'missing package UI contract: {fragment}'


def main():
    tests = [
        test_bioshock_collection_actual_member_regression,
        test_package_does_not_guess_original_remaster_equivalence,
        test_more_expensive_package_is_not_recommended,
        test_single_visible_game_does_not_trigger_multi_game_advice,
        test_unknown_extra_content_adds_no_assumed_value,
        test_family_is_counted_once_when_multiple_appids_map_to_same_family,
        test_best_package_prefers_larger_absolute_savings,
        test_returned_package_can_be_matched_by_exact_option,
        test_package_classification_requires_two_current_apps,
        test_four_game_package_materially_improves_purchase_score_without_changing_taste,
        test_package_over_practical_price_ceiling_is_visible_but_does_not_boost_score,
        test_ui_has_explicit_package_block_contract,
    ]
    for test in tests:
        test()
    print(f'fixed package purchase option tests: {len(tests)} passed')


if __name__ == '__main__':
    main()
