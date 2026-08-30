import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path('.')
POLICY = ROOT / 'config/final_ranking_policy.json'
PRODUCTION_TIMEZONE = 'Europe/Samara'

HISTORY_QUALITY_ORDER = {
    'record': 0,
    'near_record': 1,
    'good_vs_history': 2,
    'previously_free': 3,
    'unverified': 4,
    'well_above_history': 5,
}

# Only serious/high personal risks belong in this early layer. Medium/low heuristics
# remain descriptive context and must not outrank wishlist/commercial value by themselves.
RISK_LEVEL_ORDER = {'low': 0, 'unknown': 0, 'medium': 0, 'high': 2}
WINDOWS_FRICTION_ORDER = {
    'likely_none': 0,
    'unknown': 0,
    'known_fix_required': 2,
    'confirmed_pre_windows_10_target': 2,
    'serious_problem': 3,
}

FACTOR_LABELS = {
    'sale_expiry_urgency_asc': 'Срочность скидки',
    'priority_bucket_asc': 'Качественный bucket',
    'practical_or_personal_risk_asc': 'Серьёзный подтверждённый риск',
    'wishlist_desc': 'Вишлист Steam',
    'discount_percent_desc': 'Размер скидки',
    'price_quality_vs_history_desc': 'Цена относительно истории',
    'current_price_rub_asc': 'Текущая цена',
    'achievement_quality_desc': 'Достижения',
    'duration_tiebreak_asc': 'Длительность',
    'title_asc': 'Название (tie-break)',
}

HISTORY_QUALITY_LABELS = {
    'record': 'исторический минимум',
    'near_record': 'почти минимум',
    'good_vs_history': 'хорошо относительно истории',
    'previously_free': 'раньше была бесплатной',
    'unverified': 'история не подтверждена',
    'well_above_history': 'заметно выше исторического минимума',
}

URGENCY_LABELS = {
    'today': 'заканчивается сегодня',
    'tomorrow': 'заканчивается завтра',
    'later_or_unknown': 'позже или срок неизвестен',
}

WINDOWS_FRICTION_LABELS = {
    'known_fix_required': 'для современной Windows нужен подтверждённый фикс',
    'confirmed_pre_windows_10_target': 'подтверждена ориентация на старую Windows',
    'serious_problem': 'подтверждена серьёзная проблема на современной Windows',
}

DURATION_BAND_LABELS = {
    'very_short': 'очень короткая',
    'short': 'короткая',
    'medium': 'средняя',
    'long': 'длинная',
    'very_long': 'очень длинная',
    'unknown': 'неизвестна',
}


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


def sale_expiry_urgency(game, now=None):
    end = parse_utc(game.get('sale_end_utc'))
    if end is None:
        return 2, 'later_or_unknown'
    now = now or datetime.now(timezone.utc)
    local_tz = ZoneInfo(PRODUCTION_TIMEZONE)
    today = now.astimezone(local_tz).date()
    end_date = end.astimezone(local_tz).date()
    if end_date <= today:
        return 0, 'today'
    if end_date == today + timedelta(days=1):
        return 1, 'tomorrow'
    return 2, 'later_or_unknown'


def practical_risk_rank(game):
    practical = game.get('practical') or {}
    personal = RISK_LEVEL_ORDER.get(game.get('risk_level') or 'unknown', 0)
    windows = WINDOWS_FRICTION_ORDER.get(practical.get('modern_windows_friction') or 'unknown', 0)
    return max(personal, windows)


def achievement_rank(game):
    practical = game.get('practical') or {}
    if practical.get('steam_achievements') is False:
        return 7
    if practical.get('steam_achievements') is not True:
        return 6
    quality = practical.get('achievement_quality')
    if isinstance(quality, int) and 1 <= quality <= 5:
        return 5 - quality
    return 5


def factor_value(name, game, now):
    if name == 'sale_expiry_urgency_asc':
        return sale_expiry_urgency(game, now)[0]
    if name == 'priority_bucket_asc':
        return int(game.get('priority_bucket') or 99)
    if name == 'practical_or_personal_risk_asc':
        return practical_risk_rank(game)
    if name == 'wishlist_desc':
        return -int(bool(game.get('wishlist')))
    if name == 'discount_percent_desc':
        return -int(game.get('discount_percent') or 0)
    if name == 'price_quality_vs_history_desc':
        return HISTORY_QUALITY_ORDER.get(game.get('history_quality') or 'unverified', 99)
    if name == 'current_price_rub_asc':
        return int(game.get('current_price_rub') or 999999)
    if name == 'achievement_quality_desc':
        return achievement_rank(game)
    if name == 'duration_tiebreak_asc':
        return int(game.get('duration_tiebreak_penalty') or 0)
    if name == 'title_asc':
        return str(game.get('title') or '').casefold()
    raise ValueError(f'Unsupported final ranking factor: {name}')


