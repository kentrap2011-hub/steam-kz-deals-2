import json
import sys
from pathlib import Path


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, doc):
    Path(path).write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def replace_one(path, old, new):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if old not in text:
        raise SystemExit(f'Patch anchor missing in {path}: {old[:160]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


def replace_between(path, start_marker, end_marker, replacement):
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f'Start marker missing in {path}: {start_marker!r}')
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f'End marker missing in {path}: {end_marker!r}')
    p.write_text(text[:start] + replacement + text[end:], encoding='utf-8')


sys.path.insert(0, 'scripts')
from taste_cache_common import taste_semantics_digest

before_policy = load('config/mailing_policy.json')
before_contract = load('config/taste_cache_entry_contract.json')
before_semantics = taste_semantics_digest(before_policy, before_contract)

policy = before_policy
policy['version'] = '1.20'
policy['taste_evidence_state'] = {
    'required': True,
    'price_blind': True,
    'orthogonal_to_fit_cache_binding': True,
    'states': {
        'sufficient': 'Enough candidate-specific evidence exists to interpret the current fit verdict; this is not a claim that the game has no downsides.',
        'insufficient': 'The current evidence is not rich enough to conclude personal dislike; the candidate may still remain below the paid eligibility threshold until later work explicitly permits an exception.',
        'reconsiderable': 'Older or shallow negative history has been legitimately reopened by later non-commercial evidence; this is not a positive fit promotion and remains below paid eligibility until a later explicit bridge.',
        'confirmed_negative': 'Strong current/title-specific or adequately informed personal evidence supports a real negative fit; paid price, discount, wishlist or bundle value cannot override this state.'
    },
    'confidence_values': ['low', 'medium', 'high'],
    'confirmed_negative_non_overridable_by_paid_deal': True,
    'reconsiderable_requires_old_or_shallow_history_plus_later_reopening_evidence': True,
    'candidate_quality_findings_are_separate_from_personal_dislike': True,
    'recurring_public_complaints_may_populate_candidate_quality_findings': True,
    'recurring_public_complaints_alone_cannot_create_confirmed_negative': True,
    'generic_feature_presence_alone_cannot_create_strong_personal_negative': True,
    'wishlist_discount_price_bundle_value_cannot_set_or_change_evidence_state': True,
    'existing_negative_work_code_is_reused_for_evidence_backfill': 'resolve_grounded_negative_analysis',
    'new_scheduler_or_parallel_semantic_queue_forbidden': True,
    'legacy_compatibility': {
        'include_without_legacy_negative_evidence': 'sufficient',
        'exclude_insufficient': 'insufficient',
        'legacy_include_with_negative_evidence': 'requires_v5_evidence_backfill',
        'exclude_audited_below': 'requires_v5_evidence_backfill',
        'exclude_direct_conflict': 'requires_v5_evidence_backfill'
    }
}
save('config/mailing_policy.json', policy)

result_contract = load('config/taste_result_contract.json')
result_contract['contract'] = 'TASTE-SEMANTIC-RESULT-V5'
result_contract['version'] = '1.0'
result_contract['purpose'] = (
    'Define the price-blind semantic output produced by the existing Taste worker and persisted by GitHub, '
    'including normalized fit factors, grounded personal negatives, a separate evidence-state/confidence layer, '
    'historical reconsideration context, and candidate-quality findings that do not automatically imply personal dislike.'
)
evidence_fields = [
    'fit_evidence_state', 'fit_evidence_confidence', 'fit_evidence_basis',
    'historical_negative_context', 'candidate_quality_findings'
]
for field in evidence_fields:
    if field not in result_contract['required_base_result_fields']:
        result_contract['required_base_result_fields'].append(field)
    if field not in result_contract['negative_only_result_fields']:
        result_contract['negative_only_result_fields'].append(field)
result_contract['negative_finding_fields'] = [
    'category', 'code', 'evidence', 'risk_text_ru',
    'evidence_origin', 'evidence_strength', 'personal_relevance'
]
result_contract['negative_finding_catalog']['felt_technical_burden'] = {
    'category': 'felt_burden', 'ranking_score': 4
}
result_contract['fit_evidence_state'] = {
    'values': ['sufficient', 'insufficient', 'reconsiderable', 'confirmed_negative'],
    'confidence_values': ['low', 'medium', 'high'],
    'work_code': 'resolve_grounded_negative_analysis',
    'new_work_code_created': False,
    'basis_values': [
        'candidate_specific_positive_match', 'candidate_information_insufficient',
        'direct_user_current_reaction', 'title_specific_inspection',
        'historical_user_experience', 'later_quality_reputation_reopened_interest',
        'direct_current_interest_reopened_history', 'richer_title_specific_evidence_reopened_history',
        'same_series_continuity'
    ],
    'rules': {
        'sufficient_requires_include': True,
        'insufficient_requires_exclude_but_is_not_dislike': True,
        'reconsiderable_requires_exclude_and_historical_reopening_context': True,
        'confirmed_negative_requires_high_confidence_and_strong_confirmed_personal_finding': True,
        'old_brief_non_engagement_cannot_alone_be_confirmed_negative': True,
        'price_discount_wishlist_bundle_never_change_state': True
    }
}
result_contract['negative_evidence_provenance'] = {
    'origin_values': [
        'direct_user_reaction', 'title_specific_inspection', 'historical_user_experience',
        'same_series_continuity', 'candidate_specific_profile_conflict'
    ],
    'strength_values': ['weak', 'moderate', 'strong'],
    'personal_relevance_required_value': 'confirmed',
    'generic_feature_hypothesis_is_not_valid_personal_negative_origin': True,
    'recurring_player_complaint_is_not_valid_personal_negative_origin': True,
    'score_4_personal_risk_requires_strong_evidence': True
}
result_contract['historical_negative_context'] = {
    'nullable': True,
    'fields': ['exposure_depth', 'recency', 'reaction', 'later_reopening_evidence'],
    'exposure_depth_values': ['brief', 'partial', 'substantial', 'complete', 'unknown'],
    'recency_values': ['old', 'recent', 'unknown'],
    'reaction_values': ['non_engagement', 'mixed', 'explicit_dislike', 'unknown'],
    'later_reopening_values': ['none', 'quality_reputation', 'direct_current_interest', 'richer_title_specific_evidence']
}
result_contract['candidate_quality_findings'] = {
    'fields': ['category', 'code', 'evidence', 'source', 'recurrence', 'personal_relevance', 'risk_text_ru'],
    'source_values': ['recurring_player_complaints', 'substantive_review_synthesis', 'direct_user_quality_observation'],
    'recurrence_values': ['recurring_pattern', 'single_observation'],
    'personal_relevance_value': 'unresolved',
    'never_changes_fit_verdict_or_normalized_factors': True,
    'public_review_sentiment_percentage_is_not_taste_evidence': True
}
result_contract['scoring_rules']['forbidden_inputs'] = [
    'price', 'discount', 'wishlist', 'steamdb_history', 'historical_price',
    'sale_end', 'deal_quality', 'commercial_priority', 'review_sentiment_or_percentage_as_fit_evidence'
]
result_contract['scoring_rules']['candidate_quality_findings_may_use_recurring_public_complaints_only_as_separate_nonfit_evidence'] = True
save('config/taste_result_contract.json', result_contract)

