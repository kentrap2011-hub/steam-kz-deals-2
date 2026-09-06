import json
from pathlib import Path

from taste_negative_contract import validate_negative_analysis

PROFILE_PATH = Path('USER_TASTE_PROFILE.md')
ROLE_CONTRACT_PATH = Path('config/play_priority_context_contract.json')


def expect_value_error(fn, contains):
    try:
        fn()
    except ValueError as exc:
        assert contains in str(exc), (contains, str(exc))
        return
    raise AssertionError(f'Expected ValueError containing {contains!r}')


def main():
    profile = PROFILE_PATH.read_text(encoding='utf-8')
    contract = json.loads(ROLE_CONTRACT_PATH.read_text(encoding='utf-8'))

    # A2: every static title-specific role/start calibration is explicitly bound
    # to current canonical profile evidence. An unrelated profile edit does not
    # invalidate the guard; changing/removing the evidence that justified a
    # calibration does, and validation then fails until it is revalidated.
    guard = contract.get('profile_revalidation_guard') or {}
    assert guard.get('profile_path') == str(PROFILE_PATH)
    assert guard.get('scope') == 'static_title_specific_calibrations_only'
    fragments_by_key = guard.get('required_fragments_by_calibration') or {}
    calibrations = contract.get('title_calibrations') or {}
    static_keys = {
        key for key, hint in calibrations.items()
        if isinstance(hint, dict) and hint.get('title_specific_evidence') is True
    }
    assert set(fragments_by_key) == static_keys, (sorted(fragments_by_key), sorted(static_keys))
    for key in sorted(static_keys):
        fragments = fragments_by_key[key]
        assert isinstance(fragments, list) and fragments, key
        assert all(isinstance(fragment, str) and fragment in profile for fragment in fragments), key
        provenance = calibrations[key].get('provenance') or []
        assert any(str(item).startswith('USER_TASTE_PROFILE.md:') for item in provenance), (key, provenance)

    # A1: Batman and RDR2 are explicit positive exceptions. Generic structural
    # labels are not admissible evidence for a confirmed personal negative.
    positive_anchors = {
        'Batman: Arkham': '`Batman: Arkham` series — **confirmed strong replay-positive anchor**',
        'Red Dead Redemption 2': '`Red Dead Redemption 2` — **strong confirmed open-world positive**',
    }
    for title, fragment in positive_anchors.items():
        assert fragment in profile, title

    generic_cases = [
        ('Batman: Arkham', 'unchanged_repetition', 'repetition', 'Generic complexity/repetition labels only.'),
        ('Red Dead Redemption 2', 'directionlessness', 'direction', 'Generic open-world/directionlessness labels only.'),
    ]
    for title, code, category, evidence in generic_cases:
        finding = {
            'category': category,
            'code': code,
            'evidence': evidence,
            'risk_text_ru': 'Общий ярлык механики сам по себе не доказывает личный минус.',
            'evidence_origin': 'generic_feature_hypothesis',
            'evidence_strength': 'strong',
            'personal_relevance': 'confirmed',
        }
        expect_value_error(
            lambda f=finding: validate_negative_analysis(
                'complete_with_confirmed_negative', [f], [f['evidence']], require_v5=True
            ),
            'invalid personal-negative evidence origin',
        )

    print(json.dumps({
        'status': 'PASS',
        'profile_revalidation_guard': True,
        'guarded_static_calibrations': sorted(static_keys),
        'batman_positive_exception_generic_risk_blocked': True,
        'rdr2_positive_exception_generic_risk_blocked': True,
    }, ensure_ascii=False, indent=2))
    print('TASTE_STEP123_MAINTENANCE_GUARDS=PASS')


if __name__ == '__main__':
    main()
