import copy
import hashlib
import json
from pathlib import Path

import build_progressive_pass2_work
import card_explanation_policy
import priority_ranking
import progressive_pass2
import progressive_work_authority
import refine_visual_ranking
import validate_card_explanations as card_validator


KOF_FAMILY = 'game:1498570'


def attach_frozen_dossier(item):
    authority = item['score_migration_provenance']['migration_authority_commit']
    raw = progressive_work_authority.file_bytes_at_commit(authority, item['dossier_path'])
    assert hashlib.sha256(raw).hexdigest() == item['dossier_content_sha256']
    item['_dossier_record'] = {
        'path': item['dossier_path'],
        'content_sha256': item['dossier_content_sha256'],
        'doc': json.loads(raw.decode('utf-8')),
    }
    return item['_dossier_record']['doc']


def profile_ref(pointer, text):
    value_hash = hashlib.sha256(pointer.encode('utf-8')).hexdigest()
    return {
        'json_pointer': pointer,
        'profile_value_sha256': value_hash,
        'match_text_ru': text,
    }


def kof_findings(factors):
    return [
        {
            'finding_id': 'kof-combat-depth',
            'text_ru': (
                'Хопы, управление шкалой, отмены и цепочки суперприёмов дают именно ту глубину боя, '
                'где тебе важно осваивать точные действия, а не просто повторять один безопасный приём.'
            ),
            'candidate_evidence_refs': [{'kind': 'observation', 'index': 0}],
            'profile_evidence_refs': [
                profile_ref('/preferences/gameplay_mastery', 'Тебе важны механики, которые вознаграждают освоение и точность.')
            ],
            'factor_impacts': [
                {
                    'factor_id': 'gameplay_mastery',
                    'effect': 'supports',
                    'normalized_value': factors['gameplay_mastery'],
                },
                {
                    'factor_id': 'breadth_of_match',
                    'effect': 'supports',
                    'normalized_value': factors['breadth_of_match'],
                },
            ],
        },
        {
            'finding_id': 'kof-roster-variety',
            'text_ru': (
                'Большой состав и комбинации команд дают тебе много пространства для экспериментов '
                'с персонажами и составами, а концовки и музыка добавляют игре собственную идентичность.'
            ),
            'candidate_evidence_refs': [{'kind': 'observation', 'index': 2}],
            'profile_evidence_refs': [
                profile_ref('/preferences/development_variety', 'Тебе лучше подходят игры с заметным разнообразием вариантов развития игры.'),
                profile_ref('/preferences/identity_hooks', 'Тебе важны запоминающиеся особенности и собственная идентичность игры.'),
            ],
            'factor_impacts': [
                {
                    'factor_id': 'development_variety',
                    'effect': 'supports',
                    'normalized_value': factors['development_variety'],
                },
                {
                    'factor_id': 'identity_hooks',
                    'effect': 'supports',
                    'normalized_value': factors['identity_hooks'],
                },
            ],
        },
        {
            'finding_id': 'kof-single-player-limit',
            'text_ru': (
                'Сюжетный и одиночный контент здесь заметно проще самой боевой системы, поэтому для тебя '
                'ценность игры сильнее зависит от желания возвращаться именно к боям и освоению состава.'
            ),
            'candidate_evidence_refs': [{'kind': 'observation', 'index': 3}],
            'profile_evidence_refs': [
                profile_ref('/preferences/structure_pacing_direction', 'Тебе важна содержательная структура, а не только повторяемая система.')
            ],
            'factor_impacts': [
                {
                    'factor_id': 'structure_pacing_direction',
                    'effect': 'qualifies',
                    'normalized_value': factors['structure_pacing_direction'],
                },
            ],
        },
    ]


