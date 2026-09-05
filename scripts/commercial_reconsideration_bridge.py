"""Bounded paid-commercial eligibility bridge for Taste step 3.

The bridge never changes Taste fit/evidence state, play role/start priority, or
ranking weights. It may only make an already-explicit non-confirmed-negative
below-moderate candidate commercially eligible through one of two canonical
routes:
  * wishlist + canonical current good-deal signal for `insufficient`;
  * existing fixed-package strict current-price savings for `reconsiderable`.
"""

import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

import apply_fixed_package_purchase_options as fixed_packages
from taste_evidence_contract import evidence_readiness

WISHLIST_GOOD_DEAL = 'wishlist_good_deal'
RECONSIDERABLE_FIXED_PACKAGE = 'reconsiderable_fixed_package_value'
MAILING_POLICY = Path('config/mailing_policy.json')


def disposition(scenario):
    if not isinstance(scenario, dict):
        return None
    return scenario.get('final_disposition') or scenario.get('disposition')


def canonical_good_deal(scenario):
    return (
        disposition(scenario) == 'INCLUDE'
        and scenario.get('purchase_decision') == 'БРАТЬ СЕЙЧАС'
    )


@lru_cache(maxsize=1)
def package_bridge_purchase_fields():
    policy = json.loads(MAILING_POLICY.read_text(encoding='utf-8'))
    cfg = ((policy.get('commercial_reconsideration_bridge') or {}).get('reconsiderable_fixed_package_value') or {})
    decision = cfg.get('purchase_decision_when_bridge_applies')
    bucket = cfg.get('qualitative_priority_bucket')
    if not decision or bucket is None:
        raise ValueError('Canonical reconsiderable package purchase fields are missing')
    return str(decision), int(bucket)


def hard_taste_block(taste_entry, readiness=None):
    taste_entry = taste_entry if isinstance(taste_entry, dict) else {}
    readiness = readiness or evidence_readiness(taste_entry)
    # V5 evidence state is authoritative. Ambiguous legacy direct-conflict rows
    # remain fail-closed because fit_evidence_ready is false.
    return readiness.get('fit_evidence_state') == 'confirmed_negative'


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
            purchase_decision, priority_bucket = package_bridge_purchase_fields()
            result = _base_bridge(RECONSIDERABLE_FIXED_PACKAGE, readiness)
            result.update({
                'commercial_route': 'existing_fixed_package_purchase_option',
                'package_evidence': evidence,
                'bridge_purchase_decision': purchase_decision,
                'bridge_priority_bucket': priority_bucket,
                'new_discount_threshold_introduced': False,
            })
            return result
    return None


def effective_purchase_fields(bridge, moderate_scenario):
    if isinstance(bridge, dict) and bridge.get('kind') == RECONSIDERABLE_FIXED_PACKAGE:
        return package_bridge_purchase_fields()
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
