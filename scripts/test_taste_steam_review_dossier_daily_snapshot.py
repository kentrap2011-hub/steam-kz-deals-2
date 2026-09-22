#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from taste_steam_review_dossier import DOSSIER_SCHEMA, SUBMISSION_SCHEMA, build_semantic_input, canonical_sha256
from taste_steam_review_dossier_daily import (
    build_daily_work_manifest,
    canonical_dossier_scope_rows,
    load_contract,
    persist_submission_and_advance_snapshot,
)
from taste_steam_review_dossier_strict import current_worker_contract_binding
from taste_steam_review_dossier_worker_projection import (
    WORKER_GROUP_SCHEMA,
    WORKER_INDEX_SCHEMA,
    build_worker_projection,
    validate_worker_projection,
    validate_worker_projection_files,
    write_worker_projection,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
NOW = datetime(2026, 9, 13, 0, 0, tzinfo=timezone.utc)
GROUP_SIZE = int(CONTRACT["checkpointing"]["checkpoint_size"])


def queue(appids, work=None):
    result = []
    for i, appid in enumerate(appids):
        result.append({
            "taste_subject_key": f"App_{appid}_{i}", "appid": str(appid), "title": f"Game {appid}",
            "taste_fingerprint": hashlib.sha256(f"taste:{appid}:{i}".encode()).hexdigest(),
            "candidate_context_sha256": hashlib.sha256(f"ctx:{appid}:{i}".encode()).hexdigest(),
            "work_required": list(work or ["resolve_grounded_negative_analysis"]),
        })
    return result


def dossier(appid, generated=NOW):
    return {
        "schema": DOSSIER_SCHEMA, "schema_version": 1, "key": f"App_{appid}", "appid": str(appid),
        "title": f"Game {appid}", "generated_at_utc": generated.isoformat(),
        "expires_at_utc": (generated + timedelta(days=20)).isoformat(), "ttl_days": 20,
        "summary": "A compact neutral description of the game structure and recurring Steam review evidence.",
        "observations": [{
            "category": "mechanics", "statement": "Several reviews repeatedly describe deliberate movement and resource management.",
            "sentiment": "mixed", "recurrence": "moderate", "mention_count": 4, "evidence_languages": ["mixed"],
        }],
        "conflicts": [],
        "review_sample": {
            "strategy": "adaptive_stability", "sampled_total": 40, "sampled_russian": 20, "sampled_non_russian": 20,
            "sample_ids_sha256": hashlib.sha256(f"ids:{appid}".encode()).hexdigest(),
            "lanes": [
                {"language_scope": "russian", "sampled": 20, "batches": 2, "stop_reason": "stable_after_two_batches"},
                {"language_scope": "non_russian", "sampled": 20, "batches": 2, "stop_reason": "stable_after_two_batches"},
            ],
        },
        "provenance": {
            "store_description": {"url": f"https://store.steampowered.com/app/{appid}/", "captured_at_utc": generated.isoformat(), "content_sha256": hashlib.sha256(f"store:{appid}".encode()).hexdigest()},
            "steam_reviews": {"url": f"https://store.steampowered.com/appreviews/{appid}", "captured_at_utc": generated.isoformat(), "filters": ["russian", "non_russian"]},
        },
    }


def submission(work):
    return {
        "schema": SUBMISSION_SCHEMA, "schema_version": 1,
        "snapshot_id": work["snapshot_id"], "scope_sha256": work["scope_sha256"],
        "scope_source": work["scope_source"], "source_queue_sha256": work["source_queue_sha256"],
        "dossiers": [dossier(x["appid"]) for x in work["current_checkpoint_items"]],
    }


def projection_contract(td):
    contract = copy.deepcopy(CONTRACT)
    pre_ai = Path(td) / "pre_ai"
    contract["paths"]["work_manifest"] = (pre_ai / "work.json").as_posix()
    contract["paths"]["worker_index"] = (pre_ai / "worker_index.json").as_posix()
    contract["paths"]["worker_groups_root"] = (pre_ai / "worker_groups").as_posix()
    contract["worker_read_projection"]["canonical_source"] = contract["paths"]["work_manifest"]
    contract["worker_read_projection"]["descriptor_path_template"] = contract["paths"]["worker_groups_root"] + "/{snapshot_id}/g{sequence:06d}.json"
    return contract


class DailySnapshotTests(unittest.TestCase):
    def test_full_7_manifest_and_3_3_1_same_snapshot(self):
        q = queue(range(100000, 100007))
        with tempfile.TemporaryDirectory() as td:
            m1 = build_daily_work_manifest(q, CONTRACT, td, now=NOW)
            sid = m1["snapshot_id"]
            self.assertEqual(GROUP_SIZE, 3)
            self.assertEqual(m1["prepared_required_count"], 7)
            self.assertEqual(len(m1["prepared_required_items"]), 7)
            self.assertEqual(m1["current_checkpoint_count"], 3)
            _, m2 = persist_submission_and_advance_snapshot(submission(m1), m1, CONTRACT, td)
            _, m3 = persist_submission_and_advance_snapshot(submission(m2), m2, CONTRACT, td)
            self.assertEqual(m2["snapshot_id"], sid)
            self.assertEqual(m3["snapshot_id"], sid)
            self.assertEqual(m2["remaining_required_count"], 4)
            self.assertEqual(m3["remaining_required_count"], 1)
            self.assertEqual(m3["current_checkpoint_count"], 1)
            _, m4 = persist_submission_and_advance_snapshot(submission(m3), m3, CONTRACT, td)
            self.assertEqual(m4["snapshot_id"], sid)
            self.assertEqual(m4["remaining_required_count"], 0)
            self.assertTrue(m4["full_backlog_complete"])
            self.assertEqual(m4["status"], "complete")

    def test_resume_same_snapshot_without_redo_and_queue_mutation_cannot_change_it(self):
        q = queue(range(200000, 200025))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td, "work.json")
            m1 = build_daily_work_manifest(q, CONTRACT, td, now=NOW)
            path.write_text(json.dumps(m1), encoding="utf-8")
            _, _ = persist_submission_and_advance_snapshot(submission(m1), m1, CONTRACT, td, manifest_output_path=path)
            reloaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(reloaded["snapshot_id"], m1["snapshot_id"])
            self.assertEqual(reloaded["remaining_required_count"], 22)
            self.assertEqual(reloaded["current_checkpoint_items"][0]["appid"], "200003")
            q.append(queue((999999,))[0])
            self.assertEqual(reloaded, json.loads(path.read_text(encoding="utf-8")))
            next_daily = build_daily_work_manifest(q, CONTRACT, td, now=NOW + timedelta(days=1))
            self.assertIn("999999", [x["appid"] for x in next_daily["prepared_required_items"]])
            self.assertNotEqual(next_daily["snapshot_id"], reloaded["snapshot_id"])

    def test_empty_snapshot_is_valid_complete_and_fresh_reused(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td, "App_1.json").write_text(json.dumps(dossier(1)), encoding="utf-8")
            work = build_daily_work_manifest(queue((1,)), CONTRACT, td, now=NOW)
            self.assertEqual(work["prepared_required_count"], 0)
            self.assertEqual(work["remaining_required_count"], 0)
            self.assertEqual(work["current_checkpoint_items"], [])
            self.assertTrue(work["full_backlog_complete"])

    def test_stale_missing_included_nontaste_and_base_only_excluded_dedupe_first(self):
        with tempfile.TemporaryDirectory() as td:
            Path(td, "App_1.json").write_text(json.dumps(dossier(1, NOW - timedelta(days=21))), encoding="utf-8")
            q = queue((1, 2, 2))
            q += queue((3,), work=["resolve_base_support_condition"])
            q += queue((4,), work=["some_non_taste_work"])
            scope = canonical_dossier_scope_rows(q, CONTRACT)
            self.assertEqual([x["appid"] for x in scope], ["1", "2"])
            work = build_daily_work_manifest(q, CONTRACT, td, now=NOW)
            self.assertEqual([x["appid"] for x in work["prepared_required_items"]], ["1", "2"])
            self.assertEqual([x["reason"] for x in work["prepared_required_items"]], ["refresh_required", "missing_dossier"])

    def test_invalid_later_checkpoint_does_not_discard_prior_progress(self):
        with tempfile.TemporaryDirectory() as td:
            m1 = build_daily_work_manifest(queue(range(300000, 300025)), CONTRACT, td, now=NOW)
            _, m2 = persist_submission_and_advance_snapshot(submission(m1), m1, CONTRACT, td)
            bad = submission(m2)
            bad["dossiers"] = bad["dossiers"][:-1]
            before = json.loads(json.dumps(m2))
            with self.assertRaises(ValueError):
                persist_submission_and_advance_snapshot(bad, m2, CONTRACT, td)
            self.assertEqual(m2, before)
            self.assertEqual(m2["completed_required_count"], GROUP_SIZE)

    def test_semantic_input_remains_exact_active_pin_bound(self):
        pin_rows = [{"key": "App_7", "appid": "7", "taste_fingerprint": "x", "candidate_context_sha256": "y", "work_required": ["resolve_grounded_negative_analysis"]}]
        pin = {"schema": "TASTE-PINNED-WORK-UNIT-V1", "status": "active", "producer_id": "unchanged", "producer_generation": 2, "profile_identity": {}, "bindings": {}, "ordered_rows": pin_rows, "ordered_work_unit_sha256": canonical_sha256(pin_rows)}
        before = canonical_sha256(pin)
        with tempfile.TemporaryDirectory() as td:
            Path(td, "App_7.json").write_text(json.dumps(dossier(7)), encoding="utf-8")
            semantic = build_semantic_input(pin, CONTRACT, td, now=NOW)
        self.assertEqual([x["appid"] for x in semantic["rows"]], ["7"])
        self.assertEqual(semantic["pin"]["ordered_work_unit_sha256"], pin["ordered_work_unit_sha256"])
        self.assertEqual(canonical_sha256(pin), before)

    def test_compact_worker_projection_7_pointer_advances_without_descriptor_rewrite(self):
        with tempfile.TemporaryDirectory() as td:
            contract = projection_contract(td)
            store = Path(td) / "store"
            m1 = build_daily_work_manifest(queue(range(400000, 400007)), contract, store, now=NOW)
            m1["web_evidence_contract_binding"] = current_worker_contract_binding()
            p1 = write_worker_projection(m1, contract)
            self.assertEqual(p1["index"]["schema"], WORKER_INDEX_SCHEMA)
            self.assertEqual(p1["index"]["next_pending_sequence"], 1)
            self.assertEqual([len(x["items"]) for x in p1["descriptors"]], [3, 3, 1])
            self.assertTrue(all(x["schema"] == WORKER_GROUP_SCHEMA for x in p1["descriptors"]))
            group_dir = Path(contract["paths"]["worker_groups_root"]) / m1["snapshot_id"]
            before_bytes = {path.name: path.read_bytes() for path in sorted(group_dir.glob("g*.json"))}
            _, m2 = persist_submission_and_advance_snapshot(submission(m1), m1, contract, store)
            p2 = write_worker_projection(m2, contract)
            self.assertEqual(p2["index"]["next_pending_sequence"], 2)
            self.assertEqual(before_bytes, {path.name: path.read_bytes() for path in sorted(group_dir.glob("g*.json"))})
            _, m3 = persist_submission_and_advance_snapshot(submission(m2), m2, contract, store)
            p3 = write_worker_projection(m3, contract)
            self.assertEqual(p3["index"]["next_pending_sequence"], 3)
            self.assertEqual(before_bytes, {path.name: path.read_bytes() for path in sorted(group_dir.glob("g*.json"))})
            _, m4 = persist_submission_and_advance_snapshot(submission(m3), m3, contract, store)
            p4 = write_worker_projection(m4, contract)
            self.assertIsNone(p4["index"]["next_pending_sequence"])
            self.assertTrue(p4["index"]["normal_first_pass_complete"])
            self.assertTrue(p4["index"]["all_groups_accepted"])
            self.assertTrue(p4["index"]["full_backlog_complete"])
            self.assertEqual(before_bytes, {path.name: path.read_bytes() for path in sorted(group_dir.glob("g*.json"))})

    def test_compact_worker_projection_fails_closed_on_missing_and_mismatched_content(self):
        with tempfile.TemporaryDirectory() as td:
            contract = projection_contract(td)
            work = build_daily_work_manifest(queue(range(500000, 500007)), contract, Path(td) / "store", now=NOW)
            work["web_evidence_contract_binding"] = current_worker_contract_binding()
            projection = write_worker_projection(work, contract)
            index, descriptors = build_worker_projection(work, contract)
            bad_index = copy.deepcopy(index)
            bad_index["group_plan_sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                validate_worker_projection(bad_index, descriptors, work, contract)
            for field, value in (("snapshot_id", "0" * 64), ("group_plan_sha256", "1" * 64), ("source_queue_sha256", "2" * 64), ("sequence", 2), ("items_sha256", "3" * 64), ("group_sha256", "4" * 64)):
                bad = copy.deepcopy(descriptors)
                bad[0][field] = value
                with self.subTest(field=field), self.assertRaises(ValueError):
                    validate_worker_projection(index, bad, work, contract)
            missing_path = Path(contract["paths"]["worker_groups_root"]) / work["snapshot_id"] / "g000002.json"
            missing_path.unlink()
            with self.assertRaises(ValueError):
                validate_worker_projection_files(work, contract)
            self.assertEqual(projection["descriptor_count"], 3)

    def test_workflow_wiring_order_and_projection_atomic_paths(self):
        text = (ROOT / ".github/workflows/build-pre-ai-store-snapshot.yml").read_text(encoding="utf-8")
        a = text.index("Build split ChatGPT consumer bundle")
        b = text.index("Prepare fixed daily full Steam review dossier backlog")
        c = text.index("Commit atomic pre-AI payload")
        self.assertLess(a, b)
        self.assertLess(b, c)
        self.assertIn("taste_steam_review_dossier_work.json", text)
        self.assertIn("taste_steam_review_dossier_worker_index.json", text)
        self.assertIn("git add -A data/production/pre_ai/taste_steam_review_dossier_worker_groups", text)
        ingest = (ROOT / ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml").read_text(encoding="utf-8")
        self.assertIn("taste_steam_review_dossier_worker_index.json", ingest)
        self.assertIn("git add -A data/production/pre_ai/taste_steam_review_dossier_worker_groups", ingest)
        drain = (ROOT / "scripts/taste_steam_review_dossier_buffered.py").read_text(encoding="utf-8")
        self.assertNotIn("taste_steam_review_dossier_worker_index", drain)
        self.assertIn("validate_group_plan", drain)


if __name__ == "__main__":
    unittest.main()
