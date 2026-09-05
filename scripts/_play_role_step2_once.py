import json
from pathlib import Path

ROOT = Path('.')


def write_json(path, data):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def write_text(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + '\n', encoding='utf-8')


def replace_once(path, old, new):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected one patch anchor, found {count}: {old[:120]!r}')
    p.write_text(text.replace(old, new, 1), encoding='utf-8')


def append_once(path, marker, block):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    if marker in text:
        return
    p.write_text(text.rstrip() + '\n\n' + block.strip() + '\n', encoding='utf-8')


contract = {
    'contract_id': 'PLAY-ROLE-START-PRIORITY-V1',
    'schema_version': 1,
    'purpose': 'Producer-owned semantic context separating personal fit, play role, relative start priority, and commercial purchase urgency.',
    'play_role_values': [
        'main_full',
        'secondary_palate_cleanser',
        'family_coop',
        'unresolved',
    ],
    'relative_start_priority_values': ['high', 'ordinary', 'low', 'unresolved'],
    'confidence_values': ['low', 'medium', 'high'],
    'semantic_rules': {
        'orthogonal_to_fit': True,
        'orthogonal_to_sale_urgency': True,
        'wishlist_cannot_resolve_or_raise_start_priority': True,
        'price_discount_purchase_decision_cannot_resolve_or_raise_start_priority': True,
        'strong_fit_does_not_imply_main_role': True,
        'franchise_history_is_weak_prior_only': True,
        'franchise_history_alone_cannot_resolve_role_or_start_priority': True,
        'confirmed_negative_forces_non_high_start_priority': True,
        'confirmed_negative_start_priority': 'low',
        'confirmed_negative_play_role': 'unresolved',
        'changes_eligibility': False,
        'changes_fit': False,
        'changes_total_score': False,
        'changes_priority_rank': False,
        'creates_sorter': False,
    },
    'forbidden_resolution_inputs': [
        'wishlist',
        'discount_percent',
        'current_price_rub',
        'original_price_rub',
        'history_quality',
        'purchase_decision',
        'decision',
        'sale_end_utc',
        'sale_expiry_urgency',
        'sale_expiry_urgency_rank',
        'priority_rank',
        'total_score',
        'personal_score',
        'purchase_score',
    ],
    'default_context': {
        'play_role': 'unresolved',
        'play_role_confidence': 'low',
        'relative_start_priority': 'unresolved',
        'relative_start_priority_confidence': 'low',
        'provenance': ['no_title_specific_role_or_start_evidence'],
    },
    'title_calibrations': {
        'sifu': {
            'aliases': ['Sifu'],
            'title_specific_evidence': True,
            'play_role': 'main_full',
            'play_role_confidence': 'high',
            'relative_start_priority': 'high',
            'relative_start_priority_confidence': 'high',
            'provenance': ['reviewer_calibrated_title_specific_current_interest'],
        },
        'high_on_life': {
            'aliases': ['High On Life'],
            'title_specific_evidence': True,
            'play_role': 'main_full',
            'play_role_confidence': 'high',
            'relative_start_priority': 'ordinary',
            'relative_start_priority_confidence': 'high',
            'provenance': ['reviewer_calibrated_title_specific_role'],
        },
        'amnesia_the_bunker': {
            'aliases': ['Amnesia: The Bunker'],
            'title_specific_evidence': True,
            'play_role': 'main_full',
            'play_role_confidence': 'high',
            'relative_start_priority': 'ordinary',
            'relative_start_priority_confidence': 'high',
            'provenance': ['reviewer_calibrated_title_specific_role'],
        },
        'terminator_resistance': {
            'aliases': ['Terminator: Resistance'],
            'title_specific_evidence': True,
            'play_role': 'main_full',
            'play_role_confidence': 'medium',
            'relative_start_priority': 'ordinary',
            'relative_start_priority_confidence': 'high',
            'provenance': ['reviewer_calibrated_title_specific_role', 'franchise_history_weak_prior'],
        },
        'tails_of_iron_2': {
            'aliases': ['Tails of Iron 2', 'Tails of Iron 2: Whiskers of Winter'],
            'title_specific_evidence': True,
            'play_role': 'secondary_palate_cleanser',
            'play_role_confidence': 'high',
            'relative_start_priority': 'ordinary',
            'relative_start_priority_confidence': 'high',
            'provenance': ['reviewer_calibrated_title_specific_role'],
        },
        'trine_4': {
            'aliases': ['Trine 4', 'Trine 4: The Nightmare Prince'],
            'title_specific_evidence': True,
            'play_role': 'family_coop',
            'play_role_confidence': 'high',
            'relative_start_priority': 'ordinary',
            'relative_start_priority_confidence': 'medium',
            'provenance': ['reviewer_calibrated_confirmed_family_play_positive'],
        },
        'tmnt_splintered_fate': {
            'aliases': ['TMNT: Splintered Fate', 'Teenage Mutant Ninja Turtles: Splintered Fate'],
            'title_specific_evidence': False,
            'play_role': 'unresolved',
            'play_role_confidence': 'low',
            'relative_start_priority': 'unresolved',
            'relative_start_priority_confidence': 'low',
            'provenance': ['franchise_history_weak_prior'],
        },
    },
    'control_expectations': {
        'Sifu': {'play_role': 'main_full', 'relative_start_priority': 'high'},
        'High On Life': {'play_role': 'main_full', 'relative_start_priority': 'ordinary'},
        'Amnesia: The Bunker': {'play_role': 'main_full', 'relative_start_priority': 'ordinary'},
        'Terminator: Resistance': {'play_role': 'main_full', 'relative_start_priority': 'ordinary'},
        'Tails of Iron 2': {'play_role': 'secondary_palate_cleanser', 'relative_start_priority': 'ordinary'},
        'Trine 4': {'play_role': 'family_coop', 'relative_start_priority': 'ordinary'},
        'TMNT: Splintered Fate': {'play_role': 'unresolved', 'relative_start_priority': 'unresolved'},
        'HighFleet': {'play_role': 'unresolved', 'relative_start_priority': 'low', 'requires_fit_evidence_state': 'confirmed_negative'},
    },
}
write_json('config/play_priority_context_contract.json', contract)

