#!/usr/bin/env python3
"""Only synthetic/adversarial tests. No external reviews or canonical writes."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

from dossier_shadow_pilot_cohort_preview import (
    SEED, PIN, WORK_BLOB, attested_rows, choose_cohort,
    source_differences, validate_frame,
)


def synthetic_frame():
    """Synthetic 20x3 source-identities with expected 6:14 binding split."""
    result = []
    for seq in range(1, 21):
        year = 2012 if seq in (1, 2, 3, 4, 5, 6) else 2023
        games = [
            {"appid": str(seq * 100 + offset), "work_title": "fake work",
             "original_work_year_binding": year,
             "baseline_git_blob_sha": ("%040x" % (seq * 3 + offset))}
            for offset in (1, 2, 3)
        ]
        result.append({
            "sequence": seq, "group_sha256": ("%064x" % seq),
            "writer_commit": ("%040x" % seq),
            "verified_actions_run": str(1000 + seq), "games": games,
        })
    return result


class CohortPreviewSyntheticTests(unittest.TestCase):
    def test_complete_frame_and_original_order(self):
        frame = synthetic_frame()
        selected, strata = choose_cohort(frame, "synthetic-snapshot")
        self.assertEqual(len(frame), 20)
        self.assertEqual(len(selected), 6)
        self.assertEqual(len({g["appid"] for row in selected for g in row["games"]}), 18)
        self.assertEqual([r["sequence"] for r in frame], list(range(1, 21)))
        self.assertEqual({key: len(value) for key, value in strata.items()},
                         {"has_pre_2015_work_year_binding": 6,
                          "no_pre_2015_work_year_binding": 14})
        self.assertEqual(sum(x["provisionally_selected"] for x in frame), 6)
        self.assertEqual([x["sequence"] for x in selected],
                         sorted(x["sequence"] for x in selected))

    def test_deterministic_hash_has_pinned_complete_material(self):
        frame = synthetic_frame()
        a, _ = choose_cohort(frame, "synthetic-snapshot")
        second_frame = synthetic_frame()
        b, _ = choose_cohort(second_frame, "synthetic-snapshot")
        self.assertEqual([x["sequence"] for x in a], [x["sequence"] for x in b])
        first = frame[0]
        material = "|".join((SEED, PIN, WORK_BLOB, "synthetic-snapshot",
                             "1", first["group_sha256"]))
        self.assertEqual(first["selection_sha256"],
                         hashlib.sha256(material.encode()).hexdigest())
        c, _ = choose_cohort(synthetic_frame(), "other-snapshot")
        hashes1 = [g["selection_sha256"] for g in frame]
        hashes2 = [g["selection_sha256"] for g in second_frame]
        self.assertNotEqual(hashes1, [g["selection_sha256"] for g in c])
        self.assertEqual(len(set(hashes2)), 20)

    def test_fail_closed_scope_order_duplicates_and_year(self):
        for mutation in (
            lambda f: f.pop(),
            lambda f: f[0].update(sequence=2),
            lambda f: f[0].update(group_sha256="not-sha"),
            lambda f: f[1]["games"][0].update(appid=f[0]["games"][0]["appid"]),
            lambda f: f[1]["games"][0].update(original_work_year_binding=None),
            lambda f: f[1]["games"].reverse() or f[1]["games"].pop(),
            lambda f: f[0].update(writer_commit="unknown"),
            lambda f: f[0]["games"][0].update(baseline_git_blob_sha="wrong"),
        ):
            frame = synthetic_frame()
            mutation(frame)
            with self.assertRaises(ValueError):
                validate_frame(frame)

    def test_frozen_strata_invariant_blocks_mutated_years(self):
        frame = synthetic_frame()
        frame[0]["games"][0]["original_work_year_binding"] = 2025
        frame[0]["games"][1]["original_work_year_binding"] = 2025
        frame[0]["games"][2]["original_work_year_binding"] = 2025
        with self.assertRaisesRegex(ValueError, "6_14"):
            choose_cohort(frame, "synthetic-snapshot")

    def test_attestation_only_full_exact_rows_pass(self):
        line = ("| {seq} | {ids} | accepted | yes | "
                "[x](https://github.com/owner/repo/commit/{writer}) | "
                "[{run}](https://github.com/owner/repo/actions/runs/{run}) | "
                "pass¹ | eligible² | `NONE` |")
        entries = []
        for seq in range(1, 21):
            entries.append(line.format(seq=seq, ids=", ".join(
                str(seq * 100 + i) for i in range(1, 4)),
                writer=("%040x" % seq), run=1000 + seq))
        self.assertEqual(len(attested_rows("\n".join(entries))), 20)
        with self.assertRaises(ValueError):
            attested_rows("\n".join(entries[:-1]))
        with self.assertRaises(ValueError):
            attested_rows("\n".join(entries + entries[:1]))
        with self.assertRaises(ValueError):
            attested_rows("\n".join(e.replace("eligible²", "not_verified")
                                    for e in entries))

    def test_absent_comparison_never_asserts_unchanged(self):
        with tempfile.TemporaryDirectory() as folder:
            comparison = source_differences(Path(folder), "refs/remotes/origin/main")
            self.assertEqual(comparison["comparison_status"], "unknown")
            self.assertNotIn("head_moved_from_pin", comparison)
            with self.assertRaises(ValueError):
                source_differences(Path(folder), "../../other")

    def test_category_evidence_not_inferred_from_titles_or_years(self):
        frame = synthetic_frame()
        frame[0]["games"][0]["work_title"] = "DLC / Remaster Russian"
        choose_cohort(frame, "synthetic-snapshot")
        self.assertNotIn("russian_evidence_verified", frame[0])
        self.assertNotIn("source_diversity_verified", frame[0])


if __name__ == "__main__":
    unittest.main()
