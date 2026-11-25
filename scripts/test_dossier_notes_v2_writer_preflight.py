#!/usr/bin/env python3
"""Offline writer-command route regression. All owner REST responses are MOCKS.

Only disposable local Git repos are changed. No Actions dispatch, writer push,
real owner grant, external Research/Assembly or main data-plane write occurs.
"""
import copy
import json
import os
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import dossier_notes_v2_writer_preflight as preflight
import dossier_notes_v2_generic_replay as generic
import dossier_notes_v2_batch_preflight as legacy
import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_per_item_receipts as receipts
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import blob
from test_dossier_notes_v2_batch_route import add, git, source_copy
from test_dossier_notes_v2_generic_replay import SIX, issue_fixture
from taste_steam_review_dossier_test_fixture import web_dossier
from taste_steam_review_dossier_buffered import drain_buffered_groups

ROOT = Path(__file__).resolve().parents[1]


def env():
    return {
        "GITHUB_ACTIONS": "true",
        "GITHUB_EVENT_NAME": "workflow_dispatch",
        "GITHUB_REF": "refs/heads/main",
        "GITHUB_WORKFLOW_REF": batch.REPOSITORY + "/" + batch.WRITER_WORKFLOW + "@refs/heads/main",
        "GITHUB_REPOSITORY": batch.REPOSITORY,
        "GITHUB_REPOSITORY_OWNER_ID": batch.OWNER_ID,
        "GITHUB_ACTOR_ID": batch.OWNER_ID,
        "GITHUB_ACTOR": batch.OWNER_LOGIN,
        "GITHUB_TRIGGERING_ACTOR": batch.OWNER_LOGIN,
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_RUN_ID": "99887766",
        "GITHUB_TOKEN": "offline-fixture-NOT-real-owner",
    }


def mock_completed_owner_run(anchor, **changes):
    branch = anchor["request_ref"].removeprefix("refs/heads/")
    action = {
        "id": int(anchor["github_authorization_run_id"]),
        "event": "push", "status": "completed", "conclusion": "success",
        "run_attempt": 1, "head_branch": branch,
        "head_sha": anchor["request_commit"],
        "path": generic.WORKFLOW,
        "display_title": "Authorize Assembly replay " + branch + " at " + anchor["request_commit"],
        "actor": {"id": int(batch.OWNER_ID), "login": batch.OWNER_LOGIN},
        "triggering_actor": {"id": int(batch.OWNER_ID), "login": batch.OWNER_LOGIN},
    }
    return {**action, **changes}


class WriterRoutePreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp, self.repo = source_copy()
        self.addCleanup(self.tmp.cleanup)
        self.fixture = issue_fixture(self.repo, "ab" * 16, selected=SIX[:1], copies=True)
        self.trial = self.fixture["trial"]
        self.marker = self.fixture["marker"]
        self.appid, self.research, _ = self.fixture["issued"][0]
        assignment = v2.frozen_assignment(
            self.repo, marker_commit=self.marker, trial_id=self.trial,
            appid=self.appid)
        work = v2.assembly_work(
            self.repo, marker_commit=self.marker, trial_id=self.trial,
            appid=self.appid, research_commit=self.research)
        self.assertEqual(work["status"], "ready_for_autonomous_assembly")
        result = v2.candidate_assembly(
            work, outcome="assembled_candidate_ready",
            final_dossier=web_dossier(
                self.appid, datetime.now(timezone.utc), title=assignment["title"]))
        self.assembly = add(self.repo, work["output_path"], result,
                            "offline mock Assembly strict candidate")
        typed = receipts._assembly_receipt(
            self.repo, marker_commit=self.marker, trial_id=self.trial,
            appid=self.appid, authorization_commit=self.fixture["auth"],
            research_commit=self.research, assembly_commit=self.assembly,
            receipt_parent=git(self.repo, "rev-parse", "HEAD"))
        self.typed_path = typed["receipt_path"]
        add(self.repo, self.typed_path, typed["receipt_bytes"],
            "offline mock immutable typed Assembly receipt")
        git(self.repo, "branch", "-m", batch.paths(self.trial)["branch"])
        self.items = {self.appid: {"research_commit": self.research,
                                   "assembly_commit": self.assembly}}
        self.auth_mock = mock_completed_owner_run(self.fixture["anchor"])
        self.opts = dict(
            repo=self.repo, trial_id=self.trial, marker_commit=self.marker,
            item_commits=self.items, store_dir=self.repo / batch.paths(self.trial)["store"],
            accepted_dir=self.repo / batch.paths(self.trial)["accepted"],
            trial_sandbox=True, offline_fixture=False)

    def checked(self, *, environment=None, action=None, items=None, marker=None):
        with patch.object(receipts, "_github_get", return_value=action or self.auth_mock):
            return preflight.inspect(
                self.repo, trial_id=self.trial,
                marker_commit=self.marker if marker is None else marker,
                item_commits=self.items if items is None else items,
                env=environment or env())

    def assert_no_stage(self):
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")
        paths = batch.paths(self.trial)
        self.assertFalse((self.repo / paths["store"]).exists())
        self.assertFalse((self.repo / paths["accepted"] / self.trial).exists())

    def test_frozen_generic_owner_preflight_then_actual_existing_writer_path(self):
        # MOCKS ONLY: genuine preflight logic and real strict writer/persistence
        # code are executed on synthetic Git; not actual owner authentication.
        before = git(self.repo, "rev-parse", "HEAD")
        result = self.checked()
        self.assertEqual(result["status"], "authenticated_generic_owner_preflight_passed_read_only")
        self.assertEqual(result["source_kind"], "immutable_generic_owner_request")
        self.assertFalse(result["canonical_acceptance"])
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), before)
        self.assert_no_stage()
        with patch.dict(os.environ, env()), patch.object(
                receipts, "_github_get", return_value=self.auth_mock):
            written = drain_buffered_groups(notes_v2=self.opts)
        self.assertEqual(written["items"][0]["status"], "persisted_pending_github_commit")
        self.assertFalse(written["canonical_acceptance"])
        self.assertTrue((self.repo / batch.paths(self.trial)["store"] /
                         ("App_" + self.appid + ".json")).exists())
        # Local pending files are NOT Git committed, pushed or accepted.
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), before)

    def test_real_writer_does_not_stage_missing_or_tampered_typed_receipt(self):
        self.checked()
        # Immutable receipt history is invalidated by a second Git commit.
        item = json.loads((self.repo / self.typed_path).read_text())
        item["disposition"] = "forged"
        add(self.repo, self.typed_path, item, "offline forbidden receipt rewrite")
        with patch.dict(os.environ, env()), patch.object(
                receipts, "_github_get", return_value=self.auth_mock):
            result = drain_buffered_groups(notes_v2=self.opts)
        self.assertNotEqual(result["items"][0]["status"], "persisted_pending_github_commit")
        self.assertFalse((self.repo / batch.paths(self.trial)["store"]).exists())

    def test_wrong_owner_attempt_ref_token_or_github_run_is_blocked_before_writer(self):
        for key, wrong in (
            ("GITHUB_ACTOR_ID", "0"), ("GITHUB_REPOSITORY", "other/repo"),
            ("GITHUB_REF", "refs/heads/other"), ("GITHUB_RUN_ATTEMPT", "2"),
            ("GITHUB_EVENT_NAME", "push"), ("GITHUB_WORKFLOW_REF", "wrong"),
            ("GITHUB_TOKEN", "")):
            with self.subTest(key=key):
                e = {**env(), key: wrong}
                with self.assertRaises(ValueError):
                    self.checked(environment=e)
                self.assert_no_stage()
        for key, wrong in (
            ("run_attempt", 2), ("head_sha", "0" * 40),
            ("actor", {"id": 0, "login": "forged"}),
            ("triggering_actor", {"id": 0, "login": "forged"}),
            ("conclusion", "failure")):
            with self.subTest(owner_run=key):
                with self.assertRaises(ValueError):
                    self.checked(action=mock_completed_owner_run(self.fixture["anchor"], **{key: wrong}))
                self.assert_no_stage()

    def test_missing_mutated_request_grant_manifest_and_wrong_marker_fail_closed(self):
        for trial_id in (
            self.trial + "X",
            generic.PREFIX + "ab" * 15,
            "dossier-notes-v2-unknown-20261125",
            "../../outside",
        ):
            with self.subTest(trial_id=trial_id), self.assertRaises(ValueError):
                preflight.inspect(
                    self.repo, trial_id=trial_id, marker_commit=self.marker,
                    item_commits=self.items, env=env())
        with self.assertRaises(ValueError):
            self.checked(marker="0" * 40)
        with self.assertRaises(ValueError):
            self.checked(items={"999999999": self.items[self.appid]})
        self.assert_no_stage()
        paths = batch.paths(self.trial)
        grant = json.loads((self.repo / paths["grant"]).read_text())
        grant["request_commit"] = "0" * 40
        add(self.repo, paths["grant"], grant, "offline mutated owner request grant")
        with self.assertRaises((ValueError, v2.NotesV2Error)):
            self.checked()
        self.assertFalse((self.repo / paths["store"]).exists())

    def test_strict_old_cohort_still_uses_unchanged_batch_preflight(self):
        from test_dossier_notes_v2_batch_route import synthetic_issuer
        # A separate fresh disposable legacy checkout; generic route rejects it.
        temp, repo = source_copy()
        try:
            old = "dossier-notes-v2-fresh6-20261111-first"
            synthetic_issuer(repo, old)
            c, status = legacy.inspect(repo, old)
            self.assertEqual(c["trial_id"], old)
            self.assertEqual(status["status"], "batch_source_verified_not_authorized")
            with self.assertRaises(ValueError):
                preflight.inspect(repo, trial_id=old, marker_commit=self.marker,
                                  item_commits=self.items, env=env())
            with self.assertRaises((ValueError, OSError)):
                legacy.inspect(repo, "dossier-notes-v2-malformed-20261125")
        finally:
            temp.cleanup()

    def test_actual_actions_shell_dispatch_routes_are_retained(self):
        workflow = (ROOT / batch.WRITER_WORKFLOW).read_text(encoding="utf-8")
        self.assertIn("startsWith(inputs.notes_v2_trial_id, 'dossier-notes-v2-assembly-replay-')", workflow)
        self.assertIn('if [[ "${NOTES_V2_TRIAL_ID}" == dossier-notes-v2-assembly-replay-* ]]', workflow)
        self.assertIn("scripts/dossier_notes_v2_writer_preflight.py", workflow)
        self.assertIn("python scripts/dossier_notes_v2_batch_preflight.py --trial-id", workflow)
        self.assertIn("--item-commits-json", workflow)
        self.assertIn('test "${GITHUB_RUN_ATTEMPT}" = "1"', workflow)
        self.assertIn("git ls-remote origin refs/heads/sandbox/${NOTES_V2_TRIAL_ID}", workflow)
        self.assertIn("dossier_notes_v2_isolated_lean_readback.py", workflow)
        self.assertIn("git push origin HEAD:refs/heads/sandbox/${NOTES_V2_TRIAL_ID}", workflow)


if __name__ == "__main__":
    unittest.main()
