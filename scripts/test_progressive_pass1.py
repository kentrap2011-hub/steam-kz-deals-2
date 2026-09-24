import json
import tempfile
from pathlib import Path

import progressive_pass1
import progressive_personalization


FACTOR_VALUES = {
    'gameplay_mastery': 80,
    'development_variety': 75,
    'structure_pacing_direction': 70,
    'identity_hooks': 65,
    'breadth_of_match': 72,
}


def projection(source='commercial-A', fingerprint_suffix=''):
    entries = {}
    for index in range(1, 5):
        key = f'App_{index}'
        entries[key] = {
            'status': 'ai_required',
            'taste_fingerprint': f'fp-{index}{fingerprint_suffix}',
            'candidate_context_sha256': f'ctx-{index}',
        }
    return {
        'schema_version': 3,
        'status': 'complete',
        'source_mailing_updated_at_utc': source,
        'current_profile': {
            'repository': progressive_pass1.CANONICAL_PROFILE_REPOSITORY,
            'path': progressive_pass1.CANONICAL_PROFILE_PATH,
            'resolved_commit_sha': 'a' * 40,
            'blob_sha': 'b' * 40,
            'content_sha256': 'c' * 64,
            'bytes': 123,
            'raw_url': (
                'https://raw.githubusercontent.com/'
                + progressive_pass1.CANONICAL_PROFILE_REPOSITORY
                + '/' + ('a' * 40) + '/'
                + progressive_pass1.CANONICAL_PROFILE_PATH
            ),
        },
        'current_binding': {
            'taste_model_version': 'taste-v3',
            'taste_semantics_sha256': 'semantics-sha',
            'candidate_context_contract_blob_sha': 'context-contract-blob',
        },
        'entries': entries,
    }


def contexts():
    rows = []
    for index in range(1, 5):
        rows.append({
            'family_id': f'game:{index}',
            'taste_subject_key': f'App_{index}',
            'purchase': {
                'key': f'App_{index}',
                'title': f'Game {index}',
                'discount_percent': 50,
                'current_price_rub_display': 100 + index,
                'original_price_rub_display': 200 + index,
                'sale_end_utc': '2099-01-01T00:00:00+00:00',
            },
            'history': {'quality': 'unverified', 'minimum_rub_display': None},
            'deal_if_strong': {'disposition': 'INCLUDE'},
            'deal_if_moderate': {'disposition': 'INCLUDE'},
            'context_only': {'wishlist': False},
            'semantic_condition': {
                'ai_condition': 'taste_subject_include_controls_purchase_family',
                'requires_ai_base_support': False,
                'base_appids': [str(index)],
            },
        })
    return rows


def queue_rows(fingerprint_suffix=''):
    rows = []
    for index in range(1, 5):
        rows.append({
            'family_id': f'game:{index}',
            'taste_subject_key': f'App_{index}',
            'appid': str(index),
            'title': f'Game {index}',
            'taste_fingerprint': f'fp-{index}{fingerprint_suffix}',
            'candidate_context_sha256': f'ctx-{index}',
            'short_description': f'Candidate-specific gameplay description {index}',
            'bundle_members': [],
            'fit_tags': ['Action'],
            'core_fit_count': 1,
            'release_date': '1 Jan, 2026',
            'semantic_condition': {
                'ai_condition': 'taste_subject_include_controls_purchase_family',
                'requires_ai_base_support': False,
                'base_appids': [str(index)],
            },
        })
    return rows


def work_doc(bindings, queue):
    items = []
    by_family = {row['family_id']: row for row in queue}
    generation = next(iter(bindings.values()))['semantic_generation_id']
    for sequence, family_id in enumerate(sorted(bindings), 1):
        binding = bindings[family_id]
        q = by_family[family_id]
        item = {
            **binding,
            'sequence': sequence,
            'semantic_input': {
                'title': q['title'],
                'short_description': q['short_description'],
                'fit_tags': q['fit_tags'],
                'core_fit_count': q['core_fit_count'],
                'release_date': q['release_date'],
                'semantic_condition': q['semantic_condition'],
            },
            'submission_path': f"data/ai_inbox/progressive_pass1/{generation[:16]}--{binding['work_id']}.json",
        }
        items.append(item)
    return {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS1-WORK-V1',
        'pass1_active': True,
        'pass2_active': True,
        'semantic_generation_id': generation,
        'profile_pin': progressive_pass1.profile_pin_from_projection(projection()),
        'items': items,
    }


def submission(item, outcome, **kwargs):
    doc = {
        'schema_version': 1,
        'contract': 'PROGRESSIVE-PASS1-RESULT-V1',
        **{field: item[field] for field in progressive_pass1.IDENTITY_FIELDS},
        'outcome': outcome,
    }
    doc.update(kwargs)
    return doc


