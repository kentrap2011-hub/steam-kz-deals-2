#!/usr/bin/env python3
"""Synthetic/offline-only Dossier shadow quality regression tests."""
import copy
import unittest
from datetime import datetime, timezone

from dossier_two_stage_shadow_quality import (
    AREAS, SCHEMA, compare_records, evaluate_offline_fixture,
)
from dossier_two_stage_staging import blob
from dossier_two_stage_contract_guard import canonical_sha256
from taste_steam_review_dossier_test_fixture import web_dossier
from test_dossier_two_stage_final_acceptance import FinalAcceptanceOfflineTests


class ShadowQualityTests(unittest.TestCase):
    def setUp(self):
        self.helper = FinalAcceptanceOfflineTests(
            "test_01_live_paths_fail_closed_and_contract_is_not_authoritative")
        self.x, self.work, self.contract, _ = self.helper.fixture()
        self.now = datetime.now(timezone.utc)

    def tearDown(self):
        self.helper.doCleanups()

    def pure(self, index=0, *, baseline=None):
        research = copy.deepcopy(self.x.docs[index])
        a = research["assignment"]
        v2 = web_dossier(a["appid"], self.now, title=a["title"],
                         release_year=research["identity"]["original_work_release_year"])
        assembly = {"outcome": "assembled_candidate_ready",
                    "payload": {"status": "assembled_candidate_ready", "dossier": v2},
                    "supplemental_operations": []}
        return research, assembly, copy.deepcopy(baseline or v2)

    def comparison_fixture(self, *, ready=(0, 1, 2), bad_research=None, baseline_override=None):
        refs = []
        docs = []
        for i in range(3):
            a = self.x.docs[i]["assignment"]
            baseline = web_dossier(a["appid"], self.now, title=a["title"])
            if baseline_override is not None and i == 0:
                baseline_override(baseline)
            p = f"data/cache/taste_steam_review_dossiers/App_{a['appid']}.json"
            self.x.f.save(p, baseline)
            docs.append((a["appid"], p, baseline))
        baseline_commit = self.x.f.commit("Synthetic frozen one-stage baseline cache")
        bases = [{"appid": appid, "commit": baseline_commit, "path": path,
                  "git_blob_sha": blob(self.x.f.root, baseline_commit, path),
                  "canonical_sha256": canonical_sha256(baseline)}
                 for appid, path, baseline in docs]
        for i in ready:
            def tamper(doc):
                if bad_research is not None and i == bad_research:
                    doc["identity"]["original_work_release_year"] = 1995
            submitted = self.x.research_submit(i, tamper=tamper if bad_research is not None else None)
            assembled = self.helper.ready(self.x, i, submitted)
            refs.append(self.helper.locator(self.x, i, assembled))
        return refs, bases

    def test_positive_exact_immutable_three_game_fixture(self):
        refs, bases = self.comparison_fixture()
        result = evaluate_offline_fixture(
            self.x.f.root, manifest=self.work, contract=self.contract,
            item_locators=refs, baseline_references=bases)
        self.assertEqual(result["schema"], SCHEMA)
        self.assertEqual(result["cohort"]["compared"], 3)
        self.assertEqual(result["cohort"]["not_measured"], 0)
        self.assertFalse(result["cohort"]["baseline_acceptance_verified"])
        self.assertFalse(result["cohort"]["semantic_parity_approved"])
        self.assertFalse(result["cohort"]["canonical_readiness"])
        self.assertEqual(result["writes"], [])
        for g in result["per_game"]:
            self.assertEqual(g["comparison"]["fidelity"]["strict_v2"],
                             "validated_by_GitHub_existing_inspector")
            self.assertEqual(len(g["comparison"]["research"]["twelve_dimensions"]), 12)
            self.assertTrue(all(v["status"] == "unknown" for v in
                                g["comparison"]["human_quality_review"].values()))
            self.assertTrue(g["immutable_evidence"]["research_git_blob_sha"])
            self.assertFalse(g["canonical_acceptance_granted"])

    def test_missing_item_does_not_fake_partial_group_acceptance(self):
        refs, bases = self.comparison_fixture(ready=(0, 1))
        r = evaluate_offline_fixture(self.x.f.root, manifest=self.work,
                                    contract=self.contract, item_locators=refs,
                                    baseline_references=bases)
        self.assertEqual(r["cohort"]["not_measured"], 3)
        self.assertEqual(r["cohort"]["compared"], 0)

    def test_identity_conflicting_year_never_silently_parity(self):
        research, candidate, baseline = self.pure()
        baseline["game_identity"]["release_year"] = 2002
        outcome = compare_records(research, candidate, baseline)
        self.assertIn("original_work_year_disagrees_with_one_stage",
                      outcome["hard_stop_reasons"])
        candidate["payload"]["dossier"]["game_identity"]["release_year"] = 2001
        with self.assertRaisesRegex(ValueError, "original-work-year contradiction"):
            compare_records(research, candidate, baseline)

    def test_falsified_baseline_and_missing_baseline_fail_closed(self):
        refs, bases = self.comparison_fixture()
        wrong = copy.deepcopy(bases)
        wrong[0]["canonical_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "baseline hash mismatch"):
            evaluate_offline_fixture(self.x.f.root, manifest=self.work,
                                     contract=self.contract, item_locators=refs,
                                     baseline_references=wrong)
        with self.assertRaisesRegex(ValueError, "missing exact one-stage baseline"):
            evaluate_offline_fixture(self.x.f.root, manifest=self.work,
                                     contract=self.contract, item_locators=refs,
                                     baseline_references=bases[:2])
        wrong = copy.deepcopy(bases)
        wrong[0]["path"] = "some-other-file.json"
        with self.assertRaisesRegex(ValueError, "canonical one-stage cache path"):
            evaluate_offline_fixture(self.x.f.root, manifest=self.work,
                                     contract=self.contract, item_locators=refs,
                                     baseline_references=wrong)

    def test_untrusted_or_replayed_transport_is_not_a_quality_measurement(self):
        refs, bases = self.comparison_fixture()
        wrong = copy.deepcopy(refs)
        wrong[0]["result_commit"] = "0" * 40
        result = evaluate_offline_fixture(self.x.f.root, manifest=self.work,
                                          contract=self.contract, item_locators=wrong,
                                          baseline_references=bases)
        self.assertEqual(result["cohort"]["not_measured"], 3)
        with self.assertRaisesRegex(ValueError, "foreign/replayed"):
            evaluate_offline_fixture(self.x.f.root, manifest=self.work,
                                     contract=self.contract, item_locators=refs + [refs[0]],
                                     baseline_references=bases)

    def test_quality_regression_is_flagged_not_fabricated_as_semantic_truth(self):
        research, candidate, old = self.pure()
        old["observations"].append({
            **copy.deepcopy(old["observations"][0]),
            "statement": "Synthetic historical high-friction risk not restated verbatim.",
            "sentiment": "negative"})
        result = compare_records(research, candidate, old)
        self.assertTrue(result["comparison_evidence"][
            "lexically_unmatched_baseline_statements_needing_human_review"])
        self.assertEqual(result["semantic_quality_verdict"], "human_review_required")
        self.assertEqual(result["human_quality_review"]["meaningful_omissions"]["status"],
                         "unknown")
        self.assertFalse(result["canonical_acceptance_granted"])

    def test_adversarial_gap_source_independence_and_review(self):
        research, candidate, baseline = self.pure()
        research["sources"][1]["physical_source_identity"] = (
            research["sources"][2]["physical_source_identity"])
        result = compare_records(research, candidate, baseline)
        self.assertTrue(result["sources"]["research"][
            "duplicate_physical_player_source_identities"])
        research["research_audit"]["dimension_survey"] = (
            research["research_audit"]["dimension_survey"][:-1])
        with self.assertRaisesRegex(ValueError, "twelve Research dimensions"):
            compare_records(research, candidate, baseline)
        research, candidate, baseline = self.pure()
        research["research_audit"]["unresolved_gaps"] = [{
            "gap_id": "rgap-001", "material": True, "field_or_dimension": "pacing"}]
        candidate["supplemental_operations"] = [{
            "gap_id": "rgap-001", "source_ref": research["sources"][0]["ref"],
            "exact_source_revisit": {"status": "unavailable"},
            "narrow_gap_lookup": {"gap_id": "rgap-001"}}]
        with self.assertRaisesRegex(ValueError, "ineligible narrow lookup"):
            compare_records(research, candidate, baseline)
        research, candidate, baseline = self.pure()
        bad = {key: {"status": "unknown", "evidence_refs": [], "note": None}
               for key in AREAS}
        bad["source_truth"]["status"] = "confirmed_no_issue"
        with self.assertRaisesRegex(ValueError, "needs evidence"):
            compare_records(research, candidate, baseline, human_review=bad)
        bad["source_truth"] = {"status": "confirmed_issue",
                               "evidence_refs": ["rsource-002"],
                               "note": "Source does not prove the asserted fact."}
        r = compare_records(research, candidate, baseline, human_review=bad)
        self.assertIn("human_confirmed_source_truth", r["hard_stop_reasons"])

    def test_live_repo_never_accepted_as_fixture(self):
        with self.assertRaisesRegex(ValueError, "disabled"):
            evaluate_offline_fixture(self.x.f.root, manifest=self.work,
                                     contract=self.contract, item_locators=[],
                                     baseline_references=[]) if False else (
                __import__("dossier_two_stage_final_acceptance")
                .offline_gate(self.x.f.root, offline_fixture=False))


if __name__ == "__main__":
    unittest.main()
