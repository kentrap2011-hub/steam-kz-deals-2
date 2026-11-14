#!/usr/bin/env python3
"""Disposable Git tests for plain V2 Research intake; no live GitHub writes."""
import unittest
from pathlib import Path
from unittest.mock import patch

import dossier_notes_v2_research_intake as intake
import dossier_notes_v2_per_item_receipts as receipts
import dossier_research_notes_v2 as v2
from test_dossier_notes_v2_batch_route import add, git, source_copy, synthetic_issuer


class ResearchIntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp, self.repo = source_copy()
        self.trial = "dossier-notes-v2-fresh6-20261111-first"
        self.branch = "sandbox/" + self.trial
        git(self.repo, "checkout", "-b", self.branch)
        self.issuer = synthetic_issuer(self.repo, self.trial)
        self.appid = self.issuer["rows"][0]["appid"]
        self.path = intake.input_path(self.trial, self.appid)

    def tearDown(self):
        self.tmp.cleanup()

    @staticmethod
    def _owner_mock():
        return patch.object(
            receipts, "verify_scoped_semantic_run",
            return_value={"github_run_authenticated": True})

    def test_minimal_submission_creates_exact_legacy_candidate_and_receipt(self):
        raw = {"appid": self.appid,
               "notes": "Players describe tactical combat with thoughtful movement.",
               "source_urls": ["https://store.steampowered.com/app/1000010/"]}
        submission = add(self.repo, self.path, raw, "fixture: one plain submission")
        with self._owner_mock():
            work = intake.plan(self.repo, self.branch, submission, "offline-owner")
        self.assertEqual(work["appid"], self.appid)
        self.assertEqual(work["candidate"]["output_path"],
                         "data/ai_inbox/dossier_notes_v2/" + self.trial
                         + "/g000001/1000010--"
                         + self.issuer["rows"][0]["assignment_id"] + ".json")
        result = intake.materialize(self.repo, work)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"),
                         result["receipt_commit"])
        self.assertEqual(git(self.repo, "rev-parse",
                             result["receipt_commit"] + "^"),
                         result["candidate_commit"])
        self.assertFalse(result["canonical_acceptance"])
        self.assertEqual(
            receipts.require_batch_research_receipt(
                self.repo, marker_commit=self.issuer["marker"],
                trial_id=self.trial, appid=self.appid,
                authorization_commit=self.issuer["auth"],
                research_commit=result["candidate_commit"]),
            result["receipt_commit"])
        content = (Path(self.repo) / work["candidate"]["output_path"]).read_text()
        self.assertIn('"access":"unknown"', content)
        self.assertIn('"research_status":"notes_recorded"', content)
        with self._owner_mock(), self.assertRaisesRegex(v2.NotesV2Error, "create-only"):
            intake.plan(self.repo, self.branch, submission, "offline-owner")

    def test_empty_notes_are_valid_sparse_research(self):
        assignment = v2.frozen_assignment(
            self.repo, marker_commit=self.issuer["marker"],
            trial_id=self.trial, appid=self.appid)
        doc = intake.normalized_document(
            {"appid": self.appid, "notes": ""}, assignment)
        self.assertEqual(doc["research_status"], "no_verifiable_findings")
        self.assertEqual(doc["source_log"], [])
        self.assertIsNone(doc["unknowns_text"])
        self.assertEqual(v2.validate_notes(doc, assignment)[0:1], b"{")

    def test_invalid_ids_links_extra_fields_and_lengths_fail_before_write(self):
        a = v2.frozen_assignment(
            self.repo, marker_commit=self.issuer["marker"],
            trial_id=self.trial, appid=self.appid)
        for raw in (
            {"appid": "49520", "notes": "Wrong game"},
            {"appid": self.appid, "notes": "x", "author_identity": "private"},
            {"appid": self.appid, "notes": "x"*1201},
            {"appid": self.appid, "notes": "x",
             "source_urls": ["http://private.example.test"]},
            {"appid": self.appid, "notes": "x",
             "source_urls": ["https://store.steampowered.com/app/1000010/?token=secret"]},
            {"appid": self.appid, "notes": "",
             "source_urls": ["https://store.steampowered.com/app/1000010/"]},
            {"appid": self.appid, "notes": "x", "source_urls": [12]},
        ):
            with self.subTest(raw=raw), self.assertRaises((ValueError, v2.NotesV2Error)):
                intake.normalized_document(raw, a)

    def test_missing_owner_authentication_and_wrong_path_are_rejected(self):
        raw = {"appid": self.appid, "notes": "Minimal result"}
        event = add(self.repo, self.path, raw, "fixture: authorized path")
        with self.assertRaisesRegex(ValueError, "owner token"):
            intake.plan(self.repo, self.branch, event, "")
        with patch.object(receipts, "verify_scoped_semantic_run",
                          return_value={"github_run_authenticated": False}):
            with self.assertRaisesRegex(ValueError, "not verified"):
                intake.plan(self.repo, self.branch, event, "mock-owner")
        with self._owner_mock():
            with self.assertRaisesRegex(ValueError, "missing frozen trial"):
                intake.plan(self.repo, "sandbox/other-trial", event, "mock-owner")

    def test_second_plain_submission_different_game_is_independent(self):
        first = self.issuer["rows"][0]
        second = self.issuer["rows"][1]
        src1 = add(self.repo, intake.input_path(self.trial, first["appid"]),
                   {"appid": first["appid"], "notes": "One"},
                   "fixture: first input")
        with self._owner_mock():
            work1 = intake.plan(self.repo, self.branch, src1, "offline-owner")
        result1 = intake.materialize(self.repo, work1)
        src2 = add(self.repo, intake.input_path(self.trial, second["appid"]),
                   {"appid": second["appid"], "notes": "Two"},
                   "fixture: second input")
        with self._owner_mock():
            work2 = intake.plan(self.repo, self.branch, src2, "offline-owner")
        result2 = intake.materialize(self.repo, work2)
        self.assertNotEqual(result1["candidate_commit"], result2["candidate_commit"])
        self.assertNotEqual(work1["receipt_path"], work2["receipt_path"])
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")


    def test_coalesced_github_push_handles_all_pending_inputs_once(self):
        first, second = self.issuer["rows"][:2]
        add(self.repo, intake.input_path(self.trial, first["appid"]),
            {"appid": first["appid"], "notes": "First review synthesis"},
            "fixture: first incoming semantic note")
        last = add(self.repo, intake.input_path(self.trial, second["appid"]),
                   {"appid": second["appid"], "notes": "Second review synthesis"},
                   "fixture: second incoming semantic note")
        with self._owner_mock(), patch.object(
                intake, "publish",
                side_effect=lambda _repo, _branch, result: {
                    **result, "github_receipt_confirmed": True}):
            outcome = intake.reconcile(self.repo, self.branch, last, "mock-owner")
        self.assertEqual(outcome["plain_inputs_processed"], 2)
        self.assertEqual(len(outcome["submitted_candidates"]), 2)
        self.assertEqual(len(outcome["typed_receipts"]), 2)
        self.assertTrue(outcome["github_receipt_confirmed"])
        self.assertEqual(outcome["unresolved"], [])
        self.assertFalse(outcome["canonical_acceptance"])
        self.assertEqual(
            git(self.repo, "rev-parse", "HEAD"),
            outcome["typed_receipts"][-1])
        for item, intro, receipt in zip((first, second),
                                        outcome["submitted_candidates"],
                                        outcome["typed_receipts"]):
            self.assertEqual(
                receipts.require_batch_research_receipt(
                    self.repo, marker_commit=self.issuer["marker"],
                    trial_id=self.trial, appid=item["appid"],
                    authorization_commit=self.issuer["auth"],
                    research_commit=intro),
                receipt)
        with self._owner_mock(), patch.object(intake, "publish") as send:
            repeated = intake.reconcile(self.repo, self.branch, last, "mock-owner")
        self.assertEqual(repeated["plain_inputs_processed"], 0)
        send.assert_not_called()

    def test_bad_input_does_not_block_independent_sibling(self):
        first, second = self.issuer["rows"][:2]
        add(self.repo, intake.input_path(self.trial, first["appid"]),
            {"appid": second["appid"], "notes": "Wrong AppID"},
            "fixture: invalid input")
        last = add(self.repo, intake.input_path(self.trial, second["appid"]),
                   {"appid": second["appid"], "notes": "Valid independent note"},
                   "fixture: valid sibling")
        with self._owner_mock(), patch.object(
                intake, "publish", return_value={"github_receipt_confirmed": True}):
            outcome = intake.reconcile(self.repo, self.branch, last, "mock-owner")
        self.assertEqual(outcome["plain_inputs_processed"], 1)
        self.assertEqual(outcome["unresolved"],
                         [{"appid": first["appid"], "problem": "ValueError"}])
        self.assertEqual(len(outcome["typed_receipts"]), 1)
        self.assertFalse(outcome["canonical_acceptance"])

    def test_unrelated_push_event_cannot_be_used_as_intake_trigger(self):
        with self.assertRaisesRegex(ValueError, "trigger"):
            intake.reconcile(self.repo, self.branch, self.issuer["auth"],
                             "offline-owner")


if __name__ == "__main__":
    unittest.main()
