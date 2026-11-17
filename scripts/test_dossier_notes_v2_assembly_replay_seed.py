#!/usr/bin/env python3
"""Bounded adversarial REPLAY scope/transport tests; no live GitHub writes."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_dossier_notes_v2_batch_route import source_copy, git, add
from test_dossier_notes_v2_owner_push import synthetic_push_issuer
import dossier_notes_v2_assembly_replay_seed as replay
import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_per_item_receipts as receipts
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import parent, require_only_new

NEW = replay.NEW


class ResearchReplayFixtureTests(unittest.TestCase):
    def test_exact_replay_is_six_and_no_semantic_research(self):
        temp, repo = source_copy()
        try:
            src = replay.validate_source_contract(repo)
            self.assertEqual(set(src["candidate_commits"]), set(replay.SIX))
            self.assertEqual(set(src["research_receipt_blobs"]), set(replay.SIX))
            self.assertEqual(src["sandbox_head"], replay.OLD_HEAD)
            self.assertEqual(src["marker_commit"], replay.OLD_MARKER)
            self.assertEqual([x["appid"] for x in batch.rows(repo, NEW)],
                             list(replay.SIX))
            self.assertNotIn("semantic_Research", str(src))
            self.assertEqual(batch.owner_push_workflow(NEW),
                batch.OWNER_PUSH_REPLAY_WORKFLOW)
            with self.assertRaises(ValueError):
                batch.owner_push_workflow("dossier-notes-v2-arbitrary-retry-99")
            with self.assertRaises(ValueError):
                batch.expected_authorization(repo, "dossier-notes-v2-arbitrary-retry-99",
                    "0"*40,"0"*40,"1","owner_main_push")
        finally:
            temp.cleanup()

    def test_old_git_pins_are_not_worker_selectable(self):
        temp, repo = source_copy()
        try:
            path = repo / batch.paths(NEW)["contract"]
            saved = path.read_bytes()
            for field, value in (
                ("sandbox_head", "f"*40), ("trial_id", "different-old"),
                ("marker_commit", "f"*40), ("manifest_blob_sha", "f"*40),
                ("mode", "self_authorized_retry"),
            ):
                d = json.loads(saved)
                d["replay_source"][field] = value
                path.write_text(json.dumps(d), encoding="utf-8")
                with self.subTest(field=field), self.assertRaises(ValueError):
                    replay.validate_source_contract(repo)
            for field in ("candidate_commits", "candidate_blobs", "research_receipt_blobs"):
                d = json.loads(saved)
                d["replay_source"][field]["1000010"] = "not_a_git_sha"
                path.write_text(json.dumps(d), encoding="utf-8")
                with self.subTest(field=field), self.assertRaises(ValueError):
                    replay.validate_source_contract(repo)
            path.write_bytes(saved)
            self.assertEqual(replay.validate_source_contract(repo)["trial_id"], replay.OLD)
        finally:
            temp.cleanup()

    def test_new_git_intro_and_receipt_must_be_create_only(self):
        temp, repo = source_copy()
        try:
            f = synthetic_push_issuer(repo, trial=NEW)
            git(repo, "checkout", "-B", "sandbox/" + NEW, f["auth"])
            appid = replay.SIX[0]
            assignment = v2.frozen_assignment(repo, marker_commit=f["marker"],
                                               trial_id=NEW, appid=appid)
            source = {
                "schema": "DOSSIER-RESEARCH-NOTES-V2",
                "schema_version": 2, "assignment": assignment,
                "notes_text": "Existing Research text; strictly no fresh semantic work",
                "research_status": "limited_evidence",
            }
            plan = receipts.prepare_candidate(repo, marker_commit=f["marker"],
                        trial_id=NEW, appid=appid,
                        authorization_commit=f["auth"], document=source)
            candidate = replay.single_add(repo, plan["output_path"], plan["bytes"], "fixture copy")
            self.assertEqual(require_only_new(repo,candidate,[plan["output_path"]]),
                             f["auth"])
            with self.assertRaises(ValueError):
                replay.single_add(repo, plan["output_path"], plan["bytes"], "duplicate")
            receipt_plan = receipts.prepare_receipt(repo, marker_commit=f["marker"],
                trial_id=NEW, appid=appid, authorization_commit=f["auth"],
                introduction_commit=candidate)
            receipt = replay.single_add(repo,receipt_plan["receipt_path"],
                                        receipt_plan["receipt_bytes"],"fixture receipt")
            proven = receipts.inspect_receipt_commit(repo,marker_commit=f["marker"],
                trial_id=NEW,appid=appid,authorization_commit=f["auth"],
                introduction_commit=candidate,receipt_commit=receipt)
            self.assertEqual(proven["disposition"], "safe_incomplete_research")
            self.assertNotIn("research", str(proven.get("canonical_acceptance")))
        finally:
            temp.cleanup()

    def test_replay_only_runs_after_new_issuer_and_old_frozen_remote(self):
        temp, repo = source_copy()
        try:
            with self.assertRaises(ValueError):
                replay.seed(repo,trial_id="dossier-notes-v2-arbitrary-retry-99",
                            marker_commit="0"*40,authorization_commit="1"*40)
            # Even a correct trial cannot silently use unissued history.
            with self.assertRaises(ValueError):
                replay.seed(repo,trial_id=NEW,marker_commit="0"*40,
                            authorization_commit="1"*40)
        finally:
            temp.cleanup()

    def test_one_exact_owner_main_push_workflow_not_scheduler(self):
        root = Path(__file__).resolve().parents[1]
        yaml = (root / batch.OWNER_PUSH_REPLAY_WORKFLOW).read_text(encoding="utf-8")
        self.assertIn("paths:", yaml)
        self.assertIn("config/dossier_notes_v2_batches/" + NEW + ".json", yaml)
        self.assertIn("batch_issuer.py owner-push-launch", yaml)
        self.assertIn("GITHUB_TOKEN:", yaml)
        self.assertIn("cancel-in-progress: false", yaml)
        for forbidden in ("schedule:", "workflow_dispatch:", "pull_request:",
                          "retry", "force-with-lease"):
            self.assertNotIn(forbidden, yaml)
        self.assertNotIn("create_file", yaml)


if __name__ == "__main__":
    unittest.main()
