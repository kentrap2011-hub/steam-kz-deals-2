#!/usr/bin/env python3
"""GitHub-owned state-based dossier inbox drain with legacy transition support."""
import argparse
import json
from pathlib import Path

from ingest_taste_steam_review_dossiers import ingest_submission
from taste_steam_review_dossier_buffered import drain_buffered_groups
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


def drain_inbox_state(
    *,
    manifest_path="data/production/pre_ai/taste_steam_review_dossier_work.json",
    contract_path="config/taste_steam_review_dossier_contract.json",
    store_dir="data/cache/taste_steam_review_dossiers",
    buffer_dir=None,
    failed_quarantine_root=None,
    failure_audit_path=None,
    retryable_rejection_root=None,
    rejection_audit_path=None,
    terminal_receipt_archive_root=None,
    frozen_authority_audit_path=None,
    repo_root=Path("."),
    fail_on_blocked=True,
):
    """Classify present Dossier transports independently from repository state.

    A valid semantic-exhaustion terminal receipt consumes one exact normal first-pass
    group attempt into the existing failed/recovery state. Invalid transport remains
    retryable normal work after quarantine and never impersonates semantic exhaustion.
    """
    contract = load_contract(contract_path)
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validate_manifest(manifest, contract)
    inbox = Path(buffer_dir or contract["paths"]["submission_inbox_dir"])

    if manifest.get("submission_group_plan") is not None:
        drain_kwargs = {}
        if failed_quarantine_root is not None:
            drain_kwargs["failed_quarantine_root"] = failed_quarantine_root
        if failure_audit_path is not None:
            drain_kwargs["failure_audit_path"] = failure_audit_path
        if retryable_rejection_root is not None:
            drain_kwargs["retryable_rejection_root"] = retryable_rejection_root
        if rejection_audit_path is not None:
            drain_kwargs["rejection_audit_path"] = rejection_audit_path
        if terminal_receipt_archive_root is not None:
            drain_kwargs["terminal_receipt_archive_root"] = terminal_receipt_archive_root
        if frozen_authority_audit_path is not None:
            drain_kwargs["frozen_authority_audit_path"] = frozen_authority_audit_path
        drain_kwargs["repo_root"] = repo_root
        result = drain_buffered_groups(
            manifest_path=manifest_path,
            contract=contract,
            buffer_dir=inbox,
            store_dir=store_dir,
            **drain_kwargs,
        )
        changed = bool(
            result["accepted_group_count_this_run"]
            or result["failed_group_count_this_run"]
            or result.get("cache_reused_group_count_this_run")
        )
        transport_reconciled = bool(
            result.get("retryable_transport_rejection_count_this_run")
            or result.get("terminal_replay_cleanup_count_this_run")
            or result.get("frozen_authority_accepted_count_this_run")
            or result.get("frozen_authority_terminal_count_this_run")
            or result.get("frozen_authority_rejected_count_this_run")
            or result.get("frozen_authority_replay_cleanup_count_this_run")
        )
        current = json.loads(manifest_path.read_text(encoding="utf-8"))
        validate_manifest(current, contract)
        if changed or transport_reconciled:
            write_worker_projection(current, contract)
        result["mode"] = "buffered_nonblocking_group_drain"
        retryable_rejection_count = int(result.get("retryable_transport_rejection_count_this_run") or 0)
        rejected_sequences = {
            int(sequence) for sequence in result.get("rejected_sequences", [])
        }
        next_pending = result.get("next_pending_sequence")
        head_retryable_rejected = bool(
            retryable_rejection_count
            and next_pending is not None
            and int(next_pending) in rejected_sequences
        )
        result["head_retryable_transport_rejected_this_run"] = head_retryable_rejected
        result["canonical_progress_made_this_run"] = changed

        if result["all_groups_accepted"]:
            result["status"] = "all_groups_accepted"
        elif result["normal_first_pass_complete"]:
            result["status"] = "normal_first_pass_complete_with_failures"
        elif changed and retryable_rejection_count:
            result["status"] = "group_state_advanced_with_retryable_transport_rejection"
        elif changed:
            result["status"] = "group_state_advanced"
        elif head_retryable_rejected:
            result["status"] = "retryable_transport_rejected_head_blocked_zero_progress"
        elif result.get("frozen_authority_accepted_count_this_run"):
            result["status"] = "frozen_authority_dossier_persisted"
        elif result.get("frozen_authority_terminal_count_this_run"):
            result["status"] = "frozen_authority_terminal_recorded"
        elif result.get("frozen_authority_rejected_count_this_run"):
            result["status"] = "frozen_authority_transport_rejected"
        elif retryable_rejection_count:
            result["status"] = "retryable_transport_rejected_nonblocking_zero_progress"
        elif result.get("frozen_authority_replay_cleanup_count_this_run"):
            result["status"] = "frozen_authority_replay_cleaned"
        elif result.get("terminal_replay_cleanup_count_this_run"):
            result["status"] = "terminal_replay_cleaned"
        else:
            result["status"] = "no_pending_artifact_available"
        return result

    legacy_path = expected_legacy_path_from_manifest(manifest, contract)
    legacy_exists = legacy_path.exists() and not manifest["full_backlog_complete"]
    if legacy_exists:
        try:
            return ingest_inbox_submission(
                legacy_path,
                manifest_path=manifest_path,
                contract_path=contract_path,
                store_dir=store_dir,
                delete_accepted=True,
            )
        except (ValueError, FileNotFoundError, json.JSONDecodeError):
            if fail_on_blocked:
                raise
            return {
                "mode": "legacy_state_based_reconciliation",
                "status": "legacy_invalid_no_progress",
                "snapshot_id": manifest["snapshot_id"],
                "persisted": [],
                "persisted_count": 0,
                "remaining_required_count": manifest["remaining_required_count"],
                "full_backlog_complete": manifest["full_backlog_complete"],
            }

    return {
        "mode": "state_based_noop" if fail_on_blocked else "state_based_reconciliation",
        "status": "no_work_available",
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