helper = r'''"""Producer-owned play-role and relative start-priority context.

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
'''
write_text('scripts/play_priority_context.py', helper)

test = r'''import copy
import json
from pathlib import Path

import build_ranking_lookup
import play_priority_context as context
from taste_evidence_contract import current_evidence_contract_sha


def assert_context(title, role, start, taste_entry=None, **extra):
    game = {'title': title, **extra}
    resolved = context.context_for_game(game, taste_entry or {})
    assert resolved['play_role'] == role, (title, resolved)
    assert resolved['relative_start_priority'] == start, (title, resolved)
    return resolved


def confirmed_negative_entry():
    return {
        'evidence_contract_sha': current_evidence_contract_sha(),
        'verdict': 'EXCLUDE',
        'fit_level': 'below_moderate',
        'reason_code': 'exclude_direct_conflict',
        'fit_evidence_state': 'confirmed_negative',
        'fit_evidence_confidence': 'high',
        'fit_evidence_basis': ['direct_user_current_reaction'],
        'historical_negative_context': None,
        'candidate_quality_findings': [],
        'negative_analysis_status': 'complete_with_confirmed_negative',
        'negative_findings': [{
            'evidence_strength': 'strong',
            'personal_relevance': 'confirmed',
            'evidence_origin': 'direct_user_current_reaction',
        }],
    }


def main():
    contract = context.load_contract()
    expected = contract['control_expectations']

    sifu = assert_context('Sifu', 'main_full', 'high')
    high_on_life = assert_context('High On Life', 'main_full', 'ordinary', wishlist=True)
    amnesia = assert_context('Amnesia: The Bunker', 'main_full', 'ordinary')
    terminator = assert_context('Terminator: Resistance', 'main_full', 'ordinary', sale_expiry_urgency='today')
    tails = assert_context('Tails of Iron 2: Whiskers of Winter', 'secondary_palate_cleanser', 'ordinary', fit='strong')
    trine = assert_context('Trine 4: The Nightmare Prince', 'family_coop', 'ordinary')
    tmnt = assert_context('TMNT: Splintered Fate', 'unresolved', 'unresolved')
    highfleet = assert_context('HighFleet', 'unresolved', 'low', confirmed_negative_entry())

    for title, exp in expected.items():
        if title == 'HighFleet':
            got = context.context_for_game({'title': title}, confirmed_negative_entry())
        else:
            got = context.context_for_game({'title': title}, {})
        assert got['play_role'] == exp['play_role'], (title, got, exp)
        assert got['relative_start_priority'] == exp['relative_start_priority'], (title, got, exp)

    # Commercial urgency and wishlist are deliberately invisible to the resolver.
    commercial_variants = [
        {'title': 'High On Life', 'wishlist': False, 'sale_expiry_urgency': 'today', 'discount_percent': 90, 'current_price_rub': 1, 'decision': 'БРАТЬ СЕЙЧАС'},
        {'title': 'High On Life', 'wishlist': True, 'sale_expiry_urgency': 'later_or_unknown', 'discount_percent': 0, 'current_price_rub': 9999, 'decision': 'ЛУЧШЕ ЖДАТЬ'},
    ]
    commercial_results = [context.context_for_game(row, {}) for row in commercial_variants]
    assert commercial_results[0] == commercial_results[1]
    assert commercial_results[0]['relative_start_priority'] == 'ordinary'

    terminator_today = context.context_for_game({'title': 'Terminator: Resistance', 'sale_expiry_urgency': 'today'}, {})
    terminator_later = context.context_for_game({'title': 'Terminator: Resistance', 'sale_expiry_urgency': 'later_or_unknown'}, {})
    assert terminator_today == terminator_later
    assert terminator_today['relative_start_priority'] == 'ordinary'

    # Strong fit can remain a secondary role; role is not a renamed fit score.
    assert tails['play_role'] == 'secondary_palate_cleanser'
    assert tails['relative_start_priority'] == 'ordinary'

    # Family role survives downstream and is not rewritten to a solo/main role.
    visual_game = {
        'title': 'Trine 4',
        'fit': 'strong',
        'priority_rank': 11,
        'total_score': 77.5,
        'personal_score': 44.0,
        'purchase_score': 33.5,
        'score_breakdown': {},
    }
    before_rank_fields = {key: copy.deepcopy(visual_game.get(key)) for key in ('fit', 'priority_rank', 'total_score', 'personal_score', 'purchase_score')}
    assert context.apply_to_game(visual_game, {}) is True
    for key, before in before_rank_fields.items():
        assert visual_game.get(key) == before, (key, before, visual_game.get(key))
    compact = build_ranking_lookup.compact_row(visual_game)
    assert compact['play_role'] == 'family_coop'
    assert compact['relative_start_priority'] == 'ordinary'

    # Franchise history alone stays unresolved, but title-specific evidence can resolve
    # either main or secondary independently; it is a prior, not a hard cap.
    assert tmnt['play_priority_context_source'] == 'weak_prior_only'
    title_specific_main = {
        'title_specific_evidence': True,
        'play_role': 'main_full',
        'play_role_confidence': 'medium',
        'relative_start_priority': 'ordinary',
        'relative_start_priority_confidence': 'medium',
        'provenance': ['title_specific_followup_evidence', 'franchise_history_weak_prior'],
    }
    title_specific_secondary = dict(title_specific_main, play_role='secondary_palate_cleanser')
    assert context.resolve_from_hint(title_specific_main)['play_role'] == 'main_full'
    assert context.resolve_from_hint(title_specific_secondary)['play_role'] == 'secondary_palate_cleanser'

    # Step-1 confirmed negative always wins over any hypothetical high/main hint.
    aggressive_hint = {
        'title_specific_evidence': True,
        'play_role': 'main_full',
        'play_role_confidence': 'high',
        'relative_start_priority': 'high',
        'relative_start_priority_confidence': 'high',
        'provenance': ['hypothetical_title_specific_interest'],
    }
    guarded = context.resolve_from_hint(aggressive_hint, confirmed_negative=True)
    assert guarded['play_role'] == 'unresolved'
    assert guarded['relative_start_priority'] == 'low'
    assert highfleet['relative_start_priority'] != 'high'

    # Uncalibrated candidates stay unresolved instead of being inferred from genre/score.
    unknown = context.context_for_game({'title': 'Unknown Control', 'fit': 'strong', 'total_score': 99, 'wishlist': True}, {})
    assert unknown['play_role'] == 'unresolved'
    assert unknown['relative_start_priority'] == 'unresolved'

    result = {
        'status': 'PASS',
        'contract': contract['contract_id'],
        'controls': {
            'Sifu': [sifu['play_role'], sifu['relative_start_priority']],
            'High On Life': [high_on_life['play_role'], high_on_life['relative_start_priority']],
            'Amnesia: The Bunker': [amnesia['play_role'], amnesia['relative_start_priority']],
            'Terminator: Resistance': [terminator['play_role'], terminator['relative_start_priority']],
            'Tails of Iron 2': [tails['play_role'], tails['relative_start_priority']],
            'Trine 4': [trine['play_role'], trine['relative_start_priority']],
            'TMNT: Splintered Fate': [tmnt['play_role'], tmnt['relative_start_priority']],
            'HighFleet': [highfleet['play_role'], highfleet['relative_start_priority']],
        },
        'wishlist_invariance': True,
        'sale_urgency_invariance': True,
        'strong_fit_secondary_supported': True,
        'family_role_downstream_supported': True,
        'franchise_prior_not_hard_cap': True,
        'confirmed_negative_cannot_be_high': True,
        'ranking_fields_immutable': True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print('PLAY_PRIORITY_CONTEXT_TEST=PASS')


if __name__ == '__main__':
    main()
'''
write_text('scripts/test_play_priority_context.py', test)

