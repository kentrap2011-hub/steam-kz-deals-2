#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from taste_steam_review_dossier import atomic_write_json, build_semantic_input, load_contract


def main():
    parser = argparse.ArgumentParser(description="Build fail-closed downstream Taste semantic input with fresh Steam dossiers")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--pin", default="data/production/pre_ai/taste_active_work_unit.json")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    parser.add_argument("--output", default="data/production/pre_ai/taste_semantic_dossier_input.json")
    args = parser.parse_args()

    contract = load_contract(args.contract)
    pin = json.loads(Path(args.pin).read_text(encoding="utf-8"))
    doc = build_semantic_input(pin, contract, args.store_dir)
    atomic_write_json(args.output, doc)
    print(json.dumps({
        "status": doc["status"],
        "row_count": len(doc["rows"]),
        "pin_work_unit_sha256": doc["pin"]["ordered_work_unit_sha256"],
        "semantic_input_sha256": doc["semantic_input_sha256"],
        "output": args.output,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
