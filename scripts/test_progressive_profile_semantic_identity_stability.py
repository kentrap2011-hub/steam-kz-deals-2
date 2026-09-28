import copy
import hashlib
import json
from datetime import datetime, timezone

import card_explanation_policy
import grounded_negative_visual
import progressive_pass1
import progressive_pass2
import progressive_personalization
import refine_visual_ranking as refiner


def profile_projection(*, commit_char='a', content=b'profile-a', model='taste-v3',
                       semantics='s' * 64, context_contract='c' * 40):
    blob = hashlib.sha1(f"blob {len(content)}\\0".encode('ascii') + content).hexdigest()
    return {
        'schema_version': 3,
        'status': 'complete',
        'current_profile': {
            'repository': progressive_pass1.CANONICAL_PROFILE_REPOSITORY,
            'path': progressive_pass1.CANONICAL_PROFILE_PATH,
            'resolved_commit_sha': commit_char * 40,
            'blob_sha': blob,
            'content_sha256': hashlib.sha256(content).hexdigest(),
            'bytes': len(content),
        },
        'current_binding': {
            'taste_model_version': model,
            'taste_semantics_sha256': semantics,
            'candidate_context_contract_blob_sha': context_contract,
        },
    }


def contexts():
    return [
        {'family_id': 'game:1', 'taste_subject_key': 'App_1'},
        {'family_id': 'game:2', 'taste_subject_key': 'App_2'},
    ]


def queue_rows(*, fp1='fp-1'):
    return [
        {
            'family_id': 'game:1',
            'taste_subject_key': 'App_1',
            'appid': '1',
            'taste_fingerprint': fp1,
            'candidate_context_sha256': 'ctx-1',
        },
        {
            'family_id': 'game:2',
            'taste_subject_key': 'App_2',
            'appid': '2',
            'taste_fingerprint': 'fp-2',
            'candidate_context_sha256': 'ctx-2',
        },
    ]


def synthetic_rules():
    projection_a = profile_projection(commit_char='a', content=b'identical-profile')
    projection_b = profile_projection(commit_char='b', content=b'identical-profile')
    generation_a, bindings_a, _ = progressive_pass1.current_bindings(
        contexts(), projection_a, queue_rows()
    )
    generation_b, bindings_b, _ = progressive_pass1.current_bindings(
        contexts(), projection_b, queue_rows()
    )

    # PPD-012: provenance pin changes, semantic generation/work does not.
    assert generation_a['profile_pin']['pin_sha256'] != generation_b['profile_pin']['pin_sha256']
    assert (
        generation_a['semantic_profile']['profile_semantic_sha256']
        == generation_b['semantic_profile']['profile_semantic_sha256']
    )
    assert generation_a['semantic_generation_id'] == generation_b['semantic_generation_id']
    assert bindings_a['game:1']['work_id'] == bindings_b['game:1']['work_id']

    # A result accepted under the earlier exact pin remains current semantically,
    # but a new transport must still echo the exact current prepared pin.
    old_entry = {
        **{field: bindings_a['game:1'][field] for field in progressive_pass1.IDENTITY_FIELDS},
        'profile_semantic_sha256': bindings_a['game:1']['profile_semantic_sha256'],
        'pass1_attempted': True,
        'outcome': 'analyzed_fit',
        'accepted_at_utc': '2026-09-28T00:00:00+00:00',
    }
    state = {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS1-STATE-V1',
        'entries': {'game:1': old_entry},
    }
    assert progressive_pass1.matching_state_entry(bindings_b['game:1'], state) is old_entry
    old_transport = {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS1-RESULT-V1',
        **{field: bindings_a['game:1'][field] for field in progressive_pass1.IDENTITY_FIELDS},
    }
    assert progressive_pass1.identity_matches_submission(old_transport, bindings_b['game:1']) is False

    # Real profile bytes still invalidate the generation/work.
    projection_changed = profile_projection(commit_char='c', content=b'changed-profile')
    generation_changed, bindings_changed, _ = progressive_pass1.current_bindings(
        contexts(), projection_changed, queue_rows()
    )
    assert generation_changed['semantic_generation_id'] != generation_a['semantic_generation_id']
    assert bindings_changed['game:1']['work_id'] != bindings_a['game:1']['work_id']
    assert progressive_pass1.matching_state_entry(bindings_changed['game:1'], state) is None

    # Missing/inconsistent semantic content identity fails closed.
    missing_content = profile_projection(commit_char='e', content=b'identical-profile')
    missing_content['current_profile'].pop('content_sha256')
    try:
        progressive_pass1.semantic_generation(missing_content)
    except ValueError:
        pass
    else:
        raise AssertionError('missing profile content identity did not fail closed')

    missing_blob = profile_projection(commit_char='f', content=b'identical-profile')
    missing_blob['current_profile']['blob_sha'] = 'not-a-git-blob'
    try:
        progressive_pass1.semantic_generation(missing_blob)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid profile blob identity did not fail closed')

    # An arbitrary old result from different semantic content cannot be revived.
    arbitrary_old = copy.deepcopy(old_entry)
    arbitrary_old['work_authority_commit'] = '0' * 40
    assert progressive_pass1.historical_semantic_equivalence(
        arbitrary_old,
        bindings_changed['game:1'],
        manifest_path=progressive_pass1.WORK,
        expected_contract='PROGRESSIVE-PASS1-WORK-V1',
    ) is None

    # Model / semantics / context-contract changes remain global invalidators.
    for changed in (
        profile_projection(commit_char='d', content=b'identical-profile', model='taste-v4'),
        profile_projection(commit_char='d', content=b'identical-profile', semantics='t' * 64),
        profile_projection(commit_char='d', content=b'identical-profile', context_contract='d' * 40),
    ):
        assert (
            progressive_pass1.semantic_generation(changed)['semantic_generation_id']
            != generation_a['semantic_generation_id']
        )

    # Item fingerprint/context remains per-item identity, not global profile provenance.
    _g, fingerprint_bindings, _ = progressive_pass1.current_bindings(
        contexts(), projection_b, queue_rows(fp1='fp-1-changed')
    )
    assert fingerprint_bindings['game:1']['work_id'] != bindings_a['game:1']['work_id']
    assert fingerprint_bindings['game:2']['work_id'] == bindings_a['game:2']['work_id']


