"""Targeted Steam KZ sale discovery inside the existing production collector.

No global DLC traversal. Parent eligibility must be established using the
ordinary paid + review suitability rules before relation lookups. The Steam
appdetails `dlc` membership is a verified relationship, never an inferred
matching title or an owned-library entitlement.
"""
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
import json
from threading import Condition, Lock
from time import monotonic, sleep

import requests

APPDETAILS_URL = 'https://store.steampowered.com/api/appdetails'
# Bounded parallelism instead of 6000+ all-catalogue DLC pages. The parent
# universe is the COMPLETE vetted base shortlist, never the visible top-100.
RELATION_WORKERS = 3
REQUEST_SPACING_SECONDS = 0.9
APPDETAILS_MAX_ATTEMPTS = 4  # 1 original request + up to 3 HTTP 429 retries
APPDETAILS_MAX_WAIT_SECONDS = 120.0  # cumulative own HTTP 429 cooldown, NOT rate-slot waiting
APPDETAILS_MAX_TOTAL_SECONDS = 900.0  # finite per-lookup wall-clock guard, including rate slots
APPDETAILS_WINDOW_SECONDS = 300.0
APPDETAILS_MAX_STARTS_PER_WINDOW = 180  # conservative process-local guard, not a Valve quota
APPDETAILS_MAX_RETRY_AFTER_SECONDS = 60.0
APPDETAILS_BACKOFF_SECONDS = (5.0, 15.0, 30.0)


class _SharedAppdetailsPacer:
    """FIFO, process-local gate for every physical KZ appdetails attempt.

    The 180/300s counter is shared by parent, child and 429 retry requests.
    Tickets prevent three worker threads from overtaking a waiting request;
    a condition parks followers without holding the lock or busy-spinning.
    """

    def __init__(self, spacing_seconds=REQUEST_SPACING_SECONDS,
                 window_seconds=APPDETAILS_WINDOW_SECONDS,
                 max_starts=APPDETAILS_MAX_STARTS_PER_WINDOW):
        if spacing_seconds < 0 or window_seconds <= 0 or max_starts < 1:
            raise ValueError('Invalid KZ appdetails physical-start pacing limits')
        self._condition = Condition(Lock())
        self._next_request = 0.0
        self._cooldown_until = 0.0
        self._spacing_seconds = spacing_seconds
        self._window_seconds = window_seconds
        self._max_starts = max_starts
        self._starts = deque()
        self._waiters = deque()

    def acquire(self, *, clock, sleeper, deadline):
        ticket = object()
        with self._condition:
            self._waiters.append(ticket)
        try:
            while True:
                with self._condition:
                    now = clock()
                    if now >= deadline:
                        raise RuntimeError('KZ appdetails rate slot wait budget exhausted')
                    if self._waiters[0] is not ticket:
                        # A follower cannot steal the head's slot. It parks
                        # until the head reserves or cancels, with no polling.
                        # The head always notifies; then recheck the deadline.
                        self._condition.wait()
                        continue
                    # Half-open rolling window (now - 300, now]. Expired starts
                    # are removed only under the same lock used for reservation.
                    while (self._starts and
                           now - self._starts[0] >= self._window_seconds):
                        self._starts.popleft()
                    window_wait = (
                        self._starts[0] + self._window_seconds - now
                        if len(self._starts) >= self._max_starts else 0.0
                    )
                    wait = max(0.0, self._next_request - now,
                               self._cooldown_until - now, window_wait)
                    if wait <= 0.0:
                        # Reserve a physical request start atomically. Callers
                        # make exactly one GET immediately after this gate.
                        self._starts.append(now)
                        self._next_request = now + self._spacing_seconds
                        self._waiters.popleft()
                        self._condition.notify_all()
                        return now
                    if wait > deadline - now:
                        raise RuntimeError('KZ appdetails rate slot wait budget exhausted')
                # Never hold the lock across a wait: a 429 may extend cooldown
                # and every wake-up must recheck the rolling window.
                sleeper(wait)
        finally:
            # Timeouts/exceptions cannot strand a ticket or starve a follower.
            with self._condition:
                if ticket in self._waiters:
                    self._waiters.remove(ticket)
                    self._condition.notify_all()

    def throttle(self, seconds, *, clock):
        with self._condition:
            self._cooldown_until = max(self._cooldown_until, clock() + seconds)
            self._condition.notify_all()


_appdetails_pacer = _SharedAppdetailsPacer()


