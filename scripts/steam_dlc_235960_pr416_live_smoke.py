#!/usr/bin/env python3
"""One-off PR-only live smoke of the SAME production DLC discovery implementation.

Fetch only App_2820, App_201310 and App_235960 from Steam Store KZ.
Exercise discover_dlc_for_bases on *exact live relationship values*, with
root/middle candidate lists restricted to those 3 identities. A second,
strictly in-memory run substitutes a clearly synthetic price to test that a
validly linked nested child would get the exact verified_parent_chains.
Never publishes a synthetic commercial offer or claims entire catalog coverage.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
import os
from pathlib import Path

import requests

import steam_partial_publish_runner as collector
import steam_targeted_paid_lanes as targeted


IDS = ("2820", "201310", "235960")
MAX_STARTS = 6
RESULT_FILE = Path("dlc235960-pr416-smoke.json")


class ExactKzGetter:
    def __init__(self):
        self.starts = 0
        self.states = {}

    def __call__(self, url, **kwargs):
        params = kwargs.get("params") or {}
        aid = str(params.get("appids"))
        if url != targeted.APPDETAILS_URL or aid not in IDS:
            raise RuntimeError("UNEXPECTED_NETWORK_TARGET")
        if params.get("cc") != "kz" or params.get("l") != "english":
            raise RuntimeError("UNEXPECTED_REQUEST_REGION_OR_LANGUAGE")
        if self.starts >= MAX_STARTS:
            raise RuntimeError("HARD_NETWORK_START_BUDGET_EXHAUSTED")
        if kwargs.get("timeout") != 25:
            raise RuntimeError("PRODUCTION_REQUEST_TIMEOUT_NOT_USED")
        self.starts += 1
        response = requests.get(url, **kwargs)
        self.states[aid] = f"HTTP_{response.status_code}"
        return response


def brief(aid, record):
    raw_list = record.get("dlc")
    members = targeted._dlc_ids(record, aid)
    price = record.get("price_overview", "<absent>")
    if price == "<absent>":
        price_state = "absent"
    elif price is None:
        price_state = "null"
    elif price == {}:
        price_state = "empty"
    else:
        price_state = "present"
    return {
        "requested": aid,
        "steam_appid": record.get("steam_appid"),
        "type": record.get("type"),
        "fullgame_appid": targeted._fullgame_id(record, aid),
        "dlc_shape": "list" if isinstance(raw_list, list) else "absent",
        "dlc_count": len(members),
        "lists_201310": "201310" in members,
        "lists_235960": "235960" in members,
        "price_state": price_state if aid == "235960" else "not_checked",
    }


def subset_data(live):
    """Keep every relevant real relation, remove unrelated IDs from discovery only.

    The normal production collector sees *all* base DLC listings and may make
    thousands of requests. This preview deliberately never claims to replay
    its complete root set.
    """
    records = deepcopy(live)
    for aid in ("2820", "201310"):
        if "dlc" in records[aid]:
            valid = targeted._dlc_ids(records[aid], aid)
            records[aid]["dlc"] = [int(item) for item in valid if item in IDS]
    return records


def exercise_production(live):
    """Run the real importer+validator/caller with a bounded fetch injection."""
    fields = {aid: brief(aid, live[aid]) for aid in IDS}
    root = fields["2820"]
    middle = fields["201310"]
    child = fields["235960"]
    expected = (root["type"] == "game"
                and root["lists_201310"]
                and root["lists_235960"]
                and middle["type"] in ("dlc", "game")
                and middle["fullgame_appid"] == "2820"
                and child["type"] == "dlc"
                and child["fullgame_appid"] == "201310")
    if not expected:
        raise ValueError("CURRENT_LIVE_RELATIONS_DO_NOT_MATCH_BOUNDED_2820_CHAIN")

    trimmed = subset_data(live)
    core = collector.load_core()

    def run(records):
        requested = []
        def fetch(appid):
            requested.append(appid)
            if appid not in records:
                raise RuntimeError(f"SMOKE_SCOPE_EXCEEDED_{appid}")
            return deepcopy(records[appid])
        result, stats = targeted.discover_dlc_for_bases(
            ["2820"], core, fetch=fetch
        )
        if sorted(requested) != sorted(IDS):
            raise RuntimeError(f"WRONG_BOUNDED_CALLER_SCOPE_{requested}")
        return result, stats

    live_offers, actual_stats = run(trimmed)
    live_price_state = child["price_state"]
    if live_price_state in ("absent", "empty", "null") and "App_235960" in live_offers:
        raise AssertionError("UNPRICED_CHILD_WAS_PUBLISHED")

    # Synthetic price is NEVER submitted to Steam and NEVER written to the
    # catalog. It isolates exact source-code parent attribution from the
    # genuine child's unpriced KZ commercial eligibility.
    synthetic = deepcopy(trimmed)
    synthetic["235960"]["price_overview"] = {
        "currency": "KZT", "final": 25000, "discount_percent": 85,
    }
    synthetic["235960"]["name"] = "Synthetic parent-chain test"
    modeled_offers, modeled_stats = run(synthetic)
    actual_path = modeled_offers.get("App_235960", {}).get("verified_parent_chains")
    expected_path = [["2820", "201310", "235960"]]
    if actual_path != expected_path:
        raise AssertionError(f"PARENT_CHAIN_NOT_RECOGNIZED_{actual_path}")

    return {
        "fields": fields,
        "root_lists_child_but_middle_omits_child": (
            root["lists_235960"] and not middle["lists_235960"]),
        "production_discovery_on_live_values": "NO_ABORT",
        "live_child_published_as_paid": "App_235960" in live_offers,
        "live_price_state": live_price_state,
        "synthetic_price_context": "in-memory only; NOT a real Steam price",
        "synthetic_child_verified_base_appids":
            modeled_offers["App_235960"]["verified_base_appids"],
        "synthetic_child_parent_chains": actual_path,
        "real_discovery_subset_statistics": {
            key: actual_stats.get(key) for key in (
                "admitted_base_count", "parent_relation_lookups",
                "related_dlc_unique_ids", "dlc_price_lookups",
                "dlc_accepted_after_paid_gate", "relation_complete"
            )
        },
        "simulated_discovery_subset_statistics": {
            key: modeled_stats.get(key) for key in (
                "related_dlc_unique_ids", "dlc_accepted_after_paid_gate"
            )
        }
    }


def write(record):
    RESULT_FILE.write_text(
        json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8"
    )
    print("[dlc235960-pr416-live-smoke] "
          + json.dumps(record, ensure_ascii=False, sort_keys=True), flush=True)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as fd:
            fd.write("## PR #416 — App_235960 live Steam KZ parent test\n\n")
            fd.write(f"**{record['result']}** — {record['reason']}\n\n")
            fd.write(f"Source fix: \`{record['source_fix_commit']}\` "
                     f"; smoke head: \`{record['smoke_head_sha']}\`; "
                     f"UTC: {record['at_utc']}\n\n")
            fd.write(f"Real HTTP GET starts: {record['http_get_starts']}/6; "
                     f"targets: {', '.join(IDS)}; cc=kz, l=english.\n\n")
            ev = record.get("evidence") or {}
            for aid in IDS:
                item = (ev.get("fields") or {}).get(aid)
                if item:
                    fd.write(f"- App_{aid}: type={item['type']}, "
                             f"steam_appid={item['steam_appid']}, "
                             f"fullgame={item['fullgame_appid']}, "
                             f"lists235960={item['lists_235960']}, "
                             f"price={item['price_state']}\n")
            if ev:
                fd.write("\nProduction candidate logic on these *real* "
                         "relationships: " +
                         ev["production_discovery_on_live_values"] +
                         "; synthetic priced child path (in-memory only): \`" +
                         str(ev["synthetic_child_parent_chains"]) + "\`.\n\n")
            fd.write("**Bounded only:** root and middle lists intentionally "
                     "filtered to the three real targeted IDs for caller scope; "
                     "this does NOT test all eligible game roots, full production "
                     "collection, publishing or downstream pipelines.\n")


def main():
    getter = ExactKzGetter()
    record = {
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "source_fix_commit": "5b2d74aa4b750148bfd93ca847db93f60ba0ca59",
        "smoke_head_sha": os.environ.get("SMOKE_HEAD_SHA", "unavailable"),
        "queried_ids": list(IDS),
        "cc": "kz",
        "language": "english",
        "network_start_limit": MAX_STARTS,
        "http_get_starts": 0,
        "http_status_by_id": {},
        "result": "INCONCLUSIVE",
        "reason": "Network or validation incomplete",
        "evidence": {},
    }
    try:
        pacer = targeted._SharedAppdetailsPacer()
        diagnostics = targeted._AppdetailsDiagnostics()
        live = {
            aid: targeted.get_appdetails(
                aid, getter=getter, pacer=pacer, diagnostics=diagnostics
            )
            for aid in IDS
        }
        record["evidence"] = exercise_production(live)
        record["result"] = "PASS"
        record["reason"] = (
            "PR #416 source collector accepted live 2820->201310->235960 "
            "relationship within bounded subset without reciprocal middle list"
        )
    except (ValueError, AssertionError, RuntimeError) as err:
        record["result"] = "FAIL"
        record["reason"] = f"{type(err).__name__}: {str(err)[:230]}"
    except (requests.RequestException, OSError, Exception) as err:
        record["result"] = "INCONCLUSIVE"
        record["reason"] = f"{type(err).__name__}: {str(err)[:230]}"
    finally:
        record["http_get_starts"] = getter.starts
        record["http_status_by_id"] = getter.states
        write(record)
    return 0 if record["result"] == "PASS" else (1 if record["result"] == "FAIL" else 2)


if __name__ == "__main__":
    raise SystemExit(main())
