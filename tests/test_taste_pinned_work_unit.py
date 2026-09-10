import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / 'scripts'
sys.path.insert(0, str(SCRIPTS))

spec = importlib.util.spec_from_file_location('taste_pinned_work_unit', SCRIPTS / 'taste_pinned_work_unit.py')
pin = importlib.util.module_from_spec(spec); spec.loader.exec_module(pin)
ingest_spec = importlib.util.spec_from_file_location('ingest_taste_results', SCRIPTS / 'ingest_taste_results.py')
ingest = importlib.util.module_from_spec(ingest_spec); ingest_spec.loader.exec_module(ingest)
EXISTING_BATCH = ROOT / pin.LEGACY_RESULT_PATH


def projection(profile, model='taste-v3', semantics='s' * 64, source='2026-09-10T00:00:00+00:00'):
    return {
        'status': 'complete', 'complete_coverage': True, 'source_mailing_updated_at_utc': source,
        'current_profile': {'repository': 'owner/profile-repo', 'path': 'gaming_taste_live.json', 'blob_sha': profile, 'bytes': 100},
        'current_binding': {'taste_model_version': model, 'taste_semantics_sha256': semantics},
    }


def frozen(profile, tag):
    return {
        'repository': 'owner/profile-repo', 'path': 'gaming_taste_live.json',
        'resolved_commit_sha': tag * 40, 'blob_sha': profile, 'content_sha256': tag * 64, 'bytes': 100,
    }


def queue(tag='1'):
    return [{
        'taste_subject_key': f'App_{i+1}', 'appid': str(i+1),
        'taste_fingerprint': f'{(i+1)%10}' * 64,
        'candidate_context_sha256': tag * 64,
        'work_required': ['evaluate_taste_fit', 'evaluate_normalized_taste_factors', 'resolve_grounded_negative_analysis'],
    } for i in range(10)]


def result_doc(profile, rows, pin_doc, pin_commit, model='taste-v3', semantics='s' * 64, source='2026-09-10T00:00:00+00:00'):
    return {
        'schema_version': 1,
        'bindings': {
            'profile_blob_sha': profile, 'taste_model_version': model,
            'taste_semantics_sha256': semantics, 'source_mailing_updated_at_utc': source,
            'pinned_work_unit_sha256': pin_doc['ordered_work_unit_sha256'], 'pin_authority_commit': pin_commit,
        },
        'results': [{
            'key': r['taste_subject_key'], 'appid': r['appid'], 'taste_fingerprint': r['taste_fingerprint'],
            'candidate_context_sha256': r['candidate_context_sha256'],
        } for r in rows],
    }


def git(cwd, *args):
    return subprocess.run(['git', *args], cwd=cwd, text=True, capture_output=True, check=True).stdout.strip()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(value) + '\n', encoding='utf-8')


