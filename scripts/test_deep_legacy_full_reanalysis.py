import copy
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import build_progressive_pass2_work
import progressive_pass1
import progressive_pass2
import progressive_work_authority
import refine_visual_ranking


MANIFEST_PATH = Path('data/control/progressive_pass2_legacy_full_reanalysis_manifest.json')
STATE_PATH = Path('data/cache/progressive_pass2_state.json')
WORK_PATH = Path('data/production/pre_ai/progressive_pass2_work.json')
MIGRATION_ID = 'deep-legacy-full-reanalysis-with-preserved-positives-01'
JEDI_FAMILY = 'game:1172380'


def at_commit_json(commit, path):
    raw = progressive_work_authority.file_bytes_at_commit(commit, str(path))
    return json.loads(raw.decode('utf-8')), hashlib.sha256(raw).hexdigest()


def migration_work_authority(item):
    """Find the immutable Git commit that actually prepared this migration work item."""
    commits = subprocess.check_output(
        ['git', 'log', '--format=%H', '--', str(WORK_PATH)], text=True
    ).splitlines()
    for commit in commits:
        try:
            doc, _digest = at_commit_json(commit, WORK_PATH)
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if doc.get('contract') != 'PROGRESSIVE-PASS2-WORK-V1':
            continue
        candidate = next((
            row for row in (doc.get('items') or [])
            if isinstance(row, dict)
            and row.get('authorization_id') == item.get('authorization_id')
            and row.get('work_mode') == progressive_pass2.LEGACY_REANALYSIS_MODE
        ), None)
        if candidate is None:
            continue
        if all(
            str(candidate.get(field) or '') == str(item.get(field) or '')
            for field in progressive_pass2.PASS1_IDENTITY_FIELDS
        ):
            return commit
    raise AssertionError('exact immutable migration work authority not found in Git history')


def prepared_item(manifest, target):
    item = progressive_pass2.make_legacy_reanalysis_work_item(manifest, target)
    dossier, digest = at_commit_json(
        manifest['migration_authority_commit'],
        target['dossier_path'],
    )
    assert digest == target['dossier_content_sha256']
    item['_dossier_record'] = {
        'path': target['dossier_path'],
        'doc': copy.deepcopy(dossier),
        'content_sha256': digest,
    }
    item['_work_authority_commit'] = migration_work_authority(item)
    return item, dossier


def result_doc(item, *, outcome='analyzed_fit', assessment=None, **updates):
    doc = {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS2-RESULT-V1',
        **{field: item.get(field) for field in progressive_pass2.IMMUTABLE_RESULT_FIELDS},
        'dossier_compatibility_binding': copy.deepcopy(item['dossier_compatibility_binding']),
        'recovery_condition_binding': None,
        'migration_provenance': copy.deepcopy(item['migration_provenance']),
        'outcome': outcome,
    }
    if outcome in progressive_pass2.AUTHORITATIVE_OUTCOMES:
        doc['negative_assessment'] = copy.deepcopy(assessment)
    if outcome == 'analyzed_fit':
        p = item['migration_provenance']
        doc.update({
            'fit_level': p['prior_fit_level'],
            'confidence': p['prior_confidence'],
            'positive_evidence': copy.deepcopy(p['preserved_positive_evidence']),
            'taste_factors': copy.deepcopy(p['prior_taste_factors']),
        })
        requires_base = bool(
            ((item.get('semantic_input') or {}).get('semantic_condition') or {}).get(
                'requires_ai_base_support'
            )
        )
        if requires_base:
            doc['base_support_compatible'] = True
    elif outcome == 'analyzed_not_fit':
        p = item['migration_provenance']
        doc.update({
            'confidence': p['prior_confidence'] or 'high',
            'not_fit_basis': p['prior_not_fit_basis'] or 'completed_below_threshold',
            'not_fit_evidence': copy.deepcopy(p['preserved_not_fit_evidence']),
        })
    else:
        doc['issue_code'] = 'insufficient_evidence'
    doc.update(updates)
    return doc


def assessment_for(dossier, findings=None):
    refs = progressive_pass2.dossier_negative_candidate_refs(dossier)
    return {
        'status': 'completed',
        'evaluated_candidate_refs': copy.deepcopy(refs),
        'findings': copy.deepcopy(findings or []),
    }


