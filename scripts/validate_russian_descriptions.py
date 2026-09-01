import argparse
import json
from pathlib import Path

from russian_description_quality import classify_description


def validate(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    items = data.get('items') or []
    failures = []
    counts = {}
    for game in items:
        summary = game.get('summary')
        category = classify_description(summary)
        counts[category] = counts.get(category, 0) + 1
        status = game.get('description_status')
        if category != 'good_ru' or (status is not None and status != 'ready_ru'):
            failures.append({
                'id': game.get('id'),
                'title': game.get('title'),
                'category': category,
                'description_status': status,
            })

    print(json.dumps({
        'path': str(path),
        'item_count': len(items),
        'category_counts': counts,
        'invalid_count': len(failures),
        'invalid_examples': failures[:20],
    }, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(
            f'Russian description validation failed: {len(failures)}/{len(items)} visible cards are not meaningful Russian'
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default='data/production/visual/current.json')
    args = parser.parse_args()
    validate(args.path)


if __name__ == '__main__':
    main()
