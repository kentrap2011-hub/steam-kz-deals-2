"""Regression: producer caps only the already ranked paid publication, never Deep."""
import copy
import json
import tempfile
from pathlib import Path

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

    # CAP-06: bound full source funnel only; stale or incoherent manifests
    # must never be misrepresented as a current Statistics denominator.
    source = '2026-10-26T12:00:00+00:00'
    valid = {
        'complete': True,
        'country_code': 'kz',
        'updated_at_utc': source,
        'filtering_funnel': {
            'source_reported_rows': 100,
            'source_rows_seen': 100,
            'parsed_rows': 100,
            'eligible_rows_before_partition_dedupe': 70,
            'removed_non_paid_or_missing_price': 1,
            'removed_discount_below_50': 20,
            'removed_price_above_4500': 3,
            'removed_obvious_extras': 4,
            'removed_software_only': 2,
        },
        'search_partitions': [
            {'id': 'games', 'rows_seen': 60, 'eligible_rows_after_local_gate': 42},
            {'id': 'dlc', 'rows_seen': 40, 'eligible_rows_after_local_gate': 28},
        ],
    }
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / 'manifest.json'
        path.write_text(json.dumps(valid), encoding='utf-8')
        snapshot = {'source_mailing_updated_at_utc': source}
        stats = producer.bound_paid_source_funnel(snapshot, path)
        assert stats['metrics']['paid_source_rows_seen'] == 100
        assert len(stats['partitions']) == 2
        assert producer.bound_paid_source_funnel(
            {'source_mailing_updated_at_utc': 'old'}, path
        ) is None
        invalid = copy.deepcopy(valid)
        invalid['search_partitions'][1]['rows_seen'] = 39
        path.write_text(json.dumps(invalid), encoding='utf-8')
        try:
            producer.bound_paid_source_funnel(snapshot, path)
        except ValueError:
            pass
        else:
            raise AssertionError('source funnel accepted inconsistent partition')

    # CAP-07: freebies are not part of paid items/cap and remain unchanged.
    giveaways = {'state': 'ready', 'offers': [{'provider': 'Epic'}]}
    source = {'items': [game(i) for i in range(1, 105)],
              'giveaways': giveaways, 'processing_status': {}}
    producer.cap_visible_paid_offers(source, full_ranked_scope=True)
    assert source['giveaways'] is giveaways
    print('visible paid offer cap CAP-01..07: ok')


if __name__ == '__main__':
    main()
