#!/usr/bin/env python3
"""GitHub-owned buffered transport helpers for Steam review dossiers.

Buffer files are transport only. Canonical progress is derived exclusively from the
current work manifest and is advanced only after a maximal valid contiguous prefix
has been validated from repository state.
"""
import copy
import json
import re
from pathlib import Path

from taste_steam_review_dossier import atomic_write_json, canonical_sha256, dossier_path
from taste_steam_review_dossier_daily import (
    BUFFER_GROUP_SCHEMA,
    expected_group_sequence,
    progress_fields,
    validate_group_plan,
    validate_manifest,
)
from taste_steam_review_dossier_strict import validate_dossiers_against_expected_items


_BUFFER_NAME_RE = re.compile(r"^(?P<snapshot>[0-9a-f]{64})--g(?P<sequence>[0-9]{6})--(?P<group>[0-9a-f]{64})\.json$")


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
    return validate_dossiers_against_expected_items(
        docs,
        descriptor["items"],
        contract,
        expected_ttl_days=manifest["ttl_days"],
    )


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
    """Return files claiming the current canonical expected sequence."""
    validate_manifest(manifest, contract)
    validate_group_plan(manifest, contract, required=True)
    sequence = expected_group_sequence(manifest, contract)
    if sequence is None:
        return []
    root = Path(buffer_dir or contract["paths"]["submission_inbox_dir"])
    candidates, malformed = _current_snapshot_candidates(root, manifest["snapshot_id"])
    if malformed:
        return malformed
    return list(candidates.get(sequence, []))


def plan_buffered_drain(manifest, contract, buffer_dir):
    """Plan a maximal valid contiguous prefix without mutating canonical files."""
    validate_manifest(manifest, contract)
    group_plan = validate_group_plan(manifest, contract, required=True)
    expected = expected_group_sequence(manifest, contract)
    if expected is None:
        return {
            "accepted": [],
            "accepted_count": 0,
            "accepted_dossier_count": 0,
            "blocked_reason": None,
            "stop_sequence": None,
            "next_manifest": copy.deepcopy(manifest),
        }

    candidates, malformed_names = _current_snapshot_candidates(buffer_dir, manifest["snapshot_id"])
    if malformed_names:
        return {
            "accepted": [],
            "accepted_count": 0,
            "accepted_dossier_count": 0,
            "blocked_reason": "malformed_current_snapshot_buffer_filename",
            "stop_sequence": expected,
            "next_manifest": copy.deepcopy(manifest),
        }

    groups = {int(group["sequence"]): group for group in group_plan["groups"]}
    accepted = []
    sequence = expected
    blocked_reason = None
    stop_sequence = None

    while sequence in groups:
        descriptor = groups[sequence]
        paths = candidates.get(sequence, [])
        if not paths:
            blocked_reason = "gap"
            stop_sequence = sequence
            break
        if len(paths) != 1:
            blocked_reason = "duplicate_or_alternate_buffer_artifact"
            stop_sequence = sequence
            break
        path = paths[0]
        expected_path = expected_buffer_path(descriptor, contract)
        if path.as_posix() != expected_path.as_posix():
            blocked_reason = "non_deterministic_buffer_path"
            stop_sequence = sequence
            break
        try:
            artifact = json.loads(path.read_text(encoding="utf-8"))
            docs = validate_buffer_artifact(artifact, descriptor, manifest, contract)
        except (ValueError, json.JSONDecodeError, OSError, KeyError, TypeError):
            blocked_reason = "invalid_expected_group"
            stop_sequence = sequence
            break
        accepted.append({"path": path, "descriptor": descriptor, "dossiers": docs})
        sequence += 1

    dossier_count = sum(len(entry["dossiers"]) for entry in accepted)
    next_manifest = copy.deepcopy(manifest)
    if accepted:
        remaining = list(manifest["remaining_required_items"])
        accepted_items = []
        for entry in accepted:
            accepted_items.extend(entry["descriptor"]["items"])
        if remaining[:len(accepted_items)] != accepted_items:
            raise ValueError("buffered accepted prefix is not the canonical remaining prefix")
        next_remaining = remaining[len(accepted_items):]
        next_manifest.update(progress_fields(
            manifest["snapshot_id"],
            manifest["prepared_required_items"],
            next_remaining,
            int(contract["checkpointing"]["checkpoint_size"]),
        ))
        validate_manifest(next_manifest, contract)

    return {
        "accepted": accepted,
        "accepted_count": len(accepted),
        "accepted_dossier_count": dossier_count,
        "blocked_reason": blocked_reason,
        "stop_sequence": stop_sequence,
        "next_manifest": next_manifest,
    }


def apply_buffered_drain(plan, *, manifest_path, store_dir):
    """Apply a previously validated drain plan locally for one atomic Git commit."""
    accepted = plan["accepted"]
    if not accepted:
        return []
    persisted = []
    for entry in accepted:
        for doc in entry["dossiers"]:
            path = dossier_path(store_dir, str(doc["appid"]))
            atomic_write_json(path, doc)
            persisted.append({
                "appid": str(doc["appid"]),
                "path": path.as_posix(),
                "dossier_sha256": canonical_sha256(doc),
            })
    atomic_write_json(manifest_path, plan["next_manifest"])
    for entry in accepted:
        entry["path"].unlink()
    return persisted


def drain_buffered_groups(
    *,
    manifest_path="data/production/pre_ai/taste_steam_review_dossier_work.json",
    contract=None,
    buffer_dir="data/ai_inbox/taste_steam_review_dossiers",
    store_dir="data/cache/taste_steam_review_dossiers",
):
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    plan = plan_buffered_drain(manifest, contract, buffer_dir)
    persisted = apply_buffered_drain(plan, manifest_path=manifest_path, store_dir=store_dir)
    return {
        "accepted_group_count": plan["accepted_count"],
        "accepted_dossier_count": plan["accepted_dossier_count"],
        "accepted_sequences": [entry["descriptor"]["sequence"] for entry in plan["accepted"]],
        "blocked_reason": plan["blocked_reason"],
        "stop_sequence": plan["stop_sequence"],
        "persisted": persisted,
        "snapshot_id": plan["next_manifest"]["snapshot_id"],
        "remaining_required_count": plan["next_manifest"]["remaining_required_count"],
        "full_backlog_complete": plan["next_manifest"]["full_backlog_complete"],
    }
