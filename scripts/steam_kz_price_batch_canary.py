#!/usr/bin/env python3
"""Once-only 30-ID Steam KZ price batch parity trial, never a production collector."""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOTS = [2800, 2820, 461950, 3981100]
CHILDREN = [
    16860, 201310, 201805, 235960, 324332, 361843, 425360,
    488140, 662351, 844340, 975360, 1087424, 1162208,
    1238761, 1436772, 1647962, 1697640, 1788600, 1909130,
    2112232, 2307470, 2560300, 2819760, 3265830, 3845330, 5369430,
]
IDS = ROOTS + CHILDREN
assert len(IDS) == len(set(IDS)) == 30
URL = "https://store.steampowered.com/api/appdetails"
last_start = None
starts = 0
requests_log = []

def fetch(params, label):
    global last_start, starts
    if starts >= 31:
        raise RuntimeError("31 physical request start budget exceeded")
    if last_start is not None:
        time.sleep(max(0, 0.9 - (time.monotonic() - last_start)))
    start = last_start = time.monotonic()
    starts += 1
    req = urllib.request.Request(
        URL + "?" + urllib.parse.urlencode(params, safe=","),
        headers={"User-Agent": "steam-kz-deals/1.0", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            status = resp.status
            body = resp.read(2000001)
    except urllib.error.HTTPError as err:
        status, body = err.code, err.read(2000001)
    except Exception as err:
        status, body = type(err).__name__, b""
    entry = {"label": label, "status": status, "seconds": round(time.monotonic()-start, 3)}
    requests_log.append(entry)
    print("[price-canary-get] " + json.dumps(entry), flush=True)
    if status != 200 or len(body) > 2000000:
        return None, status
    try:
        return json.loads(body), status
    except (ValueError, UnicodeError):
        return None, "INVALID_JSON"

def normalize(raw, ident):
    if not isinstance(raw, dict) or str(ident) not in raw:
        return {"state": "missing"}
    item = raw[str(ident)]
    if not isinstance(item, dict) or type(item.get("success")) is not bool:
        return {"state": "invalid_success"}
    if item["success"] is False:
        return {"state": "not_found"}
    data = item.get("data")
    if not isinstance(data, dict):
        return {"state": "no_data"}
    if data.get("price_overview") is None:
        return {"state": "unpriced"}
    price = data["price_overview"]
    if not isinstance(price, dict):
        return {"state": "invalid_price"}
    vals = {}
    for field in ("currency", "initial", "final", "discount_percent"):
        val = price.get(field)
        if type(val) is not (str if field == "currency" else int):
            return {"state": "invalid_field", "field": field}
        vals[field] = val
    return {"state": "priced", **vals}

def report(result, start):
    result.update({
        "source_run": 42601207552,
        "source_sha": "9b4b0668438c20b39a48302acd27ddb3250ff41c",
        "physical_request_starts": starts, "max_physical_requests": 31,
        "elapsed_seconds": round(time.monotonic()-start, 3),
        "utc": datetime.now(timezone.utc).isoformat(),
        "get_logs": requests_log,
    })
    print("[price-canary-result] " + json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a", encoding="utf-8") as out:
            out.write("## Steam KZ 30-ID batch canary\n\n")
            for k in ("verdict", "matched", "priced_singles", "kzt_singles",
                      "physical_request_starts", "singles_seconds",
                      "batch_seconds", "elapsed_seconds", "batch_status"):
                if k in result:
                    out.write(f"- **{k}:** {result[k]}\n")
            out.write("\nThis is **price-only parity**, not proof of complete DLC parentage, coverage or a safe production switch.\n")

def main():
    begin = time.monotonic()
    print("[price-canary-start] "+json.dumps({
        "appids": IDS, "region": "kz", "source_run": 42601207552,
        "scope": "30 full individual GETs + 1 batched filtered GET",
        "max_requests": 31, "spacing": 0.9, "timeout_each": 12,
        "retries": 0,
    }), flush=True)
    singles = {}
    for ident in IDS:
        data, status = fetch({"appids": str(ident), "cc": "kz", "l": "english"},
                             f"single_{ident}")
        if data is None:
            report({"verdict": "BLOCKED_SINGLE_GET", "failed_id": ident, "status": status}, begin)
            return
        singles[ident] = normalize(data, ident)
    singles_seconds = round(time.monotonic()-begin, 3)
    data, status = fetch({"appids": ",".join(map(str, IDS)), "cc": "kz",
                          "l": "english", "filters": "price_overview"}, "batch_30")
    if data is None:
        report({"verdict": "BATCH_NOT_AVAILABLE", "batch_status": status,
                "singles_seconds": singles_seconds,
                "batch_seconds": requests_log[-1]["seconds"]}, begin)
        return
    batches = {ident: normalize(data, ident) for ident in IDS}
    differences = [{"appid": i, "single": singles[i], "batch": batches[i]}
                   for i in IDS if singles[i] != batches[i]]
    priced = sum(x["state"] == "priced" for x in singles.values())
    kzt = sum(x.get("currency") == "KZT" for x in singles.values())
    verdict = ("PRICE_PARITY_30_ONLY" if not differences and priced and kzt
               else "ALL_UNPRICED_INCONCLUSIVE" if not differences
               else "PRICE_OR_RESPONSE_MISMATCH")
    report({"verdict": verdict, "matched": 30-len(differences),
            "priced_singles": priced, "kzt_singles": kzt,
            "mismatches": differences, "singles_seconds": singles_seconds,
            "batch_seconds": requests_log[-1]["seconds"],
            "batch_status": status,
            "batch_keys": len(data) if isinstance(data, dict) else None}, begin)

if __name__ == "__main__":
    main()
