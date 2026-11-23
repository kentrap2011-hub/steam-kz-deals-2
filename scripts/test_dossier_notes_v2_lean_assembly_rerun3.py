#!/usr/bin/env python3
"""Synthetic-only exact Lean Assembly rerun3 owner route regressions, no live writes."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_dossier_notes_v2_batch_route import add, git, source_copy
from test_dossier_notes_v2_owner_push import (
    common_env, event_document, synthetic_push_issuer,
)
from test_dossier_notes_v2_lean_final import NOW, make_lean_final
from dossier_notes_v2_lean_final import validate_lean_final
import dossier_notes_v2_assembly_replay_seed as replay
import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_batch_issuer as issuer
import dossier_notes_v2_per_item_receipts as receipts
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import parent, require_only_new

TRIAL = batch.OWNER_PUSH_REPLAY_TRIAL3
RERUN2 = batch.OWNER_PUSH_REPLAY_TRIAL
RESEARCH = "dossier-notes-v2-fresh6-20261114-rerun1"
SIX = ("1000010", "102600", "1029690", "49520", "499180", "501590")


class LeanAssemblyRerun3OwnerTests(unittest.TestCase):
    def test_exact_pinned_scope_and_all_production_switches_off(self):
        temp, repo = source_copy()
        try:
            fresh = batch.scope(repo, TRIAL)
            previous = batch.scope(repo, RERUN2)
            source = replay.validate_source_contract(repo, TRIAL)
            self.assertEqual(fresh["provenance"], previous["provenance"])
            self.assertEqual(fresh["candidates"], previous["candidates"])
            self.assertEqual(source, previous["replay_source"])
            self.assertEqual(list(source["candidate_commits"]), list(source["candidate_blobs"]))
            self.assertEqual(set(source["research_receipt_blobs"]), set(SIX))
            self.assertEqual([r["appid"] for r in batch.rows(repo, TRIAL)], list(SIX))
            for prior in (RESEARCH, RERUN2):
                self.assertTrue(
                    set(r["assignment_id"] for r in batch.rows(repo, TRIAL)).isdisjoint(
                        set(r["assignment_id"] for r in batch.rows(repo, prior))))
            self.assertEqual(batch.owner_push_workflow(TRIAL), batch.OWNER_PUSH_REPLAY_WORKFLOW3)
            with self.assertRaises(ValueError):
                batch.owner_push_workflow("dossier-notes-v2-fresh6-arbitrary-retry-1234")
            policy = json.loads((repo/"config/dossier_notes_v2_batch_policy.json").read_text())
            self.assertFalse(policy["active"])
            self.assertFalse(policy["production_enabled"])
            self.assertFalse(policy["automatic_retry"])
            self.assertEqual(policy["owner_push_no_ui_assembly_rerun3"]["trial_id"], TRIAL)
            self.assertFalse(fresh["production_enabled"])
            self.assertFalse(fresh["canonical_ingest_authorized"])
            self.assertFalse(fresh["automated_retry_enabled"])
            lean = json.loads((repo/"config/dossier_lean_canonical_dual_format_contract.json").read_text())
            for flag in ("lean_writer_enabled", "lean_reader_enabled", "lean_deep_enabled"):
                self.assertIs(lean[flag], False, flag)
        finally:
            temp.cleanup()

    def test_reject_forged_source_receipt_sha_title_edition_duplicate_and_missing(self):
        temp, repo = source_copy()
        try:
            path = repo/batch.paths(TRIAL)["contract"]
            original = path.read_bytes()
            for appid_field in ("candidate_commits", "candidate_blobs", "research_receipt_blobs"):
                doc = json.loads(original)
                doc["replay_source"][appid_field]["1000010"] = "f"*40
                path.write_text(json.dumps(doc))
                with self.subTest(field=appid_field), self.assertRaises(ValueError):
                    replay.validate_source_contract(repo, TRIAL)
            for change in ("wrong_edition", "duplicate", "missing", "wrong_appid"):
                doc = json.loads(original)
                if change == "wrong_edition":
                    doc["candidates"][4]["title"] = "Braid"
                elif change == "duplicate":
                    doc["candidates"][1]["appid"] = "1000010"
                elif change == "missing":
                    doc["candidates"].pop()
                else:
                    doc["candidates"][2]["appid"] = "999999"
                path.write_text(json.dumps(doc))
                with self.subTest(change=change), self.assertRaises(ValueError):
                    if change == "missing":
                        replay.validate_source_contract(repo, TRIAL)
                    else:
                        batch.scope(repo, TRIAL)
            path.write_bytes(original)
            self.assertEqual(replay.validate_source_contract(repo, TRIAL)["trial_id"], RESEARCH)
        finally:
            temp.cleanup()

    def test_exact_owner_push_first_attempt_branch_parent_and_manual_gate(self):
        temp, repo = source_copy()
        try:
            path = batch.paths(TRIAL)["contract"]
            raw = (repo/path).read_bytes()
            git(repo, "checkout", "-B", "main")
            git(repo, "rm", "--", path)
            git(repo, "commit", "-m", "fixture remove source before first owner merge")
            add(repo, path, raw, "fixture first owner source introduction")
            sha = git(repo, "rev-parse", "HEAD")
            before = parent(repo, sha)
            git(repo, "remote", "set-url", "origin",
                "https://github.com/"+batch.REPOSITORY+".git")
            with tempfile.TemporaryDirectory() as folder:
                event = Path(folder)/"event.json"
                doc = event_document("refs/heads/main", before, sha)
                event.write_text(json.dumps(doc))
                env = common_env(batch.OWNER_PUSH_REPLAY_WORKFLOW3,
                                 "refs/heads/main", sha, event)
                def remote(_, ref):
                    return sha if ref == "refs/heads/main" else None
                with patch.object(issuer, "remote", side_effect=remote):
                    issuer.guard_owner_push(repo, TRIAL, sha, env)
                    for change in ({"GITHUB_RUN_ATTEMPT": "2"},
                                   {"GITHUB_ACTOR_ID": "0"},
                                   {"GITHUB_WORKFLOW_REF": "forged"},
                                   {"GITHUB_REF": "refs/heads/main2"},
                                   {"GITHUB_SHA": "f"*40},
                                   {"GITHUB_EVENT_NAME": "workflow_dispatch"}):
                        with self.subTest(change=change), self.assertRaises(ValueError):
                            issuer.guard_owner_push(repo, TRIAL, sha, {**env, **change})
                    event.write_text(json.dumps({**doc, "before": "0"*40}))
                    with self.assertRaises(ValueError):
                        issuer.guard_owner_push(repo, TRIAL, sha, env)
                    event.write_text(json.dumps({**doc, "forced": True}))
                    with self.assertRaises(ValueError):
                        issuer.guard_owner_push(repo, TRIAL, sha, env)
                    event.write_text(json.dumps(doc))
                    with patch.object(issuer, "remote", return_value=sha):
                        with self.assertRaises(ValueError):
                            issuer.guard_owner_push(repo, TRIAL, sha, env)
                    with self.assertRaises(ValueError):
                        issuer.guard(repo, "freeze", TRIAL, sha,
                                     issuer.FREEZE_CONFIRM+TRIAL, env)
        finally:
            temp.cleanup()

    def test_new_research_one_add_and_receipt_fail_closed_incomplete(self):
        temp, repo = source_copy()
        try:
            issuer_chain = synthetic_push_issuer(repo, trial=TRIAL)
            anchor = batch.issuer_structure(repo, trial_id=TRIAL,
                marker_commit=issuer_chain["marker"],
                authorization_commit=issuer_chain["auth"])
            self.assertEqual(anchor["authority_origin"], "owner_main_push")
            self.assertEqual(parent(repo, issuer_chain["auth"]), issuer_chain["marker"])
            git(repo, "checkout", "-B", batch.paths(TRIAL)["branch"], issuer_chain["auth"])
            item = issuer_chain["rows"][0]
            assignment = v2.frozen_assignment(repo, marker_commit=issuer_chain["marker"],
                                                trial_id=TRIAL, appid=item["appid"])
            doc = {"schema":"DOSSIER-RESEARCH-NOTES-V2", "schema_version":2,
                   "assignment":assignment, "notes_text":"Synthetic neutral Research only",
                   "research_status":"limited_evidence"}
            proposal = receipts.prepare_candidate(
                repo, marker_commit=issuer_chain["marker"], trial_id=TRIAL,
                appid=item["appid"], authorization_commit=issuer_chain["auth"],
                document=doc)
            candidate = replay.single_add(repo, proposal["output_path"],
                                           proposal["bytes"], "synthetic deterministic source")
            self.assertEqual(require_only_new(repo, candidate, [proposal["output_path"]]),
                             issuer_chain["auth"])
            with self.assertRaises(ValueError):
                replay.single_add(repo, proposal["output_path"], proposal["bytes"],
                                  "forbidden duplicate")
            rec = receipts.prepare_receipt(repo, marker_commit=issuer_chain["marker"],
                trial_id=TRIAL, appid=item["appid"], authorization_commit=issuer_chain["auth"],
                introduction_commit=candidate)
            receipt_commit = replay.single_add(repo, rec["receipt_path"],
                                                rec["receipt_bytes"], "synthetic typed receipt")
            verified = receipts.inspect_receipt_commit(
                repo, marker_commit=issuer_chain["marker"], trial_id=TRIAL,
                appid=item["appid"], authorization_commit=issuer_chain["auth"],
                introduction_commit=candidate, receipt_commit=receipt_commit)
            self.assertEqual(verified["disposition"], "safe_incomplete_research")
            sibling = v2.assembly_work(
                repo, marker_commit=issuer_chain["marker"], trial_id=TRIAL,
                appid=SIX[1], research_commit=candidate)
            self.assertNotEqual(sibling["status"], "ready_for_autonomous_assembly")
            self.assertFalse(sibling.get("canonical_acceptance", False))
            with self.assertRaises(v2.NotesV2Error):
                v2.candidate_assembly(
                    sibling, outcome="assembly_missing_evidence",
                    diagnostic="wrong original Research provenance")
            with self.assertRaises(ValueError):
                replay.seed(repo, trial_id=RERUN2, marker_commit=issuer_chain["marker"],
                            authorization_commit=issuer_chain["auth"])
        finally:
            temp.cleanup()

    def test_lean_final_exact_edition_and_temporal_safety_no_review_ledger(self):
        doc = make_lean_final(appid="499180", title="Braid, Anniversary Edition")
        self.assertNotIn("player_feedback_records", doc)
        self.assertNotIn("twelve_dimension_coverage", doc)
        self.assertEqual(validate_lean_final(doc, expected_appid="499180",
            expected_title="Braid, Anniversary Edition", expected_ttl_days=20, now=NOW), doc)
        wrong = dict(doc, title="Braid")
        with self.assertRaises(ValueError):
            validate_lean_final(wrong, expected_appid="499180",
                expected_title="Braid, Anniversary Edition", expected_ttl_days=20, now=NOW)
        current = json.loads(json.dumps(doc))
        current["observations"][0]["evidence_status"] = "current"
        with self.assertRaises(ValueError):
            validate_lean_final(current, expected_appid="499180",
                expected_title="Braid, Anniversary Edition", expected_ttl_days=20, now=NOW)


if __name__ == "__main__":
    unittest.main()
