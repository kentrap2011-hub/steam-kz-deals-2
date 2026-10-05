#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

from build_russian_description_translation_queue import build_scope, write_scope
from ingest_russian_description_translations import ingest_paths
from validate_russian_descriptions import validate as validate_russian_descriptions
from russian_description_translation_runtime import (
    CACHE_CONTRACT_ID,
    RESULT_CONTRACT_ID,
    STEAM_APPDETAILS_RU_SOURCE,
    apply_russian_appdetails_description_fallback,
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

    def test_command_conquer_appdetails_ru_fallback_avoids_translation_queue(self):
        appid = '1213210'
        title = 'Command & Conquer™ Remastered Collection'
        english = (
            'Command & Conquer and Red Alert are both remastered in 4K by the former '
            'Westwood Studios team members. Includes all 3 expansions, rebuilt multiplayer, '
            'a modernized UI, Map Editor, bonus footage gallery, and over 7 hours of remastered music.'
        )
        russian = (
            'Переиздание Command & Conquer и Red Alert в разрешении 4K от бывших сотрудников '
            'Westwood Studios включает все три дополнения, обновлённый многопользовательский режим, '
            'современный интерфейс, редактор карт, бонусные материалы и переработанную музыку.'
        )
        media = {appid: {'short_description_source': english}}
        changed = apply_russian_appdetails_description_fallback(
            media[appid],
            {'short_description': russian},
        )
        self.assertTrue(changed)
        self.assertEqual(media[appid]['short_description_source_path'], STEAM_APPDETAILS_RU_SOURCE)

        queue, status = build_scope(
            [row(appid, title)],
            metadata(appid, english, title),
            empty_cache(),
            media,
            generated_at_utc='2026-09-27T18:00:00Z',
        )
        self.assertEqual(queue, [])
        self.assertEqual(status['resolved_direct_ru_count'], 1)
        resolution = resolve_description_for_appids(
            [appid],
            media,
            metadata(appid, english, title),
            empty_cache(),
        )
        self.assertEqual(resolution['description_status'], 'ready_ru')
        self.assertEqual(resolution['description_source_path'], STEAM_APPDETAILS_RU_SOURCE)
        self.assertEqual(resolution['summary'], russian)

    def test_prince_of_persia_missing_sources_preserves_exact_appdetails_for_translation(self):
        appid = '13500'
        title = 'Prince of Persia: Warrior Within™'
        official_english = (
            'Enter a dark underworld in this action adventure sequel and master new combat abilities '
            'while the Prince fights to change his fate.'
        )
        media = {appid: {'short_description_source': None}}
        changed = apply_russian_appdetails_description_fallback(
            media[appid],
            {'short_description': official_english},
        )
        self.assertTrue(changed)
        self.assertEqual(media[appid]['short_description_source_path'], STEAM_APPDETAILS_RU_SOURCE)

        unresolved = resolve_description_for_appids(
            [appid],
            media,
            metadata(appid, None, title),
            empty_cache(),
        )
        self.assertEqual(unresolved['description_status'], 'needs_translation')
        self.assertEqual(unresolved['description_source_quality'], 'non_ru')
        self.assertEqual(unresolved['description_source_path'], STEAM_APPDETAILS_RU_SOURCE)
        self.assertIsNone(unresolved['summary'])

        queue, status = build_scope(
            [row(appid, title)],
            metadata(appid, None, title),
            empty_cache(),
            media,
            generated_at_utc='2026-09-29T00:00:00Z',
        )
        self.assertEqual([request['source_key'] for request in queue], ['App_13500'])
        self.assertEqual(queue[0]['source_path'], STEAM_APPDETAILS_RU_SOURCE)
        self.assertEqual(queue[0]['source_quality'], 'non_ru')
        self.assertNotIn(
            'App_13500',
            [blocker['key'] for blocker in status['nontranslatable_blockers']],
        )

        request = queue[0]
        cache = {
            'schema_version': 1,
            'contract': CACHE_CONTRACT_ID,
            'updated_at_utc': '2026-09-29T00:00:01Z',
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
                    'ingested_at_utc': '2026-09-29T00:00:01Z',
                }
            },
        }
        resolved = resolve_description_for_appids(
            [appid],
            media,
            metadata(appid, None, title),
            cache,
        )
        self.assertEqual(resolved['description_status'], 'ready_ru')
        self.assertEqual(resolved['description_source_locale'], 'translation_cache')
        self.assertEqual(resolved['description_source_appid'], appid)
        self.assertEqual(resolved['summary'], GOOD_RU)

        card = {
            'id': 'game:13500',
            'title': title,
            'analysis_state': 'analyzed_fit',
            'priority_rank': 7,
            'total_score': 61.5,
            'deep_stage_state': 'completed',
            'deep_stage_outcome': 'fit',
            'effective_analysis_source': 'deep',
        }
        semantic_before = {
            key: card[key]
            for key in [
                'priority_rank',
                'total_score',
                'deep_stage_state',
                'deep_stage_outcome',
                'effective_analysis_source',
            ]
        }
        card.update({
            'summary': resolved['summary'],
            'description_status': resolved['description_status'],
            'description_source_locale': resolved['description_source_locale'],
            'description_source_quality': resolved['description_source_quality'],
            'description_source_appid': resolved['description_source_appid'],
            'description_source_path': resolved['description_source_path'],
        })
        self.assertEqual(
            semantic_before,
            {key: card[key] for key in semantic_before},
        )
        with tempfile.TemporaryDirectory() as td:
            visual_path = Path(td) / 'visual.json'
            visual_path.write_text(
                json.dumps({'items': [card]}, ensure_ascii=False),
                encoding='utf-8',
            )
            validate_russian_descriptions(visual_path)

    def test_wrong_appid_translation_cache_cannot_repair_prince_of_persia(self):
        source = 'Exact official English source text for the requested Steam app.'
        wrong_request = build_translation_request({
            'description_status': 'needs_translation',
            'description_source_quality': 'non_ru',
            'description_source_appid': '13501',
            'description_source_text': source,
            'description_source_path': STEAM_APPDETAILS_RU_SOURCE,
        }, 'Wrong Edition')
        wrong_cache = {
            'schema_version': 1,
            'contract': CACHE_CONTRACT_ID,
            'updated_at_utc': '2026-09-29T00:00:00Z',
            'entries': {
                wrong_request['request_id']: {
                    'request_id': wrong_request['request_id'],
                    'source_key': wrong_request['source_key'],
                    'source_appid': wrong_request['source_appid'],
                    'source_text_sha256': wrong_request['source_text_sha256'],
                    'source_version': wrong_request['source_version'],
                    'translated_text_ru': GOOD_RU,
                    'target_locale': 'ru',
                    'validated_quality': 'good_ru',
                    'result_contract': RESULT_CONTRACT_ID,
                    'ingested_at_utc': '2026-09-29T00:00:00Z',
                }
            },
        }
        media = {'13500': {
            'short_description_source': source,
            'short_description_source_path': STEAM_APPDETAILS_RU_SOURCE,
        }}
        unresolved = resolve_description_for_appids(
            ['13500'],
            media,
            metadata('13500', None, 'Prince of Persia: Warrior Within™'),
            wrong_cache,
        )
        self.assertEqual(unresolved['description_status'], 'needs_translation')
        self.assertIsNone(unresolved['summary'])

    def test_appdetails_empty_and_boilerplate_never_become_translation_sources(self):
        for bad_text in [
            '',
            'Русское краткое описание для этой игры пока не подготовлено.',
        ]:
            media = {'1': {'short_description_source': None}}
            changed = apply_russian_appdetails_description_fallback(
                media['1'],
                {'short_description': bad_text},
            )
            self.assertFalse(changed)
            self.assertIsNone(media['1']['short_description_source'])

    def test_appdetails_non_russian_does_not_override_translation_source(self):
        english = 'Explore a strange station and escape the creatures hunting you.'
        media = {'1': {'short_description_source': english}}
        changed = apply_russian_appdetails_description_fallback(
            media['1'],
            {'short_description': 'Another English description that is still not Russian.'},
        )
        self.assertFalse(changed)
        self.assertEqual(media['1']['short_description_source'], english)
        resolution = resolve_description_for_appids(
            ['1'],
            media,
            metadata('1', english),
            empty_cache(),
        )
        self.assertEqual(resolution['description_status'], 'needs_translation')

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

    def test_placeholder_and_non_russian_results_enter_diagnostics(self):
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
                stats = ingest_paths(queue_path, cache_path, [submission])
                self.assertEqual(stats['accepted_count'], 0)
                self.assertEqual(stats['diagnostic_quarantined_count'], 1)
                cache = json.loads(cache_path.read_text(encoding='utf-8'))
                self.assertNotIn(request['request_id'], cache['entries'])
                diagnostics = json.loads(
                    (root / 'russian_description_translation_diagnostics.json').read_text(
                        encoding='utf-8'
                    )
                )
                self.assertEqual(diagnostics['entries'][request['request_id']]['state'], 'active')

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
