#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ingest_taste_steam_review_dossier_inbox import drain_inbox_state
from taste_steam_review_dossier import DOSSIER_SCHEMA
from taste_steam_review_dossier_buffered import expected_buffer_path, validate_buffer_artifact
from taste_steam_review_dossier_daily import BUFFER_GROUP_SCHEMA, build_daily_work_manifest, load_contract
from taste_steam_review_dossier_recovery import (
    load_recovery_contract,
    process_recovery_request,
    quarantine_stale_snapshot_inbox,
)
from taste_steam_review_dossier_strict import load_worker_schema, validate_dossier_strict

ROOT = Path(__file__).resolve().parents[1]
BASE_CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
BASE_RECOVERY = load_recovery_contract(ROOT / "config/taste_steam_review_dossier_recovery_contract.json")
SCHEMA = load_worker_schema(ROOT / "config/taste_steam_review_dossier_schema.json")
NOW = datetime(2026, 9, 15, 10, 0, tzinfo=timezone.utc)


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
    appid = str(appid)
    return {
        "schema": DOSSIER_SCHEMA,
        "schema_version": 1,
        "key": f"App_{appid}",  # current additional-field policy remains permissive
        "appid": appid,
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


def contract_for(td):
    root = Path(td)
    contract = copy.deepcopy(BASE_CONTRACT)
    contract["paths"]["submission_inbox_dir"] = (root / "buffer").as_posix()
    contract["paths"]["work_manifest"] = (root / "work.json").as_posix()
    contract["paths"]["worker_index"] = (root / "worker_index.json").as_posix()
    contract["paths"]["worker_groups_root"] = (root / "worker_groups").as_posix()
    contract["worker_read_projection"]["canonical_source"] = contract["paths"]["work_manifest"]
    contract["worker_read_projection"]["descriptor_path_template"] = (
        contract["paths"]["worker_groups_root"] + "/{snapshot_id}/g{sequence:06d}.json"
    )
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


class StrictSchemaTests(unittest.TestCase):
    def assertInvalid(self, mutate):
        doc = dossier(123456)
        mutate(doc)
        with self.assertRaises(ValueError):
            validate_dossier_strict(
                doc,
                BASE_CONTRACT,
                expected_appid="123456",
                expected_title="Game 123456",
                expected_ttl_days=20,
                now=NOW,
            )

    def test_schema_prompt_and_contract_enum_alignment(self):
        self.assertEqual(SCHEMA["enums"]["observation_category"], BASE_CONTRACT["neutrality"]["allowed_categories"])
        self.assertEqual(SCHEMA["enums"]["sentiment"], BASE_CONTRACT["neutrality"]["allowed_observation_sentiments"])
        self.assertEqual(SCHEMA["enums"]["recurrence"], BASE_CONTRACT["neutrality"]["allowed_recurrence"])
        self.assertEqual(
            set(SCHEMA["required_top_level_fields"]),
            set(BASE_CONTRACT["required_dossier_fields"]) | {"schema", "schema_version"},
        )
        prompt = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")
        self.assertIn("config/taste_steam_review_dossier_schema.json", prompt)
        self.assertIn('category:"content"', prompt)
        self.assertIn("source-dependent semantics that are deferred", prompt)

    def test_valid_current_shape_and_extra_key_remain_allowed(self):
        doc = dossier(123456)
        self.assertIs(validate_dossier_strict(doc, BASE_CONTRACT, expected_appid="123456", expected_title="Game 123456", expected_ttl_days=20, now=NOW), doc)

    def test_content_category_wrong_title_and_appid_url_binding_rejected(self):
        self.assertInvalid(lambda d: d["observations"][0].__setitem__("category", "content"))
        self.assertInvalid(lambda d: d.__setitem__("title", "Wrong title"))
        self.assertInvalid(lambda d: d["provenance"]["steam_reviews"].__setitem__("url", "https://store.steampowered.com/appreviews/999999"))

    def test_bool_as_int_and_numeric_appid_rejected(self):
        for mutate in (
            lambda d: d.__setitem__("schema_version", True),
            lambda d: d.__setitem__("ttl_days", True),
            lambda d: d["observations"][0].__setitem__("mention_count", True),
            lambda d: d["review_sample"].__setitem__("sampled_total", True),
            lambda d: d["review_sample"]["lanes"][0].__setitem__("sampled", True),
            lambda d: d["review_sample"]["lanes"][0].__setitem__("batches", True),
            lambda d: d.__setitem__("appid", 123456),
        ):
            with self.subTest(mutate=mutate):
                self.assertInvalid(mutate)

    def test_duplicate_lanes_count_mismatch_duplicate_observation_rejected(self):
        self.assertInvalid(lambda d: d["review_sample"]["lanes"][1].__setitem__("language_scope", "russian"))
        self.assertInvalid(lambda d: d["review_sample"]["lanes"][0].__setitem__("sampled", 19))
        self.assertInvalid(lambda d: d["observations"].append(copy.deepcopy(d["observations"][0])))

    def test_timestamp_ttl_future_and_required_structure_rejected(self):
        self.assertInvalid(lambda d: d.__setitem__("ttl_days", "20"))
        self.assertInvalid(lambda d: d.__setitem__("expires_at_utc", (NOW + timedelta(days=19)).isoformat()))
        self.assertInvalid(lambda d: (d.__setitem__("generated_at_utc", (NOW + timedelta(minutes=6)).isoformat()), d.__setitem__("expires_at_utc", (NOW + timedelta(days=20, minutes=6)).isoformat())))
        self.assertInvalid(lambda d: d["provenance"].pop("steam_reviews"))
        self.assertInvalid(lambda d: d["provenance"]["store_description"].__setitem__("captured_at_utc", "not-a-time"))


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
            result = process_recovery_request(
                request_path=request_path,
                recovery_contract_path=recovery_path,
                dossier_contract_path=contract_path,
                manifest_path=manifest_path,
            )
            self.assertTrue(result["recovered"])
            self.assertFalse(p1.exists())
            self.assertTrue(p2.exists())
            self.assertEqual(manifest_path.read_text(encoding="utf-8"), before_manifest)
            self.assertTrue(Path(recovery["invalid_expected_artifact_recovery"]["audit_log"]).exists())

            corrected = write_group(work, contract, 1)
            self.assertEqual(corrected, p1)
            drained = drain_inbox_state(
                manifest_path=manifest_path,
                contract_path=contract_path,
                store_dir=store,
                buffer_dir=contract["paths"]["submission_inbox_dir"],
                fail_on_blocked=False,
            )
            self.assertEqual(drained["accepted_group_count"], 2)
            self.assertEqual(drained["accepted_dossier_count"], 20)
            self.assertFalse(p1.exists())
            self.assertFalse(p2.exists())
            after = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(after["completed_required_count"], 20)

    def test_recovery_refuses_valid_expected(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            work = build_daily_work_manifest(queue(range(300000, 300011)), contract, Path(td) / "store", now=NOW)
            manifest_path = Path(contract["paths"]["work_manifest"])
            manifest_path.write_text(json.dumps(work), encoding="utf-8")
            contract_path, recovery_path, recovery = self._write_contracts(td, contract)
            p1 = write_group(work, contract, 1)
            descriptor = work["submission_group_plan"]["groups"][0]
            request = {"schema": recovery["request"]["schema"], "schema_version": 1, "action": recovery["request"]["allowed_action"], "snapshot_id": work["snapshot_id"], "sequence": 1, "group_sha256": descriptor["group_sha256"], "artifact_path": p1.as_posix(), "reason": "must refuse valid"}
            request_path = Path(recovery["request"]["path"])
            request_path.parent.mkdir(parents=True, exist_ok=True)
            request_path.write_text(json.dumps(request), encoding="utf-8")
            with self.assertRaises(ValueError):
                process_recovery_request(request_path=request_path, recovery_contract_path=recovery_path, dossier_contract_path=contract_path, manifest_path=manifest_path)
            self.assertTrue(p1.exists())

    def test_stale_cleanup_quarantines_old_and_preserves_current_and_unrecognized(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "buffer"
            root.mkdir()
            current = "a" * 64
            old = "b" * 64
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

    def test_lost_wakeup_reconciliation_drains_existing_valid_prefix_and_invalid_is_nonfatal(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest(queue(range(400000, 400025)), contract, store, now=NOW)
            manifest_path = Path(contract["paths"]["work_manifest"])
            manifest_path.write_text(json.dumps(work), encoding="utf-8")
            contract_path, _, _ = self._write_contracts(td, contract)
            write_group(work, contract, 1)
            result = drain_inbox_state(manifest_path=manifest_path, contract_path=contract_path, store_dir=store, buffer_dir=contract["paths"]["submission_inbox_dir"], fail_on_blocked=False)
            self.assertEqual(result["accepted_group_count"], 1)
            self.assertEqual(json.loads(manifest_path.read_text())["completed_required_count"], 10)

            current = json.loads(manifest_path.read_text())
            write_group(work, contract, 2, lambda a: a["dossiers"][0].__setitem__("schema_version", True))
            blocked = drain_inbox_state(manifest_path=manifest_path, contract_path=contract_path, store_dir=store, buffer_dir=contract["paths"]["submission_inbox_dir"], fail_on_blocked=False)
            self.assertEqual(blocked["status"], "blocked_no_progress")
            self.assertEqual(blocked["blocked_reason"], "invalid_expected_group")
            self.assertEqual(json.loads(manifest_path.read_text())["completed_required_count"], current["completed_required_count"])

    def test_buffered_title_binding_is_enforced(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            work = build_daily_work_manifest(queue(range(500000, 500010)), contract, Path(td) / "store", now=NOW)
            descriptor = work["submission_group_plan"]["groups"][0]
            artifact = buffered_artifact(work, 1)
            artifact["dossiers"][0]["title"] = "Wrong title"
            with self.assertRaises(ValueError):
                validate_buffer_artifact(artifact, descriptor, work, contract)


if __name__ == "__main__":
    unittest.main()
