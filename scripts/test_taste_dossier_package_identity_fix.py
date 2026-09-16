#!/usr/bin/env python3
import copy
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from taste_package_member_aggregation import (
    PACKAGE_MEMBER_AGGREGATION_POLICY,
    aggregate_package_member_taste,
    build_member_subject_index,
)
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


def _taste_row(appid, verdict, fit_level, *, ready=True):
    return {
        "status": "cache_hit",
        "appid": str(appid),
        "taste_subject_title": f"Game {appid}",
        "taste_fingerprint": "c" * 64,
        "candidate_context_sha256": "d" * 64,
        "negative_analysis_ready": ready,
        "fit_evidence_backfill_required": False,
        "cached_taste": {
            "verdict": verdict,
            "fit_level": fit_level,
            "reason_code": "include_strong" if fit_level == "strong" else (
                "include_moderate" if fit_level == "moderate" else "exclude_insufficient"
            ),
        },
    }


class PackageMemberDossierAggregationTests(unittest.TestCase):
    def test_ordinary_app_row_identity_is_unchanged(self):
        row = _app_row("1000360", "Hellish Quart")
        resolution = resolve_dossier_scope_identities([copy.deepcopy(row)], CONTRACT)
        self.assertEqual(resolution["identity_blocked_items"], [])
        self.assertEqual(resolution["package_member_mappings"], [])
        self.assertEqual(resolution["deduplicated_row_count"], 0)
        target = resolution["rows"][0]
        self.assertEqual((target["key"], target["appid"], target["title"]), (
            "App_1000360", "1000360", "Hellish Quart",
        ))
        self.assertEqual(target["offer_identities"], [])
        self.assertEqual(target["dossier_identity_resolution"], "direct_queue_game_identity")

    def test_single_game_package_maps_to_member_dossier_and_retains_offer_mapping(self):
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
        self.assertEqual(len(resolution["rows"]), 1)
        target = resolution["rows"][0]
        self.assertEqual((target["key"], target["appid"], target["title"]), (
            "App_222222", "222222", "Canonical Example Game",
        ))
        self.assertEqual(target["offer_identities"][0]["key"], "Sub_123")
        mapping = resolution["package_member_mappings"][0]
        self.assertEqual(mapping["member_appids"], ["222222"])
        self.assertEqual(mapping["members"][0]["dossier_key"], "App_222222")

    def test_sub_87601_expands_to_two_game_dossiers_and_reuses_direct_app_nodes(self):
        queue_path = ROOT / "data/production/pre_ai/chatgpt_taste_queue.jsonl"
        all_rows = [json.loads(line) for line in queue_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        sub = next(row for row in all_rows if row["taste_subject_key"] == "Sub_87601")
        direct_304240 = next(row for row in all_rows if row["taste_subject_key"] == "App_304240")
        direct_339340 = next(row for row in all_rows if row["taste_subject_key"] == "App_339340")
        queue_rows = [sub, direct_304240, direct_339340]
        original = copy.deepcopy(queue_rows)

        self.assertEqual(sub["semantic_condition"]["base_appids"], ["304240", "339340"])
        self.assertEqual([member["appid"] for member in sub["bundle_members"]], [
            "304240", "339340", "381710", "381711", "381712", "381713",
        ])

        resolution = resolve_dossier_scope_identities(queue_rows, CONTRACT)
        self.assertEqual(resolution["identity_blocked_items"], [])
        self.assertEqual(resolution["eligible_row_count"], 3)
        self.assertEqual(resolution["deduplicated_row_count"], 2)
        self.assertEqual(queue_rows, original, "package expansion must not mutate/remove the commercial offer row")

        by_appid = {row["appid"]: row for row in resolution["rows"]}
        self.assertEqual(set(by_appid), {"304240", "339340"})
        self.assertEqual((by_appid["304240"]["key"], by_appid["304240"]["title"]), (
            "App_304240", "Resident Evil",
        ))
        self.assertEqual((by_appid["339340"]["key"], by_appid["339340"]["title"]), (
            "App_339340", "Resident Evil 0",
        ))
        self.assertEqual(by_appid["304240"]["offer_identities"][0]["key"], "Sub_87601")
        self.assertEqual(by_appid["339340"]["offer_identities"][0]["key"], "Sub_87601")
        self.assertFalse(set(by_appid).intersection({"381710", "381711", "381712", "381713"}))

        mapping = resolution["package_member_mappings"][0]
        self.assertEqual(mapping["offer_identity"]["key"], "Sub_87601")
        self.assertEqual(mapping["member_appids"], ["304240", "339340"])
        self.assertEqual([(m["appid"], m["title"], m["dossier_key"]) for m in mapping["members"]], [
            ("304240", "Resident Evil", "App_304240"),
            ("339340", "Resident Evil 0", "App_339340"),
        ])

        with tempfile.TemporaryDirectory() as td:
            manifest = build_daily_work_manifest_web(queue_rows, CONTRACT, td, now=NOW)
            _, descriptors = build_worker_projection(manifest, CONTRACT)

        self.assertEqual(manifest["identity_blocked_count"], 0)
        self.assertEqual(manifest["package_member_mapping_count"], 1)
        self.assertEqual(manifest["prepared_required_count"], 2)
        self.assertEqual(manifest["ordered_appids"], ["304240", "339340"])
        self.assertEqual([item["appid"] for item in manifest["prepared_required_items"]], ["304240", "339340"])
        self.assertEqual(len({item["dossier_path"] for item in manifest["prepared_required_items"]}), 2)
        self.assertEqual(
            manifest["package_member_mappings"][0]["members"][0]["dossier_path"],
            (Path(CONTRACT["paths"]["dossier_store"]) / "App_304240.json").as_posix(),
        )
        descriptor_items = [item for descriptor in descriptors for item in descriptor["items"]]
        self.assertEqual([(item["appid"], item["title"]) for item in descriptor_items], [
            ("304240", "Resident Evil"),
            ("339340", "Resident Evil 0"),
        ])
        self.assertFalse(any("Deluxe Origins Bundle" in item["title"] for item in descriptor_items))

    def test_best_qualifying_member_keeps_package_eligible_without_average(self):
        families = [
            {
                "family_id": "game:304240", "family_type": "base_game",
                "taste_subject_key": "App_304240", "base_appids": ["304240"],
            },
            {
                "family_id": "game:339340", "family_type": "base_game",
                "taste_subject_key": "App_339340", "base_appids": ["339340"],
            },
            {
                "family_id": "bundle:Sub_87601", "family_type": "franchise_bundle",
                "taste_subject_key": "Sub_87601", "base_appids": ["304240", "339340"],
            },
        ]
        index = build_member_subject_index(families)
        taste = {
            "App_304240": _taste_row("304240", "INCLUDE", "strong"),
            "App_339340": _taste_row("339340", "EXCLUDE", "below_moderate"),
        }
        aggregate = aggregate_package_member_taste(families[2], taste, index)
        self.assertEqual(aggregate["policy"], PACKAGE_MEMBER_AGGREGATION_POLICY)
        self.assertEqual(aggregate["status"], "resolved_eligible")
        self.assertTrue(aggregate["package_taste_eligible"])
        self.assertEqual(aggregate["selected_member"], {
            "appid": "304240",
            "taste_subject_key": "App_304240",
            "verdict": "INCLUDE",
            "fit_level": "strong",
        })
        self.assertNotIn("average", aggregate)

        # Unknown second member must not negate a known qualifying member.
        taste["App_339340"] = {"status": "ai_required"}
        aggregate_unknown = aggregate_package_member_taste(families[2], taste, index)
        self.assertTrue(aggregate_unknown["package_taste_eligible"])
        self.assertEqual(aggregate_unknown["selected_member"]["appid"], "304240")

    def test_no_qualifying_member_with_unresolved_member_waits_on_member_semantics(self):
        families = [
            {
                "family_id": "game:1", "family_type": "base_game",
                "taste_subject_key": "App_1", "base_appids": ["1"],
            },
            {
                "family_id": "game:2", "family_type": "base_game",
                "taste_subject_key": "App_2", "base_appids": ["2"],
            },
            {
                "family_id": "bundle:Sub_9", "family_type": "franchise_bundle",
                "taste_subject_key": "Sub_9", "base_appids": ["1", "2"],
            },
        ]
        taste = {
            "App_1": _taste_row("1", "EXCLUDE", "below_moderate"),
            "App_2": {"status": "ai_required"},
        }
        aggregate = aggregate_package_member_taste(families[2], taste, build_member_subject_index(families))
        self.assertEqual(aggregate["status"], "member_semantic_pending")
        self.assertIsNone(aggregate["package_taste_eligible"])
        self.assertIsNone(aggregate["effective_taste_row"])
        self.assertTrue(aggregate["semantic_dependency_pending"])

    def test_v2_descriptor_identity_contract_remains_exact_title_and_appid(self):
        contract = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["identity"]["required_work_binding"], ["exact_descriptor_title", "exact_descriptor_appid"])
        self.assertEqual(contract["identity"]["ambiguous_identity_behavior"], "fail_closed_no_dossier")


if __name__ == "__main__":
    unittest.main()