def result_doc(item, dossier, *, factors=None, findings=None, outcome='analyzed_fit'):
    provenance = item['score_migration_provenance']
    doc = {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS2-RESULT-V1',
        **{field: item.get(field) for field in progressive_pass2.IMMUTABLE_RESULT_FIELDS},
        'dossier_compatibility_binding': copy.deepcopy(item['dossier_compatibility_binding']),
        'recovery_condition_binding': None,
        'score_migration_provenance': copy.deepcopy(provenance),
        'score_evidence_contract': copy.deepcopy(item['score_evidence_contract']),
        'outcome': outcome,
    }
    if outcome == 'analysis_incomplete':
        doc['issue_code'] = 'insufficient_evidence'
        return doc
    if outcome != 'analyzed_fit':
        raise AssertionError('test helper only needs fit/incomplete')

    factors = copy.deepcopy(factors or provenance['prior_taste_factors'])
    assessment = copy.deepcopy((ORIGINAL_STATE['entries'][KOF_FAMILY].get('negative_assessment') or {}))
    assert assessment.get('status') == 'completed'
    doc.update({
        'fit_level': provenance['prior_fit_level'],
        'confidence': provenance['prior_confidence'],
        'positive_evidence': copy.deepcopy(provenance['prior_positive_evidence']),
        'taste_factors': factors,
        'score_findings': copy.deepcopy(findings or kof_findings(factors)),
        'negative_assessment': assessment,
    })
    return doc


def accept_one(item, doc, state):
    out, receipts = progressive_pass2.process_result_documents(
        {
            'contract': 'PROGRESSIVE-PASS2-WORK-V1',
            'implemented': True,
            'pass2_active': True,
            'items': [item],
        },
        copy.deepcopy(state),
        [(Path(item['result_submission_path']).name, doc, None)],
        accepted_at_utc='2026-09-30T04:00:00+00:00',
    )
    return out, receipts


def linked_deep_card(entry, reasons, provenance):
    return {
        'id': entry['family_id'],
        'title': 'THE KING OF FIGHTERS XV',
        'analysis_state': 'analyzed_fit',
        'effective_analysis_source': 'deep',
        'analysis_semantic_generation_id': entry['semantic_generation_id'],
        'score_explainability_status': 'linked_v1',
        'why_fit': copy.deepcopy(reasons),
        'why_fit_status': {
            'has_described_fit': True,
            'grounding': 'grounded',
        },
        'why_fit_provenance': copy.deepcopy(provenance),
        'risks': [],
        'risk_codes': [],
        'risk_status': {'has_described_risk': False},
        'risk_provenance': [],
        'cautions': [],
        'caution_provenance': [],
        'negative_assessment_status': 'completed_no_relevant_negative',
    }


def assert_card_error(card, needle):
    errors = card_validator.validate_item(card)
    assert any(needle in error for error in errors), (needle, errors)


MANIFEST = progressive_pass2.load_score_explainability_manifest()
CURRENT_STATE = progressive_pass2.load_state()
ORIGINAL_STATE = progressive_pass2._json_at_commit(
    MANIFEST['migration_authority_commit'],
    progressive_pass2.STATE,
)


