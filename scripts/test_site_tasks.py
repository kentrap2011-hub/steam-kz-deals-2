#!/usr/bin/env python3
"""Contract and acceptance regressions for the complete Director forward task page."""
import copy
import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
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

    @staticmethod
    def expected_recent_ids(plan):
        """Independent oracle: newest eligible completions, capped at three."""
        eligible = [
            item for item in plan["items"]
            if item["status"] == "complete" and item["recent_completion"]
        ]
        eligible.sort(
            key=lambda item: (
                datetime.fromisoformat(item["updated_at_utc"].replace("Z", "+00:00")).astimezone(timezone.utc),
                item["id"],
            ),
            reverse=True,
        )
        return [item["id"] for item in eligible[:3]]

    @staticmethod
    def recent_ids(payload):
        return [task["id"] for group in payload["groups"] if group["status"] == "complete" for task in group["tasks"]]

    def test_full_forward_backlog_and_mobile_nav(self):
        payload = self.build()
        self.assertEqual(payload["contract"], "SITE-DIRECTOR-TASKS-PUBLIC-V1")
        counts = {g["status"]: g["count"] for g in payload["groups"]}
        expected_forward = {i["id"] for i in self.plan["items"] if i["status"] != "complete"}
        actual_forward = {t["id"] for g in payload["groups"] if g["status"] != "complete" for t in g["tasks"]}
        self.assertEqual(actual_forward, expected_forward)
        self.assertEqual(sum(counts[s] for s in ("active", "planned", "blocked")), len(expected_forward))
        self.assertEqual(payload["known_forward_count"], len(expected_forward))
        for status in ("active", "planned", "blocked"):
            self.assertEqual(counts[status], sum(i["status"] == status for i in self.plan["items"]))
        self.assertEqual(self.recent_ids(payload), self.expected_recent_ids(self.plan))
        self.assertEqual(counts["complete"], len(self.expected_recent_ids(self.plan)))

        by_id = {t["id"]: t for group in payload["groups"] for t in group["tasks"]}
        self.assertEqual(set(by_id), expected_forward | set(self.expected_recent_ids(self.plan)))
        for item in self.plan["items"]:
            self.assertEqual(payload["task_titles"][item["id"]], item["title"])
        self.assertEqual(len(payload["task_titles"]), len(self.plan["items"]))
        for tid in ("steam-50-top100", "owned-dlc", "deep-site", "deep-cutover",
                    "steam-prefilter", "steam-error-watch", "giveaway-decouple",
                    "giveaway-itad", "architecture-cleanup"):
            self.assertIn(tid, actual_forward)
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

    def test_completed_registry_entries_survive_recent_display_eviction(self):
        """Public titles preserve all canonical task identities, even when hidden by the cap."""
        payload = self.build()
        items = {item["id"]: item for item in self.plan["items"]}
        expected_forward = {tid for tid, item in items.items() if item["status"] != "complete"}
        actual_forward = {t["id"] for g in payload["groups"] if g["status"] != "complete" for t in g["tasks"]}
        self.assertEqual(actual_forward, expected_forward)
        self.assertEqual(payload["known_forward_count"], len(expected_forward))
        self.assertEqual(set(payload["task_titles"]), set(items))

        completed = {tid for tid, item in items.items() if item["status"] == "complete"}
        recent = self.recent_ids(payload)
        self.assertEqual(recent, self.expected_recent_ids(self.plan))
        self.assertLessEqual(len(recent), 3)
        self.assertTrue(set(recent).issubset(completed))
        displayed = {t["id"] for g in payload["groups"] for t in g["tasks"]}
        self.assertEqual(completed - set(recent), set(payload["task_titles"]) - displayed)

    def test_new_completion_displaces_older_recent_without_losing_backlog(self):
        """A later completion takes a capped slot; evicted completions stay in the registry."""
        plan = copy.deepcopy(self.plan)
        previous_recent = set(self.recent_ids(self.build()))
        target = next(item for item in plan["items"] if item["status"] == "active" and not item["depends_on"])
        latest = max(
            datetime.fromisoformat(item["updated_at_utc"].replace("Z", "+00:00")).astimezone(timezone.utc)
            for item in plan["items"]
        ) + timedelta(seconds=1)
        target.update(status="complete", recent_completion=True, blocker="",
                      updated_on=latest.date().isoformat(),
                      updated_at_utc=latest.isoformat().replace("+00:00", "Z"))
        payload = self.build(plan)
        unfinished = {item["id"] for item in plan["items"] if item["status"] != "complete"}
        displayed_forward = {t["id"] for g in payload["groups"] if g["status"] != "complete" for t in g["tasks"]}
        self.assertEqual(payload["known_forward_count"], len(unfinished))
        self.assertEqual(displayed_forward, unfinished)
        recent = self.recent_ids(payload)
        self.assertEqual(recent, self.expected_recent_ids(plan))
        self.assertEqual(recent[0], target["id"])
        self.assertLessEqual(len(recent), 3)
        evicted = previous_recent - set(recent)
        self.assertTrue(evicted, "The fixture must exercise a full recent-completion cap")
        self.assertTrue(evicted.issubset(payload["task_titles"]))
        self.assertTrue(evicted.isdisjoint(displayed_forward))
        self.assertEqual(set(payload["task_titles"]), {item["id"] for item in plan["items"]})

    def test_recent_completion_uses_precise_time_not_same_day_id(self):
        plan = copy.deepcopy(self.plan)
        eligible = sorted(
            (item for item in plan["items"] if item["status"] == "complete" and item["recent_completion"]),
            key=lambda item: item["id"],
        )
        self.assertGreaterEqual(len(eligible), 2)
        # Lexically smaller ID is newer by one second on the same day.
        # Date-only sorting followed by reverse ID would pick the wrong winner.
        latest = max(
            datetime.fromisoformat(item["updated_at_utc"].replace("Z", "+00:00")).astimezone(timezone.utc)
            for item in plan["items"]
        )
        next_day = latest.date() + timedelta(days=1)
        earlier = datetime(next_day.year, next_day.month, next_day.day, 12, tzinfo=timezone.utc)
        for item, instant in ((eligible[0], earlier + timedelta(seconds=1)), (eligible[1], earlier)):
            item.update(updated_on=instant.date().isoformat(),
                        updated_at_utc=instant.isoformat().replace("+00:00", "Z"))
        recent = self.build(plan)["groups"][3]["tasks"]
        self.assertEqual([item["id"] for item in recent[:2]], [eligible[0]["id"], eligible[1]["id"]])
        self.assertEqual([item["id"] for item in recent], self.expected_recent_ids(plan))
        stamps = [datetime.fromisoformat(item["updated_at_utc"].replace("Z", "+00:00")) for item in recent]
        self.assertEqual(stamps, sorted(stamps, reverse=True))

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
