#!/usr/bin/env python3
"""Contract and acceptance regressions for the complete Director forward task page."""
import copy
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site_tasks as tasks


class SiteTasksTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads((ROOT / "config/director_task_plan.json").read_text(encoding="utf-8"))
        cls.board = (ROOT / "DIRECTOR_TASK_BOARD.md").read_text(encoding="utf-8")
        cls.deep = json.loads((ROOT / "config/deep_two_stage_dependency_map.json").read_text(encoding="utf-8"))

    def build(self, plan=None):
        return tasks.build_payload(
            plan or self.plan, self.board, self.deep,
            now=datetime(2026, 10, 8, 12, tzinfo=timezone.utc),
        )

    def test_full_forward_backlog_and_mobile_nav(self):
        payload = self.build()
        self.assertEqual(payload["contract"], "SITE-DIRECTOR-TASKS-PUBLIC-V1")
        counts = {g["status"]: g["count"] for g in payload["groups"]}
        self.assertGreaterEqual(counts["active"], 4)
        self.assertGreaterEqual(counts["planned"], 8)
        self.assertGreaterEqual(counts["blocked"], 2)
        self.assertEqual(sum(counts[s] for s in ("active", "planned", "blocked")), payload["known_forward_count"])
        by_id = {t["id"]: t for group in payload["groups"] for t in group["tasks"]}
        for tid in ("site-tasks", "deep-stage1", "steam-50-top100", "owned-dlc",
                    "deep-ranking", "deep-site", "deep-cutover", "steam-prefilter",
                    "steam-error-watch", "giveaway-decouple", "giveaway-itad",
                    "architecture-cleanup"):
            self.assertIn(tid, by_id)
        self.assertIsNone(by_id["deep-site"]["worker_slot"])
        self.assertEqual(by_id["steam-50-top100"]["order"]["position"], 1)
        self.assertEqual(by_id["owned-dlc"]["order"]["position"], 2)
        self.assertEqual(by_id["deep-cutover"]["status"], "blocked")
        self.assertEqual(len(by_id["deep-cutover"]["depends_on"]), 4)
        for entry in by_id.values():
            for field in ("goal", "status", "effort", "effort_reason", "urgency",
                          "urgency_reason", "updated_on", "updated_at_utc"):
                self.assertTrue(entry[field], (entry["id"], field))
            self.assertNotIn("task_file", entry)
            self.assertNotIn("secret", str(entry).lower())
        self.assertIn('href="tasks.html"', (ROOT / "web/index.html").read_text(encoding="utf-8"))
        self.assertIn("viewport", (ROOT / "web/tasks.html").read_text(encoding="utf-8"))
        self.assertIn("min-width:700px", (ROOT / "web/tasks.css").read_text(encoding="utf-8"))
        self.assertNotIn("api.github.com", (ROOT / "web/tasks.js").read_text(encoding="utf-8"))

    def test_stage1_merged_and_next_deep_task_planned_with_full_backlog(self):
        """The Stage 1 merge must not leave a misleading active worker on the website."""
        self.assertIn("Stage 1 accepted and merged via PR #163", self.board)
        self.assertIn("WORKER_TASK_DEEP_FAST_REMOVAL_RANKING_MIGRATION_01.md", self.board)
        payload = self.build()
        self.assertEqual(payload["known_forward_count"], 19)
        statuses = {g["status"]: {t["id"]: t for t in g["tasks"]} for g in payload["groups"]}
        self.assertNotIn("deep-stage1", statuses["active"])
        self.assertIn("deep-stage1", statuses["complete"])
        self.assertIn("deep-ranking", statuses["planned"])
        self.assertEqual(statuses["planned"]["deep-ranking"]["worker_slot"], "ЧАТ 2 (следующий)")
        self.assertEqual(statuses["planned"]["deep-ranking"]["order"]["position"], 3)
        self.assertEqual(statuses["planned"]["deep-ranking"]["depends_on"], ["deep-freeze", "deep-stage1"])
        self.assertIn("deep-cutover", statuses["blocked"])
        self.assertIn("steam-prefilter", statuses["planned"])
        self.assertIn("architecture-cleanup", statuses["planned"])
        self.assertEqual(len(payload["task_titles"]), 24)

    def test_missing_late_unassigned_task_fails(self):
        plan = copy.deepcopy(self.plan)
        plan["items"] = [t for t in plan["items"] if t["id"] != "steam-error-watch"]
        with self.assertRaisesRegex(ValueError, "missing from registry"):
            self.build(plan)

    def test_missing_early_task_fails(self):
        plan = copy.deepcopy(self.plan)
        plan["items"] = [t for t in plan["items"] if t["id"] != "site-tasks"]
        with self.assertRaisesRegex(ValueError, "missing from registry"):
            self.build(plan)

    def test_dependency_cycle_fails(self):
        plan = copy.deepcopy(self.plan)
        by_id = {i["id"]: i for i in plan["items"]}
        by_id["deep-stage1"]["depends_on"] = ["deep-cutover"]
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.build(plan)

    def test_unknown_dependency_fails(self):
        plan = copy.deepcopy(self.plan)
        plan["items"][0]["depends_on"] = ["not-in-project"]
        with self.assertRaisesRegex(ValueError, "Unknown/self dependency"):
            self.build(plan)

    def test_duplicate_position_fails(self):
        plan = copy.deepcopy(self.plan)
        by_id = {i["id"]: i for i in plan["items"]}
        by_id["owned-dlc"]["order"]["position"] = 1
        with self.assertRaisesRegex(ValueError, "Duplicate ordered position"):
            self.build(plan)

    def test_private_url_and_internal_fields_fail(self):
        plan = copy.deepcopy(self.plan)
        plan["items"][0]["goal"] = "Visit https://private.example.net/secret"
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            self.build(plan)
        plan = copy.deepcopy(self.plan)
        plan["items"][0]["internal_prompt"] = "hidden"
        with self.assertRaisesRegex(ValueError, "Unexpected/omitted"):
            self.build(plan)

    def test_public_payload_does_not_dump_historical_board(self):
        payload = self.build()
        self.assertLessEqual(payload["groups"][3]["count"], 3)
        self.assertNotIn("PR #", json.dumps(payload, ensure_ascii=False))
        self.assertEqual(payload["plan_updated_on"], self.plan["last_curated_on"])
        self.assertEqual(payload["task_titles"]["deep-freeze"], "Заморозка архитектуры Deep")
        for group in payload["groups"]:
            self.assertEqual(len(group["tasks"]), group["count"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
