import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import achievement_quality
import build_visual_feed_v2 as visual_builder

ROOT = Path('.')
PAYLOAD = ROOT / 'data/production/pre_ai/chatgpt_payload.json'
TASTE_QUEUE = ROOT / 'data/production/pre_ai/chatgpt_taste_queue.jsonl'
PURCHASE_CONTEXT = ROOT / 'data/production/pre_ai/chatgpt_purchase_context.jsonl'
HISTORY_SNAPSHOT = ROOT / 'data/production/pre_ai/history_snapshot.json'
TASTE_CACHE = ROOT / 'data/cache/taste_fit.json'
TASTE_PROJECTION = ROOT / 'data/production/pre_ai/taste_projection.json'
OUT = ROOT / 'data/production/visual/current.json'


HISTORY_QUALITY_ORDER = {
    'record': 0,
    'near_record': 1,
    'good_vs_history': 2,
    'previously_free': 3,
    'unverified': 4,
    'well_above_history': 5,
}

WINDOWS_ORDER = {
    'modern': 0,
    'unknown': 1,
    'older_but_plausible': 3,
    'legacy': 3,
}

RISK_ORDER = {
    'low': 0,
    'medium': 1,
    'high': 2,
    'unknown': 1,
}

GENERIC_RISK_PLACEHOLDERS = {
    'Явный конфликт с твоим профилем пока не подтверждён; этот риск нужно уточнить при более подробном разборе игры, а не выдумывать его.',
    'Риск пока не подготовлен.',
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding='utf-8').splitlines()
        if line.strip()
    ]


def cache_entries(obj):
    entries = obj.get('entries') if isinstance(obj, dict) else None
    if isinstance(entries, dict):
        return entries
    if isinstance(entries, list):
        return {str(x.get('key')): x for x in entries if isinstance(x, dict) and x.get('key')}
    return {}


def nonempty_line_count(path: Path):
    return sum(1 for line in path.read_text(encoding='utf-8').splitlines() if line.strip())


def git_sha(path: str):
    return subprocess.check_output(['git', 'rev-parse', f'HEAD:{path}'], text=True).strip()


def rub_from_kzt(value, rate):
    if value is None or not rate:
        return None
    try:
        return int(round(float(value) / float(rate)))
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def parse_utc(value):
    if not value:
        return None
    try:
        text = str(value).strip().replace('Z', '+00:00')
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def sale_expired(value, now):
    dt = parse_utc(value)
    return bool(dt and dt <= now)


def achievement_quality_rank(practical):
    has_achievements = practical.get('steam_achievements')
    if has_achievements is False:
        return 7
    if has_achievements is not True:
        return 6
    quality = practical.get('achievement_quality')
    if isinstance(quality, int) and 1 <= quality <= 5:
        return 5 - quality
    return 5


def achievement_quality_distribution(items):
    counts = Counter()
    for game in items or []:
        practical = game.get('practical') or {}
        quality = practical.get('achievement_quality')
        if quality in {0, 1, 2, 3, 4, 5}:
            counts[str(quality)] += 1
        else:
            counts['unknown'] += 1
    return {key: counts.get(key, 0) for key in ['5', '4', '3', '2', '1', '0', 'unknown']}


def history_values(key, history_entries, rate):
    row = history_entries.get(key) if isinstance(history_entries, dict) else None
    if not isinstance(row, dict):
        return None, False, 'unverified'
    quality = row.get('history_quality') or row.get('quality') or 'unverified'
    previously_free = quality == 'previously_free' or row.get('cache_status') == 'previously_free'
    raw_min = row.get('historical_min_kzt')
    hist = None if previously_free else rub_from_kzt(raw_min, rate)
    return hist, previously_free, quality


