from __future__ import annotations

import json

import steam_partial_publish_runner as runner


def summarize(core, *, sort_by, extra_params):
    params = core['search_params'](
        0,
        sort_by,
        category1=core['SEARCH_CATEGORY_TYPES']['games'],
        maxprice_kzt=core['PAID_MAX_PRICE_KZT'],
        hidef2p=True,
    )
    params.update(extra_params)
    response = core['session'].get(
        core['URL'],
        params=params,
        timeout=40,
    )
    response.raise_for_status()
    data = response.json()
    items = runner.parse_probe_items(core, data)
    discounts = [
        int(item['discount_percent'])
        for item in items
        if item.get('discount_percent') is not None
    ]
    prices = [
        float(item['final_kzt'])
        for item in items
        if item.get('final_kzt') is not None
    ]
    return {
        'sort_by': sort_by,
        'extra_params': extra_params,
        'total_count': core['to_int'](data.get('total_count')),
        'row_count': len(items),
        'min_discount_percent': min(discounts) if discounts else None,
        'max_discount_percent': max(discounts) if discounts else None,
        'distinct_discount_percent': sorted(set(discounts)),
        'min_price_kzt': min(prices) if prices else None,
        'max_price_kzt': max(prices) if prices else None,
    }


def main():
    core = runner.load_core()
    probes = [
        ('baseline_name', 'Name_ASC', {}),
        ('baseline_price_desc', 'Price_DESC', {}),
        ('discounts_50_name', 'Name_ASC', {'discounts': 50}),
        ('discounts_50_price_desc', 'Price_DESC', {'discounts': 50}),
        ('discounts_70_name', 'Name_ASC', {'discounts': 70}),
        ('discounts_90_name', 'Name_ASC', {'discounts': 90}),
        ('min_discount_50_name', 'Name_ASC', {'min_discount': 50}),
        ('discount_50_name', 'Name_ASC', {'discount': 50}),
        ('min_discount_pct_50_name', 'Name_ASC', {'min_discount_pct': 50}),
    ]

    evidence = {}
    for name, sort_by, extra_params in probes:
        evidence[name] = summarize(
            core,
            sort_by=sort_by,
            extra_params=extra_params,
        )

    print(
        'STEAM_DISCOUNT_FILTER_BOUNDED_PROBE='
        + json.dumps(evidence, ensure_ascii=False, sort_keys=True),
        flush=True,
    )


if __name__ == '__main__':
    main()
