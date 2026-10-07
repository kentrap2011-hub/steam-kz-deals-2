#!/usr/bin/env python3
import copy
import json
import tempfile
import unittest
from pathlib import Path

import isolate_site_publication_defects as isolation
import site_publication_resilience as resilience
import validate_card_explanations


def deep_binding():
    return {
        'semantic_source': 'progressive_pass2',
        'semantic_generation_id': 'gen-1',
        'profile_pin_sha256': 'profile-1',
        'work_id': 'work-1',
        'family_id': 'game:1003590',
        'taste_subject_key': 'appid:1003590',
        'appid': '1003590',
        'taste_fingerprint': 'taste-1',
        'candidate_context_sha256': 'context-1',
        'dossier_content_sha256': 'dossier-1',
        'authorization_id': 'auth-1',
        'accepted_at_utc': '2026-10-07T10:00:00+00:00',
        'work_authority_commit': 'authority-1',
    }


def tetris_card(commercial_reason=True):
    binding = deep_binding()
    text = (
        'Высокий рейтинг и score делают эту игру особенно сильной рекомендацией.'
        if commercial_reason else
        'Ритмичная пространственная головоломка опирается на точность и непрерывное освоение механик.'
    )
    return {
        'id': 'game:1003590',
        'title': 'Tetris® Effect: Connected',
        'analysis_state': 'analyzed_fit',
        'analysis_semantic_source': 'progressive_pass2',
        'analysis_semantic_generation_id': 'gen-1',
        'analysis_resolution_pass': 'pass2',
        'effective_analysis_source': 'deep',
        'fit': 'strong',
        'total_score': 77.25,
        'score_breakdown': {'taste': 50},
        'why_fit': [text],
        'why_fit_status': {'has_described_fit': True, 'grounding': 'grounded'},
        'why_fit_provenance': [{
            'source': 'deep_score_finding',
            'finding_id': 'finding-1',
            'factor_impacts': [{'factor': 'flow', 'effect': 'supports'}],
            'evidence_refs': [{'ref': 'candidate:1'}],
            'profile_evidence_refs': [{'ref': 'profile:1'}],
            'semantic_binding': binding,
        }],
        'score_explainability_status': 'linked_v1',
        'negative_assessment_status': 'completed_no_relevant_negative',
        'summary': 'Динамичная головоломка объединяет музыку, визуальные эффекты и знакомую механику в цельное ритмичное прохождение.',
        'description_status': 'ready_ru',
    }


class SitePublicationResilienceTests(unittest.TestCase):
    def test_tetris_local_failure_is_quarantined_without_semantic_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            quarantine = Path(tmp) / 'quarantine.json'
            missing_giveaway = Path(tmp) / 'missing-giveaway.json'
            visual = {
                'generated_at_utc': '2026-10-07T10:05:00+00:00',
                'production_contract': {},
                'items': [tetris_card(True)],
            }
            before = copy.deepcopy(visual['items'][0])
            isolated, qdoc, _changed = isolation.isolate_document(
                visual,
                quarantine_path=quarantine,
                observed_at_utc='2026-10-07T10:05:00+00:00',
                giveaway_snapshot_path=missing_giveaway,
            )
            card = isolated['items'][0]
            self.assertEqual(card['total_score'], before['total_score'])
            self.assertEqual(card['score_breakdown'], before['score_breakdown'])
            self.assertEqual(card['analysis_semantic_generation_id'], before['analysis_semantic_generation_id'])
            self.assertNotIn('why_fit', card)
            self.assertEqual(card['publication_presentation_state']['explanations'], 'quarantined')
            self.assertEqual(validate_card_explanations.validate_item(card), [])
            active = resilience.active_summary(qdoc)
            self.assertEqual(active['pending_count'], 1)
            self.assertEqual(active['category_counts'], {'card_explanation': 1})
            entry = next(row for row in qdoc['entries'] if row['status'] == 'pending')
            self.assertIn('positive_commercial_or_ranking_language', entry['reason_codes'])

    def test_duplicate_observation_coalesces_and_disappeared_defect_resolves(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'quarantine.json'
            defect = {
                'category': 'card_explanation',
                'object_type': 'paid_game',
                'object_id': 'game:1',
                'field': 'player_facing_explanations',
                'reason_codes': ['bad_positive'],
            }
            first, _ = resilience.reconcile_quarantine(
                [defect, {**defect, 'reason_codes': ['bad_positive', 'bad_provenance']}],
                observed_at_utc='2026-10-07T10:00:00+00:00',
                path=path,
            )
            self.assertEqual(len(first['entries']), 1)
            self.assertEqual(first['entries'][0]['reason_codes'], ['bad_positive', 'bad_provenance'])
            second, _ = resilience.reconcile_quarantine(
                [defect],
                observed_at_utc='2026-10-07T10:10:00+00:00',
                path=path,
            )
            self.assertEqual(len(second['entries']), 1)
            self.assertEqual(second['entries'][0]['status'], 'pending')
            resolved, _ = resilience.reconcile_quarantine(
                [],
                observed_at_utc='2026-10-07T10:20:00+00:00',
                path=path,
            )
            self.assertEqual(resolved['entries'][0]['status'], 'resolved')
            self.assertEqual(resilience.active_summary(resolved)['pending_count'], 0)

    def test_invalid_description_is_hidden_not_promoted(self):
        with tempfile.TemporaryDirectory() as tmp:
            quarantine = Path(tmp) / 'quarantine.json'
            card = tetris_card(False)
            card['summary'] = 'This is definitely not a Russian description for the published card.'
            card['description_status'] = 'ready_ru'
            visual = {'production_contract': {}, 'items': [card]}
            isolated, qdoc, _changed = isolation.isolate_document(
                visual,
                quarantine_path=quarantine,
                observed_at_utc='2026-10-07T10:30:00+00:00',
                giveaway_snapshot_path=Path(tmp) / 'missing.json',
            )
            card = isolated['items'][0]
            self.assertNotIn('summary', card)
            self.assertEqual(card['description_status'], 'publication_quarantined')
            self.assertEqual(resilience.active_summary(qdoc)['category_counts'], {'description': 1})

    def test_status_workflow_has_independent_pages_wakeup(self):
        deploy = Path('.github/workflows/deploy-visual.yml').read_text(encoding='utf-8')
        self.assertIn('- "Build site current status"', deploy)
        self.assertIn("github.event.workflow_run.name == 'Build daily visual payload'", deploy)
        self.assertIn("TRIGGER_WORKFLOW: ${{ github.event.workflow_run.name }}", deploy)
        self.assertIn("Build site current status", deploy)
        self.assertIn("VISUAL_DEPLOY_SCOPE=status_only trigger=site_current_status", deploy)

    def test_missing_stable_visual_identity_is_global_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            visual = {'production_contract': {}, 'items': [{'title': 'No identity'}]}
            with self.assertRaises(RuntimeError):
                isolation.isolate_document(
                    visual,
                    quarantine_path=Path(tmp) / 'q.json',
                    observed_at_utc='2026-10-07T10:40:00+00:00',
                    giveaway_snapshot_path=Path(tmp) / 'missing.json',
                )


if __name__ == '__main__':
    unittest.main()