# Final visual producer: enrich fields in both full build and deterministic refresh,
# but never feed them into priority_ranking.
replace_once(
    'scripts/build_final_visual_payload.py',
    'import giveaway_visual_handoff\nimport priority_ranking\n',
    'import giveaway_visual_handoff\nimport play_priority_context\nimport priority_ranking\n',
)
replace_once(
    'scripts/build_final_visual_payload.py',
    "        if explanation_changed:\n            explanation_touched += 1\n            changed = True\n\n        if changed:\n",
    "        if explanation_changed:\n            explanation_touched += 1\n            changed = True\n\n        if play_priority_context.apply_to_game(game, taste_entry):\n            changed = True\n\n        if changed:\n",
)
replace_once(
    'scripts/build_final_visual_payload.py',
    "        apply_duration_resolution(game, projection, duration_entries)\n\n        if not refiner.apply_commercial_branch(game, context):\n",
    "        apply_duration_resolution(game, projection, duration_entries)\n        play_priority_context.apply_to_game(game, taste_entry)\n\n        if not refiner.apply_commercial_branch(game, context):\n",
)
replace_once(
    'scripts/build_final_visual_payload.py',
    "    contract['card_explanation_rule'] = 'positive requires specific Taste evidence; visible negative requires grounded provenance; scoring/ranking semantics unchanged'\n    contract['duration_source_distribution'] = duration_source_distribution(items)\n",
    "    contract['card_explanation_rule'] = 'positive requires specific Taste evidence; visible negative requires grounded provenance; scoring/ranking semantics unchanged'\n    contract['play_priority_context_helper_blob_sha'] = base_builder.git_sha('scripts/play_priority_context.py')\n    contract['play_priority_context_contract_blob_sha'] = base_builder.git_sha('config/play_priority_context_contract.json')\n    contract['play_priority_context_rule'] = 'play role and relative start priority are producer-owned semantic context; they do not change eligibility, fit, sale urgency, total_score, priority_rank, or create a second sorter'\n    contract['play_priority_context_distribution'] = play_priority_context.distributions(items)\n    contract['duration_source_distribution'] = duration_source_distribution(items)\n",
)
replace_once(
    'scripts/build_final_visual_payload.py',
    "        'card_explanation_policy_blob_sha': base_builder.git_sha('scripts/card_explanation_policy.py'),\n        'achievement_quality_builder_blob_sha': base_builder.git_sha('scripts/achievement_quality.py'),\n",
    "        'card_explanation_policy_blob_sha': base_builder.git_sha('scripts/card_explanation_policy.py'),\n        'play_priority_context_helper_blob_sha': base_builder.git_sha('scripts/play_priority_context.py'),\n        'play_priority_context_contract_blob_sha': base_builder.git_sha('config/play_priority_context_contract.json'),\n        'achievement_quality_builder_blob_sha': base_builder.git_sha('scripts/achievement_quality.py'),\n",
)
replace_once(
    'scripts/build_final_visual_payload.py',
    "        'card_explanation_rule': 'positive requires specific Taste evidence; visible negative requires grounded provenance; scoring/ranking semantics unchanged',\n        'fixed_package_purchase_option_rule': (\n",
    "        'card_explanation_rule': 'positive requires specific Taste evidence; visible negative requires grounded provenance; scoring/ranking semantics unchanged',\n        'play_priority_context_rule': 'play role and relative start priority are producer-owned semantic context; they do not change eligibility, fit, sale urgency, total_score, priority_rank, or create a second sorter',\n        'play_priority_context_distribution': play_priority_context.distributions(refined),\n        'fixed_package_purchase_option_rule': (\n",
)

