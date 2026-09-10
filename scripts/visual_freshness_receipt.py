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
COMMERCIAL_PAYLOAD_PATH = "data/production/pre_ai/chatgpt_payload.json"
COMMERCIAL_STORE_PATH = "data/production/pre_ai/store_snapshot.json"
COMMERCIAL_FAMILY_PATH = "data/production/pre_ai/family_graph.json"
COMMERCIAL_HELPER_PATH = "scripts/refresh_visual_commercial_fields.py"
GIVEAWAY_PATH = "data/production/giveaways/v1/current.json"
VISUAL_PATH = "data/production/visual/current.json"
FULL_SCOPE = "full_visual"
GIVEAWAY_SCOPE = "giveaway_only"
COMMERCIAL_SCOPE = "commercial_only"
GIVEAWAY_REASON = "giveaway_only_refresh"
COMMERCIAL_REASON = "commercial_only_refresh"
DETERMINISTIC_REFRESH_REASON = "deterministic_refresh_preserved_semantic_history"

COMMERCIAL_BLOB_BINDINGS = {
    "payload_blob_sha": (COMMERCIAL_PAYLOAD_PATH, "commercial_source_payload_blob_sha"),
    "store_snapshot_blob_sha": (COMMERCIAL_STORE_PATH, "commercial_source_store_snapshot_blob_sha"),
    "family_graph_blob_sha": (COMMERCIAL_FAMILY_PATH, "commercial_source_family_graph_blob_sha"),
    "history_snapshot_blob_sha": (HISTORY_PATH, "commercial_source_history_snapshot_blob_sha"),
    "helper_blob_sha": (COMMERCIAL_HELPER_PATH, "commercial_refresh_helper_blob_sha"),
}


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


