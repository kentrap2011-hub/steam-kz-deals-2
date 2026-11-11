#!/usr/bin/env python3
"""Focused real pinned-source + adversarial fresh6 preparation scope tests.

Positive test checks actual committed source blobs; mutated documents are
synthetic negative guard tests, never semantic player-feedback verification.
"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import dossier_notes_v2_fresh6_preflight as gate


def source_objects():
    c = json.loads(gate.CONTRACT.read_text(encoding="utf-8"))
    p = c["provenance"]
    repo, sha = ROOT, p["main_commit"]
    idx = json.loads(gate.read_pinned(
        repo, sha, p["worker_index_path"], p["worker_index_blob_sha"]))
    docs = {
        group["sequence"]: json.loads(gate.read_pinned(
            repo, sha, group["path"], group["blob_sha"]))
        for group in p["group_descriptors"]
    }
    old = json.loads(gate.git(
        repo, "show", f"{sha}:config/dossier_research_notes_v2_contract.json").stdout)
    return c, idx, docs, old


class FreshSixScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = source_objects()

    def data(self):
        return copy.deepcopy(self.frozen)

    def assert_blocks(self, index, change):
        c, work, docs, old = self.data()
        change(c, work, docs, old)
        with self.assertRaisesRegex(gate.ScopeBlocked, ".+"):
            gate.validate_scope(c, work, docs, old)

    def test_real_pinned_main_and_baselines_are_read_only(self):
        result = gate.inspect()
        self.assertEqual(result["status"], "scope_verified_preparation_only")
        self.assertEqual(result["candidate_count"], 6)
        self.assertEqual(result["original18_intersection"], [])
        self.assertIs(result["owner_dispatch_authorized"], False)
        self.assertIs(result["semantic_execution_authorized"], False)
        self.assertIs(result["canonical_acceptance"], False)

    def test_exact_6_source_matches_both_prepared_groups(self):
        result = gate.validate_scope(*self.data())
        self.assertEqual(result["appids"],
                         ["1000010", "102600", "1029690", "49520", "499180", "501590"])

    def test_foreign_game_or_old_original18_membership_fails(self):
        self.assert_blocks(0, lambda c, i, d, o:
                           c["candidates"][0].update(appid="2138710"))

    def test_swapped_exact_edition_title_fails(self):
        self.assert_blocks(0, lambda c, i, d, o:
                           c["candidates"][4].update(title="Braid"))

    def test_forged_appid_or_source_index_fails(self):
        self.assert_blocks(0, lambda c, i, d, o:
                           c["candidates"][5].update(appid="501591"))

    def test_wrong_descriptor_source_item_title_fails(self):
        self.assert_blocks(0, lambda c, i, d, o:
                           d[70]["items"][1].update(title="Braid"))

    def test_reordering_candidates_fails(self):
        def change(c, *_):
            c["candidates"][0], c["candidates"][1] = c["candidates"][1], c["candidates"][0]
        self.assert_blocks(0, change)

    def test_source_group_hash_mismatch_fails(self):
        self.assert_blocks(0, lambda c, i, d, o:
                           d[70].update(group_sha256="0" * 64))

    def test_source_snapshot_drift_fails(self):
        self.assert_blocks(0, lambda c, i, d, o:
                           i.update(snapshot_id="0" * 64))

    def test_cannot_enable_semantics_or_writer(self):
        for flag in gate.OFF_FLAGS:
            with self.subTest(flag=flag):
                self.assert_blocks(0, lambda c, i, d, o, f=flag:
                                   c.update({f: True}))

    def test_source_path_and_wrong_blob_pins_fail(self):
        c, _, _, _ = self.data()
        pin = c["provenance"]
        with self.assertRaises(gate.ScopeBlocked):
            gate.read_pinned(ROOT, pin["main_commit"],
                             pin["group_descriptors"][0]["path"], "0" * 40)
        with self.assertRaises(gate.ScopeBlocked):
            gate.read_pinned(ROOT, pin["main_commit"], "../outside", "0" * 40)

    def test_baseline_three_existing_three_missing(self):
        c, _, _, _ = self.data()
        self.assertEqual(sum(x["baseline_blob_sha"] is not None for x in c["candidates"]), 3)
        self.assertEqual(sum(x["baseline_blob_sha"] is None for x in c["candidates"]), 3)


if __name__ == "__main__":
    unittest.main()
