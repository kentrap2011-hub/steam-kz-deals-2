#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path

from build_russian_description_translation_queue import build_scope, write_scope
from ingest_russian_description_translations import (
    ingest_paths,
    load_submission,
    validate_submissions,
)
from russian_description_quality import classify_description
from russian_description_translation_runtime import (
    CACHE_CONTRACT_ID,
    RESULT_CONTRACT_ID,
    build_translation_request,
    empty_cache,
    empty_diagnostics,
    resolve_translation_diagnostic,
)

GOOD_RU_A = (
    'Тактическое приключение об исследовании заброшенной станции, поиске инструментов '
    'и осторожном побеге от опасных существ.'
)
GOOD_RU_C = (
    'Мрачная головоломка о старом городе, где нужно изучать улицы, находить подсказки '
    'и постепенно раскрывать скрытую тайну.'
)
PINNED_BAD_RU = (
    'Самое полное издание STAR WARS™ Battlefront™ включает STAR WARS™ Battlefront™ '
    'Deluxe Edition и Season Pass.'
)
PINNED_REQUEST_ID = '2aeac6b30b8bea9fcecd9be3269154b2bb4b84fefc3345986929ee9f4e23b76e'
PINNED_CHECKPOINT = Path(
    'data/ai_inbox/russian_descriptions/manual-one-shot-9b3f6d2c7a41.json'
)
PINNED_QUEUE = Path('data/production/pre_ai/chatgpt_ru_description_queue.jsonl')


def request(appid, source, title):
    return build_translation_request(
        {
            'description_status': 'needs_translation',
            'description_source_quality': 'non_ru',
            'description_source_appid': str(appid),
            'description_source_text': source,
            'description_source_path': f'fixture:{appid}',
        },
        title,
    )


def result(req, translated_text):
    return {
        'request_id': req['request_id'],
        'source_key': req['source_key'],
        'source_appid': req['source_appid'],
        'source_text_sha256': req['source_text_sha256'],
        'source_version': req['source_version'],
        'status': 'translated',
        'translated_text_ru': translated_text,
    }


def row(appid, title):
    return {
        'taste_subject_key': f'App_{appid}',
        'purchase': {'key': f'App_{appid}', 'title': title},
        'semantic_condition': {'base_appids': [str(appid)]},
    }


def metadata(appid, source, title):
    return {
        'entity_kind': 'app',
        'steam_id': str(appid),
        'store_name': title,
        'short_description': source,
    }


def cache_from(path):
    return json.loads(path.read_text(encoding='utf-8'))


