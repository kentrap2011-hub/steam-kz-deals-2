#!/usr/bin/env python3
"""GitHub-owned recovery and inbox lifecycle for Steam review dossiers."""
import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier import atomic_write_json
from taste_steam_review_dossier_buffered import (
    current_expected_buffer_paths,
    expected_buffer_path,
    validate_buffer_artifact,
)
from taste_steam_review_dossier_daily import (
    load_contract,
    validate_group_plan,
    validate_manifest,
)
from taste_steam_review_dossier_group_progress import (
    FAILED,
    ensure_group_progress,
    next_pending_sequence,
    reopen_failed_group,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECOVERY_CONTRACT = ROOT / "config/taste_steam_review_dossier_recovery_contract.json"
_RECOGNIZED_INBOX = re.compile(r"^(?P<snapshot>[0-9a-f]{64})--.+\.json$")


def load_recovery_contract(path=DEFAULT_RECOVERY_CONTRACT):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if (
        doc.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-RECOVERY-CONTRACT-V1"
        or type(doc.get("version")) is not int
        or doc.get("version") != 1
        or doc.get("status") != "active"
        or doc.get("owner") != "github_control_plane"
    ):
        raise ValueError("dossier recovery contract is missing, stale or unsupported")
    actions = doc.get("request", {}).get("allowed_actions")
    if not isinstance(actions, list) or set(actions) != {"quarantine_invalid_expected", "reopen_failed_group"}:
        raise ValueError("dossier recovery allowed_actions are missing or unsupported")
    return doc


def quarantine_stale_snapshot_inbox(buffer_dir, active_snapshot_id, quarantine_root):
    """Move only recognizable old-snapshot transport files out of the active inbox."""
    if not isinstance(active_snapshot_id, str) or not re.fullmatch(r"[0-9a-f]{64}", active_snapshot_id):
        raise ValueError("active snapshot id is invalid")
    root = Path(buffer_dir)
    quarantine_root = Path(quarantine_root) / "stale"
    moved, preserved_unrecognized = [], []
    if not root.exists():
        return {"moved": moved, "preserved_unrecognized": preserved_unrecognized}
    for path in sorted(root.glob("*.json")):
        match = _RECOGNIZED_INBOX.fullmatch(path.name)
        if not match:
            preserved_unrecognized.append(path.as_posix())
            continue
        snapshot = match.group("snapshot")
        if snapshot == active_snapshot_id:
            continue
        target = quarantine_root / snapshot / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise ValueError(f"stale inbox quarantine target already exists: {target.as_posix()}")
        shutil.move(path.as_posix(), target.as_posix())
        moved.append({"source": path.as_posix(), "quarantine": target.as_posix()})
    return {"moved": moved, "preserved_unrecognized": preserved_unrecognized}


def _append_audit(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def _validate_request(request, recovery, manifest, plan):
    missing = [field for field in recovery["request"]["required_fields"] if field not in request]
    if missing:
        raise ValueError(f"recovery request is missing fields: {', '.join(missing)}")
    if request.get("schema") != recovery["request"]["schema"]:
        raise ValueError("recovery request schema is invalid")
    if type(request.get("schema_version")) is not int or request["schema_version"] != 1:
        raise ValueError("recovery request schema_version is invalid")
    if request.get("action") not in recovery["request"]["allowed_actions"]:
        raise ValueError("recovery request action is not authorized")
    if request.get("snapshot_id") != manifest["snapshot_id"]:
        raise ValueError("recovery request does not bind the current snapshot")
    if not isinstance(request.get("reason"), str) or not request["reason"].strip():
        raise ValueError("recovery request reason is required")
    sequence = request.get("sequence")
    if type(sequence) is not int or sequence < 1 or sequence > len(plan["groups"]):
        raise ValueError("recovery request sequence is outside current plan")
    descriptor = plan["groups"][sequence - 1]
    if request.get("group_sha256") != descriptor["group_sha256"]:
        raise ValueError("recovery request group binding is invalid")
    return sequence, descriptor


def _archive_request(request_path, quarantine_root, suffix):
    target = Path(quarantine_root) / "requests" / f"{request_path.stem}-{suffix}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise ValueError("recovery request archive target already exists")
    shutil.move(request_path.as_posix(), target.as_posix())
    return target


def process_recovery_request(
    *,
    request_path=None,
    recovery_contract_path=DEFAULT_RECOVERY_CONTRACT,
    dossier_contract_path="config/taste_steam_review_dossier_contract.json",
    manifest_path="data/production/pre_ai/taste_steam_review_dossier_work.json",
):
    """Apply one explicit GitHub-owned recovery action; never normal first-pass retry."""
    recovery = load_recovery_contract(recovery_contract_path)
    request_path = Path(request_path or recovery["request"]["path"])
    if not request_path.exists():
        return {"status": "no_recovery_request", "recovered": False}

    contract = load_contract(dossier_contract_path)
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = ensure_group_progress(manifest, contract)
    validate_manifest(manifest, contract)
    plan = validate_group_plan(manifest, contract, required=True)
    request = json.loads(request_path.read_text(encoding="utf-8"))
    sequence, descriptor = _validate_request(request, recovery, manifest, plan)
    expected = expected_buffer_path(descriptor, contract)
    if request.get("artifact_path") != expected.as_posix():
        raise ValueError("recovery request artifact path is not the deterministic group path")

    if request["action"] == "reopen_failed_group":
        progress = manifest["group_progress"]
        entry = progress["groups"][sequence - 1]
        if entry["state"] != FAILED:
            raise ValueError("reopen recovery requires a canonically failed group")
        if not progress["normal_first_pass_complete"]:
            raise ValueError("reopen recovery is separate and may run only after normal first pass completes")
        if expected.exists():
            raise ValueError("reopen recovery requires the deterministic active inbox path to be empty")
        reopened = reopen_failed_group(manifest, contract, sequence)
        atomic_write_json(manifest_path, reopened)
        recorded_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        audit = {
            "schema": "TASTE-STEAM-REVIEW-DOSSIER-RECOVERY-AUDIT-V1",
            "recorded_at_utc": recorded_at,
            "action": request["action"],
            "snapshot_id": manifest["snapshot_id"],
            "sequence": sequence,
            "group_sha256": descriptor["group_sha256"],
            "operator_reason": request["reason"].strip(),
            "transition": "failed_or_invalid_pending_recovery_to_pending",
            "canonical_acceptance_fabricated": False,
        }
        _append_audit(recovery["invalid_expected_artifact_recovery"]["audit_log"], audit)
        archive = _archive_request(
            request_path,
            recovery["invalid_expected_artifact_recovery"]["quarantine_dir"],
            descriptor["group_sha256"][:12],
        )
        return {
            "status": "failed_group_reopened_pending",
            "recovered": True,
            "snapshot_id": manifest["snapshot_id"],
            "sequence": sequence,
            "request_archive": archive.as_posix(),
            "canonical_acceptance_fabricated": False,
        }

    pending = next_pending_sequence(manifest, contract)
    if sequence != pending:
        raise ValueError("legacy quarantine recovery may target only the current next-pending group")
    if current_expected_buffer_paths(manifest, contract) != [expected] or not expected.exists():
        raise ValueError("legacy quarantine recovery requires exactly one deterministic next-pending artifact")

    raw = expected.read_bytes()
    try:
        artifact = json.loads(raw.decode("utf-8"))
        validate_buffer_artifact(artifact, descriptor, manifest, contract)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError, KeyError, TypeError) as exc:
        validator_error = str(exc)
    else:
        raise ValueError("recovery is forbidden because expected artifact is canonically valid")

    artifact_sha = hashlib.sha256(raw).hexdigest()
    quarantine_root = Path(recovery["invalid_expected_artifact_recovery"]["quarantine_dir"])
    target = quarantine_root / "invalid_expected" / manifest["snapshot_id"] / f"{expected.name}.invalid-{artifact_sha[:12]}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise ValueError("invalid expected quarantine target already exists")
    shutil.move(expected.as_posix(), target.as_posix())

    audit = {
        "schema": "TASTE-STEAM-REVIEW-DOSSIER-RECOVERY-AUDIT-V1",
        "recorded_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "action": request["action"],
        "snapshot_id": manifest["snapshot_id"],
        "sequence": sequence,
        "group_sha256": descriptor["group_sha256"],
        "source_artifact_path": expected.as_posix(),
        "quarantine_artifact_path": target.as_posix(),
        "artifact_sha256": artifact_sha,
        "validator_error": validator_error,
        "operator_reason": request["reason"].strip(),
        "canonical_progress_advanced": False,
    }
    _append_audit(recovery["invalid_expected_artifact_recovery"]["audit_log"], audit)
    archive = _archive_request(request_path, quarantine_root, artifact_sha[:12])
    return {
        "status": "invalid_next_pending_artifact_quarantined",
        "recovered": True,
        "snapshot_id": manifest["snapshot_id"],
        "sequence": sequence,
        "quarantine_artifact_path": target.as_posix(),
        "request_archive": archive.as_posix(),
        "canonical_progress_advanced": False,
    }


def main():
    parser = argparse.ArgumentParser(description="GitHub-owned Steam review dossier recovery lifecycle")
    parser.add_argument("--request", default=None)
    parser.add_argument("--recovery-contract", default=str(DEFAULT_RECOVERY_CONTRACT))
    parser.add_argument("--dossier-contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--manifest", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    args = parser.parse_args()
    result = process_recovery_request(
        request_path=args.request,
        recovery_contract_path=args.recovery_contract,
        dossier_contract_path=args.dossier_contract,
        manifest_path=args.manifest,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
