import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path('.')
POLICY = ROOT / 'config/final_ranking_policy.json'
PRODUCTION_TIMEZONE = 'Europe/Samara'

FACTOR_LABELS = {
    'sale_expiry_urgency_asc': 'Срочность скидки',
    'total_score_desc': 'Итоговый балл',
    'title_asc': 'Название (последний критерий)',
}

URGENCY_LABELS = {
    'today': 'заканчивается сегодня',
    'tomorrow': 'заканчивается завтра',
    'later_or_unknown': 'обычная срочность',
}

HISTORY_QUALITY_LABELS = {
    'record': 'исторический минимум',
    'near_record': 'почти минимум',
    'good_vs_history': 'хорошо относительно истории',
    'previously_free': 'раньше была бесплатной',
    'unverified': 'история не подтверждена',
    'well_above_history': 'заметно выше исторического минимума',
}

TASTE_SOURCE_LABELS = {
    'direct_user_rating': 'Прямая оценка пользователя',
    'normalized_taste_factors': 'Детальная оценка по факторам',
    'legacy_coarse_fit': 'Грубая оценка по старым данным',
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


def _as_number(value, default=0.0):
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _round(value, digits):
    result = round(float(value), int(digits))
    if result == -0.0:
        return 0.0
    return result


def _clamp(value, low, high):
    return max(low, min(high, value))


def load_final_policy(policy_path=POLICY):
    policy = json.loads(Path(policy_path).read_text(encoding='utf-8'))
    if policy.get('contract') != 'FINAL-PRIORITY-RANKING-V2' or policy.get('status') != 'canonical':
        raise ValueError('final ranking policy is not the canonical FINAL-PRIORITY-RANKING-V2 contract')
    validate_score_policy(policy)
    return policy


def validate_score_policy(policy):
    order = policy.get('automatic_final_priority_order')
    expected_order = ['sale_expiry_urgency_asc', 'total_score_desc', 'title_asc']
    if order != expected_order:
        raise ValueError(f'V2 automatic_final_priority_order must be exactly {expected_order!r}')

    model = policy.get('score_model') or {}
    personal = model.get('personal') or {}
    purchase = model.get('purchase') or {}
    taste = personal.get('taste') or {}

    total_max = _as_number(model.get('total_max'), -1)
    personal_max = _as_number(personal.get('max'), -1)
    purchase_max = _as_number(purchase.get('max'), -1)
    if total_max != personal_max + purchase_max:
        raise ValueError('score_model total_max must equal personal.max + purchase.max')

    taste_max = _as_number(taste.get('max'), -1)
    factor_defs = taste.get('normalized_factor_weights') or {}
    if not factor_defs:
        raise ValueError('taste normalized_factor_weights must be non-empty')
    factor_max_sum = sum(_as_number(row.get('max_points'), -999) for row in factor_defs.values())
    if factor_max_sum != taste_max:
        raise ValueError('taste factor max_points must sum exactly to taste.max')

    positive_personal_max = (
        taste_max
        + _as_number((personal.get('wishlist') or {}).get('max'), -1)
        + _as_number((personal.get('achievements') or {}).get('max'), -1)
        + _as_number((personal.get('duration') or {}).get('max'), -1)
    )
    if positive_personal_max != personal_max:
        raise ValueError('personal positive component maxima must sum exactly to personal.max')

    purchase_component_max = sum(
        _as_number((purchase.get(name) or {}).get('max'), -1)
        for name in ('savings', 'price', 'history')
    )
    if purchase_component_max != purchase_max:
        raise ValueError('purchase component maxima must sum exactly to purchase.max')

    scale_max = _as_number(taste.get('normalized_scale_max'), 0)
    if scale_max <= 0:
        raise ValueError('taste normalized_scale_max must be positive')

    for fit, points in (taste.get('legacy_coarse_fit_points') or {}).items():
        if _as_number(points, -1) < 0 or _as_number(points) > taste_max:
            raise ValueError(f'legacy coarse fit points out of range for {fit}')

    achievements = personal.get('achievements') or {}
    achievement_min = _as_number(achievements.get('min'), 1)
    achievement_max = _as_number(achievements.get('max'), -1)
    if achievement_min >= 0 or achievement_max <= 0 or achievement_min >= achievement_max:
        raise ValueError('achievements must define a negative min and positive max')
    if achievements.get('played_confirmation') != 'numeric_direct_user_evidence_rating':
        raise ValueError('achievements played confirmation must use numeric direct_user_evidence rating')
    expected_quality_keys = {'1', '2', '3', '4', '5'}
    for table_name in ('played_quality_points', 'new_or_unconfirmed_quality_points'):
        table = achievements.get(table_name) or {}
        if set(table) != expected_quality_keys:
            raise ValueError(f'{table_name} must contain exactly quality levels 1..5')
        for quality, points in table.items():
            numeric = _as_number(points, None)
            if numeric is None or numeric < achievement_min or numeric > achievement_max:
                raise ValueError(f'{table_name}[{quality}] points out of achievement range')
    for field in (
        'played_present_quality_unknown_points',
        'played_status_unknown_points',
        'played_absent_points',
        'new_or_unconfirmed_present_quality_unknown_points',
        'new_or_unconfirmed_status_unknown_points',
        'new_or_unconfirmed_absent_points',
    ):
        numeric = _as_number(achievements.get(field), None)
        if numeric is None or numeric < achievement_min or numeric > achievement_max:
            raise ValueError(f'achievements.{field} points out of achievement range')
    if _as_number(achievements.get('played_absent_points')) >= _as_number(achievements.get('new_or_unconfirmed_absent_points')):
        raise ValueError('played game without achievements must score lower than a new/unconfirmed game without achievements')
    if max(_as_number(v) for v in (achievements.get('new_or_unconfirmed_quality_points') or {}).values()) > 1.5:
        raise ValueError('new/unconfirmed achievement bonus must not exceed 1.5 points')

    for name in ('savings', 'price'):
        component = purchase.get(name) or {}
        component_max = _as_number(component.get('max'), -1)
        bands = component.get('bands') or []
        if not bands:
            raise ValueError(f'{name} bands must be non-empty')
        for band in bands:
            if _as_number(band.get('min'), 1) > _as_number(band.get('max'), 0):
                raise ValueError(f'{name} band min exceeds max')
            points = _as_number(band.get('points'), -1)
            if points < 0 or points > component_max:
                raise ValueError(f'{name} band points out of range')

    return True


def load_final_priority_order(policy_path=POLICY):
    return list(load_final_policy(policy_path)['automatic_final_priority_order'])


def _band_points(value, component, unknown_points=0):
    if value is None:
        return _as_number(component.get('unknown_points'), unknown_points)
    numeric = _as_number(value, None)
    if numeric is None:
        return _as_number(component.get('unknown_points'), unknown_points)
    for band in component.get('bands') or []:
        if _as_number(band.get('min')) <= numeric <= _as_number(band.get('max')):
            return _as_number(band.get('points'))
    return _as_number(component.get('unknown_points'), unknown_points)


def _effective_risk_codes(game, policy):
    risk_cfg = (((policy.get('score_model') or {}).get('personal') or {}).get('risk') or {})
    ignored = {str(x) for x in risk_cfg.get('achievement_only_risk_codes_ignored') or []}
    return [str(code) for code in (game.get('risk_codes') or []) if code and str(code) not in ignored]


def practical_risk_rank(game, policy=None):
    policy = policy or load_final_policy()
    risk_cfg = (((policy.get('score_model') or {}).get('personal') or {}).get('risk') or {})
    friction = str((game.get('practical') or {}).get('modern_windows_friction') or 'unknown')
    if friction in set(risk_cfg.get('confirmed_windows_values') or []):
        return 3
    if (game.get('risk_level') or 'unknown') == 'high':
        return 2
    return 0


def build_risk_status(game, policy=None):
    policy = policy or load_final_policy()
    all_risk_codes = [str(code) for code in (game.get('risk_codes') or []) if code]
    serious_rank = practical_risk_rank(game, policy)
    if serious_rank > 0:
        return {
            'code': 'serious_risk',
            'label': 'Серьёзный риск — влияет на рейтинг',
            'affects_early_priority': False,
            'affects_score': True,
            'serious_rank': serious_rank,
            'risk_level': game.get('risk_level') or 'unknown',
            'has_described_risk': bool(all_risk_codes),
        }
    if all_risk_codes:
        return {
            'code': 'descriptive_risk',
            'label': 'Есть риск — учитывается как небольшой штраф, если это не только отсутствие достижений',
            'affects_early_priority': False,
            'affects_score': bool(_effective_risk_codes(game, policy)),
            'serious_rank': 0,
            'risk_level': game.get('risk_level') or 'unknown',
            'has_described_risk': True,
        }
    return {
        'code': 'no_confirmed_risk',
        'label': 'Подтверждённых персональных рисков не найдено',
        'affects_early_priority': False,
        'affects_score': False,
        'serious_rank': 0,
        'risk_level': game.get('risk_level') or 'low',
        'has_described_risk': False,
    }


def _taste_component(game, policy):
    model = policy['score_model']
    cfg = model['personal']['taste']
    digits = model.get('round_digits', 1)
    maximum = _as_number(cfg['max'])

    evidence = game.get('direct_user_evidence') or {}
    rating = evidence.get('rating')
    if isinstance(rating, (int, float)) and not isinstance(rating, bool):
        points = _clamp(float(rating) * _as_number(cfg.get('direct_user_rating_multiplier')), 0, maximum)
        return {
            'id': 'taste',
            'label': cfg.get('label') or 'Игра сама по себе',
            'points': _round(points, digits),
            'max_points': maximum,
            'source': 'direct_user_rating',
            'source_label': TASTE_SOURCE_LABELS['direct_user_rating'],
            'value': f'прямая оценка {float(rating):g}/5',
            'factor_breakdown': [],
        }

    factor_defs = cfg.get('normalized_factor_weights') or {}
    factors = game.get('taste_factors')
    if isinstance(factors, dict) and set(factor_defs).issubset(factors):
        scale_max = _as_number(cfg.get('normalized_scale_max'))
        details = []
        total = 0.0
        valid = True
        for factor_id, factor_cfg in factor_defs.items():
            raw = factors.get(factor_id)
            if not isinstance(raw, (int, float)) or isinstance(raw, bool) or not (0 <= float(raw) <= scale_max):
                valid = False
                break
            max_points = _as_number(factor_cfg.get('max_points'))
            points = float(raw) / scale_max * max_points
            total += points
            details.append({
                'id': factor_id,
                'label': factor_cfg.get('label') or factor_id,
                'normalized_value': _round(raw, digits),
                'normalized_max': scale_max,
                'points': _round(points, digits),
                'max_points': max_points,
            })
        if valid:
            return {
                'id': 'taste',
                'label': cfg.get('label') or 'Игра сама по себе',
                'points': _round(_clamp(total, 0, maximum), digits),
                'max_points': maximum,
                'source': 'normalized_taste_factors',
                'source_label': TASTE_SOURCE_LABELS['normalized_taste_factors'],
                'value': 'детальная нормализованная оценка',
                'factor_breakdown': details,
            }

    fit = str(game.get('fit') or game.get('source_fit') or 'moderate')
    coarse = cfg.get('legacy_coarse_fit_points') or {}
    points = _clamp(_as_number(coarse.get(fit), 0), 0, maximum)
    return {
        'id': 'taste',
        'label': cfg.get('label') or 'Игра сама по себе',
        'points': _round(points, digits),
        'max_points': maximum,
        'source': 'legacy_coarse_fit',
        'source_label': cfg.get('legacy_coarse_fit_label') or TASTE_SOURCE_LABELS['legacy_coarse_fit'],
        'value': f'{fit} · грубая оценка по старым данным',
        'factor_breakdown': [],
    }


def _wishlist_component(game, policy):
    cfg = policy['score_model']['personal']['wishlist']
    points = cfg.get('present_points') if game.get('wishlist') else cfg.get('absent_points')
    return {
        'id': 'wishlist',
        'label': cfg.get('label') or 'Вишлист Steam',
        'points': _as_number(points),
        'max_points': _as_number(cfg.get('max')),
        'value': 'да' if game.get('wishlist') else 'нет',
    }


def _achievement_component(game, policy):
    cfg = policy['score_model']['personal']['achievements']
    practical = game.get('practical') or {}
    enabled = practical.get('steam_achievements')
    quality = practical.get('achievement_quality')
    evidence = game.get('direct_user_evidence') or {}
    rating = evidence.get('rating')
    played = isinstance(rating, (int, float)) and not isinstance(rating, bool)

    prefix = 'played' if played else 'new_or_unconfirmed'
    quality_points = cfg.get(f'{prefix}_quality_points') or {}
    if enabled is False:
        points = cfg.get(f'{prefix}_absent_points')
        value = 'Steam-достижений нет'
    elif enabled is not True:
        points = cfg.get(f'{prefix}_status_unknown_points')
        value = 'нет подтверждённых данных'
    elif isinstance(quality, int) and not isinstance(quality, bool) and 1 <= quality <= 5:
        points = quality_points.get(str(quality), 0)
        value = f'качество {quality}/5'
    else:
        points = cfg.get(f'{prefix}_present_quality_unknown_points')
        value = 'есть, качество не оценено'

    numeric_points = _as_number(points)
    context_label = 'уже играл' if played else 'новая или не подтверждено, что играл'
    return {
        'id': 'achievements',
        'label': cfg.get('label') or 'Достижения',
        'points': numeric_points,
        'max_points': _as_number(cfg.get('max')) if numeric_points >= 0 else None,
        'min_points': _as_number(cfg.get('min')),
        'played_confirmed': played,
        'value': f'{value} · {context_label}',
    }


def _duration_component(game, policy):
    cfg = policy['score_model']['personal']['duration']
    band = str(game.get('duration_preference_band') or 'unknown')
    points = (cfg.get('band_points') or {}).get(band, (cfg.get('band_points') or {}).get('unknown', 0))
    hours = game.get('estimated_duration_hours')
    value = f'{float(hours):g} ч · {band}' if isinstance(hours, (int, float)) else f'{band}'
    return {
        'id': 'duration',
        'label': cfg.get('label') or 'Продолжительность',
        'points': _as_number(points),
        'max_points': _as_number(cfg.get('max')),
        'value': value,
    }


def _risk_component(game, policy):
    cfg = policy['score_model']['personal']['risk']
    practical = game.get('practical') or {}
    friction = str(practical.get('modern_windows_friction') or 'unknown')
    effective_codes = _effective_risk_codes(game, policy)
    risk_level = str(game.get('risk_level') or 'unknown')

    if friction in set(cfg.get('confirmed_windows_values') or []):
        penalty = _as_number(cfg.get('confirmed_windows_penalty'))
        value = 'подтверждённая проблема современной Windows'
    elif risk_level == 'high':
        penalty = _as_number(cfg.get('serious_personal_penalty'))
        value = 'высокий персональный риск'
    elif effective_codes and risk_level == 'medium':
        penalty = _as_number(cfg.get('descriptive_medium_penalty'))
        value = 'средний описательный риск'
    elif effective_codes:
        penalty = _as_number(cfg.get('descriptive_low_penalty'))
        value = 'небольшой описательный риск'
    else:
        penalty = _as_number(cfg.get('no_confirmed_risk_penalty'))
        value = 'штрафа нет'

    penalty = _clamp(penalty, 0, _as_number(cfg.get('max_penalty')))
    return {
        'id': 'risk',
        'label': cfg.get('label') or 'Риск',
        'points': -penalty,
        'max_penalty': _as_number(cfg.get('max_penalty')),
        'value': value,
        'risk_codes_counted': effective_codes,
    }


def _savings_component(game, policy):
    cfg = policy['score_model']['purchase']['savings']
    original = _as_number(game.get('original_price_rub'), None)
    current = _as_number(game.get('current_price_rub'), None)
    savings = None if original is None or current is None else max(0.0, original - current)
    points = _band_points(savings, cfg)
    display = 'нет данных' if savings is None else f'{int(round(savings)):,} ₽'.replace(',', ' ')
    return {
        'id': 'savings',
        'label': cfg.get('label') or 'Экономия по акции',
        'points': points,
        'max_points': _as_number(cfg.get('max')),
        'value': display,
        'savings_rub': savings,
    }


def _price_component(game, policy):
    cfg = policy['score_model']['purchase']['price']
    value = game.get('current_price_rub')
    points = _band_points(value, cfg)
    display = 'нет цены' if value is None else f'{int(value):,} ₽'.replace(',', ' ')
    return {
        'id': 'price',
        'label': cfg.get('label') or 'Текущая цена',
        'points': points,
        'max_points': _as_number(cfg.get('max')),
        'value': display,
    }


def _history_component(game, policy):
    cfg = policy['score_model']['purchase']['history']
    quality = str(game.get('history_quality') or 'unverified')
    points = _as_number((cfg.get('quality_points') or {}).get(quality, 0))
    return {
        'id': 'history',
        'label': cfg.get('label') or 'История цены',
        'points': points,
        'max_points': _as_number(cfg.get('max')),
        'value': HISTORY_QUALITY_LABELS.get(quality, quality),
    }


def build_score_breakdown(game, policy):
    model = policy['score_model']
    digits = int(model.get('round_digits', 1))
    personal_cfg = model['personal']
    purchase_cfg = model['purchase']

    taste = _taste_component(game, policy)
    personal_components = [
        taste,
        _wishlist_component(game, policy),
        _achievement_component(game, policy),
        _duration_component(game, policy),
        _risk_component(game, policy),
    ]
    personal_raw = sum(_as_number(row.get('points')) for row in personal_components)
    personal_score = _round(_clamp(personal_raw, 0, _as_number(personal_cfg.get('max'))), digits)

    purchase_components = [
        _savings_component(game, policy),
        _price_component(game, policy),
        _history_component(game, policy),
    ]
    purchase_raw = sum(_as_number(row.get('points')) for row in purchase_components)
    purchase_score = _round(_clamp(purchase_raw, 0, _as_number(purchase_cfg.get('max'))), digits)

    total = _round(
        _clamp(personal_score + purchase_score, 0, _as_number(model.get('total_max'))),
        digits,
    )
    precision = {
        'code': taste['source'],
        'label': taste['source_label'],
        'is_coarse_legacy': taste['source'] == 'legacy_coarse_fit',
    }
    return {
        'contract': policy['contract'],
        'total_score': total,
        'total_max': _as_number(model.get('total_max')),
        'personal_score': personal_score,
        'personal_max': _as_number(personal_cfg.get('max')),
        'personal_label': personal_cfg.get('label') or 'Насколько подходит тебе',
        'purchase_score': purchase_score,
        'purchase_max': _as_number(purchase_cfg.get('max')),
        'purchase_label': purchase_cfg.get('label') or 'Выгодность покупки',
        'personal_components': personal_components,
        'purchase_components': purchase_components,
        'precision': precision,
    }


def factor_value(name, game, now, policy):
    if name == 'sale_expiry_urgency_asc':
        return sale_expiry_urgency(game, now)[0]
    if name == 'total_score_desc':
        return -_as_number((game.get('score_breakdown') or {}).get('total_score'), 0)
    if name == 'title_asc':
        return str(game.get('title') or '').casefold()
    raise ValueError(f'Unsupported final ranking factor: {name}')


def factor_display_value(name, game, now, policy):
    if name == 'sale_expiry_urgency_asc':
        urgency = sale_expiry_urgency(game, now)[1]
        return URGENCY_LABELS.get(urgency, urgency)
    if name == 'total_score_desc':
        score = (game.get('score_breakdown') or {}).get('total_score', 0)
        maximum = (game.get('score_breakdown') or {}).get('total_max', 100)
        return f'{score:g}/{maximum:g}'
    if name == 'title_asc':
        return str(game.get('title') or '')
    raise ValueError(f'Unsupported final ranking factor: {name}')


def sort_key(game, order, now, policy):
    return tuple(factor_value(name, game, now, policy) for name in order)


def build_factor_diagnostics(game, order, now, policy):
    return [
        {
            'id': name,
            'label': FACTOR_LABELS.get(name, name),
            'value': factor_display_value(name, game, now, policy),
            'sort_value': factor_value(name, game, now, policy),
        }
        for name in order
    ]


def first_deciding_factor(current, next_game, order, now, policy):
    for name in order:
        current_value = factor_value(name, current, now, policy)
        next_value = factor_value(name, next_game, now, policy)
        if current_value != next_value:
            label = FACTOR_LABELS.get(name, name)
            current_display = factor_display_value(name, current, now, policy)
            next_display = factor_display_value(name, next_game, now, policy)
            if name == 'sale_expiry_urgency_asc':
                explanation = (
                    f'Первое различие со следующей игрой — «{label}»: '
                    f'у этой «{current_display}», у следующей «{next_display}». Срочность находится вне 100 баллов.'
                )
            elif name == 'total_score_desc':
                explanation = (
                    f'Первое различие со следующей игрой — «{label}»: '
                    f'у этой {current_display}, у следующей {next_display}.'
                )
            else:
                explanation = 'Баллы и срочность совпали; порядок определён названием только для стабильности.'
            return {
                'next_game_id': next_game.get('id'),
                'next_game_title': next_game.get('title'),
                'deciding_factor_id': name,
                'deciding_factor_label': label,
                'current_value': current_display,
                'next_value': next_display,
                'explanation': explanation,
            }
    return {
        'next_game_id': next_game.get('id'),
        'next_game_title': next_game.get('title'),
        'deciding_factor_id': None,
        'deciding_factor_label': None,
        'current_value': None,
        'next_value': None,
        'explanation': 'Срочность, итоговый балл и название совпали.',
    }


def apply_final_priority_order(items, now=None, policy_path=POLICY):
    now = now or datetime.now(timezone.utc)
    policy = load_final_policy(policy_path)
    order = list(policy['automatic_final_priority_order'])

    for game in items:
        urgency_rank, urgency_code = sale_expiry_urgency(game, now)
        game['sale_expiry_urgency'] = urgency_code
        game['sale_expiry_urgency_rank'] = urgency_rank
        game['practical_or_personal_risk_rank'] = practical_risk_rank(game, policy)
        game['risk_status'] = build_risk_status(game, policy)
        game['score_breakdown'] = build_score_breakdown(game, policy)
        game['total_score'] = game['score_breakdown']['total_score']
        game['personal_score'] = game['score_breakdown']['personal_score']
        game['purchase_score'] = game['score_breakdown']['purchase_score']
        savings_component = next(
            row for row in game['score_breakdown']['purchase_components'] if row['id'] == 'savings'
        )
        game['savings_rub'] = savings_component.get('savings_rub')
        risk_component = next(
            row for row in game['score_breakdown']['personal_components'] if row['id'] == 'risk'
        )
        game['risk_status']['score_penalty'] = -_as_number(risk_component.get('points'))

    items.sort(key=lambda game: sort_key(game, order, now, policy))
    for index, game in enumerate(items, 1):
        game['priority_rank'] = index
        game['priority_factors'] = build_factor_diagnostics(game, order, now, policy)
    for index, game in enumerate(items):
        next_game = items[index + 1] if index + 1 < len(items) else None
        game['priority_vs_next'] = first_deciding_factor(game, next_game, order, now, policy) if next_game else None
    return items, order