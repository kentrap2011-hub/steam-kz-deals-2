#!/usr/bin/env python3
import copy
import json
import unittest
from datetime import datetime, timezone

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_strict import (
    derive_dossier_summary,
    validate_dossier_strict,
    validate_dossiers_against_expected_items,
)
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

    def test_store_card_01_store_page_itself_remains_invalid_feedback_item(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick")
        record = doc["provenance"]["player_feedback_records"][0]
        record.update({
            "identity_mode": "stable_locator",
            "public_ref": "120-russian-reviews",
        })
        with self.assertRaisesRegex(ValueError, "stable-locator path cannot rely on a collection-only Steam Store parent"):
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
        self.assertFalse(EVIDENCE["source_policy"]["steam_store_parent_aggregate_metadata_may_satisfy_russian_found_and_used"])

    def test_store_card_03_crown_trick_concrete_card_fallback_is_accepted(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick", transient_author_tokens=("crown-a", "crown-b"))
        self.assertIs(self.validate(doc, now), doc)
        parent = doc["provenance"]["sources"][1]
        self.assertEqual(parent["feedback_surface_mode"], "concrete_item_collection")
        self.assertEqual(parent["url"], "https://store.steampowered.com/app/1000010/?l=russian")
        self.assertEqual([r["identity_mode"] for r in doc["provenance"]["player_feedback_records"]], ["transient_author_deduped", "transient_author_deduped"])

    def test_store_card_04_author_identity_is_not_persisted(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        tokens = ("steam-user-crown-a", "https://steamcommunity.com/id/crown-private/")
        doc = fallback_dossier(1000010, now, title="Crown Trick", transient_author_tokens=tokens)
        self.assertIs(self.validate(doc, now), doc)
        payload = json.dumps(doc, ensure_ascii=False)
        for token in tokens:
            self.assertNotIn(token, payload)
        self.assertNotIn("/id/", payload)

    def test_store_card_05_store_page_is_parent_only_provenance(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick")
        self.assertIs(self.validate(doc, now), doc)
        parent = doc["provenance"]["sources"][1]
        self.assertTrue(parent["player_feedback"])
        self.assertEqual(parent["feedback_surface_mode"], "concrete_item_collection")
        self.assertFalse(EVIDENCE["source_policy"]["steam_store_app_page_is_player_feedback_record"])
        self.assertTrue(EVIDENCE["source_policy"]["fallback_parent_is_not_itself_a_feedback_record_or_mention"])

    def test_store_card_06_stable_locator_remains_preferred(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        stable = web_dossier(1000360, now, title="Hellish Quart")
        self.assertIs(self.validate(stable, now), stable)
        self.assertEqual(EVIDENCE["feedback_item_identity"]["preferred_identity_order"], ["stable_locator", "transient_author_deduped"])
        self.assertTrue(EVIDENCE["feedback_item_identity"]["fallback_forbidden_when_neutral_item_locator_available"])
        self.assertFalse(EVIDENCE["feedback_item_identity"]["steam_store_exact_app_parent_allowed_for_stable_locator"])
        self.assertIn("If a neutral `recommendationid` or other accepted stable item locator is available", PROMPT)

    def test_store_card_07_exact_appid_mismatch_is_rejected(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick")
        doc["provenance"]["sources"][1]["url"] = "https://store.steampowered.com/app/999999/?l=russian"
        with self.assertRaisesRegex(ValueError, "appid does not match exact dossier appid"):
            self.validate(doc, now)

    def test_store_card_08_fallback_recurrence_caps_are_unchanged(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick", transient_author_tokens=("a", "b", "c"))
        doc["observations"][0]["recurrence"] = "moderate"
        doc["evidence"]["overall_strength"] = "moderate"
        with self.assertRaisesRegex(ValueError, "moderate recurrence requires at least three stable-locator records"):
            self.validate(doc, now)

    def test_store_card_09_russian_fallback_can_satisfy_found_and_used(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick")
        self.assertEqual(doc["evidence"]["russian_attempt"], "found_and_used")
        self.assertEqual(doc["provenance"]["player_feedback_records"][0]["language"], "russian")
        self.assertIs(self.validate(doc, now), doc)

    def test_store_card_10_no_concrete_card_means_no_fallback(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(1000010, now, title="Crown Trick")
        doc["provenance"]["player_feedback_records"] = []
        with self.assertRaisesRegex(ValueError, "references unknown player-feedback record"):
            self.validate(doc, now)

    def test_store_card_11_current_g000001_three_game_candidate_shape_validates(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        crown = fallback_dossier(1000010, now, title="Crown Trick", transient_author_tokens=("crown-a", "crown-b"))
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
        self.assertEqual(crown["provenance"]["player_feedback_records"][0]["identity_mode"], "transient_author_deduped")
        self.assertTrue(all(r.get("identity_mode", "stable_locator") == "stable_locator" for r in hellish["provenance"]["player_feedback_records"]))
        self.assertTrue(all(r.get("identity_mode", "stable_locator") == "stable_locator" for r in tetris["provenance"]["player_feedback_records"]))


if __name__ == "__main__":
    unittest.main()
