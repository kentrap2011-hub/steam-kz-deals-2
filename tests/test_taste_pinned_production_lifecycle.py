import base64
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS))

import process_taste_inbox as process
import taste_pinned_work_unit as pin


def projection(profile_blob, rows, *, safe_hits=0, ai_required=None):
    if ai_required is None:
        ai_required = len(rows)
    return {
        'status': 'complete',
        'complete_coverage': True,
        'source_mailing_updated_at_utc': '2026-09-10T00:00:00+00:00',
        'current_profile': {
            'repository': 'owner/profile-repo',
            'path': 'gaming_taste_live.json',
            'blob_sha': profile_blob,
            'bytes': 100,
        },
        'current_binding': {
            'taste_model_version': 'taste-v3',
            'taste_semantics_sha256': 's' * 64,
        },
        'safe_cache_hit_count': safe_hits,
        'ai_required_count': ai_required,
        'entries': {
            row['taste_subject_key']: {
                'status': 'ai_required',
                'appid': row['appid'],
                'taste_fingerprint': row['taste_fingerprint'],
                'candidate_context_sha256': row['candidate_context_sha256'],
            }
            for row in rows
        },
    }


def profile_binding(profile_blob, tag):
    return {
        'repository': 'owner/profile-repo',
        'path': 'gaming_taste_live.json',
        'resolved_commit_sha': tag * 40,
        'blob_sha': profile_blob,
        'content_sha256': tag * 64,
        'bytes': 100,
    }


def queue(tag='1', count=2):
    return [
        {
            'taste_subject_key': f'App_{i + 1}',
            'appid': str(i + 1),
            'taste_fingerprint': str(i + 1) * 64,
            'candidate_context_sha256': tag * 64,
            'work_required': [
                'evaluate_taste_fit',
                'evaluate_normalized_taste_factors',
                'resolve_grounded_negative_analysis',
            ],
        }
        for i in range(count)
    ]


def result_doc(profile_blob, rows, pin_doc, pin_commit):
    return {
        'schema_version': 1,
        'bindings': {
            'profile_blob_sha': profile_blob,
            'taste_model_version': 'taste-v3',
            'taste_semantics_sha256': 's' * 64,
            'source_mailing_updated_at_utc': '2026-09-10T00:00:00+00:00',
            'pinned_work_unit_sha256': pin_doc['ordered_work_unit_sha256'],
            'pin_authority_commit': pin_commit,
        },
        'results': [
            {
                'key': row['taste_subject_key'],
                'appid': row['appid'],
                'taste_fingerprint': row['taste_fingerprint'],
                'candidate_context_sha256': row['candidate_context_sha256'],
            }
            for row in rows
        ],
    }


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + '\n', encoding='utf-8')


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(json.dumps(row) for row in rows) + '\n', encoding='utf-8')


