import json
import re
import runpy
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import requests


SOURCE = Path("scripts/steam_production.py")
CACHE_PATH = Path("data/cache/steam_review_http_cache.json")
MANIFEST_PATH = Path("data/production/manifest.json")
CACHE_SCHEMA_VERSION = 1

# Steam Search is still fetched live on every run. We only shorten the
# collector's fixed inter-page courtesy delay; 429/retry backoffs are left
# untouched.
ORIGINAL_SEARCH_DELAY_SECONDS = 0.9
SEARCH_DELAY_SECONDS = 0.5

# Review summaries are coarse quality/recall guards, not deal data. Refresh
# volatile low-count games daily, medium-count games every 3 days and mature
# high-count games weekly. Prices, discounts and the sale catalog are NEVER
# served from this cache.
LOW_REVIEW_COUNT = 1_000
HIGH_REVIEW_COUNT = 10_000
LOW_COUNT_TTL_HOURS = 20
MEDIUM_COUNT_TTL_HOURS = 72
HIGH_COUNT_TTL_HOURS = 168
CACHE_RETENTION_DAYS = 90

REVIEW_URL_RE = re.compile(r"/appreviews/(\d+)")

_real_session_get = requests.Session.get
_real_sleep = time.sleep
_cache_lock = threading.Lock()
_stats_lock = threading.Lock()
_stats = {
    "review_cache_hits": 0,
    "review_network_requests": 0,
    "review_cache_writes": 0,
}


def utc_now():
    return datetime.now(timezone.utc)


def parse_utc(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def load_cache():
    try:
        payload = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        if payload.get("schema_version") != CACHE_SCHEMA_VERSION:
            return {}
        entries = payload.get("entries")
        return entries if isinstance(entries, dict) else {}
    except FileNotFoundError:
        return {}
    except Exception as exc:
        print("Review cache ignored:", exc)
        return {}


cache_entries = load_cache()


def total_reviews_from_entry(entry):
    try:
        return int(entry.get("total_reviews") or 0)
    except (TypeError, ValueError):
        return 0


def global_review_count(appid, language_entry=None):
    app_entry = cache_entries.get(str(appid)) or {}
    global_entry = app_entry.get("all") or {}
    count = total_reviews_from_entry(global_entry)
    if count > 0:
        return count
    return total_reviews_from_entry(language_entry or {})


def ttl_hours(appid, language_entry):
    count = global_review_count(appid, language_entry)
    if count < LOW_REVIEW_COUNT:
        return LOW_COUNT_TTL_HOURS
    if count < HIGH_REVIEW_COUNT:
        return MEDIUM_COUNT_TTL_HOURS
    return HIGH_COUNT_TTL_HOURS


def valid_cached_entry(appid, language):
    with _cache_lock:
        app_entry = cache_entries.get(str(appid)) or {}
        entry = app_entry.get(str(language))
        if not isinstance(entry, dict):
            return None
        fetched_at = parse_utc(entry.get("fetched_at_utc"))
        if fetched_at is None:
            return None
        age_hours = (utc_now() - fetched_at).total_seconds() / 3600.0
        if age_hours < 0 or age_hours > ttl_hours(appid, entry):
            return None
        return dict(entry)


def compact_summary(payload):
    if not isinstance(payload, dict) or payload.get("success") != 1:
        return None
    summary = payload.get("query_summary") or {}
    try:
        total_reviews = int(summary.get("total_reviews") or 0)
        total_positive = int(summary.get("total_positive") or 0)
    except (TypeError, ValueError):
        return None
    return {
        "fetched_at_utc": utc_now().isoformat(),
        "total_reviews": total_reviews,
        "total_positive": total_positive,
    }


def payload_from_entry(entry):
    return {
        "success": 1,
        "query_summary": {
            "total_reviews": int(entry.get("total_reviews") or 0),
            "total_positive": int(entry.get("total_positive") or 0),
        },
    }


class CachedResponse:
    status_code = 200
    headers = {}

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload

    def raise_for_status(self):
        return None


def cached_session_get(session, url, *args, **kwargs):
    match = REVIEW_URL_RE.search(str(url))
    params = kwargs.get("params") or {}
    language = params.get("language")

    if match and language in {"all", "russian"}:
        appid = match.group(1)
        entry = valid_cached_entry(appid, language)
        if entry is not None:
            with _stats_lock:
                _stats["review_cache_hits"] += 1
            return CachedResponse(payload_from_entry(entry))

        with _stats_lock:
            _stats["review_network_requests"] += 1

        response = _real_session_get(session, url, *args, **kwargs)
        if response.status_code == 200:
            try:
                compact = compact_summary(response.json())
            except Exception:
                compact = None
            if compact is not None:
                with _cache_lock:
                    app_entry = cache_entries.setdefault(str(appid), {})
                    app_entry[str(language)] = compact
                with _stats_lock:
                    _stats["review_cache_writes"] += 1
        return response

    return _real_session_get(session, url, *args, **kwargs)


def optimized_sleep(seconds):
    try:
        value = float(seconds)
    except (TypeError, ValueError):
        return _real_sleep(seconds)

    if abs(value - ORIGINAL_SEARCH_DELAY_SECONDS) < 1e-9:
        return _real_sleep(SEARCH_DELAY_SECONDS)
    return _real_sleep(seconds)


def prune_cache():
    cutoff = utc_now().timestamp() - CACHE_RETENTION_DAYS * 86400
    pruned = {}
    for appid, app_entry in cache_entries.items():
        if not isinstance(app_entry, dict):
            continue
        kept = {}
        for language, entry in app_entry.items():
            if not isinstance(entry, dict):
                continue
            fetched = parse_utc(entry.get("fetched_at_utc"))
            if fetched is not None and fetched.timestamp() >= cutoff:
                kept[language] = entry
        if kept:
            pruned[appid] = kept
    return pruned


def write_cache():
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "updated_at_utc": utc_now().isoformat(),
        "entries": prune_cache(),
    }
    temporary = CACHE_PATH.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    temporary.replace(CACHE_PATH)


