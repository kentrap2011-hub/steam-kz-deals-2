from __future__ import annotations

import json

import steam_partial_publish_runner as runner


def fetch(core, *, start, filter_value=None, sort_by=None):
    params = core['search_params'](
        start,
        sort_by or 'Name_ASC',
        category1=core['SEARCH_CATEGORY_TYPES']['games'],
        maxprice_kzt=core['PAID_MAX_PRICE_KZT'],
        hidef2p=True,
    )
    params['count'] = 100
    if filter_value is not None:
        params['filter'] = filter_value
    response = core['session'].get(core['URL'], params=params, timeout=40)
    response.raise_for_status()
    data = response.json()
    items = runner.parse_probe_items(core, data)
    discounts = [
        int(item['discount_percent'])
        for item in items
        if item.get('discount_percent') is not None
    ]
    return {
        'start': start,
        'row_count': len(items),
        'total_count': core['to_int'](data.get('total_count')),
        'discounts': discounts,
        'min_discount': min(discounts) if discounts else None,
        'max_discount': max(discounts) if discounts else None,
        'nonincreasing': all(
            discounts[i] >= discounts[i + 1]
            for i in range(len(discounts) - 1)
        ),
        'first_10': discounts[:10],
        'last_10': discounts[-10:],
    }


def main():
    core = runner.load_core()
    variants = [
        ('filter_discountdesc', 'discountdesc', 'Name_ASC'),
        ('sort_discount_desc', None, 'Discount_DESC'),
        ('sort_discounts_desc', None, 'Discounts_DESC'),
    ]
    evidence = {}
    for name, filter_value, sort_by in variants:
        pages = [
            fetch(
                core,
                start=start,
                filter_value=filter_value,
                sort_by=sort_by,
            )
            for start in (0, 100, 200)
        ]
        cross_page_nonincreasing = True
        prior_last = None
        for page in pages:
            if prior_last is not None and page['discounts']:
                cross_page_nonincreasing = (
                    cross_page_nonincreasing
                    and prior_last >= page['discounts'][0]
                )
            if page['discounts']:
                prior_last = page['discounts'][-1]
        evidence[name] = {
            'filter': filter_value,
            'sort_by': sort_by,
            'pages': pages,
            'cross_page_nonincreasing': cross_page_nonincreasing,
        }

    print(
        'STEAM_DISCOUNT_ORDER_BOUNDED_PROBE='
        + json.dumps(evidence, ensure_ascii=False, sort_keys=True),
        flush=True,
    )


if __name__ == '__main__':
    main()