cache_contract = before_contract
cache_contract['contract'] = 'TASTE-CACHE-ENTRY-BINDING-V5'
cache_contract['version'] = '1.0'
cache_contract['purpose'] = (
    'Preserve exact reusable price-blind fit bindings while adding an independently bound V5 evidence-state layer. '
    'Legacy V2/V3/V4 fit entries remain reusable; ambiguous evidence semantics are backfilled through the existing Taste work path.'
)
cache_contract['taste_semantics_digest']['migration_note'] = (
    'Evidence-state/confidence and grounded-negative V5 provenance are deliberately orthogonal to the existing fit semantic digest. '
    'Changing the evidence contract does not invalidate an otherwise exact fit cache entry; evidence readiness is bound separately.'
)
cache_contract['schema_v5_required_entry_fields'] = [
    'key', 'appid', 'profile_blob_sha', 'taste_model_version', 'taste_semantics_sha256',
    'candidate_context_sha256', 'taste_fingerprint', 'verdict', 'fit_level', 'reason_code',
    'positive_evidence', 'negative_analysis_status', 'negative_findings', 'negative_evidence',
    'taste_factors', 'evidence_contract_sha', 'fit_evidence_state', 'fit_evidence_confidence',
    'fit_evidence_basis', 'historical_negative_context', 'candidate_quality_findings', 'evaluated_at_utc'
]
cache_contract['evidence_state'] = {
    'contract_binding_field': 'evidence_contract_sha',
    'binding_source': 'git_blob_sha_of_config/taste_result_contract.json',
    'fit_binding_remains_independent': True,
    'legacy_entries_without_v5_evidence_remain_fit_reusable': True,
    'ambiguous_legacy_entries_require_evidence_backfill': True,
    'evidence_backfill_preserves': [
        'verdict', 'fit_level', 'reason_code', 'positive_evidence', 'taste_factors',
        'profile_blob_sha', 'taste_model_version', 'taste_semantics_sha256',
        'taste_fingerprint', 'candidate_context_sha256', 'evaluated_at_utc'
    ]
}
cache_contract['mixed_generation_rules']['legacy_v4_entries_without_evidence_state_may_be_fit_cache_hits'] = True
cache_contract['mixed_generation_rules']['legacy_v4_entries_without_evidence_state_are_not_v5_evidence_bound'] = True
cache_contract['mixed_generation_rules']['v5_evidence_backfill_may_modify_only_evidence_and_negative_analysis_fields'] = True
cache_contract['overlay']['current_entry_schema_version'] = 5
cache_contract['overlay']['mixed_v2_v3_v4_v5_rows_allowed_during_migration'] = True
save('config/taste_cache_entry_contract.json', cache_contract)

ledger = load('config/taste_ledger_contract.json')
ledger['version'] = '1.1'
ledger['purpose'] = (
    'Validate the compatibility binary price-blind fit/eligibility ledger while keeping evidence confidence separate. '
    'EXCLUDE/below_moderate is no longer interpreted as proof of personal dislike; V5 evidence state distinguishes insufficient, reconsiderable and confirmed negative.'
)
ledger['authority']['binary_fit_ledger_is_not_evidence_confidence_ledger'] = True
ledger['evidence_state_semantics'] = {
    'canonical_contract': 'config/taste_result_contract.json',
    'states': ['sufficient', 'insufficient', 'reconsiderable', 'confirmed_negative'],
    'exclude_insufficient_compatibility_state': 'insufficient',
    'exclude_audited_below_requires_v5_backfill_for_evidence_interpretation': True,
    'exclude_direct_conflict_requires_v5_backfill_for_evidence_interpretation': True,
    'legacy_reason_code_alone_never_proves_confirmed_negative': True,
    'confirmed_negative_non_overridable_by_paid_commercial_signals': True,
    'reconsiderable_is_not_fit_promotion': True
}
ledger['mapping_rationale']['exclude_insufficient'] = (
    'The compatibility fit ledger remains below_moderate/EXCLUDE, but V5 evidence semantics interpret this as insufficient evidence rather than personal dislike unless stronger evidence is separately proven.'
)
ledger['mapping_rationale']['exclude_audited_below'] = (
    'The compatibility fit ledger remains below_moderate/EXCLUDE. This reason alone is insufficient to classify evidence confidence; V5 evidence backfill decides insufficient/reconsiderable/confirmed_negative.'
)
ledger['mapping_rationale']['exclude_direct_conflict'] = (
    'The compatibility fit ledger remains below_moderate/EXCLUDE. Historical implementations used this code too coarsely, so V5 evidence state is required before treating it as a confirmed personal negative.'
)
save('config/taste_ledger_contract.json', ledger)