def annotate_manifest():
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        print("Could not annotate manifest with accelerator stats:", exc)
        return

    logical_review_requests = int(manifest.get("review_api_requests") or 0)
    cache_hits = int(_stats["review_cache_hits"])
    network_requests = int(_stats["review_network_requests"])
    manifest.update({
        "collector_acceleration": "review-cache-v1",
        "review_cache_schema_version": CACHE_SCHEMA_VERSION,
        "review_cache_hits": cache_hits,
        "review_network_requests": network_requests,
        "review_network_avoidance_ratio": (
            round(cache_hits / logical_review_requests, 6)
            if logical_review_requests
            else 0.0
        ),
        "review_cache_appids": len(prune_cache()),
        "review_cache_policy": {
            "under_1000_reviews_hours": LOW_COUNT_TTL_HOURS,
            "1000_to_9999_reviews_hours": MEDIUM_COUNT_TTL_HOURS,
            "10000_plus_reviews_hours": HIGH_COUNT_TTL_HOURS,
        },
        "steam_search_inter_page_delay_seconds": SEARCH_DELAY_SECONDS,
    })
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    if not SOURCE.exists():
        raise SystemExit(f"Missing source collector: {SOURCE}")

    requests.Session.get = cached_session_get
    time.sleep = optimized_sleep
    succeeded = False
    try:
        runpy.run_path(str(SOURCE), run_name="__main__")
        succeeded = True
    finally:
        requests.Session.get = _real_session_get
        time.sleep = _real_sleep
        write_cache()

    if succeeded:
        annotate_manifest()

    print(
        "Steam collector accelerator:",
        json.dumps(_stats, ensure_ascii=False, sort_keys=True),
    )


if __name__ == "__main__":
    main()
