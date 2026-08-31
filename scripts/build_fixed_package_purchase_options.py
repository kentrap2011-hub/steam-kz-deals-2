import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MAILING_INDEX = Path('data/production/mailing/index.json')
OUT = Path('data/production/pre_ai/fixed_package_options.json')
BATCH_SIZE = 100


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


def fetch_items(ids):
    items = []
    request_count = 0
    for start in range(0, len(ids), BATCH_SIZE):
        batch = ids[start:start + BATCH_SIZE]
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
        request_count += 1
        returned = (data.get('response') or {}).get('store_items') or []
        if len(returned) != len(batch):
            raise SystemExit(
                f'StoreBrowse batch cardinality mismatch: requested={len(batch)} returned={len(returned)}'
            )
        items.extend(returned)
    return items, request_count


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


def included_appids(store_item):
    values = [int(x) for x in (store_item.get('included_appids') or []) if str(x).isdigit()]
    if not values:
        included = store_item.get('included_items') or {}
        for app in included.get('included_apps') or []:
            if not isinstance(app, dict):
                continue
            value = app.get('appid') if app.get('appid') is not None else app.get('id')
            if value is not None and str(value).isdigit():
                values.append(int(value))
    return sorted(set(values))


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
        'current_candidate_appids_in_package': relevant,
        'source_appids': sorted(source_appids),
        'web_url': f'https://store.steampowered.com/sub/{pid}/',
        'source': 'IStoreBrowseService/GetItems',
    }, None


def main():
    started = time.monotonic()
    index, appids = load_current_appids()
    app_items, app_request_count = fetch_items([{'appid': appid} for appid in appids])
    sources = package_ids_from_app_items(appids, app_items)

    package_ids = sorted(sources)
    package_items, package_request_count = fetch_items(
        [{'packageid': pid} for pid in package_ids]
    ) if package_ids else ([], 0)

    observed = datetime.now(timezone.utc)
    observed_epoch = int(observed.timestamp())
    current_appids = set(appids)
    packages = {}
    classifications = {}
    for pid, item in zip(package_ids, package_items):
        entry, reason = classify_package(
            pid, item, sources[pid], current_appids, observed_epoch
        )
        key = f'Sub_{pid}'
        if entry is not None:
            packages[key] = entry
            classifications[key] = 'eligible_fixed_multi_candidate_package'
        else:
            classifications[key] = reason

    out = {
        'schema_version': 1,
        'purpose': 'pre_ai_purchase_only_fixed_package_options',
        'status': 'complete',
        'authoritative_for': [
            'fixed_sub_package_current_kzt_price',
            'fixed_sub_package_membership',
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
        'batch_size': BATCH_SIZE,
        'dynamic_bundle_ids_supported': False,
        'personalized_complete_the_set_supported': False,
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
        'requests': app_request_count + package_request_count,
        'elapsed_seconds': out['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
