import copy
import json
import tempfile
from pathlib import Path

import progressive_personalization as progressive
import grounded_negative_visual
import refresh_visual_commercial_fields
import priority_ranking


def context(fid, key):
    return {
        'family_id': fid,
        'family_type': 'single_game',
        'taste_subject_key': key,
        'purchase': {
            'key': key,
            'title': fid,
            'discount_percent': 50,
            'current_price_rub_display': 300,
            'original_price_rub_display': 1000,
            'sale_end_utc': '2026-09-30T12:00:00Z',
        },
        'history': {'quality': 'unverified', 'minimum_rub_display': None, 'previously_free': False},
        'deal_if_strong': {'disposition': 'INCLUDE', 'purchase_decision': 'БРАТЬ СЕЙЧАС', 'priority_bucket': 1},
        'deal_if_moderate': {'disposition': 'INCLUDE', 'purchase_decision': 'МОЖНО БРАТЬ', 'priority_bucket': 2},
        'context_only': {'wishlist': False},
        'semantic_condition': {'base_appids': [key.split('_')[-1]]},
    }


def projection(key, status='ai_required', verdict=None, fit=None, evidence_state=None, evidence_ready=False):
    row = {
        'taste_subject_key': key,
        'appid': key.split('_')[-1],
        'taste_fingerprint': f'fp-{key}',
        'candidate_context_sha256': f'ctx-{key}',
        'status': status,
        'fit_evidence_state': evidence_state,
        'fit_evidence_ready': evidence_ready,
        'fit_evidence_backfill_required': evidence_state == 'insufficient',
    }
    if status == 'cache_hit':
        row['cached_taste'] = {'verdict': verdict, 'fit_level': fit, 'reason_code': 'test'}
    return row



def projection_doc(entries):
    return {
        'current_profile': {
            'repository': 'kentrap2011-hub/stopgame-ratings-data',
            'path': 'gaming_taste_live.json',
            'resolved_commit_sha': 'a' * 40,
            'blob_sha': 'b' * 40,
            'content_sha256': 'c' * 64,
            'bytes': 123,
            'raw_url': (
                'https://raw.githubusercontent.com/kentrap2011-hub/'
                'stopgame-ratings-data/' + ('a' * 40) + '/gaming_taste_live.json'
            ),
        },
        'current_binding': {
            'taste_model_version': 'taste-v3',
            'taste_semantics_sha256': 'test-semantics-sha',
            'candidate_context_contract_blob_sha': 'test-context-contract-blob',
        },
        'entries': entries,
    }

def taste(key, verdict, fit):
    return {
        'appid': key.split('_')[-1],
        'taste_fingerprint': f'fp-{key}',
        'candidate_context_sha256': f'ctx-{key}',
        'verdict': verdict,
        'fit_level': fit,
        'evaluated_at_utc': '2026-09-20T10:00:00+00:00',
        'positive_evidence': [{'evidence': 'test'}],
    }


def game(fid, state, tier, *, price=300, original=1000, urgency=2, why=None):
    row = {
        'id': fid,
        'title': fid,
        'analysis_state': state,
        'analysis_tier': tier,
        'current_price_rub': price,
        'original_price_rub': original,
        'discount_percent': 70,
        'history_quality': 'unverified',
        'sale_end_utc': '2026-09-30T12:00:00Z',
        'sale_expiry_urgency_rank': urgency,
        'wishlist': False,
        'practical': {'modern_windows_friction': 'unknown', 'steam_achievements': None},
        'why_fit': list(why or []),
        'risks': [],
        'risk_codes': [],
        'risk_level': 'low',
    }
    if state == 'analyzed_fit':
        row.update({'fit': 'strong', 'source_fit': 'strong'})
    return row


def deep_bound_game(fid, outcome='fit'):
    state = 'analyzed_fit' if outcome == 'fit' else 'analyzed_not_fit'
    row = game(fid, state, 1 if outcome == 'fit' else None)
    row.update({
        'analysis_semantic_source': 'progressive_pass2',
        'analysis_resolution_pass': 'pass2',
        'pass2_attempted': True,
        'deep_stage_state': 'completed',
        'deep_stage_outcome': outcome,
        'effective_analysis_source': 'deep',
    })
    return row


