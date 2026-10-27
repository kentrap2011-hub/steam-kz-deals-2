import json
import math
from datetime import datetime, timezone
from pathlib import Path

import priority_ranking
import progressive_pass1
import progressive_pass2
import progressive_deep_history


OUT = Path('data/production/pre_ai/progressive_pass2_work.json')
WORK_ORDER_POLICY = Path('config/progressive_pass2_work_order_policy.json')


def parse_utc(value):
    return progressive_pass2.parse_utc(value)


def clamp01(value):
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, numeric))


def review_confidence(review_count, cap):
    try:
        count = max(0.0, float(review_count))
        cap = float(cap)
    except (TypeError, ValueError):
        return 0.0
    if cap <= 0:
        raise ValueError('semantic queue review-confidence cap must be positive')
    return min(1.0, math.log1p(count) / math.log1p(cap))


def current_price_priority(context):
    purchase = context.get('purchase') or {}
    game = {
        'current_price_rub': purchase.get('current_price_rub_display'),
    }
    breakdown = priority_ranking.build_purchase_breakdown(game)
    component = next(
        (
            row for row in (breakdown.get('standalone_purchase_components') or [])
            if row.get('id') == 'price'
        ),
        None,
    )
    if not isinstance(component, dict):
        raise ValueError('canonical current-price purchase component is missing')
    maximum = float(component.get('max_points') or 0)
    if maximum <= 0:
        raise ValueError('canonical current-price purchase component maximum is invalid')
    return clamp01(float(component.get('points') or 0) / maximum)


def semantic_queue_priority(context, ordering):
    policy = ordering.get('priority_score') or {}
    weights = policy.get('weights') or {}
    expected = {
        'steam_positive_rating',
        'steam_review_confidence',
        'current_price',
        'current_discount',
    }
    if set(weights) != expected:
        raise ValueError('semantic queue priority weights do not match canonical factors')
    if abs(sum(float(weights[key]) for key in expected) - float(policy.get('scale') or 0)) > 1e-9:
        raise ValueError('semantic queue priority weights must sum to the canonical scale')

    context_only = context.get('context_only') or {}
    reviews = context_only.get('reviews') or {}
    purchase = context.get('purchase') or {}
    cap = ((policy.get('steam_review_confidence') or {}).get('cap'))
    components = {
        'steam_positive_rating': clamp01(
            (float(reviews.get('global_positive_percent')) / 100.0)
            if reviews.get('global_positive_percent') is not None else 0.0
        ),
        'steam_review_confidence': review_confidence(reviews.get('global_count'), cap),
        'current_price': current_price_priority(context),
        'current_discount': clamp01(
            (float(purchase.get('discount_percent')) / 100.0)
            if purchase.get('discount_percent') is not None else 0.0
        ),
    }
    score = sum(float(weights[key]) * components[key] for key in expected)
    return {
        'score': round(score, 6),
        'components': components,
    }


def load_work_order_policy(path=WORK_ORDER_POLICY):
    policy = json.loads(Path(path).read_text(encoding='utf-8'))
    if policy.get('contract') != 'PROGRESSIVE-PASS2-WORK-ORDER-V1':
        raise ValueError('missing canonical Deep work ordering policy')
    if policy.get('status') != 'canonical' or policy.get('owner') != 'github_control_plane':
        raise ValueError('Deep work ordering must remain GitHub-owned')
    expected = [
        'canonical_purchase_value_desc',
        'steam_global_positive_percent_desc',
        'steam_global_review_count_desc',
        'family_id_asc',
    ]
    if policy.get('never_completed_order') != expected:
        raise ValueError('Deep normal-first-pass work ordering factors are invalid')
    limits = policy.get('constraints') or {}
    for key in ('full_eligible_deep_scope_preserved',):
        if limits.get(key) is not True:
            raise ValueError('Deep eligible scope cannot be reduced by work ordering')
    for key in ('hard_top_n', 'sale_expiry_used_for_order', 'changes_site_ranking',
                'changes_eligibility', 'changes_worker_prompt', 'recovery_attempts_not_reordered'):
        if key == 'recovery_attempts_not_reordered':
            if limits.get(key) is not True:
                raise ValueError('Deep recovery ordering is owned by its existing manifest')
        elif limits.get(key) is not False:
            raise ValueError('Deep work order must not own site/eligibility/expiry')
    return policy


