#!/usr/bin/env python3
"""Non-semantic integration preflight regressions: never activate or invent scores."""
import copy
import unittest

import deep_two_stage_cutover_preflight as gate


def documents():
    h = "a" * 64
    return {
        "architecture": {"contract": "DEEP-TWO-STAGE-ARCHITECTURE-V1",
                         "status": "frozen_not_active",
                         "production_cutover_authorized": False},
        "migration": {"contract": "DEEP-TWO-STAGE-MIGRATION-V1",
                      "mass_migration_authorized": False,
                      "semantic_execution_authorized_by_this_contract": False},
        "ownership": {"progressive_personalization_phase_c_pass2_core":
                      {"production_execution_authorized": True}},
        "old_deep": {"schema_version": 2, "contract": "PROGRESSIVE-PASS2-STATE-V2",
                     "entries": {"historical-1": {"family_id": "old-1",
                                                  "outcome": "analyzed_fit",
                                                  "legacy_score": 55}}},
        "old_deep_work": {"contract": "PROGRESSIVE-PASS2-WORK-V1",
                          "scope": {"deep_total_current_coverage_target": 2,
                                    "deep_waiting_for_dossier_count": 1}},
        "stage1_work": {"schema_version": 1, "contract": "DEEP-STAGE1-WORK-V1",
                        "implementation_status": "implemented_not_active",
                        "total_eligible": 0, "eligible_work_ids": [], "items": []},
        "stage1_state": {"schema_version": 1, "contract": "DEEP-STAGE1-STATE-V1",
                         "implementation_status": "implemented_not_active",
                         "entries": {}},
        "stage2_work": {"schema_version": 1, "contract": "DEEP-STAGE2-WORK-V1",
                        "items": []},
        "stage2_state": {"schema_version": 1, "contract": "DEEP-STAGE2-STATE-V1",
                         "implementation_status": "implemented_not_active",
                         "entries": {}},
    }


class GateTests(unittest.TestCase):
    def plan(self, d=None):
        return gate.plan(d or documents(), {"fixture": {"sha256": "a" * 64}})

    def test_current_production_stays_active_and_no_score_is_reused(self):
        p = self.plan()
        self.assertFalse(p["cutover_ready"])
        self.assertFalse(p["cutover_performed"])
        self.assertEqual(p["production_authority"], "FAST-DOSSIER-DEEP-V1")
        self.assertFalse(p["semantic_execution_performed"])
        self.assertFalse(p["research_assembly_dossier_used"])
        self.assertEqual(p["canonical_stage1_authorized_queue"], [])
        self.assertEqual(p["canonical_stage2_authorized_queue"], [])
        self.assertEqual(len(p["legacy_classification"]), 1)
        self.assertEqual(p["legacy_classification"][0]["classification"],
                         "requires_stage1_reanalysis")
        self.assertFalse(p["legacy_classification"][0]["semantic_execution_authorized"])
        self.assertNotIn("legacy_score", str(p))

    def test_only_prepared_manifests_can_authorize_items(self):
        d = documents()
        d["stage1_work"]["items"] = [{
            "sequence": 1, "work_id": "b" * 64,
            "result_submission_path": "data/ai_inbox/deep_stage1/results/x.json"
        }]
        with self.assertRaises(gate.PreflightError):
            self.plan(d)  # unlisted item is never an authorized queue
        d["stage1_work"]["eligible_work_ids"] = ["b" * 64]
        p = self.plan(d)
        self.assertEqual([x["work_id"] for x in p["canonical_stage1_authorized_queue"]],
                         ["b" * 64])
        self.assertIn("authorized_semantic_items_still_pending", p["blocking_gates"])

    def test_invalid_authority_fails_closed(self):
        d = documents()
        d["architecture"]["production_cutover_authorized"] = True
        with self.assertRaises(gate.PreflightError):
            self.plan(d)
        d = documents()
        d["migration"]["mass_migration_authorized"] = True
        with self.assertRaises(gate.PreflightError):
            self.plan(d)
        d = documents()
        d["ownership"]["progressive_personalization_phase_c_pass2_core"] = {}
        with self.assertRaises(gate.PreflightError):
            self.plan(d)

    def test_unique_calibration_two_decimal_and_range(self):
        entries = {
            "x": {"status": "calibrated", "calibrated_deep_fit_score_0_56": 35.12},
            "y": {"status": "calibrated", "calibrated_deep_fit_score_0_56": 35.13},
        }
        self.assertEqual(gate.unique_calibrations(entries), 2)
        entries["y"]["calibrated_deep_fit_score_0_56"] = 35.12
        with self.assertRaises(gate.PreflightError):
            gate.unique_calibrations(entries)
        entries["y"]["calibrated_deep_fit_score_0_56"] = 35.123
        with self.assertRaises(gate.PreflightError):
            gate.unique_calibrations(entries)

    def test_cutover_gate_requires_full_scope(self):
        d = documents()
        d["old_deep_work"]["scope"]["deep_waiting_for_dossier_count"] = 0
        d["stage1_work"]["total_eligible"] = 2
        d["stage1_work"]["eligible_work_ids"] = ["a" * 64, "b" * 64]
        fit = {"status": "accepted", "accepted": True, "outcome": "analyzed_fit",
               "family_id": "a", "appid": "10", "profile_semantic_sha256": "f" * 64,
               "accepted_result_path": "data/cache/deep_stage1_results/a.json",
               "accepted_result_sha256": "e" * 64}
        not_fit = {"status": "accepted", "accepted": True,
                   "outcome": "analyzed_not_fit", "family_id": "b"}
        d["stage1_state"]["entries"] = {"a" * 64: fit, "b" * 64: not_fit}
        p = self.plan(d)
        self.assertIn("stage2_calibrations_not_complete_for_all_stage1_fit",
                      p["blocking_gates"])
        calibration = {
            "status": "calibrated", "outcome": "calibrated_fit",
            "calibrated_deep_fit_score_0_56": 42.37,
            "stage1_work_id": "a" * 64, "family_id": "a", "appid": "10",
            "profile_semantic_sha256": "f" * 64,
            "stage1_result_path": "data/cache/deep_stage1_results/a.json",
            "stage1_result_sha256": "e" * 64,
        }
        d["stage2_state"]["entries"] = {"c" * 64: calibration}
        self.assertTrue(self.plan(d)["cutover_ready"])
        d["stage2_state"]["entries"]["c" * 64]["stage1_result_sha256"] = "d" * 64
        self.assertIn("stage2_calibrations_not_complete_for_all_stage1_fit",
                      self.plan(d)["blocking_gates"])
        self.assertFalse(self.plan(d)["cutover_performed"])


if __name__ == "__main__":
    unittest.main()
