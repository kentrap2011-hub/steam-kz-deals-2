from __future__ import annotations

import json
import shutil
import threading
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
PROGRESS_HEARTBEAT_SECONDS = 30
SEARCH_PROGRESS_EVERY_PAGES = 20
REVIEW_PROGRESS_EVERY_APPIDS = 50


def load_core():
    source = SOURCE.read_text(encoding='utf-8')
    if CORE_MARKER not in source:
        raise RuntimeError('steam_production.py orchestration marker changed')
    prefix = source.split(CORE_MARKER, 1)[0]
    namespace = {'__name__': 'steam_production_core', '__file__': str(SOURCE)}
    exec(compile(prefix, str(SOURCE), 'exec'), namespace)
    return namespace


class ProgressReporter:
    def __init__(
        self,
        *,
        stats_provider=None,
        heartbeat_seconds=PROGRESS_HEARTBEAT_SECONDS,
    ):
        self.stats_provider = stats_provider
        self.heartbeat_seconds = float(heartbeat_seconds)
        self.started_monotonic = time.monotonic()
        self.stage_started_monotonic = self.started_monotonic
        self._state = {'stage': 'initializing'}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = None

    def set_stage(self, stage, **fields):
        with self._lock:
            self.stage_started_monotonic = time.monotonic()
            self._state = {'stage': str(stage), **fields}
        self.emit('stage')

    def update(self, *, emit=False, **fields):
        with self._lock:
            self._state.update(fields)
        if emit:
            self.emit('progress')

    def snapshot(self, event='heartbeat'):
        now = time.monotonic()
        with self._lock:
            state = dict(self._state)
            stage_started = self.stage_started_monotonic
        payload = {
            'event': event,
            'elapsed_seconds': round(now - self.started_monotonic, 1),
            'stage_elapsed_seconds': round(now - stage_started, 1),
            **state,
        }
        if self.stats_provider is not None:
            try:
                payload['network'] = dict(self.stats_provider())
            except Exception as exc:
                payload['network_stats_error'] = str(exc)
        return payload

    def emit(self, event='heartbeat'):
        print(
            '[steam-progress]',
            json.dumps(
                self.snapshot(event),
                ensure_ascii=False,
                sort_keys=True,
            ),
            flush=True,
        )

    def _heartbeat_loop(self):
        while not self._stop.wait(self.heartbeat_seconds):
            self.emit('heartbeat')

    def start(self):
        if self._thread is not None:
            return
        self._thread = threading.Thread(
            target=self._heartbeat_loop,
            name='steam-progress-heartbeat',
            daemon=True,
        )
        self._thread.start()
        self.emit('start')

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1)
        self.emit('stop')


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


def parse_probe_items(core, data):
    soup = core['BeautifulSoup'](data.get('results_html', ''), 'html.parser')
    rows = soup.select('a.search_result_row')
    items = []
    for row in rows:
        item = core['parse_row'](row)
        if not item:
            raise RuntimeError('Steam price-bound probe returned an unparseable result row')
        price = item.get('final_kzt')
        if price is None:
            raise RuntimeError(
                f"Steam price-bound probe returned row without final KZT price: {item.get('key')}"
            )
        items.append(item)
    return items


def price_probe_summary(core, data):
    items = parse_probe_items(core, data)
    prices = [
        float(item['final_kzt'])
        for item in items
        if item.get('final_kzt') is not None
    ]
    return {
        'total_count': core['to_int'](data.get('total_count')),
        'row_count': len(items),
        'min_price_kzt': min(prices) if prices else None,
        'max_price_kzt': max(prices) if prices else None,
    }


