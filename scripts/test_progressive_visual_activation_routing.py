import progressive_visual_activation_routing as routing


def payload(source='S', count=719):
    return {
        'source_mailing_updated_at_utc': source,
        'progressive_candidate_count': count,
    }


def store(source='S', status='complete'):
    return {'status': status, 'discovery_source_updated_at_utc': source}


def family(source='S', status='complete'):
    return {'status': status, 'source_updated_at_utc': source}


def compatible_visual(source='S'):
    return {
        'source_mailing_updated_at_utc': source,
        'items': [
            {'id': 'A', 'analysis_state': 'analyzed_fit', 'analysis_tier': 1},
            {'id': 'B', 'analysis_state': 'analysis_incomplete', 'analysis_tier': 2},
            {'id': 'C', 'analysis_state': 'not_analyzed', 'analysis_tier': 3},
        ],
        'progressive_personalization': {
            'contract': 'PROGRESSIVE-PERSONALIZED-DEALS-V1',
            'phase': 'phase_b',
            'pass1_active': True,
            'pass2_active': False,
        },
        'processing_status': {
            'contract': 'PROGRESSIVE-PERSONALIZED-DEALS-V1',
            'phase': 'phase_b',
            'total_current_candidates': 4,
            'analyzed_success_count': 2,
            'analyzed_fit_count': 1,
            'analyzed_not_fit_count': 1,
            'analysis_incomplete_count': 1,
            'not_analyzed_count': 1,
            'normal_visible_count': 3,
            'pass1_active': True,
            'pass1_total_scope': 4,
            'pass1_attempted_count': 3,
            'pass1_remaining_count': 1,
            'pass2_active': False,
        },
        'production_contract': {
            'source_progressive_candidate_context_blob_sha': 'CTX',
            'progressive_personalization_contract_blob_sha': 'CONTRACT',
            'progressive_pass1_state_blob_sha': 'PASS1',
        },
    }


def classify(visual, *, source='S', count=719, context_count=719, store_source='S', family_source='S'):
    integrity = routing.source_integrity_ok(
        payload(source, count),
        store(store_source),
        family(family_source),
    )
    compatible, reason = routing.progressive_visual_compatible(
        payload=payload(source, count),
        store=store(store_source),
        family=family(family_source),
        visual=visual,
        progressive_context_count=context_count,
        progressive_context_blob='CTX',
        progressive_contract_blob='CONTRACT',
        pass1_state_blob='PASS1',
    )
    return integrity, compatible, reason


def main():
    # ROUTE-01: checkpoint shape — active 719-row progressive input + legacy 3-row visual.
    legacy = {
        'source_mailing_updated_at_utc': 'OLD',
        'items': [{'id': 'x'}, {'id': 'y'}, {'id': 'z'}],
        'production_contract': {},
    }
    integrity, compatible, reason = classify(legacy)
    assert integrity is True
    assert compatible is False
    assert reason in {'visual_progressive_source_mismatch', 'progressive_state_block_missing'}

    # ROUTE-02: already-compatible progressive visual remains eligible for bounded
    # commercial refresh; store/history commercial blob changes are intentionally
    # outside this compatibility predicate.
    integrity, compatible, reason = classify(compatible_visual())
    assert integrity is True
    assert compatible is True
    assert reason == 'compatible_progressive_visual'

    # ROUTE-03: missing processing/state block cannot be commercial-only compatible.
    missing = compatible_visual()
    missing.pop('processing_status')
    integrity, compatible, reason = classify(missing)
    assert integrity is True
    assert compatible is False
    assert reason == 'progressive_processing_status_invalid'

    # Stale progressive provenance also forces a full rebuild.
    stale = compatible_visual()
    stale['production_contract']['source_progressive_candidate_context_blob_sha'] = 'OLD'
    integrity, compatible, reason = classify(stale)
    assert integrity is True
    assert compatible is False
    assert reason == 'progressive_context_provenance_mismatch'


    # Phase B semantic progress must force a full rebuild when the accepted
    # PASS 1 state blob changes, even if commercial lineage is otherwise fresh.
    stale_pass1 = compatible_visual()
    stale_pass1['production_contract']['progressive_pass1_state_blob_sha'] = 'OLD-PASS1'
    integrity, compatible, reason = classify(stale_pass1)
    assert integrity is True
    assert compatible is False
    assert reason == 'progressive_pass1_state_provenance_mismatch'

    # ROUTE-04: invalid source identity remains fail-closed and must never be
    # treated as a compatible bounded-refresh candidate.
    integrity, compatible, reason = classify(compatible_visual(), store_source='OTHER')
    assert integrity is False
    assert compatible is False
    assert reason == 'source_integrity_invalid'

    print('progressive visual activation routing regression: ok')


if __name__ == '__main__':
    main()
