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
    persist_submission_and_rebuild_work,
    validate_dossier,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
NOW = datetime(2026, 9, 12, 18, 0, tzinfo=timezone.utc)


def _queue(appids=(527070, 6800), *, work_required=None):
    rows = []
    for i, appid in enumerate(appids):
        work = list(work_required or ["resolve_grounded_negative_analysis"])
        rows.append({
            "family_id": f"game:{appid}:{i}",
            "taste_subject_key": f"App_{appid}" if i == 0 else f"Sub_{4000+i}",
            "appid": str(appid),
            "title": f"Queue Game {appid}",
            "taste_fingerprint": hashlib.sha256(f"taste:{appid}:{i}".encode()).hexdigest(),
            "candidate_context_sha256": hashlib.sha256(f"ctx:{appid}:{i}".encode()).hexdigest(),
            "work_required": work,
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


def _docs_for_checkpoint(work):
    return [_dossier(x["appid"]) for x in work["required_items"]]


class SteamReviewDossierTests(unittest.TestCase):
    def test_01_full_backlog_over_100_rows_exposes_bounded_checkpoint_not_quota(self):
        queue = _queue(tuple(range(100000, 100121)))
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
        self.assertEqual(work["source_row_count"], 121)
        self.assertEqual(work["unique_appid_count"], 121)
        self.assertEqual(work["required_total_count"], 121)
        self.assertEqual(work["checkpoint"]["item_count"], 10)
        self.assertEqual(len(work["required_items"]), 10)
        self.assertEqual(work["checkpoint"]["remaining_after_checkpoint_count"], 111)
        self.assertFalse(work["full_backlog_complete"])

    def test_02_duplicate_appids_collapse_to_first_eligible_queue_occurrence(self):
        queue = _queue((527070, 6800, 527070, 6800, 9999))
        scope = canonical_dossier_scope_rows(queue, CONTRACT)
        self.assertEqual([x["appid"] for x in scope], ["527070", "6800", "9999"])
        self.assertEqual(scope[0]["key"], queue[0]["taste_subject_key"])
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
        self.assertEqual(work["eligible_row_count"], 5)
        self.assertEqual(work["deduplicated_row_count"], 2)
        self.assertEqual(work["ordered_appids"], ["527070", "6800", "9999"])

    def test_03_sequential_checkpoints_25_continue_10_then_10_then_5_then_ready(self):
        queue = _queue(tuple(range(200000, 200025)))
        with tempfile.TemporaryDirectory() as td:
            work1 = build_work_manifest(queue, CONTRACT, td, now=NOW)
            self.assertEqual(work1["required_total_count"], 25)
            self.assertEqual([x["appid"] for x in work1["required_items"]], [str(x) for x in range(200000, 200010)])

            _, work2 = persist_submission_and_rebuild_work(
                _submission(work1, _docs_for_checkpoint(work1)), work1, CONTRACT, td, queue, now=NOW
            )
            self.assertEqual(work2["required_total_count"], 15)
            self.assertEqual([x["appid"] for x in work2["required_items"]], [str(x) for x in range(200010, 200020)])

            _, work3 = persist_submission_and_rebuild_work(
                _submission(work2, _docs_for_checkpoint(work2)), work2, CONTRACT, td, queue, now=NOW
            )
            self.assertEqual(work3["required_total_count"], 5)
            self.assertEqual(work3["checkpoint"]["item_count"], 5)
            self.assertTrue(work3["checkpoint"]["is_final_checkpoint"])
            self.assertEqual([x["appid"] for x in work3["required_items"]], [str(x) for x in range(200020, 200025)])

            _, work4 = persist_submission_and_rebuild_work(
                _submission(work3, _docs_for_checkpoint(work3)), work3, CONTRACT, td, queue, now=NOW
            )
            self.assertEqual(work4["status"], "ready_from_fresh_cache")
            self.assertEqual(work4["required_total_count"], 0)
            self.assertEqual(work4["required_items"], [])
            self.assertTrue(work4["full_backlog_complete"])

    def test_04_partial_durable_progress_resumes_from_first_remaining_appid(self):
        queue = _queue(tuple(range(300000, 300025)))
        with tempfile.TemporaryDirectory() as td:
            for appid in range(300000, 300004):
                Path(td, f"App_{appid}.json").write_text(json.dumps(_dossier(appid)), encoding="utf-8")
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
        self.assertEqual(work["required_total_count"], 21)
        self.assertEqual([x["appid"] for x in work["required_items"]], [str(x) for x in range(300004, 300014)])

    def test_05_partial_checkpoint_submission_is_rejected_without_persistence(self):
        queue = _queue(tuple(range(400000, 400012)))
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
            partial = _submission(work, _docs_for_checkpoint(work)[:5])
            with self.assertRaisesRegex(ValueError, "exactly cover"):
                persist_submission(partial, work, CONTRACT, td)
            self.assertEqual(list(Path(td).glob("App_*.json")), [])

    def test_06_fresh_dossier_reused_without_reanalysis(self):
        queue = _queue((527070,))
        with tempfile.TemporaryDirectory() as td:
            Path(td, "App_527070.json").write_text(json.dumps(_dossier(527070)), encoding="utf-8")
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
            self.assertEqual(work["status"], "ready_from_fresh_cache")
            self.assertEqual(work["required_total_count"], 0)
            self.assertEqual(work["required_items"], [])
            self.assertEqual(work["items"][0]["state"], "fresh")

    def test_07_stale_dossier_requires_refresh(self):
        queue = _queue((527070,))
        with tempfile.TemporaryDirectory() as td:
            Path(td, "App_527070.json").write_text(json.dumps(_dossier(527070, generated=NOW - timedelta(days=21))), encoding="utf-8")
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
            self.assertEqual(work["required_items"][0]["reason"], "refresh_required")

    def test_08_missing_dossier_requires_create(self):
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(_queue((527070,)), CONTRACT, td, now=NOW)
            self.assertEqual(work["required_items"][0]["reason"], "missing_dossier")

    def test_09_default_ttl_20_and_configurable(self):
        queue = _queue((527070,))
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(build_work_manifest(queue, CONTRACT, td, now=NOW)["ttl_days"], 20)
            self.assertEqual(build_work_manifest(queue, CONTRACT, td, now=NOW, ttl_days=7)["ttl_days"], 7)

    def test_10_downstream_semantic_input_remains_exact_active_pin_bound(self):
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

    def test_11_semantic_input_holds_on_stale_or_missing_pin_dossier(self):
        pin = _pin((527070,))
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "missing/stale/invalid"):
                build_semantic_input(pin, CONTRACT, td, now=NOW)
            Path(td, "App_527070.json").write_text(json.dumps(_dossier(527070, generated=NOW - timedelta(days=21))), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "held"):
                build_semantic_input(pin, CONTRACT, td, now=NOW)

    def test_12_submission_is_bound_to_exact_checkpoint_and_queue_snapshot(self):
        queue = _queue(tuple(range(500000, 500015)))
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
            persist_submission(_submission(work, _docs_for_checkpoint(work)), work, CONTRACT, td)
            self.assertEqual(len(list(Path(td).glob("App_*.json"))), 10)
            bad = _submission(work, _docs_for_checkpoint(work))
            bad["source_queue_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "queue binding"):
                persist_submission(bad, work, CONTRACT, td)

    def test_13_rebuild_fails_closed_if_canonical_queue_changed_since_manifest(self):
        queue = _queue(tuple(range(600000, 600012)))
        changed = queue + _queue((699999,))
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
            with self.assertRaisesRegex(ValueError, "queue changed"):
                persist_submission_and_rebuild_work(
                    _submission(work, _docs_for_checkpoint(work)), work, CONTRACT, td, changed, now=NOW
                )
            self.assertEqual(list(Path(td).glob("App_*.json")), [])

    def test_14_base_support_only_and_other_non_taste_rows_are_excluded(self):
        queue = _queue((700001,))
        base_only = _queue((700002,), work_required=["resolve_base_support_condition"])[0]
        other_only = _queue((700003,), work_required=["some_non_taste_support_work"])[0]
        mixed = _queue((700004,), work_required=["resolve_base_support_condition", "resolve_grounded_negative_analysis"])[0]
        queue.extend([base_only, other_only, mixed])
        scope = canonical_dossier_scope_rows(queue, CONTRACT)
        self.assertEqual([x["appid"] for x in scope], ["700001", "700004"])
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
        self.assertEqual(work["source_row_count"], 4)
        self.assertEqual(work["eligible_row_count"], 2)
        self.assertEqual(work["excluded_row_count"], 2)
        self.assertEqual(work["ordered_appids"], ["700001", "700004"])

    def test_15_storage_rejects_raw_reviews_and_personalized_conclusions(self):
        doc = _dossier(527070)
        bad = copy.deepcopy(doc); bad["raw_reviews"] = [{"review_text": "raw body"}]
        with self.assertRaisesRegex(ValueError, "Raw review archive"):
            validate_dossier(bad, CONTRACT)
        polluted = copy.deepcopy(doc); polluted["observations"][0]["statement"] = "Дмитрию это не подойдет."
        with self.assertRaisesRegex(ValueError, "Personalized"):
            validate_dossier(polluted, CONTRACT)

    def test_16_adaptive_ceiling_and_russian_lane_remain_enforced(self):
        validate_dossier(_dossier(527070, ru=80, non_ru=80), CONTRACT)
        with self.assertRaisesRegex(ValueError, "ceiling"):
            validate_dossier(_dossier(527070, ru=81, non_ru=80), CONTRACT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
