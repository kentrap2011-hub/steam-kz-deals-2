#!/usr/bin/env python3
"""Synthetic Git-only joint Research feasibility -> Assembly Stage B regression.

The original history/source audit is intentionally mocked; the accepted
feasibility *Git commit shape* and Research single-add transport are real.
Existing Research feasibility and source validators run separately in PR CI.
No live marker, source lookup, or semantic computation is performed here.
"""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import dossier_shadow_18_assembly_stage_b as stage
import dossier_shadow_research_feasibility as feasibility
import dossier_shadow_research_trial as research
from dossier_shadow_18_assembly_sandbox import _decision
from dossier_two_stage_contract_guard import _privacy, canonical_sha256
from dossier_two_stage_assembly_semantic_worker import _check_exact_source_first
from dossier_two_stage_staging import blob


class StageBJointGitTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="dossier-pr228-joint-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.git("init", "-b", stage.BRANCH)
        self.git("config", "user.name", "Synthetic only")
        self.git("config", "user.email", "synthetic@example.invalid")
        for path in (stage.PROMPT, stage.CONTRACT):
            self.put(path, (Path(__file__).resolve().parents[1] / path).read_text())
        self.put(stage.RESEARCH_BUFFER, {
            "schema": "SYNTHETIC-FROZEN-BUFFER-ONLY",
            "research_buffer_id": "e" * 64})
        self.commit("Fixture original frozen parent")
        self.parent = self.head()
        self.rnonce = "a" * 32
        self.put(stage.PREFIX + "/run_starts/" + self.rnonce + ".json", {
            "schema": "DOSSIER-SHADOW-RESEARCH-RUN-START-V1",
            "schema_version": 1, "trial_id": stage.TRIAL, "nonce": self.rnonce})
        self.marker = self.commit("Original GitHub marker (synthetic)")
        self.items = []
        for g in _decision()["scope"]["groups"]:
            for i, appid in enumerate(g["appids"]):
                self.items.append({
                    "group_sequence": g["sequence"], "item_index": i,
                    "appid": appid, "assignment": {
                        "appid": appid, "assignment_id": "fixture-" + appid,
                        "title": "Synthetic original " + appid,
                        "web_evidence_contract_binding": {"synthetic": True}}})
        self.trial = {
            "status": "blocked", "sandbox_semantics_authorized": False,
            "marker_commit": self.marker, "marker_parent": self.parent,
            "nonce": self.rnonce, "buffer_path": stage.RESEARCH_BUFFER,
            "buffer_blob_sha": blob(self.root, self.parent, stage.RESEARCH_BUFFER),
            "items": self.items, "canonical_acceptance": False}
        self.authorization = {
            "schema": "SYNTHETIC-GIT-FEASIBILITY",
            "original_marker_commit": self.marker,
            "original_marker_parent": self.parent,
            "research_buffer_blob_sha": self.trial["buffer_blob_sha"],
            "group_order": [3, 8, 13, 15, 18, 20],
            "original_gate_remains_blocked": True}
        self.put(stage.AUTH_PATH, self.authorization)
        self.auth = self.commit("Separate direct-child Research authorization")
        self.assertEqual(self.git("rev-parse", self.auth + "^"), self.marker)
        self.patch_authority = patch.object(
            stage, "authorized_trial", side_effect=self.authorized)
        self.patch_transport = patch.object(
            stage, "inspect_authorized_transport", side_effect=self.transport)
        self.patch_inactive = patch.object(stage, "inactive_assembly_gate")
        for mock in (self.patch_authority, self.patch_transport, self.patch_inactive):
            mock.start()
            self.addCleanup(mock.stop)

    def git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.root), *args],
            stderr=subprocess.PIPE).decode().strip()

    def head(self):
        return self.git("rev-parse", "HEAD")

    def put(self, path, value):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value if isinstance(value, str)
                          else json.dumps(value, sort_keys=True), encoding="utf-8")

    def commit(self, label):
        self.git("add", "-A")
        self.git("commit", "-m", label)
        return self.head()

    def authorized(self, repo, *, marker_commit, buffer_path, authorization_commit):
        # Real accepted PR #227 immutable direct-child and exact payload check,
        # with ONLY the unavailable historical original source audit substituted.
        with patch.object(feasibility, "original_blocked_trial",
                          return_value=self.trial), patch.object(
                feasibility, "expected_authorization",
                return_value=self.authorization):
            trial = feasibility.verify_authorization_commit(
                repo, marker_commit=marker_commit, buffer_path=buffer_path,
                authorization_commit=authorization_commit)
        # Explicitly verify immutable same-branch first-parent ancestry.
        stage.require(
            marker_commit == self.marker and buffer_path == stage.RESEARCH_BUFFER
            and trial["status"] == "blocked"
            and not trial["sandbox_semantics_authorized"]
            and self.git("symbolic-ref", "--short", "HEAD") == stage.BRANCH
            and stage.first_parent_contains(repo, authorization_commit, self.head()),
            "Research separate authority is not on actual sandbox lineage")
        return {**trial, "status": "sandbox_research_invocation_ready",
                "canonical_acceptance": False, "production_authorized": False,
                "feasibility_authorization_commit": authorization_commit}

    def transport(self, repo, *, marker_commit, buffer_path,
                  authorization_commit, ordinal, result_commit, expected_raw=None):
        trial = self.authorized(
            repo, marker_commit=marker_commit, buffer_path=buffer_path,
            authorization_commit=authorization_commit)
        stage.require(0 <= ordinal < 18 and
                      stage.first_parent_contains(repo, self.auth, result_commit),
                      "original Research submission predates feasibility authorization")
        # Real strict Git create-only path, parent, current-blob, raw SHA256,
        # canonical SHA and original marker transport; semantics mocked only.
        with patch.object(research, "validate_candidate", return_value={
                "status": "structural_research_valid_not_accepted",
                "canonical_acceptance": False}):
            return research.inspect_transport(
                repo, trial=trial, item=self.items[ordinal],
                result_commit=result_commit, expected_raw=expected_raw)

    def research_result(self, index, payload=None):
        path = research.sandbox_output_path(self.items[index])
        self.put(path, payload or {
            "synthetic_package": True,
            "appid": self.items[index]["appid"],
            "identity": {"original_work_release_year": 2000},
            "sources": [], "research_audit": {"unresolved_gaps": []}})
        return self.commit("Submit one original Research package (synthetic)")

    def issue(self):
        plan = stage.prepare(
            self.root, research_marker_commit=self.marker,
            research_authorization_commit=self.auth)
        self.put(stage.BUFFER, plan)
        self.plan_commit = self.commit("Stage B GitHub plan (synthetic)")
        nonce = "b" * 32
        self.marker_path = stage.MARKERS + "/" + nonce + ".json"
        self.put(self.marker_path, {
            "schema": "DOSSIER-SHADOW-ASSEMBLY-RUN-START-V1",
            "schema_version": 1, "trial_id": stage.TRIAL, "nonce": nonce,
            "issuer_workflow": "issue-dossier-shadow-18-assembly.yml",
            "issuer_run_id": 12345,
            "buffer_blob_sha": blob(self.root, self.plan_commit, stage.BUFFER)})
        self.assembly_marker = self.commit("Stage B GitHub marker (synthetic)")
        return plan

    def test_01_original_blocked_but_separate_ready_18_order(self):
        plan = stage.prepare(
            self.root, research_marker_commit=self.marker,
            research_authorization_commit=self.auth)
        self.assertFalse(self.trial["sandbox_semantics_authorized"])
        self.assertEqual(self.trial["status"], "blocked")
        self.assertEqual(plan["groups"], [3, 8, 13, 15, 18, 20])
        self.assertEqual(len(plan["items"]), 18)
        self.assertEqual(plan["research_authorization_commit"], self.auth)
        self.assertEqual(plan["research_authorization_path"], stage.AUTH_PATH)
        self.assertEqual(plan["research_authorization_blob_sha"],
                         blob(self.root, self.auth, stage.AUTH_PATH))
        self.assertEqual(plan["buffer_id"], canonical_sha256({
            k: v for k, v in plan.items() if k != "buffer_id"}))
        self.assertEqual(plan["production_writes"], [])
        self.assertFalse(plan["canonical_acceptance"])

    def test_02_wrong_authority_and_foreign_child_fail_closed(self):
        with self.assertRaises(ValueError):
            stage.prepare(self.root, research_marker_commit=self.marker,
                          research_authorization_commit=self.marker)
        self.items[1]["appid"] = "999"
        with self.assertRaisesRegex(ValueError, "original"):
            stage.prepare(self.root, research_marker_commit=self.marker,
                          research_authorization_commit=self.auth)

    def test_03_wrong_original_marker_and_branch_fail_closed(self):
        with self.assertRaises(ValueError):
            stage.prepare(self.root, research_marker_commit="0" * 40,
                          research_authorization_commit=self.auth)
        self.git("checkout", "-b", "another-unapproved-sandbox")
        with self.assertRaises(ValueError):
            stage.prepare(self.root, research_marker_commit=self.marker,
                          research_authorization_commit=self.auth)

    def test_04_GitHub_direct_child_add_only_authorization_required(self):
        # A worker JSON path or a SHA not directly parented by original marker
        # is NOT a substitute for exact GitHub feasibility authority.
        self.put(stage.AUTH_PATH, {"claimed_approved": True})
        forged = self.commit("Rewrite fake authorization")
        with self.assertRaises(ValueError):
            stage.prepare(self.root, research_marker_commit=self.marker,
                          research_authorization_commit=forged)
        with self.assertRaisesRegex(ValueError, "overwritten"):
            stage.prepare(self.root, research_marker_commit=self.marker,
                          research_authorization_commit=self.auth)

    def test_05_valid_B_C_submitted_after_auth_before_Assembly_A_missing(self):
        b = self.research_result(1)
        c = self.research_result(2)
        self.issue()
        state = stage.inspect(self.root, marker_commit=self.assembly_marker,
                              research_commits={
                                  self.items[1]["appid"]: b,
                                  self.items[2]["appid"]: c})
        self.assertEqual([x["status"] for x in state["rows"][:3]],
                         ["research_not_submitted", "ready", "ready"])
        self.assertEqual(state["ready_count"], 2)
        self.assertEqual(state["semantic_attempts"], 0)
        self.assertFalse(state["deep_ready"])
        self.assertTrue(all(not x["attempt_consumed"] for x in state["rows"]))
        self.assertEqual(state["rows"][1]["research_proof"]["result_commit"], b)

    def test_06_invalid_A_does_not_stop_valid_B_or_C(self):
        b = self.research_result(1)
        c = self.research_result(2)
        self.issue()
        state = stage.inspect(self.root, marker_commit=self.assembly_marker,
                              research_commits={
                                  self.items[0]["appid"]: b,  # wrong appid/path
                                  self.items[1]["appid"]: b,
                                  self.items[2]["appid"]: c})
        self.assertEqual([x["status"] for x in state["rows"][:3]],
                         ["research_transport_invalid", "ready", "ready"])
        with self.assertRaisesRegex(ValueError, "foreign"):
            stage.inspect(self.root, marker_commit=self.assembly_marker,
                          research_commits={"not-an-appid": b})

    def test_07_mutated_Research_blob_invalid_without_blocking_sibling(self):
        b = self.research_result(1)
        c = self.research_result(2)
        self.issue()
        self.put(research.sandbox_output_path(self.items[1]), {"tampered": True})
        self.commit("Illegal overwrite original Research bytes")
        state = stage.inspect(self.root, marker_commit=self.assembly_marker,
                              research_commits={
                                  self.items[1]["appid"]: b,
                                  self.items[2]["appid"]: c})
        self.assertEqual([x["status"] for x in state["rows"][1:3]],
                         ["research_transport_invalid", "ready"])

    def test_08_mutated_plan_or_fake_marker_blocks_globally(self):
        self.issue()
        self.put(stage.BUFFER, {"tampered": True})
        self.commit("Illegal overwrite Stage B manifest")
        with self.assertRaises(ValueError):
            stage.frozen(self.root, marker_commit=self.assembly_marker)
        self.put(stage.MARKERS + "/" + "c" * 32 + ".json", {"fake": True})
        bad = self.commit("Fake alternate marker")
        with self.assertRaises(ValueError):
            stage.marker_parent(self.root, bad)

    def test_09_candidate_plus_production_write_is_rejected(self):
        self.issue()
        appid = self.items[0]["appid"]
        output = stage.result_path(stage.prepare(
            self.root, research_marker_commit=self.marker,
            research_authorization_commit=self.auth)["items"][0])
        self.put(output, {"fake": True})
        self.put("data/cache/taste_steam_review_dossiers/bad.json", {"bad": True})
        bad = self.commit("Illegal Assembly plus canonical cache write")
        with patch.object(stage, "inspect", return_value={
                "rows": [{"appid": appid, "output_path": output}]}):
            with self.assertRaises(ValueError):
                stage.verify_candidate(self.root, marker_commit=self.assembly_marker,
                                       research_commits={}, appid=appid,
                                       result_commit=bad)

    def test_10_privacy_wrong_source_and_wrong_year_reuse_existing_gates(self):
        with self.assertRaises(ValueError):
            _privacy({"steam_id": "123456789"})
        package = {
            "assignment": {"appid": "123", "title": "Exact original"},
            "identity": {"original_work_release_year": 1997},
            "sources": [{"ref": "source-A"}],
            "research_audit": {"unresolved_gaps": [{
                "gap_id": "gap-1", "field_or_dimension": "combat",
                "source_refs": ["source-A"]}]}}
        operation = {
            "gap_id": "gap-1", "source_ref": "WRONG-SOURCE",
            "missing_field_or_dimension": "combat"}
        with self.assertRaises(ValueError):
            _check_exact_source_first(package, [operation])
        operation["source_ref"] = "source-A"
        operation["missing_field_or_dimension"] = "wrong-original-work-year"
        with self.assertRaises(ValueError):
            _check_exact_source_first(package, [operation])

    def test_11_only_exact_GitHub_dispatch_identity_can_issue(self):
        base = {
            "GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "workflow_dispatch",
            "GITHUB_REPOSITORY": "kentrap2011-hub/steam-kz-deals-2",
            "GITHUB_RUN_ATTEMPT": "1", "GITHUB_REF_NAME": stage.BRANCH,
            "GITHUB_WORKFLOW_REF": "kentrap2011-hub/steam-kz-deals-2/"
            ".github/workflows/issue-dossier-shadow-18-assembly.yml@refs/heads/"
            + stage.BRANCH}
        with patch.dict("os.environ", base, clear=True):
            stage._issuer_env()
        for key, bad in [("GITHUB_REPOSITORY", "another/repo"),
                         ("GITHUB_RUN_ATTEMPT", "2"),
                         ("GITHUB_REF_NAME", "sandbox/other"),
                         ("GITHUB_WORKFLOW_REF", "forged")]:
            bad_env = {**base, key: bad}
            with patch.dict("os.environ", bad_env, clear=True):
                with self.assertRaises(ValueError):
                    stage._issuer_env()


if __name__ == "__main__":
    unittest.main()
