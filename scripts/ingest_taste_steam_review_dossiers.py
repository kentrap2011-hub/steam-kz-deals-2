#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from taste_steam_review_dossier import load_contract, persist_submission


def main():
    parser = argparse.ArgumentParser(description="Validate and persist compact Steam review dossiers")
    parser.add_argument("submission")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--manifest", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    args = parser.parse_args()

    contract = load_contract(args.contract)
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    submission = json.loads(Path(args.submission).read_text(encoding="utf-8"))
    persisted = persist_submission(submission, manifest, contract, args.store_dir)
    print(json.dumps({"status": "persisted", "count": len(persisted), "items": persisted}, ensure_ascii=False))


if __name__ == "__main__":
    main()
