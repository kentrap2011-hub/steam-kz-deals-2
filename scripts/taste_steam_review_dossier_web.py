#!/usr/bin/env python3
"""V2 web-evidence helpers layered on the unchanged GitHub dossier control plane."""
import copy
from datetime import datetime, timezone

from taste_steam_review_dossier import (
    SEMANTIC_INPUT_SCHEMA,
    atomic_write_json,
    canonical_sha256,
    dossier_path,
    load_dossier_if_present,
    parse_utc,
    resolve_ttl_days,
    utc_iso,
    validate_pin,
)
from taste_steam_review_dossier_daily import (
    WORK_SCHEMA,
    build_submission_group_plan,
    canonical_dossier_scope_rows,
    progress_fields,
    validate_manifest,
)
from taste_steam_review_dossier_strict import (
    current_worker_contract_binding,
    dossier_state_strict,
    validate_dossiers_against_expected_items,
)


def ensure_web_evidence_binding(manifest):
    """Add/validate semantic worker version metadata without changing snapshot/group identity."""
    out = copy.deepcopy(manifest)
    expected = current_worker_contract_binding()
    existing = out.get("web_evidence_contract_binding")
    if existing is not None and existing != expected:
        raise ValueError("existing daily dossier snapshot has incompatible web-evidence binding")
    out["web_evidence_contract_binding"] = expected
    return out


def build_daily_work_manifest_web(queue_rows, contract, store_dir, *, now=None, ttl_days=None, source_queue_path=None):
    """Prepare a fixed daily snapshot while treating legacy/non-V2 cache entries as invalid."""
    from zoneinfo import ZoneInfo
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    ttl = resolve_ttl_days(contract, ttl_days)
    checkpoint_size = int(contract["checkpointing"]["checkpoint_size"])
    source_queue_sha = canonical_sha256(queue_rows)
    scope_rows = canonical_dossier_scope_rows(queue_rows, contract)
    eligible_row_count = sum(
        1 for row in queue_rows
        if isinstance(row, dict) and any(
            item in set(contract["scope"]["taste_semantic_work_required_any"])
            for item in (row.get("work_required") or [])
        )
    )
    items = []
    required = []
    for row in scope_rows:
        appid = row["appid"]
        existing = load_dossier_if_present(store_dir, appid)
        try:
            state = dossier_state_strict(
                existing,
                contract,
                now=now,
                expected_appid=appid,
                expected_title=row["title"],
                expected_ttl_days=ttl,
            )
        except ValueError:
            state = "invalid"
        item = {
            "key": row["key"], "appid": appid, "title": row["title"],
            "dossier_path": dossier_path(store_dir, appid).as_posix(), "state": state,
        }
        if existing and state == "fresh":
            item.update({
                "generated_at_utc": existing["generated_at_utc"],
                "expires_at_utc": existing["expires_at_utc"],
                "dossier_sha256": canonical_sha256(existing),
            })
        else:
            reason = "refresh_required" if state in {"stale", "invalid", "invalid_future"} else "missing_dossier"
            item["reason"] = reason
            required.append({
                "key": row["key"], "appid": appid, "title": row["title"],
                "dossier_path": item["dossier_path"], "reason": reason,
            })
        items.append(item)

    prepared_date = now.astimezone(ZoneInfo("Europe/Samara")).date().isoformat()
    eligible_binding = [{"key": r["key"], "appid": r["appid"]} for r in scope_rows]
    eligible_sha = canonical_sha256(eligible_binding)
    required_sha = canonical_sha256(required)
    snapshot_id = canonical_sha256({
        "prepared_for_date": prepared_date,
        "source_queue_sha256": source_queue_sha,
        "eligible_scope_sha256": eligible_sha,
        "prepared_required_sha256": required_sha,
        "ttl_days": ttl,
    })
    source_path = source_queue_path or contract["paths"]["taste_queue"]
    group_plan = build_submission_group_plan(
        snapshot_id=snapshot_id,
        prepared_required_sha256=required_sha,
        prepared_required_items=required,
        checkpoint_size=checkpoint_size,
        scope_source=contract["scope"]["source"],
        source_queue_sha256=source_queue_sha,
    )
    manifest = {
        "schema": WORK_SCHEMA,
        "schema_version": 2,
        "preparation_mode": "daily_fixed_full_backlog",
        "snapshot_id": snapshot_id,
        "prepared_at_utc": utc_iso(now),
        "prepared_for_date": prepared_date,
        "ttl_days": ttl,
        "scope_source": contract["scope"]["source"],
        "source_queue_path": source_path,
        "source_queue_sha256": source_queue_sha,
        "source_row_count": len(queue_rows),
        "eligible_row_count": eligible_row_count,
        "excluded_row_count": len(queue_rows) - eligible_row_count,
        "unique_appid_count": len(scope_rows),
        "deduplicated_row_count": eligible_row_count - len(scope_rows),
        "eligible_scope_count": len(scope_rows),
        "eligible_scope_sha256": eligible_sha,
        "ordered_appids": [r["appid"] for r in scope_rows],
        "items": items,
        "prepared_required_items": required,
        "prepared_required_count": len(required),
        "prepared_required_sha256": required_sha,
        "checkpoint_size": checkpoint_size,
        "checkpoint_semantics": "internal_durability_boundary_not_scope_quota",
        "sampling_policy": contract["sampling"],
        "web_evidence_contract_binding": current_worker_contract_binding(),
        "submission_group_plan": group_plan,
    }
    manifest.update(progress_fields(snapshot_id, required, list(required), checkpoint_size))
    validate_manifest(manifest, contract)
    return manifest


