import json
from datetime import datetime, timezone
from pathlib import Path

import priority_ranking

ROOT = Path('.')
CONTRACT = ROOT / 'config/progressive_personalization_contract.json'
PROGRESSIVE_CONTEXT = ROOT / 'data/production/pre_ai/progressive_candidate_context.jsonl'
TASTE_PROJECTION = ROOT / 'data/production/pre_ai/taste_projection.json'
TASTE_CACHE = ROOT / 'data/cache/taste_fit.json'
TASTE_OVERLAY = ROOT / 'data/cache/taste_fit.entry_overlay.json'

STATE_TIER = {
    'analyzed_fit': 1,
    'analysis_incomplete': 2,
    'not_analyzed': 3,
    'analyzed_not_fit': None,
}
VISIBLE_STATES = {'analyzed_fit', 'analysis_incomplete', 'not_analyzed'}
UNRESOLVED_SEMANTIC_FIELDS = {
    'fit', 'source_fit', 'taste_factors', 'why_fit', 'why_fit_status',
    'why_fit_provenance', 'risks', 'risk_codes', 'risk_status',
    'risk_provenance', 'risk_level', 'risk_penalty', 'direct_user_evidence',
    'taste_rank', 'fit_adjustment_reason', 'taste_confidence', 'play_role',
    'play_role_confidence', 'play_role_provenance', 'relative_start_priority',
    'relative_start_priority_confidence', 'relative_start_priority_provenance',
    'play_priority_context_source', 'play_priority_context_contract',
    'total_score', 'personal_score', 'score_breakdown', 'priority_factors',
    'priority_vs_next', 'practical_or_personal_risk_rank',
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def load_jsonl(path):
    return [
        json.loads(line)
        for line in Path(path).read_text(encoding='utf-8').splitlines()
        if line.strip()
    ]


def cache_entries(doc):
    entries = doc.get('entries') if isinstance(doc, dict) else None
    return entries if isinstance(entries, dict) else {}


def effective_taste_entries():
    merged = dict(cache_entries(load_json(TASTE_CACHE))) if TASTE_CACHE.exists() else {}
    if TASTE_OVERLAY.exists():
        merged.update(cache_entries(load_json(TASTE_OVERLAY)))
    return merged


def load_contract(path=CONTRACT):
    contract = load_json(path)
    if contract.get('contract') != 'PROGRESSIVE-PERSONALIZED-DEALS-V1':
        raise ValueError('progressive personalization contract mismatch')
    if contract.get('status') != 'canonical' or contract.get('phase') != 'phase_a':
        raise ValueError('progressive personalization Phase A is not canonical')
    if contract.get('durable_in_progress_state') is not False:
        raise ValueError('Phase A must not add a durable analysis_in_progress state')
    if contract.get('tier_precedence') != ['analyzed_fit', 'analysis_incomplete', 'not_analyzed']:
        raise ValueError('progressive tier precedence mismatch')
    phase = contract.get('phase_a_execution') or {}
    if phase.get('pass1_active') is not False or phase.get('pass2_active') is not False:
        raise ValueError('Phase A must not activate PASS 1/PASS 2')
    return contract


def projection_state(projection, taste_entry):
    """Map only current exact-compatible semantic data into a durable Phase A state."""
    if not isinstance(projection, dict) or projection.get('status') != 'cache_hit':
        return {
            'analysis_state': 'not_analyzed',
            'analysis_tier': 3,
            'analysis_issue_code': None,
            'fit': None,
            'evaluated_at_utc': None,
        }

    cached = projection.get('cached_taste') or {}
    verdict = str(cached.get('verdict') or '').upper()
    fit = cached.get('fit_level')
    evidence_state = projection.get('fit_evidence_state')
    evidence_ready = projection.get('fit_evidence_ready') is True
    backfill = projection.get('fit_evidence_backfill_required') is True

    if not isinstance(taste_entry, dict):
        return {
            'analysis_state': 'not_analyzed',
            'analysis_tier': 3,
            'analysis_issue_code': None,
            'fit': None,
            'evaluated_at_utc': None,
        }
    if (
        str(taste_entry.get('verdict') or '').upper() != verdict
        or taste_entry.get('fit_level') != fit
        or taste_entry.get('taste_fingerprint') != projection.get('taste_fingerprint')
        or taste_entry.get('candidate_context_sha256') != projection.get('candidate_context_sha256')
    ):
        return {
            'analysis_state': 'not_analyzed',
            'analysis_tier': 3,
            'analysis_issue_code': None,
            'fit': None,
            'evaluated_at_utc': None,
        }

    evaluated_at = taste_entry.get('evaluated_at_utc')

    if verdict == 'INCLUDE' and fit in {'strong', 'moderate'}:
        return {
            'analysis_state': 'analyzed_fit',
            'analysis_tier': 1,
            'analysis_issue_code': None,
            'fit': fit,
            'evaluated_at_utc': evaluated_at,
        }

    if verdict == 'EXCLUDE':
        # V5 "insufficient" means evidence was not enough to establish a trustworthy
        # fit/not-fit conclusion for Progressive Personalized Deals. It remains visible.
        if evidence_state == 'insufficient' or backfill or not evidence_ready:
            return {
                'analysis_state': 'analysis_incomplete',
                'analysis_tier': 2,
                'analysis_issue_code': 'insufficient_current_semantic_evidence',
                'fit': None,
                'evaluated_at_utc': None,
            }
        if evidence_state in {'confirmed_negative', 'reconsiderable'}:
            return {
                'analysis_state': 'analyzed_not_fit',
                'analysis_tier': None,
                'analysis_issue_code': None,
                'fit': None,
                'evaluated_at_utc': evaluated_at,
            }

    return {
        'analysis_state': 'not_analyzed',
        'analysis_tier': 3,
        'analysis_issue_code': None,
        'fit': None,
        'evaluated_at_utc': None,
    }


def build_state_index(context_rows=None, projection_doc=None, taste_entries=None):
    load_contract()
    context_rows = context_rows if context_rows is not None else load_jsonl(PROGRESSIVE_CONTEXT)
    projection_doc = projection_doc if projection_doc is not None else load_json(TASTE_PROJECTION)
    taste_entries = taste_entries if taste_entries is not None else effective_taste_entries()
    projections = projection_doc.get('entries') or {}

    index = {}
    for row in context_rows:
        family_id = str(row.get('family_id') or '')
        taste_key = row.get('taste_subject_key')
        if not family_id or not taste_key:
            raise ValueError('progressive candidate context requires family_id and taste_subject_key')
        if family_id in index:
            raise ValueError(f'duplicate progressive family_id: {family_id}')
        projection = projections.get(taste_key) or {}
        entry = taste_entries.get(taste_key) or {}
        state = projection_state(projection, entry)
        index[family_id] = {
            **state,
            'taste_subject_key': taste_key,
            'taste_entry': entry if state['analysis_state'] == 'analyzed_fit' else {},
            'projection': projection,
            'context': row,
        }
    return index


def selected_scenario(context, fit):
    if fit == 'strong':
        return context.get('deal_if_strong') or {}
    if fit == 'moderate':
        return context.get('deal_if_moderate') or {}
    return {}


def strip_unresolved_personalization(game):
    for field in UNRESOLVED_SEMANTIC_FIELDS:
        game.pop(field, None)
    game['decision'] = 'Ожидает персонального разбора'
    return game


def apply_state_fields(game, state):
    analysis_state = state['analysis_state']
    game['analysis_state'] = analysis_state
    game['analysis_tier'] = state['analysis_tier']
    issue = state.get('analysis_issue_code')
    if issue:
        game['analysis_issue_code'] = issue
    else:
        game.pop('analysis_issue_code', None)
    if analysis_state != 'analyzed_fit':
        strip_unresolved_personalization(game)
    return game


def apply_progressive_order(items, now=None):
    """Apply tier-first order without ever comparing purchase-only and personalized scores."""
    now = now or datetime.now(timezone.utc)
    load_contract()
    fit_items = [game for game in items if game.get('analysis_state') == 'analyzed_fit']
    unresolved = [game for game in items if game.get('analysis_state') in {'analysis_incomplete', 'not_analyzed'}]

    if fit_items:
        fit_items, personalized_order = priority_ranking.apply_final_priority_order(fit_items, now=now)
        for game in fit_items:
            game['personalized_priority_rank'] = game.get('priority_rank')
            game.pop('deterministic_purchase_score', None)
    else:
        personalized_order = priority_ranking.load_final_priority_order()

    for game in unresolved:
        urgency_rank, urgency_code = priority_ranking.sale_expiry_urgency(game, now)
        purchase = priority_ranking.build_purchase_breakdown(game)
        game['sale_expiry_urgency'] = urgency_code
        game['sale_expiry_urgency_rank'] = urgency_rank
        game['deterministic_purchase_score'] = purchase['purchase_score']
        game['purchase_route'] = purchase['purchase_route']
        game['purchase_score'] = purchase['purchase_score']
        game['progressive_purchase_breakdown'] = purchase
        strip_unresolved_personalization(game)

    def default_key(game):
        tier = int(game.get('analysis_tier') or 99)
        urgency = int(game.get('sale_expiry_urgency_rank') if game.get('sale_expiry_urgency_rank') is not None else 2)
        if tier == 1:
            score = float(game.get('total_score') or 0)
        else:
            score = float(game.get('deterministic_purchase_score') or 0)
        return (tier, urgency, -score, str(game.get('title') or '').casefold())

    ordered = sorted(fit_items + unresolved, key=default_key)
    for index, game in enumerate(ordered, 1):
        game['priority_rank'] = index
    return ordered, personalized_order


def build_processing_status(state_index, visible_items, business_excluded_family_ids=None):
    business_excluded = {str(x) for x in (business_excluded_family_ids or [])}
    counts = {
        'analyzed_fit': 0,
        'analyzed_not_fit': 0,
        'analysis_incomplete': 0,
        'not_analyzed': 0,
    }
    accepted_times = []
    for family_id, state in state_index.items():
        if family_id in business_excluded:
            continue
        key = state['analysis_state']
        if key not in counts:
            raise ValueError(f'unknown analysis state: {key}')
        counts[key] += 1
        if key in {'analyzed_fit', 'analyzed_not_fit'} and state.get('evaluated_at_utc'):
            accepted_times.append(str(state['evaluated_at_utc']))

    total = sum(counts.values())
    analyzed_success = counts['analyzed_fit'] + counts['analyzed_not_fit']
    normal_visible = counts['analyzed_fit'] + counts['analysis_incomplete'] + counts['not_analyzed']
    actual_visible = len(visible_items)
    if actual_visible != normal_visible:
        raise ValueError(
            f'progressive visible count mismatch: projected={normal_visible} actual={actual_visible}'
        )
    if total != analyzed_success + counts['analysis_incomplete'] + counts['not_analyzed']:
        raise ValueError('progressive total arithmetic mismatch')

    return {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PERSONALIZED-DEALS-V1',
        'phase': 'phase_a',
        'total_current_candidates': total,
        'analyzed_success_count': analyzed_success,
        'analyzed_fit_count': counts['analyzed_fit'],
        'analyzed_not_fit_count': counts['analyzed_not_fit'],
        'analysis_incomplete_count': counts['analysis_incomplete'],
        'not_analyzed_count': counts['not_analyzed'],
        'normal_visible_count': normal_visible,
        'last_accepted_analysis_at_utc': max(accepted_times) if accepted_times else None,
        'pass1_active': False,
        'pass2_active': False,
        'semantic_queue_zero_required_for_publication': False,
    }



def business_excluded_family_ids(state_index):
    excluded = set()
    for family_id, state in state_index.items():
        if state.get('analysis_state') != 'analyzed_fit':
            continue
        scenario = selected_scenario(state.get('context') or {}, state.get('fit'))
        if scenario.get('disposition') != 'INCLUDE':
            excluded.add(str(family_id))
    return excluded


def stamp_processing_status(visual, state_index=None):
    state_index = state_index if state_index is not None else build_state_index()
    visible_items = visual.get('items') or []
    visible_ids = {str(game.get('id') or '') for game in visible_items}
    hard_excluded = business_excluded_family_ids(state_index)
    for family_id, state in state_index.items():
        if state.get('analysis_state') in VISIBLE_STATES and str(family_id) not in visible_ids:
            hard_excluded.add(str(family_id))

    status = build_processing_status(
        state_index,
        visible_items,
        business_excluded_family_ids=hard_excluded,
    )
    validate_processing_status(status)
    visual['processing_status'] = status
    visual['progressive_personalization'] = {
        'contract': 'PROGRESSIVE-PERSONALIZED-DEALS-V1',
        'phase': 'phase_a',
        'publication_status': 'current_deterministic_catalogue',
        'semantic_queue_zero_required_for_publication': False,
        'pass1_active': False,
        'pass2_active': False,
    }
    # Overall visual availability reflects the deterministic current catalogue.
    # Semantic completeness remains separately available in semantic_completeness.
    visual['status'] = 'complete'
    return status

def validate_processing_status(status):
    required = {
        'total_current_candidates', 'analyzed_success_count', 'analyzed_fit_count',
        'analyzed_not_fit_count', 'analysis_incomplete_count', 'not_analyzed_count',
        'normal_visible_count',
    }
    if not required.issubset(status):
        raise ValueError('progressive processing status missing required counters')
    total = int(status['total_current_candidates'])
    fit = int(status['analyzed_fit_count'])
    not_fit = int(status['analyzed_not_fit_count'])
    incomplete = int(status['analysis_incomplete_count'])
    untouched = int(status['not_analyzed_count'])
    analyzed = int(status['analyzed_success_count'])
    visible = int(status['normal_visible_count'])
    if total != fit + not_fit + incomplete + untouched:
        raise ValueError('total_current_candidates invariant failed')
    if analyzed != fit + not_fit:
        raise ValueError('analyzed_success_count invariant failed')
    if visible != fit + incomplete + untouched:
        raise ValueError('normal_visible_count invariant failed')
    return True
