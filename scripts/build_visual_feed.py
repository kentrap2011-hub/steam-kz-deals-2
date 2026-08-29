import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('.')
PURCHASE_CONTEXT = ROOT / 'data/production/pre_ai/chatgpt_purchase_context.jsonl'
CONTENT_METADATA = ROOT / 'data/production/pre_ai/content_metadata.json'
STORE_SNAPSHOT = ROOT / 'data/production/pre_ai/store_snapshot.json'
FAMILY_GRAPH = ROOT / 'data/production/pre_ai/family_graph.json'
HISTORY_SNAPSHOT = ROOT / 'data/production/pre_ai/history_snapshot.json'
TASTE_CACHE = ROOT / 'data/cache/taste_fit.json'
CHATGPT_PAYLOAD = ROOT / 'data/production/pre_ai/chatgpt_payload.json'
OUT = ROOT / 'web/data/current.json'


def load_json(path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding='utf-8'))


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def cache_entries(obj):
    entries = obj.get('entries') if isinstance(obj, dict) else None
    if isinstance(entries, dict):
        return entries
    if isinstance(entries, list):
        return {str(x.get('key')): x for x in entries if isinstance(x, dict) and x.get('key')}
    return {}


def evidence_text(item):
    if isinstance(item, str):
        return item.strip()
    if not isinstance(item, dict):
        return ''
    prop = item.get('candidate_property') or item.get('property') or item.get('game_property')
    anchor = item.get('profile_anchor') or item.get('user_pattern') or item.get('profile_pattern')
    reason = item.get('reason') or item.get('explanation') or item.get('text')
    if prop and anchor:
        return f'{prop} — совпадает с твоим предпочтением: {anchor}'
    if reason:
        return str(reason).strip()
    if prop:
        return str(prop).strip()
    return ''


def get_fit(row, taste_entries):
    if row.get('resolved_taste_fit') in {'strong', 'moderate'}:
        return row['resolved_taste_fit'], None
    entry = taste_entries.get(row.get('taste_subject_key'))
    if not isinstance(entry, dict):
        return None, None
    if str(entry.get('verdict')).upper() != 'INCLUDE':
        return None, entry
    fit = entry.get('fit_level')
    return (fit if fit in {'strong', 'moderate'} else None), entry


def rub_from_kzt(value, rate):
    if value is None or not rate:
        return None
    return int(round(float(value) / float(rate)))


def offer_from_store(key, store_entries, history_entries, rate):
    s = store_entries.get(key)
    if not isinstance(s, dict):
        return None
    current = rub_from_kzt(s.get('final_kzt'), rate)
    original = rub_from_kzt(s.get('original_kzt'), rate)
    if not current or not original or int(s.get('discount_percent') or 0) <= 0:
        return None
    h = history_entries.get(key) if isinstance(history_entries, dict) else None
    hist = None
    previously_free = False
    if isinstance(h, dict):
        hist = h.get('minimum_rub_display') or h.get('paid_minimum_rub_display')
        previously_free = bool(h.get('previously_free'))
    kind, steam_id = key.split('_', 1)
    if kind == 'App':
        web_url = f'https://store.steampowered.com/app/{steam_id}/'
        steam_url = f'steam://store/{steam_id}'
    else:
        web_url = f'https://store.steampowered.com/sub/{steam_id}/'
        steam_url = None
    return {
        'key': key,
        'title': s.get('purchase_option_name') or s.get('title') or key,
        'current_price_rub': current,
        'original_price_rub': original,
        'discount_percent': int(s.get('discount_percent') or 0),
        'historical_minimum_rub': hist,
        'previously_free': previously_free,
        'sale_end_utc': s.get('discount_end_utc'),
        'web_url': web_url,
        'steam_url': steam_url,
    }


