"""Producer-owned play-role and relative start-priority context.

This layer is intentionally orthogonal to reusable Taste fit, evidence state,
commercial urgency/value, and the one canonical final ranker. It is conservative:
only explicit title-specific calibrations resolve a role/start state; otherwise the
result stays unresolved. Step-1 confirmed_negative is a hard guard that can never
produce high start priority.
"""

import json
from collections import Counter
from pathlib import Path

from taste_evidence_contract import evidence_readiness

CONTRACT_PATH = Path('config/play_priority_context_contract.json')
OUTPUT_FIELDS = (
    'play_role',
    'play_role_confidence',
    'play_role_provenance',
    'relative_start_priority',
    'relative_start_priority_confidence',
    'relative_start_priority_provenance',
    'play_priority_context_source',
    'play_priority_context_contract',
)


def load_contract(path=CONTRACT_PATH):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    validate_contract(data)
    return data


def normalize_title(value):
    return ' '.join(str(value or '').strip().casefold().split())


def validate_contract(contract):
    roles = set(contract.get('play_role_values') or [])
    starts = set(contract.get('relative_start_priority_values') or [])
    confidence = set(contract.get('confidence_values') or [])
    if roles != {'main_full', 'secondary_palate_cleanser', 'family_coop', 'unresolved'}:
        raise ValueError('play role vocabulary drift')
    if starts != {'high', 'ordinary', 'low', 'unresolved'}:
        raise ValueError('relative start-priority vocabulary drift')
    if confidence != {'low', 'medium', 'high'}:
        raise ValueError('confidence vocabulary drift')
    rules = contract.get('semantic_rules') or {}
    required_true = {
        'orthogonal_to_fit',
        'orthogonal_to_sale_urgency',
        'wishlist_cannot_resolve_or_raise_start_priority',
        'price_discount_purchase_decision_cannot_resolve_or_raise_start_priority',
        'strong_fit_does_not_imply_main_role',
        'franchise_history_is_weak_prior_only',
        'franchise_history_alone_cannot_resolve_role_or_start_priority',
        'confirmed_negative_forces_non_high_start_priority',
    }
    if any(rules.get(key) is not True for key in required_true):
        raise ValueError('semantic separation rule missing')
    if any(rules.get(key) is not False for key in (
        'changes_eligibility', 'changes_fit', 'changes_total_score',
        'changes_priority_rank', 'creates_sorter',
    )):
        raise ValueError('context contract must not create ranking/eligibility authority')
    forbidden = set(contract.get('forbidden_resolution_inputs') or [])
    if not {'wishlist', 'discount_percent', 'current_price_rub', 'sale_expiry_urgency', 'priority_rank', 'total_score'} <= forbidden:
        raise ValueError('commercial/ranking forbidden inputs are incomplete')
    seen = {}
    for key, hint in (contract.get('title_calibrations') or {}).items():
        _validate_hint(hint, roles, starts, confidence, key)
        for alias in hint.get('aliases') or []:
            normalized = normalize_title(alias)
            if not normalized:
                raise ValueError(f'{key}: empty alias')
            if normalized in seen:
                raise ValueError(f'duplicate title alias: {alias!r}')
            seen[normalized] = key
    return contract


def _validate_hint(hint, roles=None, starts=None, confidence=None, label='hint'):
    roles = roles or {'main_full', 'secondary_palate_cleanser', 'family_coop', 'unresolved'}
    starts = starts or {'high', 'ordinary', 'low', 'unresolved'}
    confidence = confidence or {'low', 'medium', 'high'}
    if hint.get('play_role') not in roles:
        raise ValueError(f'{label}: invalid play_role')
    if hint.get('relative_start_priority') not in starts:
        raise ValueError(f'{label}: invalid relative_start_priority')
    if hint.get('play_role_confidence') not in confidence:
        raise ValueError(f'{label}: invalid play_role_confidence')
    if hint.get('relative_start_priority_confidence') not in confidence:
        raise ValueError(f'{label}: invalid relative_start_priority_confidence')
    provenance = hint.get('provenance') or []
    if not isinstance(provenance, list) or not provenance or any(not isinstance(x, str) or not x.strip() for x in provenance):
        raise ValueError(f'{label}: provenance must be non-empty strings')


