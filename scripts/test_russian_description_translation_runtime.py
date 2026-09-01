#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

from build_russian_description_translation_queue import build_scope, write_scope
from ingest_russian_description_translations import ingest_paths
from russian_description_translation_runtime import (
    CACHE_CONTRACT_ID,
    RESULT_CONTRACT_ID,
    build_translation_request,
    empty_cache,
    resolve_description_for_appids,
    source_binding,
)

GOOD_RU = 'Тактическое приключение о побеге с заброшенной станции, где нужно исследовать помещения, искать инструменты и находить безопасный путь вперёд.'
GOOD_RU_2 = 'Мрачное приключение с исследованием старого города, поиском подсказок и последовательным раскрытием тайны, которая меняет происходящее вокруг героя.'


def metadata(appid, description, title='Fixture Game'):
    return {
        str(appid): {
            'entity_kind': 'app',
            'steam_id': str(appid),
            'store_name': title,
            'short_description': description,
        }
    }


def row(appid, title='Fixture Game'):
    return {
        'taste_subject_key': f'App_{appid}',
        'purchase': {'key': f'App_{appid}', 'title': title},
        'semantic_condition': {'base_appids': [str(appid)]},
    }


def result_for(request, translated=GOOD_RU):
    return {
        'request_id': request['request_id'],
        'source_key': request['source_key'],
        'source_appid': request['source_appid'],
        'source_text_sha256': request['source_text_sha256'],
        'source_version': request['source_version'],
        'status': 'translated',
        'translated_text_ru': translated,
    }


