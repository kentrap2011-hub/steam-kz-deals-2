#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from build_taste_steam_review_dossier_work import build_or_preserve_daily_work
from taste_steam_review_dossier import DOSSIER_SCHEMA, SUBMISSION_SCHEMA
from taste_steam_review_dossier_daily import (
    build_daily_work_manifest,
    load_contract,
    persist_submission_and_advance_snapshot,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
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


def write_queue(path, rows):
    Path(path).write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class SameDayPreservationTests(unittest.TestCase):
    def test_same_day_legacy_manifest_migrates_additively_without_resetting_progress(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = root / "store"
            queue_path = root / "queue.jsonl"
            output = root / "work.json"
            initial_rows = queue(range(300000, 300025))
            write_queue(queue_path, initial_rows)

            prepared = build_daily_work_manifest(initial_rows, CONTRACT, store, now=NOW, source_queue_path=str(queue_path))
            _, progressed = persist_submission_and_advance_snapshot(submission(prepared), prepared, CONTRACT, store)
            legacy = copy.deepcopy(progressed)
            legacy.pop("submission_group_plan")
            output.write_text(json.dumps(legacy), encoding="utf-8")

            # Same-day repository inputs drift after canonical progress: a new queue row appears
            # and already-accepted dossiers now exist in the store. Neither may rebuild/reset scope.
            changed_rows = initial_rows + queue((999999,))
            write_queue(queue_path, changed_rows)
            manifest, transition = build_or_preserve_daily_work(
                contract=CONTRACT,
                queue_path=str(queue_path),
                store_dir=str(store),
                output_path=str(output),
                now=NOW + timedelta(hours=2),
            )

            self.assertEqual(transition["mode"], "preserved_same_day_snapshot")
            self.assertTrue(transition["group_plan_added"])
            self.assertEqual(manifest["snapshot_id"], legacy["snapshot_id"])
            self.assertEqual(manifest["prepared_required_sha256"], legacy["prepared_required_sha256"])
            self.assertEqual(manifest["prepared_required_items"], legacy["prepared_required_items"])
            self.assertEqual(manifest["completed_required_count"], 10)
            self.assertEqual(manifest["remaining_required_items"], legacy["prepared_required_items"][10:])
            self.assertNotIn("999999", [item["appid"] for item in manifest["prepared_required_items"]])
            self.assertEqual([len(g["items"]) for g in manifest["submission_group_plan"]["groups"]], [10, 10, 5])

    def test_same_day_existing_buffered_manifest_is_byte_semantically_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = root / "store"
            queue_path = root / "queue.jsonl"
            output = root / "work.json"
            rows = queue(range(400000, 400025))
            write_queue(queue_path, rows)
            prepared = build_daily_work_manifest(rows, CONTRACT, store, now=NOW, source_queue_path=str(queue_path))
            _, progressed = persist_submission_and_advance_snapshot(submission(prepared), prepared, CONTRACT, store)
            output.write_text(json.dumps(progressed), encoding="utf-8")

            manifest, transition = build_or_preserve_daily_work(
                contract=CONTRACT,
                queue_path=str(queue_path),
                store_dir=str(store),
                output_path=str(output),
                now=NOW + timedelta(hours=1),
            )
            self.assertEqual(transition["mode"], "preserved_same_day_snapshot")
            self.assertFalse(transition["group_plan_added"])
            self.assertEqual(manifest, progressed)

    def test_next_day_rebuilds_from_current_queue_and_fresh_store(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = root / "store"
            queue_path = root / "queue.jsonl"
            output = root / "work.json"
            rows = queue(range(500000, 500025))
            write_queue(queue_path, rows)
            prepared = build_daily_work_manifest(rows, CONTRACT, store, now=NOW, source_queue_path=str(queue_path))
            output.write_text(json.dumps(prepared), encoding="utf-8")

            changed_rows = rows + queue((599999,))
            write_queue(queue_path, changed_rows)
            manifest, transition = build_or_preserve_daily_work(
                contract=CONTRACT,
                queue_path=str(queue_path),
                store_dir=str(store),
                output_path=str(output),
                now=NOW + timedelta(days=1),
            )
            self.assertEqual(transition["mode"], "built_new_daily_snapshot")
            self.assertNotEqual(manifest["snapshot_id"], prepared["snapshot_id"])
            self.assertIn("599999", [item["appid"] for item in manifest["prepared_required_items"]])


if __name__ == "__main__":
    unittest.main()
