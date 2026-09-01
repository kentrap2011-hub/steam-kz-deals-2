from __future__ import annotations

import argparse
import json

from giveaway_core import REQUIRED_SOURCES, build_snapshot, failed_collection, utc_now, validate_existing_artifact, write_snapshot
from giveaway_epic import ENDPOINT as EPIC_ENDPOINT
from giveaway_epic import collect as collect_epic
from giveaway_gog import ENDPOINT as GOG_ENDPOINT
from giveaway_gog import collect as collect_gog
from giveaway_http import make_session
from giveaway_steam import collect as collect_steam


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the canonical Steam/Epic/GOG KZ claim-to-keep giveaway snapshot")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.validate_only:
        return validate_existing_artifact(require_complete=args.require_complete)

    now = utc_now()
    session = make_session()
    collectors = {
        "steam": (collect_steam, "existing KZ Steam catalog + targeted first-party validation"),
        "epic": (collect_epic, EPIC_ENDPOINT),
        "gog": (collect_gog, GOG_ENDPOINT),
    }
    collections = {}
    for source_id in REQUIRED_SOURCES:
        collector, endpoint = collectors[source_id]
        try:
            collections[source_id] = collector(session, now)
        except Exception as exc:
            collections[source_id] = failed_collection(source_id, endpoint, now, exc)

    snapshot, audit = build_snapshot(collections, now)
    write_snapshot(snapshot, audit)
    print(json.dumps({
        "contract": snapshot["contract"],
        "snapshot_status": snapshot["snapshot_status"],
        "generated_at_utc": snapshot["generated_at_utc"],
        "accepted_offer_count": snapshot["accepted_offer_count"],
        "game_group_count": snapshot["game_group_count"],
        "source_health": {
            source_id: {
                "status": snapshot["source_health"][source_id]["status"],
                "complete": snapshot["source_health"][source_id]["complete"],
                "accepted_count": snapshot["source_health"][source_id]["accepted_count"],
                "unverified_count": snapshot["source_health"][source_id]["unverified_count"],
                "error_code": snapshot["source_health"][source_id]["error_code"],
            }
            for source_id in REQUIRED_SOURCES
        },
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
