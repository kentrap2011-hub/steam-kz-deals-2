#!/usr/bin/env python3
"""Offline Git fixture proof of asynchronous Dossier P1/P2, never production."""
import copy
import json
import tempfile
import unittest

from dossier_two_stage_contract_guard import canonical_sha256
from dossier_two_stage_staging import (
    RESEARCH_MARKER, ASSEMBLY_MARKER, receipt_paths, prepared_path, blob,
)
from dossier_two_stage_async_buffer import (
    inactive_gate, make_buffer, frozen_buffer, receive_buffered_research,
    provisional_assembly_work, inspect_buffered_assembly_candidate,
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
        d = copy.deepcopy(self.docs[index])
        if tamper:
            tamper(d)
        self.f.save(receipt_paths(self.docs[index]["assignment"])["candidate"], d)
        return self.f.commit(f"Research {index} submitted, no GH ack")

    def research_receive(self, i, commit):
        return receive_buffered_research(self.f.root, marker_commit=self.f.marker,
                                         buffer_path=self.rbuffer["path"],
                                         work_path=self.paths[i], package_commit=commit)

    def preauthorize_assembly(self, indexes=(0, 1, 2)):
        paths = []
        for i in indexes:
            a = self.docs[i]["assignment"]
            plan = {
                "schema": "DOSSIER-ASSEMBLY-GITHUB-PREAUTH-PLAN-V2",
                "schema_version": 2,
                "research_assignment_id": a["assignment_id"],
                "research_prepared_work_path": self.paths[i],
                "research_prepared_work_blob_sha": blob(
                    self.f.root, self.f.run("rev-parse", "HEAD"), self.paths[i]),
                "assembly_assignment_id": f"assembly-prepared-fixture-000{i+1}",
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
            path = receipt_paths(a)["assembly_plan"]
            self.f.save(path, plan)
            paths.append(path)
        source = self.f.commit("GitHub preauthorizes Assembly; no Research receipt")
        self.abuffer = make_buffer(self.f.root, source_commit=source, phase="assembly",
                                   ordered_work_paths=paths)
        self.f.save(self.abuffer["path"], self.abuffer["manifest"])
        self.f.commit("GitHub freezes Assembly preauthorization")
        nonce = "e" * 32
        self.f.save(f"{ASSEMBLY_MARKER}/{nonce}.json", {
            "schema": "DOSSIER-ASSEMBLY-RUN-START-MARKER-V1",
            "schema_version": 1, "run_start_nonce": nonce,
        })
        self.amarker = self.f.commit("Freeze exact future Assembly buffer")
        self.apaths = paths

    def assembly_work(self, i, research_commit):
        return provisional_assembly_work(
            self.f.root, marker_commit=self.amarker, buffer_path=self.abuffer["path"],
            work_path=self.apaths[i], package_commit=research_commit)

    def assembly_submit(self, i, research_commit, mutate=None):
        work = self.assembly_work(i, research_commit)
        doc = {
            "schema": "DOSSIER-ASYNC-ASSEMBLY-RESULT-V1",
            "schema_version": 1,
            "assembly_assignment_id": work["assembly_assignment_id"],
            "original_research_assignment": copy.deepcopy(work["original_research_assignment"]),
            "research_transport": copy.deepcopy(work["research_transport"]),
            "assembly_marker_anchor_commit": work["assembly_marker_anchor_commit"],
            "assembly_marker_nonce": work["assembly_marker_nonce"],
            "assembly_contract_sha256": work["assembly_contract_sha256"],
            "assembly_prompt_sha256": work["assembly_prompt_sha256"],
            "canonical_dossier_target": copy.deepcopy(work["canonical_dossier_target"]),
            "output_path": work["output_path"], "outcome": "unresolved_semantic_gap",
            "payload": {
                "status": "unresolved_semantic_gap", "gap_id": None, "source_ref": None,
                "field_or_dimension": None, "safe_diagnostic": "No additional verified evidence.",
                "requires_github_classification": True,
                "normal_first_pass_attempt_consumed": False,
            },
            "supplemental_operations": [],
            "staged_only": True, "canonical_acceptance": False,
        }
        if mutate:
            mutate(doc)
        self.f.save(work["output_path"], doc)
        return self.f.commit(f"Assembly item {i} submitted without GH ack")

    def inspect(self, i, commit):
        return inspect_buffered_assembly_candidate(
            self.f.root, marker_commit=self.amarker, buffer_path=self.abuffer["path"],
            work_path=self.apaths[i], result_commit=commit)


class FullyAsyncBufferTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.x = AsyncFixture(t.name)

    def test_01_gates_current_one_stage_remains_authority(self):
        cfg = inactive_gate()
        self.assertFalse(cfg["active"])
        self.assertFalse(cfg["authoritative"])
        self.assertFalse(cfg["executable_in_production"])
        self.assertFalse(cfg["semantic_workers_implemented"])
        self.assertFalse(cfg["capacity"]["semantic_liveness_depends_on_open_slots"])
        self.assertEqual(self.x.f.descriptor["schema"], "TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1")

    def test_02_research_A_unaccepted_does_not_block_B_C(self):
        x = self.x
        x.research_submit(0)
        self.assertEqual(len(frozen_buffer(x.f.root, marker_commit=x.f.marker,
                             buffer_path=x.rbuffer["path"], phase="research")["items"]), 3)
        for i in (1, 2):
            self.assertEqual(x.research_receive(i, x.research_submit(i))["status"],
                             "accepted_structural_evidence")

    def test_03_Assembly_A_direct_submitted_Research_without_receipt(self):
        x = self.x
        x.preauthorize_assembly()
        research_commit = x.research_submit(0)
        work = x.assembly_work(0, research_commit)
        self.assertEqual(work["research_transport"]["research_package_git_commit"], research_commit)
        self.assertFalse(work["canonical_dossier_accepted"])
        self.assertEqual(x.inspect(0, x.assembly_submit(0, research_commit))["status"],
                         "typed_assembly_item_pending_github_classification")

    def test_04_research_A_later_rejected_assembly_A_is_quarantined_B_C_continue(self):
        x = self.x
        x.preauthorize_assembly()
        bad = x.research_submit(0, tamper=lambda d: d["findings"][0].update(
            support_feedback_refs=["rfeedback-999"]))
        candidate = x.assembly_submit(0, bad)
        self.assertEqual(x.inspect(0, candidate)["status"],
                         "research_rejected_item_chain_quarantined")
        for i in (1, 2):
            r = x.research_submit(i)
            self.assertEqual(x.inspect(i, x.assembly_submit(i, r))["status"],
                             "typed_assembly_item_pending_github_classification")

    def test_05_assembly_A_invalid_B_C_unaffected(self):
        x = self.x
        x.preauthorize_assembly()
        ra = x.research_submit(0)
        bad = x.assembly_submit(0, ra, mutate=lambda d: d.update(assembly_assignment_id="wrong"))
        with self.assertRaises(ValueError):
            x.inspect(0, bad)
        for i in (1, 2):
            r = x.research_submit(i)
            self.assertFalse(x.inspect(i, x.assembly_submit(i, r))["canonical_dossier_accepted"])

    def test_06_no_unresolved_slots_ack_check_or_daily_quota(self):
        x = self.x
        self.assertEqual(x.rbuffer["reserved_count"], 3)
        a = make_buffer(x.f.root, source_commit=x.research_source, phase="research",
                        ordered_work_paths=x.paths)
        self.assertEqual(a, x.rbuffer)
        # Limits can refuse only NEW GH preauthorization, not frozen traversal.
        with self.assertRaises(ValueError):
            make_buffer(x.f.root, source_commit=x.research_source, phase="research",
                        ordered_work_paths=x.paths, new_authorization_limit=2)
        frozen = frozen_buffer(x.f.root, marker_commit=x.f.marker,
                               buffer_path=x.rbuffer["path"], phase="research")
        self.assertEqual(len(frozen["items"]), 3)

    def test_07_exact_raw_blob_replay_and_tamper_fail_closed(self):
        x = self.x
        x.preauthorize_assembly()
        r = x.research_submit(0)
        result = x.assembly_submit(0, r)
        self.assertFalse(x.inspect(0, result)["canonical_dossier_accepted"])
        path = x.assembly_work(0, r)["output_path"]
        x.f.save(path, {"schema": "overwritten"})
        overwrite = x.f.commit("Mutate submitted assembly bytes")
        with self.assertRaises(ValueError):
            x.inspect(0, overwrite)
        with self.assertRaises(ValueError):
            x.inspect(1, result)

    def test_08_wrong_package_identity_cannot_be_consumed(self):
        x = self.x
        x.preauthorize_assembly()
        wrong = x.research_submit(0)
        with self.assertRaises(ValueError):
            x.assembly_work(1, wrong)

    def test_09_frozen_authority_survives_later_main_movement(self):
        x = self.x
        x.preauthorize_assembly()
        x.f.save(x.rbuffer["path"], {"schema": "tamper"})
        x.f.commit("Later unrelated Git movement")
        self.assertEqual(len(frozen_buffer(x.f.root, marker_commit=x.f.marker,
                             buffer_path=x.rbuffer["path"], phase="research")["items"]), 3)

    def test_10_no_worker_scope_expansion_or_recovery(self):
        x = self.x
        x.preauthorize_assembly(indexes=(0,))
        with self.assertRaises(ValueError):
            provisional_assembly_work(
                x.f.root, marker_commit=x.amarker, buffer_path=x.abuffer["path"],
                work_path=receipt_paths(x.docs[1]["assignment"])["assembly_plan"],
                package_commit=x.f.marker)
        with self.assertRaises(ValueError):
            make_buffer(x.f.root, source_commit=x.research_source, phase="research",
                        ordered_work_paths=list(reversed(x.paths)))

    def test_11_Assembly_B_C_carry_independent_immutable_Research_refs(self):
        x = self.x
        x.preauthorize_assembly()
        a = x.research_submit(0)
        x.assembly_submit(0, a)
        b = x.research_submit(1)
        c = x.research_submit(2)
        for i, r in ((1, b), (2, c)):
            self.assertEqual(x.assembly_work(i, r)["research_transport"]["research_package_git_commit"], r)
            self.assertFalse(x.inspect(i, x.assembly_submit(i, r))["deep_ready"])


if __name__ == "__main__":
    unittest.main()
