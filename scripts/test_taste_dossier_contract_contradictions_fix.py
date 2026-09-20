#!/usr/bin/env python3
import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_strict import validate_dossier_strict, validate_dossiers_against_expected_items
from taste_steam_review_dossier_test_fixture import web_dossier
from test_taste_dossier_transient_author_fallback import fallback_dossier


ROOT = Path(__file__).resolve().parents[1]
CONTROL = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
SCHEMA = json.loads((ROOT / "config/taste_steam_review_dossier_schema.json").read_text(encoding="utf-8"))
EVIDENCE = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")


def steam_discussion_dossier(appid, now, *, title=None, parent_thread="111111", child_threads=None):
    doc = web_dossier(appid, now, title=title)
    appid = str(appid)
    child_threads = list(child_threads or [parent_thread, parent_thread, parent_thread])
    source = doc["provenance"]["sources"][1]
    source.update({
        "source_type": "steam_community",
        "domain": "steamcommunity.com",
        "url": f"https://steamcommunity.com/app/{appid}/discussions/0/{parent_thread}/",
    })
    for index, record in enumerate(doc["provenance"]["player_feedback_records"][:3], start=1):
        thread = child_threads[index - 1]
        record.pop("public_ref", None)
        record["url"] = (
            f"https://steamcommunity.com/app/{appid}/discussions/0/{thread}/comment-{index}"
        )
    return doc


