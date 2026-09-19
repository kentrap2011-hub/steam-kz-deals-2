#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import timedelta, datetime, timezone
from pathlib import Path

from ingest_taste_steam_review_dossier_inbox import drain_inbox_state
from taste_steam_review_dossier_buffered import expected_buffer_path, validate_buffer_artifact
from taste_steam_review_dossier_daily import BUFFER_GROUP_SCHEMA, build_daily_work_manifest, load_contract
from taste_steam_review_dossier_recovery import (
    load_recovery_contract,
    process_recovery_request,
    quarantine_stale_snapshot_inbox,
)
from taste_steam_review_dossier_strict import (
    current_worker_contract_binding,
    load_web_evidence_contract,
    load_worker_schema,
    validate_dossier_strict,
)
from taste_steam_review_dossier_test_fixture import web_dossier

ROOT = Path(__file__).resolve().parents[1]
BASE_CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
BASE_RECOVERY = load_recovery_contract(ROOT / "config/taste_steam_review_dossier_recovery_contract.json")
SCHEMA = load_worker_schema(ROOT / "config/taste_steam_review_dossier_schema.json")
EVIDENCE_CONTRACT = load_web_evidence_contract(ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json")
NOW = datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc)
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


def dossier(appid, generated=NOW, **kwargs):
    return web_dossier(appid, generated, **kwargs)


def contract_for(td):
    root = Path(td)
    contract = copy.deepcopy(BASE_CONTRACT)
    contract["paths"]["submission_inbox_dir"] = (root / "buffer").as_posix()
    contract["paths"]["work_manifest"] = (root / "work.json").as_posix()
    contract["paths"]["worker_index"] = (root / "worker_index.json").as_posix()
    contract["paths"]["worker_groups_root"] = (root / "worker_groups").as_posix()
    contract["worker_read_projection"]["canonical_source"] = contract["paths"]["work_manifest"]
    contract["worker_read_projection"]["descriptor_path_template"] = contract["paths"]["worker_groups_root"] + "/{snapshot_id}/g{sequence:06d}.json"
    return contract


def buffered_artifact(work, sequence):
    descriptor = work["submission_group_plan"]["groups"][sequence - 1]
    return {
        "schema": BUFFER_GROUP_SCHEMA,
        "schema_version": 1,
        **copy.deepcopy(descriptor),
        "dossiers": [dossier(item["appid"]) for item in descriptor["items"]],
    }


def write_group(work, contract, sequence, mutate=None):
    descriptor = work["submission_group_plan"]["groups"][sequence - 1]
    artifact = buffered_artifact(work, sequence)
    if mutate:
        mutate(artifact)
    path = expected_buffer_path(descriptor, contract)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