class _AppdetailsDiagnostics:
    """Safe per-request Storefront telemetry; never controls request behavior."""

    def __init__(self):
        self._lock = Lock()
        self.reset()

    def reset(self):
        with self._lock:
            self._stage = 'unassigned'
            self._starts = deque()
            self._first_start = None
            self._request_total = 0
            self._statuses = {}
            self._first_429_seen = False

    def set_stage(self, stage):
        with self._lock:
            self._stage = stage

    def started(self, now):
        with self._lock:
            if self._first_start is None:
                self._first_start = now
            # Count physical starts in the process-local rolling 300s window.
            # This does not claim a corresponding Valve or per-IP rate bucket.
            while self._starts and now - self._starts[0] >= 300:
                self._starts.popleft()
            self._starts.append(now)
            self._request_total += 1
            return {
                'stage': self._stage,
                'request_index': self._request_total,
                'rolling_300s_request_starts': len(self._starts),
                'seconds_since_first_start': round(now - self._first_start, 3),
            }

    def completed(self, record, *, appid, attempt, status, elapsed,
                  retry_after_present=False, retry_after_seconds=None,
                  cooldown_seconds=None, transport_error=None):
        with self._lock:
            key = str(status)
            self._statuses[key] = self._statuses.get(key, 0) + 1
            first_429 = status == 429 and not self._first_429_seen
            if first_429:
                self._first_429_seen = True
        # Only fixed numeric facts and allowlisted class names; no URLs, raw
        # headers, request credentials, cookies or exception messages.
        payload = {
            'event': 'request',
            **record,
            'appid': appid,
            'attempt': attempt,
            'status': status,
            'duration_ms': round(max(0.0, elapsed) * 1000, 1),
            'first_429': first_429,
            'retry_after_present': bool(retry_after_present),
            'retry_after_seconds': retry_after_seconds,
            'applied_cooldown_seconds': cooldown_seconds,
        }
        if transport_error is not None:
            payload['transport_error_class'] = transport_error
        print('[steam-appdetails-diagnostic]',
              json.dumps(payload, sort_keys=True), flush=True)

    def snapshot(self):
        with self._lock:
            return {
                'request_starts': self._request_total,
                'response_status_counts': dict(self._statuses),
                'first_429_seen': self._first_429_seen,
            }


_appdetails_diagnostics = _AppdetailsDiagnostics()


def _utc_now():
    return datetime.now(timezone.utc)


def _retry_after_seconds(response, *, wall_clock):
    """Accept only valid delta-seconds or HTTP dates; bound untrusted values."""
    raw = (getattr(response, 'headers', None) or {}).get('Retry-After')
    if not isinstance(raw, str):
        return None
    raw = raw.strip()
    try:
        if raw.isascii() and raw.isdecimal():
            seconds = float(int(raw))
        else:
            when = parsedate_to_datetime(raw)
            if when.tzinfo is None:
                return None
            seconds = (when - wall_clock()).total_seconds()
    except (OverflowError, TypeError, ValueError, IndexError):
        return None
    if seconds <= 0:
        return None
    return min(seconds, APPDETAILS_MAX_RETRY_AFTER_SECONDS)