def _read_json_optional(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.exists():
        return {}, "missing"
    try:
        value = _read_json(path)
    except (json.JSONDecodeError, OSError) as exc:
        return {}, f"{type(exc).__name__}: {exc}"
    return value, None


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _as_bool(value: str | None) -> bool:
    return (value or "").strip().lower() == "true"


def _commercial_intent_ready(commercial: dict[str, Any]) -> bool:
    source = commercial.get("source_mailing_updated_at_utc")
    if not source:
        return False
    if commercial.get("store_source_updated_at_utc") != source:
        return False
    if commercial.get("family_source_updated_at_utc") != source:
        return False
    return all(commercial.get(key) for key in COMMERCIAL_BLOB_BINDINGS)


def capture_intent(repo: Path) -> dict[str, Any]:
    history_file = repo / HISTORY_PATH
    history_blob_sha = _git_optional("rev-parse", f"HEAD:{HISTORY_PATH}", cwd=repo)
    giveaway_blob_sha = _git_optional("rev-parse", f"HEAD:{GIVEAWAY_PATH}", cwd=repo)
    history, history_parse_error = _read_json_optional(history_file)
    payload, payload_parse_error = _read_json_optional(repo / COMMERCIAL_PAYLOAD_PATH)
    store, store_parse_error = _read_json_optional(repo / COMMERCIAL_STORE_PATH)
    family, family_parse_error = _read_json_optional(repo / COMMERCIAL_FAMILY_PATH)

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
    commercial_source = {
        "source_mailing_updated_at_utc": payload.get("source_mailing_updated_at_utc"),
        "store_source_updated_at_utc": store.get("discovery_source_updated_at_utc"),
        "family_source_updated_at_utc": family.get("source_updated_at_utc"),
        "store_observed_at_utc": store.get("observed_at_utc"),
        "payload_blob_sha": _git_optional("rev-parse", f"HEAD:{COMMERCIAL_PAYLOAD_PATH}", cwd=repo),
        "store_snapshot_blob_sha": _git_optional("rev-parse", f"HEAD:{COMMERCIAL_STORE_PATH}", cwd=repo),
        "family_graph_blob_sha": _git_optional("rev-parse", f"HEAD:{COMMERCIAL_FAMILY_PATH}", cwd=repo),
        "history_snapshot_blob_sha": history_blob_sha,
        "helper_blob_sha": _git_optional("rev-parse", f"HEAD:{COMMERCIAL_HELPER_PATH}", cwd=repo),
        "parse_errors": {
            key: value
            for key, value in {
                "payload": payload_parse_error,
                "store_snapshot": store_parse_error,
                "family_graph": family_parse_error,
                "history_snapshot": history_parse_error,
            }.items()
            if value
        },
    }
    return {
        "captured_checkout_commit_sha": _git_optional("rev-parse", "HEAD", cwd=repo),
        "history_snapshot_blob_sha": history_blob_sha,
        "giveaway_snapshot_blob_sha": giveaway_blob_sha,
        "history_snapshot_present": history_file.exists(),
        "history_snapshot_parse_error": history_parse_error,
        "history_status": history.get("status"),
        "history_complete_coverage": history.get("complete_coverage"),
        "source_cycle": source_cycle,
        "semantic_state": {
            "payload_status": payload.get("status"),
            "ai_queue_count": payload.get("ai_queue_count"),
            "complete_family_partition": payload.get("complete_family_partition"),
        },
        "commercial_source": commercial_source,
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
    giveaways = data.get("giveaways") or {}
    paid_freshness = data.get("paid_list_freshness") or {}
    return {
        "blob_sha": blob_sha,
        "commit_sha": commit_sha,
        "source_history_snapshot_blob_sha": contract.get("source_history_snapshot_blob_sha"),
        "source_giveaway_snapshot_blob_sha": contract.get("source_giveaway_snapshot_blob_sha"),
        "commercial_source_payload_blob_sha": contract.get("commercial_source_payload_blob_sha"),
        "commercial_source_store_snapshot_blob_sha": contract.get("commercial_source_store_snapshot_blob_sha"),
        "commercial_source_family_graph_blob_sha": contract.get("commercial_source_family_graph_blob_sha"),
        "commercial_source_history_snapshot_blob_sha": contract.get("commercial_source_history_snapshot_blob_sha"),
        "commercial_refresh_helper_blob_sha": contract.get("commercial_refresh_helper_blob_sha"),
        "commercial_source_mailing_updated_at_utc": data.get("commercial_source_mailing_updated_at_utc"),
        "commercial_store_observed_at_utc": data.get("commercial_store_observed_at_utc"),
        "paid_list_freshness": paid_freshness,
        "giveaway_state": giveaways.get("state"),
        "giveaway_generated_at_utc": giveaways.get("generated_at_utc"),
        "giveaway_fresh_until_utc": giveaways.get("fresh_until_utc"),
    }


def _commercial_visual_matches(observed: dict[str, Any], commercial: dict[str, Any]) -> bool:
    source = commercial.get("source_mailing_updated_at_utc")
    if observed.get("commercial_source_mailing_updated_at_utc") != source:
        return False
    paid = observed.get("paid_list_freshness") or {}
    if paid.get("status") != "published" or paid.get("scope") != COMMERCIAL_SCOPE:
        return False
    if paid.get("source_mailing_updated_at_utc") != source:
        return False
    if paid.get("store_observed_at_utc") != commercial.get("store_observed_at_utc"):
        return False
    for intent_key, (_, contract_key) in COMMERCIAL_BLOB_BINDINGS.items():
        expected = commercial.get(intent_key)
        if observed.get(contract_key) != expected:
            return False
        if paid.get(intent_key) != expected:
            return False
    return True


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
    scoped_giveaway = reason_override == GIVEAWAY_REASON
    scoped_commercial = reason_override == COMMERCIAL_REASON
    if scoped_giveaway:
        freshness_scope = GIVEAWAY_SCOPE
    elif scoped_commercial:
        freshness_scope = COMMERCIAL_SCOPE
    else:
        freshness_scope = FULL_SCOPE

    intended_history = intent.get("history_snapshot_blob_sha")
    intended_giveaway = intent.get("giveaway_snapshot_blob_sha")
    intended_commercial = intent.get("commercial_source") or {}
    semantic_state = intent.get("semantic_state") or {}
    try:
        pending_semantic_queue = int(semantic_state.get("ai_queue_count") or 0) > 0
    except (TypeError, ValueError):
        pending_semantic_queue = False

    # Scoped publication is a real bounded build but must never claim the unrelated
    # visual domains are globally fresh. Likewise, a FORCE deterministic refresh
    # while semantic work remains queued may persist a new visual blob, but it must
    # preserve the last accepted semantic history and therefore cannot claim full
    # semantic freshness.
    if scoped_giveaway:
        fresh_build = bool(persisted and intended_giveaway)
    elif scoped_commercial:
        fresh_build = bool(persisted and _commercial_intent_ready(intended_commercial))
    else:
        fresh_build = bool(
            build_reported
            and persisted
            and intended_history
            and not pending_semantic_queue
        )

    observed_visual: dict[str, Any] | None = None
    if scoped_giveaway or scoped_commercial:
        reason = None
    elif pending_semantic_queue and build_reported and persisted:
        reason = DETERMINISTIC_REFRESH_REASON
    else:
        reason = reason_override

    if fresh_build:
        observed_visual = _visual_state(repo)
        if scoped_giveaway:
            if observed_visual.get("source_giveaway_snapshot_blob_sha") != intended_giveaway:
                fresh_build = False
                reason = "visual_source_giveaway_mismatch"
        elif scoped_commercial:
            if not _commercial_visual_matches(observed_visual, intended_commercial):
                fresh_build = False
                reason = "visual_source_commercial_mismatch"
        elif observed_visual.get("source_history_snapshot_blob_sha") != intended_history:
            fresh_build = False
            reason = "visual_source_history_mismatch"

    if not fresh_build and not reason:
        if scoped_giveaway:
            if not intended_giveaway:
                reason = "missing_intended_giveaway_snapshot"
            elif not persisted:
                reason = "giveaway_only_refresh_not_persisted"
            else:
                reason = "no_fresh_giveaway_build"
        elif scoped_commercial:
            if not _commercial_intent_ready(intended_commercial):
                reason = "missing_or_unbound_intended_commercial_source"
            elif not persisted:
                reason = "commercial_only_refresh_not_persisted"
            else:
                reason = "no_fresh_commercial_build"
        elif not intended_history:
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
    scoped = scoped_giveaway or scoped_commercial
    receipt = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT,
        "fresh_build": fresh_build,
        "freshness_scope": freshness_scope,
        "full_visual_freshness": bool(fresh_build and not scoped),
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


def _verify_current_commercial_sources(repo: Path, commercial: dict[str, Any]) -> None:
    if not _commercial_intent_ready(commercial):
        raise SystemExit("fresh commercial receipt missing exact intended commercial source")
    for intent_key, (path, _) in COMMERCIAL_BLOB_BINDINGS.items():
        intended_blob = commercial.get(intent_key)
        current_blob = _git("rev-parse", f"HEAD:{path}", cwd=repo)
        if current_blob != intended_blob:
            raise SystemExit(
                f"stale commercial source mismatch: path={path} current={current_blob} receipt={intended_blob}"
            )


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

    scope = receipt.get("freshness_scope") or FULL_SCOPE
    if scope not in {FULL_SCOPE, GIVEAWAY_SCOPE, COMMERCIAL_SCOPE}:
        raise SystemExit(f"unsupported visual freshness scope: {scope}")

    if receipt.get("fresh_build") is not True:
        if receipt.get("outcome") != "degraded/no_fresh_build":
            raise SystemExit("fresh_build=false receipt missing degraded/no_fresh_build outcome")
        print(
            "VISUAL_FRESHNESS=degraded/no_fresh_build "
            f"scope={scope} reason={receipt.get('reason') or 'unspecified'} run_id={expected_run_id}"
        )
        return "degraded/no_fresh_build"

    if receipt.get("outcome") != "fresh_build":
        raise SystemExit("fresh_build=true receipt has non-fresh outcome")

    intended = receipt.get("intended_source_cycle") or {}
    produced = receipt.get("produced_visual") or {}
    expected_blob = produced.get("blob_sha")
    expected_commit = produced.get("commit_sha")
    if not expected_blob or not expected_commit:
        raise SystemExit("fresh receipt missing produced visual identity")

    if scope == GIVEAWAY_SCOPE:
        if receipt.get("full_visual_freshness") is not False:
            raise SystemExit("giveaway-only receipt must not claim full visual freshness")
        intended_giveaway = intended.get("giveaway_snapshot_blob_sha")
        produced_giveaway = produced.get("source_giveaway_snapshot_blob_sha")
        if not intended_giveaway:
            raise SystemExit("fresh giveaway receipt missing intended giveaway snapshot")
        current_giveaway = _git("rev-parse", f"HEAD:{GIVEAWAY_PATH}", cwd=repo)
        if current_giveaway != intended_giveaway:
            raise SystemExit(
                f"stale giveaway source mismatch: current_giveaway={current_giveaway} receipt_giveaway={intended_giveaway}"
            )
        if produced_giveaway != intended_giveaway:
            raise SystemExit(
                f"produced giveaway provenance mismatch: visual_giveaway={produced_giveaway} receipt_giveaway={intended_giveaway}"
            )
    elif scope == COMMERCIAL_SCOPE:
        if receipt.get("full_visual_freshness") is not False:
            raise SystemExit("commercial-only receipt must not claim full visual freshness")
        intended_commercial = intended.get("commercial_source") or {}
        _verify_current_commercial_sources(repo, intended_commercial)
        if not _commercial_visual_matches(produced, intended_commercial):
            raise SystemExit("produced visual/commercial provenance mismatch")
    else:
        if receipt.get("full_visual_freshness") is not True:
            raise SystemExit("full visual fresh receipt missing full_visual_freshness=true")
        intended_history = intended.get("history_snapshot_blob_sha")
        if not intended_history:
            raise SystemExit("fresh receipt missing intended history")
        current_history = _git("rev-parse", f"HEAD:{HISTORY_PATH}", cwd=repo)
        if current_history != intended_history:
            raise SystemExit(
                f"stale source cycle mismatch: current_history={current_history} receipt_history={intended_history}"
            )
        if produced.get("source_history_snapshot_blob_sha") != intended_history:
            raise SystemExit(
                "produced visual/source provenance mismatch: "
                f"visual_history={produced.get('source_history_snapshot_blob_sha')} receipt_history={intended_history}"
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
    contract = visual.get("production_contract") or {}
    if scope == GIVEAWAY_SCOPE:
        intended_giveaway = intended.get("giveaway_snapshot_blob_sha")
        visual_giveaway = contract.get("source_giveaway_snapshot_blob_sha")
        if visual_giveaway != intended_giveaway:
            raise SystemExit(
                f"visual/giveaway provenance mismatch: visual_giveaway={visual_giveaway} receipt_giveaway={intended_giveaway}"
            )
    elif scope == COMMERCIAL_SCOPE:
        intended_commercial = intended.get("commercial_source") or {}
        current_state = _visual_state(repo)
        if not _commercial_visual_matches(current_state, intended_commercial):
            raise SystemExit("visual/commercial provenance mismatch")
    else:
        intended_history = intended.get("history_snapshot_blob_sha")
        visual_history = contract.get("source_history_snapshot_blob_sha")
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

    if scope == GIVEAWAY_SCOPE:
        print(
            "VISUAL_FRESHNESS=fresh scope=giveaway_only "
            f"run_id={expected_run_id} giveaway_blob={intended.get('giveaway_snapshot_blob_sha')} "
            f"visual_blob={expected_blob} visual_commit={expected_commit} full_visual_freshness=false"
        )
    elif scope == COMMERCIAL_SCOPE:
        commercial = intended.get("commercial_source") or {}
        print(
            "VISUAL_FRESHNESS=fresh scope=commercial_only "
            f"run_id={expected_run_id} source={commercial.get('source_mailing_updated_at_utc')} "
            f"store_blob={commercial.get('store_snapshot_blob_sha')} visual_blob={expected_blob} "
            f"visual_commit={expected_commit} full_visual_freshness=false"
        )
    else:
        print(
            "VISUAL_FRESHNESS=fresh scope=full_visual "
            f"run_id={expected_run_id} history_blob={intended.get('history_snapshot_blob_sha')} "
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
            f"scope={receipt['freshness_scope']} outcome={receipt['outcome']} reason={receipt.get('reason')}"
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
