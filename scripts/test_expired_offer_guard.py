import json
import tempfile
import time
from pathlib import Path

import build_pre_ai_store_snapshot as target


def make_item(appid, discount_pct, final_cents, original_cents, end_epoch_marker):
    option = {
        'packageid': 100000 + appid,
        'purchase_option_name': f'Test {appid}',
        'discount_pct': discount_pct,
        'final_price_in_cents': final_cents,
        'original_price_in_cents': original_cents,
        'active_discounts': [],
    }
    if end_epoch_marker == 'past':
        option['active_discounts'] = [{'discount_end_date': int(time.time()) - 3600}]
    elif end_epoch_marker == 'future':
        option['active_discounts'] = [{'discount_end_date': int(time.time()) + 3600}]
    return {
        'item_type': 0,
        'id': appid,
        'appid': appid,
        'name': f'Test {appid}',
        'type': 0,
        'basic_info': {'short_description': f'Description {appid}'},
        'purchase_options': [option],
    }


def main():
    index = {
        'item_count': 4,
        'source_updated_at_utc': 'test-source',
    }
    feed = {
        'App_1': {'key': 'App_1', 'appid': '1', 'title': 'Future', 'source_discount_percent': 50, 'source_final_kzt': 500.0},
        'App_2': {'key': 'App_2', 'appid': '2', 'title': 'Unknown end', 'source_discount_percent': 50, 'source_final_kzt': 500.0},
        'App_3': {'key': 'App_3', 'appid': '3', 'title': 'Expired', 'source_discount_percent': 50, 'source_final_kzt': 500.0},
        'App_4': {'key': 'App_4', 'appid': '4', 'title': 'No discount', 'source_discount_percent': 50, 'source_final_kzt': 500.0},
    }
    items = {
        'App_1': make_item(1, 50, 50000, 100000, 'future'),
        'App_2': make_item(2, 50, 50000, 100000, None),
        'App_3': make_item(3, 50, 50000, 100000, 'past'),
        'App_4': make_item(4, 0, 100000, 100000, None),
    }

    original = {
        'load_feed': target.load_feed,
        'fetch_batches': target.fetch_batches,
        'compare_with_control': target.compare_with_control,
        'OUT_DIR': target.OUT_DIR,
        'STORE_OUT': target.STORE_OUT,
        'METADATA_OUT': target.METADATA_OUT,
    }
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target.load_feed = lambda: (index, feed)
            target.fetch_batches = lambda requested: ([(key, items[key]) for key in feed], 1)
            target.compare_with_control = lambda metadata: {'control_available': False, 'test': True}
            target.OUT_DIR = root
            target.STORE_OUT = root / 'store_snapshot.json'
            target.METADATA_OUT = root / 'content_metadata.json'
            target.main()

            store = json.loads(target.STORE_OUT.read_text(encoding='utf-8'))
            metadata = json.loads(target.METADATA_OUT.read_text(encoding='utf-8'))

            assert store['classification_complete'] is True
            assert store['classified_source_candidate_count'] == 4
            assert store['active_paid_discount_count'] == 2
            assert store['inactive_source_candidate_count'] == 2
            assert set(store['entries']) == {'App_1', 'App_2'}
            assert set(store['inactive_entries']) == {'App_3', 'App_4'}
            assert store['inactive_entries']['App_3']['reason'] == 'known_discount_end_not_after_store_observation'
            assert store['inactive_entries']['App_4']['reason'] == 'no_active_discounted_purchase_option'
            assert store['entries']['App_1']['discount_end_utc'] is not None
            assert store['entries']['App_2']['discount_end_utc'] is None
            assert store['sale_end_unknown_count'] == 1
            assert store['sale_end_unknown_keys'] == ['App_2']
            assert metadata['entry_count'] == 4
            assert set(metadata['entries']) == set(feed)
    finally:
        for name, value in original.items():
            setattr(target, name, value)

    print('EXPIRED_OFFER_GUARD=PASS')


if __name__ == '__main__':
    main()
