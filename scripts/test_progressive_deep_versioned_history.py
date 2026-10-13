"""Bounded regression for durable Deep profile-version history and oldest-first work."""
import copy
from unittest.mock import patch

import build_progressive_pass2_work as builder
import progressive_deep_history as history
import progressive_pass2 as deep


def completed(family, when, profile='old', *, appid='111', work='w1', verdict='analyzed_fit'):
    result = {
        'family_id': family,
        'taste_subject_key': 'App_111',
        'appid': appid,
        'work_id': work,
        'semantic_generation_id': profile,
        'profile_semantic_sha256': profile,
        'profile_pin_sha256': 'pin:' + profile,
        'authorization_id': 'auth:' + work,
        'work_authority_commit': 'a' * 40,
        'accepted_at_utc': when,
        'authoritative_completed': True,
        'outcome': verdict,
        'positive_evidence': ['Original positive evidence'] if verdict == 'analyzed_fit' else None,
        'not_fit_evidence': ['Original negative evidence'] if verdict == 'analyzed_not_fit' else None,
        'negative_assessment': {'status': 'completed', 'findings': []},
    }
    return result


def pin(content_sha, source_commit):
    return {
        'contract': 'PROGRESSIVE-PROFILE-PIN-V1',
        'pin_sha256': 'pin:' + content_sha,
        'profile_identity': {
            'repository': 'kentrap2011-hub/stopgame-ratings-data',
            'path': 'gaming_taste_live.json',
            'content_sha256': content_sha,
            'blob_sha': 'b' * 40,
            'resolved_commit_sha': source_commit,
        },
    }


