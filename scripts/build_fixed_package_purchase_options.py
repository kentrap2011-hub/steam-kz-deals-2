import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MAILING_INDEX = Path('data/production/mailing/index.json')
OUT = Path('data/production/pre_ai/fixed_package_options.json')
BATCH_SIZE = 100

APP_TYPE = {
    0: 'game',
    1: 'demo',
    2: 'mod',
    3: 'movie',
    4: 'dlc',
    5: 'guide',
    6: 'software',
    7: 'video',
    8: 'series',
    9: 'episode',
    10: 'hardware',
    11: 'music',
    12: 'beta',
    13: 'tool',
    14: 'advertising',
}


def final_kzt(option):
    value = option.get('final_price_in_cents')
    return None if value is None else float(value) / 100.0


def original_kzt(option):
    value = option.get('original_price_in_cents')
    return None if value is None else float(value) / 100.0


def load_current_appids():
    index = json.loads(MAILING_INDEX.read_text(encoding='utf-8'))
    columns = index['columns']
    ci = {name: i for i, name in enumerate(columns)}
    if not {'key', 'appid'} <= set(columns):
        raise SystemExit('Mailing feed lacks key/appid columns')

    appids = set()
    for number in range(1, int(index['chunk_count']) + 1):
        path = Path(index['chunk_pattern'].replace('NNN', f'{number:03d}'))
        for line in path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            cells = line.split('\t')
            if len(cells) != len(columns):
                raise SystemExit(f'Column mismatch in {path}')
            key = cells[ci['key']]
            appid = cells[ci['appid']]
            if key.startswith('App_') and appid and appid.isdigit():
                appids.add(int(appid))
    return index, sorted(appids)


def fetch_raw_batch(batch):
    payload = {
        'ids': batch,
        'context': {
            'language': 'english',
            'country_code': 'KZ',
            'steam_realm': 1,
        },
        'data_request': {
            'include_all_purchase_options': True,
            'include_basic_info': True,
            'include_included_items': True,
        },
    }
    url = (
        'https://api.steampowered.com/IStoreBrowseService/GetItems/v1/?input_json='
        + urllib.parse.quote(json.dumps(payload, separators=(',', ':')))
    )
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'steam-kz-deals/1.0', 'Accept': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        data = json.loads(response.read().decode('utf-8'))
    return (data.get('response') or {}).get('store_items') or []


def fetch_app_items(appids):
    items = []
    request_count = 0
    for start in range(0, len(appids), BATCH_SIZE):
        batch_appids = appids[start:start + BATCH_SIZE]
        batch = [{'appid': appid} for appid in batch_appids]
        returned = fetch_raw_batch(batch)
        request_count += 1
        if len(returned) != len(batch):
            raise SystemExit(
                f'StoreBrowse app batch cardinality mismatch: requested={len(batch)} returned={len(returned)}'
            )
        items.extend(returned)
    return items, request_count


def packageid_for_returned_item(store_item, requested_ids):
    direct = int(store_item.get('id') or store_item.get('packageid') or 0)
    if direct in requested_ids:
        return direct
    option_ids = {
        int(option.get('packageid') or 0)
        for option in (store_item.get('purchase_options') or [])
        if int(option.get('packageid') or 0) in requested_ids
    }
    if len(option_ids) == 1:
        return next(iter(option_ids))
    return None


def fetch_package_items(package_ids):
    by_id = {}
    request_count = 0
    for start in range(0, len(package_ids), BATCH_SIZE):
        batch_ids = package_ids[start:start + BATCH_SIZE]
        requested = set(batch_ids)
        returned = fetch_raw_batch([{'packageid': pid} for pid in batch_ids])
        request_count += 1
        for store_item in returned:
            pid = packageid_for_returned_item(store_item, requested)
            if pid is not None and pid not in by_id:
                by_id[pid] = store_item
    return by_id, request_count


def package_ids_from_app_items(appids, items):
    if len(appids) != len(items):
        raise SystemExit('App StoreBrowse cardinality mismatch')
    sources = {}
    for appid, item in zip(appids, items):
        if int(item.get('item_type') or 0) != 0 or int(item.get('id') or 0) != appid:
            raise SystemExit(f'StoreBrowse app identity mismatch for App_{appid}')
        for option in item.get('purchase_options') or []:
            pid = int(option.get('packageid') or 0)
            if pid > 0:
                sources.setdefault(pid, set()).add(appid)
    return sources


def nested_included_appids(store_item):
    values = []
    included = store_item.get('included_items') or {}
    for app in included.get('included_apps') or []:
        if not isinstance(app, dict):
            continue
        value = app.get('appid') if app.get('appid') is not None else app.get('id')
        if value is not None and str(value).isdigit():
            values.append(int(value))
    return sorted(set(values))


def included_appids(store_item):
    """Legacy coverage membership used for package candidate discovery.

    StoreBrowse's top-level included_appids has historically represented the base-game
    coverage needed by this producer. Keep that behavior stable for package discovery;
    full verified package contents are collected separately by all_included_appids().
    """
    values = [int(x) for x in (store_item.get('included_appids') or []) if str(x).isdigit()]
    if not values:
        values = nested_included_appids(store_item)
    return sorted(set(values))


