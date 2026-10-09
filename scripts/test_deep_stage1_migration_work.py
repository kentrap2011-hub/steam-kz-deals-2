#!/usr/bin/env python3
"""Focused Stage-1 migration preview/authority/reconciliation regressions."""
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import deep_stage1 as s1
import prepare_deep_stage1_migration_work as m


def h(x):
    return (x * 64)[:64]


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = datetime(2026, 10, 9, tzinfo=timezone.utc)
        self.generation = {
            "semantic_generation_id": h("a"),
            "bindings": {"profile_semantic_sha256": h("b")},
            "profile_pin": {"pin_sha256": h("c")},
        }
        self.dossier_binding = {"evidence_contract": "one_stage"}
        self.bindings = {}
        self.rows = {}
        self.contexts = []
        for idx in (41, 42, 43):
            fid = "family-" + str(idx)
            self.bindings[fid] = {
                "semantic_generation_id": h("a"), "work_id": h(str(idx)[0]),
                "family_id": fid, "taste_subject_key": "App_" + str(idx),
                "appid": str(idx), "candidate_context_sha256": h("d"),
                "profile_semantic_sha256": h("b"),
            }
            self.rows[fid] = {"title": "Game " + str(idx)}
            self.contexts.append({"family_id": fid})
        self.legacy = {
            "contract": "PROGRESSIVE-PASS2-WORK-V1",
            "projection_status": "current_github_owned_fast_dossier_deep_v1_projection",
            "semantic_generation_id": h("a"),
            "semantic_bindings": self.generation["bindings"],
            "profile_pin": self.generation["profile_pin"],
            "dossier_compatibility_binding": self.dossier_binding,
            "scope": {"deep_total_current_coverage_target": 3},
        }
        self.previous = {"contract": "PROGRESSIVE-PASS2-STATE-V2", "entries": {}}
        self.state = s1.empty_state()
        self.migration = {"contract": "DEEP-TWO-STAGE-MIGRATION-V1",
                          "status": "frozen_not_active",
                          "mass_migration_authorized": False}
        self.ownership = {"progressive_personalization_phase_c_pass2_core":
                          {"production_execution_authorized": True}}
        self.available = {41, 42}
        self.priority = lambda row: int(row["family_id"].split("-")[1])

    def loader(self, appid):
        if int(appid) not in self.available:
            return None
        path = "data/cache/taste_steam_review_dossiers/App_" + appid + ".json"
        full = self.root / path
        full.parent.mkdir(parents=True, exist_ok=True)
        doc = {"appid": appid, "web_evidence_contract_binding": self.dossier_binding,
               "expires_at_utc": "2027-01-01T00:00:00+00:00",
               "observations": [], "conflicts": []}
        raw = (json.dumps(doc) + "\n").encode()
        full.write_bytes(raw)
        return {"doc": doc, "path": path, "content_sha256": hashlib.sha256(raw).hexdigest()}

    @staticmethod
    def gate(**kwargs):
        return (True, "eligible") if kwargs["dossier_record"] else (False, "waiting_for_dossier")

    def plan(self):
        return m.make_plan(
            legacy=self.legacy, previous=self.previous,
            stage1_state=self.state, migration=self.migration,
            ownership=self.ownership, generation=self.generation,
            bindings=self.bindings, by_family=self.rows, contexts=self.contexts,
            ordering={}, dossier_binding=self.dossier_binding,
            dossier_loader=self.loader, dossier_validator=self.gate,
            priority=self.priority, now=self.now, root=self.root,
        )

    def test_real_manifest_is_gated_but_precise_and_stable(self):
        p = self.plan()
        self.assertFalse(p["executable_materialization_authorized"])
        self.assertFalse(p["semantic_execution_authorized"])
        self.assertEqual((p["current_scope_total"], p["eligible_with_current_dossier"],
                          p["requires_stage1_semantics"]), (3, 2, 2), str(p["blocked_or_waiting"]))
        self.assertEqual(len(p["blocked_or_waiting"]), 1)
        work = p["canonical_work_if_authorized"]
        self.assertEqual([x["appid"] for x in work["items"]], ["42", "41"])
        self.assertEqual([x["sequence"] for x in work["items"]], [2, 3])
        self.assertEqual(work, self.plan()["canonical_work_if_authorized"])
        for item in work["items"]:
            self.assertEqual(item["result_submission_path"],
                             "data/ai_inbox/deep_stage1/results/" + item["work_id"] + ".json")
            self.assertNotIn("score", item)
            self.assertNotIn("wishlist", item["semantic_input"])

    def test_legacy_scores_cannot_become_stage1(self):
        self.previous["entries"]["family-41"] = {
            "authoritative_completed": True, "outcome": "analyzed_fit",
            "taste_factors": {"score": 56}, "total_score": 100,
        }
        p = self.plan()
        self.assertEqual(p["requires_stage1_semantics"], 2)
        self.assertEqual(p["accepted_current_stage1"], [])
        self.assertEqual(len(p["canonical_work_if_authorized"]["items"]), 2)

    def test_accepted_exact_stage1_dedup_and_bad_state_is_blocked(self):
        p = self.plan()
        item = p["canonical_work_if_authorized"]["items"][0]
        result_path = self.root / s1.RESULTS / (item["work_id"] + ".json")
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result = {
            "schema_version": 1, "contract": s1.RESULT_CONTRACT,
            **{k: item[k] for k in (
                "semantic_generation_id", "work_id", "family_id", "taste_subject_key",
                "appid", "candidate_context_sha256", "profile_semantic_sha256",
                "dossier_content_sha256")},
            "profile_pin_sha256": item["profile_pin"]["pin_sha256"],
            "outcome": "analyzed_not_fit", "confidence": "high",
            "summary_ru": "Grounded not-fit conclusion",
            "positives": [], "negatives": [], "nuances": [],
            "provisional_deep_fit_score_0_56": None,
            "point_breakdown": [], "analysis_issue_code": None,
        }
        result_path.write_text(json.dumps(result) + "\n")
        digest = s1.file_sha256(result_path)
        s1.accept_result(self.state, item, result,
                         path=str(s1.RESULTS / (item["work_id"] + ".json")), sha=digest)
        after = self.plan()
        self.assertEqual(len(after["accepted_current_stage1"]), 1)
        self.assertEqual(after["requires_stage1_semantics"], 1)
        result_path.write_text("{}\n")
        bad = self.plan()
        self.assertEqual(bad["requires_stage1_semantics"], 1)
        self.assertTrue(any("accepted_stage1_invalid_no_retry" in b["reason"]
                            for b in bad["blocked_or_waiting"]))

    def test_local_dossier_failure_does_not_block_sibling(self):
        self.available.remove(41)
        p = self.plan()
        self.assertEqual(p["requires_stage1_semantics"], 1)
        self.assertEqual(p["canonical_work_if_authorized"]["items"][0]["appid"], "42")

    def test_global_snapshot_drift_fails_closed(self):
        self.legacy["scope"]["deep_total_current_coverage_target"] = 4
        with self.assertRaisesRegex(m.PreparationError, "coverage"):
            self.plan()

    def test_materialization_requires_separate_authority(self):
        p = self.plan()
        self.assertIn("mass_migration_authorized=false", p["authorization_blocker"])
        self.migration["mass_migration_authorized"] = True
        p = self.plan()
        self.assertTrue(p["executable_materialization_authorized"])
        self.assertFalse(p["semantic_execution_authorized"])
        self.assertFalse(p["production_cutover_performed"])
        self.assertFalse(p["research_assembly_dossier_used"])


if __name__ == "__main__":
    unittest.main()
