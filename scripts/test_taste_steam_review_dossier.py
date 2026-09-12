#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from taste_steam_review_dossier import (
    DOSSIER_SCHEMA,
    SEMANTIC_INPUT_SCHEMA,
    SUBMISSION_SCHEMA,
    build_semantic_input,
    build_work_manifest,
    canonical_dossier_scope_rows,
    canonical_sha256,
    load_contract,
    persist_submission,
    validate_dossier,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
NOW = datetime(2026, 9, 12, 18, 0, tzinfo=timezone.utc)


def _queue(appids=(527070, 6800)):
    rows = []
    for i, appid in enumerate(appids):
        rows.append({
            "family_id": f"game:{appid}:{i}",
            "taste_subject_key": f"App_{appid}" if i == 0 else f"Sub_{4000+i}",
            "appid": str(appid),
            "title": f"Queue Game {appid}",
            "taste_fingerprint": hashlib.sha256(f"taste:{appid}:{i}".encode()).hexdigest(),
            "candidate_context_sha256": hashlib.sha256(f"ctx:{appid}:{i}".encode()).hexdigest(),
            "work_required": ["resolve_grounded_negative_analysis"],
        })
    return rows


def _pin(appids=(527070, 6800)):
    rows = []
    for i, appid in enumerate(appids):
        rows.append({
            "key": f"App_{appid}" if i == 0 else f"Sub_{4000+i}",
            "appid": str(appid),
            "taste_fingerprint": hashlib.sha256(f"taste:{appid}".encode()).hexdigest(),
            "candidate_context_sha256": hashlib.sha256(f"ctx:{appid}".encode()).hexdigest(),
            "work_required": ["resolve_grounded_negative_analysis"],
        })
    return {
        "schema": "TASTE-PINNED-WORK-UNIT-V1", "status": "active",
        "producer_id": "chatgpt_scheduled_task:existing", "producer_generation": 2,
        "profile_identity": {"blob_sha": "abc"}, "bindings": {"taste_model_version": "taste-v3"},
        "ordered_rows": rows,
        "ordered_work_unit_sha256": hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
    }


def _dossier(appid, *, generated=NOW, ttl=20, title=None, ru=18, non_ru=24, ru_localization=True):
    observations = [
        {"category": "mechanics", "statement": "Reviews repeatedly describe deliberate movement and resource management as central to play.", "sentiment": "mixed", "recurrence": "moderate", "mention_count": 4, "evidence_languages": ["mixed"]},
        {"category": "repetition", "statement": "Several players report that repeated encounter patterns become noticeable during longer sessions.", "sentiment": "negative", "recurrence": "moderate", "mention_count": 3, "evidence_languages": ["non_russian"]},
    ]
    if ru_localization:
        observations.append({"category": "localization", "statement": "Russian-language reviews repeatedly report small Cyrillic UI text in several menu screens.", "sentiment": "negative", "recurrence": "moderate", "mention_count": 3, "evidence_languages": ["russian"]})
    return {
        "schema": DOSSIER_SCHEMA, "schema_version": 1, "key": f"App_{appid}", "appid": str(appid),
        "title": title or f"Fixture Game {appid}", "generated_at_utc": generated.isoformat(),
        "expires_at_utc": (generated + timedelta(days=ttl)).isoformat(), "ttl_days": ttl,
        "summary": "A compact neutral description of the game structure and how its main systems interact, based on Steam store material and recurring review evidence.",
        "observations": observations,
        "conflicts": [{"statement": "Reviewers disagree on whether the deliberate pacing is absorbing or slow.", "recurrence": "moderate"}],
        "review_sample": {
            "strategy": "adaptive_stability", "sampled_total": ru + non_ru, "sampled_russian": ru, "sampled_non_russian": non_ru,
            "sample_ids_sha256": hashlib.sha256(f"ids:{appid}:{ru}:{non_ru}".encode()).hexdigest(),
            "lanes": [
                {"language_scope": "russian", "sampled": ru, "batches": 2 if ru else 0, "stop_reason": "stable_or_source_exhausted"},
                {"language_scope": "non_russian", "sampled": non_ru, "batches": 2 if non_ru else 0, "stop_reason": "stable_after_two_batches"},
            ],
        },
        "provenance": {
            "store_description": {"url": f"https://store.steampowered.com/app/{appid}/", "captured_at_utc": generated.isoformat(), "content_sha256": hashlib.sha256(f"store:{appid}".encode()).hexdigest()},
            "steam_reviews": {"url": f"https://store.steampowered.com/appreviews/{appid}", "captured_at_utc": generated.isoformat(), "filters": ["russian", "non_russian", "recent_then_all_when_needed"]},
        },
    }


