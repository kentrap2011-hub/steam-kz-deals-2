import json
import tempfile
from pathlib import Path

from steam_partial_publish import (
    FailureQueue,
    catalog_run_is_publishable,
    fetch_segments_resilient,
    preserve_last_known_good,
    process_individual_items,
)


def test_one_game_failure_does_not_stop_others():
    items = [{'key': 'App_1', 'value': 1}, {'key': 'App_2', 'value': 2}, {'key': 'App_3', 'value': 3}]
    def processor(item):
        if item['key'] == 'App_2':
            raise RuntimeError('broken item')
        return dict(item)
    result = process_individual_items(items, processor)
    assert {row['key'] for row in result['rows']} == {'App_1', 'App_3'}
    assert result['failure_reasons']['App_2'] == 'broken item'


def test_known_failed_game_keeps_old_data():
    previous = {'App_2': {'key': 'App_2', 'title': 'Known good', 'final_kzt': 999.0}}
    rows, preserved = preserve_last_known_good([{'key': 'App_1', 'title': 'Fresh'}], previous, {'App_2'})
    assert {row['key'] for row in rows} == {'App_1', 'App_2'}
    assert preserved == ['App_2']
    assert next(row for row in rows if row['key'] == 'App_2')['final_kzt'] == 999.0


def test_segment_failure_is_separate_and_does_not_stop():
    segments = [{'start': 0}, {'start': 50}, {'start': 100}]
    def fetcher(segment):
        if segment['start'] == 50:
            raise RuntimeError('segment timeout')
        return [segment['start']]
    successful, failed = fetch_segments_resilient(segments, fetcher)
    assert [segment['start'] for segment, _ in successful] == [0, 100]
    assert failed == [({'start': 50}, 'segment timeout')]


def test_live_total_drift_is_informational():
    assert catalog_run_is_publishable(reached_end=True, unique_count=17036, reported_total=17037) is True
    assert catalog_run_is_publishable(reached_end=True, unique_count=17038, reported_total=17037) is True


def test_failures_persist_and_are_summarized():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / 'failures.json'
        q1 = FailureQueue(path, run_ref='run-1', now_fn=lambda: '2026-09-11T00:00:00+00:00')
        q1.record_game('App_9', appid='9', name='Nine', stage='review_enrichment', error=RuntimeError('review failed'), prior_site_data_exists=True)
        q1.record_segment(sort_by='Name_ASC', start=50, count=50, error=RuntimeError('page failed'))
        q1.write()
        q2 = FailureQueue(path, run_ref='run-2', now_fn=lambda: '2026-09-12T00:00:00+00:00')
        summary = q2.summary(123)
        assert summary == {
            'processed_successfully': 123,
            'problematic_games': 1,
            'problematic_catalog_segments': 1,
            'game_failures_this_run': 0,
            'catalog_segment_failures_this_run': 0,
        }
        payload = json.loads(path.read_text(encoding='utf-8'))
        assert payload['unresolved_games']['App_9']['root_error'] == 'review failed'
        assert payload['unresolved_catalog_segments']['Name_ASC:start=50:count=50']['root_error'] == 'page failed'


def main():
    tests = [
        test_one_game_failure_does_not_stop_others,
        test_known_failed_game_keeps_old_data,
        test_segment_failure_is_separate_and_does_not_stop,
        test_live_total_drift_is_informational,
        test_failures_persist_and_are_summarized,
    ]
    for test in tests:
        test()
        print(f'{test.__name__}: PASS')
    print(f'Steam partial publish regressions: {len(tests)}/{len(tests)} PASS')


if __name__ == '__main__':
    main()
