#!/usr/bin/env python3
"""Synthetic-only first-parent authorization and negative tests; never live GitHub."""
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dossier_shadow_research_trial import PREFIX, frozen_trial
from dossier_shadow_research_trial_publish import BUFFER, BRANCH, ORDER, EXPECTED_APPIDS, commit_new
from dossier_shadow_research_feasibility import (
    AUTH_PATH, FEASIBILITY_CONTRACT, FEASIBILITY_PROMPT, FEASIBILITY_VERIFIER,
    CONFIRMATION, REPOSITORY, WORKFLOW, ORIGINAL_CONTRACT, ORIGINAL_PROMPT,
    assert_authorizing_dispatch, check_contract, expected_authorization,
    verify_authorization_commit, authorized_trial, original_blocked_trial,
)

ROOT = Path(__file__).resolve().parents[1]


def g(root, *cmd):
    result = subprocess.run(["git", "-C", str(root), *cmd],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        raise AssertionError("disposable Git fixture failure " + repr(cmd) + ": "
                             + result.stderr.decode(errors="replace"))
    return result.stdout.decode().strip()


class FeasibilityAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="research-feasibility-only-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        g(self.repo, "init", "-q")
        g(self.repo, "config", "user.name", "Isolated CI synthetic")
        g(self.repo, "config", "user.email", "synthetic@example.invalid")
        for path in (FEASIBILITY_CONTRACT, FEASIBILITY_PROMPT, FEASIBILITY_VERIFIER,
                     ORIGINAL_CONTRACT, ORIGINAL_PROMPT,
                     "config/dossier_research_package_v1.schema.json"):
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
        target = self.repo / BUFFER
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('{"research_buffer_id":"fixture-buffer"}\n', encoding="utf-8")
        g(self.repo, "add", ".")
        g(self.repo, "commit", "-qm", "synthetic buffer-parent with frozen source bytes")
        self.parent = g(self.repo, "rev-parse", "HEAD")
        self.nonce = "a" * 32
        marker_path = PREFIX + "/run_starts/" + self.nonce + ".json"
        marker_doc = {"schema": "DOSSIER-SHADOW-RESEARCH-RUN-START-V1",
                      "schema_version": 1, "trial_id":
                      "dossier-shadow-calibration-20261011-6x3", "nonce": self.nonce}
        self.marker = commit_new(self.repo, marker_path,
                                 (json.dumps(marker_doc)+"\n").encode(),
                                 "synthetic original marker")
        from dossier_shadow_research_trial import blob
        self.trial = {"marker_commit": self.marker, "marker_parent": self.parent,
                      "nonce": self.nonce, "buffer_blob_sha": blob(self.repo, self.parent, BUFFER)}
        self.mock_original = patch(
            "dossier_shadow_research_feasibility.original_blocked_trial",
            return_value=self.trial)

    def add_auth(self, doc=None):
        raw = (json.dumps(doc if doc is not None else expected_authorization(
            self.repo, self.trial), sort_keys=True) + "\n").encode()
        return commit_new(self.repo, AUTH_PATH, raw, "synthetic research feasibility auth")

    def test_01_missing_real_original_historical_freeze_never_authorizes(self):
        with self.assertRaises(Exception):
            original_blocked_trial(self.repo, self.marker, BUFFER)
        with self.assertRaises(Exception):
            frozen_trial(self.repo, marker_commit=self.marker, buffer_path=BUFFER)
        with self.assertRaises(Exception):
            original_blocked_trial(self.repo, "0"*40, BUFFER)

    def test_02_static_contract_keeps_AB_C_later_and_no_production(self):
        cfg = check_contract(self.repo, self.parent)
        self.assertEqual(cfg["group_order"], ORDER)
        self.assertEqual(cfg["appids"], EXPECTED_APPIDS)
        self.assertEqual(len(cfg["appids"]), 18)
        self.assertFalse(cfg["reviewer_AB_C_appointment_required_before_feasibility"])
        self.assertFalse(cfg["assembly_authorized"])
        self.assertFalse(cfg["production_execution"])
        self.assertFalse(cfg["scheduled_tasks"])
        self.assertTrue(cfg["original_sandbox_flags_must_stay_false"])

    def test_03_no_authorization_commit_before_second_publication(self):
        with self.mock_original:
            with self.assertRaises(Exception):
                verify_authorization_commit(self.repo, marker_commit=self.marker,
                                            buffer_path=BUFFER, authorization_commit=self.marker)
            with self.assertRaises(Exception):
                verify_authorization_commit(self.repo, marker_commit=self.marker,
                                            buffer_path=BUFFER, authorization_commit="0"*40)

    def test_04_exact_second_create_only_commit_preserves_original_marker(self):
        auth = self.add_auth()
        with self.mock_original:
            out = verify_authorization_commit(
                self.repo, marker_commit=self.marker, buffer_path=BUFFER,
                authorization_commit=auth)
            self.assertEqual(out["marker_parent"], self.parent)
        self.assertEqual(g(self.repo,"rev-list","--parents","-n","1",auth).split(),
                         [auth, self.marker])
        self.assertEqual(g(self.repo,"diff-tree","--no-commit-id","--name-status","-r",auth),
                         "A\t" + AUTH_PATH)
        self.assertEqual(g(self.repo,"rev-parse",self.marker + ":" + BUFFER),
                         g(self.repo,"rev-parse",auth + ":" + BUFFER))
        with self.assertRaisesRegex(RuntimeError, "already exists"):
            self.add_auth()

    def test_05_wrong_original_parent_or_marker_rejected(self):
        (self.repo / "note.txt").write_text("unauthorized middle commit\n")
        g(self.repo, "add", "note.txt")
        g(self.repo, "commit", "-qm", "intermediate unapproved commit")
        auth = self.add_auth()
        with self.mock_original, self.assertRaisesRegex(ValueError, "direct child"):
            verify_authorization_commit(self.repo, marker_commit=self.marker,
                                        buffer_path=BUFFER, authorization_commit=auth)

    def test_06_wrong_buffer_or_original_contract_prompt_verifier_rejected(self):
        doc = expected_authorization(self.repo, self.trial)
        doc["research_buffer_blob_sha"] = "0"*40
        doc["feasibility_prompt_blob_sha"] = "f"*40
        doc["original_trial_contract_blob_sha"] = "f"*40
        doc["feasibility_verifier_blob_sha"] = "f"*40
        auth = self.add_auth(doc)
        with self.mock_original, self.assertRaisesRegex(ValueError, "binding mismatch"):
            verify_authorization_commit(self.repo, marker_commit=self.marker,
                                        buffer_path=BUFFER, authorization_commit=auth)

    def test_06b_each_individual_pin_mismatch_fails_closed(self):
        keys = (
            "original_marker_commit", "original_marker_parent",
            "original_marker_nonce", "research_buffer_blob_sha",
            "research_buffer_id", "original_trial_contract_blob_sha",
            "original_semantic_prompt_blob_sha", "feasibility_contract_blob_sha",
            "feasibility_prompt_blob_sha", "feasibility_verifier_blob_sha",
            "research_schema_blob_sha",
        )
        for key in keys:
            with self.subTest(binding=key):
                doc = copy.deepcopy(expected_authorization(self.repo, self.trial))
                doc[key] = "tampered"
                auth = self.add_auth(doc)
                with self.mock_original, self.assertRaisesRegex(
                    ValueError, "binding mismatch"
                ):
                    verify_authorization_commit(
                        self.repo, marker_commit=self.marker, buffer_path=BUFFER,
                        authorization_commit=auth)
                # Reset only the disposable synthetic test checkout; no GitHub ref.
                g(self.repo, "reset", "--hard", self.marker)

    def test_07_wrong_item_or_quality_status_rejected(self):
        doc = expected_authorization(self.repo, self.trial)
        doc["appids"][0] = "999"
        doc["production_authorized"] = True
        doc["quality_gate"] = "approved"
        auth = self.add_auth(doc)
        with self.mock_original, self.assertRaisesRegex(ValueError, "binding mismatch"):
            verify_authorization_commit(self.repo, marker_commit=self.marker,
                                        buffer_path=BUFFER, authorization_commit=auth)

    def test_08_extra_file_and_rewritten_authorization_are_rejected(self):
        doc = expected_authorization(self.repo, self.trial)
        p = self.repo / AUTH_PATH
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc), encoding="utf-8")
        extra = self.repo / "data" / "cache" / "danger.json"
        extra.parent.mkdir(parents=True, exist_ok=True)
        extra.write_text("{}")
        g(self.repo,"add",".")
        g(self.repo,"commit","-qm","synthetic forbidden two-file auth")
        auth = g(self.repo,"rev-parse","HEAD")
        with self.mock_original, self.assertRaisesRegex(ValueError, "ONLY"):
            verify_authorization_commit(self.repo, marker_commit=self.marker,
                                        buffer_path=BUFFER, authorization_commit=auth)

    def test_09_no_ready_until_remote_branch_contains_real_authorization(self):
        bare = self.root / "remote.git"
        g(self.root, "init", "--bare", str(bare))
        g(self.repo, "remote", "add", "origin", str(bare))
        branch_ref = "refs/heads/" + BRANCH
        g(self.repo, "push", "origin", self.marker + ":" + branch_ref)
        auth = self.add_auth()
        # Strictly synthetic: patch only the external GitHub URL check; no
        # synthetic Git fixture can claim to be genuine durable GitHub authority.
        with self.mock_original, patch(
            "dossier_shadow_research_feasibility.assert_canonical_remote"
        ):
            with self.assertRaisesRegex(ValueError, "not on live sandbox"):
                authorized_trial(self.repo, marker_commit=self.marker, buffer_path=BUFFER,
                                 authorization_commit=auth)
            g(self.repo,"push","origin",auth+":"+branch_ref)
            out = authorized_trial(self.repo, marker_commit=self.marker,
                                   buffer_path=BUFFER, authorization_commit=auth)
            self.assertEqual(out["status"], "sandbox_research_invocation_ready")
            self.assertFalse(out["canonical_acceptance"])
            self.assertFalse(out["production_authorized"])
            self.assertFalse(out["quality_AB_C_completed"])

    def test_10_only_main_first_dispatch_single_use_confirmation(self):
        expected = "b"*40
        env = {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "workflow_dispatch",
               "GITHUB_REPOSITORY": REPOSITORY, "GITHUB_REF": "refs/heads/main",
               "GITHUB_WORKFLOW_REF": REPOSITORY+"/"+WORKFLOW+"@refs/heads/main",
               "GITHUB_SHA": expected, "GITHUB_RUN_ATTEMPT": "1"}
        assert_authorizing_dispatch(expected, self.marker, CONFIRMATION, env)
        for key, bad in (
            ("GITHUB_EVENT_NAME","schedule"), ("GITHUB_RUN_ATTEMPT","2"),
            ("GITHUB_REF","refs/heads/sandbox"), ("GITHUB_REPOSITORY","wrong/repo"),
            ("GITHUB_SHA","0"*40), ("GITHUB_WORKFLOW_REF","bad/workflow"),
        ):
            with self.subTest(key=key), self.assertRaises(ValueError):
                assert_authorizing_dispatch(expected,self.marker,CONFIRMATION,
                                            {**env,key:bad})
        with self.assertRaises(ValueError):
            assert_authorizing_dispatch(expected,self.marker,"DO_NOT_AUTHORIZE",env)
        with self.assertRaises(ValueError):
            assert_authorizing_dispatch(expected,"short",CONFIRMATION,env)

    def test_11_no_scheduled_automatic_or_semantic_action(self):
        yaml = (ROOT / WORKFLOW).read_text("utf-8")
        self.assertIn("workflow_dispatch:",yaml)
        for trigger in ("  schedule:", "  push:", "  pull_request:"):
            self.assertNotIn(trigger,yaml)
        self.assertIn("cancel-in-progress: false",yaml)
        self.assertNotIn("data/ai_inbox/",yaml)
        self.assertNotIn("scripts/dossier_shadow_18_assembly_sandbox.py",yaml)
        original = json.loads((ROOT / ORIGINAL_CONTRACT).read_text())
        self.assertIs(original["standalone_sandbox_semantics_approved"],False)
        self.assertIs(original["reviewer_roles_finalized"],False)


if __name__ == "__main__":
    unittest.main()