def diagnostics_from(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    source_a = 'Explore an abandoned station and find a safe route out.'
    source_b = 'Fight across a distant galaxy, complete missions, and master several combat roles.'
    source_c = 'Investigate the old city, solve puzzles, and uncover its hidden mystery.'
    req_a = request('1', source_a, 'A')
    req_b = request('1237980', source_b, 'STAR WARS Battlefront')
    req_c = request('3', source_c, 'C')

    assert classify_description(PINNED_BAD_RU) != 'good_ru'

    rows = [
        row('1', 'A'),
        row('1237980', 'STAR WARS Battlefront'),
        row('3', 'C'),
    ]
    meta = {
        '1': metadata('1', source_a, 'A'),
        '1237980': metadata('1237980', source_b, 'STAR WARS Battlefront'),
        '3': metadata('3', source_c, 'C'),
    }
    media = {
        '1': {'short_description_source': source_a},
        '1237980': {'short_description_source': source_b},
        '3': {'short_description_source': source_c},
    }

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        queue_path = root / 'queue.jsonl'
        status_path = root / 'status.json'
        cache_path = root / 'russian_description_translations.json'
        diagnostics_path = root / 'russian_description_translation_diagnostics.json'
        submission_path = root / 'submission.json'

        initial_queue = [req_a, req_b, req_c]
        write_scope(
            initial_queue,
            {
                'status': 'translation_required',
                'untranslated_game_count': 3,
                'last_translation_attempt_at_utc': None,
                'last_successful_translation_at_utc': None,
            },
            queue_path,
            status_path,
        )
        cache_path.write_text(json.dumps(empty_cache()), encoding='utf-8')
        diagnostics_path.write_text(json.dumps(empty_diagnostics()), encoding='utf-8')
        submission_path.write_text(
            json.dumps(
                {
                    'contract': RESULT_CONTRACT_ID,
                    'schema_version': 1,
                    'results': [
                        result(req_a, GOOD_RU_A),
                        result(req_b, PINNED_BAD_RU),
                        result(req_c, GOOD_RU_C),
                    ],
                },
                ensure_ascii=False,
            ),
            encoding='utf-8',
        )

        # 1/2. A bad exact-bound quality result in the middle is isolated:
        # valid siblings persist and only B enters translation diagnostics.
        first_at = '2026-10-04T10:00:00+00:00'
        stats = ingest_paths(
            queue_path,
            cache_path,
            [submission_path],
            now_utc=first_at,
            status_path=status_path,
            diagnostics_path=diagnostics_path,
        )
        assert stats['accepted_count'] == 2
        assert stats['diagnostic_quarantined_count'] == 1
        cache = cache_from(cache_path)
        diagnostics = diagnostics_from(diagnostics_path)
        assert set(cache['entries']) == {req_a['request_id'], req_c['request_id']}
        assert set(diagnostics['entries']) == {req_b['request_id']}
        diag = diagnostics['entries'][req_b['request_id']]
        assert diag['state'] == 'active'
        assert diag['source_appid'] == '1237980'
        assert diag['source_text_sha256'] == req_b['source_text_sha256']
        assert diag['source_version'] == req_b['source_version']
        assert diag['diagnostic_reason'] == 'translated_text_quality_not_good_ru'
        assert diag['observed_quality'] != 'good_ru'
        assert diag['submitted_translated_text_ru'] == PINNED_BAD_RU

        # 3. Current exact diagnostic is removed from the ordinary translation queue.
        normal_queue, current_status = build_scope(
            rows,
            meta,
            cache,
            media,
            generated_at_utc='2026-10-04T10:01:00+00:00',
            diagnostics=diagnostics,
        )
        assert normal_queue == []
        assert current_status['queue_count'] == 0
        assert current_status['translation_diagnostic_count'] == 1
        assert current_status['translation_diagnostic_request_ids'] == [req_b['request_id']]
        assert current_status['untranslated_game_count'] == 1

        # 4a. Source/binding movement creates a new request identity and stale diagnostic
        # state cannot suppress it.
        changed_source_b = source_b + ' Updated source.'
        changed_meta = dict(meta)
        changed_meta['1237980'] = metadata(
            '1237980', changed_source_b, 'STAR WARS Battlefront'
        )
        changed_media = dict(media)
        changed_media['1237980'] = {'short_description_source': changed_source_b}
        changed_queue, changed_status = build_scope(
            rows,
            changed_meta,
            cache,
            changed_media,
            generated_at_utc='2026-10-04T10:02:00+00:00',
            diagnostics=diagnostics,
        )
        assert len(changed_queue) == 1
        assert changed_queue[0]['source_appid'] == '1237980'
        assert changed_queue[0]['request_id'] != req_b['request_id']
        assert changed_status['translation_diagnostic_count'] == 0

        # 4b. Direct ready_ru similarly makes the historical diagnostic non-current.
        direct_ru = (
            'Полноценное приключение во вселенной далёкой галактики, где игрок участвует '
            'в масштабных сражениях, выполняет задания и осваивает разные боевые роли.'
        )
        direct_media = dict(media)
        direct_media['1237980'] = {'short_description_source': direct_ru}
        direct_queue, direct_status = build_scope(
            rows,
            meta,
            cache,
            direct_media,
            generated_at_utc='2026-10-04T10:03:00+00:00',
            diagnostics=diagnostics,
        )
        assert direct_queue == []
        assert direct_status['translation_diagnostic_count'] == 0
        assert direct_status['untranslated_game_count'] == 0

        # 5. Explicit GitHub-owned resolution clears the exact diagnostic safely.
        resolved = resolve_translation_diagnostic(
            diagnostics,
            req_b['request_id'],
            '2026-10-04T10:04:00+00:00',
            'explicit_diagnostic_resolution',
        )
        assert resolved['entries'][req_b['request_id']]['state'] == 'resolved'
        resolved_queue, resolved_status = build_scope(
            rows,
            meta,
            cache,
            media,
            generated_at_utc='2026-10-04T10:05:00+00:00',
            diagnostics=resolved,
        )
        assert [item['request_id'] for item in resolved_queue] == [req_b['request_id']]
        assert resolved_status['translation_diagnostic_count'] == 0

        # 6. Re-ingest is idempotent for cache/diagnostic identity: no duplicate entries,
        # and the first quarantine timestamp remains stable.
        second_at = '2026-10-04T10:06:00+00:00'
        second = ingest_paths(
            queue_path,
            cache_path,
            [submission_path],
            now_utc=second_at,
            status_path=status_path,
            diagnostics_path=diagnostics_path,
        )
        assert second['accepted_count'] == 2
        assert second['diagnostic_quarantined_count'] == 1
        cache2 = cache_from(cache_path)
        diagnostics2 = diagnostics_from(diagnostics_path)
        assert len(cache2['entries']) == 2
        assert len(diagnostics2['entries']) == 1
        assert diagnostics2['entries'][req_b['request_id']]['quarantined_at_utc'] == first_at

    # 9. Identity/AppID/hash safety stays submission-level fail-closed: even a valid
    # sibling must not persist when another record has an unsafe exact-binding mismatch.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        queue_path = root / 'queue.jsonl'
        status_path = root / 'status.json'
        cache_path = root / 'russian_description_translations.json'
        diagnostics_path = root / 'russian_description_translation_diagnostics.json'
        submission_path = root / 'unsafe.json'
        write_scope(
            [req_a, req_b],
            {
                'status': 'translation_required',
                'untranslated_game_count': 2,
                'last_translation_attempt_at_utc': None,
                'last_successful_translation_at_utc': None,
            },
            queue_path,
            status_path,
        )
        cache_path.write_text(json.dumps(empty_cache()), encoding='utf-8')
        diagnostics_path.write_text(json.dumps(empty_diagnostics()), encoding='utf-8')
        unsafe = result(req_b, PINNED_BAD_RU)
        unsafe['source_appid'] = '999999'
        submission_path.write_text(
            json.dumps(
                {
                    'contract': RESULT_CONTRACT_ID,
                    'schema_version': 1,
                    'results': [result(req_a, GOOD_RU_A), unsafe],
                },
                ensure_ascii=False,
            ),
            encoding='utf-8',
        )
        try:
            ingest_paths(
                queue_path,
                cache_path,
                [submission_path],
                diagnostics_path=diagnostics_path,
            )
        except ValueError:
            pass
        else:
            raise AssertionError('unsafe exact-binding mismatch must reject submission')
        assert empty_cache() == cache_from(cache_path)
        assert empty_diagnostics() == diagnostics_from(diagnostics_path)

    # Pinned incident dry-run: use the already-submitted 20-result checkpoint without
    # changing its translations. Exact counts come from the corrected validation.
    if PINNED_CHECKPOINT.exists() and PINNED_QUEUE.exists():
        queue_rows = [
            json.loads(line)
            for line in PINNED_QUEUE.read_text(encoding='utf-8').splitlines()
            if line.strip()
        ]
        accepted, errors, diagnostic_events = validate_submissions(
            queue_rows,
            [(str(PINNED_CHECKPOINT), load_submission(PINNED_CHECKPOINT))],
        )
        total = len(load_submission(PINNED_CHECKPOINT)['results'])
        assert total == 20
        assert len(accepted) + len(errors) + len(diagnostic_events) == total
        diagnostic_ids = {event['request']['request_id'] for event in diagnostic_events}
        assert PINNED_REQUEST_ID in diagnostic_ids
        print(json.dumps({
            'pinned_checkpoint_result_count': total,
            'pinned_checkpoint_accepted_count': len(accepted),
            'pinned_checkpoint_error_count': len(errors),
            'pinned_checkpoint_diagnostic_count': len(diagnostic_events),
            'pinned_failed_request_in_diagnostics': True,
        }, sort_keys=True))

    print('Russian translation partial-accept/diagnostic regressions: ok')


if __name__ == '__main__':
    main()
