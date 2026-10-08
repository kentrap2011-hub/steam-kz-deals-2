#!/usr/bin/env python3
"""Build a public, read-only Pages snapshot from the canonical Director task registry."""
import argparse
import hashlib
import json
import re
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "config/director_task_plan.json"
BOARD = ROOT / "DIRECTOR_TASK_BOARD.md"
DEEP_MAP = ROOT / "config/deep_two_stage_dependency_map.json"
DEFAULT_OUTPUT = ROOT / "web/data/tasks.json"
STATUSES = ("active", "planned", "blocked", "complete")
EFFORT = {"низкая", "средняя", "высокая"}
URGENCY = {"критическая", "высокая", "обычная", "низкая"}
TASK_REF = re.compile(r"WORKER_TASK_[A-Z0-9_]+\.md")
PROHIBITED_PUBLIC = re.compile(r"https?://|[\w.+-]+@[\w.-]+\.[a-z]{2,}|(?:api[_ -]?key|access[_ -]?token|private[_ -]?url)", re.I)
VISIBLE_FIELDS = (
    "id", "title", "goal", "status", "worker_slot", "order",
    "depends_on", "blocker", "effort", "effort_reason", "urgency",
    "urgency_reason", "updated_on",
)


def sections(md):
    parts = re.split(r"(?=^## )", md, flags=re.M)
    return {part.splitlines()[0].strip()[3:]: part for part in parts if part.startswith("## ")}


def forward_refs(board_text, dependency_map):
    """Require every explicitly planned task in the canonical current Board lanes."""
    parts = sections(board_text)
    prefixes = (
        "CURRENT DIRECTOR STATE", "TWO-STAGE DEEP IMPLEMENTATION WAVES",
        "QUEUED PRODUCT WORK", "QUEUED LATER",
    )
    selected = [value for heading, value in parts.items() if heading.startswith(prefixes)]
    if len(selected) < 4:
        raise ValueError("Board is missing a required forward-planning section")
    found = set(TASK_REF.findall("\n".join(selected)))
    found.add(dependency_map["architecture_freeze_task"])
    found.update(task["task"] for task in dependency_map["parallelizable_after_freeze"])
    found.add(dependency_map["integration_gate"]["task"])
    found.update(dependency_map["integration_gate"]["requires_all_accepted"])
    return found


def validate_plan(plan, board_text, dependency_map, *, verify_task_files=True):
    if plan.get("schema_version") != 1 or plan.get("contract") != "DIRECTOR-FORWARD-TASK-REGISTRY-V1":
        raise ValueError("Unexpected task registry contract")
    if plan.get("source_board") != "DIRECTOR_TASK_BOARD.md":
        raise ValueError("Task registry must be bound to canonical Director Board")
    date.fromisoformat(plan["last_curated_on"])
    items = plan.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("Task registry must not be empty")

    ids, files, orders = set(), set(), set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {
            "id", "title", "goal", "status", "effort", "effort_reason", "urgency",
            "urgency_reason", "task_file", "worker_slot", "order", "depends_on",
            "blocker", "updated_on", "recent_completion"
        }:
            raise ValueError("Unexpected/omitted task registry fields")
        tid = item["id"]
        if not isinstance(tid, str) or not re.fullmatch(r"[a-z0-9-]{3,64}", tid) or tid in ids:
            raise ValueError(f"Duplicate or invalid task ID: {tid}")
        ids.add(tid)
        if item["status"] not in STATUSES or item["effort"] not in EFFORT or item["urgency"] not in URGENCY:
            raise ValueError(f"Invalid state, effort or urgency: {tid}")
        for field in ("title", "goal", "effort_reason", "urgency_reason"):
            text = item[field]
            if not isinstance(text, str) or not text.strip() or len(text) > 500 or PROHIBITED_PUBLIC.search(text):
                raise ValueError(f"Unsafe or empty public field {tid}.{field}")
        for field in ("worker_slot", "blocker"):
            val = item[field]
            if field == "worker_slot" and val is None:
                continue
            if not isinstance(val, str) or len(val) > 300 or PROHIBITED_PUBLIC.search(val):
                raise ValueError(f"Unsafe public field {tid}.{field}")
        date.fromisoformat(item["updated_on"])
        if not isinstance(item["recent_completion"], bool):
            raise ValueError(f"recent_completion is not boolean: {tid}")
        dep = item["depends_on"]
        if not isinstance(dep, list) or len(dep) != len(set(dep)) or any(not isinstance(d, str) for d in dep):
            raise ValueError(f"Invalid dependencies: {tid}")
        order = item["order"]
        if order is not None:
            if not isinstance(order, dict) or set(order) != {"track", "position"}:
                raise ValueError(f"Invalid order: {tid}")
            if not isinstance(order["track"], str) or not order["track"] or not isinstance(order["position"], int) or order["position"] <= 0:
                raise ValueError(f"Invalid order value: {tid}")
            order_id = (order["track"], order["position"])
            if order_id in orders:
                raise ValueError(f"Duplicate ordered position: {order_id}")
            orders.add(order_id)
        path = item["task_file"]
        if path is not None:
            if not isinstance(path, str) or not TASK_REF.fullmatch(path) or path in files:
                raise ValueError(f"Invalid task file: {tid}")
            if verify_task_files and not (ROOT / path).is_file():
                raise ValueError(f"Referenced task file does not exist: {path}")
            files.add(path)
    lookup = {i["id"]: i for i in items}
    for item in items:
        tid = item["id"]
        for dep in item["depends_on"]:
            if dep not in ids or dep == tid:
                raise ValueError(f"Unknown/self dependency: {tid} -> {dep}")
    seen, visiting = set(), set()

    def visit(tid):
        if tid in visiting:
            raise ValueError(f"Task dependency cycle: {tid}")
        if tid in seen:
            return
        visiting.add(tid)
        for dep in lookup[tid]["depends_on"]:
            visit(dep)
        visiting.remove(tid)
        seen.add(tid)

    for tid in ids:
        visit(tid)
    missing = forward_refs(board_text, dependency_map) - files
    if missing:
        raise ValueError("Canonical Director forward task(s) missing from registry: " + ", ".join(sorted(missing)))
    # Integration dependencies must stay in sync with the frozen source contract.
    frozen_prereqs = {lookup_file["task"] for lookup_file in dependency_map["parallelizable_after_freeze"]}
    integration = next(i for i in items if i["task_file"] == dependency_map["integration_gate"]["task"])
    by_file = {i["task_file"]: i["id"] for i in items if i["task_file"]}
    if set(integration["depends_on"]) != {by_file[p] for p in frozen_prereqs}:
        raise ValueError("Integration dependencies diverge from frozen Deep map")
    return items


