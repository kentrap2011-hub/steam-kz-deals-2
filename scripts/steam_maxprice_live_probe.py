import json

import steam_partial_publish_runner as runner


def summarize(core, data):
    items = runner.parse_probe_items(core, data)
    prices = [float(item["final_kzt"]) for item in items]
    return {
        "total_count": core["to_int"](data.get("total_count")),
        "row_count": len(items),
        "min_price_kzt": min(prices) if prices else None,
        "max_price_kzt": max(prices) if prices else None,
        "prices_kzt": prices,
        "keys": [item["key"] for item in items],
    }


def main():
    core = runner.load_core()
    games = next(
        partition for partition in core["SEARCH_PARTITIONS"]
        if partition["id"] == "games"
    )
    category1 = games["category1"]

    # Deliberately small ladder: enough to identify whether maxprice values are
    # interpreted in KZT without broad traversal.
    caps = [10, 20, 50, 100, 1000, 4500]
    cap_results = {}
    violations = []
    for cap in caps:
        data = core["get_page"](
            0,
            "Price_DESC",
            category1=category1,
            maxprice_kzt=cap,
            hidef2p=True,
        )
        summary = summarize(core, data)
        cap_results[str(cap)] = summary
        print(
            "LIVE_MAXPRICE_CAP",
            cap,
            json.dumps(summary, ensure_ascii=False, sort_keys=True),
            flush=True,
        )
        if summary["total_count"] is None or summary["total_count"] <= 0:
            violations.append(f"cap {cap}: missing/empty total_count")
        if summary["max_price_kzt"] is None or summary["min_price_kzt"] <= 0:
            violations.append(f"cap {cap}: missing/non-paid returned price")
        elif summary["max_price_kzt"] > cap:
            violations.append(
                f"cap {cap}: returned max {summary['max_price_kzt']} KZT > cap"
            )

    totals = [cap_results[str(cap)]["total_count"] for cap in caps]
    if any(totals[i] > totals[i + 1] for i in range(len(totals) - 1)):
        violations.append(f"nested maxprice totals are non-monotonic: {totals}")

    sort_results = {}
    for sort_by in ("Price_ASC", "Price_DESC", "Name_ASC"):
        data = core["get_page"](
            0,
            sort_by,
            category1=category1,
            maxprice_kzt=4500,
            hidef2p=True,
        )
        summary = summarize(core, data)
        sort_results[sort_by] = summary
        print(
            "LIVE_MAXPRICE_SORT",
            sort_by,
            json.dumps(summary, ensure_ascii=False, sort_keys=True),
            flush=True,
        )

    evidence = {
        "probe": "STEAM-KZ-MAXPRICE-BOUNDED-LIVE-PROBE-V2",
        "country_code": "kz",
        "category1": category1,
        "hidef2p": True,
        "caps_price_desc": cap_results,
        "maxprice_4500_sort_checks": sort_results,
        "logical_requests": len(caps) + len(sort_results),
        "violations": violations,
    }
    print(
        "LIVE_MAXPRICE_EVIDENCE",
        json.dumps(evidence, ensure_ascii=False, sort_keys=True),
        flush=True,
    )
    if violations:
        raise SystemExit("; ".join(violations))


if __name__ == "__main__":
    main()
