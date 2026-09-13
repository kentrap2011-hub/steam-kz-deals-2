#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from taste_steam_review_dossier import atomic_write_json
from taste_steam_review_dossier_daily import build_daily_work_manifest, load_contract


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
    parser = argparse.ArgumentParser(description="Build one complete fixed daily Steam review dossier backlog snapshot")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--queue", default="data/production/pre_ai/chatgpt_taste_queue.jsonl")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    parser.add_argument("--output", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--ttl-days", type=int)
    args = parser.parse_args()

    contract = load_contract(args.contract)
    queue_rows = _read_jsonl(args.queue)
    manifest = build_daily_work_manifest(
        queue_rows, contract, args.store_dir, ttl_days=args.ttl_days, source_queue_path=args.queue
    )
    atomic_write_json(args.output, manifest)
    print(json.dumps({
        "status": manifest["status"],
        "snapshot_id": manifest["snapshot_id"],
        "prepared_for_date": manifest["prepared_for_date"],
        "source_queue_sha256": manifest["source_queue_sha256"],
        "source_row_count": manifest["source_row_count"],
        "eligible_scope_count": manifest["eligible_scope_count"],
        "prepared_required_count": manifest["prepared_required_count"],
        "current_checkpoint_count": manifest["current_checkpoint_count"],
        "remaining_required_count": manifest["remaining_required_count"],
        "full_backlog_complete": manifest["full_backlog_complete"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