class TranslationRuntimeTests(unittest.TestCase):
    def test_queue_contains_only_unresolved_translatable(self):
        rows = [row('1', 'English Source'), row('2', 'Russian Source'), row('3', 'Missing Source')]
        meta = {}
        meta.update(metadata('1', 'Explore a strange station and escape the creatures hunting you.', 'English Source'))
        meta.update(metadata('2', GOOD_RU, 'Russian Source'))
        meta.update(metadata('3', None, 'Missing Source'))
        media = {
            '1': {'short_description_source': 'Explore a strange station and escape the creatures hunting you.'},
            '2': {'short_description_source': GOOD_RU},
            '3': {'short_description_source': None},
        }
        queue, status = build_scope(rows, meta, empty_cache(), media, generated_at_utc='2026-09-01T00:00:00Z')
        self.assertEqual([x['source_key'] for x in queue], ['App_1'])
        self.assertEqual(status['queue_count'], 1)
        self.assertEqual(status['resolved_direct_ru_count'], 1)
        self.assertEqual(status['nontranslatable_blocker_count'], 1)
        self.assertEqual(status['queue_request_ids'], [queue[0]['request_id']])

    def test_source_change_invalidates_identity(self):
        a = source_binding('App_1', 'Explore the station and escape.')
        b = source_binding('App_1', 'Explore the station and escape before dawn.')
        c = source_binding('App_2', 'Explore the station and escape.')
        self.assertNotEqual(a['request_id'], b['request_id'])
        self.assertNotEqual(a['request_id'], c['request_id'])
        self.assertNotEqual(a['source_text_sha256'], b['source_text_sha256'])

    def test_good_result_ingests_to_exact_cache(self):
        request = build_translation_request({
            'description_status': 'needs_translation',
            'description_source_quality': 'non_ru',
            'description_source_appid': '1',
            'description_source_text': 'Explore the station and escape the creatures hunting you.',
            'description_source_path': 'fixture',
        }, 'Fixture Game')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            queue_path = root / 'queue.jsonl'
            status_path = root / 'status.json'
            cache_path = root / 'cache.json'
            submission = root / 'submission.json'
            write_scope([request], {'status': 'translation_required'}, queue_path, status_path)
            cache_path.write_text(json.dumps(empty_cache()), encoding='utf-8')
            submission.write_text(json.dumps({
                'contract': RESULT_CONTRACT_ID,
                'schema_version': 1,
                'results': [result_for(request)],
            }), encoding='utf-8')
            stats = ingest_paths(queue_path, cache_path, [submission], now_utc='2026-09-01T00:00:00Z')
            self.assertEqual(stats['accepted_count'], 1)
            cache = json.loads(cache_path.read_text(encoding='utf-8'))
            entry = cache['entries'][request['request_id']]
            self.assertEqual(entry['source_text_sha256'], request['source_text_sha256'])
            self.assertEqual(entry['validated_quality'], 'good_ru')
            self.assertEqual(entry['result_contract'], RESULT_CONTRACT_ID)

    def test_stale_and_unknown_results_are_rejected(self):
        request = build_translation_request({
            'description_status': 'needs_translation',
            'description_source_quality': 'non_ru',
            'description_source_appid': '1',
            'description_source_text': 'Explore the station and escape.',
            'description_source_path': 'fixture',
        }, 'Fixture Game')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            queue_path = root / 'queue.jsonl'
            status_path = root / 'status.json'
            cache_path = root / 'cache.json'
            write_scope([request], {'status': 'translation_required'}, queue_path, status_path)
            cache_path.write_text(json.dumps(empty_cache()), encoding='utf-8')

            stale = result_for(request)
            stale['source_text_sha256'] = '0' * 64
            submission = root / 'stale.json'
            submission.write_text(json.dumps({'contract': RESULT_CONTRACT_ID, 'schema_version': 1, 'results': [stale]}), encoding='utf-8')
            with self.assertRaises(ValueError):
                ingest_paths(queue_path, cache_path, [submission])

            unknown = result_for(request)
            unknown['request_id'] = 'f' * 64
            submission.write_text(json.dumps({'contract': RESULT_CONTRACT_ID, 'schema_version': 1, 'results': [unknown]}), encoding='utf-8')
            with self.assertRaises(ValueError):
                ingest_paths(queue_path, cache_path, [submission])

    def test_duplicate_request_is_rejected(self):
        request = build_translation_request({
            'description_status': 'needs_translation',
            'description_source_quality': 'non_ru',
            'description_source_appid': '1',
            'description_source_text': 'Explore the station and escape.',
            'description_source_path': 'fixture',
        }, 'Fixture Game')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            queue_path = root / 'queue.jsonl'
            status_path = root / 'status.json'
            cache_path = root / 'cache.json'
            submission = root / 'dup.json'
            write_scope([request], {'status': 'translation_required'}, queue_path, status_path)
            cache_path.write_text(json.dumps(empty_cache()), encoding='utf-8')
            submission.write_text(json.dumps({
                'contract': RESULT_CONTRACT_ID,
                'schema_version': 1,
                'results': [result_for(request), result_for(request, GOOD_RU_2)],
            }), encoding='utf-8')
            with self.assertRaises(ValueError):
                ingest_paths(queue_path, cache_path, [submission])

    def test_placeholder_and_non_russian_results_are_rejected(self):
        request = build_translation_request({
            'description_status': 'needs_translation',
            'description_source_quality': 'non_ru',
            'description_source_appid': '1',
            'description_source_text': 'Explore the station and escape.',
            'description_source_path': 'fixture',
        }, 'Fixture Game')
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            queue_path = root / 'queue.jsonl'
            status_path = root / 'status.json'
            cache_path = root / 'cache.json'
            submission = root / 'bad.json'
            write_scope([request], {'status': 'translation_required'}, queue_path, status_path)
            cache_path.write_text(json.dumps(empty_cache()), encoding='utf-8')
            for bad_text in [
                'Русское краткое описание для этой игры пока не подготовлено.',
                'Explore the station and escape before the creatures find you.',
            ]:
                submission.write_text(json.dumps({
                    'contract': RESULT_CONTRACT_ID,
                    'schema_version': 1,
                    'results': [result_for(request, bad_text)],
                }), encoding='utf-8')
                with self.assertRaises(ValueError):
                    ingest_paths(queue_path, cache_path, [submission])

    def test_resolver_uses_exact_cache_and_misses_after_source_change(self):
        source = 'Explore the station and escape the creatures hunting you.'
        request = build_translation_request({
            'description_status': 'needs_translation',
            'description_source_quality': 'non_ru',
            'description_source_appid': '1',
            'description_source_text': source,
            'description_source_path': 'fixture',
        }, 'Fixture Game')
        cache = {
            'schema_version': 1,
            'contract': CACHE_CONTRACT_ID,
            'updated_at_utc': '2026-09-01T00:00:00Z',
            'entries': {
                request['request_id']: {
                    'request_id': request['request_id'],
                    'source_key': request['source_key'],
                    'source_appid': request['source_appid'],
                    'source_text_sha256': request['source_text_sha256'],
                    'source_version': request['source_version'],
                    'translated_text_ru': GOOD_RU,
                    'target_locale': 'ru',
                    'validated_quality': 'good_ru',
                    'result_contract': RESULT_CONTRACT_ID,
                    'ingested_at_utc': '2026-09-01T00:00:00Z',
                }
            },
        }
        meta = metadata('1', source)
        media = {'1': {'short_description_source': source}}
        resolved = resolve_description_for_appids(['1'], media, meta, cache)
        self.assertEqual(resolved['description_source_locale'], 'translation_cache')
        self.assertEqual(resolved['summary'], GOOD_RU)

        changed = 'Explore the station, find the reactor, and escape before dawn.'
        changed_meta = metadata('1', changed)
        changed_media = {'1': {'short_description_source': changed}}
        unresolved = resolve_description_for_appids(['1'], changed_media, changed_meta, cache)
        self.assertEqual(unresolved['description_status'], 'needs_translation')
        self.assertIsNone(unresolved['summary'])

    def test_direct_current_russian_has_priority_over_cache(self):
        english = 'Explore the station and escape the creatures hunting you.'
        request = build_translation_request({
            'description_status': 'needs_translation',
            'description_source_quality': 'non_ru',
            'description_source_appid': '1',
            'description_source_text': english,
            'description_source_path': 'fixture',
        }, 'Fixture Game')
        cache = {
            'schema_version': 1,
            'contract': CACHE_CONTRACT_ID,
            'updated_at_utc': '2026-09-01T00:00:00Z',
            'entries': {request['request_id']: {
                'request_id': request['request_id'], 'source_key': 'App_1', 'source_appid': '1',
                'source_text_sha256': request['source_text_sha256'], 'source_version': request['source_version'],
                'translated_text_ru': GOOD_RU, 'target_locale': 'ru', 'validated_quality': 'good_ru',
                'result_contract': RESULT_CONTRACT_ID, 'ingested_at_utc': '2026-09-01T00:00:00Z',
            }},
        }
        direct = resolve_description_for_appids(['1'], {'1': {'short_description_source': GOOD_RU_2}}, metadata('1', english), cache)
        self.assertEqual(direct['description_source_locale'], 'russian')
        self.assertEqual(direct['summary'], GOOD_RU_2)

    def test_production_like_synthetic_fixture_end_to_end(self):
        rows = [row('42', 'Synthetic Station')]
        english = 'Explore a hostile orbital station, solve environmental puzzles, and escape before the reactor fails.'
        meta = metadata('42', english, 'Synthetic Station')
        media = {'42': {'short_description_source': english}}
        queue, status = build_scope(rows, meta, empty_cache(), media, generated_at_utc='2026-09-01T00:00:00Z')
        self.assertEqual(status['queue_count'], 1)
        request = queue[0]

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            queue_path = root / 'queue.jsonl'
            status_path = root / 'status.json'
            cache_path = root / 'cache.json'
            submission = root / 'result.json'
            write_scope(queue, status, queue_path, status_path)
            cache_path.write_text(json.dumps(empty_cache()), encoding='utf-8')
            submission.write_text(json.dumps({
                'contract': RESULT_CONTRACT_ID,
                'schema_version': 1,
                'results': [result_for(request)],
            }), encoding='utf-8')
            stats = ingest_paths(queue_path, cache_path, [submission], now_utc='2026-09-01T00:00:01Z')
            self.assertEqual(stats['accepted_count'], 1)
            cache = json.loads(cache_path.read_text(encoding='utf-8'))
            resolved = resolve_description_for_appids(['42'], media, meta, cache)
            self.assertEqual(resolved['description_status'], 'ready_ru')
            self.assertEqual(resolved['description_source_locale'], 'translation_cache')
            self.assertEqual(resolved['summary'], GOOD_RU)


if __name__ == '__main__':
    unittest.main()