class WebEvidenceSchemaTests(unittest.TestCase):
    def validate(self, doc):
        return validate_dossier_strict(
            doc,
            BASE_CONTRACT,
            expected_appid="123456",
            expected_title="Game 123456",
            expected_ttl_days=20,
            now=NOW,
        )

    def assertInvalid(self, mutate):
        doc = dossier(123456)
        mutate(doc)
        with self.assertRaises(ValueError):
            self.validate(doc)

    def test_schema_evidence_contract_and_prompt_alignment(self):
        self.assertEqual(SCHEMA["version"], 2)
        self.assertEqual(SCHEMA["dossier_schema"], "TASTE-STEAM-REVIEW-DOSSIER-V2")
        self.assertEqual(EVIDENCE_CONTRACT["schema"], "TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2")
        self.assertEqual(EVIDENCE_CONTRACT["version"], 2)
        self.assertEqual(SCHEMA["evidence_contract"], EVIDENCE_CONTRACT["schema"])
        self.assertEqual(current_worker_contract_binding()["worker_prompt_revision"], "web-evidence-v2-early-multi-source-diversification-v1")
        prompt = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")
        for needle in (
            "title **plus the resolved release year**",
            "recent evidence dominates old launch-era evidence",
            "Russian-language attempt is mandatory",
            "Steam `appreviews` JSON, cursors, fixed review counts",
            "Never persist raw review bodies",
            "`mention_count` is exactly",
            "?l=russian",
            "8 web-search queries",
            "16 opened/read source pages",
            "Mandatory pre-publication validation",
            "taste_steam_review_dossier_prepublication.py",
            "Language binding — bind records first, derive claims second",
            "Russian retrieval diversification after existence proof",
            "transient_author_deduped",
            "fallback-only evidence is capped",
        ):
            self.assertIn(needle, prompt)

    def test_title_year_identity_and_multisource_pass(self):
        doc = dossier(123456)
        self.assertIs(self.validate(doc), doc)
        self.assertEqual(doc["game_identity"]["release_year"], 2020)
        self.assertEqual(doc["evidence"]["source_mix_status"], "multi_source")

    def test_aggregate_523_cannot_become_523_mentions(self):
        self.assertInvalid(lambda d: d["observations"][0].__setitem__("mention_count", 523))

    def test_one_player_record_cannot_support_moderate_or_strong_recurrence(self):
        def mutate(doc):
            doc["observations"][0]["player_feedback_ids"] = ["feedback-001"]
            doc["observations"][0]["mention_count"] = 1
            doc["observations"][0]["recurrence"] = "moderate"
        self.assertInvalid(mutate)
        def mutate_strong(doc):
            doc["observations"][0]["player_feedback_ids"] = ["feedback-001"]
            doc["observations"][0]["mention_count"] = 1
            doc["observations"][0]["recurrence"] = "strong"
        self.assertInvalid(mutate_strong)

    def test_russian_store_ui_is_not_player_feedback_or_multisource(self):
        def mutate(doc):
            doc["provenance"]["sources"][2] = {
                "source_id": "source-003",
                "source_type": "steam_reviews",
                "domain": "store.steampowered.com",
                "url": "https://store.steampowered.com/app/123456/?l=russian",
                "publication_date": NOW.date().isoformat(),
                "language": "russian",
                "freshness": "recent",
                "evidence_role": "current_state",
                "player_feedback": True,
            }
            doc["provenance"]["player_feedback_records"][3]["source_id"] = "source-003"
        self.assertInvalid(mutate)

        doc = dossier(123456, russian_status="searched_no_existence_signal")
        doc["provenance"]["sources"].append({
            "source_id": "source-004",
            "source_type": "official_metadata",
            "domain": "store.steampowered.com",
            "url": "https://store.steampowered.com/app/123456/?l=russian",
            "publication_date": None,
            "language": "russian",
            "freshness": "recent",
            "evidence_role": "current_state",
            "player_feedback": False,
        })
        self.assertIs(self.validate(doc), doc)
        self.assertEqual(doc["evidence"]["russian_attempt"], "searched_no_existence_signal")

    def test_real_russian_player_record_satisfies_found_and_used(self):
        found = dossier(123456, russian_status="found_and_used")
        self.assertIs(self.validate(found), found)
        self.assertIn("feedback-004", found["observations"][1]["player_feedback_ids"])

    def test_original_remake_ambiguity_fails_without_year_or_resolved_identity(self):
        self.assertInvalid(lambda d: d["game_identity"].pop("release_year"))
        self.assertInvalid(lambda d: d["game_identity"].__setitem__("resolution_status", "ambiguous"))
        self.assertInvalid(lambda d: d["game_identity"]["corroborators"].__setitem__(0, {"kind": "developer", "value": "Studio"}))

    def test_historical_launch_issue_requires_old_and_recent_current_check(self):
        doc = dossier(123456)
        doc["provenance"]["sources"].append({
            "source_id": "source-004", "source_type": "forum", "domain": "example.com",
            "url": "https://example.com/game/launch-thread", "publication_date": "2020-01-01",
            "language": "non_russian", "freshness": "older", "evidence_role": "historical", "player_feedback": True,
        })
        for n in range(1, 4):
            doc["provenance"]["player_feedback_records"].append({
                "feedback_id": f"feedback-{n + 4:03d}", "source_id": "source-004", "public_ref": f"launch-post-{n}",
                "publication_date": "2020-01-01", "language": "non_russian",
            })
        doc["observations"][0].update({
            "category": "friction",
            "statement": "A launch-era technical complaint is historical because a recent current-state check no longer reproduces it.",
            "sentiment": "negative",
            "recurrence": "moderate",
            "mention_count": 3,
            "evidence_status": "historical",
            "source_ids": ["source-004", "source-003"],
            "player_feedback_ids": ["feedback-005", "feedback-006", "feedback-007"],
        })
        self.assertIs(self.validate(doc), doc)
        bad = copy.deepcopy(doc)
        bad["observations"][0]["source_ids"] = ["source-004"]
        with self.assertRaises(ValueError):
            self.validate(bad)

    def test_repeated_recent_complaint_requires_three_distinct_records(self):
        doc = dossier(123456)
        for n in (5, 6):
            doc["provenance"]["player_feedback_records"].append({
                "feedback_id": f"feedback-{n:03d}", "source_id": "source-003", "public_ref": f"reddit-current-{n}",
                "publication_date": NOW.date().isoformat(), "language": "russian",
            })
        doc["observations"][1].update({
            "statement": "Recent player feedback repeatedly reports the same current localization problem.",
            "sentiment": "negative", "recurrence": "moderate", "mention_count": 3,
            "player_feedback_ids": ["feedback-004", "feedback-005", "feedback-006"],
        })
        self.assertIs(self.validate(doc), doc)

    def test_markdown_wrapped_url_is_rejected(self):
        self.assertInvalid(lambda d: d["provenance"]["sources"][1].__setitem__("url", "[Steam](https://steamcommunity.com/app/123456/reviews/)"))
        self.assertInvalid(lambda d: d["provenance"]["player_feedback_records"][0].__setitem__("url", "[review](https://steamcommunity.com/review/1)"))

    def test_duplicate_bad_provenance_and_raw_body_payload_rejected(self):
        self.assertInvalid(lambda d: d["provenance"]["sources"].append(copy.deepcopy(d["provenance"]["sources"][1])))
        self.assertInvalid(lambda d: d["provenance"]["sources"][1].__setitem__("domain", "wrong.example"))
        self.assertInvalid(lambda d: d["provenance"]["sources"][1].__setitem__("snippet", "raw player text must never be stored"))
        self.assertInvalid(lambda d: d.__setitem__("review_body", "raw body"))
        self.assertInvalid(lambda d: d["provenance"]["player_feedback_records"].append(copy.deepcopy(d["provenance"]["player_feedback_records"][0])))

    def test_legacy_placeholder_and_review_sample_rejected(self):
        legacy = {
            "schema": "TASTE-STEAM-REVIEW-DOSSIER-V1", "schema_version": 1,
            "appid": "123456", "title": "Game 123456",
            "generated_at_utc": NOW.isoformat(), "expires_at_utc": (NOW + timedelta(days=20)).isoformat(),
            "ttl_days": 20, "summary": "Legacy store-only placeholder without player evidence.",
            "observations": [], "conflicts": [], "review_sample": {}, "provenance": {},
        }
        with self.assertRaises(ValueError):
            self.validate(legacy)
        self.assertInvalid(lambda d: d.__setitem__("review_sample", {}))

    def test_prior_hardening_bool_title_duplicates_time_and_source_refs(self):
        for mutate in (
            lambda d: d.__setitem__("schema_version", True),
            lambda d: d.__setitem__("ttl_days", True),
            lambda d: d["game_identity"].__setitem__("release_year", True),
            lambda d: d["observations"][0].__setitem__("mention_count", True),
            lambda d: d.__setitem__("title", "Wrong title"),
            lambda d: d["observations"].append(copy.deepcopy(d["observations"][0])),
            lambda d: d.__setitem__("expires_at_utc", (NOW + timedelta(days=19)).isoformat()),
            lambda d: d["observations"][0]["source_ids"].append("missing-source"),
            lambda d: d["observations"][0].__setitem__("category", "content"),
        ):
            with self.subTest(mutate=mutate):
                self.assertInvalid(mutate)


