"""Targeted Steam KZ sale discovery inside the existing production collector.

No global DLC traversal. Parent eligibility must be established using the
ordinary paid + review suitability rules before relation lookups. The Steam
appdetails `dlc` membership is a verified relationship, never an inferred
matching title or an owned-library entitlement.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from threading import Lock
from time import monotonic, sleep

import requests

APPDETAILS_URL = 'https://store.steampowered.com/api/appdetails'
# Bounded parallelism instead of 6000+ all-catalogue DLC pages. The parent
# universe is the COMPLETE vetted base shortlist, never the visible top-100.
RELATION_WORKERS = 3
REQUEST_SPACING_SECONDS = 0.9
_lock = Lock()
_next_request = 0.0


def get_appdetails(appid, *, getter=requests.get):
    """One narrowly selected KZ API request; caller handles fail-closed errors."""
    global _next_request
    with _lock:
        wait = max(0.0, _next_request - monotonic())
        if wait:
            sleep(wait)
        _next_request = monotonic() + REQUEST_SPACING_SECONDS
    response = getter(
        APPDETAILS_URL,
        params={'appids': str(appid), 'cc': 'kz', 'l': 'english'},
        headers={'User-Agent': 'steam-kz-deals/1.0', 'Accept': 'application/json'},
        timeout=25,
    )
    response.raise_for_status()
    body = response.json()
    entry = body.get(str(appid))
    if not isinstance(entry, dict) or entry.get('success') is not True:
        raise RuntimeError(f'KZ appdetails missing identity {appid}')
    data = entry.get('data')
    if not isinstance(data, dict):
        raise RuntimeError(f'KZ appdetails missing metadata {appid}')
    return data


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


def discover_dlc_for_bases(base_appids, core, *, fetch=get_appdetails,
                           reporter=None):
    """Fail closed for any missing parent. Return only verified discounted DLC."""
    bases = sorted({str(x) for x in base_appids}, key=int)
    relations = {}
    with ThreadPoolExecutor(max_workers=RELATION_WORKERS) as pool:
        futures = {pool.submit(fetch, base): base for base in bases}
        for future in as_completed(futures):
            base = futures[future]
            data = future.result()
            if data.get('type') != 'game':
                raise RuntimeError(f'DLC parent {base} did not resolve to a base game')
            raw = data.get('dlc') or []
            if not isinstance(raw, list):
                raise RuntimeError(f'DLC relationship invalid for App_{base}')
            ids = sorted({str(value) for value in raw if str(value).isdigit()}, key=int)
            if len(ids) != len(raw):
                raise RuntimeError(f'DLC relationship contains duplicates/invalid identities: {base}')
            relations[base] = ids
    candidates = {}
    reverse = {}
    for base in sorted(relations, key=int):
        for appid in relations[base]:
            reverse.setdefault(appid, set()).add(base)
    for appid in sorted(reverse, key=int):
        data = fetch(appid)
        if data.get('type') != 'dlc':
            # Some pages list soundtrack/apps, not genuine DLC.
            continue
        price = data.get('price_overview') or {}
        if price.get('currency') != 'KZT':
            raise RuntimeError(f'DLC App_{appid} has non-KZT price')
        final = price.get('final')
        percent = price.get('discount_percent')
        if type(final) is not int or type(percent) is not int:
            continue
        if not (0 < final <= int(core['PAID_MAX_PRICE_KZT'] * 100)
                and percent >= core['PAID_MIN_DISCOUNT_PERCENT']):
            continue
        parent = (data.get('fullgame') or {}).get('appid')
        if parent is not None and str(parent) not in reverse[appid]:
            raise RuntimeError(f'DLC App_{appid} contradicts verified parent relation')
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
        reporter.update(**stats, emit=True)
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