def run():
    manifest = MANIFEST
    assert manifest['migration_id'] == 'deep-score-evidence-explainability-alignment-01'
    assert manifest['scope']['target_count'] == 43
    assert manifest['scope']['prior_not_fit_not_applicable_count'] == 4
    assert len(manifest['targets']) == 43
    assert any(row.get('appid') == '1498570' for row in manifest['targets'])

    # Production state is allowed to advance while this migration is being
    # executed. Validate accounting against the current durable state without
    # pinning the regression to the original 43-pending snapshot.
    current_work, current_metrics, _current_frozen = (
        progressive_pass2.score_explainability_work_and_metrics(CURRENT_STATE, manifest)
    )
    assert current_metrics['total_count'] == 43
    assert (
        current_metrics['pending_count']
        + current_metrics['accepted_count']
        + current_metrics['stale_or_missing_prior_count']
    ) == 43
    assert len(current_work) == current_metrics['pending_count']
    assert all(
        row['work_mode'] == progressive_pass2.SCORE_EXPLAINABILITY_MODE
        for row in current_work
    )

    # Detailed semantic regression remains deterministic against the migration's
    # frozen authority snapshot, independent of later accepted production work.
    work, metrics, frozen = progressive_pass2.score_explainability_work_and_metrics(
        ORIGINAL_STATE, manifest
    )
    assert metrics['total_count'] == 43
    assert metrics['pending_count'] == 43
    assert metrics['accepted_count'] == 0
    assert len(work) == 43
    assert all(row['work_mode'] == progressive_pass2.SCORE_EXPLAINABILITY_MODE for row in work)

    built = build_progressive_pass2_work.build_work_document()
    built_migration = built['scope']['score_explainability_migration']
    assert built_migration['total_count'] == 43
    assert built_migration['pending_count'] == current_metrics['pending_count']
    assert built_migration['accepted_count'] == current_metrics['accepted_count']
    if current_metrics['complete']:
        assert built['projection_status'] != 'score_explainability_migration_active'
    else:
        assert built['projection_status'] == 'score_explainability_migration_active'
        assert len(built['items']) == current_metrics['pending_count']
        assert all(
            row['work_mode'] == progressive_pass2.SCORE_EXPLAINABILITY_MODE
            for row in built['items']
        )

    item = copy.deepcopy(next(row for row in work if row['family_id'] == KOF_FAMILY))
    dossier = attach_frozen_dossier(item)
    assert dossier['observations'][0]['sentiment'] == 'positive'
    assert dossier['observations'][2]['sentiment'] == 'positive'
    assert dossier['observations'][3]['sentiment'] == 'negative'

    prior = ORIGINAL_STATE['entries'][KOF_FAMILY]
    assert progressive_pass2.score_explainability_status(prior) == 'migration_required'
    assert prior['taste_factors'] == item['score_migration_provenance']['prior_taste_factors']

    valid = result_doc(item, dossier)
    normalized = progressive_pass2.normalize_result(
        valid, item, accepted_at_utc='2026-09-30T04:00:00+00:00'
    )
    assert normalized['score_explainability_status'] == 'linked_v1'
    assert {impact['factor_id'] for row in normalized['score_findings'] for impact in row['factor_impacts']} == set(
        progressive_pass2.SCORE_FACTOR_IDS
    )

    accepted_state, receipts = accept_one(item, valid, ORIGINAL_STATE)
    assert receipts[0]['status'] == 'accepted'
    accepted = accepted_state['entries'][KOF_FAMILY]
    assert accepted['score_explainability_status'] == 'linked_v1'
    assert accepted['revision_history'][-1]['state']['authorization_id'] == prior['authorization_id']
    semantic = progressive_pass2.semantic_taste_entry(accepted)
    reasons, provenance = card_explanation_policy.deep_score_reasons(semantic)
    assert len(reasons) == 2
    assert 'Хопы' in reasons[0]
    assert 'Большой состав' in reasons[1]
    assert all(row['source'] == 'deep_score_finding' for row in provenance)

    # Card publication parity regression: linked Deep positives are validated by
    # accepted structured provenance, not by a magic Russian substring.
    semantic_no_magic_word = copy.deepcopy(semantic)
    for finding in semantic_no_magic_word['deep_score_findings']:
        finding['text_ru'] = (
            finding['text_ru']
            .replace('для тебя', 'для игрока')
            .replace('Для тебя', 'Для игрока')
            .replace('тебе', 'игроку')
            .replace('Тебе', 'Игроку')
        )
    no_magic_reasons, no_magic_provenance = card_explanation_policy.deep_score_reasons(
        semantic_no_magic_word
    )
    assert len(no_magic_reasons) == 2
    assert all('теб' not in reason.casefold() for reason in no_magic_reasons)
    for row in no_magic_provenance:
        assert row['source'] == 'deep_score_finding'
        assert row['finding_id']
        assert row['evidence_refs']
        assert row['profile_evidence_refs']
        assert any(impact.get('effect') == 'supports' for impact in row['factor_impacts'])
        for field in card_explanation_policy.POSITIVE_BINDING_FIELDS:
            assert row['semantic_binding'].get(field) not in {None, ''}

    valid_card = linked_deep_card(accepted, no_magic_reasons, no_magic_provenance)
    assert card_validator.validate_item(valid_card) == []

    missing_profile = copy.deepcopy(valid_card)
    missing_profile['why_fit_provenance'][0]['profile_evidence_refs'] = []
    assert_card_error(missing_profile, 'lacks exact candidate/profile evidence refs')

    missing_candidate = copy.deepcopy(valid_card)
    missing_candidate['why_fit_provenance'][0]['evidence_refs'] = []
    assert_card_error(missing_candidate, 'lacks exact candidate/profile evidence refs')

    missing_impacts = copy.deepcopy(valid_card)
    missing_impacts['why_fit_provenance'][0]['factor_impacts'] = []
    assert_card_error(missing_impacts, 'lacks score-factor provenance')

    non_supporting_impacts = copy.deepcopy(valid_card)
    non_supporting_impacts['why_fit_provenance'][0]['factor_impacts'][0]['effect'] = 'qualifies'
    for impact in non_supporting_impacts['why_fit_provenance'][0]['factor_impacts'][1:]:
        impact['effect'] = 'qualifies'
    assert_card_error(non_supporting_impacts, 'lacks supporting score-factor provenance')

    wrong_family = copy.deepcopy(valid_card)
    wrong_family['why_fit_provenance'][0]['semantic_binding']['family_id'] = 'game:wrong'
    assert_card_error(wrong_family, 'family binding mismatch')

    wrong_generation = copy.deepcopy(valid_card)
    wrong_generation['why_fit_provenance'][0]['semantic_binding']['semantic_generation_id'] = 'wrong-generation'
    assert_card_error(wrong_generation, 'generation binding mismatch')

    partial_binding = copy.deepcopy(valid_card)
    partial_binding['why_fit_provenance'][0]['semantic_binding'].pop('work_authority_commit', None)
    assert_card_error(partial_binding, 'lacks exact accepted-state binding')

    wrong_source = copy.deepcopy(valid_card)
    wrong_source['why_fit_provenance'][0]['source'] = 'taste_positive_evidence'
    assert_card_error(wrong_source, 'not sourced from an accepted score finding')

    generic = copy.deepcopy(valid_card)
    generic['why_fit'][0] = 'Игра прошла строгий вкусовой отбор и выглядит подходящей.'
    assert_card_error(generic, 'generic positive fallback is visible')

    commercial = copy.deepcopy(valid_card)
    commercial['why_fit'][0] = 'Скидка и высокий рейтинг делают этот вариант особенно выгодным.'
    assert_card_error(commercial, 'commercial/ranking-only language')

    unlinked = copy.deepcopy(valid_card)
    unlinked['score_explainability_status'] = 'migration_required'
    assert_card_error(unlinked, 'not linked to accepted score evidence')
    assert_card_error(unlinked, 'legacy unlinked Deep result exposes a positive reason before migration')

    ungrounded_status = copy.deepcopy(valid_card)
    ungrounded_status['why_fit_status']['grounding'] = 'insufficient_evidence'
    assert_card_error(ungrounded_status, 'why_fit_status is not grounded')

    legacy_reason = {
        'id': 'game:legacy',
        'title': 'Legacy fixture',
        'analysis_state': 'analyzed_fit',
        'effective_analysis_source': 'fast',
        'why_fit': ['Развитие способностей тебе подходит по прежнему правилу.'],
        'why_fit_status': {'has_described_fit': True, 'grounding': 'grounded'},
        'why_fit_provenance': [{
            'source': 'taste_positive_evidence',
            'evidence': 'You unlock new abilities as the campaign progresses.',
        }],
        'risks': [],
        'risk_codes': [],
        'risk_status': {'has_described_risk': False},
        'risk_provenance': [],
        'cautions': [],
        'caution_provenance': [],
    }
    assert card_validator.validate_item(legacy_reason) == []
    legacy_without_link_text = copy.deepcopy(legacy_reason)
    legacy_without_link_text['why_fit'][0] = 'Развитие способностей хорошо сочетается с прогрессией.'
    assert_card_error(legacy_without_link_text, 'positive lacks explicit personal-taste link')
    qualifiers, qualifier_provenance = card_explanation_policy.deep_score_qualifiers(semantic)
    assert qualifiers and 'Сюжетный' in qualifiers[0]
    assert qualifier_provenance[0]['source'] == 'deep_score_finding_qualifier'

    # Existing grounded negative/caution path remains independent and does not
    # become a second penalty merely because a score qualifier is visible.
    deep_cautions, _ = card_explanation_policy.deep_cautions(semantic)
    assert deep_cautions
    assert refine_visual_ranking.personal_taste_risks(semantic) == {}

    # All five score-bearing factors are mandatory: no hidden contribution may survive.
    missing = copy.deepcopy(valid)
    missing['score_findings'] = missing['score_findings'][:2]
    try:
        progressive_pass2.normalize_result(missing, item)
        raise AssertionError('missing score factor coverage was accepted')
    except ValueError as exc:
        assert 'do not explain every score-bearing factor' in str(exc)

    # Exact evidence refs are structural authority; a generic phrase with otherwise
    # plausible vocabulary still cannot stand as a score reason.
    generic = copy.deepcopy(valid)
    generic['score_findings'][0]['text_ru'] = 'Хороший файтинг'
    try:
        progressive_pass2.normalize_result(generic, item)
        raise AssertionError('generic praise was accepted')
    except ValueError as exc:
        assert 'generic praise' in str(exc)

    bad_ref = copy.deepcopy(valid)
    bad_ref['score_findings'][0]['candidate_evidence_refs'] = [{'kind': 'observation', 'index': 999}]
    try:
        progressive_pass2.normalize_result(bad_ref, item)
        raise AssertionError('out-of-bound Dossier ref was accepted')
    except ValueError as exc:
        assert 'outside exact accepted Dossier' in str(exc)

    bad_profile = copy.deepcopy(valid)
    bad_profile['score_findings'][0]['profile_evidence_refs'][0]['json_pointer'] = 'mutable.latest'
    try:
        progressive_pass2.normalize_result(bad_profile, item)
        raise AssertionError('mutable/non-exact profile ref was accepted')
    except ValueError as exc:
        assert 'exact JSON pointer' in str(exc)

    commercial = copy.deepcopy(valid)
    commercial['score_findings'][0]['text_ru'] = 'Скидка делает эту игру особенно выгодной для тебя.'
    try:
        progressive_pass2.normalize_result(commercial, item)
        raise AssertionError('commercial reason was accepted as score evidence')
    except ValueError as exc:
        assert 'commercial/ranking-only language' in str(exc)

    # An incomplete migration attempt is terminal for this finite target but must
    # preserve the prior completed Deep revision as current truth.
    incomplete = result_doc(item, dossier, outcome='analysis_incomplete')
    incomplete_state, receipts = accept_one(item, incomplete, ORIGINAL_STATE)
    assert receipts[0]['status'] == 'accepted'
    unchanged = incomplete_state['entries'][KOF_FAMILY]
    assert unchanged['authorization_id'] == prior['authorization_id']
    assert unchanged['taste_factors'] == prior['taste_factors']
    assert progressive_pass2.score_explainability_status(unchanged) == 'migration_required'
    assert len(unchanged['score_explainability_migration_attempts']) == 1

    # The migration does not pin the old factor values or old score. If the same
    # frozen semantic evidence supports a lower current factor, the accepted truth changes.
    changed_factors = copy.deepcopy(prior['taste_factors'])
    changed_factors['structure_pacing_direction'] = 60
    changed = result_doc(item, dossier, factors=changed_factors, findings=kof_findings(changed_factors))
    changed_state, receipts = accept_one(item, changed, ORIGINAL_STATE)
    assert receipts[0]['status'] == 'accepted'
    changed_entry = changed_state['entries'][KOF_FAMILY]
    assert changed_entry['taste_factors']['structure_pacing_direction'] == 60
    policy = json.loads(priority_ranking.POLICY.read_text(encoding='utf-8'))
    before_points = priority_ranking._taste_component({'taste_factors': prior['taste_factors']}, policy)['points']
    after_points = priority_ranking._taste_component({'taste_factors': changed_entry['taste_factors']}, policy)['points']
    assert after_points < before_points

    print(
        'DEEP_SCORE_EVIDENCE_EXPLAINABILITY=PASS '
        f"migration_targets={metrics['total_count']} "
        f"kof_family={KOF_FAMILY} "
        f"old_taste_points={before_points} changed_taste_points={after_points}"
    )


if __name__ == '__main__':
    run()