def _numeric_priority(value, *, upper=None):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(number):
        return 0.0
    return min(max(number, 0.0), upper) if upper is not None else max(number, 0.0)


def normal_first_pass_key(context, family_id, final_policy):
    """Strict lexicographic operational order. Does not gate Deep or rank the site."""
    purchase = context.get('purchase') or {}
    reviews = ((context.get('context_only') or {}).get('reviews') or {})
    game = {
        'current_price_rub': purchase.get('current_price_rub_display'),
        'original_price_rub': purchase.get('original_price_rub_display'),
        'historical_minimum_rub': purchase.get('historical_minimum_rub_display'),
        'history_quality': purchase.get('history_quality'),
        'previously_free': purchase.get('previously_free'),
    }
    purchase_value = _numeric_priority(
        priority_ranking.build_purchase_breakdown(game, final_policy)['purchase_score'],
        upper=40.0,
    )
    return (
        -purchase_value,
        -_numeric_priority(reviews.get('global_positive_percent'), upper=100.0),
        -_numeric_priority(reviews.get('global_count')),
        str(family_id),
    )


def entry_has_authoritative_deep_completion(entry):
    return (
        isinstance(entry, dict)
        and entry.get('authoritative_completed') is True
        and entry.get('outcome') in progressive_pass2.AUTHORITATIVE_OUTCOMES
    )


def has_authoritative_deep_history(state_doc, family_id, binding=None):
    entry = ((state_doc.get('entries') or {}).get(str(family_id))) if isinstance(state_doc, dict) else None
    if not isinstance(entry, dict):
        return False
    def exact(snapshot):
        if binding is None:
            return True
        return all(
            str(snapshot.get(key) or '') == str(binding.get(key) or '')
            and str(binding.get(key) or '')
            for key in ('family_id', 'taste_subject_key', 'appid')
        )
    if entry_has_authoritative_deep_completion(entry) and exact(entry):
        return True
    for record in progressive_deep_history.completed_versions(entry):
        if exact(record['result']):
            return True
    for revision in entry.get('revision_history') or []:
        snapshot = (revision or {}).get('state') if isinstance(revision, dict) else None
        if entry_has_authoritative_deep_completion(snapshot) and exact(snapshot):
            return True
    return False


def order_normal_items(items, context_by_family, pass2_state, contract):
    ordering = contract.get('ordering') or {}
    if ordering.get('owner') != 'github' or ordering.get('policy_id') != 'deep_history_first_oldest_success_v1':
        raise ValueError('canonical semantic queue ordering policy is missing')
    if ordering.get('changes_eligibility_or_scope') is not False:
        raise ValueError('semantic queue ordering must not change eligibility or scope')
    if ordering.get('hard_top_n') is not False:
        raise ValueError('semantic queue ordering must not introduce hard top-N')
    if ordering.get('sale_expiry_used_for_priority') is not False:
        raise ValueError('sale expiry must not be a semantic queue priority factor')

    policy = load_work_order_policy()
    if policy.get('precedence') != [
        'never_authoritatively_completed_under_any_profile_first',
        'previously_completed_oldest_last_success_at_utc_first',
    ]:
        raise ValueError('Deep historical first-pass precedence mismatch')
    final_policy = priority_ranking.load_final_policy()
    ordered = []
    for source_item in items:
        item = dict(source_item)
        family_id = str(item.get('family_id') or '')
        context = context_by_family.get(family_id) or {}
        seen = has_authoritative_deep_history(pass2_state, family_id, item)
        last = progressive_deep_history.latest_completed(pass2_state, family_id, item)
        last_at = progressive_pass2.parse_utc(last['accepted_at_utc']) if last else None
        item['_authoritative_deep_history_sort'] = int(seen)
        # Undated legacy evidence is history, not a licence to claim oldest.
        item['_last_completed_sort'] = (
            last_at.isoformat() if last_at else '9999-12-31T23:59:59+00:00'
        )
        item['_work_order_key'] = normal_first_pass_key(context, family_id, final_policy)
        ordered.append(item)

    ordered.sort(key=lambda row: (
        int(row['_authoritative_deep_history_sort']),
        row['_work_order_key'] if not row['_authoritative_deep_history_sort'] else (),
        row['_last_completed_sort'] if row['_authoritative_deep_history_sort'] else '',
        str(row.get('appid') or ''),
        str(row.get('taste_subject_key') or ''),
        str(row.get('family_id') or ''),
    ))
    for sequence, item in enumerate(ordered, 1):
        item['sequence'] = sequence
        item.pop('_authoritative_deep_history_sort', None)
        item.pop('_last_completed_sort', None)
        item.pop('_work_order_key', None)
    return ordered


