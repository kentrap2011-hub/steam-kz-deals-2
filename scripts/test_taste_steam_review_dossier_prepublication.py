#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier_buffered import plan_buffered_drain, validate_buffer_artifact
from taste_steam_review_dossier_daily import BUFFER_GROUP_SCHEMA, build_daily_work_manifest, load_contract
from taste_steam_review_dossier_prepublication import validate_prepublication_artifact
from taste_steam_review_dossier_recovery import quarantine_stale_snapshot_inbox
from taste_steam_review_dossier_strict import derive_dossier_summary
from taste_steam_review_dossier_test_fixture import web_dossier

ROOT = Path(__file__).resolve().parents[1]
BASE_CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
NOW = datetime(2026, 9, 16, 20, 0, tzinfo=timezone.utc)


def queue(appids):
    rows = []
    for i, appid in enumerate(appids):
        rows.append({
            "taste_subject_key": f"App_{appid}_{i}",
            "appid": str(appid),
            "title": f"Game {appid}",
            "taste_fingerprint": hashlib.sha256(f"taste:{appid}:{i}".encode()).hexdigest(),
            "candidate_context_sha256": hashlib.sha256(f"ctx:{appid}:{i}".encode()).hexdigest(),
            "work_required": ["resolve_grounded_negative_analysis"],
        })
    return rows


def build_group(work, sequence=1):
    descriptor = work["submission_group_plan"]["groups"][sequence - 1]
    return {
        "schema": BUFFER_GROUP_SCHEMA,
        "schema_version": 1,
        **copy.deepcopy(descriptor),
        "dossiers": [
            web_dossier(item["appid"], NOW, title=item["title"])
            for item in descriptor["items"]
        ],
    }


class PrepublicationParityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.contract = copy.deepcopy(BASE_CONTRACT)
        root = Path(self.temp.name)
        self.contract["paths"]["submission_inbox_dir"] = (root / "buffer").as_posix()
        self.work = build_daily_work_manifest(
            queue([710001, 710002, 710003]),
            self.contract,
            root / "store",
            now=NOW,
        )
        self.descriptor = self.work["submission_group_plan"]["groups"][0]

    def assert_same_failure(self, mutate, expected):
        artifact = build_group(self.work)
        mutate(artifact)
        with self.assertRaisesRegex(ValueError, expected):
            validate_prepublication_artifact(copy.deepcopy(artifact), self.work, self.contract)
        with self.assertRaisesRegex(ValueError, expected):
            validate_buffer_artifact(copy.deepcopy(artifact), self.descriptor, self.work, self.contract)

    def test_group_size_remains_three_and_valid_group_passes_both_paths(self):
        self.assertEqual(self.contract["checkpointing"]["checkpoint_size"], 3)
        artifact = build_group(self.work)
        result = validate_prepublication_artifact(copy.deepcopy(artifact), self.work, self.contract)
        docs = validate_buffer_artifact(copy.deepcopy(artifact), self.descriptor, self.work, self.contract)
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["dossier_count"], 3)
        self.assertEqual(result["canonical_validator"], "taste_steam_review_dossier_buffered.validate_buffer_artifact")
        self.assertEqual(len(docs), 3)

    def test_hellish_live_shape_rejected_before_publication(self):
        def mutate(artifact):
            source = artifact["dossiers"][0]["provenance"]["sources"][2]
            source["freshness"] = "older"
            source["evidence_role"] = "durable_trait"
        self.assert_same_failure(mutate, "freshness is incoherent with publication_date")

    def test_deeeer_live_single_source_shape_rejected_before_publication(self):
        def mutate(artifact):
            evidence = artifact["dossiers"][0]["evidence"]
            evidence["source_mix_status"] = "single_source_only"
            evidence["single_source_reason"] = "Only one player-feedback source was judged sufficient."
        self.assert_same_failure(mutate, "single_source_only must have exactly one distinct physical used player-feedback source")

    def test_sniper_live_unbound_russian_shape_rejected_before_publication(self):
        def mutate(artifact):
            dossier = artifact["dossiers"][0]
            dossier["observations"] = [dossier["observations"][0]]
            dossier["summary"] = derive_dossier_summary(dossier["observations"], dossier["conflicts"])
            dossier["evidence"]["source_mix_status"] = "single_source_only"
            dossier["evidence"]["single_source_reason"] = "Only one used player-feedback source remains bound."
        self.assert_same_failure(mutate, "russian found_and_used requires a bound Russian player-feedback record")

    def test_username_display_name_compact_refs_are_rejected(self):
        def mutate(artifact):
            artifact["dossiers"][0]["provenance"]["player_feedback_records"][0]["public_ref"] = (
                "steam-recommendation:6504942507064908210; contribution by Sugarwolf"
            )
        self.assert_same_failure(mutate, "public_ref contains author/user identity attribution")

    def test_author_profile_urls_are_rejected(self):
        def mutate_custom_profile(artifact):
            artifact["dossiers"][0]["provenance"]["sources"][1]["url"] = (
                "https://steamcommunity.com/id/maihasegawa/recommended/710001"
            )
        self.assert_same_failure(mutate_custom_profile, "url is author/profile-scoped and forbidden")

        def mutate_numeric_profile(artifact):
            artifact["dossiers"][0]["provenance"]["sources"][1]["url"] = (
                "https://steamcommunity.com/profiles/76561198442230810/recommended/710001/"
            )
        self.assert_same_failure(mutate_numeric_profile, "url is author/profile-scoped and forbidden")

    def test_review_content_like_ref_rejected_while_neutral_locator_allowed(self):
        artifact = build_group(self.work)
        neutral = "steam-recommendation:185290437"
        artifact["dossiers"][0]["provenance"]["player_feedback_records"][0]["public_ref"] = neutral
        self.assertEqual(
            validate_prepublication_artifact(copy.deepcopy(artifact), self.work, self.contract)["status"],
            "valid",
        )
        artifact["dossiers"][0]["provenance"]["player_feedback_records"][0]["public_ref"] = (
            "steam-review:710001:record-42 summarized as chaos/10 on top-rated page"
        )
        with self.assertRaisesRegex(ValueError, "public_ref contains review/post content-like summary"):
            validate_prepublication_artifact(artifact, self.work, self.contract)


