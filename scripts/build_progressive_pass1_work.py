import json
from datetime import datetime, timezone
from pathlib import Path

import priority_ranking
import progressive_pass1
import progressive_personalization

OUT = Path('data/production/pre_ai/progressive_pass1_work.json')
FAST_ERROR_CODES = {'worker_failure', 'invalid_semantic_result'}


def parse_utc(value):
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace('Z', '+00:00')
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def purchase_score(context):
    purchase = context.get('purchase') or {}
    history = context.get('history') or {}
    game = {
        'current_price_rub': purchase.get('current_price_rub_display'),
        'original_price_rub': purchase.get('original_price_rub_display'),
        'discount_percent': purchase.get('discount_percent'),
        'historical_minimum_rub': history.get('minimum_rub_display'),
        'history_quality': history.get('quality') or 'unverified',
        'wishlist': bool((context.get('context_only') or {}).get('wishlist')),
    }
    return float(priority_ranking.build_purchase_breakdown(game).get('purchase_score') or 0)


def build_work_document(now=None):
    progressive_pass1.load_contract()
    now = now or datetime.now(timezone.utc)

    contexts = progressive_pass1.load_jsonl(progressive_pass1.PROGRESSIVE_CONTEXT)
    projection = progressive_pass1.load_json(progressive_pass1.TASTE_PROJECTION)
    queue_rows = progressive_pass1.load_jsonl(progressive_pass1.TASTE_QUEUE)
    state_doc = progressive_pass1.load_state()
    generation, bindings, queue_by_family = progressive_pass1.current_bindings(
        contexts, projection, queue_rows
    )
    state_index = progressive_personalization.build_state_index(
        context_rows=contexts,
        projection_doc=projection,
    )

    pending = []
    cache_resolved = 0
    expired_skipped = 0
    deep_skipped = 0
    missing_binding = []
    fast_attempted = 0
    fast_completed_fit = 0
    fast_completed_not_fit = 0
    fast_incomplete = 0
    fast_error = 0

    for context in contexts:
        family_id = str(context.get('family_id') or '')
        state = state_index.get(family_id) or {}
        sale_end = parse_utc((context.get('purchase') or {}).get('sale_end_utc'))
        if sale_end is not None and sale_end <= now:
            expired_skipped += 1
            continue

        if state.get('analysis_semantic_source') == 'compatible_cache':
            cache_resolved += 1
            continue

        binding = bindings.get(family_id)
        if binding is None:
            if state.get('analysis_state') == 'not_analyzed':
                missing_binding.append(family_id)
            continue

        pass1_entry = progressive_pass1.matching_state_entry(binding, state_doc)
        if pass1_entry is not None:
            fast_attempted += 1
            outcome = pass1_entry.get('outcome')
            if outcome == 'analyzed_fit':
                fast_completed_fit += 1
            elif outcome == 'analyzed_not_fit':
                fast_completed_not_fit += 1
            elif outcome == 'analysis_incomplete':
                if pass1_entry.get('analysis_issue_code') in FAST_ERROR_CODES:
                    fast_error += 1
                else:
                    fast_incomplete += 1
            continue

        # Only a current authoritative completed Deep result suppresses future Fast.
        # Deep waiting/incomplete/recovery never suppresses the independent Fast path.
        if state.get('deep_authoritative_completed') is True:
            deep_skipped += 1
            continue

        queue_row = queue_by_family[family_id]
        semantic_input = {
            'title': queue_row.get('title'),
            'short_description': queue_row.get('short_description'),
            'bundle_members': list(queue_row.get('bundle_members') or []),
            'fit_tags': list(queue_row.get('fit_tags') or []),
            'core_fit_count': int(queue_row.get('core_fit_count') or 0),
            'release_date': queue_row.get('release_date'),
            'semantic_condition': dict(queue_row.get('semantic_condition') or {}),
        }
        item = {
            **binding,
            'semantic_input': semantic_input,
            'submission_path': (
                'data/ai_inbox/progressive_pass1/'
                f"{generation['semantic_generation_id'][:16]}--{binding['work_id']}.json"
            ),
            '_sale_end_sort': sale_end.isoformat() if sale_end else '9999-12-31T23:59:59+00:00',
            '_purchase_score': purchase_score(context),
        }
        pending.append(item)

    if missing_binding:
        raise SystemExit(
            'PASS 1 current not_analyzed items missing semantic queue binding: '
            + ','.join(sorted(missing_binding)[:20])
        )

    pending.sort(key=lambda row: (
        row['_sale_end_sort'],
        -float(row['_purchase_score']),
        row['family_id'],
    ))
    for sequence, item in enumerate(pending, 1):
        item['sequence'] = sequence
        item.pop('_sale_end_sort', None)
        item.pop('_purchase_score', None)

    fast_remaining = len(pending)
    pass1_total_scope = fast_attempted + fast_remaining
    fast_total_current_scope = pass1_total_scope + deep_skipped
    if fast_total_current_scope != fast_attempted + deep_skipped + fast_remaining:
        raise SystemExit('Fast scope accounting mismatch')

    return {
        'schema_version': 2,
        'contract': 'PROGRESSIVE-PASS1-WORK-V1',
        'phase': 'phase_b_pass1',
        'pass1_active': True,
        'pass2_active': True,
        'semantic_generation_id': generation['semantic_generation_id'],
        'semantic_bindings': generation['bindings'],
        'source_mailing_updated_at_utc': projection.get('source_mailing_updated_at_utc'),
        'transport': {
            'mode': 'immutable_item_create_only',
            'one_result_artifact_per_item': True,
            'batch_atomicity': False,
            'maximal_contiguous_prefix': False,
        },
        'scope': {
            # Legacy PASS 1 scope excludes items skipped before an attempt because
            # authoritative Deep already exists, preserving the old arithmetic.
            'pass1_total_scope': pass1_total_scope,
            'pass1_attempted_count': fast_attempted,
            'pass1_remaining_count': fast_remaining,
            'compatible_cache_resolved_count': cache_resolved,
            'expired_before_pass1_count': expired_skipped,
            # Canonical Fast/Dossier/Deep observability.
            'fast_total_current_scope': fast_total_current_scope,
            'fast_attempted_count': fast_attempted,
            'fast_completed_fit_count': fast_completed_fit,
            'fast_completed_not_fit_count': fast_completed_not_fit,
            'fast_incomplete_count': fast_incomplete,
            'fast_error_count': fast_error,
            'fast_skipped_due_to_authoritative_deep_count': deep_skipped,
            'fast_remaining_count': fast_remaining,
        },
        'items': pending,
    }


def main():
    doc = build_work_document()
    scope = doc['scope']
    if scope['pass1_total_scope'] != scope['pass1_attempted_count'] + scope['pass1_remaining_count']:
        raise SystemExit('PASS 1 scope arithmetic mismatch')
    if scope['fast_total_current_scope'] != (
        scope['fast_attempted_count']
        + scope['fast_skipped_due_to_authoritative_deep_count']
        + scope['fast_remaining_count']
    ):
        raise SystemExit('Fast current-scope arithmetic mismatch')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(
        'PROGRESSIVE_PASS1_WORK=READY '
        f"generation={doc['semantic_generation_id']} "
        f"scope={scope['pass1_total_scope']} "
        f"attempted={scope['pass1_attempted_count']} "
        f"remaining={scope['pass1_remaining_count']} "
        f"deep_skipped={scope['fast_skipped_due_to_authoritative_deep_count']} "
        f"cache_resolved={scope['compatible_cache_resolved_count']} "
        f"expired={scope['expired_before_pass1_count']}"
    )


if __name__ == '__main__':
    main()
