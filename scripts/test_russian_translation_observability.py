#!/usr/bin/env python3
import json
import tempfile
from pathlib import Path

import progressive_personalization as progressive


def write(path, value):
    Path(path).write_text(json.dumps(value), encoding='utf-8')


def main():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        status = root / 'status.json'
        cache = root / 'cache.json'

        write(status, {
            'schema_version': 2,
            'untranslated_game_count': 7,
            'last_translation_attempt_at': '2026-09-29T08:15:00+00:00',
            'last_successful_translation_at': '2026-09-29T08:05:00+00:00',
        })
        write(cache, {'schema_version': 1, 'entries': {}})
        metrics = progressive._translation_processing_metrics(status, cache)
        assert metrics['translation_observability'] == 'available'
        assert metrics['untranslated_game_count'] == 7
        assert metrics['last_translation_attempt_at'] == '2026-09-29T08:15:00+00:00'
        assert metrics['last_successful_translation_at'] == '2026-09-29T08:05:00+00:00'
        assert metrics['translation_stage_counts']['untranslated_game_count'] == 7

        # Schema-v1 status may be written by the concurrently running translation
        # worker before this implementation lands. Exact arithmetic is enough to
        # recover the current count, while accepted cache time durably backfills
        # success/attempt history.
        write(status, {
            'schema_version': 1,
            'scope_record_count': 10,
            'resolved_direct_ru_count': 6,
            'resolved_translation_cache_count': 1,
            'queue_count': 2,
            'nontranslatable_blocker_count': 1,
        })
        write(cache, {
            'schema_version': 1,
            'updated_at_utc': '2026-09-29T08:20:00+00:00',
            'entries': {'accepted': {}},
        })
        metrics = progressive._translation_processing_metrics(status, cache)
        assert metrics['untranslated_game_count'] == 3
        assert metrics['last_translation_attempt_at'] == '2026-09-29T08:20:00+00:00'
        assert metrics['last_successful_translation_at'] == '2026-09-29T08:20:00+00:00'

        # Contradictory legacy arithmetic fails closed instead of inventing a
        # count from incomplete browser-visible/card data.
        write(status, {
            'schema_version': 1,
            'scope_record_count': 10,
            'resolved_direct_ru_count': 6,
            'resolved_translation_cache_count': 1,
            'queue_count': 1,
            'nontranslatable_blocker_count': 1,
        })
        metrics = progressive._translation_processing_metrics(status, cache)
        assert metrics['translation_observability'].startswith('unavailable:')
        assert metrics['untranslated_game_count'] is None
        assert metrics['last_translation_attempt_at'] is None
        assert metrics['last_successful_translation_at'] is None

    print('Russian translation producer observability regression: ok')


if __name__ == '__main__':
    main()
