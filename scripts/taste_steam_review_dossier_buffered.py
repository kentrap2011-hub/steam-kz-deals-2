#!/usr/bin/env python3
"""GitHub-owned non-blocking buffered transport for Steam review dossiers."""
import copy
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier import atomic_write_json, canonical_sha256, dossier_path
from taste_steam_review_dossier_compact_provenance import (
    load_compact_provenance_policy,
    validate_compact_provenance,
)
from taste_steam_review_dossier_daily import (
    BUFFER_GROUP_SCHEMA,
    progress_fields,
    validate_group_plan,
    validate_manifest,
)
from taste_steam_review_dossier_group_progress import (
    ACCEPTED,
    FAILED,
    accepted_contiguous_prefix_item_count,
    ensure_group_progress,
    next_pending_sequence,
    pending_sequences,
    set_group_state,
)
from taste_steam_review_dossier_strict import validate_dossiers_against_expected_items


_BUFFER_NAME_RE = re.compile(r"^(?P<snapshot>[0-9a-f]{64})--g(?P<sequence>[0-9]{6})--(?P<group>[0-9a-f]{64})\.json$")
_DEFAULT_FAILED_QUARANTINE = Path("data/quarantine/taste_steam_review_dossier_inbox/failed_group")
_DEFAULT_FAILURE_AUDIT = Path("data/audit/taste_steam_review_dossier_group_failures.jsonl")


def expected_buffer_path(descriptor, contract):
    inbox = Path(contract["paths"]["submission_inbox_dir"])
    return inbox / (
        f"{descriptor['snapshot_id']}--g{int(descriptor['sequence']):06d}--"
        f"{descriptor['group_sha256']}.json"
    )


def _descriptor_fields():
    return (
        "snapshot_id",
        "prepared_required_sha256",
        "sequence",
        "start_index",
        "end_index_exclusive",
        "items",
        "appids",
        "items_sha256",
        "group_sha256",
        "scope_source",
        "source_queue_sha256",
    )


def validate_buffer_artifact(artifact, descriptor, manifest, contract):
    """Validate one buffered group exactly against its immutable descriptor."""
    if not isinstance(artifact, dict):
        raise ValueError("buffered dossier group must be an object")
    if artifact.get("schema") != BUFFER_GROUP_SCHEMA or artifact.get("schema_version") != 1:
        raise ValueError("unsupported buffered dossier group schema")
    for field in _descriptor_fields():
        if artifact.get(field) != descriptor.get(field):
            raise ValueError(f"buffered dossier group identity mismatch: {field}")
    if artifact.get("items_sha256") != canonical_sha256(artifact.get("items")):
        raise ValueError("buffered dossier group items_sha256 mismatch")
    docs = artifact.get("dossiers")
    if not isinstance(docs, list):
        raise ValueError("buffered dossier group must contain dossiers list")
    actual_appids = [str(doc.get("appid") or "") if isinstance(doc, dict) else "" for doc in docs]
    if actual_appids != descriptor["appids"] or len(actual_appids) != len(set(actual_appids)):
        raise ValueError("buffered dossier group dossiers must exactly cover planned appids in order")
    docs = validate_dossiers_against_expected_items(
        docs,
        descriptor["items"],
        contract,
        expected_ttl_days=manifest["ttl_days"],
    )
    compact_policy = load_compact_provenance_policy()
    for doc in docs:
        validate_compact_provenance(doc, compact_policy)
    return docs


def _current_snapshot_candidates(buffer_dir, snapshot_id):
    """Return current-snapshot group files keyed by sequence; old snapshots are inert."""
    root = Path(buffer_dir)
    candidates = {}
    malformed = []
    if not root.exists():
        return candidates, malformed
    prefix = f"{snapshot_id}--g"
    for path in sorted(root.glob("*.json")):
        name = path.name
        if not name.startswith(prefix):
            continue
        match = _BUFFER_NAME_RE.fullmatch(name)
        if not match or match.group("snapshot") != snapshot_id:
            partial = re.match(rf"^{re.escape(snapshot_id)}--g([0-9]{{6}})--", name)
            if partial:
                candidates.setdefault(int(partial.group(1)), []).append(path)
            else:
                malformed.append(path)
            continue
        candidates.setdefault(int(match.group("sequence")), []).append(path)
    return candidates, malformed


