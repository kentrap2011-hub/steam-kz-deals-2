#!/usr/bin/env python3
"""Bounded control helper for Copilot CLI zero-cost live read-only Pilot 02.

All authoritative state writes go through director_orchestration_controller.persist_state.
The worker never imports or executes this helper and has no repository write authority.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from director_orchestration_controller import (  # noqa: E402
    acquire_cloud_lease,
    canonical_digest,
    load_intakes,
    load_json,
    persist_state,
    req,
    validate_state,
    verify_repository_bindings,
)
from director_report_publisher import (  # noqa: E402
    publish_exact_report,
    validate_publication,
)

TASK_ID = "epic-ru-availability-source-probe-02"
TASK_FILE = "WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_02.md"
TASK_BLOB = "8270487fb3019135adc5662d0b67f0f37e189bed"
REPORT = "reviews/worker_reports/epic-ru-availability-source-probe-02.md"
PILOT_REPORT = "reviews/worker_reports/copilot-cli-zero-cost-live-readonly-pilot-02.md"
INTAKE_ID = "intake-20260906-0005-epic-recon-02-r1"
ATTEMPT_ID = f"{TASK_ID}:r1:a1"
LEASE_ID = f"slot_2:{ATTEMPT_ID}"


def dump(path: str | Path, value) -> None:
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def phase2a():
    return load_json(ROOT / "config/director_orchestration_phase2a_contract.json")


def pilot_contract():
    c = load_json(ROOT / "config/director_orchestration_copilot_cli_pilot02_contract.json")
    req(c.get("state_persistence_enabled") is True, "pilot state persistence not explicitly enabled")
    req(c.get("single_state_writer") == "scripts/director_orchestration_controller.py", "single writer changed")
    req(c.get("automatic_next_dispatch") is False, "automatic next dispatch enabled")
    req(c.get("general_dispatch_enabled") is False, "general dispatch enabled")
    req(c.get("implement_dispatch_allowed") is False, "IMPLEMENT dispatch enabled")
    cost = c.get("cost_gate", {})
    for k in ("additional_payment_allowed", "paid_overage_allowed", "paid_fallback_allowed", "pat_allowed", "openai_api_key_allowed"):
        req(cost.get(k) is False, f"zero-cost gate changed: {k}")
    req(cost.get("authentication") == "GITHUB_TOKEN", "authentication changed")
    req(c.get("limits", {}).get("max_live_attempts") == 1, "pilot must allow one attempt only")
    req(c.get("limits", {}).get("max_logical_slots") == 2, "slot count changed")
    return c


def build_task(event, p2a):
    return {
        "allowed_input_refs": list(event["allowed_input_refs"]),
        "allowed_result_statuses": list(event["allowed_result_statuses"]),
        "assigned_slot": None,
        "attempt_id": None,
        "attempt_number": 0,
        "base_sha": event["base_sha"],
        "conflict_keys": list(event.get("conflict_keys", [])),
        "dependencies": list(event.get("dependencies", [])),
        "domain": event["domain"],
        "evidence_refs": [],
        "expected_report": event["expected_report_path"],
        "intake_event_id": event["event_id"],
        "mode": event["mode"],
        "priority": event["priority"],
        "queue_sequence": event["queue_sequence"],
        "retry": {"failure_count": 0, "last_failure": None, "max_attempts": p2a["limits"]["max_attempts_per_revision"], "next_attempt_number": 1},
        "review_gate": event.get("review_gate", "none"),
        "revision": event["task_revision"],
        "status": event["initial_status"],
        "task_file": event["task_file"],
        "task_file_blob_sha": event["task_file_blob_sha"],
        "task_id": event["task_id"],
        "user_gate": event.get("user_gate", "none"),
    }


def prepare(base_sha: str, out_request: str, out_meta: str) -> None:
    p2a, contract = phase2a(), pilot_contract()
    state, events = load_json(ROOT / "orchestration/state.json"), load_intakes(ROOT)
    req(INTAKE_ID in events, "Pilot 02 immutable intake missing")
    event = events[INTAKE_ID]
    prior = {k: v for k, v in events.items() if k != INTAKE_ID}
    validate_state(p2a, state, prior)
    verify_repository_bindings(ROOT, state)

    req(state.get("dispatch_enabled") is False, "general dispatch unexpectedly enabled")
    req(len(state["slots"]) == 2, "logical slot count changed")
    req(all(s.get("status") == "free" for s in state["slots"]), "slot occupancy changed; fail closed")
    req(not any(s.get("occupancy_type") == "cloud_worker" for s in state["slots"]), "another cloud worker active")
    req(not any(t.get("task_id") == TASK_ID for t in state["tasks"]), "Pilot 02 already exists; second dispatch forbidden")
    req(not (ROOT / REPORT).exists(), "semantic report path collision")
    req(not (ROOT / PILOT_REPORT).exists(), "pilot report path collision")

    expected = {
        "event_id": INTAKE_ID,
        "task_id": TASK_ID,
        "task_revision": 1,
        "mode": "READ_ONLY_RECON",
        "task_file": TASK_FILE,
        "task_file_blob_sha": TASK_BLOB,
        "base_sha": base_sha,
        "expected_report_path": REPORT,
        "initial_status": "queued",
    }
    for k, v in expected.items():
        req(event.get(k) == v, f"intake binding mismatch: {k}")
    req(event.get("allowed_result_statuses") == ["complete", "blocked", "needs_user_evidence"], "allowed statuses changed")

    staged = copy.deepcopy(state)
    staged["applied_intake_events"].append({"digest_sha256": canonical_digest(event), "event_id": INTAKE_ID})
    staged["tasks"].append(build_task(event, p2a))
    staged["slots"] = sorted(staged["slots"], key=lambda s: 0 if s["slot_id"] == "slot_2" else 1)
    leased, request = acquire_cloud_lease(
        {"limits": {"cloud_lease_seconds": contract["limits"]["cloud_lease_seconds"]}},
        staged,
        TASK_ID,
        1,
        datetime.now(timezone.utc),
    )
    leased["slots"] = sorted(leased["slots"], key=lambda s: s["slot_id"])
    leased["dispatch_enabled"] = False
    leased["orchestration_phase"] = "copilot_cli_zero_cost_live_readonly_pilot_02_attempt_1"

    req(request["attempt_number"] == 1 and request["attempt_id"] == ATTEMPT_ID, "attempt binding changed")
    req(request["lease_id"] == LEASE_ID, "lease binding changed")
    req(request["mode"] == "READ_ONLY_RECON", "worker mode changed")
    req(request["task_file"] == TASK_FILE and request["task_file_blob_sha"] == TASK_BLOB, "task binding changed")
    req(request["base_sha"] == base_sha and request["expected_report_path"] == REPORT, "base/report binding changed")
    for k in ("repository_write_authority", "github_write_credential", "state_write_authority", "product_write_authority", "worker_can_choose_next_task"):
        req(request[k] is False, f"worker authority changed: {k}")
    req(request["secret_values"] == [], "worker request contains secret values")
    slot2 = next(s for s in leased["slots"] if s["slot_id"] == "slot_2")
    slot1 = next(s for s in leased["slots"] if s["slot_id"] == "slot_1")
    req(slot2.get("task_id") == TASK_ID and slot2.get("occupancy_type") == "cloud_worker", "Pilot 02 not on slot_2")
    req(slot1.get("status") == "free", "slot_1 truth changed")
    validate_state(p2a, leased, events)
    verify_repository_bindings(ROOT, leased)

    persist_state(contract, ROOT / "orchestration/state.json", leased)
    dump(out_request, request)
    dump(out_meta, {"state_revision": leased["state_revision"], "base_sha": base_sha, "attempt_id": ATTEMPT_ID, "lease_id": LEASE_ID})


def quota_lines(evidence):
    q = evidence.get("quota_preflight") or {}
    snaps = q.get("quotaSnapshots") or {}
    if not snaps:
        return ["- No usable quota snapshot was returned."]
    lines = []
    for name, s in sorted(snaps.items()):
        lines.append(
            f"- `{name}`: entitlementRequests={s.get('entitlementRequests')}, usedRequests={s.get('usedRequests')}, "
            f"remainingPercentage={s.get('remainingPercentage')}, overage={s.get('overage')}, "
            f"overageAllowedWithExhaustedQuota={s.get('overageAllowedWithExhaustedQuota')}"
        )
    return lines


def finalize(request_path: str, evidence_path: str, jobs_path: str, launch_sha: str, prepared_head: str, run_id: str, run_attempt: str) -> None:
    p2a, contract = phase2a(), pilot_contract()
    state, events = load_json(ROOT / "orchestration/state.json"), load_intakes(ROOT)
    request, evidence = load_json(Path(request_path)), load_json(Path(evidence_path))
    jobs = load_json(Path(jobs_path)).get("jobs", [])
    validate_state(p2a, state, events)
    verify_repository_bindings(ROOT, state)
    req(state.get("dispatch_enabled") is False, "general dispatch changed")
    req(evidence.get("copilot_invocation_count") in (0, 1), "invalid Copilot invocation count")

    task = next((t for t in state["tasks"] if t["task_id"] == TASK_ID), None)
    req(task is not None, "Pilot 02 task missing")
    req(task.get("status") == "assigned" and task.get("assigned_slot") == "slot_2", "Pilot 02 lease no longer current")
    req(task.get("attempt_number") == 1 and task.get("attempt_id") == ATTEMPT_ID, "attempt changed")
    req(task.get("base_sha") == request["base_sha"] and task.get("task_file_blob_sha") == TASK_BLOB, "base/blob changed")
    req(task.get("expected_report") == REPORT, "report binding changed")
    slot2 = next(s for s in state["slots"] if s["slot_id"] == "slot_2")
    req(slot2.get("lease", {}).get("lease_id") == LEASE_ID, "lease changed")
    impl = next(t for t in state["tasks"] if t["task_id"] == "top-summary-filter-buttons-01")
    req(impl.get("mode") == "IMPLEMENT" and impl.get("attempt_number") == 0 and impl.get("attempt_id") is None, "autonomous IMPLEMENT occurred")

    publication_ok = False
    publisher_diag = "semantic worker did not return an accepted result"
    semantic_status = None
    result = evidence.get("semantic_result")
    if evidence.get("provider_outcome") == "semantic_result" and isinstance(result, dict):
        req(evidence.get("copilot_invocation_count") == 1, "semantic result without exactly one invocation")
        try:
            publication = validate_publication(request, result, state)
            publish_exact_report(ROOT, publication)
            publication_ok = True
            publisher_diag = "accepted exact worker result"
            semantic_status = result["status"]
        except Exception as exc:
            publisher_diag = f"publisher rejected result: {type(exc).__name__}: {exc}"
    else:
        req(evidence.get("copilot_invocation_count") == 0 or evidence.get("provider_outcome") != "provider_unavailable_zero_cost_gate", "zero-cost gate outcome inconsistent")

    task["assigned_slot"] = None
    if publication_ok:
        task["evidence_refs"].append(REPORT)
        task["status"] = "accepted" if semantic_status == "complete" else "blocked"
    else:
        task["status"] = "blocked"
        task["retry"]["failure_count"] = max(1, task["retry"].get("failure_count", 0))
        task["retry"]["last_failure"] = {
            "class": evidence.get("provider_outcome", "publisher_rejected"),
            "run_id": int(run_id),
        }
    slot2.update({"status": "free", "occupancy_type": None, "task_id": None, "task_file": None, "conflict_keys": [], "lease": None})
    state["state_revision"] += 1
    state["dispatch_enabled"] = False
    state["orchestration_phase"] = "copilot_cli_zero_cost_live_readonly_pilot_02_closed"
    state["copilot_cli_pilot02_closeout"] = {
        "status": "complete" if publication_ok else "blocked",
        "provider_outcome": evidence.get("provider_outcome"),
        "semantic_status": semantic_status,
        "attempt_id": ATTEMPT_ID,
        "lease_id": LEASE_ID,
        "base_sha": request["base_sha"],
        "task_file_blob_sha": TASK_BLOB,
        "report_path": REPORT if publication_ok else None,
        "automatic_next_dispatch": False,
        "paid_fallback_used": False,
        "copilot_invocation_count": evidence["copilot_invocation_count"],
        "source_run_id": int(run_id),
        "finalized_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    validate_state(p2a, state, events)
    persist_state(contract, ROOT / "orchestration/state.json", state)

    by_name = {j.get("name"): j for j in jobs}
    def jid(name):
        return str(by_name.get(name, {}).get("id", "unresolved-at-report-time"))

    q = evidence.get("quota_preflight") or {}
    status = "complete" if publication_ok else "blocked"
    post = evidence.get("quota_postflight")
    post_note = "not available" if not isinstance(post, dict) else str(post.get("reason", "returned"))
    semantic_path = REPORT if publication_ok else "not published"
    lines = [
        "# Copilot CLI Zero-Cost Live Read-Only Pilot 02",
        "", "## Status", "", f"`{status}`", "",
        "## Scope", "",
        f"Exactly one bounded provider-adapter pilot for `{TASK_FILE}`. No queue draining, no second dispatch, no autonomous `IMPLEMENT`, and no paid fallback.", "",
        "## Implementation and live run", "",
        f"- Launch commit: `{launch_sha}`",
        f"- Prepared state commit: `{prepared_head}`",
        f"- Bound base SHA: `{request['base_sha']}`",
        f"- GitHub Actions run ID: `{run_id}`",
        f"- Run attempt: `{run_attempt}`",
        f"- Prepare job ID: `{jid('prepare-exact-pilot-lease')}`",
        f"- Worker job ID: `{jid('copilot-cli-readonly-worker')}`",
        f"- Publisher job ID: `{jid('trusted-publisher-and-closeout')}`",
        f"- Copilot CLI version: `{evidence.get('copilot_cli_version', 'unknown')}`",
        "- Install method: `npm install -g @github/copilot@latest`",
        "- Quota preflight: `@github/copilot-sdk@latest` / `account.getQuota`", "",
        "## Authentication, entitlement, and cost gate", "",
        "Worker authentication was only the Actions built-in `GITHUB_TOKEN`; worker permissions were `contents: read` and `copilot-requests: write`. The workflow references no repository secret and supplies no PAT, `OPENAI_API_KEY`, provider secret, alternate provider, or paid fallback.", "",
        f"Quota preflight decision: `{q.get('reason')}`.",
        f"Zero-additional-payment gate passed: `{q.get('safeForZeroAdditionalPayment')}`.", "",
        *quota_lines(evidence), "",
        f"Postflight quota snapshot: `{post_note}`.",
        "Exact AI-credit consumption is reported only if GitHub safely exposes it; no estimate is substituted for an unobservable value.", "",
        "## Exact worker binding", "",
        f"- task: `{request['task_id']}`",
        f"- revision: `{request['task_revision']}`",
        f"- attempt: `{request['attempt_number']}`",
        f"- attempt ID: `{request['attempt_id']}`",
        f"- lease ID: `{request['lease_id']}`",
        f"- worker mode: `{request['mode']}`",
        f"- task file: `{request['task_file']}`",
        f"- task-file blob: `{request['task_file_blob_sha']}`",
        f"- base SHA: `{request['base_sha']}`",
        f"- exact semantic report path: `{request['expected_report_path']}`",
        f"- Copilot CLI semantic invocations: `{evidence['copilot_invocation_count']}`", "",
        "## Worker conclusion", "",
        f"Provider outcome: `{evidence.get('provider_outcome')}`.",
        f"Diagnostic: `{evidence.get('provider_diagnostic') or 'none'}`.",
        f"Semantic worker status: `{(result or {}).get('status', 'not produced')}`.", "",
        "## Trusted publisher conclusion", "",
        f"Publication accepted: `{publication_ok}`.",
        f"Semantic report: `{semantic_path}`.",
        f"Publisher diagnostic: `{publisher_diag}`.", "",
        "## Security and dispatch invariants", "",
        "- Worker checkout used `persist-credentials: false` and had no `contents: write`.",
        "- Publisher had `contents: write` but no `copilot-requests` permission.",
        "- General `dispatch_enabled` remained `false`.",
        "- Copilot invocation count is 0 or 1; the workflow contains no retry loop.",
        "- `top-summary-filter-buttons-01` remained `IMPLEMENT` at attempt 0.",
        "- No automatic next dispatch occurred.",
        "- No PAT, OpenAI API key, paid-overage enablement, paid provider fallback, or second provider was used.", "",
        "## Final decision", "",
    ]
    if publication_ok:
        lines.append("A real Copilot CLI semantic worker executed exactly once after the zero-cost quota gate passed, and the trusted publisher accepted the exact semantic report. General dispatch remains disabled; broader enablement is out of scope.")
    else:
        lines.append("Pilot 02 is closed `blocked`. The zero-cost/auth/quota/provider or publisher gate did not permit a successful durable semantic publication. No paid fallback and no second dispatch were attempted.")
    (ROOT / PILOT_REPORT).write_text("\n".join(lines) + "\n", encoding="utf-8")


def selftest() -> None:
    c = pilot_contract()
    assert c["worker"]["permissions"] == {"contents": "read", "copilot-requests": "write"}
    assert c["worker"]["available_tools"] == ["view", "glob", "grep", "web_fetch"]
    assert c["worker"]["repository_write_authority"] is False
    assert c["worker"]["state_write_authority"] is False
    assert c["worker"]["product_write_authority"] is False
    assert c["worker"]["worker_can_choose_next_task"] is False
    assert c["publisher"]["exact_report_path_only"] is True
    assert c["publisher"]["requires_active_lease"] is True
    print("Pilot 02 contract selftest: OK")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--base-sha", required=True)
    p.add_argument("--out-request", required=True)
    p.add_argument("--out-meta", required=True)
    f = sub.add_parser("finalize")
    f.add_argument("--request", required=True)
    f.add_argument("--evidence", required=True)
    f.add_argument("--jobs", required=True)
    f.add_argument("--launch-sha", required=True)
    f.add_argument("--prepared-head", required=True)
    f.add_argument("--run-id", required=True)
    f.add_argument("--run-attempt", required=True)
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "prepare": prepare(a.base_sha, a.out_request, a.out_meta)
    elif a.cmd == "finalize": finalize(a.request, a.evidence, a.jobs, a.launch_sha, a.prepared_head, a.run_id, a.run_attempt)
    else: selftest()


if __name__ == "__main__":
    main()
