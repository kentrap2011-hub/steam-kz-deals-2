#!/usr/bin/env python3
"""Durable GitHub-owned validation/recovery observability for dossier candidates."""
import argparse
import hashlib
import json
from pathlib import Path

from taste_steam_review_dossier import atomic_write_json
from taste_steam_review_dossier_buffered import (
    _current_snapshot_candidates,
    expected_buffer_path,
    validate_buffer_artifact,
)
from taste_steam_review_dossier_daily import load_contract, validate_group_plan, validate_manifest
from taste_steam_review_dossier_group_progress import ensure_group_progress, next_pending_sequence

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARALLEL_CONTRACT = ROOT / "config/taste_steam_review_dossier_parallel_validation_contract.json"


def load_parallel_validation_contract(path=DEFAULT_PARALLEL_CONTRACT):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if (
        doc.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-PARALLEL-VALIDATION-CONTRACT-V1"
        or type(doc.get("version")) is not int
        or doc.get("version") != 1
        or doc.get("status") != "active"
        or doc.get("owner") != "github_control_plane"
    ):
        raise ValueError("parallel dossier validation contract is missing, stale or unsupported")
    if doc.get("candidate_publication", {}).get("required_group_size") != 3:
        raise ValueError("parallel dossier validation contract must preserve group size 3")
    if doc.get("validation_status", {}).get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-PARALLEL-VALIDATION-STATUS-V2":
        raise ValueError("parallel dossier validation status schema is unsupported")
    return doc


def _candidate_record(*, manifest, descriptor, paths, contract, canonical_state, next_pending):
    sequence = int(descriptor["sequence"])
    record = {
        "snapshot_id": manifest["snapshot_id"],
        "sequence": sequence,
        "group_sha256": descriptor["group_sha256"],
        "web_evidence_contract_binding": manifest["web_evidence_contract_binding"],
        "canonical_group_state": canonical_state,
        "validation": "invalid",
        "normal_first_pass_position": (
            "next_pending" if next_pending == sequence
            else "pending_later" if canonical_state == "pending"
            else canonical_state
        ),
        "artifact_paths": [path.as_posix() for path in paths],
        "artifact_sha256": None,
        "validator_error": None,
    }
    if len(paths) != 1:
        record["validator_error"] = "duplicate_or_alternate_buffer_artifact"
        return record
    path = paths[0]
    deterministic = expected_buffer_path(descriptor, contract)
    if path.as_posix() != deterministic.as_posix():
        record["validator_error"] = "non_deterministic_buffer_path"
        return record
    try:
        raw = path.read_bytes()
        record["artifact_sha256"] = hashlib.sha256(raw).hexdigest()
        artifact = json.loads(raw.decode("utf-8"))
        validate_buffer_artifact(artifact, descriptor, manifest, contract)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError, OSError, KeyError, TypeError) as exc:
        record["validator_error"] = str(exc)
        return record
    record["validation"] = "valid"
    return record


