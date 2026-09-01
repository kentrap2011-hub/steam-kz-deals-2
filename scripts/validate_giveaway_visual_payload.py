import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


def parse_utc(value):
    if not isinstance(value, str) or not value:
        return None
    text = value[:-1] + '+00:00' if value.endswith('Z') else value
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def main(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    contract = data.get('production_contract') or {}
    assert contract.get('mode') == 'daily_precomputed_read_only_for_ui'
    assert contract.get('heavy_calculation_allowed_in_ui') is False
    assert contract.get('external_lookup_allowed_in_ui') is False

    giveaways = data.get('giveaways')
    assert isinstance(giveaways, dict)
    assert giveaways.get('schema_version') == 1
    assert giveaways.get('source_contract') == 'CROSS-PLATFORM-GIVEAWAY-V1'
    assert giveaways.get('state') in {'active', 'empty', 'unavailable'}
    assert isinstance(giveaways.get('games'), list)

    count = 0
    for game in giveaways.get('games') or []:
        assert isinstance(game.get('game_key'), str) and game.get('game_key')
        assert isinstance(game.get('title'), str) and game.get('title')
        offers = game.get('offers')
        assert isinstance(offers, list) and offers
        for offer in offers:
            end = parse_utc(offer.get('promotion_end_utc'))
            assert end is not None
            claim_url = offer.get('claim_url')
            parsed = urlparse(claim_url)
            assert parsed.scheme == 'https' and parsed.netloc
            assert offer.get('storefront') in {'steam', 'epic', 'gog'}
            assert isinstance(offer.get('source_offer_id'), str) and offer.get('source_offer_id')
            count += 1

    if giveaways.get('state') == 'active':
        assert count > 0
        assert count == giveaways.get('accepted_offer_count_at_build')
    else:
        assert count == 0
        assert giveaways.get('accepted_offer_count_at_build') == 0

    print(
        'GIVEAWAY_VISUAL_PAYLOAD=PASS '
        f"state={giveaways.get('state')} offers={count} "
        f"fresh_until={giveaways.get('fresh_until_utc')}"
    )


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'data/production/visual/current.json')
