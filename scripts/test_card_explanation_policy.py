from card_explanation_policy import positive_reasons, visible_risk_payload


def run():
    specific = ['Alternates between a 2.5D platformer and first-person exploration sections.']
    reasons, provenance = positive_reasons(specific)
    assert len(reasons) == 1
    assert '2.5D-платформинг' in reasons[0]
    assert 'от первого лица' in reasons[0]
    assert 'тебе' in reasons[0]
    assert provenance[0]['evidence'] == specific[0]

    reasons, provenance = positive_reasons([
        'Passed eligibility filter with a high score and large discount.',
        'Tactical strategy.',
    ])
    assert reasons == []
    assert provenance == []

    heuristic_only = {
        'candidate': {
            'code': 'platform_repetition',
            'score': 5,
            'text': 'Possible repetition.',
            'source': 'derived',
        }
    }
    hidden = visible_risk_payload(heuristic_only)
    assert hidden['risks'] == []
    assert hidden['risk_codes'] == []
    assert hidden['risk_status']['has_described_risk'] is False

    mixed = dict(heuristic_only)
    mixed['grounded'] = {
        'code': 'unchanged_repetition',
        'score': 4,
        'text': 'Подтверждённый персональный риск повторения.',
        'source': 'taste_negative_evidence',
    }
    first = visible_risk_payload(mixed)
    second = visible_risk_payload(mixed)
    assert first == second
    assert first['risks'] == ['Подтверждённый персональный риск повторения.']
    assert first['risk_codes'] == ['unchanged_repetition']
    assert first['risk_status']['has_described_risk'] is True
    assert first['risk_provenance'] == [
        {'code': 'unchanged_repetition', 'source': 'taste_negative_evidence'}
    ]

    unrelated = {
        'title': 'Fixture',
        'current_price_rub': 99,
        'discount_percent': 90,
        'priority_rank': 1,
    }
    before = dict(unrelated)
    positive_reasons([])
    assert unrelated == before

    print('CARD_EXPLANATION_POLICY_TESTS=PASS count=5')


if __name__ == '__main__':
    run()