class TastePinnedWorkUnitLifecycleTests(unittest.TestCase):
    def test_a_pin_survives_live_b_and_new_work_after_retirement_uses_b(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp); git(repo, 'init'); git(repo, 'config', 'user.email', 't@example.invalid'); git(repo, 'config', 'user.name', 'Taste Test')
            proj = repo / 'data/production/pre_ai/taste_projection.json'; q = repo / 'data/production/pre_ai/chatgpt_taste_queue.jsonl'
            active = repo / pin.ACTIVE_PIN; inbox = repo / 'data/ai_inbox/taste/batch-a.json'
            rows_a = queue('a'); write_json(proj, projection('A' * 40)); q.parent.mkdir(parents=True, exist_ok=True); q.write_text('\n'.join(json.dumps(x) for x in rows_a) + '\n')
            pin_a = pin.build_pinned_work_unit(projection('A' * 40), rows_a, frozen('A' * 40, 'a'), prepared_at_utc='2026-09-10T00:00:00+00:00')
            write_json(active, pin_a); git(repo, 'add', '.'); git(repo, 'commit', '-m', 'pin A before semantics'); a_commit = git(repo, 'rev-parse', 'HEAD')

            write_json(proj, projection('B' * 40)); git(repo, 'add', str(proj.relative_to(repo))); git(repo, 'commit', '-m', 'live advances to B')
            write_json(inbox, result_doc('A' * 40, rows_a, pin_a, a_commit)); git(repo, 'add', str(inbox.relative_to(repo))); git(repo, 'commit', '-m', 'A semantic result')
            resolved_a, _, resolved_rows_a = pin.resolve_pinned_work_unit(inbox, proj, q, active, repo)
            self.assertEqual(resolved_a['bindings']['profile_blob_sha'], 'A' * 40)
            self.assertEqual(len(resolved_rows_a), 10)

            active.unlink(); rows_b = queue('b'); q.write_text('\n'.join(json.dumps(x) for x in rows_b) + '\n'); write_json(proj, projection('B' * 40))
            git(repo, 'add', '-A'); git(repo, 'commit', '-m', 'retire A')
            pin_b = pin.build_pinned_work_unit(projection('B' * 40), rows_b, frozen('B' * 40, 'b'), prepared_at_utc='2026-09-10T01:00:00+00:00')
            write_json(active, pin_b); git(repo, 'add', '.'); git(repo, 'commit', '-m', 'pin B next work'); b_commit = git(repo, 'rev-parse', 'HEAD')
            self.assertEqual(pin_b['bindings']['profile_blob_sha'], 'B' * 40)
            self.assertNotEqual(pin_a['ordered_work_unit_sha256'], pin_b['ordered_work_unit_sha256'])

            stale = repo / 'data/ai_inbox/taste/copied-old-a.json'; write_json(stale, result_doc('A' * 40, rows_a, pin_a, a_commit)); git(repo, 'add', str(stale.relative_to(repo))); git(repo, 'commit', '-m', 'arbitrary stale A')
            with self.assertRaises(ValueError):
                pin.resolve_pinned_work_unit(stale, proj, q, active, repo)

            fresh_b = repo / 'data/ai_inbox/taste/batch-b.json'; write_json(fresh_b, result_doc('B' * 40, rows_b, pin_b, b_commit)); git(repo, 'add', str(fresh_b.relative_to(repo))); git(repo, 'commit', '-m', 'B semantic result')
            resolved_b, _, _ = pin.resolve_pinned_work_unit(fresh_b, proj, q, active, repo)
            self.assertEqual(resolved_b['bindings']['profile_blob_sha'], 'B' * 40)

    def test_pin_hash_commit_order_fingerprint_context_model_semantics_and_count_fail_closed(self):
        rows = queue('a'); p = pin.build_pinned_work_unit(projection('A' * 40), rows, frozen('A' * 40, 'a'), prepared_at_utc='2026-09-10T00:00:00+00:00'); commit = '1' * 40
        base = result_doc('A' * 40, rows, p, commit)
        pin.validate_document_against_pin(base, p, authority_commit=commit)
        variants = []
        x = copy.deepcopy(base); x['bindings']['pinned_work_unit_sha256'] = '0' * 64; variants.append(x)
        x = copy.deepcopy(base); x['bindings']['pin_authority_commit'] = '2' * 40; variants.append(x)
        x = copy.deepcopy(base); x['results'][0], x['results'][1] = x['results'][1], x['results'][0]; variants.append(x)
        x = copy.deepcopy(base); x['results'][0]['taste_fingerprint'] = 'f' * 64; variants.append(x)
        x = copy.deepcopy(base); x['results'][0]['candidate_context_sha256'] = 'e' * 64; variants.append(x)
        x = copy.deepcopy(base); x['bindings']['taste_model_version'] = 'old'; variants.append(x)
        x = copy.deepcopy(base); x['bindings']['taste_semantics_sha256'] = '0' * 64; variants.append(x)
        x = copy.deepcopy(base); x['results'].pop(); variants.append(x)
        x = copy.deepcopy(base); x['results'][1] = copy.deepcopy(x['results'][0]); variants.append(x)
        for x in variants:
            with self.subTest(case=x):
                with self.assertRaises(ValueError): pin.validate_document_against_pin(x, p, authority_commit=commit)

    def test_active_pin_requires_full_immutable_profile_identity(self):
        rows = queue('a'); bad = frozen('A' * 40, 'a'); bad.pop('content_sha256')
        with self.assertRaisesRegex(ValueError, 'immutable profile identity'):
            pin.build_pinned_work_unit(projection('A' * 40), rows, bad)

    def test_existing_10_package_is_exactly_grandfatherable_and_v5_stays_strict(self):
        doc = json.loads(EXISTING_BATCH.read_text(encoding='utf-8'))
        resolved, pinned_projection, pinned_rows = pin.resolve_pinned_work_unit(EXISTING_BATCH, pin.DEFAULT_PROJECTION, pin.DEFAULT_QUEUE, pin.ACTIVE_PIN, ROOT)
        self.assertTrue(resolved['grandfathered_legacy_package'])
        self.assertEqual(resolved['authority_commit'], pin.LEGACY_PIN_COMMIT)
        self.assertEqual(resolved['result_commit'], pin.LEGACY_RESULT_COMMIT)
        self.assertEqual(resolved['bindings']['profile_blob_sha'], 'b487e62b3fec9f413fb001d96b4894f8ac43e5d5')
        queue_by_key = {r['taste_subject_key']: r for r in pinned_rows}
        ingest.validate_input(copy.deepcopy(doc), queue_by_key, pinned_projection, {}, resolved)
        missing = copy.deepcopy(doc); missing['results'][0].pop('fit_evidence_state')
        with self.assertRaisesRegex(ValueError, 'Missing result fields'):
            ingest.validate_input(missing, queue_by_key, pinned_projection, {}, resolved)
        duplicate = copy.deepcopy(doc); duplicate['results'][1] = copy.deepcopy(duplicate['results'][0])
        with self.assertRaises(ValueError): ingest.validate_input(duplicate, queue_by_key, pinned_projection, {}, resolved)


if __name__ == '__main__':
    unittest.main()