def build_payload(plan, board_text, deep_map, *, now=None, verify_task_files=True):
    items = validate_plan(plan, board_text, deep_map, verify_task_files=verify_task_files)
    ordered_tracks = {}
    for item in items:
        if item["order"]:
            track = item["order"]["track"]
            ordered_tracks.setdefault(track, []).append(item)
    for lane in ordered_tracks.values():
        lane.sort(key=lambda i: i["order"]["position"])
    track_order = {"Очередь продукта": 0, "Очередь Deep": 1, "Позднее": 2}

    def order_key(item):
        order = item["order"]
        if order:
            return (0, track_order.get(order["track"], 50), order["position"], item["id"])
        return (1, 0, 0, item["title"])

    groups = []
    names = (("active", "В работе"), ("planned", "Запланировано"),
             ("blocked", "Ожидает / заблокировано"), ("complete", "Недавно завершено"))
    for status, label in names:
        chunk = [i for i in items if i["status"] == status and (status != "complete" or i["recent_completion"])]
        if status == "complete":
            chunk.sort(key=lambda i: (i["updated_on"], i["id"]), reverse=True)
            chunk = chunk[:3]
        else:
            chunk.sort(key=order_key)
        groups.append({"status": status, "label": label, "count": len(chunk),
                       "tasks": [{k: i[k] for k in VISIBLE_FIELDS} for i in chunk]})
    timestamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return {
        "schema_version": 1, "contract": "SITE-DIRECTOR-TASKS-PUBLIC-V1",
        "generated_at_utc": timestamp, "plan_updated_on": plan["last_curated_on"],
        "known_forward_count": sum(i["status"] != "complete" for i in items),
        "groups": groups,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--validate-current", type=Path)
    args = parser.parse_args()
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    board = BOARD.read_text(encoding="utf-8")
    deep_map = json.loads(DEEP_MAP.read_text(encoding="utf-8"))
    payload = build_payload(plan, board, deep_map)
    if args.validate_current:
        current = json.loads(args.validate_current.read_text(encoding="utf-8"))
        # Validate current shape and canonically computed task fields, but not its build time.
        for field in ("contract", "schema_version", "plan_updated_on", "known_forward_count", "groups"):
            if current.get(field) != payload[field]:
                raise SystemExit(f"STALE_OR_INVALID_TASK_PAYLOAD field={field}")
        datetime.fromisoformat(current["generated_at_utc"].replace("Z", "+00:00"))
        print("SITE_TASKS=validated")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        print(f"SITE_TASKS=built forward={payload['known_forward_count']}")


if __name__ == "__main__":
    main()
