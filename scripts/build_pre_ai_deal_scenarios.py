import json
import time
from collections import Counter
from pathlib import Path

FAMILIES = Path('data/production/pre_ai/family_graph.json')
STORE = Path('data/production/pre_ai/store_snapshot.json')
FX = Path('data/production/pre_ai/fx_snapshot.json')
HISTORY = Path('data/production/pre_ai/history_snapshot.json')
CONTRACT = Path('config/deal_quality_contract.json')
OUT = Path('data/production/pre_ai/deal_scenarios.json')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    started = time.monotonic()
    family_doc = load(FAMILIES)
    store_doc = load(STORE)
    fx_doc = load(FX)
    history_doc = load(HISTORY)
    contract = load(CONTRACT)

    if family_doc.get('status') != 'complete' or not family_doc.get('complete_coverage_of_nonexcluded_candidates'):
        raise SystemExit('Pre-AI family graph incomplete')
    if store_doc.get('status') != 'complete':
        raise SystemExit('Pre-AI Store snapshot incomplete')
    if fx_doc.get('status') != 'complete' or not fx_doc.get('complete_coverage'):
        raise SystemExit('Pre-AI FX snapshot incomplete')
    if history_doc.get('status') != 'complete' or not history_doc.get('complete_coverage'):
        raise SystemExit('Pre-AI history snapshot incomplete')
    if contract.get('contract') != 'DEAL-QUALITY-AND-SORT-V1' or contract.get('version') != '1.1':
        raise SystemExit('Unexpected deal quality contract')

    symbolic_max = int(contract['commercial_visibility_gate']['symbolic_discount_max_percent_inclusive'])
    if symbolic_max < 0 or symbolic_max > 20:
        raise SystemExit('Invalid symbolic discount threshold')

    purchase_decisions = contract.get('purchase_decision') or {}
    families = family_doc.get('families') or []
    store = store_doc.get('entries') or {}
    fx = fx_doc.get('entries') or {}
    history = history_doc.get('entries') or {}
    entries = {}

    for family in families:
        key = family['primary_key']
        store_row = store.get(key)
        fx_row = fx.get(key)
        history_row = history.get(key)
        if store_row is None or fx_row is None or history_row is None:
            raise SystemExit(f'Missing Store/FX/history prerequisite for {key}')

        discount_percent = int(store_row.get('discount_percent') or 0)
        price_rub = float(fx_row['final_rub_unrounded'])
        quality = history_row['history_quality']
        decision_label = purchase_decisions.get(quality)
        if not isinstance(decision_label, str):
            raise SystemExit(f'No purchase decision mapping for history quality {quality!r}')

        symbolic = discount_percent <= symbolic_max
        common = {
            'family_id': family['family_id'],
            'primary_key': key,
            'title': family['primary_title'],
            'discount_percent': discount_percent,
            'current_kzt': float(fx_row['final_kzt']),
            'current_price_rub_unrounded': price_rub,
            'current_price_rub_display': int(fx_row['final_rub_display']),
            'history_quality': quality,
            'historical_min_kzt': history_row.get('historical_min_kzt'),
            'delta_vs_paid_historical_minimum': history_row.get('delta_vs_paid_historical_minimum'),
            'symbolic_discount': symbolic,
        }

        for fit in ('strong', 'moderate'):
            if symbolic:
                scenario = {
                    'assumed_taste_fit': fit,
                    'final_disposition': 'EXCLUDE',
                    'active_price_ceiling_rub': None,
                    'price_gate_reason': 'symbolic_discount_at_or_below_user_threshold',
                    'exclusion_reason_code': 'symbolic_discount_not_worth_mailing_attention',
                }
            else:
                scenario = {
                    'assumed_taste_fit': fit,
                    'final_disposition': 'INCLUDE',
                    'active_price_ceiling_rub': None,
                    'price_gate_reason': 'no_hard_price_cap_non_symbolic_discount',
                    'purchase_decision': decision_label,
                }
            common[f'decision_if_{fit}'] = scenario

        entries[key] = common

    expected = {f['primary_key'] for f in families}
    if set(entries) != expected:
        raise SystemExit('Deal scenario primary coverage mismatch')

    strong_counts = Counter(row['decision_if_strong']['final_disposition'] for row in entries.values())
    moderate_counts = Counter(row['decision_if_moderate']['final_disposition'] for row in entries.values())
    symbolic_count = sum(1 for row in entries.values() if row['symbolic_discount'])

    out = {
        'schema_version': 2,
        'purpose': 'pre_ai_deal_context_without_hard_price_caps',
        'status': 'complete',
        'family_count': len(families),
        'scenario_count': len(entries) * 2,
        'complete_coverage': True,
        'external_calls': 0,
        'commercial_visibility_gate': {
            'symbolic_discount_max_percent_inclusive': symbolic_max,
            'symbolic_discount_count': symbolic_count,
            'non_symbolic_offers_are_not_removed_by_price_alone': True,
        },
        'strong_disposition_counts': dict(sorted(strong_counts.items())),
        'moderate_disposition_counts': dict(sorted(moderate_counts.items())),
        'legacy_hard_price_cap_control_intentionally_retired': True,
        'entries': entries,
        'elapsed_seconds': round(time.monotonic() - started, 3),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')

    print(json.dumps({
        'status': out['status'],
        'family_count': out['family_count'],
        'scenario_count': out['scenario_count'],
        'symbolic_discount_count': symbolic_count,
        'strong_disposition_counts': out['strong_disposition_counts'],
        'moderate_disposition_counts': out['moderate_disposition_counts'],
        'elapsed_seconds': out['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
