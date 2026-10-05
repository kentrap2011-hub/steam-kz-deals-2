import json

import steam_partial_publish_runner as runner


def core():
    return runner.load_core()


def test_conservative_global_display_percent_never_promotes_threshold_boundary():
    assert runner.conservative_global_display_percent(78) == 77.5
    assert runner.conservative_global_display_percent(79) == 78.5
    assert runner.conservative_global_display_percent(None) is None


def test_search_surface_reuse_is_limited_to_decisive_review_cases():
    low_count = {
        'search_review_count': 99,
        'search_review_positive': 55,
    }
    pair = runner.search_surface_review_pair(low_count, 90)
    assert pair is not None
    assert pair['global']['count'] == 99

    clears_every_rating_gate = {
        'search_review_count': 5000,
        'search_review_positive': 91,
    }
    pair = runner.search_surface_review_pair(clears_every_rating_gate, 90)
    assert pair is not None
    assert pair['global']['positive'] == 90.5

    ambiguous = {
        'search_review_count': 5000,
        'search_review_positive': 90,
    }
    assert runner.search_surface_review_pair(ambiguous, 90) is None


def test_storebrowse_pair_preserves_global_count_and_russian_display_semantics():
    pair = runner.storebrowse_review_pair({
        'reviews': {
            'summary_filtered': {'review_count': 5000, 'percent_positive': 78},
            'summary_language_specific': {'review_count': 700, 'percent_positive': 78},
        }
    })
    assert pair['global']['count'] == 5000
    assert pair['global']['display_positive'] == 78.0
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
    def __init__(self, payload=None, status_code=200, headers=None):
        self._payload = payload or {'response': {'store_items': []}}
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f'HTTP {self.status_code}')

    def json(self):
        return self._payload


def storebrowse_payload_for_call(kwargs):
    encoded = kwargs['params']['input_json']
    request_payload = json.loads(encoded)
    return [
        {
            'appid': spec['appid'],
            'reviews': {
                'summary_filtered': {
                    'review_count': 1000,
                    'percent_positive': 80,
                },
                'summary_language_specific': {
                    'review_count': 200,
                    'percent_positive': 81,
                },
            },
        }
        for spec in request_payload['ids']
    ]


def test_batch_fallback_uses_one_request_for_small_batch_without_network():
    original_get = runner.requests.get
    original_interval = runner.STORE_BROWSE_MIN_INTERVAL_SECONDS
    calls = []
    try:
        runner.STORE_BROWSE_MIN_INTERVAL_SECONDS = 0

        def fake_get(*args, **kwargs):
            calls.append((args, kwargs))
            return FakeResponse({
                'response': {
                    'store_items': storebrowse_payload_for_call(kwargs),
                }
            })

        runner.requests.get = fake_get
        result, stats = runner.fetch_storebrowse_review_fallback(['1', '2'])
    finally:
        runner.requests.get = original_get
        runner.STORE_BROWSE_MIN_INTERVAL_SECONDS = original_interval

    assert stats['physical_http_requests'] == 1
    assert stats['successful_batches'] == 1
    assert len(calls) == 1
    assert set(result) == {'1', '2'}
    assert result['1']['global']['positive'] == 79.5
    assert result['2']['russian']['ok'] is True


def test_storebrowse_429_retries_same_batch_and_keeps_prior_results():
    original_get = runner.requests.get
    original_sleep = runner.time.sleep
    original_interval = runner.STORE_BROWSE_MIN_INTERVAL_SECONDS
    calls = []
    sleeps = []
    try:
        runner.STORE_BROWSE_MIN_INTERVAL_SECONDS = 0
        runner.time.sleep = lambda seconds: sleeps.append(float(seconds))

        def fake_get(*args, **kwargs):
            calls.append((args, kwargs))
            ids = [
                spec['appid']
                for spec in json.loads(kwargs['params']['input_json'])['ids']
            ]
            if ids[0] == 101 and sum(1 for _, call in calls if json.loads(call['params']['input_json'])['ids'][0]['appid'] == 101) == 1:
                return FakeResponse(status_code=429, headers={'Retry-After': '2'})
            return FakeResponse({
                'response': {'store_items': storebrowse_payload_for_call(kwargs)}
            })

        runner.requests.get = fake_get
        appids = [str(value) for value in range(1, 102)]
        result, stats = runner.fetch_storebrowse_review_fallback(appids)
    finally:
        runner.requests.get = original_get
        runner.time.sleep = original_sleep
        runner.STORE_BROWSE_MIN_INTERVAL_SECONDS = original_interval

    assert len(result) == 101
    assert stats['physical_http_requests'] == 3
    assert stats['successful_batches'] == 2
    assert stats['failed_batches'] == 0
    assert stats['http_429_events'] == 1
    assert stats['retry_events'] == 1
    assert stats['backoff_seconds'] == 2.0
    assert 2.0 in sleeps


