#!/usr/bin/env python3
"""Disposable Git regression cases for the six exact-groups offline adapter."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dossier_shadow_18_assembly_sandbox import (
    _decision, _frozen_authority, _inspect_group, inspect_offline_pilot,
    AUTHORITY_SCHEMA, SEQUENCES,
)
from dossier_two_stage_contract_guard import canonical_sha256
from dossier_two_stage_staging import blob, git
from test_dossier_two_stage_async_buffer import AsyncFixture


class Sandbox18AssemblyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.addCleanup(temp.cleanup)
        self.x = AsyncFixture(temp.name)
        self.x.preauthorize_assembly()
        self.root = self.x.f.root
        git(self.root, "config", "gc.auto", "0")
        git(self.root, "config", "maintenance.auto", "false")
        # Keep offline safety marker untracked and out of create-only Git commits.
        exclude = Path(self.root) / ".git/info/exclude"
        exclude.write_text(exclude.read_text(encoding="utf-8") +
                           "\n.dossier-final-offline-fixture\n", encoding="utf-8")
        (Path(self.root) / ".dossier-final-offline-fixture").touch()
        desc = self.x.f.descriptor
        self.group = {"sequence": 1, "group_sha256": desc["group_sha256"],
                      "appids": desc["appids"]}
        self.authority_group = {
            "sequence": 1, "research_marker_commit": self.x.f.marker,
            "research_buffer_path": self.x.rbuffer["path"],
            "assembly_marker_commit": self.x.amarker,
            "assembly_buffer_path": self.x.abuffer["path"],
        }

    def inspect(self, commits=None, group=None, auth=None):
        return _inspect_group(self.root, group or self.group,
                              auth or self.authority_group, commits or {})

    def test_01_no_pilot_authority_is_18_not_measured_zero_attempts(self):
        result = inspect_offline_pilot(self.root, offline_fixture=True)
        self.assertEqual(result["status"], "waiting_for_authorized_research")
        self.assertEqual(result["counts"]["frozen_games"], 18)
        self.assertEqual(len(result["per_game"]), 18)
        self.assertEqual([x["sequence"] for x in _decision()["scope"]["groups"]],
                         list(SEQUENCES))
        self.assertTrue(all(x["research_elapsed_ms"] is None and
                            x["assembly_elapsed_ms"] is None and
                            x["pair_quality_status"] == "not_measured" for x in result["per_game"]))
        self.assertFalse(result["semantic_execution_permitted"])
        self.assertEqual(result["production_writes"], [])

    def test_02_disposable_git_only_no_live_authority_or_canonical_paths(self):
        (Path(self.root) / ".dossier-final-offline-fixture").unlink()
        with self.assertRaises(ValueError):
            inspect_offline_pilot(self.root, offline_fixture=True)
        with self.assertRaises(ValueError):
            inspect_offline_pilot(self.root, offline_fixture=False)

    def test_03_missing_A_does_not_block_B_C_original_order(self):
        b = self.x.research_submit(1)
        c = self.x.research_submit(2)
        decisions = self.inspect({self.x.apaths[1]: b, self.x.apaths[2]: c})
        self.assertEqual([x["status"] for x in decisions],
                         ["research_not_submitted", "ready", "ready"], str(decisions))
        self.assertFalse(any(x["attempt_consumed"] for x in decisions))
        for d in decisions[1:]:
            rt = d["work"]["research_transport"]
            self.assertEqual(len(rt), 9)
            self.assertEqual(rt["research_package_blob_sha"],
                             blob(self.root, rt["research_package_git_commit"],
                                  rt["research_package_path"]))
            self.assertFalse(d["work"]["canonical_dossier_accepted"])

    def test_04_wrong_original_research_commit_only_exact_item_invalid(self):
        b = self.x.research_submit(1)
        decisions = self.inspect({self.x.apaths[0]: b, self.x.apaths[1]: b})
        self.assertEqual([d["status"] for d in decisions],
                         ["research_transport_invalid", "ready", "research_not_submitted"], str(decisions))
        self.assertTrue(all(d["attempt_consumed"] is False for d in decisions))

    def test_05_tampered_research_original_git_blob_rejected_without_rebind(self):
        r = self.x.research_submit(0)
        path = self.x.docs[0]["assignment"]
        from dossier_two_stage_staging import receipt_paths
        transport = receipt_paths(path)["candidate"]
        original_blob = blob(self.root, r, transport)
        self.x.f.save(transport, {"changed": "do not rebind"})
        self.x.f.commit("Synthetic adversarial rewrite after original Research commit")
        d = self.inspect({self.x.apaths[0]: r})
        self.assertEqual(d[0]["status"], "research_transport_invalid")
        self.assertFalse(d[0]["attempt_consumed"])
        # Presemantic and downstream strict final bridge both reject HEAD rewrite.
        self.assertNotEqual(blob(self.root, "HEAD", transport), original_blob)

    def test_06_forged_marker_and_stale_group_sha_fail_closed(self):
        bad = copy.deepcopy(self.authority_group)
        bad["assembly_marker_commit"] = self.x.f.marker  # Wrong marker namespace.
        with self.assertRaises(ValueError):
            self.inspect(auth=bad)
        other = copy.deepcopy(self.group)
        other["group_sha256"] = "a" * 64
        with self.assertRaises(ValueError):
            self.inspect(group=other)

    def test_07_no_source_group_replacement_or_unpinned_reorder(self):
        different = copy.deepcopy(self.group)
        different["appids"] = list(reversed(different["appids"]))
        with self.assertRaises(ValueError):
            self.inspect(group=different)
        bad = dict(self.authority_group)
        bad["unexpected_retry"] = True
        with self.assertRaises(ValueError):
            self.inspect(auth=bad)
        with self.assertRaises(ValueError):
            self.inspect({"data/production/visual/current.json": "a" * 40})

    def _authority_ref(self, mutate=None):
        decision = _decision()
        groups = []
        for g in decision["scope"]["groups"]:
            groups.append({**self.authority_group, "sequence": g["sequence"]})
        record = {
            "schema": AUTHORITY_SCHEMA, "trial_id": decision["trial_id"],
            "director_decision_sha256": canonical_sha256(decision),
            "group_order": list(SEQUENCES), "groups": groups,
            "sandbox_only": True, "external_semantic_authorized": False,
            "production_writes": [], "scheduled_tasks_mutated": False,
        }
        if mutate:
            mutate(record)
        path = "reviews/dossier_shadow_offline/synthetic-18-sandbox-authority.json"
        self.x.f.save(path, record)
        commit = self.x.f.commit("Synthetic offline authority lock (not actual Director approval)")
        return {"commit": commit, "path": path,
                "git_blob_sha": blob(self.root, commit, path)}

    def test_08_unpinned_or_mismatched_authority_ref_never_accepted(self):
        ref = self._authority_ref()
        self.assertEqual(_frozen_authority(self.root, ref, _decision())["schema"],
                         AUTHORITY_SCHEMA)
        wrong = dict(ref, git_blob_sha="0" * 40)
        with self.assertRaises(ValueError):
            _frozen_authority(self.root, wrong, _decision())
        self.x.f.save(ref["path"], {"forged": True})
        self.x.f.commit("Rewrite synthetic authority after frozen original")
        with self.assertRaises(ValueError):
            _frozen_authority(self.root, ref, _decision())

    def test_09_scope_immutability_and_six_group_denominator_with_partial_Research(self):
        ref = self._authority_ref()
        # Test double ONLY: actual per-group transport is exercised by tests 3-7;
        # six different real pilot markers are not present and must not be invented.
        def simulated_group(repo, expected, authority, commits):
            return [{"work_path": f"fixture:{i}",
                     "status": ("ready" if expected["sequence"] == 8 and i == 1
                                else "research_not_submitted"),
                     "attempt_consumed": False,
                     **({"work": {"research_transport": {"fixture": True}}}
                        if expected["sequence"] == 8 and i == 1 else {})}
                    for i in range(3)]
        with patch("dossier_shadow_18_assembly_sandbox._inspect_group", simulated_group):
            plan = inspect_offline_pilot(self.root, authority_ref=ref,
                                         submitted_commits={}, offline_fixture=True)
        self.assertEqual(plan["status"], "sandbox_assembly_invocation_ready")
        self.assertFalse(plan["semantic_execution_permitted"])
        self.assertEqual(plan["counts"]["assembly_transport_ready"], 1)
        self.assertEqual(plan["counts"]["research_not_submitted_or_unproven"], 17)
        self.assertEqual(len(plan["per_game"]), 18)
        self.assertEqual([(x["sequence"], x["denominator"]) for x in plan["groups"]],
                         [(seq, 3) for seq in SEQUENCES])

    def test_10_wrong_writer_proof_privacy_and_group_atomicity_remain_strict(self):
        # Existing full-history writer, source-safe A/B/C and final group tests
        # run independently in the PR-only workflow; no simulated evidence here.
        from dossier_shadow_quality_review_gate import _evaluate_rows
        frame = {"trial_id": "synthetic-trial", "groups": [{
            "sequence": 1, "group_sha256": "b" * 64,
            "games": [{"appid": a, "title": "Synthetic", "original_work_year": 2000}
                      for a in ("11", "12", "13")]
        }]}
        gate = _evaluate_rows(frame, {}, set(), set(), {})
        self.assertEqual(gate["cohort"]["not_measured"], 3)
        self.assertEqual(gate["cohort"]["historical_baseline_proven_games"], 0)
        self.assertFalse(gate["quality_verified"])
        self.assertIsNone(gate["approved_stop_thresholds"])


if __name__ == "__main__":
    unittest.main()
