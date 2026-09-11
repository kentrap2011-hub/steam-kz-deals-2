from __future__ import annotations

import json
import shutil
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests

import steam_production_cached as accelerator
from steam_partial_publish import (
    FailureQueue,
    catalog_run_is_publishable,
    load_previous_shortlist,
    preserve_last_known_good,
    source_coverage_metadata,
)

SOURCE = Path('scripts/steam_production.py')
OUT = Path('data/production')
SHORT = OUT / 'shortlist'
MANIFEST_PATH = OUT / 'manifest.json'
CORE_MARKER = '\nstarted = datetime.now(timezone.utc)\n'
MAX_LEADING_FAILED_SEGMENTS = 10


def load_core():
    source = SOURCE.read_text(encoding='utf-8')
    if CORE_MARKER not in source:
        raise RuntimeError('steam_production.py orchestration marker changed')
    prefix = source.split(CORE_MARKER, 1)[0]
    namespace = {'__name__': 'steam_production_core', '__file__': str(SOURCE)}
    exec(compile(prefix, str(SOURCE), 'exec'), namespace)
    return namespace


def safe_row_identity(core, row):
    try:
        key = core['identity'](row)
    except Exception:
        key = ''
    raw_appid = (row.get('data-ds-appid') or '').split(',')[0]
    if not key and raw_appid:
        key = f'App_{raw_appid}'
    title_node = row.select_one('span.title')
    title = title_node.get_text(' ', strip=True) if title_node else None
    return key, raw_appid or None, title


def collect_partial(core, failures, previous_by_key, sort_by='Name_ASC'):
    page_size = core['PAGE_SIZE']
    start = 0
    catalog = {}
    rows_seen = duplicate_rows = requests_made = 0
    total = None
    reached_end = False
    seen_pages = set()
    leading_failures = 0

    while True:
        try:
            data = core['get_page'](start, sort_by)
            requests_made += 1
            failures.resolve_segment(sort_by=sort_by, start=start, count=page_size)
            leading_failures = 0
        except Exception as exc:
            requests_made += 1
            failures.record_segment(sort_by=sort_by, start=start, count=page_size, error=exc)
            print('catalog segment failed:', sort_by, start, exc)
            start += page_size
            if total is not None and start >= total:
                reached_end = True
                break
            if total is None:
                leading_failures += 1
                if leading_failures >= MAX_LEADING_FAILED_SEGMENTS:
                    break
            time.sleep(core['REQUEST_DELAY'])
            continue

        current_total = core['to_int'](data.get('total_count'))
        if current_total is not None:
            total = current_total

        soup = core['BeautifulSoup'](data.get('results_html', ''), 'html.parser')
        rows = soup.select('a.search_result_row')
        rows_seen += len(rows)
        print(f'{sort_by}: start={start} rows={len(rows)} total={total} unique={len(catalog)}')

        if not rows:
            reached_end = True
            break

        page_keys = []
        for row in rows:
            try:
                item = core['parse_row'](row)
            except Exception as exc:
                key, appid, title = safe_row_identity(core, row)
                failures.record_game(
                    key,
                    appid=appid,
                    name=title,
                    stage='catalog_row_parse',
                    error=exc,
                    prior_site_data_exists=key in previous_by_key,
                )
                print('catalog row failed:', key or '<unknown>', exc)
                continue
            if not item:
                continue
            key = item['key']
            page_keys.append(key)
            if key in catalog:
                duplicate_rows += 1
            catalog[key] = item

        signature = tuple(page_keys)
        if signature in seen_pages:
            failures.record_segment(
                sort_by=sort_by,
                start=start,
                count=page_size,
                error=RuntimeError('Steam repeated the same page signature'),
            )
            start += page_size
            if total is not None and start >= total:
                reached_end = True
                break
            time.sleep(core['REQUEST_DELAY'])
            continue
        seen_pages.add(signature)

        start += page_size
        if len(rows) < page_size:
            reached_end = True
            break
        if total is not None and start >= total:
            reached_end = True
            break
        time.sleep(core['REQUEST_DELAY'])

    return {
        'catalog': catalog,
        'rows_seen': rows_seen,
        'duplicate_rows': duplicate_rows,
        'requests_made': requests_made,
        'total': total,
        'reached_end': reached_end,
    }


def clean(value):
    if value is None:
        return ''
    if isinstance(value, list):
        value = '|'.join(map(str, value))
    return str(value).replace('\t', ' ').replace('\r', ' ').replace('\n', ' ')