evidence_module = r'''"""Canonical V5 evidence-state validation for price-blind Taste.

This layer is deliberately orthogonal to the reusable fit binding. It answers
how much and what kind of personal evidence supports the fit verdict, while
candidate-quality findings remain separate from personal dislike.
"""

import hashlib
from pathlib import Path

RESULT_CONTRACT = Path('config/taste_result_contract.json')

EVIDENCE_RESULT_FIELDS = {
    'fit_evidence_state',
    'fit_evidence_confidence',
    'fit_evidence_basis',
    'historical_negative_context',
    'candidate_quality_findings',
}
FIT_EVIDENCE_STATES = {'sufficient', 'insufficient', 'reconsiderable', 'confirmed_negative'}
CONFIDENCE_VALUES = {'low', 'medium', 'high'}
BASIS_VALUES = {
    'candidate_specific_positive_match',
    'candidate_information_insufficient',
    'direct_user_current_reaction',
    'title_specific_inspection',
    'historical_user_experience',
    'later_quality_reputation_reopened_interest',
    'direct_current_interest_reopened_history',
    'richer_title_specific_evidence_reopened_history',
    'same_series_continuity',
}
HISTORY_FIELDS = {'exposure_depth', 'recency', 'reaction', 'later_reopening_evidence'}
EXPOSURE_VALUES = {'brief', 'partial', 'substantial', 'complete', 'unknown'}
RECENCY_VALUES = {'old', 'recent', 'unknown'}
REACTION_VALUES = {'non_engagement', 'mixed', 'explicit_dislike', 'unknown'}
REOPEN_VALUES = {'none', 'quality_reputation', 'direct_current_interest', 'richer_title_specific_evidence'}
QUALITY_FIELDS = {'category', 'code', 'evidence', 'source', 'recurrence', 'personal_relevance', 'risk_text_ru'}
QUALITY_CATALOG = {
    'opaque_navigation_feedback': 'navigation_feedback',
    'mandatory_grind_or_upkeep': 'grind_upkeep',
    'boring_or_repetitive_content': 'content_repetition',
    'technical_friction': 'technical_friction',
    'weak_combat_or_ai': 'combat_ai',
    'other_recurring_quality_issue': 'other_quality',
}
QUALITY_SOURCES = {'recurring_player_complaints', 'substantive_review_synthesis', 'direct_user_quality_observation'}
QUALITY_RECURRENCE = {'recurring_pattern', 'single_observation'}


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a non-empty string')
    return value.strip()


def git_blob_sha_bytes(raw):
    return hashlib.sha1(f'blob {len(raw)}\0'.encode('ascii') + raw).hexdigest()


def current_evidence_contract_sha(path=RESULT_CONTRACT):
    return git_blob_sha_bytes(Path(path).read_bytes())


def validate_historical_negative_context(context):
    if context is None:
        return None
    if not isinstance(context, dict) or set(context) != HISTORY_FIELDS:
        raise ValueError(f'historical_negative_context must contain exactly {sorted(HISTORY_FIELDS)!r}')
    if context['exposure_depth'] not in EXPOSURE_VALUES:
        raise ValueError('historical_negative_context.exposure_depth is invalid')
    if context['recency'] not in RECENCY_VALUES:
        raise ValueError('historical_negative_context.recency is invalid')
    if context['reaction'] not in REACTION_VALUES:
        raise ValueError('historical_negative_context.reaction is invalid')
    if context['later_reopening_evidence'] not in REOPEN_VALUES:
        raise ValueError('historical_negative_context.later_reopening_evidence is invalid')
    return dict(context)


def validate_candidate_quality_findings(findings):
    if not isinstance(findings, list):
        raise ValueError('candidate_quality_findings must be an array')
    normalized = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict) or set(finding) != QUALITY_FIELDS:
            raise ValueError(f'candidate_quality_findings[{index}] must contain exactly {sorted(QUALITY_FIELDS)!r}')
        code = _text(finding['code'], f'candidate_quality_findings[{index}].code')
        category = _text(finding['category'], f'candidate_quality_findings[{index}].category')
        expected = QUALITY_CATALOG.get(code)
        if expected is None:
            raise ValueError(f'candidate_quality_findings[{index}] has unknown code: {code!r}')
        if category != expected:
            raise ValueError(f'candidate_quality_findings[{index}] category/code mismatch')
        source = _text(finding['source'], f'candidate_quality_findings[{index}].source')
        recurrence = _text(finding['recurrence'], f'candidate_quality_findings[{index}].recurrence')
        if source not in QUALITY_SOURCES:
            raise ValueError(f'candidate_quality_findings[{index}] has invalid source')
        if recurrence not in QUALITY_RECURRENCE:
            raise ValueError(f'candidate_quality_findings[{index}] has invalid recurrence')
        if source in {'recurring_player_complaints', 'substantive_review_synthesis'} and recurrence != 'recurring_pattern':
            raise ValueError('public/review candidate-quality evidence must be a recurring pattern')
        if finding['personal_relevance'] != 'unresolved':
            raise ValueError('candidate_quality_findings personal_relevance must remain unresolved')
        normalized.append({
            'category': category,
            'code': code,
            'evidence': _text(finding['evidence'], f'candidate_quality_findings[{index}].evidence'),
            'source': source,
            'recurrence': recurrence,
            'personal_relevance': 'unresolved',
            'risk_text_ru': _text(finding['risk_text_ru'], f'candidate_quality_findings[{index}].risk_text_ru'),
        })
    return normalized


def _strong_personal_findings(negative_findings):
    return [
        finding for finding in (negative_findings or [])
        if isinstance(finding, dict)
        and finding.get('evidence_strength') == 'strong'
        and finding.get('personal_relevance') == 'confirmed'
    ]


def validate_fit_evidence_fields(result, require_v5=True):
    present = EVIDENCE_RESULT_FIELDS & set(result or {})
    if not present and not require_v5:
        return None
    missing = EVIDENCE_RESULT_FIELDS - set(result or {})
    if missing:
        raise ValueError(f'Missing V5 evidence fields: {sorted(missing)!r}')

    state = result.get('fit_evidence_state')
    confidence = result.get('fit_evidence_confidence')
    basis = result.get('fit_evidence_basis')
    if state not in FIT_EVIDENCE_STATES:
        raise ValueError(f'Unknown fit_evidence_state: {state!r}')
    if confidence not in CONFIDENCE_VALUES:
        raise ValueError(f'Unknown fit_evidence_confidence: {confidence!r}')
    if not isinstance(basis, list) or not basis or len(set(basis)) != len(basis):
        raise ValueError('fit_evidence_basis must be a non-empty unique array')
    unknown_basis = set(basis) - BASIS_VALUES
    if unknown_basis:
        raise ValueError(f'Unknown fit_evidence_basis values: {sorted(unknown_basis)!r}')

    history = validate_historical_negative_context(result.get('historical_negative_context'))
    validate_candidate_quality_findings(result.get('candidate_quality_findings'))
    verdict = result.get('verdict')
    fit_level = result.get('fit_level')
    reason_code = result.get('reason_code')
    strong = _strong_personal_findings(result.get('negative_findings'))

    if state == 'sufficient':
        if verdict != 'INCLUDE' or fit_level not in {'strong', 'moderate'}:
            raise ValueError('sufficient evidence state requires INCLUDE strong/moderate fit')
        if confidence not in {'medium', 'high'}:
            raise ValueError('sufficient evidence state requires medium/high confidence')
    elif state == 'insufficient':
        if verdict != 'EXCLUDE' or fit_level != 'below_moderate':
            raise ValueError('insufficient evidence state requires EXCLUDE/below_moderate compatibility fit')
        if confidence not in {'low', 'medium'}:
            raise ValueError('insufficient evidence state requires low/medium confidence')
        if strong:
            raise ValueError('insufficient evidence state cannot contain a strong confirmed personal negative')
        if 'candidate_information_insufficient' not in basis:
            raise ValueError('insufficient evidence state requires candidate_information_insufficient basis')
    elif state == 'reconsiderable':
        if verdict != 'EXCLUDE' or fit_level != 'below_moderate':
            raise ValueError('reconsiderable evidence state requires EXCLUDE/below_moderate compatibility fit')
        if confidence not in {'medium', 'high'}:
            raise ValueError('reconsiderable evidence state requires medium/high confidence')
        if strong:
            raise ValueError('reconsiderable evidence state cannot contain a strong current confirmed personal negative')
        if not history:
            raise ValueError('reconsiderable evidence state requires historical_negative_context')
        if history['recency'] != 'old' or history['exposure_depth'] not in {'brief', 'partial'}:
            raise ValueError('reconsiderable evidence state requires old brief/partial prior exposure')
        if history['reaction'] not in {'non_engagement', 'mixed'}:
            raise ValueError('reconsiderable evidence state requires non-engagement/mixed historical reaction')
        if history['later_reopening_evidence'] == 'none':
            raise ValueError('reconsiderable evidence state requires later reopening evidence')
        if 'historical_user_experience' not in basis:
            raise ValueError('reconsiderable evidence state requires historical_user_experience basis')
    else:
        if verdict != 'EXCLUDE' or fit_level != 'below_moderate' or reason_code != 'exclude_direct_conflict':
            raise ValueError('confirmed_negative requires EXCLUDE/below_moderate/exclude_direct_conflict')
        if confidence != 'high':
            raise ValueError('confirmed_negative requires high confidence')
        if result.get('negative_analysis_status') != 'complete_with_confirmed_negative' or not strong:
            raise ValueError('confirmed_negative requires a complete strong confirmed personal negative finding')
        historical_only = all(row.get('evidence_origin') == 'historical_user_experience' for row in strong)
        if historical_only:
            if not history or history['exposure_depth'] not in {'substantial', 'complete'} or history['reaction'] != 'explicit_dislike':
                raise ValueError('historical evidence alone is confirmed negative only after substantial/complete explicit dislike')

    return {
        'fit_evidence_state': state,
        'fit_evidence_confidence': confidence,
        'fit_evidence_basis': list(basis),
        'historical_negative_context': history,
        'candidate_quality_findings': result.get('candidate_quality_findings'),
    }


def validate_entry_evidence_fields(entry, require_v5=False):
    present = EVIDENCE_RESULT_FIELDS & set(entry or {})
    has_binding = 'evidence_contract_sha' in (entry or {})
    if not present and not has_binding and not require_v5:
        return None
    if require_v5 and not has_binding:
        raise ValueError('V5 Taste entry requires evidence_contract_sha')
    if has_binding:
        sha = entry.get('evidence_contract_sha')
        if not isinstance(sha, str) or len(sha) != 40:
            raise ValueError('evidence_contract_sha must be a Git blob SHA')
    return validate_fit_evidence_fields(entry, require_v5=True)


def evidence_readiness(entry):
    if not isinstance(entry, dict):
        return {
            'fit_evidence_state': None, 'fit_evidence_confidence': None,
            'fit_evidence_ready': False, 'fit_evidence_bound': False,
            'fit_evidence_source': 'missing_entry', 'fit_evidence_backfill_required': True,
        }
    binding = entry.get('evidence_contract_sha')
    if binding is not None:
        if binding != current_evidence_contract_sha():
            return {
                'fit_evidence_state': None, 'fit_evidence_confidence': None,
                'fit_evidence_ready': False, 'fit_evidence_bound': False,
                'fit_evidence_source': 'stale_evidence_contract', 'fit_evidence_backfill_required': True,
            }
        try:
            validate_entry_evidence_fields(entry, require_v5=True)
        except ValueError:
            return {
                'fit_evidence_state': None, 'fit_evidence_confidence': None,
                'fit_evidence_ready': False, 'fit_evidence_bound': False,
                'fit_evidence_source': 'invalid_v5_evidence', 'fit_evidence_backfill_required': True,
            }
        return {
            'fit_evidence_state': entry['fit_evidence_state'],
            'fit_evidence_confidence': entry['fit_evidence_confidence'],
            'fit_evidence_ready': True, 'fit_evidence_bound': True,
            'fit_evidence_source': 'canonical_v5', 'fit_evidence_backfill_required': False,
        }

    if entry.get('verdict') == 'INCLUDE' and not (entry.get('negative_evidence') or []):
        return {
            'fit_evidence_state': 'sufficient', 'fit_evidence_confidence': 'medium',
            'fit_evidence_ready': True, 'fit_evidence_bound': False,
            'fit_evidence_source': 'legacy_include_without_negative', 'fit_evidence_backfill_required': False,
        }
    if entry.get('reason_code') == 'exclude_insufficient':
        return {
            'fit_evidence_state': 'insufficient', 'fit_evidence_confidence': 'low',
            'fit_evidence_ready': True, 'fit_evidence_bound': False,
            'fit_evidence_source': 'legacy_exclude_insufficient', 'fit_evidence_backfill_required': False,
        }
    return {
        'fit_evidence_state': None, 'fit_evidence_confidence': None,
        'fit_evidence_ready': False, 'fit_evidence_bound': False,
        'fit_evidence_source': 'legacy_ambiguous', 'fit_evidence_backfill_required': True,
    }
'''
Path('scripts/taste_evidence_contract.py').write_text(evidence_module, encoding='utf-8')