def enrich_history_and_remove_expired(ready, context_by_family, payload):
    history_entries = (load_json(HISTORY_SNAPSHOT).get('entries') or {}) if HISTORY_SNAPSHOT.exists() else {}
    rate = (payload.get('fx_binding') or {}).get('kzt_per_rub')
    now = datetime.now(timezone.utc)
    kept = []
    expired_family_count = 0

    for game in ready.get('items') or []:
        row = context_by_family.get(str(game.get('id'))) or {}
        purchase = row.get('purchase') or {}
        primary_key = purchase.get('key')

        active_offers = []
        for offer in game.get('offers') or []:
            if sale_expired(offer.get('sale_end_utc'), now):
                continue
            hist, previously_free, quality = history_values(offer.get('key'), history_entries, rate)
            offer['historical_minimum_rub'] = hist
            offer['previously_free'] = previously_free
            offer['history_quality'] = quality
            active_offers.append(offer)

        if not active_offers:
            expired_family_count += 1
            continue

        primary = next((x for x in active_offers if x.get('key') == primary_key), None)
        if primary is None:
            primary = min(
                active_offers,
                key=lambda x: (
                    int(x.get('current_price_rub') or 999999),
                    -int(x.get('discount_percent') or 0),
                    str(x.get('title') or '').casefold(),
                ),
            )

        active_offers = [primary] + [x for x in active_offers if x is not primary]
        game['offers'] = active_offers
        game['current_price_rub'] = primary.get('current_price_rub')
        game['original_price_rub'] = primary.get('original_price_rub')
        game['discount_percent'] = primary.get('discount_percent')
        game['historical_minimum_rub'] = primary.get('historical_minimum_rub')
        game['previously_free'] = bool(primary.get('previously_free'))
        game['history_quality'] = primary.get('history_quality') or 'unverified'
        game['sale_end_utc'] = primary.get('sale_end_utc')
        game['steam_url'] = primary.get('steam_url') or game.get('steam_url')
        game['web_url'] = primary.get('web_url') or game.get('web_url')
        kept.append(game)

    ready['items'] = kept
    ready['item_count'] = len(kept)
    ready['expired_family_count_removed_at_build'] = expired_family_count
    return ready


def add_risk(candidates, score, text):
    if not text or text in GENERIC_RISK_PLACEHOLDERS:
        return
    if any(existing_text == text for _, existing_text in candidates):
        return
    candidates.append((score, text))


def evidence_risk(ev):
    text = str(ev or '').lower()
    if 'backtrack' in text:
        return 4, 'Есть риск заметного бэктрекинга по уже знакомым местам — такое повторение у тебя уже вызывало усталость.'
    if any(k in text for k in ['repet', 'grind', 'loop']):
        return 4, 'Есть риск, что повторяющийся цикл или гринд начнёт доминировать над новыми ситуациями — для тебя это сильный минус.'
    if any(k in text for k in ['dialogue', 'reading', 'passive']):
        return 3, 'Заметная доля времени может уходить на диалоги, чтение или пассивные эпизоды; при нехватке активного геймплея интерес может просесть.'
    if any(k in text for k in ['hard', 'difficulty', 'punish']):
        return 2, 'Сложность может быть жёсткой; тебе она лучше подходит, когда ощущается обучаемой, а не просто наказующей.'
    if 'stealth' in text:
        return 2, 'Стелс может требовать ожидания и повторения после ошибок; если таких эпизодов много, темп может начать раздражать.'
    return None