# Diagnostics carry the orthogonal fields without changing rank math.
replace_once(
    'scripts/build_ranking_lookup.py',
    "        'fit_evidence_state_source': game.get('fit_evidence_state_source'),\n        'decision': game.get('decision'),\n",
    "        'fit_evidence_state_source': game.get('fit_evidence_state_source'),\n        'play_role': game.get('play_role'),\n        'play_role_confidence': game.get('play_role_confidence'),\n        'play_role_provenance': game.get('play_role_provenance') or [],\n        'relative_start_priority': game.get('relative_start_priority'),\n        'relative_start_priority_confidence': game.get('relative_start_priority_confidence'),\n        'relative_start_priority_provenance': game.get('relative_start_priority_provenance') or [],\n        'play_priority_context_source': game.get('play_priority_context_source'),\n        'decision': game.get('decision'),\n",
)
replace_once('scripts/build_ranking_lookup.py', "        'schema_version': 3,\n", "        'schema_version': 4,\n")

# Existing visual workflow owns validation and persistence; add only a focused validator
# and trigger paths. No new recurring job/stage is created.
replace_once(
    '.github/workflows/build-daily-visual-payload.yml',
    '      - "scripts/card_explanation_policy.py"\n      - "scripts/test_card_explanation_policy.py"\n',
    '      - "scripts/card_explanation_policy.py"\n      - "scripts/test_card_explanation_policy.py"\n      - "scripts/play_priority_context.py"\n      - "scripts/test_play_priority_context.py"\n',
)
replace_once(
    '.github/workflows/build-daily-visual-payload.yml',
    '      - "config/taste_cache_entry_contract.json"\n      - "data/cache/duration_estimates.json"\n',
    '      - "config/taste_cache_entry_contract.json"\n      - "config/play_priority_context_contract.json"\n      - "data/cache/duration_estimates.json"\n',
)
replace_once(
    '.github/workflows/build-daily-visual-payload.yml',
    "      - name: Validate card explanation policy\n        shell: bash\n        run: |\n          set -euo pipefail\n          python scripts/test_card_explanation_policy.py\n\n      - name: Validate giveaway visual handoff\n",
    "      - name: Validate card explanation policy\n        shell: bash\n        run: |\n          set -euo pipefail\n          python scripts/test_card_explanation_policy.py\n\n      - name: Validate play role and relative start priority context\n        shell: bash\n        run: |\n          set -euo pipefail\n          python scripts/test_play_priority_context.py\n\n      - name: Validate giveaway visual handoff\n",
)
replace_once(
    '.github/workflows/build-daily-visual-payload.yml',
    "                  'taste_confidence': game.get('taste_confidence'),\n                  'direct_user_rating': direct.get('rating'),\n",
    "                  'taste_confidence': game.get('taste_confidence'),\n                  'play_role': game.get('play_role'),\n                  'play_role_confidence': game.get('play_role_confidence'),\n                  'play_role_provenance': game.get('play_role_provenance') or [],\n                  'relative_start_priority': game.get('relative_start_priority'),\n                  'relative_start_priority_confidence': game.get('relative_start_priority_confidence'),\n                  'relative_start_priority_provenance': game.get('relative_start_priority_provenance') or [],\n                  'play_priority_context_source': game.get('play_priority_context_source'),\n                  'direct_user_rating': direct.get('rating'),\n",
)

