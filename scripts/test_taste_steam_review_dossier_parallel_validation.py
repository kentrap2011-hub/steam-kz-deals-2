#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier_buffered import (
    apply_buffered_drain,
    expected_buffer_path,
    plan_buffered_drain,
)
from taste_steam_review_dossier_daily import BUFFER_GROUP_SCHEMA, load_contract
from taste_steam_review_dossier_parallel_validation import build_parallel_validation_status
from taste_steam_review_dossier_test_fixture import web_dossier
from taste_steam_review_dossier_web import build_daily_work_manifest_web

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
    def test_middle_invalid_group_blocks_progress_but_later_valid_groups_remain_buffered(self):
        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            store = Path(td) / "store"
            work = build_daily_work_manifest_web(queue(range(810001, 810013)), contract, store)
            self.assertEqual(int(contract["checkpointing"]["checkpoint_size"]), 3)
            self.assertEqual(work["completed_required_count"], 0)
            self.assertEqual(len(work["submission_group_plan"]["groups"]), 4)

            p1 = write_candidate(work, contract, 1)
            p2 = write_candidate(
                work,
                contract,
                2,
                lambda artifact: artifact["dossiers"][0].__setitem__("schema_version", 1),
            )
            p3 = write_candidate(work, contract, 3)
            p4 = write_candidate(work, contract, 4)

            # Candidate publication itself is transport-only: all four groups can
            # exist while canonical progress still expects group 1.
            self.assertEqual(work["completed_required_count"], 0)
            before = {path: path.read_bytes() for path in (p2, p3, p4)}

            plan = plan_buffered_drain(work, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual([entry["descriptor"]["sequence"] for entry in plan["accepted"]], [1])
            self.assertEqual(plan["blocked_reason"], "invalid_expected_group")
            self.assertEqual(plan["stop_sequence"], 2)

            manifest_path = Path(td) / "work.json"
            manifest_path.write_text(json.dumps(work), encoding="utf-8")
            persisted = apply_buffered_drain(plan, manifest_path=manifest_path, store_dir=store)
            current = json.loads(manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(len(persisted), 3)
            self.assertEqual(current["completed_required_count"], 3)
            self.assertEqual(current["remaining_required_count"], 9)
            self.assertFalse(p1.exists())
            for path in (p2, p3, p4):
                self.assertTrue(path.exists())
                self.assertEqual(path.read_bytes(), before[path])

            # No member of invalid group 2 was partially persisted.
            group2_appids = work["submission_group_plan"]["groups"][1]["appids"]
            for appid in group2_appids:
                self.assertFalse((store / f"App_{appid}.json").exists())

            status = build_parallel_validation_status(
                current,
                contract,
                contract["paths"]["submission_inbox_dir"],
            )
            self.assertEqual(status["canonical_expected_sequence"], 2)
            by_sequence = {record["sequence"]: record for record in status["candidate_groups"]}
            self.assertEqual(by_sequence[2]["validation"], "invalid")
            self.assertEqual(by_sequence[2]["canonical_position"], "expected")
            self.assertIsNotNone(by_sequence[2]["validator_error"])
            self.assertEqual(by_sequence[3]["validation"], "valid")
            self.assertEqual(by_sequence[3]["canonical_position"], "later_buffered")
            self.assertEqual(by_sequence[4]["validation"], "valid")
            self.assertEqual(by_sequence[4]["canonical_position"], "later_buffered")
            self.assertEqual(status["invalid_expected_group"]["sequence"], 2)
            self.assertFalse(status["canonical_progress_authority"])
            self.assertFalse(status["retry_state"])

            # Replanning cannot cross the invalid group even though later groups validate.
            blocked_again = plan_buffered_drain(current, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual(blocked_again["accepted_count"], 0)
            self.assertEqual(blocked_again["blocked_reason"], "invalid_expected_group")
            self.assertEqual(blocked_again["stop_sequence"], 2)
            self.assertEqual(blocked_again["next_manifest"]["completed_required_count"], 3)

    def test_worker_contract_is_async_create_only_without_runtime_python_gate(self):
        prompt = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")
        self.assertNotIn("python scripts/taste_steam_review_dossier_prepublication.py", prompt)
        self.assertNotIn("prepublication_validator_unavailable", prompt)
        self.assertIn("candidate buffered", prompt)
        self.assertIn("Do not wait for GitHub validation or canonical acceptance", prompt)
        self.assertIn("local traversal target only to `N+1`", prompt)

        evidence = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
        publication = evidence["prepublication_validation"]
        self.assertFalse(publication["validate_complete_group_before_create_only_publication"])
        self.assertFalse(publication["scheduled_worker_python_execution_required"])
        self.assertTrue(publication["github_validation_after_candidate_write_required"])

        parallel = json.loads((ROOT / "config/taste_steam_review_dossier_parallel_validation_contract.json").read_text(encoding="utf-8"))
        self.assertEqual(parallel["candidate_publication"]["required_group_size"], 3)
        self.assertFalse(parallel["github_validation"]["partial_per_game_acceptance"])
        self.assertFalse(parallel["github_validation"]["automatic_semantic_retry_or_healing"])
        self.assertEqual(
            parallel["validation_status"]["required_binding"],
            ["snapshot_id", "sequence", "group_sha256", "web_evidence_contract_binding"],
        )
        self.assertTrue(parallel["validation_status"]["new_snapshot_supersedes_prior_status"])

    def test_ingest_workflow_records_status_and_treats_semantic_block_as_state_not_retry(self):
        workflow = (ROOT / ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml").read_text(encoding="utf-8")
        self.assertIn("python scripts/ingest_taste_steam_review_dossier_inbox.py --reconcile-nonfatal", workflow)
        self.assertIn("python scripts/taste_steam_review_dossier_parallel_validation.py", workflow)
        self.assertIn("taste_steam_review_dossier_validation_status.json", workflow)
        self.assertNotIn("workflow_dispatch", workflow)


if __name__ == "__main__":
    unittest.main()
