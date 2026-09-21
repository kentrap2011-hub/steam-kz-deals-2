import json
import tempfile
from pathlib import Path

import build_daily_visual_payload as daily


def offer(key, sale_end, price=100):
    return {
        'key': key,
        'title': key,
        'current_price_rub': price,
        'original_price_rub': price * 2,
        'discount_percent': 50,
        'sale_end_utc': sale_end,
        'steam_url': f'steam://store/{key}',
        'web_url': f'https://store.steampowered.com/app/{key}/',
    }


def game(family_id, state, tier, sale_end, *, personalized=False):
    row = {
        'id': family_id,
        'analysis_state': state,
        'analysis_tier': tier,
        'title': family_id,
        'offers': [offer(family_id, sale_end)],
        'total_score': 91 if personalized else None,
        'why_fit': ['supported fit reason'] if personalized else ['must be stripped'],
        'risks': ['supported fit risk'] if personalized else ['must be stripped'],
        'fit': 'strong' if personalized else 'stale-fit',
    }
    return row


def main():
    future = '2099-01-01T00:00:00+00:00'
    past = '2000-01-01T00:00:00+00:00'

    ready = {
        'items': [
            game('not-analyzed', 'not_analyzed', 3, future),
            game('incomplete', 'analysis_incomplete', 2, future),
            game('expired-unresolved', 'not_analyzed', 3, past),
            game('fit', 'analyzed_fit', 1, future, personalized=True),
        ]
    }
    context = {
        family_id: {'purchase': {'key': family_id}}
        for family_id in ['not-analyzed', 'incomplete', 'expired-unresolved', 'fit']
    }

    original_history = daily.HISTORY_SNAPSHOT
    try:
        with tempfile.TemporaryDirectory() as tmp:
            history = Path(tmp) / 'history.json'
            history.write_text(json.dumps({
                'entries': {
                    'not-analyzed': {'history_quality': 'complete', 'historical_min_kzt': 500},
                    'incomplete': {'history_quality': 'complete', 'historical_min_kzt': 600},
                    'expired-unresolved': {'history_quality': 'complete', 'historical_min_kzt': 700},
                    'fit': {'history_quality': 'complete', 'historical_min_kzt': 800},
                }
            }), encoding='utf-8')
            daily.HISTORY_SNAPSHOT = history
            result = daily.enrich_history_and_remove_expired(
                ready,
                context,
                {'fx_binding': {'kzt_per_rub': 5}},
            )
    finally:
        daily.HISTORY_SNAPSHOT = original_history

    by_id = {row['id']: row for row in result['items']}

    # ROW-01 / ROW-02: unresolved visible states survive while the offer is active.
    assert 'not-analyzed' in by_id
    assert 'incomplete' in by_id
    assert by_id['not-analyzed']['analysis_state'] == 'not_analyzed'
    assert by_id['not-analyzed']['analysis_tier'] == 3
    assert by_id['incomplete']['analysis_state'] == 'analysis_incomplete'
    assert by_id['incomplete']['analysis_tier'] == 2

    # ROW-03: unsupported personalized fields remain stripped on unresolved rows.
    for family_id in ['not-analyzed', 'incomplete']:
        row = by_id[family_id]
        for field in ['fit', 'total_score', 'why_fit', 'risks']:
            assert field not in row, (family_id, field, row.get(field))

    # Deterministic history data is still applied to unresolved rows.
    assert by_id['not-analyzed']['history_quality'] == 'complete'
    assert by_id['not-analyzed']['historical_minimum_rub'] == 100
    assert by_id['incomplete']['historical_minimum_rub'] == 120

    # ROW-04: a truly expired unresolved offer is still removed.
    assert 'expired-unresolved' not in by_id
    assert result['expired_family_count_removed_at_build'] == 1
    assert result['expired_family_ids_removed_at_build'] == ['expired-unresolved']

    # ROW-05: analyzed-fit keeps its supported personalized fields and uses the
    # same deterministic history/expiry path as before.
    fit = by_id['fit']
    assert fit['fit'] == 'strong'
    assert fit['total_score'] == 91
    assert fit['why_fit'] == ['supported fit reason']
    assert fit['risks'] == ['supported fit risk']
    assert fit['history_quality'] == 'complete'
    assert fit['historical_minimum_rub'] == 160

    assert result['item_count'] == 3
    print('progressive unresolved row preservation regression: ok')


if __name__ == '__main__':
    main()