append_once(
    'PROJECT_RULES.md',
    '## Роль игры и относительный приоритет запуска',
    '''## Роль игры и относительный приоритет запуска

После price-blind Taste/evidence оценки хранить отдельный producer-owned контекст `play_role` и `relative_start_priority`. Он отвечает не за выгодность покупки, а за то, какое место игра занимает в реальном игровом режиме пользователя и насколько скоро её разумно запускать среди подходящих игр.

Канонические роли: `main_full`, `secondary_palate_cleanser`, `family_coop`, `unresolved`. Относительный start priority: `high`, `ordinary`, `low`, `unresolved`.

`play_role` не равен fit: сильное Taste-попадание может быть secondary/palate-cleanser или family/co-op. `relative_start_priority` не равен sale urgency: окончание скидки сегодня означает коммерческую срочность покупки, но само по себе не делает игру следующей для запуска. Wishlist также не означает «играть следующей».

Franchise history используется только как слабый prior и без title-specific evidence не может жёстко назначить main/secondary роль или высокий/низкий start priority. При недостатке доказательств сохранять `unresolved`, а не угадывать по жанру, score или франшизе.

`confirmed_negative` из канонического Taste evidence-state остаётся сильным негативом: такой кандидат не может получить `high` start priority. Этот контекст не меняет eligibility, Taste fit, `total_score`, `priority_rank` и не создаёт вторую формулу сортировки. Канонический контракт: `config/play_priority_context_contract.json`.''',
)

