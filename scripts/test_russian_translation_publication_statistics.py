#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path

import progressive_personalization as progressive
from build_russian_description_translation_queue import (
    build_scope,
    record_translation_attempt,
    translation_observability,
    write_scope,
)
from ingest_russian_description_translations import ingest_paths
from russian_description_translation_runtime import (
    RESULT_CONTRACT_ID,
    empty_cache,
)
from validate_russian_descriptions import validate as validate_russian_descriptions


GOOD_RU = (
    'Мрачное приключение с исследованием заброшенного комплекса, поиском подсказок '
    'и осторожным продвижением через опасные помещения.'
)
ENGLISH_1 = 'Explore a strange station and escape the creatures hunting you.'
ENGLISH_2 = 'Investigate the old city, solve puzzles, and uncover a hidden mystery.'


def row(appid, title):
    return {
        'taste_subject_key': f'App_{appid}',
        'purchase': {'key': f'App_{appid}', 'title': title},
        'semantic_condition': {'base_appids': [str(appid)]},
    }


def metadata(appid, text, title):
    return {
        str(appid): {
            'entity_kind': 'app',
            'steam_id': str(appid),
            'store_name': title,
            'short_description': text,
        }
    }


def translated_result(request):
    return {
        'request_id': request['request_id'],
        'source_key': request['source_key'],
        'source_appid': request['source_appid'],
        'source_text_sha256': request['source_text_sha256'],
        'source_version': request['source_version'],
        'status': 'translated',
        'translated_text_ru': GOOD_RU,
    }


def error_result(request):
    return {
        'request_id': request['request_id'],
        'source_key': request['source_key'],
        'source_appid': request['source_appid'],
        'source_text_sha256': request['source_text_sha256'],
        'source_version': request['source_version'],
        'status': 'error',
        'error_code': 'semantic_translation_failed',
    }


