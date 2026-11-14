#!/usr/bin/env python3
"""Offline regression for one-write Research -> GitHub-owned typed receipts.

Uses the same immutable issuer and receipt validator as live V2. Synthetic
disposable Git only; no owner Actions dispatch, no live Research, no network.
"""
import copy
import unittest
from pathlib import Path

from test_dossier_notes_v2_batch_route import source_copy, synthetic_issuer, git, add
import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_per_item_receipts as receipts
import dossier_notes_v2_research_receipt_ingest as ingest
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import require_only_new


class SimpleResearchIngestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp, cls.repo = source_copy()
        cls.trial = "dossier-notes-v2-fresh6-20261111-first"
        cls.fixture = synthetic_issuer(cls.repo, cls.trial)
        cls.anchor = ingest.issuer_from_sandbox(cls.repo, cls.trial)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        git(self.repo, "reset", "--hard", self.fixture["auth"])
        git(self.repo, "clean", "-fd")
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def assignment(self, appid):
        return v2.frozen_assignment(
            self.repo, marker_commit=self.fixture["marker"],
            trial_id=self.trial, appid=appid,
        )

    def note(self, appid, **changes):
        result = {
            "schema": "DOSSIER-RESEARCH-NOTES-V2",
            "schema_version": 2,
            "assignment": self.assignment(appid),
            "notes_text": "Public player opinions: controls and pacing are mixed.",
            "research_status": "limited_evidence",
        }
        result.update(changes)
        return result

    def submit(self, appid, document=None):
        return add(self.repo, v2._path("research", self.assignment(appid)),
                   self.note(appid) if document is None else document,
                   "fixture: one Research create_file " + appid)

    def ingest(self):
        return ingest.ingest_local(
            self.repo, trial_id=self.trial, anchor=self.anchor,
        )

    def test_all_six_one_candidate_each_no_source_audit_and_no_replay(self):
        submitted = {}
        for row in self.fixture["rows"]:
            appid = row["appid"]
            submitted[appid] = self.submit(appid)
            self.assertEqual(
                require_only_new(self.repo, submitted[appid],
                                 [v2._path("research", self.assignment(appid))]),
                git(self.repo, "rev-parse", submitted[appid] + "^"),
            )
        result = self.ingest()
        self.assertEqual(result["receipts_created"], 6, result)
        self.assertEqual([item["appid"] for item in result["items"]],
                         [r["appid"] for r in self.fixture["rows"]])
        self.assertTrue(all(i["status"] == "safe_incomplete_research"
                            for i in result["items"]), result)
        for row in self.fixture["rows"]:
            appid = row["appid"]
            proven = receipts.require_batch_research_receipt(
                self.repo, marker_commit=self.fixture["marker"],
                trial_id=self.trial, appid=appid,
                authorization_commit=self.fixture["auth"],
                research_commit=submitted[appid],
            )
            self.assertEqual(len(proven), 40)
            work = v2.assembly_work(
                self.repo, marker_commit=self.fixture["marker"],
                trial_id=self.trial, appid=appid,
                research_commit=submitted[appid],
            )
            self.assertEqual(work["status"], "ready_for_autonomous_assembly")
        self.assertEqual(self.ingest()["receipts_created"], 0)
        self.assertFalse((self.repo / "data/control/dossier_notes_v2/batch_pilot_store").exists())
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def test_partial_batch_not_submitted_is_not_rejected_or_consumed(self):
        first = self.fixture["rows"][0]["appid"]
        self.submit(first)
        result = self.ingest()
        self.assertEqual(result["receipts_created"], 1)
        self.assertEqual(sum(i["status"] == "not_submitted" for i in result["items"]), 5)
        second = self.fixture["rows"][1]["appid"]
        self.submit(second)
        later = self.ingest()
        self.assertEqual(later["receipts_created"], 1)
        self.assertEqual(later["items"][0]["status"], "existing_receipt_not_replayed")
        self.assertEqual(later["items"][1]["status"], "safe_incomplete_research")

    def test_forged_assignment_broken_json_and_healthy_sibling(self):
        first, second, third = [i["appid"] for i in self.fixture["rows"][:3]]
        wrong = self.note(first)
        wrong["assignment"] = copy.deepcopy(self.assignment(second))
        self.submit(first, wrong)
        self.submit(second, b"{ malformed json")
        self.submit(third)
        result = self.ingest()
        self.assertEqual(result["receipts_created"], 3, result)
        self.assertEqual([i["status"] for i in result["items"][:3]],
                         ["wrong_binding", "unparseable", "safe_incomplete_research"])
        self.assertRaises(v2.NotesV2Error, receipts.require_batch_research_receipt,
                          self.repo, marker_commit=self.fixture["marker"],
                          trial_id=self.trial, appid=first,
                          authorization_commit=self.fixture["auth"],
                          research_commit=result["items"][0]["candidate_commit"])
        self.assertEqual(
            v2.assembly_work(self.repo, marker_commit=self.fixture["marker"],
                             trial_id=self.trial, appid=third,
                             research_commit=result["items"][2]["candidate_commit"])["status"],
            "ready_for_autonomous_assembly",
        )

    def test_overwritten_candidate_does_not_stop_other_games(self):
        first, second = [i["appid"] for i in self.fixture["rows"][:2]]
        self.submit(first)
        add(self.repo, v2._path("research", self.assignment(first)),
            self.note(first, notes_text="Overwritten unauthorized revision"),
            "fixture: rewrite forbidden")
        self.submit(second)
        result = self.ingest()
        self.assertEqual(result["receipts_created"], 1, result)
        self.assertEqual(result["items"][0]["status"], "item_blocked")
        self.assertEqual(result["items"][1]["status"], "safe_incomplete_research")

    def test_unexpected_extra_file_and_private_source_are_quarantined(self):
        first, second = [i["appid"] for i in self.fixture["rows"][:2]]
        path = v2._path("research", self.assignment(first))
        file = self.repo / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(batch.canonical(self.note(first)))
        extra = self.repo / "data/ai_inbox/dossier_notes_v2/unrelated-extra.json"
        extra.write_text("{}", encoding="utf-8")
        git(self.repo, "add", "--", path, "data/ai_inbox/dossier_notes_v2/unrelated-extra.json")
        git(self.repo, "commit", "-m", "fixture: two files, not an original one-add")
        self.submit(second, self.note(second, source_log=[{
            "locator": {"url": "http://localhost/private"},
            "access": "opened", "observation": "untrusted",
        }]))
        result = self.ingest()
        self.assertEqual(result["receipts_created"], 2, result)
        self.assertEqual(result["items"][0]["status"], "broken_git_provenance")
        self.assertEqual(result["items"][1]["status"], "unsafe_material")

    def test_legacy_source_log_still_accepted(self):
        first = self.fixture["rows"][0]["appid"]
        self.submit(first, self.note(first, source_log=[{
            "locator": {"url": "https://store.steampowered.com/app/1000010/"},
            "access": "search_result_only",
            "observation": "Public review themes",
        }]))
        result = self.ingest()
        self.assertEqual(result["items"][0]["status"], "safe_incomplete_research")
        self.assertEqual(result["receipts_created"], 1)

    def test_owner_gate_rejects_any_interactive_or_wrong_owner(self):
        real = {
            "GITHUB_ACTIONS": "true",
            "GITHUB_EVENT_NAME": "workflow_dispatch",
            "GITHUB_REPOSITORY": batch.REPOSITORY,
            "GITHUB_REPOSITORY_OWNER_ID": batch.OWNER_ID,
            "GITHUB_ACTOR_ID": batch.OWNER_ID,
            "GITHUB_ACTOR": batch.OWNER_LOGIN,
            "GITHUB_TRIGGERING_ACTOR": batch.OWNER_LOGIN,
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_WORKFLOW_REF": batch.REPOSITORY + "/" + ingest.WORKFLOW
                                   + "@refs/heads/main",
            "GITHUB_RUN_ATTEMPT": "1",
            "GITHUB_RUN_ID": "1234",
        }
        ingest._owner_action_gate(self.trial, real)
        for override in (
            {"GITHUB_EVENT_NAME": "push"},
            {"GITHUB_ACTOR_ID": "0"},
            {"GITHUB_WORKFLOW_REF": "other"},
            {"GITHUB_RUN_ATTEMPT": "2"},
            {"GITHUB_REF": "refs/heads/sandbox/forged"},
        ):
            with self.subTest(override=override), self.assertRaises(ValueError):
                ingest._owner_action_gate(self.trial, {**real, **override})
        with self.assertRaises(ValueError):
            ingest.issuer_from_sandbox(self.repo, "dossier-notes-v2-original18-first")


if __name__ == "__main__":
    unittest.main()
