#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from taste_steam_review_dossier import load_contract, persist_submission_and_rebuild_work


def _read_jsonl(path):
    rows = []
    for n, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{n}: {exc}") from exc
    return rows


def main():
    parser = argparse.ArgumentParser(description="Validate and persist one exact Steam review dossier checkpoint, then expose the next remaining checkpoint")
    parser.add_argument("submission")
    parser.add_argument("--manifest", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--queue", default="data/production/pre_ai/chatgpt_taste_queue.jsonl")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    args = parser.parse_args()

    contract = load_contract(args.contract)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    submission = json.loads(Path(args.submission).read_text(encoding="utf-8"))
    queue_rows = _read_jsonl(args.queue)
    persisted, next_manifest = persist_submission_and_rebuild_work(
        submission,
        manifest,
        contract,
        args.store_dir,
        queue_rows,
        manifest_output_path=args.manifest,
    )
    print(json.dumps({
        "status": "full_backlog_exhausted" if next_manifest["full_backlog_complete"] else "checkpoint_persisted_work_remaining",
        "persisted": persisted,
        "persisted_count": len(persisted),
        "next_scope_sha256": next_manifest["scope_sha256"],
        "next_checkpoint_required_count": next_manifest["checkpoint"]["item_count"],
        "remaining_required_count": next_manifest["required_total_count"],
        "remaining_after_checkpoint_count": next_manifest["checkpoint"]["remaining_after_checkpoint_count"],
        "full_backlog_complete": next_manifest["full_backlog_complete"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
