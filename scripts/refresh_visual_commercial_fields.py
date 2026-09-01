import json
from datetime import datetime, timezone
from pathlib import Path

import build_daily_visual_payload as base_builder

ROOT = Path('.')
PAYLOAD = ROOT / 'data/production/pre_ai/chatgpt_payload.json'
STORE_SNAPSHOT = ROOT / 'data/production/pre_ai/store_snapshot.json'
FAMILY_GRAPH = ROOT / 'data/production/pre_ai/family_graph.json'
HISTORY_SNAPSHOT = ROOT / 'data/production/pre_ai/history_snapshot.json'


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def current_docs():
    return (
        load_json(PAYLOAD),
        load_json(STORE_SNAPSHOT),
        load_json(FAMILY_GRAPH),
        load_json(HISTORY_SNAPSHOT),
    )


def validate_commercial_binding(payload, store_snapshot, family_graph):
    source = payload.get('source_mailing_updated_at_utc')
    store_source = store_snapshot.get('discovery_source_updated_at_utc')
    family_source = family_graph.get('source_updated_at_utc')
    if not source:
        raise ValueError('Commercial refresh requires payload source_mailing_updated_at_utc')
    if store_snapshot.get('status') != 'complete':
        raise ValueError('Commercial refresh requires complete store_snapshot')
    if family_graph.get('status') != 'complete':
        raise ValueError('Commercial refresh requires complete family_graph')
    if store_source != source or family_source != source:
        raise ValueError(
            'Commercial source mismatch: '
            f'payload={source} store={store_source} family={family_source}'
        )
    rate = ((payload.get('fx_binding') or {}).get('kzt_per_rub'))
    if rate is None or float(rate) <= 0:
        raise ValueError('Commercial refresh requires positive kzt_per_rub')
    return source, float(rate)


def offer_keys_for_family(family, store_entries):
    base_appids = {
        str(value)
        for value in (family.get('base_appids') or [])
        if str(value).isdigit()
    }
    keys = []
    for key in [
        family.get('primary_key'),
        *(family.get('alternative_purchase_keys') or []),
        *(family.get('all_member_keys') or []),
    ]:
        if key and key not in keys:
            keys.append(key)
    for key, row in store_entries.items():
        if not isinstance(row, dict):
            continue
        if str(row.get('appid') or '') in base_appids and key not in keys:
            keys.append(key)
    return keys


def refreshed_offer(key, store_entries, history_entries, rate, now):
    offer = base_builder.visual_builder.offer_from_store(
        key,
        store_entries,
        history_entries,
        rate,
    )
    if not offer:
        return None
    if base_builder.sale_expired(offer.get('sale_end_utc'), now):
        return None
    hist, previously_free, quality = base_builder.history_values(
        key,
        history_entries,
        rate,
    )
    offer['historical_minimum_rub'] = hist
    offer['previously_free'] = previously_free
    offer['history_quality'] = quality
    return offer


def refresh_visual_commercial_fields(
    visual,
    *,
    payload=None,
    store_snapshot=None,
    family_graph=None,
    history_snapshot=None,
    now=None,
):
    """Refresh deterministic commercial fields without recalculating semantic Taste.

    The accepted semantic card remains the same object: fit, taste factors, explanations,
    risks and semantic source stay untouched. Only current offers/price/history/deadline
    are rebuilt from one current GitHub-owned commercial source before package scoring.
    """
    if payload is None or store_snapshot is None or family_graph is None or history_snapshot is None:
        current_payload, current_store, current_family, current_history = current_docs()
        payload = payload or current_payload
        store_snapshot = store_snapshot or current_store
        family_graph = family_graph or current_family
        history_snapshot = history_snapshot or current_history

    source, rate = validate_commercial_binding(payload, store_snapshot, family_graph)
    store_entries = store_snapshot.get('entries') or {}
    history_entries = history_snapshot.get('entries') or {}
    family_by_id = {
        str(row.get('family_id')): row
        for row in (family_graph.get('families') or [])
        if isinstance(row, dict) and row.get('family_id')
    }
    now = now or datetime.now(timezone.utc)

    refreshed = []
    missing_families = []
    removed_without_active_offer = []
    changed_price_count = 0
    changed_offer_count = 0

    for game in visual.get('items') or []:
        family_id = str(game.get('id') or '')
        family = family_by_id.get(family_id)
        if family is None:
            missing_families.append(family_id)
            continue

        offers = []
        for key in offer_keys_for_family(family, store_entries):
            offer = refreshed_offer(key, store_entries, history_entries, rate, now)
            if offer is not None:
                offers.append(offer)
        offers.sort(key=lambda row: (
            int(row.get('current_price_rub') or 999999),
            -int(row.get('discount_percent') or 0),
            str(row.get('title') or '').casefold(),
        ))
        if not offers:
            removed_without_active_offer.append(family_id)
            continue

        primary_key = family.get('primary_key')
        primary = next((row for row in offers if row.get('key') == primary_key), None)
        if primary is None:
            primary = offers[0]
        offers = [primary] + [row for row in offers if row is not primary]

        old_price = game.get('current_price_rub')
        old_offer_signature = [
            (row.get('key'), row.get('current_price_rub'), row.get('discount_percent'), row.get('sale_end_utc'))
            for row in (game.get('offers') or [])
            if isinstance(row, dict) and row.get('offer_kind') != 'fixed_multi_game_package'
        ]
        new_offer_signature = [
            (row.get('key'), row.get('current_price_rub'), row.get('discount_percent'), row.get('sale_end_utc'))
            for row in offers
        ]
        if old_price != primary.get('current_price_rub'):
            changed_price_count += 1
        if old_offer_signature != new_offer_signature:
            changed_offer_count += 1

        game['offers'] = offers
        game['current_price_rub'] = primary.get('current_price_rub')
        game['original_price_rub'] = primary.get('original_price_rub')
        game['discount_percent'] = primary.get('discount_percent')
        game['historical_minimum_rub'] = primary.get('historical_minimum_rub')
        game['previously_free'] = bool(primary.get('previously_free'))
        game['history_quality'] = primary.get('history_quality') or 'unverified'
        game['sale_end_utc'] = primary.get('sale_end_utc')
        game['steam_url'] = primary.get('steam_url') or game.get('steam_url')
        game['web_url'] = primary.get('web_url') or game.get('web_url')
        refreshed.append(game)

    if missing_families:
        raise ValueError(
            'Commercial refresh cannot source-align every visible semantic family: '
            + ','.join(sorted(missing_families)[:20])
        )

    visual['items'] = refreshed
    visual['item_count'] = len(refreshed)
    visual['commercial_source_mailing_updated_at_utc'] = source
    visual['commercial_store_observed_at_utc'] = store_snapshot.get('observed_at_utc')
    stats = {
        'schema_version': 1,
        'semantic_source_preserved': visual.get('source_mailing_updated_at_utc'),
        'commercial_source_mailing_updated_at_utc': source,
        'store_observed_at_utc': store_snapshot.get('observed_at_utc'),
        'visible_item_count_before_refresh': len(visual.get('items') or []) + len(removed_without_active_offer),
        'visible_item_count_after_refresh': len(refreshed),
        'removed_without_active_offer_count': len(removed_without_active_offer),
        'removed_without_active_offer_ids': removed_without_active_offer,
        'changed_price_count': changed_price_count,
        'changed_offer_count': changed_offer_count,
        'taste_recalculated': False,
        'semantic_fields_rewritten': False,
    }
    visual['commercial_refresh'] = stats
    return stats
