import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

MAILING_INDEX = Path('data/production/mailing/index.json')
OUT_DIR = Path('data/production/pre_ai')
OUT = OUT_DIR / 'store_snapshot.json'
BATCH_SIZE = 100
DISPLAY_TZ = ZoneInfo('Europe/Berlin')


def final_kzt(option):
    value = option.get('final_price_in_cents')
    return None if value is None else float(value) / 100.0


def original_kzt(option):
    value = option.get('original_price_in_cents')
    return None if value is None else float(value) / 100.0


def load_feed():
    index = json.loads(MAILING_INDEX.read_text(encoding='utf-8'))
    columns = index['columns']
    ci = {name: i for i, name in enumerate(columns)}
    required = {'key', 'appid', 'discount_percent', 'final_kzt', 'title'}
    missing = required - set(columns)
    if missing:
        raise SystemExit(f'Mailing feed lacks required columns: {sorted(missing)}')

    feed = {}
    for number in range(1, int(index['chunk_count']) + 1):
        path = Path(index['chunk_pattern'].replace('NNN', f'{number:03d}'))
        for line in path.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            cells = line.split('\t')
            if len(cells) != len(columns):
                raise SystemExit(f'Column mismatch in {path}')
            key = cells[ci['key']]
            if key in feed:
                raise SystemExit(f'Duplicate mailing key: {key}')
            feed[key] = {
                'key': key,
                'appid': cells[ci['appid']],
                'title': cells[ci['title']],
                'source_discount_percent': int(float(cells[ci['discount_percent']])),
                'source_final_kzt': float(cells[ci['final_kzt']]),
            }
    if len(feed) != int(index['item_count']):
        raise SystemExit('Mailing item_count mismatch')
    return index, feed


def requested_ids(feed):
    requested = []
    for row in feed.values():
        key = row['key']
        if key.startswith('App_') and row['appid']:
            requested.append((key, {'appid': int(row['appid'])}))
        elif key.startswith('Sub_'):
            requested.append((key, {'packageid': int(key.split('_', 1)[1])}))
        else:
            raise SystemExit(f'Unsupported StoreBrowse key: {key}')
    return requested


