#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier import dossier_state, load_contract, validate_pin

CLEANUP_SCHEMA = "TASTE-STEAM-REVIEW-DOSSIER-CLEANUP-V1"
_CANONICAL_NAME = re.compile(r"^App_(\d+)\.json$")


def cleanup_dossier_store(pin, contract, store_dir, *, now=None):
    """Delete only stale dossiers that are outside the current canonical Taste scope.

    Fresh dossiers are always preserved. Stale dossiers that are still needed by the
    current Taste scope are preserved and reported as refresh_required until a fresh
    dossier successfully replaces the same App_<appid>.json path.
    """
    validate_pin(pin)
    cleanup = contract.get("cleanup") or {}
    if cleanup.get("owner") != "github_control_plane":
        raise ValueError("Dossier cleanup ownership contract is missing or invalid")
    if cleanup.get("delete_rule") != "stale_and_not_in_current_taste_scope":
        raise ValueError("Dossier cleanup delete rule is missing or unsupported")

    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    store = Path(store_dir)
    store.mkdir(parents=True, exist_ok=True)
    scope_appids = {str(row["appid"]) for row in pin["ordered_rows"]}

    deleted = []
    refresh_required = []
    preserved_fresh = []
    preserved_invalid = []
    ignored = []

    for path in sorted(store.glob("App_*.json"), key=lambda p: p.name):
        match = _CANONICAL_NAME.fullmatch(path.name)
        if not match:
            ignored.append({"path": path.as_posix(), "reason": "noncanonical_filename"})
            continue
        appid = match.group(1)
        try:
            dossier = json.loads(path.read_text(encoding="utf-8"))
            state = dossier_state(dossier, contract, now=now, expected_appid=appid)
        except Exception as exc:
            preserved_invalid.append({
                "appid": appid,
                "path": path.as_posix(),
                "state": "invalid",
                "reason": str(exc),
                "in_current_scope": appid in scope_appids,
            })
            continue

        if state == "stale" and appid not in scope_appids:
            path.unlink()
            deleted.append({
                "appid": appid,
                "path": path.as_posix(),
                "state": "stale",
                "action": "deleted_out_of_scope",
            })
        elif state == "stale":
            refresh_required.append({
                "appid": appid,
                "path": path.as_posix(),
                "state": "stale",
                "action": "refresh_required",
            })
        elif state == "fresh":
            preserved_fresh.append({
                "appid": appid,
                "path": path.as_posix(),
                "state": "fresh",
                "in_current_scope": appid in scope_appids,
                "action": "preserved_until_ttl_expiry",
            })
        else:
            preserved_invalid.append({
                "appid": appid,
                "path": path.as_posix(),
                "state": state,
                "in_current_scope": appid in scope_appids,
                "action": "preserved_fail_closed",
            })

    return {
        "schema": CLEANUP_SCHEMA,
        "schema_version": 1,
        "status": "complete",
        "owner": "github_control_plane",
        "evaluated_at_utc": now.replace(microsecond=0).isoformat(),
        "pin_work_unit_sha256": pin["ordered_work_unit_sha256"],
        "current_scope_appids": sorted(scope_appids, key=int),
        "deleted_stale_out_of_scope": deleted,
        "preserved_refresh_required": refresh_required,
        "preserved_fresh": preserved_fresh,
        "preserved_invalid": preserved_invalid,
        "ignored": ignored,
    }


def main():
    parser = argparse.ArgumentParser(description="Delete expired out-of-scope Steam review dossiers deterministically")
    parser.add_argument("--contract", default="config/taste_steam_review_dossier_contract.json")
    parser.add_argument("--pin", default="data/production/pre_ai/taste_active_work_unit.json")
    parser.add_argument("--store-dir", default="data/cache/taste_steam_review_dossiers")
    args = parser.parse_args()

    contract = load_contract(args.contract)
    pin = json.loads(Path(args.pin).read_text(encoding="utf-8"))
    result = cleanup_dossier_store(pin, contract, args.store_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