negative_module = r'''"""Grounded negative-analysis contract shared by Taste cache, queue and visual output.

V5 adds explicit provenance/strength for personal negatives while retaining
legacy V4 parsing during migration. Candidate-quality complaints live in the
separate evidence-state layer and never become personal negatives here.
"""

NEGATIVE_ANALYSIS_STATUSES = {
    'complete_with_confirmed_negative',
    'incomplete_no_confirmed_negative',
}

NEGATIVE_FINDING_CATALOG = {
    'unchanged_repetition': {'category': 'repetition', 'score': 4},
    'low_active_gameplay': {'category': 'activity_balance', 'score': 3},
    'directionlessness': {'category': 'direction', 'score': 4},
    'management_routine': {'category': 'management_routine', 'score': 3},
    'difficulty_punishment': {'category': 'difficulty_friction', 'score': 2},
    'stealth_restart_pressure': {'category': 'stealth_friction', 'score': 2},
    'felt_technical_burden': {'category': 'felt_burden', 'score': 4},
    'other_grounded_taste_risk': {'category': 'other_grounded', 'score': 0},
}
V4_FIELDS = {'category', 'code', 'evidence', 'risk_text_ru'}
V5_FIELDS = V4_FIELDS | {'evidence_origin', 'evidence_strength', 'personal_relevance'}
V5_ORIGINS = {
    'direct_user_reaction', 'title_specific_inspection', 'historical_user_experience',
    'same_series_continuity', 'candidate_specific_profile_conflict',
}
V5_STRENGTH = {'weak', 'moderate', 'strong'}


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a non-empty string')
    return value.strip()


def validate_negative_analysis(status, findings, negative_evidence, require_v5=False):
    if status not in NEGATIVE_ANALYSIS_STATUSES:
        raise ValueError(f'Unknown negative_analysis_status: {status!r}')
    if not isinstance(findings, list):
        raise ValueError('negative_findings must be an array')
    if not isinstance(negative_evidence, list):
        raise ValueError('negative_evidence must be an array')

    normalized = []
    evidence_projection = []
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            raise ValueError(f'negative_findings[{index}] must be an object')
        is_v5 = require_v5 or bool(set(finding) & (V5_FIELDS - V4_FIELDS))
        expected_fields = V5_FIELDS if is_v5 else V4_FIELDS
        unknown = set(finding) - expected_fields
        missing = expected_fields - set(finding)
        if unknown:
            raise ValueError(f'negative_findings[{index}] has unexpected fields: {sorted(unknown)}')
        if missing:
            raise ValueError(f'negative_findings[{index}] missing fields: {sorted(missing)}')

        code = _text(finding['code'], f'negative_findings[{index}].code')
        category = _text(finding['category'], f'negative_findings[{index}].category')
        spec = NEGATIVE_FINDING_CATALOG.get(code)
        if spec is None:
            raise ValueError(f'negative_findings[{index}] has unknown code: {code!r}')
        if category != spec['category']:
            raise ValueError(f'negative_findings[{index}] category/code mismatch: category={category!r} code={code!r}')
        evidence = _text(finding['evidence'], f'negative_findings[{index}].evidence')
        risk_text_ru = _text(finding['risk_text_ru'], f'negative_findings[{index}].risk_text_ru')
        row = {'category': category, 'code': code, 'evidence': evidence, 'risk_text_ru': risk_text_ru}
        if is_v5:
            origin = _text(finding['evidence_origin'], f'negative_findings[{index}].evidence_origin')
            strength = _text(finding['evidence_strength'], f'negative_findings[{index}].evidence_strength')
            relevance = _text(finding['personal_relevance'], f'negative_findings[{index}].personal_relevance')
            if origin not in V5_ORIGINS:
                raise ValueError(f'negative_findings[{index}] has invalid personal-negative evidence origin')
            if strength not in V5_STRENGTH:
                raise ValueError(f'negative_findings[{index}] has invalid evidence strength')
            if relevance != 'confirmed':
                raise ValueError(f'negative_findings[{index}] personal_relevance must be confirmed')
            row.update({
                'evidence_origin': origin,
                'evidence_strength': strength,
                'personal_relevance': relevance,
            })
        normalized.append(row)
        evidence_projection.append(evidence)

    if status == 'complete_with_confirmed_negative':
        if not normalized:
            raise ValueError('complete_with_confirmed_negative requires at least one negative finding')
    elif normalized or negative_evidence:
        raise ValueError('incomplete_no_confirmed_negative requires empty findings and evidence')

    if negative_evidence != evidence_projection:
        raise ValueError('negative_evidence must equal the ordered projection of negative_findings[].evidence')
    return normalized


def validate_entry_negative_fields(entry, *, require_v4=False, require_v5=False):
    has_status = 'negative_analysis_status' in entry
    has_findings = 'negative_findings' in entry
    if (require_v4 or require_v5) and (not has_status or not has_findings):
        raise ValueError('Taste entry requires negative_analysis_status and negative_findings')
    if not has_status and not has_findings:
        return None
    if has_status != has_findings:
        raise ValueError('negative_analysis_status and negative_findings must appear together')
    return validate_negative_analysis(
        entry.get('negative_analysis_status'), entry.get('negative_findings'),
        entry.get('negative_evidence'), require_v5=require_v5,
    )


def negative_readiness(entry):
    if not isinstance(entry, dict) or 'negative_analysis_status' not in entry:
        return {'negative_analysis_status': None, 'confirmed_negative_count': 0, 'negative_analysis_ready': False}
    try:
        findings = validate_entry_negative_fields(entry, require_v4=True)
    except ValueError:
        return {
            'negative_analysis_status': entry.get('negative_analysis_status'),
            'confirmed_negative_count': 0, 'negative_analysis_ready': False,
        }
    status = entry.get('negative_analysis_status')
    count = len(findings or [])
    return {
        'negative_analysis_status': status,
        'confirmed_negative_count': count,
        'negative_analysis_ready': status == 'complete_with_confirmed_negative' and count >= 1,
    }


def structured_grounded_risks(entry):
    readiness = negative_readiness(entry)
    if not readiness['negative_analysis_ready']:
        return {}
    findings = validate_entry_negative_fields(entry, require_v4=True)
    risks = {}
    for finding in findings:
        spec = NEGATIVE_FINDING_CATALOG[finding['code']]
        score = int(spec['score'])
        if 'evidence_strength' in finding:
            if finding['evidence_strength'] == 'weak':
                score = min(score, 1)
            elif finding['evidence_strength'] == 'moderate':
                score = min(score, 3)
        row = {
            'code': finding['code'], 'score': score, 'text': finding['risk_text_ru'],
            'source': 'taste_negative_evidence', 'category': finding['category'],
            'evidence': finding['evidence'],
        }
        for field in ('evidence_origin', 'evidence_strength', 'personal_relevance'):
            if field in finding:
                row[field] = finding[field]
        current = risks.get(finding['code'])
        if current is None or row['score'] > current['score']:
            risks[finding['code']] = row
    return risks
'''
Path('scripts/taste_negative_contract.py').write_text(negative_module, encoding='utf-8')

replace_one(
    'scripts/taste_cache_common.py',
    'from taste_negative_contract import validate_entry_negative_fields\n',
    'from taste_negative_contract import validate_entry_negative_fields\nfrom taste_evidence_contract import validate_entry_evidence_fields\n',
)
replace_one(
    'scripts/taste_cache_common.py',
    '    require_v4_negative_fields=False,\n):',
    '    require_v4_negative_fields=False,\n    require_v5_evidence_fields=False,\n):',
)
replace_one(
    'scripts/taste_cache_common.py',
    '    validate_entry_negative_fields(entry, require_v4=require_v4_negative_fields)\n    return True\n',
    '    validate_entry_negative_fields(\n        entry,\n        require_v4=require_v4_negative_fields,\n        require_v5=require_v5_evidence_fields,\n    )\n    validate_entry_evidence_fields(entry, require_v5=require_v5_evidence_fields)\n    return True\n',
)