def current_expected_buffer_paths(manifest, contract, buffer_dir=None):
    """Compatibility helper: files claiming the current next-pending group."""
    manifest = ensure_group_progress(manifest, contract)
    validate_manifest(manifest, contract)
    validate_group_plan(manifest, contract, required=True)
    sequence = next_pending_sequence(manifest, contract)
    if sequence is None:
        return []
    root = Path(buffer_dir or contract["paths"]["submission_inbox_dir"])
    candidates, malformed = _current_snapshot_candidates(root, manifest["snapshot_id"])
    if malformed:
        return malformed
    return list(candidates.get(sequence, []))


def _quarantine_target(path, manifest, sequence, artifact_sha, root):
    return Path(root) / manifest["snapshot_id"] / f"g{sequence:06d}" / f"{path.name}.invalid-{artifact_sha[:12]}"


def _failure_entry(*, manifest, descriptor, paths, validator_error, quarantine_root):
    expected = expected_buffer_path(descriptor, {"paths": {"submission_inbox_dir": str(Path(paths[0]).parent) if paths else ""}})
    primary = paths[0] if paths else expected
    if len(paths) == 1 and paths[0].exists():
        artifact_sha = hashlib.sha256(paths[0].read_bytes()).hexdigest()
    else:
        artifact_sha = canonical_sha256([p.as_posix() for p in paths] or [expected.as_posix()])
    targets = [
        _quarantine_target(p, manifest, int(descriptor["sequence"]), hashlib.sha256(p.read_bytes()).hexdigest(), quarantine_root)
        for p in paths if p.exists()
    ]
    primary_target = targets[0] if targets else Path(quarantine_root) / manifest["snapshot_id"] / f"g{int(descriptor['sequence']):06d}" / "missing-invalid-artifact"
    failure = {
        "validator_error": validator_error,
        "artifact_path": primary.as_posix(),
        "artifact_sha256": artifact_sha,
        "quarantine_artifact_path": primary_target.as_posix(),
        "recovery_eligible": True,
    }
    return {
        "descriptor": descriptor,
        "paths": list(paths),
        "quarantine_targets": targets,
        "failure": failure,
    }


def plan_buffered_drain(
    manifest,
    contract,
    buffer_dir,
    *,
    failed_quarantine_root=_DEFAULT_FAILED_QUARANTINE,
):
    """Validate/classify every present pending group independently."""
    manifest = ensure_group_progress(manifest, contract)
    validate_manifest(manifest, contract)
    group_plan = validate_group_plan(manifest, contract, required=True)
    candidates, malformed_names = _current_snapshot_candidates(buffer_dir, manifest["snapshot_id"])
    groups = {int(group["sequence"]): group for group in group_plan["groups"]}
    accepted = []
    failed = []
    next_manifest = copy.deepcopy(manifest)

    for sequence in pending_sequences(manifest, contract):
        descriptor = groups[sequence]
        paths = candidates.get(sequence, [])
        if not paths:
            continue
        deterministic = expected_buffer_path(descriptor, contract)
        if len(paths) != 1:
            entry = _failure_entry(
                manifest=manifest,
                descriptor=descriptor,
                paths=paths,
                validator_error="duplicate_or_alternate_buffer_artifact",
                quarantine_root=failed_quarantine_root,
            )
            failed.append(entry)
            next_manifest = set_group_state(next_manifest, contract, sequence, FAILED, failure=entry["failure"])
            continue
        path = paths[0]
        if path.as_posix() != deterministic.as_posix():
            entry = _failure_entry(
                manifest=manifest,
                descriptor=descriptor,
                paths=paths,
                validator_error="non_deterministic_buffer_path",
                quarantine_root=failed_quarantine_root,
            )
            failed.append(entry)
            next_manifest = set_group_state(next_manifest, contract, sequence, FAILED, failure=entry["failure"])
            continue
        try:
            artifact = json.loads(path.read_text(encoding="utf-8"))
            docs = validate_buffer_artifact(artifact, descriptor, manifest, contract)
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError, KeyError, TypeError) as exc:
            entry = _failure_entry(
                manifest=manifest,
                descriptor=descriptor,
                paths=paths,
                validator_error=str(exc),
                quarantine_root=failed_quarantine_root,
            )
            failed.append(entry)
            next_manifest = set_group_state(next_manifest, contract, sequence, FAILED, failure=entry["failure"])
            continue
        accepted.append({"path": path, "descriptor": descriptor, "dossiers": docs})
        next_manifest = set_group_state(next_manifest, contract, sequence, ACCEPTED)

    prefix_count = accepted_contiguous_prefix_item_count(next_manifest, contract)
    next_remaining = list(next_manifest["prepared_required_items"])[prefix_count:]
    next_manifest.update(progress_fields(
        next_manifest["snapshot_id"],
        next_manifest["prepared_required_items"],
        next_remaining,
        int(contract["checkpointing"]["checkpoint_size"]),
    ))
    validate_manifest(next_manifest, contract)

    return {
        "accepted": accepted,
        "failed": failed,
        "accepted_count": len(accepted),
        "accepted_dossier_count": sum(len(entry["dossiers"]) for entry in accepted),
        "failed_count": len(failed),
        "malformed_current_snapshot_artifacts": [path.as_posix() for path in malformed_names],
        "next_manifest": next_manifest,
    }


