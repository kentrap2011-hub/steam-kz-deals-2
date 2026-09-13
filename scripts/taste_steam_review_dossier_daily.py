#!/usr/bin/env python3
"""Deterministic V2 control plane for the fixed daily Steam-review-dossier snapshot."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from taste_steam_review_dossier import (
    SUBMISSION_SCHEMA,
    atomic_write_json,
    canonical_sha256,
    dossier_path,
    dossier_state,
    load_dossier_if_present,
    resolve_ttl_days,
    validate_dossier,
)

CONTRACT_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-CONTRACT-V2"
WORK_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-WORK-V2"
_SAMARA = ZoneInfo("Europe/Samara")
_HEX64 = set("0123456789abcdef")


def _hex64(value):
    return isinstance(value, str) and len(value) == 64 and all(c in _HEX64 for c in value)


def utc_iso(dt):
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def load_contract(path):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if doc.get("schema") != CONTRACT_SCHEMA or doc.get("version") != 2 or doc.get("status") != "active":
        raise ValueError("Steam review dossier daily snapshot contract is missing, stale or unsupported")
    scope = doc.get("scope") or {}
    markers = scope.get("taste_semantic_work_required_any")
    if scope.get("source") != "daily_fixed_snapshot_of_full_current_canonical_taste_queue":
        raise ValueError("Daily dossier scope source is missing or invalid")
    if not isinstance(markers, list) or not markers or any(not isinstance(x, str) or not x for x in markers):
        raise ValueError("Daily dossier Taste eligibility markers are missing or invalid")
    checkpoint = doc.get("checkpointing") or {}
    if checkpoint.get("owner") != "github_control_plane" or checkpoint.get("semantics") != "internal_durability_boundary_not_scope_quota":
        raise ValueError("Daily dossier checkpoint ownership/semantics are invalid")
    if checkpoint.get("advance_rule") != "after_successful_checkpoint_persistence_advance_progress_inside_same_snapshot_without_queue_or_store_scope_rebuild":
        raise ValueError("Daily dossier same-snapshot advance rule is invalid")
    if not isinstance(checkpoint.get("checkpoint_size"), int) or checkpoint["checkpoint_size"] <= 0:
        raise ValueError("Daily dossier checkpoint size is invalid")
    freshness = doc.get("freshness") or {}
    if freshness.get("default_ttl_days") != 20:
        raise ValueError("Daily dossier default TTL must remain 20 days")
    return doc


def _row_requires_dossier(work_required, contract):
    if not isinstance(work_required, list):
        raise ValueError("work_required must be a list")
    markers = set(contract["scope"]["taste_semantic_work_required_any"])
    return any(item in markers for item in work_required)


def canonical_dossier_scope_rows(queue_rows, contract):
    """Project the full current eligible Taste queue to one deterministic row per appid."""
    if not isinstance(queue_rows, list):
        raise ValueError("canonical Taste queue rows must be a list")
    rows = []
    seen = set()
    for index, row in enumerate(queue_rows):
        if not isinstance(row, dict):
            raise ValueError(f"canonical Taste queue row {index} is malformed")
        appid = str(row.get("appid") or "")
        key = row.get("taste_subject_key") if "taste_subject_key" in row else row.get("key")
        work = row.get("work_required")
        if not appid.isdigit() or not isinstance(key, str) or not key:
            raise ValueError(f"canonical Taste queue row {index} lacks appid/taste subject identity")
        try:
            eligible = _row_requires_dossier(work, contract)
        except ValueError as exc:
            raise ValueError(f"canonical Taste queue row {index} has no canonical work_required") from exc
        if not eligible or appid in seen:
            continue
        seen.add(appid)
        rows.append({
            "key": key,
            "appid": appid,
            "title": str(row.get("title") or ""),
            "taste_fingerprint": row.get("taste_fingerprint"),
            "candidate_context_sha256": row.get("candidate_context_sha256"),
            "work_required": list(work),
        })
    return rows


def _checkpoint_binding(snapshot_id, remaining_items, checkpoint_items):
    return canonical_sha256({
        "snapshot_id": snapshot_id,
        "remaining_required_sha256": canonical_sha256(remaining_items),
        "current_checkpoint_items": checkpoint_items,
    })


def _progress_fields(snapshot_id, prepared_items, remaining_items, checkpoint_size):
    current = remaining_items[:checkpoint_size]
    remaining_count = len(remaining_items)
    return {
        "remaining_required_items": remaining_items,
        "remaining_required_count": remaining_count,
        "remaining_required_sha256": canonical_sha256(remaining_items),
        "completed_required_count": len(prepared_items) - remaining_count,
        "current_checkpoint_items": current,
        "current_checkpoint_count": len(current),
        "current_checkpoint_sha256": canonical_sha256(current),
        "scope_sha256": _checkpoint_binding(snapshot_id, remaining_items, current),
        "full_backlog_complete": remaining_count == 0,
        "status": "complete" if remaining_count == 0 else "work_required",
    }


def build_daily_work_manifest(queue_rows, contract, store_dir, *, now=None, ttl_days=None, source_queue_path=None):
    """Prepare one complete fixed daily backlog snapshot from one queue read."""
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    ttl = resolve_ttl_days(contract, ttl_days)
    checkpoint_size = int(contract["checkpointing"]["checkpoint_size"])
    source_queue_sha = canonical_sha256(queue_rows)
    scope_rows = canonical_dossier_scope_rows(queue_rows, contract)
    eligible_row_count = sum(
        1 for row in queue_rows
        if isinstance(row, dict) and _row_requires_dossier(row.get("work_required"), contract)
    )
    items = []
    required = []
    for row in scope_rows:
        appid = row["appid"]
        existing = load_dossier_if_present(store_dir, appid)
        try:
            state = dossier_state(existing, contract, now=now, expected_appid=appid)
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

    prepared_date = now.astimezone(_SAMARA).date().isoformat()
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
    }
    manifest.update(_progress_fields(snapshot_id, required, list(required), checkpoint_size))
    return manifest


def validate_manifest(manifest, contract):
    if not isinstance(manifest, dict) or manifest.get("schema") != WORK_SCHEMA or manifest.get("schema_version") != 2:
        raise ValueError("GitHub-prepared daily dossier snapshot is missing or unsupported")
    if manifest.get("preparation_mode") != "daily_fixed_full_backlog":
        raise ValueError("Daily dossier snapshot preparation mode is invalid")
    if manifest.get("scope_source") != contract["scope"]["source"]:
        raise ValueError("Daily dossier snapshot scope source mismatch")
    if not _hex64(manifest.get("snapshot_id")) or not _hex64(manifest.get("source_queue_sha256")):
        raise ValueError("Daily dossier snapshot provenance binding is invalid")
    prepared = manifest.get("prepared_required_items")
    remaining = manifest.get("remaining_required_items")
    current = manifest.get("current_checkpoint_items")
    if not isinstance(prepared, list) or not isinstance(remaining, list) or not isinstance(current, list):
        raise ValueError("Daily dossier snapshot scope/progress lists are missing")
    if manifest.get("prepared_required_count") != len(prepared) or manifest.get("prepared_required_sha256") != canonical_sha256(prepared):
        raise ValueError("Daily dossier immutable prepared scope binding mismatch")
    checkpoint_size = int(contract["checkpointing"]["checkpoint_size"])
    expected_progress = _progress_fields(manifest["snapshot_id"], prepared, remaining, checkpoint_size)
    for key, value in expected_progress.items():
        if manifest.get(key) != value:
            raise ValueError(f"Daily dossier snapshot progress field mismatch: {key}")
    prepared_appids = [str(x.get("appid") or "") for x in prepared]
    remaining_appids = [str(x.get("appid") or "") for x in remaining]
    if len(prepared_appids) != len(set(prepared_appids)) or len(remaining_appids) != len(set(remaining_appids)):
        raise ValueError("Daily dossier snapshot contains duplicate appids")
    if any(appid not in prepared_appids for appid in remaining_appids):
        raise ValueError("Daily dossier remaining scope escaped immutable prepared scope")
    return current


def validate_submission(submission, manifest, contract):
    if not isinstance(submission, dict) or submission.get("schema") != SUBMISSION_SCHEMA or submission.get("schema_version") != 1:
        raise ValueError("unsupported dossier submission schema")
    current = validate_manifest(manifest, contract)
    if manifest["status"] != "work_required" or not current:
        raise ValueError("no dossier checkpoint work is currently prepared")
    for field in ("snapshot_id", "scope_sha256", "scope_source", "source_queue_sha256"):
        if submission.get(field) != manifest.get(field):
            raise ValueError(f"dossier submission {field} mismatch")
    docs = submission.get("dossiers")
    if not isinstance(docs, list):
        raise ValueError("dossier submission must contain a dossiers list")
    expected = [str(x["appid"]) for x in current]
    actual = [str(doc.get("appid") or "") if isinstance(doc, dict) else "" for doc in docs]
    if len(actual) != len(set(actual)) or actual != expected:
        raise ValueError("dossier submission must exactly cover the current internal checkpoint in canonical order")
    return [
        validate_dossier(doc, contract, expected_appid=appid, expected_ttl_days=manifest["ttl_days"])
        for doc, appid in zip(docs, expected)
    ]


def persist_submission_and_advance_snapshot(submission, manifest, contract, store_dir, *, manifest_output_path=None):
    """Persist one valid checkpoint, then advance only progress inside the same snapshot."""
    docs = validate_submission(submission, manifest, contract)
    current = list(manifest["current_checkpoint_items"])
    persisted = []
    for doc in docs:
        path = dossier_path(store_dir, str(doc["appid"]))
        atomic_write_json(path, doc)
        persisted.append({"appid": str(doc["appid"]), "path": path.as_posix(), "dossier_sha256": canonical_sha256(doc)})

    next_manifest = json.loads(json.dumps(manifest))
    remaining = list(manifest["remaining_required_items"])
    expected = [str(x["appid"]) for x in current]
    if [str(x["appid"]) for x in remaining[:len(current)]] != expected:
        raise ValueError("current checkpoint is not the canonical prefix of remaining daily snapshot scope")
    next_remaining = remaining[len(current):]
    next_manifest.update(_progress_fields(
        manifest["snapshot_id"],
        manifest["prepared_required_items"],
        next_remaining,
        int(contract["checkpointing"]["checkpoint_size"]),
    ))
    validate_manifest(next_manifest, contract)
    if manifest_output_path is not None:
        atomic_write_json(manifest_output_path, next_manifest)
    return persisted, next_manifest
