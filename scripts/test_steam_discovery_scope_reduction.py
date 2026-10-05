import json
from pathlib import Path

import steam_partial_publish_runner as runner


ROOT = Path(__file__).resolve().parents[1]


def core():
    return runner.load_core()


def paid_item(*, discount=50, price=4500, key='App_100', title='Representative Game'):
    return {
        'key': key,
        'appid': key.split('_', 1)[1] if key.startswith('App_') else '100',
        'title': title,
        'discount_percent': discount,
        'final_kzt': price,
        'tag_ids': [19, 4182],
        'release_date': '',
        'global_review_positive': 99.0,
        'global_review_count': 50000,
        'russian_review_positive': 99.0,
        'russian_review_count': 5000,
    }


def result_row(appid, price_kzt, *, discount=50, item_key=None, title=None):
    item_key = item_key or f'App_{appid}'
    title = title or f'Probe {appid}'
    final_minor = int(round(float(price_kzt) * 100))
    return (
        f'<a class="search_result_row" data-ds-itemkey="{item_key}" '
        f'data-ds-appid="{appid}" data-ds-tagids="[19,4182]" '
        f'href="https://store.steampowered.com/app/{appid}/">'
        f'<span class="title">{title}</span>'
        f'<div class="discount_block" data-discount="{discount}" '
        f'data-price-final="{final_minor}"></div>'
        f'</a>'
    )


def page(total, rows):
    return {
        'total_count': total,
        'results_html': ''.join(rows),
    }


def test_explicit_partitions_cover_supported_content_types_and_params():
    c = core()
    assert c['PAGE_SIZE'] == 100
    assert tuple(c['SEARCH_CATEGORY_TYPES']) == ('games', 'dlc')
    assert c['SEARCH_CATEGORY_TYPES'] == {
        'games': '998',
        'dlc': '21',
    }
    assert '996' not in {
        partition['category1']
        for partition in c['SEARCH_PARTITIONS']
    }
    bundle_policy = c['PAID_DISCOVERY_POLICY']['bundle_package_discovery']
    assert bundle_policy['mode'] == 'embedded_in_games_partition'
    assert bundle_policy['representative_identity'] == 'Sub_76471'
    assert bundle_policy['representative_live_category1'] == '998'
    assert bundle_policy['standalone_category1_996_traversal'] is False
    for partition in c['SEARCH_PARTITIONS']:
        params = c['search_params'](
            0,
            'Name_ASC',
            category1=partition['category1'],
            maxprice_kzt=4500,
            hidef2p=True,
        )
        assert params['cc'] == 'kz'
        assert params['count'] == 100
        assert params['specials'] == 1
        assert params['category1'] == partition['category1']
        assert params['category1'] != c['SEARCH_CATEGORY1']
        assert params['maxprice'] == 4500
        assert params['hidef2p'] == 1
        assert params['ignore_preferences'] == 1


def test_partition_merge_is_deterministic_and_preserves_representatives():
    game = paid_item(key='App_100', title='Game')
    dlc = paid_item(key='App_200', title='DLC')
    bundle = paid_item(key='Sub_300', title='Bundle')
    duplicate = dict(game, title='Later duplicate must not replace game partition')

    traversals = [
        {
            'partition_id': 'games',
            # Live KZ evidence proves package Sub_ identities are returned by
            # category1=998, so packages are preserved inside this partition.
            'catalog': {'App_100': game, 'Sub_300': bundle},
        },
        {
            'partition_id': 'dlc',
            'catalog': {'App_200': dlc, 'App_100': duplicate},
        },
    ]
    merged, provenance, duplicate_count = runner.merge_partition_traversals(traversals)
    assert list(merged) == ['App_100', 'Sub_300', 'App_200']
    assert merged['App_100']['title'] == 'Game'
    assert provenance['App_100'] == ['games', 'dlc']
    assert provenance['Sub_300'] == ['games']
    assert duplicate_count == 1

    reversed_insertion = [
        {
            'partition_id': 'games',
            'catalog': dict(reversed(list(traversals[0]['catalog'].items()))),
        },
        {
            'partition_id': 'dlc',
            'catalog': dict(reversed(list(traversals[1]['catalog'].items()))),
        },
    ]
    merged_again, provenance_again, duplicate_count_again = (
        runner.merge_partition_traversals(reversed_insertion)
    )
    assert merged_again == merged
    assert provenance_again == provenance
    assert duplicate_count_again == duplicate_count


