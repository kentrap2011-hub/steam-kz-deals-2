import json
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def replace_once(path, old, new):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Expected snippet not found in {path}: {old[:120]!r}')
    if text.count(old) != 1:
        raise SystemExit(f'Expected exactly one snippet in {path}, found {text.count(old)}')
    p.write_text(text.replace(old, new), encoding='utf-8')


# Canonical policy: make the existing 60/40 principle operational without a fake numeric score.
policy = load_json('config/mailing_policy.json')
if policy.get('version') not in {'1.17', '1.18'}:
    raise SystemExit(f"Unexpected mailing policy version: {policy.get('version')}")
policy['version'] = '1.18'

pricing = policy['pricing']
pricing['weak_but_non_symbolic_deal_remains_available_for_wait_or_low_priority'] = (
    'within_standard_fit_budget_band'
)

sorting = policy['sorting']
sorting['ranking_method'] = 'explicit_qualitative_60_40_matrix_no_hidden_numeric_score'
sorting['purchase_decision_order_is_not_primary_sort'] = True
sorting['qualitative_priority_buckets'] = [
    {'bucket': 1, 'taste_fit': 'strong', 'purchase_decision': 'БРАТЬ СЕЙЧАС'},
    {'bucket': 2, 'taste_fit': 'strong', 'purchase_decision': 'МОЖНО БРАТЬ'},
    {'bucket': 3, 'taste_fit': 'moderate', 'purchase_decision': 'БРАТЬ СЕЙЧАС'},
    {'bucket': 4, 'taste_fit': 'strong', 'purchase_decision': 'ЛУЧШЕ ЖДАТЬ'},
    {'bucket': 5, 'taste_fit': 'moderate', 'purchase_decision': 'МОЖНО БРАТЬ'},
    {'bucket': 6, 'taste_fit': 'moderate', 'purchase_decision': 'ЛУЧШЕ ЖДАТЬ'},
]
sorting['primary_order'] = ['priority_bucket_asc']
sorting['within_priority_bucket_order'] = [
    'wishlist_desc',
    'price_quality_vs_history_desc',
    'best_variant_value_desc',
    'discount_percent_desc',
    'current_price_rub_asc',
    'title_asc',
]
sorting['weak_non_symbolic_deal_should_rank_low_or_wait_not_disappear'] = (
    'within_standard_fit_budget_band'
)

deal = policy['deal_selection']
deal['weak_non_symbolic_deal_within_standard_fit_band_remains_visible_as_wait_or_low_priority'] = True
deal['strong_standard_fit_band_max_rub'] = 650
deal['moderate_standard_fit_band_max_rub'] = 550
deal['high_overage_650_to_750_requires_strong_taste_and_exceptional_discount'] = True

policy['final_self_check']['qualitative_60_40_priority_bucket_applied'] = True
save_json('config/mailing_policy.json', policy)

# Implementation contract.
contract = load_json('config/deal_quality_contract.json')
if contract.get('version') not in {'1.2', '1.3'}:
    raise SystemExit(f"Unexpected deal contract version: {contract.get('version')}")
contract['version'] = '1.3'
contract['user_price_tolerance']['strong_fit']['rules'] = [
    'price <= 500 RUB is within the normal budget target after the symbolic-discount gate',
    '500 < price <= 650 RUB remains eligible for strong taste; weak history becomes ЛУЧШЕ ЖДАТЬ instead of disappearing',
    '650 < price <= 750 RUB is allowed only for strong taste fit, discount >= 75%, and record or near-record history when exact history is available',
    'price > 750 RUB is always excluded regardless of taste or discount',
]
contract['user_price_tolerance']['moderate_fit']['rules'] = [
    'price <= 500 RUB is within the normal budget target after the symbolic-discount gate',
    '500 < price <= 550 RUB remains eligible for moderate taste; weak history becomes ЛУЧШЕ ЖДАТЬ instead of disappearing',
    'price > 550 RUB is excluded for moderate taste fit',
]
contract['final_ranking_principles']['ranking_method'] = 'explicit_qualitative_60_40_matrix_no_hidden_numeric_score'
contract['final_ranking_principles']['qualitative_priority_buckets'] = {
    'strong': {
        'БРАТЬ СЕЙЧАС': 1,
        'МОЖНО БРАТЬ': 2,
        'ЛУЧШЕ ЖДАТЬ': 4,
    },
    'moderate': {
        'БРАТЬ СЕЙЧАС': 3,
        'МОЖНО БРАТЬ': 5,
        'ЛУЧШЕ ЖДАТЬ': 6,
    },
}
contract['final_ranking_principles']['wishlist_role'] = 'tie_breaker_within_priority_bucket_only'
save_json('config/deal_quality_contract.json', contract)

