#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

from build_pre_ai_chatgpt_payload import classify_independent_dlc_semantic_scope
from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_web import (
    build_daily_work_manifest_web,
    classify_story_dlc_scope,
    resolve_dossier_scope_identities,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")


def row(appid, title, description, *, addon=True):
    appid = str(appid)
    return {
        "family_id": f"addon:App_{appid}" if addon else f"game:{appid}",
        "taste_subject_key": f"App_{appid}",
        "appid": appid,
        "title": title,
        "taste_fingerprint": "a" * 64,
        "candidate_context_sha256": "b" * 64,
        "short_description": description,
        "bundle_members": [],
        "work_required": ["evaluate_taste_fit"],
        "semantic_condition": {
            "ai_condition": (
                "addon_taste_include_and_base_support_required"
                if addon else "taste_subject_include_controls_purchase_family"
            ),
            "requires_ai_base_support": bool(addon),
            "base_appids": ["100"] if addon else [appid],
        },
    }


class StoryDlcScopeTests(unittest.TestCase):
    def test_story_dlc_01_bg3_digital_deluxe_excluded_before_taste_queue(self):
        bg3 = row(
            2378500,
            "Baldur's Gate 3 - Digital Deluxe Edition DLC",
            "The Digital Deluxe Edition includes both practical and cosmetic in-game items, "
            "such as a unique custom dice skin and the Mask of the Shapeshifter from Divinity: "
            "Original Sin 2. As well as the Original Game Soundtrack for Baldur's Gate 3, "
            "digital Artbook and printable pre-made Origin character sheets",
        )
        classified = classify_story_dlc_scope(bg3)
        self.assertEqual(classified["classification"], "non_story_dlc_excluded")
        self.assertFalse(classified["eligible"])
        self.assertIn("digital_deluxe", classified["matched_signals"])

        family = {
            "family_id": "addon:App_2378500",
            "ai_condition": "addon_taste_include_and_base_support_required",
            "requires_ai_base_support": True,
            "base_appids": ["1086940"],
        }
        taste_row = {
            "appid": "2378500",
            "taste_subject_title": bg3["title"],
            "short_description": bg3["short_description"],
        }
        upstream = classify_independent_dlc_semantic_scope(family, taste_row)
        self.assertEqual(upstream["classification"], "non_story_dlc_excluded")
        self.assertFalse(upstream["eligible"])

    def test_story_dlc_02_obvious_non_story_addons_excluded(self):
        fixtures = [
            row(2001, "Game OST", "The original soundtrack and bonus songs from the game."),
            row(2002, "Digital Artbook", "A digital artbook with concept art and wallpapers."),
            row(2003, "Cosmetic Pack", "A cosmetic pack with character skins."),
            row(2004, "Equipment Pack", "An equipment pack containing weapon and item packs."),
        ]
        resolution = resolve_dossier_scope_identities(fixtures, CONTRACT)
        self.assertEqual(resolution["rows"], [])
        self.assertEqual(resolution["story_dlc_scope"]["non_story_excluded_count"], 4)

    def test_story_dlc_03_real_story_expansion_included(self):
        item = row(3001, "The Lost Chapter", "Adds a new story campaign with a separate questline and playable encounters.")
        classified = classify_story_dlc_scope(item)
        self.assertEqual(classified["classification"], "story_dlc_eligible")
        self.assertTrue(classified["eligible"])
        resolution = resolve_dossier_scope_identities([item], CONTRACT)
        self.assertEqual([x["appid"] for x in resolution["rows"]], ["3001"])
        family = {
            "family_id": item["family_id"],
            "ai_condition": item["semantic_condition"]["ai_condition"],
            "requires_ai_base_support": True,
            "base_appids": ["100"],
        }
        taste_row = {
            "appid": item["appid"],
            "taste_subject_title": item["title"],
            "short_description": item["short_description"],
        }
        self.assertTrue(classify_independent_dlc_semantic_scope(family, taste_row)["eligible"])

    def test_story_dlc_04_ambiguous_addon_fails_closed(self):
        item = row(4001, "Arena Add-on", "Adds new maps, characters and weapons for an additional mode.")
        classified = classify_story_dlc_scope(item)
        self.assertEqual(classified["classification"], "story_content_unproven_excluded")
        self.assertFalse(classified["eligible"])
        family = {
            "family_id": item["family_id"],
            "ai_condition": item["semantic_condition"]["ai_condition"],
            "requires_ai_base_support": True,
            "base_appids": ["100"],
        }
        taste_row = {
            "appid": item["appid"],
            "taste_subject_title": item["title"],
            "short_description": item["short_description"],
        }
        upstream = classify_independent_dlc_semantic_scope(family, taste_row)
        self.assertEqual(upstream["classification"], "story_content_unproven_excluded")
        self.assertFalse(upstream["eligible"])

    def test_story_dlc_05_mixed_story_and_cosmetics_remains_eligible(self):
        item = row(5001, "Story & Bonus Pack", "Adds a new story campaign and questline, plus cosmetic skins and a soundtrack.")
        classified = classify_story_dlc_scope(item)
        self.assertEqual(classified["classification"], "story_dlc_eligible")
        self.assertTrue(classified["eligible"])

    def test_story_dlc_06_season_pass_container_not_story_identity(self):
        item = row(6001, "Season Pass", "Grants access to a story expansion, two cosmetic packs and future DLC.")
        classified = classify_story_dlc_scope(item)
        self.assertEqual(classified["classification"], "non_story_dlc_excluded")
        self.assertEqual(classified["reason"], "container_entitlement_is_not_independent_story_identity")
        self.assertFalse(classified["eligible"])

    def test_story_dlc_07_base_game_unaffected(self):
        item = row(7001, "Base Game", "A competitive action game with maps and weapons.", addon=False)
        self.assertIsNone(classify_story_dlc_scope(item))
        family = {
            "family_id": item["family_id"],
            "ai_condition": item["semantic_condition"]["ai_condition"],
            "requires_ai_base_support": False,
            "base_appids": [item["appid"]],
        }
        taste_row = {
            "appid": item["appid"],
            "taste_subject_title": item["title"],
            "short_description": item["short_description"],
        }
        self.assertIsNone(classify_independent_dlc_semantic_scope(family, taste_row))
        resolution = resolve_dossier_scope_identities([item], CONTRACT)
        self.assertEqual([x["appid"] for x in resolution["rows"]], ["7001"])

    def test_story_dlc_08_regenerated_current_group_plan_excludes_bg3(self):
        queue_path = ROOT / "data/production/pre_ai/chatgpt_taste_queue.jsonl"
        current = [
            json.loads(line)
            for line in queue_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        with tempfile.TemporaryDirectory() as td:
            manifest = build_daily_work_manifest_web(current, CONTRACT, td)
        self.assertNotIn("2378500", manifest["ordered_appids"])
        group_appids = [
            appid
            for group in manifest["submission_group_plan"]["groups"]
            for appid in group["appids"]
        ]
        self.assertNotIn("2378500", group_appids)

        # Before activation the checked-in queue may still contain the old BG3 row;
        # after activation it must not. The dossier gate remains defense in depth
        # in either state, so this regression is intentionally count-agnostic.
        summary = manifest["story_dlc_scope"]
        self.assertEqual(
            summary["considered_count"],
            summary["story_eligible_count"]
            + summary["non_story_excluded_count"]
            + summary["ambiguous_excluded_count"],
        )


if __name__ == "__main__":
    unittest.main()