def test_storebrowse_failed_batch_isolated_without_discarding_siblings():
    original_get = runner.requests.get
    original_sleep = runner.time.sleep
    original_interval = runner.STORE_BROWSE_MIN_INTERVAL_SECONDS
    original_retries = runner.STORE_BROWSE_RETRIES
    try:
        runner.STORE_BROWSE_MIN_INTERVAL_SECONDS = 0
        runner.STORE_BROWSE_RETRIES = 2
        runner.time.sleep = lambda seconds: None

        def fake_get(*args, **kwargs):
            ids = [
                spec['appid']
                for spec in json.loads(kwargs['params']['input_json'])['ids']
            ]
            if ids[0] == 101:
                return FakeResponse(status_code=500)
            return FakeResponse({
                'response': {'store_items': storebrowse_payload_for_call(kwargs)}
            })

        runner.requests.get = fake_get
        appids = [str(value) for value in range(1, 202)]
        result, stats = runner.fetch_storebrowse_review_fallback(appids)
    finally:
        runner.requests.get = original_get
        runner.time.sleep = original_sleep
        runner.STORE_BROWSE_MIN_INTERVAL_SECONDS = original_interval
        runner.STORE_BROWSE_RETRIES = original_retries

    assert '1' in result
    assert '201' in result
    assert '101' not in result
    assert stats['successful_batches'] == 2
    assert stats['failed_batches'] == 1
    assert stats['physical_http_requests'] == 4


class ReviewResponse:
    def __init__(self, status_code=200, headers=None):
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f'HTTP {self.status_code}')

    def json(self):
        return {
            'success': 1,
            'query_summary': {
                'total_reviews': 1000,
                'total_positive': 800,
            },
        }


class ReviewSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def get(self, *args, **kwargs):
        self.calls += 1
        if not self.responses:
            raise AssertionError('unexpected extra review HTTP request')
        return self.responses.pop(0)


def test_appreviews_circuit_opens_on_four_consecutive_429_and_then_skips_http():
    c = core()
    session = ReviewSession([ReviewResponse(429) for _ in range(4)])
    c['get_review_session'] = lambda: session
    original_sleep = c['time'].sleep
    sleeps = []
    try:
        c['time'].sleep = lambda seconds: sleeps.append(float(seconds))
        result = c['get_review_summary']('1', 'all')
        assert result['rate_limited'] is True
        assert c['review_rate_limit_event'].is_set() is True
        stats = c['network_stats_snapshot']()
        assert session.calls == 4
        assert stats['review_http_requests'] == 4
        assert stats['review_429_events'] == 4
        assert stats['review_backoff_seconds'] == 7.0

        skipped = c['get_review_summary']('2', 'all')
        assert skipped['rate_limited'] is True
        stats = c['network_stats_snapshot']()
        assert session.calls == 4
        assert stats['review_circuit_skipped_components'] == 1
    finally:
        c['time'].sleep = original_sleep


def test_appreviews_retry_after_is_honoured_and_success_resets_429_streak():
    c = core()
    session = ReviewSession([
        ReviewResponse(429, headers={'Retry-After': '7'}),
        ReviewResponse(200),
        ReviewResponse(429),
        ReviewResponse(200),
    ])
    c['get_review_session'] = lambda: session
    original_sleep = c['time'].sleep
    sleeps = []
    try:
        c['time'].sleep = lambda seconds: sleeps.append(float(seconds))
        first = c['get_review_summary']('1', 'all')
        second = c['get_review_summary']('2', 'all')
    finally:
        c['time'].sleep = original_sleep

    assert first['ok'] is True
    assert second['ok'] is True
    assert c['review_rate_limit_event'].is_set() is False
    assert sleeps[0] == 7.0
    stats = c['network_stats_snapshot']()
    assert stats['review_http_requests'] == 4
    assert stats['review_429_events'] == 2
    assert stats['review_successful_components'] == 2


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
        test_search_surface_reuse_is_limited_to_decisive_review_cases,
        test_storebrowse_pair_preserves_global_count_and_russian_display_semantics,
        test_global_boundary_does_not_create_false_positive_but_russian_can_use_existing_rule,
        test_missing_russian_summary_does_not_block_valid_global_path,
        test_batch_fallback_uses_one_request_for_small_batch_without_network,
        test_storebrowse_429_retries_same_batch_and_keeps_prior_results,
        test_storebrowse_failed_batch_isolated_without_discarding_siblings,
        test_appreviews_circuit_opens_on_four_consecutive_429_and_then_skips_http,
        test_appreviews_retry_after_is_honoured_and_success_resets_429_streak,
        test_rate_limit_result_is_explicitly_non_ok,
    ]
    for test in tests:
        test()
        print(f'{test.__name__}: PASS')
    print(f'steam review fallback tests: {len(tests)}/{len(tests)} PASS')


if __name__ == '__main__':
    main()