replace_one(
    'scripts/ingest_taste_results.py',
    'from taste_negative_contract import validate_negative_analysis\n',
    "from taste_negative_contract import validate_negative_analysis\nfrom taste_evidence_contract import (\n    EVIDENCE_RESULT_FIELDS,\n    current_evidence_contract_sha,\n    validate_fit_evidence_fields,\n)\n",
)
replace_one(
    'scripts/ingest_taste_results.py',
    "OPTIONAL_FULL_RESULT_FIELDS = {'taste_factors'}\n",
    "FULL_RESULT_FIELDS |= EVIDENCE_RESULT_FIELDS\nNEGATIVE_ONLY_RESULT_FIELDS |= EVIDENCE_RESULT_FIELDS\nOPTIONAL_FULL_RESULT_FIELDS = {'taste_factors'}\n",
)
replace_one(
    'scripts/ingest_taste_results.py',
    "    if doc.get('schema_version') != 1 or doc.get('entry_schema_version') not in {2, 3, 4}:\n",
    "    if doc.get('schema_version') != 1 or doc.get('entry_schema_version') not in {2, 3, 4, 5}:\n",
)
replace_one(
    'scripts/ingest_taste_results.py',
    "        result.get('negative_evidence'),\n    )\n",
    "        result.get('negative_evidence'),\n        require_v5=True,\n    )\n",
)
insert_anchor = "def validate_current_base_entry(key, entry, queue_row, projection):\n"
quality_validator = '''def validate_noncommercial_quality_text(name, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be a non-empty string')
    forbidden = [
        'price', 'discount', 'wishlist', 'steamdb', 'historical price', 'sale price',
        'rub', 'kzt', 'цена', 'скидк', 'вишлист', 'историческ', 'руб.', 'рублей', 'тенге', 'распродаж',
    ]
    folded = value.casefold()
    hit = next((fragment for fragment in forbidden if fragment in folded), None)
    if hit is not None:
        raise ValueError(f'{name} contains forbidden commercial evidence fragment: {hit!r}')


'''
replace_one('scripts/ingest_taste_results.py', insert_anchor, quality_validator + insert_anchor)
replace_one(
    'scripts/ingest_taste_results.py',
    "        validate_negative_result_fields(result)\n\n        if full_eval:\n",
    "        validate_negative_result_fields(result)\n        validate_fit_evidence_fields(result, require_v5=True)\n        for q_index, finding in enumerate(result.get('candidate_quality_findings') or []):\n            validate_noncommercial_quality_text(f'candidate_quality_findings[{q_index}].evidence', finding['evidence'])\n            validate_noncommercial_quality_text(f'candidate_quality_findings[{q_index}].risk_text_ru', finding['risk_text_ru'])\n\n        if full_eval:\n",
)
replace_one(
    'scripts/ingest_taste_results.py',
    "            if result['reason_code'] == 'exclude_direct_conflict' and not result['negative_evidence']:\n                raise ValueError(f'exclude_direct_conflict requires explicit negative evidence: {key}')\n",
    "            if (\n                result['reason_code'] == 'exclude_direct_conflict'\n                and result['fit_evidence_state'] == 'confirmed_negative'\n                and not result['negative_evidence']\n            ):\n                raise ValueError(f'confirmed exclude_direct_conflict requires explicit negative evidence: {key}')\n",
)
replace_one(
    'scripts/ingest_taste_results.py',
    "        'negative_evidence': result['negative_evidence'],\n        'evaluated_at_utc': evaluated_at,\n",
    "        'negative_evidence': result['negative_evidence'],\n        'evidence_contract_sha': current_evidence_contract_sha(),\n        'fit_evidence_state': result['fit_evidence_state'],\n        'fit_evidence_confidence': result['fit_evidence_confidence'],\n        'fit_evidence_basis': result['fit_evidence_basis'],\n        'historical_negative_context': result['historical_negative_context'],\n        'candidate_quality_findings': result['candidate_quality_findings'],\n        'evaluated_at_utc': evaluated_at,\n",
)
replace_one(
    'scripts/ingest_taste_results.py',
    "    entry['negative_evidence'] = result['negative_evidence']\n    return entry\n",
    "    entry['negative_evidence'] = result['negative_evidence']\n    entry['evidence_contract_sha'] = current_evidence_contract_sha()\n    for field in EVIDENCE_RESULT_FIELDS:\n        entry[field] = result[field]\n    return entry\n",
)
replace_one(
    'scripts/ingest_taste_results.py',
    "    v4_required = contract.get('schema_v4_required_entry_fields') or base_required\n",
    "    v5_required = contract.get('schema_v5_required_entry_fields') or contract.get('schema_v4_required_entry_fields') or base_required\n",
)
replace_one('scripts/ingest_taste_results.py', "            required_fields = v4_required\n", "            required_fields = v5_required\n")
replace_one(
    'scripts/ingest_taste_results.py',
    "                require_v4_negative_fields=True,\n",
    "                require_v4_negative_fields=True,\n                require_v5_evidence_fields=True,\n",
)
replace_one('scripts/ingest_taste_results.py', "    updated['entry_schema_version'] = 4\n", "    updated['entry_schema_version'] = 5\n")

replace_one(
    'scripts/build_taste_cache_index.py',
    "        'TASTE-CACHE-ENTRY-BINDING-V4',\n",
    "        'TASTE-CACHE-ENTRY-BINDING-V4',\n        'TASTE-CACHE-ENTRY-BINDING-V5',\n",
)
replace_one(
    'scripts/build_taste_cache_index.py',
    "    if overlay.get('schema_version') != 1 or overlay.get('entry_schema_version') not in {2, 3, 4}:\n",
    "    if overlay.get('schema_version') != 1 or overlay.get('entry_schema_version') not in {2, 3, 4, 5}:\n",
)

