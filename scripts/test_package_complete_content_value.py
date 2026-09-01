from build_fixed_package_purchase_options import all_included_appids, build_content_catalog
from apply_fixed_package_purchase_options import build_recommendations


RATE = 5.4


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


def content(appid, title, app_type, parent=None, current=None, status='verified_single_app_purchase_route'):
    return {
        'appid': str(appid),
        'title': title,
        'app_type': app_type,
        'parent_appid': str(parent) if parent is not None else None,
        'current_standalone_kzt': current,
        'original_standalone_kzt': current,
        'standalone_discount_percent': 0,
        'standalone_purchase_packageid': appid + 100000 if current is not None else None,
        'standalone_purchase_option_name': title if current is not None else None,
        'valuation_status': status if current is not None else 'no_verified_single_app_purchase_route',
        'source': 'IStoreBrowseService/GetItems',
    }


def bioshock_package():
    return {
        'key': 'Sub_127633',
        'packageid': 127633,
        'entity_kind': 'sub',
        'fixed_price_semantics': True,
        'personalized_price': False,
        'title': 'BioShock: The Collection',
        'final_kzt': 1420,
        'original_kzt': 7100,
        'discount_percent': 80,
        'included_appids': ['409710', '409720', '8870'],
        'all_included_appids': ['409710', '409720', '525720', '8870', '214933', '2028850'],
        'included_content': [
            content(409710, 'BioShock Remastered', 'game'),
            content(409720, 'BioShock 2 Remastered', 'game'),
            content(525720, "BioShock 2: Minerva's Den Remastered", 'dlc', parent=409720, current=300),
            content(8870, 'BioShock Infinite', 'game'),
            content(214933, 'BioShock Infinite - Season Pass', 'dlc', parent=8870, current=500),
            content(2028850, "Bioshock Infinite: Columbia's Finest", 'dlc', parent=8870, current=200),
        ],
        'web_url': 'https://store.steampowered.com/sub/127633/',
    }


def test_full_membership_unions_base_appids_and_nested_dlc():
    item = {
        'included_appids': [409710, 409720, 8870],
        'included_items': {
            'included_apps': [
                {'appid': 409710},
                {'appid': 409720},
                {'appid': 525720},
                {'appid': 8870},
                {'appid': 214933},
                {'appid': 2028850},
            ]
        },
    }
    assert all_included_appids(item) == [8870, 214933, 409710, 409720, 525720, 2028850]


def test_content_price_requires_exact_single_app_purchase_sub():
    appid = 214933
    item = {
        'item_type': 0,
        'id': appid,
        'name': 'BioShock Infinite - Season Pass',
        'type': 4,
        'related_items': {'parent_appid': 8870},
        'purchase_options': [
            {
                'packageid': 900,
                'final_price_in_cents': 30000,
                'original_price_in_cents': 30000,
                'discount_pct': 0,
                'purchase_option_name': 'Cheaper shared bundle',
            },
            {
                'packageid': 901,
                'final_price_in_cents': 50000,
                'original_price_in_cents': 200000,
                'discount_pct': 75,
                'purchase_option_name': 'BioShock Infinite Season Pass',
            },
        ],
    }
    route_packages = {
        900: {'included_appids': [8870, 214933]},
        901: {'included_appids': [214933]},
    }
    catalog = build_content_catalog([appid], [item], route_packages)
    row = catalog[appid]
    assert row['app_type'] == 'dlc'
    assert row['parent_appid'] == '8870'
    assert row['current_standalone_kzt'] == 500
    assert row['standalone_purchase_packageid'] == 901
    assert row['valuation_status'] == 'verified_single_app_purchase_route'


