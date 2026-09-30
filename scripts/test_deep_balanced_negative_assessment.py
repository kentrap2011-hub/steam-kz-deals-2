import copy
import hashlib
import json
from pathlib import Path

import build_final_visual_payload
import card_explanation_policy
import priority_ranking
import progressive_pass2
import refine_visual_ranking
from taste_negative_contract import NEGATIVE_FINDING_CATALOG


JEDI_DOSSIER_PATH = Path('data/cache/taste_steam_review_dossiers/App_1172380.json')
FACTOR_VALUES = {
    'gameplay_mastery': 88,
    'development_variety': 81,
    'structure_pacing_direction': 71,
    'identity_hooks': 87,
    'breadth_of_match': 86,
}


def load_jedi():
    raw = JEDI_DOSSIER_PATH.read_bytes()
    return json.loads(raw.decode('utf-8')), hashlib.sha256(raw).hexdigest()


def work_item(dossier, digest, suffix='base'):
    item = {
        'profile_pin_sha256': 'profile-' + suffix,
        'semantic_generation_id': 'generation-' + suffix,
        'work_id': 'work-' + suffix,
        'family_id': 'game:1172380',
        'taste_subject_key': 'App_1172380',
        'appid': '1172380',
        'taste_fingerprint': 'taste-' + suffix,
        'candidate_context_sha256': 'context-' + suffix,
        'dossier_content_sha256': digest,
        'authorization_id': 'auth-' + suffix,
        'work_mode': 'normal_first_pass',
        'recovery_authorization_id': None,
        'recovery_reason': None,
        'recovery_condition_binding': None,
        'dossier_compatibility_binding': copy.deepcopy(dossier['web_evidence_contract_binding']),
        'dossier_path': JEDI_DOSSIER_PATH.as_posix(),
        'semantic_input': {'semantic_condition': {'requires_ai_base_support': False}},
        'result_submission_path': f'data/ai_inbox/progressive_pass2/results/jedi-{suffix}.json',
        '_work_authority_commit': 'a' * 40,
    }
    item['_dossier_record'] = {
        'path': item['dossier_path'],
        'content_sha256': digest,
        'doc': copy.deepcopy(dossier),
    }
    return item


def assessment(findings=None, status='completed', evaluated=None):
    candidates = [
        {'kind': 'observation', 'index': 1},
        {'kind': 'observation', 'index': 3},
        {'kind': 'conflict', 'index': 0},
    ]
    return {
        'status': status,
        'evaluated_candidate_refs': copy.deepcopy(candidates if evaluated is None else evaluated),
        'findings': copy.deepcopy(findings or []),
    }


def result_doc(item, negative_assessment, outcome='analyzed_fit', **extra):
    doc = {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS2-RESULT-V1',
        **{field: item.get(field) for field in progressive_pass2.IMMUTABLE_RESULT_FIELDS},
        'dossier_compatibility_binding': copy.deepcopy(item['dossier_compatibility_binding']),
        'recovery_condition_binding': copy.deepcopy(item.get('recovery_condition_binding')),
        'outcome': outcome,
        'negative_assessment': copy.deepcopy(negative_assessment),
    }
    if outcome == 'analyzed_fit':
        doc.update({
            'fit_level': 'strong',
            'confidence': 'high',
            'positive_evidence': [
                'Lightsaber combat emphasizes parrying, dodging and enemy reading.',
                'New movement and Force abilities open previously inaccessible routes.',
            ],
            'taste_factors': copy.deepcopy(FACTOR_VALUES),
        })
    doc.update(extra)
    return doc


def accept(item, doc):
    state, receipts = progressive_pass2.process_result_documents(
        {
            'schema_version': 2,
            'contract': 'PROGRESSIVE-PASS2-WORK-V1',
            'implemented': True,
            'pass2_active': True,
            'items': [item],
        },
        {'schema_version': 2, 'contract': 'PROGRESSIVE-PASS2-STATE-V2', 'entries': {}},
        [(Path(item['result_submission_path']).name, doc, None)],
        accepted_at_utc='2026-09-27T20:00:00+00:00',
    )
    return state, receipts


