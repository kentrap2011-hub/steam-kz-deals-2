#!/usr/bin/env python3
"""DATE-01..DATE-10 regressions for GitHub-derived Dossier temporal classification."""
import copy
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_strict import (
    derive_dossier_summary,
    derive_temporal_state,
    load_web_evidence_contract,
    load_worker_schema,
    validate_dossier_strict,
)
from taste_steam_review_dossier_test_fixture import web_dossier

CONTROL = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
EVIDENCE = load_web_evidence_contract()
SCHEMA = load_worker_schema()
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")


class GithubDerivedDossierDatesTest(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 27, 10, 0, 0, tzinfo=timezone.utc)

    def validate(self, doc):
        return validate_dossier_strict(
            doc,
            CONTROL,
            expected_appid=doc["appid"],
            expected_title=doc["title"],
            expected_ttl_days=20,
            now=self.now,
        )

    def current_doc(self, appid, *, title=None):
        doc = web_dossier(appid, self.now, title=title)
        source = doc["provenance"]["sources"][2]
        source["publication_date"] = None
        source.pop("freshness", None)
        return doc

    def test_date_01_exactly_365_days_is_recent(self):
        day = self.now.date() - timedelta(days=365)
        self.assertEqual(derive_temporal_state(day, self.now.date(), EVIDENCE), "recent")
        doc = self.current_doc("1002601")
        doc["provenance"]["player_feedback_records"][3]["publication_date"] = day.isoformat()
        self.assertIs(self.validate(doc), doc)
        self.assertEqual(doc["provenance"]["sources"][2]["freshness"], "unknown")

    def test_date_02_366_days_is_older(self):
        day = self.now.date() - timedelta(days=366)
        self.assertEqual(derive_temporal_state(day, self.now.date(), EVIDENCE), "older")
        doc = self.current_doc("1002602")
        doc["provenance"]["player_feedback_records"][3]["publication_date"] = day.isoformat()
        with self.assertRaisesRegex(ValueError, "current claim lacks recent dated current-state feedback"):
            self.validate(doc)

    def test_date_03_unknown_date_is_unknown_never_recent(self):
        self.assertEqual(derive_temporal_state(None, self.now.date(), EVIDENCE), "unknown")
        doc = self.current_doc("1002603")
        doc["provenance"]["player_feedback_records"][3]["publication_date"] = None
        with self.assertRaisesRegex(ValueError, "current claim lacks recent dated current-state feedback"):
            self.validate(doc)

    def test_date_04_05_tiny_snow_undated_parent_uses_actual_child_date(self):
        old = self.current_doc("1002560", title="Tiny Snow")
        old["provenance"]["player_feedback_records"][3]["publication_date"] = (
            self.now.date() - timedelta(days=800)
        ).isoformat()
        with self.assertRaisesRegex(ValueError, "current claim lacks recent dated current-state feedback"):
            self.validate(old)
        self.assertEqual(old["provenance"]["sources"][2]["freshness"], "unknown")

        recent = self.current_doc("1002560", title="Tiny Snow")
        recent["provenance"]["player_feedback_records"][3]["publication_date"] = (
            self.now.date() - timedelta(days=20)
        ).isoformat()
        self.assertIs(self.validate(recent), recent)
        self.assertEqual(recent["provenance"]["sources"][2]["freshness"], "unknown")

    def test_date_06_mixed_children_are_classified_per_support_record(self):
        doc = self.current_doc("1002606")
        source = doc["provenance"]["sources"][2]
        recent_date = (self.now.date() - timedelta(days=10)).isoformat()
        old_date = (self.now.date() - timedelta(days=700)).isoformat()
        doc["provenance"]["player_feedback_records"][3]["publication_date"] = recent_date
        doc["provenance"]["player_feedback_records"].append({
            "feedback_id": "feedback-005",
            "source_id": source["source_id"],
            "url": "https://www.reddit.com/r/games/comments/test1002606/game_1002606/comment2/",
            "publication_date": old_date,
            "language": "russian",
            "acquisition_mode": "stable_item",
        })
        obs = doc["observations"][1]
        obs["player_feedback_ids"] = ["feedback-004", "feedback-005"]
        obs["mention_count"] = 2
        obs["recurrence"] = "limited"
        self.assertIs(self.validate(doc), doc)
        self.assertEqual(source["freshness"], "unknown")
        self.assertEqual(
            derive_temporal_state(
                datetime.fromisoformat(recent_date).date(), self.now.date(), EVIDENCE
            ),
            "recent",
        )
        self.assertEqual(
            derive_temporal_state(
                datetime.fromisoformat(old_date).date(), self.now.date(), EVIDENCE
            ),
            "older",
        )

        old_only = copy.deepcopy(doc)
        old_only["observations"][1]["player_feedback_ids"] = ["feedback-005"]
        old_only["observations"][1]["mention_count"] = 1
        old_only["observations"][1]["recurrence"] = "anecdotal"
        with self.assertRaisesRegex(ValueError, "current claim lacks recent dated current-state feedback"):
            self.validate(old_only)

    def test_date_07_unknown_child_cannot_satisfy_current_state(self):
        doc = self.current_doc("1002607")
        doc["provenance"]["player_feedback_records"][3]["publication_date"] = None
        with self.assertRaisesRegex(ValueError, "current claim lacks recent dated current-state feedback"):
            self.validate(doc)
        self.assertFalse(EVIDENCE["recency"]["unknown_temporal_evidence_satisfies_recent_requirement"])

    def test_date_08_worker_candidate_does_not_choose_freshness(self):
        doc = web_dossier("1002608", self.now)
        for source in doc["provenance"]["sources"]:
            source.pop("freshness", None)
        self.assertNotIn("freshness", SCHEMA["provenance_source_required_fields"])
        self.assertIn("do **not** choose or serialize `freshness`", PROMPT)
        self.assertIs(self.validate(doc), doc)

    def test_date_09_canonical_output_receives_derived_source_state(self):
        doc = web_dossier("1002609", self.now)
        for source in doc["provenance"]["sources"]:
            source.pop("freshness", None)
        self.assertIs(self.validate(doc), doc)
        self.assertEqual(
            [source["freshness"] for source in doc["provenance"]["sources"]],
            ["unknown", "older", "recent"],
        )
        self.assertEqual(EVIDENCE["recency"]["temporal_classification_owner"], "github_control_plane")

    def test_date_10_taste_012_historical_requires_recent_dated_current_check(self):
        doc = web_dossier("1002610", self.now, russian_status="searched_no_existence_signal")
        historical = copy.deepcopy(doc["observations"][0])
        historical.update({
            "category": "friction",
            "statement": "Older feedback records a historical technical issue.",
            "evidence_status": "historical",
            "source_ids": ["source-002"],
            "player_feedback_ids": ["feedback-001", "feedback-002", "feedback-003"],
            "mention_count": 3,
            "evidence_languages": ["non_russian"],
        })
        doc["provenance"]["sources"][1]["evidence_role"] = "historical"
        current_control = copy.deepcopy(doc["observations"][1])
        doc["observations"] = [historical, current_control]
        doc["summary"] = derive_dossier_summary(doc["observations"], doc["conflicts"])
        with self.assertRaisesRegex(ValueError, "historical/fixed claim lacks recent dated current-state check"):
            self.validate(doc)

        doc["observations"][0]["source_ids"].append("source-003")
        doc["observations"][0]["player_feedback_ids"].append("feedback-004")
        doc["observations"][0]["mention_count"] = 4
        doc["summary"] = derive_dossier_summary(doc["observations"], doc["conflicts"])
        self.assertIs(self.validate(doc), doc)


if __name__ == "__main__":
    unittest.main()
