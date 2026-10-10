#!/usr/bin/env python3
"""Cross-helper, offline-only Research -> Assembly compatibility proof.

Every Git write is confined to a disposable TemporaryDirectory.  Research
and Assembly are the actual merged inactive helper APIs; no semantic network
calls, canonical repository writes, worker scheduling or production changes.
"""
import copy
import hashlib
import json
import tempfile
import unittest

from jsonschema import Draft202012Validator

from dossier_two_stage_assembly_semantic_worker import (
    frozen_assembly_traversal, offline_assembly_candidate,
)
from dossier_two_stage_async_buffer import frozen_buffer, inactive_gate
from dossier_two_stage_contract_guard import CONFIG, canonical_sha256
from dossier_two_stage_research_worker import (
    ROOT, PROMPT_PATH, frozen_research_batch,
    inspect_existing_research_transport, prepare_research_transport,
)
from dossier_two_stage_staging import (
    blob, file_at, marker_context, receipt_paths, strict_json,
)
from test_dossier_two_stage_assembly_semantic_worker import diagnosis
from test_dossier_two_stage_async_buffer import AsyncFixture
import test_dossier_two_stage_research_worker as research_tests


class CrossHelperCompatibilityTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.x = AsyncFixture(temp.name)
        # Reuse the existing Research suite's GitHub-fixture expansion and
        # exact worker prompt pinning, not its synthetic package submission.
        self.r = research_tests.ResearchWorkerTests("test_01_inactive_and_exact_prompt_parent_identity")
        self.r.x = self.x

    def authorize(self, twelve=False):
        if twelve:
            buffer = self.r.extend_twelve()
            self.r.pin(buffer=buffer["path"])
            self.r.paths = list(self.x.paths)
        else:
            self.r.pin()
        self.x.preauthorize_assembly(indexes=tuple(range(len(self.x.docs))))
        return self.x

    def research(self, i):
        x = self.x
        planned = prepare_research_transport(
            x.f.root, marker_commit=self.r.marker, buffer_path=self.r.buffer,
            work_path=self.r.paths[i], document=copy.deepcopy(x.docs[i]))
        self.assertEqual(planned["status"], "ready_for_create_only_submission")
        self.assertFalse(planned["canonical_acceptance"])
        path = x.f.root / planned["output_path"]
        self.assertFalse(path.exists(), "Research destination must be create-only")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(planned["transport_bytes"])
        commit = x.f.commit(f"Immutable Research candidate {i}, no GitHub acceptance")
        submitted = inspect_existing_research_transport(
            x.f.root, marker_commit=self.r.marker, buffer_path=self.r.buffer,
            work_path=self.r.paths[i], expected_bytes=planned["transport_bytes"])
        self.assertEqual(submitted["status"], "submitted_unaccepted")
        self.assertEqual(submitted["research_package_git_commit"], commit)
        self.assertEqual(submitted["research_package_blob_sha"],
                         planned["expected_git_blob_sha"])
        self.assertEqual(submitted["research_package_raw_sha256"],
                         planned["expected_raw_sha256"])
        self.assertEqual(submitted["research_package_sha256"],
                         planned["expected_canonical_sha256"])
        self.assertFalse((x.f.root / receipt_paths(
            x.docs[i]["assignment"])["accepted"]).exists())
        return commit, submitted

    def traversal(self, submissions):
        x = self.x
        return frozen_assembly_traversal(
            x.f.root, marker_commit=x.amarker,
            buffer_path=x.abuffer["path"], submitted_commits=submissions)

    def candidate(self, i, commit):
        x = self.x
        return offline_assembly_candidate(
            x.f.root, marker_commit=x.amarker, buffer_path=x.abuffer["path"],
            work_path=x.apaths[i], research_package_commit=commit,
            outcome="unresolved_semantic_gap", payload=diagnosis(),
            supplemental_operations=[])

    def test_01_actual_helpers_twelve_items_four_atomic_groups_before_any_receipts(self):
        x = self.authorize(twelve=True)
        rb = frozen_research_batch(
            x.f.root, marker_commit=self.r.marker, buffer_path=self.r.buffer)
        ab = frozen_buffer(
            x.f.root, marker_commit=x.amarker,
            buffer_path=x.abuffer["path"], phase="assembly")
        self.assertEqual(len(rb["items"]), len(ab["items"]))
        self.assertEqual(len(ab["items"]), 12)
        self.assertEqual([(v["group_sequence"], v["item_index"]) for v in ab["items"]],
                         [(g, j) for g in range(1, 5) for j in range(3)])
        self.assertEqual(rb["marker_parent"],
                         x.f.run("rev-parse", self.r.marker + "^"))
        self.assertEqual(rb["prompt_blob_sha"],
                         blob(x.f.root, rb["marker_parent"], PROMPT_PATH))
        self.assertEqual(rb["prompt_sha256"], hashlib.sha256(
            (ROOT / PROMPT_PATH).read_bytes()).hexdigest())
        self.assertEqual(rb["buffer_blob_sha"],
                         blob(x.f.root, rb["marker_parent"], self.r.buffer))
        self.assertEqual(ab["buffer_id"], x.abuffer["manifest"]["buffer_id"])
        self.assertEqual(marker_context(x.f.root, x.amarker, "assembly")[0],
                         x.f.run("rev-parse", x.amarker + "^"))

        submissions = {}
        for i in range(12):
            research_commit, evidence = self.research(i)
            submissions[x.apaths[i]] = research_commit
            self.assertEqual(evidence["research_package_sha256"],
                             canonical_sha256(strict_json(file_at(
                                 x.f.root, research_commit, evidence["output_path"]))))
        ready = self.traversal(dict(reversed(list(submissions.items()))))
        self.assertEqual([v["work_path"] for v in ready], x.apaths)
        self.assertEqual([v["status"] for v in ready], ["ready"] * 12)
        self.assertTrue(all(v["attempt_consumed"] is False for v in ready))

        schema = json.loads((CONFIG / "dossier_async_assembly_result_v1.schema.json")
                            .read_text("utf-8"))
        validator = Draft202012Validator(schema)
        for i, row in enumerate(ready):
            path, doc = self.candidate(i, submissions[x.apaths[i]])
            self.assertEqual(path, row["work"]["output_path"])
            self.assertEqual(doc["research_transport"], row["work"]["research_transport"])
            self.assertEqual(doc["original_research_assignment"],
                             x.docs[i]["assignment"])
            self.assertEqual(doc["assembly_marker_anchor_commit"], x.amarker)
            self.assertEqual(doc["assembly_contract_sha256"],
                             row["work"]["assembly_contract_sha256"])
            self.assertEqual(doc["assembly_prompt_sha256"],
                             row["work"]["assembly_prompt_sha256"])
            self.assertEqual(doc["canonical_dossier_target"]["schema"],
                             "TASTE-STEAM-REVIEW-DOSSIER-V2")
            self.assertFalse(list(validator.iter_errors(doc)))
            self.assertFalse(doc["canonical_acceptance"])
            self.assertTrue(doc["staged_only"])
            x.f.save(path, doc)
            assembly_commit = x.f.commit(f"Assembly candidate {i}, still no Research receipt")
            verdict = x.inspect(i, assembly_commit)
            self.assertEqual(verdict["status"],
                             "typed_assembly_item_pending_github_classification")
            self.assertFalse(verdict["canonical_dossier_accepted"])
            self.assertFalse(verdict["deep_ready"])
            # Original submitted Research commit/raw/blob/sha are immutable
            # across both helpers and the independent Assembly submissions.
            ref = doc["research_transport"]
            original = file_at(x.f.root, submissions[x.apaths[i]],
                               ref["research_package_path"])
            self.assertEqual(ref["research_package_raw_sha256"],
                             hashlib.sha256(original).hexdigest())
            self.assertEqual(ref["research_package_blob_sha"],
                             blob(x.f.root, submissions[x.apaths[i]],
                                  ref["research_package_path"]))
            self.assertEqual(ref["research_package_sha256"],
                             canonical_sha256(strict_json(original)))
            self.assertEqual(ref["research_prepared_work_blob_sha"],
                             blob(x.f.root, rb["marker_parent"], self.r.paths[i]))
            self.assertEqual(ref["assembly_plan_blob_sha"],
                             blob(x.f.root, x.amarker + "^", x.apaths[i]))
            self.assertEqual(ref["research_marker_anchor_commit"], self.r.marker)
            self.assertFalse((x.f.root / receipt_paths(
                x.docs[i]["assignment"])["accepted"]).exists())

    def test_02_missing_invalid_and_late_rejected_A_never_block_B_C(self):
        x = self.authorize()
        b, _ = self.research(1)
        c, _ = self.research(2)
        status = self.traversal({x.apaths[2]: c, x.apaths[1]: b})
        self.assertEqual([r["status"] for r in status],
                         ["research_not_submitted", "ready", "ready"])
        self.assertTrue(all(r["attempt_consumed"] is False for r in status))
        sibling_commits = {}
        for i, commit in ((1, b), (2, c)):
            path, doc = self.candidate(i, commit)
            x.f.save(path, doc)
            sibling_commits[i] = x.f.commit(f"Assembly sibling {i} ahead of A")
            self.assertEqual(x.inspect(i, sibling_commits[i])["status"],
                             "typed_assembly_item_pending_github_classification")
        # Invalid Research semantics are NOT an Assembly timing barrier;
        # eventual GitHub strict validation quarantines only its item.
        a = x.research_submit(0, tamper=lambda d: d["findings"][0].update(
            support_feedback_refs=["rfeedback-invalid"]))
        path, doc = self.candidate(0, a)
        x.f.save(path, doc)
        late = x.f.commit("Late invalid A before eventual GitHub rejection")
        self.assertEqual(x.inspect(0, late)["status"],
                         "research_rejected_item_chain_quarantined")
        self.assertFalse(x.inspect(0, late)["deep_ready"])
        self.assertEqual(x.inspect(1, sibling_commits[1])["status"],
                         "typed_assembly_item_pending_github_classification")
        self.assertEqual(x.inspect(2, sibling_commits[2])["status"],
                         "typed_assembly_item_pending_github_classification")

    def test_03_wrong_work_wrong_commit_and_unapproved_scope_fail_closed(self):
        x = self.authorize()
        a, _ = self.research(0)
        c, _ = self.research(2)
        decisions = self.traversal({x.apaths[0]: a, x.apaths[1]: a, x.apaths[2]: c})
        self.assertEqual([r["status"] for r in decisions],
                         ["ready", "research_transport_invalid", "ready"])
        self.assertFalse(decisions[1]["attempt_consumed"])
        with self.assertRaises(ValueError):
            self.candidate(1, a)
        with self.assertRaises(ValueError):
            self.traversal({"unapproved/new/assembly-plan.json": a})
        with self.assertRaises(ValueError):
            prepare_research_transport(
                x.f.root, marker_commit=self.r.marker, buffer_path=self.r.buffer,
                work_path="unapproved/research-work.json", document=x.docs[0])
        # Later moving HEAD cannot change either frozen marker parent's scope.
        x.f.save("data/irrelevant-main-movement.json", {"never_authority": True})
        x.f.commit("Simulate main moving after frozen authorizations")
        self.assertEqual(len(frozen_research_batch(
            x.f.root, marker_commit=self.r.marker,
            buffer_path=self.r.buffer)["items"]), 3)
        self.assertEqual([r["work_path"] for r in self.traversal(
            {x.apaths[2]: c, x.apaths[0]: a})], x.apaths)

    def test_04_duplicate_tampered_transport_and_forged_acceptance_fail_closed(self):
        x = self.authorize()
        a, _ = self.research(0)
        self.assertEqual(prepare_research_transport(
            x.f.root, marker_commit=self.r.marker, buffer_path=self.r.buffer,
            work_path=self.r.paths[0], document=x.docs[0])["status"],
            "submitted_unaccepted")
        mutated = copy.deepcopy(x.docs[0])
        mutated["research_audit"]["completeness"] = "research_incomplete"
        with self.assertRaises(ValueError):
            prepare_research_transport(
                x.f.root, marker_commit=self.r.marker, buffer_path=self.r.buffer,
                work_path=self.r.paths[0], document=mutated)
        path, doc = self.candidate(0, a)
        forged = copy.deepcopy(doc)
        forged["canonical_acceptance"] = True
        x.f.save(path, forged)
        forged_commit = x.f.commit("Forged canonical acceptance is invalid")
        with self.assertRaises(ValueError):
            x.inspect(0, forged_commit)
        with self.assertRaises(ValueError):
            self.candidate(0, a)  # create-only collision
        # Research worker refuses changed original HEAD bytes even if the
        # older immutable package commit is available to an Assembly reader.
        rpath = receipt_paths(x.docs[0]["assignment"])["candidate"]
        x.f.save(rpath, {"schema": "tampered"})
        x.f.commit("Illegal overwrite of Research transport")
        with self.assertRaises(ValueError):
            inspect_existing_research_transport(
                x.f.root, marker_commit=self.r.marker, buffer_path=self.r.buffer,
                work_path=self.r.paths[0])
        self.assertIs(inactive_gate()["active"], False)
        self.assertIs(inactive_gate()["executable_in_production"], False)


if __name__ == "__main__":
    unittest.main()
