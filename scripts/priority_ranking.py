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

RISK_LEVEL_ORDER = {'low': 0, 'unknown': 0, 'medium': 1, 'high': 2}
WINDOWS_FRICTION_ORDER = {
    'likely_none': 0,
    'unknown': 0,
    'known_fix_required': 2,
    'confirmed_pre_windows_10_target': 2,
    'serious_problem': 3,
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
    return items, order
