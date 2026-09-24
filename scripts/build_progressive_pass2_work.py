import json
from datetime import datetime, timezone
from pathlib import Path

import priority_ranking
import progressive_pass1
import progressive_pass2


OUT = Path('data/production/pre_ai/progressive_pass2_work.json')


def parse_utc(value):
    return progressive_pass2.parse_utc(value)


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

    items = []
    for item in recomputed['items']:
        context = context_by_family.get(item['family_id']) or {}
        sale_end = parse_utc((context.get('purchase') or {}).get('sale_end_utc'))
        item = dict(item)
        item['_sale_end_sort'] = sale_end.isoformat() if sale_end else '9999-12-31T23:59:59+00:00'
        item['_purchase_score'] = purchase_score(context)
        items.append(item)

    items.sort(key=lambda row: (
        row['_sale_end_sort'],
        -float(row['_purchase_score']),
        row['family_id'],
    ))
    for sequence, item in enumerate(items, 1):
        item['sequence'] = sequence
        item.pop('_sale_end_sort', None)
        item.pop('_purchase_score', None)

    counts = dict(recomputed['counts'])
    if counts['pass2_eligible_count'] != len(items):
        raise SystemExit('PASS 2 eligibility count mismatch')

    return {
        'schema_version': 2,
        'contract': 'PROGRESSIVE-PASS2-WORK-V1',
        'phase': 'phase_c_pass2',
        'implemented': True,
        'pass1_active': True,
        'pass2_active': bool(contract.get('active')),
        'projection_status': 'current_github_owned_fast_dossier_deep_v1_projection',
        'semantic_generation_id': recomputed['semantic_generation_id'],
        'semantic_bindings': recomputed['semantic_bindings'],
        'profile_pin': recomputed['profile_pin'],
        'dossier_compatibility_binding': binding,
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