def persist_submission_and_advance_snapshot_strict(submission, manifest, contract, store_dir, *, manifest_output_path=None):
    if not isinstance(submission, dict) or submission.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-SUBMISSION-V1" or submission.get("schema_version") != 1:
        raise ValueError("unsupported dossier submission schema")
    current = validate_manifest(manifest, contract)
    if manifest["status"] != "work_required" or not current:
        raise ValueError("no dossier checkpoint work is currently prepared")
    for field in ("snapshot_id", "scope_sha256", "scope_source", "source_queue_sha256"):
        if submission.get(field) != manifest.get(field):
            raise ValueError(f"dossier submission {field} mismatch")
    docs = validate_dossiers_against_expected_items(
        submission.get("dossiers"), current, contract, expected_ttl_days=manifest["ttl_days"]
    )
    persisted = []
    for doc in docs:
        path = dossier_path(store_dir, str(doc["appid"]))
        atomic_write_json(path, doc)
        persisted.append({"appid": str(doc["appid"]), "path": path.as_posix(), "dossier_sha256": canonical_sha256(doc)})

    next_manifest = copy.deepcopy(manifest)
    remaining = list(manifest["remaining_required_items"])
    if remaining[:len(current)] != list(current):
        raise ValueError("current checkpoint is not the canonical prefix of remaining daily snapshot scope")
    next_remaining = remaining[len(current):]
    next_manifest.update(progress_fields(
        manifest["snapshot_id"], manifest["prepared_required_items"], next_remaining,
        int(contract["checkpointing"]["checkpoint_size"]),
    ))
    next_manifest = ensure_web_evidence_binding(next_manifest)
    validate_manifest(next_manifest, contract)
    if manifest_output_path is not None:
        atomic_write_json(manifest_output_path, next_manifest)
    return persisted, next_manifest


def build_semantic_input_strict(pin, contract, store_dir, *, now=None):
    """Keep Taste Semantic Producer input shape unchanged while requiring fresh V2 dossiers."""
    validate_pin(pin)
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    rows = []
    missing = []
    for row in pin["ordered_rows"]:
        appid = str(row["appid"])
        doc = load_dossier_if_present(store_dir, appid)
        try:
            state = dossier_state_strict(doc, contract, now=now, expected_appid=appid)
        except ValueError as exc:
            missing.append({"key": row["key"], "appid": appid, "state": "invalid", "error": str(exc)})
            continue
        if state != "fresh":
            missing.append({"key": row["key"], "appid": appid, "state": state})
            continue
        rows.append({
            "key": row["key"],
            "appid": appid,
            "taste_fingerprint": row.get("taste_fingerprint"),
            "candidate_context_sha256": row.get("candidate_context_sha256"),
            "work_required": list(row.get("work_required") or []),
            "dossier": doc,
            "dossier_binding": {
                "dossier_sha256": canonical_sha256(doc),
                "generated_at_utc": doc["generated_at_utc"],
                "expires_at_utc": doc["expires_at_utc"],
            },
        })
    if missing:
        raise ValueError("Taste semantic input held: missing/stale/invalid web-evidence dossier(s): " + __import__("json").dumps(missing, ensure_ascii=False))
    out = {
        "schema": SEMANTIC_INPUT_SCHEMA,
        "schema_version": 1,
        "status": "ready_for_taste_semantic_producer",
        "prepared_at_utc": utc_iso(now),
        "pin": {
            "schema": pin["schema"],
            "ordered_work_unit_sha256": pin["ordered_work_unit_sha256"],
            "producer_id": pin.get("producer_id"),
            "producer_generation": pin.get("producer_generation"),
            "profile_identity": pin.get("profile_identity"),
            "bindings": pin.get("bindings"),
        },
        "rows": rows,
    }
    out["semantic_input_sha256"] = canonical_sha256({"pin": out["pin"], "rows": rows})
    return out
