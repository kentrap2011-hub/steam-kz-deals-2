import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

MAILING_INDEX = Path('data/production/mailing/index.json')
OLD_METADATA = Path('data/cache/content_metadata.json')
OUT_DIR = Path('data/production/pre_ai')
STORE_OUT = OUT_DIR / 'store_snapshot.json'
METADATA_OUT = OUT_DIR / 'content_metadata.json'
BATCH_SIZE = 100
DISPLAY_TZ = ZoneInfo('Europe/Berlin')

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
        for (key, rid), store_item in zip(batch, returned):
            if 'appid' in rid:
                # StoreItem.id identifies the requested store entity. StoreItem.appid can
                # point at underlying content for legacy/collection store pages.
                identity_ok = (
                    int(store_item.get('item_type') or 0) == 0
                    and int(store_item.get('id') or 0) == rid['appid']
                )
            else:
                pid = rid['packageid']
                identity_ok = (
                    int(store_item.get('id') or store_item.get('packageid') or 0) == pid
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
            exact.sort(key=lambda o: (
                final_kzt(o) if final_kzt(o) is not None else float('inf'),
                -int(o.get('discount_pct') or 0),
            ))
            return exact[0], 'exact_packageid_lowest_price'
        return None, 'no_exact_package_purchase_option'

    exact = [
        o for o in options
        if int(o.get('discount_pct') or 0) == row['source_discount_percent']
        and final_kzt(o) is not None
        and abs(final_kzt(o) - row['source_final_kzt']) < 0.011
    ]
    if exact:
        exact.sort(key=lambda o: (
            int(o.get('packageid') or 0),
            str(o.get('purchase_option_name') or ''),
        ))
        return exact[0], 'exact_source_deal'

    discounted = [
        o for o in options
        if int(o.get('discount_pct') or 0) > 0 and final_kzt(o) is not None
    ]
    if discounted:
        discounted.sort(key=lambda o: (
            final_kzt(o),
            -int(o.get('discount_pct') or 0),
            int(o.get('packageid') or 0),
        ))
        return discounted[0], 'current_lowest_discounted_option_after_source_change'

    return None, 'no_active_discounted_purchase_option'


def included_app_name_map(store_item):
    result = {}
    included = store_item.get('included_items') or {}
    for app in included.get('included_apps') or []:
        if not isinstance(app, dict):
            continue
        appid = app.get('appid') or app.get('id')
        if appid is None:
            continue
        result[str(appid)] = app.get('name')
    return result


def metadata_entry(key, row, store_item):
    store_name = store_item.get('name') or row['title']
    if key.startswith('Sub_'):
        subid = key.split('_', 1)[1]
        appids = [str(x) for x in (store_item.get('included_appids') or [])]
        if not appids:
            included = store_item.get('included_items') or {}
            appids = [
                str(app.get('appid') or app.get('id'))
                for app in (included.get('included_apps') or [])
                if isinstance(app, dict) and (app.get('appid') is not None or app.get('id') is not None)
            ]
        appids = sorted(set(appids), key=lambda x: int(x))
        names = included_app_name_map(store_item)
        return {
            'key': key,
            'entity_kind': 'sub',
            'steam_id': str(subid),
            'store_name': store_name,
            'short_description': str((store_item.get('basic_info') or {}).get('short_description') or '').strip() or None,
            'package_apps': [
                {'appid': appid, 'name': names.get(appid)}
                for appid in appids
            ],
            'metadata_source': 'IStoreBrowseService/GetItems',
        }

    type_number = int(store_item.get('type') or 0)
    app_type = APP_TYPE.get(type_number, f'unknown:{type_number}')
    related = store_item.get('related_items') or {}
    parent_appid = related.get('parent_appid')
    return {
        'key': key,
        'entity_kind': 'app',
        'steam_id': str(row['appid']),
        'store_name': store_name,
        'short_description': str((store_item.get('basic_info') or {}).get('short_description') or '').strip() or None,
        'app_type': app_type,
        'fullgame_appid': str(parent_appid) if parent_appid is not None else None,
        'fullgame_name': None,
        'metadata_source': 'IStoreBrowseService/GetItems',
    }


def compare_with_control(metadata_entries):
    if not OLD_METADATA.exists():
        return {
            'control_available': False,
            'comparable_count': 0,
            'match_count': 0,
            'mismatch_count': 0,
            'match_ratio': None,
        }
    old = json.loads(OLD_METADATA.read_text(encoding='utf-8'))
    controls = old.get('entries') or {}
    comparable = 0
    mismatches = []

    for key, expected in controls.items():
        got = metadata_entries.get(key)
        if not isinstance(expected, dict) or not isinstance(got, dict):
            continue
        if expected.get('entity_kind') == 'app' and got.get('entity_kind') == 'app':
            comparable += 1
            expected_parent = str(expected.get('fullgame_appid') or '') or None
            got_parent = str(got.get('fullgame_appid') or '') or None
            ok = (
                expected.get('app_type') == got.get('app_type')
                and (
                    expected.get('app_type') != 'dlc'
                    or expected_parent == got_parent
                )
            )
            if not ok:
                mismatches.append({
                    'key': key,
                    'expected_type': expected.get('app_type'),
                    'got_type': got.get('app_type'),
                    'expected_parent': expected_parent,
                    'got_parent': got_parent,
                })
        elif expected.get('entity_kind') == 'sub' and got.get('entity_kind') == 'sub':
            comparable += 1
            expected_ids = sorted(
                str(app.get('appid'))
                for app in (expected.get('package_apps') or [])
                if isinstance(app, dict) and app.get('appid') is not None
            )
            got_ids = sorted(
                str(app.get('appid'))
                for app in (got.get('package_apps') or [])
                if isinstance(app, dict) and app.get('appid') is not None
            )
            if expected_ids != got_ids:
                mismatches.append({
                    'key': key,
                    'expected_appids': expected_ids,
                    'got_appids': got_ids,
                })

    if mismatches:
        raise SystemExit(
            'StoreBrowse metadata differs from validated control: '
            + json.dumps(mismatches[:20], ensure_ascii=False)
        )
    return {
        'control_available': True,
        'control_entry_count': len(controls),
        'comparable_count': comparable,
        'match_count': comparable,
        'mismatch_count': 0,
        'match_ratio': 1.0 if comparable else None,
    }


def main():
    started = time.monotonic()
    index, feed = load_feed()
    requested = requested_ids(feed)
    paired, request_count = fetch_batches(requested)
    observed = datetime.now(timezone.utc)

    store_entries = {}
    metadata_entries = {}
    changed = []
    sale_end_unknown = []
    selection_counts = {}
    type_counts = {}

    inactive_entries = {}
    observed_epoch = int(observed.timestamp())

    for key, store_item in paired:
        row = feed[key]

        # Content identity/metadata remains complete even when the paid offer has ended.
        meta = metadata_entry(key, row, store_item)
        metadata_entries[key] = meta
        label = meta.get('app_type') if meta.get('entity_kind') == 'app' else 'package'
        type_counts[label or 'unknown'] = type_counts.get(label or 'unknown', 0) + 1

        option, selection_method = choose_option(key, row, store_item)
        selection_counts[selection_method] = selection_counts.get(selection_method, 0) + 1
        if option is None:
            inactive_entries[key] = {
                'key': key,
                'appid': row['appid'] or None,
                'title': row['title'],
                'reason': selection_method,
                'source_discount_percent': row['source_discount_percent'],
                'source_final_kzt': row['source_final_kzt'],
            }
            continue

        discount = int(option.get('discount_pct') or 0)
        current = final_kzt(option)
        original = original_kzt(option)
        if discount <= 0 or current is None or current <= 0:
            inactive_entries[key] = {
                'key': key,
                'appid': row['appid'] or None,
                'title': row['title'],
                'reason': 'observed_option_is_not_an_active_paid_discount',
                'observed_discount_percent': discount,
                'observed_final_kzt': current,
                'source_discount_percent': row['source_discount_percent'],
                'source_final_kzt': row['source_final_kzt'],
            }
            continue
        if original is None or original < current:
            raise SystemExit(f'Invalid original price for current discounted option {key}')

        end_values = sorted({
            int(d.get('discount_end_date') or 0)
            for d in (option.get('active_discounts') or [])
            if int(d.get('discount_end_date') or 0) > 0
        })
        # A live endpoint can briefly expose a just-expired option. Never carry it
        # forward merely because discount_pct has not yet refreshed.
        if end_values and min(end_values) <= observed_epoch:
            inactive_entries[key] = {
                'key': key,
                'appid': row['appid'] or None,
                'title': row['title'],
                'reason': 'known_discount_end_not_after_store_observation',
                'observed_discount_percent': discount,
                'observed_final_kzt': current,
                'observed_discount_end_epoch': min(end_values),
                'source_discount_percent': row['source_discount_percent'],
                'source_final_kzt': row['source_final_kzt'],
            }
            continue

        if end_values:
            # If stacked active discounts exist, the earliest ending component can change the current final price.
            end_epoch = min(end_values)
            end_utc = datetime.fromtimestamp(end_epoch, tz=timezone.utc)
            end_local = end_utc.astimezone(DISPLAY_TZ)
        else:
            sale_end_unknown.append(key)
            end_epoch = None
            end_utc = None
            end_local = None

        deal_changed = (
            discount != row['source_discount_percent']
            or abs(current - row['source_final_kzt']) >= 0.011
        )
        if deal_changed:
            changed.append(key)

        store_entries[key] = {
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
            'discount_end_utc': end_utc.isoformat() if end_utc else None,
            'discount_end_europe_berlin': end_local.isoformat() if end_local else None,
            'discount_end_date_europe_berlin': end_local.date().isoformat() if end_local else None,
            'source_discount_percent': row['source_discount_percent'],
            'source_final_kzt': row['source_final_kzt'],
            'changed_since_discovery_snapshot': deal_changed,
        }

    if len(store_entries) + len(inactive_entries) != len(feed):
        raise SystemExit(
            'Pre-AI Store classification incomplete: '
            f'active={len(store_entries)} inactive={len(inactive_entries)} source={len(feed)}'
        )
    if len(metadata_entries) != len(feed):
        raise SystemExit(
            'Pre-AI metadata snapshot incomplete: '
            f'metadata={len(metadata_entries)} source={len(feed)}'
        )

    control = compare_with_control(metadata_entries)
    elapsed = round(time.monotonic() - started, 3)

    sale_end_known_count = len(store_entries) - len(sale_end_unknown)
    sale_end_coverage = (sale_end_known_count / len(store_entries)) if store_entries else 1.0
    store_out = {
        'schema_version': 3,
        'purpose': 'pre_ai_current_store_snapshot',
        'status': 'complete',
        'authoritative_for': ['current_active_paid_offer_state', 'current_price_kzt', 'discount_percent', 'discount_end'],
        'discovery_source_path': 'data/production/mailing/index.json',
        'discovery_source_updated_at_utc': index.get('source_updated_at_utc'),
        'observed_at_utc': observed.isoformat(),
        'display_timezone': 'Europe/Berlin',
        'source_item_count': len(feed),
        'classified_source_candidate_count': len(store_entries) + len(inactive_entries),
        'classification_complete': len(store_entries) + len(inactive_entries) == len(feed),
        'entry_count': len(store_entries),
        'active_paid_discount_count': len(store_entries),
        'inactive_source_candidate_count': len(inactive_entries),
        'inactive_source_candidate_keys': sorted(inactive_entries),
        'inactive_entries': inactive_entries,
        'request_count': request_count,
        'batch_size': BATCH_SIZE,
        'sale_end_known_count': sale_end_known_count,
        'sale_end_unknown_count': len(sale_end_unknown),
        'sale_end_unknown_keys': sorted(sale_end_unknown),
        'sale_end_coverage_ratio': round(sale_end_coverage, 4),
        'changed_since_discovery_count': len(changed),
        'changed_since_discovery_keys': sorted(changed),
        'selection_method_counts': selection_counts,
        'shared_storebrowse_pass_includes_content_metadata': True,
        'expired_or_inactive_source_candidates_are_not_current_entries': True,
        'elapsed_seconds_shared_pass': elapsed,
        'entries': store_entries,
    }
    metadata_out = {
        'schema_version': 1,
        'purpose': 'pre_ai_content_metadata_for_all_candidates',
        'status': 'complete',
        'source_path': 'data/production/mailing/index.json',
        'source_updated_at_utc': index.get('source_updated_at_utc'),
        'observed_at_utc': observed.isoformat(),
        'source_item_count': len(feed),
        'entry_count': len(metadata_entries),
        'complete_coverage': True,
        'network_source': 'IStoreBrowseService/GetItems',
        'network_request_count_shared_with_store_snapshot': request_count,
        'additional_network_requests_beyond_store_snapshot': 0,
        'type_counts': type_counts,
        'validated_control_comparison': control,
        'elapsed_seconds_shared_pass': elapsed,
        'entries': metadata_entries,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STORE_OUT.write_text(json.dumps(store_out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    METADATA_OUT.write_text(json.dumps(metadata_out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': 'complete',
        'source': len(feed),
        'classified': len(store_entries) + len(inactive_entries),
        'active_paid_discounts': len(store_entries),
        'inactive_source_candidates': len(inactive_entries),
        'metadata_entries': len(metadata_entries),
        'requests_shared': request_count,
        'sale_end_coverage': round(sale_end_coverage, 4),
        'sale_end_unknown': len(sale_end_unknown),
        'changed_since_discovery': len(changed),
        'metadata_types': type_counts,
        'control_comparison': control,
        'elapsed_seconds_shared_pass': elapsed,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
