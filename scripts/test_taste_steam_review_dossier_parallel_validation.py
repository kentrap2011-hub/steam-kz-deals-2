#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier_buffered import apply_buffered_drain, expected_buffer_path, plan_buffered_drain
from taste_steam_review_dossier_daily import BUFFER_GROUP_SCHEMA, load_contract
from taste_steam_review_dossier_group_progress import reopen_failed_group
from taste_steam_review_dossier_parallel_validation import build_parallel_validation_status
from taste_steam_review_dossier_strict import current_worker_contract_binding
from taste_steam_review_dossier_test_fixture import web_dossier
from taste_steam_review_dossier_web import build_daily_work_manifest_web
from taste_steam_review_dossier_worker_projection import (
    buffered_candidate_descriptor_projection,
    build_worker_projection,
)

ROOT = Path(__file__).resolve().parents[1]
BASE_CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")


def queue(appids):
    return [{
        "taste_subject_key": f"App_{appid}_{index}",
        "appid": str(appid),
        "title": f"Game {appid}",
        "taste_fingerprint": hashlib.sha256(f"taste:{appid}:{index}".encode()).hexdigest(),
        "candidate_context_sha256": hashlib.sha256(f"ctx:{appid}:{index}".encode()).hexdigest(),
        "work_required": ["resolve_grounded_negative_analysis"],
    } for index, appid in enumerate(appids)]


def contract_for(td):
    contract = copy.deepcopy(BASE_CONTRACT)
    contract["paths"]["submission_inbox_dir"] = (Path(td) / "buffer").as_posix()
    return contract


def candidate(work, sequence):
    descriptor = work["submission_group_plan"]["groups"][sequence - 1]
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return {
        "schema": BUFFER_GROUP_SCHEMA,
        "schema_version": 1,
        **copy.deepcopy(descriptor),
        "dossiers": [web_dossier(item["appid"], now, title=item["title"]) for item in descriptor["items"]],
    }


def write_candidate(work, contract, sequence, mutate=None):
    artifact = candidate(work, sequence)
    if mutate:
        mutate(artifact)
    descriptor = work["submission_group_plan"]["groups"][sequence - 1]
    path = expected_buffer_path(descriptor, contract)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