def get_appdetails(appid, *, getter=requests.get, pacer=None,
                   clock=monotonic, sleeper=sleep, wall_clock=_utc_now,
                   diagnostics=None):
    """Exact KZ appdetails; a shared rolling start cap covers every attempt.

    The 120s HTTP 429 retry-cooldown budget is separate from planned
    window-slot waiting. A finite 900s lookup guard and the 60-minute
    GitHub job timeout remain in force; all failures remain fail-closed.
    """
    appid = _canonical_appid(appid, 'KZ appdetails request')
    pacer = pacer if pacer is not None else _appdetails_pacer
    diagnostics = (diagnostics if diagnostics is not None
                   else _appdetails_diagnostics)
    deadline = clock() + APPDETAILS_MAX_TOTAL_SECONDS
    own_429_wait_seconds = 0.0
    for attempt in range(APPDETAILS_MAX_ATTEMPTS):
        reserved_start = pacer.acquire(
            clock=clock, sleeper=sleeper, deadline=deadline
        )
        started_at = clock()
        record = diagnostics.started(reserved_start)
        try:
            response = getter(
                APPDETAILS_URL,
                params={'appids': appid, 'cc': 'kz', 'l': 'english'},
                headers={'User-Agent': 'steam-kz-deals/1.0',
                         'Accept': 'application/json'},
                timeout=25,
            )
        except requests.RequestException as exc:
            diagnostics.completed(
                record, appid=appid, attempt=attempt + 1,
                status='transport_error', elapsed=clock() - started_at,
                transport_error=type(exc).__name__,
            )
            raise
        status = getattr(response, 'status_code', None)
        if status == 429:
            retry_after_present = (
                (getattr(response, 'headers', None) or {}).get('Retry-After')
                is not None
            )
            if attempt + 1 == APPDETAILS_MAX_ATTEMPTS:
                diagnostics.completed(
                    record, appid=appid, attempt=attempt + 1, status=status,
                    elapsed=clock() - started_at,
                    retry_after_present=retry_after_present,
                )
                response.raise_for_status()
                raise RuntimeError(f'KZ appdetails HTTP 429 exhausted for App_{appid}')
            seconds = _retry_after_seconds(response, wall_clock=wall_clock)
            from_header = seconds is not None
            if seconds is None:
                seconds = APPDETAILS_BACKOFF_SECONDS[attempt]
            if own_429_wait_seconds + seconds > APPDETAILS_MAX_WAIT_SECONDS:
                diagnostics.completed(
                    record, appid=appid, attempt=attempt + 1, status=status,
                    elapsed=clock() - started_at,
                    retry_after_present=retry_after_present,
                    retry_after_seconds=seconds if from_header else None,
                )
                raise RuntimeError('KZ appdetails retry wait budget exhausted')
            own_429_wait_seconds += seconds
            diagnostics.completed(
                record, appid=appid, attempt=attempt + 1, status=status,
                elapsed=clock() - started_at,
                retry_after_present=retry_after_present,
                retry_after_seconds=seconds if from_header else None,
                cooldown_seconds=seconds,
            )
            pacer.throttle(seconds, clock=clock)
            continue
        diagnostics.completed(
            record, appid=appid, attempt=attempt + 1, status=status,
            elapsed=clock() - started_at,
        )
        # 5xx, connection failures and bad identity remain fail-closed.
        response.raise_for_status()
        body = response.json()
        entry = body.get(appid) if isinstance(body, dict) else None
        if not isinstance(entry, dict) or entry.get('success') is not True:
            raise RuntimeError(f'KZ appdetails missing identity {appid}')
        data = entry.get('data')
        if not isinstance(data, dict):
            raise RuntimeError(f'KZ appdetails missing metadata {appid}')
        _check_fetched_identity(data, appid, f'KZ appdetails App_{appid}')
        return data
    raise RuntimeError(f'KZ appdetails HTTP 429 exhausted for App_{appid}')


def suitable_base_ids(items, failed_keys, core, today):
    """Normal existing quality eligibility, not weak search-review guessing."""
    admitted = []
    for item in items:
        if item['key'] in failed_keys or not str(item.get('key','')).startswith('App_'):
            continue
        if core['paid_source_rejection_reason'](item):
            continue
        reasons, tags = core['broad_reasons'](item, today)
        if not reasons:
            continue
        candidate = dict(item, broad_reasons=reasons, fit_tags=tags)
        refined, _ = core['refined_reasons'](candidate)
        if refined:
            admitted.append(str(item['appid']))
    return sorted(set(admitted), key=lambda value: int(value))


def _canonical_appid(value, context):
    """Only positive canonical decimal AppIDs; reject bools and lossy coercion."""
    if type(value) is int and value > 0:
        return str(value)
    if (type(value) is str and value.isascii() and value.isdecimal()
            and value[0] != '0'):
        return value
    raise RuntimeError(f'{context} has invalid AppID identity')


def _check_fetched_identity(data, appid, context):
    if not isinstance(data, dict):
        raise RuntimeError(f'{context} missing appdetails metadata')
    if ('steam_appid' in data and
            _canonical_appid(data['steam_appid'], context) != appid):
        raise RuntimeError(f'{context} contradicts requested AppID {appid}')


