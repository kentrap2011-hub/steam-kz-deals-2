import steam_partial_publish_runner as runner


def core():
    return runner.load_core()


def test_conservative_global_display_percent_never_promotes_threshold_boundary():
    assert runner.conservative_global_display_percent(78) == 77.5
    assert runner.conservative_global_display_percent(79) == 78.5
    assert runner.conservative_global_display_percent(None) is None


def test_storebrowse_pair_preserves_global_count_and_russian_display_semantics():
    pair = runner.storebrowse_review_pair({
        'reviews': {
            'summary_filtered': {'review_count': 5000, 'percent_positive': 78},
            'summary_language_specific': {'review_count': 700, 'percent_positive': 78},
        }
    })
    assert pair['global']['count'] == 5000
    assert pair['global']['positive'] == 77.5
    assert pair['russian']['count'] == 700
    assert pair['russian']['positive'] == 78.0


def test_global_boundary_does_not_create_false_positive_but_russian_can_use_existing_rule():
    c = core()
    pair = runner.storebrowse_review_pair({
        'reviews': {
            'summary_filtered': {'review_count': 5000, 'percent_positive': 78},
            'summary_language_specific': {'review_count': 700, 'percent_positive': 78},
        }
    })
    item = {
        'global_review_positive': pair['global']['positive'],
        'global_review_count': pair['global']['count'],
        'russian_review_positive': None,
        'russian_review_count': 0,
    }
    assert c['review_passes'](item, 1500, 78) is False

    item['russian_review_positive'] = pair['russian']['positive']
    item['russian_review_count'] = pair['russian']['count']
    assert c['review_passes'](item, 1500, 78) is True


def test_missing_russian_summary_does_not_block_valid_global_path():
    c = core()
    pair = runner.storebrowse_review_pair({
        'reviews': {
            'summary_filtered': {'review_count': 6000, 'percent_positive': 82},
        }
    })
    assert pair['russian']['ok'] is True
    assert pair['russian']['count'] == 0
    item = {
        'global_review_positive': pair['global']['positive'],
        'global_review_count': pair['global']['count'],
        'russian_review_positive': pair['russian']['positive'],
        'russian_review_count': pair['russian']['count'],
    }
    assert c['review_passes'](item, 1500, 80) is True


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            'response': {
                'store_items': [
                    {
                        'appid': 1,
                        'reviews': {
                            'summary_filtered': {'review_count': 1000, 'percent_positive': 80},
                            'summary_language_specific': {'review_count': 200, 'percent_positive': 81},
                        },
                    },
                    {
                        'appid': 2,
                        'reviews': {
                            'summary_filtered': {'review_count': 3000, 'percent_positive': 90},
                        },
                    },
                ]
            }
        }


def test_batch_fallback_uses_one_request_for_small_batch_without_network():
    original = runner.requests.get
    calls = []
    try:
        def fake_get(*args, **kwargs):
            calls.append((args, kwargs))
            return FakeResponse()
        runner.requests.get = fake_get
        result, request_count = runner.fetch_storebrowse_review_fallback(['1', '2'])
    finally:
        runner.requests.get = original

    assert request_count == 1
    assert len(calls) == 1
    assert set(result) == {'1', '2'}
    assert result['1']['global']['positive'] == 79.5
    assert result['2']['russian']['ok'] is True


def test_rate_limit_result_is_explicitly_non_ok():
    c = core()
    value = c['rate_limited_review_result']()
    assert value == {
        'ok': False,
        'positive': None,
        'count': 0,
        'rate_limited': True,
    }


def main():
    tests = [
        test_conservative_global_display_percent_never_promotes_threshold_boundary,
        test_storebrowse_pair_preserves_global_count_and_russian_display_semantics,
        test_global_boundary_does_not_create_false_positive_but_russian_can_use_existing_rule,
        test_missing_russian_summary_does_not_block_valid_global_path,
        test_batch_fallback_uses_one_request_for_small_batch_without_network,
        test_rate_limit_result_is_explicitly_non_ok,
    ]
    for test in tests:
        test()
        print(f'{test.__name__}: PASS')
    print(f'steam review fallback tests: {len(tests)}/{len(tests)} PASS')


if __name__ == '__main__':
    main()
