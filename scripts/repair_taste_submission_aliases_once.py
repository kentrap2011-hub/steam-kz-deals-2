import copy
import json
import subprocess
from pathlib import Path

from taste_cache_common import candidate_context_digest

PROJECTION = Path('data/production/pre_ai/taste_projection.json')
QUEUE = Path('data/production/pre_ai/chatgpt_taste_queue.jsonl')
TARGET = Path('data/ai_inbox/taste/2026-08-31T1407Z-001.json')
EXPECTED_KEYS = [
    'App_515570',
    'App_520720',
    'App_526160',
    'App_531510',
    'App_539470',
    'App_539720',
    'App_540840',
    'App_544330',
    'App_545040',
    'App_55230',
]
EXPECTED_EXCLUDE_ALIAS_KEYS = {
    'App_515570',
    'App_520720',
    'App_539720',
    'App_545040',
}
BINDING_FIELDS = (
    'profile_blob_sha',
    'taste_model_version',
    'taste_semantics_sha256',
    'source_mailing_updated_at_utc',
)


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
    before_doc = copy.deepcopy(doc)

    if doc.get('schema_version') != 1:
        raise SystemExit('Unexpected pending checkpoint schema_version')
    if doc.get('bindings') is not None:
        raise SystemExit('Expected the known malformed checkpoint to have no nested bindings object')

    submitted_top_level_bindings = {field: doc.get(field) for field in BINDING_FIELDS}
    if submitted_top_level_bindings != bindings:
        raise SystemExit(
            'Top-level binding values are not exactly the current canonical bindings; repair refused'
        )

    results = doc.get('results')
    if not isinstance(results, list):
        raise SystemExit('Pending checkpoint results must be a list')
    keys = [row.get('key') if isinstance(row, dict) else None for row in results]
    if keys != EXPECTED_KEYS:
        raise SystemExit(f'Pending checkpoint key/order mismatch: {keys!r}')

    serialization_changed_keys = set()
    for result in results:
        key = result['key']
        queue_row = queue_by_key.get(key)
        if queue_row is None:
            raise SystemExit(f'Pending key is not in current queue: {key}')

        if str(result.get('appid')) != str(queue_row.get('appid')):
            raise SystemExit(f'Appid mismatch for {key}')
        if result.get('taste_fingerprint') != queue_row.get('taste_fingerprint'):
            raise SystemExit(f'Taste fingerprint mismatch for {key}; this repair does not alter identity')
        if result.get('candidate_context_sha256') != queue_row.get('candidate_context_sha256'):
            raise SystemExit(f'Candidate context mismatch for {key}')
        if result.get('candidate_context_sha256') != prove_current_queue_context(queue_row):
            raise SystemExit(f'Canonical candidate-context proof failed for {key}')

        semantic_before = {
            field: copy.deepcopy(result.get(field))
            for field in ('verdict', 'positive_evidence', 'negative_evidence', 'taste_factors')
        }

        if key in EXPECTED_EXCLUDE_ALIAS_KEYS:
            if result.get('verdict') != 'EXCLUDE':
                raise SystemExit(f'Expected EXCLUDE for known alias row {key}')
            if result.get('fit_level') != 'weak' or result.get('reason_code') != 'exclude_weak':
                raise SystemExit(
                    f'Unexpected noncanonical exclusion serialization for {key}: '
                    f"fit={result.get('fit_level')!r} reason={result.get('reason_code')!r}"
                )
            result['fit_level'] = 'below_moderate'
            result['reason_code'] = 'exclude_insufficient'
            serialization_changed_keys.add(key)
        else:
            expected_pairs = {
                ('INCLUDE', 'strong', 'include_strong'),
                ('INCLUDE', 'moderate', 'include_moderate'),
            }
            actual = (result.get('verdict'), result.get('fit_level'), result.get('reason_code'))
            if actual not in expected_pairs:
                raise SystemExit(f'Unexpected serialization for non-alias row {key}: {actual!r}')

        semantic_after = {
            field: result.get(field)
            for field in ('verdict', 'positive_evidence', 'negative_evidence', 'taste_factors')
        }
        if semantic_before != semantic_after:
            raise SystemExit(f'Repair attempted to alter verdict/evidence/factors for {key}')

    if serialization_changed_keys != EXPECTED_EXCLUDE_ALIAS_KEYS:
        raise SystemExit(
            f'Expected exactly alias keys {sorted(EXPECTED_EXCLUDE_ALIAS_KEYS)}, '
            f'got {sorted(serialization_changed_keys)}'
        )

    doc['bindings'] = bindings
    for field in BINDING_FIELDS:
        doc.pop(field, None)

    # Prove that the only envelope change is moving the exact four binding values into
    # `bindings`, and the only result changes are the four explicit serialization aliases.
    before_results = {row['key']: row for row in before_doc['results']}
    after_results = {row['key']: row for row in doc['results']}
    for key in EXPECTED_KEYS:
        before = before_results[key]
        after = after_results[key]
        for field in before:
            if field in {'fit_level', 'reason_code'} and key in EXPECTED_EXCLUDE_ALIAS_KEYS:
                continue
            if before.get(field) != after.get(field):
                raise SystemExit(f'Unexpected changed field {field!r} for {key}')

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
        'scope': 'known_envelope_and_serialization_aliases_only',
        'file': TARGET.name,
        'result_count': len(results),
        'bindings_moved_into_nested_object': True,
        'serialization_changed_keys': sorted(serialization_changed_keys),
        'identity_unchanged_and_current_queue_proven': True,
        'verdict_evidence_factors_unchanged': True,
        'canonical_dry_run': True,
    }, ensure_ascii=False, indent=2))
    print('TASTE_ALIAS_REPAIR=PASS')


if __name__ == '__main__':
    main()