def _submission(work, dossiers):
    return {"schema": SUBMISSION_SCHEMA, "schema_version": 1, "scope_sha256": work["scope_sha256"], "scope_source": work["scope_source"], "source_queue_sha256": work["source_queue_sha256"], "dossiers": dossiers}


class SteamReviewDossierTests(unittest.TestCase):
    def test_01_full_backlog_over_100_rows_is_not_capped_by_checkpoint(self):
        queue = _queue(tuple(range(100000, 100121)))
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
        self.assertEqual(work["source_row_count"], 121)
        self.assertEqual(work["unique_appid_count"], 121)
        self.assertEqual(len(work["items"]), 121)
        self.assertEqual(work["required_total_count"], 121)
        self.assertEqual(len(work["required_items"]), 10)
        self.assertEqual(work["checkpoint"]["checkpoint_size"], 10)
        self.assertEqual(work["checkpoint"]["remaining_required_count"], 121)
        self.assertEqual(work["checkpoint"]["remaining_after_checkpoint_count"], 111)
        self.assertEqual([x["appid"] for x in work["required_items"]], [str(x) for x in range(100000, 100010)])

    def test_02_duplicate_appids_collapse_to_first_queue_occurrence(self):
        queue = _queue((527070, 6800, 527070, 6800, 9999))
        scope = canonical_dossier_scope_rows(queue)
        self.assertEqual([x["appid"] for x in scope], ["527070", "6800", "9999"])
        self.assertEqual(scope[0]["key"], queue[0]["taste_subject_key"])
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
        self.assertEqual(work["deduplicated_row_count"], 2)
        self.assertEqual(work["ordered_appids"], ["527070", "6800", "9999"])

    def test_03_fresh_dossier_reused_without_reanalysis(self):
        queue = _queue((527070,))
        with tempfile.TemporaryDirectory() as td:
            Path(td, "App_527070.json").write_text(json.dumps(_dossier(527070)), encoding="utf-8")
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
            self.assertEqual(work["status"], "ready_from_fresh_cache")
            self.assertEqual(work["required_total_count"], 0)
            self.assertEqual(work["required_items"], [])
            self.assertEqual(work["items"][0]["state"], "fresh")

    def test_04_stale_dossier_requires_refresh(self):
        queue = _queue((527070,))
        with tempfile.TemporaryDirectory() as td:
            Path(td, "App_527070.json").write_text(json.dumps(_dossier(527070, generated=NOW - timedelta(days=21))), encoding="utf-8")
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
            self.assertEqual(work["required_items"][0]["reason"], "refresh_required")

    def test_05_missing_dossier_requires_create(self):
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(_queue((527070,)), CONTRACT, td, now=NOW)
            self.assertEqual(work["required_items"][0]["reason"], "missing_dossier")

    def test_06_default_ttl_20_and_configurable(self):
        queue = _queue((527070,))
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(build_work_manifest(queue, CONTRACT, td, now=NOW)["ttl_days"], 20)
            self.assertEqual(build_work_manifest(queue, CONTRACT, td, now=NOW, ttl_days=7)["ttl_days"], 7)

    def test_07_downstream_semantic_input_remains_exact_active_pin_bound(self):
        pin = _pin(tuple(range(100000, 100010)))
        before = canonical_sha256(pin)
        with tempfile.TemporaryDirectory() as td:
            for row in pin["ordered_rows"]:
                Path(td, f"App_{row['appid']}.json").write_text(json.dumps(_dossier(row["appid"])), encoding="utf-8")
            semantic = build_semantic_input(pin, CONTRACT, td, now=NOW)
        self.assertEqual(semantic["schema"], SEMANTIC_INPUT_SCHEMA)
        self.assertEqual(len(semantic["rows"]), 10)
        self.assertEqual([x["key"] for x in semantic["rows"]], [x["key"] for x in pin["ordered_rows"]])
        self.assertEqual(semantic["pin"]["ordered_work_unit_sha256"], pin["ordered_work_unit_sha256"])
        self.assertEqual(canonical_sha256(pin), before)

    def test_08_semantic_input_holds_on_stale_or_missing_pin_dossier(self):
        pin = _pin((527070,))
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "missing/stale/invalid"):
                build_semantic_input(pin, CONTRACT, td, now=NOW)
            Path(td, "App_527070.json").write_text(json.dumps(_dossier(527070, generated=NOW - timedelta(days=21))), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "held"):
                build_semantic_input(pin, CONTRACT, td, now=NOW)

    def test_09_submission_is_bound_to_full_queue_scope_and_persists_by_appid(self):
        queue = _queue((6800,))
        queue[0]["taste_subject_key"] = "Sub_4156"
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
            persist_submission(_submission(work, [_dossier(6800)]), work, CONTRACT, td)
            self.assertTrue(Path(td, "App_6800.json").exists())
            bad = _submission(work, [_dossier(6800)])
            bad["source_queue_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "queue binding"):
                persist_submission(bad, work, CONTRACT, td)

    def test_10_storage_rejects_raw_reviews_and_personalized_conclusions(self):
        doc = _dossier(527070)
        bad = copy.deepcopy(doc); bad["raw_reviews"] = [{"review_text": "raw body"}]
        with self.assertRaisesRegex(ValueError, "Raw review archive"):
            validate_dossier(bad, CONTRACT)
        polluted = copy.deepcopy(doc); polluted["observations"][0]["statement"] = "Дмитрию это не подойдет."
        with self.assertRaisesRegex(ValueError, "Personalized"):
            validate_dossier(polluted, CONTRACT)

    def test_11_adaptive_ceiling_and_russian_lane_remain_enforced(self):
        validate_dossier(_dossier(527070, ru=80, non_ru=80), CONTRACT)
        with self.assertRaisesRegex(ValueError, "ceiling"):
            validate_dossier(_dossier(527070, ru=81, non_ru=80), CONTRACT)

    def test_12_twenty_five_missing_apps_progress_10_10_5_then_ready(self):
        appids = tuple(range(200000, 200025))
        queue = _queue(appids)
        with tempfile.TemporaryDirectory() as td:
            first = build_work_manifest(queue, CONTRACT, td, now=NOW)
            self.assertEqual(first["required_total_count"], 25)
            self.assertEqual([x["appid"] for x in first["required_items"]], [str(x) for x in appids[:10]])
            self.assertEqual(first["checkpoint"]["remaining_after_checkpoint_count"], 15)
            self.assertTrue(first["checkpoint"]["continue_same_invocation"])
            persist_submission(_submission(first, [_dossier(x) for x in appids[:10]]), first, CONTRACT, td)

            second = build_work_manifest(queue, CONTRACT, td, now=NOW)
            self.assertEqual(second["required_total_count"], 15)
            self.assertEqual([x["appid"] for x in second["required_items"]], [str(x) for x in appids[10:20]])
            self.assertEqual(second["checkpoint"]["remaining_after_checkpoint_count"], 5)
            self.assertTrue(second["checkpoint"]["continue_same_invocation"])
            persist_submission(_submission(second, [_dossier(x) for x in appids[10:20]]), second, CONTRACT, td)

            third = build_work_manifest(queue, CONTRACT, td, now=NOW)
            self.assertEqual(third["required_total_count"], 5)
            self.assertEqual([x["appid"] for x in third["required_items"]], [str(x) for x in appids[20:]])
            self.assertEqual(third["checkpoint"]["remaining_after_checkpoint_count"], 0)
            self.assertFalse(third["checkpoint"]["continue_same_invocation"])
            persist_submission(_submission(third, [_dossier(x) for x in appids[20:]]), third, CONTRACT, td)

            done = build_work_manifest(queue, CONTRACT, td, now=NOW)
            self.assertEqual(done["status"], "ready_from_fresh_cache")
            self.assertEqual(done["required_total_count"], 0)
            self.assertEqual(done["required_items"], [])
            self.assertEqual(done["checkpoint"]["remaining_required_count"], 0)

    def test_13_incomplete_or_invalid_checkpoint_fails_before_any_persistence(self):
        appids = tuple(range(300000, 300012))
        queue = _queue(appids)
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
            incomplete = [_dossier(x) for x in appids[:9]]
            with self.assertRaisesRegex(ValueError, "exactly cover.*checkpoint"):
                persist_submission(_submission(work, incomplete), work, CONTRACT, td)
            self.assertEqual(list(Path(td).glob("App_*.json")), [])

            invalid = [_dossier(x) for x in appids[:10]]
            invalid[-1]["raw_reviews"] = [{"review_text": "must not persist"}]
            with self.assertRaisesRegex(ValueError, "Raw review archive"):
                persist_submission(_submission(work, invalid), work, CONTRACT, td)
            self.assertEqual(list(Path(td).glob("App_*.json")), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
