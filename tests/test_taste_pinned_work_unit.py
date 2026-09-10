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

PIN_MODULE_PATH = SCRIPTS / 'taste_pinned_work_unit.py'
spec = importlib.util.spec_from_file_location('taste_pinned_work_unit', PIN_MODULE_PATH)
pin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pin)

INGEST_MODULE_PATH = SCRIPTS / 'ingest_taste_results.py'
ingest_spec = importlib.util.spec_from_file_location('ingest_taste_results', INGEST_MODULE_PATH)
ingest = importlib.util.module_from_spec(ingest_spec)
ingest_spec.loader.exec_module(ingest)

EXISTING_BATCH = ROOT / 'data/ai_inbox/taste/manual-throughput-drain-01-batch-001.json'


def projection(profile, model='taste-v3', semantics='s' * 64, source='2026-09-10T00:00:00+00:00'):
    return {
        'status': 'complete',
        'complete_coverage': True,
        'source_mailing_updated_at_utc': source,
        'current_profile': {
            'repository': 'owner/profile-repo',
            'path': 'gaming_taste_live.json',
            'blob_sha': profile,
            'bytes': 123,
        },
        'current_binding': {
            'taste_model_version': model,
            'taste_semantics_sha256': semantics,
        },
    }


def queue(profile_tag='a'):
    rows = []
    for number in range(10):
        rows.append({
            'taste_subject_key': f'App_{number + 1}',
            'appid': str(number + 1),
            'taste_fingerprint': (profile_tag + f'{number:x}')[:1] * 64,
            'candidate_context_sha256': f'{number:x}' * 64,
            'work_required': [
                'evaluate_taste_fit',
                'evaluate_normalized_taste_factors',
                'resolve_grounded_negative_analysis',
            ],
        })
    return rows


def result_document(pinned_profile, rows, model='taste-v3', semantics='s' * 64, source='2026-09-10T00:00:00+00:00'):
    return {
        'schema_version': 1,
        'bindings': {
            'profile_blob_sha': pinned_profile,
            'taste_model_version': model,
            'taste_semantics_sha256': semantics,
            'source_mailing_updated_at_utc': source,
        },
        'results': [{
            'key': row['taste_subject_key'],
            'appid': row['appid'],
            'taste_fingerprint': row['taste_fingerprint'],
            'candidate_context_sha256': row['candidate_context_sha256'],
        } for row in rows],
    }


def git(cwd, *args):
    proc = subprocess.run(['git', *args], cwd=cwd, text=True, capture_output=True, check=True)
    return proc.stdout.strip()


