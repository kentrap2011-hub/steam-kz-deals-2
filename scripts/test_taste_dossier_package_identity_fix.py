#!/usr/bin/env python3
import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_web import (
    build_daily_work_manifest_web,
    resolve_dossier_scope_identities,
)
from taste_steam_review_dossier_worker_projection import build_worker_projection

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
NOW = datetime(2026, 9, 16, 3, 0, tzinfo=timezone.utc)


def _app_row(appid, title):
    return {
        "family_id": f"game:{appid}",
        "taste_subject_key": f"App_{appid}",
        "appid": str(appid),
        "title": title,
        "taste_fingerprint": "a" * 64,
        "candidate_context_sha256": "b" * 64,
        "bundle_members": [],
        "work_required": ["evaluate_taste_fit"],
        "semantic_condition": {
            "ai_condition": "taste_subject_include_controls_purchase_family",
            "requires_ai_base_support": False,
            "base_appids": [str(appid)],
        },
    }


class PackageIdentityFixTests(unittest.TestCase):
    def test_ordinary_app_row_identity_is_unchanged(self):
        row = _app_row("1000360", "Hellish Quart")
        resolution = resolve_dossier_scope_identities([copy.deepcopy(row)], CONTRACT)
        self.assertEqual(resolution["identity_blocked_items"], [])
        self.assertEqual(resolution["deduplicated_row_count"], 0)
        self.assertEqual(resolution["rows"], [{
            "key": "App_1000360",
            "appid": "1000360",
            "title": "Hellish Quart",
            "taste_fingerprint": "a" * 64,
            "candidate_context_sha256": "b" * 64,
            "work_required": ["evaluate_taste_fit"],
        }])

    def test_single_game_package_maps_to_exact_game_and_retains_offer_identity(self):
        row = {
            "family_id": "bundle:Sub_123",
            "taste_subject_key": "Sub_123",
            "appid": "999999",
            "title": "Example Deluxe Package",
            "taste_fingerprint": "c" * 64,
            "candidate_context_sha256": "d" * 64,
            "bundle_members": [
                {"appid": "222222", "name": "Canonical Example Game"},
                {"appid": "333333", "name": "Cosmetic Add-on"},
            ],
            "work_required": ["evaluate_taste_fit"],
            "semantic_condition": {
                "ai_condition": "bundle_or_package_taste_evaluation_required",
                "requires_ai_base_support": False,
                "base_appids": ["222222"],
            },
        }
        resolution = resolve_dossier_scope_identities([copy.deepcopy(row)], CONTRACT)
        self.assertEqual(resolution["identity_blocked_items"], [])
        target = resolution["rows"][0]
        self.assertEqual((target["appid"], target["title"]), ("222222", "Canonical Example Game"))
        self.assertEqual(target["offer_identity"], {
            "key": "Sub_123",
            "family_id": "bundle:Sub_123",
            "title": "Example Deluxe Package",
            "source_row_appid": "999999",
        })
        self.assertEqual(target["dossier_identity_resolution"], "single_canonical_base_appid_and_bundle_member_title")

    def test_sub_87601_is_blocked_before_dedupe_and_worker_projection(self):
        queue_path = ROOT / "data/production/pre_ai/chatgpt_taste_queue.jsonl"
        all_rows = [json.loads(line) for line in queue_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        first_rows = all_rows[:4]
        coherent_app_304240 = next(row for row in all_rows if row["taste_subject_key"] == "App_304240")
        queue_rows = first_rows + [coherent_app_304240]
        original = copy.deepcopy(queue_rows)

        sub = next(row for row in queue_rows if row["taste_subject_key"] == "Sub_87601")
        self.assertEqual(sub["appid"], "304240")
        self.assertIn("Deluxe Origins Bundle", sub["title"])
        self.assertEqual(sub["semantic_condition"]["base_appids"], ["304240", "339340"])
        self.assertEqual((coherent_app_304240["appid"], coherent_app_304240["title"]), ("304240", "Resident Evil"))

        resolution = resolve_dossier_scope_identities(queue_rows, CONTRACT)
        resolved_by_key = {row["key"]: row for row in resolution["rows"]}
        self.assertNotIn("Sub_87601", resolved_by_key)
        self.assertEqual(
            (resolved_by_key["App_304240"]["appid"], resolved_by_key["App_304240"]["title"]),
            ("304240", "Resident Evil"),
            "blocked package must not consume appid dedupe identity before the coherent App row",
        )
        blocked = next(item for item in resolution["identity_blocked_items"] if item["key"] == "Sub_87601")
        self.assertEqual(blocked["reason"], "ambiguous_multi_game_offer_no_single_dossier_identity")
        self.assertEqual(blocked["candidate_game_appids"], ["304240", "339340"])
        self.assertEqual(blocked["offer_identity"]["source_row_appid"], "304240")
        self.assertIn("Deluxe Origins Bundle", blocked["offer_identity"]["title"])
        self.assertEqual(queue_rows, original, "dossier projection must not mutate/remove the package offer")

        with tempfile.TemporaryDirectory() as td:
            manifest = build_daily_work_manifest_web(queue_rows, CONTRACT, td, now=NOW)
            _, descriptors = build_worker_projection(manifest, CONTRACT)

        self.assertEqual(manifest["source_row_count"], 5)
        self.assertEqual(manifest["eligible_row_count"], 5)
        self.assertEqual(manifest["identity_blocked_count"], 1)
        self.assertEqual(manifest["completed_required_count"], 0)
        self.assertEqual(manifest["prepared_required_count"], 4)
        self.assertEqual([item["key"] for item in manifest["prepared_required_items"][:3]], [
            "App_2378500", "App_1000360", "App_1003590",
        ])
        self.assertEqual(
            (manifest["prepared_required_items"][3]["key"], manifest["prepared_required_items"][3]["appid"], manifest["prepared_required_items"][3]["title"]),
            ("App_304240", "304240", "Resident Evil"),
        )
        first_items = descriptors[0]["items"]
        self.assertEqual([(item["key"], item["appid"], item["title"]) for item in first_items[:3]], [
            ("App_2378500", "2378500", "Baldur's Gate 3 - Digital Deluxe Edition DLC"),
            ("App_1000360", "1000360", "Hellish Quart"),
            ("App_1003590", "1003590", "Tetris® Effect: Connected"),
        ])
        self.assertIn(("App_304240", "304240", "Resident Evil"), [
            (item["key"], item["appid"], item["title"])
            for descriptor in descriptors for item in descriptor["items"]
        ])
        self.assertFalse(any(
            item["appid"] == "304240" and "Deluxe Origins Bundle" in item["title"]
            for descriptor in descriptors for item in descriptor["items"]
        ))

    def test_v2_descriptor_identity_contract_remains_exact_title_and_appid(self):
        contract = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["identity"]["required_work_binding"], ["exact_descriptor_title", "exact_descriptor_appid"])
        self.assertEqual(contract["identity"]["ambiguous_identity_behavior"], "fail_closed_no_dossier")


if __name__ == "__main__":
    unittest.main()
