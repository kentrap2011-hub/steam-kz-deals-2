import json
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from card_explanation_policy import positive_reasons
from semantic_runtime_completion import apply_visual_semantic_status
from russian_description_quality import classify_description
import commercial_reconsideration_bridge as commercial_bridge
from russian_description_translation_runtime import (
    load_translation_cache,
    resolve_description_for_appids as resolve_description_with_translation_cache,
)

ROOT = Path('.')
PURCHASE_CONTEXT = ROOT / 'data/production/pre_ai/chatgpt_purchase_context.jsonl'
STORE_SNAPSHOT = ROOT / 'data/production/pre_ai/store_snapshot.json'
CONTENT_METADATA = ROOT / 'data/production/pre_ai/content_metadata.json'
FAMILY_GRAPH = ROOT / 'data/production/pre_ai/family_graph.json'
HISTORY_SNAPSHOT = ROOT / 'data/production/pre_ai/history_snapshot.json'
TASTE_CACHE = ROOT / 'data/cache/taste_fit.json'
TASTE_OVERLAY = ROOT / 'data/cache/taste_fit.entry_overlay.json'
TASTE_PROJECTION = ROOT / 'data/production/pre_ai/taste_projection.json'
CHATGPT_PAYLOAD = ROOT / 'data/production/pre_ai/chatgpt_payload.json'
TRANSLATION_CACHE = ROOT / 'data/cache/russian_description_translations.json'
OUT = ROOT / 'web/data/current.json'


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def cache_entries(obj):
    entries = obj.get('entries') if isinstance(obj, dict) else None
    if isinstance(entries, dict):
        return entries
    if isinstance(entries, list):
        return {str(x.get('key')): x for x in entries if isinstance(x, dict) and x.get('key')}
    return {}


def effective_taste_entries():
    merged = dict(cache_entries(load_json(TASTE_CACHE)))
    merged.update(cache_entries(load_json(TASTE_OVERLAY)))
    return merged


def get_fit(row, taste_entries):
    if row.get('resolved_taste_fit') in {'strong', 'moderate'}:
        return row['resolved_taste_fit']
    entry = taste_entries.get(row.get('taste_subject_key'))
    if not isinstance(entry, dict) or str(entry.get('verdict')).upper() != 'INCLUDE':
        return None
    fit = entry.get('fit_level')
    return fit if fit in {'strong', 'moderate'} else None




def get_visual_eligibility(row, taste_entries):
    fit = get_fit(row, taste_entries)
    if fit in {'strong', 'moderate'}:
        scenario = row.get(f'deal_if_{fit}') or {}
        return fit, scenario, None
    taste_entry = taste_entries.get(row.get('taste_subject_key')) if isinstance(taste_entries, dict) else None
    validated = commercial_bridge.validate_visual_bridge(row, taste_entry if isinstance(taste_entry, dict) else {})
    if not validated:
        return None, None, None
    scenario = row.get('deal_if_moderate') or {}
    if scenario.get('disposition') != 'INCLUDE':
        return None, None, None
    return 'below_moderate', scenario, validated


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


def has_russian_text(value):
    return classify_description(value) == 'good_ru'


def strip_html(value):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', str(value or ''))).strip()


