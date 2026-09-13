#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from taste_steam_review_dossier_daily import load_contract, persist_submission_and_advance_snapshot


def main():
    parser = argparse.ArgumentParser(description="Validate and persist one exact dossier checkpoint, then advance the same fixed daily snapshot")
    parser.add_argument("submission")
    parser.add_argument("--manifest", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    args = parser.parse_args()

    contract = load_contract(args.contract)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    submission = json.loads(Path(args.submission).read_text(encoding="utf-8"))
    persisted, next_manifest = persist_submission_and_advance_snapshot(
        submission,
        manifest,
        contract,
        args.store_dir,
        manifest_output_path=args.manifest,
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
