#!/usr/bin/env python3
import json
import tempfile
import unittest
from pathlib import Path

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
    def test_story_dlc_01_current_bg3_digital_deluxe_excluded(self):
        queue_path = ROOT / "data/production/pre_ai/chatgpt_taste_queue.jsonl"
        current = [
            json.loads(line)
            for line in queue_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        bg3 = next(x for x in current if str(x.get("appid")) == "2378500")
        classified = classify_story_dlc_scope(bg3)
        self.assertEqual(classified["classification"], "non_story_dlc_excluded")
        self.assertFalse(classified["eligible"])
        self.assertIn("digital_deluxe", classified["matched_signals"])

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

    def test_story_dlc_04_ambiguous_addon_fails_closed(self):
        item = row(4001, "Arena Add-on", "Adds new maps, characters and weapons for an additional mode.")
        classified = classify_story_dlc_scope(item)
        self.assertEqual(classified["classification"], "story_content_unproven_excluded")
        self.assertFalse(classified["eligible"])

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
        summary = manifest["story_dlc_scope"]
        self.assertEqual(summary["considered_count"], 1)
        self.assertEqual(summary["story_eligible_count"], 0)
        self.assertEqual(summary["non_story_excluded_count"], 1)
        self.assertEqual(summary["ambiguous_excluded_count"], 0)


if __name__ == "__main__":
    unittest.main()
