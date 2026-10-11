#!/usr/bin/env python3
"""No live data/semantic calls; disposable Git negative/strict transport proof."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from dossier_shadow_research_trial import (
    PREFIX, TRIAL, exact_marker, frozen_trial, sandbox_output_path,
    validate_candidate, inspect_transport, _three_by_six,
)
from test_dossier_two_stage_async_buffer import AsyncFixture


class ShadowResearchTrialTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="shadow-6x3-tests-")
        self.addCleanup(tmp.cleanup)
        self.x = AsyncFixture(tmp.name)
        self.nonce = "e" * 32
        self.path = f"{PREFIX}/run_starts/{self.nonce}.json"

    def start(self, *, body=None, extra=False, path=None):
        self.x.f.save(path or self.path, body or {
            "schema": "DOSSIER-SHADOW-RESEARCH-RUN-START-V1",
            "schema_version": 1, "trial_id": TRIAL, "nonce": self.nonce})
        if extra:
            self.x.f.save("data/production/forbidden.json", {"bad": True})
        return self.x.f.commit("Synthetic ONLY sandbox run-start")

    def test_01_marker_commit_must_have_exact_parent_and_exclusive_path(self):
        anchor = self.start()
        parent, nonce = exact_marker(self.x.f.root, anchor)
        self.assertEqual(nonce, self.nonce)
        self.assertEqual(len(parent), 40)
        with self.assertRaises(ValueError):
            exact_marker(self.x.f.root, "0" * 40)

    def test_02_incorrect_marker_contents_and_prod_path_fail_closed(self):
        for wrong in [
            {"schema": "BAD", "schema_version": 1, "trial_id": TRIAL, "nonce": self.nonce},
            {"schema": "DOSSIER-SHADOW-RESEARCH-RUN-START-V1",
             "schema_version": 1, "trial_id": "OTHER", "nonce": self.nonce},
        ]:
            with tempfile.TemporaryDirectory() as root:
                fixture = AsyncFixture(root)
                fixture.f.save(self.path, wrong)
                marker = fixture.f.commit("Invalid marker")
                with self.assertRaises(ValueError):
                    exact_marker(fixture.f.root, marker)
        with tempfile.TemporaryDirectory() as root:
            fixture = AsyncFixture(root)
            fixture.f.save("data/control/forbidden-marker.json", {"bad": True})
            marker = fixture.f.commit("Invalid namespace")
            with self.assertRaises(ValueError):
                exact_marker(fixture.f.root, marker)

    def test_03_second_file_in_marker_fails_closed(self):
        marker = self.start(extra=True)
        with self.assertRaisesRegex(ValueError, "marker-only"):
            exact_marker(self.x.f.root, marker)

    def test_04_no_Github_frozen_buffer_means_zero_semantics(self):
        marker = self.start()
        with self.assertRaises(ValueError):
            frozen_trial(self.x.f.root, marker_commit=marker,
                         buffer_path=PREFIX + "/research_buffer.json")
        with self.assertRaises(ValueError):
            frozen_trial(self.x.f.root, marker_commit=marker,
                         buffer_path="data/ai_inbox/dossier_research/forbidden.json")

    def test_05_strict_research_schema_source_privacy_and_12_dimensions(self):
        marker = self.start()
        doc = copy.deepcopy(self.x.docs[0])
        a = doc["assignment"]
        a["research_marker_anchor_commit"] = marker
        a["research_marker_nonce"] = self.nonce
        item = {"assignment": {k: v for k, v in a.items()
                               if k not in ("research_marker_anchor_commit",
                                            "research_marker_nonce")},
                "group_sequence": a["group_sequence"],
                "item_index": a["item_index"], "appid": a["appid"],
                "old_year": doc["identity"]["original_work_release_year"]}
        r = validate_candidate(item, doc, marker_commit=marker, nonce=self.nonce)
        self.assertEqual(r["year_comparison"], "legacy_year_claim_matches_unverified")
        self.assertFalse(r["canonical_acceptance"])
        # New factual original year must not be overwritten by legacy old-year claim.
        item["old_year"] = (r["old_year_claim"] or 2000) + 1
        self.assertEqual(validate_candidate(
            item, doc, marker_commit=marker, nonce=self.nonce
        )["year_comparison"], "legacy_original_year_conflict_needs_comparison_adjudication")
        for edit in (
            lambda d: d["research_audit"]["dimension_survey"].pop(),
            lambda d: d["assignment"].update(appid="666"),
            lambda d: d["findings"][0].update(safe_neutral_synthesis="username: secret"),
            lambda d: d["observed_feedback"][0].update(parent_source_ref="rsource-999"),
        ):
            wrong = copy.deepcopy(doc)
            edit(wrong)
            with self.assertRaises(ValueError):
                validate_candidate(item, wrong, marker_commit=marker, nonce=self.nonce)

    def test_06_create_only_shadow_transport_raw_and_canonical_hashes(self):
        marker = self.start()
        doc = copy.deepcopy(self.x.docs[0])
        a = doc["assignment"]
        a["research_marker_anchor_commit"] = marker
        a["research_marker_nonce"] = self.nonce
        item = {"assignment": {k: v for k, v in a.items()
                               if k not in ("research_marker_anchor_commit",
                                            "research_marker_nonce")},
                "group_sequence": a["group_sequence"], "item_index": a["item_index"],
                "appid": a["appid"], "old_year": doc["identity"]["original_work_release_year"]}
        path = sandbox_output_path(item)
        self.assertTrue(path.startswith("reviews/dossier_shadow_offline/trials/"))
        self.assertNotIn("data/ai_inbox", path)
        self.x.f.save(path, doc)
        result_commit = self.x.f.commit("Synthetic shadow candidate ONLY")
        found = inspect_transport(self.x.f.root, trial={"marker_commit": marker,
                    "nonce": self.nonce}, item=item, result_commit=result_commit)
        self.assertEqual(found["status"], "submitted_unaccepted_shadow_only")
        self.assertEqual(found["result_commit"], result_commit)
        self.assertFalse(found["canonical_acceptance"])
        with self.assertRaisesRegex(ValueError, "collision"):
            inspect_transport(self.x.f.root, trial={"marker_commit": marker,
                    "nonce": self.nonce}, item=item, result_commit=result_commit,
                    expected_raw=b"DIFFERENT BYTES")
        self.x.f.save(path, {"schema": "MALICIOUS"})
        self.x.f.commit("Overwriting immutable sandbox result forbidden")
        with self.assertRaisesRegex(ValueError, "overwritten"):
            inspect_transport(self.x.f.root, trial={"marker_commit": marker,
                    "nonce": self.nonce}, item=item, result_commit=result_commit)

    def test_07_sandbox_result_extra_file_rejected_no_production_writes(self):
        marker = self.start()
        doc = copy.deepcopy(self.x.docs[0])
        a = doc["assignment"]
        a["research_marker_anchor_commit"] = marker
        a["research_marker_nonce"] = self.nonce
        item = {"assignment": {k: v for k, v in a.items()
                               if k not in ("research_marker_anchor_commit",
                                            "research_marker_nonce")},
                "group_sequence": a["group_sequence"], "item_index": a["item_index"],
                "appid": a["appid"], "old_year": doc["identity"]["original_work_release_year"]}
        self.x.f.save(sandbox_output_path(item), doc)
        self.x.f.save("data/production/bad.json", {"bad": True})
        commit = self.x.f.commit("Forbidden extra file")
        with self.assertRaisesRegex(ValueError, "create-only"):
            inspect_transport(self.x.f.root, trial={"marker_commit": marker,
                    "nonce": self.nonce}, item=item, result_commit=commit)

    def test_08_six_exact_indivisible_original_group_order_and_scope(self):
        decision = json.loads((Path(__file__).resolve().parents[1] /
            "reviews/dossier_shadow_offline/dossier_shadow_calibration_20261011_6x3_director_decision_v1.json").read_text("utf-8"))
        groups = [{"sequence": i, "group_sha256": "0" * 64,
                   "appids": [], "items": []} for i in range(1, 21)]
        for d in decision["scope"]["groups"]:
            groups[d["sequence"] - 1] = {**d, "items": [
                {"appid": v} for v in d["appids"]]}
        self.assertEqual(len(_three_by_six(decision, groups)), 6)
        altered = copy.deepcopy(decision)
        altered["scope"]["groups"][0]["appids"][0] = "9999"
        with self.assertRaisesRegex(ValueError, "group SHA"):
            _three_by_six(altered, groups)
        altered = copy.deepcopy(decision)
        altered["scope"]["groups"][2]["sequence"] = 8
        with self.assertRaises(ValueError):
            _three_by_six(altered, groups)


if __name__ == "__main__":
    unittest.main()
