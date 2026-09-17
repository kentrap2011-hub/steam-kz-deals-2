#!/usr/bin/env python3
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_strict import validate_dossier_strict
from taste_steam_review_dossier_test_fixture import web_dossier


ROOT = Path(__file__).resolve().parents[1]
CONTROL = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
EVIDENCE = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")


class LanguageBindingRegressionTests(unittest.TestCase):
    def validate(self, doc, now):
        return validate_dossier_strict(
            doc,
            CONTROL,
            expected_appid=doc["appid"],
            expected_title=doc["title"],
            expected_ttl_days=20,
            now=now,
        )

    def test_live_blacksad_non_russian_bound_records_cannot_claim_russian(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(729040, now, title="Blacksad: Under the Skin", russian_status="searched_not_found_or_insufficient")
        observation = doc["observations"][0]
        self.assertEqual(observation["player_feedback_ids"], ["pf1", "pf2", "pf3"])
        self.assertEqual(
            {record["language"] for record in doc["provenance"]["player_feedback_records"] if record["feedback_id"] in observation["player_feedback_ids"]},
            {"non_russian"},
        )
        observation["evidence_languages"] = ["russian"]
        with self.assertRaisesRegex(ValueError, "claims Russian evidence without Russian player-feedback record"):
            self.validate(doc, now)

    def test_non_russian_only_bound_feedback_cannot_gain_russian_from_russian_context_or_search_attempt(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(729041, now, russian_status="searched_not_found_or_insufficient")
        doc["provenance"]["sources"].append({
            "source_id": "ru_context",
            "source_type": "official_metadata",
            "domain": "store.steampowered.com",
            "url": "https://store.steampowered.com/app/729041/?l=russian",
            "publication_date": None,
            "language": "russian",
            "freshness": "unknown",
            "evidence_role": "identity",
            "player_feedback": False,
        })
        observation = doc["observations"][1]
        self.assertEqual(observation["player_feedback_ids"], ["pf4"])
        self.assertEqual(doc["provenance"]["player_feedback_records"][3]["language"], "non_russian")
        self.assertEqual(doc["evidence"]["russian_attempt"], "searched_not_found_or_insufficient")
        observation["evidence_languages"] = ["russian"]
        with self.assertRaisesRegex(ValueError, "claims Russian evidence without Russian player-feedback record"):
            self.validate(doc, now)

    def test_russian_bound_record_permits_russian_claim(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(729042, now, russian_status="found_and_used")
        self.assertEqual(doc["observations"][1]["evidence_languages"], ["russian"])
        self.assertEqual(doc["provenance"]["player_feedback_records"][3]["language"], "russian")
        self.assertIs(self.validate(doc, now), doc)

    def test_mixed_bound_record_projects_to_russian_and_non_russian_support(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(729043, now, russian_status="found_and_used")
        doc["provenance"]["sources"][2]["language"] = "mixed"
        doc["provenance"]["player_feedback_records"][3]["language"] = "mixed"
        doc["observations"][1]["evidence_languages"] = ["russian", "non_russian"]
        self.assertIs(self.validate(doc, now), doc)

    def test_worker_contract_makes_language_summary_deterministic_from_bound_records(self):
        binding = EVIDENCE["language_binding"]
        self.assertFalse(binding["observation_summary_is_free_form"])
        self.assertTrue(binding["bind_records_before_language_summary"])
        self.assertEqual(binding["record_language_support_projection"]["russian"], ["russian"])
        self.assertEqual(binding["record_language_support_projection"]["non_russian"], ["non_russian"])
        self.assertEqual(binding["record_language_support_projection"]["mixed"], ["russian", "non_russian"])
        self.assertEqual(binding["record_language_support_projection"]["unknown"], ["unknown"])
        self.assertEqual(binding["canonical_output_order"], ["russian", "non_russian", "unknown"])
        self.assertFalse(binding["search_attempt_is_language_evidence"])
        self.assertFalse(binding["source_page_or_locale_is_language_evidence"])
        self.assertIsNone(binding["conflict_language_summary_field"])
        self.assertIn("bound player_feedback_ids", binding["conflict_statement_rule"])

    def test_worker_prompt_prevents_prepublication_drift(self):
        self.assertIn("### Language binding — bind records first, derive claims second", PROMPT)
        self.assertIn("Read language support **only from those bound records**", PROMPT)
        self.assertIn('if every record bound to an observation is `non_russian`, its `evidence_languages` must be exactly `["non_russian"]`', PROMPT)
        self.assertIn("A Russian/mixed record that was found during research but is **not bound to that observation or conflict** gives that entry no Russian support.", PROMPT)
        self.assertIn("Before serializing each observation/conflict, perform the derivation from its final `player_feedback_ids` again.", PROMPT)

    def test_parallel_buffer_and_group_size_contract_are_unchanged(self):
        buffered = CONTROL["buffered_submission"]
        self.assertEqual(int(CONTROL["checkpointing"]["checkpoint_size"]), 3)
        self.assertTrue(buffered["buffer"]["multiple_pending_groups_same_snapshot_allowed"])
        self.assertEqual(
            buffered["drain"]["acceptance_rule"],
            "accept_only_the_maximal_valid_contiguous_prefix_starting_at_expected_sequence",
        )
        self.assertEqual(buffered["drain"]["owner"], "github_control_plane")


if __name__ == "__main__":
    unittest.main()
