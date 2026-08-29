import base64
import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path('.')
OUT = ROOT / 'data/production/visual/current.json'
TASTE_CACHE = ROOT / 'data/cache/taste_fit.json'
TASTE_OVERLAY = ROOT / 'data/cache/taste_fit.entry_overlay.json'
TASTE_PROJECTION = ROOT / 'data/production/pre_ai/taste_projection.json'
PURCHASE_CONTEXT = ROOT / 'data/production/pre_ai/chatgpt_purchase_context.jsonl'
PAYLOAD = ROOT / 'data/production/pre_ai/chatgpt_payload.json'

HISTORY_QUALITY_ORDER = {
    'record': 0,
    'near_record': 1,
    'good_vs_history': 2,
    'previously_free': 3,
    'unverified': 4,
    'well_above_history': 5,
}

RISK_LEVEL_ORDER = {'low': 0, 'medium': 1, 'high': 2, 'unknown': 1}
DIRECT_EVIDENCE_ORDER = {'positive': 0, 'mixed': 1, 'none': 2, 'negative': 3}
GENERIC_WHY_FIT = 'Игра прошла строгий вкусовой отбор, но конкретное русское объяснение этого совпадения ещё нужно доработать после утверждения оформления.'


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_jsonl(path: Path):
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
    if TASTE_OVERLAY.exists():
        merged.update(cache_entries(load_json(TASTE_OVERLAY)))
    return merged


def git_sha(path: str):
    return subprocess.check_output(['git', 'rev-parse', f'HEAD:{path}'], text=True).strip()


def normalize_title(value):
    text = str(value or '').casefold()
    text = text.replace('™', ' ').replace('®', ' ').replace('©', ' ')
    text = re.sub(r'\([^)]*\b(?:19|20)\d{2}\b[^)]*\)', ' ', text)
    suffixes = [
        'special edition', 'definitive edition', 'ultimate edition', 'complete edition',
        'game of the year edition', 'goty edition', 'steam edition', 'remastered',
        'remaster', 'hd collection', 'hd',
    ]
    changed = True
    while changed:
        changed = False
        for suffix in suffixes:
            pattern = rf'(?:\s*[-:–—]\s*|\s+){re.escape(suffix)}\s*$'
            new = re.sub(pattern, '', text).strip()
            if new != text:
                text = new
                changed = True
    text = re.sub(r'[^a-zа-яё0-9]+', ' ', text, flags=re.I)
    return re.sub(r'\s+', ' ', text).strip()


def fetch_bound_profile(payload):
    binding = payload.get('profile_binding') or {}
    blob_sha = binding.get('canonical_profile_blob_sha')
    if not blob_sha:
        return None, 'missing_blob_sha'
    url = f'https://api.github.com/repos/kentrap2011-hub/stopgame-ratings-data/git/blobs/{blob_sha}'
    headers = {
        'User-Agent': 'steam-kz-ranking-refiner/1.0',
        'Accept': 'application/vnd.github+json',
    }
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            wrapper = json.loads(response.read().decode('utf-8'))
        if wrapper.get('encoding') != 'base64' or not wrapper.get('content'):
            return None, 'unsupported_blob_encoding'
        raw = base64.b64decode(wrapper['content']).decode('utf-8')
        return json.loads(raw), None
    except Exception as exc:
        return None, type(exc).__name__


def direct_profile_index(profile):
    result = {}
    if not isinstance(profile, dict):
        return result
    for card in profile.get('stopgame_cards') or []:
        if not isinstance(card, dict):
            continue
        key = normalize_title(card.get('title'))
        rating = card.get('rating')
        if not key or not isinstance(rating, (int, float)):
            continue
        result[key] = card
    return result


def direct_evidence(game, direct_index):
    key = normalize_title(game.get('title'))
    card = direct_index.get(key)
    if not card:
        return None
    rating = float(card.get('rating'))
    if rating >= 4.0:
        level = 'positive'
    elif rating >= 3.5:
        level = 'mixed'
    else:
        level = 'negative'
    return {
        'rating': rating,
        'level': level,
        'confidence': card.get('discussion_confidence'),
        'why_this_rating': card.get('why_this_rating'),
    }


def add_risk(risks, code, score, text, source='derived'):
    if not code or not text:
        return
    current = risks.get(code)
    row = {'code': code, 'score': int(score), 'text': text, 'source': source}
    if current is None or row['score'] > current['score']:
        risks[code] = row


