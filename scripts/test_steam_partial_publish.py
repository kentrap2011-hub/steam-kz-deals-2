import json
import tempfile
from pathlib import Path

from steam_partial_publish import (
    FailureQueue,
    catalog_run_is_publishable,
    fetch_segments_resilient,
    preserve_last_known_good,
    process_individual_items,
    source_coverage_metadata,
)


def test_one_game_failure_does_not_stop_others():
    items = [
        {'key': 'App_1', 'value': 1},
        {'key': 'App_2', 'value': 2},
        {'key': 'App_3', 'value': 3},
    ]

    def processor(item):
        if item['key'] == 'App_2':
            raise RuntimeError('broken item')
        return dict(item)

    result = process_individual_items(items, processor)
    assert {row['key'] for row in result['rows']} == {'App_1', 'App_3'}
    assert result['failure_reasons']['App_2'] == 'broken item'


def test_known_failed_game_keeps_old_data():
    previous = {
        'App_2': {
            'key': 'App_2',
            'title': 'Known good',
            'final_kzt': 999.0,
        }
    }
    rows, preserved = preserve_last_known_good(
        [{'key': 'App_1', 'title': 'Fresh'}],
        previous,
        {'App_2'},
    )
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


def test_failed_segment_marks_source_partial():
    partial = source_coverage_metadata(1)
    assert partial == {
        'source_complete': False,
        'source_has_known_gaps': True,
        'known_gap_count': 1,
        'source_status': 'partial',
    }
    complete = source_coverage_metadata(0)
    assert complete['source_complete'] is True
    assert complete['source_has_known_gaps'] is False
    assert complete['source_status'] == 'complete'


def test_live_total_drift_is_informational():
    assert catalog_run_is_publishable(
        reached_end=True,
        unique_count=17036,
        reported_total=17037,
    ) is True
    assert catalog_run_is_publishable(
        reached_end=True,
        unique_count=17038,
        reported_total=17037,
    ) is True


def test_failures_persist_and_are_summarized():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / 'failures.json'
        q1 = FailureQueue(
            path,
            run_ref='run-1',
            now_fn=lambda: '2026-09-11T00:00:00+00:00',
        )
        q1.record_game(
            'App_9',
            appid='9',
            name='Nine',
            stage='review_enrichment',
            error=RuntimeError('review failed'),
            prior_site_data_exists=True,
        )
        q1.record_segment(
            sort_by='Name_ASC',
            start=50,
            count=50,
            error=RuntimeError('page failed'),
        )
        q1.write()

        q2 = FailureQueue(
            path,
            run_ref='run-2',
            now_fn=lambda: '2026-09-12T00:00:00+00:00',
        )
        summary = q2.summary(123)
        assert summary == {
            'processed_successfully': 123,
            'problematic_games': 1,
            'problematic_catalog_segments': 1,
            'problematic_system_state': 0,
            'game_failures_this_run': 0,
            'catalog_segment_failures_this_run': 0,
            'failure_queue_recovery_this_run': False,
        }
        payload = json.loads(path.read_text(encoding='utf-8'))
        assert payload['unresolved_games']['App_9']['root_error'] == 'review failed'
        assert (
            payload['unresolved_catalog_segments']
            ['Name_ASC:start=50:count=50']['root_error']
            == 'page failed'
        )


def test_corrupt_failure_queue_is_quarantined_and_recorded():
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / 'failures.json'
        corrupt_bytes = b'{this is not valid json'
        path.write_bytes(corrupt_bytes)

        queue = FailureQueue(
            path,
            run_ref='run-corrupt',
            now_fn=lambda: '2026-09-11T12:34:56+00:00',
        )

        assert not path.exists(), 'corrupt active queue must leave the working path'
        assert queue.load_incident is not None
        assert queue.summary(0)['problematic_system_state'] == 1
        problem = queue.state['system_problems'][0]
        assert problem['problem_type'] == 'failure_queue_unreadable'
        assert problem['original_path'] == str(path)
        quarantine_path = Path(problem['quarantined_path'])
        assert quarantine_path.exists()
        assert quarantine_path.read_bytes() == corrupt_bytes

        queue.write()
        assert path.exists(), 'fresh active queue is created only after quarantine/recovery'
        reloaded = json.loads(path.read_text(encoding='utf-8'))
        assert len(reloaded['system_problems']) == 1
        assert reloaded['system_problems'][0]['quarantined_path'] == str(quarantine_path)


def main():
    tests = [
        test_one_game_failure_does_not_stop_others,
        test_known_failed_game_keeps_old_data,
        test_segment_failure_is_separate_and_does_not_stop,
        test_failed_segment_marks_source_partial,
        test_live_total_drift_is_informational,
        test_failures_persist_and_are_summarized,
        test_corrupt_failure_queue_is_quarantined_and_recorded,
    ]
    for test in tests:
        test()
        print(f'{test.__name__}: PASS')
    print(f'Steam partial publish regressions: {len(tests)}/{len(tests)} PASS')


if __name__ == '__main__':
    main()
