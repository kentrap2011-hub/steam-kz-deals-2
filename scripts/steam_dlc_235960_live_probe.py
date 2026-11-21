#!/usr/bin/env python3
"""Read-only, one-off PR diagnosis for Steam KZ App_235960.

Exactly three target identities; at most six physical HTTP GET starts in all,
including appdetails retries. Production policy, source code and data are untouched.
A three-ID sample MUST NOT report full production relation PASS.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import steam_targeted_paid_lanes as targeted

IDS = ("2820", "201310", "235960")
MAX_PHYSICAL_STARTS = 6
ARTIFACT = Path("dlc235960-live-diagnostic.json")


def app_id(value):
    """Small, bounded display helper; does not coerce invalid relations to valid ones."""
    return str(value)[:100] if value is not None else None


def summarize(appid, data):
    if not isinstance(data, dict):
        return {"requested_appid": appid, "metadata": "missing"}
    raw_dlc = data.get("dlc")
    fg = data.get("fullgame")
    price = data.get("price_overview", "<absent>")
    if price == "<absent>":
        price_state = "absent"
    elif price is None:
        price_state = "null"
    elif price == {}:
        price_state = "empty"
    elif isinstance(price, dict):
        price_state = "present"
    else:
        price_state = "malformed"
    out = {
        "requested_appid": appid,
        "data_type": app_id(data.get("type")),
        "data_steam_appid": app_id(data.get("steam_appid")),
        "fullgame_appid": app_id(fg.get("appid")) if isinstance(fg, dict) else None,
        "fullgame_shape": ("object" if isinstance(fg, dict)
                           else "absent" if fg is None else "invalid"),
        "dlc_shape": ("array" if isinstance(raw_dlc, list)
                      else "absent" if raw_dlc is None else "invalid"),
        "dlc_count": len(raw_dlc) if isinstance(raw_dlc, list) else None,
        "lists_201310": (201310 in raw_dlc or "201310" in raw_dlc)
                           if isinstance(raw_dlc, list) else None,
        "lists_235960": (235960 in raw_dlc or "235960" in raw_dlc)
                           if isinstance(raw_dlc, list) else None,
        "price_state": price_state if appid == "235960" else "not_inspected",
    }
    if appid == "235960" and isinstance(price, dict) and price:
        out["price_currency"] = app_id(price.get("currency"))
        out["price_final_minor"] = price.get("final") if type(price.get("final")) is int else None
        out["price_discount_percent"] = (price.get("discount_percent")
                                         if type(price.get("discount_percent")) is int else None)
    return out


class BoundedGetter:
    def __init__(self):
        self.starts = 0
        self.snapshots = {}

    def __call__(self, url, **kwargs):
        params = kwargs.get("params") or {}
        appid = str(params.get("appids"))
        if url != targeted.APPDETAILS_URL or appid not in IDS:
            raise RuntimeError("INCONCLUSIVE: unexpected appdetails target or URL")
        if params.get("cc") != "kz" or params.get("l") != "english":
            raise RuntimeError("INCONCLUSIVE: KZ/English request parameters changed")
        if self.starts >= MAX_PHYSICAL_STARTS:
            raise RuntimeError("INCONCLUSIVE: hard physical GET budget exhausted")
        self.starts += 1
        response = requests.get(url, **kwargs)
        if response.status_code == 200:
            try:
                entry = response.json().get(appid)
                data = entry.get("data") if isinstance(entry, dict) and entry.get("success") is True else None
                self.snapshots[appid] = summarize(appid, data)
            except (ValueError, TypeError, AttributeError):
                self.snapshots[appid] = {
                    "requested_appid": appid, "metadata": "invalid JSON or entry"
                }
        return response


def evaluate(values):
    root = values["2820"]
    mid = values["201310"]
    child = values["235960"]
    root_list = targeted._dlc_ids(root, "2820")
    middle_list = targeted._dlc_ids(mid, "201310")
    declared_parent = targeted._fullgame_id(child, "235960")
    mid_parent = targeted._fullgame_id(mid, "201310")
    root_middle = "201310" in root_list
    root_child = "235960" in root_list
    middle_child = "235960" in middle_list
    mid_valid = mid.get("type") in ("dlc", "game") and mid_parent in (None, "2820")
    exact_chain = (root_middle and middle_child and declared_parent == "201310"
                   and mid_valid and root.get("type") == "game"
                   and child.get("type") == "dlc")
    detail = {
        "root_2820_lists_201310": root_middle,
        "root_2820_lists_235960": root_child,
        "intermediate_201310_lists_235960": middle_child,
        "intermediate_201310_fullgame_appid": mid_parent,
        "child_235960_fullgame_appid": declared_parent,
        "exact_2820_to_201310_to_235960_chain_valid": exact_chain,
        "other_origin_roots_proven": False,
    }
    if (root_child and child.get("type") == "dlc"
            and declared_parent == "201310"
            and not (root_middle and middle_child and mid_valid)):
        return "FAIL", "Exact parent path claimed by root 2820 is broken in this live sample", detail
    if exact_chain:
        return ("INCONCLUSIVE",
                "Three-ID chain is valid for root 2820; other admitted origin roots are unknown",
                detail)
    return ("INCONCLUSIVE",
            "Three-ID sample does not prove the original contradiction or all origin roots",
            detail)


def write_evidence(record):
    ARTIFACT.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    brief = {
        "result": record["result"],
        "reason": record["reason"],
        "checked": list(IDS),
        "physical_get_starts": record["physical_get_starts"],
        "relations": record.get("relations"),
    }
    print("[dlc235960-live-probe] " + json.dumps(brief, ensure_ascii=False, sort_keys=True),
          flush=True)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write("## Steam KZ App_235960 — bounded diagnostic only\n\n")
            handle.write(f"**{record['result']}** — {record['reason']}\n\n")
            handle.write(f"UTC: {record['checked_at_utc']}; PR head: {record['pr_head_sha']}; "
                         f"physical GET starts: {record['physical_get_starts']}/6\n\n")
            handle.write("| Requested | data.type | data.steam_appid | fullgame.appid | "
                         "lists 201310 | lists 235960 | Price state |\n")
            handle.write("|---|---|---|---|---|---|---|\n")
            for aid in IDS:
                s = record["fields"].get(aid, {})
                handle.write("| " + " | ".join(str(s.get(key, "?")) for key in (
                    "requested_appid", "data_type", "data_steam_appid",
                    "fullgame_appid", "lists_201310", "lists_235960",
                    "price_state")) + " |\n")
            handle.write("\n**Never production-wide PASS:** other eligible origin roots "
                         "and the historical API body are not available from three GETs.\n")


def main():
    pr_sha = os.environ.get("DLC235960_PR_HEAD", "unavailable")
    getter = BoundedGetter()
    pacer = targeted._SharedAppdetailsPacer()
    diagnostics = targeted._AppdetailsDiagnostics()
    record = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "pr_head_sha": pr_sha,
        "requested_ids": list(IDS),
        "physical_get_limit": MAX_PHYSICAL_STARTS,
        "physical_get_starts": 0,
        "fields": {},
        "relations": None,
        "result": "INCONCLUSIVE",
        "reason": "Not all requested responses verified",
        "limitations": [
            "Current 2026 KZ API is not an archival copy of the failed collector run",
            "Only three AppIDs sampled; no reconstruction of all admitted origin roots",
            "No production writes, no new schedule, no full collector call",
        ],
    }
    values = {}
    try:
        for aid in IDS:
            values[aid] = targeted.get_appdetails(
                aid, getter=getter, pacer=pacer, diagnostics=diagnostics
            )
        result, reason, relations = evaluate(values)
        record.update(result=result, reason=reason, relations=relations)
    except Exception as exc:
        record.update(result="INCONCLUSIVE",
                      reason=f"{type(exc).__name__}: {str(exc)[:240]}")
    finally:
        record["physical_get_starts"] = getter.starts
        record["fields"] = getter.snapshots
        write_evidence(record)
    return 1 if record["result"] == "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