def factor_display_value(name, game, now):
    if name == 'sale_expiry_urgency_asc':
        urgency = sale_expiry_urgency(game, now)[1]
        return URGENCY_LABELS.get(urgency, urgency)
    if name == 'priority_bucket_asc':
        bucket = int(game.get('priority_bucket') or 99)
        decision = str(game.get('decision') or '').strip()
        return f'bucket {bucket}' + (f' · {decision}' if decision else '')
    if name == 'practical_or_personal_risk_asc':
        practical = game.get('practical') or {}
        rank = practical_risk_rank(game)
        parts = []
        if (game.get('risk_level') or 'unknown') == 'high':
            parts.append('высокий персональный риск')
        windows = practical.get('modern_windows_friction') or 'unknown'
        if windows in WINDOWS_FRICTION_LABELS:
            parts.append(WINDOWS_FRICTION_LABELS[windows])
        if parts:
            return ' · '.join(parts)
        if rank == 0:
            return 'нет серьёзного подтверждённого штрафа'
        return f'штраф риска {rank}'
    if name == 'wishlist_desc':
        return 'да' if game.get('wishlist') else 'нет'
    if name == 'discount_percent_desc':
        return f'−{int(game.get("discount_percent") or 0)}%'
    if name == 'price_quality_vs_history_desc':
        quality = game.get('history_quality') or 'unverified'
        return HISTORY_QUALITY_LABELS.get(quality, str(quality))
    if name == 'current_price_rub_asc':
        value = game.get('current_price_rub')
        return 'нет цены' if value is None else f'{int(value):,} ₽'.replace(',', ' ')
    if name == 'achievement_quality_desc':
        practical = game.get('practical') or {}
        enabled = practical.get('steam_achievements')
        quality = practical.get('achievement_quality')
        if enabled is False:
            return 'Steam-достижений нет'
        if enabled is not True:
            return 'нет подтверждённых данных'
        if isinstance(quality, int) and 1 <= quality <= 5:
            return f'есть · качество {quality}/5'
        return 'есть · качество не оценено'
    if name == 'duration_tiebreak_asc':
        hours = game.get('estimated_duration_hours')
        band = game.get('duration_preference_band') or 'unknown'
        penalty = int(game.get('duration_tiebreak_penalty') or 0)
        if isinstance(hours, (int, float)):
            hours_text = f'{hours:g} ч'
        else:
            hours_text = 'оценки длительности нет'
        return f'{hours_text} · {DURATION_BAND_LABELS.get(band, band)} · tie-break {penalty}'
    if name == 'title_asc':
        return str(game.get('title') or '')
    raise ValueError(f'Unsupported final ranking factor: {name}')


def load_final_priority_order(policy_path=POLICY):
    policy = json.loads(Path(policy_path).read_text(encoding='utf-8'))
    if policy.get('contract') != 'FINAL-PRIORITY-RANKING-V1' or policy.get('status') != 'canonical':
        raise ValueError('final ranking policy is not the canonical FINAL-PRIORITY-RANKING-V1 contract')
    order = policy.get('automatic_final_priority_order')
    if not isinstance(order, list) or not order:
        raise ValueError('final ranking policy automatic_final_priority_order must be a non-empty list')
    if len(order) != len(set(order)):
        raise ValueError('final ranking policy contains duplicate factors')
    probe = {'title': 'probe'}
    now = datetime.now(timezone.utc)
    for name in order:
        factor_value(name, probe, now)
    return order


def sort_key(game, order, now):
    return tuple(factor_value(name, game, now) for name in order)


def build_factor_diagnostics(game, order, now):
    return [
        {
            'id': name,
            'label': FACTOR_LABELS.get(name, name),
            'value': factor_display_value(name, game, now),
            'sort_value': factor_value(name, game, now),
        }
        for name in order
    ]


def first_deciding_factor(current, next_game, order, now):
    for name in order:
        current_value = factor_value(name, current, now)
        next_value = factor_value(name, next_game, now)
        if current_value != next_value:
            label = FACTOR_LABELS.get(name, name)
            current_display = factor_display_value(name, current, now)
            next_display = factor_display_value(name, next_game, now)
            return {
                'next_game_id': next_game.get('id'),
                'next_game_title': next_game.get('title'),
                'deciding_factor_id': name,
                'deciding_factor_label': label,
                'current_value': current_display,
                'next_value': next_display,
                'explanation': (
                    f'Первое различие со следующей игрой — «{label}»: '
                    f'у этой «{current_display}», у следующей «{next_display}».'
                ),
            }
    return {
        'next_game_id': next_game.get('id'),
        'next_game_title': next_game.get('title'),
        'deciding_factor_id': None,
        'deciding_factor_label': None,
        'current_value': None,
        'next_value': None,
        'explanation': 'Все canonical ranking-факторы у двух игр совпали.',
    }


def apply_final_priority_order(items, now=None, policy_path=POLICY):
    now = now or datetime.now(timezone.utc)
    order = load_final_priority_order(policy_path)
    for game in items:
        urgency_rank, urgency_label = sale_expiry_urgency(game, now)
        game['sale_expiry_urgency'] = urgency_label
        game['sale_expiry_urgency_rank'] = urgency_rank
        game['practical_or_personal_risk_rank'] = practical_risk_rank(game)
    items.sort(key=lambda game: sort_key(game, order, now))
    for index, game in enumerate(items, 1):
        game['priority_rank'] = index
        game['priority_factors'] = build_factor_diagnostics(game, order, now)
    for index, game in enumerate(items):
        next_game = items[index + 1] if index + 1 < len(items) else None
        game['priority_vs_next'] = first_deciding_factor(game, next_game, order, now) if next_game else None
    return items, order