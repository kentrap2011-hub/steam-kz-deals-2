from pathlib import Path

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
            {
                'id': 'A', 'analysis_state': 'analyzed_fit', 'analysis_tier': 1,
                'fast_stage_state': 'completed', 'fast_stage_outcome': 'fit',
                'dossier_stage_state': 'accepted',
                'deep_stage_state': 'completed', 'deep_stage_outcome': 'fit',
                'deep_recovery_state': 'none',
                'effective_personalized_result_source': 'deep',
            },
            {
                'id': 'B', 'analysis_state': 'analysis_incomplete', 'analysis_tier': 2,
                'fast_stage_state': 'incomplete', 'fast_stage_outcome': None,
                'dossier_stage_state': 'failed_or_recovery',
                'deep_stage_state': 'waiting_for_dossier', 'deep_stage_outcome': None,
                'deep_recovery_state': 'none',
                'effective_personalized_result_source': 'none',
            },
            {
                'id': 'C', 'analysis_state': 'not_analyzed', 'analysis_tier': 3,
                'fast_stage_state': 'not_started', 'fast_stage_outcome': None,
                'dossier_stage_state': 'accepted',
                'deep_stage_state': 'eligible_or_pending', 'deep_stage_outcome': None,
                'deep_recovery_state': 'none',
                'effective_personalized_result_source': 'none',
            },
        ],
        'progressive_personalization': {
            'contract': 'PROGRESSIVE-PERSONALIZED-DEALS-V1',
            'phase': 'phase_b',
            'pass1_active': True,
            'pass2_implemented': True,
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
            'pass2_implemented': True,
            'pass2_active': False,
            'fast_total_current_scope': 4,
            'fast_attempted_count': 3,
            'fast_completed_fit_count': 1,
            'fast_completed_not_fit_count': 1,
            'fast_incomplete_count': 1,
            'fast_error_count': 0,
            'fast_skipped_due_to_authoritative_deep_count': 0,
            'fast_remaining_count': 1,
            'dossier_observability': 'available',
            'dossier_total_current_scope': 4,
            'dossier_accepted_count': 1,
            'dossier_pending_count': 2,
            'dossier_failed_or_recovery_count': 1,
            'dossier_normal_first_pass_complete': False,
            'dossier_all_accepted_or_recovered_complete': False,
            'deep_total_current_coverage_target': 4,
            'deep_first_pass_attempted_count': 1,
            'deep_authoritative_completed_count': 1,
            'deep_completed_fit_count': 1,
            'deep_completed_not_fit_count': 0,
            'deep_incomplete_or_recovery_count': 0,
            'deep_waiting_for_dossier_count': 2,
            'deep_ready_or_pending_count': 1,
            'deep_normal_first_pass_remaining_count': 3,
            'deep_remaining_until_all_authoritative_count': 3,
            'deep_normal_first_pass_complete': False,
            'deep_all_current_authoritative_complete': False,
        },
        'production_contract': {
            'source_progressive_candidate_context_blob_sha': 'CTX',
            'progressive_personalization_contract_blob_sha': 'CONTRACT',
            'progressive_pass1_state_blob_sha': 'PASS1',
            'progressive_pass2_state_blob_sha': 'PASS2',
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
        pass2_state_blob='PASS2',
    )
    return integrity, compatible, reason


def main():
    # ROUTE-00: accepted Progressive PASS 1 ingest must enter the existing
    # GitHub-owned visual rebuild workflow through workflow_run, because pushes
    # made by the ingest workflow token do not recursively trigger push workflows.
    workflow = Path('.github/workflows/build-daily-visual-payload.yml').read_text(encoding='utf-8')
    assert '      - "Ingest Progressive PASS 1 item"' in workflow
    assert '      - "Ingest Progressive PASS 2 item"' in workflow

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

    # Implemented PASS 2 is still inactive, but accepted PASS 2 state is a
    # producer-owned semantic input and must force the same full rebuild path.
    stale_pass2 = compatible_visual()
    stale_pass2['production_contract']['progressive_pass2_state_blob_sha'] = 'OLD-PASS2'
    integrity, compatible, reason = classify(stale_pass2)
    assert integrity is True
    assert compatible is False
    assert reason == 'progressive_pass2_state_provenance_mismatch'

    # Stage observability is producer-owned; a stale visual missing any stage
    # field must force a full Progressive rebuild before bounded refresh.
    missing_stage = compatible_visual()
    missing_stage['items'][0].pop('deep_stage_state')
    integrity, compatible, reason = classify(missing_stage)
    assert integrity is True
    assert compatible is False
    assert reason == 'visible_stage_field_missing:deep_stage_state'

    # ROUTE-04: invalid source identity remains fail-closed and must never be
    # treated as a compatible bounded-refresh candidate.
    integrity, compatible, reason = classify(compatible_visual(), store_source='OTHER')
    assert integrity is False
    assert compatible is False
    assert reason == 'source_integrity_invalid'

    print('progressive visual activation routing regression: ok')


if __name__ == '__main__':
    main()
