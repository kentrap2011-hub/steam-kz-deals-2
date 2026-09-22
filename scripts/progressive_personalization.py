import json
from datetime import datetime, timezone
from pathlib import Path

import priority_ranking
import progressive_pass1
import progressive_pass2

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


def canonical_taste_entries():
    merged = dict(cache_entries(load_json(TASTE_CACHE))) if TASTE_CACHE.exists() else {}
    if TASTE_OVERLAY.exists():
        merged.update(cache_entries(load_json(TASTE_OVERLAY)))
    return merged


def effective_taste_entries():
    """Tier-1 rendering view with canonical cache precedence over PASS 1."""
    canonical = canonical_taste_entries()
    pass1 = progressive_pass1.current_fit_semantic_entries() if progressive_pass1.STATE.exists() else {}
    pass2 = progressive_pass2.current_fit_semantic_entries() if progressive_pass2.STATE.exists() else {}
    merged = dict(pass1)
    # PASS 2 is a later recovery result for a PASS 1-incomplete item. Canonical
    # Taste remains the strongest reusable source when present.
    merged.update(pass2)
    merged.update(canonical)
    return merged


def load_contract(path=CONTRACT):
    contract = load_json(path)
    if contract.get('contract') != 'PROGRESSIVE-PERSONALIZED-DEALS-V1':
        raise ValueError('progressive personalization contract mismatch')
    if contract.get('status') != 'canonical' or contract.get('phase') != 'phase_b':
        raise ValueError('progressive personalization Phase B is not canonical')
    if contract.get('durable_in_progress_state') is not False:
        raise ValueError('Progressive publication must not add durable analysis_in_progress')
    if contract.get('tier_precedence') != ['analyzed_fit', 'analysis_incomplete', 'not_analyzed']:
        raise ValueError('progressive tier precedence mismatch')
    phase = contract.get('phase_b_execution') or {}
    if phase.get('pass1_active') is not True or phase.get('pass2_active') is not False:
        raise ValueError('Phase B must activate PASS 1 and keep PASS 2 inactive')
    if phase.get('pass2_implemented') is not True:
        raise ValueError('Phase C PASS 2 core must be implemented before projection')
    progressive_pass1.load_contract()
    progressive_pass2.load_contract()
    return contract


def _base_state(analysis_state='not_analyzed', *, issue=None, fit=None, evaluated_at=None, source=None):
    return {
        'analysis_state': analysis_state,
        'analysis_tier': STATE_TIER[analysis_state],
        'analysis_issue_code': issue,
        'fit': fit,
        'evaluated_at_utc': evaluated_at,
        'analysis_semantic_source': source,
        'analysis_resolution_pass': None,
        'semantic_generation_id': None,
        'pass1_attempted': False,
        'pass2_attempted': False,
    }


def projection_state(projection, taste_entry):
    """Map only current exact-compatible canonical Taste cache into progressive state."""
    if not isinstance(projection, dict) or projection.get('status') != 'cache_hit':
        return _base_state()

    cached = projection.get('cached_taste') or {}
    verdict = str(cached.get('verdict') or '').upper()
    fit = cached.get('fit_level')
    evidence_state = projection.get('fit_evidence_state')
    evidence_ready = projection.get('fit_evidence_ready') is True
    backfill = projection.get('fit_evidence_backfill_required') is True

    if not isinstance(taste_entry, dict):
        return _base_state()
    if (
        str(taste_entry.get('verdict') or '').upper() != verdict
        or taste_entry.get('fit_level') != fit
        or taste_entry.get('taste_fingerprint') != projection.get('taste_fingerprint')
        or taste_entry.get('candidate_context_sha256') != projection.get('candidate_context_sha256')
    ):
        return _base_state()

    evaluated_at = taste_entry.get('evaluated_at_utc')

    if verdict == 'INCLUDE' and fit in {'strong', 'moderate'}:
        return _base_state(
            'analyzed_fit',
            fit=fit,
            evaluated_at=evaluated_at,
            source='compatible_cache',
        )

    if verdict == 'EXCLUDE':
        if evidence_state == 'insufficient' or backfill or not evidence_ready:
            return _base_state(
                'analysis_incomplete',
                issue='insufficient_current_semantic_evidence',
                source='compatible_cache',
            )
        if evidence_state in {'confirmed_negative', 'reconsiderable'}:
            return _base_state(
                'analyzed_not_fit',
                evaluated_at=evaluated_at,
                source='compatible_cache',
            )

    return _base_state()