class ContractContradictionsFixRegressionTests(unittest.TestCase):
    def validate(self, doc, now):
        return validate_dossier_strict(
            doc,
            CONTROL,
            expected_appid=doc["appid"],
            expected_title=doc["title"],
            expected_ttl_days=20,
            now=now,
        )

    def test_contra_fix_01_wrong_steam_child_appid_rejected(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(810001, now)
        record = doc["provenance"]["player_feedback_records"][0]
        record.pop("public_ref", None)
        record["url"] = "https://steamcommunity.com/app/999999/discussions/0/123456/comment-1"
        with self.assertRaisesRegex(ValueError, "Steam stable child appid does not match exact dossier appid"):
            self.validate(doc, now)

    def test_contra_fix_02_matching_steam_stable_child_accepted(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = steam_discussion_dossier(810002, now)
        self.assertIs(self.validate(doc, now), doc)

    def test_contra_fix_03_wrong_steam_physical_container_rejected(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = steam_discussion_dossier(
            810003,
            now,
            parent_thread="111111",
            child_threads=["222222", "111111", "111111"],
        )
        with self.assertRaisesRegex(ValueError, "does not belong to its parent Steam discussion/container"):
            self.validate(doc, now)

    def test_contra_fix_04_fallback_not_over_tightened(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(810004, now, transient_author_tokens=("author-a", "author-b"))
        self.assertIs(self.validate(doc, now), doc)
        self.assertTrue(all("url" not in r and "public_ref" not in r for r in doc["provenance"]["player_feedback_records"]))

    def test_contra_fix_05_author_derived_feedback_id_rejected(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(810005, now)
        leaked_id = "steamid-76561198442230810"
        doc["provenance"]["player_feedback_records"][0]["feedback_id"] = leaked_id
        doc["observations"][0]["player_feedback_ids"][0] = leaked_id
        with self.assertRaisesRegex(ValueError, "dossier-local feedback-NNN"):
            self.validate(doc, now)

    def test_contra_fix_06_author_derived_source_id_rejected(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(810006, now)
        leaked_id = "profile-76561198442230810"
        doc["provenance"]["sources"][1]["source_id"] = leaked_id
        for record in doc["provenance"]["player_feedback_records"][:3]:
            record["source_id"] = leaked_id
        doc["observations"][0]["source_ids"] = [leaked_id]
        with self.assertRaisesRegex(ValueError, "dossier-local source-NNN"):
            self.validate(doc, now)

    def test_contra_fix_07_neutral_stable_local_ids_accepted(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(810007, now)
        self.assertEqual([s["source_id"] for s in doc["provenance"]["sources"]], [
            "source-001", "source-002", "source-003"
        ])
        self.assertEqual(
            [r["feedback_id"] for r in doc["provenance"]["player_feedback_records"]],
            ["feedback-001", "feedback-002", "feedback-003", "feedback-004"],
        )
        self.assertIs(self.validate(doc, now), doc)

    def test_contra_fix_08_mixed_record_language_projection(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(810008, now)
        doc["provenance"]["sources"][2]["language"] = "mixed"
        doc["provenance"]["player_feedback_records"][3]["language"] = "mixed"
        doc["observations"][1]["evidence_languages"] = ["russian", "non_russian"]
        self.assertIs(self.validate(doc, now), doc)

    def test_contra_fix_09_unknown_preserved(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(810009, now)
        doc["provenance"]["player_feedback_records"][0]["language"] = "unknown"
        doc["observations"][0]["evidence_languages"] = ["non_russian", "unknown"]
        self.assertIs(self.validate(doc, now), doc)

    def test_contra_fix_10_incomplete_language_summary_rejected(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(810010, now)
        doc["provenance"]["sources"][1]["language"] = "mixed"
        doc["provenance"]["player_feedback_records"][0]["language"] = "russian"
        doc["observations"][0]["evidence_languages"] = ["russian"]
        with self.assertRaisesRegex(ValueError, "canonical bound-record language projection"):
            self.validate(doc, now)

    def test_contra_fix_11_mixed_summary_token_rejected(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(810011, now)
        doc["observations"][0]["evidence_languages"] = ["mixed"]
        with self.assertRaisesRegex(ValueError, "evidence_languages are invalid"):
            self.validate(doc, now)

    def test_contra_fix_12_wrong_language_order_rejected(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(810012, now)
        doc["provenance"]["sources"][1]["language"] = "mixed"
        doc["provenance"]["player_feedback_records"][0]["language"] = "russian"
        doc["observations"][0]["evidence_languages"] = ["non_russian", "russian"]
        with self.assertRaisesRegex(ValueError, "canonical bound-record language projection"):
            self.validate(doc, now)

    def test_contra_fix_13_current_g000001_complete_candidate_fixture(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        work = json.loads(
            (ROOT / "data/production/pre_ai/taste_steam_review_dossier_work.json").read_text(encoding="utf-8")
        )
        first_group = work["submission_group_plan"]["groups"][0]
        self.assertEqual(first_group["appids"], ["1000010", "1000360", "1003590"])

        crown = fallback_dossier(
            1000010, now, title="Crown Trick", transient_author_tokens=("crown-a", "crown-b")
        )
        hellish = web_dossier(1000360, now, title="Hellish Quart")
        tetris = web_dossier(1003590, now, title="Tetris® Effect: Connected")
        expected = [
            {"appid": "1000010", "title": "Crown Trick"},
            {"appid": "1000360", "title": "Hellish Quart"},
            {"appid": "1003590", "title": "Tetris® Effect: Connected"},
        ]
        validated = validate_dossiers_against_expected_items(
            [crown, hellish, tetris],
            expected,
            CONTROL,
            expected_ttl_days=20,
            now=now,
        )
        self.assertEqual([d["appid"] for d in validated], first_group["appids"])

    def test_contract_surfaces_align_on_all_three_closeouts(self):
        self.assertEqual(SCHEMA["schema_revision"], "identity-provenance-generation-fix-2026-09-20")
        self.assertEqual(EVIDENCE["contract_revision"], "contract-contradictions-fix-2026-09-18")
        self.assertEqual(EVIDENCE["worker_prompt_revision"], "web-evidence-v2-identity-provenance-generation-v1")
        self.assertTrue(EVIDENCE["language_binding"]["strict_exact_equality_required"])
        self.assertEqual(SCHEMA["enums"]["evidence_languages"], ["russian", "non_russian", "unknown"])
        self.assertTrue(SCHEMA["provenance_internal_id_invariants"]["ids_are_author_independent"])
        self.assertTrue(SCHEMA["provenance_relationship_invariants"]["stable_steam_child_exposed_appid_must_equal_dossier_appid"])
        self.assertIn("same host or the same broad review/discussion surface class is not enough", PROMPT)
        self.assertIn("must equal that exact canonical projection", PROMPT)


if __name__ == "__main__":
    unittest.main()