def main():
    rows = [row('1', 'One'), row('2', 'Two')]
    meta = {}
    meta.update(metadata('1', ENGLISH_1, 'One'))
    meta.update(metadata('2', ENGLISH_2, 'Two'))
    media = {
        '1': {'short_description_source': ENGLISH_1},
        '2': {'short_description_source': ENGLISH_2},
    }

    # 1. Current untranslated count is producer-owned and counts current scope rows,
    # not browser cards or worker claims.
    queue, status = build_scope(
        rows, meta, empty_cache(), media, generated_at_utc='2026-09-29T08:00:00+00:00'
    )
    assert len(queue) == 2
    assert status['untranslated_game_count'] == 2
    assert status['last_translation_attempt_at_utc'] is None
    assert status['last_successful_translation_at_utc'] is None

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        queue_path = root / 'queue.jsonl'
        status_path = root / 'status.json'
        cache_path = root / 'cache.json'
        submission = root / 'submission.json'
        write_scope(queue, status, queue_path, status_path)
        cache_path.write_text(json.dumps(empty_cache()), encoding='utf-8')

        # 2. Accepted exact-bound translation advances attempt + success.
        submission.write_text(
            json.dumps(
                {
                    'contract': RESULT_CONTRACT_ID,
                    'schema_version': 1,
                    'results': [translated_result(queue[0])],
                },
                ensure_ascii=False,
            ),
            encoding='utf-8',
        )
        accepted_at = '2026-09-29T08:05:00+00:00'
        stats = ingest_paths(
            queue_path,
            cache_path,
            [submission],
            now_utc=accepted_at,
            status_path=status_path,
        )
        assert stats['accepted_count'] == 1
        stamped = json.loads(status_path.read_text(encoding='utf-8'))
        assert stamped['last_translation_attempt_at_utc'] == accepted_at
        assert stamped['last_successful_translation_at_utc'] == accepted_at

        # 3. Rebuilding current scope after that partial success keeps the remaining
        # untranslated count honest instead of treating the whole batch as complete.
        cache = json.loads(cache_path.read_text(encoding='utf-8'))
        remaining_queue, remaining_status = build_scope(
            rows, meta, cache, media, generated_at_utc='2026-09-29T08:06:00+00:00'
        )
        remaining_status = translation_observability(
            remaining_status, previous_status=stamped
        )
        assert len(remaining_queue) == 1
        assert remaining_status['untranslated_game_count'] == 1
        assert remaining_status['last_translation_attempt_at_utc'] == accepted_at
        assert remaining_status['last_successful_translation_at_utc'] == accepted_at
        write_scope(remaining_queue, remaining_status, queue_path, status_path)

        # 4. A valid exact-bound worker error is an attempt, but not a success.
        failed_at = '2026-09-29T08:10:00+00:00'
        submission.write_text(
            json.dumps(
                {
                    'contract': RESULT_CONTRACT_ID,
                    'schema_version': 1,
                    'results': [error_result(remaining_queue[0])],
                }
            ),
            encoding='utf-8',
        )
        failed_stats = ingest_paths(
            queue_path,
            cache_path,
            [submission],
            now_utc=failed_at,
            status_path=status_path,
        )
        assert failed_stats['accepted_count'] == 0
        assert failed_stats['error_count'] == 1
        failed_status = json.loads(status_path.read_text(encoding='utf-8'))
        assert failed_status['last_translation_attempt_at_utc'] == failed_at
        assert failed_status['last_successful_translation_at_utc'] == accepted_at
        assert failed_status['untranslated_game_count'] == 1

        # 5. A zero-work current scope check is both an attempt/check and a success.
        zero_rows = [row('3', 'Three')]
        zero_meta = metadata('3', GOOD_RU, 'Three')
        zero_media = {'3': {'short_description_source': GOOD_RU}}
        zero_queue, zero_status = build_scope(
            zero_rows,
            zero_meta,
            empty_cache(),
            zero_media,
            generated_at_utc='2026-09-29T08:20:00+00:00',
        )
        assert zero_queue == []
        zero_status = translation_observability(
            zero_status,
            previous_status=failed_status,
            check_at_utc='2026-09-29T08:20:00+00:00',
            zero_work_check=True,
        )
        assert zero_status['untranslated_game_count'] == 0
        assert zero_status['last_translation_attempt_at_utc'] == '2026-09-29T08:20:00+00:00'
        assert zero_status['last_successful_translation_at_utc'] == '2026-09-29T08:20:00+00:00'

        # 6. Producer projection consumes only canonical status facts. Legacy status
        # without the new count still derives it from existing scope arithmetic.
        producer_status = {
            'scope_record_count': 2,
            'unique_base_app_key_count': 2,
            'resolved_direct_ru_count': 0,
            'resolved_translation_cache_count': 1,
            'last_translation_attempt_at_utc': failed_at,
            'last_successful_translation_at_utc': accepted_at,
        }
        producer_path = root / 'producer-status.json'
        producer_path.write_text(json.dumps(producer_status), encoding='utf-8')
        original_status_path = progressive.RUSSIAN_TRANSLATION_STATUS
        try:
            progressive.RUSSIAN_TRANSLATION_STATUS = producer_path
            metrics = progressive._translation_processing_metrics()
        finally:
            progressive.RUSSIAN_TRANSLATION_STATUS = original_status_path
        assert metrics['translation_observability'] == 'available'
        assert metrics['untranslated_game_count'] == 1
        assert metrics['last_translation_attempt_at_utc'] == failed_at
        assert metrics['last_successful_translation_at_utc'] == accepted_at

        # 7. Missing translation remains explicitly invalid as Russian. Strict
        # validation still fails when requested, while the publication workflow may
        # explicitly use nonblocking diagnostic mode without relabelling the card.
        visual = root / 'visual.json'
        card = {
            'id': 'game:1',
            'title': 'One',
            'analysis_state': 'analyzed_fit',
            'summary': None,
            'description_status': 'needs_translation',
        }
        visual.write_text(json.dumps({'items': [card]}), encoding='utf-8')
        try:
            validate_russian_descriptions(visual)
        except SystemExit:
            pass
        else:
            raise AssertionError('strict Russian validation must still reject unresolved text')
        diagnostic = validate_russian_descriptions(visual, allow_untranslated=True)
        assert diagnostic['invalid_count'] == 1
        assert diagnostic['publication_blocking'] is False
        unchanged = json.loads(visual.read_text(encoding='utf-8'))['items'][0]
        assert unchanged['summary'] is None
        assert unchanged['description_status'] == 'needs_translation'

    # 8. Publication and post-attempt refresh must be explicit GitHub workflow
    # behavior; the browser is not allowed to create either fact.
    build_workflow = Path('.github/workflows/build-daily-visual-payload.yml').read_text(
        encoding='utf-8'
    )
    ingest_workflow = Path(
        '.github/workflows/ingest-russian-description-translations.yml'
    ).read_text(encoding='utf-8')
    deploy_workflow = Path('.github/workflows/deploy-visual.yml').read_text(encoding='utf-8')
    assert '--allow-untranslated' in build_workflow
    assert '--allow-untranslated' in deploy_workflow
    assert 'Require meaningful Russian descriptions before canonical commit' not in build_workflow
    assert 'Require meaningful Russian descriptions for general visual changes' not in deploy_workflow
    assert "steps.ingest.outputs.submission_count != '0'" in ingest_workflow

    print('Russian translation nonblocking publication/statistics regression: ok')


if __name__ == '__main__':
    main()
