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
from taste_steam_review_dossier import SUBMISSION_SCHEMA
from taste_steam_review_dossier_buffered import expected_buffer_path, plan_buffered_drain
from taste_steam_review_dossier_daily import (
    BUFFER_GROUP_SCHEMA,
    ensure_submission_group_plan,
    expected_group_sequence,
    load_contract,
    progress_fields,
)
from taste_steam_review_dossier_test_fixture import web_dossier
from taste_steam_review_dossier_web import (
    build_daily_work_manifest_web,
    persist_submission_and_advance_snapshot_strict,
)

ROOT = Path(__file__).resolve().parents[1]
BASE_CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
NOW = datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc)
GROUP_SIZE = int(BASE_CONTRACT["checkpointing"]["checkpoint_size"])


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
    return web_dossier(appid, generated)


def submission(work):
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


def advance(work, contract, store_dir, groups):
    current = work
    for _ in range(groups):
        _, current = persist_submission_and_advance_snapshot_strict(
            submission(current), current, contract, store_dir
        )
    return current


class BufferedSubmissionTests(unittest.TestCase):
    def test_deterministic_group_plan_25_is_groups_of_three_plus_tail_and_identity_survives_progress(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest_web(queue(range(100000, 100025)), contract, store, now=NOW)
            plan_before = copy.deepcopy(work["submission_group_plan"])
            self.assertEqual(GROUP_SIZE, 3)
            self.assertEqual([len(g["items"]) for g in plan_before["groups"]], [3] * 8 + [1])
            progressed = advance(work, contract, store, 1)
            self.assertEqual(progressed["submission_group_plan"], plan_before)
            self.assertEqual(expected_group_sequence(progressed, contract), 2)
            self.assertEqual(progressed["web_evidence_contract_binding"], work["web_evidence_contract_binding"])

    def test_present_later_pending_group_is_independently_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            work = build_daily_work_manifest_web(queue(range(110000, 110025)), contract, Path(td) / "store", now=NOW)
            future = write_group(work, contract, 2)
            plan = plan_buffered_drain(work, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual([x["descriptor"]["sequence"] for x in plan["accepted"]], [2])
            self.assertEqual(plan["failed_count"], 0)
            self.assertEqual(plan["next_manifest"]["group_progress"]["groups"][0]["state"], "pending")
            self.assertEqual(plan["next_manifest"]["group_progress"]["groups"][1]["state"], "accepted")
            self.assertTrue(future.exists())

    def test_nonblocking_drain_crosses_missing_pending_group(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest_web(queue(range(120000, 120080)), contract, store, now=NOW)
            current = advance(work, contract, store, 3)
            p4, p5, p7 = [write_group(work, contract, sequence) for sequence in (4, 5, 7)]
            plan = plan_buffered_drain(current, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual([x["descriptor"]["sequence"] for x in plan["accepted"]], [4, 5, 7])
            self.assertEqual(plan["failed_count"], 0)
            self.assertEqual(plan["next_manifest"]["group_progress"]["groups"][5]["state"], "pending")
            self.assertEqual(plan["next_manifest"]["group_progress"]["groups"][6]["state"], "accepted")
            manifest_path = Path(td) / "work.json"
            manifest_path.write_text(json.dumps(current), encoding="utf-8")
            buffered.apply_buffered_drain(plan, manifest_path=manifest_path, store_dir=store)
            self.assertFalse(p4.exists())
            self.assertFalse(p5.exists())
            self.assertFalse(p7.exists())
            persisted_manifest = json.loads(manifest_path.read_text())
            self.assertEqual(persisted_manifest["completed_required_count"], GROUP_SIZE * 5)
            self.assertEqual(persisted_manifest["group_progress"]["groups"][5]["state"], "pending")
            self.assertEqual(persisted_manifest["group_progress"]["groups"][6]["state"], "accepted")

    def test_invalid_group_fails_without_blocking_later_group(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest_web(queue(range(130000, 130040)), contract, store, now=NOW)
            p1 = write_group(work, contract, 1)
            p2 = write_group(work, contract, 2, lambda a: a["dossiers"][0].__setitem__("schema_version", 1))
            p3 = write_group(work, contract, 3)
            quarantine = Path(td) / "quarantine"
            plan = plan_buffered_drain(
                work, contract, contract["paths"]["submission_inbox_dir"],
                failed_quarantine_root=quarantine,
            )
            self.assertEqual([x["descriptor"]["sequence"] for x in plan["accepted"]], [1, 3])
            self.assertEqual([x["descriptor"]["sequence"] for x in plan["failed"]], [2])
            manifest_path = Path(td) / "work.json"
            manifest_path.write_text(json.dumps(work), encoding="utf-8")
            buffered.apply_buffered_drain(
                plan, manifest_path=manifest_path, store_dir=store,
                failure_audit_path=Path(td) / "failures.jsonl",
            )
            self.assertFalse(p1.exists())
            self.assertFalse(p2.exists())
            self.assertFalse(p3.exists())
            current = json.loads(manifest_path.read_text())
            self.assertEqual(current["group_progress"]["groups"][1]["state"], "failed_or_invalid_pending_recovery")
            self.assertEqual(current["group_progress"]["groups"][2]["state"], "accepted")
            self.assertTrue(any(quarantine.rglob("*.invalid-*")))

    def test_stale_snapshot_inert_and_replay_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            old = build_daily_work_manifest_web(queue(range(140000, 140025)), contract, store, now=NOW)
            current = build_daily_work_manifest_web(queue(range(150000, 150025)), contract, store, now=NOW + timedelta(days=1))
            stale = write_group(old, contract, 1)
            plan = plan_buffered_drain(current, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual(plan["accepted_count"], 0)
            self.assertEqual(plan["failed_count"], 0)
            self.assertTrue(stale.exists())

        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest_web(queue(range(160000, 160030)), contract, store, now=NOW)
            p1 = write_group(work, contract, 1)
            first = plan_buffered_drain(work, contract, contract["paths"]["submission_inbox_dir"])
            manifest_path = Path(td) / "work.json"
            manifest_path.write_text(json.dumps(work), encoding="utf-8")
            buffered.apply_buffered_drain(first, manifest_path=manifest_path, store_dir=store)
            current = json.loads(manifest_path.read_text())
            self.assertFalse(p1.exists())
            write_group(work, contract, 1)
            replay = plan_buffered_drain(current, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual(replay["accepted_count"], 0)
            self.assertEqual(replay["failed_count"], 0)
            self.assertEqual(replay["next_manifest"]["completed_required_count"], GROUP_SIZE)
            self.assertEqual(replay["next_manifest"]["group_progress"]["groups"][0]["state"], "accepted")
            self.assertEqual(replay["next_manifest"]["group_progress"]["groups"][1]["state"], "pending")

    def test_atomic_multi_group_apply_and_restart_before_apply(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest_web(queue(range(170000, 170009)), contract, store, now=NOW)
            for sequence in (1, 2, 3):
                write_group(work, contract, sequence)
            manifest_path = Path(td) / "work.json"
            original_text = json.dumps(work, sort_keys=True)
            manifest_path.write_text(original_text, encoding="utf-8")
            first_plan = plan_buffered_drain(work, contract, contract["paths"]["submission_inbox_dir"])
            restarted_plan = plan_buffered_drain(json.loads(manifest_path.read_text()), contract, contract["paths"]["submission_inbox_dir"])
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

    def test_group_plan_migration_and_v2_fresh_cache_reuse(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest_web(queue(range(180000, 180025)), contract, store, now=NOW)
            progressed = advance(work, contract, store, 2)
            legacy = copy.deepcopy(progressed)
            legacy.pop("submission_group_plan")
            legacy.pop("group_progress", None)
            sid = legacy["snapshot_id"]
            migrated = ensure_submission_group_plan(legacy, contract)
            self.assertEqual(migrated["snapshot_id"], sid)
            self.assertEqual(migrated["completed_required_count"], GROUP_SIZE * 2)
            broken = copy.deepcopy(legacy)
            broken["remaining_required_items"] = broken["prepared_required_items"][5:]
            broken.update(progress_fields(broken["snapshot_id"], broken["prepared_required_items"], broken["remaining_required_items"], GROUP_SIZE))
            with self.assertRaises(ValueError):
                ensure_submission_group_plan(broken, contract)

        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            store.mkdir(parents=True)
            appids = list(range(190000, 190050))
            for appid in appids[:40]:
                (store / f"App_{appid}.json").write_text(json.dumps(dossier(appid)), encoding="utf-8")
            work = build_daily_work_manifest_web(queue(appids), contract, store, now=NOW)
            self.assertEqual(work["prepared_required_count"], 10)
            self.assertEqual([x["appid"] for x in work["prepared_required_items"]], [str(x) for x in appids[40:]])

    def test_buffer_runtime_does_not_take_taste_semantic_producer_ownership(self):
        joined = "\n".join([
            (ROOT / "scripts/taste_steam_review_dossier_buffered.py").read_text(encoding="utf-8"),
            (ROOT / "scripts/ingest_taste_steam_review_dossier_inbox.py").read_text(encoding="utf-8"),
        ])
        for forbidden in ("taste_fit.json", "taste_active_work_unit.json", "ingest_taste_results.py", "taste_semantic_producer"):
            self.assertNotIn(forbidden, joined)
        workflow = (ROOT / ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml").read_text(encoding="utf-8")
        self.assertIn("taste-steam-review-dossier-canonical-writer", workflow)
        self.assertNotIn("workflow_dispatch", workflow)


if __name__ == "__main__":
    unittest.main()