class FreshSnapshotRecoveryTests(unittest.TestCase):
    def test_old_snapshot_artifact_is_inert_then_quarantined_without_progress_change(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract = copy.deepcopy(BASE_CONTRACT)
            contract["paths"]["submission_inbox_dir"] = (root / "buffer").as_posix()
            work = build_daily_work_manifest(
                queue([720001, 720002, 720003]),
                contract,
                root / "store",
                now=NOW,
            )
            buffer_dir = Path(contract["paths"]["submission_inbox_dir"])
            buffer_dir.mkdir(parents=True, exist_ok=True)
            old_snapshot = "a" * 64
            old_path = buffer_dir / f"{old_snapshot}--g000001--{'b' * 64}.json"
            old_path.write_text(json.dumps({"invalid": True}), encoding="utf-8")

            before_completed = work["completed_required_count"]
            before_remaining = work["remaining_required_count"]
            plan = plan_buffered_drain(work, contract, buffer_dir)
            self.assertEqual(plan["accepted_count"], 0)
            self.assertEqual(plan["failed_count"], 0)
            self.assertEqual(plan["next_manifest"]["group_progress"]["pending_group_count"], 1)
            self.assertEqual(plan["next_manifest"]["completed_required_count"], before_completed)
            self.assertEqual(plan["next_manifest"]["remaining_required_count"], before_remaining)

            quarantine = root / "quarantine"
            result = quarantine_stale_snapshot_inbox(buffer_dir, work["snapshot_id"], quarantine)
            self.assertEqual(len(result["moved"]), 1)
            self.assertFalse(old_path.exists())
            self.assertEqual(work["completed_required_count"], before_completed)
            self.assertEqual(work["remaining_required_count"], before_remaining)


if __name__ == "__main__":
    unittest.main()