class RecoveryLifecycleTests(unittest.TestCase):
    def _write_contracts(self, td, contract):
        root = Path(td)
        contract_path = root / "contract.json"
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        recovery = copy.deepcopy(BASE_RECOVERY)
        recovery["request"]["path"] = (root / "control" / "request.json").as_posix()
        recovery["invalid_expected_artifact_recovery"]["quarantine_dir"] = (root / "quarantine").as_posix()
        recovery["invalid_expected_artifact_recovery"]["audit_log"] = (root / "audit.jsonl").as_posix()
        recovery_path = root / "recovery.json"
        recovery_path.write_text(json.dumps(recovery), encoding="utf-8")
        return contract_path, recovery_path, recovery

    def test_invalid_expected_recovery_frees_same_path_preserves_later_then_republish_drains(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest(queue(range(200000, 200025)), contract, store, now=NOW)
            work["web_evidence_contract_binding"] = current_worker_contract_binding()
            manifest_path = Path(contract["paths"]["work_manifest"])
            manifest_path.write_text(json.dumps(work), encoding="utf-8")
            contract_path, recovery_path, recovery = self._write_contracts(td, contract)
            p1 = write_group(work, contract, 1, lambda a: a["dossiers"][0]["observations"][0].__setitem__("category", "content"))
            p2 = write_group(work, contract, 2)
            before_manifest = manifest_path.read_text(encoding="utf-8")
            descriptor = work["submission_group_plan"]["groups"][0]
            request = {
                "schema": recovery["request"]["schema"], "schema_version": 1,
                "action": recovery["request"]["allowed_action"], "snapshot_id": work["snapshot_id"],
                "sequence": 1, "group_sha256": descriptor["group_sha256"],
                "artifact_path": p1.as_posix(), "reason": "validator-proven test invalid artifact",
            }
            request_path = Path(recovery["request"]["path"])
            request_path.parent.mkdir(parents=True, exist_ok=True)
            request_path.write_text(json.dumps(request), encoding="utf-8")
            result = process_recovery_request(request_path=request_path, recovery_contract_path=recovery_path, dossier_contract_path=contract_path, manifest_path=manifest_path)
            self.assertTrue(result["recovered"])
            self.assertFalse(p1.exists())
            self.assertTrue(p2.exists())
            self.assertEqual(manifest_path.read_text(encoding="utf-8"), before_manifest)
            corrected = write_group(work, contract, 1)
            self.assertEqual(corrected, p1)
            drained = drain_inbox_state(manifest_path=manifest_path, contract_path=contract_path, store_dir=store, buffer_dir=contract["paths"]["submission_inbox_dir"], fail_on_blocked=False)
            self.assertEqual(drained["accepted_group_count"], 2)
            self.assertEqual(drained["accepted_dossier_count"], GROUP_SIZE * 2)
            self.assertEqual(json.loads(manifest_path.read_text())["completed_required_count"], GROUP_SIZE * 2)

    def test_recovery_refuses_valid_expected_and_title_binding_still_holds(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            work = build_daily_work_manifest(queue(range(300000, 300011)), contract, Path(td) / "store", now=NOW)
            work["web_evidence_contract_binding"] = current_worker_contract_binding()
            descriptor = work["submission_group_plan"]["groups"][0]
            artifact = buffered_artifact(work, 1)
            artifact["dossiers"][0]["title"] = "Wrong title"
            with self.assertRaises(ValueError):
                validate_buffer_artifact(artifact, descriptor, work, contract)
            manifest_path = Path(contract["paths"]["work_manifest"])
            manifest_path.write_text(json.dumps(work), encoding="utf-8")
            contract_path, recovery_path, recovery = self._write_contracts(td, contract)
            p1 = write_group(work, contract, 1)
            request = {"schema": recovery["request"]["schema"], "schema_version": 1, "action": recovery["request"]["allowed_action"], "snapshot_id": work["snapshot_id"], "sequence": 1, "group_sha256": descriptor["group_sha256"], "artifact_path": p1.as_posix(), "reason": "must refuse valid"}
            request_path = Path(recovery["request"]["path"])
            request_path.parent.mkdir(parents=True, exist_ok=True)
            request_path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaises(ValueError):
                process_recovery_request(request_path=request_path, recovery_contract_path=recovery_path, dossier_contract_path=contract_path, manifest_path=manifest_path)
            self.assertTrue(p1.exists())

    def test_stale_cleanup_and_lost_wakeup_regressions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "buffer"
            root.mkdir()
            current, old = "a" * 64, "b" * 64
            current_path = root / f"{current}--g000001--{'c'*64}.json"
            old_path = root / f"{old}--g000001--{'d'*64}.json"
            unknown = root / "manual.json"
            for path in (current_path, old_path, unknown):
                path.write_text("{}", encoding="utf-8")
            result = quarantine_stale_snapshot_inbox(root, current, Path(td) / "quarantine")
            self.assertEqual(len(result["moved"]), 1)
            self.assertTrue(current_path.exists())
            self.assertFalse(old_path.exists())
            self.assertTrue(unknown.exists())

        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest(queue(range(400000, 400025)), contract, store, now=NOW)
            work["web_evidence_contract_binding"] = current_worker_contract_binding()
            manifest_path = Path(contract["paths"]["work_manifest"])
            manifest_path.write_text(json.dumps(work), encoding="utf-8")
            contract_path, _, _ = self._write_contracts(td, contract)
            write_group(work, contract, 1)
            result = drain_inbox_state(manifest_path=manifest_path, contract_path=contract_path, store_dir=store, buffer_dir=contract["paths"]["submission_inbox_dir"], fail_on_blocked=False)
            self.assertEqual(result["accepted_group_count"], 1)
            current_progress = json.loads(manifest_path.read_text())["completed_required_count"]
            write_group(work, contract, 2, lambda a: a["dossiers"][0].__setitem__("schema_version", True))
            blocked = drain_inbox_state(manifest_path=manifest_path, contract_path=contract_path, store_dir=store, buffer_dir=contract["paths"]["submission_inbox_dir"], fail_on_blocked=False)
            self.assertEqual(blocked["status"], "blocked_no_progress")
            self.assertEqual(blocked["blocked_reason"], "invalid_expected_group")
            self.assertEqual(json.loads(manifest_path.read_text())["completed_required_count"], current_progress)


if __name__ == "__main__":
    unittest.main()
