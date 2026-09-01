import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

EXPECTED_CONTRACT = 'CROSS-PLATFORM-GIVEAWAY-V1'
EXPECTED_SCHEMA_VERSION = 1
EXPECTED_COUNTRY = 'KZ'
REQUIRED_SOURCES = ('steam', 'epic', 'gog')
DEFAULT_SNAPSHOT = Path('data/production/giveaways/v1/current.json')


def parse_utc(value):
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def utc_iso(value):
    return value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def valid_https_url(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return parsed.scheme == 'https' and bool(parsed.netloc)


def unavailable(snapshot=None, now=None):
    snapshot = snapshot if isinstance(snapshot, dict) else {}
    now = now or datetime.now(timezone.utc)
    return {
        'schema_version': 1,
        'source_contract': EXPECTED_CONTRACT,
        'state': 'unavailable',
        'generated_at_utc': snapshot.get('generated_at_utc'),
        'fresh_until_utc': snapshot.get('fresh_until_utc'),
        'derived_at_utc': utc_iso(now),
        'accepted_offer_count_at_build': 0,
        'games': [],
    }


def snapshot_is_trusted(snapshot, now):
    if not isinstance(snapshot, dict):
        return False
    if snapshot.get('contract') != EXPECTED_CONTRACT:
        return False
    if snapshot.get('schema_version') != EXPECTED_SCHEMA_VERSION:
        return False
    if snapshot.get('country_code') != EXPECTED_COUNTRY:
        return False
    if snapshot.get('snapshot_status') != 'complete':
        return False

    required = snapshot.get('required_sources')
    if not isinstance(required, list) or not all(source in required for source in REQUIRED_SOURCES):
        return False

    source_health = snapshot.get('source_health')
    if not isinstance(source_health, dict):
        return False
    for source in REQUIRED_SOURCES:
        row = source_health.get(source)
        if not isinstance(row, dict):
            return False
        if row.get('complete') is not True or row.get('status') != 'ok':
            return False

    generated_at = parse_utc(snapshot.get('generated_at_utc'))
    fresh_until = parse_utc(snapshot.get('fresh_until_utc'))
    if generated_at is None or fresh_until is None:
        return False
    if fresh_until <= generated_at or fresh_until <= now:
        return False
    return True


def _presentation_offer(raw_offer, now):
    if not isinstance(raw_offer, dict):
        raise ValueError('offer_not_object')

    claim_url = raw_offer.get('claim_url')
    if not valid_https_url(claim_url):
        raise ValueError('invalid_claim_url')

    promotion_end = parse_utc(raw_offer.get('promotion_end_utc'))
    if promotion_end is None:
        raise ValueError('invalid_promotion_end')
    if promotion_end <= now:
        return None

    storefront = raw_offer.get('storefront')
    source_offer_id = raw_offer.get('source_offer_id')
    if storefront not in REQUIRED_SOURCES or not isinstance(source_offer_id, str) or not source_offer_id:
        raise ValueError('invalid_offer_identity')

    return {
        'storefront': storefront,
        'source_offer_id': source_offer_id,
        'source_product_id': raw_offer.get('source_product_id'),
        'claim_url': claim_url,
        'promotion_end_utc': utc_iso(promotion_end),
    }


def derive_giveaways(snapshot, now=None):
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)

    if not snapshot_is_trusted(snapshot, now):
        return unavailable(snapshot, now)

    games = snapshot.get('games')
    if not isinstance(games, list):
        return unavailable(snapshot, now)

    derived_games = []
    try:
        for raw_game in games:
            if not isinstance(raw_game, dict):
                raise ValueError('game_not_object')
            game_key = raw_game.get('canonical_game_key')
            title = raw_game.get('title')
            offers = raw_game.get('offers')
            if not isinstance(game_key, str) or not game_key or not isinstance(title, str) or not title.strip():
                raise ValueError('invalid_game_identity')
            if not isinstance(offers, list):
                raise ValueError('offers_not_list')

            active_offers = []
            for raw_offer in offers:
                offer = _presentation_offer(raw_offer, now)
                if offer is not None:
                    active_offers.append(offer)

            active_offers.sort(
                key=lambda offer: (
                    offer['promotion_end_utc'],
                    offer['storefront'],
                    offer['source_offer_id'],
                )
            )
            if active_offers:
                derived_games.append({
                    'game_key': game_key,
                    'title': title.strip(),
                    'offers': active_offers,
                })
    except ValueError:
        return unavailable(snapshot, now)

    derived_games.sort(
        key=lambda game: (
            game['offers'][0]['promotion_end_utc'],
            game['title'].casefold(),
            game['game_key'],
        )
    )
    active_offer_count = sum(len(game['offers']) for game in derived_games)

    return {
        'schema_version': 1,
        'source_contract': EXPECTED_CONTRACT,
        'state': 'active' if active_offer_count else 'empty',
        'generated_at_utc': snapshot.get('generated_at_utc'),
        'fresh_until_utc': snapshot.get('fresh_until_utc'),
        'derived_at_utc': utc_iso(now),
        'accepted_offer_count_at_build': active_offer_count,
        'games': derived_games,
    }


def derive_from_path(path=DEFAULT_SNAPSHOT, now=None):
    try:
        snapshot = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return unavailable({}, now or datetime.now(timezone.utc))
    return derive_giveaways(snapshot, now=now)
