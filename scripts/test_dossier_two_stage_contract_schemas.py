#!/usr/bin/env python3
"""P1 deterministic contract fixtures. No production data, jobs, or web access."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from dossier_two_stage_contract_guard import (
    CONFIG, DIMENSIONS, FILES, canonical_sha256, check_gate,
    schema_validate, validate_research, validate_research_receipt,
    validate_assembly_assignment, validate_assembly_result,
    validate_assembly_receipt,
)


def research_fixture():
    sha = lambda char: char * 64
    assignment = {
        "assignment_id": "research-fixture-0001",
        "snapshot_id": sha("a"),
        "group_sequence": 1, "group_sha256": sha("b"),
        "prepared_required_sha256": sha("c"),
        "group_plan_sha256": sha("d"),
        "items_sha256": sha("e"), "item_index": 0,
        "appid": "12345", "title": "Fixture Game",
        "scope_source": "fixed_descriptor", "source_queue_sha256": sha("f"),
        "research_contract_sha256": sha("1"),
        "web_evidence_contract_binding": {
            "evidence_contract_schema": "TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2",
            "evidence_contract_version": 2, "evidence_contract_revision": "fixture-revision",
            "evidence_contract_sha256": sha("2"),
            "worker_schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2",
            "worker_schema_version": 2, "worker_schema_revision": "fixture-schema-revision",
            "worker_schema_sha256": sha("3"),
            "dossier_schema": "TASTE-STEAM-REVIEW-DOSSIER-V2",
            "dossier_schema_version": 2, "worker_prompt_revision": "fixture-v2",
            "worker_prompt_sha256": sha("4"),
        },
        "research_marker_anchor_commit": "5" * 40,
        "research_marker_nonce": "6" * 32,
    }
    binding = {
        "basis": "appid", "appid": "12345", "title": "Fixture Game",
        "original_work_release_year": 2020, "evidence_source_refs": ["rsource-001"],
    }
    sources = [
        {
            "ref": "rsource-001",
            "locator": {"url": "https://example.org/metadata/game12345"},
            "normalized_locator": "https://example.org/metadata/game12345",
            "domain": "example.org",
            "physical_source_identity": "https://example.org/metadata/game12345",
            "source_type": "official_metadata", "evidence_role_hint": "identity",
            "player_feedback": False, "language": "unknown",
            "publication_date": None, "temporal_kind_hint": "identity",
            "feedback_surface_mode": None, "exact_product_binding": binding,
            "observed_mode": "opened_source",
            "availability_on_revisit": "not_checked",
        },
        {
            "ref": "rsource-002",
            "locator": {"url": "https://example.org/games/12345/feedback"},
            "normalized_locator": "https://example.org/games/12345/feedback",
            "domain": "example.org",
            "physical_source_identity": "https://example.org/games/12345/feedback",
            "source_type": "reddit", "evidence_role_hint": "durable_trait",
            "player_feedback": True, "language": "russian",
            "publication_date": None, "temporal_kind_hint": "durable",
            "feedback_surface_mode": "concrete_item_collection",
            "exact_product_binding": binding, "observed_mode": "inspected_collection",
            "availability_on_revisit": "not_checked",
        },
    ]
    finding = {
        "ref": "rfinding-001", "kind": "observation",
        "safe_neutral_synthesis": "Player feedback indicates the core interaction is a focus.",
        "polarity_hint": "neutral", "recurrence_basis": None,
        "dimension_hints": ["core_play_mechanics"],
        "support_feedback_refs": ["rfeedback-001"],
        "contextual_source_refs": [], "temporal_relevance_hint": "durable",
        "uncertainty_note": None,
    }
    return {
        "schema": "DOSSIER-RESEARCH-PACKAGE-V1", "schema_version": 1,
        "assignment": assignment,
        "identity": {
            "resolved_title": "Fixture Game", "original_work_release_year": 2020,
            "resolution": "resolved", "corroborators": [{"kind": "appid", "value": "12345"}],
            "identity_source_refs": ["rsource-001"], "ambiguity_notes": None,
        },
        "sources": sources,
        "observed_feedback": [{
            "ref": "rfeedback-001", "parent_source_ref": "rsource-002",
            "acquisition_mode": "inspected_collection_item", "item_locator": None,
            "publication_date": None, "language": "russian",
            "exact_product_binding_ref": "rsource-002",
            "observed": True, "independent_evidence_note": None,
        }],
        "findings": [finding],
        "research_audit": {
            "russian_attempt_observed": "found_and_used",
            "russian_existence_signal": "confirmed",
            "dimension_survey": [
                {
                    "dimension": dimension,
                    "finding_refs": ["rfinding-001"] if i == 0 else [],
                    "investigation_state": "supported" if i == 0 else "not_material",
                } for i, dimension in enumerate(DIMENSIONS)
            ],
            "strengths_investigated": True,
            "weaknesses_tradeoffs_investigated": True,
            "used_distinct_route_classes": ["official_metadata", "reddit"],
            "required_route_state": {
                "identity": "investigated", "russian": "investigated",
                "source_diversification": "investigated", "temporal": "investigated",
            },
            "unresolved_gaps": [], "completeness": "assembly_ready",
            "completion_basis": "compact_central_experience",
        },
        "package_hash_algorithm": "github_accepted_canonical_json_sha256_sorted_keys_compact_utf8",
    }


def research_receipt_fixture(doc):
    a = doc["assignment"]
    return {
        "schema": "DOSSIER-RESEARCH-ACCEPTANCE-RECEIPT-V1",
        "schema_version": 1, "status": "accepted_structural_evidence_not_canonical_dossier",
        "owner": "github_control_plane", "assignment": copy.deepcopy(a),
        "research_package_path": (
            f"data/ai_inbox/dossier_research/{a['snapshot_id']}/"
            f"g{a['group_sequence']:06d}/{a['appid']}--{a['assignment_id']}.json"
        ),
        "research_package_sha256": canonical_sha256(doc),
        "research_package_blob_sha": "a" * 40,
        "research_package_git_commit": "b" * 40,
        "validation_revision": "test-contract-guard-v1",
        "research_schema_id": "DOSSIER-RESEARCH-PACKAGE-V1",
        "research_contract_sha256": a["research_contract_sha256"],
        "accepted_identity": {
            "appid": a["appid"], "title": a["title"],
            "original_work_release_year": doc["identity"]["original_work_release_year"],
            "identity_resolution": doc["identity"]["resolution"],
        },
        "canonical_acceptance": False, "deep_eligibility_issued": False,
    }


def assembly_assignment_fixture(doc, receipt):
    a = doc["assignment"]
    return {
        "schema": "DOSSIER-ASSEMBLY-ASSIGNMENT-V1",
        "schema_version": 1,
        "assembly_assignment_id": "assembly-fixture-0001",
        "original_research_assignment": copy.deepcopy(a),
        "accepted_research": copy.deepcopy(receipt),
        "accepted_research_receipt_blob_sha": "c" * 40,
        "assembly_marker_anchor_commit": "d" * 40,
        "assembly_marker_nonce": "e" * 32,
        "assembly_contract_sha256": "f" * 64,
        "assembly_prompt_sha256": "1" * 64,
        "assembly_prompt_revision": "assembly-fixture-v1",
        "canonical_dossier_target": {
            "schema": "TASTE-STEAM-REVIEW-DOSSIER-V2", "schema_version": 2,
            "worker_schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2",
            "worker_schema_version": 2,
            "web_evidence_contract": "TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2",
            "web_evidence_contract_version": 2,
            "canonical_worker_binding_sha256": canonical_sha256(a["web_evidence_contract_binding"]),
        },
        "output_path": (
            f"data/ai_inbox/dossier_assembly/{a['snapshot_id']}/"
            f"g{a['group_sequence']:06d}/{a['appid']}--assembly-fixture-0001.json"
        ),
        "permitted_result_namespace": "data/ai_inbox/dossier_assembly/",
        "create_only": True,
        "canonical_acceptance_authority": "existing_github_strict_v2_validator_and_group_ingest_only",
    }


def result_fixture(work):
    return {
        "schema": "DOSSIER-ASSEMBLY-RESULT-V1", "schema_version": 1,
        "assembly_assignment_id": work["assembly_assignment_id"],
        "original_research_assignment": copy.deepcopy(work["original_research_assignment"]),
        "accepted_research_package_sha256": work["accepted_research"]["research_package_sha256"],
        "accepted_research_receipt_blob_sha": work["accepted_research_receipt_blob_sha"],
        "assembly_marker_anchor_commit": work["assembly_marker_anchor_commit"],
        "assembly_marker_nonce": work["assembly_marker_nonce"],
        "assembly_contract_sha256": work["assembly_contract_sha256"],
        "assembly_prompt_sha256": work["assembly_prompt_sha256"],
        "canonical_dossier_target": copy.deepcopy(work["canonical_dossier_target"]),
        "output_path": work["output_path"],
        "outcome": "unresolved_semantic_gap",
        "payload": {
            "status": "unresolved_semantic_gap", "gap_id": None, "source_ref": None,
            "field_or_dimension": None, "safe_diagnostic": "No further observed evidence.",
            "requires_github_classification": True,
            "normal_first_pass_attempt_consumed": False,
        },
        "supplemental_operations": [],
        "staged_only": True, "canonical_acceptance": False,
    }


class P1ContractSchemasTest(unittest.TestCase):
    def setUp(self):
        self.doc = research_fixture()
        self.receipt = research_receipt_fixture(self.doc)
        self.work = assembly_assignment_fixture(self.doc, self.receipt)
        self.result = result_fixture(self.work)

    def test_01_inactive_gate_and_existing_one_stage_live(self):
        config = check_gate()
        self.assertFalse(config["active"])
        self.assertFalse(config["authoritative"])
        one_stage = json.loads((CONFIG / "taste_steam_review_dossier_schema.json").read_text())
        self.assertEqual(one_stage["status"], "active")
        self.assertEqual(one_stage["dossier_schema"], "TASTE-STEAM-REVIEW-DOSSIER-V2")

    def test_02_all_schema_dialects_and_interfaces_resolve(self):
        from jsonschema import Draft202012Validator
        for filename in FILES.values():
            schema = json.loads((CONFIG / filename).read_text(encoding="utf-8"))
            Draft202012Validator.check_schema(schema)
            self.assertEqual(schema["additionalProperties"], False)

    def test_03_valid_structural_research_and_hash(self):
        self.assertEqual(validate_research(self.doc), canonical_sha256(self.doc))
        self.assertIsNone(self.doc["observed_feedback"][0]["publication_date"])

    def test_04_unknown_fields_and_missing_immutable_bindings_fail(self):
        self.doc["unexpected"] = "surprise"
        with self.assertRaises(ValueError):
            validate_research(self.doc)
        self.doc.pop("unexpected")
        self.doc["assignment"].pop("group_sha256")
        with self.assertRaises(ValueError):
            validate_research(self.doc)

    def test_05_broken_refs_and_duplicate_local_ids_fail(self):
        self.doc["findings"][0]["support_feedback_refs"] = ["rfeedback-999"]
        with self.assertRaisesRegex(ValueError, "broken support"):
            validate_research(self.doc)
        self.doc = research_fixture()
        self.doc["observed_feedback"].append(copy.deepcopy(self.doc["observed_feedback"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate feedback"):
            validate_research(self.doc)

    def test_06_invalid_parent_and_source_type_fail(self):
        self.doc["observed_feedback"][0]["parent_source_ref"] = "rsource-001"
        with self.assertRaisesRegex(ValueError, "invalid feedback parent"):
            validate_research(self.doc)
        self.doc = research_fixture()
        self.doc["sources"][1]["source_type"] = "professional_context"
        with self.assertRaisesRegex(ValueError, "context-only source"):
            validate_research(self.doc)

    def test_07_aliases_and_duplicate_dimensions_fail(self):
        self.doc["sources"][1]["physical_source_identity"] = self.doc["sources"][0]["physical_source_identity"]
        with self.assertRaisesRegex(ValueError, "duplicate physical source"):
            validate_research(self.doc)
        self.doc = research_fixture()
        self.doc["research_audit"]["dimension_survey"][1]["dimension"] = DIMENSIONS[0]
        with self.assertRaisesRegex(ValueError, "12 dimensions"):
            validate_research(self.doc)

    def test_08_privacy_and_unsafe_locator_fail(self):
        for url in [
            "http://example.org/games/12345/feedback",
            "https://example.org/users/personal-handle/comments",
            "https://example.org/games/12345?steamid=123",
        ]:
            with self.subTest(url=url):
                self.doc = research_fixture()
                self.doc["sources"][1]["locator"]["url"] = url
                with self.assertRaises(ValueError):
                    validate_research(self.doc)
        self.doc = research_fixture()
        self.doc["sources"][1]["username"] = "private"
        with self.assertRaises(ValueError):
            validate_research(self.doc)

    def test_09_no_semantic_evidence_defaults(self):
        self.doc["observed_feedback"][0]["publication_date"] = None
        self.doc["observed_feedback"][0]["language"] = "unknown"
        before = copy.deepcopy(self.doc)
        schema_validate(self.doc, "research")
        self.assertEqual(self.doc, before)
        self.doc["observed_feedback"][0].pop("publication_date")
        with self.assertRaises(ValueError):
            validate_research(self.doc)

    def test_10_research_receipt_hash_release_and_identity_binds(self):
        validate_research_receipt(self.receipt, self.doc)
        self.receipt["research_package_sha256"] = "9" * 64
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            validate_research_receipt(self.receipt, self.doc)
        self.receipt = research_receipt_fixture(self.doc)
        self.receipt["accepted_identity"]["original_work_release_year"] = 2019
        with self.assertRaisesRegex(ValueError, "release identity mismatch"):
            validate_research_receipt(self.receipt, self.doc)

    def test_11_assembly_rejects_unaccepted_or_stale_package(self):
        validate_assembly_assignment(self.work, self.doc)
        self.work["accepted_research"]["status"] = "not_accepted"
        with self.assertRaises(ValueError):
            validate_assembly_assignment(self.work, self.doc)
        self.work = assembly_assignment_fixture(self.doc, self.receipt)
        self.result["accepted_research_package_sha256"] = "9" * 64
        with self.assertRaisesRegex(ValueError, "stale/unaccepted"):
            validate_assembly_result(self.result, self.work, self.doc)

    def test_12_result_bindings_and_outcome_are_exact(self):
        validate_assembly_result(self.result, self.work, self.doc)
        self.result["payload"]["status"] = "source_unavailable"
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            validate_assembly_result(self.result, self.work, self.doc)
        self.result = result_fixture(self.work)
        self.result["original_research_assignment"]["appid"] = "999"
        with self.assertRaisesRegex(ValueError, "immutable binding"):
            validate_assembly_result(self.result, self.work, self.doc)

    def test_13_exact_source_first_blocks_premature_gap_search(self):
        self.doc["research_audit"]["unresolved_gaps"] = [{
            "gap_id": "rgap-001", "field_or_dimension": "pacing_structure_direction",
            "reason": "not_observed", "source_refs": ["rsource-002"],
            "material": True, "next_materially_distinct_route": "forum",
        }]
        self.doc["research_audit"]["completeness"] = "research_incomplete"
        self.receipt = research_receipt_fixture(self.doc)
        self.work = assembly_assignment_fixture(self.doc, self.receipt)
        self.result = result_fixture(self.work)
        self.result["supplemental_operations"] = [{
            "gap_id": "rgap-001", "source_ref": "rsource-002",
            "missing_field_or_dimension": "pacing_structure_direction",
            "exact_source_revisit": {
                "attempted": True, "status": "unavailable",
                "observed_fact_present": False, "neutral_fact_or_unknown": None,
            },
            "narrow_gap_lookup": {
                "gap_id": "rgap-001", "missing_field_or_dimension": "pacing_structure_direction",
                "appid": "12345", "original_work_title": "Fixture Game",
                "original_work_release_year": 2020,
                "query_scope": "one_named_gap_one_exact_product_no_broad_research",
                "proposed_distinct_route_class": "forum", "observed_new_facts": [],
            },
        }]
        with self.assertRaises(ValueError):
            validate_assembly_result(self.result, self.work, self.doc)
        self.result["supplemental_operations"][0]["exact_source_revisit"]["status"] = "genuinely_absent"
        validate_assembly_result(self.result, self.work, self.doc)

    def test_14_exhaustive_unambiguous_result_statuses(self):
        config = check_gate()
        known = config["assembly_supplemental_rule"]["status_vocabulary"]
        schema = json.loads((CONFIG / FILES["assembly_result"]).read_text())
        self.assertEqual(schema["properties"]["outcome"]["enum"], known)
        self.assertEqual(len(known), len(set(known)))
        for outcome in known:
            result = result_fixture(self.work)
            if outcome == "assembled_candidate_ready":
                result["payload"] = {
                    "status": "assembled_candidate_ready",
                    "dossier": {
                        "schema": "TASTE-STEAM-REVIEW-DOSSIER-V2", "schema_version": 2,
                        "web_evidence_contract_binding": {},
                        "appid": "12345", "title": "Fixture Game",
                        "generated_at_utc": "2026-10-08T12:00:00Z",
                        "expires_at_utc": "2026-10-28T12:00:00Z",
                        "ttl_days": 20, "game_identity": {},
                        "summary": "Neutral fixture.", "observations": [{}],
                        "conflicts": [], "evidence": {}, "provenance": {},
                    },
                }
            else:
                result["payload"]["status"] = outcome
            result["outcome"] = outcome
            with self.subTest(outcome=outcome):
                validate_assembly_result(result, self.work, self.doc)

    def test_15_receipt_bindings_and_no_acceptance(self):
        receipt = {
            "schema": "DOSSIER-ASSEMBLY-RECEIPT-V1", "schema_version": 1,
            "owner": "github_control_plane",
            "assembly_assignment_id": self.work["assembly_assignment_id"],
            "original_research_assignment": copy.deepcopy(self.doc["assignment"]),
            "accepted_research_package_sha256": self.receipt["research_package_sha256"],
            "assembly_result_path": self.work["output_path"],
            "assembly_result_sha256": canonical_sha256(self.result),
            "assembly_result_blob_sha": "e" * 40,
            "assembly_outcome": self.result["outcome"],
            "classification": "assembly_gap", "validation_revision": "P1-test",
            "canonical_dossier_accepted": False,
            "deep_eligibility_issued": False, "retry_or_recovery_authorized": False,
        }
        validate_assembly_receipt(receipt, self.result, self.work)
        receipt["canonical_dossier_accepted"] = True
        with self.assertRaises(ValueError):
            validate_assembly_receipt(receipt, self.result, self.work)


if __name__ == "__main__":
    unittest.main()