def map_negative_evidence(value, risks):
    text = str(value or '').casefold()
    if not text:
        return
    if any(k in text for k in ['same thing', 'same conditions', 'unchanged', 'repet', 'grind', 'однообраз', 'повтор']):
        add_risk(
            risks,
            'unchanged_repetition',
            4,
            'Есть риск повторения одних и тех же действий без достаточного изменения условий или развития — именно такой повтор для тебя быстро становится утомительным.',
            'taste_negative_evidence',
        )
    if any(k in text for k in ['dialogue', 'reading', 'passive', 'low active', 'много чтения', 'пассив']):
        add_risk(
            risks,
            'low_active_gameplay',
            3,
            'Заметная доля времени может уходить на чтение, диалоги или пассивные эпизоды; если активного взаимодействия мало, интерес может просесть.',
            'taste_negative_evidence',
        )
    if any(k in text for k in ['direction', 'unclear', 'what to do', 'where to go', 'бесцель', 'непонятно куда', 'непонятно что делать']):
        add_risk(
            risks,
            'directionlessness',
            4,
            'Есть риск недостатка ясного направления: тебе заметно хуже заходят игры, когда непонятно, куда идти, что делать и ради чего развиваться.',
            'taste_negative_evidence',
        )
    if any(k in text for k in ['management', 'routine', 'resource', 'craft', 'рутин', 'менеджмент', 'ресурс']):
        add_risk(
            risks,
            'management_routine',
            3,
            'Есть риск, что управление ресурсами или повторяющаяся хозяйственная рутина займут слишком большую часть игры.',
            'taste_negative_evidence',
        )
    if any(k in text for k in ['punish', 'difficulty', 'hard', 'сложност', 'наказ']):
        add_risk(
            risks,
            'difficulty_punishment',
            2,
            'Сложность может требовать много повторных попыток; для тебя это хорошо работает только когда ошибки понятны, а освоение ощущается содержательным.',
            'taste_negative_evidence',
        )
    if 'stealth' in text or 'стелс' in text:
        add_risk(
            risks,
            'stealth_restart_pressure',
            2,
            'Стелс может провоцировать перезапуск после неидеального прохождения; это становится минусом, если игра заставляет долго планировать и повторять эпизоды.',
            'taste_negative_evidence',
        )
    # Deliberately no plain backtracking penalty. Reused locations are only a
    # problem when the evidence also indicates unchanged/repetitive play.


def structural_risks(projection, practical):
    risks = {}
    tags = [str(x).casefold() for x in projection.get('fit_tags') or []]
    desc = str(projection.get('short_description') or '').casefold()
    joined = ' '.join(tags) + ' ' + desc

    explicit_management = any(
        phrase in joined
        for phrase in [
            'city builder', 'management sim', 'management simulation', 'production chain',
            'manage your staff', 'manage a settlement', 'manage survivors', 'manage your crew',
            'manage your hospital', 'manage resources', 'build and manage', 'tycoon',
        ]
    )
    if explicit_management:
        add_risk(
            risks,
            'management_routine',
            3,
            'В игре явно заметен слой управления и рутины; если он начинает доминировать над новыми игровыми ситуациями, это для тебя минус.',
        )

    has_open_world = 'open world' in tags or 'open-world' in desc or 'open world' in desc
    has_clear_vector = any(
        phrase in joined
        for phrase in [
            'mystery', 'investigat', 'detective', 'mission', 'quest', 'objective', 'escape',
            'rescue', 'save the', 'find ', 'unravel', 'solve ', 'campaign', 'story',
        ]
    )
    if has_open_world and not has_clear_vector:
        add_risk(
            risks,
            'directionlessness',
            3,
            'Открытая структура может давать слишком мало направления; тебе такие миры лучше заходят, когда постоянно понятно, зачем исследовать следующую точку.',
        )
    elif ('exploration' in tags or 'explore' in desc) and not has_clear_vector:
        add_risk(
            risks,
            'exploration_direction',
            2,
            'Исследование может оказаться слишком самоцельным; тебе оно лучше подходит, когда есть ясный вектор и плотные открытия.',
        )

    if 'platform' in joined:
        add_risk(
            risks,
            'platform_repetition',
            1,
            'Если сложные участки платформинга начнут требовать слишком много одинаковых повторов, это может утомлять.',
        )
    if 'puzzle' in joined:
        add_risk(
            risks,
            'puzzle_pacing',
            1,
            'Если головоломки станут однотипными или надолго остановят темп, сильная сторона игры может превратиться в минус.',
        )
    if any(x in joined for x in ['detective', 'investigation', 'interrogation', 'clue', 'evidence']):
        add_risk(
            risks,
            'reading_investigation',
            1,
            'Расследование может включать много чтения и сопоставления улик; важно, чтобы это не вытесняло активное взаимодействие с игрой.',
        )

    release = str(projection.get('release_date') or '')
    match = re.search(r'(19|20)\d{2}', release)
    if match and int(match.group(0)) <= 2011:
        add_risk(
            risks,
            'old_design_friction',
            1,
            'Возраст игры может ощущаться в управлении или интерфейсе, хотя сам по себе старый год выпуска не делает игру плохой.',
        )

    friction = practical.get('modern_windows_friction')
    if friction == 'known_fix_required':
        add_risk(
            risks,
            'windows_friction',
            4,
            'Для запуска на современной Windows подтверждённо нужны дополнительные действия — это серьёзный практический минус.',
            'confirmed_practical',
        )
    elif friction == 'serious_problem':
        add_risk(
            risks,
            'windows_friction',
            5,
            'На современной Windows подтверждены серьёзные проблемы с запуском или стабильностью — это сильный практический минус.',
            'confirmed_practical',
        )

    if practical.get('steam_achievements') is False:
        add_risk(
            risks,
            'no_steam_achievements',
            1,
            'В Steam нет достижений — для тебя это небольшой минус по сравнению с похожей игрой с интересным набором ачивок.',
            'confirmed_practical',
        )

    return risks


