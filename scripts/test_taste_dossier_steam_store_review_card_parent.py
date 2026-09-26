#!/usr/bin/env python3
import copy
import json
import unittest
from datetime import datetime, timezone

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_strict import validate_dossier_strict, validate_dossiers_against_expected_items
from taste_steam_review_dossier_test_fixture import web_dossier
from test_taste_dossier_transient_author_fallback import fallback_dossier


CONTROL = load_contract("config/taste_steam_review_dossier_contract.json")
SCHEMA = json.load(open("config/taste_steam_review_dossier_schema.json", encoding="utf-8"))
EVIDENCE = json.load(open("config/taste_steam_review_dossier_web_evidence_contract.json", encoding="utf-8"))
PROMPT = open("config/taste_steam_review_dossier_worker_prompt.md", encoding="utf-8").read()


class SteamStoreReviewCardParentRegressionTests(unittest.TestCase):
    def validate(self, doc, now):
        return validate_dossier_strict(
            doc,
            CONTROL,
            expected_appid=doc["appid"],
            expected_title=doc["title"],
            expected_ttl_days=20,
            now=now,
        )

    def test_store_card_01_aggregate_label_is_not_stable_feedback_item(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick")
        record = doc["provenance"]["player_feedback_records"][0]
        record["acquisition_mode"] = "stable_item"
        record["public_ref"] = "120-russian-reviews"
        with self.assertRaisesRegex(ValueError, "stable public item identity|stable_item|public_ref"):
            self.validate(doc, now)
        self.assertTrue(SCHEMA["evidence_invariants"]["steam_store_app_page_cannot_be_player_feedback_record"])

    def test_store_card_02_aggregate_russian_count_is_existence_only(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick")
        doc["provenance"]["sources"][1]["language"] = "non_russian"
        doc["provenance"]["player_feedback_records"][0]["language"] = "non_russian"
        doc["observations"][0]["evidence_languages"] = ["non_russian"]
        with self.assertRaisesRegex(ValueError, "found_and_used requires a bound Russian player-feedback record"):
            self.validate(doc, now)
        self.assertFalse(EVIDENCE["source_policy"]["aggregate_storefront_statistics_are_player_feedback_mentions"])
        self.assertFalse(EVIDENCE["russian_evidence"]["aggregate_activity_alone_may_satisfy_found_and_used"])

    def test_store_card_03_crown_trick_concrete_card_is_accepted_without_author(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick", transient_author_tokens=("card-a", "card-b"))
        self.assertIs(self.validate(doc, now), doc)
        parent = doc["provenance"]["sources"][1]
        self.assertEqual(parent["feedback_surface_mode"], "concrete_item_collection")
        self.assertEqual(parent["url"], "https://store.steampowered.com/app/1000010/?l=russian")
        self.assertTrue(all(r["acquisition_mode"] == "inspected_collection_item" for r in doc["provenance"]["player_feedback_records"]))

    def test_store_card_04_author_identity_is_not_persisted_or_required(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        tokens = ("legacy-author-marker", "https://steamcommunity.com/id/private/")
        doc = fallback_dossier(1000010, now, title="Crown Trick", transient_author_tokens=tokens)
        self.assertIs(self.validate(doc, now), doc)
        payload = json.dumps(doc, ensure_ascii=False)
        for token in tokens:
            self.assertNotIn(token, payload)
        self.assertFalse(EVIDENCE["feedback_item_identity"]["relaxed_mode_author_identity_required"])

    def test_store_card_05_store_page_is_parent_provenance_not_feedback_item(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick")
        self.assertIs(self.validate(doc, now), doc)
        parent = doc["provenance"]["sources"][1]
        self.assertTrue(parent["player_feedback"])
        self.assertEqual(parent["feedback_surface_mode"], "concrete_item_collection")
        self.assertFalse(EVIDENCE["source_policy"]["steam_store_app_page_is_player_feedback_record"])
        self.assertTrue(EVIDENCE["feedback_item_identity"]["collection_surface_is_parent_provenance_not_feedback_item"])

    def test_store_card_06_stable_locator_remains_preferred_auditability(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        stable = web_dossier(1000360, now, title="Hellish Quart")
        self.assertIs(self.validate(stable, now), stable)
        self.assertEqual(
            EVIDENCE["feedback_item_identity"]["preferred_auditability_order"],
            ["stable_item", "inspected_collection_item", "search_result_observation"],
        )
        self.assertIn("most auditable mode", PROMPT)

    def test_store_card_07_exact_appid_mismatch_is_rejected(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick")
        doc["provenance"]["sources"][1]["url"] = "https://store.steampowered.com/app/999999/?l=russian"
        with self.assertRaisesRegex(ValueError, "appid does not match exact dossier appid"):
            self.validate(doc, now)

    def test_store_card_08_collection_records_do_not_need_stable_locator_threshold(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick", transient_author_tokens=("card-a", "card-b"))
        doc["observations"][0]["recurrence"] = "moderate"
        doc["evidence"]["overall_strength"] = "moderate"
        self.assertIs(self.validate(doc, now), doc)

    def test_store_card_09_russian_collection_card_can_satisfy_found_and_used(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick")
        self.assertEqual(doc["evidence"]["russian_attempt"], "found_and_used")
        self.assertEqual(doc["provenance"]["player_feedback_records"][0]["language"], "russian")
        self.assertIs(self.validate(doc, now), doc)

    def test_store_card_10_no_concrete_card_means_no_feedback_record(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick")
        doc["provenance"]["player_feedback_records"] = []
        with self.assertRaisesRegex(ValueError, "player_feedback_records must be a non-empty list"):
            self.validate(doc, now)

    def test_store_card_11_current_group_shape_validates_under_new_acquisition_model(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        crown = fallback_dossier(1000010, now, title="Crown Trick", transient_author_tokens=("card-a", "card-b"))
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
        self.assertEqual([d["appid"] for d in validated], ["1000010", "1000360", "1003590"])
        self.assertEqual(crown["provenance"]["player_feedback_records"][0]["acquisition_mode"], "inspected_collection_item")
        self.assertTrue(all(r["acquisition_mode"] == "stable_item" for r in hellish["provenance"]["player_feedback_records"]))
        self.assertTrue(all(r["acquisition_mode"] == "stable_item" for r in tetris["provenance"]["player_feedback_records"]))


if __name__ == "__main__":
    unittest.main()
