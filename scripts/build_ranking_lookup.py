import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

ROOT = Path('.')
SOURCE = ROOT / 'data/production/visual/current.json'
LEGACY_LOOKUP = ROOT / 'data/production/visual/ranking_lookup.json'
LOOKUP_DIR = ROOT / 'data/production/visual/ranking_lookup'
MANIFEST = LOOKUP_DIR / '_manifest.json'


def bucket_for(title):
    text = str(title or '').strip().casefold()
    if not text:
        return '_'
    first = text[0]
    if 'a' <= first <= 'z':
        return first
    if '0' <= first <= '9':
        return '0-9'
    return '_'


def compact_row(game):
    return {
        'rank': game.get('priority_rank'),
        'taste_rank': game.get('taste_rank'),
        'fit': game.get('fit'),
        'decision': game.get('decision'),
        'priority_group': game.get('priority_bucket'),
        'serious_risk_rank': game.get('practical_or_personal_risk_rank'),
        'risk_level': game.get('risk_level'),
        'wishlist': bool(game.get('wishlist')),
        'discount_percent': game.get('discount_percent'),
        'history_quality': game.get('history_quality'),
        'current_price_rub': game.get('current_price_rub'),
    }


def main():
    data = json.loads(SOURCE.read_text(encoding='utf-8'))
    games = sorted(data.get('items') or [], key=lambda g: str(g.get('title') or '').casefold())

    if LOOKUP_DIR.exists():
        shutil.rmtree(LOOKUP_DIR)
    LOOKUP_DIR.mkdir(parents=True, exist_ok=True)
    if LEGACY_LOOKUP.exists():
        LEGACY_LOOKUP.unlink()

    buckets = defaultdict(dict)
    for game in games:
        title = str(game.get('title') or game.get('id') or '').strip()
        if not title:
            continue
        buckets[bucket_for(title)][title] = compact_row(game)

    counts = {}
    for bucket, rows in sorted(buckets.items()):
        path = LOOKUP_DIR / f'{bucket}.json'
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        counts[bucket] = len(rows)

    manifest = {
        'schema_version': 1,
        'source': str(SOURCE),
        'bucket_rule': 'first case-folded title character; a-z, 0-9, or _',
        'item_count': sum(counts.values()),
        'bucket_counts': counts,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'RANKING_LOOKUP_ITEMS={manifest["item_count"]}')
    print(f'RANKING_LOOKUP_BUCKETS={len(counts)}')


if __name__ == '__main__':
    main()
