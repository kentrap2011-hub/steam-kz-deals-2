import argparse
import json
from pathlib import Path

import build_daily_visual_payload as readiness_builder
from russian_description_quality import classify_description


CURRENT_VISUAL = Path('data/production/visual/current.json')


def semantic_validation_required(path):
    candidate = Path(path)
    if candidate.resolve() != CURRENT_VISUAL.resolve():
        return True
    source_key, _payload = readiness_builder.current_production_readiness()
    return source_key is not None


def validate(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    items = data.get('items') or []

    if not semantic_validation_required(path):
        print(json.dumps({
            'path': str(path),
            'item_count': len(items),
            'validation_mode': 'preserve_existing_semantics',
            'reason': 'pending_ai_queue',
        }, ensure_ascii=False, indent=2))
        print('RUSSIAN_DESCRIPTION_VALIDATION=SKIP reason=pending_ai_queue_preserve_existing_semantics')
        return

    failures = []
    explicit_unresolved = []
    counts = {}
    validated_count = 0
    unresolved_statuses = {
        'needs_translation',
        'needs_ru_rewrite',
        'technical_source',
        'missing_source',
    }
    for game in items:
        if game.get('analysis_state') in {'analysis_incomplete', 'not_analyzed'}:
            continue
        validated_count += 1
        summary = game.get('summary')
        category = classify_description(summary)
        counts[category] = counts.get(category, 0) + 1
        status = game.get('description_status')

        if category == 'good_ru' and (status is None or status == 'ready_ru'):
            continue

        # Missing Russian text is a producer-owned, visible diagnostic rather than
        # a publication blocker. It is nonblocking only while no summary is
        # published. Source/provenance fields may retain the exact non-Russian
        # input for translation, but that text must never masquerade as Russian.
        if status in unresolved_statuses and not str(summary or '').strip():
            explicit_unresolved.append({
                'id': game.get('id'),
                'title': game.get('title'),
                'description_status': status,
                'description_source_quality': game.get('description_source_quality'),
            })
            counts['explicit_unresolved_nonblocking'] = (
                counts.get('explicit_unresolved_nonblocking', 0) + 1
            )
            continue

        failures.append({
            'id': game.get('id'),
            'title': game.get('title'),
            'category': category,
            'description_status': status,
        })

    print(json.dumps({
        'path': str(path),
        'item_count': len(items),
        'validated_personalized_item_count': validated_count,
        'progressive_unresolved_item_count': len(items) - validated_count,
        'explicit_untranslated_nonblocking_count': len(explicit_unresolved),
        'explicit_untranslated_examples': explicit_unresolved[:20],
        'category_counts': counts,
        'invalid_count': len(failures),
        'invalid_examples': failures[:20],
    }, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(
            f'Russian description validation failed: {len(failures)}/{validated_count} personalized cards contain invalid or masquerading Russian-description state'
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default=str(CURRENT_VISUAL))
    args = parser.parse_args()
    validate(args.path)


if __name__ == '__main__':
    main()
