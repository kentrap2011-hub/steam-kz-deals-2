#!/usr/bin/env python3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import duration_enrichment as de


CONTRACT = {
    'contract': 'DURATION-ENRICHMENT-V1',
    'authority': {
        'primary_provider': 'igdb',
        'api_base_url': 'https://api.igdb.com/v4',
        'identity_source_endpoint': 'external_game_sources',
        'identity_endpoint': 'external_games',
        'duration_endpoint': 'game_time_to_beats',
    },
    'canonical_cache': {
        'container_schema_version': 1,
        'entry_schema': {
            'durable_unresolved_statuses': [
                'provider_row_missing',
                'steam_mapping_missing',
                'steam_mapping_ambiguous',
                'invalid_values',
            ],
            'transient_error_statuses': ['auth_failure', 'transport_failure'],
        },
    },
    'freshness': {
        'confirmed_soft_stale_after_days': 180,
        'durable_unresolved_retry_after_days': 30,
    },
    'normalization': {
        'conversion_divisor': 3600,
        'selected_metric': 'normally',
    },
    'provisioning_gates': {'production_collection_enabled': False},
}


class DurationEnrichmentTests(unittest.TestCase):
    def test_scope_uses_only_explicit_base_appids(self):
        rows = [
            {'semantic_condition': {'base_appids': ['10', '20']}},
            {'semantic_condition': {'base_appids': [20, '0030', 'bad']}},
            {'title': 'No fuzzy fallback 999'},
        ]
        self.assertEqual(de.required_appids_from_purchase_context(rows), ['10', '20', '30'])

    def test_external_game_query_uses_current_source_not_deprecated_category(self):
        query = de.build_external_games_query(['10', '20'], 77)
        self.assertIn('external_game_source = 77', query)
        self.assertIn('uid = ("10","20")', query)
        self.assertNotIn('category', query)

    def test_resolve_steam_source_id_by_name_not_legacy_numeric_enum(self):
        rows = [{'id': 77, 'name': 'Steam'}, {'id': 88, 'name': 'GOG'}]
        self.assertEqual(de.resolve_steam_source_id(rows), 77)
        with self.assertRaises(ValueError):
            de.resolve_steam_source_id([{'id': 1, 'name': 'GOG'}])

    def test_exact_mapping_accepts_one_game_and_rejects_ambiguous(self):
        rows = [
            {'uid': '10', 'external_game_source': 77, 'game': 1000},
            {'uid': '20', 'external_game_source': 77, 'game': 2000},
            {'uid': '20', 'external_game_source': 77, 'game': 2001},
        ]
        result = de.classify_external_game_mappings(['10', '20', '30'], rows, 77)
        self.assertEqual(result['10'], {'status': 'mapped', 'igdb_game_id': 1000})
        self.assertEqual(result['20']['status'], 'steam_mapping_ambiguous')
        self.assertEqual(result['30']['status'], 'steam_mapping_missing')

    def test_wrong_source_does_not_sneak_through(self):
        rows = [{'uid': '10', 'external_game_source': 999, 'game': 1000}]
        result = de.classify_external_game_mappings(['10'], rows, 77)
        self.assertEqual(result['10']['status'], 'invalid_values')

    def test_seconds_to_hours_and_raw_values_are_preserved(self):
        now = datetime(2026, 9, 1, tzinfo=timezone.utc)
        row = {
            'game_id': 1000,
            'hastily': 18000,
            'normally': 36000,
            'completely': 72000,
            'count': 42,
            'created_at': 100,
            'updated_at': 200,
            'checksum': 'abc',
        }
        entry = de.normalize_confirmed_entry('10', {'igdb_game_id': 1000}, row, 77, now, CONTRACT)
        self.assertEqual(entry['estimated_duration_hours'], 10.0)
        self.assertEqual(entry['selected_metric'], 'normally')
        self.assertEqual(entry['raw']['normally_seconds'], 36000)
        self.assertEqual(entry['raw']['count'], 42)
        self.assertEqual(entry['raw']['checksum'], 'abc')
        self.assertIsNone(de.normalize_confirmed_entry('10', {'igdb_game_id': 1000}, {**row, 'normally': 0}, 77, now, CONTRACT))

    def test_transient_error_does_not_overwrite_confirmed_or_durable_negative(self):
        now = datetime(2026, 9, 1, tzinfo=timezone.utc)
        confirmed = {
            'steam_appid': '10', 'status': 'confirmed', 'provider': 'igdb',
            'provider_schema': 'game_time_to_beats', 'fetched_at_utc': de.iso_utc(now),
            'refresh_after_utc': de.iso_utc(now + timedelta(days=180)),
            'selected_metric': 'normally', 'estimated_duration_hours': 10.0,
            'raw': {'steam_appid': '10', 'steam_external_game_uid': '10', 'normally_seconds': 36000},
        }
        transient = de.unresolved_entry('10', 'transport_failure', now + timedelta(days=1), CONTRACT, 'network')
        merged = de.merge_entry(confirmed, transient, now)
        self.assertEqual(merged['status'], 'confirmed')
        self.assertEqual(merged['estimated_duration_hours'], 10.0)
        self.assertEqual(merged['last_attempt_status'], 'transport_failure')

        durable = de.unresolved_entry('20', 'steam_mapping_missing', now, CONTRACT)
        transient2 = de.unresolved_entry('20', 'auth_failure', now + timedelta(days=1), CONTRACT, 'auth')
        merged2 = de.merge_entry(durable, transient2, now)
        self.assertEqual(merged2['status'], 'steam_mapping_missing')
        self.assertEqual(merged2['last_attempt_status'], 'auth_failure')

    def test_due_selection_obeys_refresh_after(self):
        now = datetime(2026, 9, 1, tzinfo=timezone.utc)
        entries = {
            '10': {'refresh_after_utc': de.iso_utc(now + timedelta(days=1))},
            '20': {'refresh_after_utc': de.iso_utc(now - timedelta(seconds=1))},
        }
        self.assertEqual(de.due_appids(['10', '20', '30'], entries, now), ['20', '30'])

    def test_structured_duration_precedes_legacy_text(self):
        entries = {
            '10': {
                'steam_appid': '10',
                'status': 'confirmed',
                'provider': 'igdb',
                'provider_schema': 'game_time_to_beats',
                'fetched_at_utc': '2026-09-01T00:00:00Z',
                'refresh_after_utc': '2027-01-01T00:00:00Z',
                'igdb_game_id': 1000,
                'steam_external_game_uid': '10',
                'steam_external_game_source_id': 77,
                'selected_metric': 'normally',
                'estimated_duration_hours': 10.0,
                'raw': {
                    'steam_appid': '10',
                    'steam_external_game_uid': '10',
                    'normally_seconds': 36000,
                    'count': 42,
                },
            }
        }
        legacy = lambda projection, game: (99.0, 'explicit_description')
        resolved = de.resolve_duration_for_game({'base_appids': ['10']}, {}, entries, legacy)
        self.assertEqual(resolved['hours'], 10.0)
        self.assertEqual(resolved['source'], 'igdb_game_time_to_beats_normally')

    def test_legacy_fallback_then_unknown_and_no_multigame_aggregation(self):
        legacy = lambda projection, game: (12.0, 'explicit_description')
        resolved = de.resolve_duration_for_game({'base_appids': ['10']}, {}, {}, legacy)
        self.assertEqual(resolved['hours'], 12.0)
        self.assertEqual(resolved['source'], 'legacy_text_explicit_duration_phrase')

        no_legacy = lambda projection, game: (None, None)
        unknown = de.resolve_duration_for_game({'base_appids': ['10']}, {}, {}, no_legacy)
        self.assertIsNone(unknown['hours'])
        self.assertIsNone(unknown['source'])

        entries = {'10': {'status': 'confirmed'}, '20': {'status': 'confirmed'}}
        multi = de.resolve_duration_for_game({'base_appids': ['10', '20']}, {}, entries, legacy)
        self.assertEqual(multi['source'], 'legacy_text_explicit_duration_phrase')

    def test_cache_writer_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / 'cache.json'
            cache = de.empty_cache(CONTRACT)
            self.assertTrue(de.write_cache(path, cache, before_text=''))
            first = path.read_text(encoding='utf-8')
            self.assertFalse(de.write_cache(path, cache, before_text=first))


if __name__ == '__main__':
    unittest.main(verbosity=2)
