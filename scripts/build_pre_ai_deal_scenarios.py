import json
import math
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


def build_gate(contract):
    gate_cfg = contract['commercial_visibility_gate']
    tol = contract['user_price_tolerance']
    symbolic_max = int(gate_cfg['symbolic_discount_max_percent_inclusive'])
    base = float(tol['base_target_rub'])
    exceptional_discount = int(tol['exceptional_discount_min_percent'])
    strong_standard = float(tol['strong_fit']['standard_overage_ceiling_rub'])
    strong_absolute = float(tol['strong_fit']['absolute_ceiling_rub'])
    moderate_absolute = float(tol['moderate_fit']['absolute_ceiling_rub'])

    if not (0 <= symbolic_max <= 20):
        raise SystemExit('Invalid symbolic discount threshold')
    if not (0 < base <= moderate_absolute <= strong_standard <= strong_absolute):
        raise SystemExit('Invalid price thresholds')
    if not (50 <= exceptional_discount <= 95):
        raise SystemExit('Invalid exceptional discount threshold')

    missing_history = {'unverified', 'previously_free'}

    def gate(fit, price_rub, quality, discount_percent):
        if discount_percent <= symbolic_max:
            return False, None, 'symbolic_discount_at_or_below_user_threshold'

        if price_rub <= base + 1e-12:
            return True, base, 'within_normal_budget_target'

        if fit == 'strong':
            if price_rub > strong_absolute + 1e-12:
                return False, strong_absolute, 'strong_absolute_budget_ceiling'
            if price_rub <= strong_standard + 1e-12:
                if quality == 'well_above_history':
                    return True, strong_standard, 'strong_standard_overage_known_weak_history_wait'
                return True, strong_standard, 'strong_standard_overage_with_value_support_or_missing_history'

            # The 650..750 band is intentionally exceptional: strong taste + huge discount.
            if discount_percent < exceptional_discount:
                return False, strong_absolute, 'strong_high_overage_requires_exceptional_discount'
            if quality in {'record', 'near_record'} | missing_history:
                return True, strong_absolute, 'strong_high_overage_exceptional_discount'
            return False, strong_absolute, 'strong_high_overage_known_history_not_near_record'

        if fit == 'moderate':
            if price_rub > moderate_absolute + 1e-12:
                return False, moderate_absolute, 'moderate_absolute_budget_ceiling'
            if quality == 'well_above_history':
                return True, moderate_absolute, 'moderate_small_overage_known_weak_history_wait'
            return True, moderate_absolute, 'moderate_small_overage_allowed'

        raise SystemExit(f'Unsupported taste fit scenario: {fit}')

    return gate, {
        'symbolic_discount_max_percent_inclusive': symbolic_max,
        'base_target_rub': base,
        'exceptional_discount_min_percent': exceptional_discount,
        'strong_standard_overage_ceiling_rub': strong_standard,
        'strong_absolute_ceiling_rub': strong_absolute,
        'moderate_absolute_ceiling_rub': moderate_absolute,
    }