def storebrowse_media(appids):
    ids = sorted({str(x) for x in appids if str(x).isdigit()}, key=int)
    result = {}
    for start in range(0, len(ids), 100):
        batch = ids[start:start + 100]
        payload = {
            'ids': [{'appid': int(appid)} for appid in batch],
            'context': {'language': 'russian', 'country_code': 'KZ', 'steam_realm': 1},
            'data_request': {'include_basic_info': True, 'include_assets': True, 'include_screenshots': True},
        }
        url = 'https://api.steampowered.com/IStoreBrowseService/GetItems/v1/?input_json=' + urllib.parse.quote(json.dumps(payload, separators=(',', ':')))
        req = urllib.request.Request(url, headers={'User-Agent': 'steam-kz-deals-visual/3.0', 'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
        except Exception as exc:
            print(f'visual media batch failed: {type(exc).__name__}: {exc}')
            continue
        requested_ids = set(batch)
        for store_item in (data.get('response') or {}).get('store_items') or []:
            # StoreBrowse may resolve a requested storefront app to another internal
            # appid for its assets. `id` preserves the requested storefront identity;
            # `appid` is still the correct path component for the returned assets.
            request_id = str(store_item.get('id') or '').strip()
            asset_appid = str(store_item.get('appid') or request_id).strip()
            result_key = request_id if request_id in requested_ids else asset_appid
            if not result_key or not asset_appid:
                continue
            shots = []
            for shot in ((store_item.get('screenshots') or {}).get('all_ages_screenshots') or []):
                filename = str(shot.get('filename') or '').strip()
                if filename:
                    img = f'https://shared.fastly.steamstatic.com/store_item_assets/{filename}'
                    if img not in shots:
                        shots.append(img)
                if len(shots) >= 5:
                    break
            assets = store_item.get('assets') or {}
            header_file = str(assets.get('header') or '').strip()
            header = f'https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/{asset_appid}/{header_file}' if header_file else None
            desc = str((store_item.get('basic_info') or {}).get('short_description') or '').strip() or None
            desc_quality = classify_description(desc)
            result[result_key] = {
                'screenshots': shots,
                'header_image': header,
                'short_description_source': desc,
                'short_description_source_quality': desc_quality,
                'short_description_ru': desc if desc_quality == 'good_ru' else None,
            }
    return result


def load_content_metadata_by_appid():
    entries = load_json(CONTENT_METADATA).get('entries') or {}
    return {
        str(entry.get('steam_id')): entry
        for entry in entries.values()
        if isinstance(entry, dict)
        and entry.get('entity_kind') == 'app'
        and entry.get('steam_id')
    }


def resolve_description_for_appids(appids, media, content_metadata_by_appid, translation_cache):
    return resolve_description_with_translation_cache(
        appids,
        media,
        content_metadata_by_appid,
        translation_cache,
    )


def classify_windows(requirements):
    text = strip_html(requirements).lower()
    if not text:
        return 'unknown'
    if re.search(r'windows\s*(10|11)|win\s*(10|11)', text):
        return 'modern'
    if re.search(r'windows\s*(7|8|8\.1)|win\s*(7|8)', text):
        return 'older_but_plausible'
    if re.search(r'windows\s*(xp|vista|2000)|win\s*(xp|vista)', text):
        return 'legacy'
    return 'unknown'


def fetch_appdetails(appid):
    url = f'https://store.steampowered.com/api/appdetails?appids={appid}&cc=kz&l=russian'
    req = urllib.request.Request(url, headers={'User-Agent': 'steam-kz-deals-visual/3.0', 'Accept': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            payload = json.loads(response.read().decode('utf-8'))
        wrapper = payload.get(str(appid)) or {}
        data = wrapper.get('data') if wrapper.get('success') else None
        if not isinstance(data, dict):
            raise ValueError('missing appdetails')
        total = (data.get('achievements') or {}).get('total')
        categories = data.get('categories') or []
        achievements = int(total) > 0 if total is not None else any(int(c.get('id') or -1) == 22 or 'achievement' in str(c.get('description') or '').lower() for c in categories)
        reqs = data.get('pc_requirements') or {}
        if isinstance(reqs, list):
            reqs = {}
        recommendation = reqs.get('recommended') or reqs.get('minimum') or ''
        return str(appid), {
            'steam_achievements': achievements,
            'achievement_total': int(total) if total is not None else None,
            'windows_status': classify_windows(recommendation),
        }
    except Exception:
        return str(appid), {'steam_achievements': None, 'achievement_total': None, 'windows_status': 'unknown'}


def practical_facts(appids):
    ids = sorted({str(x) for x in appids if str(x).isdigit()}, key=int)
    result = {}
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = [pool.submit(fetch_appdetails, appid) for appid in ids]
        for future in as_completed(futures):
            appid, facts = future.result()
            result[appid] = facts
    return result


def reason_ru(evidence, tags, description):
    text = str(evidence or '').lower()
    if '2.5d platformer' in text and 'first-person' in text:
        return 'Игра чередует 2.5D-платформинг и эпизоды от первого лица — тебе обычно лучше заходят игры, которые меняют формат и игровые ситуации, а не повторяют один цикл.'
    if any(k in text for k in ['tactical', 'tactics', 'formation', 'strategic situation', 'different solutions', 'army composition', 'unit types']):
        return 'Игра регулярно ставит понятные тактические задачи, где можно выбирать подход и улучшать исполнение — это хорошо совпадает с твоей любовью к анализу ситуации и освоению игровых систем.'
    if any(k in text for k in ['traversal', 'movement', 'parkour', 'glide', 'levitation', 'climb', 'climbing', 'flying']):
        return 'Передвижение здесь — важная часть самого удовольствия от игры, а тебе особенно нравятся игры, где движение и контроль персонажа интересны сами по себе.'
    if any(k in text for k in ['progression', 'upgrade', 'abilities', 'new abilities', 'unlock']):
        return 'Есть заметное развитие возможностей персонажа с понятным игровым эффектом — это совпадает с твоей любовью к ясному и полезному прогрессу.'
    if any(k in text for k in ['investigation', 'detective', 'clue', 'interrogat']):
        return 'В центре есть конкретное расследование и понятный вопрос, на который нужно найти ответ — тебе такие загадки лучше заходят, когда направление поиска остаётся ясным.'
    if any(k in text for k in ['mystery', 'secret', 'unravel']):
        return 'В игре есть конкретная тайна, которая даёт исследованию и продвижению понятный смысл — это хорошо совпадает с твоей любовью к направленным загадкам.'
    if any(k in text for k in ['different', 'alternat', 'multiple', 'varied', 'changes of format', 'changes of situation']):
        return 'Игра регулярно меняет ситуации или способ взаимодействия, поэтому меньше риска застрять в одном повторяющемся цикле — это сильный плюс для твоего профиля.'
    if any(k in text for k in ['clear objective', 'clear goal', 'purpose', 'escape premise']):
        return 'У игровых задач есть понятная общая цель, поэтому исследование и отдельные механики не ощущаются бесцельными.'
    if any(k in text for k in ['choices', 'consequences', 'decision']):
        return 'Решения заметно влияют на происходящее, а тебе обычно интереснее игры, где действия меняют ситуацию, а не служат только декорацией.'

    joined = (' '.join(tags or []) + ' ' + str(description or '')).lower()
    if 'detective' in joined or 'investigation' in joined:
        return 'Основной игровой интерес связан с расследованием и поиском ответов — это хорошо совпадает с твоей любовью к направленным загадкам.'
    if 'mystery' in joined:
        return 'В игре есть конкретная тайна, которая направляет исследование и даёт ему понятную цель — это хорошо совпадает с твоим вкусом.'
    if 'choices matter' in joined:
        return 'Здесь важны решения и их последствия, поэтому ситуации могут развиваться по-разному, а не идти по полностью однообразному сценарию.'
    if any(k in joined for k in ['platform', 'parkour', 'climb', 'climbing']):
        return 'Заметная часть игры построена вокруг активного передвижения, а выразительное движение для тебя само по себе является плюсом.'
    if 'puzzle' in joined:
        return 'Головоломки дают конкретные задачи и понятные точки прогресса, что обычно лучше соответствует твоему вкусу, чем бесцельное исследование.'
    if 'exploration' in joined:
        return 'Исследование здесь связано с открытиями и продвижением, а тебе важнее плотность причин исследовать, чем просто большой мир.'
    if 'combat' in joined or 'action' in joined:
        return 'В игре заметную роль играет непосредственное управление и действие, а не только чтение или наблюдение — это соответствует твоему предпочтению активного геймплея.'
    return 'Игра прошла строгий вкусовой отбор, но конкретное русское объяснение этого совпадения ещё нужно доработать после утверждения оформления.'


def risk_from_negative(evidence):
    text = str(evidence or '').lower()
    if 'backtrack' in text:
        return 'Есть риск заметного бэктрекинга по уже знакомым местам — именно такое повторение у тебя уже вызывало усталость в других играх.'
    if any(k in text for k in ['repet', 'grind', 'loop']):
        return 'Есть риск, что повторяющийся цикл начнёт доминировать над новыми ситуациями, а однообразное повторение у тебя часто снижает интерес.'
    if any(k in text for k in ['dialogue', 'reading', 'passive']):
        return 'Заметная доля времени может уходить на диалоги или пассивные эпизоды; если активного геймплея окажется мало, интерес может просесть.'
    if any(k in text for k in ['hard', 'difficulty', 'punish']):
        return 'Сложность может быть жёсткой; тебе она подходит лучше, когда быстро становится понятной и ощущается как обучаемое мастерство.'
    return None


def derive_risks(negative_evidence, tags, description, release_date, practical):
    risks = []
    for ev in negative_evidence or []:
        r = risk_from_negative(ev)
        if r and r not in risks:
            risks.append(r)
    text = (' '.join(tags or []) + ' ' + str(description or '')).lower()
    if practical.get('windows_status') == 'legacy':
        risks.append('Steam указывает только старые версии Windows; на современной Windows может понадобиться дополнительная настройка или исправления.')
    if practical.get('steam_achievements') is False:
        risks.append('В Steam нет достижений — для тебя это дополнительный минус по сравнению с похожей игрой с ачивками.')
    if not risks and any(k in text for k in ['roguelike', 'rogue-lite', 'roguelite', 'procedural', 'endless']):
        risks.append('Структура опирается на повторные забеги или процедурное повторение, а однообразные повторы для тебя часто становятся минусом.')
    if not risks and any(k in text for k in ['dialogue-focused', 'visual novel', 'point & click', 'point-and-click']):
        risks.append('Здесь может быть много диалогов и сравнительно пассивных эпизодов; если активного геймплея окажется мало, интерес может просесть.')
    if not risks and any(k in text for k in ['craft', 'farming', 'management', 'production chains', 'survival simulation']):
        risks.append('Есть заметная доля менеджмента или сбора ресурсов; если рутина начнёт доминировать над новыми ситуациями, игра может утомить.')
    if not risks and ('sandbox' in text or ('open world' in text and not any(k in text for k in ['mystery', 'quest', 'mission', 'objective']))):
        risks.append('Есть риск недостатка направления: тебе открытый мир лучше заходит, когда в нём постоянно понятны причины что-то исследовать или делать.')
    if not risks and release_date:
        m = re.search(r'(19|20)\d{2}', str(release_date))
        if m and int(m.group(0)) <= 2011:
            risks.append('Возраст игры может ощущаться в управлении и интерфейсе сильнее, чем в современных проектах.')
    if not risks:
        risks.append('Явный конфликт с твоим профилем пока не подтверждён; этот риск нужно уточнить при более подробном разборе игры, а не выдумывать его.')
    return risks[:2]


def windows_rank(status):
    return 2 if status == 'legacy' else 0


def achievements_rank(value):
    return 0 if value is True else (1 if value is None else 2)


def main():
    rows = load_jsonl(PURCHASE_CONTEXT)
    store_entries = load_json(STORE_SNAPSHOT).get('entries') or {}
    content_metadata_by_appid = load_content_metadata_by_appid()
    family_obj = load_json(FAMILY_GRAPH)
    families = family_obj.get('families') or []
    family_by_id = {x.get('family_id'): x for x in families if isinstance(x, dict)}
    history_entries = load_json(HISTORY_SNAPSHOT).get('entries') or {}
    taste_entries = effective_taste_entries()
    projection_entries = load_json(TASTE_PROJECTION).get('entries') or {}
    payload = load_json(CHATGPT_PAYLOAD)
    translation_cache = load_translation_cache(TRANSLATION_CACHE)
    rate = (payload.get('fx_binding') or {}).get('kzt_per_rub')

    family_base_map = {}
    for fam in families:
        if isinstance(fam, dict):
            for appid in fam.get('base_appids') or []:
                family_base_map.setdefault(str(appid), []).append(fam)

    prepared = []
    wanted_appids = set()
    for row in rows:
        fit, scenario, eligibility_bridge = get_visual_eligibility(row, taste_entries)
        if fit not in {'strong', 'moderate', 'below_moderate'} or not isinstance(scenario, dict):
            continue
        if scenario.get('disposition') != 'INCLUDE':
            continue
        purchase = row.get('purchase') or {}
        family_id = row.get('family_id')
        fam = family_by_id.get(family_id) or {}
        base_appids = [str(x) for x in ((row.get('semantic_condition') or {}).get('base_appids') or fam.get('base_appids') or [])]
        wanted_appids.update(x for x in base_appids if x.isdigit())
        prepared.append((row, fit, scenario, purchase, family_id, fam, base_appids, eligibility_bridge))

    media = storebrowse_media(wanted_appids)
    facts = practical_facts(wanted_appids)
    visible = []

    for row, fit, scenario, purchase, family_id, fam, base_appids, eligibility_bridge in prepared:
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

        screenshots, header = [], None
        for appid in base_appids:
            m = media.get(appid) or {}
            header = header or m.get('header_image')
            for url in m.get('screenshots') or []:
                if url not in screenshots:
                    screenshots.append(url)
                if len(screenshots) >= 5:
                    break

        description_resolution = resolve_description_for_appids(
            base_appids,
            media,
            content_metadata_by_appid,
            translation_cache,
        )

        taste_key = row.get('taste_subject_key')
        taste_entry = taste_entries.get(taste_key) if isinstance(taste_entries, dict) else {}
        projection = projection_entries.get(taste_key) if isinstance(projection_entries, dict) else {}
        taste_entry = taste_entry if isinstance(taste_entry, dict) else {}
        projection = projection if isinstance(projection, dict) else {}
        tags = projection.get('fit_tags') or []
        taste_description = projection.get('short_description') or ''
        reasons, why_fit_provenance = positive_reasons(taste_entry.get('positive_evidence') or [])

        base_facts = [facts.get(appid) or {} for appid in base_appids]
        statuses = [x.get('windows_status') for x in base_facts]
        windows_status = 'legacy' if 'legacy' in statuses else ('modern' if 'modern' in statuses else ('older_but_plausible' if 'older_but_plausible' in statuses else 'unknown'))
        achievement_values = [x.get('steam_achievements') for x in base_facts if x.get('steam_achievements') is not None]
        steam_achievements = True if True in achievement_values else (False if achievement_values and all(x is False for x in achievement_values) else None)
        achievement_total = next((x.get('achievement_total') for x in base_facts if x.get('achievement_total') is not None), None)
        practical = {'windows_status': windows_status, 'steam_achievements': steam_achievements, 'achievement_total': achievement_total}
        risks = derive_risks(taste_entry.get('negative_evidence') or [], tags, taste_description, projection.get('release_date'), practical)

        final_decision, final_bucket = commercial_bridge.effective_purchase_fields(eligibility_bridge, scenario)
        visible.append({
            'id': family_id,
            'family_type': row.get('family_type'),
            'title': purchase.get('title'),
            'base_appids': base_appids,
            'fit': fit,
            'taste_factors': taste_entry.get('taste_factors'),
            'decision': final_decision,
            'priority_bucket': final_bucket,
            'fit_evidence_state': (eligibility_bridge or {}).get('fit_evidence_state') if eligibility_bridge else None,
            'fit_evidence_confidence': (eligibility_bridge or {}).get('fit_evidence_confidence') if eligibility_bridge else None,
            'eligibility_override': (eligibility_bridge or {}).get('kind') if eligibility_bridge else None,
            'commercial_eligibility_bridge': eligibility_bridge,
            'wishlist': bool((row.get('context_only') or {}).get('wishlist')),
            'current_price_rub': primary_offer.get('current_price_rub'),
            'original_price_rub': primary_offer.get('original_price_rub'),
            'discount_percent': primary_offer.get('discount_percent'),
            'historical_minimum_rub': primary_offer.get('historical_minimum_rub'),
            'previously_free': primary_offer.get('previously_free'),
            'sale_end_utc': primary_offer.get('sale_end_utc'),
            'summary': description_resolution.get('summary'),
            'description_status': description_resolution.get('description_status'),
            'description_source_locale': description_resolution.get('description_source_locale'),
            'description_source_quality': description_resolution.get('description_source_quality'),
            'description_source_appid': description_resolution.get('description_source_appid'),
            'description_source_path': description_resolution.get('description_source_path'),
            'description_source_text': description_resolution.get('description_source_text'),
            'description_translation_request_id': description_resolution.get('description_translation_request_id'),
            'description_translation_source_text_sha256': description_resolution.get('description_translation_source_text_sha256'),
            'description_translation_source_version': description_resolution.get('description_translation_source_version'),
            'gameplay_points': [],
            'why_fit': reasons[:2],
            'why_fit_status': {
                'has_described_fit': bool(reasons),
                'grounding': 'grounded' if reasons else 'insufficient_evidence',
            },
            'why_fit_provenance': why_fit_provenance[:2],
            'risks': risks,
            'practical': practical,
            'offers': offers,
            'screenshots': screenshots,
            'header_image': header,
            'steam_url': primary_offer.get('steam_url') or (f'steam://store/{base_appids[0]}' if base_appids else None),
            'web_url': primary_offer.get('web_url') or (f'https://store.steampowered.com/app/{base_appids[0]}/' if base_appids else None),
        })

    visible.sort(key=lambda x: (
        int(x.get('priority_bucket') or 99),
        windows_rank((x.get('practical') or {}).get('windows_status')),
        achievements_rank((x.get('practical') or {}).get('steam_achievements')),
        -int(bool(x.get('wishlist'))),
        -int(x.get('discount_percent') or 0),
        int(x.get('current_price_rub') or 999999),
        (x.get('title') or '').casefold(),
    ))
    for index, game in enumerate(visible, 1):
        game['priority_rank'] = index

    output = {
        'schema_version': 3,
        'status': 'complete',
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'source_mailing_updated_at_utc': payload.get('source_mailing_updated_at_utc'),
        'item_count': len(visible),
        'items': visible,
    }
    apply_visual_semantic_status(output, payload)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'visual items: {len(visible)}; media items: {len(media)}; practical facts: {len(facts)}')


if __name__ == '__main__':
    main()
