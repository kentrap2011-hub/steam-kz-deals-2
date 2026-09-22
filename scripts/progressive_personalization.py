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
    """Current rendering view: Deep > Fast > reusable canonical Taste.

    Exact reusable-cache compatibility is still decided by projection_state; this
    merged semantic lookup only controls the payload used after a current source
    has already been selected.
    """
    canonical = canonical_taste_entries()
    pass1 = progressive_pass1.current_fit_semantic_entries() if progressive_pass1.STATE.exists() else {}
    pass2 = progressive_pass2.current_fit_semantic_entries() if progressive_pass2.STATE.exists() else {}
    merged = dict(canonical)
    merged.update(pass1)
    merged.update(pass2)
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


def _fast_stage(pass1_entry):
    if not isinstance(pass1_entry, dict):
        return 'not_started', None
    outcome = pass1_entry.get('outcome')
    if outcome == 'analyzed_fit':
        return 'completed', 'fit'
    if outcome == 'analyzed_not_fit':
        return 'completed', 'not_fit'
    if outcome == 'analysis_incomplete':
        if pass1_entry.get('analysis_issue_code') in {'worker_failure', 'invalid_semantic_result'}:
            return 'error', None
        return 'incomplete', None
    return 'error', None


def build_state_index(context_rows=None, projection_doc=None, taste_entries=None):
    load_contract()
    context_rows = context_rows if context_rows is not None else load_jsonl(PROGRESSIVE_CONTEXT)
    projection_doc = projection_doc if projection_doc is not None else load_json(TASTE_PROJECTION)
    taste_entries = taste_entries if taste_entries is not None else canonical_taste_entries()
    projections = projection_doc.get('entries') or {}
    pass1_state_doc = progressive_pass1.load_state()
    pass2_state_doc = progressive_pass2.load_state()
    queue_rows = progressive_pass1.load_jsonl(progressive_pass1.TASTE_QUEUE)
    generation, pass1_bindings, queue_by_family = progressive_pass1.current_bindings(
        context_rows,
        projection_doc,
        queue_rows,
    )
    try:
        current_dossier_binding = progressive_pass2.current_dossier_binding()
    except Exception:
        current_dossier_binding = {}
    dossier_work_doc = progressive_pass2.load_json(progressive_pass2.DOSSIER_WORK)
    deep_work_doc = progressive_pass2.load_json(progressive_pass2.WORK)

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
        cache_state = projection_state(projection, canonical_entry)
        state = dict(cache_state)
        binding = pass1_bindings.get(family_id)
        pass1_entry = progressive_pass1.matching_state_entry(binding, pass1_state_doc) if binding else None
        deep_entry = progressive_pass2.matching_state_entry(binding, pass2_state_doc) if binding else None
        deep_authoritative = (
            progressive_pass2.authoritative_completion_entry(binding, pass2_state_doc)
            if binding else None
        )

        # Fast remains the provisional current result when no compatible reusable
        # cache already resolved the identity.
        if cache_state.get('analysis_semantic_source') != 'compatible_cache' and pass1_entry is not None:
            pass1_state = progressive_pass1.project_state(binding, pass1_state_doc)
            if pass1_state is not None:
                state = pass1_state
                state['analysis_resolution_pass'] = 'pass1'

        # Authoritative Deep always wins. Unresolved Deep is diagnostic/recovery
        # state only and must not erase a valid Fast or reusable-cache success.
        if deep_authoritative is not None:
            deep_state = progressive_pass2.project_state(binding, pass2_state_doc)
            if deep_state is not None:
                state = deep_state
        elif deep_entry is not None and state.get('analysis_state') not in {'analyzed_fit', 'analyzed_not_fit'}:
            deep_state = progressive_pass2.project_state(binding, pass2_state_doc)
            if deep_state is not None:
                state = deep_state

        fast_stage_state, fast_stage_outcome = _fast_stage(pass1_entry)
        queue_row = queue_by_family.get(family_id) or {}
        semantic_input = progressive_pass2._semantic_input(queue_row)
        if binding and current_dossier_binding:
            try:
                dossier_stage = progressive_pass2.dossier_stage_state(
                    binding=binding,
                    semantic_input=semantic_input,
                    current_binding=current_dossier_binding,
                    dossier_work_doc=dossier_work_doc,
                )
            except Exception:
                dossier_stage = 'not_ready'
        else:
            dossier_stage = 'not_ready'

        if not binding:
            deep_stage = 'not_started'
        elif deep_authoritative is not None:
            deep_stage = 'completed'
        elif deep_entry is not None:
            deep_stage = 'incomplete_or_recovery'
        elif dossier_stage == 'accepted':
            deep_stage = 'eligible_or_pending'
        else:
            deep_stage = 'waiting_for_dossier'

        deep_recovery = (
            progressive_pass2.deep_recovery_state(binding, pass2_state_doc, deep_work_doc)
            if binding else 'none'
        )
        deep_outcome = None
        if deep_authoritative is not None:
            deep_outcome = 'fit' if deep_authoritative.get('outcome') == 'analyzed_fit' else 'not_fit'

        if deep_authoritative is not None:
            effective_source = 'deep'
        elif (
            pass1_entry is not None
            and pass1_entry.get('outcome') in {'analyzed_fit', 'analyzed_not_fit'}
            and state.get('analysis_semantic_source') == 'progressive_pass1'
        ):
            effective_source = 'fast'
        else:
            effective_source = 'none'

        state['pass1_attempted'] = pass1_entry is not None
        state['pass2_attempted'] = deep_entry is not None
        state['fast_stage_state'] = fast_stage_state
        state['fast_stage_outcome'] = fast_stage_outcome
        state['dossier_stage_state'] = dossier_stage
        state['deep_stage_state'] = deep_stage
        state['deep_stage_outcome'] = deep_outcome
        state['deep_recovery_state'] = deep_recovery
        state['effective_personalized_result_source'] = effective_source
        state['deep_authoritative_completed'] = deep_authoritative is not None
        state['deep_first_pass_attempted'] = deep_entry is not None
        state['fast_scope_eligible'] = bool(binding) and cache_state.get('analysis_semantic_source') != 'compatible_cache'
        state['deep_scope_eligible'] = bool(binding)

        if deep_authoritative is not None and deep_authoritative.get('outcome') == 'analyzed_fit':
            semantic_entry = progressive_pass2.semantic_taste_entry(deep_authoritative)
        elif state.get('analysis_state') == 'analyzed_fit' and state.get('analysis_semantic_source') == 'progressive_pass1':
            semantic_entry = progressive_pass1.semantic_taste_entry(pass1_entry)
        elif state.get('analysis_state') == 'analyzed_fit' and state.get('analysis_semantic_source') == 'compatible_cache':
            semantic_entry = canonical_entry
        else:
            semantic_entry = {}

        index[family_id] = {
            **state,
            'taste_subject_key': taste_key,
            'taste_entry': semantic_entry,
            'projection': projection,
            'context': row,
            'pass1_scope_eligible': state['fast_scope_eligible'],
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

    for field in (
        'fast_stage_state',
        'fast_stage_outcome',
        'dossier_stage_state',
        'deep_stage_state',
        'deep_stage_outcome',
        'deep_recovery_state',
        'effective_personalized_result_source',
    ):
        game[field] = state.get(field)

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


def _dossier_processing_metrics():
    try:
        doc = progressive_pass2.load_json(progressive_pass2.DOSSIER_WORK)
        progress = doc.get('group_progress') or {}
        total = int(doc.get('prepared_required_count'))
        accepted = int(progress.get('accepted_dossier_count'))
        failed = int(progress.get('failed_dossier_count'))
        pending = int(progress.get('pending_dossier_count'))
        if total != accepted + failed + pending:
            raise ValueError('Dossier progress arithmetic mismatch')
        return {
            'dossier_observability': 'available',
            'dossier_total_current_scope': total,
            'dossier_accepted_count': accepted,
            'dossier_pending_count': pending,
            'dossier_failed_or_recovery_count': failed,
            'dossier_normal_first_pass_complete': bool(progress.get('normal_first_pass_complete')),
            'dossier_all_accepted_or_recovered_complete': bool(progress.get('all_groups_accepted')),
        }
    except Exception as exc:
        return {
            'dossier_observability': f'unavailable:{type(exc).__name__}',
            'dossier_total_current_scope': None,
            'dossier_accepted_count': None,
            'dossier_pending_count': None,
            'dossier_failed_or_recovery_count': None,
            'dossier_normal_first_pass_complete': None,
            'dossier_all_accepted_or_recovered_complete': None,
        }


def build_processing_status(state_index, visible_items, business_excluded_family_ids=None):
    business_excluded = {str(x) for x in (business_excluded_family_ids or [])}
    counts = {
        'analyzed_fit': 0,
        'analyzed_not_fit': 0,
        'analysis_incomplete': 0,
        'not_analyzed': 0,
    }
    accepted_times = []

    fast_total = fast_attempted = fast_fit = fast_not_fit = 0
    fast_incomplete = fast_error = fast_skipped_deep = fast_remaining = 0
    deep_total = deep_first_pass_attempted = deep_authoritative = 0
    deep_fit = deep_not_fit = deep_incomplete = deep_waiting = deep_ready = 0

    for family_id, state in state_index.items():
        if family_id in business_excluded:
            continue
        key = state['analysis_state']
        if key not in counts:
            raise ValueError(f'unknown analysis state: {key}')
        counts[key] += 1
        if state.get('evaluated_at_utc'):
            accepted_times.append(str(state['evaluated_at_utc']))

        if state.get('fast_scope_eligible'):
            fast_total += 1
            fast_state = state.get('fast_stage_state')
            fast_outcome = state.get('fast_stage_outcome')
            if fast_state == 'completed':
                fast_attempted += 1
                if fast_outcome == 'fit':
                    fast_fit += 1
                elif fast_outcome == 'not_fit':
                    fast_not_fit += 1
                else:
                    raise ValueError('completed Fast stage missing fit/not_fit outcome')
            elif fast_state == 'incomplete':
                fast_attempted += 1
                fast_incomplete += 1
            elif fast_state == 'error':
                fast_attempted += 1
                fast_error += 1
            elif fast_state == 'not_started':
                if state.get('deep_authoritative_completed'):
                    fast_skipped_deep += 1
                else:
                    fast_remaining += 1
            else:
                raise ValueError(f'unknown Fast stage state: {fast_state!r}')

        if state.get('deep_scope_eligible'):
            deep_total += 1
            if state.get('deep_first_pass_attempted'):
                deep_first_pass_attempted += 1
            if state.get('deep_authoritative_completed'):
                deep_authoritative += 1
                if state.get('deep_stage_outcome') == 'fit':
                    deep_fit += 1
                elif state.get('deep_stage_outcome') == 'not_fit':
                    deep_not_fit += 1
                else:
                    raise ValueError('completed Deep stage missing fit/not_fit outcome')
            elif state.get('deep_first_pass_attempted'):
                deep_incomplete += 1

            deep_stage = state.get('deep_stage_state')
            recovery_state = state.get('deep_recovery_state')
            if deep_stage == 'waiting_for_dossier':
                deep_waiting += 1
            elif deep_stage == 'eligible_or_pending':
                deep_ready += 1
            elif recovery_state in {'recovery_eligible', 'recovery_pending'}:
                deep_ready += 1

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
    if fast_total != fast_attempted + fast_skipped_deep + fast_remaining:
        raise ValueError('Fast stage arithmetic mismatch')

    deep_normal_remaining = deep_total - deep_first_pass_attempted
    deep_authoritative_remaining = deep_total - deep_authoritative
    if deep_normal_remaining < 0 or deep_authoritative_remaining < 0:
        raise ValueError('Deep progress arithmetic underflow')

    dossier = _dossier_processing_metrics()
    return {
        'schema_version': 3,
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
        'pass1_total_scope': fast_attempted + fast_remaining,
        'pass1_attempted_count': fast_attempted,
        'pass1_remaining_count': fast_remaining,
        'pass2_implemented': True,
        'pass2_active': False,
        'semantic_queue_zero_required_for_publication': False,

        'fast_total_current_scope': fast_total,
        'fast_attempted_count': fast_attempted,
        'fast_completed_fit_count': fast_fit,
        'fast_completed_not_fit_count': fast_not_fit,
        'fast_incomplete_count': fast_incomplete,
        'fast_error_count': fast_error,
        'fast_skipped_due_to_authoritative_deep_count': fast_skipped_deep,
        'fast_remaining_count': fast_remaining,

        **dossier,

        'deep_total_current_coverage_target': deep_total,
        'deep_first_pass_attempted_count': deep_first_pass_attempted,
        'deep_authoritative_completed_count': deep_authoritative,
        'deep_completed_fit_count': deep_fit,
        'deep_completed_not_fit_count': deep_not_fit,
        'deep_incomplete_or_recovery_count': deep_incomplete,
        'deep_waiting_for_dossier_count': deep_waiting,
        'deep_ready_or_pending_count': deep_ready,
        'deep_normal_first_pass_remaining_count': deep_normal_remaining,
        'deep_remaining_until_all_authoritative_count': deep_authoritative_remaining,
        'deep_normal_first_pass_complete': deep_normal_remaining == 0,
        'deep_all_current_authoritative_complete': deep_authoritative_remaining == 0,

        'fast_stage_counts': {
            'total_current_scope': fast_total,
            'attempted': fast_attempted,
            'completed_fit': fast_fit,
            'completed_not_fit': fast_not_fit,
            'incomplete': fast_incomplete,
            'error': fast_error,
            'skipped_due_to_authoritative_deep': fast_skipped_deep,
            'remaining': fast_remaining,
        },
        'dossier_stage_counts': {
            key: dossier[key]
            for key in (
                'dossier_observability',
                'dossier_total_current_scope',
                'dossier_accepted_count',
                'dossier_pending_count',
                'dossier_failed_or_recovery_count',
                'dossier_normal_first_pass_complete',
                'dossier_all_accepted_or_recovered_complete',
            )
        },
        'deep_stage_counts': {
            'total_current_coverage_target': deep_total,
            'first_pass_attempted': deep_first_pass_attempted,
            'authoritative_completed': deep_authoritative,
            'completed_fit': deep_fit,
            'completed_not_fit': deep_not_fit,
            'incomplete_or_recovery': deep_incomplete,
            'waiting_for_dossier': deep_waiting,
            'ready_or_pending': deep_ready,
            'normal_first_pass_remaining': deep_normal_remaining,
            'remaining_until_all_authoritative': deep_authoritative_remaining,
            'normal_first_pass_complete': deep_normal_remaining == 0,
            'all_current_authoritative_complete': deep_authoritative_remaining == 0,
        },
        'effective_result_counts': {
            'deep': sum(
                1 for fid, state in state_index.items()
                if fid not in business_excluded
                and state.get('effective_personalized_result_source') == 'deep'
            ),
            'fast': sum(
                1 for fid, state in state_index.items()
                if fid not in business_excluded
                and state.get('effective_personalized_result_source') == 'fast'
            ),
            'none': sum(
                1 for fid, state in state_index.items()
                if fid not in business_excluded
                and state.get('effective_personalized_result_source') == 'none'
            ),
        },
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
        'publication_status': 'current_deterministic_catalogue_with_independent_fast_dossier_deep_runtime',
        'semantic_queue_zero_required_for_publication': False,
        'pass1_active': True,
        'pass2_implemented': True,
        'pass2_active': False,
        'deep_runtime_adapted': True,
    }
    visual['status'] = 'complete'
    return status


def validate_processing_status(status):
    required = {
        'total_current_candidates', 'analyzed_success_count', 'analyzed_fit_count',
        'analyzed_not_fit_count', 'analysis_incomplete_count', 'not_analyzed_count',
        'normal_visible_count', 'pass1_total_scope', 'pass1_attempted_count',
        'pass1_remaining_count',
        'fast_total_current_scope', 'fast_attempted_count',
        'fast_completed_fit_count', 'fast_completed_not_fit_count',
        'fast_incomplete_count', 'fast_error_count',
        'fast_skipped_due_to_authoritative_deep_count', 'fast_remaining_count',
        'dossier_total_current_scope', 'dossier_accepted_count',
        'dossier_pending_count', 'dossier_failed_or_recovery_count',
        'dossier_normal_first_pass_complete', 'dossier_all_accepted_or_recovered_complete',
        'deep_total_current_coverage_target', 'deep_first_pass_attempted_count',
        'deep_authoritative_completed_count', 'deep_completed_fit_count',
        'deep_completed_not_fit_count', 'deep_incomplete_or_recovery_count',
        'deep_waiting_for_dossier_count', 'deep_ready_or_pending_count',
        'deep_normal_first_pass_remaining_count',
        'deep_remaining_until_all_authoritative_count',
        'deep_normal_first_pass_complete', 'deep_all_current_authoritative_complete',
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

    fast_total = int(status['fast_total_current_scope'])
    fast_attempted = int(status['fast_attempted_count'])
    fast_skipped = int(status['fast_skipped_due_to_authoritative_deep_count'])
    fast_remaining = int(status['fast_remaining_count'])
    if fast_total != fast_attempted + fast_skipped + fast_remaining:
        raise ValueError('Fast scope invariant failed')
    if fast_attempted != (
        int(status['fast_completed_fit_count'])
        + int(status['fast_completed_not_fit_count'])
        + int(status['fast_incomplete_count'])
        + int(status['fast_error_count'])
    ):
        raise ValueError('Fast attempted-outcome invariant failed')

    dossier_total = status.get('dossier_total_current_scope')
    if dossier_total is not None:
        if int(dossier_total) != (
            int(status['dossier_accepted_count'])
            + int(status['dossier_pending_count'])
            + int(status['dossier_failed_or_recovery_count'])
        ):
            raise ValueError('Dossier scope invariant failed')

    deep_total = int(status['deep_total_current_coverage_target'])
    deep_first = int(status['deep_first_pass_attempted_count'])
    deep_authoritative = int(status['deep_authoritative_completed_count'])
    if deep_first + int(status['deep_normal_first_pass_remaining_count']) != deep_total:
        raise ValueError('Deep normal first-pass invariant failed')
    if deep_authoritative + int(status['deep_remaining_until_all_authoritative_count']) != deep_total:
        raise ValueError('Deep authoritative completion invariant failed')
    if deep_authoritative != (
        int(status['deep_completed_fit_count']) + int(status['deep_completed_not_fit_count'])
    ):
        raise ValueError('Deep completed-outcome invariant failed')
    if bool(status['deep_normal_first_pass_complete']) != (
        int(status['deep_normal_first_pass_remaining_count']) == 0
    ):
        raise ValueError('Deep normal first-pass completion flag mismatch')
    if bool(status['deep_all_current_authoritative_complete']) != (
        int(status['deep_remaining_until_all_authoritative_count']) == 0
    ):
        raise ValueError('Deep all-authoritative completion flag mismatch')

    if (
        status.get('pass1_active') is not True
        or status.get('pass2_implemented') is not True
        or status.get('pass2_active') is not False
    ):
        raise ValueError('Fast/Deep implementation or activation flags invalid')
    return True