def main():
    progressive.load_contract()

    # Deep visual authoritative binding regression:
    # current authoritative PASS 2 is valid even when reusable Taste projection
    # remains ai_required; stale/non-current Deep must still fail closed.
    deep_fit = deep_bound_game('deep-fit', 'fit')
    assert grounded_negative_visual.has_current_personalized_binding(
        deep_fit, projection('App_201', 'ai_required')
    )

    original_package_apply = grounded_negative_visual.package_options.apply_current_artifacts_to_visual
    original_order = grounded_negative_visual.progressive_personalization.apply_progressive_order
    original_stamp = grounded_negative_visual.progressive_personalization.stamp_processing_status
    try:
        grounded_negative_visual.package_options.apply_current_artifacts_to_visual = lambda ready: None
        grounded_negative_visual.progressive_personalization.apply_progressive_order = (
            lambda items: (list(items), [])
        )
        grounded_negative_visual.progressive_personalization.stamp_processing_status = lambda ready: None
        ready = {'items': [copy.deepcopy(deep_fit)]}
        stats = grounded_negative_visual.apply_to_document(
            ready,
            contexts={'deep-fit': {'taste_subject_key': 'App_201'}},
            taste_entries={
                'App_201': {
                    'verdict': 'INCLUDE',
                    'negative_analysis_status': 'incomplete_no_confirmed_negative',
                    'negative_findings': [],
                    'negative_evidence': [],
                }
            },
            projections={'App_201': projection('App_201', 'ai_required')},
        )
        assert ready['item_count'] == 1
        assert stats['negative_pending_count'] == 1
    finally:
        grounded_negative_visual.package_options.apply_current_artifacts_to_visual = original_package_apply
        grounded_negative_visual.progressive_personalization.apply_progressive_order = original_order
        grounded_negative_visual.progressive_personalization.stamp_processing_status = original_stamp

    deep_not_fit = deep_bound_game('deep-not-fit', 'not_fit')
    assert grounded_negative_visual.has_current_personalized_binding(
        deep_not_fit, projection('App_202', 'ai_required')
    )
    not_fit_visible, _ = progressive.apply_progressive_order([copy.deepcopy(deep_not_fit)])
    assert not_fit_visible == []

    stale_deep = copy.deepcopy(deep_fit)
    stale_deep['deep_stage_state'] = 'waiting_for_dossier'
    stale_deep['deep_stage_outcome'] = None
    stale_deep['effective_analysis_source'] = 'none'
    assert not grounded_negative_visual.has_current_personalized_binding(
        stale_deep, projection('App_203', 'ai_required')
    )
    try:
        grounded_negative_visual.apply_to_document(
            {'items': [stale_deep]},
            contexts={'deep-fit': {'taste_subject_key': 'App_203'}},
            taste_entries={'App_203': {'verdict': 'INCLUDE'}},
            projections={'App_203': projection('App_203', 'ai_required')},
        )
    except RuntimeError as exc:
        assert 'personalized card binding is not current/INCLUDE' in str(exc)
    else:
        raise AssertionError('stale/non-current Deep must not bypass personalized binding guard')

    assert grounded_negative_visual.has_current_personalized_binding(
        {'analysis_semantic_source': 'progressive_pass1'},
        projection('App_204', 'ai_required'),
    )
    assert grounded_negative_visual.has_current_personalized_binding(
        {},
        projection('App_205', 'cache_hit', 'INCLUDE', 'strong', 'sufficient', True),
    )

    # A. Zero semantic results -> every current deterministic candidate is Tier 3.
    contexts = [context('A', 'App_1'), context('B', 'App_2'), context('C', 'App_3')]
    proj = projection_doc({r['taste_subject_key']: projection(r['taste_subject_key']) for r in contexts})
    states = progressive.build_state_index(contexts, proj, {})
    assert {s['analysis_state'] for s in states.values()} == {'not_analyzed'}
    visible = [game(fid, 'not_analyzed', 3) for fid in states]
    visible, _ = progressive.apply_progressive_order(visible)
    status = progressive.build_processing_status(states, visible)
    assert status['total_current_candidates'] == 3
    assert status['not_analyzed_count'] == 3
    assert status['normal_visible_count'] == 3
    assert status['semantic_queue_zero_required_for_publication'] is False

    # B/D/E. Mixed state, stale Taste and V5 insufficient mapping.
    rows = [
        context('fit', 'App_11'),
        context('incomplete', 'App_12'),
        context('untouched', 'App_13'),
        context('notfit', 'App_14'),
        context('stale', 'App_15'),
    ]
    projections = {
        'App_11': projection('App_11', 'cache_hit', 'INCLUDE', 'strong', 'sufficient', True),
        'App_12': projection('App_12', 'cache_hit', 'EXCLUDE', 'below_moderate', 'insufficient', True),
        'App_13': projection('App_13'),
        'App_14': projection('App_14', 'cache_hit', 'EXCLUDE', 'below_moderate', 'confirmed_negative', True),
        # An old cache row exists, but projection says current binding requires AI.
        'App_15': projection('App_15', 'ai_required'),
    }
    tastes = {
        'App_11': taste('App_11', 'INCLUDE', 'strong'),
        'App_12': taste('App_12', 'EXCLUDE', 'below_moderate'),
        'App_14': taste('App_14', 'EXCLUDE', 'below_moderate'),
        'App_15': taste('App_15', 'INCLUDE', 'strong'),
    }
    states = progressive.build_state_index(rows, projection_doc(projections), tastes)
    assert states['fit']['analysis_state'] == 'analyzed_fit'
    assert states['incomplete']['analysis_state'] == 'analysis_incomplete'
    assert states['untouched']['analysis_state'] == 'not_analyzed'
    assert states['notfit']['analysis_state'] == 'analyzed_not_fit'
    assert states['stale']['analysis_state'] == 'not_analyzed'

    mixed = [
        game('fit', 'analyzed_fit', 1, price=700, original=750, why=['Подходит тебе по структуре.']),
        game('incomplete', 'analysis_incomplete', 2, price=20, original=5000),
        game('untouched', 'not_analyzed', 3, price=10, original=6000),
        game('stale', 'not_analyzed', 3, price=5, original=7000),
    ]
    ordered, _ = progressive.apply_progressive_order(copy.deepcopy(mixed))
    assert [g['analysis_state'] for g in ordered] == [
        'analyzed_fit', 'analysis_incomplete', 'not_analyzed', 'not_analyzed'
    ]
    assert all(g.get('total_score') is None for g in ordered if g['analysis_state'] != 'analyzed_fit')
    assert all(not g.get('why_fit') for g in ordered if g['analysis_state'] != 'analyzed_fit')
    assert ordered[0]['why_fit'] == ['Подходит тебе по структуре.']
    assert ordered[0]['total_score'] is not None

    status = progressive.build_processing_status(states, ordered)
    progressive.validate_processing_status(status)
    assert status['total_current_candidates'] == 5
    assert status['analyzed_success_count'] == 2
    assert status['analyzed_fit_count'] == 1
    assert status['analyzed_not_fit_count'] == 1
    assert status['analysis_incomplete_count'] == 1
    assert status['not_analyzed_count'] == 2
    assert status['normal_visible_count'] == 4

    # F. Hard source binding mismatch remains fail-closed.
    payload = {'source_mailing_updated_at_utc': 'A', 'fx_binding': {'kzt_per_rub': 5}}
    store = {'status': 'complete', 'discovery_source_updated_at_utc': 'B'}
    family = {'status': 'complete', 'source_updated_at_utc': 'A'}
    try:
        refresh_visual_commercial_fields.validate_commercial_binding(payload, store, family)
    except ValueError:
        pass
    else:
        raise AssertionError('source mismatch must fail closed')

    # I. Unresolved cards cannot retain semantic claims.
    dirty = game('dirty', 'not_analyzed', 3, why=['should disappear'])
    dirty['total_score'] = 99
    dirty['score_breakdown'] = {'total_score': 99}
    dirty['risks'] = ['unsupported']
    dirty['risk_status'] = {'label': 'unsupported'}
    progressive.strip_unresolved_personalization(dirty)
    assert 'total_score' not in dirty and 'score_breakdown' not in dirty
    assert 'why_fit' not in dirty and 'risks' not in dirty and 'risk_status' not in dirty

    # Purchase-only score is bounded separately and never manufactures a personal score.
    purchase = priority_ranking.build_purchase_breakdown(game('purchase', 'not_analyzed', 3))
    assert 0 <= purchase['purchase_score'] <= 40
    assert 'personal_score' not in purchase and 'total_score' not in purchase

    # J. Dossier statistics are projected from the canonical work manifest on every build.
    # Advancing one 3-game group changes accepted/pending counts without any semantic rerun.
    original_dossier_work = progressive.progressive_pass2.DOSSIER_WORK
    with tempfile.TemporaryDirectory() as tmp:
        dossier_path = Path(tmp) / 'dossier-work.json'
        progressive.progressive_pass2.DOSSIER_WORK = dossier_path
        try:
            base = {
                'eligible_scope_count': 4,
                'prepared_required_count': 4,
                'group_progress': {
                    'accepted_dossier_count': 0,
                    'failed_dossier_count': 0,
                    'pending_dossier_count': 4,
                    'normal_first_pass_complete': False,
                    'all_groups_accepted': False,
                },
            }
            dossier_path.write_text(json.dumps(base), encoding='utf-8')
            before = progressive._dossier_processing_metrics()
            assert before['dossier_accepted_count'] == 0
            assert before['dossier_pending_count'] == 4

            advanced = copy.deepcopy(base)
            advanced['group_progress']['accepted_dossier_count'] = 3
            advanced['group_progress']['pending_dossier_count'] = 1
            dossier_path.write_text(json.dumps(advanced), encoding='utf-8')
            after = progressive._dossier_processing_metrics()
            assert after['dossier_accepted_count'] == 3
            assert after['dossier_pending_count'] == 1
            assert after['dossier_failed_or_recovery_count'] == 0
        finally:
            progressive.progressive_pass2.DOSSIER_WORK = original_dossier_work

    # K. Arithmetic contradictions fail validation.
    broken = dict(status)
    broken['total_current_candidates'] += 1
    try:
        progressive.validate_processing_status(broken)
    except ValueError:
        pass
    else:
        raise AssertionError('counter mismatch must fail validation')

    print('progressive personalization Phase A fallback / Phase B regression: ok')


if __name__ == '__main__':
    main()