def test_verified_dlc_changes_bioshock_complete_content_economics_without_valuing_excluded_game():
    families = [
        family('game:8850', 8850, 397, 'BioShock 2'),
        family('game:8870', 8870, 975, 'BioShock Infinite'),
    ]
    items = [visible('game:8850', 'BioShock 2'), visible('game:8870', 'BioShock Infinite')]
    artifact = {'packages': {'Sub_127633': bioshock_package()}}
    graph = {'families': families}
    recs, best = build_recommendations(
        artifact,
        graph,
        items,
        RATE,
        purchase_equivalence=bioshock_equivalence(),
    )
    assert len(recs) == 1
    rec = recs[0]

    # Base games are still only the two personalized/visible families.
    assert rec['visible_standalone_game_total_kzt'] == 1372
    # Three verified top-level DLC/content apps attached to those covered games count.
    assert rec['verified_incremental_content_total_kzt'] == 1000
    assert rec['verified_incremental_content_count'] == 3
    assert rec['comparable_entitlement_total_kzt'] == 2372
    assert rec['standalone_total_kzt'] == 2372
    assert rec['savings_kzt'] == 952
    assert rec['strict_current_price_savings'] is True

    # BioShock Remastered is present in the real package but its corresponding first
    # BioShock family is not visible here. Price must not rescue that Taste-excluded game.
    nonpersonalized = {row['appid']: row for row in rec['verified_nonpersonalized_included_content']}
    assert '409710' in nonpersonalized
    assert nonpersonalized['409710']['personalized_value_kzt'] == 0
    assert nonpersonalized['409710']['counted_in_package_comparable_value'] is False

    assert set(best) == {'game:8850', 'game:8870'}


def test_unpriced_verified_dlc_is_visible_but_has_zero_monetary_value():
    package = bioshock_package()
    package['included_content'].append(
        content(999001, 'Verified DLC without standalone price', 'dlc', parent=8870, current=None)
    )
    artifact = {'packages': {'Sub_127633': package}}
    graph = {'families': [
        family('game:8850', 8850, 397, 'BioShock 2'),
        family('game:8870', 8870, 975, 'BioShock Infinite'),
    ]}
    items = [visible('game:8850', 'BioShock 2'), visible('game:8870', 'BioShock Infinite')]
    recs, _ = build_recommendations(
        artifact,
        graph,
        items,
        RATE,
        purchase_equivalence=bioshock_equivalence(),
    )
    rec = recs[0]
    assert rec['verified_incremental_content_total_kzt'] == 1000
    assert rec['verified_incremental_content_unpriced_count'] == 1
    assert rec['verified_incremental_content_unpriced'][0]['appid'] == '999001'
    assert rec['verified_unpriced_content_value_assumed_kzt'] == 0


def test_dlc_for_noncovered_game_does_not_increase_personalized_value():
    package = bioshock_package()
    package['included_content'].append(
        content(999002, 'DLC for excluded game', 'dlc', parent=409710, current=999)
    )
    artifact = {'packages': {'Sub_127633': package}}
    graph = {'families': [
        family('game:8850', 8850, 397, 'BioShock 2'),
        family('game:8870', 8870, 975, 'BioShock Infinite'),
    ]}
    items = [visible('game:8850', 'BioShock 2'), visible('game:8870', 'BioShock Infinite')]
    recs, _ = build_recommendations(
        artifact,
        graph,
        items,
        RATE,
        purchase_equivalence=bioshock_equivalence(),
    )
    rec = recs[0]
    assert rec['verified_incremental_content_total_kzt'] == 1000
    by_appid = {row['appid']: row for row in rec['verified_nonpersonalized_included_content']}
    assert by_appid['999002']['personalized_value_kzt'] == 0


def main():
    tests = [
        test_full_membership_unions_base_appids_and_nested_dlc,
        test_content_price_requires_exact_single_app_purchase_sub,
        test_verified_dlc_changes_bioshock_complete_content_economics_without_valuing_excluded_game,
        test_unpriced_verified_dlc_is_visible_but_has_zero_monetary_value,
        test_dlc_for_noncovered_game_does_not_increase_personalized_value,
    ]
    for test in tests:
        test()
    print(f'package complete-content value tests: {len(tests)} passed')


if __name__ == '__main__':
    main()