replace_one(
    'scripts/build_pre_ai_chatgpt_payload.py',
    'from taste_negative_contract import negative_readiness\n',
    'from taste_negative_contract import negative_readiness\nfrom taste_evidence_contract import evidence_readiness\n',
)
new_annotator = '''def annotate_negative_readiness(taste_doc, effective_entries):
    ready_count = 0
    unresolved_cache_hit_count = 0
    evidence_ready_count = 0
    evidence_bound_count = 0
    evidence_backfill_count = 0
    evidence_state_counts = Counter()
    changed = False
    for key, row in (taste_doc.get('entries') or {}).items():
        if row.get('status') == 'cache_hit':
            entry = effective_entries.get(key) or {}
            readiness = negative_readiness(entry)
            evidence = evidence_readiness(entry)
        else:
            readiness = {
                'negative_analysis_status': None,
                'confirmed_negative_count': 0,
                'negative_analysis_ready': False,
            }
            evidence = {
                'fit_evidence_state': None,
                'fit_evidence_confidence': None,
                'fit_evidence_ready': False,
                'fit_evidence_bound': False,
                'fit_evidence_source': 'new_fit_evaluation_required',
                'fit_evidence_backfill_required': False,
            }
        merged = dict(readiness)
        merged.update(evidence)
        for field, value in merged.items():
            if row.get(field) != value:
                row[field] = value
                changed = True
        cached = row.get('cached_taste')
        if isinstance(cached, dict):
            for field, value in merged.items():
                if cached.get(field) != value:
                    cached[field] = value
                    changed = True
        if row.get('status') == 'cache_hit':
            ready_count += int(readiness['negative_analysis_ready'])
            unresolved_cache_hit_count += int(not readiness['negative_analysis_ready'])
            evidence_ready_count += int(evidence['fit_evidence_ready'])
            evidence_bound_count += int(evidence['fit_evidence_bound'])
            evidence_backfill_count += int(evidence['fit_evidence_backfill_required'])
            evidence_state_counts[str(evidence['fit_evidence_state'] or 'unresolved')] += 1

    wanted = {
        'work_code': NEGATIVE_WORK_CODE,
        'cache_hit_ready_count': ready_count,
        'cache_hit_unresolved_count': unresolved_cache_hit_count,
        'legacy_free_text_never_implies_readiness': True,
    }
    if taste_doc.get('negative_analysis') != wanted:
        taste_doc['negative_analysis'] = wanted
        changed = True
    evidence_summary = {
        'work_code': NEGATIVE_WORK_CODE,
        'new_work_code_created': False,
        'cache_hit_ready_count': evidence_ready_count,
        'cache_hit_bound_v5_count': evidence_bound_count,
        'cache_hit_backfill_required_count': evidence_backfill_count,
        'state_counts': dict(sorted(evidence_state_counts.items())),
        'price_blind': True,
    }
    if taste_doc.get('fit_evidence_state') != evidence_summary:
        taste_doc['fit_evidence_state'] = evidence_summary
        changed = True
    if changed:
        TASTE.write_text(json.dumps(taste_doc, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    return ready_count, unresolved_cache_hit_count
'''
replace_between(
    'scripts/build_pre_ai_chatgpt_payload.py',
    'def annotate_negative_readiness(taste_doc, effective_entries):\n',
    '\n\ndef main():',
    new_annotator,
)
replace_one(
    'scripts/build_pre_ai_chatgpt_payload.py',
    '    negative_ready_without_ai_count = 0\n',
    '    negative_ready_without_ai_count = 0\n    evidence_backfill_queue_count = 0\n',
)
cache_start = "        if cache_hit:\n            if cached_taste['verdict'] != 'INCLUDE':\n"
cache_end = "            continue\n\n        work = ['evaluate_taste_fit', 'evaluate_normalized_taste_factors', NEGATIVE_WORK_CODE]\n"
cache_replacement = '''        if cache_hit:
            evidence_backfill = bool(taste_row.get('fit_evidence_backfill_required'))
            if cached_taste['verdict'] != 'INCLUDE':
                if evidence_backfill:
                    work = [NEGATIVE_WORK_CODE]
                    if family.get('requires_ai_base_support'):
                        work.append('resolve_base_support_condition')
                    ai_queue.append({
                        'family_id': family['family_id'],
                        'taste_subject_key': taste_key,
                        'appid': taste_row['appid'],
                        'title': taste_row['taste_subject_title'],
                        'taste_fingerprint': taste_row['taste_fingerprint'],
                        'candidate_context_sha256': taste_row['candidate_context_sha256'],
                        'short_description': taste_row.get('short_description'),
                        'bundle_members': taste_row.get('bundle_members') or [],
                        'resolved_taste_fit': cached_taste['fit_level'],
                        'resolved_taste_verdict': cached_taste['verdict'],
                        'resolved_taste_reason_code': cached_taste['reason_code'],
                        'fit_evidence_state': taste_row.get('fit_evidence_state'),
                        'fit_evidence_confidence': taste_row.get('fit_evidence_confidence'),
                        'fit_evidence_source': taste_row.get('fit_evidence_source'),
                        'negative_analysis_status': taste_row.get('negative_analysis_status'),
                        'confirmed_negative_count': int(taste_row.get('confirmed_negative_count') or 0),
                        'work_required': work,
                        'semantic_condition': semantic_condition,
                    })
                    ai_context.append({
                        'family_id': family['family_id'],
                        'family_type': family['family_type'],
                        'taste_subject_key': taste_key,
                        'semantic_condition': semantic_condition,
                        'context_kind': 'taste_evidence_backfill_only',
                        'commercial_context_withheld': True,
                    })
                    evidence_backfill_queue_count += 1
                    negative_backfill_queue_count += 1
                else:
                    excluded_keys.append(primary_key)
                    state = cached_taste.get('fit_evidence_state') or 'legacy_below_moderate'
                    exclusion_counts[f'valid_cached_taste_{state}'] += 1
                continue

            fit = cached_taste['fit_level']
            selected = strong_scenario if fit == 'strong' else moderate_scenario
            if selected['disposition'] != 'INCLUDE':
                excluded_keys.append(primary_key)
                exclusion_counts['deal_excludes_for_valid_cached_fit'] += 1
                continue

            work = []
            if not taste_row.get('negative_analysis_ready') or evidence_backfill:
                work.append(NEGATIVE_WORK_CODE)
                negative_backfill_queue_count += 1
                evidence_backfill_queue_count += int(evidence_backfill)
            if family.get('requires_ai_base_support'):
                work.append('resolve_base_support_condition')

            if work:
                ai_queue.append({
                    'family_id': family['family_id'],
                    'taste_subject_key': taste_key,
                    'appid': taste_row['appid'],
                    'title': taste_row['taste_subject_title'],
                    'taste_fingerprint': taste_row['taste_fingerprint'],
                    'candidate_context_sha256': taste_row['candidate_context_sha256'],
                    'short_description': taste_row.get('short_description'),
                    'bundle_members': taste_row.get('bundle_members') or [],
                    'resolved_taste_fit': fit,
                    'resolved_taste_verdict': cached_taste['verdict'],
                    'resolved_taste_reason_code': cached_taste['reason_code'],
                    'fit_evidence_state': taste_row.get('fit_evidence_state'),
                    'fit_evidence_confidence': taste_row.get('fit_evidence_confidence'),
                    'fit_evidence_source': taste_row.get('fit_evidence_source'),
                    'negative_analysis_status': taste_row.get('negative_analysis_status'),
                    'confirmed_negative_count': int(taste_row.get('confirmed_negative_count') or 0),
                    'work_required': work,
                    'semantic_condition': semantic_condition,
                })
                ai_context.append(context)
            else:
                negative_ready_without_ai_count += 1
                context['resolved_taste_fit'] = fit
                context['fit_evidence_state'] = taste_row.get('fit_evidence_state')
                context['fit_evidence_confidence'] = taste_row.get('fit_evidence_confidence')
                context['fit_evidence_source'] = taste_row.get('fit_evidence_source')
                context['final_purchase_decision'] = selected['purchase_decision']
                context['final_priority_bucket'] = int(selected['priority_bucket'])
                ready_context.append(context)
            continue

        work = ['evaluate_taste_fit', 'evaluate_normalized_taste_factors', NEGATIVE_WORK_CODE]
'''
replace_between('scripts/build_pre_ai_chatgpt_payload.py', cache_start, cache_end, cache_replacement)
replace_one(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "            'confirmed_negative_count': 0,\n            'work_required': work,\n",
    "            'confirmed_negative_count': 0,\n            'fit_evidence_state': None,\n            'fit_evidence_confidence': None,\n            'fit_evidence_source': 'new_fit_evaluation_required',\n            'work_required': work,\n",
)
replace_one(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "        'schema_version': 4,\n        'purpose': 'chatgpt_consumer_bundle_with_context_bound_strict_price_blind_taste_phase_and_grounded_negative_readiness',\n",
    "        'schema_version': 5,\n        'purpose': 'chatgpt_consumer_bundle_with_context_bound_price_blind_taste_fit_evidence_state_and_grounded_negative_readiness',\n",
)
replace_one(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "            'negative_only_backfill_must_preserve_existing_fit_semantics': True,\n",
    "            'negative_only_backfill_must_preserve_existing_fit_semantics': True,\n            'negative_work_also_resolves_fit_evidence_state_v5': True,\n            'new_evidence_work_code_or_scheduler_created': False,\n            'fit_evidence_states': ['sufficient', 'insufficient', 'reconsiderable', 'confirmed_negative'],\n            'candidate_quality_findings_do_not_change_fit_or_personal_negative': True,\n            'confirmed_negative_cannot_be_rescued_by_paid_commercial_signals': True,\n",
)
replace_one(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "            'negative_ready_without_ai_count': negative_ready_without_ai_count,\n            'normal_ready_requires_confirmed_negative': True,\n",
    "            'negative_ready_without_ai_count': negative_ready_without_ai_count,\n            'evidence_backfill_queue_count': evidence_backfill_queue_count,\n            'normal_ready_requires_confirmed_negative': True,\n",
)
replace_one(
    'scripts/build_pre_ai_chatgpt_payload.py',
    "        'negative_ready_without_ai_count': negative_ready_without_ai_count,\n        'sale_end_coverage': manifest['sale_end_coverage'],\n",
    "        'negative_ready_without_ai_count': negative_ready_without_ai_count,\n        'evidence_backfill_queue_count': evidence_backfill_queue_count,\n        'sale_end_coverage': manifest['sale_end_coverage'],\n",
)

