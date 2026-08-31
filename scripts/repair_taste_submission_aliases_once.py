import copy
import json
import subprocess
from pathlib import Path

from taste_cache_common import candidate_context_digest

PROJECTION = Path('data/production/pre_ai/taste_projection.json')
QUEUE = Path('data/production/pre_ai/chatgpt_taste_queue.jsonl')
TARGET = Path('data/ai_inbox/taste/2026-08-31T1250Z-005.json')
EXPECTED_RESULTS = 20
EXPECTED_REPAIR_KEY = 'App_461620'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def read_jsonl(path):
    return [
        json.loads(line)
        for line in path.read_text(encoding='utf-8').splitlines()
        if line.strip()
    ]


def expected_bindings(projection):
    return {
        'profile_blob_sha': projection['current_profile']['blob_sha'],
        'taste_model_version': projection['current_binding']['taste_model_version'],
        'taste_semantics_sha256': projection['current_binding']['taste_semantics_sha256'],
        'source_mailing_updated_at_utc': projection['source_mailing_updated_at_utc'],
    }


def prove_current_queue_context(queue_row):
    expected_context, _payload = candidate_context_digest(
        queue_row['taste_fingerprint'],
        queue_row.get('short_description'),
        queue_row.get('bundle_members') or [],
    )
    if expected_context != queue_row.get('candidate_context_sha256'):
        raise SystemExit(
            'Current queue candidate context is internally inconsistent for '
            f"{queue_row.get('taste_subject_key')}"
        )
    return expected_context


def main():
    projection = load(PROJECTION)
    if projection.get('status') != 'complete' or projection.get('complete_coverage') is not True:
        raise SystemExit('Current taste projection is not complete')
    bindings = expected_bindings(projection)

    queue = read_jsonl(QUEUE)
    queue_by_key = {row['taste_subject_key']: row for row in queue}
    if len(queue_by_key) != len(queue):
        raise SystemExit('Current taste queue contains duplicate taste_subject_key values')

    if not TARGET.exists():
        raise SystemExit(f'Missing expected pending checkpoint: {TARGET}')
    doc = load(TARGET)
    if doc.get('schema_version') != 1:
        raise SystemExit('Unexpected pending checkpoint schema_version')
    if doc.get('bindings') != bindings:
        raise SystemExit('Pending checkpoint bindings are no longer current; repair refused')

    results = doc.get('results')
    if not isinstance(results, list) or len(results) != EXPECTED_RESULTS:
        raise SystemExit(
            f'Expected exactly {EXPECTED_RESULTS} pending results, '
            f'got {len(results) if isinstance(results, list) else None}'
        )

    changed = []
    for result in results:
        if not isinstance(result, dict):
            raise SystemExit('Pending checkpoint contains a non-object result')
        key = result.get('key')
        queue_row = queue_by_key.get(key)
        if queue_row is None:
            raise SystemExit(f'Pending key is not in current queue: {key}')

        semantic_before = {
            field: copy.deepcopy(result.get(field))
            for field in ('verdict', 'fit_level', 'reason_code', 'positive_evidence', 'negative_evidence', 'taste_factors')
        }

        submitted_fp = result.get('taste_fingerprint')
        current_fp = queue_row.get('taste_fingerprint')
        if submitted_fp != current_fp:
            if key != EXPECTED_REPAIR_KEY:
                raise SystemExit(
                    f'Unexpected fingerprint mismatch for {key}; one-shot repair only authorizes '
                    f'{EXPECTED_REPAIR_KEY}'
                )
            if str(result.get('appid')) != str(queue_row.get('appid')):
                raise SystemExit(f'Appid mismatch cannot be repaired for {key}')
            input_context = result.get('candidate_context_sha256')
            current_context = queue_row.get('candidate_context_sha256')
            if input_context != current_context:
                raise SystemExit(f'Candidate context mismatch cannot be repaired for {key}')
            proven_context = prove_current_queue_context(queue_row)
            if input_context != proven_context:
                raise SystemExit(f'Canonical context proof failed for {key}')

            result['taste_fingerprint'] = current_fp
            changed.append({
                'key': key,
                'input_taste_fingerprint': submitted_fp,
                'canonical_taste_fingerprint': current_fp,
                'candidate_context_sha256': input_context,
            })

        semantic_after = {
            field: result.get(field)
            for field in ('verdict', 'fit_level', 'reason_code', 'positive_evidence', 'negative_evidence', 'taste_factors')
        }
        if semantic_before != semantic_after:
            raise SystemExit(f'Repair attempted to alter semantic content for {key}')

    if len(changed) != 1 or changed[0]['key'] != EXPECTED_REPAIR_KEY:
        raise SystemExit(
            f'Expected exactly one proven repair for {EXPECTED_REPAIR_KEY}; got {changed!r}'
        )

    TARGET.write_text(
        json.dumps(doc, ensure_ascii=False, separators=(',', ':')) + '\n',
        encoding='utf-8',
    )

    subprocess.run(
        ['python', 'scripts/ingest_taste_results.py', '--input', str(TARGET), '--dry-run'],
        check=True,
    )

    print(json.dumps({
        'status': 'validated',
        'scope': 'single_proven_identity_copy_error_only',
        'file': TARGET.name,
        'result_count': len(results),
        'repairs': changed,
        'bindings_unchanged': True,
        'semantic_content_unchanged': True,
        'canonical_dry_run': True,
    }, ensure_ascii=False, indent=2))
    print('TASTE_ALIAS_REPAIR=PASS')


if __name__ == '__main__':
    main()
