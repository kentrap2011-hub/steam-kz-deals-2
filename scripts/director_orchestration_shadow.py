#!/usr/bin/env python3
"""Phase 1 deterministic Director orchestration shadow planner.

This module is deliberately side-effect free with respect to repository state and
workflow dispatch. It only reads JSON and emits a plan to stdout and, when asked,
to an output artifact file.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


class ShadowPlanError(ValueError):
    """Fail-closed validation/planning error."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ShadowPlanError(message)


def load_json(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ShadowPlanError(f"cannot read valid JSON from {path}: {exc}") from exc
    _require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def validate_contract(contract: dict[str, Any]) -> None:
    _require(contract.get("phase") == 1, "contract phase must be 1")
    _require(contract.get("mode") == "shadow_observer", "contract mode must be shadow_observer")
    limits = contract.get("limits")
    _require(isinstance(limits, dict), "contract.limits must be an object")
    _require(limits.get("max_logical_slots") == 2, "Phase 1 must define exactly two logical slots")
    security = contract.get("security")
    _require(isinstance(security, dict), "contract.security must be an object")
    for key in ("openai_or_codex_in_phase_1", "worker_dispatch_in_phase_1", "product_mutation_in_phase_1"):
        _require(security.get(key) == "forbidden", f"contract.security.{key} must be forbidden")
    priority = contract.get("priority")
    _require(isinstance(priority, dict), "contract.priority must be an object")
    weights = priority.get("class_weights")
    _require(isinstance(weights, dict) and weights, "priority.class_weights must be non-empty")
    tasks = contract.get("tasks")
    _require(isinstance(tasks, dict), "contract.tasks must be an object")
    _require(tasks.get("eligible_statuses") == ["queued"], "only queued tasks may be eligible in Phase 1")
    deps = contract.get("dependencies")
    _require(isinstance(deps, dict), "contract.dependencies must be an object")
    _require(deps.get("missing_dependency_behavior") == "fail_closed", "missing dependencies must fail closed")
    conflicts = contract.get("conflicts")
    _require(isinstance(conflicts, dict) and conflicts.get("exclusive_on_shared_key") is True,
             "shared semantic conflict keys must be exclusive")


def validate_state(contract: dict[str, Any], state: dict[str, Any]) -> None:
    _require(state.get("schema_version") == 1, "state.schema_version must be 1")
    _require(isinstance(state.get("state_revision"), int) and state["state_revision"] >= 1,
             "state_revision must be a positive integer")
    _require(state.get("phase") == "shadow_observer", "state.phase must be shadow_observer")

    max_slots = contract["limits"]["max_logical_slots"]
    slots = state.get("slots")
    _require(isinstance(slots, list) and len(slots) == max_slots,
             f"state must contain exactly {max_slots} logical slots")
    allowed_slot_ids = set(contract["slots"]["allowed_ids"])
    seen_slot_ids: set[str] = set()
    occupied_task_ids: set[str] = set()
    for slot in slots:
        _require(isinstance(slot, dict), "each slot must be an object")
        slot_id = slot.get("slot_id")
        _require(slot_id in allowed_slot_ids, f"unknown slot_id {slot_id!r}")
        _require(slot_id not in seen_slot_ids, f"duplicate slot_id {slot_id!r}")
        seen_slot_ids.add(slot_id)
        status = slot.get("status")
        _require(status in contract["slots"]["allowed_statuses"], f"invalid slot status {status!r}")
        keys = slot.get("conflict_keys")
        _require(isinstance(keys, list) and all(isinstance(v, str) and v for v in keys),
                 f"slot {slot_id} conflict_keys must be a list of non-empty strings")
        if status == "occupied":
            _require(slot.get("occupancy_type") in contract["slots"]["allowed_occupancy_types"],
                     f"occupied slot {slot_id} has invalid occupancy_type")
            task_id = slot.get("task_id")
            _require(isinstance(task_id, str) and task_id, f"occupied slot {slot_id} must have task_id")
            _require(task_id not in occupied_task_ids, f"task {task_id} occupies multiple slots")
            occupied_task_ids.add(task_id)
        else:
            _require(slot.get("task_id") is None and slot.get("occupancy_type") is None,
                     f"free slot {slot_id} cannot carry occupancy")
            _require(keys == [], f"free slot {slot_id} cannot carry conflict keys")

    tasks = state.get("tasks")
    _require(isinstance(tasks, list), "state.tasks must be a list")
    required_fields = set(contract["tasks"]["required_fields"])
    allowed_statuses = set(contract["tasks"]["allowed_statuses"])
    weights = contract["priority"]["class_weights"]
    task_by_id: dict[str, dict[str, Any]] = {}
    assigned_slots: dict[str, str] = {}
    for task in tasks:
        _require(isinstance(task, dict), "each task must be an object")
        missing = required_fields - task.keys()
        _require(not missing, f"task missing required fields: {sorted(missing)}")
        task_id = task.get("task_id")
        _require(isinstance(task_id, str) and task_id, "task_id must be a non-empty string")
        _require(task_id not in task_by_id, f"duplicate task_id {task_id}")
        task_by_id[task_id] = task
        _require(isinstance(task.get("revision"), int) and task["revision"] >= 1,
                 f"task {task_id} revision must be positive integer")
        _require(task.get("status") in allowed_statuses, f"task {task_id} has invalid status")
        _require(task.get("priority") in weights, f"task {task_id} has unknown priority")
        _require(isinstance(task.get("queue_sequence"), int) and task["queue_sequence"] >= 0,
                 f"task {task_id} queue_sequence must be non-negative integer")
        keys = task.get("conflict_keys")
        _require(isinstance(keys, list) and all(isinstance(v, str) and v for v in keys),
                 f"task {task_id} conflict_keys must be a list of non-empty strings")
        deps = task.get("dependencies")
        _require(isinstance(deps, list) and all(isinstance(v, str) and v for v in deps),
                 f"task {task_id} dependencies must be a list of non-empty task ids")
        assigned = task.get("assigned_slot")
        if assigned is not None:
            _require(assigned in allowed_slot_ids, f"task {task_id} assigned to unknown slot")
            _require(assigned not in assigned_slots, f"multiple tasks assigned to {assigned}")
            assigned_slots[assigned] = task_id

    for slot in slots:
        if slot["status"] == "occupied":
            task_id = slot["task_id"]
            _require(task_id in task_by_id, f"occupied task {task_id} missing from state.tasks")
            _require(task_by_id[task_id]["assigned_slot"] == slot["slot_id"],
                     f"occupied slot/task binding mismatch for {task_id}")
    for slot_id, task_id in assigned_slots.items():
        slot = next(s for s in slots if s["slot_id"] == slot_id)
        _require(slot["status"] == "occupied" and slot["task_id"] == task_id,
                 f"assigned task {task_id} does not match slot {slot_id}")

    for task in tasks:
        for dep in task["dependencies"]:
            _require(dep in task_by_id, f"task {task['task_id']} has missing dependency {dep}")
            _require(dep != task["task_id"], f"task {task['task_id']} cannot depend on itself")


def _task_summary(task: dict[str, Any], **extra: Any) -> dict[str, Any]:
    result = {
        "task_id": task["task_id"],
        "revision": task["revision"],
        "mode": task["mode"],
        "priority": task["priority"],
        "domain": task["domain"],
        "conflict_keys": list(task["conflict_keys"]),
        "task_file": task["task_file"],
        "expected_report": task["expected_report"]
    }
    result.update(extra)
    return result


def plan_shadow(contract: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    validate_contract(contract)
    validate_state(contract, state)

    tasks = state["tasks"]
    task_by_id = {task["task_id"]: task for task in tasks}
    max_slots = contract["limits"]["max_logical_slots"]
    occupied_slots = [copy.deepcopy(slot) for slot in state["slots"] if slot["status"] == "occupied"]
    free_slots = [slot["slot_id"] for slot in state["slots"] if slot["status"] == "free"]
    _require(len(occupied_slots) <= max_slots, "occupied slots exceed max logical slots")
    available_capacity = max_slots - len(occupied_slots)
    _require(available_capacity == len(free_slots), "slot capacity is ambiguous")

    occupied_conflict_keys = {
        key for slot in occupied_slots for key in slot.get("conflict_keys", [])
    }
    satisfied_statuses = set(contract["dependencies"]["satisfied_statuses"])
    clear_user = set(contract["gates"]["clear_user_gate_values"])
    clear_review = set(contract["gates"]["clear_review_gate_values"])
    eligible_statuses = set(contract["tasks"]["eligible_statuses"])

    blocked_by_dependency: list[dict[str, Any]] = []
    blocked_by_conflict: list[dict[str, Any]] = []
    ineligible: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    for task in tasks:
        if task["status"] not in eligible_statuses:
            ineligible.append(_task_summary(task, reason=f"status:{task['status']}"))
            continue

        gate_reasons = []
        if task["user_gate"] not in clear_user:
            gate_reasons.append(f"user_gate:{task['user_gate']}")
        if task["review_gate"] not in clear_review:
            gate_reasons.append(f"review_gate:{task['review_gate']}")
        if gate_reasons:
            ineligible.append(_task_summary(task, reason=",".join(gate_reasons)))
            continue

        unsatisfied = [dep for dep in task["dependencies"] if task_by_id[dep]["status"] not in satisfied_statuses]
        if unsatisfied:
            blocked_by_dependency.append(_task_summary(task, unsatisfied_dependencies=unsatisfied))

        overlap = sorted(set(task["conflict_keys"]) & occupied_conflict_keys)
        if overlap:
            blocked_by_conflict.append(_task_summary(task, conflicts_with="occupied_slots", overlapping_keys=overlap))

        if unsatisfied or overlap:
            continue

        dependency_unblocking_value = sum(
            1 for other in tasks
            if task["task_id"] in other.get("dependencies", []) and other["status"] == "queued"
        )
        candidate = copy.deepcopy(task)
        candidate["dependency_unblocking_value"] = dependency_unblocking_value
        candidates.append(candidate)

    weights = contract["priority"]["class_weights"]
    candidates.sort(key=lambda task: (
        -weights[task["priority"]],
        -task["dependency_unblocking_value"],
        task["queue_sequence"],
        task["task_id"]
    ))

    selected: list[dict[str, Any]] = []
    eligible_not_selected: list[dict[str, Any]] = []
    active_keys = set(occupied_conflict_keys)
    free_iter = iter(sorted(free_slots))
    for task in candidates:
        if len(selected) >= available_capacity:
            eligible_not_selected.append(_task_summary(
                task,
                reason="capacity",
                dependency_unblocking_value=task["dependency_unblocking_value"]
            ))
            continue
        overlap = sorted(set(task["conflict_keys"]) & active_keys)
        if overlap:
            blocked_by_conflict.append(_task_summary(
                task,
                conflicts_with="planned_assignment",
                overlapping_keys=overlap
            ))
            continue
        slot_id = next(free_iter)
        selected.append(_task_summary(
            task,
            would_assign_slot=slot_id,
            dependency_unblocking_value=task["dependency_unblocking_value"]
        ))
        active_keys.update(task["conflict_keys"])

    total_after_plan = len(occupied_slots) + len(selected)
    _require(total_after_plan <= max_slots, "planner exceeded max logical slots")

    return {
        "schema_version": 1,
        "mode": "shadow_observer",
        "observed_state_revision": state["state_revision"],
        "max_logical_slots": max_slots,
        "occupied_slots": occupied_slots,
        "free_slots_before_plan": sorted(free_slots),
        "would_assign": selected,
        "blocked_by_conflict": sorted(blocked_by_conflict, key=lambda x: x["task_id"]),
        "blocked_by_dependency": sorted(blocked_by_dependency, key=lambda x: x["task_id"]),
        "eligible_not_selected": eligible_not_selected,
        "ineligible": sorted(ineligible, key=lambda x: x["task_id"]),
        "warnings": [],
        "assertions": {
            "total_occupied_or_would_assign": total_after_plan,
            "max_two_slots_respected": total_after_plan <= max_slots,
            "manual_external_occupancy_reserved": any(
                slot.get("occupancy_type") == "external_manual" for slot in occupied_slots
            ),
            "worker_dispatch_performed": false_value(),
            "product_mutation_performed": false_value(),
            "openai_or_codex_invoked": false_value()
        }
    }


def false_value() -> bool:
    """Explicit helper keeps safety assertions grep-friendly and JSON-boolean."""
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", default="config/director_orchestration_contract.json")
    parser.add_argument("--state", default="orchestration/state.json")
    parser.add_argument("--output", help="Optional shadow-plan artifact path")
    args = parser.parse_args(argv)
    try:
        contract = load_json(args.contract)
        state = load_json(args.state)
        plan = plan_shadow(contract, state)
    except ShadowPlanError as exc:
        print(f"shadow planner failed closed: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    sys.stdout.write(rendered)
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
