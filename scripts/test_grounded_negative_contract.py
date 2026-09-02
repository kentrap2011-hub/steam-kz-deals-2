import json

import grounded_negative_visual
from taste_negative_contract import negative_readiness, structured_grounded_risks


def expect_error(fn, contains):
    try:
        fn()
    except (ValueError, RuntimeError) as exc:
        assert contains in str(exc), (contains, str(exc))
        return
    raise AssertionError(f'Expected error containing {contains!r}')


def ready_entry(code='other_grounded_taste_risk', category='other_grounded', score_text=None):
    evidence = score_text or 'This confirmed downside uses wording absent from the legacy keyword mapper.'
    return {
        'negative_analysis_status': 'complete_with_confirmed_negative',
        'negative_findings': [
            {
                'category': category,
                'code': code,
                'evidence': evidence,
                'risk_text_ru': 'Это подтверждённый персональный минус с прямой привязкой к данным игры.',
            }
        ],
        'negative_evidence': [evidence],
    }


def main():
    entry = ready_entry()
    readiness = negative_readiness(entry)
    assert readiness == {
        'negative_analysis_status': 'complete_with_confirmed_negative',
        'confirmed_negative_count': 1,
        'negative_analysis_ready': True,
    }

    structured = structured_grounded_risks(entry)
    other = structured['other_grounded_taste_risk']
    assert other['score'] == 0
    assert other['source'] == 'taste_negative_evidence'
    assert other['evidence'] == entry['negative_findings'][0]['evidence']

    visible = grounded_negative_visual.visible_grounded_payload(structured)
    assert visible['risk_status']['grounded_taste_negative_witness'] is True
    assert visible['risk_provenance'][0]['source'] == 'taste_negative_evidence'
    assert visible['risk_provenance'][0]['category'] == 'other_grounded'
    assert visible['risk_provenance'][0]['evidence'] == entry['negative_findings'][0]['evidence']

    # Heuristics and even confirmed practical facts may remain useful additional
    # risks, but neither may satisfy the mandatory Taste-owned readiness witness.
    heuristic_only = {
        'possible_issue': {
            'code': 'possible_issue',
            'score': 5,
            'text': 'A derived heuristic candidate.',
            'source': 'derived',
        }
    }
    practical_only = {
        'windows_friction': {
            'code': 'windows_friction',
            'score': 5,
            'text': 'A confirmed practical downside.',
            'source': 'confirmed_practical',
        }
    }
    expect_error(
        lambda: grounded_negative_visual.visible_grounded_payload(heuristic_only),
        'no visible grounded Taste negative candidate',
    )
    expect_error(
        lambda: grounded_negative_visual.visible_grounded_payload(practical_only),
        'no visible grounded Taste negative candidate',
    )

    # An unresolved truthful result remains unresolved; no generic fallback is
    # manufactured by the contract helper.
    unresolved = {
        'negative_analysis_status': 'incomplete_no_confirmed_negative',
        'negative_findings': [],
        'negative_evidence': [],
    }
    assert negative_readiness(unresolved)['negative_analysis_ready'] is False
    assert structured_grounded_risks(unresolved) == {}

    # A dedicated serious code retains its deterministic ranking score without
    # relying on any keyword contained in the raw evidence wording.
    serious = ready_entry(
        code='directionlessness',
        category='direction',
        score_text='The supplied proof sentence deliberately avoids the old mapper vocabulary.',
    )
    serious_risk = structured_grounded_risks(serious)['directionlessness']
    assert serious_risk['score'] == 4

    print(json.dumps({
        'status': 'PASS',
        'unfamiliar_grounded_finding_survives': True,
        'other_grounded_taste_risk_score': other['score'],
        'heuristic_only_cannot_satisfy_readiness': True,
        'confirmed_practical_only_cannot_satisfy_taste_readiness': True,
        'truthful_incomplete_has_no_fabricated_fallback': True,
        'structured_code_score_independent_of_evidence_keywords': True,
    }, ensure_ascii=False, indent=2))
    print('GROUNDED_NEGATIVE_CONTRACT_TEST=PASS')


if __name__ == '__main__':
    main()