def all_included_appids(store_item):
    """Union every verified top-level included app exposed by StoreBrowse.

    This deliberately differs from included_appids(): a non-empty top-level base-app list
    must not suppress DLC/content present in included_items.included_apps.
    """
    values = {
        int(x)
        for x in (store_item.get('included_appids') or [])
        if str(x).isdigit()
    }
    values.update(nested_included_appids(store_item))
    return sorted(values)


def exact_package_option(pid, store_item):
    exact = [
        option for option in (store_item.get('purchase_options') or [])
        if int(option.get('packageid') or 0) == pid and final_kzt(option) is not None
    ]
    if not exact:
        return None
    exact.sort(key=lambda option: (
        final_kzt(option),
        -int(option.get('discount_pct') or 0),
        str(option.get('purchase_option_name') or ''),
    ))
    return exact[0]


def classify_package(pid, store_item, source_appids, current_appids, observed_epoch):
    identity_ok = (
        int(store_item.get('id') or store_item.get('packageid') or 0) == pid
        or any(
            int(option.get('packageid') or 0) == pid
            for option in (store_item.get('purchase_options') or [])
        )
    )
    if not identity_ok:
        return None, 'package_identity_mismatch'

    option = exact_package_option(pid, store_item)
    if option is None:
        return None, 'no_exact_package_purchase_option'

    current = final_kzt(option)
    if current is None or current <= 0:
        return None, 'package_not_current_paid_offer'

    discount = int(option.get('discount_pct') or 0)
    end_values = sorted({
        int(row.get('discount_end_date') or 0)
        for row in (option.get('active_discounts') or [])
        if int(row.get('discount_end_date') or 0) > 0
    })
    if discount > 0 and end_values and min(end_values) <= observed_epoch:
        return None, 'package_discount_end_not_after_observation'

    apps = included_appids(store_item)
    relevant = sorted(set(apps) & current_appids)
    if len(relevant) < 2:
        return None, 'fewer_than_two_current_app_candidates'

    original = original_kzt(option)
    if original is None or original < current:
        original = current

    end_epoch = min(end_values) if end_values else None
    end_utc = (
        datetime.fromtimestamp(end_epoch, tz=timezone.utc).isoformat()
        if end_epoch is not None else None
    )
    return {
        'key': f'Sub_{pid}',
        'packageid': pid,
        'entity_kind': 'sub',
        'fixed_price_semantics': True,
        'personalized_price': False,
        'title': store_item.get('name') or option.get('purchase_option_name') or f'Steam package {pid}',
        'purchase_option_name': option.get('purchase_option_name'),
        'final_kzt': current,
        'original_kzt': original,
        'discount_percent': discount,
        'discount_end_utc': end_utc,
        'included_appids': apps,
        'all_included_appids': all_included_appids(store_item),
        'current_candidate_appids_in_package': relevant,
        'source_appids': sorted(source_appids),
        'web_url': f'https://store.steampowered.com/sub/{pid}/',
        'source': 'IStoreBrowseService/GetItems',
    }, None


def content_type(store_item):
    value = int(store_item.get('type') or 0)
    return APP_TYPE.get(value, f'unknown:{value}')


def candidate_single_app_purchase_options(appid, store_item):
    rows = []
    for option in store_item.get('purchase_options') or []:
        pid = int(option.get('packageid') or 0)
        price = final_kzt(option)
        if pid <= 0 or price is None or price <= 0:
            continue
        rows.append((pid, price, option))
    rows.sort(key=lambda row: (
        row[1],
        -int(row[2].get('discount_pct') or 0),
        row[0],
    ))
    return rows


def build_content_catalog(content_appids, content_items, purchase_route_packages):
    if len(content_appids) != len(content_items):
        raise SystemExit('Included-content StoreBrowse cardinality mismatch')
    catalog = {}
    for appid, item in zip(content_appids, content_items):
        if int(item.get('item_type') or 0) != 0 or int(item.get('id') or 0) != appid:
            raise SystemExit(f'Included-content identity mismatch for App_{appid}')
        related = item.get('related_items') or {}
        parent = related.get('parent_appid')
        verified_option = None
        for pid, price, option in candidate_single_app_purchase_options(appid, item):
            route_item = purchase_route_packages.get(pid)
            if route_item is None:
                continue
            # Count a monetary value only when Steam proves this fixed Sub acquires
            # exactly this top-level app. That prevents a bundle/season-pack route
            # from being counted independently for multiple included entitlements.
            if set(all_included_appids(route_item)) != {appid}:
                continue
            verified_option = (pid, price, option)
            break

        if verified_option is None:
            current = None
            original = None
            discount = None
            route_pid = None
            route_name = None
            valuation_status = 'no_verified_single_app_purchase_route'
        else:
            route_pid, current, option = verified_option
            original = original_kzt(option)
            if original is None or original < current:
                original = current
            discount = int(option.get('discount_pct') or 0)
            route_name = option.get('purchase_option_name')
            valuation_status = 'verified_single_app_purchase_route'

        catalog[appid] = {
            'appid': str(appid),
            'title': item.get('name') or f'App {appid}',
            'app_type': content_type(item),
            'parent_appid': str(parent) if parent is not None else None,
            'current_standalone_kzt': current,
            'original_standalone_kzt': original,
            'standalone_discount_percent': discount,
            'standalone_purchase_packageid': route_pid,
            'standalone_purchase_option_name': route_name,
            'valuation_status': valuation_status,
            'source': 'IStoreBrowseService/GetItems',
        }
    return catalog


