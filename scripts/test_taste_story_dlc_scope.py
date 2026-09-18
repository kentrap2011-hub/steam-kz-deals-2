#!/usr/bin/env python3
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_web import (
    build_daily_work_manifest_web,
    classify_story_dlc_scope,
    resolve_dossier_scope_identities,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
NOW = datetime(2026, 9, 18, 8, 0, tzinfo=timezone.utc)


def _addon_row(appid, title, short_description):
    return {
        "family_id": f"addon:App_{appid}",
        "taste_subject_key": f"App_{appid}",
        "appid": str(appid),
        "title": title,
        "taste_fingerprint": "a" * 64,
        "candidate_context_sha256": "b" * 64,
        "short_description": short_description,
        "bundle_members": [],
        "work_required": ["evaluate_taste_fit"],
        "semantic_condition": {
            "ai_condition": "addon_taste_include_and_base_support_required",
            "requires_ai_base_support": True,
            "base_appids": ["999"],
        },
    }


def _base_row(appid, title, short_description=""):
    return {
        "family_id": f"game:{appid}",
        "taste_subject_key": f"App_{appid}",
        "appid": str(appid),
        "title": title,
        "taste_fingerprint": "c" * 64,
        "candidate_context_sha256": "d" * 64,
        "short_description": short_description,
        "bundle_members": [],
        "work_required": ["evaluate_taste_fit"],
        "semantic_condition": {
            "ai_condition": "taste_subject_include_controls_purchase_family",
            "requires_ai_base_support": False,
            "base_appids": [str(appid)],
        },
    }


class StoryDlcScopePolicyTests(unittest.TestCase):
    def test_story_dlc_01_bg3_digital_deluxe_excluded(self):
        queue_path = ROOT / "data/production/pre_ai/chatgpt_taste_queue.jsonl"
        rows = [json.loads(line) for line in queue_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        row = next(item for item in rows if str(item.get("appid")) == "2378500")

        classification = classify_story_dlc_scope(row, CONTRACT)
        self.assertEqual(classification["classification"], "non_story_dlc_excluded")
        self.assertEqual(classification["reason_code"], "explicit_non_story_product_metadata")
        self.assertIn("digital deluxe", classification["matched_non_story_signals"])

        resolution = resolve_dossier_scope_identities([row], CONTRACT)
        self.assertEqual(resolution["rows"], [])
        self.assertEqual(resolution["story_dlc_scope_summary"], {
            "dlc_like_considered": 1,
            "story_eligible": 0,
            "non_story_excluded": 1,
            "ambiguous_excluded": 0,
        })

    def test_story_dlc_02_obvious_non_story_addons_excluded(self):
        fixtures = [
            _addon_row("200001", "Example Original Soundtrack", "Includes the original game soundtrack and bonus songs."),
            _addon_row("200002", "Example Digital Artbook", "A digital artbook with concept art and wallpapers."),
            _addon_row("200003", "Example Cosmetic Pack", "Adds cosmetic skins and avatars."),
            _addon_row("200004", "Example Item Pack", "Adds an item pack with new weapons and equipment."),
        ]
        resolution = resolve_dossier_scope_identities(fixtures, CONTRACT)
        self.assertEqual(resolution["rows"], [])
        self.assertEqual(resolution["story_dlc_scope_summary"]["non_story_excluded"], 4)
        self.assertTrue(all(
            item["classification"] == "non_story_dlc_excluded"
            for item in resolution["story_dlc_classifications"]
        ))

    def test_story_dlc_03_confirmed_story_expansion_included(self):
        row = _addon_row(
            "200010",
            "Example: The Lost Chapter",
            "Adds a new story campaign, a new questline, and several new locations.",
        )
        classification = classify_story_dlc_scope(row, CONTRACT)
        self.assertEqual(classification["classification"], "story_dlc_eligible")
        resolution = resolve_dossier_scope_identities([row], CONTRACT)
        self.assertEqual([item["appid"] for item in resolution["rows"]], ["200010"])

    def test_story_dlc_04_ambiguous_dlc_fails_closed(self):
        row = _addon_row(
            "200020",
            "Example Additional Content",
            "Adds new content, challenges, and additional gameplay options.",
        )
        classification = classify_story_dlc_scope(row, CONTRACT)
        self.assertEqual(classification["classification"], "story_content_unproven_excluded")
        self.assertEqual(classification["reason_code"], "positive_story_content_evidence_missing")
        self.assertEqual(resolve_dossier_scope_identities([row], CONTRACT)["rows"], [])

    def test_story_dlc_05_mixed_story_and_cosmetics_is_included(self):
        row = _addon_row(
            "200030",
            "Example Story Expansion Deluxe Pack",
            "Adds a new story campaign and questline, plus cosmetic skins and a digital artbook.",
        )
        classification = classify_story_dlc_scope(row, CONTRACT)
        self.assertEqual(classification["classification"], "story_dlc_eligible")
        self.assertTrue(classification["matched_story_signals"])
        self.assertTrue(classification["matched_non_story_signals"])
        self.assertEqual(
            [item["appid"] for item in resolve_dossier_scope_identities([row], CONTRACT)["rows"]],
            ["200030"],
        )

    def test_story_dlc_06_season_pass_container_is_not_story_object(self):
        row = _addon_row(
            "200040",
            "Example Season Pass",
            "Grants access to two story expansions, each with a new story campaign.",
        )
        classification = classify_story_dlc_scope(row, CONTRACT)
        self.assertEqual(classification["classification"], "non_story_dlc_excluded")
        self.assertEqual(classification["reason_code"], "entitlement_container_not_independent_story_content")
        self.assertEqual(resolve_dossier_scope_identities([row], CONTRACT)["rows"], [])

    def test_story_dlc_07_base_game_is_unaffected(self):
        row = _base_row("200050", "Example Base Game", "A sandbox RPG with no DLC metadata.")
        self.assertIsNone(classify_story_dlc_scope(row, CONTRACT))
        resolution = resolve_dossier_scope_identities([row], CONTRACT)
        self.assertEqual([item["appid"] for item in resolution["rows"]], ["200050"])
        self.assertEqual(resolution["story_dlc_scope_summary"]["dlc_like_considered"], 0)

    def test_story_dlc_08_current_group_plan_regeneration_excludes_bg3_deluxe(self):
        queue_path = ROOT / "data/production/pre_ai/chatgpt_taste_queue.jsonl"
        rows = [json.loads(line) for line in queue_path.read_text(encoding="utf-8").splitlines() if line.strip()]

        with tempfile.TemporaryDirectory() as td:
            manifest = build_daily_work_manifest_web(
                rows,
                CONTRACT,
                td,
                now=NOW,
                source_queue_path=queue_path.as_posix(),
            )

        self.assertEqual(manifest["story_dlc_scope_summary"], {
            "dlc_like_considered": 1,
            "story_eligible": 0,
            "non_story_excluded": 1,
            "ambiguous_excluded": 0,
        })
        self.assertNotIn("2378500", manifest["ordered_appids"])
        self.assertNotIn("2378500", [item["appid"] for item in manifest["prepared_required_items"]])
        self.assertEqual(manifest["prepared_required_count"], 731)
        self.assertEqual(manifest["submission_group_plan"]["checkpoint_size"], 3)
        self.assertEqual(manifest["submission_group_plan"]["group_count"], 244)
        first_group = manifest["submission_group_plan"]["groups"][0]
        self.assertEqual(first_group["sequence"], 1)
        self.assertEqual(first_group["appids"], ["1000010", "1000360", "1003590"])


if __name__ == "__main__":
    unittest.main()
