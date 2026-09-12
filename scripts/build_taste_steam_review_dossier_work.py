#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from taste_steam_review_dossier import atomic_write_json, build_work_manifest, load_contract


def main():
    parser = argparse.ArgumentParser(description="Build exact Steam review dossier preparation work for the current Taste pin")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--pin", default="data/production/pre_ai/taste_active_work_unit.json")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    parser.add_argument("--output", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--ttl-days", type=int)
    args = parser.parse_args()

    contract = load_contract(args.contract)
    pin = json.loads(Path(args.pin).read_text(encoding="utf-8"))
    manifest = build_work_manifest(pin, contract, args.store_dir, ttl_days=args.ttl_days)
    atomic_write_json(args.output, manifest)
    print(json.dumps({
        "status": manifest["status"],
        "scope_sha256": manifest["scope_sha256"],
        "required_count": len(manifest["required_items"]),
        "fresh_reuse_count": len(manifest["items"]) - len(manifest["required_items"]),
        "output": args.output,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
