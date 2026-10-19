#!/usr/bin/env python3
"""Offline synthetic Git handoff tests: no live Assembly or Research semantics."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import dossier_shadow_18_github_python_handoff as gh
import dossier_shadow_18_assembly_stage_b as stage
from dossier_shadow_research_trial_publish import EXPECTED_APPIDS
from test_dossier_shadow_18_assembly_stage_b import StageBJointGitTests


class GithubOriginalHandoffTests(unittest.TestCase):
    def setUp(self):
        self.fixture = StageBJointGitTests(methodName="test_01_original_blocked_but_separate_ready_18_order")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def issue_with_submissions(self):
        f = self.fixture
        submitted = {}
        for i, row in enumerate(f.items):
            if row["appid"] not in gh.FIXED_MISSING:
                submitted[row["appid"]] = f.research_result(i)
        f.issue()
        return submitted

    def test_01_pinned_18_exact_scope_and_original_missing(self):
        source = Path(__file__).resolve().parents[1] / "config/dossier_shadow_18_github_python_handoff_pins_v1.json"
        doc = json.loads(source.read_text("utf-8"))
        self.assertEqual(doc["original_research_introduction_commits"],
                         gh.FIXED_RESEARCH_COMMITS)
        self.assertEqual(set(doc["missing_research_appids"]), gh.FIXED_MISSING)
        self.assertEqual(set(EXPECTED_APPIDS),
                         set(gh.FIXED_RESEARCH_COMMITS) | gh.FIXED_MISSING)
        self.assertEqual(len(EXPECTED_APPIDS), 18)
        self.assertEqual(doc["assembly_marker_commit"], gh.FIXED_MARKER)
        self.assertEqual(doc["production_writes"], [])
        self.assertFalse(doc["scheduled_tasks"])
        self.assertFalse(doc["canonical_acceptance"])

    def test_02_canonical_python_14_ready_4_missing_under_mock_semantics(self):
        submitted = self.issue_with_submissions()
        f = self.fixture
        # Genuine fixture Git commits and original stage.inspect, only the
        # unavailable historic source audits and fixed real-SHA pins are mocked.
        with patch.object(gh, "FIXED_MARKER", f.assembly_marker), patch.object(
                gh, "checked", return_value={
                    "original_research_introduction_commits": submitted}):
            s = gh.readiness(f.root, Path("synthetic-pins"), stage)
        self.assertEqual([r["appid"] for r in s["rows"]], EXPECTED_APPIDS)
        self.assertEqual(s["ready_count"], 14)
        self.assertEqual(sum(r["status"] == "research_not_submitted"
                             for r in s["rows"]), 4)
        self.assertFalse(s["deep_ready"])
        self.assertEqual(s["semantic_attempts"], 0)

    def test_03_two_bad_Git_origins_item_local_B_C_still_run(self):
        submitted = self.issue_with_submissions()
        f = self.fixture
        # Wrong committed AppID/path simulates a transport-invalid submission,
        # not a shortcut around actual source provenance checks.
        culprit = "1517180"
        broken = dict(submitted)
        broken["2124120"] = submitted[culprit]
        broken["2138710"] = submitted[culprit]
        with patch.object(gh, "FIXED_MARKER", f.assembly_marker), patch.object(
                gh, "checked", return_value={
                    "original_research_introduction_commits": broken}):
            s = gh.readiness(f.root, Path("synthetic-pins"), stage)
        statuses = {r["appid"]:r["status"] for r in s["rows"]}
        self.assertEqual(statuses["2124120"], "research_transport_invalid")
        self.assertEqual(statuses["2138710"], "research_transport_invalid")
        self.assertEqual(statuses["213610"], "ready")
        self.assertEqual(s["ready_count"], 12)
        self.assertEqual(sum(v == "research_not_submitted"
                             for v in statuses.values()), 4)
        self.assertTrue(all(not r["attempt_consumed"] for r in s["rows"]))

    def test_04_single_file_typed_Git_submission_and_rewrite_rejected(self):
        f = self.fixture
        f.issue()
        handoff_branch = "handoff/dossier-shadow-18-assembly-typed"
        path_prefix = stage.PREFIX.replace("/trials/", "/handoff/")
        f.git("checkout", "-b", handoff_branch)
        path = path_prefix + "/1517180.json"
        semantic = {"outcome": "runtime_or_tool_failure",
                    "payload": {"status": "runtime_or_tool_failure",
                                "gap_id": None, "source_ref": None,
                                "field_or_dimension": None,
                                "safe_diagnostic": "Synthetic offline tool failure",
                                "requires_github_classification": True,
                                "normal_first_pass_attempt_consumed": False},
                    "supplemental_operations": []}
        f.put(path, semantic)
        commit = f.commit("Synthetic only typed create-once semantic input")
        f.git("update-ref", "refs/remotes/origin/" + handoff_branch, commit)
        f.git("checkout", stage.BRANCH)
        pins = {"submission_branch": handoff_branch,
                "submission_namespace": path_prefix}
        with patch.object(gh, "remote_tip", return_value=commit):
            self.assertEqual(gh.semantic_submission(
                f.root, stage, pins, "1517180", commit, commit), semantic)
        with self.assertRaisesRegex(ValueError, "no source Research"):
            with patch.object(gh, "remote_tip", return_value=commit):
                gh.semantic_submission(f.root, stage, pins, "1508750", commit, commit)
        f.git("checkout", handoff_branch)
        altered = dict(semantic)
        altered["forged_marker"] = True
        f.put(path, altered)
        f.commit("Synthetic malicious rewritten semantic bytes")
        f.git("update-ref", "refs/remotes/origin/" + handoff_branch, f.head())
        f.git("checkout", stage.BRANCH)
        with self.assertRaises(ValueError):
            with patch.object(gh, "remote_tip", return_value=f.head()):
                gh.semantic_submission(f.root, stage, pins, "1517180", commit, f.head())

    def test_05_ready_A_unavailable_B_and_C_independent_no_retry(self):
        rows = [
            {"appid": "1508750", "status": "research_not_submitted"},
            {"appid": "1517180", "status": "ready"},  # A never published
            {"appid": "1533420", "status": "ready"},  # B independently allowed
            {"appid": "1590230", "status": "ready"},  # C independently allowed
            {"appid": "2124120", "status": "research_transport_invalid"},
        ]
        state = {"rows": rows}
        gh.original_order_gate(state, "1533420")
        gh.original_order_gate(state, "1590230")
        gh.original_order_gate(state, "1517180")  # no sibling state mutation/retry
        self.assertEqual(rows[1]["status"], "ready")
        self.assertEqual([r["appid"] for r in state["rows"]],
                         [r["appid"] for r in rows])
        for denied in ("1508750", "2124120"):
            with self.assertRaisesRegex(ValueError, "not canonical Python ready"):
                gh.original_order_gate(state, denied)
        with self.assertRaisesRegex(ValueError, "foreign AppID"):
            gh.original_order_gate(state, "999999999")


    def test_06_typed_mock_diagnostic_original_Python_build_and_verify(self):
        # All semantic facts synthetic; the real original Stage B schema,
        # path and Git create-only verifier are deliberately NOT mocked.
        f = self.fixture
        row = f.items[1]
        a = row["assignment"]
        a.update({
            "snapshot_id": "a" * 64,
            "group_sequence": row["group_sequence"],
            "group_sha256": "b" * 64,
            "prepared_required_sha256": "c" * 64,
            "group_plan_sha256": "d" * 64,
            "items_sha256": "e" * 64,
            "item_index": row["item_index"],
            "scope_source": "synthetic_fixture_only",
            "source_queue_sha256": "f" * 64,
            "research_contract_sha256": "0" * 64,
            "web_evidence_contract_binding": {
                "evidence_contract_schema":
                    "TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2",
                "evidence_contract_version": 2,
                "evidence_contract_revision": "synthetic-fixture-v2",
                "evidence_contract_sha256": "1" * 64,
                "worker_schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2",
                "worker_schema_version": 2,
                "worker_schema_revision": "synthetic-fixture-v2",
                "worker_schema_sha256": "2" * 64,
                "dossier_schema": "TASTE-STEAM-REVIEW-DOSSIER-V2",
                "dossier_schema_version": 2,
                "worker_prompt_revision": "synthetic-fixture-v2",
                "worker_prompt_sha256": "3" * 64,
            },
        })
        source_commit = f.research_result(1)
        f.issue()
        semantic = {
            "outcome": "runtime_or_tool_failure",
            "payload": {
                "status": "runtime_or_tool_failure",
                "gap_id": None,
                "source_ref": None,
                "field_or_dimension": None,
                "safe_diagnostic": "Synthetic fixture backend unavailable",
                "requires_github_classification": True,
                "normal_first_pass_attempt_consumed": False,
            },
            "supplemental_operations": [],
        }
        mapping = {row["appid"]: source_commit}
        path, candidate = stage.build_candidate(
            f.root, marker_commit=f.assembly_marker,
            research_commits=mapping, appid=row["appid"], semantic=semantic)
        self.assertTrue(path.startswith(stage.PREFIX + "/assembly/"))
        self.assertFalse(candidate["canonical_acceptance"])
        self.assertTrue(candidate["staged_only"])
        f.put(path, candidate)
        created = f.commit("Fixture typed diagnostic, one-add only")
        proof = stage.verify_candidate(
            f.root, marker_commit=f.assembly_marker,
            research_commits=mapping, appid=row["appid"], result_commit=created)
        self.assertEqual(proof["result_commit"], created)
        self.assertFalse(proof["canonical_acceptance"])
        self.assertFalse(proof["deep_ready"])
        with self.assertRaisesRegex(ValueError, "candidate already exists"):
            stage.build_candidate(
                f.root, marker_commit=f.assembly_marker,
                research_commits=mapping, appid=row["appid"], semantic=semantic)

    def test_07_non_fast_forward_sandbox_race_fails_without_retry(self):
        import subprocess
        with tempfile.TemporaryDirectory(prefix="shadow-race-only-") as tmp:
            remote = Path(tmp) / "remote.git"
            subprocess.run(["git", "init", "--bare", str(remote)],
                           check=True, stdout=subprocess.DEVNULL)
            f = self.fixture
            f.git("remote", "add", "synthetic-race", str(remote))
            f.git("push", "synthetic-race", "HEAD:refs/heads/frozen")
            writers = []
            for suffix in ("one", "two"):
                clone = Path(tmp) / suffix
                subprocess.run(["git", "clone", "--branch", "frozen",
                                str(remote), str(clone)], check=True,
                               stdout=subprocess.DEVNULL)
                for key, value in (("user.name", "fixture"),
                                   ("user.email", "fixture@example.invalid")):
                    subprocess.run(["git", "-C", str(clone), "config",
                                    key, value], check=True)
                (clone / (suffix + ".txt")).write_text(
                    "mock candidate only", encoding="utf-8")
                subprocess.run(["git", "-C", str(clone), "add", "."],
                               check=True)
                subprocess.run(["git", "-C", str(clone), "commit", "-m",
                                "Synthetic one-add"], check=True,
                               stdout=subprocess.DEVNULL)
                writers.append(clone)
            def push(clone):
                return subprocess.run([
                    "git", "-C", str(clone), "push",
                    "origin", "HEAD:refs/heads/frozen"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.assertEqual(push(writers[0]).returncode, 0)
            self.assertNotEqual(push(writers[1]).returncode, 0)

    def test_08_post_marker_single_candidate_allowed_but_code_and_schema_tamper_rejected(self):
        f = self.fixture
        f.issue()
        manifest, _nonce, _parent = stage.frozen(
            f.root, marker_commit=f.assembly_marker)
        allowed = {stage.result_path(e) for e in manifest["items"]}
        path = stage.result_path(manifest["items"][1])
        f.put(path, {"outcome": "synthetic-only"})
        good = f.commit("Synthetic one-add-only original Assembly candidate")
        self.assertEqual(
            gh.validate_sandbox_descendants(
                f.root, stage, f.assembly_marker, good, allowed), 1)
        # Both tampering cases are REAL Git commits on a checkout whose
        # simulated fetched remote tracking tip exactly equals the HEAD.
        for malicious_path in (
            "scripts/dossier_shadow_18_assembly_stage_b.py",
            "config/dossier_async_assembly_result_v1.schema.json",
        ):
            f.git("reset", "--hard", good)
            f.put(malicious_path, "# malicious mutable sandbox authority")
            bad = f.commit("Post-marker Python or strict-schema injection")
            f.git("update-ref", "refs/remotes/origin/" + stage.BRANCH, bad)
            self.assertEqual(f.head(), f.git(
                "rev-parse", "refs/remotes/origin/" + stage.BRANCH))
            with self.assertRaisesRegex(ValueError, "non-authorized path"):
                gh.validate_sandbox_descendants(
                    f.root, stage, f.assembly_marker, bad, allowed)
        f.git("reset", "--hard", good)

    def test_09_semantic_remote_rewrite_with_stale_fetched_tracking_ref(self):
        import subprocess
        f = self.fixture
        f.issue()
        with tempfile.TemporaryDirectory(prefix="shadow-handoff-remote-") as tmp:
            remote = Path(tmp) / "origin.git"
            subprocess.run(["git", "init", "--bare", str(remote)],
                           check=True, stdout=subprocess.DEVNULL)
            f.git("remote", "add", "origin", str(remote))
            handoff_branch = "handoff/dossier-shadow-18-assembly-typed"
            path_prefix = stage.PREFIX.replace("/trials/", "/handoff/")
            f.git("checkout", "-b", handoff_branch)
            path = path_prefix + "/1517180.json"
            original = {"outcome": "runtime_or_tool_failure",
                        "payload": {}, "supplemental_operations": []}
            f.put(path, original)
            commit = f.commit("Exact one-file typed semantic introduction")
            f.git("push", "origin", "HEAD:refs/heads/" + handoff_branch)
            f.git("update-ref", "refs/remotes/origin/" + handoff_branch, commit)
            f.git("checkout", stage.BRANCH)
            pins = {"submission_branch": handoff_branch,
                    "submission_namespace": path_prefix}
            self.assertEqual(gh.semantic_submission(
                f.root, stage, pins, "1517180", commit, commit), original)
            # Remote can be rewritten/withdrawn without changing the local
            # already-fetched tracking ref (the exploit under review).
            subprocess.run(["git", "-C", str(remote), "update-ref",
                            "refs/heads/" + handoff_branch, f.assembly_marker],
                           check=True)
            self.assertEqual(f.git(
                "rev-parse", "refs/remotes/origin/" + handoff_branch), commit)
            with self.assertRaisesRegex(ValueError, "withdrawn or drifted"):
                gh.semantic_submission(
                    f.root, stage, pins, "1517180", commit, commit)
            with self.assertRaisesRegex(ValueError, "withdrawn or drifted"):
                gh.semantic_submission(
                    f.root, stage, pins, "1517180", commit, f.assembly_marker)

    def test_10_extra_file_wrong_path_and_rewrite_in_typed_intro_fail(self):
        f = self.fixture
        f.issue()
        handoff_branch = "handoff/dossier-shadow-18-assembly-typed"
        prefix = stage.PREFIX.replace("/trials/", "/handoff/")
        path = prefix + "/1517180.json"
        f.git("checkout", "-b", handoff_branch)
        # Wrong path: the exact target does not exist at introducing commit.
        f.put(prefix + "/9999999.json", {"outcome": "x"})
        wrong = f.commit("Wrong AppID path")
        f.git("update-ref", "refs/remotes/origin/" + handoff_branch, wrong)
        f.git("checkout", stage.BRANCH)
        p = {"submission_branch": handoff_branch, "submission_namespace": prefix}
        with patch.object(gh, "remote_tip", return_value=wrong):
            with self.assertRaises((ValueError, Exception)):
                gh.semantic_submission(f.root, stage, p, "1517180", wrong, wrong)
        # Add two paths in the SAME introduction; original require_only_new fails.
        f.git("checkout", handoff_branch)
        f.put(path, {"outcome": "x"})
        f.put(prefix + "/1533420.json", {"outcome": "x"})
        extra = f.commit("Two-file typed introduction forbidden")
        f.git("update-ref", "refs/remotes/origin/" + handoff_branch, extra)
        f.git("checkout", stage.BRANCH)
        with patch.object(gh, "remote_tip", return_value=extra):
            with self.assertRaises(Exception):
                gh.semantic_submission(f.root, stage, p, "1517180", extra, extra)

    def test_11_publish_authority_forbidden_event_actor_branch_and_inputs(self):
        good = dict(event="workflow_dispatch", ref="refs/heads/main",
                    repository="kentrap2011-hub/steam-kz-deals-2",
                    actor="kentrap2011-hub", attempt="1",
                    operation="publish",
                    approval="DIRECTOR_AUTHORIZED_SHADOW_ASSEMBLY_TYPED_HANDOFF",
                    appid="1517180", commit="a" * 40)
        gh.require_publish_dispatch(**good)
        for k, invalid in (
            ("event", "pull_request"), ("ref", "refs/heads/other"),
            ("repository", "someone-else/steam-kz-deals-2"),
            ("actor", "attacker"), ("attempt", "2"),
            ("operation", "inspect"), ("approval", ""),
            ("appid", "1508750"), ("appid", "nope"),
            ("commit", "bad"), ("commit", "f" * 39),
        ):
            case = dict(good, **{k: invalid})
            with self.subTest(field=k, invalid=invalid):
                with self.assertRaises(ValueError):
                    gh.require_publish_dispatch(**case)

    def test_12_stage_B_only_frozen_authority_loader_contract(self):
        import inspect
        code = inspect.getsource(gh.load_original_stage)
        self.assertIn("FIXED_MARKER", code)
        self.assertIn("sys.path.insert(0, str(authority / \"scripts\"))", code)
        self.assertIn('Path(CONFIG).resolve()', code)


if __name__ == "__main__":
    unittest.main()
