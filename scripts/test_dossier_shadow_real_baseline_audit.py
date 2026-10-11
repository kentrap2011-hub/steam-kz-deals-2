#!/usr/bin/env python3
"""Adversarial, entirely synthetic tests for the read-only audit wrapper."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from dossier_shadow_real_baseline_audit import (
    AUDIT, original_plan, reason_code, writer_receipts,
)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args]).decode().strip()


class RealBaselineAuditTests(unittest.TestCase):
    def manifest(self):
        groups = [
            {"sequence": 1, "appids": ["1", "2", "3"],
             "items": [{"appid": str(x)} for x in (1, 2, 3)],
             "group_sha256": "a"},
            {"sequence": 2, "appids": ["4", "5", "6"],
             "items": [{"appid": str(x)} for x in (4, 5, 6)],
             "group_sha256": "b"},
        ]
        return {
            "submission_group_plan": {"group_count": 2, "groups": groups},
            "group_progress": {"groups": [
                {"sequence": 1, "state": "accepted", "group_sha256": "a"},
                {"sequence": 2, "state": "pending", "group_sha256": "b"},
            ]},
        }

    def test_entire_frozen_frame_and_only_canonical_accepted_scope(self):
        doc = self.manifest()
        self.assertEqual([x[0]["sequence"] for x in original_plan(doc)], [1])
        self.assertEqual([x[0]["sequence"] for x in original_plan(doc, False)], [1, 2])

    def test_reject_mutated_plan_duplicate_identity_and_order(self):
        for mutation in (
            lambda m: m["submission_group_plan"].update(group_count=3),
            lambda m: m["submission_group_plan"]["groups"][0].update(
                appids=["1", "1", "3"]),
            lambda m: m["group_progress"]["groups"][0].update(sequence=2),
            lambda m: m["group_progress"]["groups"][0].update(group_sha256="fake"),
        ):
            doc = self.manifest()
            mutation(doc)
            with self.assertRaisesRegex(ValueError, "MISMATCH"):
                original_plan(doc)

    def test_receipt_must_be_historically_appended_not_just_present_at_head(self):
        with tempfile.TemporaryDirectory(prefix="dossier-shadow-test-") as tmp:
            root = Path(tmp)
            git(root, "init", "-q")
            git(root, "config", "user.email", "test@example.invalid")
            git(root, "config", "user.name", "Synthetic test")
            path = root / AUDIT
            path.parent.mkdir(parents=True)
            path.write_text('{"schema":"unrelated"}\n', encoding="utf-8")
            git(root, "add", AUDIT)
            git(root, "commit", "-qm", "synthetic initial audit")
            record = {
                "authority_sequence": 7, "authority_snapshot_id": "synthetic",
                "outcome": "dossier_candidate_accepted_current_snapshot",
            }
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, separators=(",", ":")) + "\n")
            git(root, "add", AUDIT)
            git(root, "commit", "-qm", "synthetic writer append")
            head = git(root, "rev-parse", "HEAD")
            rows = writer_receipts(root, head, "synthetic")
            self.assertEqual(set(rows), {7})
            self.assertEqual(rows[7][0], head)
            # A printed current file is not a historical newly-appended receipt.
            path.write_text('{"schema":"replaced"}\n', encoding="utf-8")
            git(root, "add", AUDIT)
            git(root, "commit", "-qm", "synthetic rewrite")
            with self.assertRaisesRegex(ValueError, "AUDIT_NOT_APPEND_ONLY"):
                writer_receipts(root, git(root, "rev-parse", "HEAD"), "synthetic")

    def test_structured_fail_closed_reasons(self):
        self.assertEqual(reason_code(ValueError("missing historical writer audit")),
                         "HISTORICAL_WRITER_RECEIPT_NOT_PROVEN")
        self.assertEqual(reason_code(ValueError("wrong legacy cache blob")),
                         "CACHE_BINDING_NOT_PROVEN")


if __name__ == "__main__":
    unittest.main()
