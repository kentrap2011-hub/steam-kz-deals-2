import json
from pathlib import Path


def replace_once(path, old, new):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected one anchor, found {count}: {old[:120]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


replace_once(
    'scripts/commercial_reconsideration_bridge.py',
    'from collections import Counter\n\nimport apply_fixed_package_purchase_options as fixed_packages\n',
    'import json\nfrom collections import Counter\nfrom functools import lru_cache\nfrom pathlib import Path\n\nimport apply_fixed_package_purchase_options as fixed_packages\n',
)
replace_once(
    'scripts/commercial_reconsideration_bridge.py',
    "WISHLIST_GOOD_DEAL = 'wishlist_good_deal'\nRECONSIDERABLE_FIXED_PACKAGE = 'reconsiderable_fixed_package_value'\nDIRECT_CONFLICT_REASON = 'exclude_direct_conflict'\nPACKAGE_PURCHASE_DECISION = 'МОЖНО БРАТЬ'\nPACKAGE_PRIORITY_BUCKET = 5\n",
    "WISHLIST_GOOD_DEAL = 'wishlist_good_deal'\nRECONSIDERABLE_FIXED_PACKAGE = 'reconsiderable_fixed_package_value'\nMAILING_POLICY = Path('config/mailing_policy.json')\n",
)
replace_once(
    'scripts/commercial_reconsideration_bridge.py',
    'def hard_taste_block(taste_entry, readiness=None):\n',
    "@lru_cache(maxsize=1)\ndef package_bridge_purchase_fields():\n    policy = json.loads(MAILING_POLICY.read_text(encoding='utf-8'))\n    cfg = ((policy.get('commercial_reconsideration_bridge') or {}).get('reconsiderable_fixed_package_value') or {})\n    decision = cfg.get('purchase_decision_when_bridge_applies')\n    bucket = cfg.get('qualitative_priority_bucket')\n    if not decision or bucket is None:\n        raise ValueError('Canonical reconsiderable package purchase fields are missing')\n    return str(decision), int(bucket)\n\n\ndef hard_taste_block(taste_entry, readiness=None):\n",
)
replace_once(
    'scripts/commercial_reconsideration_bridge.py',
    "        if evidence.get('strict_current_price_savings') is True and evidence.get('comparison_source_aligned') is True:\n            result = _base_bridge(RECONSIDERABLE_FIXED_PACKAGE, readiness)\n            result.update({\n                'commercial_route': 'existing_fixed_package_purchase_option',\n                'package_evidence': evidence,\n                'bridge_purchase_decision': PACKAGE_PURCHASE_DECISION,\n                'bridge_priority_bucket': PACKAGE_PRIORITY_BUCKET,\n                'new_discount_threshold_introduced': False,\n            })\n",
    "        if evidence.get('strict_current_price_savings') is True and evidence.get('comparison_source_aligned') is True:\n            purchase_decision, priority_bucket = package_bridge_purchase_fields()\n            result = _base_bridge(RECONSIDERABLE_FIXED_PACKAGE, readiness)\n            result.update({\n                'commercial_route': 'existing_fixed_package_purchase_option',\n                'package_evidence': evidence,\n                'bridge_purchase_decision': purchase_decision,\n                'bridge_priority_bucket': priority_bucket,\n                'new_discount_threshold_introduced': False,\n            })\n",
)
replace_once(
    'scripts/commercial_reconsideration_bridge.py',
    "def effective_purchase_fields(bridge, moderate_scenario):\n    if isinstance(bridge, dict) and bridge.get('kind') == RECONSIDERABLE_FIXED_PACKAGE:\n        return PACKAGE_PURCHASE_DECISION, PACKAGE_PRIORITY_BUCKET\n    return moderate_scenario.get('purchase_decision'), moderate_scenario.get('priority_bucket')\n",
    "def effective_purchase_fields(bridge, moderate_scenario):\n    if isinstance(bridge, dict) and bridge.get('kind') == RECONSIDERABLE_FIXED_PACKAGE:\n        return package_bridge_purchase_fields()\n    return moderate_scenario.get('purchase_decision'), moderate_scenario.get('priority_bucket')\n",
)

replace_once(
    'scripts/refine_visual_ranking.py',
    'from taste_evidence_contract import evidence_readiness\nfrom taste_negative_contract import structured_grounded_risks\n',
    'from taste_evidence_contract import evidence_readiness\nfrom taste_negative_contract import structured_grounded_risks\nimport commercial_reconsideration_bridge as commercial_bridge\n',
)
replace_once(
    'scripts/refine_visual_ranking.py',
    'def apply_fit_adjustment(game, evidence, risks, taste_entry, projection):\n',
    "def validated_commercial_bridge(context, taste_entry):\n    if not isinstance(context, dict):\n        return None\n    return commercial_bridge.validate_visual_bridge(\n        context,\n        taste_entry if isinstance(taste_entry, dict) else {},\n    )\n\n\ndef apply_fit_adjustment(game, evidence, risks, taste_entry, projection, eligibility_bridge=None):\n",
)
replace_once(
    'scripts/refine_visual_ranking.py',
    "    else:\n        game['taste_confidence'] = 'unknown'\n\n    game['fit'] = fit\n    game['fit_adjustment_reason'] = reason\n",
    "    else:\n        game['taste_confidence'] = 'unknown'\n\n    if isinstance(eligibility_bridge, dict):\n        # Step 3 is an eligibility exception only. Final refinement may add\n        # diagnostics, but must not promote the original below-threshold Taste fit.\n        fit = source_fit\n        reason = 'commercial_eligibility_bridge_preserves_original_taste_fit'\n\n    game['fit'] = fit\n    game['fit_adjustment_reason'] = reason\n",
)
replace_once(
    'scripts/refine_visual_ranking.py',
    "def apply_commercial_branch(game, context):\n    fit = game.get('fit')\n    branch = context.get('deal_if_strong') if fit == 'strong' else context.get('deal_if_moderate')\n    if not isinstance(branch, dict):\n        game['fit_adjustment_commercial_branch_missing'] = True\n        return True\n    if branch.get('disposition') != 'INCLUDE':\n        game['refiner_exclusion_reason'] = branch.get('exclusion_reason_code') or branch.get('price_gate_reason') or 'commercial_branch_exclude'\n        return False\n    if branch.get('purchase_decision'):\n        game['decision'] = branch.get('purchase_decision')\n    if branch.get('priority_bucket') is not None:\n        game['priority_bucket'] = int(branch.get('priority_bucket'))\n    return True\n",
    "def apply_commercial_branch(game, context, eligibility_bridge=None):\n    fit = game.get('fit')\n    branch = context.get('deal_if_strong') if fit == 'strong' else context.get('deal_if_moderate')\n    if not isinstance(branch, dict):\n        game['fit_adjustment_commercial_branch_missing'] = True\n        return True\n    if branch.get('disposition') != 'INCLUDE':\n        game['refiner_exclusion_reason'] = branch.get('exclusion_reason_code') or branch.get('price_gate_reason') or 'commercial_branch_exclude'\n        return False\n    if isinstance(eligibility_bridge, dict):\n        decision, bucket = commercial_bridge.effective_purchase_fields(eligibility_bridge, branch)\n        game['fit'] = 'below_moderate'\n        game['eligibility_override'] = eligibility_bridge.get('kind')\n        game['commercial_eligibility_bridge'] = eligibility_bridge\n        if decision:\n            game['decision'] = decision\n        if bucket is not None:\n            game['priority_bucket'] = int(bucket)\n        return True\n    if branch.get('purchase_decision'):\n        game['decision'] = branch.get('purchase_decision')\n    if branch.get('priority_bucket') is not None:\n        game['priority_bucket'] = int(branch.get('priority_bucket'))\n    return True\n",
)
replace_once(
    'scripts/refine_visual_ranking.py',
    "        old_fit = game.get('fit')\n        apply_fit_adjustment(game, evidence, risks, taste_entry, projection)\n",
    "        eligibility_bridge = validated_commercial_bridge(context, taste_entry)\n        old_fit = game.get('fit')\n        apply_fit_adjustment(game, evidence, risks, taste_entry, projection, eligibility_bridge)\n",
)
replace_once(
    'scripts/refine_visual_ranking.py',
    '        if not apply_commercial_branch(game, context):\n',
    '        if not apply_commercial_branch(game, context, eligibility_bridge):\n',
)

replace_once(
    'scripts/build_final_visual_payload.py',
    "        old_fit = game.get('fit')\n        refiner.apply_fit_adjustment(game, evidence, risks, taste_entry, projection)\n",
    "        eligibility_bridge = refiner.validated_commercial_bridge(context, taste_entry)\n        old_fit = game.get('fit')\n        refiner.apply_fit_adjustment(game, evidence, risks, taste_entry, projection, eligibility_bridge)\n",
)
replace_once(
    'scripts/build_final_visual_payload.py',
    '        if not refiner.apply_commercial_branch(game, context):\n',
    '        if not refiner.apply_commercial_branch(game, context, eligibility_bridge):\n',
)

replace_once(
    'scripts/test_reconsideration_commercial_bridge.py',
    'import play_priority_context\nfrom taste_evidence_contract import current_evidence_contract_sha\n',
    'import play_priority_context\nimport refine_visual_ranking as refiner\nfrom taste_evidence_contract import current_evidence_contract_sha\n',
)
replace_once(
    'scripts/test_reconsideration_commercial_bridge.py',
    "    package_bad = bridge.resolve_bridge(\n        taste_entry=reconsiderable,\n        wishlist=False,\n        moderate_scenario=scenario('ЛУЧШЕ ЖДАТЬ', 'INCLUDE', 6),\n        package_evidence=package_evidence(False),\n    )\n    assert package_bad is None\n\n    highfleet = bridge.resolve_bridge(\n",
    "    package_bad = bridge.resolve_bridge(\n        taste_entry=reconsiderable,\n        wishlist=False,\n        moderate_scenario=scenario('ЛУЧШЕ ЖДАТЬ', 'INCLUDE', 6),\n        package_evidence=package_evidence(False),\n    )\n    assert package_bad is None\n    package_commercial_exclude = bridge.resolve_bridge(\n        taste_entry=reconsiderable,\n        wishlist=False,\n        moderate_scenario=scenario('БРАТЬ СЕЙЧАС', 'EXCLUDE', 3),\n        package_evidence=package_evidence(True),\n    )\n    assert package_commercial_exclude is None\n\n    bioshock = evidence_entry('reconsiderable', 'exclude_direct_conflict')\n    bioshock_bridge = bridge.resolve_bridge(\n        taste_entry=bioshock,\n        wishlist=False,\n        moderate_scenario=scenario('ЛУЧШЕ ЖДАТЬ', 'INCLUDE', 6),\n        package_evidence=package_evidence(True),\n    )\n    assert bioshock_bridge and bioshock_bridge['kind'] == bridge.RECONSIDERABLE_FIXED_PACKAGE\n\n    highfleet = bridge.resolve_bridge(\n",
)
replace_once(
    'scripts/test_reconsideration_commercial_bridge.py',
    "    validated = bridge.validate_visual_bridge(row, insufficient)\n    assert validated and row['risks'] == ['confirmed practical warning']\n\n    print(json.dumps({\n",
    "    validated = bridge.validate_visual_bridge(row, insufficient)\n    assert validated and row['risks'] == ['confirmed practical warning']\n\n    package_row = {\n        'taste_subject_key': 'App_bioshock',\n        'context_only': {'wishlist': False},\n        'deal_if_moderate': scenario('ЛУЧШЕ ЖДАТЬ', 'INCLUDE', 6),\n        'commercial_eligibility_bridge': bioshock_bridge,\n        'risks': ['package route warning must survive'],\n        'risk_provenance': [{'source': 'confirmed_practical'}],\n    }\n    validated_package = bridge.validate_visual_bridge(package_row, bioshock)\n    assert validated_package and package_row['risks'] == ['package route warning must survive']\n    assert package_row['risk_provenance'] == [{'source': 'confirmed_practical'}]\n\n    final_game = {\n        'fit': 'below_moderate',\n        'decision': 'ЛУЧШЕ ЖДАТЬ',\n        'priority_bucket': 6,\n        'risks': list(package_row['risks']),\n        'risk_provenance': list(package_row['risk_provenance']),\n    }\n    final_bridge = refiner.validated_commercial_bridge(package_row, bioshock)\n    assert final_bridge and final_bridge['kind'] == bridge.RECONSIDERABLE_FIXED_PACKAGE\n    refiner.apply_fit_adjustment(\n        final_game,\n        {'rating': 5.0, 'level': 'positive'},\n        {},\n        bioshock,\n        {},\n        final_bridge,\n    )\n    assert final_game['fit'] == 'below_moderate'\n    assert refiner.apply_commercial_branch(final_game, package_row, final_bridge) is True\n    assert final_game['decision'] == 'МОЖНО БРАТЬ' and final_game['priority_bucket'] == 5\n    assert final_game['risks'] == ['package route warning must survive']\n    assert final_game['risk_provenance'] == [{'source': 'confirmed_practical'}]\n\n    print(json.dumps({\n",
)
replace_once(
    'scripts/test_reconsideration_commercial_bridge.py',
    "        'package_without_strict_savings_blocked': True,\n        'highfleet_non_rescuable': True,\n        'strong_positive_unchanged': True,\n        'role_start_priority_invariant': True,\n        'risks_preserved': True,\n",
    "        'package_without_strict_savings_blocked': True,\n        'package_commercial_exclusion_preserved': True,\n        'bioshock_v5_reconsiderable_over_legacy_reason': True,\n        'highfleet_non_rescuable': True,\n        'strong_positive_unchanged': True,\n        'role_start_priority_invariant': True,\n        'wishlist_risks_preserved': True,\n        'package_risk_provenance_preserved': True,\n        'final_refinement_preserves_bridge_fit_and_purchase_value': True,\n",
)

deal_path = Path('config/deal_quality_contract.json')
deal = json.loads(deal_path.read_text(encoding='utf-8'))
deal['version'] = '1.5'
authority = deal.setdefault('authority', {})
authority.pop('weak_taste_can_never_be_rescued_by_discount', None)
authority['discount_alone_never_rescues_below_moderate_taste'] = True
authority['bounded_v5_commercial_bridge_is_only_below_moderate_paid_exception'] = True
deal_path.write_text(json.dumps(deal, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

replace_once(
    'PROJECT_RULES.md',
    '`confirmed_negative` and `exclude_direct_conflict` are non-overridable regardless of wishlist, discount, package savings, or other paid commercial signals. Existing content/store/sale/symbolic/budget gates, package equivalence rules, risk/warning visibility, giveaway path, and the single final ranking authority remain unchanged.',
    'Exact V5 `fit_evidence_state=confirmed_negative` — including a direct conflict that V5 has actually confirmed — is non-overridable regardless of wishlist, discount, package savings, or other paid commercial signals. A legacy `reason_code=exclude_direct_conflict` alone is not confirmation: ambiguous legacy rows remain fail-closed until V5 backfill, while an exact V5 `reconsiderable` row may use the bounded package bridge. Existing content/store/sale/symbolic/budget gates, package equivalence rules, risk/warning visibility, giveaway path, and the single final ranking authority remain unchanged.',
)
replace_once(
    'PROJECT_DECISIONS.md',
    '**Инвариант:** bridge не повышает `fit_level`, не меняет `fit_evidence_state`, не переписывает `play_role`/`relative_start_priority`, не стирает риски и не создаёт новый ranking score. `confirmed_negative` и `exclude_direct_conflict` fail closed и не спасаются коммерческими сигналами.',
    '**Инвариант:** bridge не повышает `fit_level`, не меняет `fit_evidence_state`, не переписывает `play_role`/`relative_start_priority`, не стирает риски и не создаёт новый ranking score. Exact V5 `confirmed_negative` / direct confirmed conflict fail closed и не спасаются коммерческими сигналами. Сам по себе legacy `reason_code=exclude_direct_conflict` не равен V5-confirmation: без V5 binding он остаётся fail-closed, а при exact V5 `reconsiderable` не блокирует bounded package bridge.',
)
replace_once(
    'PROJECT_ROUTES.md',
    '- visual revalidation: `scripts/build_visual_feed_v2.py` without fake promotion to moderate;\n- fixed package source: existing `scripts/apply_fixed_package_purchase_options.py` economics and exact/verified purchase-equivalence rules;',
    '- visual revalidation: `scripts/build_visual_feed_v2.py` without fake promotion to moderate;\n- final downstream revalidation: `scripts/refine_visual_ranking.py` + `scripts/build_final_visual_payload.py` preserve the explicit bridge through final fit/commercial recheck;\n- fixed package source: existing `scripts/apply_fixed_package_purchase_options.py` economics and exact/verified purchase-equivalence rules;',
)
replace_once(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "            'commercial_bridge_never_rescues_confirmed_negative_or_direct_conflict': True,\n",
    "            'commercial_bridge_never_rescues_confirmed_negative_or_direct_confirmed_conflict': True,\n            'legacy_exclude_direct_conflict_reason_alone_is_not_v5_confirmation': True,\n",
)

print('TASTE_STEP3_BOUNDED_CLOSEOUT_FIXES=APPLIED')
