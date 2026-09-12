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
    canonical_sha256,
    load_contract,
    persist_submission,
    validate_dossier,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
NOW = datetime(2026, 9, 12, 18, 0, tzinfo=timezone.utc)


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
        "schema": "TASTE-PINNED-WORK-UNIT-V1",
        "status": "active",
        "producer_id": "chatgpt_scheduled_task:existing",
        "producer_generation": 2,
        "profile_identity": {"blob_sha": "abc"},
        "bindings": {"taste_model_version": "taste-v3"},
        "ordered_rows": rows,
        "ordered_work_unit_sha256": hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
    }


def _dossier(appid, *, generated=NOW, ttl=20, title=None, ru=18, non_ru=24, ru_localization=True):
    observations = [
        {
            "category": "mechanics",
            "statement": "Reviews repeatedly describe deliberate movement and resource management as central to play.",
            "sentiment": "mixed",
            "recurrence": "moderate",
            "mention_count": 4,
            "evidence_languages": ["mixed"],
        },
        {
            "category": "repetition",
            "statement": "Several players report that repeated encounter patterns become noticeable during longer sessions.",
            "sentiment": "negative",
            "recurrence": "moderate",
            "mention_count": 3,
            "evidence_languages": ["non_russian"],
        },
    ]
    if ru_localization:
        observations.append({
            "category": "localization",
            "statement": "Russian-language reviews repeatedly report small Cyrillic UI text in several menu screens.",
            "sentiment": "negative",
            "recurrence": "moderate",
            "mention_count": 3,
            "evidence_languages": ["russian"],
        })
    doc = {
        "schema": DOSSIER_SCHEMA,
        "schema_version": 1,
        "key": f"App_{appid}",
        "appid": str(appid),
        "title": title or f"Fixture Game {appid}",
        "generated_at_utc": generated.isoformat(),
        "expires_at_utc": (generated + timedelta(days=ttl)).isoformat(),
        "ttl_days": ttl,
        "summary": "A compact neutral description of the game structure and how its main systems interact, based on Steam store material and recurring review evidence.",
        "observations": observations,
        "conflicts": [
            {
                "statement": "Reviewers disagree on whether the deliberate pacing is absorbing or slow.",
                "recurrence": "moderate"
            }
        ],
        "review_sample": {
            "strategy": "adaptive_stability",
            "sampled_total": ru + non_ru,
            "sampled_russian": ru,
            "sampled_non_russian": non_ru,
            "sample_ids_sha256": hashlib.sha256(f"ids:{appid}:{ru}:{non_ru}".encode()).hexdigest(),
            "lanes": [
                {"language_scope": "russian", "sampled": ru, "batches": 2 if ru else 0, "stop_reason": "stable_or_source_exhausted"},
                {"language_scope": "non_russian", "sampled": non_ru, "batches": 2 if non_ru else 0, "stop_reason": "stable_after_two_batches"},
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
                "filters": ["russian", "non_russian", "recent_then_all_when_needed"],
            },
        },
    }
    return doc