def build_work_document(now=None):
    contract = progressive_pass2.load_contract()
    now = now or datetime.now(timezone.utc)
    contexts = progressive_pass1.load_jsonl(progressive_pass1.PROGRESSIVE_CONTEXT)
    projection = progressive_pass2.load_json(progressive_pass1.TASTE_PROJECTION)
    queue_rows = progressive_pass1.load_jsonl(progressive_pass1.TASTE_QUEUE)
    pass1_state = progressive_pass1.load_state()
    pass2_state = progressive_pass2.load_state()
    binding = progressive_pass2.current_dossier_binding()

    recomputed = progressive_pass2.recompute_eligibility(
        context_rows=contexts,
        projection_doc=projection,
        queue_rows=queue_rows,
        pass1_state_doc=pass1_state,
        pass2_state_doc=pass2_state,
        current_binding=binding,
        now=now,
    )
    context_by_family = {str(row.get('family_id') or ''): row for row in contexts}

    normal_items = order_normal_items(
        recomputed['items'],
        context_by_family,
        pass2_state,
        contract,
    )

    migration_manifest = progressive_pass2.load_legacy_reanalysis_manifest()
    migration_items, migration_metrics = progressive_pass2.legacy_reanalysis_work_and_metrics(
        pass2_state,
        migration_manifest,
    )
    migration_active = bool(migration_manifest) and not migration_metrics['complete']
    score_manifest = progressive_pass2.load_score_explainability_manifest()
    if score_manifest:
        score_items, score_metrics, score_frozen = progressive_pass2.score_explainability_work_and_metrics(
            pass2_state,
            score_manifest,
        )
    else:
        score_items, score_metrics, score_frozen = [], {
            'migration_id': None,
            'migration_authority_commit': None,
            'total_count': 0,
            'pending_count': 0,
            'submitted_count': 0,
            'accepted_count': 0,
            'accepted_completed_count': 0,
            'incomplete_count': 0,
            'already_compliant_count': 0,
            'stale_or_missing_prior_count': 0,
            'complete': True,
            'exhausted': False,
        }, {}
    if len(score_items) != score_metrics['pending_count']:
        raise ValueError('Deep score migration runnable work/count mismatch')
    if score_metrics['submitted_count'] > score_metrics['pending_count']:
        raise ValueError('Deep score migration submitted/pending accounting mismatch')
    # Keep a frozen migration first only while it has authorized runnable work.
    # A submitted-but-unresolved target is still pending and keeps priority.
    # Frozen stale targets remain visible as exhausted, not falsely completed.
    score_migration_active = (
        bool(score_manifest)
        and not score_metrics['complete']
        and score_metrics['pending_count'] > 0
    )
    if migration_active:
        # The one-off migration freezes its own profile/evidence authority. Keep one
        # homogeneous worker manifest until it terminates; ordinary Deep work is
        # merely paused, not consumed or reordered in its own accounting.
        items = [dict(item) for item in migration_items]
        items.sort(key=lambda row: int(row.get('migration_sequence') or 0))
        for sequence, item in enumerate(items, 1):
            item['sequence'] = sequence
        semantic_generation_id = migration_manifest['semantic_generation_id']
        semantic_bindings = migration_manifest['semantic_bindings']
        profile_pin = migration_manifest['profile_pin']
        dossier_binding = migration_manifest['dossier_compatibility_binding']
        projection_status = 'legacy_full_reanalysis_migration_active'
    elif score_migration_active:
        items = [dict(item) for item in score_items]
        items.sort(key=lambda row: int(row.get('migration_sequence') or 0))
        for sequence, item in enumerate(items, 1):
            item['sequence'] = sequence
        semantic_generation_id = score_frozen['semantic_generation_id']
        semantic_bindings = score_frozen['semantic_bindings']
        profile_pin = score_frozen['profile_pin']
        dossier_binding = score_frozen['dossier_compatibility_binding']
        projection_status = 'score_explainability_migration_active'
    else:
        items = normal_items
        semantic_generation_id = recomputed['semantic_generation_id']
        semantic_bindings = recomputed['semantic_bindings']
        profile_pin = recomputed['profile_pin']
        dossier_binding = binding
        projection_status = 'current_github_owned_fast_dossier_deep_v1_projection'

    counts = dict(recomputed['counts'])
    _, current_bindings, _ = progressive_pass1.current_bindings(contexts, projection, queue_rows)
    current_authoritative = {
        fid for fid, current in current_bindings.items()
        if progressive_pass2.authoritative_completion_entry(current, pass2_state) is not None
    }
    counts.update(progressive_deep_history.version_counts(
        pass2_state,
        current_bindings,
        (projection.get('current_profile') or {}).get('content_sha256'),
        current_authoritative_families=current_authoritative,
    ))
    counts['normal_pass2_eligible_count'] = counts['pass2_eligible_count']
    counts['pass2_eligible_count'] = len(items)
    counts['deep_normal_work_paused_for_legacy_reanalysis'] = migration_active
    counts['deep_normal_work_paused_for_score_explainability_migration'] = score_migration_active
    counts['legacy_full_reanalysis'] = migration_metrics
    counts['score_explainability_migration'] = score_metrics

    return {
        'schema_version': 2,
        'contract': 'PROGRESSIVE-PASS2-WORK-V1',
        'phase': 'phase_c_pass2',
        'implemented': True,
        'pass1_active': True,
        'pass2_active': bool(contract.get('active')),
        'projection_status': projection_status,
        'semantic_generation_id': semantic_generation_id,
        'semantic_bindings': semantic_bindings,
        'profile_pin': profile_pin,
        'dossier_compatibility_binding': dossier_binding,
        'transport': {
            'mode': 'immutable_item_create_only',
            'batch_atomicity': False,
            'maximal_contiguous_prefix': False,
        },
        'scope': counts,
        'items': items,
    }


def main():
    doc = build_work_document()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    scope = doc['scope']
    print(
        'PROGRESSIVE_PASS2_WORK=READY '
        f"active={str(doc['pass2_active']).lower()} "
        f"generation={doc['semantic_generation_id']} "
        f"target={scope['deep_total_current_coverage_target']} "
        f"first_pass_attempted={scope['deep_first_pass_attempted_count']} "
        f"authoritative={scope['deep_authoritative_completed_count']} "
        f"waiting_dossier={scope['deep_waiting_for_dossier_count']} "
        f"ready_or_pending={scope['deep_ready_or_pending_count']} "
        f"recovery_pending={scope['recovery_pending_count']}"
    )


if __name__ == '__main__':
    main()
