#!/usr/bin/env python3
"""Regression coverage for the TASTE-010 supersession by pragmatic observed feedback."""
import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_strict import derive_dossier_summary, validate_dossier_strict
from taste_steam_review_dossier_test_fixture import web_dossier


ROOT = Path(__file__).resolve().parents[1]
CONTROL = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
SCHEMA = json.loads((ROOT / "config/taste_steam_review_dossier_schema.json").read_text(encoding="utf-8"))
EVIDENCE = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")


def fallback_dossier(appid, now, *, title=None, transient_author_tokens=("legacy-fixture-card",)):
    """Compatibility fixture name: serialize visible collection cards without author identity.

    The historical keyword is retained only so older regression helpers can call this
    fixture. Values model how many concrete cards were visibly inspected; they are
    never used as author identity, dedupe keys, or persisted data.
    """
    appid = str(appid)
    doc = web_dossier(appid, now, title=title, russian_status="searched_no_existence_signal")
    metadata = copy.deepcopy(doc["provenance"]["sources"][0])
    card_count = max(1, len(tuple(transient_author_tokens)))
    collection = {
        "source_id": "source-002",
        "source_type": "steam_reviews",
        "domain": "store.steampowered.com",
        "url": f"https://store.steampowered.com/app/{appid}/?l=russian",
        "publication_date": None,
        "language": "russian",
        "freshness": "unknown",
        "evidence_role": "durable_trait",
        "player_feedback": True,
        "feedback_surface_mode": "concrete_item_collection",
        "exact_product_binding": {
            "basis": "source_appid",
            "appid": appid,
            "title": None,
            "release_year": None,
        },
    }
    records = [
        {
            "feedback_id": f"feedback-{index:03d}",
            "source_id": "source-002",
            "publication_date": now.date().isoformat(),
            "language": "russian",
            "acquisition_mode": "inspected_collection_item",
        }
        for index in range(1, card_count + 1)
    ]
    observation = {
        "category": "mechanics",
        "statement": "Observed Russian player feedback describes a durable gameplay characteristic.",
        "sentiment": "mixed",
        "recurrence": "anecdotal" if card_count == 1 else "limited",
        "mention_count": card_count,
        "evidence_languages": ["russian"],
        "evidence_status": "durable",
        "source_ids": ["source-002"],
        "player_feedback_ids": [record["feedback_id"] for record in records],
    }
    doc["observations"] = [observation]
    doc["conflicts"] = []
    doc["summary"] = derive_dossier_summary(doc["observations"], doc["conflicts"])
    doc["evidence"] = {
        "strategy": "adaptive_multi_source_web",
        "research_state": "sufficient",
        "source_mix_status": "single_source_only",
        "single_source_reason": "One exact-product collection supplies the compact central-experience fixture.",
        "russian_attempt": "found_and_used",
        "overall_strength": "limited",
        "stop_reason": "evidence_stable",
        "coverage": {
            "dimensions": [
                {
                    "dimension": dimension,
                    "state": "covered" if dimension in {
                        "core_play_mechanics",
                        "recurring_strengths",
                        "recurring_complaints_tradeoffs",
                    } else "not_material_or_not_applicable",
                    "observation_indices": [0] if dimension in {
                        "core_play_mechanics",
                        "recurring_strengths",
                        "recurring_complaints_tradeoffs",
                    } else [],
                }
                for dimension in EVIDENCE["coverage_sufficiency"]["dimensions"]
            ],
            "closure_basis": "compact_central_experience",
            "strengths_investigated": True,
            "weaknesses_tradeoffs_investigated": True,
        },
    }
    doc["provenance"] = {"sources": [metadata, collection], "player_feedback_records": records}
    return doc


class PragmaticCollectionObservationRegressionTests(unittest.TestCase):
    def validate(self, doc, now):
        return validate_dossier_strict(
            doc,
            CONTROL,
            expected_appid=doc["appid"],
            expected_title=doc["title"],
            expected_ttl_days=20,
            now=now,
        )

    def test_collection_01_stable_item_remains_valid_optional_auditability(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(710001, now)
        self.assertIs(self.validate(doc, now), doc)
        self.assertEqual(
            EVIDENCE["feedback_item_identity"]["preferred_auditability_order"][0],
            "stable_item",
        )
        self.assertFalse(EVIDENCE["feedback_item_identity"]["global_per_review_identity_required"])

    def test_collection_02_visible_card_needs_no_locator_or_author(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(710002, now)
        record = doc["provenance"]["player_feedback_records"][0]
        self.assertEqual(record["acquisition_mode"], "inspected_collection_item")
        self.assertNotIn("url", record)
        self.assertNotIn("public_ref", record)
        self.assertIs(self.validate(doc, now), doc)

    def test_collection_03_author_identity_is_rejected_not_required(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(710003, now)
        doc["provenance"]["player_feedback_records"][0]["author"] = "do-not-persist"
        with self.assertRaisesRegex(ValueError, "unsupported fields|author identity"):
            self.validate(doc, now)
        self.assertFalse(EVIDENCE["feedback_item_identity"]["relaxed_mode_author_identity_required"])

    def test_collection_04_no_stable_locator_threshold_for_moderate(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(710004, now, transient_author_tokens=("card-a", "card-b", "card-c"))
        doc["observations"][0]["recurrence"] = "moderate"
        doc["evidence"]["overall_strength"] = "moderate"
        self.assertIs(self.validate(doc, now), doc)
        self.assertFalse(
            EVIDENCE["mention_binding"]["recurrence_identity_strength"]["stable_locator_thresholds_active"]
        )

    def test_collection_05_one_observed_item_cannot_claim_stronger_recurrence(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(710005, now)
        doc["observations"][0]["recurrence"] = "moderate"
        doc["evidence"]["overall_strength"] = "moderate"
        with self.assertRaisesRegex(ValueError, "one observed feedback item supports anecdotal recurrence only"):
            self.validate(doc, now)

    def test_collection_06_exact_appid_mismatch_stays_fail_closed(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(710006, now)
        doc["provenance"]["sources"][1]["url"] = "https://store.steampowered.com/app/999999/?l=russian"
        with self.assertRaisesRegex(ValueError, "appid does not match exact dossier appid"):
            self.validate(doc, now)

    def test_collection_07_russian_card_satisfies_found_and_used(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(710007, now)
        self.assertEqual(doc["evidence"]["russian_attempt"], "found_and_used")
        self.assertEqual(doc["provenance"]["player_feedback_records"][0]["language"], "russian")
        self.assertIs(self.validate(doc, now), doc)

    def test_collection_08_aggregate_only_has_no_feedback_record(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(710008, now)
        doc["provenance"]["player_feedback_records"] = []
        with self.assertRaisesRegex(ValueError, "player_feedback_records must be a non-empty list"):
            self.validate(doc, now)
        self.assertFalse(EVIDENCE["russian_evidence"]["aggregate_activity_alone_may_satisfy_found_and_used"])

    def test_collection_09_prompt_explicitly_supersedes_transient_author_requirement(self):
        self.assertEqual(
            EVIDENCE["transient_author_fallback"]["status"],
            "superseded_by_pragmatic_observed_feedback_model",
        )
        self.assertIn("Author identity is **not required**", PROMPT)
        self.assertIn("no recurrence level requires 3 or 5 stable locators", PROMPT)


if __name__ == "__main__":
    unittest.main()