# Deal gates: standard fit-scaled budget bands no longer erase weak-history candidates.
deal_script = 'scripts/build_pre_ai_deal_scenarios.py'
replace_once(
    deal_script,
    """            if price_rub <= strong_standard + 1e-12:\n                if quality in {'record', 'near_record', 'good_vs_history'} | missing_history:\n                    return True, strong_standard, 'strong_standard_overage_with_value_support_or_missing_history'\n                return False, strong_standard, 'strong_standard_overage_known_weak_history'\n""",
    """            if price_rub <= strong_standard + 1e-12:\n                if quality == 'well_above_history':\n                    return True, strong_standard, 'strong_standard_overage_known_weak_history_wait'\n                return True, strong_standard, 'strong_standard_overage_with_value_support_or_missing_history'\n""",
)
replace_once(
    deal_script,
    """        if fit == 'moderate':\n            if price_rub > moderate_absolute + 1e-12:\n                return False, moderate_absolute, 'moderate_absolute_budget_ceiling'\n            if quality in {'record', 'near_record'} | missing_history:\n                return True, moderate_absolute, 'moderate_small_overage_record_or_missing_history'\n            return False, moderate_absolute, 'moderate_small_overage_known_history_not_near_record'\n""",
    """        if fit == 'moderate':\n            if price_rub > moderate_absolute + 1e-12:\n                return False, moderate_absolute, 'moderate_absolute_budget_ceiling'\n            if quality == 'well_above_history':\n                return True, moderate_absolute, 'moderate_small_overage_known_weak_history_wait'\n            return True, moderate_absolute, 'moderate_small_overage_allowed'\n""",
)
replace_once(
    deal_script,
    """        (gate('strong', ss, 'unverified', sm + 1)[0], True, 'strong standard missing history nonblocking'),\n""",
    """        (gate('strong', ss, 'unverified', sm + 1)[0], True, 'strong standard missing history nonblocking'),\n        (gate('strong', ss, 'well_above_history', sm + 1)[0], True, 'strong standard weak history remains wait'),\n""",
)
replace_once(
    deal_script,
    """        (gate('moderate', ma, 'unverified', sm + 1)[0], True, 'moderate missing history nonblocking'),\n""",
    """        (gate('moderate', ma, 'unverified', sm + 1)[0], True, 'moderate missing history nonblocking'),\n        (gate('moderate', ma, 'well_above_history', sm + 1)[0], True, 'moderate weak history remains wait'),\n""",
)
replace_once(
    deal_script,
    "contract.get('version') != '1.2'",
    "contract.get('version') != '1.3'",
)
replace_once(
    deal_script,
    """    purchase_decisions = contract.get('purchase_decision') or {}\n\n    families = family_doc.get('families') or []\n""",
    """    purchase_decisions = contract.get('purchase_decision') or {}\n    priority_buckets = (contract.get('final_ranking_principles') or {}).get('qualitative_priority_buckets') or {}\n\n    families = family_doc.get('families') or []\n""",
)
replace_once(
    deal_script,
    """            if allowed:\n                scenario['purchase_decision'] = decision_label\n            else:\n""",
    """            if allowed:\n                scenario['purchase_decision'] = decision_label\n                try:\n                    scenario['priority_bucket'] = int(priority_buckets[fit][decision_label])\n                except Exception as exc:\n                    raise SystemExit(f'Missing qualitative priority bucket for {fit}/{decision_label}: {exc}')\n            else:\n""",
)
replace_once(
    deal_script,
    """        'absolute_user_budget_ceiling_rub': thresholds['strong_absolute_ceiling_rub'],\n        'entries': entries,\n""",
    """        'absolute_user_budget_ceiling_rub': thresholds['strong_absolute_ceiling_rub'],\n        'qualitative_priority_buckets': priority_buckets,\n        'entries': entries,\n""",
)

