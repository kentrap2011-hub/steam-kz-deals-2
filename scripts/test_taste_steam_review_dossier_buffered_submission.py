#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import taste_steam_review_dossier_buffered as buffered
from taste_steam_review_dossier import DOSSIER_SCHEMA, SUBMISSION_SCHEMA, canonical_sha256
from taste_steam_review_dossier_buffered import expected_buffer_path, plan_buffered_drain
from taste_steam_review_dossier_daily import (
    BUFFER_GROUP_SCHEMA,
    build_daily_work_manifest,
    ensure_submission_group_plan,
    expected_group_sequence,
    load_contract,
    persist_submission_and_advance_snapshot,
    progress_fields,
    validate_manifest,
)

ROOT = Path(__file__).resolve().parents[1]
BASE_CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
NOW = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)


def queue(appids):
    return [{
        "taste_subject_key": f"App_{appid}_{i}",
        "appid": str(appid),
        "title": f"Game {appid}",
        "taste_fingerprint": hashlib.sha256(f"taste:{appid}:{i}".encode()).hexdigest(),
        "candidate_context_sha256": hashlib.sha256(f"ctx:{appid}:{i}".encode()).hexdigest(),
        "work_required": ["resolve_grounded_negative_analysis"],
    } for i, appid in enumerate(appids)]


def dossier(appid, generated=NOW):
    return {
        "schema": DOSSIER_SCHEMA,
        "schema_version": 1,
        "key": f"App_{appid}",
        "appid": str(appid),
        "title": f"Game {appid}",
        "generated_at_utc": generated.isoformat(),
        "expires_at_utc": (generated + timedelta(days=20)).isoformat(),
        "ttl_days": 20,
        "summary": "A compact neutral description of recurring game structure and review evidence.",
        "observations": [{
            "category": "mechanics",
            "statement": "Several reviews repeatedly describe deliberate movement and resource management.",
            "sentiment": "mixed",
            "recurrence": "moderate",
            "mention_count": 4,
            "evidence_languages": ["mixed"],
        }],
        "conflicts": [],
        "review_sample": {
            "strategy": "adaptive_stability",
            "sampled_total": 40,
            "sampled_russian": 20,
            "sampled_non_russian": 20,
            "sample_ids_sha256": hashlib.sha256(f"ids:{appid}".encode()).hexdigest(),
            "lanes": [
                {"language_scope": "russian", "sampled": 20, "batches": 2, "stop_reason": "stable_after_two_batches"},
                {"language_scope": "non_russian", "sampled": 20, "batches": 2, "stop_reason": "stable_after_two_batches"},
            ],
        },
        "provenance": {
            "store_description": {
                "url": f"https://store.steampowered.com/app/{appid}/",
                "captured_at_utc": generated.isoformat(),
                "content_sha256": hashlib.sha256(f"store:{appid}".encode()).hexdigest(),
            },
            "steam_reviews": {
                "url": f"https://store.steampowered.com/appreviews/{appid}",
                "captured_at_utc": generated.isoformat(),
                "filters": ["russian", "non_russian"],
            },
        },
    }


def legacy_submission(work):
    return {
        "schema": SUBMISSION_SCHEMA,
        "schema_version": 1,
        "snapshot_id": work["snapshot_id"],
        "scope_sha256": work["scope_sha256"],
        "scope_source": work["scope_source"],
        "source_queue_sha256": work["source_queue_sha256"],
        "dossiers": [dossier(item["appid"]) for item in work["current_checkpoint_items"]],
    }


def contract_for(td):
    contract = copy.deepcopy(BASE_CONTRACT)
    contract["paths"]["submission_inbox_dir"] = str(Path(td) / "buffer")
    return contract


def buffered_artifact(work, sequence):
    descriptor = work["submission_group_plan"]["groups"][sequence - 1]
    return {
        "schema": BUFFER_GROUP_SCHEMA,
        "schema_version": 1,
        **copy.deepcopy(descriptor),
        "dossiers": [dossier(appid) for appid in descriptor["appids"]],
    }