def main():
    contract = progressive_pass1.load_contract()
    assert contract['attempt_budget']['maximum_attempts_per_work_id'] == 1
    assert contract['attempt_budget']['automatic_pass1_retry'] is False
    assert contract['transport']['one_result_artifact_per_item'] is True
    assert contract['transport']['batch_atomicity'] is False
    assert contract['transport']['maximal_contiguous_prefix'] is False
    assert contract['pass2']['active'] is True

    base_projection = projection('commercial-A')
    generation_a = progressive_pass1.semantic_generation(base_projection)
    generation_b = progressive_pass1.semantic_generation(projection('commercial-B'))
    # PASS1-16: commercial source refresh alone does not reset semantic generation.
    assert generation_a == generation_b

    ctx = contexts()
    queue = queue_rows()
    _generation, bindings, _ = progressive_pass1.current_bindings(ctx, base_projection, queue)
    _generation2, bindings_after_commercial, _ = progressive_pass1.current_bindings(
        ctx, projection('commercial-B'), queue
    )
    assert {k: v['work_id'] for k, v in bindings.items()} == {
        k: v['work_id'] for k, v in bindings_after_commercial.items()
    }

    # Fingerprint change rebinds only affected item work.
    changed_queue = queue_rows()
    changed_queue[0]['taste_fingerprint'] = 'fp-1-new'
    _g3, changed_bindings, _ = progressive_pass1.current_bindings(ctx, base_projection, changed_queue)
    assert changed_bindings['game:1']['work_id'] != bindings['game:1']['work_id']
    assert changed_bindings['game:2']['work_id'] == bindings['game:2']['work_id']

    work = work_doc(bindings, queue)
    by_family = {item['family_id']: item for item in work['items']}
    fit = submission(
        by_family['game:1'],
        'analyzed_fit',
        fit_level='strong',
        confidence='high',
        positive_evidence=['active decision making and learnable mastery'],
        taste_factors=FACTOR_VALUES,
    )
    not_fit = submission(
        by_family['game:2'],
        'analyzed_not_fit',
        confidence='medium',
        not_fit_basis='completed_below_threshold',
        not_fit_evidence=['candidate-specific structure conflicts with durable preference for clear direction'],
    )
    insufficient = submission(
        by_family['game:3'],
        'analysis_incomplete',
        issue_code='insufficient_evidence',
    )
    invalid = submission(
        by_family['game:4'],
        'analyzed_fit',
        fit_level='moderate',
        confidence='medium',
        positive_evidence=['candidate-specific active play'],
        # taste_factors deliberately missing
    )

    docs = [
        (Path(by_family['game:1']['submission_path']).name, fit, None),
        (Path(by_family['game:2']['submission_path']).name, not_fit, None),
        (Path(by_family['game:3']['submission_path']).name, insufficient, None),
        (Path(by_family['game:4']['submission_path']).name, invalid, None),
    ]
    initial_state = {'schema_version': 1, 'contract': 'PROGRESSIVE-PASS1-STATE-V1', 'entries': {}}
    state, receipts = progressive_pass1.process_submission_documents(
        work, initial_state, docs, accepted_at_utc='2026-09-21T00:00:00+00:00'
    )

    # PASS1-01..04: independent fit/not-fit/incomplete/invalid child acceptance.
    assert state['entries']['game:1']['outcome'] == 'analyzed_fit'
    assert state['entries']['game:2']['outcome'] == 'analyzed_not_fit'
    assert state['entries']['game:3']['outcome'] == 'analysis_incomplete'
    assert state['entries']['game:3']['analysis_issue_code'] == 'insufficient_evidence'
    assert state['entries']['game:4']['outcome'] == 'analysis_incomplete'
    assert state['entries']['game:4']['analysis_issue_code'] == 'invalid_semantic_result'
    assert [r['status'] for r in receipts] == [
        'accepted', 'accepted', 'accepted', 'accepted_as_incomplete_invalid_result'
    ]

    # PASS1-07: replay never consumes a second attempt.
    replay_state, replay_receipts = progressive_pass1.process_submission_documents(
        work,
        state,
        [(Path(by_family['game:1']['submission_path']).name, fit, None)],
        accepted_at_utc='2026-09-22T00:00:00+00:00',
    )
    assert replay_state == state
    assert replay_receipts[0]['status'] == 'replay_ignored'

    # PASS1-09: an artifact outside the current deterministic path is stale and
    # cannot mutate the current item. Wrong content published at the exact current
    # path is the item's one attempt and becomes invalid_semantic_result.
    stale = dict(fit, taste_fingerprint='wrong')
    stale_state, stale_receipts = progressive_pass1.process_submission_documents(
        work,
        initial_state,
        [('old-generation--old-work.json', stale, None)],
        accepted_at_utc='2026-09-21T00:00:00+00:00',
    )
    assert stale_state == initial_state
    assert stale_receipts[0]['status'] == 'rejected_stale_or_mismatched'

    wrong_identity_state, wrong_identity_receipts = progressive_pass1.process_submission_documents(
        work,
        initial_state,
        [(Path(by_family['game:1']['submission_path']).name, stale, None)],
        accepted_at_utc='2026-09-21T00:00:00+00:00',
    )
    assert wrong_identity_state['entries']['game:1']['outcome'] == 'analysis_incomplete'
    assert wrong_identity_state['entries']['game:1']['analysis_issue_code'] == 'invalid_semantic_result'
    assert wrong_identity_receipts[0]['status'] == 'accepted_as_incomplete_invalid_result'

    malformed_state, malformed_receipts = progressive_pass1.process_submission_documents(
        work,
        initial_state,
        [(Path(by_family['game:4']['submission_path']).name, None, 'JSONDecodeError:test')],
        accepted_at_utc='2026-09-21T00:00:00+00:00',
    )
    assert malformed_state['entries']['game:4']['outcome'] == 'analysis_incomplete'
    assert malformed_state['entries']['game:4']['analysis_issue_code'] == 'invalid_semantic_result'
    assert malformed_receipts[0]['status'] == 'accepted_as_incomplete_invalid_result'

    # Worker/tool failure is a typed incomplete outcome and does not require retry.
    worker_failure = submission(
        by_family['game:1'],
        'analysis_incomplete',
        issue_code='worker_failure',
    )
    wf_state, _ = progressive_pass1.process_submission_documents(
        work,
        initial_state,
        [(Path(by_family['game:1']['submission_path']).name, worker_failure, None)],
        accepted_at_utc='2026-09-21T00:00:00+00:00',
    )
    assert wf_state['entries']['game:1']['outcome'] == 'analysis_incomplete'
    assert wf_state['entries']['game:1']['analysis_issue_code'] == 'worker_failure'

    # Projection into the site is independently item-level.
    original_state = progressive_pass1.STATE
    original_queue = progressive_pass1.TASTE_QUEUE
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            state_path = tmp / 'state.json'
            queue_path = tmp / 'queue.jsonl'
            # Leave game:4 untouched for Tier 3 and persist only 1/2/3.
            partial_state = json.loads(json.dumps(state))
            partial_state['entries'].pop('game:4')
            state_path.write_text(json.dumps(partial_state), encoding='utf-8')
            queue_path.write_text(
                ''.join(json.dumps(row) + '\n' for row in queue),
                encoding='utf-8',
            )
            progressive_pass1.STATE = state_path
            progressive_pass1.TASTE_QUEUE = queue_path

            state_index = progressive_personalization.build_state_index(
                context_rows=ctx,
                projection_doc=base_projection,
                taste_entries={},
            )
    finally:
        progressive_pass1.STATE = original_state
        progressive_pass1.TASTE_QUEUE = original_queue

    assert state_index['game:1']['analysis_state'] == 'analyzed_fit'
    assert state_index['game:1']['analysis_tier'] == 1
    assert state_index['game:2']['analysis_state'] == 'analyzed_not_fit'
    assert state_index['game:3']['analysis_state'] == 'analysis_incomplete'
    assert state_index['game:3']['analysis_tier'] == 2
    assert state_index['game:4']['analysis_state'] == 'not_analyzed'
    assert state_index['game:4']['analysis_tier'] == 3

    # PASS1-11/14: counts reconcile after partial progress; not-fit is counted but hidden.
    visible_items = [
        {'id': 'game:1', 'analysis_state': 'analyzed_fit', 'analysis_tier': 1},
        {'id': 'game:3', 'analysis_state': 'analysis_incomplete', 'analysis_tier': 2},
        {'id': 'game:4', 'analysis_state': 'not_analyzed', 'analysis_tier': 3},
    ]
    status = progressive_personalization.build_processing_status(state_index, visible_items)
    assert status['total_current_candidates'] == 4
    assert status['analyzed_fit_count'] == 1
    assert status['analyzed_not_fit_count'] == 1
    assert status['analysis_incomplete_count'] == 1
    assert status['not_analyzed_count'] == 1
    assert status['normal_visible_count'] == 3
    assert status['pass1_total_scope'] == 4
    assert status['pass1_attempted_count'] == 3
    assert status['pass1_remaining_count'] == 1
    progressive_personalization.validate_processing_status(status)

    # PASS1-12/13: tier precedence is preserved for accepted fit and incomplete.
    ordered, _ = progressive_personalization.apply_progressive_order([
        {
            'id': 'game:4', 'title': 'Game 4', 'analysis_state': 'not_analyzed',
            'analysis_tier': 3, 'current_price_rub': 100, 'original_price_rub': 200,
            'discount_percent': 50, 'history_quality': 'unverified',
        },
        {
            'id': 'game:3', 'title': 'Game 3', 'analysis_state': 'analysis_incomplete',
            'analysis_tier': 2, 'current_price_rub': 100, 'original_price_rub': 200,
            'discount_percent': 50, 'history_quality': 'unverified',
        },
    ])
    assert [row['analysis_state'] for row in ordered] == ['analysis_incomplete', 'not_analyzed']

    print('progressive PASS 1 item-level regression: ok')


if __name__ == '__main__':
    main()
