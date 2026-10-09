#!/usr/bin/env python3
"""Offline Git fixture proof of asynchronous Dossier P1/P2, never production."""
import copy
import json
import tempfile
import unittest

from dossier_two_stage_contract_guard import canonical_sha256
from dossier_two_stage_staging import (
    RESEARCH_MARKER, ASSEMBLY_MARKER, receipt_paths, prepared_path,
)
from dossier_two_stage_async_buffer import (
    CAPACITY, inactive_gate, make_buffer, frozen_buffer,
    receive_buffered_research, stage_assembly_buffer, staged_assembly_member,
    inspect_buffered_assembly_candidate,
)
from test_dossier_two_stage_staging import GitFixture
from test_dossier_two_stage_contract_schemas import result_fixture


class AsyncFixture:
    """One exact existing Dossier group, three separately authorized games."""
    def __init__(self, root):
        self.f = GitFixture(root)
        self.docs = []
        items = [
            {"appid": "12345", "title": "Fixture Game"},
            {"appid": "23456", "title": "Fixture Sequel"},
            {"appid": "34567", "title": "Fixture Third"},
        ]
        desc = self.f.descriptor
        fields = {
            "snapshot_id": self.f.a["snapshot_id"],
            "prepared_required_sha256": self.f.a["prepared_required_sha256"],
            "sequence": 1, "start_index": 0, "end_index_exclusive": 3,
            "appids": [i["appid"] for i in items],
            "items_sha256": canonical_sha256(items),
            "scope_source": self.f.a["scope_source"],
            "source_queue_sha256": self.f.a["source_queue_sha256"],
        }
        desc.update(fields)
        desc["items"] = items
        desc["group_sha256"] = canonical_sha256(fields)
        self.paths = []
        for i, item in enumerate(items):
            d = copy.deepcopy(self.f.doc)
            a = d["assignment"]
            a.update({
                "assignment_id": f"research-fixture-000{i+1}",
                "item_index": i, "appid": item["appid"], "title": item["title"],
                "items_sha256": fields["items_sha256"],
                "group_sha256": desc["group_sha256"],
            })
            d["identity"]["resolved_title"] = item["title"]
            d["identity"]["corroborators"][0]["value"] = item["appid"]
            for source in d["sources"]:
                for key in ("normalized_locator", "physical_source_identity"):
                    source[key] = source[key].replace("12345", item["appid"])
                source["locator"]["url"] = source["locator"]["url"].replace("12345", item["appid"])
                source["exact_product_binding"].update({
                    "appid": item["appid"], "title": item["title"],
                })
            path = prepared_path(a)
            self.f.save(path, {k: v for k, v in a.items()
                               if k not in ("research_marker_anchor_commit", "research_marker_nonce")})
            self.paths.append(path)
            self.docs.append(d)
        self.f.save("data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
                    f"{self.f.a['snapshot_id']}/g000001.json", desc)
        frozen = self.f.commit("Prepare all three exact GitHub assignments")
        self.research_source = frozen
        self.rbuffer = make_buffer(self.f.root, source_commit=frozen, phase="research",
                                   ordered_work_paths=self.paths)
        self.f.save(self.rbuffer["path"], self.rbuffer["manifest"])
        self.f.commit("Publish immutable three-item Research buffer")
        self.f.nonce = "c" * 32
        self.f.save(f"{RESEARCH_MARKER}/{self.f.nonce}.json", {
            "schema": "DOSSIER-RESEARCH-RUN-START-MARKER-V1",
            "schema_version": 1, "run_start_nonce": self.f.nonce,
        })
        self.f.marker = self.f.commit("Freeze Research buffer in marker parent")
        for d in self.docs:
            d["assignment"]["research_marker_anchor_commit"] = self.f.marker
            d["assignment"]["research_marker_nonce"] = self.f.nonce
        self.f.doc = self.docs[0]
        self.f.a = self.docs[0]["assignment"]
        self.f.source_path = receipt_paths(self.f.a)["candidate"]
        self.accepted = {}

    def research_submit(self, index, *, tamper=None):
        doc = copy.deepcopy(self.docs[index])
        if tamper:
            tamper(doc)
        path = receipt_paths(self.docs[index]["assignment"])["candidate"]
        self.f.save(path, doc)
        commit = self.f.commit(f"Submit Research item {index} without prior ack")
        return commit

    def research_receive(self, index, commit, persist=False):
        proposal = receive_buffered_research(
            self.f.root, marker_commit=self.f.marker, buffer_path=self.rbuffer["path"],
            work_path=self.paths[index], package_commit=commit)
        if persist:
            self.f.persist(proposal)
            if proposal["status"] == "accepted_structural_evidence":
                self.accepted[index] = proposal
        return proposal

    def accept_research(self, index):
        return self.research_receive(index, self.research_submit(index), persist=True)

    def make_assembly(self, indexes=(0, 1, 2)):
        for i in indexes:
            if i not in self.accepted:
                self.accept_research(i)
        plans = []
        for i in indexes:
            d = self.docs[i]
            a = d["assignment"]
            receipt = self.accepted[i]["files"][self.accepted[i]["receipt_path"]]
            plan = {
                "schema": "DOSSIER-ASSEMBLY-GITHUB-PLAN-V1", "schema_version": 1,
                "research_assignment_id": a["assignment_id"],
                "assembly_assignment_id": f"assembly-prepared-fixture-000{i+1}",
                "accepted_research_package_sha256": receipt["research_package_sha256"],
                "accepted_research_receipt_blob_sha": self.accepted[i]["receipt_blob_sha"],
                "assembly_contract_sha256": "9" * 64,
                "assembly_prompt_sha256": "8" * 64,
                "assembly_prompt_revision": "fixture-inactive",
                "canonical_dossier_target": {
                    "schema": "TASTE-STEAM-REVIEW-DOSSIER-V2", "schema_version": 2,
                    "worker_schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2",
                    "worker_schema_version": 2,
                    "web_evidence_contract": "TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2",
                    "web_evidence_contract_version": 2,
                    "canonical_worker_binding_sha256": canonical_sha256(
                        a["web_evidence_contract_binding"]),
                },
            }
            p = receipt_paths(a)["assembly_plan"]
            self.f.save(p, plan)
            plans.append(p)
        source = self.f.commit("GitHub plans Assembly from accepted Research only")
        self.abuffer = make_buffer(self.f.root, source_commit=source, phase="assembly",
                                   ordered_work_paths=plans)
        self.f.save(self.abuffer["path"], self.abuffer["manifest"])
        self.f.commit("Publish immutable Assembly buffer")
        nonce = "e" * 32
        self.f.save(f"{ASSEMBLY_MARKER}/{nonce}.json", {
            "schema": "DOSSIER-ASSEMBLY-RUN-START-MARKER-V1",
            "schema_version": 1, "run_start_nonce": nonce,
        })
        self.amarker = self.f.commit("Freeze accepted Research Assembly buffer")
        self.apaths = plans
        stage = stage_assembly_buffer(self.f.root, marker_commit=self.amarker,
                                      buffer_path=self.abuffer["path"])
        self.stage = stage
        self.stage_commit = self.f.persist(stage)

    def member(self, i):
        return staged_assembly_member(self.f.root, marker_commit=self.amarker,
                                      buffer_path=self.abuffer["path"],
                                      work_path=self.apaths[i], staging_commit=self.stage_commit)

    def assembly_submit(self, i, mutate=None):
        work = self.member(i)
        doc = result_fixture(work)
        if mutate:
            mutate(doc)
        self.f.save(work["output_path"], doc)
        return self.f.commit(f"Submit Assembly item {i}")

    def assembly_inspect(self, i, result_commit):
        return inspect_buffered_assembly_candidate(
            self.f.root, marker_commit=self.amarker, buffer_path=self.abuffer["path"],
            work_path=self.apaths[i], staging_commit=self.stage_commit,
            result_commit=result_commit)


class AsyncBufferTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.x = AsyncFixture(temp.name)

    def test_01_inactive_authority_and_real_three_game_boundary_unchanged(self):
        cfg = inactive_gate()
        self.assertFalse(cfg["active"])
        self.assertFalse(cfg["authoritative"])
        self.assertFalse(cfg["executable_in_production"])
        self.assertEqual(CAPACITY, 8)
        self.assertEqual(len(self.x.f.descriptor["items"]), 3)
        self.assertEqual(self.x.rbuffer["reserved_count"], 3)

    def test_02_research_B_and_C_pre_authorized_after_A_submission_without_receipt(self):
        x = self.x
        x.research_submit(0)
        doc = frozen_buffer(x.f.root, marker_commit=x.f.marker,
                            buffer_path=x.rbuffer["path"], phase="research")
        self.assertEqual(len(doc["items"]), 3)
        self.assertEqual(x.research_receive(1, x.research_submit(1))["status"],
                         "accepted_structural_evidence")
        self.assertEqual(x.research_receive(2, x.research_submit(2))["status"],
                         "accepted_structural_evidence")

    def test_03_research_rejected_A_does_not_revoke_B_C(self):
        x = self.x
        a_commit = x.research_submit(0, tamper=lambda d: d["assignment"].update(appid="99999"))
        self.assertEqual(x.research_receive(0, a_commit, persist=True)["status"],
                         "rejected_invalid")
        for i in (1, 2):
            self.assertEqual(x.research_receive(i, x.research_submit(i))["status"],
                             "accepted_structural_evidence")

    def test_04_assembly_B_C_authorized_after_A_submission_without_final_receipt(self):
        x = self.x
        x.make_assembly()
        x.assembly_submit(0)
        self.assertEqual(x.member(1)["assembly_assignment_id"], "assembly-prepared-fixture-0002")
        self.assertEqual(x.member(2)["assembly_assignment_id"], "assembly-prepared-fixture-0003")
        self.assertFalse(x.stage["canonical_acceptance"])
        self.assertEqual(x.assembly_inspect(1, x.assembly_submit(1))["canonical_dossier_accepted"], False)

    def test_05_invalid_assembly_A_cannot_revoke_unrelated_B(self):
        x = self.x
        x.make_assembly()
        invalid_commit = x.assembly_submit(0, mutate=lambda d: d.update(assembly_assignment_id="wrong"))
        with self.assertRaises(ValueError):
            x.assembly_inspect(0, invalid_commit)
        valid = x.assembly_submit(1)
        self.assertIn("pending_github_final_strict_ingest",
                      x.assembly_inspect(1, valid)["status"])

    def test_06_accepted_Research_A_feeds_Assembly_while_later_Research_B_C_continue(self):
        x = self.x
        x.accept_research(0)
        x.make_assembly(indexes=(0,))
        self.assertEqual(x.member(0)["original_research_assignment"]["appid"], "12345")
        for i in (1, 2):
            self.assertEqual(x.research_receive(i, x.research_submit(i))["status"],
                             "accepted_structural_evidence")

    def test_07_capacity_backpressure_is_deterministic_and_not_daily_quota(self):
        x = self.x
        source = x.research_source
        for occupied, expected in ((0, 3), (6, 2), (7, 1), (8, 0)):
            a = make_buffer(x.f.root, source_commit=source, phase="research",
                            ordered_work_paths=x.paths, occupied_slots=occupied)
            b = make_buffer(x.f.root, source_commit=source, phase="research",
                            ordered_work_paths=x.paths, occupied_slots=occupied)
            self.assertEqual(a, b)
            self.assertEqual(0 if a is None else a["reserved_count"], expected)

    def test_08_no_self_assigned_work_or_retries_and_duplicate_paths(self):
        x = self.x
        with self.assertRaises(ValueError):
            make_buffer(x.f.root, source_commit=x.f.marker, phase="research",
                        ordered_work_paths=[x.paths[0], x.paths[0]])
        with self.assertRaises(ValueError):
            make_buffer(x.f.root, source_commit=x.f.marker, phase="research",
                        ordered_work_paths=list(reversed(x.paths)))
        with self.assertRaises(ValueError):
            receive_buffered_research(x.f.root, marker_commit=x.f.marker,
                                     buffer_path=x.rbuffer["path"],
                                     work_path="data/control/dossier_research_assignments/forged.json",
                                     package_commit=x.f.marker)

    def test_09_stale_tampered_frozen_buffer_fails_closed(self):
        x = self.x
        x.f.save(x.rbuffer["path"], {**x.rbuffer["manifest"], "capacity": 100})
        x.f.commit("Tamper mutable later HEAD, original marker-parent unchanged")
        self.assertEqual(len(frozen_buffer(x.f.root, marker_commit=x.f.marker,
                            buffer_path=x.rbuffer["path"], phase="research")["items"]), 3)
        with self.assertRaises(ValueError):
            frozen_buffer(x.f.root, marker_commit=x.f.marker,
                          buffer_path=x.rbuffer["path"], phase="assembly")

    def test_10_stale_or_duplicate_assembly_candidates_fail_closed(self):
        x = self.x
        x.make_assembly()
        good = x.assembly_submit(0)
        self.assertFalse(x.assembly_inspect(0, good)["canonical_dossier_accepted"])
        path = x.member(0)["output_path"]
        x.f.save(path, {"schema": "overwritten"})
        second = x.f.commit("Attempt duplicate overwrite")
        with self.assertRaises(ValueError):
            x.assembly_inspect(0, second)
        with self.assertRaises(ValueError):
            x.assembly_inspect(1, good)

    def test_11_rejected_Research_is_not_assembly_eligible(self):
        x = self.x
        a = x.research_submit(0, tamper=lambda d: d.update(schema="untrusted"))
        x.research_receive(0, a, persist=True)
        # Assembly candidate planning is GitHub-only and requires an accepted receipt.
        with self.assertRaises(ValueError):
            make_buffer(x.f.root, source_commit=x.f.run("rev-parse", "HEAD"),
                        phase="assembly",
                        ordered_work_paths=[receipt_paths(x.docs[0]["assignment"])["assembly_plan"]])


if __name__ == "__main__":
    unittest.main()
