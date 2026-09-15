#!/usr/bin/env python3
"""GitHub-owned recovery and inbox lifecycle for Steam review dossiers."""
import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier_buffered import (
    current_expected_buffer_paths,
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


def process_recovery_request(
    *,
    request_path=None,
    recovery_contract_path=DEFAULT_RECOVERY_CONTRACT,
    dossier_contract_path="config/taste_steam_review_dossier_contract.json",
    manifest_path="data/production/pre_ai/taste_steam_review_dossier_work.json",
):
    """Quarantine only a validator-proven invalid current expected deterministic artifact."""
    recovery = load_recovery_contract(recovery_contract_path)
    request_path = Path(request_path or recovery["request"]["path"])
    if not request_path.exists():
        return {"status": "no_recovery_request", "recovered": False}

    contract = load_contract(dossier_contract_path)
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    validate_manifest(manifest, contract)
    plan = validate_group_plan(manifest, contract, required=True)
    sequence = expected_group_sequence(manifest, contract)
    if sequence is None:
        raise ValueError("cannot recover an inbox artifact after canonical completion")

    request = json.loads(request_path.read_text(encoding="utf-8"))
    missing = [field for field in recovery["request"]["required_fields"] if field not in request]
    if missing:
        raise ValueError(f"recovery request is missing fields: {', '.join(missing)}")
    if request.get("schema") != recovery["request"]["schema"]:
        raise ValueError("recovery request schema is invalid")
    if type(request.get("schema_version")) is not int or request["schema_version"] != 1:
        raise ValueError("recovery request schema_version is invalid")
    if request.get("action") != recovery["request"]["allowed_action"]:
        raise ValueError("recovery request action is not authorized")
    if type(request.get("sequence")) is not int or request["sequence"] != sequence:
        raise ValueError("recovery request does not bind the current expected sequence")
    if request.get("snapshot_id") != manifest["snapshot_id"]:
        raise ValueError("recovery request does not bind the current snapshot")
    if not isinstance(request.get("reason"), str) or not request["reason"].strip():
        raise ValueError("recovery request reason is required")

    descriptor = plan["groups"][sequence - 1]
    expected = expected_buffer_path(descriptor, contract)
    if request.get("group_sha256") != descriptor["group_sha256"]:
        raise ValueError("recovery request group binding is invalid")
    if request.get("artifact_path") != expected.as_posix():
        raise ValueError("recovery request artifact path is not deterministic expected path")
    if current_expected_buffer_paths(manifest, contract) != [expected] or not expected.exists():
        raise ValueError("recovery requires exactly one deterministic current expected artifact")

    raw = expected.read_bytes()
    try:
        artifact = json.loads(raw.decode("utf-8"))
        validate_buffer_artifact(artifact, descriptor, manifest, contract)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError, KeyError, TypeError) as exc:
        validator_error = str(exc)
    else:
        raise ValueError("recovery is forbidden because expected artifact is canonically valid")

    completed_before = manifest["completed_required_count"]
    remaining_before = manifest["remaining_required_count"]
    artifact_sha = hashlib.sha256(raw).hexdigest()
    quarantine_root = Path(recovery["invalid_expected_artifact_recovery"]["quarantine_dir"])
    target = quarantine_root / "invalid_expected" / manifest["snapshot_id"] / f"{expected.name}.invalid-{artifact_sha[:12]}"
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise ValueError("invalid expected quarantine target already exists")
    shutil.move(expected.as_posix(), target.as_posix())

    after = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    validate_manifest(after, contract)
    if (
        after["snapshot_id"] != manifest["snapshot_id"]
        or after["completed_required_count"] != completed_before
        or after["remaining_required_count"] != remaining_before
        or expected_group_sequence(after, contract) != sequence
    ):
        raise ValueError("recovery unexpectedly changed canonical progress")

    recorded_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    audit = {
        "schema": "TASTE-STEAM-REVIEW-DOSSIER-RECOVERY-AUDIT-V1",
        "recorded_at_utc": recorded_at,
        "action": request["action"],
        "snapshot_id": manifest["snapshot_id"],
        "sequence": sequence,
        "group_sha256": descriptor["group_sha256"],
        "source_artifact_path": expected.as_posix(),
        "quarantine_artifact_path": target.as_posix(),
        "artifact_sha256": artifact_sha,
        "validator_error": validator_error,
        "operator_reason": request["reason"].strip(),
        "completed_required_count_before": completed_before,
        "remaining_required_count_before": remaining_before,
        "canonical_progress_advanced": False
    }
    _append_audit(recovery["invalid_expected_artifact_recovery"]["audit_log"], audit)

    request_archive = quarantine_root / "requests" / f"{request_path.stem}-{artifact_sha[:12]}.json"
    request_archive.parent.mkdir(parents=True, exist_ok=True)
    if request_archive.exists():
        raise ValueError("recovery request archive target already exists")
    shutil.move(request_path.as_posix(), request_archive.as_posix())
    return {
        "status": "invalid_expected_artifact_quarantined",
        "recovered": True,
        "snapshot_id": manifest["snapshot_id"],
        "sequence": sequence,
        "quarantine_artifact_path": target.as_posix(),
        "canonical_progress_advanced": False
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
