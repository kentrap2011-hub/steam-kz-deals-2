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

    caps = [3000, 4000, 4500, 5000, 6000]
    cap_results = {}
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
        if summary["total_count"] is None or summary["total_count"] <= 0:
            raise SystemExit(f"cap {cap}: missing/empty total_count")
        if (
            summary["max_price_kzt"] is None
            or summary["max_price_kzt"] > cap
            or summary["min_price_kzt"] <= 0
        ):
            raise SystemExit(
                f"cap {cap}: returned price outside paid 0 < price <= cap"
            )

    totals = [cap_results[str(cap)]["total_count"] for cap in caps]
    if any(totals[i] > totals[i + 1] for i in range(len(totals) - 1)):
        raise SystemExit(f"nested maxprice totals are non-monotonic: {totals}")

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
        if summary["total_count"] != cap_results["4500"]["total_count"]:
            raise SystemExit(
                "same maxprice=4500 produced sort-dependent total_count: "
                f"{sort_results}"
            )
        if summary["max_price_kzt"] is None or summary["max_price_kzt"] > 4500:
            raise SystemExit(
                f"maxprice=4500 leaked over-cap row under {sort_by}"
            )

    capped_total = cap_results["4500"]["total_count"]
    page_size = core["PAGE_SIZE"]
    boundary_start = max(0, ((capped_total - 1) // page_size) * page_size)
    starts = [
        max(0, boundary_start - page_size),
        boundary_start,
        boundary_start + page_size,
    ]
    boundary_pages = []
    for start in starts:
        data = core["get_page"](
            start,
            "Price_ASC",
            category1=category1,
            hidef2p=True,
        )
        summary = summarize(core, data)
        summary["start"] = start
        boundary_pages.append(summary)

    boundary_prices = [
        price
        for page in boundary_pages
        for price in page["prices_kzt"]
    ]
    nonmonotonic_pairs = [
        {
            "index": index,
            "left": boundary_prices[index],
            "right": boundary_prices[index + 1],
        }
        for index in range(len(boundary_prices) - 1)
        if boundary_prices[index] > boundary_prices[index + 1]
    ]

    evidence = {
        "probe": "STEAM-KZ-MAXPRICE-BOUNDED-LIVE-PROBE-V1",
        "country_code": "kz",
        "category1": category1,
        "hidef2p": True,
        "caps_price_desc": cap_results,
        "maxprice_4500_sort_checks": sort_results,
        "uncapped_price_asc_boundary_start": boundary_start,
        "uncapped_price_asc_boundary_pages": boundary_pages,
        "uncapped_price_asc_nonmonotonic_pairs": nonmonotonic_pairs,
        "logical_requests": len(caps) + 3 + len(starts),
    }
    print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
