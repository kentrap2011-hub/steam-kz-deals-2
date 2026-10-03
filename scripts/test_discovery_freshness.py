from datetime import datetime, timezone

from discovery_freshness import (
    assess_discovery_freshness,
    require_fresh_discovery,
    require_store_snapshot_freshness,
)


SOURCE = '2026-10-02T20:20:00+00:00'
OBSERVED = datetime(2026, 10, 2, 20, 40, tzinfo=timezone.utc)


def docs(source=SOURCE, count=12):
    manifest = {
        'updated_at_utc': source,
        'complete': True,
        'source_has_known_gaps': False,
        'shortlist_items': count,
    }
    shortlist = {
        'source_updated_at_utc': source,
        'source_complete': True,
        'source_has_known_gaps': False,
        'item_count': count,
    }
    mailing = {
        'source_updated_at_utc': source,
        'source_complete': True,
        'manifest_complete': True,
        'item_count': count,
        'source_item_count': count,
    }
    return manifest, shortlist, mailing


def test_fresh_aligned_current_cycle_passes():
    result = assess_discovery_freshness(*docs(), OBSERVED)
    assert result['fresh'] is True
    assert result['candidate_universe_rebuilt_for_current_cycle'] is True
    assert result['source_binding']['source_chain_aligned'] is True


def test_stale_discovery_fresh_price_fails_closed():
    manifest, shortlist, mailing = docs('2026-09-23T23:12:47.031485+00:00')
    result = assess_discovery_freshness(
        manifest,
        shortlist,
        mailing,
        datetime(2026, 10, 1, 18, 15, tzinfo=timezone.utc),
    )
    assert result['fresh'] is False
    assert 'discovery_source_older_than_allowed' in result['stale_reasons']
    assert 'candidate_universe_not_rebuilt_for_current_production_cycle' in result['stale_reasons']
    try:
        require_fresh_discovery(
            manifest,
            shortlist,
            mailing,
            datetime(2026, 10, 1, 18, 15, tzinfo=timezone.utc),
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError('stale discovery must fail closed')


def test_price_refresh_never_substitutes_for_discovery_refresh():
    result = assess_discovery_freshness(*docs(), OBSERVED)
    assert result['price_refresh_can_substitute_for_discovery_refresh'] is False


def test_source_chain_mismatch_is_stale():
    manifest, shortlist, mailing = docs()
    shortlist['source_updated_at_utc'] = '2026-10-02T19:00:00+00:00'
    result = assess_discovery_freshness(manifest, shortlist, mailing, OBSERVED)
    assert result['fresh'] is False
    assert 'discovery_source_chain_mismatch' in result['stale_reasons']


def test_candidate_count_mismatch_is_stale():
    manifest, shortlist, mailing = docs()
    mailing['item_count'] = 11
    result = assess_discovery_freshness(manifest, shortlist, mailing, OBSERVED)
    assert result['fresh'] is False
    assert 'discovery_candidate_count_chain_mismatch' in result['stale_reasons']


def test_known_catalog_gap_is_not_authoritative_fresh_discovery():
    manifest, shortlist, mailing = docs()
    manifest['complete'] = False
    manifest['source_has_known_gaps'] = True
    result = assess_discovery_freshness(manifest, shortlist, mailing, OBSERVED)
    assert result['fresh'] is False
    assert 'discovery_source_incomplete_or_has_known_gaps' in result['stale_reasons']


def test_previous_local_cycle_fails_even_inside_age_limit():
    source = '2026-10-01T15:00:00+00:00'
    observed = datetime(2026, 10, 2, 0, 5, tzinfo=timezone.utc)
    result = assess_discovery_freshness(*docs(source), observed)
    assert result['discovery_age_hours_at_commercial_observation'] < 18
    assert result['fresh'] is False
    assert 'candidate_universe_not_rebuilt_for_current_production_cycle' in result['stale_reasons']


def test_store_snapshot_requires_exact_freshness_binding():
    result = assess_discovery_freshness(*docs(), OBSERVED)
    store = {
        'observed_at_utc': result['commercial_observed_at_utc'],
        'discovery_source_updated_at_utc': result['discovery_generated_at_utc'],
        'discovery_freshness': result,
    }
    assert require_store_snapshot_freshness(store)['fresh'] is True


def test_store_snapshot_rejects_price_only_legacy_shape():
    legacy = {
        'status': 'complete',
        'observed_at_utc': '2026-10-01T18:15:33.903961+00:00',
        'discovery_source_updated_at_utc': '2026-09-23T23:12:47.031485+00:00',
    }
    try:
        require_store_snapshot_freshness(legacy)
    except ValueError:
        pass
    else:
        raise AssertionError('legacy price-only snapshot must not publish as current')


def main():
    tests = [
        test_fresh_aligned_current_cycle_passes,
        test_stale_discovery_fresh_price_fails_closed,
        test_price_refresh_never_substitutes_for_discovery_refresh,
        test_source_chain_mismatch_is_stale,
        test_candidate_count_mismatch_is_stale,
        test_known_catalog_gap_is_not_authoritative_fresh_discovery,
        test_previous_local_cycle_fails_even_inside_age_limit,
        test_store_snapshot_requires_exact_freshness_binding,
        test_store_snapshot_rejects_price_only_legacy_shape,
    ]
    for test in tests:
        test()
        print(f'{test.__name__}: PASS')
    print(f'discovery freshness tests: {len(tests)}/{len(tests)} PASS')


if __name__ == '__main__':
    main()
