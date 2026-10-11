#!/usr/bin/env python3
"""Synthetic isolated Dossier review gate regression; never real semantic analysis."""
import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from dossier_shadow_quality_review_gate import (
    DIMENSIONS, _evaluate_rows, _frozen_json,
)


class DossierReviewGateTests(unittest.TestCase):
    def setUp(self):
        self.frame = {"trial_id": "synthetic-01", "groups": [{
            "sequence": 1, "group_sha256": "a" * 64,
            "games": [{"appid": str(x), "title": f"Synthetic {x}",
                       "original_work_year": 2008} for x in (101, 102, 103)],
        }]}
        self.comps = {str(x): self.comparison(str(x)) for x in (101, 102, 103)}
        self.accepted = {"101", "102", "103"}
        self.strict = {1}
        self.reviews = {x: self.pair(x) for x in self.accepted}

    @staticmethod
    def comparison(appid):
        old = {"sentiment": "mixed", "statement": "NEVER EMIT REVIEW TEXT",
               "source_ids": ["src-old"], "player_feedback_ids": ["feed-old"]}
        new = copy.deepcopy(old)
        new.update(source_ids=["src-new"], player_feedback_ids=["feed-new"])
        return {
            "appid": appid, "title": f"Synthetic {appid}",
            "identity": {
                "original_work_year_research": 2008,
                "original_work_year_two_stage": 2008,
                "original_work_year_one_stage": 2008,
                "year_conflict_with_baseline": False,
            },
            "comparison_evidence": {
                "one_stage_statements": [old], "two_stage_statements": [new],
                "research_findings": [{"ref": "finding-001"}],
            },
            "sources": {"research": {
                "research_source_refs": ["rsource-001", "rsource-002"],
                "physical_player_source_identities": ["parent-A", "parent-B"],
                "duplicate_physical_player_source_identities": [],
            }},
            "research": {"gaps": [{"gap_id": "gap-001"}]},
        }

    @staticmethod
    def review(role, appid):
        dimensions = {
            key: {"state": "confirmed_no_issue", "severity": "none",
                  "reason_code": "evidence_supported", "anchors": ["new:obs:0"]}
            for key in DIMENSIONS
        }
        dimensions["source_independence"]["anchors"] = [
            "research:source:rsource-001", "research:source:rsource-002"]
        return {"role": role, "subject": {"trial_id": "synthetic-01",
                                        "group_sequence": 1, "appid": appid},
                "dimensions": dimensions,
                "negative_retention": {
                    "old:obs:0": {"disposition": "preserved", "anchors": ["new:obs:0"]}},
                "unknown_resolution": {
                    "research:gap:gap-001": {
                        "disposition": "still_unknown", "anchors": ["research:gap:gap-001"]}}}

    def pair(self, appid):
        return {"A": self.review("A", appid), "B": self.review("B", appid),
                "adjudication": None}

    def evaluate(self):
        return _evaluate_rows(self.frame, self.comps, self.accepted, self.strict,
                              self.reviews)

    def reasons(self):
        return self.evaluate()["per_game"][0]["reason_codes"]

    def test_valid_synthetic_packet_never_quality_verified(self):
        x = self.evaluate()
        self.assertEqual(x["cohort"]["frozen_groups"], 1)
        self.assertEqual(x["cohort"]["frozen_games"], 3)
        self.assertEqual(x["cohort"]["offline_gate_ready"], 3)
        self.assertEqual(x["cohort"]["not_measured"], 0)
        for field in ("quality_verified", "pilot_authorized", "canonical_readiness",
                      "deep_readiness", "real_source_authenticity_verified"):
            self.assertIs(x[field], False)
        self.assertIsNone(x["approved_stop_thresholds"])
        self.assertEqual(x["writes"], [])
        self.assertNotIn("NEVER EMIT REVIEW TEXT", str(x))

    def test_nonexistent_or_unproven_historical_writer_never_accepts(self):
        self.accepted.remove("101")
        self.assertIn("baseline_writer_provenance_not_verified", self.reasons())
        x = self.evaluate()["cohort"]
        self.assertEqual(x["historical_baseline_proven_games"], 2)
        self.assertEqual(x["not_measured"], 1)

    def test_candidate_group_missing_strict_chain_blocks_all_three(self):
        self.strict.clear()
        self.assertEqual(self.evaluate()["cohort"]["offline_gate_ready"], 0)
        self.assertEqual(self.evaluate()["cohort"]["not_measured"], 3)

    def test_original_work_year_conflict_is_not_storefront_date(self):
        self.comps["101"]["identity"]["original_work_year_research"] = 2023
        self.assertIn("original_work_identity_year_conflict", self.reasons())

    def test_missing_independent_reviewer(self):
        self.reviews["101"]["B"] = None
        self.assertIn("review_record_invalid_or_unfrozen", self.reasons())

    def test_fake_or_reused_source_anchor(self):
        field = self.reviews["101"]["A"]["dimensions"]["supported_claims"]
        field["anchors"] = ["research:source:invented"]
        self.assertIn("fake_or_reused_source_anchor", self.reasons())
        self.reviews["101"] = self.pair("101")
        self.reviews["101"]["A"]["dimensions"]["supported_claims"]["anchors"] *= 2
        self.assertIn("fake_or_reused_source_anchor", self.reasons())

    def test_duplicate_physical_sources_not_independent(self):
        self.comps["101"]["sources"]["research"]["duplicate_physical_player_source_identities"] = ["same-parent"]
        self.assertIn("review_record_invalid_or_unfrozen", self.reasons())

    def test_negative_observation_not_silently_dropped(self):
        self.reviews["101"]["A"]["negative_retention"] = {}
        self.assertIn("review_record_invalid_or_unfrozen", self.reasons())
        self.reviews["101"] = self.pair("101")
        self.comps["101"]["comparison_evidence"]["two_stage_statements"][0]["sentiment"] = "neutral"
        self.assertIn("review_record_invalid_or_unfrozen", self.reasons())
        self.comps["101"]["comparison_evidence"]["two_stage_statements"][0]["sentiment"] = "mixed"
        self.reviews["101"] = self.pair("101")
        self.reviews["101"]["A"]["negative_retention"]["old:obs:0"]["disposition"] = "missing"
        self.assertIn("substantive_negative_not_proven_preserved", self.reasons())

    def test_unknown_not_confirmed_without_bound_source(self):
        self.reviews["101"]["A"]["unknown_resolution"]["research:gap:gap-001"] = {
            "disposition": "confirmed_with_source", "anchors": ["new:obs:0"]}
        self.assertIn("review_record_invalid_or_unfrozen", self.reasons())
        self.reviews["101"] = self.pair("101")
        self.reviews["101"]["A"]["unknown_resolution"]["research:gap:gap-001"] = {
            "disposition": "omitted", "anchors": []}
        self.assertIn("unknown_omitted_or_overstated", self.reasons())

    def test_copied_player_profile_review_field_rejected(self):
        self.reviews["101"]["A"]["raw_player_review"] = "@someone private profile"
        self.assertIn("review_record_invalid_or_unfrozen", self.reasons())

    def test_unverified_or_fabricated_public_source_is_defect(self):
        self.reviews["101"]["A"]["dimensions"]["source_authenticity"] = {
            "state": "confirmed_issue", "severity": "critical",
            "reason_code": "source_not_verifiable",
            "anchors": ["research:source:rsource-001"]}
        self.assertIn("human_confirmed_quality_defect", self.reasons())

    def test_unknown_dimension_not_parity(self):
        self.reviews["101"]["B"]["dimensions"]["confidence_calibration"] = {
            "state": "unknown", "severity": "none",
            "reason_code": "insufficient_evidence", "anchors": []}
        self.assertIn("human_dimension_not_verified", self.reasons())

    def test_disagreement_requires_adjudicator(self):
        self.reviews["101"]["A"]["dimensions"]["supported_claims"]["anchors"] = ["old:obs:0"]
        self.assertIn("adjudication_missing_or_unresolved", self.reasons())
        self.assertEqual(self.evaluate()["cohort"]["unadjudicated_disagreements"], 1)

    def test_separately_anchored_adjudicator_records_difference(self):
        self.reviews["101"]["A"]["dimensions"]["supported_claims"]["anchors"] = ["old:obs:0"]
        self.reviews["101"]["adjudication"] = {
            "role": "adjudicator", "subject": {"trial_id": "synthetic-01",
                                               "group_sequence": 1, "appid": "101"},
            "resolved": {"supported_claims": "B"},
            "justifications": {
                "supported_claims": {
                    "reason_code": "reviewer_difference", "anchors": ["old:obs:0"]}}}
        x = self.evaluate()["cohort"]
        self.assertEqual(x["reviewer_disagreements"], 1)
        self.assertEqual(x["unadjudicated_disagreements"], 0)
        self.assertEqual(x["offline_gate_ready"], 3)

    def test_original_group_membership_replacement_rejected(self):
        self.frame["groups"][0]["games"][0]["appid"] = "999"
        with self.assertRaisesRegex(ValueError, "resampled"):
            self.evaluate()
        self.frame["groups"][0]["games"][0]["appid"] = "101"
        self.comps["not-in-frame"] = self.comps["101"]
        with self.assertRaisesRegex(ValueError, "resampled"):
            self.evaluate()

    def test_cherry_picked_missing_pair_remains_denominator(self):
        self.comps.pop("102")
        self.reviews.pop("102")
        x = self.evaluate()["cohort"]
        self.assertEqual(x["frozen_games"], 3)
        self.assertEqual(x["not_measured"], 1)
        self.assertEqual(x["offline_gate_ready"], 2)

    def test_stale_wrong_commit_review_blob_in_disposable_git(self):
        with tempfile.TemporaryDirectory(prefix="dossier-shadow-review-git-") as t:
            root = Path(t)

            def git(*args):
                return subprocess.run(["git", "-C", str(root), *args], check=True,
                                      capture_output=True, text=True).stdout.strip()

            git("init", "-q")
            git("config", "user.name", "Synthetic")
            git("config", "user.email", "test@example.invalid")
            path = "reviews/dossier_shadow_offline/a.json"
            file = root / path
            file.parent.mkdir(parents=True)
            file.write_text(json.dumps({"role": "A"}), encoding="utf-8")
            git("add", path)
            git("commit", "-qm", "Synthetic first round")
            ref = {"commit": git("rev-parse", "HEAD"), "path": path,
                   "blob_sha256": git("rev-parse", "HEAD:" + path)}
            self.assertEqual(_frozen_json(root, ref), {"role": "A"})
            ref["blob_sha256"] = "0" * 40
            with self.assertRaisesRegex(ValueError, "wrong-commit"):
                _frozen_json(root, ref)
            ref["blob_sha256"] = git("rev-parse", "HEAD:" + path)
            file.write_text(json.dumps({"role": "B"}), encoding="utf-8")
            git("add", path)
            git("commit", "-qm", "Synthetic changed blob")
            with self.assertRaisesRegex(ValueError, "wrong-commit"):
                _frozen_json(root, ref)


if __name__ == "__main__":
    unittest.main()