def accept(state, item, doc):
    out, receipts = progressive_pass2.process_result_documents(
        {
            'schema_version': 2,
            'contract': 'PROGRESSIVE-PASS2-WORK-V1',
            'implemented': True,
            'pass2_active': True,
            'items': [item],
        },
        state,
        [(Path(item['result_submission_path']).name, doc, None)],
        accepted_at_utc='2026-09-28T05:00:00+00:00',
    )
    return out, receipts


def run():
    manifest = progressive_pass2.load_legacy_reanalysis_manifest()
    assert manifest['migration_id'] == MIGRATION_ID
    assert manifest['migration_authority_commit'] == '97d7798dfbf113ff0c3c4e71a75c7d50b39f3b3a'
    assert manifest['scope']['target_count'] == 30
    assert manifest['scope']['prior_fit_count'] == 26
    assert manifest['scope']['prior_not_fit_count'] == 4
    assert manifest['scope']['stale_older_generation_excluded_count'] == 2
    assert len(manifest['targets']) == 30
    assert [row['sequence'] for row in manifest['targets']] == list(range(1, 31))
    assert len({row['target_id'] for row in manifest['targets']}) == 30
    assert len({row['family_id'] for row in manifest['targets']}) == 30

    authority = manifest['migration_authority_commit']
    frozen_state, state_digest = at_commit_json(authority, STATE_PATH)
    assert state_digest == hashlib.sha256(
        progressive_work_authority.file_bytes_at_commit(authority, str(STATE_PATH))
    ).hexdigest()

    # Frozen scope is exactly current-generation authoritative old-contract Deep.
    expected = []
    excluded_old_generation = 0
    for entry in (frozen_state.get('entries') or {}).values():
        if (
            entry.get('authoritative_completed') is True
            and entry.get('outcome') in progressive_pass2.AUTHORITATIVE_OUTCOMES
            and 'negative_assessment' not in entry
        ):
            if entry.get('semantic_generation_id') == manifest['semantic_generation_id']:
                expected.append(entry)
            else:
                excluded_old_generation += 1
    assert len(expected) == 30
    assert excluded_old_generation == 2
    assert {row['family_id'] for row in manifest['targets']} == {
        row['family_id'] for row in expected
    }

    # Every target retains an exact old revision and exact frozen accepted Dossier.
    for target in manifest['targets']:
        old = frozen_state['entries'][target['family_id']]
        prior = target['prior_revision']
        assert old['authorization_id'] == prior['authorization_id']
        assert old['accepted_at_utc'] == prior['accepted_at_utc']
        assert old['outcome'] == prior['outcome']
        assert 'negative_assessment' not in old
        raw = progressive_work_authority.file_bytes_at_commit(authority, target['dossier_path'])
        assert hashlib.sha256(raw).hexdigest() == target['dossier_content_sha256']
        dossier = json.loads(raw.decode('utf-8'))
        assert dossier['web_evidence_contract_binding'] == manifest['dossier_compatibility_binding']
        if prior['outcome'] == 'analyzed_fit':
            assert prior['positive_evidence']
        else:
            assert prior['not_fit_evidence']

    # Canonical prepared work may be either the finite migration view or the
    # resumed ordinary Deep view after that same finite migration completed.
    # This regression must not reopen/rewrite PPD-010 merely because production
    # naturally consumed all 30 frozen targets.
    persisted_work = json.loads(WORK_PATH.read_text(encoding='utf-8'))
    migration_scope = persisted_work['scope']['legacy_full_reanalysis']
    assert migration_scope['total_count'] == 30
    if migration_scope['complete'] is False:
        assert persisted_work['projection_status'] == 'legacy_full_reanalysis_migration_active'
        assert len(persisted_work['items']) == 30
        assert all(row['work_mode'] == progressive_pass2.LEGACY_REANALYSIS_MODE for row in persisted_work['items'])
        assert all(row['recovery_authorization_id'] is None for row in persisted_work['items'])
        assert migration_scope['pending_count'] == 30
        assert migration_scope['accepted_count'] == 0
    else:
        assert persisted_work['projection_status'] == 'current_github_owned_fast_dossier_deep_v1_projection'
        assert migration_scope['pending_count'] == 0
        assert migration_scope['accepted_count'] == 30
        assert all(row['work_mode'] != progressive_pass2.LEGACY_REANALYSIS_MODE for row in persisted_work['items'])
    rebuilt = build_progressive_pass2_work.build_work_document()
    assert rebuilt['scope']['legacy_full_reanalysis']['total_count'] == 30
    assert rebuilt['scope']['legacy_full_reanalysis']['complete'] == migration_scope['complete']
    if migration_scope['complete'] is False:
        assert rebuilt['projection_status'] == persisted_work['projection_status']
        assert [row['authorization_id'] for row in rebuilt['items']] == [
            row['authorization_id'] for row in persisted_work['items']
        ]
    else:
        assert rebuilt['projection_status'] == 'current_github_owned_fast_dossier_deep_v1_projection'
        assert rebuilt['scope']['legacy_full_reanalysis']['pending_count'] == 0
        assert rebuilt['scope']['legacy_full_reanalysis']['accepted_count'] == 30
        assert all(row['work_mode'] != progressive_pass2.LEGACY_REANALYSIS_MODE for row in rebuilt['items'])

    # Run-start validation uses the frozen migration authority Dossier, while the
    # ordinary V2 run-start receipt remains mandatory as publication authority.
    jedi_target = next(row for row in manifest['targets'] if row['family_id'] == JEDI_FAMILY)
    jedi_item, jedi_dossier = prepared_item(manifest, jedi_target)
    receipt = {
        'status': 'confirmed',
        'run_start_authority_commit': jedi_item['_work_authority_commit'],
        'run_start_anchor_commit': jedi_item['_work_authority_commit'],
        'run_started_at_utc': manifest['migration_frozen_at_utc'],
    }
    assert progressive_pass2.validate_run_start_authority(jedi_item, receipt)
    assert jedi_item['_dossier_evidence_authority_commit'] == authority

    # A later run-start/Dossier commit cannot substitute newer Dossier bytes for
    # the frozen migration authority. Build a two-commit synthetic repository:
    # A contains the frozen accepted Dossier, B mutates that Dossier.
    with tempfile.TemporaryDirectory() as td:
        temp_repo = Path(td)
        subprocess.run(['git', 'init', '-q'], cwd=temp_repo, check=True)
        subprocess.run(['git', 'config', 'user.email', 'migration-test@example.invalid'], cwd=temp_repo, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Migration Test'], cwd=temp_repo, check=True)
        frozen_path = temp_repo / jedi_target['dossier_path']
        frozen_path.parent.mkdir(parents=True, exist_ok=True)
        frozen_raw = progressive_work_authority.file_bytes_at_commit(authority, jedi_target['dossier_path'])
        frozen_path.write_bytes(frozen_raw)
        subprocess.run(['git', 'add', '.'], cwd=temp_repo, check=True)
        subprocess.run(['git', 'commit', '-q', '-m', 'frozen dossier'], cwd=temp_repo, check=True)
        synthetic_authority = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=temp_repo, text=True
        ).strip()
        later_doc = json.loads(frozen_raw.decode('utf-8'))
        later_doc['migration_test_later_write'] = True
        frozen_path.write_text(json.dumps(later_doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        subprocess.run(['git', 'add', '.'], cwd=temp_repo, check=True)
        subprocess.run(['git', 'commit', '-q', '-m', 'later dossier write'], cwd=temp_repo, check=True)
        later_authority = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=temp_repo, text=True
        ).strip()
        later_digest = hashlib.sha256(frozen_path.read_bytes()).hexdigest()
        assert later_digest != jedi_target['dossier_content_sha256']

        frozen_item = copy.deepcopy(jedi_item)
        frozen_item['migration_provenance']['migration_authority_commit'] = synthetic_authority
        frozen_item['_work_authority_commit'] = later_authority
        later_receipt = {
            'status': 'confirmed',
            'run_start_authority_commit': later_authority,
            'run_start_anchor_commit': later_authority,
            'run_started_at_utc': manifest['migration_frozen_at_utc'],
        }
        assert progressive_pass2.validate_run_start_authority(
            frozen_item, later_receipt, repo_root=temp_repo
        )
        assert frozen_item['_dossier_evidence_authority_commit'] == synthetic_authority
        assert frozen_item['_dossier_record']['content_sha256'] == jedi_target['dossier_content_sha256']
        assert frozen_item['_dossier_record']['content_sha256'] != later_digest

    # Fresh-positive invention is rejected with zero migration attempt.
    old_full_state = copy.deepcopy(frozen_state)
    clean_assessment = assessment_for(jedi_dossier)
    bad = result_doc(jedi_item, assessment=clean_assessment)
    bad['positive_evidence'] = list(bad['positive_evidence']) + ['invented fresh positive']
    rejected_state, receipts = accept(old_full_state, jedi_item, bad)
    assert receipts[0]['status'] == 'rejected_invalid_result_no_attempt'
    assert rejected_state == old_full_state

    # A completed migration can change grounded risk while reusing exact positives.
    ea_index = next(
        i for i, row in enumerate(jedi_dossier['observations'])
        if 'ea application' in str(row.get('statement') or '').casefold()
    )
    risk = {
        'disposition': 'confirmed_personal_risk',
        'risk_code': 'felt_technical_burden',
        'text_ru': 'Дополнительный EA-клиент создаёт подтверждённый риск лишнего технического трения.',
        'evidence_refs': [{'kind': 'observation', 'index': ea_index}],
    }
    risk_assessment = assessment_for(jedi_dossier, [risk])
    migrated_state, receipts = accept(
        copy.deepcopy(frozen_state),
        jedi_item,
        result_doc(jedi_item, assessment=risk_assessment),
    )
    assert receipts[0]['status'] == 'accepted'
    assert receipts[0]['work_mode'] == progressive_pass2.LEGACY_REANALYSIS_MODE
    migrated = migrated_state['entries'][JEDI_FAMILY]
    old = frozen_state['entries'][JEDI_FAMILY]
    assert migrated['normal_first_pass_attempted'] is True
    assert migrated['normal_first_pass'] == old['normal_first_pass']
    assert migrated['recovery_attempts'] == old['recovery_attempts']
    assert migrated['work_mode'] == progressive_pass2.LEGACY_REANALYSIS_MODE
    assert migrated['positive_evidence'] == old['positive_evidence']
    assert migrated['negative_assessment'] == risk_assessment
    assert migrated['migration_result_changed'] is True
    assert len(migrated['revision_history']) == 1
    archived = migrated['revision_history'][0]['state']
    assert archived['authorization_id'] == old['authorization_id']
    assert archived['accepted_at_utc'] == old['accepted_at_utc']
    assert archived['positive_evidence'] == old['positive_evidence']
    semantic = progressive_pass2.semantic_taste_entry(migrated)
    assert semantic['positive_evidence'] == old['positive_evidence']
    assert semantic['positive_evidence_binding']['migration_provenance']['prior_authorization_id'] == old['authorization_id']
    risks = refine_visual_ranking.personal_taste_risks(semantic)
    assert set(risks) == {'felt_technical_burden'}

    remaining, metrics = progressive_pass2.legacy_reanalysis_work_and_metrics(
        migrated_state, manifest
    )
    assert len(remaining) == 29
    assert metrics['accepted_count'] == 1
    assert metrics['accepted_completed_count'] == 1
    assert metrics['changed_result_count'] == 1
    assert metrics['changed_fit_outcome_count'] == 0
    assert metrics['unchanged_fit_outcome_count'] == 1
    assert metrics['confirmed_risk_count'] == 1
    assert metrics['pending_count'] == 29
    assert metrics['complete'] is False

    # A grounded migration may change the old fit verdict to not-fit. This is
    # synthetic regression evidence only; no production game conclusion is authored here.
    changed_verdict_doc = result_doc(
        jedi_item,
        outcome='analyzed_not_fit',
        assessment=risk_assessment,
        confidence='high',
        not_fit_basis='confirmed_personal_negative',
        not_fit_evidence=[
            'Frozen Dossier EA application friction is a confirmed personal technical-burden risk.'
        ],
    )
    changed_verdict_state, receipts = accept(
        copy.deepcopy(frozen_state), jedi_item, changed_verdict_doc
    )
    assert receipts[0]['status'] == 'accepted'
    changed_verdict = changed_verdict_state['entries'][JEDI_FAMILY]
    assert changed_verdict['outcome'] == 'analyzed_not_fit'
    assert changed_verdict['migration_fit_outcome_changed'] is True
    _, changed_verdict_metrics = progressive_pass2.legacy_reanalysis_work_and_metrics(
        changed_verdict_state, manifest
    )
    assert changed_verdict_metrics['changed_fit_outcome_count'] == 1
    assert changed_verdict_metrics['unchanged_fit_outcome_count'] == 0

    # Fit level / confidence / taste factors may also be revised while exact old
    # positive evidence remains byte-for-byte semantically identical.
    revised_factors = copy.deepcopy(jedi_item['migration_provenance']['prior_taste_factors'])
    first_factor = next(iter(revised_factors))
    revised_factors[first_factor] = max(0, int(revised_factors[first_factor]) - 1)
    caution = {
        'disposition': 'caution',
        'risk_code': None,
        'text_ru': 'Возвраты по знакомым маршрутам без быстрого перемещения могут создавать дополнительное трение.',
        'evidence_refs': [progressive_pass2.dossier_negative_candidate_refs(jedi_dossier)[0]],
    }
    revised_fit_doc = result_doc(
        jedi_item,
        assessment=assessment_for(jedi_dossier, [caution]),
        fit_level=('moderate' if jedi_item['migration_provenance']['prior_fit_level'] == 'strong' else 'strong'),
        confidence=('medium' if jedi_item['migration_provenance']['prior_confidence'] == 'high' else 'high'),
        taste_factors=revised_factors,
    )
    revised_fit_state, receipts = accept(
        copy.deepcopy(frozen_state), jedi_item, revised_fit_doc
    )
    assert receipts[0]['status'] == 'accepted'
    revised_fit = revised_fit_state['entries'][JEDI_FAMILY]
    assert revised_fit['positive_evidence'] == frozen_state['entries'][JEDI_FAMILY]['positive_evidence']
    assert revised_fit['migration_result_changed'] is True
    revised_semantic = progressive_pass2.semantic_taste_entry(revised_fit)
    assert refine_visual_ranking.personal_taste_risks(revised_semantic) == {}
    assert revised_semantic['deep_negative_assessment_status'] == 'completed_with_caution'

    # The same completed core verdict with fully evaluated but empty negative
    # findings is counted unchanged rather than changed merely for schema backfill.
    unchanged_state, receipts = accept(
        copy.deepcopy(frozen_state),
        jedi_item,
        result_doc(jedi_item, assessment=clean_assessment),
    )
    assert receipts[0]['status'] == 'accepted'
    unchanged = unchanged_state['entries'][JEDI_FAMILY]
    assert unchanged['migration_result_changed'] is False
    _, unchanged_metrics = progressive_pass2.legacy_reanalysis_work_and_metrics(
        unchanged_state, manifest
    )
    assert unchanged_metrics['unchanged_result_count'] == 1
    assert unchanged_metrics['changed_fit_outcome_count'] == 0
    assert unchanged_metrics['unchanged_fit_outcome_count'] == 1
    assert unchanged_metrics['completed_no_relevant_negative_count'] == 1

    # Incomplete migration is terminal for this one-off target but leaves the old
    # authoritative revision current and unmodified.
    incomplete_doc = result_doc(jedi_item, outcome='analysis_incomplete')
    incomplete_state, receipts = accept(
        copy.deepcopy(frozen_state),
        jedi_item,
        incomplete_doc,
    )
    assert receipts[0]['status'] == 'accepted'
    assert receipts[0]['outcome'] == 'analysis_incomplete'
    fallback = incomplete_state['entries'][JEDI_FAMILY]
    assert fallback['outcome'] == old['outcome']
    assert fallback['authorization_id'] == old['authorization_id']
    assert fallback['accepted_at_utc'] == old['accepted_at_utc']
    assert 'revision_history' not in fallback
    assert fallback['legacy_reanalysis_attempts'][-1]['outcome'] == 'analysis_incomplete'
    pending, incomplete_metrics = progressive_pass2.legacy_reanalysis_work_and_metrics(
        incomplete_state, manifest
    )
    assert len(pending) == 29
    assert incomplete_metrics['accepted_count'] == 1
    assert incomplete_metrics['incomplete_count'] == 1

    # A prior not-fit row cannot be flipped to fit by inventing positives that
    # were never accepted in the old revision.
    not_fit_target = next(
        row for row in manifest['targets']
        if row['prior_revision']['outcome'] == 'analyzed_not_fit'
    )
    not_fit_item, not_fit_dossier = prepared_item(manifest, not_fit_target)
    invented_fit = result_doc(
        not_fit_item,
        outcome='analyzed_fit',
        assessment=assessment_for(not_fit_dossier),
        fit_level='moderate',
        confidence='medium',
        positive_evidence=['invented positive'],
        taste_factors={
            'gameplay_mastery': 50,
            'development_variety': 50,
            'structure_pacing_direction': 50,
            'identity_hooks': 50,
            'breadth_of_match': 50,
        },
    )
    rejected_state, receipts = accept(copy.deepcopy(frozen_state), not_fit_item, invented_fit)
    assert receipts[0]['status'] == 'rejected_invalid_result_no_attempt'
    assert rejected_state == frozen_state

    # Normal first-pass/recovery accounting is unchanged by migration acceptance.
    contexts = progressive_pass1.load_jsonl(progressive_pass1.PROGRESSIVE_CONTEXT)
    projection = progressive_pass2.load_json(progressive_pass1.TASTE_PROJECTION)
    queue_rows = progressive_pass1.load_jsonl(progressive_pass1.TASTE_QUEUE)
    pass1_state = progressive_pass1.load_state()
    before = progressive_pass2.recompute_eligibility(
        context_rows=contexts,
        projection_doc=projection,
        queue_rows=queue_rows,
        pass1_state_doc=pass1_state,
        pass2_state_doc=frozen_state,
        current_binding=manifest['dossier_compatibility_binding'],
    )['counts']
    after = progressive_pass2.recompute_eligibility(
        context_rows=contexts,
        projection_doc=projection,
        queue_rows=queue_rows,
        pass1_state_doc=pass1_state,
        pass2_state_doc=migrated_state,
        current_binding=manifest['dossier_compatibility_binding'],
    )['counts']
    for key in (
        'deep_total_current_coverage_target',
        'deep_first_pass_attempted_count',
        'deep_authoritative_completed_count',
        'deep_normal_first_pass_remaining_count',
        'recovery_owned_count',
        'recovery_eligible_count',
        'recovery_pending_count',
    ):
        assert before[key] == after[key], (key, before[key], after[key])

    # Finite non-recurrence: terminal migration attempts for every frozen target
    # remove all migration work; no later legacy discovery is performed.
    terminal_state = copy.deepcopy(frozen_state)
    for target in manifest['targets']:
        entry = terminal_state['entries'][target['family_id']]
        prov = progressive_pass2.migration_provenance(manifest, target)
        entry['legacy_reanalysis_attempts'] = [{
            **{field: target.get(field) for field in progressive_pass2.PASS1_IDENTITY_FIELDS},
            'authorization_id': progressive_pass2.make_legacy_reanalysis_work_item(
                manifest, target
            )['authorization_id'],
            'migration_provenance': prov,
            'outcome': 'analysis_incomplete',
            'analysis_issue_code': 'insufficient_evidence',
            'accepted_at_utc': '2026-09-28T05:00:00+00:00',
        }]
    no_work, terminal_metrics = progressive_pass2.legacy_reanalysis_work_and_metrics(
        terminal_state, manifest
    )
    assert no_work == []
    assert terminal_metrics['accepted_count'] == 30
    assert terminal_metrics['incomplete_count'] == 30
    assert terminal_metrics['pending_count'] == 0
    assert terminal_metrics['complete'] is True

    # Result/terminal schemas explicitly support migration and keep it distinct
    # from normal/recovery; the canonical prompt forbids fresh positive research.
    result_schema = json.loads(
        Path('config/progressive_pass2_result_schema.json').read_text(encoding='utf-8')
    )
    terminal_schema = json.loads(
        Path('config/progressive_pass2_execution_receipt_schema.json').read_text(encoding='utf-8')
    )
    for schema in (result_schema, terminal_schema):
        assert 'legacy_full_reanalysis' in schema['properties']['work_mode']['enum']
        assert 'migration_provenance' in schema['properties']
    prompt = Path('config/progressive_pass2_worker_prompt.md').read_text(encoding='utf-8')
    assert 'One-off legacy full reanalysis mode' in prompt
    assert 'Do **not** search the web or Dossier for additional positive evidence' in prompt
    decisions = Path('PROJECT_DECISIONS.md').read_text(encoding='utf-8')
    assert 'PPD-010' in decisions

    print(
        'DEEP_LEGACY_FULL_REANALYSIS_TESTS=PASS '
        f"targets={manifest['scope']['target_count']} "
        f"prior_fit={manifest['scope']['prior_fit_count']} "
        f"prior_not_fit={manifest['scope']['prior_not_fit_count']}"
    )


if __name__ == '__main__':
    run()
