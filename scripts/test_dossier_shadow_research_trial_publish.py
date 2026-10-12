#!/usr/bin/env python3
"""PR-only synthetic Git tests for the single-use GH-owned shadow publisher.

All remote tests use OS-temporary local bare Git repositories, never GitHub.
"""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dossier_shadow_research_trial import PREFIX, exact_marker, frozen_trial
from dossier_shadow_research_trial_publish import (
    APPROVAL, BRANCH, BUFFER, EXPECTED_APPIDS, ORDER, REPOSITORY, WORKFLOW,
    assert_github_dispatch, assert_one_new_path, commit_new, local_two_commit_freeze,
    remote_sha, run,
)


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if r.returncode:
        raise AssertionError("disposable Git fixture failed: " + str(args))
    return r.stdout.decode().strip()


class PublisherDisposableTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="shadow-publisher-test-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.gitdir = self.root / "sandbox"
        self.gitdir.mkdir()
        git(self.gitdir, "init", "-q")
        git(self.gitdir, "config", "user.name", "Isolated test fixture")
        git(self.gitdir, "config", "user.email", "test@example.invalid")
        (self.gitdir / "README.txt").write_text("OS temporary fake commit\n")
        git(self.gitdir, "add", "README.txt")
        git(self.gitdir, "commit", "-qm", "Disposable original")
        self.source = git(self.gitdir, "rev-parse", "HEAD")

    def test_01_only_explicit_actual_github_dispatch_can_start(self):
        env = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_EVENT_NAME": "workflow_dispatch",
            "GITHUB_REPOSITORY": REPOSITORY,
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_WORKFLOW_REF": REPOSITORY + "/" + WORKFLOW + "@refs/heads/main",
            "GITHUB_SHA": self.source,
            "GITHUB_RUN_ATTEMPT": "1",
        }
        assert_github_dispatch(self.source, APPROVAL, env)
        for field, wrong in [
            ("GITHUB_EVENT_NAME", "schedule"),
            ("GITHUB_EVENT_NAME", "push"),
            ("GITHUB_EVENT_NAME", "pull_request"),
            ("GITHUB_REPOSITORY", "other/project"),
            ("GITHUB_REF", "refs/heads/feature"),
            ("GITHUB_WORKFLOW_REF", REPOSITORY + "/" + WORKFLOW + "@refs/heads/feature"),
            ("GITHUB_SHA", "a" * 40),
            ("GITHUB_RUN_ATTEMPT", "2"),
        ]:
            with self.subTest(field=field, wrong=wrong), self.assertRaises(RuntimeError):
                assert_github_dispatch(self.source, APPROVAL, {**env, field: wrong})
        with self.assertRaises(RuntimeError):
            assert_github_dispatch(self.source, "NOT_AUTHORIZED", env)
        with self.assertRaises(RuntimeError):
            assert_github_dispatch("main", APPROVAL, env)
        with self.assertRaises(RuntimeError):
            assert_github_dispatch(self.source, APPROVAL, {})

    def test_02_two_real_single_parent_git_commits_and_no_other_paths(self):
        proof = local_two_commit_freeze(self.gitdir, b'{"fixture_only":true}\n', "f" * 32)
        self.assertEqual(proof["source_commit"], self.source)
        self.assertEqual(proof["marker_parent"], proof["buffer_commit"])
        self.assertNotEqual(proof["buffer_commit"], proof["marker_commit"])
        assert_one_new_path(self.gitdir, self.source, proof["buffer_commit"], BUFFER)
        assert_one_new_path(self.gitdir, proof["buffer_commit"], proof["marker_commit"],
                            proof["marker_path"])
        self.assertEqual(exact_marker(self.gitdir, proof["marker_commit"]),
                         (proof["buffer_commit"], "f" * 32))
        self.assertEqual(git(self.gitdir, "diff", "--name-only", self.source,
                             proof["marker_commit"]).splitlines(),
                         [BUFFER, proof["marker_path"]])
        # A fake marker structure cannot confer the old strict frozen trial authority.
        with self.assertRaises(Exception):
            frozen_trial(self.gitdir, marker_commit=proof["marker_commit"],
                         buffer_path=BUFFER)

    def test_03_replay_nonce_or_buffer_path_collision_fails_closed(self):
        local_two_commit_freeze(self.gitdir, b'{"fixture_only":true}\n', "f" * 32)
        with self.assertRaisesRegex(RuntimeError, "already exists"):
            commit_new(self.gitdir, BUFFER, b"overwrite", "forbidden")
        with self.assertRaisesRegex(RuntimeError, "already exists"):
            local_two_commit_freeze(self.gitdir, b'{"fixture_only":true}\n', "f" * 32)
        with self.assertRaisesRegex(RuntimeError, "nonce invalid"):
            local_two_commit_freeze(self.gitdir, b"x", "fake")

    def test_04_unapproved_extra_staged_path_rejected(self):
        (self.gitdir / "data" / "production").mkdir(parents=True)
        (self.gitdir / "data" / "production" / "bad.json").write_text("{}")
        git(self.gitdir, "add", "data/production/bad.json")
        with self.assertRaisesRegex(RuntimeError, "only allowlisted"):
            commit_new(self.gitdir, BUFFER, b"{}", "forbidden extra")
        self.assertEqual(git(self.gitdir, "rev-parse", "HEAD"), self.source)

    def test_05_remote_create_only_single_use_ref_or_replay(self):
        bare = self.root / "remote.git"
        git(self.root, "init", "--bare", str(bare))
        git(self.gitdir, "remote", "add", "origin", str(bare))
        git(self.gitdir, "branch", "-M", "main")
        git(self.gitdir, "push", "-q", "origin", "main")
        self.assertEqual(remote_sha(self.gitdir, "refs/heads/main"), self.source)
        ref = "refs/heads/" + BRANCH
        self.assertIsNone(remote_sha(self.gitdir, ref))
        proof = local_two_commit_freeze(self.gitdir, b'{"fixture_only":true}\n', "e" * 32)
        # Push is only in the local OS-temporary bare Git fixture, never GitHub.
        git(self.gitdir, "push", "--force-with-lease=" + ref + ":",
            "origin", "HEAD:" + ref)
        self.assertEqual(remote_sha(self.gitdir, ref), proof["marker_commit"])
        second = subprocess.run(
            ["git", "-C", str(self.gitdir), "push",
             "--force-with-lease=" + ref + ":", "origin", "HEAD:" + ref],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertNotEqual(second.returncode, 0)
        # Source branch drift must not be silently accepted.
        git(self.gitdir, "checkout", "-q", "main")
        (self.gitdir / "README.txt").write_text("drifted local main\n")
        git(self.gitdir, "commit", "-qam", "Changed source")
        git(self.gitdir, "push", "-q", "origin", "main")
        self.assertNotEqual(remote_sha(self.gitdir, "refs/heads/main"), self.source)

    def test_06_canonical_fixed_six_by_three_including_known_old_year_disputes(self):
        decision = json.loads((Path(__file__).resolve().parents[1] /
            "reviews/dossier_shadow_offline/dossier_shadow_calibration_20261011_6x3_director_decision_v1.json").read_text("utf-8"))
        self.assertEqual(decision["scope"]["group_order"], ORDER)
        self.assertEqual([a for g in decision["scope"]["groups"] for a in g["appids"]],
                         EXPECTED_APPIDS)
        self.assertEqual(len(EXPECTED_APPIDS), 18)
        self.assertEqual([len(g["appids"]) for g in decision["scope"]["groups"]], [3]*6)
        self.assertTrue({"213610", "2138710"}.issubset(EXPECTED_APPIDS))
        self.assertEqual(decision["scope"]["total_games"], 18)

    def test_07_only_manual_dispatch_workflow_and_no_production_gate_flip(self):
        repo = Path(__file__).resolve().parents[1]
        yaml = (repo / WORKFLOW).read_text("utf-8")
        self.assertIn("workflow_dispatch:", yaml)
        self.assertNotIn("  push:", yaml)
        self.assertNotIn("  schedule:", yaml)
        self.assertNotIn("  pull_request:", yaml)
        self.assertIn("contents: write", yaml)
        self.assertIn("cancel-in-progress: false", yaml)
        self.assertNotIn("manual-shell-write.yml", yaml)
        c = json.loads((repo / "config/dossier_shadow_research_trial_contract_v1.json").read_text())
        self.assertIs(c["standalone_sandbox_semantics_approved"], False)
        self.assertIs(c["reviewer_roles_finalized"], False)
        self.assertIs(c["production_execution"], False)
        for path in ("config/dossier_two_stage_interfaces_contract.json",
                     "config/dossier_two_stage_staging_contract.json",
                     "config/dossier_two_stage_async_buffer_contract.json"):
            inactive = json.loads((repo / path).read_text())
            self.assertIs(inactive["active"], False)
            self.assertIsNot(inactive.get("authorized_for_semantic_execution"), True)


if __name__ == "__main__":
    unittest.main()