def structural_risks(tags, description, release_date):
    text = (' '.join(tags or []) + ' ' + str(description or '')).lower()
    out = []
    if any(k in text for k in ['metroidvania', 'backtracking']):
        add_risk(out, 4, 'Структура может требовать возвращаться в уже знакомые зоны после получения новых возможностей; для тебя затяжной бэктрекинг — заметный риск.')
    if any(k in text for k in ['management', 'city builder', 'tycoon', 'farming', 'crafting', 'production chain']):
        add_risk(out, 3, 'Есть риск рутины из менеджмента, ресурсов или повторяющихся хозяйственных действий; если они станут основой игры, она может утомить.')
    if any(k in text for k in ['grand strategy', '4x', 'real-time strategy', 'rts', 'strategy']):
        add_risk(out, 2, 'Значительная часть интереса может быть в планировании и управлении вместо непосредственного контроля персонажа — это потенциально менее точное попадание в твой вкус.')
    if any(k in text for k in ['turn-based', 'turn based']):
        add_risk(out, 2, 'Пошаговый темп может ощущаться медленнее, чем игры с постоянным непосредственным управлением; это стоит учитывать при сравнении похожих вариантов.')
    if 'stealth' in text:
        add_risk(out, 2, 'Стелс может требовать ожидания и повторения после ошибок; если таких эпизодов много, темп может начать раздражать.')
    if any(k in text for k in ['sandbox', 'open world']) and not any(k in text for k in ['clear objective', 'mission', 'quest', 'mystery']):
        add_risk(out, 3, 'Есть риск недостатка направления: тебе открытый мир лучше заходит, когда постоянно понятны причины что-то исследовать или делать.')
    elif 'exploration' in text and not any(k in text for k in ['objective', 'mystery', 'investigation', 'quest']):
        add_risk(out, 2, 'Исследование может оказаться слишком самоцельным; тебе оно лучше заходит, когда есть понятная цель и плотные открытия.')
    if 'platform' in text:
        add_risk(out, 1, 'Если точный платформинг начнёт требовать многократного повторения одних и тех же участков, это может снизить удовольствие от движения.')
    if 'puzzle' in text:
        add_risk(out, 1, 'Если головоломки станут слишком однотипными или надолго остановят темп, сильная сторона игры может превратиться для тебя в минус.')
    if any(k in text for k in ['detective', 'investigation', 'mystery']):
        add_risk(out, 1, 'Расследование может включать много чтения и сопоставления улик; важно, чтобы оно не вытесняло активное взаимодействие с игрой.')
    if release_date:
        match = re.search(r'(19|20)\d{2}', str(release_date))
        if match and int(match.group(0)) <= 2011:
            add_risk(out, 2, 'Возраст игры может ощущаться в управлении, интерфейсе или удобстве сильнее, чем в современных проектах.')
    return out


def enrich_personal_risks(ready, context_by_family):
    taste_entries = cache_entries(load_json(TASTE_CACHE)) if TASTE_CACHE.exists() else {}
    projection_entries = (load_json(TASTE_PROJECTION).get('entries') or {}) if TASTE_PROJECTION.exists() else {}

    for game in ready.get('items') or []:
        row = context_by_family.get(str(game.get('id'))) or {}
        taste_key = row.get('taste_subject_key')
        taste_entry = taste_entries.get(taste_key) if isinstance(taste_entries, dict) else {}
        projection = projection_entries.get(taste_key) if isinstance(projection_entries, dict) else {}
        taste_entry = taste_entry if isinstance(taste_entry, dict) else {}
        projection = projection if isinstance(projection, dict) else {}

        candidates = []
        for risk in game.get('risks') or []:
            score = 1
            lower = str(risk).lower()
            if any(k in lower for k in ['бэктрекин', 'повторяющ', 'гринд']):
                score = 4
            elif any(k in lower for k in ['менеджмент', 'ресурс', 'диалог', 'пассив']):
                score = 3
            elif any(k in lower for k in ['сложност', 'возраст игры']):
                score = 2
            add_risk(candidates, score, risk)

        for ev in taste_entry.get('negative_evidence') or []:
            mapped = evidence_risk(ev)
            if mapped:
                add_risk(candidates, mapped[0], mapped[1])

        for score, text in structural_risks(
            projection.get('fit_tags') or [],
            projection.get('short_description') or '',
            projection.get('release_date'),
        ):
            add_risk(candidates, score, text)

        practical = game.get('practical') or {}
        if practical.get('windows_status') in {'legacy', 'older_but_plausible'}:
            add_risk(candidates, 5, 'Для нормального запуска на современной Windows могут понадобиться дополнительные действия; для тебя это сильный практический минус.')
        if practical.get('steam_achievements') is False:
            add_risk(candidates, 1, 'В Steam нет достижений — для тебя это минус по сравнению с похожей игрой с ачивками.')

        candidates.sort(key=lambda x: (-x[0], x[1]))
        if candidates:
            top = candidates[:2]
            max_score = top[0][0]
            level = 'high' if max_score >= 4 else ('medium' if max_score >= 2 else 'low')
            game['risks'] = [text for _, text in top]
            game['risk_penalty'] = sum(score for score, _ in top)
            game['risk_level'] = level
        else:
            game['risks'] = ['По доступным подтверждённым данным конкретный персональный минус не выявлен; лучше оставить честную неопределённость, чем приписывать игре несуществующий недостаток.']
            game['risk_penalty'] = 0
            game['risk_level'] = 'low'
    return ready


