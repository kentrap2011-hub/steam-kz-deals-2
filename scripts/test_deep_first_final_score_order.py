import copy
import json
from pathlib import Path

import priority_ranking
import progressive_personalization as progressive


STAGES = ['deep_fit', 'fast_fit', 'analysis_incomplete', 'not_analyzed']


def staged(fid, stage, score, *, urgency=2, title=None):
    row = {
        'id': fid,
        'title': title or fid,
        'ranking_stage': stage,
        'ranking_stage_rank': STAGES.index(stage) + 1,
        'sale_expiry_urgency_rank': urgency,
    }
    if stage in {'deep_fit', 'fast_fit'}:
        row['total_score'] = score
    else:
        row['deterministic_purchase_score'] = score
    return row


def base_fit(fid, source):
    semantic = 'progressive_pass2' if source == 'deep' else 'progressive_pass1'
    row = {
        'id': fid,
        'title': fid,
        'analysis_state': 'analyzed_fit',
        'analysis_tier': 1,
        'analysis_semantic_source': semantic,
        'effective_analysis_source': source,
        'fit': 'strong',
        'source_fit': 'strong',
        'risk_level': 'low',
        'risk_codes': [],
        'wishlist': False,
        'history_quality': 'record',
        'original_price_rub': 1000,
        'current_price_rub': 300,
        'discount_percent': 70,
        'sale_end_utc': '2026-10-08T07:00:00+00:00',
        'direct_user_evidence': {'level': 'none'},
        'duration_preference_band': 'unknown',
        'estimated_duration_hours': None,
        'practical': {
            'modern_windows_friction': 'unknown',
            'steam_achievements': True,
            'achievement_quality': 3,
        },
        'fast_stage_state': 'completed' if source == 'fast' else 'not_started',
        'fast_stage_outcome': 'fit' if source == 'fast' else None,
        'deep_stage_state': 'completed' if source == 'deep' else 'waiting_for_dossier',
        'deep_stage_outcome': 'fit' if source == 'deep' else None,
    }
    return row


def base_unresolved(fid, state, *, price=300, original=1000):
    assert state in {'analysis_incomplete', 'not_analyzed'}
    return {
        'id': fid,
        'title': fid,
        'analysis_state': state,
        'analysis_tier': 2 if state == 'analysis_incomplete' else 3,
        'analysis_semantic_source': None,
        'effective_analysis_source': 'none',
        'risk_level': 'low',
        'risk_codes': [],
        'wishlist': False,
        'history_quality': 'record',
        'original_price_rub': original,
        'current_price_rub': price,
        'discount_percent': 70,
        'sale_end_utc': '2026-10-08T07:00:00+00:00',
        'practical': {'modern_windows_friction': 'unknown', 'steam_achievements': None},
    }


def score_bytes(row):
    keys = (
        'total_score', 'personal_score', 'purchase_score', 'purchase_route',
        'package_value_points', 'savings_rub', 'score_breakdown',
    )
    return json.dumps(
        {key: row.get(key) for key in keys},
        ensure_ascii=False,
        sort_keys=True,
        separators=(',', ':'),
    )