def test_paid_gate_blocks_below_50_and_above_4500_before_reviews_and_shortlist():
    c = core()
    below_discount = paid_item(discount=49, price=1000)
    above_price = paid_item(discount=90, price=4500.01)
    boundary = paid_item(discount=50, price=4500)

    assert c['paid_source_rejection_reason'](below_discount) == 'discount_below_minimum'
    assert c['paid_source_rejection_reason'](above_price) == 'price_above_maximum'
    assert c['paid_source_rejection_reason'](boundary) is None

    assert c['needs_review_enrichment'](below_discount, __import__('datetime').date.today()) is False
    assert c['needs_review_enrichment'](above_price, __import__('datetime').date.today()) is False
    assert c['needs_review_enrichment'](boundary, __import__('datetime').date.today()) is True

    below_broad, _ = c['broad_reasons'](below_discount, __import__('datetime').date.today())
    above_broad, _ = c['broad_reasons'](above_price, __import__('datetime').date.today())
    boundary_broad, fit_tags = c['broad_reasons'](boundary, __import__('datetime').date.today())
    assert below_broad == []
    assert above_broad == []
    assert boundary_broad

    below_refined = dict(below_discount, fit_tags=fit_tags, broad_reasons=boundary_broad)
    above_refined = dict(above_price, fit_tags=fit_tags, broad_reasons=boundary_broad)
    boundary_refined = dict(boundary, fit_tags=fit_tags, broad_reasons=boundary_broad)
    assert c['refined_reasons'](below_refined)[0] == []
    assert c['refined_reasons'](above_refined)[0] == []
    assert c['refined_reasons'](boundary_refined)[0]

    assert runner.row_meets_current_paid_gate(c, below_discount) is False
    assert runner.row_meets_current_paid_gate(c, above_price) is False
    assert runner.row_meets_current_paid_gate(c, boundary) is True


def test_kz_maxprice_validation_does_not_require_monotonic_price_asc():
    c = dict(core())

    def fake_get_page(
        start,
        sort_by,
        *,
        category1=None,
        maxprice_kzt=None,
        hidef2p=False,
    ):
        assert start == 0
        assert hidef2p is True
        if sort_by == 'Price_ASC':
            raise AssertionError(
                'validation must not rely on Steam Price_ASC monotonicity'
            )

        if category1 == '998' and maxprice_kzt == 4500:
            if sort_by == 'Price_DESC':
                return page(3, [
                    result_row(1, 4500),
                    # Real Steam Price_DESC can be locally out of order too;
                    # only the cap, not monotonic ordering, is authoritative.
                    result_row(2, 4300),
                ])
            if sort_by == 'Name_ASC':
                return page(3, [
                    result_row(3, 1000),
                    result_row(4, 4400),
                ])

        if category1 == '21' and maxprice_kzt == 4500 and sort_by == 'Price_DESC':
            return page(2, [
                result_row(20, 4499),
                result_row(21, 500),
            ])

        if category1 == '998' and maxprice_kzt is None and sort_by == 'Price_DESC':
            return page(6, [
                result_row(10, 6000),
                result_row(11, 4400),
            ])

        raise AssertionError(
            f'unexpected probe: category1={category1} '
            f'sort={sort_by} maxprice={maxprice_kzt}'
        )

    c['get_page'] = fake_get_page
    evidence = runner.validate_kz_source_price_bound(c)
    assert evidence['validated'] is True
    assert evidence['country_code'] == 'kz'
    assert evidence['maxprice_kzt'] == 4500
    assert evidence['price_asc_monotonicity_required'] is False
    assert evidence['partition_price_desc_checks']['games']['max_price_kzt'] == 4500
    assert evidence['partition_price_desc_checks']['dlc']['max_price_kzt'] == 4499
    assert tuple(evidence['partition_price_desc_checks']) == ('games', 'dlc')
    assert evidence['games_sort_invariant_check']['total_count'] == 3
    assert evidence['games_uncapped_control']['total_count'] == 6
    assert evidence['games_uncapped_control']['max_price_kzt'] == 6000
    assert evidence['logical_requests'] == 4