def assert_boundary_contract(gate, t):
    base = t['base_target_rub']
    ss = t['strong_standard_overage_ceiling_rub']
    sa = t['strong_absolute_ceiling_rub']
    ma = t['moderate_absolute_ceiling_rub']
    ed = t['exceptional_discount_min_percent']
    sm = t['symbolic_discount_max_percent_inclusive']

    checks = [
        (gate('strong', base, 'unverified', sm)[0], False, 'symbolic discount excludes'),
        (gate('strong', base, 'unverified', sm + 1)[0], True, 'base target survives'),
        (gate('strong', ss, 'good_vs_history', sm + 1)[0], True, 'strong standard good history'),
        (gate('strong', ss, 'unverified', sm + 1)[0], True, 'strong standard missing history nonblocking'),
        (gate('strong', ss, 'well_above_history', sm + 1)[0], True, 'strong standard weak history remains wait'),
        (gate('strong', ss + 0.01, 'record', ed - 1)[0], False, 'high band requires exceptional discount'),
        (gate('strong', ss + 0.01, 'record', ed)[0], True, 'high band exceptional discount record'),
        (gate('strong', ss + 0.01, 'unverified', ed)[0], True, 'high band missing history nonblocking'),
        (gate('strong', ss + 0.01, 'good_vs_history', ed)[0], False, 'high band known not-near history fails'),
        (gate('strong', sa + 0.01, 'record', 95)[0], False, '750 absolute ceiling'),
        (gate('moderate', base, 'unverified', sm + 1)[0], True, 'moderate base target'),
        (gate('moderate', ma, 'near_record', sm + 1)[0], True, 'moderate overage near record'),
        (gate('moderate', ma, 'unverified', sm + 1)[0], True, 'moderate missing history nonblocking'),
        (gate('moderate', ma, 'well_above_history', sm + 1)[0], True, 'moderate weak history remains wait'),
        (gate('moderate', ma + 0.01, 'record', 95)[0], False, 'moderate absolute ceiling'),
    ]
    failures = [name for got, expected, name in checks if got != expected]
    if failures:
        raise SystemExit(f'Deal scenario boundary regression: {failures}')


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
    if contract.get('contract') != 'DEAL-QUALITY-AND-SORT-V1' or contract.get('version') != '1.3':
        raise SystemExit('Unexpected deal quality contract')

    gate, thresholds = build_gate(contract)
    assert_boundary_contract(gate, thresholds)
    purchase_decisions = contract.get('purchase_decision') or {}
    priority_buckets = (contract.get('final_ranking_principles') or {}).get('qualitative_priority_buckets') or {}

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
        if not math.isfinite(price_rub) or price_rub <= 0:
            raise SystemExit(f'Invalid RUB price for {key}')
        quality = history_row['history_quality']
        decision_label = purchase_decisions.get(quality)
        if not isinstance(decision_label, str):
            raise SystemExit(f'No purchase decision mapping for history quality {quality!r}')

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
        }

        for fit in ('strong', 'moderate'):
            allowed, ceiling, reason = gate(fit, price_rub, quality, discount_percent)
            scenario = {
                'assumed_taste_fit': fit,
                'final_disposition': 'INCLUDE' if allowed else 'EXCLUDE',
                'active_price_ceiling_rub': ceiling,
                'price_gate_reason': reason,
            }
            if allowed:
                scenario['purchase_decision'] = decision_label
                try:
                    scenario['priority_bucket'] = int(priority_buckets[fit][decision_label])
                except Exception as exc:
                    raise SystemExit(f'Missing qualitative priority bucket for {fit}/{decision_label}: {exc}')
            else:
                if reason == 'symbolic_discount_at_or_below_user_threshold':
                    scenario['exclusion_reason_code'] = 'symbolic_discount_not_worth_mailing_attention'
                else:
                    scenario['exclusion_reason_code'] = 'price_clearly_unreasonable_after_soft_target_evaluation'
            common[f'decision_if_{fit}'] = scenario

        entries[key] = common

    expected = {f['primary_key'] for f in families}
    if set(entries) != expected:
        raise SystemExit('Deal scenario primary coverage mismatch')

    strong_counts = Counter(row['decision_if_strong']['final_disposition'] for row in entries.values())
    moderate_counts = Counter(row['decision_if_moderate']['final_disposition'] for row in entries.values())
    reason_counts = Counter(
        row[scenario]['price_gate_reason']
        for row in entries.values()
        for scenario in ('decision_if_strong', 'decision_if_moderate')
    )

    out = {
        'schema_version': 3,
        'purpose': 'pre_ai_budget_aware_hypothetical_deal_decisions_for_final_taste_fit',
        'status': 'complete',
        'family_count': len(families),
        'scenario_count': len(entries) * 2,
        'complete_coverage': True,
        'external_calls': 0,
        'thresholds': thresholds,
        'strong_disposition_counts': dict(sorted(strong_counts.items())),
        'moderate_disposition_counts': dict(sorted(moderate_counts.items())),
        'gate_reason_counts': dict(sorted(reason_counts.items())),
        'absolute_user_budget_ceiling_rub': thresholds['strong_absolute_ceiling_rub'],
        'qualitative_priority_buckets': priority_buckets,
        'entries': entries,
        'elapsed_seconds': round(time.monotonic() - started, 3),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')

    print(json.dumps({
        'status': out['status'],
        'family_count': out['family_count'],
        'scenario_count': out['scenario_count'],
        'thresholds': thresholds,
        'strong_disposition_counts': out['strong_disposition_counts'],
        'moderate_disposition_counts': out['moderate_disposition_counts'],
        'gate_reason_counts': out['gate_reason_counts'],
        'elapsed_seconds': out['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