class SteamReviewDossierTests(unittest.TestCase):
    def test_01_fresh_dossier_reused_without_reanalysis(self):
        pin = _pin((527070,))
        with tempfile.TemporaryDirectory() as td:
            Path(td, "App_527070.json").write_text(json.dumps(_dossier(527070)), encoding="utf-8")
            work = build_work_manifest(pin, CONTRACT, td, now=NOW)
            self.assertEqual(work["status"], "ready_from_fresh_cache")
            self.assertEqual(work["required_items"], [])
            self.assertEqual(work["items"][0]["state"], "fresh")

    def test_02_stale_dossier_requires_refresh_and_semantic_input_holds(self):
        pin = _pin((527070,))
        stale = _dossier(527070, generated=NOW - timedelta(days=21))
        with tempfile.TemporaryDirectory() as td:
            Path(td, "App_527070.json").write_text(json.dumps(stale), encoding="utf-8")
            work = build_work_manifest(pin, CONTRACT, td, now=NOW)
            self.assertEqual(work["required_items"][0]["reason"], "refresh_required")
            with self.assertRaisesRegex(ValueError, "held"):
                build_semantic_input(pin, CONTRACT, td, now=NOW)

    def test_03_default_ttl_20_and_configurable(self):
        pin = _pin((527070,))
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(build_work_manifest(pin, CONTRACT, td, now=NOW)["ttl_days"], 20)
            self.assertEqual(build_work_manifest(pin, CONTRACT, td, now=NOW, ttl_days=7)["ttl_days"], 7)

    def test_04_russian_review_localization_finding_is_valid_neutral_evidence(self):
        doc = _dossier(527070, ru_localization=True)
        validate_dossier(doc, CONTRACT)
        loc = [x for x in doc["observations"] if x["category"] == "localization"]
        self.assertEqual(len(loc), 1)
        self.assertEqual(loc[0]["evidence_languages"], ["russian"])
        self.assertEqual(loc[0]["sentiment"], "negative")

    def test_05_recurring_negative_is_allowed_without_personal_negative(self):
        doc = _dossier(527070)
        validate_dossier(doc, CONTRACT)
        negatives = [x for x in doc["observations"] if x["sentiment"] == "negative"]
        self.assertGreaterEqual(len(negatives), 1)
        polluted = copy.deepcopy(doc)
        polluted["observations"][0]["statement"] = "Дмитрию это не подойдет."
        with self.assertRaisesRegex(ValueError, "Personalized"):
            validate_dossier(polluted, CONTRACT)

    def test_06_downstream_input_contains_prepared_dossier_and_exact_pin_binding(self):
        pin = _pin((527070,))
        with tempfile.TemporaryDirectory() as td:
            doc = _dossier(527070)
            Path(td, "App_527070.json").write_text(json.dumps(doc), encoding="utf-8")
            semantic = build_semantic_input(pin, CONTRACT, td, now=NOW)
            self.assertEqual(semantic["schema"], SEMANTIC_INPUT_SCHEMA)
            self.assertEqual(semantic["pin"]["ordered_work_unit_sha256"], pin["ordered_work_unit_sha256"])
            self.assertEqual(semantic["rows"][0]["dossier"]["appid"], "527070")

    def test_07_missing_dossier_never_falls_back_to_store_only(self):
        pin = _pin((527070,))
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError, "missing/stale/invalid"):
                build_semantic_input(pin, CONTRACT, td, now=NOW)

    def test_08_storage_rejects_raw_review_archive_and_persists_compact_synthesis(self):
        pin = _pin((527070,))
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(pin, CONTRACT, td, now=NOW)
            doc = _dossier(527070)
            submission = {
                "schema": SUBMISSION_SCHEMA,
                "schema_version": 1,
                "scope_sha256": work["scope_sha256"],
                "pin_work_unit_sha256": work["pin_work_unit_sha256"],
                "dossiers": [doc],
            }
            persisted = persist_submission(submission, work, CONTRACT, td)
            self.assertEqual(len(persisted), 1)
            stored = json.loads(Path(td, "App_527070.json").read_text(encoding="utf-8"))
            self.assertNotIn("raw_reviews", stored)
            bad = copy.deepcopy(doc)
            bad["raw_reviews"] = [{"review_text": "raw body"}]
            with self.assertRaisesRegex(ValueError, "Raw review archive"):
                validate_dossier(bad, CONTRACT)

    def test_09_pin_authority_is_read_only_and_preserved(self):
        pin = _pin((527070, 6800))
        before = canonical_sha256(pin)
        with tempfile.TemporaryDirectory() as td:
            Path(td, "App_527070.json").write_text(json.dumps(_dossier(527070)), encoding="utf-8")
            Path(td, "App_6800.json").write_text(json.dumps(_dossier(6800)), encoding="utf-8")
            semantic = build_semantic_input(pin, CONTRACT, td, now=NOW)
            self.assertEqual(canonical_sha256(pin), before)
            self.assertEqual([x["key"] for x in semantic["rows"]], [x["key"] for x in pin["ordered_rows"]])
            self.assertEqual(semantic["pin"]["ordered_work_unit_sha256"], pin["ordered_work_unit_sha256"])

    def test_10_reusable_dossier_scope_is_appid_bound_not_taste_subject_key(self):
        pin = _pin((6800,))
        pin["ordered_rows"][0]["key"] = "Sub_4156"
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(pin, CONTRACT, td, now=NOW)
            doc = _dossier(6800)
            self.assertEqual(doc["key"], "App_6800")
            submission = {
                "schema": SUBMISSION_SCHEMA,
                "schema_version": 1,
                "scope_sha256": work["scope_sha256"],
                "pin_work_unit_sha256": work["pin_work_unit_sha256"],
                "dossiers": [doc],
            }
            persist_submission(submission, work, CONTRACT, td)
            self.assertTrue(Path(td, "App_6800.json").exists())

    def test_11_exact_scope_submission_and_adaptive_ceiling(self):
        pin = _pin((527070,))
        with tempfile.TemporaryDirectory() as td:
            work = build_work_manifest(pin, CONTRACT, td, now=NOW)
            doc = _dossier(527070, ru=80, non_ru=80)
            submission = {
                "schema": SUBMISSION_SCHEMA,
                "schema_version": 1,
                "scope_sha256": work["scope_sha256"],
                "pin_work_unit_sha256": work["pin_work_unit_sha256"],
                "dossiers": [doc],
            }
            persist_submission(submission, work, CONTRACT, td)
            too_many = _dossier(527070, ru=81, non_ru=80)
            with self.assertRaisesRegex(ValueError, "ceiling"):
                validate_dossier(too_many, CONTRACT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