def git(cwd, *args):
    return subprocess.run(
        ['git', *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def manifest(queue_count):
    return {
        'source_family_count': queue_count,
        'sale_end_coverage': 1.0,
        'sale_end_missing_count': 0,
        'sale_end_missing_primary_keys': [],
        'complete_family_partition': True,
        'ai_queue_count': queue_count,
        'deterministically_excluded_primary_keys': [],
        'contract': {
            'missing_sale_end_does_not_exclude_candidate': True,
        },
    }


class TastePinnedProductionLifecycleTests(unittest.TestCase):
    def test_freeze_profile_identity_is_exact_and_mixed_projection_fails_closed(self):
        raw = b'{"profile":"A"}\n'
        blob = hashlib.sha1(f'blob {len(raw)}\0'.encode('ascii') + raw).hexdigest()
        commit = 'a' * 40
        contents = {
            'type': 'file',
            'sha': blob,
            'encoding': 'base64',
            'content': base64.b64encode(raw).decode('ascii'),
        }
        calls = []

        def fake_fetch(url):
            calls.append(url)
            if '/contents/' in url:
                return contents
            return {'sha': commit}

        prepared = projection(blob, queue(), ai_required=2)
        prepared['current_profile']['bytes'] = len(raw)
        frozen = pin.freeze_profile_identity_for_projection(prepared, fetch_json=fake_fetch)
        self.assertEqual(frozen['resolved_commit_sha'], commit)
        self.assertEqual(frozen['blob_sha'], blob)
        self.assertEqual(frozen['content_sha256'], hashlib.sha256(raw).hexdigest())
        self.assertEqual(len(calls), 3)

        mixed = json.loads(json.dumps(prepared))
        mixed['current_profile']['blob_sha'] = 'b' * 40
        with self.assertRaisesRegex(ValueError, 'mixed profile/work-unit tuple'):
            pin.freeze_profile_identity_for_projection(mixed, fetch_json=fake_fetch)

    def test_production_lifecycle_a_to_b_retains_b_work_and_rejects_stale_a(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git(repo, 'init')
            git(repo, 'config', 'user.email', 'taste@example.invalid')
            git(repo, 'config', 'user.name', 'Taste Lifecycle Test')

            proj = repo / pin.DEFAULT_PROJECTION
            q = repo / pin.DEFAULT_QUEUE
            active = repo / pin.ACTIVE_PIN
            binding_a_path = repo / 'binding-a.json'
            binding_b_path = repo / 'binding-b.json'
            rows = queue('c', count=2)
            profile_a = 'A' * 40
            profile_b = 'B' * 40

            write_json(proj, projection(profile_a, rows, ai_required=2))
            write_jsonl(q, rows)
            write_json(binding_a_path, profile_binding(profile_a, 'a'))
            write_json(binding_b_path, profile_binding(profile_b, 'b'))

            prepared_a = pin.ensure_active_pin(proj, q, binding_a_path, active)
            self.assertEqual(prepared_a['status'], 'prepared_new_active_pin')
            pin_a = prepared_a['pin']
            git(repo, 'add', '.')
            git(repo, 'commit', '-m', 'durably pin A before semantics')
            pin_a_commit = git(repo, 'rev-parse', 'HEAD')

            # Live/projection advances to B while A remains the active authority.
            projection_b = projection(profile_b, rows, ai_required=2)
            write_json(proj, projection_b)
            preserved = pin.ensure_active_pin(proj, q, binding_b_path, active)
            self.assertEqual(preserved['status'], 'preserved_existing_active_pin')
            self.assertEqual(preserved['pin']['bindings']['profile_blob_sha'], profile_a)
            git(repo, 'add', str(proj.relative_to(repo)))
            git(repo, 'commit', '-m', 'live projection advances to B')

            result_a_path = repo / 'data/ai_inbox/taste/batch-a.json'
            doc_a = result_doc(profile_a, rows, pin_a, pin_a_commit)
            write_json(result_a_path, doc_a)
            git(repo, 'add', str(result_a_path.relative_to(repo)))
            git(repo, 'commit', '-m', 'A result arrives after B is live')

            resolved_a, _pinned_projection, _pinned_rows = pin.resolve_pinned_work_unit(
                result_a_path,
                proj,
                q,
                active,
                repo,
            )
            self.assertEqual(resolved_a['bindings']['profile_blob_sha'], profile_a)

            baseline_projection = projection(profile_b, rows, safe_hits=5, ai_required=2)
            after_projection = json.loads(json.dumps(baseline_projection))
            current_reusable = {
                result['key']: process.result_is_reusable_for_current_projection(
                    result,
                    resolved_a,
                    baseline_projection,
                    rows[index],
                )
                for index, result in enumerate(doc_a['results'])
            }
            self.assertEqual(current_reusable, {'App_1': False, 'App_2': False})

            checks, retained, mismatches, expected_queue, full_eval_count = process.build_transactional_proof_checks(
                all_keys=['App_1', 'App_2'],
                result_by_key={row['key']: row for row in doc_a['results']},
                baseline_queue_by_key={row['taste_subject_key']: row for row in rows},
                baseline_safe_hits=5,
                baseline_ai_required=2,
                baseline_ai_queue=2,
                baseline_projection=baseline_projection,
                current_reusable_by_key=current_reusable,
                after_projection=after_projection,
                after_manifest=manifest(2),
                after_queue=rows,
            )
            self.assertTrue(all(checks.values()), checks)
            self.assertEqual(full_eval_count, 2)
            self.assertEqual(expected_queue, 2)
            self.assertEqual(mismatches, {})
            self.assertEqual(set(retained), {'App_1', 'App_2'})
            self.assertEqual(after_projection['safe_cache_hit_count'], 5)
            self.assertEqual(after_projection['ai_required_count'], 2)
            self.assertTrue(checks['older_pinned_result_does_not_become_current_live_cache_hit'])
            self.assertTrue(checks['newer_live_work_remains_exact_for_next_work_unit'])

            # Only after the transactional proof succeeds is A retired and B pinned.
            transition = pin.transition_active_pin_after_success(
                resolved_a,
                proj,
                q,
                binding_b_path,
                active,
            )
            self.assertEqual(transition['status'], 'retired_and_prepared_next_active_pin')
            pin_b = transition['next_pin']
            self.assertEqual(pin_b['bindings']['profile_blob_sha'], profile_b)
            self.assertNotEqual(pin_a['ordered_work_unit_sha256'], pin_b['ordered_work_unit_sha256'])
            git(repo, 'add', '-A')
            git(repo, 'commit', '-m', 'retire A and durably pin B')
            pin_b_commit = git(repo, 'rev-parse', 'HEAD')

            result_b_path = repo / 'data/ai_inbox/taste/batch-b.json'
            write_json(result_b_path, result_doc(profile_b, rows, pin_b, pin_b_commit))
            git(repo, 'add', str(result_b_path.relative_to(repo)))
            git(repo, 'commit', '-m', 'fresh B result')
            resolved_b, _, _ = pin.resolve_pinned_work_unit(result_b_path, proj, q, active, repo)
            self.assertEqual(resolved_b['bindings']['profile_blob_sha'], profile_b)

            stale_a_path = repo / 'data/ai_inbox/taste/copied-old-a.json'
            write_json(stale_a_path, doc_a)
            git(repo, 'add', str(stale_a_path.relative_to(repo)))
            git(repo, 'commit', '-m', 'arbitrary stale A copy')
            with self.assertRaises(ValueError):
                pin.resolve_pinned_work_unit(stale_a_path, proj, q, active, repo)

    def test_production_workflows_wire_pin_before_semantics_and_commit_retirement(self):
        pre_ai = (ROOT / '.github/workflows/build-pre-ai-store-snapshot.yml').read_text(encoding='utf-8')
        ingest = (ROOT / '.github/workflows/ingest-taste-batch.yml').read_text(encoding='utf-8')
        build_marker = '- name: Build split ChatGPT consumer bundle'
        pin_marker = '- name: Persist or preserve pre-semantic Taste active pin'
        self.assertIn('python scripts/taste_pinned_work_unit.py ensure', pre_ai)
        self.assertIn('data/production/pre_ai/taste_active_work_unit.json', pre_ai)
        self.assertLess(pre_ai.index(build_marker), pre_ai.index(pin_marker))
        self.assertIn('python scripts/process_taste_inbox.py', ingest)
        self.assertIn('data/production/pre_ai/taste_active_work_unit.json', ingest)


if __name__ == '__main__':
    unittest.main()