def write_shortlist(selected, columns, chunk_size):
    if SHORT.exists():
        shutil.rmtree(SHORT)
    SHORT.mkdir(parents=True, exist_ok=True)
    for chunk_number, start in enumerate(range(0, len(selected), chunk_size), start=1):
        subset = selected[start:start + chunk_size]
        lines = ['\t'.join(clean(item.get(column)) for column in columns) for item in subset]
        (SHORT / f'chunk_{chunk_number:03d}.tsv').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return (len(selected) + chunk_size - 1) // chunk_size


def run():
    started = datetime.now(timezone.utc)
    failures = FailureQueue()
    previous_by_key, previous_columns = load_previous_shortlist(SHORT)
    try:
        previous_manifest = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))
    except Exception:
        previous_manifest = {}

    core = load_core()
    traversal = collect_partial(core, failures, previous_by_key)
    catalog = traversal['catalog']
    reported_total = traversal['total']
    items = sorted(catalog.values(), key=lambda item: (item['title'].casefold(), item['key']))
    publishable = catalog_run_is_publishable(
        reached_end=traversal['reached_end'],
        unique_count=len(items),
        reported_total=reported_total,
    )
    if not publishable:
        failures.write()
        raise SystemExit('Steam traversal could not establish the end of the catalog')

    coverage = (len(items) / reported_total) if reported_total else None
    count_drift = bool(reported_total is not None and len(items) != reported_total)
    if count_drift:
        print(f'Steam total drift (informational): unique={len(items)} reported={reported_total}')

    items_with_search_review_data = sum(item['search_review_count'] is not None for item in items)
    search_review_coverage = items_with_search_review_data / len(items) if items else 0
    items_with_tags = sum(bool(item['tag_ids']) for item in items)
    tag_coverage = items_with_tags / len(items) if items else 0
    today = datetime.now(timezone.utc).date()

    review_candidate_items = []
    failed_keys = set(failures.failed_game_keys_this_run)
    for item in items:
        try:
            if core['needs_review_enrichment'](item, today):
                review_candidate_items.append(item)
        except Exception as exc:
            key = item['key']
            failures.record_game(
                key,
                appid=item.get('appid'),
                name=item.get('title'),
                stage='review_candidate_selection',
                error=exc,
                prior_site_data_exists=key in previous_by_key,
            )
            failed_keys.add(key)

    review_appids = sorted({
        str(item['appid'])
        for item in review_candidate_items
        if item.get('appid') and str(item['appid']).isdigit()
    })
    review_item_keys = {}
    for item in review_candidate_items:
        review_item_keys.setdefault(str(item.get('appid')), []).append(item['key'])

    review_cache = {}
    review_api_failed_requests = 0
    if review_appids:
        with ThreadPoolExecutor(max_workers=core['REVIEW_WORKERS']) as executor:
            futures = {
                executor.submit(core['get_review_pair'], appid): appid
                for appid in review_appids
            }
            for future in as_completed(futures):
                appid = futures[future]
                try:
                    result = future.result()
                except Exception as exc:
                    result = None
                    error = exc
                else:
                    error = None
                if (
                    result is None
                    or not result.get('global', {}).get('ok')
                    or not result.get('russian', {}).get('ok')
                ):
                    if result:
                        if not result.get('global', {}).get('ok'):
                            review_api_failed_requests += 1
                        if not result.get('russian', {}).get('ok'):
                            review_api_failed_requests += 1
                    else:
                        review_api_failed_requests += 2
                    for key in review_item_keys.get(appid, []):
                        item = catalog.get(key) or {}
                        failures.record_game(
                            key,
                            appid=appid,
                            name=item.get('title'),
                            stage='review_enrichment',
                            error=error or RuntimeError(
                                'Steam Reviews API did not return both required summaries'
                            ),
                            prior_site_data_exists=key in previous_by_key,
                        )
                        failed_keys.add(key)
                    continue
                review_cache[appid] = result

    for item in items:
        if item['key'] in failed_keys:
            continue
        appid = str(item.get('appid')) if item.get('appid') else None
        result = review_cache.get(appid) if appid else None
        if result:
            item['global_review_positive'] = result['global']['positive']
            item['global_review_count'] = result['global']['count']
            item['russian_review_positive'] = result['russian']['positive']
            item['russian_review_count'] = result['russian']['count']

    broad = []
    broad_reason_counts = Counter()
    excluded_extra = excluded_software = 0
    successful_keys = set()
    for item in items:
        key = item['key']
        if key in failed_keys:
            continue
        try:
            tags = set(item['tag_ids'])
            if core['EXTRA_RE'].search(item['title']):
                excluded_extra += 1
            elif tags & core['SOFTWARE_TAGS'] and not tags & core['GAME_TAGS']:
                excluded_software += 1
            reasons, fit_tags = core['broad_reasons'](item, today)
        except Exception as exc:
            failures.record_game(
                key,
                appid=item.get('appid'),
                name=item.get('title'),
                stage='broad_selection',
                error=exc,
                prior_site_data_exists=key in previous_by_key,
            )
            failed_keys.add(key)
            continue
        if not reasons:
            successful_keys.add(key)
            continue
        broad_reason_counts.update(reasons)
        broad.append({
            'key': key,
            'appid': item['appid'],
            'title': item['title'],
            'discount_percent': item['discount_percent'],
            'final_kzt': item['final_kzt'],
            'review_positive': item['global_review_positive'],
            'review_count': item['global_review_count'],
            'global_review_positive': item['global_review_positive'],
            'global_review_count': item['global_review_count'],
            'russian_review_positive': item['russian_review_positive'],
            'russian_review_count': item['russian_review_count'],
            'fit_tags': fit_tags,
            'release_date': item['release_date'],
            'broad_reasons': reasons,
        })

    selected = []
    refined_reason_counts = Counter()
    for item in broad:
        key = item['key']
        try:
            reasons, core_fit_count = core['refined_reasons'](item)
        except Exception as exc:
            failures.record_game(
                key,
                appid=item.get('appid'),
                name=item.get('title'),
                stage='refined_selection',
                error=exc,
                prior_site_data_exists=key in previous_by_key,
            )
            failed_keys.add(key)
            continue
        successful_keys.add(key)
        if not reasons:
            continue
        refined_reason_counts.update(reasons)
        selected.append({
            'key': key,
            'appid': item['appid'],
            'discount_percent': item['discount_percent'],
            'final_kzt': item['final_kzt'],
            'review_positive': item['global_review_positive'],
            'review_count': item['global_review_count'],
            'global_review_positive': item['global_review_positive'],
            'global_review_count': item['global_review_count'],
            'russian_review_positive': item['russian_review_positive'],
            'russian_review_count': item['russian_review_count'],
            'core_fit_count': core_fit_count,
            'reasons': reasons,
            'fit_tags': item['fit_tags'],
            'release_date': item['release_date'],
            'title': item['title'],
        })

    failures.resolve_games(successful_keys)
    selected, preserved_keys = preserve_last_known_good(
        selected,
        previous_by_key,
        failed_keys,
    )
    for key in preserved_keys:
        entry = failures.state['unresolved_games'].get(key)
        if entry:
            entry['prior_site_data_exists'] = True
            entry['last_known_good_preserved'] = True

    selected.sort(
        key=lambda item: (
            -len(item.get('reasons') or []),
            -int(item.get('core_fit_count') or 0),
            -int(item.get('discount_percent') or 0),
            float(item.get('final_kzt') or 0),
            str(item.get('title') or '').casefold(),
        )
    )

    if tag_coverage < 0.85:
        failures.write()
        raise SystemExit(f'Steam tag parsing coverage too low: {tag_coverage:.3f}')
    if search_review_coverage < 0.40:
        failures.write()
        raise SystemExit(
            f'Steam search review parsing coverage too low: {search_review_coverage:.3f}'
        )
    if not selected:
        failures.write()
        raise SystemExit('Production shortlist is empty')

    columns = previous_columns or [
        'key',
        'appid',
        'discount_percent',
        'final_kzt',
        'review_positive',
        'review_count',
        'global_review_positive',
        'global_review_count',
        'russian_review_positive',
        'russian_review_count',
        'core_fit_count',
        'reasons',
        'fit_tags',
        'release_date',
        'title',
    ]
    required_columns = [
        'key',
        'appid',
        'discount_percent',
        'final_kzt',
        'review_positive',
        'review_count',
        'global_review_positive',
        'global_review_count',
        'russian_review_positive',
        'russian_review_count',
        'core_fit_count',
        'reasons',
        'fit_tags',
        'release_date',
        'title',
    ]
    if not set(required_columns).issubset(columns):
        columns = required_columns

    finished = datetime.now(timezone.utc)
    failures.write()
    summary = failures.summary(len(successful_keys))
    source_coverage = source_coverage_metadata(
        len(failures.failed_segment_ids_this_run)
    )
    chunk_count = write_shortlist(selected, columns, core['SHORT_CHUNK'])
    logical_review_requests = len(review_appids) * 2

    manifest = {
        'collector_version': 8,
        'source': 'Steam Store',
        'country_code': 'kz',
        'region': 'Kazakhstan',
        'started_at_utc': started.isoformat(),
        'updated_at_utc': finished.isoformat(),
        'page_size': core['PAGE_SIZE'],
        'steam_total_reported': reported_total,
        'unique_items': len(items),
        'rows_seen': traversal['rows_seen'],
        'duplicate_rows_seen': traversal['duplicate_rows'],
        'requests_made': traversal['requests_made'],
        'recovery_pass_used': False,
        'traversal_pass_count': 1,
        'coverage_ratio': round(coverage, 6) if coverage is not None else None,
        'complete': source_coverage['source_complete'],
        'source_status': source_coverage['source_status'],
        'source_has_known_gaps': source_coverage['source_has_known_gaps'],
        'known_catalog_gap_count': source_coverage['known_gap_count'],
        'catalog_count_drift_informational': count_drift,
        'items_with_review_data': items_with_search_review_data,
        'review_coverage': round(search_review_coverage, 6),
        'items_with_search_review_data': items_with_search_review_data,
        'search_review_coverage': round(search_review_coverage, 6),
        'review_candidate_items': len(review_candidate_items),
        'review_candidate_appids': len(review_appids),
        'review_api_requests': logical_review_requests,
        'review_api_failed_requests': review_api_failed_requests,
        'review_api_failure_rate': (
            round(review_api_failed_requests / logical_review_requests, 6)
            if logical_review_requests
            else 0
        ),
        'global_review_appids_ok': len(review_cache),
        'russian_review_appids_ok': len(review_cache),
        'review_selection_rule': 'global_count_and_global_or_russian_rating',
        'review_count_basis': 'global',
        'russian_review_count_cap': core['RUSSIAN_REVIEW_COUNT_CAP'],
        'russian_rating_comparison': 'steam_display_whole_percent',
        'review_policy_regression_guard': True,
        'review_threshold_profile': core['REVIEW_THRESHOLD_PROFILE'],
        'review_thresholds': dict(core['REVIEW_THRESHOLDS']),
        'global_review_language': 'all',
        'russian_review_language': 'russian',
        'review_purchase_type': 'all',
        'items_with_tags': items_with_tags,
        'tag_coverage': round(tag_coverage, 6),
        'excluded_obvious_extras': excluded_extra,
        'excluded_software_only': excluded_software,
        'broad_shortlist_items': len(broad),
        'shortlist_items': len(selected),
        'shortlist_chunk_size': core['SHORT_CHUNK'],
        'shortlist_chunk_count': chunk_count,
        'free_items': previous_manifest.get('free_items'),
        'needs_tuning': len(selected) > 800,
        'broad_reason_counts': dict(broad_reason_counts),
        'reason_counts': dict(refined_reason_counts),
        'partial_publish_failure_queue': (
            'data/cache/steam_partial_publish_failures.json'
        ),
        'partial_publish_summary': summary,
        'last_known_good_games_preserved': len(preserved_keys),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    index = {
        'version': 8,
        'format': 'tsv',
        'columns': columns,
        'country_code': 'kz',
        'item_count': len(selected),
        'chunk_size': core['SHORT_CHUNK'],
        'chunk_count': chunk_count,
        'chunk_pattern': 'data/production/shortlist/chunk_NNN.tsv',
        'source_total': reported_total,
        'source_complete': source_coverage['source_complete'],
        'source_status': source_coverage['source_status'],
        'source_has_known_gaps': source_coverage['source_has_known_gaps'],
        'known_catalog_gap_count': source_coverage['known_gap_count'],
        'source_coverage_ratio': round(coverage, 6) if coverage is not None else None,
        'source_updated_at_utc': finished.isoformat(),
        'needs_tuning': len(selected) > 800,
        'review_selection_rule': 'global_count_and_global_or_russian_rating',
        'review_count_basis': 'global',
        'russian_review_count_cap': core['RUSSIAN_REVIEW_COUNT_CAP'],
        'russian_rating_comparison': 'steam_display_whole_percent',
        'review_policy_regression_guard': True,
        'review_threshold_profile': core['REVIEW_THRESHOLD_PROFILE'],
        'review_thresholds': dict(core['REVIEW_THRESHOLDS']),
        'review_fields': {
            'global': ['global_review_positive', 'global_review_count'],
            'russian': ['russian_review_positive', 'russian_review_count'],
        },
        'reason_counts': dict(refined_reason_counts),
        'partial_publish_summary': summary,
    }
    (SHORT / 'index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def main():
    requests.Session.get = accelerator.cached_session_get
    time.sleep = accelerator.optimized_sleep
    succeeded = False
    try:
        run()
        succeeded = True
    finally:
        requests.Session.get = accelerator._real_session_get
        time.sleep = accelerator._real_sleep
        accelerator.write_cache()
    if succeeded:
        accelerator.annotate_manifest()
    print(
        'Steam collector accelerator:',
        json.dumps(accelerator._stats, ensure_ascii=False, sort_keys=True),
    )


if __name__ == '__main__':
    main()