def run():
    dossier, digest = load_jedi()

    # JEDI fixture: the accepted Dossier really contains the diagnosed candidate
    # path — mixed backtracking/no-fast-travel, current EA-app friction, conflict.
    candidates = progressive_pass2.dossier_negative_candidate_refs(dossier)
    assert candidates == [
        {'kind': 'observation', 'index': 1},
        {'kind': 'observation', 'index': 3},
        {'kind': 'conflict', 'index': 0},
    ]
    assert 'fast travel' in dossier['observations'][1]['statement'].casefold()
    assert 'ea application' in dossier['observations'][3]['statement'].casefold()
    assert 'backtracking' in dossier['conflicts'][0]['statement'].casefold()

    # 1) Fit + caution-only: findings survive result -> ingest/state -> semantic
    # projection -> visual, and no scoring risk is manufactured.
    caution_findings = [
        {
            'disposition': 'caution',
            'risk_code': None,
            'text_ru': 'Возвраты по уже знакомым маршрутам без быстрого перемещения могут утомлять, если захочется часто зачищать старые зоны.',
            'evidence_refs': [
                {'kind': 'observation', 'index': 1},
                {'kind': 'conflict', 'index': 0},
            ],
        },
        {
            'disposition': 'caution',
            'risk_code': None,
            'text_ru': 'Для запуска требуется приложение EA; по свежему отзыву это может создавать лишнее трение при входе и старте игры.',
            'evidence_refs': [{'kind': 'observation', 'index': 3}],
        },
    ]
    caution_item = work_item(dossier, digest, 'caution')
    caution_doc = result_doc(caution_item, assessment(caution_findings))
    caution_state, receipts = accept(caution_item, caution_doc)
    assert receipts[0]['status'] == 'accepted'
    caution_entry = caution_state['entries']['game:1172380']
    assert caution_entry['negative_assessment'] == caution_doc['negative_assessment']
    semantic = progressive_pass2.semantic_taste_entry(caution_entry)
    assert semantic['deep_negative_assessment_status'] == 'completed_with_caution'
    assert refine_visual_ranking.personal_taste_risks(semantic) == {}
    cautions, caution_provenance = card_explanation_policy.deep_cautions(semantic)
    assert len(cautions) == 2
    assert len(caution_provenance) == 2
    assert all(row['semantic_binding']['dossier_content_sha256'] == digest for row in caution_provenance)

    game = {'practical': {}}
    build_final_visual_payload.apply_card_explanation_policy(game, semantic, {})
    assert game['risks'] == []
    assert game['risk_codes'] == []
    assert len(game['cautions']) == 2
    assert game['risk_penalty'] == 0
    caution_status = priority_ranking.build_risk_status(game)
    assert caution_status['code'] == 'caution_only'
    assert caution_status['affects_score'] is False

    # 2) Explicit confirmed personal risk uses only an existing risk code and
    # existing risk catalog score; the same result may also carry a caution.
    risk_findings = [
        {
            'disposition': 'confirmed_personal_risk',
            'risk_code': 'felt_technical_burden',
            'text_ru': 'Обязательный дополнительный EA-клиент создаёт подтверждённый для этого профиля риск лишнего технического трения.',
            'evidence_refs': [{'kind': 'observation', 'index': 3}],
        },
        caution_findings[0],
    ]
    risk_item = work_item(dossier, digest, 'risk')
    risk_state, receipts = accept(risk_item, result_doc(risk_item, assessment(risk_findings)))
    assert receipts[0]['status'] == 'accepted'
    risk_semantic = progressive_pass2.semantic_taste_entry(risk_state['entries']['game:1172380'])
    assert risk_semantic['deep_negative_assessment_status'] == 'completed_with_confirmed_risk'
    risks = refine_visual_ranking.personal_taste_risks(risk_semantic)
    assert set(risks) == {'felt_technical_burden'}
    assert risks['felt_technical_burden']['score'] == NEGATIVE_FINDING_CATALOG['felt_technical_burden']['score']
    visible = card_explanation_policy.visible_risk_payload(risks)
    assert visible['risk_codes'] == ['felt_technical_burden']
    assert visible['risk_provenance'][0]['semantic_binding']['authorization_id'] == 'auth-risk'
    risk_game = {'practical': {}}
    build_final_visual_payload.apply_card_explanation_policy(risk_game, risk_semantic, {})
    assert risk_game['risk_codes'] == ['felt_technical_burden']
    assert len(risk_game['cautions']) == 1
    assert priority_ranking.build_risk_status(risk_game)['affects_score'] is True

    # 3) Completed assessment may surface nothing, but only after every exact
    # negative/mixed candidate has been explicitly evaluated.
    none_item = work_item(dossier, digest, 'none')
    none_state, receipts = accept(none_item, result_doc(none_item, assessment([])))
    assert receipts[0]['status'] == 'accepted'
    none_semantic = progressive_pass2.semantic_taste_entry(none_state['entries']['game:1172380'])
    assert none_semantic['deep_negative_assessment_status'] == 'completed_no_relevant_negative'
    none_game = {'practical': {}}
    build_final_visual_payload.apply_card_explanation_policy(none_game, none_semantic, {})
    assert priority_ranking.build_risk_status(none_game)['code'] == 'evaluated_no_relevant_negative'

    incomplete_eval = assessment([], evaluated=[{'kind': 'observation', 'index': 1}])
    bad_item = work_item(dossier, digest, 'incomplete-eval')
    bad_state, bad_receipts = accept(bad_item, result_doc(bad_item, incomplete_eval))
    assert bad_receipts[0]['status'] == 'rejected_semantic_contract_result_attempt_consumed'
    assert bad_receipts[0]['attempt_consumed'] is True
    assert bad_state['entries']['game:1172380']['recovery_owned'] is True

    # 4) Unresolved negative assessment remains a visible unresolved state and is
    # never projected as no-risk.
    unresolved_item = work_item(dossier, digest, 'unresolved')
    unresolved_assessment = assessment(
        [],
        status='unresolved',
        evaluated=[{'kind': 'observation', 'index': 1}],
    )
    unresolved_state, receipts = accept(
        unresolved_item,
        result_doc(unresolved_item, unresolved_assessment),
    )
    assert receipts[0]['status'] == 'accepted'
    unresolved_semantic = progressive_pass2.semantic_taste_entry(
        unresolved_state['entries']['game:1172380']
    )
    assert unresolved_semantic['deep_negative_assessment_status'] == 'unresolved'
    unresolved_game = {'practical': {}}
    build_final_visual_payload.apply_card_explanation_policy(unresolved_game, unresolved_semantic, {})
    assert priority_ranking.build_risk_status(unresolved_game)['code'] == 'negative_assessment_unresolved'

    # 5) Historical Deep analyzed_fit remains authoritative without replay, but
    # its missing new field is explicitly legacy/not-evaluated.
    legacy_entry = copy.deepcopy(caution_entry)
    legacy_entry.pop('negative_assessment', None)
    before = copy.deepcopy(legacy_entry)
    legacy_semantic = progressive_pass2.semantic_taste_entry(legacy_entry)
    assert legacy_entry == before
    assert legacy_semantic['deep_negative_assessment_status'] == 'legacy_not_evaluated'
    legacy_game = {'practical': {}}
    build_final_visual_payload.apply_card_explanation_policy(legacy_game, legacy_semantic, {})
    legacy_status = priority_ranking.build_risk_status(legacy_game)
    assert legacy_status['code'] == 'legacy_negative_not_evaluated'
    assert 'не оценивались' in legacy_status['label']

    # 6) Exact-bound semantic evidence that violates the result contract fails
    # closed, consumes the proven semantic attempt, and enters recovery ownership.
    unbound_item = work_item(dossier, digest, 'unbound')
    unbound = assessment([
        {
            'disposition': 'caution',
            'risk_code': None,
            'text_ru': 'Нельзя привязать к положительному наблюдению.',
            'evidence_refs': [{'kind': 'observation', 'index': 0}],
        },
    ])
    unbound_state, unbound_receipts = accept(unbound_item, result_doc(unbound_item, unbound))
    assert unbound_receipts[0]['status'] == 'rejected_semantic_contract_result_attempt_consumed'
    assert unbound_receipts[0]['attempt_consumed'] is True
    assert unbound_state['entries']['game:1172380']['recovery_owned'] is True

    malformed_item = work_item(dossier, digest, 'malformed')
    malformed = assessment(caution_findings)
    malformed['findings'][0]['unexpected'] = True
    malformed_state, malformed_receipts = accept(
        malformed_item, result_doc(malformed_item, malformed)
    )
    assert malformed_receipts[0]['status'] == 'rejected_semantic_contract_result_attempt_consumed'
    assert malformed_receipts[0]['attempt_consumed'] is True
    assert malformed_state['entries']['game:1172380']['recovery_owned'] is True

    # 7) analyzed_not_fit stays coherent: confirmed_personal_negative must carry
    # a completed confirmed risk, not merely a caution.
    not_fit_item = work_item(dossier, digest, 'not-fit')
    not_fit_doc = result_doc(
        not_fit_item,
        assessment(risk_findings),
        outcome='analyzed_not_fit',
        confidence='high',
        not_fit_basis='confirmed_personal_negative',
        not_fit_evidence=['Accepted Dossier plus bound profile establish a completed personal negative.'],
    )
    not_fit_state, not_fit_receipts = accept(not_fit_item, not_fit_doc)
    assert not_fit_receipts[0]['status'] == 'accepted'
    assert not_fit_state['entries']['game:1172380']['outcome'] == 'analyzed_not_fit'

    caution_not_fit_item = work_item(dossier, digest, 'bad-not-fit')
    caution_not_fit_doc = result_doc(
        caution_not_fit_item,
        assessment(caution_findings),
        outcome='analyzed_not_fit',
        confidence='high',
        not_fit_basis='confirmed_personal_negative',
        not_fit_evidence=['This basis cannot be supported by caution-only findings.'],
    )
    state, receipts = accept(caution_not_fit_item, caution_not_fit_doc)
    assert receipts[0]['status'] == 'rejected_semantic_contract_result_attempt_consumed'
    assert receipts[0]['attempt_consumed'] is True
    assert state['entries']['game:1172380']['recovery_owned'] is True

    # 8) Existing non-Deep Fast/cache negative mapping remains unchanged.
    legacy_fast = {'negative_evidence': ['repetitive grind under the same conditions']}
    assert 'unchanged_repetition' in refine_visual_ranking.personal_taste_risks(legacy_fast)

    # 9) Schema is fail-closed for the new structures; ranking weights are still
    # exactly the pre-existing policy values (this task adds no new weight).
    schema = json.loads(Path('config/progressive_pass2_result_schema.json').read_text(encoding='utf-8'))
    assert schema['$defs']['deepNegativeAssessment']['additionalProperties'] is False
    assert schema['$defs']['deepNegativeFinding']['additionalProperties'] is False
    assert schema['$defs']['deepNegativeEvidenceRef']['additionalProperties'] is False
    policy = json.loads(Path('config/final_ranking_policy.json').read_text(encoding='utf-8'))
    risk_policy = policy['score_model']['personal']['risk']
    assert risk_policy['descriptive_low_penalty'] == 1
    assert risk_policy['descriptive_medium_penalty'] == 3
    assert risk_policy['serious_personal_penalty'] == 10
    assert risk_policy['confirmed_windows_penalty'] == 12

    # 10) Browser is presentation-only: it renders producer-owned risk/caution
    # payloads and does not classify the negative-assessment statuses itself.
    app = Path('web/app.js').read_text(encoding='utf-8')
    index = Path('web/index.html').read_text(encoding='utf-8')
    assert 'g.cautions' in app
    assert 'id="cautions"' in index
    assert 'completed_with_caution' not in app
    assert 'legacy_not_evaluated' not in app
    assert 'felt_technical_burden' not in app

    # 11) Control-plane ownership remains unchanged and no scheduler/retry
    # authority moved into the semantic worker.
    ownership = json.loads(Path('config/execution_ownership_contract.json').read_text(encoding='utf-8'))
    deep_owner = ownership['progressive_personalization_phase_c_pass2_core']
    assert deep_owner['control_plane'] == 'github'
    assert deep_owner['scheduler']['configuration_owner'] == 'external_user_operator'
    assert deep_owner['scheduled_chatgpt_responsibilities_when_activated']
    assert 'blind automatic recovery retry loop or hidden arbitrary recovery quota' in deep_owner['forbidden']

    print('DEEP_BALANCED_NEGATIVE_ASSESSMENT_TEST=PASS')


if __name__ == '__main__':
    run()