def discover_dlc_for_bases(base_appids, core, *, fetch=get_appdetails,
                           reporter=None):
    """Fail closed for missing/invalid parents; dedupe exact valid DLC membership."""
    bases = sorted({_canonical_appid(x, 'targeted DLC parent')
                    for x in base_appids}, key=int)
    relations = {}
    _appdetails_diagnostics.reset()
    _appdetails_diagnostics.set_stage('parent_relations')
    with ThreadPoolExecutor(max_workers=RELATION_WORKERS) as pool:
        futures = {pool.submit(fetch, base): base for base in bases}
        for future in as_completed(futures):
            base = futures[future]
            data = future.result()
            _check_fetched_identity(data, base, f'DLC parent App_{base}')
            if data.get('type') != 'game':
                raise RuntimeError(f'DLC parent {base} did not resolve to a base game')
            # Missing 'dlc' means no known relations; an explicitly malformed
            # relation is not equivalent to an empty verified membership.
            raw = data.get('dlc', [])
            if not isinstance(raw, list):
                raise RuntimeError(f'DLC relationship invalid for App_{base}')
            # Steam's parent list is set membership, not a cardinality proof.
            # Repeated *valid* IDs are safe; any malformed identity still fails
            # the entire parent instead of silently dropping a relationship.
            ids = sorted({_canonical_appid(value, f'DLC relationship App_{base}')
                          for value in raw}, key=int)
            relations[base] = ids
    candidates = {}
    reverse = {}
    for base in sorted(relations, key=int):
        for appid in relations[base]:
            reverse.setdefault(appid, set()).add(base)
    _appdetails_diagnostics.set_stage('dlc_price')
    for appid in sorted(reverse, key=int):
        data = fetch(appid)
        _check_fetched_identity(data, appid, f'DLC App_{appid}')
        if data.get('type') != 'dlc':
            # Some pages list soundtrack/apps, not genuine DLC.
            continue
        # Integrity precedes any price-based skip: a corrupt relationship is
        # never silently converted into an ordinary unsold DLC.
        fullgame = data.get('fullgame')
        if fullgame is not None and not isinstance(fullgame, dict):
            raise RuntimeError(f'DLC App_{appid} has invalid fullgame relationship')
        if fullgame is not None and 'appid' in fullgame:
            parent = _canonical_appid(fullgame['appid'], f'DLC App_{appid} fullgame')
            if parent not in reverse[appid]:
                raise RuntimeError(f'DLC App_{appid} contradicts verified parent relation')
        # An absent/null/empty object has no verified paid KZ offer. Do not
        # mistake it for a foreign currency, or emit a made-up zero-price card.
        if 'price_overview' not in data or data['price_overview'] is None:
            continue
        price = data['price_overview']
        if type(price) is not dict:
            raise RuntimeError(f'DLC App_{appid} has malformed price_overview')
        if not price:
            continue
        # A nonempty object is price evidence, including partial/foreign
        # markers: it must never take the no-price skip path.
        if price.get('currency') != 'KZT':
            raise RuntimeError(f'DLC App_{appid} has non-KZT price')
        final = price.get('final')
        percent = price.get('discount_percent')
        if type(final) is not int or type(percent) is not int:
            raise RuntimeError(f'DLC App_{appid} has incomplete KZT price')
        if not (0 < final <= int(core['PAID_MAX_PRICE_KZT'] * 100)
                and percent >= core['PAID_MIN_DISCOUNT_PERCENT']):
            continue
        item = {
            'key': f'App_{appid}', 'appid': appid,
            'title': data.get('name') or f'DLC {appid}',
            'discount_percent': percent, 'final_minor': final,
            'final_kzt': final / 100.0,
            'global_review_positive': None, 'global_review_count': 0,
            'russian_review_positive': None, 'russian_review_count': 0,
            'search_review_positive': None, 'search_review_count': None,
            'tag_ids': [], 'release_date': '',
            'url': f'https://store.steampowered.com/app/{appid}/',
            'verified_base_appids': sorted(reverse[appid], key=int),
            'targeted_dlc_relation': True,
        }
        if core['paid_source_rejection_reason'](item):
            continue
        candidates[item['key']] = item
    stats = {
        'admitted_base_count': len(bases),
        'parent_relation_lookups': len(relations),
        'related_dlc_unique_ids': len(reverse),
        'dlc_price_lookups': len(reverse),
        'dlc_accepted_after_paid_gate': len(candidates),
        'dlc_rejected_after_paid_gate': len(reverse) - len(candidates),
        'relation_lookup_mode': 'verified_base_appdetails_kz_no_global_dlc_search',
        'relation_complete': len(relations) == len(bases),
    }
    if reporter:
        reporter.update(**stats, appdetails_diagnostics=_appdetails_diagnostics.snapshot(),
                        emit=True)
    return candidates, stats


def classify_discounted_package_rows(rows, core):
    """Sub identities are first-class discounted purchases from game search."""
    accepted = {}
    rejected = 0
    seen = 0
    for item in rows:
        if not str(item.get('key') or '').startswith('Sub_'):
            continue
        seen += 1
        if core['paid_source_rejection_reason'](item):
            rejected += 1
            continue
        accepted[item['key']] = item
    return accepted, {
        'bundle_offers_seen': seen,
        'bundle_offers_survived_cheap_gate': len(accepted),
        'bundle_offers_rejected_cheap_gate': rejected,
        'bundle_source': 'verified_kz_category1_998_sub_identifiers',
    }


def candidate_needs_obscure_gate(item, *, minimum_count=50):
    """Only decisive positive low-signal evidence can trigger early rejection.

    Unknown review coverage is not low quality. Exceptional review quality and
    extreme commercial value each independently rescue a tiny sample.
    """
    count = item.get('search_review_count')
    positive = item.get('search_review_positive')
    if type(count) is not int or type(positive) is not int:
        return False
    if count >= minimum_count:
        return False
    exceptional = (
        (count >= 10 and positive >= 95)
        or (item.get('discount_percent') or 0) >= 90
        and 0 < (item.get('final_kzt') or 0) <= 1000
    )
    return not exceptional
