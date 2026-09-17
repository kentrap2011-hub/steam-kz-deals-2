#!/usr/bin/env python3
import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_strict import derive_dossier_summary, validate_dossier_strict
from taste_steam_review_dossier_test_fixture import web_dossier


ROOT = Path(__file__).resolve().parents[1]
CONTROL = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
SCHEMA = json.loads((ROOT / "config/taste_steam_review_dossier_schema.json").read_text(encoding="utf-8"))
EVIDENCE = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")


class SemanticConsistencyRegressionTests(unittest.TestCase):
    def validate(self, doc, now):
        return validate_dossier_strict(
            doc,
            CONTROL,
            expected_appid=doc["appid"],
            expected_title=doc["title"],
            expected_ttl_days=20,
            now=now,
        )

    @staticmethod
    def refresh_summary(doc):
        doc["summary"] = derive_dossier_summary(doc["observations"], doc["conflicts"])

    def test_scg01_wrong_parent_surface_rejected_and_same_thread_distinct_items_preserved(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)

        wrong_reddit = web_dossier(610001, now)
        wrong_reddit["provenance"]["sources"][2]["url"] = "https://www.reddit.com/r/sniperelite/"
        with self.assertRaisesRegex(ValueError, "parent Reddit source locator"):
            self.validate(wrong_reddit, now)

        wrong_steam = web_dossier(610002, now)
        wrong_steam["provenance"]["sources"][1]["source_type"] = "steam_reviews"
        wrong_steam["provenance"]["player_feedback_records"][0]["public_ref"] = (
            "steam-discussion:729153699965901699:comment-442019"
        )
        with self.assertRaisesRegex(ValueError, "Steam discussion item cannot use an explicit Steam reviews parent source"):
            self.validate(wrong_steam, now)

        same_thread = web_dossier(610003, now)
        same_thread["provenance"]["player_feedback_records"].append({
            "feedback_id": "pf5",
            "source_id": "p2",
            "url": "https://www.reddit.com/r/games/comments/test610003/game_610003/comment2/",
            "publication_date": now.date().isoformat(),
            "language": "russian",
        })
        same_thread["observations"][1]["recurrence"] = "limited"
        same_thread["observations"][1]["mention_count"] = 2
        same_thread["observations"][1]["player_feedback_ids"] = ["pf4", "pf5"]
        self.assertIs(self.validate(same_thread, now), same_thread)

    def test_scg02_old_known_child_cannot_be_laundered_by_undated_recent_parent_but_unknown_child_is_preserved(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        old_date = (now.date() - timedelta(days=800)).isoformat()

        old_child = web_dossier(620001, now)
        old_child["provenance"]["sources"][2]["publication_date"] = None
        old_child["provenance"]["sources"][2]["freshness"] = "recent"
        old_child["provenance"]["sources"][2]["evidence_role"] = "current_state"
        old_child["provenance"]["player_feedback_records"][3]["publication_date"] = old_date
        with self.assertRaisesRegex(ValueError, "older feedback cannot inherit recent parent-source freshness"):
            self.validate(old_child, now)

        unknown_child = web_dossier(620002, now)
        unknown_child["provenance"]["sources"][2]["publication_date"] = None
        unknown_child["provenance"]["sources"][2]["freshness"] = "recent"
        unknown_child["provenance"]["sources"][2]["evidence_role"] = "current_state"
        unknown_child["provenance"]["player_feedback_records"][3]["publication_date"] = None
        self.assertIs(self.validate(unknown_child, now), unknown_child)

    def test_scg03_summary_is_exact_structured_projection_and_cannot_add_claims(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        valid = web_dossier(630001, now)
        self.assertEqual(valid["summary"], derive_dossier_summary(valid["observations"], valid["conflicts"]))
        self.assertIs(self.validate(valid, now), valid)

        unsupported = web_dossier(630002, now)
        unsupported["summary"] = (
            "Evidence summary: No attributable Russian player feedback was found, and a recurring localization defect exists."
        )
        with self.assertRaisesRegex(ValueError, "summary must equal canonical structured-finding derivation"):
            self.validate(unsupported, now)

    def test_scg04_exact_duplicate_conflict_is_rejected(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(640001, now)
        conflict = {
            "statement": "Players report materially different experiences with the same durable mechanic.",
            "recurrence": "moderate",
            "mention_count": 3,
            "source_ids": ["p1"],
            "player_feedback_ids": ["pf1", "pf2", "pf3"],
        }
        doc["conflicts"] = [conflict, copy.deepcopy(conflict)]
        self.refresh_summary(doc)
        with self.assertRaisesRegex(ValueError, "exact duplicate conflict"):
            self.validate(doc, now)

    def test_scg05_strong_conflict_alone_does_not_promote_overall_strength(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(650001, now)
        older_date = (now.date() - timedelta(days=400)).isoformat()
        for suffix in (5, 6):
            doc["provenance"]["player_feedback_records"].append({
                "feedback_id": f"pf{suffix}",
                "source_id": "p1",
                "public_ref": f"steam-review-650001-{suffix}",
                "publication_date": older_date,
                "language": "non_russian",
            })
        doc["conflicts"] = [{
            "statement": "A strong recurring conflict is present without any strongly recurring observation.",
            "recurrence": "strong",
            "mention_count": 5,
            "source_ids": ["p1"],
            "player_feedback_ids": ["pf1", "pf2", "pf3", "pf5", "pf6"],
        }]
        doc["evidence"]["overall_strength"] = "strong"
        self.refresh_summary(doc)
        with self.assertRaisesRegex(ValueError, "overall strong evidence requires at least one strongly recurring observation"):
            self.validate(doc, now)

        binding = EVIDENCE["overall_strength_binding"]
        self.assertEqual(binding["source"], "observations_only_for_strong_and_moderate_thresholds")
        self.assertFalse(binding["conflict_recurrence_promotes_overall_strength"])
        self.assertFalse(SCHEMA["overall_strength_invariants"]["conflict_recurrence_may_promote_overall_strength"])
        self.assertIn("Conflict recurrence does not promote `overall_strength`", PROMPT)

    def test_scg06_parent_child_language_containment_is_worker_facing_and_strict(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        mismatch = web_dossier(660001, now, russian_status="found_and_used")
        mismatch["provenance"]["sources"][2]["language"] = "non_russian"
        with self.assertRaisesRegex(ValueError, "Russian feedback conflicts with source language"):
            self.validate(mismatch, now)

        machine_rule = EVIDENCE["language_binding"]["parent_source_language_containment"]
        self.assertEqual(machine_rule["russian_child_requires_parent_language"], ["russian", "mixed"])
        self.assertEqual(machine_rule["non_russian_child_requires_parent_language"], ["non_russian", "mixed"])
        self.assertEqual(
            SCHEMA["provenance_relationship_invariants"]["parent_child_language_containment"]["russian_child_parent_languages"],
            ["russian", "mixed"],
        )
        self.assertIn('A child feedback record with `language:"russian"` requires its parent source `language` to be `russian` or `mixed`', PROMPT)

    def test_worker_facing_contract_covers_all_six_without_changing_buffer_architecture(self):
        self.assertFalse(EVIDENCE["parent_item_binding"]["host_match_alone_is_sufficient"])
        self.assertTrue(EVIDENCE["parent_item_binding"]["same_thread_distinct_items_allowed"])
        self.assertIn("known_child_date_parent_coherence_rule", EVIDENCE["recency"])
        self.assertEqual(EVIDENCE["summary_binding"]["mode"], "mechanically_derived_from_validated_structured_findings")
        self.assertFalse(EVIDENCE["summary_binding"]["free_form_summary_allowed"])
        self.assertFalse(EVIDENCE["conflicts"]["exact_duplicate_objects_allowed"])
        self.assertEqual(int(CONTROL["checkpointing"]["checkpoint_size"]), 3)
        self.assertTrue(CONTROL["buffered_submission"]["buffer"]["multiple_pending_groups_same_snapshot_allowed"])
        self.assertEqual(
            CONTROL["buffered_submission"]["drain"]["acceptance_rule"],
            "accept_only_the_maximal_valid_contiguous_prefix_starting_at_expected_sequence",
        )


if __name__ == "__main__":
    unittest.main()
