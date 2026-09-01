#!/usr/bin/env python3
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from russian_description_translation_runtime import (
    CACHE_CONTRACT_ID,
    REQUEST_CONTRACT_ID,
    RESULT_CONTRACT_ID,
    build_translation_request,
    fetch_russian_store_descriptions,
    load_translation_cache,
    resolve_description_for_appids,
)

PURCHASE_CONTEXT = Path('data/production/pre_ai/chatgpt_purchase_context.jsonl')
CONTENT_METADATA = Path('data/production/pre_ai/content_metadata.json')
CHATGPT_PAYLOAD = Path('data/production/pre_ai/chatgpt_payload.json')
QUEUE_OUT = Path('data/production/pre_ai/chatgpt_ru_description_queue.jsonl')
STATUS_OUT = Path('data/production/pre_ai/chatgpt_ru_description_status.json')
CACHE_PATH = Path('data/cache/russian_description_translations.json')


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def load_jsonl(path):
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def content_metadata_by_appid(doc):
    entries = doc.get('entries') or {}
    return {
        str(entry.get('steam_id')): entry
        for entry in entries.values()
        if isinstance(entry, dict)
        and entry.get('entity_kind') == 'app'
        and str(entry.get('steam_id') or '').isdigit()
    }


def base_appids_for_row(row):
    appids = [
        str(x)
        for x in ((row.get('semantic_condition') or {}).get('base_appids') or [])
        if str(x).isdigit()
    ]
    if appids:
        return appids
    taste_key = str(row.get('taste_subject_key') or '')
    if taste_key.startswith('App_') and taste_key[4:].isdigit():
        return [taste_key[4:]]
    purchase_key = str((row.get('purchase') or {}).get('key') or '')
    if purchase_key.startswith('App_') and purchase_key[4:].isdigit():
        return [purchase_key[4:]]
    return []


def queue_sha256(queue):
    raw = ''.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n' for row in queue)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def build_scope(rows, metadata_by_appid, cache, media, source_mailing_updated_at_utc=None, generated_at_utc=None):
    generated_at_utc = generated_at_utc or datetime.now(timezone.utc).isoformat()
    queue_by_id = {}
    blocker_by_key = {}
    resolved_direct = set()
    resolved_cache = set()
    scope_keys = set()

    for row in rows:
        base_appids = base_appids_for_row(row)
        for appid in base_appids:
            scope_keys.add(f'App_{appid}')
        resolution = resolve_description_for_appids(base_appids, media, metadata_by_appid, cache)
        source_appid = str(resolution.get('description_source_appid') or '')
        source_key = f'App_{source_appid}' if source_appid.isdigit() else None
        status = resolution.get('description_status')
        if status == 'ready_ru':
            if resolution.get('description_source_locale') == 'translation_cache':
                if source_key:
                    resolved_cache.add(source_key)
            elif source_key:
                resolved_direct.add(source_key)
            continue

        title = None
        if source_appid.isdigit():
            title = (metadata_by_appid.get(source_appid) or {}).get('store_name')
        title = title or (row.get('purchase') or {}).get('title') or row.get('taste_subject_key')
        request = build_translation_request(resolution, title)
        if request:
            existing = queue_by_id.get(request['request_id'])
            if existing is not None and existing != request:
                raise SystemExit(f'non-deterministic duplicate translation request {request["request_id"]}')
            queue_by_id[request['request_id']] = request
            continue

        blocker_key = source_key or str(row.get('taste_subject_key') or (row.get('purchase') or {}).get('key') or 'unknown')
        blocker_by_key[blocker_key] = {
            'key': blocker_key,
            'description_status': status or 'missing_source',
            'description_source_quality': resolution.get('description_source_quality') or 'missing',
        }

    queue = list(queue_by_id.values())
    blocker_rows = [blocker_by_key[key] for key in sorted(blocker_by_key, key=str.casefold)]
    if queue:
        status_value = 'translation_required'
    elif blocker_rows:
        status_value = 'blocked_nontranslatable'
    else:
        status_value = 'translation_complete'

    status = {
        'schema_version': 1,
        'contract': REQUEST_CONTRACT_ID,
        'status': status_value,
        'generated_at_utc': generated_at_utc,
        'source_mailing_updated_at_utc': source_mailing_updated_at_utc,
        'scope_source': str(PURCHASE_CONTEXT),
        'scope_record_count': len(rows),
        'unique_base_app_key_count': len(scope_keys),
        'queue_path': str(QUEUE_OUT),
        'queue_count': len(queue),
        'queue_sha256': queue_sha256(queue),
        'queue_request_ids': [row['request_id'] for row in queue],
        'resolved_direct_ru_source_keys': sorted(resolved_direct),
        'resolved_direct_ru_count': len(resolved_direct),
        'resolved_translation_cache_source_keys': sorted(resolved_cache),
        'resolved_translation_cache_count': len(resolved_cache),
        'nontranslatable_blockers': blocker_rows,
        'nontranslatable_blocker_count': len(blocker_rows),
        'retry_and_completeness_owner': 'github_control_plane',
        'worker_completeness_authority': False,
        'daily_item_quota': None,
    }
    return queue, status


