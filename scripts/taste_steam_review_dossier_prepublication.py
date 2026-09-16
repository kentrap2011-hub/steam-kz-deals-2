#!/usr/bin/env python3
"""Fail-closed worker-side prepublication guard using the canonical buffer validator."""
import argparse
import json
import sys
from pathlib import Path

from taste_steam_review_dossier_buffered import validate_buffer_artifact
from taste_steam_review_dossier_daily import load_contract, validate_group_plan, validate_manifest


def descriptor_for_artifact(artifact, manifest, contract):
    validate_manifest(manifest, contract)
    plan = validate_group_plan(manifest, contract, required=True)
    if not isinstance(artifact, dict):
        raise ValueError("buffered dossier group must be an object")
    sequence = artifact.get("sequence")
    if type(sequence) is not int or sequence < 1 or sequence > len(plan["groups"]):
        raise ValueError("prepublication group sequence is outside the immutable group plan")
    descriptor = plan["groups"][sequence - 1]
    if artifact.get("snapshot_id") != manifest.get("snapshot_id"):
        raise ValueError("prepublication group snapshot_id does not match the current canonical manifest")
    return descriptor


def validate_prepublication_artifact(artifact, manifest, contract):
    """Run exactly the canonical buffered acceptance implementation before publication."""
    descriptor = descriptor_for_artifact(artifact, manifest, contract)
    docs = validate_buffer_artifact(artifact, descriptor, manifest, contract)
    return {
        "status": "valid",
        "snapshot_id": descriptor["snapshot_id"],
        "sequence": descriptor["sequence"],
        "group_sha256": descriptor["group_sha256"],
        "dossier_count": len(docs),
        "canonical_validator": "taste_steam_review_dossier_buffered.validate_buffer_artifact",
    }


def _read_artifact(path):
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(
        description="Validate one complete Taste dossier buffered group before create-only publication"
    )
    parser.add_argument("--artifact", required=True, help="candidate JSON path, or - for stdin")
    parser.add_argument("--manifest", default="data/production/pre_ai/taste_steam_review_dossier_work.json")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    args = parser.parse_args()
    try:
        contract = load_contract(args.contract)
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        artifact = _read_artifact(args.artifact)
        result = validate_prepublication_artifact(artifact, manifest, contract)
    except (ValueError, json.JSONDecodeError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "invalid", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