replace_one(
    'scripts/refine_visual_ranking.py',
    "import urllib.request\nfrom pathlib import Path\n",
    "import urllib.request\nfrom pathlib import Path\n\nfrom taste_evidence_contract import evidence_readiness\nfrom taste_negative_contract import structured_grounded_risks\n",
)
personal_risk_helper = '''def personal_taste_risks(taste_entry):
    """Use V5 structured personal negatives once exactly evidence-bound.

    Legacy free text remains a migration fallback so an informed negative such
    as HighFleet is never silently erased before its V5 backfill completes.
    Candidate-quality findings are intentionally absent from this path.
    """
    state = evidence_readiness(taste_entry)
    if state.get('fit_evidence_bound'):
        return structured_grounded_risks(taste_entry)
    risks = {}
    for value in (taste_entry or {}).get('negative_evidence') or []:
        map_negative_evidence(value, risks)
    return risks


'''
replace_one('scripts/refine_visual_ranking.py', '\ndef structural_risks(projection, practical):\n', '\n' + personal_risk_helper + 'def structural_risks(projection, practical):\n')
replace_one('scripts/refine_visual_ranking.py', 'def direct_fit_cap(source_fit, evidence):\n', 'def direct_fit_cap(source_fit, evidence, fit_evidence_state=None):\n')
replace_one(
    'scripts/refine_visual_ranking.py',
    "    if source_fit == 'strong':\n        return 'moderate', 'direct_user_rating_below_3_5_caps_strong'\n",
    "    if fit_evidence_state == 'reconsiderable':\n        return source_fit, 'old_shallow_reconsiderable_rating_does_not_hard_cap_current_fit'\n    if source_fit == 'strong':\n        return 'moderate', 'direct_user_rating_below_3_5_caps_strong'\n",
)
replace_one(
    'scripts/refine_visual_ranking.py',
    "    fit, reason = direct_fit_cap(source_fit, evidence)\n\n    direct_override = bool(evidence)\n",
    "    evidence_state = evidence_readiness(taste_entry)\n    game['fit_evidence_state'] = evidence_state.get('fit_evidence_state')\n    game['fit_evidence_confidence'] = evidence_state.get('fit_evidence_confidence')\n    game['fit_evidence_state_source'] = evidence_state.get('fit_evidence_source')\n    game['fit_evidence_bound'] = bool(evidence_state.get('fit_evidence_bound'))\n    fit, reason = direct_fit_cap(source_fit, evidence, evidence_state.get('fit_evidence_state'))\n\n    direct_override = bool(evidence)\n",
)
replace_one(
    'scripts/refine_visual_ranking.py',
    "        risks = {}\n        for ev in taste_entry.get('negative_evidence') or []:\n            map_negative_evidence(ev, risks)\n",
    "        risks = personal_taste_risks(taste_entry)\n",
)
replace_one(
    'scripts/refine_visual_ranking.py',
    "    contract['taste_evidence_merge_rule'] = 'legacy base plus incremental overlay; overlay exact key wins'\n",
    "    contract['taste_evidence_merge_rule'] = 'legacy fit remains reusable; V5 evidence state is separately bound and ambiguous legacy evidence is backfilled through existing Taste work'\n",
)

replace_one(
    'scripts/build_final_visual_payload.py',
    "    risks = {}\n    for ev in taste_entry.get('negative_evidence') or []:\n        refiner.map_negative_evidence(ev, risks)\n",
    "    risks = refiner.personal_taste_risks(taste_entry)\n",
)
replace_one(
    'scripts/build_ranking_lookup.py',
    "        'fit': game.get('fit'),\n",
    "        'fit': game.get('fit'),\n        'fit_evidence_state': game.get('fit_evidence_state'),\n        'fit_evidence_confidence': game.get('fit_evidence_confidence'),\n        'fit_evidence_state_source': game.get('fit_evidence_state_source'),\n",
)

replace_one(
    'scripts/validate_taste_v3_contract.py',
    "                'risk_text_ru': 'У игры есть подтверждённый персональный минус, который пока не относится к отдельной категории риска.',\n",
    "                'risk_text_ru': 'У игры есть подтверждённый персональный минус, который пока не относится к отдельной категории риска.',\n                'evidence_origin': 'title_specific_inspection',\n                'evidence_strength': 'strong',\n                'personal_relevance': 'confirmed',\n",
)
replace_one(
    'scripts/validate_taste_v3_contract.py',
    "        'negative_evidence': [\n            'A confirmed candidate-specific downside that does not fit the initial taxonomy.'\n        ],\n        'taste_factors': {\n",
    "        'negative_evidence': [\n            'A confirmed candidate-specific downside that does not fit the initial taxonomy.'\n        ],\n        'fit_evidence_state': 'sufficient',\n        'fit_evidence_confidence': 'high',\n        'fit_evidence_basis': ['candidate_specific_positive_match', 'title_specific_inspection'],\n        'historical_negative_context': None,\n        'candidate_quality_findings': [],\n        'taste_factors': {\n",
)
replace_one('scripts/validate_taste_v3_contract.py', "    required = contract['schema_v4_required_entry_fields']\n", "    required = contract['schema_v5_required_entry_fields']\n")
replace_one(
    'scripts/validate_taste_v3_contract.py',
    "        require_v4_negative_fields=True,\n    )\n",
    "        require_v4_negative_fields=True,\n        require_v5_evidence_fields=True,\n    )\n",
)
replace_one(
    'scripts/validate_taste_v3_contract.py',
    "            'negative_analysis_status', 'negative_findings', 'negative_evidence',\n        ]\n",
    "            'negative_analysis_status', 'negative_findings', 'negative_evidence',\n            'fit_evidence_state', 'fit_evidence_confidence', 'fit_evidence_basis',\n            'historical_negative_context', 'candidate_quality_findings',\n        ]\n",
)
replace_one('scripts/validate_taste_v3_contract.py', "        'contract': 'TASTE-SEMANTIC-RESULT-V4',\n", "        'contract': 'TASTE-SEMANTIC-RESULT-V5',\n")
replace_one('scripts/validate_taste_v3_contract.py', "    print('TASTE_V4_CONTRACT_VALIDATION=PASS')\n", "    print('TASTE_V5_CONTRACT_VALIDATION=PASS')\n")

