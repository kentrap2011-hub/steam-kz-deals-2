import json
import math
import time
from collections import Counter
from pathlib import Path

FAMILIES = Path('data/production/pre_ai/family_graph.json')
FX = Path('data/production/pre_ai/fx_snapshot.json')
HISTORY = Path('data/production/pre_ai/history_snapshot.json')
CONTRACT = Path('config/deal_quality_contract.json')
CONTROL = Path('data/cache/deal_quality.validation.json')
OUT = Path('data/production/pre_ai/deal_scenarios.json')


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def build_price_gate(contract):
    tol = contract['user_price_tolerance']
    base = float(tol['base_target_rub'])
    strong_standard = float(tol['strong_fit']['standard_overage_ceiling_rub'])
    strong_absolute = float(tol['strong_fit']['absolute_ceiling_rub'])
    moderate_absolute = float(tol['moderate_fit']['absolute_ceiling_rub'])

    if not (0 < base <= strong_standard <= strong_absolute):
        raise SystemExit('Invalid strong-fit price thresholds')
    if not (0 < base <= moderate_absolute):
        raise SystemExit('Invalid moderate-fit price thresholds')

    def gate(fit, price_rub, quality):
        if price_rub <= base + 1e-12:
            return True, base, 'base_target'
        if fit == 'strong':
            if price_rub > strong_absolute + 1e-12:
                return False, strong_absolute, 'strong_absolute_ceiling'
            if price_rub <= strong_standard + 1e-12:
                ok = quality in {'record', 'near_record', 'good_vs_history'}
                return ok, strong_standard, 'strong_standard_overage_requires_good_history'
            ok = quality in {'record', 'near_record'}
            return ok, strong_absolute, 'strong_high_overage_requires_record_or_near_record'
        if fit == 'moderate':
            if price_rub > moderate_absolute + 1e-12:
                return False, moderate_absolute, 'moderate_absolute_ceiling'
            ok = quality in {'record', 'near_record'}
            return ok, moderate_absolute, 'moderate_overage_requires_record_or_near_record'
        raise SystemExit(f'Unsupported taste fit scenario: {fit}')

    return gate, {
        'base_target_rub': base,
        'strong_standard_overage_ceiling_rub': strong_standard,
        'strong_absolute_ceiling_rub': strong_absolute,
        'moderate_absolute_ceiling_rub': moderate_absolute,
    }


def assert_boundary_contract(gate, thresholds):
    base = thresholds['base_target_rub']
    ss = thresholds['strong_standard_overage_ceiling_rub']
    sa = thresholds['strong_absolute_ceiling_rub']
    ma = thresholds['moderate_absolute_ceiling_rub']

    checks = [
        (gate('strong', base, 'unverified')[0], True, 'strong base target'),
        (gate('strong', base + 0.01, 'good_vs_history')[0], True, 'strong standard good'),
        (gate('strong', base + 0.01, 'unverified')[0], False, 'strong standard unverified'),
        (gate('strong', ss, 'good_vs_history')[0], True, 'strong standard boundary'),
        (gate('strong', ss + 0.01, 'good_vs_history')[0], False, 'strong high good'),
        (gate('strong', ss + 0.01, 'near_record')[0], True, 'strong high near'),
        (gate('strong', sa + 0.01, 'record')[0], False, 'strong absolute'),
        (gate('moderate', base, 'unverified')[0], True, 'moderate base target'),
        (gate('moderate', base + 0.01, 'near_record')[0], True, 'moderate overage near'),
        (gate('moderate', base + 0.01, 'good_vs_history')[0], False, 'moderate overage good'),
        (gate('moderate', ma + 0.01, 'record')[0], False, 'moderate absolute'),
    ]
    failures = [name for got, expected, name in checks if got != expected]
    if failures:
        raise SystemExit(f'Deal scenario boundary regression: {failures}')


def regime(fit, price, thresholds):
    base = thresholds['base_target_rub']
    if fit == 'strong':
        ss = thresholds['strong_standard_overage_ceiling_rub']
        sa = thresholds['strong_absolute_ceiling_rub']
        if price <= base + 1e-12:
            return 'base'
        if price <= ss + 1e-12:
            return 'standard'
        if price <= sa + 1e-12:
            return 'high'
        return 'over_absolute'
    if fit == 'moderate':
        ma = thresholds['moderate_absolute_ceiling_rub']
        if price <= base + 1e-12:
            return 'base'
        if price <= ma + 1e-12:
            return 'overage'
        return 'over_absolute'
    return 'unsupported'


