#!/usr/bin/env python3
import hashlib
import json
import urllib.parse
import urllib.request
from pathlib import Path

from russian_description_quality import classify_description, normalize_description, resolve_description

REQUEST_CONTRACT_ID = 'RUSSIAN-DESCRIPTION-TRANSLATION-V1'
RESULT_CONTRACT_ID = 'RUSSIAN-DESCRIPTION-TRANSLATION-RESULT-V1'
CACHE_CONTRACT_ID = 'RUSSIAN-DESCRIPTION-TRANSLATION-CACHE-ENTRY-V1'

TRANSLATABLE_STATUSES = {'needs_translation', 'needs_ru_rewrite'}
TRANSLATABLE_QUALITIES = {'non_ru', 'weak_ru'}


def sha256_text(value):
    return hashlib.sha256(str(value).encode('utf-8')).hexdigest()


def source_binding(source_key, source_text):
    normalized = normalize_description(source_text)
    if not normalized:
        raise ValueError('translation source text must be nonempty after normalization')
    source_hash = sha256_text(normalized)
    serialized = '\n'.join([REQUEST_CONTRACT_ID, str(source_key), source_hash])
    return {
        'source_text': normalized,
        'source_text_sha256': source_hash,
        'source_version': f'sha256:{source_hash}',
        'request_id': sha256_text(serialized),
    }


def empty_cache():
    return {
        'schema_version': 1,
        'contract': CACHE_CONTRACT_ID,
        'updated_at_utc': None,
        'entries': {},
    }


def validate_cache_container(cache):
    if not isinstance(cache, dict):
        return empty_cache()
    if cache.get('schema_version') != 1 or cache.get('contract') != CACHE_CONTRACT_ID:
        return empty_cache()
    entries = cache.get('entries')
    if not isinstance(entries, dict):
        return empty_cache()
    return cache


def load_translation_cache(path):
    path = Path(path)
    if not path.exists():
        return empty_cache()
    try:
        return validate_cache_container(json.loads(path.read_text(encoding='utf-8')))
    except Exception:
        return empty_cache()


def validated_cache_hit(cache, resolution):
    if not isinstance(resolution, dict):
        return None
    if resolution.get('description_status') not in TRANSLATABLE_STATUSES:
        return None
    if resolution.get('description_source_quality') not in TRANSLATABLE_QUALITIES:
        return None
    appid = str(resolution.get('description_source_appid') or '')
    source_text = resolution.get('description_source_text')
    if not appid.isdigit() or not source_text:
        return None
    binding = source_binding(f'App_{appid}', source_text)
    entries = validate_cache_container(cache).get('entries') or {}
    entry = entries.get(binding['request_id'])
    if not isinstance(entry, dict):
        return None
    exact = {
        'request_id': binding['request_id'],
        'source_key': f'App_{appid}',
        'source_appid': appid,
        'source_text_sha256': binding['source_text_sha256'],
        'source_version': binding['source_version'],
        'target_locale': 'ru',
        'validated_quality': 'good_ru',
        'result_contract': RESULT_CONTRACT_ID,
    }
    if any(entry.get(key) != value for key, value in exact.items()):
        return None
    translated = normalize_description(entry.get('translated_text_ru'))
    if classify_description(translated) != 'good_ru':
        return None
    return {
        'summary': translated,
        'description_status': 'ready_ru',
        'description_source_locale': 'translation_cache',
        'description_source_quality': 'good_ru',
        'description_source_text': None,
        'description_source_appid': appid,
        'description_source_path': 'data/cache/russian_description_translations.json',
        'description_translation_request_id': binding['request_id'],
        'description_translation_source_text_sha256': binding['source_text_sha256'],
        'description_translation_source_version': binding['source_version'],
    }


def _resolution_for_appid(appid, media, content_metadata_by_appid):
    appid = str(appid)
    store = media.get(appid) or {}
    metadata = content_metadata_by_appid.get(appid) or {}
    resolution = resolve_description(
        store.get('short_description_source'),
        metadata.get('short_description'),
    )
    resolution['description_source_appid'] = appid
    if resolution.get('description_source_locale') == 'english':
        resolution['description_source_path'] = 'data/production/pre_ai/content_metadata.json'
    elif resolution.get('description_source_locale') == 'russian':
        resolution['description_source_path'] = 'IStoreBrowseService/GetItems(language=russian)'
    else:
        resolution['description_source_path'] = None
    return resolution


def resolve_description_for_appids(appids, media, content_metadata_by_appid, cache=None):
    resolutions = []
    for appid in [str(x) for x in appids if str(x).isdigit()]:
        resolution = _resolution_for_appid(appid, media, content_metadata_by_appid)
        if resolution.get('description_status') == 'ready_ru':
            return resolution
        resolutions.append(resolution)

    # Cache is second priority globally: a validated exact translation is better than
    # returning any unresolved translatable source, but never overrides current direct RU.
    for resolution in resolutions:
        hit = validated_cache_hit(cache or empty_cache(), resolution)
        if hit:
            return hit

    if not resolutions:
        return resolve_description(None, None)

    priority = {
        'needs_translation': 0,
        'needs_ru_rewrite': 1,
        'technical_source': 2,
        'missing_source': 3,
    }
    return min(resolutions, key=lambda row: priority.get(row.get('description_status'), 99))


def build_translation_request(resolution, title):
    if not isinstance(resolution, dict):
        return None
    status = resolution.get('description_status')
    quality = resolution.get('description_source_quality')
    if status not in TRANSLATABLE_STATUSES or quality not in TRANSLATABLE_QUALITIES:
        return None
    appid = str(resolution.get('description_source_appid') or '')
    source_text = resolution.get('description_source_text')
    if not appid.isdigit() or not source_text:
        return None
    binding = source_binding(f'App_{appid}', source_text)
    return {
        'request_id': binding['request_id'],
        'source_key': f'App_{appid}',
        'source_appid': appid,
        'title': normalize_description(title) or f'App {appid}',
        'work_type': 'translate_to_ru' if status == 'needs_translation' else 'rewrite_ru',
        'source_text': binding['source_text'],
        'source_text_sha256': binding['source_text_sha256'],
        'source_version': binding['source_version'],
        'source_locale_state': quality,
        'source_quality': quality,
        'source_path': resolution.get('description_source_path') or 'unknown_source',
        'target_locale': 'ru',
    }


def fetch_russian_store_descriptions(appids, timeout=30):
    ids = sorted({str(x) for x in appids if str(x).isdigit()}, key=int)
    result = {}
    for start in range(0, len(ids), 100):
        batch = ids[start:start + 100]
        payload = {
            'ids': [{'appid': int(appid)} for appid in batch],
            'context': {'language': 'russian', 'country_code': 'KZ', 'steam_realm': 1},
            'data_request': {'include_basic_info': True},
        }
        url = 'https://api.steampowered.com/IStoreBrowseService/GetItems/v1/?input_json=' + urllib.parse.quote(
            json.dumps(payload, separators=(',', ':'))
        )
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'steam-kz-deals-translation/1.0', 'Accept': 'application/json'},
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode('utf-8'))
        requested = set(batch)
        for store_item in (data.get('response') or {}).get('store_items') or []:
            request_id = str(store_item.get('id') or '').strip()
            asset_appid = str(store_item.get('appid') or request_id).strip()
            result_key = request_id if request_id in requested else asset_appid
            if not result_key:
                continue
            text = normalize_description((store_item.get('basic_info') or {}).get('short_description'))
            result[result_key] = {'short_description_source': text or None}
    return result