def test_kz_maxprice_validation_fails_closed_if_capped_partition_leaks_over_cap():
    c = dict(core())

    def fake_get_page(
        start,
        sort_by,
        *,
        category1=None,
        maxprice_kzt=None,
        hidef2p=False,
    ):
        assert start == 0
        assert hidef2p is True
        if maxprice_kzt == 4500 and sort_by == 'Price_DESC':
            if category1 == '998':
                return page(3, [result_row(1, 4500)])
            if category1 == '21':
                return page(2, [result_row(20, 4600)])
        raise AssertionError('validator should fail on DLC leak before controls')

    c['get_page'] = fake_get_page
    try:
        runner.validate_kz_source_price_bound(c)
    except RuntimeError as exc:
        assert 'dlc maxprice=4500 leaked 4600.0 KZT' in str(exc)
    else:
        raise AssertionError('over-cap capped row must fail closed')


def test_kz_maxprice_validation_fails_closed_if_filter_is_not_material():
    c = dict(core())

    def fake_get_page(
        start,
        sort_by,
        *,
        category1=None,
        maxprice_kzt=None,
        hidef2p=False,
    ):
        assert start == 0
        assert hidef2p is True
        if maxprice_kzt == 4500 and sort_by == 'Price_DESC':
            return page(3, [result_row(1, 4500)])
        if category1 == '998' and maxprice_kzt == 4500 and sort_by == 'Name_ASC':
            return page(3, [result_row(2, 1000)])
        if category1 == '998' and maxprice_kzt is None and sort_by == 'Price_DESC':
            return page(3, [result_row(3, 4500)])
        raise AssertionError('unexpected probe')

    c['get_page'] = fake_get_page
    try:
        runner.validate_kz_source_price_bound(c)
    except RuntimeError as exc:
        assert 'uncapped games control does not have a larger source total' in str(exc)
    else:
        raise AssertionError('ignored/non-material maxprice must fail closed')


def test_progress_reporter_exposes_stage_and_network_metrics():
    stats = {
        'search_http_requests': 21,
        'search_retry_events': 2,
        'search_429_events': 1,
        'search_backoff_seconds': 6.0,
        'review_http_requests': 100,
        'review_retry_events': 3,
        'review_429_events': 4,
        'review_backoff_seconds': 4.0,
    }
    reporter = runner.ProgressReporter(
        stats_provider=lambda: stats,
        heartbeat_seconds=999,
    )
    reporter.set_stage(
        'search_traversal',
        partition='games',
        page_number=20,
        rows_seen=1000,
        reported_total=5000,
        progress_percent=20.0,
        eligible_rows_after_local_gate=123,
        duplicate_rows=7,
    )
    snapshot = reporter.snapshot('test')
    assert snapshot['event'] == 'test'
    assert snapshot['stage'] == 'search_traversal'
    assert snapshot['partition'] == 'games'
    assert snapshot['page_number'] == 20
    assert snapshot['rows_seen'] == 1000
    assert snapshot['reported_total'] == 5000
    assert snapshot['progress_percent'] == 20.0
    assert snapshot['eligible_rows_after_local_gate'] == 123
    assert snapshot['duplicate_rows'] == 7
    assert snapshot['network'] == stats


