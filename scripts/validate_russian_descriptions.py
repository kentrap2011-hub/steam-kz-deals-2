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


def validate(path, allow_untranslated=False):
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
    counts = {}
    validated_count = 0
    for game in items:
        if game.get('analysis_state') in {'analysis_incomplete', 'not_analyzed'}:
            continue
        validated_count += 1
        summary = game.get('summary')
        category = classify_description(summary)
        counts[category] = counts.get(category, 0) + 1
        status = game.get('description_status')
        pass1_pending_translation = (
            game.get('analysis_semantic_source') == 'progressive_pass1'
            and not summary
            and status in {
                'needs_translation',
                'needs_ru_rewrite',
                'technical_source',
                'missing_source',
            }
        )
        if pass1_pending_translation:
            counts['progressive_pass1_translation_pending'] = (
                counts.get('progressive_pass1_translation_pending', 0) + 1
            )
            continue
        if category != 'good_ru' or (status is not None and status != 'ready_ru'):
            failures.append({
                'id': game.get('id'),
                'title': game.get('title'),
                'category': category,
                'description_status': status,
            })

    result = {
        'path': str(path),
        'item_count': len(items),
        'validated_personalized_item_count': validated_count,
        'progressive_unresolved_item_count': len(items) - validated_count,
        'category_counts': counts,
        'invalid_count': len(failures),
        'invalid_examples': failures[:20],
        'publication_blocking': bool(failures) and not allow_untranslated,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if failures and allow_untranslated:
        print(
            'RUSSIAN_DESCRIPTION_VALIDATION=NONBLOCKING '
            f'untranslated_or_invalid={len(failures)} publication_allowed=true'
        )
    elif failures:
        raise SystemExit(
            f'Russian description validation failed: {len(failures)}/{validated_count} personalized cards are not meaningful Russian'
        )
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default=str(CURRENT_VISUAL))
    parser.add_argument(
        '--allow-untranslated',
        action='store_true',
        help='report unresolved/invalid Russian descriptions without blocking publication',
    )
    args = parser.parse_args()
    validate(args.path, allow_untranslated=args.allow_untranslated)


if __name__ == '__main__':
    main()