def build_parallel_validation_status(manifest, contract, buffer_dir):
    """Observe present candidates plus canonical per-group progress/recovery projection."""
    manifest = ensure_group_progress(manifest, contract)
    validate_manifest(manifest, contract)
    group_plan = validate_group_plan(manifest, contract, required=True)
    if int(contract["checkpointing"]["checkpoint_size"]) != 3:
        raise ValueError("parallel validation requires canonical checkpoint size 3")

    next_pending = next_pending_sequence(manifest, contract)
    candidates, malformed = _current_snapshot_candidates(buffer_dir, manifest["snapshot_id"])
    groups = {int(group["sequence"]): group for group in group_plan["groups"]}
    state_by_sequence = {
        int(entry["sequence"]): entry for entry in manifest["group_progress"]["groups"]
    }
    records = []
    for sequence in sorted(candidates):
        descriptor = groups.get(sequence)
        paths = candidates[sequence]
        if descriptor is None:
            records.append({
                "snapshot_id": manifest["snapshot_id"],
                "sequence": sequence,
                "group_sha256": None,
                "web_evidence_contract_binding": manifest["web_evidence_contract_binding"],
                "canonical_group_state": "outside_plan",
                "validation": "invalid",
                "normal_first_pass_position": "outside_plan",
                "artifact_paths": [path.as_posix() for path in paths],
                "artifact_sha256": None,
                "validator_error": "buffer_artifact_sequence_outside_current_group_plan",
            })
            continue
        records.append(_candidate_record(
            manifest=manifest,
            descriptor=descriptor,
            paths=paths,
            contract=contract,
            canonical_state=state_by_sequence[sequence]["state"],
            next_pending=next_pending,
        ))

    failed_groups = [
        {
            "sequence": entry["sequence"],
            "group_sha256": entry["group_sha256"],
            "failure": entry["failure"],
        }
        for entry in manifest["group_progress"]["groups"]
        if entry["state"] == "failed_or_invalid_pending_recovery"
    ]
    progress = manifest["group_progress"]
    return {
        "schema": "TASTE-STEAM-REVIEW-DOSSIER-PARALLEL-VALIDATION-STATUS-V2",
        "schema_version": 2,
        "snapshot_id": manifest["snapshot_id"],
        "prepared_required_sha256": manifest["prepared_required_sha256"],
        "group_plan_sha256": group_plan["group_plan_sha256"],
        "web_evidence_contract_binding": manifest["web_evidence_contract_binding"],
        "next_pending_sequence": next_pending,
        "accepted_group_count": progress["accepted_group_count"],
        "failed_group_count": progress["failed_group_count"],
        "pending_group_count": progress["pending_group_count"],
        "normal_first_pass_complete": progress["normal_first_pass_complete"],
        "all_groups_accepted": progress["all_groups_accepted"],
        "full_backlog_complete": manifest["full_backlog_complete"],
        "candidate_count": len(records),
        "valid_candidate_count": sum(1 for record in records if record["validation"] == "valid"),
        "invalid_candidate_count": sum(1 for record in records if record["validation"] == "invalid"),
        "failed_groups_pending_recovery": failed_groups,
        "candidate_groups": records,
        "malformed_current_snapshot_artifacts": [path.as_posix() for path in malformed],
        "canonical_progress_authority": False,
        "recovery_projection_authority": False,
    }


def write_parallel_validation_status(
    *,
    manifest_path="data/production/pre_ai/taste_steam_review_dossier_work.json",
    dossier_contract_path="config/taste_steam_review_dossier_contract.json",
    parallel_contract_path=DEFAULT_PARALLEL_CONTRACT,
    buffer_dir=None,
    output_path=None,
):
    parallel = load_parallel_validation_contract(parallel_contract_path)
    contract = load_contract(dossier_contract_path)
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    root = Path(buffer_dir or contract["paths"]["submission_inbox_dir"])
    status = build_parallel_validation_status(manifest, contract, root)
    target = Path(output_path or parallel["validation_status"]["path"])
    atomic_write_json(target, status)
    return target, status


def main():
    parser = argparse.ArgumentParser(description="Write GitHub-owned dossier validation/recovery observability")
    parser.add_argument("--manifest", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--dossier-contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--parallel-contract", default=str(DEFAULT_PARALLEL_CONTRACT))
    parser.add_argument("--buffer-dir", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    target, status = write_parallel_validation_status(
        manifest_path=args.manifest,
        dossier_contract_path=args.dossier_contract,
        parallel_contract_path=args.parallel_contract,
        buffer_dir=args.buffer_dir,
        output_path=args.output,
    )
    print(json.dumps({
        "status": "written",
        "path": target.as_posix(),
        "snapshot_id": status["snapshot_id"],
        "next_pending_sequence": status["next_pending_sequence"],
        "accepted_group_count": status["accepted_group_count"],
        "failed_group_count": status["failed_group_count"],
        "pending_group_count": status["pending_group_count"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