def current_production_readiness():
    payload = load_json(PAYLOAD)
    if payload.get('status') != 'complete':
        raise SystemExit('ChatGPT production payload is not complete')
    if payload.get('complete_family_partition') is not True:
        raise SystemExit('Production family partition is not complete')

    source_count = int(payload.get('source_family_count') or 0)
    ready_count = int(payload.get('ready_without_ai_count') or 0)
    excluded_count = int(payload.get('deterministically_excluded_without_ai_count') or 0)
    ai_queue_count = int(payload.get('ai_queue_count') or 0)
    purchase_context_count = int(payload.get('purchase_context_line_count') or 0)

    actual_queue_count = nonempty_line_count(TASTE_QUEUE)
    actual_purchase_context_count = nonempty_line_count(PURCHASE_CONTEXT)

    if ai_queue_count != actual_queue_count:
        raise SystemExit(f'AI queue count mismatch: payload={ai_queue_count} actual={actual_queue_count}')
    if purchase_context_count != actual_purchase_context_count:
        raise SystemExit('Purchase context count mismatch: ' f'payload={purchase_context_count} actual={actual_purchase_context_count}')
    if ready_count + excluded_count + ai_queue_count != source_count:
        raise SystemExit('Production partition arithmetic mismatch: ' f'ready={ready_count} excluded={excluded_count} ai={ai_queue_count} source={source_count}')

    source_key = payload.get('source_mailing_updated_at_utc')
    if not source_key:
        raise SystemExit('Production payload has no source_mailing_updated_at_utc')
    if ai_queue_count != 0:
        return None, payload
    if ready_count != purchase_context_count:
        raise SystemExit('Closed AI queue must leave one purchase-context row per ready family: ' f'ready={ready_count} purchase_context={purchase_context_count}')
    return source_key, payload


def existing_identity():
    if not OUT.exists():
        return None, None, None, None
    try:
        current = load_json(OUT)
        contract = current.get('production_contract') or {}
        return (
            current.get('source_mailing_updated_at_utc'),
            contract.get('visual_builder_blob_sha'),
            contract.get('daily_visual_builder_blob_sha'),
            contract.get('achievement_quality_builder_blob_sha'),
        )
    except Exception:
        return None, None, None, None


def apply_canonical_priority_order(ready, context_by_family):
    def key(game):
        row = context_by_family.get(str(game.get('id'))) or {}
        history = row.get('history') or {}
        history_quality = game.get('history_quality') or history.get('quality') or 'unverified'
        practical = game.get('practical') or {}
        windows_status = practical.get('windows_status') or 'unknown'
        return (
            int(game.get('priority_bucket') or 99),
            WINDOWS_ORDER.get(windows_status, 1),
            RISK_ORDER.get(game.get('risk_level') or 'unknown', 1),
            achievement_quality_rank(practical),
            -int(bool(game.get('wishlist'))),
            HISTORY_QUALITY_ORDER.get(history_quality, 99),
            -int(game.get('discount_percent') or 0),
            int(game.get('current_price_rub') or 999999),
            (game.get('title') or '').casefold(),
        )

    items = ready.get('items') or []
    items.sort(key=key)
    for index, game in enumerate(items, 1):
        game['priority_rank'] = index
    ready['items'] = items
    ready['item_count'] = len(items)
    return ready


