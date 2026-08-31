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


def test_bioshock_collection_actual_member_regression():
    # These KZT values are deterministic comparison fixtures, not a live-price assertion.
    # The important regression is the current Steam package membership identity:
    # BioShock Remastered (409710), BioShock 2 Remastered (409720), BioShock Infinite (8870).
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
    packages = [
        package(
            127633,
            1420,
            [409710, 409720, 8870],
            'BioShock: The Collection',
        )
    ]
    recs, best = run(packages, families, items)
    assert len(recs) == 1
    rec = recs[0]
    assert rec['standalone_total_kzt'] == 2034
    assert rec['savings_kzt'] == 614
    assert rec['covered_visible_game_count'] == 3
    assert set(best) == {'game:409710', 'game:409720', 'game:8870'}


def test_package_does_not_guess_original_remaster_equivalence():
    families = [
        family('game:7670', 7670, 662, 'BioShock'),
        family('game:8850', 8850, 397, 'BioShock 2'),
        family('game:8870', 8870, 975, 'BioShock Infinite'),
    ]
    items = [
        visible('game:7670', 'BioShock'),
        visible('game:8850', 'BioShock 2'),
        visible('game:8870', 'BioShock Infinite'),
    ]
    packages = [
        package(
            127633,
            1420,
            [409710, 409720, 8870],
            'BioShock: The Collection',
        )
    ]
    recs, best = run(packages, families, items)
    assert recs == []
    assert best == {}


def test_more_expensive_package_is_not_recommended():
    families = [
        family('game:1', 1, 500, 'One'),
        family('game:2', 2, 500, 'Two'),
    ]
    items = [visible('game:1', 'One'), visible('game:2', 'Two')]
    recs, best = run([package(10, 1100, [1, 2])], families, items)
    assert recs == []
    assert best == {}


def test_single_visible_game_does_not_trigger_multi_game_advice():
    families = [
        family('game:1', 1, 500, 'One'),
        family('game:2', 2, 500, 'Two'),
    ]
    items = [visible('game:1', 'One')]
    recs, best = run([package(10, 400, [1, 2])], families, items)
    assert recs == []
    assert best == {}


def test_unknown_extra_content_adds_no_assumed_value():
    families = [
        family('game:1', 1, 500, 'One'),
        family('game:2', 2, 500, 'Two'),
    ]
    items = [visible('game:1', 'One'), visible('game:2', 'Two')]
    recs, _ = run([package(10, 900, [1, 2, 999999])], families, items)
    assert recs[0]['standalone_total_kzt'] == 1000
    assert recs[0]['savings_kzt'] == 100
    assert recs[0]['unknown_extra_content_value_assumed_kzt'] == 0


def test_family_is_counted_once_when_multiple_appids_map_to_same_family():
    families = [{
        'family_id': 'game:1',
        'family_type': 'base_game',
        'base_appids': ['1', '11'],
        'primary_final_kzt': 500,
        'primary_title': 'Edition Family',
    }, family('game:2', 2, 500, 'Two')]
    items = [visible('game:1', 'Edition Family'), visible('game:2', 'Two')]
    recs, _ = run([package(10, 800, [1, 11, 2])], families, items)
    assert recs[0]['covered_visible_game_count'] == 2
    assert recs[0]['standalone_total_kzt'] == 1000
    assert recs[0]['savings_kzt'] == 200


def test_best_package_prefers_larger_absolute_savings():
    families = [
        family('game:1', 1, 500, 'One'),
        family('game:2', 2, 500, 'Two'),
    ]
    items = [visible('game:1', 'One'), visible('game:2', 'Two')]
    recs, best = run(
        [package(10, 800, [1, 2]), package(11, 700, [1, 2])],
        families,
        items,
    )
    assert len(recs) == 2
    assert best['game:1']['packageid'] == 11
    assert best['game:2']['packageid'] == 11


def test_returned_package_can_be_matched_by_exact_option():
    item = {
        'id': 999999,
        'purchase_options': [
            {'packageid': 127633},
        ],
    }
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
    entry, reason = classify_package(
        127633,
        item,
        {409710},
        {409710},
        1,
    )
    assert entry is None
    assert reason == 'fewer_than_two_current_app_candidates'


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
    ]
    for test in tests:
        test()
    print(f'fixed package purchase option tests: {len(tests)} passed')


if __name__ == '__main__':
    main()