def main():
    # 01: even one punctuation change changes profile-content version.
    p1 = pin('1' * 64, 'a' * 40)
    punct = pin('2' * 64, 'b' * 40)
    same_bytes_new_commit = pin('1' * 64, 'c' * 40)
    a = history.content_profile_version(p1, {'profile_pin_sha256': p1['pin_sha256']})
    b = history.content_profile_version(punct, {'profile_pin_sha256': punct['pin_sha256']})
    c = history.content_profile_version(same_bytes_new_commit, {'profile_pin_sha256': same_bytes_new_commit['pin_sha256']})
    assert a['content_version_id'] != b['content_version_id']
    assert a['content_version_id'] == c['content_version_id']
    assert a['source_commit_sha'] != c['source_commit_sha']
    assert a['source_commit_at_utc'] is None and c['source_commit_at_utc'] is None
    assert history.content_profile_version(p1, {'profile_pin_sha256': punct['pin_sha256']}) is None

    # 02-04: old accepted evidence/verdict/time survives new version, even a
    # newer failed/incomplete attempt, without being called current authority.
    prior = completed('game:one', '2026-09-30T13:01:00+00:00')
    current = completed('game:one', '2026-10-13T13:07:00+00:00', 'new', work='w2',
                        verdict='analyzed_not_fit')
    new_pin = pin('2' * 64, 'b' * 40)
    updated = history.preserve_completion(
        prior, copy.deepcopy(current),
        {'profile_pin_sha256': new_pin['pin_sha256']},
        {'outcome': 'analyzed_not_fit'}, new_pin,
    )
    records = history.completed_versions(updated)
    assert len(records) == 2
    assert [r['accepted_at_utc'] for r in records] == [
        '2026-09-30T13:01:00+00:00', '2026-10-13T13:07:00+00:00'
    ]
    assert records[0]['result']['positive_evidence'] == ['Original positive evidence']
    assert records[-1]['result']['outcome'] == 'analyzed_not_fit'
    assert records[-1]['profile_version']['content_version_id'] == '2' * 64
    assert len(history.completed_versions(history.preserve_completion(
        updated, copy.deepcopy(updated), {'profile_pin_sha256': new_pin['pin_sha256']},
        {'outcome': 'analysis_incomplete'}, new_pin,
    ))) == 2
    failed_root = dict(updated, authoritative_completed=False, outcome='analysis_incomplete')
    failed_root['completed_versions'] = copy.deepcopy(updated['completed_versions'])
    assert history.latest_completed({'entries': {'game:one': failed_root}}, 'game:one')['revision_id'] == records[-1]['revision_id']
    assert history.latest_completed({'entries': {'game:one': failed_root}}, 'game:one', {
        'family_id': 'game:one', 'appid': '999', 'taste_subject_key': 'App_111'
    }) is None

    # 05: a new normal first-pass ingest for a changed semantic generation
    # copies an old success before the per-game root is overwritten.
    row = {field: 'value:' + field for field in deep.PASS1_IDENTITY_FIELDS}
    row.update(family_id='game:one', appid='111', taste_subject_key='App_111',
               profile_semantic_sha256='new', profile_pin_sha256=new_pin['pin_sha256'],
               work_mode='normal_first_pass', result_submission_path='test/new.json',
               authorization_id='auth:new', work_id='w-new',
               dossier_content_sha256='digest', dossier_compatibility_binding={'binding': True})
    attempt = {
        'outcome': 'analysis_incomplete',
        'accepted_at_utc': '2026-10-14T00:00:00+00:00',
        'analysis_issue_code': 'worker_failure',
        'attempt_consumption_source': 'accepted_result',
        'authorization_id': 'auth:new',
        'dossier_content_sha256': 'digest',
        'dossier_compatibility_binding': {'binding': True},
    }
    with patch.object(deep, 'matching_state_entry', return_value=None), \
         patch.object(deep, '_identity_matches', return_value=True), \
         patch.object(deep, 'normalize_result', return_value=attempt):
        state, receipts = deep.process_result_documents(
            {'items': [row], 'profile_pin': new_pin},
            {'schema_version': 2, 'contract': 'PROGRESSIVE-PASS2-STATE-V2',
             'entries': {'game:one': prior}},
            [('new.json', {'outcome': 'analysis_incomplete'}, None)],
        )
    assert receipts[0]['status'] == 'accepted'
    assert state['entries']['game:one']['outcome'] == 'analysis_incomplete'
    assert history.latest_completed(state, 'game:one')['result']['outcome'] == 'analyzed_fit'
    assert state['entries']['game:one']['normal_first_pass_attempted'] is True

    # 06: no cross-release/appid history; exact game tie break, never first.
    from test_semantic_queue_priority import context, item, CONTRACT
    items = [item('game:oldest'), item('game:newest'), item('game:never')]
    for row in items:
        row['appid'] = '111'
        row['taste_subject_key'] = 'App_111'
    seen = {
        'game:oldest': completed('game:oldest', '2026-09-01T00:00:00Z', appid='111'),
        'game:newest': completed('game:newest', '2026-10-01T00:00:00Z', appid='111'),
        'game:never': completed('game:never', '2026-08-01T00:00:00Z', appid='222'),
    }
    contexts = {
        'game:oldest': context('game:oldest', rating=20),
        'game:newest': context('game:newest', rating=99),
        'game:never': context('game:never', rating=99),
    }
    ordered = builder.order_normal_items(items, contexts, {'entries': seen}, CONTRACT)
    assert [v['family_id'] for v in ordered] == ['game:never', 'game:oldest', 'game:newest']

    # 07-08: overlapping legacy reanalysis and score migration revisions
    # count one game per content version and never invent a profile SHA.
    old_revision = {
        'revision_kind': 'pre_legacy_full_reanalysis',
        'state': completed('game:one', '2026-09-20T00:00:00Z', work='older'),
    }
    upgraded = copy.deepcopy(updated)
    upgraded['revision_history'] = [old_revision, old_revision]
    game2 = completed('game:two', '2026-09-19T00:00:00Z', appid='112')
    game2['taste_subject_key'] = 'App_112'
    stats = history.version_counts(
        {'entries': {'game:one': upgraded, 'game:two': game2}},
        {
            'game:one': {'family_id': 'game:one', 'appid': '111', 'taste_subject_key': 'App_111'},
            'game:two': {'family_id': 'game:two', 'appid': '112', 'taste_subject_key': 'App_112'},
            'game:never': {'family_id': 'game:never', 'appid': '113', 'taste_subject_key': 'App_113'},
        },
        '2' * 64, current_authoritative_families={'game:one'},
    )
    assert stats['deep_current_version_target'] == 3
    assert stats['deep_current_version_completed_count'] == 1
    assert stats['deep_historical_only_not_current_compatible_count'] == 1
    assert stats['deep_never_completed_count'] == 1
    assert stats['deep_current_version_remaining_count'] == 2
    assert stats['deep_profile_version_unique_game_counts']['2' * 64] == 1
    assert stats['deep_profile_version_unique_game_counts']['legacy-unverified:pin:old'] == 2
    # Existing exact/current authority remains separate from historical presence.
    incompatible = {'family_id': 'game:one', 'work_id': 'new-work',
                    'profile_semantic_sha256': 'other-profile'}
    assert deep.authoritative_completion_entry(incompatible, {
        'entries': {'game:one': prior}
    }) is None
    print('Deep versioned history: punctuation, provenance, preservation, ordering, identity, overlap: OK')


if __name__ == '__main__':
    main()