# Consumer payload exposes the precomputed bucket, so the night task does not recalculate it.
payload_script = 'scripts/build_pre_ai_chatgpt_payload.py'
replace_once(
    payload_script,
    """    if scenario['final_disposition'] == 'INCLUDE':\n        out['purchase_decision'] = scenario['purchase_decision']\n""",
    """    if scenario['final_disposition'] == 'INCLUDE':\n        out['purchase_decision'] = scenario['purchase_decision']\n        out['priority_bucket'] = int(scenario['priority_bucket'])\n""",
)
replace_once(
    payload_script,
    """                context['resolved_taste_fit'] = fit\n                context['final_purchase_decision'] = selected['purchase_decision']\n                ready_context.append(context)\n""",
    """                context['resolved_taste_fit'] = fit\n                context['final_purchase_decision'] = selected['purchase_decision']\n                context['final_priority_bucket'] = int(selected['priority_bucket'])\n                ready_context.append(context)\n""",
)
replace_once(
    payload_script,
    """            'chatgpt_selects_precomputed_deal_scenario_from_final_taste_fit': True,\n""",
    """            'chatgpt_selects_precomputed_deal_scenario_from_final_taste_fit': True,\n            'qualitative_60_40_priority_bucket_is_precomputed': True,\n            'smaller_priority_bucket_means_higher_purchase_priority': True,\n""",
)

# Night contract: use the bucket as the primary order; wishlist only breaks ties inside a bucket.
daily = load_json('config/daily_execution_contract.json')
resp = daily['night_preparation']['responsibilities']
rank_rule = 'sort eligible paid candidates by precomputed final_priority_bucket ascending; within the same bucket prefer wishlist, then stronger history value, larger discount, lower price, then title'
if rank_rule not in resp:
    resp.insert(3, rank_rule)
save_json('config/daily_execution_contract.json', daily)

# Permanent human-readable rule entry.
rules_path = Path('PROJECT_RULES.md')
rules_text = rules_path.read_text(encoding='utf-8')
anchor = 'Зона ближе к верхнему пределу 750 ₽ предназначена только для действительно сильного вкусового совпадения и очень большой скидки относительно обычной цены. Операционный ориентир для «очень большой скидки» — 75% и выше. Скидка не повышает вкусовую оценку и не может спасти игру, которая сама по себе пользователю не подходит.\n'
addition = '\nВ стандартном диапазоне небольшого превышения бюджета слабая история цены сама по себе не удаляет подходящую игру: сильное вкусовое совпадение до 650 ₽ и умеренное до 550 ₽ могут оставаться в рассылке с решением «ЛУЧШЕ ЖДАТЬ». Зона 650–750 ₽ остаётся исключительной и требует сильного вкусового совпадения и скидки не меньше 75%; выше 750 ₽ предложение исключается.\n\nДля ориентира 60/40 используется явная качественная матрица вместо скрытого числового балла: сильное попадание + «БРАТЬ СЕЙЧАС», сильное + «МОЖНО БРАТЬ», умеренное + «БРАТЬ СЕЙЧАС», сильное + «ЛУЧШЕ ЖДАТЬ», умеренное + «МОЖНО БРАТЬ», умеренное + «ЛУЧШЕ ЖДАТЬ». Wishlist применяется только как дополнительный приоритет внутри одной такой группы.\n'
if addition.strip() not in rules_text:
    if anchor not in rules_text:
        raise SystemExit('PROJECT_RULES anchor not found')
    rules_text = rules_text.replace(anchor, anchor + addition, 1)
    rules_path.write_text(rules_text, encoding='utf-8')

# Validator follows the canonical policy version and locks the new invariants.
validator = 'scripts/validate_mailing_policy.py'
replace_once(validator, "p.get('version') == '1.17'", "p.get('version') == '1.18'")
replace_once(
    validator,
    """        'budget_before_ranking': sorting['absolute_budget_ceiling_applied_before_ranking'] is True,\n""",
    """        'budget_before_ranking': sorting['absolute_budget_ceiling_applied_before_ranking'] is True,\n        'qualitative_ranking_method': sorting['ranking_method'] == 'explicit_qualitative_60_40_matrix_no_hidden_numeric_score',\n        'qualitative_bucket_count': len(sorting['qualitative_priority_buckets']) == 6,\n        'strong_standard_weak_deal_waits': deal['weak_non_symbolic_deal_within_standard_fit_band_remains_visible_as_wait_or_low_priority'] is True,\n""",
)

print('Final ranking patch applied successfully')