def fetch_batches(requested):
    paired = []
    request_count = 0
    for start in range(0, len(requested), BATCH_SIZE):
        batch = requested[start:start + BATCH_SIZE]
        payload = {
            'ids': [rid for _, rid in batch],
            'context': {
                'language': 'english',
                'country_code': 'KZ',
                'steam_realm': 1,
            },
            'data_request': {'include_all_purchase_options': True},
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
        for (key, rid), store_item in zip(batch, returned):
            if 'appid' in rid:
                identity_ok = int(store_item.get('appid') or 0) == rid['appid']
            else:
                pid = rid['packageid']
                identity_ok = (
                    int(store_item.get('packageid') or 0) == pid
                    or any(
                        int(option.get('packageid') or 0) == pid
                        for option in (store_item.get('purchase_options') or [])
                    )
                )
            if not identity_ok:
                raise SystemExit(f'StoreBrowse identity mismatch for {key}')
            paired.append((key, store_item))
    return paired, request_count


def choose_option(key, row, store_item):
    options = store_item.get('purchase_options') or []
    if key.startswith('Sub_'):
        pid = int(key.split('_', 1)[1])
        exact = [o for o in options if int(o.get('packageid') or 0) == pid]
        if len(exact) == 1:
            return exact[0], 'exact_packageid'
        if len(exact) > 1:
            exact.sort(key=lambda o: (final_kzt(o) if final_kzt(o) is not None else float('inf'), -int(o.get('discount_pct') or 0)))
            return exact[0], 'exact_packageid_lowest_price'
        raise SystemExit(f'No exact package purchase option for {key}')

    exact = [
        o for o in options
        if int(o.get('discount_pct') or 0) == row['source_discount_percent']
        and final_kzt(o) is not None
        and abs(final_kzt(o) - row['source_final_kzt']) < 0.011
    ]
    if exact:
        exact.sort(key=lambda o: (int(o.get('packageid') or 0), str(o.get('purchase_option_name') or '')))
        return exact[0], 'exact_source_deal'

    discounted = [
        o for o in options
        if int(o.get('discount_pct') or 0) > 0 and final_kzt(o) is not None
    ]
    if discounted:
        discounted.sort(key=lambda o: (final_kzt(o), -int(o.get('discount_pct') or 0), int(o.get('packageid') or 0)))
        return discounted[0], 'current_lowest_discounted_option_after_source_change'

    raise SystemExit(f'No active discounted purchase option for {key}')


def main():
    started = time.monotonic()
    index, feed = load_feed()
    requested = requested_ids(feed)
    paired, request_count = fetch_batches(requested)
    observed = datetime.now(timezone.utc)

    entries = {}
    changed = []
    sale_end_unknown = []
    selection_counts = {}

    for key, store_item in paired:
        row = feed[key]
        option, selection_method = choose_option(key, row, store_item)
        selection_counts[selection_method] = selection_counts.get(selection_method, 0) + 1

        discount = int(option.get('discount_pct') or 0)
        current = final_kzt(option)
        original = original_kzt(option)
        if discount <= 0 or current is None or current <= 0:
            raise SystemExit(f'Selected StoreBrowse option is not an active paid discount for {key}')

        end_values = sorted({
            int(d.get('discount_end_date') or 0)
            for d in (option.get('active_discounts') or [])
            if int(d.get('discount_end_date') or 0) > 0
        })
        if not end_values:
            sale_end_unknown.append(key)
            continue
        # If stacked active discounts exist, the earliest ending component can change the current final price.
        end_epoch = min(end_values)
        end_utc = datetime.fromtimestamp(end_epoch, tz=timezone.utc)
        end_local = end_utc.astimezone(DISPLAY_TZ)

        deal_changed = (
            discount != row['source_discount_percent']
            or abs(current - row['source_final_kzt']) >= 0.011
        )
        if deal_changed:
            changed.append(key)

        entries[key] = {
            'key': key,
            'appid': row['appid'] or None,
            'title': row['title'],
            'purchase_packageid': int(option.get('packageid') or 0) or None,
            'purchase_option_name': option.get('purchase_option_name'),
            'selection_method': selection_method,
            'discount_percent': discount,
            'final_kzt': current,
            'original_kzt': original,
            'discount_end_epoch': end_epoch,
            'discount_end_utc': end_utc.isoformat(),
            'discount_end_europe_berlin': end_local.isoformat(),
            'discount_end_date_europe_berlin': end_local.date().isoformat(),
            'source_discount_percent': row['source_discount_percent'],
            'source_final_kzt': row['source_final_kzt'],
            'changed_since_discovery_snapshot': deal_changed,
        }

    if sale_end_unknown:
        raise SystemExit(f'Missing sale end for active discounts: {sale_end_unknown[:20]}')
    if len(entries) != len(feed):
        raise SystemExit(f'Pre-AI Store snapshot incomplete: entries={len(entries)} source={len(feed)}')

    out = {
        'schema_version': 1,
        'purpose': 'pre_ai_current_store_snapshot',
        'status': 'complete',
        'authoritative_for': ['current_price_kzt', 'discount_percent', 'discount_end'],
        'discovery_source_path': 'data/production/mailing/index.json',
        'discovery_source_updated_at_utc': index.get('source_updated_at_utc'),
        'observed_at_utc': observed.isoformat(),
        'display_timezone': 'Europe/Berlin',
        'source_item_count': len(feed),
        'entry_count': len(entries),
        'request_count': request_count,
        'batch_size': BATCH_SIZE,
        'sale_end_known_count': len(entries),
        'sale_end_unknown_count': 0,
        'sale_end_coverage_ratio': 1.0,
        'changed_since_discovery_count': len(changed),
        'changed_since_discovery_keys': sorted(changed),
        'selection_method_counts': selection_counts,
        'elapsed_seconds': round(time.monotonic() - started, 3),
        'entries': entries,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': out['status'],
        'entries': out['entry_count'],
        'requests': out['request_count'],
        'sale_end_coverage': out['sale_end_coverage_ratio'],
        'changed_since_discovery': out['changed_since_discovery_count'],
        'selection_methods': out['selection_method_counts'],
        'elapsed_seconds': out['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
