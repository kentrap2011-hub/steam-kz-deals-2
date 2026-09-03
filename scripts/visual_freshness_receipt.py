#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

CONTRACT = "visual-freshness-receipt-v1"
SCHEMA_VERSION = 1
HISTORY_PATH = "data/production/pre_ai/history_snapshot.json"
VISUAL_PATH = "data/production/visual/current.json"


def _git(*args: str, cwd: Path) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def _git_optional(*args: str, cwd: Path) -> str | None:
    try:
        value = _git(*args, cwd=cwd)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return value or None


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_bool(value: str | None) -> bool:
    return (value or "").strip().lower() == "true"


def capture_intent(repo: Path) -> dict[str, Any]:
    history_file = repo / HISTORY_PATH
    blob_sha = _git_optional("rev-parse", f"HEAD:{HISTORY_PATH}", cwd=repo)
    history: dict[str, Any] = {}
    if history_file.exists():
        history = _read_json(history_file)

    source_cycle = {
        key: history.get(key)
        for key in (
            "source_mailing_updated_at_utc",
            "source_mailing_generated_at_utc",
            "generated_at_utc",
            "persistent_cache_updated_at_utc",
        )
        if history.get(key) is not None
    }
    return {
        "history_snapshot_blob_sha": blob_sha,
        "history_snapshot_present": history_file.exists(),
        "history_status": history.get("status"),
        "history_complete_coverage": history.get("complete_coverage"),
        "source_cycle": source_cycle,
    }


def _visual_state(repo: Path) -> dict[str, Any]:
    visual_file = repo / VISUAL_PATH
    data = _read_json(visual_file)
    contract = data.get("production_contract") or {}
    blob_sha = _git("rev-parse", f"HEAD:{VISUAL_PATH}", cwd=repo)
    commit_sha = _git("log", "-1", "--format=%H", "--", VISUAL_PATH, cwd=repo)
    commit_blob_sha = _git("rev-parse", f"{commit_sha}:{VISUAL_PATH}", cwd=repo)
    if commit_blob_sha != blob_sha:
        raise SystemExit(
            f"canonical visual commit/blob mismatch: commit_blob={commit_blob_sha} head_blob={blob_sha}"
        )
    return {
        "blob_sha": blob_sha,
        "commit_sha": commit_sha,
        "source_history_snapshot_blob_sha": contract.get("source_history_snapshot_blob_sha"),
    }


def create_receipt(
    repo: Path,
    intent: dict[str, Any],
    *,
    run_id: str,
    run_attempt: str,
    event_name: str,
    workflow_head_sha: str,
    upstream_run_id: str | None,
    upstream_head_sha: str | None,
    build_reported: bool,
    persisted: bool,
    history_ready: bool,
    reason_override: str | None,
) -> dict[str, Any]:
    intended_history = intent.get("history_snapshot_blob_sha")
    fresh_build = bool(build_reported and persisted and intended_history)
    observed_visual: dict[str, Any] | None = None
    reason = reason_override

    if fresh_build:
        observed_visual = _visual_state(repo)
        if observed_visual.get("source_history_snapshot_blob_sha") != intended_history:
            fresh_build = False
            reason = "visual_source_history_mismatch"

    if not fresh_build and not reason:
        if not intended_history:
            reason = "missing_intended_history_snapshot"
        elif not history_ready:
            reason = "prerequisite_not_ready"
        elif not build_reported:
            reason = "build_reported_no_fresh_change"
        elif not persisted:
            reason = "canonical_persistence_failed"
        else:
            reason = "no_fresh_build"

    produced_visual = observed_visual if fresh_build else None
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT,
        "fresh_build": fresh_build,
        "outcome": "fresh_build" if fresh_build else "degraded/no_fresh_build",
        "reason": None if fresh_build else reason,
        "intended_source_cycle": intent,
        "produced_visual": produced_visual,
        "workflow_run": {
            "id": int(run_id),
            "attempt": int(run_attempt),
            "event": event_name,
            "head_sha": workflow_head_sha or None,
            "upstream_workflow_run_id": int(upstream_run_id) if upstream_run_id else None,
            "upstream_head_sha": upstream_head_sha or None,
        },
    }
    if observed_visual and not fresh_build:
        receipt["observed_visual"] = observed_visual
    return receipt