def normalize_windows(practical):
    old = practical.get('windows_status')
    existing_friction = practical.get('modern_windows_friction')
    if old in {'legacy', 'older_but_plausible'}:
        practical['legacy_windows_requirement_label'] = old
        practical['windows_status'] = 'unknown'
        practical['modern_windows_friction'] = existing_friction or 'unknown'
    elif old == 'modern':
        practical['modern_windows_friction'] = existing_friction or 'likely_none'
    else:
        practical['modern_windows_friction'] = existing_friction or 'unknown'
    return practical


def risk_summary(risks):
    rows = sorted(risks.values(), key=lambda x: (-x['score'], x['code']))
    if not rows:
        return (
            ['По доступным подтверждённым данным конкретный персональный минус не выявлен; отсутствие найденного риска не считается доказательством идеального совпадения.'],
            [],
            0,
            'low',
        )
    top = rows[:2]
    max_score = top[0]['score']
    level = 'high' if max_score >= 4 else ('medium' if max_score >= 2 else 'low')
    return [x['text'] for x in top], [x['code'] for x in rows], sum(x['score'] for x in rows), level


def direct_fit_cap(source_fit, evidence):
    if not evidence:
        return source_fit, None
    rating = evidence['rating']
    if rating >= 4.0:
        return 'strong', 'direct_user_rating_4_or_higher'
    if rating >= 3.5:
        return 'moderate', 'direct_user_rating_3_5_mixed'
    if source_fit == 'strong':
        return 'moderate', 'direct_user_rating_below_3_5_caps_strong'
    return source_fit, 'direct_user_rating_below_3_5'


def serious_taste_risk(risks):
    serious_codes = {'unchanged_repetition', 'directionlessness'}
    return any(code in serious_codes and row.get('score', 0) >= 4 for code, row in risks.items())


def apply_fit_adjustment(game, evidence, risks, taste_entry, projection):
    source_fit = game.get('fit') or 'moderate'
    game['source_fit'] = source_fit
    fit, reason = direct_fit_cap(source_fit, evidence)

    direct_override = bool(evidence)
    if not direct_override and fit == 'strong' and serious_taste_risk(risks):
        fit = 'moderate'
        reason = 'serious_confirmed_personal_risk_caps_strong'

    cache_has_grounding = isinstance(taste_entry, dict) and bool(taste_entry)
    projection_cached = str(projection.get('status') or '') == 'cache_hit'
    why = game.get('why_fit') or []
    generic_only = bool(why) and all(str(x).strip() == GENERIC_WHY_FIT for x in why)
    if generic_only and not cache_has_grounding and not projection_cached:
        game['taste_confidence'] = 'low'
        if fit == 'strong':
            fit = 'moderate'
            reason = reason or 'insufficient_grounding_for_strong'
    elif evidence:
        game['taste_confidence'] = 'direct_user_evidence'
    elif cache_has_grounding or projection_cached:
        game['taste_confidence'] = 'derived_grounded'
    else:
        game['taste_confidence'] = 'unknown'

    game['fit'] = fit
    game['fit_adjustment_reason'] = reason
    return game


