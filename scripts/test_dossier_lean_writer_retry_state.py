#!/usr/bin/env python3
"""Disposable real Git control-branch retry journal regressions (never live)."""
import datetime as dt
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import dossier_lean_writer_retry_state as state

TRIAL = "dossier-notes-v2-assembly-replay-" + "b" * 32
DIGEST = "e" * 64
HEAD = "f" * 40
MARKER = "a" * 40


def git(directory, *args):
    p = subprocess.run(["git", "-C", str(directory), *args],
                       capture_output=True, text=True)
    if p.returncode:
        raise AssertionError(f"git {args}: {p.stderr}")
    return p.stdout.strip()


class DisposableJournal(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="lean-retry-real-git-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.remote = root / "remote.git"
        self.repo = root / "source"
        subprocess.run(["git", "init", "--bare", str(self.remote)],
                       check=True, capture_output=True)
        subprocess.run(["git", "init", "-b", "main", str(self.repo)],
                       check=True, capture_output=True)
        git(self.repo, "config", "user.name", "test")
        git(self.repo, "config", "user.email", "test@example.invalid")
        git(self.repo, "remote", "add", "origin", str(self.remote))
        (self.repo / "README.md").write_text("source\n")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-m", "main source")
        self.main = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "push", "origin", "main")
        git(self.repo, "checkout", "-b", "control")
        f = self.repo / state.BASE / (TRIAL + ".json")
        f.parent.mkdir(parents=True)
        f.write_text(json.dumps({
            "schema": "DOSSIER-LEAN-AUTO-WRITER-ATTEMPT-V1",
            "trial_id": TRIAL,
            "automation_source_main_sha": self.main,
            "original_frozen_sandbox_head": HEAD,
            "marker_commit": MARKER,
            "item_commits_sha256": DIGEST, "no_retry": False,
            "canonical_acceptance": False, "production": False, "deep": False,
        }) + "\n")
        git(self.repo, "add", str(f.relative_to(self.repo)))
        git(self.repo, "commit", "-m", "claim one")
        self.anchor = git(self.repo, "rev-parse", "HEAD")
        git(self.repo, "push", "origin", "HEAD:" + state.ref_for(TRIAL))
        git(self.repo, "checkout", "main")
        self.env = {"GITHUB_RUN_ID": "9901", "GITHUB_SHA": self.main}
        self.ready = {
            "trial_id": TRIAL, "sandbox_head": HEAD,
            "marker_commit": MARKER,
            "issuer": {"github_authorization_run_id": "777"},
            "pairs_sha256": DIGEST,
        }

    def snapshot(self):
        return state.read(self.repo, TRIAL, DIGEST)

    def record(self, snapshot, kind, number, env=None):
        return state.make_event(snapshot, self.ready, env or self.env, kind, number,
                                sandbox_commit="8" * 40 if kind == "accepted" else None)

    def transition(self, kind, number, env=None):
        snapshot = self.snapshot()
        event = self.record(snapshot, kind, number, env)
        return state.append(self.repo, TRIAL, snapshot, event)

    def test_claim_append_only_start_failure_code_fix_retry_acceptance_noop(self):
        s = self.snapshot()
        self.assertEqual(s["anchor"], self.anchor)
        self.assertEqual(state.eligible(s, source_sha=self.main), (True, 1))
        first = self.transition("started", 1)
        self.assertTrue(state.active_for_writer(
            self.repo, self.ready, self.env, first))
        self.assertEqual(state.eligible(self.snapshot(), source_sha=self.main)[1],
                         "writer_lease_active")
        self.transition("retryable_failed", 1)
        self.assertEqual(state.eligible(
            self.snapshot(), source_sha=self.main)[1],
            "same_source_retry_disallowed")
        updated = {"GITHUB_RUN_ID": "9902", "GITHUB_SHA": "c" * 40}
        ok, attempt = state.eligible(
            self.snapshot(), source_sha=updated["GITHUB_SHA"],
            retry_delay_minutes=0)
        self.assertTrue(ok)
        self.assertEqual(attempt, 2)
        second = self.transition("started", 2, updated)
        self.assertTrue(state.active_for_writer(
            self.repo, self.ready, updated, second))
        self.transition("accepted", 2, updated)
        self.assertEqual(state.eligible(
            self.snapshot(), source_sha="d" * 40)[1], "already_accepted")
        self.assertEqual(self.snapshot()["anchor"], self.anchor)
        self.assertEqual(len(self.snapshot()["events"]), 4)

    def test_stale_snapshot_cannot_publish_second_concurrent_start(self):
        old = self.snapshot()
        event = self.record(old, "started", 1)
        state.append(self.repo, TRIAL, old, event)
        with self.assertRaisesRegex(ValueError, "CAS lease lost"):
            state.append(self.repo, TRIAL, old, event)
        self.assertEqual(len(self.snapshot()["events"]), 1)

    def test_changed_grant_sha_and_spoofed_identity_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "claim/grant mismatch"):
            state.read(self.repo, TRIAL, "0" * 64)
        with self.assertRaisesRegex(ValueError, "invalid trial"):
            state.ref_for("../arbitrary")
        with self.assertRaisesRegex(ValueError, "historic consumed claim"):
            state.read(self.repo, TRIAL, DIGEST,
                       historical_anchor="0" * 40)
        self.transition("started", 1)
        with self.assertRaisesRegex(ValueError, "active execution lease"):
            state.active_for_writer(
                self.repo, self.ready, self.env, "a" * 40)
        other = dict(self.env, GITHUB_RUN_ID="9999")
        with self.assertRaisesRegex(ValueError, "no verified active lease"):
            state.active_for_writer(
                self.repo, self.ready, other, self.snapshot()["head"])

    def test_invalid_transition_and_claim_reuse_cannot_be_hidden(self):
        self.transition("started", 1)
        last = self.snapshot()
        # An append-only, but impossible second 'started' must fail readback.
        bad = self.record(last, "started", 2,
                          dict(self.env, GITHUB_RUN_ID="9902",
                               GITHUB_SHA="0" * 40))
        state.append(self.repo, TRIAL, last, bad)
        with self.assertRaisesRegex(ValueError, "invalid retry transition"):
            self.snapshot()

    def test_attempt_budget_and_no_repeat_for_same_main(self):
        self.transition("started", 1)
        self.transition("retryable_failed", 1)
        second = dict(self.env, GITHUB_RUN_ID="9902", GITHUB_SHA="2" * 40)
        self.transition("started", 2, second)
        self.transition("retryable_failed", 2, second)
        third = dict(self.env, GITHUB_RUN_ID="9903", GITHUB_SHA="3" * 40)
        self.transition("started", 3, third)
        self.transition("retryable_failed", 3, third)
        self.assertEqual(state.eligible(
            self.snapshot(), source_sha="4" * 40,
            retry_delay_minutes=0)[1], "attempt_budget_exhausted")

    def test_reviewed_source_fix_discovers_unique_failed_exact_owner_grant(self):
        import dossier_lean_writer_auto_ready as ready
        config = {
            "recovery": {"trial_id": "dossier-notes-v2-assembly-replay-" + "c" * 32},
            "retry_lifecycle": {"historical_live_retry_authorized": False,
                                "historical_spent_claim_sha": "0" * 40,
                                "max_total_attempts": 3},
        }
        self.assertIsNone(ready.unique_failed_source_retry(
            self.repo, {"GITHUB_SHA": "2" * 40}, config))
        self.transition("started", 1)
        self.transition("retryable_failed", 1)
        self.assertEqual(ready.unique_failed_source_retry(
            self.repo, {"GITHUB_SHA": "2" * 40}, config), (TRIAL, HEAD))
        self.assertIsNone(ready.unique_failed_source_retry(
            self.repo, {"GITHUB_SHA": self.main}, config))
        self.transition("started", 2,
                        {"GITHUB_RUN_ID": "9902", "GITHUB_SHA": "2" * 40})
        self.transition("accepted", 2,
                        {"GITHUB_RUN_ID": "9902", "GITHUB_SHA": "2" * 40})
        self.assertIsNone(ready.unique_failed_source_retry(
            self.repo, {"GITHUB_SHA": "3" * 40}, config))

    def test_historical_claim_requires_exact_spent_anchor(self):
        # Real historic data has a V1-only claim and no V2 event.
        # V2 must start as attempt 2 and must not rewrite the original ref.
        a = self.snapshot()
        self.assertEqual(a["anchor"], self.anchor)
        self.assertEqual(len(a["events"]), 0)
        a["claim"]["no_retry"] = True
        self.assertEqual(state.eligible(a, source_sha="c" * 40), (True, 2))

    def test_stale_lease_is_a_reconcile_gate_not_permission(self):
        self.transition("started", 1)
        snapshot = self.snapshot()
        self.assertEqual(state.eligible(
            snapshot, source_sha="2" * 40, stale_minutes=0)[1],
            "stale_lease_requires_reconcile")
        with patch.object(state, "minutes_since", return_value=31):
            self.assertEqual(state.eligible(
                snapshot, source_sha="2" * 40)[1],
                "stale_lease_requires_reconcile")


if __name__ == "__main__":
    unittest.main()