def verify_receipt(
    repo: Path,
    receipt: dict[str, Any],
    *,
    expected_run_id: str,
    staged_path: Path,
) -> str:
    if receipt.get("schema_version") != SCHEMA_VERSION or receipt.get("contract") != CONTRACT:
        raise SystemExit("unsupported visual freshness receipt contract")

    run = receipt.get("workflow_run") or {}
    if str(run.get("id")) != str(expected_run_id):
        raise SystemExit(
            f"freshness receipt run mismatch: receipt={run.get('id')} expected={expected_run_id}"
        )

    if receipt.get("fresh_build") is not True:
        if receipt.get("outcome") != "degraded/no_fresh_build":
            raise SystemExit("fresh_build=false receipt missing degraded/no_fresh_build outcome")
        print(
            "VISUAL_FRESHNESS=degraded/no_fresh_build "
            f"reason={receipt.get('reason') or 'unspecified'} run_id={expected_run_id}"
        )
        return "degraded/no_fresh_build"

    if receipt.get("outcome") != "fresh_build":
        raise SystemExit("fresh_build=true receipt has non-fresh outcome")

    intended = receipt.get("intended_source_cycle") or {}
    intended_history = intended.get("history_snapshot_blob_sha")
    produced = receipt.get("produced_visual") or {}
    expected_blob = produced.get("blob_sha")
    expected_commit = produced.get("commit_sha")
    if not intended_history or not expected_blob or not expected_commit:
        raise SystemExit("fresh receipt missing intended history or produced visual identity")

    current_history = _git("rev-parse", f"HEAD:{HISTORY_PATH}", cwd=repo)
    if current_history != intended_history:
        raise SystemExit(
            f"stale source cycle mismatch: current_history={current_history} receipt_history={intended_history}"
        )

    current_blob = _git("rev-parse", f"HEAD:{VISUAL_PATH}", cwd=repo)
    if current_blob != expected_blob:
        raise SystemExit(
            f"stale visual blob mismatch: current_blob={current_blob} receipt_blob={expected_blob}"
        )

    current_visual_commit = _git("log", "-1", "--format=%H", "--", VISUAL_PATH, cwd=repo)
    if current_visual_commit != expected_commit:
        raise SystemExit(
            f"visual commit mismatch: current_commit={current_visual_commit} receipt_commit={expected_commit}"
        )

    commit_blob = _git("rev-parse", f"{expected_commit}:{VISUAL_PATH}", cwd=repo)
    if commit_blob != expected_blob:
        raise SystemExit(
            f"receipt commit/blob mismatch: commit_blob={commit_blob} receipt_blob={expected_blob}"
        )

    visual = _read_json(repo / VISUAL_PATH)
    visual_history = (visual.get("production_contract") or {}).get("source_history_snapshot_blob_sha")
    if visual_history != intended_history:
        raise SystemExit(
            f"visual/source provenance mismatch: visual_history={visual_history} receipt_history={intended_history}"
        )

    staged_bytes = staged_path.read_bytes()
    canonical_bytes = (repo / VISUAL_PATH).read_bytes()
    if staged_bytes != canonical_bytes:
        raise SystemExit("staged visual payload differs from canonical current.json")

    staged_blob = subprocess.check_output(
        ["git", "hash-object", "--stdin"], cwd=repo, input=staged_bytes
    ).decode("utf-8").strip()
    if staged_blob != expected_blob:
        raise SystemExit(
            f"staged visual blob mismatch: staged_blob={staged_blob} receipt_blob={expected_blob}"
        )

    print(
        "VISUAL_FRESHNESS=fresh "
        f"run_id={expected_run_id} history_blob={intended_history} "
        f"visual_blob={expected_blob} visual_commit={expected_commit}"
    )
    return "fresh"


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture-intent")
    capture.add_argument("--repo", default=".")
    capture.add_argument("--output", required=True)

    create = sub.add_parser("create-receipt")
    create.add_argument("--repo", default=".")
    create.add_argument("--intent", required=True)
    create.add_argument("--output", required=True)
    create.add_argument("--run-id", required=True)
    create.add_argument("--run-attempt", required=True)
    create.add_argument("--event-name", required=True)
    create.add_argument("--workflow-head-sha", default="")
    create.add_argument("--upstream-run-id", default="")
    create.add_argument("--upstream-head-sha", default="")
    create.add_argument("--build-reported", default="false")
    create.add_argument("--persisted", default="false")
    create.add_argument("--history-ready", default="false")
    create.add_argument("--reason", default="")

    verify = sub.add_parser("verify-receipt")
    verify.add_argument("--repo", default=".")
    verify.add_argument("--receipt", required=True)
    verify.add_argument("--expected-run-id", required=True)
    verify.add_argument("--staged-path", required=True)

    args = parser.parse_args()
    repo = Path(args.repo).resolve()

    if args.command == "capture-intent":
        _write_json(Path(args.output), capture_intent(repo))
        return

    if args.command == "create-receipt":
        intent = _read_json(Path(args.intent))
        receipt = create_receipt(
            repo,
            intent,
            run_id=args.run_id,
            run_attempt=args.run_attempt,
            event_name=args.event_name,
            workflow_head_sha=args.workflow_head_sha,
            upstream_run_id=args.upstream_run_id or None,
            upstream_head_sha=args.upstream_head_sha or None,
            build_reported=_as_bool(args.build_reported),
            persisted=_as_bool(args.persisted),
            history_ready=_as_bool(args.history_ready),
            reason_override=args.reason or None,
        )
        _write_json(Path(args.output), receipt)
        print(
            f"FRESHNESS_RECEIPT fresh_build={str(receipt['fresh_build']).lower()} "
            f"outcome={receipt['outcome']} reason={receipt.get('reason')}"
        )
        return

    receipt = _read_json(Path(args.receipt))
    verify_receipt(
        repo,
        receipt,
        expected_run_id=args.expected_run_id,
        staged_path=Path(args.staged_path),
    )


if __name__ == "__main__":
    main()
