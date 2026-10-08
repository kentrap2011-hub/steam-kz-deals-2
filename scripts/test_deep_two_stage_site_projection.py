#!/usr/bin/env python3
"""Bounded frozen Deep site projection regressions; no production mutation."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import deep_two_stage_site_projection as projection


class SiteProjectionTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = {
            "contract": "DEEP-STAGE1-WORK-V1", "eligible_work_ids": ["w1"],
            "items": [{"work_id": "w1", "family_id": "family-1", "appid": "101"}],
        }
        self.stage1 = {
            "contract": "DEEP-STAGE1-STATE-V1", "entries": {},
            "progress": {"total_eligible": 1, "completed_fit": 0,
                         "completed_not_fit": 0, "pending": 1,
                         "diagnostic_incomplete": 0,
                         "last_attempt_at_utc": None,
                         "last_successful_result_at_utc": None},
        }
        self.stage2 = {
            "contract": "DEEP-STAGE2-STATE-V1", "entries": {},
            "progress": {"stage1_fit_eligible": 0, "calibrated": 0,
                         "awaiting_calibration": 0, "diagnostic_incomplete": 0,
                         "last_attempt_at_utc": None,
                         "last_successful_calibration_at_utc": None},
        }
        self.game = {
            "id": "family-1", "family_id": "family-1", "appid": "101",
            "title": "Example", "dossier_stage_state": "accepted",
            "wishlist_bonus_0_or_4": 4, "purchase_score_0_40": 31.1,
            "total_score": 99, "personal_score": 59, "score_breakdown": {"total_score": 99},
            "fast_stage_state": "completed", "priority_rank": 7,
        }
        self.dossier = {
            "dossier_total_current_scope": 2, "dossier_accepted_count": 1,
            "dossier_pending_count": 1, "dossier_failed_or_recovery_count": 0,
            "dossier_last_write_at_utc": "2026-10-08T10:00:00+00:00",
        }

    def visual(self):
        return {"items": [copy.deepcopy(self.game)],
                "processing_status": copy.deepcopy(self.dossier)}

    def project(self):
        return projection.project_visual(
            self.visual(), stage1_work=self.work, stage1_state=self.stage1,
            stage2_state=self.stage2, root=self.root)

    def accept_stage1(self, outcome="analyzed_fit"):
        result = {
            "contract": "DEEP-STAGE1-RESULT-V1", "work_id": "w1",
            "family_id": "family-1", "appid": "101", "outcome": outcome,
            "profile_semantic_sha256": "p", "dossier_content_sha256": "d",
            "summary_ru": "Вывод о конкретной игре",
            "positives": [{"finding_id": "p1", "text_ru": "Продуманная система"}],
            "negatives": [{"finding_id": "n1", "text_ru": "Монотонный темп"}],
            "nuances": [{"finding_id": "o1", "text_ru": "Много дополнительных режимов"}],
            "point_breakdown": [{"label_ru": "Боевая глубина",
                                 "direction": "positive", "points": 46.2, "finding_refs": ["p1"]}],
            "provisional_deep_fit_score_0_56": 46.2 if outcome == "analyzed_fit" else None,
        }
        rel = Path("data/cache/deep_stage1_results/result.json")
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        contents = json.dumps(result, ensure_ascii=False).encode("utf-8")
        path.write_bytes(contents)
        sha = hashlib.sha256(contents).hexdigest()
        self.stage1["entries"]["w1"] = {
            "work_id": "w1", "family_id": "family-1", "appid": "101",
            "status": "accepted", "accepted": True, "outcome": outcome,
            "profile_semantic_sha256": "p", "dossier_content_sha256": "d",
            "accepted_result_path": str(rel), "accepted_result_sha256": sha,
        }
        self.work["items"] = []
        self.stage1["progress"].update({
            "completed_fit": int(outcome == "analyzed_fit"),
            "completed_not_fit": int(outcome == "analyzed_not_fit"),
            "diagnostic_incomplete": int(outcome == "analysis_incomplete"),
            "pending": 0, "last_attempt_at_utc": "2026-10-08T12:00:00Z",
            "last_successful_result_at_utc": "2026-10-08T12:00:00Z",
        })
        return sha

    def test_pending_never_falls_back_to_fast_or_provisional(self):
        projected = self.project()
        game = projected["items"][0]
        self.assertEqual(game["stage1_status"], "pending")
        self.assertEqual(game["stage2_status"], "not_eligible")
        self.assertIsNone(game["personal_quality_score_0_60"])
        self.assertIsNone(game["total_score_0_100"])
        self.assertNotIn("total_score", game)
        self.assertNotIn("score_breakdown", game)
        self.assertEqual(projected["processing_status"]["deep_stage1"]["pending"], 1)
        self.assertEqual(projected["processing_status"]["dossier"]["progress_percent"], 50)
        # No fabricated success: last Dossier write can be a failed attempt.
        self.assertIsNone(projected["processing_status"]["dossier"]["last_successful_result_at_utc"])
        self.assertEqual(projected["processing_status"]["deep_stage1"]["progress_percent"], 0)

    def test_stage1_provisional_detail_only_until_calibrated(self):
        self.accept_stage1()
        p = self.project()
        game = p["items"][0]
        self.assertEqual(game["stage1_status"], "completed_fit")
        self.assertEqual(game["stage2_status"], "awaiting_calibration")
        self.assertEqual(game["stage1_provisional_deep_fit_score_0_56"], 46.2)
        self.assertEqual(game["stage1_point_breakdown"][0]["label_ru"], "Боевая глубина")
        self.assertEqual(game["stage1_point_breakdown"][0]["finding_reasons_ru"], ["Продуманная система"])
        self.assertIsNone(game["personal_quality_score_0_60"])
        self.assertIsNone(game["total_score_0_100"])
        self.assertNotIn("total_score", game)
        self.assertEqual(p["processing_status"]["deep_stage1"]["completed"], 1)

    def test_calibrated_math_two_decimals_and_neighbors(self):
        sha = self.accept_stage1()
        self.stage2["entries"]["calibration-1"] = {
            "stage1_work_id": "w1", "stage1_result_sha256": sha,
            "profile_semantic_sha256": "p", "status": "calibrated",
            "calibrated_deep_fit_score_0_56": 47.03,
            "comparisons": [{"anchor_id": "nearby-1", "relation": "near_tie_target_above",
                             "reasons_ru": ["Чуть увереннее в механиках"]}],
            "why_stage2_changed_ru": "Лучше ближайшего соседа",
            "why_above_ru": ["Больше вариативности"],
            "why_below_ru": ["Слабее по темпу"],
        }
        self.stage2["progress"].update({
            "stage1_fit_eligible": 1, "calibrated": 1,
            "last_attempt_at_utc": "2026-10-08T13:00:00Z",
            "last_successful_calibration_at_utc": "2026-10-08T13:00:00Z",
        })
        p = self.project()
        g = p["items"][0]
        self.assertEqual(g["stage2_status"], "calibrated")
        self.assertEqual(g["stage2_calibrated_deep_fit_score_0_56"], 47.03)
        self.assertEqual(g["stage2_calibration_delta"], .83)
        self.assertEqual(g["personal_quality_score_0_60"], 51.03)
        self.assertEqual(g["purchase_score_0_40"], 31.1)
        self.assertEqual(g["total_score_0_100"], 82.13)
        self.assertEqual(g["total_score"], 82.13)
        self.assertEqual(g["stage2_neighbor_comparisons"][0]["relation"], "near_tie_target_above")
        self.assertEqual(p["processing_status"]["deep_stage2"]["progress_percent"], 100.0)

    def test_stage1_not_fit_not_stage2(self):
        self.accept_stage1("analyzed_not_fit")
        g = self.project()["items"][0]
        self.assertEqual(g["stage1_status"], "completed_not_fit")
        self.assertEqual(g["stage2_status"], "not_eligible")
        self.assertIsNone(g["total_score_0_100"])

    def test_stage2_diagnostic_does_not_show_score(self):
        sha = self.accept_stage1()
        self.stage2["entries"]["calibration-1"] = {
            "stage1_work_id": "w1", "stage1_result_sha256": sha,
            "profile_semantic_sha256": "p", "status": "calibration_incomplete",
        }
        g = self.project()["items"][0]
        self.assertEqual(g["stage2_status"], "diagnostic_incomplete")
        self.assertIsNone(g["personal_quality_score_0_60"])

    def test_invalid_bindings_and_scores_fail_closed(self):
        self.accept_stage1()
        self.stage1["entries"]["w1"]["accepted_result_sha256"] = "0"*64
        with self.assertRaisesRegex(projection.ProjectionError, "bytes"):
            self.project()
        self.stage1["entries"]["w1"]["accepted_result_sha256"] = hashlib.sha256(
            (self.root/"data/cache/deep_stage1_results/result.json").read_bytes()).hexdigest()
        self.game["wishlist_bonus_0_or_4"] = 3
        with self.assertRaisesRegex(projection.ProjectionError, "Wishlist"):
            self.project()
        self.game["wishlist_bonus_0_or_4"] = 4
        self.stage1["progress"]["pending"] = 1
        with self.assertRaisesRegex(projection.ProjectionError, "stale Stage-1"):
            self.project()


if __name__ == "__main__":
    unittest.main()