def main():
    source_key, payload = current_production_readiness()
    if source_key is None:
        print(f'VISUAL_DAILY_BUILD=WAIT source={payload.get("source_mailing_updated_at_utc")} ai_queue={payload.get("ai_queue_count")}')
        return

    builder_sha = git_sha('scripts/build_visual_feed_v2.py')
    daily_builder_sha = git_sha('scripts/build_daily_visual_payload.py')
    achievement_builder_sha = git_sha('scripts/achievement_quality.py')
    current_source, current_builder, current_daily_builder, current_achievement_builder = existing_identity()
    force = os.environ.get('FORCE_VISUAL_BUILD') == '1'
    if (
        not force
        and current_source == source_key
        and current_builder == builder_sha
        and current_daily_builder == daily_builder_sha
        and current_achievement_builder == achievement_builder_sha
    ):
        print(f'VISUAL_DAILY_BUILD=SKIP source={source_key} builder={builder_sha} daily_builder={daily_builder_sha} achievement_builder={achievement_builder_sha}')
        return

    context_by_family = {
        str(row.get('family_id')): row
        for row in load_jsonl(PURCHASE_CONTEXT)
        if row.get('family_id')
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    visual_builder.OUT = OUT
    visual_builder.main()

    ready = load_json(OUT)
    ready['items'] = achievement_quality.enrich_visual_items(ready.get('items') or [])
    ready = enrich_history_and_remove_expired(ready, context_by_family, payload)
    ready = enrich_personal_risks(ready, context_by_family)
    distribution = achievement_quality_distribution(ready.get('items') or [])
    ready = apply_canonical_priority_order(ready, context_by_family)
    ready['production_contract'] = {
        'schema_version': 4,
        'mode': 'daily_precomputed_read_only_for_ui',
        'heavy_calculation_allowed_in_ui': False,
        'external_lookup_allowed_in_ui': False,
        'visual_builder_blob_sha': builder_sha,
        'daily_visual_builder_blob_sha': daily_builder_sha,
        'achievement_quality_builder_blob_sha': achievement_builder_sha,
        'source_chatgpt_payload_blob_sha': git_sha('data/production/pre_ai/chatgpt_payload.json'),
        'source_purchase_context_blob_sha': git_sha('data/production/pre_ai/chatgpt_purchase_context.jsonl'),
        'source_taste_queue_blob_sha': git_sha('data/production/pre_ai/chatgpt_taste_queue.jsonl'),
        'source_history_snapshot_blob_sha': git_sha('data/production/pre_ai/history_snapshot.json'),
        'source_family_count': payload.get('source_family_count'),
        'ready_family_count_before_expiry_filter': payload.get('ready_without_ai_count'),
        'visible_family_count': ready.get('item_count'),
        'expired_family_count_removed_at_build': ready.get('expired_family_count_removed_at_build'),
        'ai_queue_count': payload.get('ai_queue_count'),
        'complete_family_partition': payload.get('complete_family_partition'),
        'canonical_profile_blob_sha': (payload.get('profile_binding') or {}).get('canonical_profile_blob_sha'),
        'taste_model_version': (payload.get('profile_binding') or {}).get('taste_model_version'),
        'priority_factors': ['taste_deal_bucket', 'windows_compatibility', 'personal_risk_level', 'achievement_quality', 'wishlist', 'history_quality', 'discount', 'price'],
        'achievement_profile_scale': {
            '5': 'new_play_styles_or_challenges',
            '4': 'deeper_mechanic_use',
            '3': 'meaningful_optional_goals_or_secrets',
            '2': 'mostly_grind_or_collectathon',
            '1': 'mostly_automatic_story_progression',
        },
        'achievement_quality_distribution': distribution,
    }
    OUT.write_text(json.dumps(ready, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(
        f'VISUAL_DAILY_BUILD=BUILT source={source_key} items={ready.get("item_count")} '
        f'expired_removed={ready.get("expired_family_count_removed_at_build")} '
        f'achievement_quality_distribution={json.dumps(distribution, separators=(",", ":"))} '
        f'builder={builder_sha} daily_builder={daily_builder_sha} achievement_builder={achievement_builder_sha} force={force}'
    )


if __name__ == '__main__':
    main()
