"""Canonical V5 evidence-state validation for price-blind Taste.

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