def write_scope(queue, status, queue_path=QUEUE_OUT, status_path=STATUS_OUT):
    queue_path = Path(queue_path)
    status_path = Path(status_path)
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(
        ''.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n' for row in queue),
        encoding='utf-8',
    )
    status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def attach_to_chatgpt_payload(payload_path, queue_count):
    payload_path = Path(payload_path)
    payload = load_json(payload_path)
    semantic_work = payload.get('semantic_work')
    if not isinstance(semantic_work, dict):
        semantic_work = {}
    semantic_work['taste'] = {
        'work_type': 'taste',
        'queue_path': str(payload.get('files', {}).get('taste_queue_jsonl') or 'data/production/pre_ai/chatgpt_taste_queue.jsonl'),
        'queue_count': int(payload.get('ai_queue_count') or 0),
        'result_contract': 'config/taste_result_contract.json',
    }
    semantic_work['russian_description_translation'] = {
        'work_type': 'russian_description_translation',
        'contract': REQUEST_CONTRACT_ID,
        'result_contract': RESULT_CONTRACT_ID,
        'cache_contract': CACHE_CONTRACT_ID,
        'queue_path': str(QUEUE_OUT),
        'status_path': str(STATUS_OUT),
        'queue_count': int(queue_count),
        'submission_glob': 'data/ai_inbox/russian_descriptions/*.json',
        'runtime_owner': 'scheduled_chatgpt_runtime_data_plane',
        'control_plane_owner': 'github_control_plane',
    }
    payload['semantic_work'] = semantic_work
    files = payload.get('files')
    if isinstance(files, dict):
        files['russian_description_translation_queue_jsonl'] = str(QUEUE_OUT)
        files['russian_description_translation_status_json'] = str(STATUS_OUT)
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def build_repo_scope(fetcher=fetch_russian_store_descriptions):
    rows = load_jsonl(PURCHASE_CONTEXT)
    metadata = content_metadata_by_appid(load_json(CONTENT_METADATA))
    cache = load_translation_cache(CACHE_PATH)
    appids = []
    for row in rows:
        appids.extend(base_appids_for_row(row))
    media = fetcher(appids)
    payload = load_json(CHATGPT_PAYLOAD)
    queue, status = build_scope(
        rows,
        metadata,
        cache,
        media,
        source_mailing_updated_at_utc=payload.get('source_mailing_updated_at_utc'),
    )
    write_scope(queue, status)
    attach_to_chatgpt_payload(CHATGPT_PAYLOAD, len(queue))
    print(json.dumps({
        'status': status['status'],
        'scope_record_count': status['scope_record_count'],
        'unique_base_app_key_count': status['unique_base_app_key_count'],
        'translation_queue_count': status['queue_count'],
        'resolved_direct_ru_count': status['resolved_direct_ru_count'],
        'resolved_translation_cache_count': status['resolved_translation_cache_count'],
        'nontranslatable_blocker_count': status['nontranslatable_blocker_count'],
        'queue_sha256': status['queue_sha256'],
    }, ensure_ascii=False, indent=2))
    return queue, status


if __name__ == '__main__':
    build_repo_scope()
