#!/usr/bin/env python3
"""P2 offline Git-history, immutable transport and lifecycle regressions only."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from test_dossier_two_stage_contract_schemas import research_fixture
from dossier_two_stage_contract_guard import CONFIG, canonical_sha256
from dossier_two_stage_staging import (
    gate, prepared_path, receipt_paths, bytes_json, blob_for,
    receive_research, prepare_assembly, RESEARCH_MARKER, ASSEMBLY_MARKER,
    assembly_authority, first_parent_contains,
)


class GitFixture:
    def __init__(self, root):
        self.root = Path(root)
        self.run("init", "-q")
        self.run("config", "user.name", "P2 Fixture")
        self.run("config", "user.email", "fixture@example.invalid")
        self.doc = research_fixture()
        self.a = self.doc["assignment"]
        self.a["research_contract_sha256"] = canonical_sha256(json.loads(
            (CONFIG / "dossier_research_package_v1.schema.json").read_text("utf-8")))
        self.nonce = "a" * 32
        items = [{"appid": self.a["appid"], "title": self.a["title"]}]
        fields = {
            "snapshot_id": self.a["snapshot_id"],
            "prepared_required_sha256": self.a["prepared_required_sha256"],
            "sequence": 1, "start_index": 0, "end_index_exclusive": 1,
            "appids": [self.a["appid"]],
            "items_sha256": canonical_sha256(items),
            "scope_source": self.a["scope_source"],
            "source_queue_sha256": self.a["source_queue_sha256"],
        }
        self.a["items_sha256"] = fields["items_sha256"]
        self.a["group_sha256"] = canonical_sha256(fields)
        self.descriptor = {
            "schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1",
            "schema_version": 1,
            "group_plan_sha256": self.a["group_plan_sha256"],
            "group_count": 1,
            "web_evidence_contract_binding": copy.deepcopy(self.a["web_evidence_contract_binding"]),
            "items": items,
            "group_sha256": self.a["group_sha256"], **fields,
        }
        self.index = {
            "schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2",
            "schema_version": 2, "snapshot_id": self.a["snapshot_id"],
            "prepared_required_sha256": self.a["prepared_required_sha256"],
            "group_plan_sha256": self.a["group_plan_sha256"],
            "pending_group_sequences": [1],
        }
        self.p_path = prepared_path(self.a)
        self.save("config/dossier_research_package_v1.schema.json", json.loads(
            (CONFIG / "dossier_research_package_v1.schema.json").read_text("utf-8")))
        self.save(self.p_path, {k: v for k, v in self.a.items()
                                if k not in ("research_marker_anchor_commit", "research_marker_nonce")})
        self.save("data/production/pre_ai/taste_steam_review_dossier_worker_index.json", self.index)
        self.save("data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
                  f"{self.a['snapshot_id']}/g000001.json", self.descriptor)
        self.commit("GitHub prepared frozen Research assignment")
        self.save(f"{RESEARCH_MARKER}/{self.nonce}.json", {
            "schema": "DOSSIER-RESEARCH-RUN-START-MARKER-V1",
            "schema_version": 1, "run_start_nonce": self.nonce,
        })
        self.marker = self.commit("Research marker create-only")
        self.a["research_marker_anchor_commit"] = self.marker
        self.a["research_marker_nonce"] = self.nonce
        self.source_path = receipt_paths(self.a)["candidate"]
        self.package_commit = None

    def run(self, *args):
        proc = subprocess.run(["git", *args], cwd=self.root, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True)
        if proc.returncode:
            raise AssertionError(f"Fixture git command {args} failed: {proc.stderr}")
        return proc.stdout.strip()

    def save(self, path, obj):
        dest = self.root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(bytes_json(obj))

    def commit(self, message):
        self.run("add", "-A")
        self.run("commit", "-qm", message)
        return self.run("rev-parse", "HEAD")

    def submit(self, mutate=None, raw=None):
        obj = copy.deepcopy(self.doc)
        if mutate:
            mutate(obj)
        dest = self.root / self.source_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw if raw is not None else bytes_json(obj))
        self.package_commit = self.commit("Research worker immutable package candidate")
        return self.package_commit

    def receive(self):
        return receive_research(self.root, marker_commit=self.marker,
                                prepared_work_path=self.p_path,
                                package_commit=self.package_commit)

    def persist(self, proposal):
        for path, doc in proposal["files"].items():
            if (self.root / path).exists():
                raise AssertionError("fixture must be create-only")
            self.save(path, doc)
        return self.commit("GitHub staged create-only exact Research/Assembly outcomes")

    def research_accepted(self):
        self.submit()
        p = self.receive()
        if p["status"] != "accepted_structural_evidence":
            raise AssertionError(p["status"])
        self.persist(p)
        return p

    def stage_plan(self, accepted):
        self.plan = {
            "schema": "DOSSIER-ASSEMBLY-GITHUB-PLAN-V1", "schema_version": 1,
            "research_assignment_id": self.a["assignment_id"],
            "assembly_assignment_id": "assembly-prepared-fixture-0001",
            "accepted_research_package_sha256": accepted["files"][accepted["receipt_path"]]["research_package_sha256"],
            "accepted_research_receipt_blob_sha": accepted["receipt_blob_sha"],
            "assembly_contract_sha256": "9" * 64, "assembly_prompt_sha256": "8" * 64,
            "assembly_prompt_revision": "fixture-inactive",
            "canonical_dossier_target": {
                "schema": "TASTE-STEAM-REVIEW-DOSSIER-V2", "schema_version": 2,
                "worker_schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2",
                "worker_schema_version": 2,
                "web_evidence_contract": "TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2",
                "web_evidence_contract_version": 2,
                "canonical_worker_binding_sha256": canonical_sha256(self.a["web_evidence_contract_binding"]),
            },
        }
        self.plan_path = receipt_paths(self.a)["assembly_plan"]
        self.save(self.plan_path, self.plan)
        self.commit("GitHub predeclared exact Assembly plan")
        self.assembly_nonce = "b" * 32
        self.save(f"{ASSEMBLY_MARKER}/{self.assembly_nonce}.json", {
            "schema": "DOSSIER-ASSEMBLY-RUN-START-MARKER-V1", "schema_version": 1,
            "run_start_nonce": self.assembly_nonce,
        })
        self.assembly_marker = self.commit("GitHub frozen Stage B marker")

    def prepare(self):
        return prepare_assembly(self.root, marker_commit=self.assembly_marker,
                                plan_path=self.plan_path)


class P2StagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.f = GitFixture(self.temp.name)

    def test_01_gate_closed_and_no_active_production_writer(self):
        c, s = gate()
        self.assertFalse(c["active"])
        self.assertFalse(s["active"])
        self.assertFalse(s["executable_in_production"])

    def test_02_accepted_receipt_real_git_blob_and_state(self):
        self.f.submit()
        result = self.f.receive()
        self.assertEqual(result["status"], "accepted_structural_evidence")
        receipt = result["files"][result["receipt_path"]]
        state = result["files"][receipt_paths(self.f.a)["state"]]
        self.assertEqual(receipt["research_package_sha256"], canonical_sha256(self.f.doc))
        self.assertEqual(receipt["research_package_git_commit"], self.f.package_commit)
        self.assertEqual(result["receipt_blob_sha"], blob_for(bytes_json(receipt)))
        self.assertEqual(state["research_receipt_blob_sha"], result["receipt_blob_sha"])
        self.assertFalse(receipt["canonical_acceptance"])
        self.assertFalse(state["normal_first_pass_attempt_consumed"])

    def test_03_invalid_json_produces_safe_typed_rejection(self):
        self.f.submit(raw=b'{"bad": [}')
        p = self.f.receive()
        self.assertEqual(p["status"], "rejected_invalid")
        r = p["files"][p["receipt_path"]]
        self.assertEqual(r["reason_code"], "invalid_json")
        self.assertNotIn("bad", json.dumps(r))
        self.assertFalse(r["retry_authorized"])

    def test_04_duplicate_raw_json_field_rejected(self):
        self.f.submit(raw=b'{"schema": 1, "schema": 2}')
        self.assertEqual(self.f.receive()["status"], "rejected_invalid")

    def test_05_unknown_schema_field_rejected(self):
        self.f.submit(lambda x: x.update({"extra": "forbidden"}))
        p = self.f.receive()
        self.assertEqual(p["files"][p["receipt_path"]]["reason_code"], "invalid_schema")

    def test_06_broken_feedback_and_privacy_fail_closed(self):
        for mutation in (
            lambda x: x["findings"][0].update({"support_feedback_refs": ["rfeedback-999"]}),
            lambda x: x["sources"][1].update({"username": "private_handle"}),
            lambda x: x["sources"][1].update({"locator": {"url": "https://example.org/users/me"}}),
        ):
            with self.subTest(mutation=mutation):
                with tempfile.TemporaryDirectory() as d:
                    f = GitFixture(d)
                    f.submit(mutation)
                    self.assertEqual(f.receive()["status"], "rejected_invalid")

    def test_07_alias_source_dedupe_normalizes_tracking(self):
        def mutate(x):
            s = copy.deepcopy(x["sources"][1])
            s["ref"] = "rsource-003"
            s["locator"]["url"] += "/?utm_source=foo"
            s["normalized_locator"] = None
            s["physical_source_identity"] = None
            x["sources"].append(s)
        self.f.submit(mutate)
        p = self.f.receive()
        self.assertEqual(p["status"], "rejected_invalid")

    def test_08_mismatched_work_id_does_not_rebind(self):
        self.f.submit(lambda x: x["assignment"].update({"appid": "56789"}))
        self.assertEqual(self.f.receive()["status"], "rejected_invalid")

    def test_09_missing_frozen_descriptor_rejected_before_publication(self):
        self.f.submit()
        with self.assertRaisesRegex(ValueError, "Git provenance|descriptor"):
            receive_research(self.f.root, marker_commit=self.f.marker,
                             prepared_work_path=self.f.p_path + "-wrong",
                             package_commit=self.f.package_commit)

    def test_10_tampered_marker_fails_without_receipt(self):
        self.f.submit()
        with self.assertRaises(ValueError):
            receive_research(self.f.root, marker_commit=self.f.package_commit,
                             prepared_work_path=self.f.p_path,
                             package_commit=self.f.package_commit)

    def test_11_replayed_same_path_fails_even_after_invalid(self):
        self.f.submit(raw=b'{"bad"')
        proposal = self.f.receive()
        self.f.persist(proposal)
        with self.assertRaisesRegex(ValueError, "collision|replay"):
            self.f.receive()

    def test_12_semantically_incomplete_not_promoted(self):
        def mutate(x):
            x["research_audit"]["completeness"] = "research_incomplete"
            x["research_audit"]["completion_basis"] = None
        self.f.submit(mutate)
        r = self.f.receive()
        self.assertEqual(r["status"], "research_incomplete")
        self.assertEqual(r["files"][r["receipt_path"]]["reason_code"], "research_not_assembly_ready")
        self.assertNotIn("dossier_research_accepted", r["receipt_path"])

    def test_13_semantic_exhaustion_not_canonical_attempt(self):
        self.f.submit(lambda x: x["research_audit"].update({
            "completeness": "semantic_exhausted", "completion_basis": None}))
        r = self.f.receive()
        self.assertEqual(r["status"], "semantic_exhausted")
        self.assertFalse(r["files"][r["receipt_path"]]["normal_first_pass_attempt_consumed"])

    def test_14_assembly_only_from_accepted_package(self):
        r = self.f.research_accepted()
        self.f.stage_plan(r)
        p = self.f.prepare()
        self.assertEqual(p["status"], "assigned")
        work = p["files"][p["assignment_path"]]
        self.assertEqual(work["accepted_research"]["research_package_sha256"],
                         r["files"][r["receipt_path"]]["research_package_sha256"])
        self.assertEqual(work["accepted_research_receipt_blob_sha"], r["receipt_blob_sha"])
        self.assertTrue(work["create_only"])

    def test_15_stale_assembly_plan_hash_fails(self):
        r = self.f.research_accepted()
        self.f.stage_plan(r)
        # A new GitHub plan cannot silently take over an existing frozen marker.
        self.f.plan["accepted_research_package_sha256"] = "0" * 64
        self.f.save(self.f.plan_path, self.f.plan)
        self.f.commit("tamper plan after marker")
        # frozen marker-parent plan remains the immutable authority
        self.assertEqual(self.f.prepare()["status"], "assigned")

    def test_16_assembly_plan_in_frozen_parent_wrong_hash_rejected(self):
        r = self.f.research_accepted()
        self.f.stage_plan(r)
        # Recreate an alternative frozen marker from a mismatched plan commit.
        self.f.plan["accepted_research_package_sha256"] = "0" * 64
        self.f.save(self.f.plan_path, self.f.plan)
        self.f.commit("GitHub plan corrupted")
        self.f.assembly_nonce = "c" * 32
        self.f.save(f"{ASSEMBLY_MARKER}/{self.f.assembly_nonce}.json", {
            "schema": "DOSSIER-ASSEMBLY-RUN-START-MARKER-V1",
            "schema_version": 1, "run_start_nonce": self.f.assembly_nonce,
        })
        self.f.assembly_marker = self.f.commit("new Stage B marker")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.f.prepare()

    def test_17_no_accepted_receipt_blocks_assembly(self):
        self.f.submit(raw=b'bad')
        rejected = self.f.receive()
        self.f.persist(rejected)
        self.f.stage_plan({"files": {
            "not_a_receipt": {"research_package_sha256": "9" * 64}
        }, "receipt_path": "not_a_receipt", "receipt_blob_sha": "0" * 40})
        with self.assertRaises(ValueError):
            self.f.prepare()

    def test_18_assembly_marker_kind_mismatch(self):
        r = self.f.research_accepted()
        self.f.stage_plan(r)
        with self.assertRaisesRegex(ValueError, "marker|namespace"):
            prepare_assembly(self.f.root, marker_commit=self.f.marker,
                             plan_path=self.f.plan_path)

    def test_19_duplicate_assembly_assignment_collision(self):
        r = self.f.research_accepted()
        self.f.stage_plan(r)
        proposal = self.f.prepare()
        self.f.persist(proposal)
        with self.assertRaisesRegex(ValueError, "collision"):
            self.f.prepare()

    def test_20_no_crossing_one_stage_transport(self):
        r = self.f.research_accepted()
        self.f.stage_plan(r)
        paths = [*r["files"], *self.f.prepare()["files"]]
        self.assertTrue(all(p.startswith("data/control/dossier_") for p in paths))
        self.assertFalse(any("taste_steam_review_dossiers" in p for p in paths))
        self.assertFalse(any(p.startswith("data/cache/") for p in paths))

    def test_21_release_year_frozen_in_assembly_receipt(self):
        r = self.f.research_accepted()
        self.f.stage_plan(r)
        a = self.f.prepare()["files"]
        assignment = next(value for key, value in a.items() if key.endswith("--assembly-prepared-fixture-0001.json"))
        self.assertEqual(assignment["accepted_research"]["accepted_identity"]["original_work_release_year"], 2020)
        self.assertEqual(assignment["original_research_assignment"]["appid"], "12345")

    def test_22_changed_frozen_work_ignored_after_marker(self):
        self.f.submit()
        self.f.index["pending_group_sequences"] = []
        self.f.save("data/production/pre_ai/taste_steam_review_dossier_worker_index.json", self.f.index)
        self.f.commit("Later mutable index state change")
        self.assertEqual(self.f.receive()["status"], "accepted_structural_evidence")

    def test_23_incorrect_original_anchor_cannot_be_substituted(self):
        self.f.submit()
        with self.assertRaises(ValueError):
            receive_research(self.f.root, marker_commit=self.f.marker[:-1] + "0",
                             prepared_work_path=self.f.p_path,
                             package_commit=self.f.package_commit)

    def test_24_assembly_wrong_predeclared_id_rejected(self):
        r = self.f.research_accepted()
        self.f.stage_plan(r)
        with self.assertRaisesRegex(ValueError, "plan path"):
            prepare_assembly(self.f.root, marker_commit=self.f.assembly_marker,
                             plan_path=self.f.plan_path.replace(self.f.a["appid"], "77777"))

    def test_25_not_authorized_recovery_after_rejection(self):
        self.f.submit(lambda x: x["research_audit"].update({
            "completeness": "research_incomplete", "completion_basis": None}))
        proposal = self.f.receive()
        state = proposal["files"][receipt_paths(self.f.a)["state"]]
        self.assertEqual(state["assembly_status"], "not_authorized")
        self.assertFalse(state["retry_authorized"])


if __name__ == "__main__":
    unittest.main()