def appdetails(appids):
    result = {}
    ids = sorted({str(x) for x in appids if str(x).isdigit()}, key=int)
    for start in range(0, len(ids), 20):
        batch = ids[start:start + 20]
        query = urllib.parse.urlencode({
            'appids': ','.join(batch),
            'cc': 'kz',
            'l': 'english',
        })
        req = urllib.request.Request(
            'https://store.steampowered.com/api/appdetails?' + query,
            headers={'User-Agent': 'steam-kz-deals-visual/1.0', 'Accept': 'application/json'},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
        except Exception:
            continue
        for appid in batch:
            payload = data.get(appid) or {}
            d = payload.get('data') if payload.get('success') else None
            if not isinstance(d, dict):
                continue
            shots = []
            for shot in d.get('screenshots') or []:
                url = shot.get('path_full') or shot.get('path_thumbnail')
                if url and url not in shots:
                    shots.append(url)
                if len(shots) >= 5:
                    break
            result[appid] = {
                'screenshots': shots,
                'header_image': d.get('header_image'),
                'short_description': d.get('short_description'),
            }
    return result


def main():
    rows = load_jsonl(PURCHASE_CONTEXT)
    metadata = cache_entries(load_json(CONTENT_METADATA))
    store_obj = load_json(STORE_SNAPSHOT)
    store_entries = store_obj.get('entries') or {}
    family_obj = load_json(FAMILY_GRAPH)
    families = family_obj.get('families') or []
    family_by_id = {x.get('family_id'): x for x in families if isinstance(x, dict)}
    history_obj = load_json(HISTORY_SNAPSHOT)
    history_entries = history_obj.get('entries') or {}
    taste_entries = cache_entries(load_json(TASTE_CACHE))
    payload = load_json(CHATGPT_PAYLOAD)
    rate = ((payload.get('fx_binding') or {}).get('kzt_per_rub'))

    family_base_map = {}
    for fam in families:
        if not isinstance(fam, dict):
            continue
        for appid in fam.get('base_appids') or []:
            family_base_map.setdefault(str(appid), []).append(fam)

    visible = []
    wanted_appids = set()
    for row in rows:
        fit, taste_entry = get_fit(row, taste_entries)
        if fit not in {'strong', 'moderate'}:
            continue
        scenario = row.get(f'deal_if_{fit}') or {}
        if scenario.get('disposition') != 'INCLUDE':
            continue
        purchase = row.get('purchase') or {}
        family_id = row.get('family_id')
        fam = family_by_id.get(family_id) or {}
        base_appids = [str(x) for x in ((row.get('semantic_condition') or {}).get('base_appids') or fam.get('base_appids') or [])]
        wanted_appids.update(x for x in base_appids if x.isdigit())

        main_key = purchase.get('key')
        offers = []
        seen_offer_keys = set()
        candidate_offer_keys = [main_key]
        candidate_offer_keys += list(fam.get('alternative_purchase_keys') or [])
        candidate_offer_keys += [x.get('primary_key') for appid in base_appids for x in family_base_map.get(appid, [])]
        candidate_offer_keys += [k for k, s in store_entries.items() if isinstance(s, dict) and str(s.get('appid') or '') in base_appids]
        for key in candidate_offer_keys:
            if not key or key in seen_offer_keys:
                continue
            seen_offer_keys.add(key)
            offer = offer_from_store(key, store_entries, history_entries, rate)
            if offer:
                offers.append(offer)
        offers.sort(key=lambda x: (x['current_price_rub'], -x['discount_percent'], x['title'].lower()))

        primary_offer = next((x for x in offers if x['key'] == main_key), None)
        if not primary_offer:
            primary_offer = {
                'key': main_key,
                'title': purchase.get('title'),
                'current_price_rub': purchase.get('current_price_rub_display'),
                'original_price_rub': purchase.get('original_price_rub_display'),
                'discount_percent': purchase.get('discount_percent'),
                'historical_minimum_rub': (row.get('history') or {}).get('minimum_rub_display'),
                'previously_free': bool((row.get('history') or {}).get('previously_free')),
                'sale_end_utc': purchase.get('sale_end_utc'),
                'web_url': f'https://store.steampowered.com/app/{base_appids[0]}/' if base_appids else None,
                'steam_url': f'steam://store/{base_appids[0]}' if base_appids else None,
            }
            offers.insert(0, primary_offer)

        meta = metadata.get(row.get('taste_subject_key')) or metadata.get(main_key) or {}
        evidence_source = taste_entry or taste_entries.get(row.get('taste_subject_key')) or {}
        positives = [evidence_text(x) for x in (evidence_source.get('positive_evidence') or [])]
        negatives = [evidence_text(x) for x in (evidence_source.get('negative_evidence') or [])]
        positives = [x for x in positives if x]
        negatives = [x for x in negatives if x]
        gameplay = []
        for item in evidence_source.get('positive_evidence') or []:
            if isinstance(item, dict):
                prop = item.get('candidate_property') or item.get('property') or item.get('game_property')
                if prop and str(prop) not in gameplay:
                    gameplay.append(str(prop))
        visible.append({
            'id': family_id,
            'family_type': row.get('family_type'),
            'title': purchase.get('title'),
            'base_appids': base_appids,
            'fit': fit,
            'decision': scenario.get('purchase_decision'),
            'priority_bucket': scenario.get('priority_bucket'),
            'wishlist': bool((row.get('context_only') or {}).get('wishlist')),
            'current_price_rub': primary_offer.get('current_price_rub'),
            'original_price_rub': primary_offer.get('original_price_rub'),
            'discount_percent': primary_offer.get('discount_percent'),
            'historical_minimum_rub': primary_offer.get('historical_minimum_rub'),
            'previously_free': primary_offer.get('previously_free'),
            'sale_end_utc': primary_offer.get('sale_end_utc'),
            'summary': meta.get('short_description'),
            'gameplay_points': gameplay[:3],
            'why_fit': positives[:2],
            'risks': negatives[:2],
            'offers': offers,
            'steam_url': primary_offer.get('steam_url') or (f'steam://store/{base_appids[0]}' if base_appids else None),
            'web_url': primary_offer.get('web_url') or (f'https://store.steampowered.com/app/{base_appids[0]}/' if base_appids else None),
        })

    media = appdetails(wanted_appids)
    for game in visible:
        screenshots = []
        header = None
        for appid in game['base_appids']:
            m = media.get(appid) or {}
            if not header:
                header = m.get('header_image')
            for url in m.get('screenshots') or []:
                if url not in screenshots:
                    screenshots.append(url)
                if len(screenshots) >= 5:
                    break
            if len(screenshots) >= 5:
                break
        game['screenshots'] = screenshots
        game['header_image'] = header
        if not game.get('summary'):
            for appid in game['base_appids']:
                desc = (media.get(appid) or {}).get('short_description')
                if desc:
                    game['summary'] = desc
                    break

    visible.sort(key=lambda x: (
        int(x.get('priority_bucket') or 99),
        -int(bool(x.get('wishlist'))),
        x.get('current_price_rub') if x.get('current_price_rub') is not None else 10**9,
        (x.get('title') or '').lower(),
    ))

    source_updated = payload.get('source_mailing_updated_at_utc')
    output = {
        'schema_version': 1,
        'status': 'complete',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'source_mailing_updated_at_utc': source_updated,
        'item_count': len(visible),
        'items': visible,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'visual items: {len(visible)}')


if __name__ == '__main__':
    main()