def apply_commercial_branch(game, context):
    fit = game.get('fit')
    branch = context.get('deal_if_strong') if fit == 'strong' else context.get('deal_if_moderate')
    if not isinstance(branch, dict):
        game['fit_adjustment_commercial_branch_missing'] = True
        return True
    if branch.get('disposition') != 'INCLUDE':
        game['refiner_exclusion_reason'] = branch.get('exclusion_reason_code') or branch.get('price_gate_reason') or 'commercial_branch_exclude'
        return False
    if branch.get('purchase_decision'):
        game['decision'] = branch.get('purchase_decision')
    if branch.get('priority_bucket') is not None:
        game['priority_bucket'] = int(branch.get('priority_bucket'))
    return True


def extract_duration_hours(projection, game):
    sources = [
        str(projection.get('short_description') or ''),
        str(game.get('summary') or ''),
    ]
    patterns = [
        r'(?:playtime|gameplay|length|time)[^\d]{0,15}(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours)\b',
        r'(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours|ч\.?|час(?:а|ов)?)\b',
        r'(?:playtime|gameplay|length|time)[^\d]{0,15}(\d+(?:\.\d+)?)\s*(?:h|hr|hrs|hour|hours)\b',
        r'(?:время прохождения)[^\d]{0,15}(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)\s*(?:ч\.?|час(?:а|ов)?)\b',
    ]
    for source in sources:
        for pattern in patterns:
            match = re.search(pattern, source, flags=re.I)
            if not match:
                continue
            values = [float(x) for x in match.groups() if x is not None]
            if not values:
                continue
            hours = sum(values) / len(values)
            if 0.5 <= hours <= 500:
                return round(hours, 1), 'explicit_description'
    return None, None


def duration_band(hours):
    if hours is None:
        return 'unknown', 0
    if 10 <= hours <= 40:
        return 'preferred_medium', 0
    if 5 <= hours < 10 or 40 < hours <= 60:
        return 'slightly_short_or_long', 1
    if hours < 5 or 60 < hours <= 100:
        return 'very_short_or_long', 2
    return 'extreme_length', 3


def achievement_rank(practical):
    if practical.get('steam_achievements') is False:
        return 7
    if practical.get('steam_achievements') is not True:
        return 6
    quality = practical.get('achievement_quality')
    if isinstance(quality, int) and 1 <= quality <= 5:
        return 5 - quality
    return 5


def direct_rank(game):
    evidence = game.get('direct_user_evidence') or {}
    return DIRECT_EVIDENCE_ORDER.get(evidence.get('level') or 'none', 2)


def taste_sort_key(game):
    fit_order = 0 if game.get('fit') == 'strong' else 1
    return (
        fit_order,
        direct_rank(game),
        RISK_LEVEL_ORDER.get(game.get('risk_level') or 'unknown', 1),
        achievement_rank(game.get('practical') or {}),
        int(game.get('duration_tiebreak_penalty') or 0),
        str(game.get('title') or '').casefold(),
    )


def main_sort_key(game):
    return (
        int(game.get('priority_bucket') or 99),
        direct_rank(game),
        RISK_LEVEL_ORDER.get(game.get('risk_level') or 'unknown', 1),
        achievement_rank(game.get('practical') or {}),
        -int(bool(game.get('wishlist'))),
        HISTORY_QUALITY_ORDER.get(game.get('history_quality') or 'unverified', 99),
        -int(game.get('discount_percent') or 0),
        int(game.get('current_price_rub') or 999999),
        int(game.get('duration_tiebreak_penalty') or 0),
        str(game.get('title') or '').casefold(),
    )


