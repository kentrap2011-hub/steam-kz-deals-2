#!/usr/bin/env python3
import json
from pathlib import Path

from build_russian_description_translation_queue import build_scope
from ingest_russian_description_translations import validate_submissions
from russian_description_translation_runtime import (
    RESULT_CONTRACT_ID,
    build_translation_request,
    empty_cache,
)

ROOT = Path('.')
GOOD_RU = 'Тактическое приключение с исследованием станции, поиском инструментов и выбором безопасного пути к спасению.'


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def main():
    ownership = load('config/execution_ownership_contract.json')
    contract = load('config/russian_description_translation_contract.json')
    result_contract = load('config/russian_description_translation_result_contract.json')
    prompt = (ROOT / 'config/russian_description_manual_semantic_worker_prompt.md').read_text(encoding='utf-8')

    # 1. Ordinary interactive chat remains non-production.
    assert (contract['ownership']['interactive_chat']['production_catalog_translation_allowed'] is False)
    assert ownership['interactive_chat']['role'] == 'developer/operator session, not a production execution engine'
    assert any('outside the explicitly user-launched canonical' in x for x in ownership['interactive_chat']['forbidden'])

    # 2/4/7. The explicit manual role is narrow, current-scope-only, cannot write
    # canonical cache, and cannot create/modify a Scheduled Task or recurrence.
    manual = contract['manual_semantic_worker']
    ownership_manual = ownership['russian_description_manual_semantic_worker']
    assert manual['status'] == 'authorized_canonical_one_shot'
    assert manual['authorization'] == 'explicit_user_launch_required_for_every_run'
    assert manual['current_scope_only'] is True
    assert manual['preserve_github_order'] is True
    assert manual['direct_cache_write_allowed'] is False
    assert manual['scheduled_task_action_allowed'] is False
    assert manual['recurring_schedule_allowed'] is False
    assert ownership_manual['recurring_scheduler'] is False
    assert ownership_manual['scheduled_task_action_allowed'] is False
    assert 'Never write directly to:' in prompt

    source = 'Explore a strange station and escape the creatures hunting you.'
    request = build_translation_request({
        'description_status': 'needs_translation',
        'description_source_quality': 'non_ru',
        'description_source_appid': '123',
        'description_source_text': source,
        'description_source_path': 'fixture',
    }, 'Fixture Game')
    exact = {
        'request_id': request['request_id'],
        'source_key': request['source_key'],
        'source_appid': request['source_appid'],
        'source_text_sha256': request['source_text_sha256'],
        'source_version': request['source_version'],
        'status': 'translated',
        'translated_text_ru': GOOD_RU,
    }

    # 2. Explicit manual semantic worker can submit only an exact current request.
    accepted, errors = validate_submissions(
        [request],
        [('manual-fixture', {
            'contract': RESULT_CONTRACT_ID,
            'schema_version': 1,
            'results': [exact],
        })],
    )
    assert len(accepted) == 1 and errors == []

    # 3. Forged/old identities fail closed.
    forged = dict(exact, request_id='f' * 64)
    try:
        validate_submissions(
            [request],
            [('manual-forged', {
                'contract': RESULT_CONTRACT_ID,
                'schema_version': 1,
                'results': [forged],
            })],
        )
    except ValueError:
        pass
    else:
        raise AssertionError('manual forged request identity must fail closed')

    # 5. Subset result transport is permitted but never defines completeness.
    assert contract['worker_output_binding']['worker_may_return_subset_checkpoint'] is True
    assert manual['subset_checkpoint_allowed_for_transport_only'] is True
    assert manual['checkpoint_defines_quota_or_completeness'] is False
    assert result_contract['ownership']['worker_decides_completeness'] is False

    # 6. Empty current queue accepts an empty canonical result document, and the
    # GitHub-owned current-scope rebuild records the no-work attempt as success.
    accepted, errors = validate_submissions(
        [],
        [('manual-empty', {
            'contract': RESULT_CONTRACT_ID,
            'schema_version': 1,
            'results': [],
        })],
    )
    assert accepted == [] and errors == []
    queue, status = build_scope(
        [],
        {},
        empty_cache(),
        {},
        generated_at_utc='2026-09-29T09:00:00Z',
        translation_attempt_at_utc='2026-09-29T09:00:00Z',
        translation_success=False,
    )
    assert queue == []
    assert status['untranslated_game_count'] == 0
    assert status['last_translation_attempt_at'] == '2026-09-29T09:00:00+00:00'
    assert status['last_successful_translation_at'] == '2026-09-29T09:00:00+00:00'

    # 8. A manual failed/error attempt feeds the same GitHub-owned observability:
    # attempt advances, success does not while work remains.
    previous = {'last_successful_translation_at': '2026-09-29T08:00:00+00:00'}
    queue, status = build_scope(
        [{'taste_subject_key': 'App_123', 'purchase': {'key': 'App_123', 'title': 'Fixture Game'}, 'semantic_condition': {'base_appids': ['123']}}],
        {'123': {'entity_kind': 'app', 'steam_id': '123', 'store_name': 'Fixture Game', 'short_description': source}},
        empty_cache(),
        {'123': {'short_description_source': source}},
        generated_at_utc='2026-09-29T09:01:00Z',
        previous_status=previous,
        translation_attempt_at_utc='2026-09-29T09:00:00Z',
        translation_success=False,
    )
    assert len(queue) == 1
    assert status['last_translation_attempt_at'] == '2026-09-29T09:00:00+00:00'
    assert status['last_successful_translation_at'] == '2026-09-29T08:00:00+00:00'

    print('manual Russian description semantic worker regression: ok')


if __name__ == '__main__':
    main()
