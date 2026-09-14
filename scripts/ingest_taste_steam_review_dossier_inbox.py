#!/usr/bin/env python3
"""GitHub-owned adapter for one Scheduled ChatGPT dossier checkpoint artifact."""
import argparse
import json
from pathlib import Path

from ingest_taste_steam_review_dossiers import ingest_submission


def expected_submission_path(submission, contract):
    snapshot_id = str(submission.get("snapshot_id") or "")
    scope_sha256 = str(submission.get("scope_sha256") or "")
    if len(snapshot_id) != 64 or len(scope_sha256) != 64:
        raise ValueError("dossier inbox submission lacks snapshot/scope binding")
    inbox = Path(contract["paths"]["submission_inbox_dir"])
    return inbox / f"{snapshot_id}--{scope_sha256}.json"


def ingest_inbox_submission(
    submission_path,
    *,
    manifest_path="data/production/pre_ai/taste_steam_review_dossier_work.json",
    contract_path="config/taste_steam_review_dossier_contract.json",
    store_dir="data/cache/taste_steam_review_dossiers",
    delete_accepted=True,
):
    submission_path = Path(submission_path)
    contract = json.loads(Path(contract_path).read_text(encoding="utf-8"))
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
    if delete_accepted:
        submission_path.unlink()
    return {
        "status": "full_backlog_exhausted" if next_manifest["full_backlog_complete"] else "checkpoint_persisted_work_remaining",
        "snapshot_id": next_manifest["snapshot_id"],
        "persisted": persisted,
        "persisted_count": len(persisted),
        "next_scope_sha256": next_manifest["scope_sha256"],
        "next_checkpoint_required_count": next_manifest["current_checkpoint_count"],
        "remaining_required_count": next_manifest["remaining_required_count"],
        "full_backlog_complete": next_manifest["full_backlog_complete"],
    }


def main():
    parser = argparse.ArgumentParser(description="Ingest one exact GitHub inbox dossier checkpoint artifact")
    parser.add_argument("submission")
    parser.add_argument("--manifest", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    parser.add_argument("--keep-accepted-submission", action="store_true")
    args = parser.parse_args()
    try:
        result = ingest_inbox_submission(
            args.submission,
            manifest_path=args.manifest,
            contract_path=args.contract,
            store_dir=args.store_dir,
            delete_accepted=not args.keep_accepted_submission,
        )
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        raise SystemExit(f"TASTE_STEAM_REVIEW_DOSSIER_INBOX_INVALID: {exc}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
