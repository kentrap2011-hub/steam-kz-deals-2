from card_explanation_policy import positive_reasons, visible_risk_payload
import progressive_pass2
import test_grounded_negative_contract


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

    multiple_solution_reasons, _ = positive_reasons([
        'Objectives support multiple approaches and different solutions.',
    ])
    assert len(multiple_solution_reasons) == 1
    assert 'теб' in multiple_solution_reasons[0].casefold()

    progression_reasons, _ = positive_reasons([
        'You unlock new abilities as the campaign progresses.',
    ])
    assert len(progression_reasons) == 1
    assert 'теб' in progression_reasons[0].casefold()

    # Regression: current authoritative Deep evidence from the Jedi case must
    # produce grounded Russian reasons and preserve the exact accepted-state
    # identity in provenance. A mismatched/stale binding must not be accepted as
    # current Deep evidence.
    deep_entry = {
        'semantic_generation_id': 'gen-jedi',
        'profile_pin_sha256': 'profile-jedi',
        'work_id': 'work-jedi',
        'family_id': 'game:1172380',
        'taste_subject_key': 'App_1172380',
        'appid': '1172380',
        'taste_fingerprint': 'taste-jedi',
        'candidate_context_sha256': 'context-jedi',
        'pass2_attempted': True,
        'normal_first_pass_attempted': True,
        'authoritative_completed': True,
        'outcome': 'analyzed_fit',
        'fit_level': 'strong',
        'confidence': 'high',
        'positive_evidence': [
            'Lightsaber combat repeatedly emphasizes parrying, dodging, enemy reading and expanding Force abilities, closely matching the profile\'s strongest mastery and skill-growth signals.',
            'New movement and Force abilities open previously inaccessible routes, so progression changes both combat and exploration instead of only raising statistics.',
            'The Star Wars atmosphere, cinematic presentation and character-driven story provide a clear identity hook beyond the mechanical fit.',
        ],
        'taste_factors': {
            'gameplay_mastery': 88,
            'development_variety': 81,
            'structure_pacing_direction': 71,
            'identity_hooks': 87,
            'breadth_of_match': 86,
        },
        'dossier_content_sha256': 'dossier-jedi',
        'authorization_id': 'auth-jedi',
        'accepted_at_utc': '2026-09-27T17:16:49+00:00',
        'work_authority_commit': 'authority-jedi',
    }
    semantic = progressive_pass2.semantic_taste_entry(deep_entry)
    deep_reasons, deep_provenance = positive_reasons(
        semantic['positive_evidence'],
        source_binding=semantic['positive_evidence_binding'],
    )
    assert len(deep_reasons) == 2
    assert all('теб' in reason.casefold() for reason in deep_reasons)
    assert 'парирован' in deep_reasons[0].casefold()
    assert 'способност' in deep_reasons[1].casefold()
    for row in deep_provenance:
        binding = row['semantic_binding']
        assert binding['semantic_source'] == 'progressive_pass2'
        assert binding['semantic_generation_id'] == 'gen-jedi'
        assert binding['work_id'] == 'work-jedi'
        assert binding['family_id'] == 'game:1172380'
        assert binding['dossier_content_sha256'] == 'dossier-jedi'
        assert binding['authorization_id'] == 'auth-jedi'
        assert binding['accepted_at_utc'] == '2026-09-27T17:16:49+00:00'

    binding = {field: deep_entry[field] for field in progressive_pass2.PASS1_IDENTITY_FIELDS}
    state_doc = {'entries': {'game:1172380': deep_entry}}
    assert progressive_pass2.authoritative_completion_entry(binding, state_doc) is deep_entry
    stale_binding = dict(binding)
    stale_binding['work_id'] = 'different-work'
    assert progressive_pass2.authoritative_completion_entry(stale_binding, state_doc) is None

    # Existing Fast/cache explanation behavior remains unbound and unchanged.
    legacy_reason, legacy_provenance = positive_reasons([
        'You unlock new abilities as the campaign progresses.',
    ])
    assert legacy_reason == progression_reasons
    assert legacy_provenance[0]['source'] == 'taste_positive_evidence'
    assert 'semantic_binding' not in legacy_provenance[0]

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

    print('CARD_EXPLANATION_POLICY_TESTS=PASS count=8')
    test_grounded_negative_contract.main()


if __name__ == '__main__':
    run()