evidence_test = r'''import json
from copy import deepcopy

import ingest_taste_results
import refine_visual_ranking
from taste_evidence_contract import evidence_readiness, validate_fit_evidence_fields
from taste_negative_contract import structured_grounded_risks, validate_negative_analysis


def expect_error(fn, contains):
    try:
        fn()
    except ValueError as exc:
        assert contains in str(exc), (contains, str(exc))
        return
    raise AssertionError(f'Expected ValueError containing {contains!r}')


def base_result(state, confidence, basis, *, reason='exclude_insufficient'):
    return {
        'key': 'App_1', 'appid': '1', 'taste_fingerprint': '1' * 64,
        'candidate_context_sha256': '2' * 64, 'verdict': 'EXCLUDE',
        'fit_level': 'below_moderate', 'reason_code': reason,
        'positive_evidence': [], 'negative_analysis_status': 'incomplete_no_confirmed_negative',
        'negative_findings': [], 'negative_evidence': [],
        'fit_evidence_state': state, 'fit_evidence_confidence': confidence,
        'fit_evidence_basis': basis, 'historical_negative_context': None,
        'candidate_quality_findings': [],
    }


def quality_finding():
    return {
        'category': 'navigation_feedback', 'code': 'opaque_navigation_feedback',
        'evidence': 'Recurring player reports describe unclear action feedback and repeated backtracking.',
        'source': 'recurring_player_complaints', 'recurrence': 'recurring_pattern',
        'personal_relevance': 'unresolved',
        'risk_text_ru': 'Игроки регулярно отмечают непрозрачную обратную связь и возвраты; это требует дополнительной проверки, но не доказывает личный минус.',
    }


def strong_negative(code='felt_technical_burden', category='felt_burden', origin='title_specific_inspection'):
    return {
        'category': category, 'code': code,
        'evidence': 'Direct title-specific inspection produced a strong dry, technical and tedious reaction.',
        'risk_text_ru': 'После прямого просмотра игра ощущается сухой, чрезмерно технической и утомительной.',
        'evidence_origin': origin, 'evidence_strength': 'strong', 'personal_relevance': 'confirmed',
    }


def main():
    haven = base_result('insufficient', 'low', ['candidate_information_insufficient'])
    haven['candidate_quality_findings'] = [quality_finding()]
    validate_fit_evidence_fields(haven)
    assert structured_grounded_risks(haven) == {}

    bioshock = base_result(
        'reconsiderable', 'medium',
        ['historical_user_experience', 'later_quality_reputation_reopened_interest'],
        reason='exclude_direct_conflict',
    )
    bioshock['historical_negative_context'] = {
        'exposure_depth': 'brief', 'recency': 'old', 'reaction': 'non_engagement',
        'later_reopening_evidence': 'quality_reputation',
    }
    validate_fit_evidence_fields(bioshock)
    fit, reason = refine_visual_ranking.direct_fit_cap('strong', {'rating': 3.0}, 'reconsiderable')
    assert fit == 'strong' and 'does_not_hard_cap' in reason

    highfleet = base_result(
        'confirmed_negative', 'high',
        ['direct_user_current_reaction', 'title_specific_inspection'],
        reason='exclude_direct_conflict',
    )
    highfleet['negative_analysis_status'] = 'complete_with_confirmed_negative'
    highfleet['negative_findings'] = [strong_negative()]
    highfleet['negative_evidence'] = [highfleet['negative_findings'][0]['evidence']]
    validate_negative_analysis(highfleet['negative_analysis_status'], highfleet['negative_findings'], highfleet['negative_evidence'], require_v5=True)
    validate_fit_evidence_fields(highfleet)
    risks = structured_grounded_risks(highfleet)
    assert risks['felt_technical_burden']['score'] == 4
    assert refine_visual_ranking.risk_summary(risks)[3] == 'high'

    generic = deepcopy(highfleet['negative_findings'])
    generic[0]['evidence_origin'] = 'generic_feature_hypothesis'
    expect_error(
        lambda: validate_negative_analysis('complete_with_confirmed_negative', generic, [generic[0]['evidence']], require_v5=True),
        'invalid personal-negative evidence origin',
    )

    old_hard = deepcopy(highfleet)
    old_hard['fit_evidence_basis'] = ['historical_user_experience']
    old_hard['negative_findings'][0]['evidence_origin'] = 'historical_user_experience'
    old_hard['historical_negative_context'] = {
        'exposure_depth': 'brief', 'recency': 'old', 'reaction': 'non_engagement',
        'later_reopening_evidence': 'none',
    }
    expect_error(lambda: validate_fit_evidence_fields(old_hard), 'substantial/complete explicit dislike')

    informed = deepcopy(old_hard)
    informed['historical_negative_context'] = {
        'exposure_depth': 'substantial', 'recency': 'recent', 'reaction': 'explicit_dislike',
        'later_reopening_evidence': 'none',
    }
    validate_fit_evidence_fields(informed)

    quality_only = deepcopy(haven)
    validate_fit_evidence_fields(quality_only)
    assert quality_only['candidate_quality_findings']
    assert structured_grounded_risks(quality_only) == {}

    expect_error(
        lambda: ingest_taste_results.validate_noncommercial_quality_text('quality', 'Great only because the discount is 90%'),
        'forbidden commercial evidence fragment',
    )

    legacy_include = {'verdict': 'INCLUDE', 'fit_level': 'moderate', 'reason_code': 'include_moderate', 'negative_evidence': []}
    assert evidence_readiness(legacy_include)['fit_evidence_state'] == 'sufficient'
    legacy_insufficient = {'verdict': 'EXCLUDE', 'fit_level': 'below_moderate', 'reason_code': 'exclude_insufficient', 'negative_evidence': []}
    assert evidence_readiness(legacy_insufficient)['fit_evidence_state'] == 'insufficient'
    legacy_bioshock = {'verdict': 'EXCLUDE', 'fit_level': 'below_moderate', 'reason_code': 'exclude_direct_conflict', 'negative_evidence': ['old attempt']}
    assert evidence_readiness(legacy_bioshock)['fit_evidence_backfill_required'] is True
    legacy_risk = {'verdict': 'INCLUDE', 'fit_level': 'moderate', 'reason_code': 'include_moderate', 'negative_evidence': ['direction unclear']}
    assert evidence_readiness(legacy_risk)['fit_evidence_backfill_required'] is True

    print(json.dumps({
        'status': 'PASS', 'insufficient_not_confirmed_negative': True,
        'reconsiderable_not_confirmed_negative': True,
        'old_shallow_weaker_than_informed_rejection': True,
        'generic_feature_cannot_create_strong_personal_negative': True,
        'candidate_quality_risk_without_personal_dislike': True,
        'highfleet_strong_negative_score': risks['felt_technical_burden']['score'],
        'bioshock_reconsiderable_supported': True, 'haven_moon_insufficient_supported': True,
        'commercial_signals_rejected_from_evidence_state': True,
        'legacy_ambiguous_backfill_required': True,
    }, ensure_ascii=False, indent=2))
    print('TASTE_EVIDENCE_STATE_TEST=PASS')


if __name__ == '__main__':
    main()
'''
Path('scripts/test_taste_evidence_states.py').write_text(evidence_test, encoding='utf-8')

routes = Path('PROJECT_ROUTES.md')
route_text = routes.read_text(encoding='utf-8')
if '## Taste V5 / evidence state and reconsideration' not in route_text:
    route_text += '''\n\n---\n\n## Taste V5 / evidence state and reconsideration\n\n**Что ищем:** price-blind distinction between `sufficient`, `insufficient`, `reconsiderable`, and `confirmed_negative` without invalidating reusable fit verdicts.\n\n**Канонические контракты:**\n- `config/mailing_policy.json -> taste_evidence_state`;\n- `config/taste_result_contract.json` (`TASTE-SEMANTIC-RESULT-V5`);\n- `config/taste_cache_entry_contract.json` (`TASTE-CACHE-ENTRY-BINDING-V5`);\n- `config/taste_ledger_contract.json` keeps the binary fit ledger as compatibility/eligibility only.\n\n**Быстрая точка входа:**\n1. `scripts/taste_evidence_contract.py` — state/confidence/history/candidate-quality validation + legacy compatibility.\n2. `scripts/taste_negative_contract.py` — V5 personal-negative provenance/strength; legacy V4 accepted only for migration.\n3. `scripts/ingest_taste_results.py` — GitHub stamps exact `evidence_contract_sha`; evidence-only backfill preserves fit semantics.\n4. `scripts/build_pre_ai_chatgpt_payload.py` — reuses `resolve_grounded_negative_analysis`; ambiguous legacy excludes are queued for evidence backfill before being interpreted as dislike.\n5. `scripts/refine_visual_ranking.py` — exact V5 state uses structured personal negatives; legacy free text remains only until backfill, preventing migration-time loss of real negatives.\n6. `scripts/test_taste_evidence_states.py` — Haven Moon / BioShock / HighFleet and evidence-boundary controls.\n\n**Архитектурный инвариант:** evidence-state binding is orthogonal to the existing fit semantic digest. No new scheduler, queue authority, ranking authority, wishlist override, or play-role logic is introduced.\n'''
    routes.write_text(route_text, encoding='utf-8')

decisions = Path('PROJECT_DECISIONS.md')
decision_text = decisions.read_text(encoding='utf-8')
if '## TASTE-001 — Evidence confidence is not the fit verdict' not in decision_text:
    decision_text += '''\n\n---\n\n## TASTE-001 — Evidence confidence is not the fit verdict\n\n**Дата:** 2026-09-05  \n**Статус:** implemented as internal Taste step 1; independent Taste Review required before material product acceptance.\n\n**Решение:** binary `INCLUDE/EXCLUDE` and `strong/moderate/below_moderate` remain compatibility fit/eligibility semantics, while a separately bound price-blind evidence layer distinguishes `sufficient`, `insufficient`, `reconsiderable`, and `confirmed_negative`.\n\n**Почему:** lack of evidence, an old shallow failed attempt, and a current informed rejection have different meaning. Collapsing them into `below_moderate` made uncertainty look like dislike and could turn old non-engagement into a permanent veto.\n\n**Граница:** price, discount, wishlist and bundle value never manufacture or change evidence state. Recurring public complaints may establish candidate-quality risk but stay `personal_relevance=unresolved`; a strong personal-negative finding requires candidate-specific personal/title evidence. `confirmed_negative` remains non-overridable by paid commercial value.\n\n**Миграция:** existing exact fit bindings remain reusable. Safe legacy cases receive compatibility evidence states; ambiguous legacy direct-conflict/audited-below and risk-bearing include rows are backfilled through the existing `resolve_grounded_negative_analysis` work path. Until exact V5 backfill, legacy personal-risk scoring remains fail-safe so real negatives are not silently erased.\n\n**Не делать:** не use evidence state as wishlist override, play-role/start-priority, discount boost, second ranking formula, or new semantic scheduler.\n\n**Основные места:** `config/taste_result_contract.json`, `config/taste_cache_entry_contract.json`, `scripts/taste_evidence_contract.py`, `scripts/ingest_taste_results.py`, `scripts/build_pre_ai_chatgpt_payload.py`, `scripts/refine_visual_ranking.py`.\n'''
    decisions.write_text(decision_text, encoding='utf-8')

after_policy = load('config/mailing_policy.json')
after_contract = load('config/taste_cache_entry_contract.json')
after_semantics = taste_semantics_digest(after_policy, after_contract)
if before_semantics != after_semantics:
    raise SystemExit(f'Existing fit semantic digest changed unexpectedly: {before_semantics} -> {after_semantics}')
Path('/tmp/taste_fit_semantics_digest.txt').write_text(after_semantics, encoding='utf-8')
print(f'FIT_SEMANTICS_UNCHANGED={after_semantics}')