def main():
    if not OUT.exists():
        raise SystemExit('Visual payload does not exist')

    ready = load_json(OUT)
    payload = load_json(PAYLOAD)
    taste_entries = effective_taste_entries()
    projections = (load_json(TASTE_PROJECTION).get('entries') or {}) if TASTE_PROJECTION.exists() else {}
    contexts = {str(x.get('family_id')): x for x in load_jsonl(PURCHASE_CONTEXT) if x.get('family_id')}

    profile, profile_error = fetch_bound_profile(payload)
    direct_index = direct_profile_index(profile)

    fit_changes = 0
    removed = 0
    windows_labels_neutralized = 0
    refined = []

    for game in ready.get('items') or []:
        family_id = str(game.get('id') or '')
        context = contexts.get(family_id) or {}
        taste_key = context.get('taste_subject_key')
        taste_entry = taste_entries.get(taste_key) if taste_key else {}
        projection = projections.get(taste_key) if taste_key else {}
        taste_entry = taste_entry if isinstance(taste_entry, dict) else {}
        projection = projection if isinstance(projection, dict) else {}

        practical = game.setdefault('practical', {})
        old_windows = practical.get('windows_status')
        normalize_windows(practical)
        if old_windows in {'legacy', 'older_but_plausible'}:
            windows_labels_neutralized += 1

        risks = {}
        for ev in taste_entry.get('negative_evidence') or []:
            map_negative_evidence(ev, risks)
        for code, row in structural_risks(projection, practical).items():
            add_risk(risks, code, row['score'], row['text'], row.get('source') or 'derived')

        risk_texts, risk_codes, risk_penalty, risk_level = risk_summary(risks)
        game['risks'] = risk_texts
        game['risk_codes'] = risk_codes
        game['risk_penalty'] = risk_penalty
        game['risk_level'] = risk_level

        evidence = direct_evidence(game, direct_index)
        game['direct_user_evidence'] = evidence or {'level': 'none'}
        old_fit = game.get('fit')
        apply_fit_adjustment(game, evidence, risks, taste_entry, projection)
        if game.get('fit') != old_fit:
            fit_changes += 1

        hours, duration_source = extract_duration_hours(projection, game)
        band, penalty = duration_band(hours)
        game['estimated_duration_hours'] = hours
        game['duration_estimate_source'] = duration_source
        game['duration_preference_band'] = band
        game['duration_tiebreak_penalty'] = penalty

        if not apply_commercial_branch(game, context):
            removed += 1
            continue
        refined.append(game)

    taste_sorted = sorted(refined, key=taste_sort_key)
    for index, game in enumerate(taste_sorted, 1):
        game['taste_rank'] = index

    refined.sort(key=main_sort_key)
    for index, game in enumerate(refined, 1):
        game['priority_rank'] = index

    ready['items'] = refined
    ready['item_count'] = len(refined)
    contract = ready.setdefault('production_contract', {})
    contract['schema_version'] = 5
    contract['ranking_refiner_blob_sha'] = git_sha('scripts/refine_visual_ranking.py')
    contract['priority_factors'] = [
        'taste_deal_bucket',
        'direct_user_evidence',
        'personal_risk_level',
        'achievement_quality',
        'wishlist',
        'history_quality',
        'discount',
        'price',
        'duration_tiebreak',
    ]
    contract['windows_rule'] = 'old_requirement_labels_do_not_reduce_rank; only confirmed modern Windows friction may penalize'
    contract['backtracking_rule'] = 'location reuse itself is neutral; penalize unchanged repetition without new gameplay value'
    contract['duration_rule'] = 'very weak late tiebreak only; medium duration preferred over very short or very long games when otherwise equal'
    contract['fit_adjustment_rule'] = 'direct user evidence overrides inference; serious confirmed personal conflicts can cap strong to moderate'
    contract['taste_evidence_merge_rule'] = 'legacy base plus incremental overlay; overlay exact key wins'
    contract['refinement_stats'] = {
        'fit_changes': fit_changes,
        'removed_after_fit_change_and_commercial_recheck': removed,
        'legacy_windows_labels_neutralized': windows_labels_neutralized,
        'direct_profile_loaded': profile is not None,
        'direct_profile_error': profile_error,
    }
    contract['visible_family_count'] = len(refined)

    OUT.write_text(json.dumps(ready, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(
        'VISUAL_RANKING_REFINED '
        f'items={len(refined)} fit_changes={fit_changes} removed={removed} '
        f'windows_labels_neutralized={windows_labels_neutralized} profile_loaded={profile is not None}'
    )


if __name__ == '__main__':
    main()
