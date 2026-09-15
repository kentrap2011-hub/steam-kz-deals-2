#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_web import persist_submission_and_advance_snapshot_strict


def ingest_submission(
    submission_path,
    *,
    manifest_path="data/production/pre_ai/taste_steam_review_dossier_work.json",
    contract_path="config/taste_steam_review_dossier_contract.json",
    store_dir="data/cache/taste_steam_review_dossiers",
):
    """Run canonical V2 validation/persistence/same-snapshot advancement."""
    contract = load_contract(contract_path)
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    submission = json.loads(Path(submission_path).read_text(encoding="utf-8"))
    return persist_submission_and_advance_snapshot_strict(
        submission,
        manifest,
        contract,
        store_dir,
        manifest_output_path=manifest_path,
    )


def main():
    parser = argparse.ArgumentParser(description="Validate and persist one exact V2 web-evidence dossier checkpoint")
    parser.add_argument("submission")
    parser.add_argument("--manifest", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    args = parser.parse_args()

    persisted, next_manifest = ingest_submission(
        args.submission,
        manifest_path=args.manifest,
        contract_path=args.contract,
        store_dir=args.store_dir,
    )
    print(json.dumps({
        "status": "full_backlog_exhausted" if next_manifest["full_backlog_complete"] else "checkpoint_persisted_work_remaining",
        "snapshot_id": next_manifest["snapshot_id"],
        "persisted": persisted,
        "persisted_count": len(persisted),
        "next_scope_sha256": next_manifest["scope_sha256"],
        "next_checkpoint_required_count": next_manifest["current_checkpoint_count"],
        "remaining_required_count": next_manifest["remaining_required_count"],
        "full_backlog_complete": next_manifest["full_backlog_complete"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
