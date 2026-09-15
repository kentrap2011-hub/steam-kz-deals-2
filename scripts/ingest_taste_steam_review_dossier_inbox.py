#!/usr/bin/env python3
"""GitHub-owned state-based dossier inbox drain with legacy transition support."""
import argparse
import json
from pathlib import Path

from ingest_taste_steam_review_dossiers import ingest_submission
from taste_steam_review_dossier_buffered import current_expected_buffer_paths, drain_buffered_groups
from taste_steam_review_dossier_daily import load_contract, validate_manifest
from taste_steam_review_dossier_worker_projection import write_worker_projection


def expected_submission_path(submission, contract):
    snapshot_id = str(submission.get("snapshot_id") or "")
    scope_sha256 = str(submission.get("scope_sha256") or "")
    if len(snapshot_id) != 64 or len(scope_sha256) != 64:
        raise ValueError("dossier inbox submission lacks snapshot/scope binding")
    inbox = Path(contract["paths"]["submission_inbox_dir"])
    return inbox / f"{snapshot_id}--{scope_sha256}.json"


def expected_legacy_path_from_manifest(manifest, contract):
    inbox = Path(contract["paths"]["submission_inbox_dir"])
    return inbox / f"{manifest['snapshot_id']}--{manifest['scope_sha256']}.json"


def ingest_inbox_submission(
    submission_path,
    *,
    manifest_path="data/production/pre_ai/taste_steam_review_dossier_work.json",
    contract_path="config/taste_steam_review_dossier_contract.json",
    store_dir="data/cache/taste_steam_review_dossiers",
    delete_accepted=True,
):
    """Compatibility entry point for the retained legacy current-checkpoint path."""
    submission_path = Path(submission_path)
    contract = load_contract(contract_path)
    submission = json.loads(submission_path.read_text(encoding="utf-8"))
    expected = expected_submission_path(submission, contract)
    if submission_path.as_posix() != expected.as_posix():
        raise ValueError(f"dossier inbox path mismatch: expected {expected.as_posix()}")

    persisted, next_manifest = ingest_submission(
        submission_path,
        manifest_path=manifest_path,
        contract_path=contract_path,
        store_dir=store_dir,
    )
    write_worker_projection(next_manifest, contract)
    if delete_accepted:
        submission_path.unlink()
    return {
        "mode": "legacy_current_checkpoint",
        "status": "full_backlog_exhausted" if next_manifest["full_backlog_complete"] else "checkpoint_persisted_work_remaining",
        "snapshot_id": next_manifest["snapshot_id"],
        "persisted": persisted,
        "persisted_count": len(persisted),
        "next_scope_sha256": next_manifest["scope_sha256"],
        "next_checkpoint_required_count": next_manifest["current_checkpoint_count"],
        "remaining_required_count": next_manifest["remaining_required_count"],
        "full_backlog_complete": next_manifest["full_backlog_complete"],
    }


def _blocked_result(manifest, reason, sequence, mode):
    return {
        "mode": mode,
        "status": "blocked_no_progress",
        "snapshot_id": manifest["snapshot_id"],
        "persisted": [],
        "persisted_count": 0,
        "accepted_group_count": 0,
        "accepted_dossier_count": 0,
        "blocked_reason": reason,
        "stop_sequence": sequence,
        "remaining_required_count": manifest["remaining_required_count"],
        "full_backlog_complete": manifest["full_backlog_complete"],
    }


def drain_inbox_state(
    *,
    manifest_path="data/production/pre_ai/taste_steam_review_dossier_work.json",
    contract_path="config/taste_steam_review_dossier_contract.json",
    store_dir="data/cache/taste_steam_review_dossiers",
    buffer_dir=None,
    fail_on_blocked=True,
):
    """Drain current repository state; the push event is only a wake-up signal.

    With fail_on_blocked=False this is the existing-writer lost-wakeup reconciliation
    mode: an invalid/gapped pending state is reported without mutating progress or
    failing the unrelated pre-AI build.
    """
    contract = load_contract(contract_path)
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest, contract)
    inbox = Path(buffer_dir or contract["paths"]["submission_inbox_dir"])
    legacy_path = expected_legacy_path_from_manifest(manifest, contract)
    legacy_exists = legacy_path.exists() and not manifest["full_backlog_complete"]

    buffered_expected = current_expected_buffer_paths(manifest, contract, inbox) if manifest.get("submission_group_plan") else []
    if legacy_exists and buffered_expected:
        if fail_on_blocked:
            raise ValueError("both legacy and buffered artifacts claim the current canonical expected group")
        return _blocked_result(manifest, "legacy_and_buffered_claim_same_position", None, "state_based_reconciliation")

    if manifest.get("submission_group_plan") is not None:
        result = drain_buffered_groups(
            manifest_path=manifest_path,
            contract=contract,
            buffer_dir=inbox,
            store_dir=store_dir,
        )
        if result["accepted_group_count"]:
            next_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            validate_manifest(next_manifest, contract)
            write_worker_projection(next_manifest, contract)
            result["mode"] = "buffered_contiguous_drain" if fail_on_blocked else "state_based_reconciliation"
            result["status"] = "full_backlog_exhausted" if result["full_backlog_complete"] else "buffered_prefix_persisted"
            return result
        if result["blocked_reason"] not in (None, "gap"):
            if fail_on_blocked:
                raise ValueError(
                    f"buffered drain blocked at sequence {result['stop_sequence']}: {result['blocked_reason']}"
                )
            return _blocked_result(
                manifest,
                result["blocked_reason"],
                result["stop_sequence"],
                "state_based_reconciliation",
            )

    if legacy_exists:
        try:
            return ingest_inbox_submission(
                legacy_path,
                manifest_path=manifest_path,
                contract_path=contract_path,
                store_dir=store_dir,
                delete_accepted=True,
            )
        except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
            if fail_on_blocked:
                raise
            return _blocked_result(manifest, f"invalid_legacy_expected:{exc}", None, "state_based_reconciliation")

    return {
        "mode": "state_based_noop" if fail_on_blocked else "state_based_reconciliation",
        "status": "no_contiguous_work_available",
        "snapshot_id": manifest["snapshot_id"],
        "persisted": [],
        "persisted_count": 0,
        "remaining_required_count": manifest["remaining_required_count"],
        "full_backlog_complete": manifest["full_backlog_complete"],
    }


def main():
    parser = argparse.ArgumentParser(description="Drain current GitHub dossier inbox state")
    parser.add_argument("submission", nargs="?", help="legacy exact checkpoint path; omit for state-based drain")
    parser.add_argument("--manifest", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    parser.add_argument("--buffer-dir", default=None)
    parser.add_argument("--keep-accepted-submission", action="store_true")
    parser.add_argument("--reconcile-nonfatal", action="store_true")
    args = parser.parse_args()
    try:
        if args.submission:
            if args.reconcile_nonfatal:
                raise ValueError("--reconcile-nonfatal is state-based and cannot be combined with a submission path")
            result = ingest_inbox_submission(
                args.submission,
                manifest_path=args.manifest,
                contract_path=args.contract,
                store_dir=args.store_dir,
                delete_accepted=not args.keep_accepted_submission,
            )
        else:
            result = drain_inbox_state(
                manifest_path=args.manifest,
                contract_path=args.contract,
                store_dir=args.store_dir,
                buffer_dir=args.buffer_dir,
                fail_on_blocked=not args.reconcile_nonfatal,
            )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        raise SystemExit(f"TASTE_STEAM_REVIEW_DOSSIER_INBOX_INVALID: {exc}")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
