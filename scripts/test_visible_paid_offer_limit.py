"""Regression: producer caps only the already ranked paid publication, never Deep."""
import copy

import build_final_visual_payload as producer


def game(index, *, stage='not_analyzed', discount=50, price=4500):
    return {
        'id': f'game:{index:03}',
        'title': f'Game {index:03}',
        'priority_rank': index,
        'analysis_state': 'analyzed_fit' if stage == 'deep_fit' else 'not_analyzed',
        'ranking_stage': stage,
        'ranking_stage_rank': 1 if stage == 'deep_fit' else 4,
        'discount_percent': discount,
        'current_price_kzt': price,
    }


def main():
    # CAP-01: no source/eligible truncation; only 100 current visual cards.
    full = [game(i, stage='deep_fit' if i <= 5 else 'not_analyzed')
            for i in range(1, 166)]
    before = copy.deepcopy(full)
    visual = {'items': full, 'processing_status': {'deep_total_current_coverage_target': 165}}
    result = producer.cap_visible_paid_offers(visual, full_ranked_scope=True)
    assert len(visual['items']) == visual['item_count'] == 100
    assert result['ranked_internal_count'] == 165
    assert result['hidden_below_visible_line_count'] == 65
    assert visual['items'][0]['id'] == 'game:001'
    assert visual['items'][-1]['id'] == 'game:100'
    assert full == before
    assert visual['processing_status']['deep_total_current_coverage_target'] == 165
    assert result['deep_scope_truncated'] is False

    # CAP-02: repeated commercial refresh keeps last full-scope counters.
    partial = {'items': [game(i) for i in range(1, 98)],
               'processing_status': copy.deepcopy(visual['processing_status'])}
    producer.cap_visible_paid_offers(partial, full_ranked_scope=False)
    assert partial['processing_status']['ranked_internal_paid_offer_count'] == 165
    assert partial['processing_status']['visible_paid_offer_count'] == 97

    # CAP-03: accepted positive Deep ranks above unresolved at publication
    # because the producer slices canonical priority_rank, never Steam order.
    changed = [game(i, stage='deep_fit' if i <= 6 else 'not_analyzed')
               for i in range(1, 166)]
    changed[5]['id'] = 'game:outside-prior-cut-now-Deep'
    renewed = {'items': changed, 'processing_status': {}}
    producer.cap_visible_paid_offers(renewed, full_ranked_scope=True)
    assert renewed['items'][5]['id'] == 'game:outside-prior-cut-now-Deep'

    # CAP-04: 49% and over-price paid rows must not be published.
    for bad in (game(1, discount=49), game(1, price=4501),
                {**game(1), 'current_price_kzt': None}):
        try:
            producer.cap_visible_paid_offers({'items': [bad]}, full_ranked_scope=True)
        except ValueError:
            pass
        else:
            raise AssertionError('paid visual cap accepted invalid sale')

    # CAP-05: never accept an unordered feed as canonical top-100.
    try:
        producer.cap_visible_paid_offers(
            {'items': [game(2), game(1)]}, full_ranked_scope=True
        )
    except ValueError:
        pass
    else:
        raise AssertionError('cap silently used Steam/unsorted first rows')

    # CAP-06: freebies are not part of paid items/cap and remain unchanged.
    giveaways = {'state': 'ready', 'offers': [{'provider': 'Epic'}]}
    source = {'items': [game(i) for i in range(1, 105)],
              'giveaways': giveaways, 'processing_status': {}}
    producer.cap_visible_paid_offers(source, full_ranked_scope=True)
    assert source['giveaways'] is giveaways
    print('visible paid offer cap CAP-01..06: ok')


if __name__ == '__main__':
    main()
