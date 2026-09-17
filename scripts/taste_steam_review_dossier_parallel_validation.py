#!/usr/bin/env python3
"""Durable GitHub-owned validation status for buffered Taste dossier candidates.

This module is observational only. It never advances canonical progress, mutates
candidate artifacts, creates retry state, or repairs semantic output. Canonical
persistence remains owned by the existing contiguous buffer drain.
"""
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
from taste_steam_review_dossier_daily import (
    expected_group_sequence,
    load_contract,
    validate_group_plan,
    validate_manifest,
)

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
    if doc.get("validation_status", {}).get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-PARALLEL-VALIDATION-STATUS-V1":
        raise ValueError("parallel dossier validation status schema is unsupported")
    return doc


def _candidate_record(*, manifest, descriptor, paths, contract, expected_sequence):
    sequence = int(descriptor["sequence"])
    record = {
        "snapshot_id": manifest["snapshot_id"],
        "sequence": sequence,
        "group_sha256": descriptor["group_sha256"],
        "web_evidence_contract_binding": manifest["web_evidence_contract_binding"],
        "validation": "invalid",
        "canonical_position": (
            "expected"
            if expected_sequence == sequence
            else "later_buffered"
            if expected_sequence is not None and sequence > expected_sequence
            else "replay_or_completed"
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
    """Strict-validate every present current-snapshot candidate independently.

    Later valid candidates are observable as valid even when an earlier expected
    group is invalid. This function never promotes them; canonical contiguous
    acceptance remains a separate GitHub-owned operation.
    """
    validate_manifest(manifest, contract)
    group_plan = validate_group_plan(manifest, contract, required=True)
    if int(contract["checkpointing"]["checkpoint_size"]) != 3:
        raise ValueError("parallel validation requires canonical checkpoint size 3")

    expected = expected_group_sequence(manifest, contract)
    candidates, malformed = _current_snapshot_candidates(buffer_dir, manifest["snapshot_id"])
    groups = {int(group["sequence"]): group for group in group_plan["groups"]}
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
                "validation": "invalid",
                "canonical_position": "outside_plan",
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
            expected_sequence=expected,
        ))

    invalid_expected = next(
        (
            {
                "sequence": record["sequence"],
                "group_sha256": record["group_sha256"],
                "artifact_sha256": record["artifact_sha256"],
                "validator_error": record["validator_error"],
            }
            for record in records
            if expected is not None and record["sequence"] == expected and record["validation"] == "invalid"
        ),
        None,
    )
    return {
        "schema": "TASTE-STEAM-REVIEW-DOSSIER-PARALLEL-VALIDATION-STATUS-V1",
        "schema_version": 1,
        "snapshot_id": manifest["snapshot_id"],
        "prepared_required_sha256": manifest["prepared_required_sha256"],
        "group_plan_sha256": group_plan["group_plan_sha256"],
        "web_evidence_contract_binding": manifest["web_evidence_contract_binding"],
        "canonical_expected_sequence": expected,
        "completed_required_count": manifest["completed_required_count"],
        "remaining_required_count": manifest["remaining_required_count"],
        "full_backlog_complete": manifest["full_backlog_complete"],
        "candidate_count": len(records),
        "valid_candidate_count": sum(1 for record in records if record["validation"] == "valid"),
        "invalid_candidate_count": sum(1 for record in records if record["validation"] == "invalid"),
        "invalid_expected_group": invalid_expected,
        "candidate_groups": records,
        "malformed_current_snapshot_artifacts": [path.as_posix() for path in malformed],
        "canonical_progress_authority": False,
        "retry_state": False,
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
    parser = argparse.ArgumentParser(description="Write durable GitHub-owned validation status for buffered Taste dossier candidates")
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
        "canonical_expected_sequence": status["canonical_expected_sequence"],
        "valid_candidate_count": status["valid_candidate_count"],
        "invalid_candidate_count": status["invalid_candidate_count"],
        "invalid_expected_group": status["invalid_expected_group"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
