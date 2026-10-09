#!/usr/bin/env python3
"""INACTIVE Assembly semantic boundary: disposable Git, no live semantic calls."""
import copy
import hashlib
import tempfile
import unittest

from dossier_two_stage_async_buffer import inactive_gate
from dossier_two_stage_assembly_semantic_worker import (
    inactive_assembly_gate, frozen_assembly_traversal, offline_assembly_candidate,
)
from dossier_two_stage_contract_guard import canonical_sha256
from dossier_two_stage_staging import blob, file_at
from test_dossier_two_stage_async_buffer import AsyncFixture


def diagnosis():
    return {
        "status": "unresolved_semantic_gap",
        "gap_id": None, "source_ref": None, "field_or_dimension": None,
        "safe_diagnostic": "Unresolved original evidence gap; GitHub must classify.",
        "requires_github_classification": True,
        "normal_first_pass_attempt_consumed": False,
    }


def source_operation(*, state="genuinely_absent", lookup=False):
    result = {
        "gap_id": "rgap-001", "source_ref": "rsource-002",
        "missing_field_or_dimension": "technical_performance_localization_regional",
        "exact_source_revisit": {
            "attempted": True, "status": state,
            "observed_fact_present": state == "fact_found",
            "neutral_fact_or_unknown": "No further verifiable details.",
        },
        "narrow_gap_lookup": None,
    }
    if lookup:
        result["narrow_gap_lookup"] = {
            "gap_id": "rgap-001",
            "missing_field_or_dimension": result["missing_field_or_dimension"],
            "appid": "12345", "original_work_title": "Fixture Game",
            "original_work_release_year": 2020,
            "query_scope": "one_named_gap_one_exact_product_no_broad_research",
            "proposed_distinct_route_class": "other_player_feedback",
            "observed_new_facts": [],
        }
    return result


class InactiveAssemblySemanticTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.x = AsyncFixture(temp.name)

    def prepare(self, with_gap=False):
        x = self.x
        x.preauthorize_assembly()
        if with_gap:
            x.docs[0]["research_audit"]["unresolved_gaps"] = [{
                "gap_id": "rgap-001",
                "field_or_dimension": "technical_performance_localization_regional",
                "reason": "not_observed", "source_refs": ["rsource-002"],
                "material": True, "next_materially_distinct_route": "other_player_feedback",
            }]
        return x

    def traversal(self, submissions):
        x = self.x
        return frozen_assembly_traversal(
            x.f.root, marker_commit=x.amarker, buffer_path=x.abuffer["path"],
            submitted_commits=submissions)

    def candidate(self, index, research_commit, operations=None, payload=None, outcome=None):
        x = self.x
        return offline_assembly_candidate(
            x.f.root, marker_commit=x.amarker, buffer_path=x.abuffer["path"],
            work_path=x.apaths[index], research_package_commit=research_commit,
            outcome=outcome or "unresolved_semantic_gap", payload=payload or diagnosis(),
            supplemental_operations=operations or [])

    def test_01_assembly_gate_and_one_stage_parity(self):
        gate = inactive_assembly_gate()
        self.assertIs(gate["active"], False)
        self.assertIs(gate["executable_in_production"], False)
        self.assertIs(gate["semantic_workers_implemented"], False)
        self.assertIs(inactive_gate()["active"], False)
        self.assertEqual(self.x.f.descriptor["schema"],
                         "TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1")

    def test_02_A_missing_B_C_ready_in_frozen_order_zero_attempt(self):
        x = self.prepare()
        b = x.research_submit(1)
        c = x.research_submit(2)
        outcomes = self.traversal({x.apaths[2]: c, x.apaths[1]: b})
        self.assertEqual([d["work_path"] for d in outcomes], x.apaths)
        self.assertEqual([d["status"] for d in outcomes],
                         ["research_not_submitted", "ready", "ready"])
        self.assertTrue(all(d["attempt_consumed"] is False for d in outcomes))

    def test_03_A_candidate_before_any_GitHub_Research_acceptance(self):
        x = self.prepare()
        r = x.research_submit(0)
        path, doc = self.candidate(0, r)
        self.assertEqual(doc["research_transport"]["research_package_git_commit"], r)
        self.assertEqual(path, x.assembly_work(0, r)["output_path"])
        self.assertTrue(doc["staged_only"])
        self.assertFalse(doc["canonical_acceptance"])
        x.f.save(path, doc)
        commit = x.f.commit("Offline Assembly A create-only candidate before GH receipt")
        verdict = x.inspect(0, commit)
        self.assertEqual(verdict["status"], "typed_assembly_item_pending_github_classification")
        self.assertFalse(verdict["deep_ready"])

    def test_04_later_Research_A_rejection_only_A_B_C_independent(self):
        x = self.prepare()
        a = x.research_submit(0, tamper=lambda d: d["findings"][0].update(
            support_feedback_refs=["rfeedback-999"]))
        path, doc = self.candidate(0, a)
        x.f.save(path, doc)
        ac = x.f.commit("Offline Assembly A ahead of Research structural rejection")
        self.assertEqual(x.inspect(0, ac)["status"],
                         "research_rejected_item_chain_quarantined")
        for index in (1, 2):
            commit = x.research_submit(index)
            path, doc = self.candidate(index, commit)
            x.f.save(path, doc)
            result = x.f.commit(f"Offline independent Assembly item {index}")
            self.assertEqual(x.inspect(index, result)["status"],
                             "typed_assembly_item_pending_github_classification")

    def test_05_exact_raw_blob_canonical_hash_marker_plan_preserved(self):
        x = self.prepare()
        r = x.research_submit(0)
        path, doc = self.candidate(0, r)
        origin = doc["research_transport"]
        raw = file_at(x.f.root, r, origin["research_package_path"])
        self.assertEqual(origin["research_package_blob_sha"],
                         blob(x.f.root, r, origin["research_package_path"]))
        self.assertEqual(origin["research_package_raw_sha256"],
                         hashlib.sha256(raw).hexdigest())
        from dossier_two_stage_staging import strict_json
        self.assertEqual(origin["research_package_sha256"], canonical_sha256(strict_json(raw)))
        self.assertEqual(origin["research_marker_anchor_commit"], x.f.marker)
        self.assertEqual(origin["assembly_plan_blob_sha"],
                         blob(x.f.root, x.amarker + "^", x.apaths[0]))
        self.assertEqual(path, doc["output_path"])

    def test_06_wrong_marker_work_or_wrong_game_only_rejects_local_item(self):
        x = self.prepare()
        r = x.research_submit(0)
        c = x.research_submit(2)
        results = self.traversal({x.apaths[0]: r, x.apaths[1]: r, x.apaths[2]: c})
        self.assertEqual([d["status"] for d in results],
                         ["ready", "research_transport_invalid", "ready"])
        self.assertFalse(results[1]["attempt_consumed"])
        # Malformed Research marker supplied in immutable package fails closed.
        bad = x.research_submit(1, tamper=lambda d: d["assignment"].update(
            research_marker_anchor_commit="0" * 40))
        results = self.traversal({x.apaths[0]: r, x.apaths[1]: bad, x.apaths[2]: c})
        self.assertEqual(results[1]["status"], "research_transport_invalid")
        self.assertEqual(results[2]["status"], "ready")

    def test_07_duplicate_candidate_create_only_no_alternate_name(self):
        x = self.prepare()
        r = x.research_submit(0)
        path, doc = self.candidate(0, r)
        x.f.save(path, doc)
        x.f.commit("Existing Assembly A staged candidate")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.candidate(0, r)
        self.assertEqual(self.traversal({x.apaths[0]: r})[0]["status"],
                         "candidate_already_submitted")

    def test_08_gap_exact_source_first_and_one_named_lookup(self):
        x = self.prepare(with_gap=True)
        r = x.research_submit(0)
        path, doc = self.candidate(0, r, [source_operation(lookup=True)])
        self.assertEqual(doc["supplemental_operations"][0]["gap_id"], "rgap-001")
        self.assertEqual(doc["output_path"], path)
        with self.assertRaisesRegex(ValueError, "narrow lookup"):
            self.candidate(0, r, [source_operation(state="unavailable", lookup=True)])
        with self.assertRaisesRegex(ValueError, "revisit"):
            self.candidate(0, r, [source_operation(state="fact_found", lookup=True)])
        wrong = source_operation(lookup=True)
        wrong["narrow_gap_lookup"]["appid"] = "23456"
        with self.assertRaisesRegex(ValueError, "identity"):
            self.candidate(0, r, [wrong])
        wrong = source_operation()
        wrong["source_ref"] = "rsource-001"  # existing, but not the gap source
        with self.assertRaisesRegex(ValueError, "gap/source"):
            self.candidate(0, r, [wrong])

    def test_09_no_new_retry_lease_scope_or_unfrozen_reorder(self):
        x = self.prepare()
        r = x.research_submit(0)
        with self.assertRaisesRegex(ValueError, "out-of-scope"):
            self.traversal({"arbitrary/unfrozen/plan.json": r})
        # Submissions map may be unordered but output may never be reordered.
        x.research_submit(1)
        result = self.traversal({x.apaths[2]: None, x.apaths[0]: r})
        self.assertEqual([d["work_path"] for d in result], x.apaths)
        self.assertEqual(result[-1]["status"], "research_not_submitted")
        self.assertEqual(set(result[0]), {"work_path", "status", "attempt_consumed", "work"})

    def test_10_cannot_claim_accepted_or_submit_invalid_typed_shape(self):
        x = self.prepare()
        r = x.research_submit(0)
        typed = diagnosis()
        typed["normal_first_pass_attempt_consumed"] = True
        with self.assertRaises(ValueError):
            self.candidate(0, r, payload=typed)
        typed = diagnosis()
        with self.assertRaisesRegex(ValueError, "differs"):
            self.candidate(0, r, payload=typed, outcome="runtime_or_tool_failure")
        typed = diagnosis()
        typed["safe_diagnostic"] = "Quoted raw passage \"not allowed\""
        with self.assertRaises(ValueError):
            self.candidate(0, r, payload=typed, operations=[source_operation()])
        # This fixture has no named source gap; worker cannot invent one.
        with self.assertRaises(ValueError):
            self.candidate(0, r, operations=[source_operation()])


if __name__ == "__main__":
    unittest.main()
