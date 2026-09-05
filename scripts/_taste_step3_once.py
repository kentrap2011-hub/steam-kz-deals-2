import json
from pathlib import Path

ROOT = Path('.')


def write_text(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + '\n', encoding='utf-8')


def write_json(path, obj):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def replace_once(path, old, new):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected one anchor, found {count}: {old[:140]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


def append_once(path, marker, block):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    if marker in text:
        return
    p.write_text(text.rstrip() + '\n\n' + block.strip() + '\n', encoding='utf-8')


bridge = r'''"""Bounded paid-commercial eligibility bridge for Taste step 3.

The bridge never changes Taste fit/evidence state, play role/start priority, or
ranking weights. It may only make an already-explicit non-confirmed-negative
below-moderate candidate commercially eligible through one of two canonical
routes:
  * wishlist + canonical current good-deal signal for `insufficient`;
  * existing fixed-package strict current-price savings for `reconsiderable`.
"""

from collections import Counter

import apply_fixed_package_purchase_options as fixed_packages
from taste_evidence_contract import evidence_readiness

WISHLIST_GOOD_DEAL = 'wishlist_good_deal'
RECONSIDERABLE_FIXED_PACKAGE = 'reconsiderable_fixed_package_value'
DIRECT_CONFLICT_REASON = 'exclude_direct_conflict'
PACKAGE_PURCHASE_DECISION = 'МОЖНО БРАТЬ'
PACKAGE_PRIORITY_BUCKET = 5


def disposition(scenario):
    if not isinstance(scenario, dict):
        return None
    return scenario.get('final_disposition') or scenario.get('disposition')


def canonical_good_deal(scenario):
    return (
        disposition(scenario) == 'INCLUDE'
        and scenario.get('purchase_decision') == 'БРАТЬ СЕЙЧАС'
    )


def hard_taste_block(taste_entry, readiness=None):
    taste_entry = taste_entry if isinstance(taste_entry, dict) else {}
    readiness = readiness or evidence_readiness(taste_entry)
    return (
        readiness.get('fit_evidence_state') == 'confirmed_negative'
        or taste_entry.get('reason_code') == DIRECT_CONFLICT_REASON
    )


def _base_bridge(kind, readiness):
    return {
        'kind': kind,
        'fit_evidence_state': readiness.get('fit_evidence_state'),
        'fit_evidence_confidence': readiness.get('fit_evidence_confidence'),
        'taste_state_preserved': True,
        'taste_fit_preserved': 'below_moderate',
        'taste_verdict_preserved': 'EXCLUDE',
        'play_role_start_priority_preserved': True,
        'risks_and_warnings_preserved': True,
        'ranking_weights_unchanged': True,
    }


def resolve_bridge(*, taste_entry, wishlist, moderate_scenario, package_evidence=None):
    taste_entry = taste_entry if isinstance(taste_entry, dict) else {}
    readiness = evidence_readiness(taste_entry)
    if readiness.get('fit_evidence_ready') is not True:
        return None
    if hard_taste_block(taste_entry, readiness):
        return None
    if str(taste_entry.get('verdict') or '').upper() != 'EXCLUDE':
        return None
    if taste_entry.get('fit_level') != 'below_moderate':
        return None

    state = readiness.get('fit_evidence_state')
    if state == 'insufficient' and bool(wishlist) and canonical_good_deal(moderate_scenario):
        result = _base_bridge(WISHLIST_GOOD_DEAL, readiness)
        result.update({
            'commercial_route': 'decision_if_moderate',
            'canonical_good_deal_signal': {
                'moderate_disposition': 'INCLUDE',
                'purchase_decision': 'БРАТЬ СЕЙЧАС',
            },
            'new_discount_threshold_introduced': False,
        })
        return result

    if state == 'reconsiderable' and disposition(moderate_scenario) == 'INCLUDE':
        evidence = package_evidence if isinstance(package_evidence, dict) else {}
        if evidence.get('strict_current_price_savings') is True and evidence.get('comparison_source_aligned') is True:
            result = _base_bridge(RECONSIDERABLE_FIXED_PACKAGE, readiness)
            result.update({
                'commercial_route': 'existing_fixed_package_purchase_option',
                'package_evidence': evidence,
                'bridge_purchase_decision': PACKAGE_PURCHASE_DECISION,
                'bridge_priority_bucket': PACKAGE_PRIORITY_BUCKET,
                'new_discount_threshold_introduced': False,
            })
            return result
    return None


def effective_purchase_fields(bridge, moderate_scenario):
    if isinstance(bridge, dict) and bridge.get('kind') == RECONSIDERABLE_FIXED_PACKAGE:
        return PACKAGE_PURCHASE_DECISION, PACKAGE_PRIORITY_BUCKET
    return moderate_scenario.get('purchase_decision'), moderate_scenario.get('priority_bucket')


def validate_visual_bridge(row, taste_entry):
    marker = row.get('commercial_eligibility_bridge') if isinstance(row, dict) else None
    if not isinstance(marker, dict):
        return None
    resolved = resolve_bridge(
        taste_entry=taste_entry,
        wishlist=bool((row.get('context_only') or {}).get('wishlist')),
        moderate_scenario=row.get('deal_if_moderate') or {},
        package_evidence=marker.get('package_evidence'),
    )
    if not resolved or resolved.get('kind') != marker.get('kind'):
        return None
    return resolved


def package_evidence_summary(rec):
    return {
        'package_key': rec.get('package_key'),
        'packageid': rec.get('packageid'),
        'package_title': rec.get('package_title'),
        'package_price_kzt': rec.get('package_price_kzt'),
        'covered_visible_game_ids': rec.get('covered_visible_game_ids') or [],
        'covered_visible_titles': rec.get('covered_visible_titles') or [],
        'covered_visible_game_count': rec.get('covered_visible_game_count'),
        'uses_verified_purchase_equivalence': bool(rec.get('uses_verified_purchase_equivalence')),
        'verified_incremental_content_total_kzt': rec.get('verified_incremental_content_total_kzt'),
        'comparable_entitlement_total_kzt': rec.get('comparable_entitlement_total_kzt'),
        'savings_kzt': rec.get('savings_kzt'),
        'savings_percent_vs_standalone': rec.get('savings_percent_vs_standalone'),
        'strict_current_price_savings': rec.get('strict_current_price_savings') is True,
        'comparison_source_aligned': rec.get('comparison_source_aligned') is True,
        'comparison_scope': rec.get('comparison_scope'),
        'requires_multi_game_intent': rec.get('requires_multi_game_intent') is True,
        'unknown_extra_content_value_assumed_kzt': rec.get('unknown_extra_content_value_assumed_kzt'),
        'verified_unpriced_content_value_assumed_kzt': rec.get('verified_unpriced_content_value_assumed_kzt'),
    }


def build_package_bridge_index(*, package_artifact, family_graph, store_entries,
                               taste_projection_entries, effective_taste_entries,
                               deal_entries, kzt_per_rub, purchase_equivalence,
                               source_stamp):
    stats = {
        'status': 'unavailable',
        'source_aligned': False,
        'stable_positive_family_count': 0,
        'reconsiderable_candidate_count': 0,
        'strict_savings_candidate_count': 0,
    }
    if not isinstance(package_artifact, dict) or package_artifact.get('status') != 'complete':
        stats['reason'] = 'fixed_package_artifact_unavailable_or_incomplete'
        return {}, stats
    if package_artifact.get('source_mailing_updated_at_utc') != source_stamp:
        stats['reason'] = 'fixed_package_artifact_stale_vs_mailing'
        return {}, stats
    if family_graph.get('source_updated_at_utc') != source_stamp:
        stats['reason'] = 'family_graph_stale_vs_mailing'
        return {}, stats

    stable = []
    candidates = {}
    families = family_graph.get('families') or []
    for family in families:
        if not isinstance(family, dict) or family.get('family_type') != 'base_game':
            continue
        fid = str(family.get('family_id') or '')
        primary_key = family.get('primary_key')
        taste_key = family.get('taste_subject_key')
        if not fid or not primary_key or not taste_key:
            continue
        store = store_entries.get(primary_key) or {}
        deal = deal_entries.get(primary_key) or {}
        projection = taste_projection_entries.get(taste_key) or {}
        entry = effective_taste_entries.get(taste_key)
        if not isinstance(entry, dict) and isinstance(projection.get('cached_taste'), dict):
            entry = projection.get('cached_taste')
        if not isinstance(entry, dict):
            continue
        price = store.get('final_kzt')
        if price is None:
            price = family.get('primary_final_kzt')
        if price is None or float(price) <= 0:
            continue
        base_appids = [str(x) for x in (family.get('base_appids') or []) if str(x).isdigit()]
        if not base_appids:
            continue
        visible_item = {
            'id': fid,
            'title': family.get('primary_title') or fid,
            'current_price_kzt': float(price),
            'base_appids': base_appids,
        }
        moderate = deal.get('decision_if_moderate') or {}
        strong = deal.get('decision_if_strong') or {}
        verdict = str(entry.get('verdict') or '').upper()
        fit = entry.get('fit_level')
        if verdict == 'INCLUDE' and fit in {'strong', 'moderate'}:
            selected = strong if fit == 'strong' else moderate
            if disposition(selected) == 'INCLUDE':
                stable.append(visible_item)
                continue
        readiness = evidence_readiness(entry)
        if (
            verdict == 'EXCLUDE'
            and entry.get('fit_level') == 'below_moderate'
            and readiness.get('fit_evidence_ready') is True
            and readiness.get('fit_evidence_state') == 'reconsiderable'
            and not hard_taste_block(entry, readiness)
            and disposition(moderate) == 'INCLUDE'
        ):
            candidates[fid] = visible_item

    stats['source_aligned'] = True
    stats['status'] = 'complete'
    stats['stable_positive_family_count'] = len(stable)
    stats['reconsiderable_candidate_count'] = len(candidates)
    evidence = {}
    for fid, candidate in candidates.items():
        _, best = fixed_packages.build_recommendations(
            package_artifact,
            family_graph,
            stable + [candidate],
            kzt_per_rub,
            purchase_equivalence,
        )
        rec = best.get(fid)
        if not isinstance(rec, dict):
            continue
        if rec.get('strict_current_price_savings') is not True:
            continue
        if rec.get('comparison_source_aligned') is not True:
            continue
        evidence[fid] = package_evidence_summary(rec)
    stats['strict_savings_candidate_count'] = len(evidence)
    stats['bridge_family_ids'] = sorted(evidence)
    return evidence, stats


def bridge_counts(rows):
    counter = Counter()
    for row in rows or []:
        marker = (row or {}).get('commercial_eligibility_bridge') or {}
        if marker.get('kind'):
            counter[str(marker['kind'])] += 1
    return dict(sorted(counter.items()))
'''
write_text('scripts/commercial_reconsideration_bridge.py', bridge)


test = r'''import copy
import json

import commercial_reconsideration_bridge as bridge
import play_priority_context
from taste_evidence_contract import current_evidence_contract_sha


def evidence_entry(state, reason='exclude_insufficient'):
    common = {
        'evidence_contract_sha': current_evidence_contract_sha(),
        'verdict': 'EXCLUDE',
        'fit_level': 'below_moderate',
        'reason_code': reason,
        'fit_evidence_state': state,
        'fit_evidence_confidence': 'medium',
        'fit_evidence_basis': ['candidate_information_insufficient'],
        'historical_negative_context': None,
        'candidate_quality_findings': [],
        'negative_analysis_status': 'complete_no_confirmed_negative',
        'negative_findings': [],
    }
    if state == 'reconsiderable':
        common.update({
            'fit_evidence_confidence': 'high',
            'fit_evidence_basis': ['historical_user_experience'],
            'historical_negative_context': {
                'evidence_depth': 'brief_or_partial',
                'outcome': 'mixed',
                'explicit_dislike': False,
                'current_reopening_evidence': 'meaningful_new_context',
            },
        })
    if state == 'confirmed_negative':
        common.update({
            'reason_code': 'exclude_direct_conflict',
            'fit_evidence_confidence': 'high',
            'fit_evidence_basis': ['direct_user_current_reaction'],
            'negative_analysis_status': 'complete_with_confirmed_negative',
            'negative_findings': [{
                'evidence_strength': 'strong',
                'personal_relevance': 'confirmed',
                'evidence_origin': 'direct_user_current_reaction',
            }],
        })
    return common


def scenario(decision='БРАТЬ СЕЙЧАС', disposition='INCLUDE', bucket=3):
    return {'disposition': disposition, 'purchase_decision': decision, 'priority_bucket': bucket}


def package_evidence(strict=True):
    return {
        'package_key': 'Sub_42',
        'strict_current_price_savings': strict,
        'comparison_source_aligned': True,
        'covered_visible_game_count': 2,
        'requires_multi_game_intent': True,
        'savings_kzt': 500.0,
    }


def main():
    insufficient = evidence_entry('insufficient')
    wishlist_good = bridge.resolve_bridge(
        taste_entry=insufficient,
        wishlist=True,
        moderate_scenario=scenario(),
    )
    assert wishlist_good and wishlist_good['kind'] == bridge.WISHLIST_GOOD_DEAL
    assert wishlist_good['taste_state_preserved'] is True

    ordinary = bridge.resolve_bridge(
        taste_entry=insufficient,
        wishlist=True,
        moderate_scenario=scenario('МОЖНО БРАТЬ', 'INCLUDE', 5),
    )
    assert ordinary is None

    confirmed = evidence_entry('confirmed_negative', 'exclude_direct_conflict')
    huge_discount = bridge.resolve_bridge(
        taste_entry=confirmed,
        wishlist=True,
        moderate_scenario=scenario(),
        package_evidence=package_evidence(),
    )
    assert huge_discount is None

    nonwishlist = bridge.resolve_bridge(
        taste_entry=insufficient,
        wishlist=False,
        moderate_scenario=scenario(),
    )
    assert nonwishlist is None

    reconsiderable = evidence_entry('reconsiderable', 'exclude_audited_below')
    package_bridge = bridge.resolve_bridge(
        taste_entry=reconsiderable,
        wishlist=False,
        moderate_scenario=scenario('ЛУЧШЕ ЖДАТЬ', 'INCLUDE', 6),
        package_evidence=package_evidence(),
    )
    assert package_bridge and package_bridge['kind'] == bridge.RECONSIDERABLE_FIXED_PACKAGE
    decision, bucket = bridge.effective_purchase_fields(package_bridge, scenario('ЛУЧШЕ ЖДАТЬ', 'INCLUDE', 6))
    assert decision == 'МОЖНО БРАТЬ' and bucket == 5

    package_bad = bridge.resolve_bridge(
        taste_entry=reconsiderable,
        wishlist=False,
        moderate_scenario=scenario('ЛУЧШЕ ЖДАТЬ', 'INCLUDE', 6),
        package_evidence=package_evidence(False),
    )
    assert package_bad is None

    highfleet = bridge.resolve_bridge(
        taste_entry=confirmed,
        wishlist=True,
        moderate_scenario=scenario(),
        package_evidence=package_evidence(),
    )
    assert highfleet is None

    positive = copy.deepcopy(insufficient)
    positive.update({'verdict': 'INCLUDE', 'fit_level': 'strong', 'reason_code': 'include_strong', 'fit_evidence_state': 'sufficient', 'fit_evidence_confidence': 'high', 'fit_evidence_basis': ['normalized_taste_factors']})
    assert bridge.resolve_bridge(taste_entry=positive, wishlist=True, moderate_scenario=scenario(), package_evidence=package_evidence()) is None

    # Step-2 role/start is invariant to commercial inputs.
    base_game = {'title': 'High On Life'}
    before = play_priority_context.context_for_game(base_game, {})
    commercial_game = {'title': 'High On Life', 'wishlist': True, 'discount_percent': 99, 'decision': 'БРАТЬ СЕЙЧАС', 'commercial_eligibility_bridge': wishlist_good}
    after = play_priority_context.context_for_game(commercial_game, {})
    assert before == after
    assert after['play_role'] == 'main_full' and after['relative_start_priority'] == 'ordinary'

    # Risks/warnings are data carried beside the bridge, not replaced by it.
    row = {
        'taste_subject_key': 'App_test',
        'context_only': {'wishlist': True},
        'deal_if_moderate': scenario(),
        'commercial_eligibility_bridge': wishlist_good,
        'risks': ['confirmed practical warning'],
    }
    validated = bridge.validate_visual_bridge(row, insufficient)
    assert validated and row['risks'] == ['confirmed practical warning']

    print(json.dumps({
        'status': 'PASS',
        'wishlist_good_deal_insufficient': True,
        'wishlist_ordinary_insufficient_blocked': True,
        'confirmed_negative_huge_discount_blocked': True,
        'nonwishlist_weak_unchanged': True,
        'reconsiderable_package_purchase_worthy': True,
        'package_without_strict_savings_blocked': True,
        'highfleet_non_rescuable': True,
        'strong_positive_unchanged': True,
        'role_start_priority_invariant': True,
        'risks_preserved': True,
    }, ensure_ascii=False, indent=2))
    print('RECONSIDERATION_COMMERCIAL_BRIDGE_TEST=PASS')


if __name__ == '__main__':
    main()
'''
write_text('scripts/test_reconsideration_commercial_bridge.py', test)

# Canonical mailing policy: new top-level eligibility bridge outside price-blind Taste semantics.
mailing_path = ROOT / 'config/mailing_policy.json'
mailing = json.loads(mailing_path.read_text(encoding='utf-8'))
mailing['version'] = '1.21'
mailing['commercial_reconsideration_bridge'] = {
    'enabled': True,
    'affects_taste_fit': False,
    'affects_fit_evidence_state': False,
    'affects_play_role_or_start_priority': False,
    'confirmed_negative_non_overridable': True,
    'direct_confirmed_conflict_non_overridable': True,
    'preserve_risks_and_warnings': True,
    'ranking_weights_unchanged': True,
    'wishlist_good_deal': {
        'required_fit_evidence_state': 'insufficient',
        'wishlist_required': True,
        'commercial_scenario': 'decision_if_moderate',
        'required_disposition': 'INCLUDE',
        'required_purchase_decision': 'БРАТЬ СЕЙЧАС',
        'new_discount_threshold': None,
    },
    'reconsiderable_fixed_package_value': {
        'required_fit_evidence_state': 'reconsiderable',
        'standalone_moderate_scenario_must_include': True,
        'package_semantics': 'existing_fixed_sub_purchase_option_only',
        'strict_current_price_savings_required': True,
        'comparison_source_alignment_required': True,
        'personalized_complete_the_set_allowed': False,
        'fuzzy_equivalence_allowed': False,
        'purchase_decision_when_bridge_applies': 'МОЖНО БРАТЬ',
        'qualitative_priority_bucket': 5,
    },
}
write_json('config/mailing_policy.json', mailing)

# Deal contract: replace the obsolete blanket statement with the bounded exception.
deal_path = ROOT / 'config/deal_quality_contract.json'
deal = json.loads(deal_path.read_text(encoding='utf-8'))
deal['version'] = '1.4'
authority = deal.setdefault('authority_and_separation', {})
authority.pop('weak_taste_can_never_be_rescued_by_discount', None)
authority.update({
    'commercial_bridge_never_changes_taste_fit': True,
    'confirmed_negative_can_never_be_rescued_by_paid_commercial_signals': True,
    'direct_confirmed_conflict_can_never_be_rescued_by_paid_commercial_signals': True,
    'wishlist_insufficient_exception_uses_existing_moderate_include_and_buy_now_signal': True,
    'reconsiderable_package_exception_uses_existing_fixed_package_strict_current_price_savings': True,
    'no_new_discount_threshold_for_commercial_bridge': True,
})
principles = deal.setdefault('final_ranking_principles', {})
principles['strong_discount_cannot_promote_below_moderate_taste'] = True
principles['commercial_bridge_may_create_eligibility_without_promoting_taste_fit'] = True
principles['wishlist_role'] = 'existing_ranking_bonus_plus_bounded_insufficient_good_deal_eligibility_exception'
write_json('config/deal_quality_contract.json', deal)

# Pre-AI consumer: compute package bridge evidence from existing fixed-package economics.
replace_once(
    'scripts/build_pre_ai_chatgpt_payload.py',
    'from semantic_runtime_completion import apply_payload_status\n',
    'from semantic_runtime_completion import apply_payload_status\nimport apply_fixed_package_purchase_options as fixed_packages\nimport commercial_reconsideration_bridge as commercial_bridge\n',
)
replace_once(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "TASTE_OVERLAY = Path('data/cache/taste_fit.entry_overlay.json')\nLATEST_RUNTIME_STATUS = Path('data/cache/taste_ingest_receipts/latest_runtime_status.json')\n",
    "TASTE_OVERLAY = Path('data/cache/taste_fit.entry_overlay.json')\nFIXED_PACKAGE_OPTIONS = Path('data/production/pre_ai/fixed_package_options.json')\nLATEST_RUNTIME_STATUS = Path('data/cache/taste_ingest_receipts/latest_runtime_status.json')\n",
)
replace_once(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "    deals_doc = load(DEALS)\n\n    docs = [store_doc, fx_doc, family_doc, taste_doc, history_doc, deals_doc]\n",
    "    deals_doc = load(DEALS)\n    package_doc = load(FIXED_PACKAGE_OPTIONS) if FIXED_PACKAGE_OPTIONS.exists() else {}\n\n    docs = [store_doc, fx_doc, family_doc, taste_doc, history_doc, deals_doc]\n",
)
replace_once(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "    if len(families) != int(family_doc['family_count']):\n        raise SystemExit('Family count mismatch')\n\n    ai_queue = []\n",
    "    if len(families) != int(family_doc['family_count']):\n        raise SystemExit('Family count mismatch')\n\n    purchase_equivalence = fixed_packages.load_purchase_equivalence()\n    package_bridge_by_family, package_bridge_stats = commercial_bridge.build_package_bridge_index(\n        package_artifact=package_doc,\n        family_graph=family_doc,\n        store_entries=store,\n        taste_projection_entries=taste,\n        effective_taste_entries=effective_entries,\n        deal_entries=deals,\n        kzt_per_rub=rate,\n        purchase_equivalence=purchase_equivalence,\n        source_stamp=source_stamp,\n    )\n\n    ai_queue = []\n",
)
replace_once(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "    evidence_backfill_queue_count = 0\n\n    for family in families:\n",
    "    evidence_backfill_queue_count = 0\n    commercial_bridge_counts = Counter()\n\n    for family in families:\n",
)
replace_once(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "        if cache_hit:\n            evidence_backfill = bool(taste_row.get('fit_evidence_backfill_required'))\n            if cached_taste['verdict'] != 'INCLUDE':\n",
    "        if cache_hit:\n            evidence_backfill = bool(taste_row.get('fit_evidence_backfill_required'))\n            eligibility_bridge = None\n            if cached_taste['verdict'] != 'INCLUDE' and not evidence_backfill:\n                effective_taste = effective_entries.get(taste_key) or cached_taste\n                eligibility_bridge = commercial_bridge.resolve_bridge(\n                    taste_entry=effective_taste,\n                    wishlist=bool((context.get('context_only') or {}).get('wishlist')),\n                    moderate_scenario=moderate_scenario,\n                    package_evidence=package_bridge_by_family.get(str(family.get('family_id') or '')),\n                )\n                if eligibility_bridge:\n                    context['commercial_eligibility_bridge'] = eligibility_bridge\n                    context['eligibility_override'] = eligibility_bridge['kind']\n                    commercial_bridge_counts[eligibility_bridge['kind']] += 1\n            if cached_taste['verdict'] != 'INCLUDE' and not eligibility_bridge:\n",
)
replace_once(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "            fit = cached_taste['fit_level']\n            selected = strong_scenario if fit == 'strong' else moderate_scenario\n            if selected['disposition'] != 'INCLUDE':\n",
    "            fit = cached_taste['fit_level']\n            selected = strong_scenario if fit == 'strong' else moderate_scenario\n            if selected['disposition'] != 'INCLUDE':\n",
)
# The no-op anchor above intentionally asserts the downstream route still exists.
replace_once(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "                context['resolved_taste_fit'] = fit\n                context['fit_evidence_state'] = taste_row.get('fit_evidence_state')\n                context['fit_evidence_confidence'] = taste_row.get('fit_evidence_confidence')\n                context['fit_evidence_source'] = taste_row.get('fit_evidence_source')\n                context['final_purchase_decision'] = selected['purchase_decision']\n                context['final_priority_bucket'] = int(selected['priority_bucket'])\n                ready_context.append(context)\n",
    "                context['resolved_taste_fit'] = fit\n                context['fit_evidence_state'] = taste_row.get('fit_evidence_state')\n                context['fit_evidence_confidence'] = taste_row.get('fit_evidence_confidence')\n                context['fit_evidence_source'] = taste_row.get('fit_evidence_source')\n                if eligibility_bridge:\n                    context['resolved_taste_verdict'] = cached_taste['verdict']\n                    context['resolved_taste_reason_code'] = cached_taste['reason_code']\n                final_decision, final_bucket = commercial_bridge.effective_purchase_fields(eligibility_bridge, selected)\n                context['final_purchase_decision'] = final_decision\n                context['final_priority_bucket'] = int(final_bucket)\n                ready_context.append(context)\n",
)
replace_once(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "            'wishlist_is_context_only': True,\n            'wishlist_applies_only_during_final_sorting': True,\n            'wishlist_never_causes_inclusion_or_changes_taste_fit': True,\n            'wishlist_is_strong_but_bounded_priority_bonus': True,\n",
    "            'wishlist_is_not_taste_proof': True,\n            'wishlist_never_changes_taste_fit_or_evidence_state': True,\n            'wishlist_can_only_create_bounded_eligibility_exception_for_explicit_insufficient_plus_canonical_good_deal': True,\n            'canonical_good_deal_signal': 'decision_if_moderate INCLUDE + БРАТЬ СЕЙЧАС',\n            'reconsiderable_package_bridge_uses_existing_fixed_package_strict_current_price_savings': True,\n            'commercial_bridge_never_rescues_confirmed_negative_or_direct_conflict': True,\n            'wishlist_is_strong_but_bounded_priority_bonus': True,\n",
)
replace_once(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "        'deterministic_exclusion_counts': dict(sorted(exclusion_counts.items())),\n        'complete_family_partition': partition_count == len(families),\n",
    "        'deterministic_exclusion_counts': dict(sorted(exclusion_counts.items())),\n        'commercial_eligibility_bridge_counts': dict(sorted(commercial_bridge_counts.items())),\n        'fixed_package_bridge_evidence': package_bridge_stats,\n        'complete_family_partition': partition_count == len(families),\n",
)
replace_once(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "        'deterministic_exclusion_counts': manifest['deterministic_exclusion_counts'],\n        'complete_family_partition': manifest['complete_family_partition'],\n",
    "        'deterministic_exclusion_counts': manifest['deterministic_exclusion_counts'],\n        'commercial_eligibility_bridge_counts': manifest['commercial_eligibility_bridge_counts'],\n        'fixed_package_bridge_evidence': package_bridge_stats,\n        'complete_family_partition': manifest['complete_family_partition'],\n",
)

# Visual producer: accept only a revalidated bridge marker; preserve actual below-moderate fit.
replace_once(
    'scripts/build_visual_feed_v2.py',
    'from russian_description_quality import classify_description\n',
    'from russian_description_quality import classify_description\nimport commercial_reconsideration_bridge as commercial_bridge\n',
)
helper_fn = r'''

def get_visual_eligibility(row, taste_entries):
    fit = get_fit(row, taste_entries)
    if fit in {'strong', 'moderate'}:
        scenario = row.get(f'deal_if_{fit}') or {}
        return fit, scenario, None
    taste_entry = taste_entries.get(row.get('taste_subject_key')) if isinstance(taste_entries, dict) else None
    validated = commercial_bridge.validate_visual_bridge(row, taste_entry if isinstance(taste_entry, dict) else {})
    if not validated:
        return None, None, None
    scenario = row.get('deal_if_moderate') or {}
    if scenario.get('disposition') != 'INCLUDE':
        return None, None, None
    return 'below_moderate', scenario, validated
'''
replace_once(
    'scripts/build_visual_feed_v2.py',
    "def rub_from_kzt(value, rate):\n",
    helper_fn + "\n\ndef rub_from_kzt(value, rate):\n",
)
replace_once(
    'scripts/build_visual_feed_v2.py',
    "    for row in rows:\n        fit = get_fit(row, taste_entries)\n        if fit not in {'strong', 'moderate'}:\n            continue\n        scenario = row.get(f'deal_if_{fit}') or {}\n        if scenario.get('disposition') != 'INCLUDE':\n            continue\n",
    "    for row in rows:\n        fit, scenario, eligibility_bridge = get_visual_eligibility(row, taste_entries)\n        if fit not in {'strong', 'moderate', 'below_moderate'} or not isinstance(scenario, dict):\n            continue\n        if scenario.get('disposition') != 'INCLUDE':\n            continue\n",
)
replace_once(
    'scripts/build_visual_feed_v2.py',
    "        prepared.append((row, fit, scenario, purchase, family_id, fam, base_appids))\n\n    media = storebrowse_media(wanted_appids)\n",
    "        prepared.append((row, fit, scenario, purchase, family_id, fam, base_appids, eligibility_bridge))\n\n    media = storebrowse_media(wanted_appids)\n",
)
replace_once(
    'scripts/build_visual_feed_v2.py',
    "    for row, fit, scenario, purchase, family_id, fam, base_appids in prepared:\n",
    "    for row, fit, scenario, purchase, family_id, fam, base_appids, eligibility_bridge in prepared:\n",
)
replace_once(
    'scripts/build_visual_feed_v2.py',
    "        visible.append({\n            'id': family_id,\n",
    "        final_decision, final_bucket = commercial_bridge.effective_purchase_fields(eligibility_bridge, scenario)\n        visible.append({\n            'id': family_id,\n",
)
replace_once(
    'scripts/build_visual_feed_v2.py',
    "            'fit': fit,\n            'taste_factors': taste_entry.get('taste_factors'),\n            'decision': scenario.get('purchase_decision'),\n            'priority_bucket': scenario.get('priority_bucket'),\n",
    "            'fit': fit,\n            'taste_factors': taste_entry.get('taste_factors'),\n            'decision': final_decision,\n            'priority_bucket': final_bucket,\n            'fit_evidence_state': (eligibility_bridge or {}).get('fit_evidence_state') if eligibility_bridge else None,\n            'fit_evidence_confidence': (eligibility_bridge or {}).get('fit_evidence_confidence') if eligibility_bridge else None,\n            'eligibility_override': (eligibility_bridge or {}).get('kind') if eligibility_bridge else None,\n            'commercial_eligibility_bridge': eligibility_bridge,\n",
)

append_once(
    'PROJECT_RULES.md',
    '## Bounded commercial reconsideration bridge',
    '''## Bounded commercial reconsideration bridge

Paid commercial signals may affect eligibility only after the price-blind Taste/evidence state is already explicit. They never rewrite Taste fit/evidence, play role, relative start priority, risks, or ranking weights.

Two bounded routes are canonical. First: Steam wishlist + `fit_evidence_state=insufficient` may pass the ordinary weak Taste eligibility gate only when the already-existing moderate commercial scenario is `INCLUDE` and its current purchase decision is exactly `БРАТЬ СЕЙЧАС`. This is the canonical good-deal signal; do not add another raw discount threshold.

Second: `fit_evidence_state=reconsiderable` may become purchase-worthy through an existing verified fixed Steam `Sub_` package only when the existing fixed-package economics produce `strict_current_price_savings=true` with aligned sources. The package route may set commercial purchase advice to `МОЖНО БРАТЬ`, but the Taste verdict remains `EXCLUDE / below_moderate / reconsiderable`.

`confirmed_negative` and `exclude_direct_conflict` are non-overridable regardless of wishlist, discount, package savings, or other paid commercial signals. Existing content/store/sale/symbolic/budget gates, package equivalence rules, risk/warning visibility, giveaway path, and the single final ranking authority remain unchanged.''',
)
append_once(
    'PROJECT_DECISIONS.md',
    '## TASTE-003 — Commercial signals can reopen eligibility, not Taste',
    '''---

## TASTE-003 — Commercial signals can reopen eligibility, not Taste

**Дата:** 2026-09-05
**Статус:** implemented as internal Taste step 3; independent combined Taste Review required before final material acceptance.

**Решение:** разрешить только два explicit post-Taste commercial eligibility bridges: `insufficient + Steam wishlist + canonical good deal`, а также `reconsiderable + existing fixed-package strict current-price savings`.

**Инвариант:** bridge не повышает `fit_level`, не меняет `fit_evidence_state`, не переписывает `play_role`/`relative_start_priority`, не стирает риски и не создаёт новый ranking score. `confirmed_negative` и `exclude_direct_conflict` fail closed и не спасаются коммерческими сигналами.

**Good deal:** только существующий `decision_if_moderate.final_disposition=INCLUDE` + `purchase_decision=БРАТЬ СЕЙЧАС`; новый discount threshold не вводится.

**Package:** используется существующий fixed-Sub deterministic economics / exact-or-verified purchase equivalence / `strict_current_price_savings`; personalized Complete-the-Set и fuzzy equivalence по-прежнему запрещены. Package value может использовать уже `reconsiderable`, но не создаёт это состояние.

**Основные места:** `config/mailing_policy.json`, `config/deal_quality_contract.json`, `scripts/commercial_reconsideration_bridge.py`, `scripts/build_pre_ai_chatgpt_payload.py`, `scripts/build_visual_feed_v2.py`, `scripts/test_reconsideration_commercial_bridge.py`.''',
)
append_once(
    'PROJECT_ROUTES.md',
    '## Taste reconsideration / wishlist commercial bridge',
    '''## Taste reconsideration / wishlist commercial bridge

- canonical policy: `config/mailing_policy.json -> commercial_reconsideration_bridge`;
- implementation contract alignment: `config/deal_quality_contract.json`;
- deterministic helper: `scripts/commercial_reconsideration_bridge.py`;
- first eligibility application: `scripts/build_pre_ai_chatgpt_payload.py` cache-hit EXCLUDE boundary;
- visual revalidation: `scripts/build_visual_feed_v2.py` without fake promotion to moderate;
- fixed package source: existing `scripts/apply_fixed_package_purchase_options.py` economics and exact/verified purchase-equivalence rules;
- focused regression: `scripts/test_reconsideration_commercial_bridge.py`;
- no new scheduler, ranker, giveaway path, discount threshold, or Taste evaluator.''',
)

print('TASTE_STEP3_PATCH=APPLIED')