def test_core_network_stats_expose_retry_and_backoff_counters():
    c = core()
    initial = c['network_stats_snapshot']()
    expected_keys = {
        'search_http_requests',
        'search_retry_events',
        'search_429_events',
        'search_backoff_seconds',
        'review_http_requests',
        'review_retry_events',
        'review_429_events',
        'review_backoff_seconds',
    }
    assert set(initial) == expected_keys
    c['bump_network_stat']('search_http_requests', 2)
    c['bump_network_stat']('review_backoff_seconds', 1.5)
    updated = c['network_stats_snapshot']()
    assert updated['search_http_requests'] == 2
    assert updated['review_backoff_seconds'] == 1.5


def test_search_pacing_matches_live_proven_rate_limit_safe_delay():
    assert runner.accelerator.ORIGINAL_SEARCH_DELAY_SECONDS == 0.9
    assert runner.accelerator.SEARCH_DELAY_SECONDS == 1.8


def test_free_giveaway_lane_remains_separate_from_paid_filters():
    policy = json.loads((ROOT / 'config/mailing_policy.json').read_text(encoding='utf-8'))
    paid = policy['paid_discovery']
    assert paid['free_or_giveaway_lane_is_separate'] is True
    assert paid['paid_filters_must_not_remove_free_or_giveaway_lane'] is True
    assert policy['freebies']['steam_feed_path'] == 'data/production/freebies.tsv'

    workflow = (ROOT / '.github/workflows/steam-test.yml').read_text(encoding='utf-8')
    paid_step = workflow.index('Collect Steam KZ catalog with partial publish failure isolation')
    giveaway_step = workflow.index('Build canonical Steam Epic GOG KZ giveaways')
    assert paid_step < giveaway_step
    assert 'python scripts/giveaway_production.py' in workflow


def test_discovery_scope_remains_github_owned_without_new_scheduler_or_top_n():
    ownership = json.loads(
        (ROOT / 'config/execution_ownership_contract.json').read_text(encoding='utf-8')
    )
    github = ownership['github_control_plane']
    assert github['owner'] == 'GitHub repository and GitHub Actions'
    assert 'decide the exact current production scope' in github['responsibilities']
    assert 'scope selection' in github['must_not_delegate']

    policy = json.loads((ROOT / 'config/mailing_policy.json').read_text(encoding='utf-8'))
    assert policy['paid_discovery']['raw_source_top_n'] is None
    assert policy['delivery']['fixed_top_n'] is None

    workflow = (ROOT / '.github/workflows/steam-test.yml').read_text(encoding='utf-8')
    assert workflow.count('\n  schedule:') == 1
    assert 'timeout-minutes: 60' in workflow


def test_mirrors_edge_catalyst_is_not_special_cased():
    for relative in (
        'scripts/steam_production.py',
        'scripts/steam_partial_publish_runner.py',
    ):
        text = (ROOT / relative).read_text(encoding='utf-8').casefold()
        assert '1233570' not in text
        assert "mirror's edge catalyst" not in text
        assert 'mirrors edge catalyst' not in text


def main():
    tests = [
        test_explicit_partitions_cover_supported_content_types_and_params,
        test_partition_merge_is_deterministic_and_preserves_representatives,
        test_paid_gate_blocks_below_50_and_above_4500_before_reviews_and_shortlist,
        test_kz_maxprice_validation_does_not_require_monotonic_price_asc,
        test_kz_maxprice_validation_fails_closed_if_capped_partition_leaks_over_cap,
        test_kz_maxprice_validation_fails_closed_if_filter_is_not_material,
        test_progress_reporter_exposes_stage_and_network_metrics,
        test_core_network_stats_expose_retry_and_backoff_counters,
        test_search_pacing_matches_live_proven_rate_limit_safe_delay,
        test_free_giveaway_lane_remains_separate_from_paid_filters,
        test_discovery_scope_remains_github_owned_without_new_scheduler_or_top_n,
        test_mirrors_edge_catalyst_is_not_special_cased,
    ]
    for test in tests:
        test()
        print(f'{test.__name__}: PASS')
    print(f'Steam discovery scope reduction regressions: {len(tests)}/{len(tests)} PASS')


if __name__ == '__main__':
    main()
