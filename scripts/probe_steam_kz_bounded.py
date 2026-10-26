"""Bounded, read-only Steam KZ source shape probe for STEAM-DISC-001.

Run explicitly for acceptance recon, never in the recurring production collector.
No API keys, no writes and no retries: 4 requests maximum.
"""
import json
import requests

QUERIES = [
    (
        'game_dlc_relation',
        'https://store.steampowered.com/api/appdetails',
        {'appids': '1091500', 'cc': 'kz', 'l': 'english'},
    ),
    (
        'related_dlc_kz_price',
        'https://store.steampowered.com/api/appdetails',
        {'appids': '2138330', 'cc': 'kz', 'l': 'english'},
    ),
    (
        'known_sub_package',
        'https://store.steampowered.com/api/packagedetails',
        {'packageids': '76471', 'cc': 'kz', 'l': 'english'},
    ),
    (
        'discounted_games_partition',
        'https://store.steampowered.com/search/results/',
        {
            'cc': 'kz', 'l': 'english', 'infinite': 1, 'ignore_preferences': 1,
            'specials': 1, 'hidef2p': 1, 'category1': '998',
            'maxprice': 4500, 'sort_by': 'Price_DESC', 'start': 0, 'count': 10,
        },
    ),
]


def main():
    results = []
    for name, url, params in QUERIES:
        try:
            response = requests.get(
                url, params=params, timeout=12,
                headers={'User-Agent': 'SteamKZDeals/1.0 bounded-acceptance-recon'}
            )
            record = {'probe_id': name, 'http_status': response.status_code}
            if response.status_code == 200:
                doc = response.json()
                if name == 'discounted_games_partition':
                    record.update({
                        'reported_total': doc.get('total_count'),
                        'first_row_keys': __import__('re').findall(
                            r'data-ds-itemkey="([^"]+)"',
                            doc.get('results_html') or '',
                        )[:10],
                    })
                else:
                    key = params.get('appids') or params.get('packageids')
                    data = (doc.get(key) or {}).get('data') or {}
                    record.update({
                        'success': (doc.get(key) or {}).get('success'),
                        'type': data.get('type'),
                        'name': data.get('name'),
                        'dlc_appids': (data.get('dlc') or [])[:12],
                        'dlc_total': len(data.get('dlc') or []),
                        'price_overview': data.get('price_overview'),
                        'price': data.get('price'),
                        'included_apps_count': len(data.get('apps') or []),
                        'included_apps_sample': [
                            row.get('id') for row in (data.get('apps') or [])[:10]
                        ],
                    })
            results.append(record)
        except Exception as exc:
            results.append({'probe_id': name, 'error': str(exc)[:200]})
    print('BOUNDED_STEAM_KZ_SOURCE_PROBE=' +
          json.dumps(results, ensure_ascii=False, separators=(',', ':')))
    # Recon is diagnostic only: inconclusive live responses must not fail
    # unrelated deterministic validation or be treated as source proof.


if __name__ == '__main__':
    main()