def enrich_verified_included_content(packages, package_items):
    content_appids = sorted({
        appid
        for package in packages.values()
        for appid in (package.get('all_included_appids') or [])
    })
    if not content_appids:
        return 0, 0, 0

    content_items, content_request_count = fetch_app_items(content_appids)
    route_package_ids = sorted({
        int(option.get('packageid') or 0)
        for item in content_items
        for option in (item.get('purchase_options') or [])
        if int(option.get('packageid') or 0) > 0 and final_kzt(option) is not None and final_kzt(option) > 0
    })
    route_packages, route_request_count = (
        fetch_package_items(route_package_ids) if route_package_ids else ({}, 0)
    )
    catalog = build_content_catalog(content_appids, content_items, route_packages)

    for key, package in packages.items():
        pid = int(package.get('packageid') or 0)
        original_item = package_items.get(pid) or {}
        full_ids = all_included_appids(original_item)
        package['all_included_appids'] = [str(value) for value in full_ids]
        package['included_content'] = [catalog[value] for value in full_ids if value in catalog]
        package['verified_included_content_count'] = len(package['included_content'])
        package['verified_priced_included_content_count'] = sum(
            1 for row in package['included_content']
            if row.get('current_standalone_kzt') is not None
        )
        package['included_content_complete_for_all_included_appids'] = (
            len(package['included_content']) == len(full_ids)
        )
    return content_request_count, route_request_count, len(content_appids)


def main():
    started = time.monotonic()
    index, appids = load_current_appids()
    app_items, app_request_count = fetch_app_items(appids)
    sources = package_ids_from_app_items(appids, app_items)

    package_ids = sorted(sources)
    package_items, package_request_count = (
        fetch_package_items(package_ids) if package_ids else ({}, 0)
    )

    observed = datetime.now(timezone.utc)
    observed_epoch = int(observed.timestamp())
    current_appids = set(appids)
    packages = {}
    classifications = {}
    for pid in package_ids:
        key = f'Sub_{pid}'
        item = package_items.get(pid)
        if item is None:
            classifications[key] = 'package_not_returned_by_storebrowse'
            continue
        entry, reason = classify_package(
            pid, item, sources[pid], current_appids, observed_epoch
        )
        if entry is not None:
            packages[key] = entry
            classifications[key] = 'eligible_fixed_multi_candidate_package'
        else:
            classifications[key] = reason

    content_request_count, content_route_request_count, included_content_app_count = (
        enrich_verified_included_content(packages, package_items)
        if packages else (0, 0, 0)
    )

    out = {
        'schema_version': 2,
        'purpose': 'pre_ai_purchase_only_fixed_package_options',
        'status': 'complete',
        'authoritative_for': [
            'fixed_sub_package_current_kzt_price',
            'fixed_sub_package_membership',
            'fixed_sub_verified_top_level_included_content',
            'verified_single_app_kzt_acquisition_price_for_included_content',
        ],
        'source_mailing_updated_at_utc': index.get('source_updated_at_utc'),
        'observed_at_utc': observed.isoformat(),
        'network_source': 'IStoreBrowseService/GetItems',
        'current_app_candidate_count': len(appids),
        'discovered_packageid_count': len(package_ids),
        'eligible_package_count': len(packages),
        'classified_package_count': len(classifications),
        'classification_complete': len(classifications) == len(package_ids),
        'app_discovery_request_count': app_request_count,
        'package_detail_request_count': package_request_count,
        'included_content_app_count': included_content_app_count,
        'included_content_detail_request_count': content_request_count,
        'included_content_purchase_route_request_count': content_route_request_count,
        'batch_size': BATCH_SIZE,
        'dynamic_bundle_ids_supported': False,
        'personalized_complete_the_set_supported': False,
        'verified_content_unpriced_value_assumed_kzt': 0,
        'package_classifications': classifications,
        'packages': packages,
        'elapsed_seconds': round(time.monotonic() - started, 3),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n',
        encoding='utf-8',
    )
    print(json.dumps({
        'status': out['status'],
        'apps': len(appids),
        'packageids_discovered': len(package_ids),
        'eligible_fixed_packages': len(packages),
        'included_content_apps': included_content_app_count,
        'requests': (
            app_request_count + package_request_count
            + content_request_count + content_route_request_count
        ),
        'elapsed_seconds': out['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
