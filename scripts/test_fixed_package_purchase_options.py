import json
from copy import deepcopy
from pathlib import Path

import build_final_visual_payload as final_visual
import priority_ranking
from apply_fixed_package_purchase_options import build_recommendations, load_purchase_equivalence
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


def run(packages, families, items, equivalence=None):
    artifact = {'packages': {row['key']: row for row in packages}}
    graph = {'families': families}
    return build_recommendations(
        artifact,
        graph,
        items,
        RATE,
        purchase_equivalence=equivalence,
    )


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
        'strict_current_price_savings': price < 600,
        'web_url': 'https://store.steampowered.com/sub/400/',
    }


def bioshock_equivalence():
    return {
        '7670': {
            'package_substitute_appids': {'409710'},
            'relationship': 'verified_remastered_purchase_substitute',
            'evidence_note': 'BioShock -> BioShock Remastered',
        },
        '8850': {
            'package_substitute_appids': {'409720'},
            'relationship': 'verified_remastered_purchase_substitute',
            'evidence_note': 'BioShock 2 -> BioShock 2 Remastered',
        },
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
    assert rec['strict_current_price_savings'] is True
    assert rec['covered_visible_game_count'] == 3
    assert rec['uses_verified_purchase_equivalence'] is False
    assert rec['package_price_per_visible_game_rub'] == round(rec['package_price_rub'] / 3, 1)
    assert set(best) == {'game:409710', 'game:409720', 'game:8870'}


def test_package_does_not_guess_original_remaster_equivalence_without_explicit_override():
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


def test_bioshock_collection_uses_explicit_directional_purchase_equivalence():
    families = [
        family('game:8850', 8850, 397, 'BioShock 2'),
        family('game:8870', 8870, 975, 'BioShock Infinite'),
    ]
    items = [visible('game:8850', 'BioShock 2'), visible('game:8870', 'BioShock Infinite')]
    packages = [package(127633, 1420, [409710, 409720, 8870], 'BioShock: The Collection')]
    recs, best = run(packages, families, items, bioshock_equivalence())
    assert len(recs) == 1
    rec = recs[0]
    assert rec['covered_visible_game_count'] == 2
    assert set(rec['covered_visible_game_ids']) == {'game:8850', 'game:8870'}
    assert rec['uses_verified_purchase_equivalence'] is True
    assert rec['strict_current_price_savings'] is False
    assert rec['savings_kzt'] == -48
    assert set(best) == {'game:8850', 'game:8870'}

    evidence = {row['family_id']: row['matches'] for row in rec['coverage_evidence']}
    assert any(
        row['coverage_mode'] == 'verified_purchase_equivalence'
        and row['visible_appid'] == '8850'
        and row['package_appid'] == '409720'
        for row in evidence['game:8850']
    )
    assert any(
        row['coverage_mode'] == 'exact_included_appid'
        and row['visible_appid'] == '8870'
        and row['package_appid'] == '8870'
        for row in evidence['game:8870']
    )


def test_more_expensive_relevant_package_is_visible_as_information():
    families = [family('game:1', 1, 500, 'One'), family('game:2', 2, 500, 'Two')]
    items = [visible('game:1', 'One'), visible('game:2', 'Two')]
    recs, best = run([package(10, 1100, [1, 2])], families, items)
    assert len(recs) == 1
    assert recs[0]['strict_current_price_savings'] is False
    assert recs[0]['savings_kzt'] == -100
    assert set(best) == {'game:1', 'game:2'}


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


def test_best_package_prefers_strict_savings_then_larger_absolute_savings():
    families = [family('game:1', 1, 500, 'One'), family('game:2', 2, 500, 'Two')]
    items = [visible('game:1', 'One'), visible('game:2', 'Two')]
    recs, best = run([package(10, 1100, [1, 2]), package(11, 700, [1, 2])], families, items)
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


def test_non_saving_package_stays_visible_but_does_not_boost_ranking():
    option = strong_four_game_package(price=610)
    option['standalone_total_rub'] = 600
    option['savings_rub'] = -10
    option['savings_percent_vs_standalone'] = -1.7
    option['strict_current_price_savings'] = False
    option['price_delta_vs_standalone_rub'] = 10
    row = ranking_game('Relevant package', better_purchase_option=option)
    ranked, _ = priority_ranking.apply_final_priority_order([row])
    game = ranked[0]
    breakdown = game['score_breakdown']
    assert breakdown['purchase_route'] == 'standalone'
    assert breakdown['package_route']['available'] is True
    assert breakdown['package_route']['eligible_for_score'] is False
    assert breakdown['package_route']['status'] == 'no_strict_saving_vs_standalone'
    assert game['package_value_points'] == 0


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


def test_deterministic_refresh_reapplies_package_before_ranking():
    ready = {
        'items': [ranking_game('Standalone'), ranking_game('Bundled')],
        'production_contract': {},
    }
    original_apply = final_visual.package_options.apply_current_artifacts_to_visual

    def fake_package_refresh(payload):
        for game in payload.get('items') or []:
            if game.get('title') == 'Bundled':
                game['better_purchase_option'] = strong_four_game_package()
        return {
            'qualifying_package_count': 1,
            'strict_savings_package_count': 1,
            'verified_equivalence_package_count': 0,
            'visible_game_count_with_better_package': 1,
        }

    try:
        final_visual.package_options.apply_current_artifacts_to_visual = fake_package_refresh
        stats, order = final_visual.apply_deterministic_purchase_refresh(ready)
    finally:
        final_visual.package_options.apply_current_artifacts_to_visual = original_apply

    by_title = {row['title']: row for row in ready['items']}
    assert by_title['Standalone']['score_breakdown']['purchase_route'] == 'standalone'
    assert by_title['Bundled']['score_breakdown']['purchase_route'] == 'fixed_package'
    assert by_title['Bundled']['priority_rank'] == 1
    assert stats['visible_game_count_with_better_package'] == 1
    assert order == ['sale_expiry_urgency_asc', 'total_score_desc', 'title_asc']
    assert ready['production_contract']['fixed_package_touched_game_count'] == 1


def test_force_refresh_path_wires_deterministic_purchase_refresh():
    source = Path('scripts/build_final_visual_payload.py').read_text(encoding='utf-8')
    assert 'package_stats, _ = apply_deterministic_purchase_refresh(ready)' in source
    assert 'mode=deterministic_refresh' in source
    assert 'purchase_equivalence_blob_sha' in source


def test_ui_has_explicit_package_block_contract():
    app = Path('web/app.js').read_text(encoding='utf-8')
    override = Path('web/package-deal-ui.js').read_text(encoding='utf-8')
    index = Path('web/index.html').read_text(encoding='utf-8')
    required_app = [
        'function renderPackageDeal(g)',
        'better_purchase_option',
        'package_price_per_visible_game_rub',
        'standalone_total_rub',
        'savings_rub',
        "purchase_route==='fixed_package'",
    ]
    for fragment in required_app:
        assert fragment in app, f'missing base package UI contract: {fragment}'
    required_override = [
        'window.renderPackageDeal=function(g)',
        "strict_current_price_savings",
        "'🎁 Выгодный набор Steam':'🎁 Набор Steam'",
        'verified_purchase_equivalence',
        'не повышает рейтинг',
    ]
    for fragment in required_override:
        assert fragment in override, f'missing package UI override contract: {fragment}'
    assert 'package-deal-ui.js?v=purchase-equivalence-1' in index


def test_canonical_purchase_equivalence_config_is_purchase_only():
    eq = load_purchase_equivalence()
    assert eq['7670']['package_substitute_appids'] == {'409710'}
    assert eq['8850']['package_substitute_appids'] == {'409720'}


def test_current_production_inputs_expose_bioshock_collection_for_visible_bioshock_cards():
    package_path = Path('data/production/pre_ai/fixed_package_options.json')
    family_path = Path('data/production/pre_ai/family_graph.json')
    visual_path = Path('data/production/visual/current.json')
    if not (package_path.exists() and family_path.exists() and visual_path.exists()):
        return

    packages = json.loads(package_path.read_text(encoding='utf-8'))
    family_graph = json.loads(family_path.read_text(encoding='utf-8'))
    visual = json.loads(visual_path.read_text(encoding='utf-8'))
    visible_items = visual.get('items') or []
    bioshock2 = next((row for row in visible_items if row.get('title') == 'BioShock® 2'), None)
    infinite = next((row for row in visible_items if row.get('title') == 'BioShock Infinite'), None)
    if not bioshock2 or not infinite:
        raise AssertionError('Expected current production scope to contain BioShock® 2 and BioShock Infinite')

    recs, best = build_recommendations(
        packages,
        family_graph,
        visible_items,
        RATE,
        purchase_equivalence=load_purchase_equivalence(),
    )
    collection = next((row for row in recs if row.get('packageid') == 127633), None)
    assert collection is not None, 'BioShock: The Collection must be a relevant current package option'
    expected_ids = {str(bioshock2['id']), str(infinite['id'])}
    assert expected_ids <= set(collection['covered_visible_game_ids'])
    assert best[str(bioshock2['id'])]['packageid'] == 127633
    assert best[str(infinite['id'])]['packageid'] == 127633

    evidence = {
        row['family_id']: row['matches']
        for row in collection['coverage_evidence']
    }
    assert any(
        match.get('coverage_mode') == 'verified_purchase_equivalence'
        and match.get('visible_appid') == '8850'
        and match.get('package_appid') == '409720'
        for match in evidence[str(bioshock2['id'])]
    )
    assert any(
        match.get('coverage_mode') == 'exact_included_appid'
        and match.get('visible_appid') == '8870'
        and match.get('package_appid') == '8870'
        for match in evidence[str(infinite['id'])]
    )


def main():
    tests = [
        test_bioshock_collection_actual_member_regression,
        test_package_does_not_guess_original_remaster_equivalence_without_explicit_override,
        test_bioshock_collection_uses_explicit_directional_purchase_equivalence,
        test_more_expensive_relevant_package_is_visible_as_information,
        test_single_visible_game_does_not_trigger_multi_game_advice,
        test_unknown_extra_content_adds_no_assumed_value,
        test_family_is_counted_once_when_multiple_appids_map_to_same_family,
        test_best_package_prefers_strict_savings_then_larger_absolute_savings,
        test_returned_package_can_be_matched_by_exact_option,
        test_package_classification_requires_two_current_apps,
        test_four_game_package_materially_improves_purchase_score_without_changing_taste,
        test_non_saving_package_stays_visible_but_does_not_boost_ranking,
        test_package_over_practical_price_ceiling_is_visible_but_does_not_boost_score,
        test_deterministic_refresh_reapplies_package_before_ranking,
        test_force_refresh_path_wires_deterministic_purchase_refresh,
        test_ui_has_explicit_package_block_contract,
        test_canonical_purchase_equivalence_config_is_purchase_only,
        test_current_production_inputs_expose_bioshock_collection_for_visible_bioshock_cards,
    ]
    for test in tests:
        test()
    print(f'fixed package purchase option tests: {len(tests)} passed')


if __name__ == '__main__':
    main()
