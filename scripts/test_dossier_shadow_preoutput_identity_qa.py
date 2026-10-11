"""Synthetic ONLY: identity/year audit frame, categories, date kind, and whole group."""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from dossier_shadow_preoutput_identity_qa import (
    EXPECTED, NEEDED_SOURCE_CATEGORIES, inspect, compatibility_check,
)

DATA = HERE.parent / "reviews/dossier_shadow_preoutput/identity_year_20_groups_v1.json"


class FrozenIdentityAuditTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(DATA.read_text(encoding="utf-8"))

    def row(self, appid):
        return next(game for group in self.payload["groups"] for game in group["games"]
                    if game["appid"] == str(appid))

    def test_pinned_complete_real_frame_offline(self):
        self.assertEqual(inspect(self.payload), [])
        self.assertEqual([g["sequence"] for g in self.payload["groups"]], list(EXPECTED))
        self.assertEqual(sum(len(g["games"]) for g in self.payload["groups"]), 60)
        self.assertEqual(self.payload["metrics"]["old_year_binding_conflict_candidates"], 3)
        self.assertEqual(self.payload["metrics"]["independently_verified_original_work_year"], 5)

    def test_exact_independent_conflict_evidence(self):
        self.assertEqual({x["appid"] for group in self.payload["groups"] for x in group["games"]
                          if x["disagrees_with_old_binding"]},
                         {"1638220", "213610", "2138710"})
        self.assertEqual(self.row(2140020)["same_version_comparison"],
                         "not_comparable_distinct_definitive_edition")

    def test_missing_group_fails_closed(self):
        p = copy.deepcopy(self.payload)
        p["groups"].pop()
        self.assertIn("FRAME_NOT_EXACT_20_GROUPS", inspect(p))

    def test_original_title_and_binding_claim_are_frozen(self):
        p = copy.deepcopy(self.payload)
        p["groups"][0]["games"][0]["work_title"] = "Different title, same AppID"
        p["groups"][0]["games"][1]["original_work_year_binding_claim"] = 2025
        self.assertIn("HISTORICAL_GAME_TITLE_OR_YEAR_BINDING_CHANGED", inspect(p))

    def test_swapped_or_split_group_rejected(self):
        p = copy.deepcopy(self.payload)
        p["groups"][0]["games"][0], p["groups"][1]["games"][0] = (
            p["groups"][1]["games"][0], p["groups"][0]["games"][0])
        self.assertIn("GROUP_SPLIT_OR_APPID_REBOUND", inspect(p))

    def test_original_work_year_cannot_be_steam_store_only(self):
        p = copy.deepcopy(self.payload)
        row = next(x for group in p["groups"] for x in group["games"]
                   if x["appid"] == "1562430")
        row["verified_original_work_year"] = 2023
        row["date_unknown"] = False
        row["original_work_provenance_state"] = "claimed_from_store_only"
        self.assertIn("ORIGINAL_YEAR_INFERRED_FROM_STORE_ONLY", inspect(p))

    def test_unknown_cannot_silently_become_pass(self):
        p = copy.deepcopy(self.payload)
        self.assertTrue(self.row("1202690")["date_unknown"])
        p["groups"][0]["games"][1]["date_unknown"] = False
        self.assertIn("UNKNOWN_CONVERTED_TO_KNOWN", inspect(p))

    def test_claimed_wrong_year_requires_real_work_proof(self):
        p = copy.deepcopy(self.payload)
        p["groups"][0]["games"][0]["disagrees_with_old_binding"] = True
        self.assertIn("CLAIMED_CONFLICT_WITHOUT_POSITIVE_ORIGINAL_WORK_PROOF", inspect(p))

    def test_edition_year_cannot_be_treated_as_original_conflict(self):
        p = copy.deepcopy(self.payload)
        row = next(x for group in p["groups"] for x in group["games"]
                   if x["appid"] == "2140020")
        row["disagrees_with_old_binding"] = True
        self.assertIn("DIFFERENT_VERSIONS_CALLED_CONFLICT", inspect(p))

    def test_missing_category_not_approved(self):
        p = copy.deepcopy(self.payload)
        outcome = compatibility_check(p, [3, 8, 13, 15, 18, 20],
                                      {category: "not_measured" for category in NEEDED_SOURCE_CATEGORIES})
        self.assertIn("PREOUTPUT_CATEGORY_ABSENT_OR_UNVERIFIED", outcome["errors"])
        self.assertFalse(outcome["pilot_authorized"])

    def test_six_eighteen_overclaim_and_group_split(self):
        self.assertIn("SIX_GROUPS_OVERCLAIM",
                      compatibility_check(self.payload, [3, 8, 13, 15, 18])["errors"])
        self.assertIn("ORIGINAL_GROUP_SPLIT_OR_OUTSIDE_FRAME",
                      compatibility_check(self.payload, [3, 8, 13, 15, 999, 20])["errors"])
        self.assertEqual(compatibility_check(self.payload, [3, 8, 13, 15, 18, 20])["proposed_game_count"], 18)

    def test_no_future_source_metadata_is_not_approval(self):
        a = compatibility_check(self.payload, [3, 8, 13, 15, 18, 20])
        self.assertEqual(a["state"], "PREOUTPUT_DECISION_ONLY_NOT_READY_FOR_APPROVAL")
        self.assertIn("CHAT1_SOURCE_METADATA_NOT_INDEPENDENTLY_DELIVERED", a["errors"])
        self.assertFalse(a["semantic_execution"])
        self.assertEqual(sum(v == "not_measured" for v in a["source_categories"].values()),
                         len(NEEDED_SOURCE_CATEGORIES))

    def test_invalid_frozen_pin_or_production_flag_rejected(self):
        p = copy.deepcopy(self.payload)
        p["immutable_source"]["pinned_commit"] = "0" * 40
        p["pilot_authorized"] = True
        self.assertEqual(set(inspect(p)), {"PIN_DRIFT", "INACTIVE_AUTHORITY_OVERRIDDEN"})


if __name__ == "__main__":
    unittest.main()