def compare_control(entries, thresholds):
    if not CONTROL.exists():
        return {'control_available': False}
    control = load(CONTROL)
    old_rows = {}
    for disposition, source_rows in [
        ('INCLUDE', control.get('sorted_recommendations') or []),
        ('EXCLUDE', control.get('price_exclusions') or []),
    ]:
        for row in source_rows:
            key = row.get('primary_key')
            if key:
                old_rows[key] = (disposition, row)

    comparable = []
    mismatches = []
    for key, (old_disposition, old) in old_rows.items():
        new = entries.get(key)
        if not new:
            continue
        fit = old.get('fit_level')
        if fit not in {'strong', 'moderate'}:
            continue
        if old.get('history_quality') != new.get('history_quality'):
            continue
        old_price = old.get('current_price_rub_unrounded')
        if old_price is None:
            continue
        new_price = new['current_price_rub_unrounded']
        if regime(fit, float(old_price), thresholds) != regime(fit, new_price, thresholds):
            continue

        comparable.append(key)
        scenario = new[f'decision_if_{fit}']
        if scenario['final_disposition'] != old_disposition:
            mismatches.append({
                'primary_key': key,
                'kind': 'disposition',
                'fit': fit,
                'old': old_disposition,
                'new': scenario['final_disposition'],
            })
            continue
        if old_disposition == 'INCLUDE' and scenario.get('purchase_decision') != old.get('purchase_decision'):
            mismatches.append({
                'primary_key': key,
                'kind': 'purchase_decision',
                'fit': fit,
                'old': old.get('purchase_decision'),
                'new': scenario.get('purchase_decision'),
            })

    if mismatches:
        raise SystemExit(f'Deal scenarios differ from same-regime validated control: {mismatches[:5]}')

    return {
        'control_available': True,
        'control_row_count': len(old_rows),
        'comparable_same_regime_count': len(comparable),
        'match_count': len(comparable),
        'mismatch_count': 0,
        'match_ratio': 1.0 if comparable else None,
    }


def main():
    started = time.monotonic()
    family_doc = load(FAMILIES)
    fx_doc = load(FX)
    history_doc = load(HISTORY)
    contract = load(CONTRACT)

    if family_doc.get('status') != 'complete' or not family_doc.get('complete_coverage_of_nonexcluded_candidates'):
        raise SystemExit('Pre-AI family graph incomplete')
    if fx_doc.get('status') != 'complete' or not fx_doc.get('complete_coverage'):
        raise SystemExit('Pre-AI FX snapshot incomplete')
    if history_doc.get('status') != 'complete' or not history_doc.get('complete_coverage'):
        raise SystemExit('Pre-AI history snapshot incomplete')
    if contract.get('contract') != 'DEAL-QUALITY-AND-SORT-V1':
        raise SystemExit('Unexpected deal quality contract')

    gate, thresholds = build_price_gate(contract)
    assert_boundary_contract(gate, thresholds)
    purchase_decisions = contract.get('purchase_decision') or {}

    families = family_doc.get('families') or []
    fx = fx_doc.get('entries') or {}
    history = history_doc.get('entries') or {}
    entries = {}

    for family in families:
        key = family['primary_key']
        fx_row = fx.get(key)
        history_row = history.get(key)
        if fx_row is None or history_row is None:
            raise SystemExit(f'Missing FX/history prerequisite for {key}')
        price_rub = float(fx_row['final_rub_unrounded'])
        quality = history_row['history_quality']
        decision_label = purchase_decisions.get(quality)
        if not isinstance(decision_label, str):
            raise SystemExit(f'No purchase decision mapping for history quality {quality!r}')

        common = {
            'family_id': family['family_id'],
            'primary_key': key,
            'title': family['primary_title'],
            'current_kzt': float(fx_row['final_kzt']),
            'current_price_rub_unrounded': price_rub,
            'current_price_rub_display': int(fx_row['final_rub_display']),
            'history_quality': quality,
            'historical_min_kzt': history_row.get('historical_min_kzt'),
            'delta_vs_paid_historical_minimum': history_row.get('delta_vs_paid_historical_minimum'),
        }

        for fit in ('strong', 'moderate'):
            allowed, ceiling, reason = gate(fit, price_rub, quality)
            scenario = {
                'assumed_taste_fit': fit,
                'final_disposition': 'INCLUDE' if allowed else 'EXCLUDE',
                'active_price_ceiling_rub': ceiling,
                'price_gate_reason': reason,
            }
            if allowed:
                scenario['purchase_decision'] = decision_label
            else:
                scenario['exclusion_reason_code'] = 'price_clearly_unreasonable_after_soft_target_evaluation'
            common[f'decision_if_{fit}'] = scenario

        entries[key] = common

    expected = {f['primary_key'] for f in families}
    if set(entries) != expected:
        raise SystemExit('Deal scenario primary coverage mismatch')

    strong_counts = Counter(row['decision_if_strong']['final_disposition'] for row in entries.values())
    moderate_counts = Counter(row['decision_if_moderate']['final_disposition'] for row in entries.values())
    control = compare_control(entries, thresholds)

    out = {
        'schema_version': 1,
        'purpose': 'pre_ai_hypothetical_deal_decisions_for_final_taste_fit',
        'status': 'complete',
        'family_count': len(families),
        'scenario_count': len(entries) * 2,
        'complete_coverage': True,
        'external_calls': 0,
        'thresholds': thresholds,
        'strong_disposition_counts': dict(sorted(strong_counts.items())),
        'moderate_disposition_counts': dict(sorted(moderate_counts.items())),
        'validated_control_comparison': control,
        'entries': entries,
        'elapsed_seconds': round(time.monotonic() - started, 3),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')

    print(json.dumps({
        'status': out['status'],
        'family_count': out['family_count'],
        'scenario_count': out['scenario_count'],
        'complete_coverage': out['complete_coverage'],
        'external_calls': out['external_calls'],
        'thresholds': thresholds,
        'strong_disposition_counts': out['strong_disposition_counts'],
        'moderate_disposition_counts': out['moderate_disposition_counts'],
        'control': control,
        'elapsed_seconds': out['elapsed_seconds'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