class ParallelValidationTests(unittest.TestCase):
    def test_bad_group_5_does_not_block_good_groups_6_and_7(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            manifest_path = Path(td) / "work.json"
            quarantine = Path(td) / "quarantine"
            audit = Path(td) / "failure.jsonl"
            work = build_daily_work_manifest_web(queue(range(810001, 810022)), contract, store)
            self.assertEqual(len(work["submission_group_plan"]["groups"]), 7)

            # Establish accepted groups 1..4 first.
            for sequence in range(1, 5):
                write_candidate(work, contract, sequence)
            first = plan_buffered_drain(work, contract, contract["paths"]["submission_inbox_dir"], failed_quarantine_root=quarantine)
            self.assertEqual([x["descriptor"]["sequence"] for x in first["accepted"]], [1, 2, 3, 4])
            self.assertEqual(first["failed_count"], 0)
            manifest_path.write_text(json.dumps(work), encoding="utf-8")
            apply_buffered_drain(first, manifest_path=manifest_path, store_dir=store, failure_audit_path=audit)
            current = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(current["group_progress"]["accepted_group_count"], 4)
            self.assertEqual(current["group_progress"]["pending_group_count"], 3)

            p5 = write_candidate(
                current, contract, 5,
                lambda artifact: artifact["dossiers"][0].__setitem__("schema_version", 1),
            )
            p6 = write_candidate(current, contract, 6)
            p7 = write_candidate(current, contract, 7)
            second = plan_buffered_drain(current, contract, contract["paths"]["submission_inbox_dir"], failed_quarantine_root=quarantine)

            self.assertEqual([x["descriptor"]["sequence"] for x in second["failed"]], [5])
            self.assertEqual([x["descriptor"]["sequence"] for x in second["accepted"]], [6, 7])
            apply_buffered_drain(second, manifest_path=manifest_path, store_dir=store, failure_audit_path=audit)
            final = json.loads(manifest_path.read_text(encoding="utf-8"))

            self.assertFalse(p5.exists())
            self.assertFalse(p6.exists())
            self.assertFalse(p7.exists())
            self.assertEqual(final["group_progress"]["accepted_group_count"], 6)
            self.assertEqual(final["group_progress"]["failed_group_count"], 1)
            self.assertEqual(final["group_progress"]["pending_group_count"], 0)
            self.assertTrue(final["group_progress"]["normal_first_pass_complete"])
            self.assertFalse(final["group_progress"]["all_groups_accepted"])
            self.assertFalse(final["full_backlog_complete"])
            self.assertEqual(final["completed_required_count"], 12)  # legacy contiguous accepted prefix only
            self.assertEqual(final["remaining_required_count"], 9)

            # Group 5 is not accepted; groups 6 and 7 were independently persisted.
            for appid in current["submission_group_plan"]["groups"][4]["appids"]:
                self.assertFalse((store / f"App_{appid}.json").exists())
            for sequence in (6, 7):
                for appid in current["submission_group_plan"]["groups"][sequence - 1]["appids"]:
                    self.assertTrue((store / f"App_{appid}.json").exists())

            index, _ = build_worker_projection(final, contract)
            self.assertIsNone(index["next_pending_sequence"])
            self.assertEqual(index["failed_group_sequences"], [5])
            self.assertTrue(index["normal_first_pass_complete"])
            self.assertFalse(index["all_groups_accepted"])

            status = build_parallel_validation_status(final, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual(status["failed_group_count"], 1)
            self.assertEqual(status["failed_groups_pending_recovery"][0]["sequence"], 5)
            self.assertEqual(status["candidate_count"], 0)

    def test_failed_group_recovery_is_separate_and_never_fabricates_acceptance(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            manifest_path = Path(td) / "work.json"
            work = build_daily_work_manifest_web(queue(range(820001, 820007)), contract, store)
            p1 = write_candidate(
                work, contract, 1,
                lambda artifact: artifact["dossiers"][0].__setitem__("schema_version", 1),
            )
            write_candidate(work, contract, 2)
            plan = plan_buffered_drain(
                work, contract, contract["paths"]["submission_inbox_dir"],
                failed_quarantine_root=Path(td) / "quarantine",
            )
            manifest_path.write_text(json.dumps(work), encoding="utf-8")
            apply_buffered_drain(plan, manifest_path=manifest_path, store_dir=store, failure_audit_path=Path(td) / "audit.jsonl")
            failed = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertFalse(p1.exists())
            self.assertTrue(failed["group_progress"]["normal_first_pass_complete"])
            self.assertEqual(failed["group_progress"]["failed_group_count"], 1)

            reopened = reopen_failed_group(failed, contract, 1)
            self.assertEqual(reopened["group_progress"]["groups"][0]["state"], "pending")
            self.assertEqual(reopened["group_progress"]["accepted_group_count"], 1)
            self.assertEqual(reopened["group_progress"]["failed_group_count"], 0)
            self.assertEqual(reopened["group_progress"]["pending_group_count"], 1)
            self.assertFalse(reopened["group_progress"]["normal_first_pass_complete"])

    def test_control_plane_owns_next_pending_and_forbids_schedule_edit(self):
        ownership = json.loads((ROOT / "config/execution_ownership_contract.json").read_text(encoding="utf-8"))
        forbidden = ownership["scheduled_chatgpt_runtime_data_plane"]["forbidden"]
        self.assertIn("enable_disable_pause_delete_reschedule_or_edit_its_own_scheduled_task", forbidden)
        dossier = ownership["taste_steam_review_dossier_nonblocking_progress"]
        self.assertEqual(dossier["owner"], "github_control_plane")
        self.assertFalse(dossier["failed_group_blocks_unrelated_groups"])
        self.assertFalse(dossier["new_queue_retry_loop_or_scheduler_created"])
        self.assertFalse(dossier["scheduled_worker_may_edit_own_schedule"])

        parallel = json.loads((ROOT / "config/taste_steam_review_dossier_parallel_validation_contract.json").read_text(encoding="utf-8"))
        self.assertEqual(parallel["candidate_publication"]["required_group_size"], 3)
        self.assertFalse(parallel["github_validation"]["partial_per_game_acceptance"])
        self.assertFalse(parallel["github_validation"]["automatic_semantic_retry_or_healing"])
        self.assertFalse(parallel["error_philosophy"]["normal_forward_progress_blocked_by_invalid_group"])

    def test_runtime_prompt_is_index_only_and_outside_semantic_binding(self):
        runtime_path = ROOT / "config/taste_steam_review_dossier_runtime_prompt.md"
        runtime_text = runtime_path.read_text(encoding="utf-8")
        self.assertIn("TASTE-STEAM-REVIEW-DOSSIER-RUNTIME-PROMPT-V1", runtime_text)
        self.assertIn("next_pending_sequence", runtime_text)
        self.assertIn("Exact buffered identity serialization", runtime_text)
        self.assertIn("top-level `items` is mandatory", runtime_text)
        self.assertIn("must never enable, disable, pause, delete, reschedule, or edit its own Scheduled Task", runtime_text)

        runtime_contract = BASE_CONTRACT["worker_runtime_prompt"]
        self.assertEqual(
            runtime_contract["revision"],
            "nonblocking-group-progress-v2-exact-buffer-identity",
        )
        self.assertFalse(runtime_contract["semantic_evidence_binding"])
        self.assertFalse(runtime_contract["descriptor_binding"])
        self.assertTrue(runtime_contract["worker_index_binding"])

        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            work = build_daily_work_manifest_web(queue(range(830001, 830004)), contract, Path(td) / "store")
            index, descriptors = build_worker_projection(work, contract)

        semantic_binding = current_worker_contract_binding()
        self.assertEqual(index["web_evidence_contract_binding"], semantic_binding)
        self.assertEqual(descriptors[0]["web_evidence_contract_binding"], semantic_binding)
        self.assertEqual(index["runtime_prompt_path"], runtime_contract["path"])
        self.assertEqual(index["runtime_prompt_revision"], runtime_contract["revision"])
        self.assertEqual(len(index["runtime_prompt_sha256"]), 64)
        self.assertEqual(
            index["buffer_identity_fields"],
            BASE_CONTRACT["buffered_submission"]["group_plan"]["immutable_descriptor_required_fields"],
        )
        self.assertIn("items", index["buffer_identity_fields"])
        self.assertEqual(
            index["buffer_candidate_serialization_rule"],
            "verbatim_deep_copy_group_descriptor_replace_schema_marker_then_add_dossiers",
        )
        candidate_projection = buffered_candidate_descriptor_projection(descriptors[0], contract)
        self.assertEqual(candidate_projection["items"], descriptors[0]["items"])
        self.assertIsNot(candidate_projection["items"], descriptors[0]["items"])
        self.assertNotIn("schema", candidate_projection)
        self.assertNotIn("schema_version", candidate_projection)
        self.assertNotIn("runtime_prompt_path", descriptors[0])
        self.assertNotIn("runtime_prompt_revision", descriptors[0])
        self.assertNotIn("runtime_prompt_sha256", descriptors[0])

    def test_ingest_workflow_records_status_and_has_no_second_scheduler(self):
        workflow = (ROOT / ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml").read_text(encoding="utf-8")
        self.assertIn("python scripts/ingest_taste_steam_review_dossier_inbox.py --reconcile-nonfatal", workflow)
        self.assertIn("python scripts/taste_steam_review_dossier_parallel_validation.py", workflow)
        self.assertIn("taste_steam_review_dossier_validation_status.json", workflow)
        self.assertNotIn("workflow_dispatch", workflow)


if __name__ == "__main__":
    unittest.main()
