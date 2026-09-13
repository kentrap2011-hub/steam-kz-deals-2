#!/usr/bin/env python3
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

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
NOW = datetime(2026, 9, 13, 0, 0, tzinfo=timezone.utc)


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


class DailySnapshotTests(unittest.TestCase):
    def test_full_25_manifest_and_10_10_5_same_snapshot(self):
        q = queue(range(100000, 100025))
        with tempfile.TemporaryDirectory() as td:
            m1 = build_daily_work_manifest(q, CONTRACT, td, now=NOW)
            sid = m1["snapshot_id"]
            self.assertEqual(m1["prepared_required_count"], 25)
            self.assertEqual(len(m1["prepared_required_items"]), 25)
            self.assertEqual(m1["current_checkpoint_count"], 10)
            _, m2 = persist_submission_and_advance_snapshot(submission(m1), m1, CONTRACT, td)
            _, m3 = persist_submission_and_advance_snapshot(submission(m2), m2, CONTRACT, td)
            self.assertEqual(m2["snapshot_id"], sid)
            self.assertEqual(m3["snapshot_id"], sid)
            self.assertEqual(m2["remaining_required_count"], 15)
            self.assertEqual(m3["remaining_required_count"], 5)
            self.assertEqual(m3["current_checkpoint_count"], 5)
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
            _, m2 = persist_submission_and_advance_snapshot(submission(m1), m1, CONTRACT, td, manifest_output_path=path)
            reloaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(reloaded["snapshot_id"], m1["snapshot_id"])
            self.assertEqual(reloaded["remaining_required_count"], 15)
            self.assertEqual(reloaded["current_checkpoint_items"][0]["appid"], "200010")
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
            self.assertEqual(m2["completed_required_count"], 10)

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

    def test_workflow_wiring_order(self):
        text = (ROOT / ".github/workflows/build-pre-ai-store-snapshot.yml").read_text(encoding="utf-8")
        a = text.index("Build split ChatGPT consumer bundle")
        b = text.index("Prepare fixed daily full Steam review dossier backlog")
        c = text.index("Commit atomic pre-AI payload")
        self.assertLess(a, b)
        self.assertLess(b, c)
        self.assertIn("taste_steam_review_dossier_work.json", text)


if __name__ == "__main__":
    unittest.main()
