#!/usr/bin/env python3
import argparse
import glob
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from build_russian_description_translation_queue import build_repo_scope, load_jsonl
from russian_description_quality import classify_description, normalize_description
from russian_description_translation_runtime import (
    CACHE_CONTRACT_ID,
    RESULT_CONTRACT_ID,
    empty_cache,
    load_translation_cache,
)

QUEUE_PATH = Path('data/production/pre_ai/chatgpt_ru_description_queue.jsonl')
CACHE_PATH = Path('data/cache/russian_description_translations.json')
INBOX_GLOB = 'data/ai_inbox/russian_descriptions/*.json'

SUBMISSION_KEYS = {'contract', 'schema_version', 'results'}
RESULT_REQUIRED = {
    'request_id',
    'source_key',
    'source_appid',
    'source_text_sha256',
    'source_version',
    'status',
}
RESULT_OPTIONAL = {'translated_text_ru', 'error_code', 'quality_note'}
ECHO_FIELDS = ['request_id', 'source_key', 'source_appid', 'source_text_sha256', 'source_version']


def fail(message):
    raise ValueError(message)


def load_submission(path):
    doc = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(doc, dict):
        fail(f'{path}: submission must be an object')
    if set(doc) != SUBMISSION_KEYS:
        fail(f'{path}: submission fields mismatch: {sorted(set(doc) ^ SUBMISSION_KEYS)}')
    if doc.get('contract') != RESULT_CONTRACT_ID:
        fail(f'{path}: wrong result contract')
    if doc.get('schema_version') != 1:
        fail(f'{path}: wrong schema_version')
    if not isinstance(doc.get('results'), list):
        fail(f'{path}: results must be an array')
    return doc


def validate_submissions(queue, submission_docs):
    queue_by_id = {row['request_id']: row for row in queue}
    if len(queue_by_id) != len(queue):
        fail('current translation queue contains duplicate request_id')

    seen = set()
    accepted = []
    errors = []
    for source_name, doc in submission_docs:
        local_seen = set()
        for index, result in enumerate(doc['results']):
            if not isinstance(result, dict):
                fail(f'{source_name}: result[{index}] must be an object')
            keys = set(result)
            missing = RESULT_REQUIRED - keys
            unknown = keys - RESULT_REQUIRED - RESULT_OPTIONAL
            if missing or unknown:
                fail(f'{source_name}: result[{index}] shape invalid missing={sorted(missing)} unknown={sorted(unknown)}')
            request_id = result.get('request_id')
            if request_id in local_seen or request_id in seen:
                fail(f'{source_name}: duplicate request_id {request_id}')
            local_seen.add(request_id)
            seen.add(request_id)
            request = queue_by_id.get(request_id)
            if request is None:
                fail(f'{source_name}: unknown or stale request_id {request_id}')
            for field in ECHO_FIELDS:
                if result.get(field) != request.get(field):
                    fail(f'{source_name}: exact binding mismatch for {request_id} field={field}')

            status = result.get('status')
            if status == 'translated':
                if 'error_code' in result:
                    fail(f'{source_name}: translated result {request_id} forbids error_code')
                translated = normalize_description(result.get('translated_text_ru'))
                if not translated:
                    fail(f'{source_name}: translated result {request_id} requires translated_text_ru')
                if classify_description(translated) != 'good_ru':
                    fail(f'{source_name}: translated result {request_id} failed good_ru quality gate')
                accepted.append((request, translated))
            elif status == 'error':
                if 'translated_text_ru' in result:
                    fail(f'{source_name}: error result {request_id} forbids translated_text_ru')
                error_code = str(result.get('error_code') or '').strip()
                if not error_code:
                    fail(f'{source_name}: error result {request_id} requires error_code')
                errors.append({'request_id': request_id, 'error_code': error_code})
            else:
                fail(f'{source_name}: invalid status for {request_id}: {status!r}')
    return accepted, errors


def merge_validated_results(cache, accepted, ingested_at_utc):
    cache = json.loads(json.dumps(cache if isinstance(cache, dict) else empty_cache()))
    if cache.get('schema_version') != 1 or cache.get('contract') != CACHE_CONTRACT_ID or not isinstance(cache.get('entries'), dict):
        cache = empty_cache()
    entries = cache['entries']
    for request, translated in accepted:
        entries[request['request_id']] = {
            'request_id': request['request_id'],
            'source_key': request['source_key'],
            'source_appid': request['source_appid'],
            'source_text_sha256': request['source_text_sha256'],
            'source_version': request['source_version'],
            'translated_text_ru': translated,
            'target_locale': 'ru',
            'validated_quality': 'good_ru',
            'result_contract': RESULT_CONTRACT_ID,
            'ingested_at_utc': ingested_at_utc,
        }
    if accepted:
        cache['updated_at_utc'] = ingested_at_utc
    cache['entries'] = dict(sorted(entries.items()))
    return cache


def ingest_paths(queue_path, cache_path, submission_paths, now_utc=None, delete_processed=False, rebuild_repo_scope=False):
    queue = load_jsonl(queue_path)
    docs = [(str(path), load_submission(path)) for path in submission_paths]
    accepted, errors = validate_submissions(queue, docs)
    now_utc = now_utc or datetime.now(timezone.utc).isoformat()
    cache = load_translation_cache(cache_path)
    merged = merge_validated_results(cache, accepted, now_utc)

    cache_path = Path(cache_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    if rebuild_repo_scope:
        build_repo_scope()
    if delete_processed:
        for path in submission_paths:
            Path(path).unlink()

    return {
        'submission_count': len(submission_paths),
        'accepted_count': len(accepted),
        'error_count': len(errors),
        'cache_entry_count': len(merged.get('entries') or {}),
        'error_results': errors,
    }


def emit_github_output(stats, path):
    if not path:
        return
    with open(path, 'a', encoding='utf-8') as handle:
        for key in ['submission_count', 'accepted_count', 'error_count', 'cache_entry_count']:
            handle.write(f'{key}={stats[key]}\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--queue', default=str(QUEUE_PATH))
    parser.add_argument('--cache', default=str(CACHE_PATH))
    parser.add_argument('--inbox-glob', default=INBOX_GLOB)
    parser.add_argument('--github-output', default=os.environ.get('GITHUB_OUTPUT'))
    args = parser.parse_args()

    paths = [Path(p) for p in sorted(glob.glob(args.inbox_glob))]
    if not paths:
        print(json.dumps({'status': 'no_submissions', 'submission_count': 0}, indent=2))
        emit_github_output({'submission_count': 0, 'accepted_count': 0, 'error_count': 0, 'cache_entry_count': len(load_translation_cache(args.cache).get('entries') or {})}, args.github_output)
        return

    try:
        stats = ingest_paths(
            Path(args.queue),
            Path(args.cache),
            paths,
            delete_processed=True,
            rebuild_repo_scope=True,
        )
    except ValueError as exc:
        raise SystemExit(f'RUSSIAN_DESCRIPTION_TRANSLATION_INGEST_INVALID: {exc}')
    emit_github_output(stats, args.github_output)
    print(json.dumps({'status': 'complete', **stats}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