def _append_failure_audit(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def apply_buffered_drain(
    plan,
    *,
    manifest_path,
    store_dir,
    failure_audit_path=_DEFAULT_FAILURE_AUDIT,
):
    """Apply independent group classifications locally for one atomic Git commit."""
    persisted = []
    for entry in plan["accepted"]:
        for doc in entry["dossiers"]:
            path = dossier_path(store_dir, str(doc["appid"]))
            atomic_write_json(path, doc)
            persisted.append({
                "appid": str(doc["appid"]),
                "path": path.as_posix(),
                "dossier_sha256": canonical_sha256(doc),
            })

    for entry in plan["failed"]:
        for source, target in zip(entry["paths"], entry["quarantine_targets"]):
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                raise ValueError(f"failed-group quarantine target already exists: {target.as_posix()}")
            shutil.move(source.as_posix(), target.as_posix())
        _append_failure_audit(failure_audit_path, {
            "schema": "TASTE-STEAM-REVIEW-DOSSIER-GROUP-FAILURE-AUDIT-V1",
            "recorded_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "snapshot_id": plan["next_manifest"]["snapshot_id"],
            "sequence": entry["descriptor"]["sequence"],
            "group_sha256": entry["descriptor"]["group_sha256"],
            **entry["failure"],
            "normal_forward_progress_blocked": False,
        })

    atomic_write_json(manifest_path, plan["next_manifest"])
    for entry in plan["accepted"]:
        entry["path"].unlink()
    return persisted


def drain_buffered_groups(
    *,
    manifest_path="data/production/pre_ai/taste_steam_review_dossier_work.json",
    contract=None,
    buffer_dir="data/ai_inbox/taste_steam_review_dossiers",
    store_dir="data/cache/taste_steam_review_dossiers",
    failed_quarantine_root=_DEFAULT_FAILED_QUARANTINE,
    failure_audit_path=_DEFAULT_FAILURE_AUDIT,
):
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    plan = plan_buffered_drain(
        manifest,
        contract,
        buffer_dir,
        failed_quarantine_root=failed_quarantine_root,
    )
    persisted = apply_buffered_drain(
        plan,
        manifest_path=manifest_path,
        store_dir=store_dir,
        failure_audit_path=failure_audit_path,
    )
    progress = plan["next_manifest"]["group_progress"]
    return {
        "accepted_group_count_this_run": plan["accepted_count"],
        "accepted_dossier_count_this_run": plan["accepted_dossier_count"],
        "failed_group_count_this_run": plan["failed_count"],
        "accepted_sequences": [entry["descriptor"]["sequence"] for entry in plan["accepted"]],
        "failed_sequences": [entry["descriptor"]["sequence"] for entry in plan["failed"]],
        "malformed_current_snapshot_artifacts": plan["malformed_current_snapshot_artifacts"],
        "persisted": persisted,
        "snapshot_id": plan["next_manifest"]["snapshot_id"],
        "next_pending_sequence": next_pending_sequence(plan["next_manifest"], contract),
        "accepted_group_count": progress["accepted_group_count"],
        "failed_group_count": progress["failed_group_count"],
        "pending_group_count": progress["pending_group_count"],
        "accepted_dossier_count": progress["accepted_dossier_count"],
        "failed_dossier_count": progress["failed_dossier_count"],
        "pending_dossier_count": progress["pending_dossier_count"],
        "normal_first_pass_complete": progress["normal_first_pass_complete"],
        "all_groups_accepted": progress["all_groups_accepted"],
        "legacy_contiguous_remaining_required_count": plan["next_manifest"]["remaining_required_count"],
        "full_backlog_complete": plan["next_manifest"]["full_backlog_complete"],
    }
