#!/usr/bin/env python3
"""GitHub-owned non-blocking per-group progress for Steam review dossiers."""
import copy

GROUP_PROGRESS_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-GROUP-PROGRESS-V1"
PENDING = "pending"
ACCEPTED = "accepted"
FAILED = "failed_or_invalid_pending_recovery"
_ALLOWED = {PENDING, ACCEPTED, FAILED}


def _plan(manifest):
    plan = manifest.get("submission_group_plan")
    if not isinstance(plan, dict) or not isinstance(plan.get("groups"), list):
        raise ValueError("dossier group progress requires immutable submission_group_plan")
    return plan


def _summarize(manifest, entries):
    plan = _plan(manifest)
    by_seq = {int(entry["sequence"]): entry for entry in entries}
    accepted_groups = failed_groups = pending_groups = 0
    accepted_dossiers = failed_dossiers = pending_dossiers = 0
    for group in plan["groups"]:
        seq = int(group["sequence"])
        state = by_seq[seq]["state"]
        count = len(group["items"])
        if state == ACCEPTED:
            accepted_groups += 1
            accepted_dossiers += count
        elif state == FAILED:
            failed_groups += 1
            failed_dossiers += count
        else:
            pending_groups += 1
            pending_dossiers += count
    return {
        "accepted_group_count": accepted_groups,
        "failed_group_count": failed_groups,
        "pending_group_count": pending_groups,
        "accepted_dossier_count": accepted_dossiers,
        "failed_dossier_count": failed_dossiers,
        "pending_dossier_count": pending_dossiers,
        "normal_first_pass_complete": pending_groups == 0,
        "all_groups_accepted": accepted_groups == len(plan["groups"]),
    }


def _base_progress(manifest, entries):
    plan = _plan(manifest)
    progress = {
        "schema": GROUP_PROGRESS_SCHEMA,
        "schema_version": 1,
        "snapshot_id": manifest["snapshot_id"],
        "prepared_required_sha256": manifest["prepared_required_sha256"],
        "group_plan_sha256": plan["group_plan_sha256"],
        "groups": entries,
    }
    progress.update(_summarize(manifest, entries))
    return progress


def infer_group_progress(manifest, contract):
    """Migrate legacy contiguous-prefix state without inventing acceptance."""
    plan = _plan(manifest)
    size = int(contract["checkpointing"]["checkpoint_size"])
    completed = int(manifest.get("completed_required_count") or 0)
    if completed < 0 or completed > len(manifest.get("prepared_required_items") or []):
        raise ValueError("legacy dossier progress is outside prepared scope")
    if completed != len(manifest.get("prepared_required_items") or []) and completed % size != 0:
        raise ValueError("legacy dossier progress does not end on a group boundary")
    accepted_prefix_groups = len(plan["groups"]) if manifest.get("full_backlog_complete") else completed // size
    entries = []
    for group in plan["groups"]:
        seq = int(group["sequence"])
        entries.append({
            "sequence": seq,
            "group_sha256": group["group_sha256"],
            "state": ACCEPTED if seq <= accepted_prefix_groups else PENDING,
        })
    return _base_progress(manifest, entries)


def validate_group_progress(manifest, contract, progress=None):
    progress = progress if progress is not None else manifest.get("group_progress")
    if not isinstance(progress, dict):
        raise ValueError("canonical dossier group_progress is missing")
    plan = _plan(manifest)
    if (
        progress.get("schema") != GROUP_PROGRESS_SCHEMA
        or progress.get("schema_version") != 1
        or progress.get("snapshot_id") != manifest.get("snapshot_id")
        or progress.get("prepared_required_sha256") != manifest.get("prepared_required_sha256")
        or progress.get("group_plan_sha256") != plan.get("group_plan_sha256")
    ):
        raise ValueError("canonical dossier group_progress binding is invalid")
    entries = progress.get("groups")
    if not isinstance(entries, list) or len(entries) != len(plan["groups"]):
        raise ValueError("canonical dossier group_progress group set is incomplete")
    for entry, group in zip(entries, plan["groups"]):
        if (
            not isinstance(entry, dict)
            or entry.get("sequence") != group.get("sequence")
            or entry.get("group_sha256") != group.get("group_sha256")
            or entry.get("state") not in _ALLOWED
        ):
            raise ValueError("canonical dossier group_progress entry binding/state is invalid")
        failure = entry.get("failure")
        if entry["state"] == FAILED:
            if not isinstance(failure, dict):
                raise ValueError("failed dossier group requires failure metadata")
            required = ("validator_error", "artifact_path", "artifact_sha256", "quarantine_artifact_path")
            if any(not isinstance(failure.get(key), str) or not failure[key] for key in required):
                raise ValueError("failed dossier group recovery metadata is incomplete")
            if failure.get("recovery_eligible") is not True:
                raise ValueError("failed dossier group must remain recovery eligible")
        elif failure is not None:
            raise ValueError("non-failed dossier group cannot carry failure metadata")
    expected_summary = _summarize(manifest, entries)
    for key, value in expected_summary.items():
        if progress.get(key) != value:
            raise ValueError(f"canonical dossier group_progress summary mismatch: {key}")
    return progress


def ensure_group_progress(manifest, contract):
    migrated = copy.deepcopy(manifest)
    if migrated.get("group_progress") is None:
        migrated["group_progress"] = infer_group_progress(migrated, contract)
    validate_group_progress(migrated, contract)
    return migrated


def next_pending_sequence(manifest, contract):
    progress = manifest.get("group_progress")
    if progress is None:
        progress = infer_group_progress(manifest, contract)
    else:
        validate_group_progress(manifest, contract, progress)
    for entry in progress["groups"]:
        if entry["state"] == PENDING:
            return int(entry["sequence"])
    return None


def pending_sequences(manifest, contract):
    progress = manifest.get("group_progress") or infer_group_progress(manifest, contract)
    validate_group_progress(manifest, contract, progress)
    return [int(entry["sequence"]) for entry in progress["groups"] if entry["state"] == PENDING]


def failed_sequences(manifest, contract):
    progress = manifest.get("group_progress") or infer_group_progress(manifest, contract)
    validate_group_progress(manifest, contract, progress)
    return [int(entry["sequence"]) for entry in progress["groups"] if entry["state"] == FAILED]


def set_group_state(manifest, contract, sequence, state, *, failure=None):
    if state not in (ACCEPTED, FAILED):
        raise ValueError("normal dossier drain may only classify pending groups accepted or failed")
    migrated = ensure_group_progress(manifest, contract)
    entries = copy.deepcopy(migrated["group_progress"]["groups"])
    found = False
    for entry in entries:
        if int(entry["sequence"]) != int(sequence):
            continue
        found = True
        if entry["state"] != PENDING:
            raise ValueError("normal dossier drain cannot reclassify an already attempted group")
        entry["state"] = state
        if state == FAILED:
            if not isinstance(failure, dict):
                raise ValueError("failed dossier group classification requires recovery metadata")
            entry["failure"] = copy.deepcopy(failure)
        break
    if not found:
        raise ValueError("dossier group sequence is outside immutable plan")
    migrated["group_progress"] = _base_progress(migrated, entries)
    validate_group_progress(migrated, contract)
    return migrated


def accepted_contiguous_prefix_item_count(manifest, contract):
    progress = manifest.get("group_progress") or infer_group_progress(manifest, contract)
    validate_group_progress(manifest, contract, progress)
    plan = _plan(manifest)
    count = 0
    for entry, group in zip(progress["groups"], plan["groups"]):
        if entry["state"] != ACCEPTED:
            break
        count += len(group["items"])
    return count