def build_state_index(context_rows=None, projection_doc=None, taste_entries=None):
    load_contract()
    context_rows = context_rows if context_rows is not None else load_jsonl(PROGRESSIVE_CONTEXT)
    projection_doc = projection_doc if projection_doc is not None else load_json(TASTE_PROJECTION)
    taste_entries = taste_entries if taste_entries is not None else canonical_taste_entries()
    projections = projection_doc.get('entries') or {}
    pass1_state_doc = progressive_pass1.load_state()
    pass2_state_doc = progressive_pass2.load_state()
    queue_rows = progressive_pass1.load_jsonl(progressive_pass1.TASTE_QUEUE)
    generation, pass1_bindings, _queue_by_family = progressive_pass1.current_bindings(
        context_rows,
        projection_doc,
        queue_rows,
    )

    index = {}
    for row in context_rows:
        family_id = str(row.get('family_id') or '')
        taste_key = row.get('taste_subject_key')
        if not family_id or not taste_key:
            raise ValueError('progressive candidate context requires family_id and taste_subject_key')
        if family_id in index:
            raise ValueError(f'duplicate progressive family_id: {family_id}')

        projection = projections.get(taste_key) or {}
        canonical_entry = taste_entries.get(taste_key) or {}
        state = projection_state(projection, canonical_entry)
        binding = pass1_bindings.get(family_id)
        pass1_entry = progressive_pass1.matching_state_entry(binding, pass1_state_doc) if binding else None
        pass2_entry = progressive_pass2.matching_state_entry(binding, pass2_state_doc) if binding else None

        if state['analysis_state'] == 'not_analyzed' and pass1_entry is not None:
            pass1_state = progressive_pass1.project_state(binding, pass1_state_doc)
            if pass1_state is not None:
                state = pass1_state
                state['analysis_resolution_pass'] = 'pass1'
                state['pass2_attempted'] = False

        # PASS 2 may only replace the current exact PASS 1 incomplete projection.
        if (
            state['analysis_state'] == 'analysis_incomplete'
            and state.get('analysis_semantic_source') == 'progressive_pass1'
            and pass1_entry is not None
            and pass2_entry is not None
        ):
            pass2_state = progressive_pass2.project_state(binding, pass2_state_doc)
            if pass2_state is not None:
                state = pass2_state

        if state['analysis_state'] == 'analyzed_fit' and state.get('analysis_semantic_source') == 'progressive_pass2':
            semantic_entry = progressive_pass2.semantic_taste_entry(pass2_entry)
        elif state['analysis_state'] == 'analyzed_fit' and state.get('analysis_semantic_source') == 'progressive_pass1':
            semantic_entry = progressive_pass1.semantic_taste_entry(pass1_entry)
        elif state['analysis_state'] == 'analyzed_fit':
            semantic_entry = canonical_entry
        else:
            semantic_entry = {}

        index[family_id] = {
            **state,
            'taste_subject_key': taste_key,
            'taste_entry': semantic_entry,
            'projection': projection,
            'context': row,
            'pass1_scope_eligible': bool(binding) and state.get('analysis_semantic_source') != 'compatible_cache',
            'pass1_work_id': binding.get('work_id') if binding else None,
            'pass1_current_generation_id': generation['semantic_generation_id'] if binding else None,
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
    source = state.get('analysis_semantic_source')
    if source:
        game['analysis_semantic_source'] = source
    else:
        game.pop('analysis_semantic_source', None)
    generation = state.get('semantic_generation_id')
    if generation:
        game['analysis_semantic_generation_id'] = generation
    else:
        game.pop('analysis_semantic_generation_id', None)
    game['pass1_attempted'] = bool(state.get('pass1_attempted'))
    game['pass2_attempted'] = bool(state.get('pass2_attempted'))
    resolution_pass = state.get('analysis_resolution_pass')
    if resolution_pass:
        game['analysis_resolution_pass'] = resolution_pass
    else:
        game.pop('analysis_resolution_pass', None)
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
    pass1_total_scope = 0
    pass1_attempted = 0

    for family_id, state in state_index.items():
        if family_id in business_excluded:
            continue
        key = state['analysis_state']
        if key not in counts:
            raise ValueError(f'unknown analysis state: {key}')
        counts[key] += 1
        if state.get('evaluated_at_utc'):
            accepted_times.append(str(state['evaluated_at_utc']))
        if state.get('pass1_scope_eligible'):
            pass1_total_scope += 1
            if state.get('pass1_attempted'):
                pass1_attempted += 1

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
    pass1_remaining = pass1_total_scope - pass1_attempted
    if pass1_remaining < 0:
        raise ValueError('PASS 1 progress arithmetic mismatch')

    return {
        'schema_version': 2,
        'contract': 'PROGRESSIVE-PERSONALIZED-DEALS-V1',
        'phase': 'phase_b',
        'total_current_candidates': total,
        'analyzed_success_count': analyzed_success,
        'analyzed_fit_count': counts['analyzed_fit'],
        'analyzed_not_fit_count': counts['analyzed_not_fit'],
        'analysis_incomplete_count': counts['analysis_incomplete'],
        'not_analyzed_count': counts['not_analyzed'],
        'normal_visible_count': normal_visible,
        'last_accepted_analysis_at_utc': max(accepted_times) if accepted_times else None,
        'pass1_active': True,
        'pass1_total_scope': pass1_total_scope,
        'pass1_attempted_count': pass1_attempted,
        'pass1_remaining_count': pass1_remaining,
        'pass2_implemented': True,
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
        'phase': 'phase_b',
        'publication_status': 'current_deterministic_catalogue_with_incremental_pass1',
        'semantic_queue_zero_required_for_publication': False,
        'pass1_active': True,
        'pass2_implemented': True,
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
        'normal_visible_count', 'pass1_total_scope', 'pass1_attempted_count',
        'pass1_remaining_count',
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
    pass1_total = int(status['pass1_total_scope'])
    pass1_attempted = int(status['pass1_attempted_count'])
    pass1_remaining = int(status['pass1_remaining_count'])
    if pass1_total != pass1_attempted + pass1_remaining:
        raise ValueError('PASS 1 scope invariant failed')
    if (
        status.get('pass1_active') is not True
        or status.get('pass2_implemented') is not True
        or status.get('pass2_active') is not False
    ):
        raise ValueError('PASS 1/PASS 2 implementation or activation flags invalid')
    return True
