#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from director_orchestration_shadow import ShadowPlanError, plan_shadow


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "config/director_orchestration_contract.json").read_text(encoding="utf-8"))
STATE = json.loads((ROOT / "orchestration/state.json").read_text(encoding="utf-8"))


def task(task_id: str, *, priority: str = "NORMAL", sequence: int = 100, conflicts=None, deps=None,
         status: str = "queued"):
    return {
        "task_id": task_id,
        "revision": 1,
        "mode": "READ_ONLY_RECON",
        "priority": priority,
        "domain": task_id,
        "conflict_keys": list(conflicts or []),
        "status": status,
        "task_file": f"WORKER_TASK_{task_id}.md",
        "expected_report": f"reviews/worker_reports/{task_id}.md",
        "dependencies": list(deps or []),
        "assigned_slot": None,
        "queue_sequence": sequence,
        "user_gate": "none",
        "review_gate": "none"
    }


class ShadowPlannerTests(unittest.TestCase):
    def test_initial_state_reserves_chat1_and_fills_only_one_slot(self):
        plan = plan_shadow(CONTRACT, copy.deepcopy(STATE))
        self.assertEqual(1, len(plan["occupied_slots"]))
        self.assertEqual("taste-evidence-state-and-confidence-implement-01", plan["occupied_slots"][0]["task_id"])
        self.assertEqual("external_manual", plan["occupied_slots"][0]["occupancy_type"])
        self.assertEqual(1, len(plan["would_assign"]))
        self.assertEqual("slot_2", plan["would_assign"][0]["would_assign_slot"])
        self.assertLessEqual(plan["assertions"]["total_occupied_or_would_assign"], 2)

    def test_conflicting_taste_ranking_task_not_selected(self):
        plan = plan_shadow(CONTRACT, copy.deepcopy(STATE))
        self.assertNotIn("wishlist-good-deal-override-recon-01", [x["task_id"] for x in plan["would_assign"]])
        blocked = next(x for x in plan["blocked_by_conflict"] if x["task_id"] == "wishlist-good-deal-override-recon-01")
        self.assertIn("taste-ranking-policy", blocked["overlapping_keys"])

    def test_unrelated_safe_task_selected_for_free_slot(self):
        plan = plan_shadow(CONTRACT, copy.deepcopy(STATE))
        self.assertEqual("epic-ru-availability-source-probe-01", plan["would_assign"][0]["task_id"])

    def test_unmet_dependency_blocks_assignment(self):
        plan = plan_shadow(CONTRACT, copy.deepcopy(STATE))
        blocked = next(x for x in plan["blocked_by_dependency"] if x["task_id"] == "wishlist-good-deal-override-recon-01")
        self.assertEqual(["taste-evidence-state-and-confidence-implement-01"], blocked["unsatisfied_dependencies"])

    def test_higher_explicit_priority_wins_when_both_safe(self):
        state = {
            "schema_version": 1,
            "state_revision": 9,
            "phase": "shadow_observer",
            "slots": [
                {"slot_id": "slot_1", "status": "free", "occupancy_type": None, "task_id": None, "task_file": None, "conflict_keys": []},
                {"slot_id": "slot_2", "status": "free", "occupancy_type": None, "task_id": None, "task_file": None, "conflict_keys": []}
            ],
            "tasks": [
                task("low", priority="LOW", sequence=1),
                task("high", priority="HIGH", sequence=2),
                task("normal", priority="NORMAL", sequence=0)
            ]
        }
        plan = plan_shadow(CONTRACT, state)
        self.assertEqual(["high", "normal"], [x["task_id"] for x in plan["would_assign"]])

    def test_dependency_unblocking_value_breaks_equal_priority(self):
        state = {
            "schema_version": 1,
            "state_revision": 10,
            "phase": "shadow_observer",
            "slots": [
                {"slot_id": "slot_1", "status": "free", "occupancy_type": None, "task_id": None, "task_file": None, "conflict_keys": []},
                {"slot_id": "slot_2", "status": "free", "occupancy_type": None, "task_id": None, "task_file": None, "conflict_keys": []}
            ],
            "tasks": [
                task("plain", priority="HIGH", sequence=1),
                task("unblocker", priority="HIGH", sequence=2),
                task("dependent", priority="LOW", sequence=3, deps=["unblocker"])
            ]
        }
        plan = plan_shadow(CONTRACT, state)
        self.assertEqual("unblocker", plan["would_assign"][0]["task_id"])

    def test_stale_cancelled_deferred_tasks_not_selected(self):
        state = {
            "schema_version": 1,
            "state_revision": 11,
            "phase": "shadow_observer",
            "slots": [
                {"slot_id": "slot_1", "status": "free", "occupancy_type": None, "task_id": None, "task_file": None, "conflict_keys": []},
                {"slot_id": "slot_2", "status": "free", "occupancy_type": None, "task_id": None, "task_file": None, "conflict_keys": []}
            ],
            "tasks": [
                task("stale", status="stale"),
                task("cancelled", status="cancelled"),
                task("deferred", status="deferred")
            ]
        }
        plan = plan_shadow(CONTRACT, state)
        self.assertEqual([], plan["would_assign"])
        self.assertEqual({"stale", "cancelled", "deferred"}, {x["task_id"] for x in plan["ineligible"]})

    def test_malformed_or_ambiguous_state_fails_closed(self):
        malformed = copy.deepcopy(STATE)
        malformed["slots"][0]["task_id"] = "different-task"
        with self.assertRaises(ShadowPlanError):
            plan_shadow(CONTRACT, malformed)

    def test_missing_dependency_fails_closed(self):
        malformed = copy.deepcopy(STATE)
        malformed["tasks"][2]["dependencies"] = ["missing-task"]
        with self.assertRaises(ShadowPlanError):
            plan_shadow(CONTRACT, malformed)

    def test_selected_tasks_conflict_with_each_other(self):
        state = {
            "schema_version": 1,
            "state_revision": 12,
            "phase": "shadow_observer",
            "slots": [
                {"slot_id": "slot_1", "status": "free", "occupancy_type": None, "task_id": None, "task_file": None, "conflict_keys": []},
                {"slot_id": "slot_2", "status": "free", "occupancy_type": None, "task_id": None, "task_file": None, "conflict_keys": []}
            ],
            "tasks": [
                task("first", priority="HIGH", sequence=1, conflicts=["frontend-feed"]),
                task("second", priority="NORMAL", sequence=2, conflicts=["frontend-feed"]),
                task("third", priority="LOW", sequence=3, conflicts=["provider-authority:epic"])
            ]
        }
        plan = plan_shadow(CONTRACT, state)
        self.assertEqual(["first", "third"], [x["task_id"] for x in plan["would_assign"]])
        self.assertIn("second", [x["task_id"] for x in plan["blocked_by_conflict"]])


if __name__ == "__main__":
    unittest.main()
