import json
from datetime import datetime, timezone
from pathlib import Path

import priority_ranking
import progressive_pass1
import progressive_personalization

OUT = Path('data/production/pre_ai/progressive_pass1_work.json')


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

    current_scope = []
    pending = []
    cache_resolved = 0
    expired_skipped = 0
    missing_binding = []

    for context in contexts:
        family_id = str(context.get('family_id') or '')
        state = state_index.get(family_id) or {}
        sale_end = parse_utc((context.get('purchase') or {}).get('sale_end_utc'))
        if sale_end is not None and sale_end <= now:
            expired_skipped += 1
            continue

        source = state.get('analysis_semantic_source')
        if source == 'compatible_cache':
            cache_resolved += 1
            continue

        binding = bindings.get(family_id)
        pass1_entry = progressive_pass1.matching_state_entry(binding, state_doc) if binding else None
        if binding is None:
            if state.get('analysis_state') == 'not_analyzed':
                missing_binding.append(family_id)
            continue

        # Once an item is part of PASS 1 scope for this current binding, it remains
        # in the scope accounting after its single accepted attempt.
        current_scope.append(family_id)
        if pass1_entry is not None:
            continue
        if state.get('analysis_state') != 'not_analyzed':
            # Current exact cache or another trustworthy semantic source already
            # resolved this item; do not invoke PASS 1 redundantly.
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

    attempted = len(current_scope) - len(pending)
    if attempted < 0:
        raise SystemExit('PASS 1 attempted accounting underflow')

    return {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS1-WORK-V1',
        'phase': 'phase_b_pass1',
        'pass1_active': True,
        'pass2_active': False,
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
            'pass1_total_scope': len(current_scope),
            'pass1_attempted_count': attempted,
            'pass1_remaining_count': len(pending),
            'compatible_cache_resolved_count': cache_resolved,
            'expired_before_pass1_count': expired_skipped,
        },
        'items': pending,
    }


def main():
    doc = build_work_document()
    scope = doc['scope']
    if scope['pass1_total_scope'] != scope['pass1_attempted_count'] + scope['pass1_remaining_count']:
        raise SystemExit('PASS 1 scope arithmetic mismatch')
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(
        'PROGRESSIVE_PASS1_WORK=READY '
        f"generation={doc['semantic_generation_id']} "
        f"scope={scope['pass1_total_scope']} "
        f"attempted={scope['pass1_attempted_count']} "
        f"remaining={scope['pass1_remaining_count']} "
        f"cache_resolved={scope['compatible_cache_resolved_count']} "
        f"expired={scope['expired_before_pass1_count']}"
    )


if __name__ == '__main__':
    main()
