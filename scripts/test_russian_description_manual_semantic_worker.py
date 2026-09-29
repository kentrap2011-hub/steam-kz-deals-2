#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path

from ingest_russian_description_translations import ingest_paths
from russian_description_translation_runtime import (
    RESULT_CONTRACT_ID,
    build_translation_request,
    empty_cache,
)


GOOD_RU = (
    'Мрачное приключение об исследовании заброшенного комплекса, поиске подсказок '
    'и осторожном продвижении через опасные помещения.'
)


def request(appid, source):
    return build_translation_request(
        {
            'description_status': 'needs_translation',
            'description_source_quality': 'non_ru',
            'description_source_appid': str(appid),
            'summary': source,
            'description_source_path': f'fixture:{appid}',
        },
        f'Fixture {appid}',
    )


def translated(req):
    return {
        'request_id': req['request_id'],
        'source_key': req['source_key'],
        'source_appid': req['source_appid'],
        'source_text_sha256': req['source_text_sha256'],
        'source_version': req['source_version'],
        'status': 'translated',
        'translated_text_ru': GOOD_RU,
    }


def submission(results):
    return {
        'contract': RESULT_CONTRACT_ID,
        'schema_version': 1,
        'results': results,
    }


def write_queue(path, rows):
    path.write_text(
        ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows),
        encoding='utf-8',
    )


def main():
    ownership = json.loads(Path('config/execution_ownership_contract.json').read_text(encoding='utf-8'))
    contract = json.loads(Path('config/russian_description_translation_contract.json').read_text(encoding='utf-8'))
    result_contract = json.loads(
        Path('config/russian_description_translation_result_contract.json').read_text(encoding='utf-8')
    )
    prompt_path = Path('config/russian_description_manual_semantic_worker_prompt.md')
    prompt = prompt_path.read_text(encoding='utf-8')

    # 1. Ordinary interactive chat stays non-production.
    assert contract['ownership']['interactive_chat']['production_catalog_translation_allowed'] is False
    assert ownership['explicit_manual_semantic_worker_chats']['ordinary_interactive_chat_role_unchanged'] is True

    # 2. Only the explicit canonical one-shot role is authorized.
    manual = ownership['explicit_manual_semantic_worker_chats']['russian_description_one_shot']
    assert manual['allowed'] is True
    assert manual['canonical_prompt'] == str(prompt_path)
    assert manual['requires_fresh_explicit_user_launch_every_run'] is True
    assert contract['ownership']['manual_one_shot_chatgpt_data_plane']['canonical_prompt'] == str(prompt_path)

    # 3/4/7. Exact current work + same result transport, never direct cache/Scheduled Task authority.
    assert 'data/production/pre_ai/chatgpt_ru_description_queue.jsonl' in prompt
    assert 'data/ai_inbox/russian_descriptions/manual-one-shot-' in prompt
    assert 'data/cache/russian_description_translations.json' in prompt
    assert 'Never write directly' in prompt
    assert 'Scheduled Task' in prompt
    assert manual['recurring_schedule_allowed'] is False
    assert manual['may_create_or_modify_scheduled_task'] is False
    assert 'explicitly user-launched one-shot worker bound to config/russian_description_manual_semantic_worker_prompt.md' in (
        result_contract['ownership']['allowed_semantic_producers']
    )

    req1 = request('1', 'Explore a strange station and escape the creatures hunting you.')
    req2 = request('2', 'Investigate an old city, solve puzzles, and uncover a hidden mystery.')

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        queue_path = root / 'queue.jsonl'
        cache_path = root / 'cache.json'
        status_path = root / 'status.json'
        inbox = root / 'submission.json'
        cache_path.write_text(json.dumps(empty_cache()), encoding='utf-8')

        # 3. Forged/old request identity still fails closed.
        write_queue(queue_path, [req1])
        status_path.write_text(json.dumps({
            'untranslated_game_count': 1,
            'last_translation_attempt_at_utc': None,
            'last_successful_translation_at_utc': None,
        }), encoding='utf-8')
        forged = translated(req1)
        forged['request_id'] = 'f' * 64
        inbox.write_text(json.dumps(submission([forged]), ensure_ascii=False), encoding='utf-8')
        try:
            ingest_paths(queue_path, cache_path, [inbox], status_path=status_path)
        except ValueError:
            pass
        else:
            raise AssertionError('forged manual request identity must fail closed')

        # 5. A subset checkpoint accepts only its exact records; missing work remains in the queue.
        write_queue(queue_path, [req1, req2])
        status_path.write_text(json.dumps({
            'untranslated_game_count': 2,
            'last_translation_attempt_at_utc': None,
            'last_successful_translation_at_utc': None,
        }), encoding='utf-8')
        inbox.write_text(json.dumps(submission([translated(req1)]), ensure_ascii=False), encoding='utf-8')
        accepted_at = '2026-09-29T09:00:00+00:00'
        stats = ingest_paths(
            queue_path,
            cache_path,
            [inbox],
            now_utc=accepted_at,
            status_path=status_path,
        )
        assert stats['accepted_count'] == 1
        assert stats['attempted_current_work'] is True
        assert stats['successful_no_work'] is False
        assert len(queue_path.read_text(encoding='utf-8').splitlines()) == 2
        cache = json.loads(cache_path.read_text(encoding='utf-8'))
        assert req1['request_id'] in cache['entries']
        assert req2['request_id'] not in cache['entries']

        # 6/8. Empty current queue + zero-result submission is a GitHub-owned successful
        # no-work check and feeds the same attempt/success status used by Statistics.
        write_queue(queue_path, [])
        status_path.write_text(json.dumps({
            'untranslated_game_count': 0,
            'last_translation_attempt_at_utc': accepted_at,
            'last_successful_translation_at_utc': accepted_at,
        }), encoding='utf-8')
        inbox.write_text(json.dumps(submission([])), encoding='utf-8')
        no_work_at = '2026-09-29T09:10:00+00:00'
        no_work = ingest_paths(
            queue_path,
            cache_path,
            [inbox],
            now_utc=no_work_at,
            status_path=status_path,
        )
        assert no_work['attempted_current_work'] is True
        assert no_work['successful_no_work'] is True
        no_work_status = json.loads(status_path.read_text(encoding='utf-8'))
        assert no_work_status['last_translation_attempt_at_utc'] == no_work_at
        assert no_work_status['last_successful_translation_at_utc'] == no_work_at

        # Zero-result transport against nonempty work is not an attempt and cannot
        # manufacture timestamp progress.
        write_queue(queue_path, [req2])
        status_path.write_text(json.dumps({
            'untranslated_game_count': 1,
            'last_translation_attempt_at_utc': no_work_at,
            'last_successful_translation_at_utc': no_work_at,
        }), encoding='utf-8')
        inbox.write_text(json.dumps(submission([])), encoding='utf-8')
        noop = ingest_paths(
            queue_path,
            cache_path,
            [inbox],
            now_utc='2026-09-29T09:20:00+00:00',
            status_path=status_path,
        )
        assert noop['attempted_current_work'] is False
        assert noop['successful_no_work'] is False
        unchanged = json.loads(status_path.read_text(encoding='utf-8'))
        assert unchanged['last_translation_attempt_at_utc'] == no_work_at
        assert unchanged['last_successful_translation_at_utc'] == no_work_at

    print('Manual Russian semantic-worker contract/runtime regression: ok')


if __name__ == '__main__':
    main()