def _confirmed_negative(taste_entry):
    if not isinstance(taste_entry, dict):
        return False
    readiness = evidence_readiness(taste_entry)
    return readiness.get('fit_evidence_ready') is True and readiness.get('fit_evidence_state') == 'confirmed_negative'


def _default_context(contract, source='unresolved'):
    default = contract['default_context']
    provenance = list(default['provenance'])
    return {
        'play_role': default['play_role'],
        'play_role_confidence': default['play_role_confidence'],
        'play_role_provenance': provenance,
        'relative_start_priority': default['relative_start_priority'],
        'relative_start_priority_confidence': default['relative_start_priority_confidence'],
        'relative_start_priority_provenance': provenance,
        'play_priority_context_source': source,
        'play_priority_context_contract': contract['contract_id'],
    }


def resolve_from_hint(hint, *, contract=None, confirmed_negative=False, source='title_specific_calibration'):
    contract = contract or load_contract()
    _validate_hint(hint)
    if confirmed_negative:
        provenance = ['confirmed_negative_step1_guard']
        return {
            'play_role': contract['semantic_rules']['confirmed_negative_play_role'],
            'play_role_confidence': 'high',
            'play_role_provenance': provenance,
            'relative_start_priority': contract['semantic_rules']['confirmed_negative_start_priority'],
            'relative_start_priority_confidence': 'high',
            'relative_start_priority_provenance': provenance,
            'play_priority_context_source': 'confirmed_negative_guard',
            'play_priority_context_contract': contract['contract_id'],
        }
    if hint.get('title_specific_evidence') is not True:
        unresolved = _default_context(contract, source='weak_prior_only')
        provenance = list(hint.get('provenance') or unresolved['play_role_provenance'])
        unresolved['play_role_provenance'] = provenance
        unresolved['relative_start_priority_provenance'] = provenance
        return unresolved
    provenance = list(hint['provenance'])
    return {
        'play_role': hint['play_role'],
        'play_role_confidence': hint['play_role_confidence'],
        'play_role_provenance': provenance,
        'relative_start_priority': hint['relative_start_priority'],
        'relative_start_priority_confidence': hint['relative_start_priority_confidence'],
        'relative_start_priority_provenance': provenance,
        'play_priority_context_source': source,
        'play_priority_context_contract': contract['contract_id'],
    }


def _calibration_index(contract):
    index = {}
    for key, hint in (contract.get('title_calibrations') or {}).items():
        for alias in hint.get('aliases') or []:
            index[normalize_title(alias)] = (key, hint)
    return index


def context_for_game(game, taste_entry=None, contract=None):
    contract = contract or load_contract()
    if _confirmed_negative(taste_entry):
        # A synthetic resolved hint is supplied only so the guard is exercised before
        # any title calibration. Its values are never observable after this branch.
        guard_hint = {
            'title_specific_evidence': True,
            'play_role': 'main_full',
            'play_role_confidence': 'high',
            'relative_start_priority': 'high',
            'relative_start_priority_confidence': 'high',
            'provenance': ['guard_probe'],
        }
        return resolve_from_hint(guard_hint, contract=contract, confirmed_negative=True)
    title = normalize_title((game or {}).get('title'))
    match = _calibration_index(contract).get(title)
    if not match:
        return _default_context(contract)
    _, hint = match
    return resolve_from_hint(hint, contract=contract)


def apply_to_game(game, taste_entry=None, contract=None):
    resolved = context_for_game(game, taste_entry, contract)
    changed = False
    for key in OUTPUT_FIELDS:
        value = resolved[key]
        if game.get(key) != value:
            game[key] = value
            changed = True
    return changed


def distributions(items):
    roles = Counter(str((row or {}).get('play_role') or 'unresolved') for row in (items or []))
    starts = Counter(str((row or {}).get('relative_start_priority') or 'unresolved') for row in (items or []))
    return {
        'play_role': dict(sorted(roles.items())),
        'relative_start_priority': dict(sorted(starts.items())),
    }
