from __future__ import annotations

import json
import time
from collections import Counter
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

import steam_partial_publish_runner as runner


def query(core, *, category1, start=0, count=100, extra=None):
    params = core['search_params'](
        start,
        'Name_ASC',
        category1=category1,
        maxprice_kzt=core['PAID_MAX_PRICE_KZT'],
        hidef2p=True,
    )
    params['count'] = count
    if extra:
        params.update(extra)
    response = core['session'].get(core['URL'], params=params, timeout=40)
    result = {
        'status_code': response.status_code,
        'retry_after': response.headers.get('Retry-After'),
        'content_length': response.headers.get('Content-Length'),
    }
    response.raise_for_status()
    data = response.json()
    soup = core['BeautifulSoup'](data.get('results_html', ''), 'html.parser')
    rows = soup.select('a.search_result_row')
    metadata = []
    prefixes = Counter()
    url_types = Counter()
    keyword_counts = Counter()
    attr_counts = Counter()
    for row in rows:
        item = core['parse_row'](row)
        key = str(item.get('key') or '') if item else ''
        prefix = key.split('_', 1)[0] if '_' in key else 'other'
        prefixes[prefix] += 1
        path = urlparse((row.get('href') or '')).path
        path_type = next(
            (kind for kind in ('app', 'sub', 'bundle') if f'/{kind}/' in path),
            'other',
        )
        url_types[path_type] += 1
        title = item.get('title') if item else ''
        lower = str(title or '').casefold()
        for word in (
            'bundle', 'pack', 'collection', 'complete', 'edition',
            'soundtrack', 'demo', 'upgrade', 'dlc',
        ):
            if word in lower:
                keyword_counts[word] += 1
        for attr in (
            'data-ds-itemkey', 'data-ds-appid', 'data-ds-bundleid',
            'data-ds-packageid', 'data-ds-tagids',
        ):
            if row.get(attr):
                attr_counts[attr] += 1
        if len(metadata) < 15:
            metadata.append({
                'key': key,
                'appid': item.get('appid') if item else None,
                'title': title,
                'discount_percent': item.get('discount_percent') if item else None,
                'final_kzt': item.get('final_kzt') if item else None,
                'href': row.get('href'),
                'data_ds_appid': row.get('data-ds-appid'),
                'data_ds_bundleid': row.get('data-ds-bundleid'),
                'data_ds_packageid': row.get('data-ds-packageid'),
                'tag_ids': item.get('tag_ids') if item else None,
            })
    result.update({
        'category1': category1,
        'start': start,
        'requested_count': count,
        'total_count': core['to_int'](data.get('total_count')),
        'row_count': len(rows),
        'identity_prefix_counts': dict(prefixes),
        'url_type_counts': dict(url_types),
        'keyword_counts': dict(keyword_counts),
        'attribute_counts': dict(attr_counts),
        'sample': metadata,
    })
    return result


def search_page_type_controls(core):
    response = core['session'].get(
        'https://store.steampowered.com/search/',
        params={
            'specials': 1,
            'category1': '996',
            'cc': 'kz',
            'l': 'english',
            'maxprice': core['PAID_MAX_PRICE_KZT'],
            'hidef2p': 1,
        },
        timeout=40,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    controls = []
    for node in soup.select('input'):
        value = str(node.get('value') or '')
        name = str(node.get('name') or '')
        node_id = str(node.get('id') or '')
        if value in {'998', '994', '21', '10', '990', '989', '997', '993', '996'}:
            parent = node.parent
            controls.append({
                'name': name,
                'value': value,
                'id': node_id,
                'checked': node.has_attr('checked'),
                'parent_text': parent.get_text(' ', strip=True)[:180] if parent else '',
            })
    return controls


def pacing_sequence(core, *, delay_seconds, requests_count=35):
    session = requests.Session()
    session.headers.update(dict(core['session'].headers))
    session.cookies.update(core['session'].cookies.get_dict())
    statuses = Counter()
    retry_after_values = Counter()
    started = time.monotonic()
    first_429_request = None
    for index in range(requests_count):
        params = core['search_params'](
            index * 100,
            'Name_ASC',
            category1='996',
            maxprice_kzt=core['PAID_MAX_PRICE_KZT'],
            hidef2p=True,
        )
        params['count'] = 100
        response = session.get(core['URL'], params=params, timeout=40)
        statuses[str(response.status_code)] += 1
        if response.status_code == 429 and first_429_request is None:
            first_429_request = index + 1
        retry_after_values[str(response.headers.get('Retry-After'))] += 1
        if index + 1 < requests_count:
            time.sleep(delay_seconds)
    return {
        'delay_seconds': delay_seconds,
        'requests': requests_count,
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'statuses': dict(statuses),
        'retry_after_values': dict(retry_after_values),
        'first_429_request': first_429_request,
    }


def main():
    core = runner.load_core()
    evidence = {
        'type_controls': search_page_type_controls(core),
        'shapes': {},
    }
    for name, category1, start in (
        ('games_start0', '998', 0),
        ('dlc_start0', '21', 0),
        ('bundles_start0', '996', 0),
        ('bundles_start10000', '996', 10000),
        ('bundles_start50000', '996', 50000),
        ('bundles_start100000', '996', 100000),
        ('games_plus_bundles', '998,996', 0),
        ('supported_combined', '998,21,996', 0),
    ):
        evidence['shapes'][name] = query(
            core,
            category1=category1,
            start=start,
        )

    # Existing production logs already prove the 0.5s-like cadence repeatedly
    # reaches a 429 burst. This short control re-confirms response headers, then
    # a cooldown separates it from the conservative pacing trial.
    evidence['pacing_current'] = pacing_sequence(
        core,
        delay_seconds=0.5,
        requests_count=35,
    )
    time.sleep(65)
    evidence['pacing_conservative'] = pacing_sequence(
        core,
        delay_seconds=2.2,
        requests_count=35,
    )

    print(
        'STEAM_BUNDLE_RATE_LIMIT_BOUNDED_PROBE='
        + json.dumps(evidence, ensure_ascii=False, sort_keys=True),
        flush=True,
    )


if __name__ == '__main__':
    main()