def write_group(work, contract, sequence, mutate=None):
    artifact = buffered_artifact(work, sequence)
    if mutate:
        mutate(artifact)
    descriptor = work["submission_group_plan"]["groups"][sequence - 1]
    path = expected_buffer_path(descriptor, contract)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def advance_legacy(work, contract, store_dir, groups):
    current = work
    for _ in range(groups):
        _, current = persist_submission_and_advance_snapshot(
            legacy_submission(current), current, contract, store_dir
        )
    return current


class BufferedSubmissionTests(unittest.TestCase):
    def test_deterministic_group_plan_25_is_10_10_5_and_identity_survives_progress(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest(queue(range(100000, 100025)), contract, store, now=NOW)
            plan_before = copy.deepcopy(work["submission_group_plan"])
            self.assertEqual([len(g["items"]) for g in plan_before["groups"]], [10, 10, 5])
            self.assertEqual([g["sequence"] for g in plan_before["groups"]], [1, 2, 3])
            rebuilt = build_daily_work_manifest(queue(range(100000, 100025)), contract, store, now=NOW)
            self.assertEqual(rebuilt["submission_group_plan"], plan_before)
            progressed = advance_legacy(work, contract, store, 1)
            self.assertEqual(progressed["submission_group_plan"], plan_before)
            self.assertEqual(expected_group_sequence(progressed, contract), 2)

    def test_future_group_can_wait_before_canonical_advancement(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            work = build_daily_work_manifest(queue(range(110000, 110025)), contract, Path(td) / "store", now=NOW)
            future = write_group(work, contract, 2)
            plan = plan_buffered_drain(work, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual(plan["accepted_count"], 0)
            self.assertEqual(plan["blocked_reason"], "gap")
            self.assertEqual(plan["stop_sequence"], 1)
            self.assertTrue(future.exists())

    def test_contiguous_drain_expected_4_accepts_4_5_6_7(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest(queue(range(120000, 120070)), contract, store, now=NOW)
            current = advance_legacy(work, contract, store, 3)
            self.assertEqual(expected_group_sequence(current, contract), 4)
            paths = [write_group(work, contract, sequence) for sequence in (4, 5, 6, 7)]
            plan = plan_buffered_drain(current, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual([x["descriptor"]["sequence"] for x in plan["accepted"]], [4, 5, 6, 7])
            self.assertEqual(plan["next_manifest"]["completed_required_count"], 70)
            manifest_path = Path(td) / "work.json"
            manifest_path.write_text(json.dumps(current), encoding="utf-8")
            buffered.apply_buffered_drain(plan, manifest_path=manifest_path, store_dir=store)
            after = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertTrue(after["full_backlog_complete"])
            self.assertTrue(all(not path.exists() for path in paths))

    def test_gap_expected_4_with_4_5_7_accepts_only_4_5(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest(queue(range(130000, 130080)), contract, store, now=NOW)
            current = advance_legacy(work, contract, store, 3)
            p4, p5, p7 = [write_group(work, contract, sequence) for sequence in (4, 5, 7)]
            plan = plan_buffered_drain(current, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual([x["descriptor"]["sequence"] for x in plan["accepted"]], [4, 5])
            self.assertEqual(plan["blocked_reason"], "gap")
            self.assertEqual(plan["stop_sequence"], 6)
            manifest_path = Path(td) / "work.json"
            manifest_path.write_text(json.dumps(current), encoding="utf-8")
            buffered.apply_buffered_drain(plan, manifest_path=manifest_path, store_dir=store)
            self.assertFalse(p4.exists())
            self.assertFalse(p5.exists())
            self.assertTrue(p7.exists())
            self.assertEqual(json.loads(manifest_path.read_text())["completed_required_count"], 50)

    def test_malformed_expected_group_blocks_it_and_later_but_keeps_valid_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest(queue(range(140000, 140080)), contract, store, now=NOW)
            current = advance_legacy(work, contract, store, 3)
            p4 = write_group(work, contract, 4)
            p5 = write_group(work, contract, 5)
            p6 = write_group(work, contract, 6, lambda a: a["dossiers"].pop())
            p7 = write_group(work, contract, 7)
            plan = plan_buffered_drain(current, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual([x["descriptor"]["sequence"] for x in plan["accepted"]], [4, 5])
            self.assertEqual(plan["blocked_reason"], "invalid_expected_group")
            self.assertEqual(plan["stop_sequence"], 6)
            manifest_path = Path(td) / "work.json"
            manifest_path.write_text(json.dumps(current), encoding="utf-8")
            buffered.apply_buffered_drain(plan, manifest_path=manifest_path, store_dir=store)
            self.assertFalse(p4.exists())
            self.assertFalse(p5.exists())
            self.assertTrue(p6.exists())
            self.assertTrue(p7.exists())

    def test_stale_snapshot_is_inert_and_wrong_snapshot_at_expected_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            old = build_daily_work_manifest(queue(range(150000, 150025)), contract, store, now=NOW)
            current = build_daily_work_manifest(queue(range(160000, 160025)), contract, store, now=NOW + timedelta(days=1))
            stale = write_group(old, contract, 1)
            plan = plan_buffered_drain(current, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual(plan["accepted_count"], 0)
            self.assertEqual(plan["blocked_reason"], "gap")
            self.assertTrue(stale.exists())
            wrong = write_group(current, contract, 1, lambda a: a.__setitem__("snapshot_id", old["snapshot_id"]))
            blocked = plan_buffered_drain(current, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual(blocked["accepted_count"], 0)
            self.assertEqual(blocked["blocked_reason"], "invalid_expected_group")
            self.assertTrue(wrong.exists())

    def test_replay_is_idempotent_and_does_not_advance_again(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest(queue(range(170000, 170030)), contract, store, now=NOW)
            p1 = write_group(work, contract, 1)
            first = plan_buffered_drain(work, contract, contract["paths"]["submission_inbox_dir"])
            manifest_path = Path(td) / "work.json"
            manifest_path.write_text(json.dumps(work), encoding="utf-8")
            buffered.apply_buffered_drain(first, manifest_path=manifest_path, store_dir=store)
            current = json.loads(manifest_path.read_text())
            self.assertFalse(p1.exists())
            write_group(work, contract, 1)  # exact replay after canonical advancement
            replay = plan_buffered_drain(current, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual(replay["accepted_count"], 0)
            self.assertEqual(replay["stop_sequence"], 2)
            self.assertEqual(replay["next_manifest"]["completed_required_count"], 10)

    def test_atomic_multi_group_plan_and_restart_before_apply(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest(queue(range(180000, 180025)), contract, store, now=NOW)
            for sequence in (1, 2, 3):
                write_group(work, contract, sequence)
            manifest_path = Path(td) / "work.json"
            original_text = json.dumps(work, sort_keys=True)
            manifest_path.write_text(original_text, encoding="utf-8")
            first_plan = plan_buffered_drain(work, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual(first_plan["accepted_count"], 3)
            # Simulated interruption before canonical push/apply: durable canonical file is unchanged.
            self.assertEqual(json.dumps(json.loads(manifest_path.read_text()), sort_keys=True), original_text)
            restarted_plan = plan_buffered_drain(
                json.loads(manifest_path.read_text()), contract, contract["paths"]["submission_inbox_dir"]
            )
            self.assertEqual(
                [x["descriptor"]["group_sha256"] for x in restarted_plan["accepted"]],
                [x["descriptor"]["group_sha256"] for x in first_plan["accepted"]],
            )
            original_atomic = buffered.atomic_write_json
            manifest_writes = []
            def tracking_write(path, value):
                if Path(path) == manifest_path:
                    manifest_writes.append(Path(path))
                return original_atomic(path, value)
            with patch.object(buffered, "atomic_write_json", side_effect=tracking_write):
                buffered.apply_buffered_drain(restarted_plan, manifest_path=manifest_path, store_dir=store)
            self.assertEqual(len(manifest_writes), 1)
            self.assertTrue(json.loads(manifest_path.read_text())["full_backlog_complete"])

    def test_migration_proof_preserves_snapshot_and_accepted_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest(queue(range(190000, 190025)), contract, store, now=NOW)
            progressed = advance_legacy(work, contract, store, 2)
            legacy = copy.deepcopy(progressed)
            legacy.pop("submission_group_plan")
            sid = legacy["snapshot_id"]
            migrated = ensure_submission_group_plan(legacy, contract)
            self.assertEqual(migrated["snapshot_id"], sid)
            self.assertEqual(migrated["completed_required_count"], 20)
            self.assertEqual(migrated["remaining_required_items"], migrated["prepared_required_items"][20:])
            self.assertEqual(expected_group_sequence(migrated, contract), 3)
            self.assertEqual(migrated["submission_group_plan"]["groups"][0]["appids"], work["submission_group_plan"]["groups"][0]["appids"])
            broken = copy.deepcopy(legacy)
            broken["remaining_required_items"] = broken["prepared_required_items"][15:]
            broken.update(progress_fields(broken["snapshot_id"], broken["prepared_required_items"], broken["remaining_required_items"], 10))
            with self.assertRaises(ValueError):
                ensure_submission_group_plan(broken, contract)

    def test_forty_fresh_dossiers_are_not_recreated_or_reingested(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            store.mkdir(parents=True)
            appids = list(range(200000, 200050))
            for appid in appids[:40]:
                (store / f"App_{appid}.json").write_text(json.dumps(dossier(appid)), encoding="utf-8")
            work = build_daily_work_manifest(queue(appids), contract, store, now=NOW)
            self.assertEqual(work["prepared_required_count"], 10)
            self.assertEqual([x["appid"] for x in work["prepared_required_items"]], [str(x) for x in appids[40:]])
            self.assertTrue(all(str(x) not in work["submission_group_plan"]["groups"][0]["appids"] for x in appids[:40]))

    def test_dossier_buffer_runtime_does_not_take_taste_semantic_producer_ownership(self):
        texts = [
            (ROOT / "scripts/taste_steam_review_dossier_buffered.py").read_text(encoding="utf-8"),
            (ROOT / "scripts/ingest_taste_steam_review_dossier_inbox.py").read_text(encoding="utf-8"),
        ]
        joined = "\n".join(texts)
        for forbidden in (
            "taste_fit.json",
            "taste_active_work_unit.json",
            "ingest_taste_results.py",
            "taste_semantic_producer",
        ):
            self.assertNotIn(forbidden, joined)
        workflow = (ROOT / ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml").read_text(encoding="utf-8")
        self.assertIn("taste-steam-review-dossier-canonical-writer", workflow)
        self.assertNotIn("workflow_dispatch", workflow)

    def test_synthetic_25_items_multiple_buffer_groups_then_single_drain(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest(queue(range(210000, 210025)), contract, store, now=NOW)
            paths = [write_group(work, contract, sequence) for sequence in (1, 2, 3)]
            self.assertEqual(sum(path.exists() for path in paths), 3)
            plan = plan_buffered_drain(work, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual([x["descriptor"]["sequence"] for x in plan["accepted"]], [1, 2, 3])
            self.assertEqual(plan["accepted_dossier_count"], 25)
            manifest_path = Path(td) / "work.json"
            manifest_path.write_text(json.dumps(work), encoding="utf-8")
            buffered.apply_buffered_drain(plan, manifest_path=manifest_path, store_dir=store)
            final = json.loads(manifest_path.read_text())
            self.assertEqual(final["remaining_required_count"], 0)
            self.assertEqual(final["completed_required_count"], 25)
            self.assertTrue(all(not path.exists() for path in paths))


if __name__ == "__main__":
    unittest.main()