class TastePinnedWorkUnitLifecycleTests(unittest.TestCase):
    def test_profile_a_pin_survives_live_profile_b_before_validation(self):
        rows = queue('a')
        pinned = pin.build_pinned_work_unit(projection('A' * 40), rows, authority_commit='1' * 40)
        doc = result_document('A' * 40, rows)

        live_after_semantics = projection('B' * 40)
        self.assertEqual(live_after_semantics['current_profile']['blob_sha'], 'B' * 40)
        pin.validate_document_against_pin(doc, pinned)
        self.assertEqual(pinned['bindings']['profile_blob_sha'], 'A' * 40)

    def test_new_work_unit_after_live_profile_b_pins_b(self):
        rows = queue('b')
        pinned_b = pin.build_pinned_work_unit(projection('B' * 40), rows, authority_commit='2' * 40)
        self.assertEqual(pinned_b['bindings']['profile_blob_sha'], 'B' * 40)
        self.assertNotEqual(pinned_b['bindings']['profile_blob_sha'], 'A' * 40)

    def test_arbitrary_stale_a_result_cannot_reach_back_into_history(self):
        rows = queue('a')
        stale_a = result_document('A' * 40, rows)
        current_pin_b = pin.build_pinned_work_unit(projection('B' * 40), rows, authority_commit='2' * 40)
        with self.assertRaisesRegex(ValueError, 'pinned profile_blob_sha'):
            pin.validate_document_against_pin(stale_a, current_pin_b)

    def test_order_fingerprint_context_model_and_semantics_mismatches_fail_closed(self):
        rows = queue('a')
        pinned = pin.build_pinned_work_unit(projection('A' * 40), rows)
        base = result_document('A' * 40, rows)

        variants = []
        changed = copy.deepcopy(base)
        changed['results'][0], changed['results'][1] = changed['results'][1], changed['results'][0]
        variants.append(changed)
        changed = copy.deepcopy(base)
        changed['results'][0]['taste_fingerprint'] = 'f' * 64
        variants.append(changed)
        changed = copy.deepcopy(base)
        changed['results'][0]['candidate_context_sha256'] = 'e' * 64
        variants.append(changed)
        changed = copy.deepcopy(base)
        changed['bindings']['taste_model_version'] = 'taste-v-old'
        variants.append(changed)
        changed = copy.deepcopy(base)
        changed['bindings']['taste_semantics_sha256'] = '0' * 64
        variants.append(changed)

        for changed in variants:
            with self.subTest(changed=changed):
                with self.assertRaises(ValueError):
                    pin.validate_document_against_pin(changed, pinned)

    def test_result_count_and_duplicate_guards_remain_strict(self):
        rows = queue('a')
        pinned = pin.build_pinned_work_unit(projection('A' * 40), rows)
        base = result_document('A' * 40, rows)

        too_short = copy.deepcopy(base)
        too_short['results'].pop()
        with self.assertRaisesRegex(ValueError, 'result count'):
            pin.validate_document_against_pin(too_short, pinned)

        duplicate = copy.deepcopy(base)
        duplicate['results'][1] = copy.deepcopy(duplicate['results'][0])
        with self.assertRaisesRegex(ValueError, 'Duplicate ingest key'):
            pin.validate_document_against_pin(duplicate, pinned)

    def test_git_introduction_parent_is_the_authority_even_after_head_advances(self):
        rows = queue('a')
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git(repo, 'init')
            git(repo, 'config', 'user.email', 'test@example.invalid')
            git(repo, 'config', 'user.name', 'Taste Test')
            (repo / 'data/production/pre_ai').mkdir(parents=True)
            (repo / 'data/ai_inbox/taste').mkdir(parents=True)
            projection_path = repo / 'data/production/pre_ai/taste_projection.json'
            queue_path = repo / 'data/production/pre_ai/chatgpt_taste_queue.jsonl'
            input_path = repo / 'data/ai_inbox/taste/batch.json'

            projection_path.write_text(json.dumps(projection('A' * 40)), encoding='utf-8')
            queue_path.write_text('\n'.join(json.dumps(row) for row in rows) + '\n', encoding='utf-8')
            git(repo, 'add', '.')
            git(repo, 'commit', '-m', 'prepare profile A work')
            pre_result_commit = git(repo, 'rev-parse', 'HEAD')

            input_path.write_text(json.dumps(result_document('A' * 40, rows)), encoding='utf-8')
            git(repo, 'add', str(input_path.relative_to(repo)))
            git(repo, 'commit', '-m', 'submit A results')
            result_commit = git(repo, 'rev-parse', 'HEAD')

            projection_path.write_text(json.dumps(projection('B' * 40)), encoding='utf-8')
            git(repo, 'add', str(projection_path.relative_to(repo)))
            git(repo, 'commit', '-m', 'advance live profile to B')

            resolved, _, _ = pin.resolve_pinned_work_unit(input_path, projection_path, queue_path, repo)
            pin.validate_document_against_pin(json.loads(input_path.read_text()), resolved)
            self.assertEqual(resolved['authority_commit'], pre_result_commit)
            self.assertEqual(resolved['result_commit'], result_commit)
            self.assertEqual(resolved['bindings']['profile_blob_sha'], 'A' * 40)

            copied = repo / 'data/ai_inbox/taste/copied-stale.json'
            copied.write_bytes(input_path.read_bytes())
            git(repo, 'add', str(copied.relative_to(repo)))
            git(repo, 'commit', '-m', 'copy stale A result after B')
            copied_pin, _, _ = pin.resolve_pinned_work_unit(copied, projection_path, queue_path, repo)
            self.assertEqual(copied_pin['bindings']['profile_blob_sha'], 'B' * 40)
            with self.assertRaisesRegex(ValueError, 'pinned profile_blob_sha'):
                pin.validate_document_against_pin(json.loads(copied.read_text()), copied_pin)

    def test_existing_v5_package_still_hits_full_ingest_shape_validation(self):
        doc = json.loads(EXISTING_BATCH.read_text(encoding='utf-8'))
        bindings = doc['bindings']
        rows = []
        for result in doc['results']:
            work_required = ['evaluate_taste_fit', 'resolve_grounded_negative_analysis']
            if 'taste_factors' in result:
                work_required.append('evaluate_normalized_taste_factors')
            rows.append({
                'taste_subject_key': result['key'],
                'appid': str(result['appid']),
                'taste_fingerprint': result['taste_fingerprint'],
                'candidate_context_sha256': result['candidate_context_sha256'],
                'work_required': work_required,
            })
        pinned_projection = projection(
            bindings['profile_blob_sha'],
            model=bindings['taste_model_version'],
            semantics=bindings['taste_semantics_sha256'],
            source=bindings['source_mailing_updated_at_utc'],
        )
        pinned = pin.build_pinned_work_unit(pinned_projection, rows)
        queue_by_key = {row['taste_subject_key']: row for row in rows}

        ingest.validate_input(copy.deepcopy(doc), queue_by_key, pinned_projection, {}, pinned)

        missing_v5 = copy.deepcopy(doc)
        missing_v5['results'][0].pop('fit_evidence_state')
        with self.assertRaisesRegex(ValueError, 'Missing result fields'):
            ingest.validate_input(missing_v5, queue_by_key, pinned_projection, {}, pinned)

        duplicated = copy.deepcopy(doc)
        duplicated['results'][1] = copy.deepcopy(duplicated['results'][0])
        with self.assertRaises(ValueError):
            ingest.validate_input(duplicated, queue_by_key, pinned_projection, {}, pinned)


if __name__ == '__main__':
    unittest.main()