def main():
    contract = progressive.load_contract()
    policy = priority_ranking.load_final_policy()
    assert (contract.get('ranking_stage_model') or {}).get('precedence') == STAGES
    assert policy['automatic_final_priority_order'] == [
        'ranking_stage_asc', 'stage_score_desc', 'title_asc'
    ]
    assert policy['explicit_urgency_view_order'] == [
        'ranking_stage_asc', 'sale_expiry_urgency_asc', 'stage_score_desc', 'title_asc'
    ]

    # 1. Deep 60 outranks Fast 99 because stage precedes score.
    assert sorted(
        [staged('fast99', 'fast_fit', 99), staged('deep60', 'deep_fit', 60)],
        key=progressive._default_ranking_key,
    )[0]['id'] == 'deep60'

    # 2. Inside Deep, higher final score wins.
    assert sorted(
        [staged('deep60', 'deep_fit', 60), staged('deep70', 'deep_fit', 70)],
        key=progressive._default_ranking_key,
    )[0]['id'] == 'deep70'

    # 3. Inside Fast, higher final score wins.
    assert sorted(
        [staged('fast80', 'fast_fit', 80), staged('fast90', 'fast_fit', 90)],
        key=progressive._default_ranking_key,
    )[0]['id'] == 'fast90'

    # 4. Deterministic title/id tie-break remains stable.
    tied = sorted(
        [staged('b-id', 'deep_fit', 70, title='Same'), staged('a-id', 'deep_fit', 70, title='Same')],
        key=progressive._default_ranking_key,
    )
    assert [row['id'] for row in tied] == ['a-id', 'b-id']

    # 5-7. Valid Fast stays Fast when Deep is absent, waiting, incomplete or errored.
    for deep_state in ('not_started', 'waiting_for_dossier', 'incomplete_or_recovery'):
        row = base_fit(f'fast-{deep_state}', 'fast')
        row['deep_stage_state'] = deep_state
        row['deep_stage_outcome'] = None
        progressive.stamp_ranking_stage(row)
        assert row['ranking_stage'] == 'fast_fit'

    # 8. A stale/historical-looking Deep field cannot grant Deep priority when
    # current effective authority is still Fast.
    stale = base_fit('stale-deep', 'fast')
    stale['deep_stage_state'] = 'completed'
    stale['deep_stage_outcome'] = 'fit'
    progressive.stamp_ranking_stage(stale)
    assert stale['ranking_stage'] == 'fast_fit'

    # 9. PPD-012 reconciled current Deep presents as current authoritative Deep
    # through the same effective source and receives Deep stage.
    reconciled = base_fit('ppd012-current-deep', 'deep')
    reconciled['analysis_resolution_pass'] = 'pass2'
    progressive.stamp_ranking_stage(reconciled)
    assert reconciled['ranking_stage'] == 'deep_fit'

    # Existing exact-compatible reusable cache is provisional/Fast-equivalent,
    # never Deep.
    cache = base_fit('compatible-cache', 'fast')
    cache['effective_analysis_source'] = 'none'
    cache['analysis_semantic_source'] = 'compatible_cache'
    progressive.stamp_ranking_stage(cache)
    assert cache['ranking_stage'] == 'fast_fit'

    # 10-11. Unresolved and not-analyzed cannot outrank completed Fast/Deep even
    # with a much larger purchase-only score.
    rows = [
        staged('unresolved100', 'analysis_incomplete', 100),
        staged('not100', 'not_analyzed', 100),
        staged('fast1', 'fast_fit', 1),
        staged('deep0', 'deep_fit', 0),
    ]
    assert [r['id'] for r in sorted(rows, key=progressive._default_ranking_key)] == [
        'deep0', 'fast1', 'unresolved100', 'not100'
    ]

    # 12. Purchase-only score still orders cards inside the same unresolved stage.
    assert sorted(
        [staged('u10', 'analysis_incomplete', 10), staged('u40', 'analysis_incomplete', 40)],
        key=progressive._default_ranking_key,
    )[0]['id'] == 'u40'

    # 13. Default order ignores urgency inside a stage.
    default_urgency_pair = [
        staged('urgent-low', 'deep_fit', 40, urgency=0),
        staged('later-high', 'deep_fit', 90, urgency=2),
    ]
    assert [r['id'] for r in sorted(default_urgency_pair, key=progressive._default_ranking_key)] == [
        'later-high', 'urgent-low'
    ]

    # 14. Explicit urgency view is separately covered by the JS UI regression;
    # contract proves it is nested after ranking_stage and cannot cross it.
    urgency_view = policy['explicit_urgency_view_order']
    assert urgency_view.index('ranking_stage_asc') < urgency_view.index('sale_expiry_urgency_asc')

    # 15. Score bytes are unchanged by the new stage wrapper: the exact same V2
    # scorer is used independently inside Deep and Fast.
    source = base_fit('score-stability', 'deep')
    direct = copy.deepcopy(source)
    priority_ranking.apply_final_priority_order([direct])
    progressive_row = copy.deepcopy(source)
    ranked, returned_order = progressive.apply_progressive_order([progressive_row])
    assert returned_order == ['ranking_stage_asc', 'stage_score_desc', 'title_asc']
    assert score_bytes(ranked[0]) == score_bytes(direct)

    # Real integration: Deep and Fast receive canonical global priority_rank and
    # unresolved rows keep purchase-only scoring without total_score.
    integration = [
        base_fit('fast-real', 'fast'),
        base_fit('deep-real', 'deep'),
        base_unresolved('incomplete-real', 'analysis_incomplete', price=10, original=5000),
        base_unresolved('not-real', 'not_analyzed', price=5, original=6000),
    ]
    ordered, _ = progressive.apply_progressive_order(integration)
    assert [r['ranking_stage'] for r in ordered] == STAGES
    assert [r['priority_rank'] for r in ordered] == [1, 2, 3, 4]
    assert 'total_score' not in ordered[2] and 'total_score' not in ordered[3]

    # 16. UI default queue consumes producer-owned canonical priority_rank and
    # user-facing cursor is a feed position, not "Приоритет".
    ui_source = Path('web/progressive-personalization-ui.js').read_text(encoding='utf-8')
    app_source = Path('web/app.js').read_text(encoding='utf-8')
    assert 'canonicalRank(a)-canonicalRank(b)' in ui_source
    assert 'Позиция в ленте:' in app_source
    assert 'Приоритет: ${pos+1}' not in app_source

    # 17. Explicit manual end remains absolute after automatic/view sorting.
    assert "if(r.manual_end_at)manual.push(g.id);else normal.push(g.id);" in app_source
    assert "return [...normal,...manual];" in app_source
    assert "r.manual_end_at=Date.now();" in app_source

    # 18. Concrete reported regression: MY HERO Deep 67.1 must outrank KOF Fast
    # 68.0 even though the Fast score is numerically higher.
    kof = staged('game:1498570', 'fast_fit', 68.0, title='THE KING OF FIGHTERS XV')
    my_hero = staged('my-hero', 'deep_fit', 67.1, title="MY HERO ONE'S JUSTICE 2")
    concrete = sorted([kof, my_hero], key=progressive._default_ranking_key)
    assert [r['title'] for r in concrete] == ["MY HERO ONE'S JUSTICE 2", 'THE KING OF FIGHTERS XV']

    print('DEEP_FIRST_FINAL_SCORE_ORDER=PASS')


if __name__ == '__main__':
    main()
