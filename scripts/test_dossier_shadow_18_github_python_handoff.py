#!/usr/bin/env python3
"""Offline synthetic Git handoff tests: no live Assembly or Research semantics."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import dossier_shadow_18_github_python_handoff as gh
import dossier_shadow_18_assembly_stage_b as stage
from dossier_shadow_research_trial_publish import EXPECTED_APPIDS
from test_dossier_shadow_18_assembly_stage_b import StageBJointGitTests


class GithubOriginalHandoffTests(unittest.TestCase):
    def setUp(self):
        self.fixture = StageBJointGitTests(methodName="test_01_original_blocked_but_separate_ready_18_order")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def issue_with_submissions(self):
        f = self.fixture
        submitted = {}
        for i, row in enumerate(f.items):
            if row["appid"] not in gh.FIXED_MISSING:
                submitted[row["appid"]] = f.research_result(i)
        f.issue()
        return submitted

    def test_01_pinned_18_exact_scope_and_original_missing(self):
        source = Path(__file__).resolve().parents[1] / "config/dossier_shadow_18_github_python_handoff_pins_v1.json"
        doc = json.loads(source.read_text("utf-8"))
        self.assertEqual(doc["original_research_introduction_commits"],
                         gh.FIXED_RESEARCH_COMMITS)
        self.assertEqual(set(doc["missing_research_appids"]), gh.FIXED_MISSING)
        self.assertEqual(set(EXPECTED_APPIDS),
                         set(gh.FIXED_RESEARCH_COMMITS) | gh.FIXED_MISSING)
        self.assertEqual(len(EXPECTED_APPIDS), 18)
        self.assertEqual(doc["assembly_marker_commit"], gh.FIXED_MARKER)
        self.assertEqual(doc["production_writes"], [])
        self.assertFalse(doc["scheduled_tasks"])
        self.assertFalse(doc["canonical_acceptance"])

    def test_02_canonical_python_14_ready_4_missing_under_mock_semantics(self):
        submitted = self.issue_with_submissions()
        f = self.fixture
        # Genuine fixture Git commits and original stage.inspect, only the
        # unavailable historic source audits and fixed real-SHA pins are mocked.
        with patch.object(gh, "FIXED_MARKER", f.assembly_marker), patch.object(
                gh, "checked", return_value={
                    "original_research_introduction_commits": submitted}):
            s = gh.readiness(f.root, Path("synthetic-pins"), stage)
        self.assertEqual([r["appid"] for r in s["rows"]], EXPECTED_APPIDS)
        self.assertEqual(s["ready_count"], 14)
        self.assertEqual(sum(r["status"] == "research_not_submitted"
                             for r in s["rows"]), 4)
        self.assertFalse(s["deep_ready"])
        self.assertEqual(s["semantic_attempts"], 0)

    def test_03_two_bad_Git_origins_item_local_B_C_still_run(self):
        submitted = self.issue_with_submissions()
        f = self.fixture
        # Wrong committed AppID/path simulates a transport-invalid submission,
        # not a shortcut around actual source provenance checks.
        culprit = "1517180"
        broken = dict(submitted)
        broken["2124120"] = submitted[culprit]
        broken["2138710"] = submitted[culprit]
        with patch.object(gh, "FIXED_MARKER", f.assembly_marker), patch.object(
                gh, "checked", return_value={
                    "original_research_introduction_commits": broken}):
            s = gh.readiness(f.root, Path("synthetic-pins"), stage)
        statuses = {r["appid"]:r["status"] for r in s["rows"]}
        self.assertEqual(statuses["2124120"], "research_transport_invalid")
        self.assertEqual(statuses["2138710"], "research_transport_invalid")
        self.assertEqual(statuses["213610"], "ready")
        self.assertEqual(s["ready_count"], 12)
        self.assertEqual(sum(v == "research_not_submitted"
                             for v in statuses.values()), 4)
        self.assertTrue(all(not r["attempt_consumed"] for r in s["rows"]))

    def test_04_single_file_typed_Git_submission_and_rewrite_rejected(self):
        f = self.fixture
        f.issue()
        handoff_branch = "handoff/dossier-shadow-18-assembly-typed"
        path_prefix = stage.PREFIX.replace("/trials/", "/handoff/")
        f.git("checkout", "-b", handoff_branch)
        path = path_prefix + "/1517180.json"
        semantic = {"outcome": "runtime_or_tool_failure",
                    "payload": {"status": "runtime_or_tool_failure",
                                "gap_id": None, "source_ref": None,
                                "field_or_dimension": None,
                                "safe_diagnostic": "Synthetic offline tool failure",
                                "requires_github_classification": True,
                                "normal_first_pass_attempt_consumed": False},
                    "supplemental_operations": []}
        f.put(path, semantic)
        commit = f.commit("Synthetic only typed create-once semantic input")
        f.git("update-ref", "refs/remotes/origin/" + handoff_branch, commit)
        f.git("checkout", stage.BRANCH)
        pins = {"submission_branch": handoff_branch,
                "submission_namespace": path_prefix}
        self.assertEqual(gh.semantic_submission(
            f.root, stage, pins, "1517180", commit), semantic)
        with self.assertRaisesRegex(ValueError, "no source Research"):
            gh.semantic_submission(f.root, stage, pins, "1508750", commit)
        f.git("checkout", handoff_branch)
        altered = dict(semantic)
        altered["forged_marker"] = True
        f.put(path, altered)
        f.commit("Synthetic malicious rewritten semantic bytes")
        f.git("update-ref", "refs/remotes/origin/" + handoff_branch, f.head())
        f.git("checkout", stage.BRANCH)
        with self.assertRaises(ValueError):
            gh.semantic_submission(f.root, stage, pins, "1517180", commit)

    def test_05_no_reordering_of_preceding_ready_but_missing_invalid_skippable(self):
        rows = [
            {"appid": "1508750", "status": "research_not_submitted"},
            {"appid": "1517180", "status": "ready"},
            {"appid": "1533420", "status": "ready"},
        ]
        gh.original_order_gate({"rows": rows}, "1517180")
        with self.assertRaisesRegex(ValueError, "earlier ready"):
            gh.original_order_gate({"rows": rows}, "1533420")
        rows[1]["status"] = "candidate_already_submitted"
        gh.original_order_gate({"rows": rows}, "1533420")
        rows[1]["status"] = "research_transport_invalid"
        gh.original_order_gate({"rows": rows}, "1533420")
        with self.assertRaisesRegex(ValueError, "foreign AppID"):
            gh.original_order_gate({"rows": rows}, "999999999")


if __name__ == "__main__":
    unittest.main()
