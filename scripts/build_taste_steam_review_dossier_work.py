#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from taste_steam_review_dossier import atomic_write_json, build_work_manifest, load_contract


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
    parser = argparse.ArgumentParser(description="Build the next bounded Steam review dossier checkpoint from the full canonical Taste backlog")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--queue", default="data/production/pre_ai/chatgpt_taste_queue.jsonl")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    parser.add_argument("--output", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--ttl-days", type=int)
    args = parser.parse_args()

    contract = load_contract(args.contract)
    queue_rows = _read_jsonl(args.queue)
    manifest = build_work_manifest(queue_rows, contract, args.store_dir, ttl_days=args.ttl_days)
    atomic_write_json(args.output, manifest)
    print(json.dumps({
        "status": manifest["status"],
        "scope_sha256": manifest["scope_sha256"],
        "source_queue_sha256": manifest["source_queue_sha256"],
        "source_row_count": manifest["source_row_count"],
        "eligible_row_count": manifest["eligible_row_count"],
        "unique_appid_count": manifest["unique_appid_count"],
        "deduplicated_row_count": manifest["deduplicated_row_count"],
        "checkpoint_size": manifest["checkpoint"]["checkpoint_size"],
        "checkpoint_required_count": manifest["checkpoint"]["item_count"],
        "remaining_required_count": manifest["required_total_count"],
        "remaining_after_checkpoint_count": manifest["checkpoint"]["remaining_after_checkpoint_count"],
        "full_backlog_complete": manifest["full_backlog_complete"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
