import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import progressive_pass1
import progressive_work_authority
import taste_pinned_work_unit


def git_blob(raw):
    return hashlib.sha1(f'blob {len(raw)}\0'.encode('ascii') + raw).hexdigest()


def projection(identity):
    return {
        'status': 'complete',
        'current_profile': {
            'repository': identity['repository'],
            'path': identity['path'],
            'raw_url': identity['immutable_raw_url'],
            'resolved_commit_sha': identity['resolved_commit_sha'],
            'blob_sha': identity['blob_sha'],
            'content_sha256': identity['content_sha256'],
            'bytes': identity['bytes'],
        },
        'current_binding': {
            'taste_model_version': 'taste-v3',
            'taste_semantics_sha256': 's' * 64,
            'candidate_context_contract_blob_sha': 'c' * 40,
        },
    }


def content(raw):
    return {
        'type': 'file',
        'sha': git_blob(raw),
        'encoding': 'base64',
        'content': base64.b64encode(raw).decode('ascii'),
    }


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False) + '\n', encoding='utf-8')


def git(repo, *args):
    return subprocess.run(
        ['git', *args], cwd=repo, text=True, capture_output=True, check=True
    ).stdout.strip()


def main():
    raw_a = json.dumps({
        'durable_preferences': {
            'likes': ['active mastery', 'purposeful progression'],
            'dislikes': ['passive drift'],
        }
    }, ensure_ascii=False).encode('utf-8')
    raw_b = json.dumps({
        'durable_preferences': {
            'likes': ['active mastery', 'purposeful progression', 'tactical identity'],
            'dislikes': ['passive drift'],
        }
    }, ensure_ascii=False).encode('utf-8')
    commit_a = 'a' * 40
    commit_b = 'b' * 40
    repo_name = progressive_pass1.CANONICAL_PROFILE_REPOSITORY
    profile_path = progressive_pass1.CANONICAL_PROFILE_PATH

    heads = iter([commit_a, commit_b, commit_b, commit_b])
    def changing_fetch(url):
        if '/contents/' in url:
            return content(raw_a if f'ref={commit_a}' in url else raw_b)
        return {'sha': next(heads)}

    frozen_b = taste_pinned_work_unit.freeze_current_live_profile(
        repo_name, profile_path, fetch_json=changing_fetch, max_attempts=3
    )
    assert frozen_b['resolved_commit_sha'] == commit_b
    assert frozen_b['blob_sha'] == git_blob(raw_b)
    assert frozen_b['content_sha256'] == hashlib.sha256(raw_b).hexdigest()

    pin_b = progressive_pass1.profile_pin_from_projection(projection(frozen_b))
    assert pin_b['immutable_raw_url'].endswith(f'/{commit_b}/{profile_path}')
    parsed = progressive_pass1.verify_profile_content(pin_b, raw_b)
    assert parsed['durable_preferences']['likes'][0] == 'active mastery'
    try:
        progressive_pass1.verify_profile_content(pin_b, raw_a)
    except ValueError:
        pass
    else:
        raise AssertionError('wrong pinned profile bytes must fail closed')

    churn = iter(['1' * 40, '2' * 40, '3' * 40, '4' * 40, '5' * 40, '6' * 40])
    def churn_fetch(url):
        if '/contents/' in url:
            return content(raw_a)
        return {'sha': next(churn)}
    try:
        taste_pinned_work_unit.freeze_current_live_profile(
            repo_name, profile_path, fetch_json=churn_fetch, max_attempts=3
        )
    except ValueError as exc:
        assert 'bounded pin freeze attempts' in str(exc)
    else:
        raise AssertionError('continuous profile churn must fail closed after bounded attempts')

    frozen_a = {
        'repository': repo_name,
        'path': profile_path,
        'resolved_commit_sha': commit_a,
        'blob_sha': git_blob(raw_a),
        'content_sha256': hashlib.sha256(raw_a).hexdigest(),
        'bytes': len(raw_a),
        'immutable_raw_url': f'https://raw.githubusercontent.com/{repo_name}/{commit_a}/{profile_path}',
    }
    gen_a = progressive_pass1.semantic_generation(projection(frozen_a))
    gen_b = progressive_pass1.semantic_generation(projection(frozen_b))
    assert gen_a['profile_pin']['pin_sha256'] != gen_b['profile_pin']['pin_sha256']
    assert gen_a['semantic_generation_id'] != gen_b['semantic_generation_id']

    def exact_a_fetch(url):
        assert f'ref={commit_a}' in url
        return content(raw_a)
    resolved_a = taste_pinned_work_unit.freeze_profile_identity_for_projection(
        projection(frozen_a), fetch_json=exact_a_fetch
    )
    assert resolved_a['resolved_commit_sha'] == commit_a

    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        git(repo, 'init', '-q')
        git(repo, 'config', 'user.name', 'test')
        git(repo, 'config', 'user.email', 'test@example.invalid')
        manifest = repo / 'data/production/pre_ai/progressive_pass1_work.json'
        result_a = repo / 'data/ai_inbox/progressive_pass1/a.json'
        result_c = repo / 'data/ai_inbox/progressive_pass1/c.json'
        item_a = {
            'profile_pin_sha256': gen_a['profile_pin']['pin_sha256'],
            'work_id': 'work-a',
            'submission_path': 'data/ai_inbox/progressive_pass1/a.json',
        }
        write(manifest, {
            'contract': 'PROGRESSIVE-PASS1-WORK-V1',
            'profile_pin': gen_a['profile_pin'],
            'items': [item_a],
        })
        git(repo, 'add', '.'); git(repo, 'commit', '-qm', 'durably prepare A')
        write(manifest, {
            'contract': 'PROGRESSIVE-PASS1-WORK-V1',
            'profile_pin': gen_b['profile_pin'],
            'items': [{
                'profile_pin_sha256': gen_b['profile_pin']['pin_sha256'],
                'work_id': 'work-b',
                'submission_path': 'data/ai_inbox/progressive_pass1/b.json',
            }],
        })
        git(repo, 'add', '.'); git(repo, 'commit', '-qm', 'advance current work to B')
        write(result_a, {'work_id': 'work-a'})
        git(repo, 'add', '.'); git(repo, 'commit', '-qm', 'A finishes in flight')
        resolved = progressive_work_authority.resolve_presemantic_work_item(
            result_a,
            manifest,
            path_field='submission_path',
            expected_contract='PROGRESSIVE-PASS1-WORK-V1',
            repo_root=repo,
        )
        assert resolved['work_id'] == 'work-a'
        assert resolved['_profile_pin']['pin_sha256'] == gen_a['profile_pin']['pin_sha256']

        write(result_c, {'work_id': 'work-c'})
        git(repo, 'add', '.'); git(repo, 'commit', '-qm', 'arbitrary unpinned C')
        try:
            progressive_work_authority.resolve_presemantic_work_item(
                result_c,
                manifest,
                path_field='submission_path',
                expected_contract='PROGRESSIVE-PASS1-WORK-V1',
                repo_root=repo,
            )
        except ValueError:
            pass
        else:
            raise AssertionError('arbitrary unpinned historical result must fail closed')

    print('progressive pinned live-profile handoff regression: ok')


if __name__ == '__main__':
    main()