append_once(
    'PROJECT_DECISIONS.md',
    '## TASTE-002 — Play role and start priority are not purchase urgency',
    '''---

## TASTE-002 — Play role and start priority are not purchase urgency

**Дата:** 2026-09-05
**Статус:** implemented as internal Taste step 2; combined independent Taste Review remains pending after step 3.

**Решение:** хранить `play_role` и `relative_start_priority` как отдельный producer-owned semantic/context layer поверх price-blind Taste evidence, но вне commercial urgency/value и вне канонического ranker.

**Почему:** scalar fit/score не умеет одновременно выразить `Sifu = main/high`, `High On Life = main/ordinary`, `Tails of Iron 2 = secondary`, `Trine 4 = family/co-op`. Sale deadline отвечает на вопрос «не пропустить ли покупку», а start priority — «насколько скоро запускать среди подходящих игр».

**Граница:** wishlist, цена, скидка, history quality, purchase verdict и sale expiry не разрешают role/start state. Franchise history — только слабый prior; без title-specific evidence состояние остаётся `unresolved`. Step-1 `confirmed_negative` не может получить `high`. `priority_ranking.py` и `config/final_ranking_policy.json` остаются единственной автоматической ranking authority и этой задачей не меняются.

**Основные места:** `config/play_priority_context_contract.json`, `scripts/play_priority_context.py`, `scripts/build_final_visual_payload.py`, `scripts/build_ranking_lookup.py`, `scripts/test_play_priority_context.py`.''',
)

append_once(
    'PROJECT_ROUTES.md',
    '## Taste play-role / start-priority context',
    '''## Taste play-role / start-priority context

- contract: `config/play_priority_context_contract.json`;
- deterministic helper: `scripts/play_priority_context.py`;
- focused controls/regression: `scripts/test_play_priority_context.py`;
- canonical visual attachment: `scripts/build_final_visual_payload.py`;
- compact diagnostics: `scripts/build_ranking_lookup.py`;
- validation owner: existing `.github/workflows/build-daily-visual-payload.yml` build job;
- semantics: role/start are separate from fit, wishlist and sale urgency; no second ranker/sorter; `confirmed_negative` cannot receive high start priority.''',
)

print('PLAY_ROLE_STEP2_PATCH=APPLIED')
