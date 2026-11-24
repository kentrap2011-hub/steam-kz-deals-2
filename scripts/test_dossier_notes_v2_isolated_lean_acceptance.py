#!/usr/bin/env python3
"""Offline exact-six Lean writer transaction regression; never live authorization."""
import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import dossier_lean_canonical_dual as dual
import dossier_notes_v2_isolated_lean_readback as reader
from taste_steam_review_dossier import canonical_sha256
from test_dossier_notes_v2_lean_final import make_lean_final


class SixItemSandboxWriterTests(unittest.TestCase):
    def setUp(self):
        self.grant = json.loads(dual.SANDBOX_GRANT.read_text(encoding="utf-8"))
        self.temp = tempfile.TemporaryDirectory(prefix="lean-six-writer-git-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q", "-b", "sandbox/" + self.grant["trial_id"])
        self.git("config", "user.name", "offline-fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.docs = {}
        self.receipts = {}
        now = datetime.now(timezone.utc).replace(microsecond=0)
        for row in self.grant["items"]:
            appid = row["appid"]
            doc = make_lean_final(appid, row["title"], now=now)
            doc["ttl_days"] = 14
            doc["expires_at_utc"] = (now + timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")
            doc["game_identity"]["release_year"] = 2020
            store = self.root / reader.ROOT_STORE / self.grant["trial_id"] / ("App_" + appid + ".json")
            receipt = self.root / reader.ROOT_RECEIPTS / self.grant["trial_id"] / (
                "g" + str(row["group_sequence"]).zfill(6)) / (
                appid + "--" + row["assignment_id"] + ".json")
            raw = (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            store.parent.mkdir(parents=True, exist_ok=True)
            store.write_bytes(raw)
            record = {
                "schema": reader.RECEIPT_SCHEMA,
                "trial_id": self.grant["trial_id"],
                "marker_commit": self.grant["marker_commit"],
                "assignment": {"trial_id": self.grant["trial_id"],
                               "appid": appid, "title": row["title"],
                               "assignment_id": row["assignment_id"],
                               "group_sequence": row["group_sequence"]},
                "research_commit": row["research_commit"],
                "assembly_commit": row["assembly_commit"],
                "dossier_sha256": canonical_sha256(doc),
                "dossier_raw_sha256": hashlib.sha256(raw).hexdigest(),
                "dossier_format": dual.LEAN_SCHEMA,
                "quality_binding": dual.quality_binding(),
                "original_release_year": doc["game_identity"]["release_year"],
                "isolated_sandbox_acceptance": True,
                "canonical_acceptance": False,
                "deep_ready": False,
            }
            receipt.parent.mkdir(parents=True, exist_ok=True)
            receipt.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            self.docs[appid] = (doc, store)
            self.receipts[appid] = receipt
        self.git("add", "data/control/dossier_notes_v2/")

    def git(self, *args):
        completed = subprocess.run(["git", "-C", str(self.root), *args],
                                   capture_output=True, text=True)
        if completed.returncode:
            raise AssertionError(completed.stderr)
        return completed.stdout.strip()

    def verify(self, mode):
        def work(*args, **kwargs):
            return {"output_path": "candidate/" + kwargs["appid"]}

        def original(repo, commit, path):
            appid = path.split("/")[-1]
            return {"outcome": "assembled_candidate_ready", "final_dossier": self.docs[appid][0]}

        with patch("dossier_research_notes_v2.inspect_assembly", return_value={
                "status": "strict_item_valid_pending_existing_atomic_group_ingest"
             }), patch("dossier_research_notes_v2.assembly_work", side_effect=work), patch(
                "dossier_two_stage_staging.json_at", side_effect=original):
            return reader.exact_transaction(self.root, mode=mode)

    def test_six_positive_staged_then_committed_and_no_deep_main(self):
        result = self.verify("staged")
        self.assertEqual(result["verified_items"], 6)
        self.assertFalse(result["canonical_acceptance"])
        self.assertFalse(result["deep_ready"])
        self.git("commit", "-qm", "offline isolated six-item writer")
        self.assertEqual(self.verify("committed")["verified_items"], 6)
        self.assertEqual(len(self.git("show", "--pretty=format:", "--name-only", "HEAD").splitlines()), 12)

    def test_missing_one_receipt_does_not_count_as_six(self):
        self.receipts["102600"].unlink()
        with self.assertRaisesRegex(ValueError, "missing or unsafe"):
            self.verify("staged")

    def test_staged_group_must_have_exactly_twelve_paths(self):
        (self.root / "unexpected.txt").write_text("other")
        self.git("add", "unexpected.txt")
        with self.assertRaisesRegex(ValueError, "not exactly 12"):
            self.verify("staged")

    def test_wrong_edition_or_appid_refused(self):
        doc, store = self.docs["499180"]
        doc = copy.deepcopy(doc)
        doc["title"] = "Braid"
        store.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
        self.git("add", "data/control/dossier_notes_v2/")
        with self.assertRaisesRegex(ValueError, "record/receipt/hash mismatch"):
            self.verify("staged")

    def test_hash_tamper_and_wrong_acceptance_flags_refused(self):
        receipt = self.receipts["1000010"]
        value = json.loads(receipt.read_text())
        value["dossier_raw_sha256"] = "0" * 64
        receipt.write_text(json.dumps(value), encoding="utf-8")
        self.git("add", "data/control/dossier_notes_v2/")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.verify("staged")
        value["dossier_raw_sha256"] = hashlib.sha256(self.docs["1000010"][1].read_bytes()).hexdigest()
        value["canonical_acceptance"] = True
        receipt.write_text(json.dumps(value), encoding="utf-8")
        self.git("add", "data/control/dossier_notes_v2/")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            self.verify("staged")

    def test_bad_ttl_and_unsafe_source_refused(self):
        doc, store = self.docs["49520"]
        doc["ttl_days"] = 20
        store.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
        self.git("add", "data/control/dossier_notes_v2/")
        with self.assertRaises(ValueError):
            self.verify("staged")
        # Independent Lean validator (not a typed transport receipt).
        doc["ttl_days"] = 14
        doc["sources"][0]["url"] = "http://127.0.0.1/private"
        with self.assertRaises(ValueError):
            dual.validate_writer_lean(doc, appid="49520", title="Borderlands 2",
                                      expected_ttl_days=14)

    def test_wrong_git_branch_refused_and_head_never_uncommitted_acceptance(self):
        self.git("checkout", "-qb", "wrong-target")
        with self.assertRaisesRegex(ValueError, "not on frozen sandbox"):
            self.verify("staged")

    def test_frozen_exact_six_and_strict_gate_separation(self):
        self.assertEqual([x["appid"] for x in self.grant["items"]],
                         ["1000010","102600","1029690","49520","499180","501590"])
        for key in ("lean_writer_enabled","lean_reader_enabled","lean_deep_enabled"):
            self.assertFalse(dual._policy()[key])
        with self.assertRaisesRegex(ValueError, "disabled"):
            dual.require_gate("writer")
        with self.assertRaisesRegex(ValueError, "frozen"):
            dual.require_isolated_sandbox_writer(
                self.root, trial_id=self.grant["trial_id"],
                marker_commit=self.grant["marker_commit"],
                item_commits={row["appid"]:{
                    "research_commit":row["research_commit"],
                    "assembly_commit":row["assembly_commit"]
                } for row in self.grant["items"]},
                issuer={"authorization_commit":self.grant["authorization_commit"],
                        "github_authorization_run_id":self.grant["owner_source_actions_run_id"],
                        "request_commit":self.grant["original_request_commit"]})


    def isolated_writer(self, *, broken_appid=None, incomplete=False):
        # Exercise the REAL shared writer on disposable Git only. Authentication
        # and immutable source Git lookups are synthetic mocks, never accepted
        # owner evidence. Full Lean validation, writes and collision gates are real.
        import os
        import shutil
        from taste_steam_review_dossier_buffered import drain_buffered_groups
        from dossier_notes_v2_batch_route import REPOSITORY, WRITER_WORKFLOW, OWNER_ID, OWNER_LOGIN

        self.git("reset", "-q")
        shutil.rmtree(self.root / reader.ROOT_STORE)
        shutil.rmtree(self.root / reader.ROOT_RECEIPTS)
        trial = self.grant["trial_id"]
        auth_path = (self.root / "data/control/dossier_notes_v2/authorizations"
                     / (trial + ".json"))
        auth_path.parent.mkdir(parents=True, exist_ok=True)
        auth_path.write_text('{"offline_fixture_only":true}\n', encoding="utf-8")
        self.git("add", str(auth_path.relative_to(self.root)))
        self.git("commit", "-qm", "offline synthetic authorizer")
        rows = self.grant["items"]
        item_map = {r["appid"]: {
            "research_commit": r["research_commit"],
            "assembly_commit": r["assembly_commit"],
        } for r in rows}
        documents = {a: copy.deepcopy(doc) for a, (doc, _) in self.docs.items()}
        if broken_appid is not None:
            documents[broken_appid]["game_identity"]["release_year"] = None
        projection = {"items": [
            {"appid": row["appid"], "group_sequence": row["group_sequence"],
             "status": "missing" if incomplete and row["appid"] == "102600" else "ready"}
            for row in rows
        ]}
        assignment = {
            row["appid"]: {
                "trial_id": trial, "appid": row["appid"],
                "title": row["title"], "group_sequence": row["group_sequence"],
                "assignment_id": row["assignment_id"],
            } for row in rows
        }
        current_appid = ["1000010"]

        def inspect(repo, *, marker_commit, trial_id, appid, research_commit, result_commit):
            current_appid[0] = appid
            return {"status": "strict_item_valid_pending_existing_atomic_group_ingest"}

        def work(repo, *, marker_commit, trial_id, appid, research_commit):
            current_appid[0] = appid
            return {"status": "ready_for_autonomous_assembly",
                    "assignment": assignment[appid], "research_transport": {},
                    "output_path": "dummy/" + appid}

        def candidate(repo, commit, path):
            a = path.split("/")[-1]
            return {"assignment": assignment[a], "research_transport": {},
                    "outcome": "assembled_candidate_ready", "final_dossier": documents[a]}

        env = {
            "GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "workflow_dispatch",
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_WORKFLOW_REF": REPOSITORY + "/" + WRITER_WORKFLOW + "@refs/heads/main",
            "GITHUB_REPOSITORY": REPOSITORY,
            "GITHUB_REPOSITORY_OWNER_ID": OWNER_ID,
            "GITHUB_ACTOR_ID": OWNER_ID, "GITHUB_ACTOR": OWNER_LOGIN,
            "GITHUB_TRIGGERING_ACTOR": OWNER_LOGIN,
            "GITHUB_RUN_ATTEMPT": "1", "GITHUB_RUN_ID": "1234",
            "GITHUB_TOKEN": "offline-fixture-not-a-real-token",
        }
        with patch.dict(os.environ, env), patch(
                "dossier_notes_v2_generic_replay.policy", return_value={}), patch(
                "dossier_notes_v2_batch_route.issuer_structure",
                return_value={"authorization_commit": self.grant["authorization_commit"],
                              "semantic_execution_authorized": True}), patch(
                "dossier_notes_v2_batch_route.authenticated_owner_run",
                return_value=True), patch(
                "dossier_research_notes_v2.individual_final_readiness",
                return_value=projection), patch(
                "dossier_notes_v2_per_item_receipts.require_batch_terminal_receipts",
                return_value=True), patch(
                "dossier_research_notes_v2.inspect_assembly", side_effect=inspect), patch(
                "dossier_research_notes_v2.assembly_work", side_effect=work), patch(
                "dossier_two_stage_staging.json_at", side_effect=candidate), patch.object(
                dual, "require_isolated_sandbox_writer",
                return_value={r["appid"]: r for r in rows}):
            return drain_buffered_groups(notes_v2={
                "repo": self.root, "marker_commit": self.grant["marker_commit"],
                "trial_id": trial, "item_commits": item_map,
                "store_dir": self.root / reader.ROOT_STORE / trial,
                "accepted_dir": self.root / reader.ROOT_RECEIPTS,
                "offline_fixture": False, "trial_sandbox": True,
            })

    def test_actual_writer_six_lean_records_and_receipts_in_sandbox_only(self):
        result = self.isolated_writer()
        self.assertFalse(result["canonical_acceptance"])
        self.assertEqual(len(result["items"]), 6)
        self.assertEqual([r["status"] for r in result["items"]],
                         ["persisted_pending_github_commit"] * 6)
        for row in self.grant["items"]:
            appid = row["appid"]
            receipt = self.root / reader.ROOT_RECEIPTS / self.grant["trial_id"] / (
                "g" + str(row["group_sequence"]).zfill(6)) / (
                appid + "--" + row["assignment_id"] + ".json")
            bound = json.loads(receipt.read_text())
            raw = (self.root / reader.ROOT_STORE / self.grant["trial_id"]
                   / ("App_" + appid + ".json")).read_bytes()
            self.assertEqual(bound["dossier_raw_sha256"],
                             hashlib.sha256(raw).hexdigest())
            self.assertFalse(bound["canonical_acceptance"])
            self.assertFalse(bound["deep_ready"])
        self.assertFalse((self.root / dual.STORE).exists())
        self.assertFalse((self.root / dual.RECEIPTS).exists())

    def test_actual_writer_rejects_invalid_lean_atomically(self):
        with self.assertRaisesRegex(ValueError, "six-item transaction incomplete"):
            self.isolated_writer(broken_appid="1029690")
        # Disposable transient files are NOT an accepted owner Git commit/push.
        self.assertFalse(self.git("log", "-1", "--format=%s").startswith("Persist isolated"))

    def test_actual_writer_rejects_partial_group_before_any_write(self):
        with self.assertRaisesRegex(ValueError, "six-item Lean sandbox atomic readiness"):
            self.isolated_writer(incomplete=True)
        self.assertFalse((self.root / reader.ROOT_STORE).exists())

if __name__ == "__main__":
    unittest.main()
