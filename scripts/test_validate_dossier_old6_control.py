#!/usr/bin/env python3
"""Offline negative and contract tests; no semantic research or GitHub writes."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import validate_dossier_old6_control as v


class StrictSixControlTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "manifest.json"
        self.doc = json.loads(v.CONFIG.read_text(encoding="utf-8"))
        self.patcher = patch.object(v, "CONFIG", self.path)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def verify(self, expected=True):
        self.path.write_text(json.dumps(self.doc), encoding="utf-8")
        if expected:
            self.assertEqual(len(v.config()["work_groups"]), 2)
        else:
            with self.assertRaises(ValueError):
                v.config()

    def test_exact_scope_passes(self):
        self.verify()

    def test_new_research_mandatory(self):
        self.doc["minimum_fresh_research"] = False
        self.verify(False)

    def test_cached_old_reuse_rejected(self):
        self.doc["reuse_prior_strict_cache"] = True
        self.verify(False)

    def test_reusing_lean_or_notes_rejected(self):
        self.doc["reuse_lean_or_notes_v2_research"] = True
        self.verify(False)

    def test_canonical_ingest_rejected(self):
        self.doc["canonical_cache_write_allowed"] = True
        self.verify(False)

    def test_recurring_run_rejected(self):
        self.doc["recurring_or_background_execution_allowed"] = True
        self.verify(False)

    def test_no_spontaneous_semantic_activation(self):
        self.doc["semantic_launch_authorized_by_source_pr_alone"] = True
        self.verify(False)

    def test_substitute_edition_rejected(self):
        self.doc["work_groups"][1]["items"][1]["title"] = "Braid"
        self.verify(False)

    def test_swapped_items_rejected(self):
        items = self.doc["work_groups"][0]["items"]
        items[0], items[1] = items[1], items[0]
        self.verify(False)

    def test_ttl_drift_rejected(self):
        self.doc["ttl_days"] = 365
        self.verify(False)

    def test_bogus_source_pin_rejected(self):
        self.doc["source_main_sha"] = "x" * 40
        self.verify(False)

    def test_no_marker_no_candidate_acceptance(self):
        self.path.write_text(json.dumps(self.doc), encoding="utf-8")
        with patch.object(v, "ROOT", Path(self.temp.name)):
            with self.assertRaisesRegex(ValueError, "missing create-only run-start marker"):
                v.validate_outputs()

    def test_git_marker_exact_one_add(self):
        root = Path(self.temp.name) / "sandbox"
        root.mkdir()
        def git(*args):
            result = subprocess.run(["git", "-C", str(root), *args],
                                    check=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
            return result.stdout.strip()
        git("init", "-q")
        git("config", "user.name", "Strict Six Test")
        git("config", "user.email", "strict-six@example.invalid")
        (root / "README.md").write_text("base", encoding="utf-8")
        git("add", "README.md")
        git("commit", "-qm", "base")
        base = git("rev-parse", "HEAD")
        marker_rel = v.RESULT_ROOT + "/run_start.json"
        marker_path = root / marker_rel
        marker_path.parent.mkdir(parents=True)
        marker_path.write_text('{"schema":"marker"}', encoding="utf-8")
        git("add", marker_rel)
        git("commit", "-qm", "one marker")
        marker = git("rev-parse", "HEAD")
        with patch.object(v, "ROOT", root):
            self.assertEqual(v._one_add_commit(marker_rel), (marker, base))
            malformed = v.RESULT_ROOT + "/App_1000010.json"
            (root / malformed).write_text("{}", encoding="utf-8")
            (root / (v.RESULT_ROOT + "/extra.txt")).write_text("extra", encoding="utf-8")
            git("add", malformed, v.RESULT_ROOT + "/extra.txt")
            git("commit", "-qm", "invalid two-path candidate")
            with self.assertRaisesRegex(ValueError, "exactly one path"):
                v._one_add_commit(malformed)


if __name__ == "__main__":
    unittest.main()
