#!/usr/bin/env python3
"""Disposable Git-only Notes V2 per-item receipt regression, no network or semantics."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import dossier_research_notes_v2 as v2
import dossier_notes_v2_per_item_receipts as receipts
from dossier_two_stage_staging import blob
from test_dossier_research_notes_v2 import TRIAL, NONCE, run, write, commit


def raw_commit(repo, path, raw, message):
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(raw)
    return commit(repo, message)


class PerItemReceiptGitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        run(self.repo, "init", "-q")
        run(self.repo, "config", "user.name", "Disposable Receipt Fixture")
        run(self.repo, "config", "user.email", "receipt-fixture@example.invalid")
        contract = json.loads(v2.CONTRACT_PATH.read_text(encoding="utf-8"))
        rows = v2._original_rows()
        self.appid = "2124120"
        self.grant_path = "config/dossier_notes_v2_issuer_human_grant.json"
        self.manifest_path = f"data/control/dossier_notes_v2/manifests/{TRIAL}.json"
        self.marker_path = f"data/control/dossier_notes_v2/run_starts/{NONCE}.json"
        self.authorization_path = f"data/control/dossier_notes_v2/authorizations/{TRIAL}.json"
        # Only disposable Git inputs; actual original frozen snapshot is read-only.
        for path, source in (
            ("config/dossier_research_notes_v2_contract.json", v2.CONTRACT_PATH),
            ("scripts/dossier_research_notes_v2.py", Path(v2.__file__))):
            p = self.repo / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(source.read_bytes())
        commit(self.repo, "fixture: inert code/contract")
        write(self.repo, self.grant_path, {
            "schema": "DOSSIER-NOTES-V2-MANUAL-ISSUER-HUMAN-GRANT",
            "schema_version": 2, "trial_id": TRIAL,
            "original_buffer_blob_sha": contract["original_research_identity_authority"]["original_buffer_git_blob_sha"],
            "original_pins": contract["immutable_original_pins"],
            "original_groups": contract["original_groups"],
            "github_actor_id": "12345",
            "scope": "issue_single_original18_V2_manifest_marker_then_separate_authorization_only",
            "semantic_execution_approved": False, "production_approved": False,
        })
        self.grant = commit(self.repo, "fixture: fake grant only")
        write(self.repo, self.manifest_path, {
            "schema": "DOSSIER-NOTES-V2-FROZEN-MANIFEST", "schema_version": 2,
            "trial_id": TRIAL, "original_pins": contract["immutable_original_pins"],
            "items": copy.deepcopy(rows),
        })
        self.manifest_parent = commit(self.repo, "fixture: frozen original eighteen")
        write(self.repo, self.marker_path, {
            "schema": "DOSSIER-NOTES-V2-RUN-START", "schema_version": 2,
            "nonce": NONCE, "trial_id": TRIAL,
        })
        self.marker = commit(self.repo, "fixture: distinct mock V2 marker")
        self.auth_doc = {
            "schema": receipts.ISSUER_SCHEMA, "schema_version": 2,
            "trial_id": TRIAL, "marker_commit": self.marker,
            "marker_parent": self.manifest_parent, "marker_nonce": NONCE,
            "manifest_path": self.manifest_path,
            "manifest_blob_sha": blob(self.repo, self.manifest_parent, self.manifest_path),
            "original_pins": contract["immutable_original_pins"],
            "original_buffer_blob_sha": contract["original_research_identity_authority"]["original_buffer_git_blob_sha"],
            "v2_contract_blob_sha": blob(self.repo, self.manifest_parent,
                                        "config/dossier_research_notes_v2_contract.json"),
            "v2_research_guard_blob_sha": blob(self.repo, self.manifest_parent,
                                              "scripts/dossier_research_notes_v2.py"),
            "human_grant_commit": self.grant,
            "human_grant_blob_sha": blob(self.repo, self.grant, self.grant_path),
            "github_actor_id": "12345", "github_authorization_run_id": "98765",
            "mode": "original18_inactive_V2_control_plane_issuance_only",
            "semantic_execution_authorized": False, "canonical_acceptance": False,
            "assembly_authorized": False, "production_authorized": False,
        }
        write(self.repo, self.authorization_path, self.auth_doc)
        self.auth = commit(self.repo, "fixture: direct child mock issuer")
        self.assignment = v2.frozen_assignment(
            self.repo, marker_commit=self.marker, trial_id=TRIAL, appid=self.appid)
        self.notes_path = v2._path("research", self.assignment)

    def kw(self, **overrides):
        return {
            **{"marker_commit": self.marker, "trial_id": TRIAL,
               "appid": self.appid, "authorization_commit": self.auth},
            **overrides,
        }

    def note(self, **updates):
        doc = {"schema": "DOSSIER-RESEARCH-NOTES-V2", "schema_version": 2,
               "assignment": copy.deepcopy(self.assignment), "notes_text": "",
               "source_log": [], "research_status": "no_verifiable_findings"}
        doc.update(updates)
        return doc

    def add_candidate(self, doc=None):
        doc = self.note() if doc is None else doc
        write(self.repo, self.notes_path, doc)
        return commit(self.repo, "fixture: one add notes")

    def receipt(self, source_commit):
        return receipts.prepare_receipt(
            self.repo, **self.kw(introduction_commit=source_commit))

    def add_receipt(self, source_commit):
        proposed = self.receipt(source_commit)
        p = self.repo / proposed["receipt_path"]
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(proposed["receipt_bytes"])
        sha = commit(self.repo, "fixture: one immutable receipt")
        return sha, proposed

    def inspect(self, receipt_commit, source_commit):
        return receipts.inspect_receipt_commit(
            self.repo, **self.kw(introduction_commit=source_commit,
                                 receipt_commit=receipt_commit))

    def test_one_valid_item_and_provenance_stays_noncanonical(self):
        proposal = receipts.prepare_candidate(
            self.repo, **self.kw(document=self.note()))
        self.assertFalse(proposal["github_receipt_confirmed"])
        self.assertEqual(proposal["blob_sha"], v2.blob_for(proposal["bytes"]))
        source = self.add_candidate()
        local = receipts.inspect_candidate(
            self.repo, **self.kw(introduction_commit=source))
        self.assertTrue(local["transport_technically_verified"])
        self.assertFalse(local["semantic_quality_accepted"])
        sha, plan = self.add_receipt(source)
        proof = self.inspect(sha, source)
        self.assertEqual(proof["receipt_blob_sha"], plan["receipt_blob_sha"])
        self.assertEqual(proof["disposition"], "safe_incomplete_research")
        self.assertFalse(proof["github_receipt_confirmed"])
        self.assertFalse(proof["canonical_acceptance"])

    def test_create_only_replay_and_altered_payload(self):
        source = self.add_candidate()
        with self.assertRaises(v2.NotesV2Error):
            receipts.prepare_candidate(self.repo, **self.kw(document=self.note()))
        sha, _ = self.add_receipt(source)
        with self.assertRaises(v2.NotesV2Error):
            self.receipt(source)
        changed = self.note(notes_text="forged after first write")
        write(self.repo, self.notes_path, changed)
        commit(self.repo, "fixture: corrupt original Notes")
        with self.assertRaises(v2.NotesV2Error):
            self.inspect(sha, source)

    def test_receipt_blob_replacement_and_restore_are_not_accepted(self):
        source = self.add_candidate()
        sha, plan = self.add_receipt(source)
        raw_commit(self.repo, plan["receipt_path"], b"{}", "fixture: rewrite receipt")
        raw_commit(self.repo, plan["receipt_path"], plan["receipt_bytes"], "fixture: restore receipt")
        with self.assertRaises(v2.NotesV2Error):
            self.inspect(sha, source)

    def test_wrong_item_group_and_source_binding(self):
        d = self.note()
        d["assignment"]["group_sequence"] = 3
        with self.assertRaises(v2.NotesV2Error):
            receipts.prepare_candidate(self.repo, **self.kw(document=d))
        with self.assertRaises(v2.NotesV2Error):
            receipts.prepare_candidate(self.repo, **self.kw(appid="999999",
                                                            document=self.note()))

    def test_wrong_issuer_parent_nonce_or_no_grant(self):
        for key, value in (
            ("marker_nonce", "f"*32), ("human_grant_commit", "f"*40),
            ("v2_contract_blob_sha", "0"*40),
            ("semantic_execution_authorized", True)):
            run(self.repo, "checkout", "-q", "-b", "wrong-"+key, self.marker)
            forged = copy.deepcopy(self.auth_doc)
            forged[key] = value
            write(self.repo, self.authorization_path, forged)
            wrong = commit(self.repo, "fixture: poisoned issuer " + key)
            with self.subTest(key=key), self.assertRaises((ValueError, RuntimeError)):
                receipts.issuer_structure(
                    self.repo, marker_commit=self.marker, trial_id=TRIAL,
                    authorization_commit=wrong)
            run(self.repo, "checkout", "-q", "--detach", self.auth)

    def test_auth_commit_not_direct_child_or_marker_not_ancestor(self):
        source = self.add_candidate()
        with self.assertRaises((ValueError, RuntimeError)):
            receipts.inspect_candidate(
                self.repo, **self.kw(authorization_commit=source,
                                     introduction_commit=source))
        with self.assertRaises((ValueError, RuntimeError)):
            receipts.inspect_candidate(
                self.repo, **self.kw(introduction_commit=self.marker))

    def test_rejection_receipt_never_becomes_accepted(self):
        bad = raw_commit(self.repo, self.notes_path, b"{broken", "fixture: bad JSON")
        rejected = receipts.inspect_candidate(
            self.repo, **self.kw(introduction_commit=bad))
        self.assertEqual(rejected["status"], "unparseable")
        self.assertFalse(rejected["transport_technically_verified"])
        sha, proposed = self.add_receipt(bad)
        self.assertFalse(proposed["technical_acceptance_proposed"])
        proof = self.inspect(sha, bad)
        self.assertEqual(proof["disposition"], "unparseable")
        self.assertFalse(proof["github_receipt_confirmed"])

    def test_missing_candidate_does_not_consume_attempt(self):
        plan = self.receipt(None)
        self.assertEqual(plan["disposition"], "missing_research_transport")
        self.assertEqual(plan["attempt_state"], "unknown")
        self.assertFalse(plan["technical_acceptance_proposed"])

    def test_extra_file_in_candidate_is_rejected(self):
        write(self.repo, self.notes_path, self.note())
        write(self.repo, "data/ai_inbox/dossier_notes_v2/extra.json", {"bad": True})
        source = commit(self.repo, "fixture: illegal candidate double add")
        info = receipts.inspect_candidate(
            self.repo, **self.kw(introduction_commit=source))
        self.assertEqual(info["status"], "broken_git_provenance")
        sha, _ = self.add_receipt(source)
        proof = self.inspect(sha, source)
        self.assertEqual(proof["disposition"], "broken_git_provenance")
        self.assertFalse(proof["technical_acceptance_proposed"])

    def test_concurrent_local_branches_are_not_remote_confirmation(self):
        source = self.add_candidate()
        run(self.repo, "branch", "second-writer", source)
        sha_a, _ = self.add_receipt(source)
        self.assertFalse(self.inspect(sha_a, source)["github_receipt_confirmed"])
        run(self.repo, "checkout", "-q", "second-writer")
        sha_b, _ = self.add_receipt(source)
        self.assertFalse(self.inspect(sha_b, source)["github_receipt_confirmed"])
        # Both branches could have produced local commits: only future GitHub
        # remote ref CAS + authenticated re-fetch may choose the winner.
        self.assertTrue(sha_a)
        self.assertTrue(sha_b)



    def setup_disposable_remote(self):
        """Bare Git transport only: never a GitHub-authenticated result."""
        bare = self.repo / "remote.git"
        run(self.repo, "init", "--bare", str(bare))
        run(self.repo, "remote", "add", "origin", str(bare))
        branch = "sandbox/notes-v2-fixture"
        run(self.repo, "branch", branch, self.auth)
        run(self.repo, "push", "origin", branch)
        return branch

    def test_remote_candidate_then_receipt_one_item_exact_readback(self):
        branch = self.setup_disposable_remote()
        sent = receipts.publish_candidate_remote(
            self.repo, branch=branch, expected_remote_head=self.auth,
            **self.kw(document=self.note()))
        self.assertTrue(sent["remote_git_confirmed"])
        self.assertFalse(sent["github_candidate_confirmed"])
        self.assertFalse(sent["github_receipt_confirmed"])
        self.assertEqual(receipts._remote_tip(self.repo, branch), sent["remote_commit"])
        self.assertEqual(run(self.repo, "rev-parse", "HEAD"), self.auth)
        receipt = receipts.publish_receipt_remote(
            self.repo, branch=branch, expected_remote_head=sent["remote_commit"],
            **self.kw(introduction_commit=sent["remote_commit"]))
        self.assertEqual(receipts._remote_tip(self.repo, branch), receipt["remote_commit"])
        self.assertTrue(receipt["remote_git_confirmed"])
        self.assertFalse(receipt["github_receipt_confirmed"])
        self.assertFalse(receipt["canonical_acceptance"])
        self.assertEqual(run(self.repo, "rev-parse", "HEAD"), self.auth)

    def test_remote_failure_for_a_does_not_prevent_b(self):
        branch = self.setup_disposable_remote()
        bad_a = self.note()
        bad_a["assignment"]["appid"] = "invalid"
        with self.assertRaises(v2.NotesV2Error):
            receipts.publish_candidate_remote(
                self.repo, branch=branch, expected_remote_head=self.auth,
                **self.kw(document=bad_a))
        self.assertEqual(receipts._remote_tip(self.repo, branch), self.auth)
        other = "213610"
        other_assignment = v2.frozen_assignment(
            self.repo, marker_commit=self.marker, trial_id=TRIAL, appid=other)
        good_b = {**self.note(), "assignment": other_assignment}
        sent = receipts.publish_candidate_remote(
            self.repo, branch=branch, expected_remote_head=self.auth,
            **self.kw(appid=other, document=good_b))
        self.assertTrue(sent["remote_git_confirmed"])
        receipt = receipts.publish_receipt_remote(
            self.repo, branch=branch, expected_remote_head=sent["remote_commit"],
            **self.kw(appid=other, introduction_commit=sent["remote_commit"]))
        self.assertTrue(receipt["remote_git_confirmed"])
        self.assertFalse(receipt["github_receipt_confirmed"])
        self.assertEqual(receipts._remote_tip(self.repo, branch), receipt["remote_commit"])

    def test_complete_one_game_remote_path_remains_noncanonical(self):
        branch = self.setup_disposable_remote()
        result = receipts.publish_one_research_item_remote(
            self.repo, branch=branch, expected_remote_head=self.auth,
            **self.kw(document=self.note()))
        self.assertEqual(result["status"], "disposable_remote_item_only")
        self.assertEqual(receipts._remote_tip(self.repo, branch), result["receipt_commit"])
        self.assertNotEqual(result["candidate_commit"], result["receipt_commit"])
        self.assertFalse(result["github_receipt_confirmed"])
        self.assertFalse(result["semantic_quality_accepted"])
        self.assertFalse(result["canonical_acceptance"])

    def test_remote_duplicate_stale_parent_and_spoofed_github_fail_closed(self):
        branch = self.setup_disposable_remote()
        sent = receipts.publish_candidate_remote(
            self.repo, branch=branch, expected_remote_head=self.auth,
            **self.kw(document=self.note()))
        with self.assertRaises(v2.NotesV2Error):
            receipts.publish_candidate_remote(
                self.repo, branch=branch, expected_remote_head=self.auth,
                **self.kw(document=self.note()))
        with self.assertRaises(v2.NotesV2Error):
            receipts.publish_candidate_remote(
                self.repo, branch=branch, expected_remote_head=sent["remote_commit"],
                **self.kw(document=self.note()))
        with self.assertRaises(v2.NotesV2Error):
            receipts.publish_receipt_remote(
                self.repo, branch=branch, expected_remote_head=sent["remote_commit"],
                github_repository="kentrap2011-hub/steam-kz-deals-2",
                github_token="fixture-not-a-real-token",
                **self.kw(introduction_commit=sent["remote_commit"]))
        self.assertEqual(receipts._remote_tip(self.repo, branch), sent["remote_commit"])


if __name__ == "__main__":
    unittest.main()
