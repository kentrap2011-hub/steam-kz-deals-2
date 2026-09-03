import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from semantic_runtime_completion import (
    apply_payload_status,
    apply_visual_semantic_status,
    build_runtime_observability,
    build_runtime_status,
    build_semantic_completeness,
)


class SemanticRuntimeCompletionTests(unittest.TestCase):
    def test_partition_complete_with_unresolved_queue_is_degraded(self):
        payload = {
            'source_mailing_updated_at_utc': '2026-09-02T20:36:22+00:00',
            'source_family_count': 743,
            'ai_queue_count': 644,
            'ready_without_ai_count': 0,
            'complete_family_partition': True,
        }
        state = build_semantic_completeness(
            payload,
            now=datetime(2026, 9, 3, 0, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(state['status'], 'degraded')
        self.assertFalse(state['sufficiently_complete_for_publication'])
        self.assertTrue(state['scope_partition_complete'])
        self.assertEqual(state['unresolved_semantic_count'], 644)
        self.assertEqual(state['total_relevant_semantic_scope'], 644)
        self.assertGreater(state['unresolved_scope_age_seconds'], 0)

    def test_zero_result_execution_does_not_advance_last_accepted_progress(self):
        previous = {
            'last_accepted_semantic_progress_at_utc': '2026-09-01T21:03:08+00:00',
            'last_accepted_source_mailing_updated_at_utc': 'scope-a',
            'last_accepted_batch_id': 'batch-a',
        }
        receipt = {
            'status': 'complete',
            'batch_id': 'heartbeat-only',
            'processed_at_utc': '2026-09-03T00:00:00+00:00',
            'source_mailing_updated_at_utc': 'scope-b',
            'result_count': 0,
            'baseline': {'ai_queue_count': 20},
            'after': {'ai_queue_count': 20},
            'checks': {'transactional': True},
        }
        status = build_runtime_status(receipt, previous)
        self.assertEqual(status['last_successful_semantic_execution_at_utc'], receipt['processed_at_utc'])
        self.assertEqual(status['last_accepted_semantic_progress_at_utc'], previous['last_accepted_semantic_progress_at_utc'])
        self.assertEqual(status['last_accepted_source_mailing_updated_at_utc'], 'scope-a')
        self.assertFalse(status['accepted_progress_in_last_execution'])

    def test_accepted_runtime_work_advances_progress_receipt(self):
        receipt = {
            'status': 'complete',
            'batch_id': 'batch-b',
            'processed_at_utc': '2026-09-03T00:05:00+00:00',
            'source_mailing_updated_at_utc': 'scope-b',
            'result_count': 5,
            'baseline': {'ai_queue_count': 20},
            'after': {'ai_queue_count': 15},
            'checks': {'transactional': True, 'queue_exact': True},
        }
        status = build_runtime_status(receipt)
        self.assertTrue(status['accepted_progress_in_last_execution'])
        self.assertEqual(status['last_accepted_semantic_progress_at_utc'], receipt['processed_at_utc'])
        self.assertEqual(status['last_queue_delta_count'], 5)
        observed = build_runtime_observability(status, 'scope-b')
        self.assertTrue(observed['current_scope_progress_observed'])
        self.assertEqual(observed['status'], 'current_scope_progress_observed')

    def test_stale_receipt_does_not_prove_current_scope_progress(self):
        latest = {
            'last_accepted_semantic_progress_at_utc': '2026-09-01T21:03:08+00:00',
            'last_accepted_source_mailing_updated_at_utc': 'old-scope',
            'last_queue_before_count': 37,
            'last_queue_after_count': 26,
            'last_queue_delta_count': 11,
        }
        observed = build_runtime_observability(latest, 'new-scope')
        self.assertFalse(observed['current_scope_progress_observed'])
        self.assertEqual(observed['status'], 'no_current_scope_progress_observed')
        self.assertEqual(observed['scheduler_platform_enabled_state'], 'not_exposed_to_repository')

    def test_status_application_does_not_change_taste_contract_fields(self):
        payload = {
            'schema_version': 4,
            'status': 'complete',
            'source_mailing_updated_at_utc': '2026-09-02T20:36:22+00:00',
            'source_family_count': 743,
            'ai_queue_count': 644,
            'ready_without_ai_count': 0,
            'complete_family_partition': True,
            'contract': {
                'minimum_taste_fit': 'moderate',
                'taste_phase_is_strictly_price_blind': True,
                'negative_only_backfill_must_preserve_existing_fit_semantics': True,
            },
        }
        contract_before = copy.deepcopy(payload['contract'])
        apply_payload_status(payload, None, now=datetime(2026, 9, 3, tzinfo=timezone.utc))
        self.assertEqual(payload['contract'], contract_before)
        self.assertEqual(payload['status'], 'degraded')
        visual = {'schema_version': 3, 'status': 'complete', 'items': [{'id': 'x'}]}
        apply_visual_semantic_status(visual, payload)
        self.assertEqual(visual['status'], 'degraded')
        self.assertEqual(visual['items'], [{'id': 'x'}])

    def test_current_canonical_artifacts_are_non_ambiguous_when_present(self):
        payload_path = Path('data/production/pre_ai/chatgpt_payload.json')
        if not payload_path.exists():
            self.skipTest('canonical pre-AI payload not present')
        payload = json.loads(payload_path.read_text(encoding='utf-8'))
        if int(payload.get('ai_queue_count') or 0) > 0:
            self.assertEqual(payload.get('status'), 'degraded')
            semantic = payload.get('semantic_completeness') or {}
            self.assertEqual(semantic.get('unresolved_semantic_count'), payload.get('ai_queue_count'))
            self.assertFalse(semantic.get('sufficiently_complete_for_publication'))

        visual_path = Path('data/production/visual/current.json')
        if visual_path.exists() and int(payload.get('ai_queue_count') or 0) > 0:
            visual = json.loads(visual_path.read_text(encoding='utf-8'))
            self.assertEqual(visual.get('status'), 'degraded')
            self.assertEqual(
                (visual.get('semantic_completeness') or {}).get('unresolved_semantic_count'),
                payload.get('ai_queue_count'),
            )


if __name__ == '__main__':
    unittest.main()