def validate_kz_source_price_bound(core):
    """
    Prove that the exact live KZ maxprice=4500 filter is active without relying
    on Steam's Price_ASC ordering being globally monotonic.

    Steam Search can return locally non-monotonic price ordering, so ordering is
    not a completeness authority. Instead:
      * every supported paid partition is probed with maxprice=4500 +
        Price_DESC and must return no over-cap row;
      * the games partition is checked with a second capped sort and must report
        the same capped total;
      * an otherwise-identical uncapped Price_DESC control must currently expose
        an over-cap row and a larger total, directly proving that maxprice=4500
        materially applies to the KZ response rather than being ignored.

    Production still applies the local <=4500 KZT gate to every parsed row.
    """
    cap = core['PAID_MAX_PRICE_KZT']
    partition_evidence = {}
    logical_requests = 0

    for partition in core['SEARCH_PARTITIONS']:
        data = core['get_page'](
            0,
            'Price_DESC',
            category1=partition['category1'],
            maxprice_kzt=cap,
            hidef2p=True,
        )
        logical_requests += 1
        summary = price_probe_summary(core, data)
        total = summary['total_count']
        if total is None or total < 0:
            raise RuntimeError(
                'Cannot validate KZ maxprice: '
                f"{partition['id']} capped total is unknown"
            )
        if (
            summary['max_price_kzt'] is not None
            and summary['max_price_kzt'] > cap
        ):
            raise RuntimeError(
                'Cannot validate KZ maxprice: '
                f"{partition['id']} maxprice={cap} leaked "
                f"{summary['max_price_kzt']} KZT"
            )
        partition_evidence[partition['id']] = {
            'category1': partition['category1'],
            **summary,
        }

    games = next(
        partition for partition in core['SEARCH_PARTITIONS']
        if partition['id'] == 'games'
    )
    capped_games = partition_evidence['games']

    capped_name = core['get_page'](
        0,
        'Name_ASC',
        category1=games['category1'],
        maxprice_kzt=cap,
        hidef2p=True,
    )
    logical_requests += 1
    capped_name_summary = price_probe_summary(core, capped_name)
    if capped_name_summary['total_count'] != capped_games['total_count']:
        raise RuntimeError(
            'Cannot validate KZ maxprice: capped total changes with sort '
            f"({capped_games['total_count']} != "
            f"{capped_name_summary['total_count']})"
        )
    if (
        capped_name_summary['max_price_kzt'] is not None
        and capped_name_summary['max_price_kzt'] > cap
    ):
        raise RuntimeError(
            'Cannot validate KZ maxprice: Name_ASC capped sample leaked '
            f"{capped_name_summary['max_price_kzt']} KZT"
        )

    uncapped_games = core['get_page'](
        0,
        'Price_DESC',
        category1=games['category1'],
        hidef2p=True,
    )
    logical_requests += 1
    uncapped_summary = price_probe_summary(core, uncapped_games)
    uncapped_total = uncapped_summary['total_count']
    if uncapped_total is None or uncapped_total <= capped_games['total_count']:
        raise RuntimeError(
            'Cannot validate KZ maxprice: uncapped games control does not '
            'have a larger source total than maxprice=4500'
        )
    if (
        uncapped_summary['max_price_kzt'] is None
        or uncapped_summary['max_price_kzt'] <= cap
    ):
        raise RuntimeError(
            'Cannot validate KZ maxprice: uncapped games control did not '
            'expose an over-cap KZT row'
        )

    return {
        'validated': True,
        'country_code': 'kz',
        'maxprice_kzt': cap,
        'hidef2p': True,
        'partition_price_desc_checks': partition_evidence,
        'games_sort_invariant_check': {
            'sort_by': 'Name_ASC',
            **capped_name_summary,
        },
        'games_uncapped_control': uncapped_summary,
        'logical_requests': logical_requests,
        'proof': (
            'all_capped_partition_price_desc_samples_at_or_below_kzt_cap;'
            'games_capped_total_sort_invariant;'
            'uncapped_games_control_has_larger_total_and_over_cap_row'
        ),
        'price_asc_monotonicity_required': False,
    }