def production_history_reconciliation():
    context_rows = progressive_pass1.load_jsonl(progressive_pass1.PROGRESSIVE_CONTEXT)
    projection_doc = progressive_pass1.load_json(progressive_pass1.TASTE_PROJECTION)
    queue = progressive_pass1.load_jsonl(progressive_pass1.TASTE_QUEUE)
    pass1_state = progressive_pass1.load_state()
    pass2_state = progressive_pass2.load_state()
    migration = progressive_pass2.load_legacy_reanalysis_manifest()
    generation, bindings, queue_by_family = progressive_pass1.current_bindings(
        context_rows, projection_doc, queue
    )

    targets = list(migration.get('targets') or [])
    assert len(targets) == 30
    target_families = {row['family_id'] for row in targets}
    before = copy.deepcopy(pass2_state)

    reconciled = []
    for target in targets:
        family_id = target['family_id']
        binding = bindings.get(family_id)
        assert binding is not None, f'migration target missing current binding: {family_id}'
        entry = (pass2_state.get('entries') or {}).get(family_id)
        assert isinstance(entry, dict), f'migration target missing durable state: {family_id}'
        proof = progressive_pass1.historical_semantic_equivalence(
            entry,
            binding,
            manifest_path=progressive_pass2.WORK,
            expected_contract='PROGRESSIVE-PASS2-WORK-V1',
        )
        assert proof is not None, f'migration target semantic equivalence not proven: {family_id}'
        assert progressive_pass2.authoritative_completion_entry(binding, pass2_state) is entry
        reconciled.append(family_id)

    # Projection recomputation is read-only and must not emit any of the 30 again.
    current_binding = progressive_pass2.current_dossier_binding()
    recomputed = progressive_pass2.recompute_eligibility(
        context_rows=context_rows,
        projection_doc=projection_doc,
        queue_rows=queue,
        pass1_state_doc=pass1_state,
        pass2_state_doc=pass2_state,
        current_binding=current_binding,
        now=datetime(2026, 9, 28, 12, 55, tzinfo=timezone.utc),
    )
    emitted = {row['family_id'] for row in recomputed['items']}
    assert not (target_families & emitted)
    assert recomputed['counts']['deep_authoritative_completed_count'] >= 30
    assert pass2_state == before

    # Inspect every non-migration durable authoritative completion separately.
    nonmigration = []
    for family_id, entry in (pass2_state.get('entries') or {}).items():
        if family_id in target_families or entry.get('authoritative_completed') is not True:
            continue
        binding = bindings.get(family_id)
        proof = None
        current = False
        if binding is not None:
            proof = progressive_pass1.historical_semantic_equivalence(
                entry,
                binding,
                manifest_path=progressive_pass2.WORK,
                expected_contract='PROGRESSIVE-PASS2-WORK-V1',
            )
            current = progressive_pass2.authoritative_completion_entry(binding, pass2_state) is entry
        nonmigration.append({
            'family_id': family_id,
            'appid': entry.get('appid'),
            'outcome': entry.get('outcome'),
            'semantically_equivalent': proof is not None,
            'current_after_ppd012': current,
        })
    assert len(nonmigration) >= 2

    print('PPD012_MIGRATION_RECONCILED=' + json.dumps({
        'count': len(reconciled),
        'semantic_generation_id': generation['semantic_generation_id'],
        'profile_semantic_sha256': generation['semantic_profile']['profile_semantic_sha256'],
        'authoritative_count': recomputed['counts']['deep_authoritative_completed_count'],
        'ordinary_emitted_migration_targets': 0,
    }, sort_keys=True))
    effective = progressive_personalization.effective_taste_entries()
    deep_fit_projection = []
    for family_id, binding in bindings.items():
        entry = progressive_pass2.authoritative_completion_entry(binding, pass2_state)
        if not isinstance(entry, dict) or entry.get('outcome') != 'analyzed_fit':
            continue
        taste_entry = effective.get(binding['taste_subject_key'])
        assert isinstance(taste_entry, dict), f'current Deep fit missing effective taste entry: {family_id}'
        assert taste_entry.get('semantic_source') == 'progressive_pass2', (
            family_id, taste_entry.get('semantic_source')
        )
        risks = refiner.personal_taste_risks(taste_entry)
        visible = card_explanation_policy.visible_risk_payload(risks)
        finalizer_risks = grounded_negative_visual.all_risk_candidates(taste_entry, {}, {})
        finalizer_has_taste_risk = any(
            row.get('source') == 'taste_negative_evidence'
            for row in finalizer_risks.values()
            if isinstance(row, dict)
        )
        finalizer_visible = (
            grounded_negative_visual.visible_grounded_payload(finalizer_risks)
            if finalizer_has_taste_risk
            else {'risks': [], 'risk_provenance': []}
        )
        for payload in (visible, finalizer_visible):
            for row in payload['risk_provenance']:
                if row.get('source') != 'taste_negative_evidence':
                    continue
                assert (row.get('semantic_binding') or {}).get('semantic_source') == 'progressive_pass2', (
                    family_id, row
                )
                assert row.get('evidence_refs'), (family_id, row)
        deep_fit_projection.append({
            'family_id': family_id,
            'taste_subject_key': binding['taste_subject_key'],
            'risk_count': len(finalizer_visible['risks']),
            'bound_risk_count': sum(
                1 for row in finalizer_visible['risk_provenance']
                if row.get('source') == 'taste_negative_evidence'
                and (row.get('semantic_binding') or {}).get('semantic_source') == 'progressive_pass2'
                and row.get('evidence_refs')
            ),
        })
    assert len(deep_fit_projection) == recomputed['counts']['deep_completed_fit_count']

    print('PPD012_NONMIGRATION_INSPECTION=' + json.dumps(nonmigration, sort_keys=True))
    print('PPD012_DEEP_VISUAL_PROVENANCE=' + json.dumps({
        'fit_count': len(deep_fit_projection),
        'cards_with_visible_risk': sum(row['risk_count'] > 0 for row in deep_fit_projection),
        'bound_visible_risk_rows': sum(row['bound_risk_count'] for row in deep_fit_projection),
    }, sort_keys=True))


def main():
    synthetic_rules()
    production_history_reconciliation()
    print('progressive profile semantic identity stability regression: ok')


if __name__ == '__main__':
    main()
