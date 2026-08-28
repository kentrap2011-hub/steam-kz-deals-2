import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

MAILING_INDEX = Path('data/production/mailing/index.json')
OLD_METADATA = Path('data/cache/content_metadata.json')
OUT_DIR = Path('data/production/pre_ai')
OUT = OUT_DIR / 'content_metadata.json'
WORKERS = 8
RETRIES = 5

local = threading.local()


def session():
    value = getattr(local, 'session', None)
    if value is None:
        value = requests.Session()
        value.headers.update({
            'User-Agent': 'Mozilla/5.0 SteamKZPreAIMetadata/1.0',
            'Accept': 'application/json,text/plain,*/*',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        local.session = value
    return value


def fetch_json(url, params):
    last = None
    for attempt in range(RETRIES):
        try:
            response = session().get(url, params=params, timeout=30)
            if response.status_code == 429:
                wait = int(response.headers.get('Retry-After') or min(30, 2 ** (attempt + 1)))
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            last = exc
            if attempt + 1 < RETRIES:
                time.sleep(min(20, 2 ** attempt))
    raise RuntimeError(str(last))


def load_feed():
    index = json.loads(MAILING_INDEX.read_text(encoding='utf-8'))
    cols = index['columns']
    ci = {name: i for i, name in enumerate(cols)}
    feed = {}
    for n in range(1, int(index['chunk_count']) + 1):
        path = Path(index['chunk_pattern'].replace('NNN', f'{n:03d}'))
        for line in path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            cells = line.split('\t')
            if len(cells) != len(cols):
                raise SystemExit(f'Column mismatch in {path}')
            key = cells[ci['key']]
            feed[key] = {
                'key': key,
                'appid': cells[ci['appid']],
                'title': cells[ci['title']],
            }
    if len(feed) != int(index['item_count']):
        raise SystemExit('Mailing item_count mismatch')
    return index, feed


def reusable_seed(required_keys):
    if not OLD_METADATA.exists():
        return {}
    try:
        old = json.loads(OLD_METADATA.read_text(encoding='utf-8'))
    except Exception:
        return {}
    entries = old.get('entries')
    if not isinstance(entries, dict):
        return {}
    reusable = {}
    for key in required_keys:
        entry = entries.get(key)
        if not isinstance(entry, dict):
            continue
        if entry.get('key') != key:
            continue
        kind = entry.get('entity_kind')
        if kind == 'app' and entry.get('app_type'):
            reusable[key] = entry
        elif kind == 'sub' and isinstance(entry.get('package_apps'), list):
            reusable[key] = entry
    return reusable


def fetch_one(row):
    key = row['key']
    appid = row['appid']
    if key.startswith('App_'):
        data = fetch_json(
            'https://store.steampowered.com/api/appdetails',
            {'appids': appid, 'cc': 'kz', 'l': 'english'},
        )
        payload = data.get(str(appid)) or {}
        if not payload.get('success') or not isinstance(payload.get('data'), dict):
            raise RuntimeError(f'appdetails unavailable for {key}')
        d = payload['data']
        fullgame = d.get('fullgame') if isinstance(d.get('fullgame'), dict) else None
        return key, {
            'key': key,
            'entity_kind': 'app',
            'steam_id': str(appid),
            'store_name': d.get('name'),
            'app_type': d.get('type'),
            'fullgame_appid': str(fullgame.get('appid')) if fullgame and fullgame.get('appid') is not None else None,
            'fullgame_name': fullgame.get('name') if fullgame else None,
            'is_free': d.get('is_free'),
        }
    if key.startswith('Sub_'):
        subid = key.split('_', 1)[1]
        data = fetch_json(
            'https://store.steampowered.com/api/packagedetails',
            {'packageids': subid, 'cc': 'kz', 'l': 'english'},
        )
        payload = data.get(str(subid)) or {}
        if not payload.get('success') or not isinstance(payload.get('data'), dict):
            raise RuntimeError(f'packagedetails unavailable for {key}')
        d = payload['data']
        apps = []
        for app in d.get('apps') or []:
            if isinstance(app, dict) and app.get('id') is not None:
                apps.append({'appid': str(app.get('id')), 'name': app.get('name')})
        return key, {
            'key': key,
            'entity_kind': 'sub',
            'steam_id': str(subid),
            'store_name': d.get('name'),
            'package_apps': apps,
        }
    raise RuntimeError(f'Unsupported key kind: {key}')


def main():
    started = time.monotonic()
    index, feed = load_feed()
    required = set(feed)
    entries = reusable_seed(required)
    seed_hits = len(entries)
    missing = [feed[key] for key in sorted(required - set(entries))]
    failures = []

    print(f'Pre-AI metadata source={len(feed)} seed_hits={seed_hits} fetch_misses={len(missing)}')
    if missing:
        with ThreadPoolExecutor(max_workers=WORKERS) as pool:
            futures = {pool.submit(fetch_one, row): row for row in missing}
            for future in as_completed(futures):
                row = futures[future]
                try:
                    key, value = future.result()
                    entries[key] = value
                except Exception as exc:
                    failures.append({'key': row['key'], 'error': str(exc)})
                    print('FAIL', row['key'], exc)

    unresolved = sorted(required - set(entries))
    if failures or unresolved:
        raise SystemExit(
            'Pre-AI content metadata incomplete: '
            + json.dumps({'failures': failures[:20], 'unresolved': unresolved[:20]}, ensure_ascii=False)
        )

    current = {key: entries[key] for key in sorted(required)}
    counts = {}
    for entry in current.values():
        label = entry.get('app_type') if entry.get('entity_kind') == 'app' else 'package'
        counts[label or 'unknown'] = counts.get(label or 'unknown', 0) + 1

    result = {
        'schema_version': 1,
        'purpose': 'pre_ai_content_metadata_for_all_candidates',
        'status': 'complete',
        'source_path': 'data/production/mailing/index.json',
        'source_updated_at_utc': index.get('source_updated_at_utc'),
        'source_item_count': len(feed),
        'entry_count': len(current),
        'complete_coverage': len(current) == len(feed),
        'seed_hit_count': seed_hits,
        'network_fetch_count': len(missing),
        'type_counts': counts,
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'entries': current,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': result['status'],
        'source': result['source_item_count'],
        'entries': result['entry_count'],
        'seed_hits': result['seed_hit_count'],
        'network_fetches': result['network_fetch_count'],
        'type_counts': result['type_counts'],
        'elapsed_seconds': result['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