def collect_partial(core, failures, previous_by_key, partition, sort_by='Name_ASC', reporter=None):
    page_size = core['PAGE_SIZE']
    cap = core['PAID_MAX_PRICE_KZT']
    partition_id = partition['id']
    category1 = partition['category1']
    failure_scope = f'{partition_id}:{sort_by}'
    start = 0
    catalog = {}
    rows_seen = parsed_rows = eligible_rows_seen = duplicate_rows = requests_made = 0
    total = None
    reached_end = False
    seen_pages = set()
    leading_failures = 0
    rejection_counts = Counter()
    partition_started = time.monotonic()

    if reporter is not None:
        reporter.set_stage(
            'search_traversal',
            partition=partition_id,
            category1=category1,
            sort_by=sort_by,
            page_size=page_size,
            source_maxprice_kzt=cap,
            page_number=0,
            logical_page_requests=0,
            rows_seen=0,
            reported_total=None,
            progress_percent=None,
            eligible_rows_after_local_gate=0,
            duplicate_rows=0,
        )

    while True:
        try:
            data = core['get_page'](
                start,
                sort_by,
                category1=category1,
                maxprice_kzt=cap,
                hidef2p=True,
            )
            requests_made += 1
            failures.resolve_segment(
                sort_by=failure_scope,
                start=start,
                count=page_size,
            )
            leading_failures = 0
        except Exception as exc:
            requests_made += 1
            failures.record_segment(
                sort_by=failure_scope,
                start=start,
                count=page_size,
                error=exc,
            )
            if reporter is not None:
                reporter.update(
                    page_number=(start // page_size) + 1,
                    logical_page_requests=requests_made,
                    rows_seen=rows_seen,
                    reported_total=total,
                    eligible_rows_after_local_gate=eligible_rows_seen,
                    duplicate_rows=duplicate_rows,
                    last_event='catalog_segment_failed',
                    last_error=str(exc),
                    emit=True,
                )
            print(
                'catalog segment failed:',
                partition_id,
                sort_by,
                start,
                exc,
                flush=True,
            )
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
        if not rows:
            reached_end = True
            break

        page_keys = []
        for row in rows:
            raw_key, _, _ = safe_row_identity(core, row)
            if raw_key:
                page_keys.append(raw_key)
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
                print('catalog row failed:', partition_id, key or '<unknown>', exc)
                continue
            if not item:
                rejection_counts['unparseable_or_missing_title'] += 1
                continue

            parsed_rows += 1
            rejection = core['paid_source_rejection_reason'](item)
            if rejection:
                rejection_counts[rejection] += 1
                continue

            eligible_rows_seen += 1
            key = item['key']
            if key in catalog:
                duplicate_rows += 1
            catalog[key] = item

        page_number = (start // page_size) + 1
        progress_percent = (
            round(min(rows_seen, total) * 100.0 / total, 2)
            if total
            else None
        )
        if reporter is not None:
            reporter.update(
                page_number=page_number,
                logical_page_requests=requests_made,
                current_start=start,
                rows_seen=rows_seen,
                reported_total=total,
                progress_percent=progress_percent,
                eligible_rows_after_local_gate=eligible_rows_seen,
                duplicate_rows=duplicate_rows,
                emit=(
                    page_number == 1
                    or page_number % SEARCH_PROGRESS_EVERY_PAGES == 0
                ),
            )

        signature = tuple(page_keys)
        if signature in seen_pages:
            failures.record_segment(
                sort_by=failure_scope,
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

    partition_elapsed_seconds = round(
        time.monotonic() - partition_started,
        3,
    )
    if reporter is not None:
        reporter.update(
            partition_complete=True,
            logical_page_requests=requests_made,
            rows_seen=rows_seen,
            reported_total=total,
            progress_percent=(
                round(min(rows_seen, total) * 100.0 / total, 2)
                if total
                else None
            ),
            eligible_rows_after_local_gate=eligible_rows_seen,
            duplicate_rows=duplicate_rows,
            partition_elapsed_seconds=partition_elapsed_seconds,
            emit=True,
        )

    return {
        'partition_id': partition_id,
        'category1': category1,
        'catalog': catalog,
        'rows_seen': rows_seen,
        'parsed_rows': parsed_rows,
        'eligible_rows_seen': eligible_rows_seen,
        'rejection_counts': dict(rejection_counts),
        'duplicate_rows': duplicate_rows,
        'requests_made': requests_made,
        'total': total,
        'reached_end': reached_end,
        'elapsed_seconds': partition_elapsed_seconds,
    }


def merge_partition_traversals(traversals):
    catalog = {}
    provenance = {}
    cross_partition_duplicates = 0

    for traversal in traversals:
        partition_id = traversal['partition_id']
        for key in sorted(traversal['catalog']):
            provenance.setdefault(key, []).append(partition_id)
            if key in catalog:
                cross_partition_duplicates += 1
                continue
            catalog[key] = traversal['catalog'][key]

    return catalog, provenance, cross_partition_duplicates


def row_meets_current_paid_gate(core, row):
    discount = core['to_int'](row.get('discount_percent'))
    try:
        price = float(row.get('final_kzt'))
    except (TypeError, ValueError):
        price = None
    return bool(
        discount is not None
        and discount >= core['PAID_MIN_DISCOUNT_PERCENT']
        and price is not None
        and 0 < price <= core['PAID_MAX_PRICE_KZT']
    )


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


STORE_BROWSE_URL = 'https://api.steampowered.com/IStoreBrowseService/GetItems/v1/'
REVIEW_FALLBACK_BATCH_SIZE = 100
STORE_BROWSE_RETRIES = 5
STORE_BROWSE_MIN_INTERVAL_SECONDS = 1.0


def conservative_global_display_percent(value):
    if value is None:
        return None
    # StoreBrowse/Search expose Steam's displayed whole percent. The canonical
    # global rule may compare the more precise AppReviews percentage. Subtract
    # half a point so rounded display data can never create a false positive.
    return max(0.0, float(value) - 0.5)


def search_surface_review_pair(item, maximum_rating_threshold):
    """
    Reuse Search review data only when it is decisive for every current review
    gate: either the global count is below the minimum 100-review gate, or the
    conservative global display percentage already clears the highest current
    rating threshold. All ambiguous rows continue to a richer review source.
    """
    count = item.get('search_review_count')
    display = item.get('search_review_positive')
    if count is None or display is None:
        return None
    count = int(count)
    conservative = conservative_global_display_percent(display)
    if count >= 100 and (
        conservative is None
        or conservative < float(maximum_rating_threshold)
    ):
        return None
    return {
        'global': {
            'ok': True,
            'positive': conservative,
            'count': count,
            'rate_limited': False,
            'source': 'steam_search_conservative_display_decisive',
        },
        'russian': {
            # Russian evidence is unnecessary in these two decisive cases:
            # below 100 global reviews no current rule can pass its global-count
            # baseline; at/above the maximum rating threshold global quality
            # already satisfies every current rating gate that the count allows.
            'ok': True,
            'positive': None,
            'count': 0,
            'rate_limited': False,
            'source': 'not_required_search_surface_decisive',
        },
    }


def storebrowse_review_pair(store_item):
    reviews = (store_item or {}).get('reviews') or {}
    global_summary = reviews.get('summary_filtered') or {}
    russian_summary = reviews.get('summary_language_specific') or {}

    global_count = int(global_summary.get('review_count') or 0)
    global_display = global_summary.get('percent_positive')
    global_ok = global_display is not None or global_count == 0

    russian_count = int(russian_summary.get('review_count') or 0)
    russian_display = russian_summary.get('percent_positive')

    return {
        'global': {
            'ok': global_ok,
            'positive': conservative_global_display_percent(global_display),
            'display_positive': (
                float(global_display) if global_display is not None else None
            ),
            'count': global_count,
            'rate_limited': False,
            'source': 'storebrowse_summary_filtered_conservative_display',
        },
        'russian': {
            # Missing language-specific summary is equivalent to no usable
            # Russian-language sample; global review eligibility can still pass.
            'ok': True,
            'positive': float(russian_display) if russian_display is not None else None,
            'count': russian_count,
            'rate_limited': False,
            'source': 'storebrowse_summary_language_specific',
        },
    }


def _retry_after_seconds(response):
    try:
        value = int(response.headers.get('Retry-After'))
    except (AttributeError, TypeError, ValueError):
        return None
    return value if value > 0 else None


def fetch_storebrowse_review_fallback(appids, reporter=None):
    """
    Fetch batched StoreBrowse review summaries without losing already-completed
    batches when one request fails. This is intentionally sequential and paced;
    a failed batch is retried in place and, after exhaustion, isolated so other
    appids can still progress to AppReviews fallback.
    """
    results = {}
    ordered = [str(appid) for appid in appids if str(appid).isdigit()]
    stats = {
        'physical_http_requests': 0,
        'successful_batches': 0,
        'failed_batches': 0,
        'retry_events': 0,
        'http_429_events': 0,
        'backoff_seconds': 0.0,
        'pacing_seconds': 0.0,
    }
    last_request_monotonic = None

    for batch_number, start in enumerate(
        range(0, len(ordered), REVIEW_FALLBACK_BATCH_SIZE),
        start=1,
    ):
        batch = ordered[start:start + REVIEW_FALLBACK_BATCH_SIZE]
        payload = {
            'ids': [{'appid': int(appid)} for appid in batch],
            'context': {
                'language': 'russian',
                'country_code': 'KZ',
                'steam_realm': 1,
            },
            'data_request': {
                'include_reviews': True,
                'include_basic_info': True,
                'apply_user_filters': False,
            },
        }

        returned = None
        last_error = None
        for attempt in range(STORE_BROWSE_RETRIES):
            if last_request_monotonic is not None:
                elapsed = time.monotonic() - last_request_monotonic
                pacing_wait = max(0.0, STORE_BROWSE_MIN_INTERVAL_SECONDS - elapsed)
                if pacing_wait:
                    stats['pacing_seconds'] += pacing_wait
                    time.sleep(pacing_wait)

            try:
                stats['physical_http_requests'] += 1
                response = requests.get(
                    STORE_BROWSE_URL,
                    params={'input_json': json.dumps(payload, separators=(',', ':'))},
                    headers={
                        'User-Agent': 'steam-kz-deals/1.0',
                        'Accept': 'application/json',
                    },
                    timeout=30,
                )
                last_request_monotonic = time.monotonic()

                if getattr(response, 'status_code', None) == 429:
                    stats['http_429_events'] += 1
                    stats['retry_events'] += 1
                    wait = _retry_after_seconds(response)
                    if wait is None:
                        wait = float(min(30, 2 ** attempt))
                    stats['backoff_seconds'] += float(wait)
                    time.sleep(float(wait))
                    last_error = RuntimeError('StoreBrowse HTTP 429')
                    continue

                response.raise_for_status()
                returned = (
                    (response.json().get('response') or {}).get('store_items')
                    or []
                )
                break
            except Exception as exc:
                last_error = exc
                stats['retry_events'] += 1
                if attempt + 1 < STORE_BROWSE_RETRIES:
                    wait = float(min(20, 2 ** attempt))
                    stats['backoff_seconds'] += wait
                    time.sleep(wait)

        if returned is None:
            stats['failed_batches'] += 1
            print(
                '[steam-network] StoreBrowse review batch failed:',
                'batch=', batch_number,
                'appids=', len(batch),
                'error=', last_error,
                flush=True,
            )
        else:
            stats['successful_batches'] += 1
            for store_item in returned:
                appid = str(store_item.get('appid') or store_item.get('id') or '')
                if appid in batch:
                    results[appid] = storebrowse_review_pair(store_item)

        if reporter is not None:
            reporter.update(
                fallback_batches_completed=(
                    stats['successful_batches'] + stats['failed_batches']
                ),
                fallback_http_requests=stats['physical_http_requests'],
                fallback_429_events=stats['http_429_events'],
                fallback_failed_batches=stats['failed_batches'],
                fallback_appids_total=len(ordered),
                fallback_appids_attempted=min(start + len(batch), len(ordered)),
                emit=(
                    batch_number == 1
                    or batch_number % 5 == 0
                    or start + len(batch) >= len(ordered)
                ),
            )

    return results, stats


def run():
    started = datetime.now(timezone.utc)
    failures = FailureQueue()
    previous_by_key, previous_columns = load_previous_shortlist(SHORT)
    try:
        previous_manifest = json.loads(MANIFEST_PATH.read_text(encoding='utf-8'))
    except Exception:
        previous_manifest = {}

    core = load_core()
    reporter = ProgressReporter(
        stats_provider=core.get('network_stats_snapshot'),
    )
    reporter.start()
    stage_timings_seconds = {}

    reporter.set_stage(
        'source_validation',
        source_maxprice_kzt=core['PAID_MAX_PRICE_KZT'],
        partitions=[
            partition['id']
            for partition in core['SEARCH_PARTITIONS']
        ],
    )
    source_validation_started = time.monotonic()
    try:
        source_price_bound_validation = validate_kz_source_price_bound(core)
    except Exception as exc:
        reporter.set_stage(
            'source_validation_failed',
            error=str(exc),
        )
        reporter.stop()
        failures.write()
        raise SystemExit(f'Steam KZ source price-bound validation failed: {exc}')

    stage_timings_seconds['source_validation'] = round(
        time.monotonic() - source_validation_started,
        3,
    )
    reporter.update(
        validated=True,
        validation_elapsed_seconds=stage_timings_seconds['source_validation'],
        validation_requests=source_price_bound_validation['logical_requests'],
        emit=True,
    )

    traversals = []
    for partition in core['SEARCH_PARTITIONS']:
        traversal = collect_partial(
            core,
            failures,
            previous_by_key,
            partition,
            reporter=reporter,
        )
        publishable = catalog_run_is_publishable(
            reached_end=traversal['reached_end'],
            unique_count=len(traversal['catalog']),
            reported_total=traversal['total'],
        )
        if not publishable:
            reporter.set_stage(
                'search_traversal_failed',
                partition=partition['id'],
                rows_seen=traversal['rows_seen'],
                reported_total=traversal['total'],
            )
            reporter.stop()
            failures.write()
            raise SystemExit(
                'Steam traversal could not establish the end of partition '
                f"{partition['id']}"
            )
        traversals.append(traversal)

    local_filter_started = time.monotonic()
    reporter.set_stage(
        'local_merge_filter',
        partition_count=len(traversals),
        partition_rows_seen=sum(
            traversal['rows_seen']
            for traversal in traversals
        ),
    )
    catalog, partition_provenance, cross_partition_duplicates = (
        merge_partition_traversals(traversals)
    )
    items = sorted(
        catalog.values(),
        key=lambda item: (item['title'].casefold(), item['key']),
    )

    reported_total = sum(
        int(traversal['total'] or 0)
        for traversal in traversals
    )
    rows_seen = sum(traversal['rows_seen'] for traversal in traversals)
    parsed_rows = sum(traversal['parsed_rows'] for traversal in traversals)
    eligible_rows_seen = sum(
        traversal['eligible_rows_seen']
        for traversal in traversals
    )
    source_rejection_counts = Counter()
    for traversal in traversals:
        source_rejection_counts.update(traversal['rejection_counts'])

    coverage = (
        min(1.0, rows_seen / reported_total)
        if reported_total
        else None
    )
    count_drift = any(
        traversal['total'] is not None
        and traversal['rows_seen'] != traversal['total']
        for traversal in traversals
    )
    if count_drift:
        print(
            'Steam partition total drift (informational):',
            [
                (
                    traversal['partition_id'],
                    traversal['rows_seen'],
                    traversal['total'],
                )
                for traversal in traversals
            ],
            flush=True,
        )

    partition_stats = [
        {
            'id': traversal['partition_id'],
            'category1': traversal['category1'],
            'reported_total': traversal['total'],
            'rows_seen': traversal['rows_seen'],
            'parsed_rows': traversal['parsed_rows'],
            'eligible_rows_after_local_gate': traversal['eligible_rows_seen'],
            'unique_eligible_items': len(traversal['catalog']),
            'rejection_counts': traversal['rejection_counts'],
            'duplicate_rows_seen': traversal['duplicate_rows'],
            'requests_made': traversal['requests_made'],
            'reached_end': traversal['reached_end'],
            'elapsed_seconds': traversal['elapsed_seconds'],
        }
        for traversal in traversals
    ]
    collection_requests = sum(
        traversal['requests_made']
        for traversal in traversals
    )
    source_requests = (
        collection_requests
        + source_price_bound_validation['logical_requests']
    )
    multi_partition_identity_count = sum(
        len(partitions) > 1
        for partitions in partition_provenance.values()
    )

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

    stage_timings_seconds['local_merge_filter'] = round(
        time.monotonic() - local_filter_started,
        3,
    )
    reporter.update(
        unique_eligible_after_partition_dedupe=len(items),
        review_candidate_items=len(review_candidate_items),
        review_candidate_appids=len(review_appids),
        local_filter_elapsed_seconds=stage_timings_seconds['local_merge_filter'],
        emit=True,
    )

    review_started = time.monotonic()
    review_logical_components_required = len(review_appids) * 2
    reporter.set_stage(
        'review_enrichment',
        candidate_items=len(review_candidate_items),
        candidate_appids=len(review_appids),
        completed_appids=0,
        logical_review_requests_total=review_logical_components_required,
        logical_review_requests_completed=0,
        workers=core['REVIEW_WORKERS'],
    )

    review_cache = {}
    review_api_failed_requests = 0
    review_failed_results = {}
    review_search_surface_reused_appids = 0
    review_exact_cache_reused_appids = 0
    review_storebrowse_fallback_appids = 0
    review_appreviews_successful_appids = 0
    review_appreviews_attempted_appids = set()
    review_appreviews_logical_components_attempted = 0
    review_storebrowse_stats = {
        'physical_http_requests': 0,
        'successful_batches': 0,
        'failed_batches': 0,
        'retry_events': 0,
        'http_429_events': 0,
        'backoff_seconds': 0.0,
        'pacing_seconds': 0.0,
    }

    review_items_by_appid = {}
    for item in review_candidate_items:
        review_items_by_appid.setdefault(str(item.get('appid')), []).append(item)

    if review_appids:
        maximum_rating_threshold = max(core['REVIEW_THRESHOLDS'].values())
        storebrowse_needed = []

        # Search review summaries are reused only in two mathematically decisive
        # cases. A conflicting Search summary for the same appid is not trusted.
        for appid in review_appids:
            candidates = review_items_by_appid.get(appid, [])
            signatures = {
                (
                    int(item['search_review_count']),
                    int(item['search_review_positive']),
                )
                for item in candidates
                if item.get('search_review_count') is not None
                and item.get('search_review_positive') is not None
            }
            search_pair = None
            if len(signatures) == 1:
                count, positive = next(iter(signatures))
                representative = dict(candidates[0])
                representative['search_review_count'] = count
                representative['search_review_positive'] = positive
                search_pair = search_surface_review_pair(
                    representative,
                    maximum_rating_threshold,
                )

            if search_pair is not None:
                review_cache[appid] = search_pair
                review_search_surface_reused_appids += 1
                continue

            # Exact AppReviews cache remains the next-cheapest source when both
            # components are still fresh. Prechecking prevents cache misses from
            # becoming bulk live AppReviews traffic.
            if (
                accelerator.valid_cached_entry(appid, 'all') is not None
                and accelerator.valid_cached_entry(appid, 'russian') is not None
            ):
                cached_pair = core['get_review_pair'](appid)
                if (
                    cached_pair.get('global', {}).get('ok')
                    and cached_pair.get('russian', {}).get('ok')
                ):
                    review_cache[appid] = cached_pair
                    review_exact_cache_reused_appids += 1
                    continue

            storebrowse_needed.append(appid)

        fallback = {}
        if storebrowse_needed:
            fallback, review_storebrowse_stats = fetch_storebrowse_review_fallback(
                storebrowse_needed,
                reporter=reporter,
            )

        appreviews_needed = []
        for appid in storebrowse_needed:
            fallback_pair = fallback.get(appid) or {}
            if (
                fallback_pair.get('global', {}).get('ok')
                and fallback_pair.get('russian', {}).get('ok')
            ):
                review_cache[appid] = fallback_pair
                review_storebrowse_fallback_appids += 1
            else:
                appreviews_needed.append(appid)

        # Live AppReviews is now a serial exact fallback only for appids that
        # Search/cache/StoreBrowse could not resolve.
        review_appreviews_attempted_appids = set(appreviews_needed)
        review_appreviews_logical_components_attempted = len(appreviews_needed) * 2
        if appreviews_needed:
            with ThreadPoolExecutor(max_workers=core['REVIEW_WORKERS']) as executor:
                futures = {
                    executor.submit(core['get_review_pair'], appid): appid
                    for appid in appreviews_needed
                }
                completed_appreviews = 0
                for future in as_completed(futures):
                    appid = futures[future]
                    try:
                        result = future.result()
                    except Exception as exc:
                        result = None
                        error = exc
                    else:
                        error = None

                    completed_appreviews += 1
                    fallback_pair = fallback.get(appid) or {}
                    merged = {}
                    for language in ('global', 'russian'):
                        exact = (result or {}).get(language) or {}
                        alternate = fallback_pair.get(language) or {}
                        if exact.get('ok'):
                            merged[language] = exact
                        elif alternate.get('ok'):
                            merged[language] = alternate
                        else:
                            merged[language] = exact or alternate

                    global_ok = bool(merged.get('global', {}).get('ok'))
                    russian_ok = bool(merged.get('russian', {}).get('ok'))
                    if global_ok and russian_ok:
                        review_cache[appid] = merged
                        review_appreviews_successful_appids += 1
                    else:
                        review_api_failed_requests += (
                            int(not global_ok) + int(not russian_ok)
                        )
                        review_failed_results[appid] = {
                            'result': result,
                            'error': error,
                        }

                    reporter.update(
                        completed_appids=(
                            len(review_cache) + len(review_failed_results)
                        ),
                        appreviews_fallback_appids_total=len(appreviews_needed),
                        appreviews_fallback_appids_completed=completed_appreviews,
                        logical_review_requests_completed=(
                            min(
                                review_logical_components_required,
                                (
                                    len(review_cache)
                                    + len(review_failed_results)
                                ) * 2,
                            )
                        ),
                        emit=(
                            completed_appreviews == 1
                            or completed_appreviews == len(appreviews_needed)
                            or completed_appreviews % REVIEW_PROGRESS_EVERY_APPIDS == 0
                        ),
                    )

        for appid in review_appids:
            if appid in review_cache or appid in review_failed_results:
                continue
            review_failed_results[appid] = {
                'result': fallback.get(appid),
                'error': RuntimeError(
                    'Steam review sources did not return required summaries'
                ),
            }

        for appid, failure in review_failed_results.items():
            for key in review_item_keys.get(appid, []):
                item = catalog.get(key) or {}
                failures.record_game(
                    key,
                    appid=appid,
                    name=item.get('title'),
                    stage='review_enrichment',
                    error=failure.get('error') or RuntimeError(
                        'Steam review sources did not return required summaries'
                    ),
                    prior_site_data_exists=key in previous_by_key,
                )
                failed_keys.add(key)

    review_candidate_items_resolved_without_appreviews = sum(
        1
        for item in review_candidate_items
        if str(item.get('appid')) in review_cache
        and str(item.get('appid')) not in review_appreviews_attempted_appids
    )

    stage_timings_seconds['review_enrichment'] = round(
        time.monotonic() - review_started,
        3,
    )
    reporter.update(
        review_enrichment_complete=True,
        completed_appids=len(review_appids),
        logical_review_requests_completed=review_logical_components_required,
        review_failed_appids=len(review_failed_results),
        search_surface_reused_appids=review_search_surface_reused_appids,
        exact_cache_reused_appids=review_exact_cache_reused_appids,
        storebrowse_fallback_appids=review_storebrowse_fallback_appids,
        storebrowse_fallback_requests=review_storebrowse_stats[
            'physical_http_requests'
        ],
        appreviews_fallback_appids=len(review_appreviews_attempted_appids),
        review_elapsed_seconds=stage_timings_seconds['review_enrichment'],
        emit=True,
    )

    shortlist_started = time.monotonic()
    reporter.set_stage(
        'shortlist_selection',
        eligible_items=len(items),
        failed_keys=len(failed_keys),
    )

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
    excluded_extra = int(source_rejection_counts.get('obvious_extra', 0))
    excluded_software = int(source_rejection_counts.get('software_only', 0))
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
    preserved_key_set = set(preserved_keys)
    dropped_preserved_due_current_paid_gate = []
    paid_gate_selected = []
    for row in selected:
        if row_meets_current_paid_gate(core, row):
            paid_gate_selected.append(row)
            continue
        if str(row.get('key')) in preserved_key_set:
            dropped_preserved_due_current_paid_gate.append(str(row.get('key')))
    selected = paid_gate_selected
    preserved_keys = [
        key
        for key in preserved_keys
        if key not in dropped_preserved_due_current_paid_gate
    ]

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

    stage_timings_seconds['shortlist_selection'] = round(
        time.monotonic() - shortlist_started,
        3,
    )
    reporter.update(
        broad_shortlist_items=len(broad),
        paid_shortlist_items=len(selected),
        preserved_last_known_good=len(preserved_keys),
        shortlist_elapsed_seconds=stage_timings_seconds['shortlist_selection'],
        emit=True,
    )

    persistence_started = time.monotonic()
    reporter.set_stage(
        'persistence_preparation',
        paid_shortlist_items=len(selected),
    )

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
    logical_review_requests = review_appreviews_logical_components_attempted
    review_network_stats = core['network_stats_snapshot']()
    shortlist_items_without_appreviews = sum(
        1
        for item in selected
        if str(item.get('appid')) not in review_appreviews_attempted_appids
    )

    filtering_funnel = {
        'source_reported_rows': reported_total,
        'source_rows_seen': rows_seen,
        'parsed_rows': parsed_rows,
        'removed_non_paid_or_missing_price': int(
            source_rejection_counts.get('non_paid_or_missing_price', 0)
        ),
        'removed_discount_below_50': int(
            source_rejection_counts.get('discount_below_minimum', 0)
        ),
        'removed_price_above_4500': int(
            source_rejection_counts.get('price_above_maximum', 0)
        ),
        'removed_obvious_extras': int(
            source_rejection_counts.get('obvious_extra', 0)
        ),
        'removed_software_only': int(
            source_rejection_counts.get('software_only', 0)
        ),
        'eligible_rows_before_partition_dedupe': eligible_rows_seen,
        'unique_eligible_after_partition_dedupe': len(items),
        'review_candidate_items': len(review_candidate_items),
        'review_candidate_appids': len(review_appids),
        'broad_shortlist_items': len(broad),
        'paid_shortlist_items': len(selected),
        'last_known_good_dropped_by_current_paid_gate': len(
            dropped_preserved_due_current_paid_gate
        ),
    }

    stage_timings_seconds['persistence_preparation'] = round(
        time.monotonic() - persistence_started,
        3,
    )
    reporter.update(
        persistence_preparation_elapsed_seconds=stage_timings_seconds[
            'persistence_preparation'
        ],
        emit=True,
    )

    manifest = {
        'collector_version': 9,
        'source': 'Steam Store',
        'country_code': 'kz',
        'region': 'Kazakhstan',
        'source_scope_contract': core['PAID_DISCOVERY_POLICY'][
            'source_scope_contract'
        ],
        # Retained as a diagnostic union for older consumers. Production no
        # longer sends the combined category string to Steam.
        'search_category1': core['SEARCH_CATEGORY1'],
        'search_category_types': core['SEARCH_CATEGORY_TYPES'],
        'search_query_shape': 'explicit_partitions',
        'search_combined_category_query_used': False,
        'search_partitions': partition_stats,
        'search_specials_only': True,
        'search_hidef2p_paid_partitions': True,
        'search_maxprice_kzt': core['PAID_MAX_PRICE_KZT'],
        'paid_minimum_discount_percent': core['PAID_MIN_DISCOUNT_PERCENT'],
        'raw_source_top_n': None,
        'source_price_bound_validation': source_price_bound_validation,
        'free_or_giveaway_lane_separate': True,
        'paid_filters_apply_to_free_or_giveaway_lane': False,
        'started_at_utc': started.isoformat(),
        'updated_at_utc': finished.isoformat(),
        'page_size': core['PAGE_SIZE'],
        'partition_count': len(traversals),
        'steam_total_reported': reported_total,
        'source_rows_seen': rows_seen,
        'rows_seen': rows_seen,
        'parsed_rows': parsed_rows,
        'eligible_rows_before_partition_dedupe': eligible_rows_seen,
        'unique_items': len(items),
        'cross_partition_duplicate_identities': cross_partition_duplicates,
        'multi_partition_identity_count': multi_partition_identity_count,
        'duplicate_rows_seen': (
            sum(traversal['duplicate_rows'] for traversal in traversals)
            + cross_partition_duplicates
        ),
        'requests_made': source_requests,
        'source_validation_requests': source_price_bound_validation[
            'logical_requests'
        ],
        'production_collection_requests': collection_requests,
        'recovery_pass_used': False,
        'traversal_pass_count': len(traversals),
        'coverage_ratio': round(coverage, 6) if coverage is not None else None,
        'complete': source_coverage['source_complete'],
        'source_status': source_coverage['source_status'],
        'source_has_known_gaps': source_coverage['source_has_known_gaps'],
        'known_catalog_gap_count': source_coverage['known_gap_count'],
        'catalog_count_drift_informational': count_drift,
        'stage_timings_seconds': {
            **stage_timings_seconds,
            'partitions': {
                traversal['partition_id']: traversal['elapsed_seconds']
                for traversal in traversals
            },
        },
        'network_stats': review_network_stats,
        'filtering_funnel': filtering_funnel,
        'items_with_review_data': items_with_search_review_data,
        'review_coverage': round(search_review_coverage, 6),
        'items_with_search_review_data': items_with_search_review_data,
        'search_review_coverage': round(search_review_coverage, 6),
        'review_candidate_items': len(review_candidate_items),
        'review_candidate_appids': len(review_appids),
        'review_source_strategy': (
            'decisive_search_then_fresh_exact_cache_then_paced_storebrowse_'
            'then_serial_appreviews'
        ),
        'review_logical_components_required': review_logical_components_required,
        # Compatibility field now means AppReviews logical components actually
        # attempted, rather than counting circuit-skipped/non-AppReviews work.
        'review_api_requests': logical_review_requests,
        'review_appreviews_logical_components_attempted': (
            review_appreviews_logical_components_attempted
        ),
        'review_appreviews_physical_http_requests': review_network_stats.get(
            'review_http_requests', 0
        ),
        'review_appreviews_successful_components': review_network_stats.get(
            'review_successful_components', 0
        ),
        'review_appreviews_successful_appids': review_appreviews_successful_appids,
        'review_api_failed_requests': review_api_failed_requests,
        'review_appreviews_temporary_failures': review_network_stats.get(
            'review_temporary_failures', 0
        ),
        'review_appreviews_permanent_failures': review_network_stats.get(
            'review_permanent_failures', 0
        ),
        'review_appreviews_429_events': review_network_stats.get(
            'review_429_events', 0
        ),
        'review_appreviews_backoff_seconds': review_network_stats.get(
            'review_backoff_seconds', 0.0
        ),
        'review_rate_limit_circuit_open': core['review_rate_limit_event'].is_set(),
        'review_rate_limit_circuit_reason': (
            'consecutive_http_429'
            if core['review_rate_limit_event'].is_set()
            else None
        ),
        'review_rate_limit_circuit_threshold': core[
            'REVIEW_RATE_LIMIT_CIRCUIT_THRESHOLD'
        ],
        'review_circuit_skipped_components': review_network_stats.get(
            'review_circuit_skipped_components', 0
        ),
        'review_search_surface_reused_appids': review_search_surface_reused_appids,
        'review_exact_cache_reused_appids': review_exact_cache_reused_appids,
        'review_storebrowse_fallback_appids': review_storebrowse_fallback_appids,
        'review_storebrowse_fallback_requests': review_storebrowse_stats[
            'physical_http_requests'
        ],
        'review_storebrowse_successful_batches': review_storebrowse_stats[
            'successful_batches'
        ],
        'review_storebrowse_failed_batches': review_storebrowse_stats[
            'failed_batches'
        ],
        'review_storebrowse_retry_events': review_storebrowse_stats['retry_events'],
        'review_storebrowse_429_events': review_storebrowse_stats['http_429_events'],
        'review_storebrowse_backoff_seconds': round(
            review_storebrowse_stats['backoff_seconds'], 3
        ),
        'review_storebrowse_pacing_seconds': round(
            review_storebrowse_stats['pacing_seconds'], 3
        ),
        'review_storebrowse_fallback_policy': (
            'paced_batched_review_source_after_decisive_search_or_exact_cache; '
            'global_display_percent_is_half_point_conservative; '
            'russian_uses_language_specific_display_percent; '
            'failed_batches_preserve_prior_results_and_fall_through_to_appreviews'
        ),
        'review_candidate_items_resolved_without_appreviews': (
            review_candidate_items_resolved_without_appreviews
        ),
        'shortlist_items_without_appreviews': shortlist_items_without_appreviews,
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
        'last_known_good_dropped_by_current_paid_gate': (
            dropped_preserved_due_current_paid_gate
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding='utf-8',
    )

    index = {
        'version': 9,
        'format': 'tsv',
        'columns': columns,
        'country_code': 'kz',
        'source_scope_contract': core['PAID_DISCOVERY_POLICY'][
            'source_scope_contract'
        ],
        'search_query_shape': 'explicit_partitions',
        'source_partitions': [
            {
                'id': partition['id'],
                'category1': partition['category1'],
            }
            for partition in core['SEARCH_PARTITIONS']
        ],
        'source_price_bound_validated': source_price_bound_validation[
            'validated'
        ],
        'source_maxprice_kzt': core['PAID_MAX_PRICE_KZT'],
        'minimum_discount_percent': core['PAID_MIN_DISCOUNT_PERCENT'],
        'raw_source_top_n': None,
        'filtering_funnel': filtering_funnel,
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
    reporter.set_stage(
        'complete',
        paid_shortlist_items=len(selected),
        manifest_updated_at_utc=finished.isoformat(),
        persistence_elapsed_seconds=stage_timings_seconds[
            'persistence_preparation'
        ],
        total_elapsed_seconds=round(time.monotonic() - reporter.started_monotonic, 3),
    )
    reporter.stop()
    print(json.dumps(manifest, ensure_ascii=False, indent=2), flush=True)


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
