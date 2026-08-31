import copy
import json
import subprocess
from pathlib import Path

from taste_cache_common import candidate_context_digest

PROJECTION = Path('data/production/pre_ai/taste_projection.json')
QUEUE = Path('data/production/pre_ai/chatgpt_taste_queue.jsonl')
LEDGER_CONTRACT = Path('config/taste_ledger_contract.json')
TARGETS = [
    Path('data/ai_inbox/taste/2026-08-31T0955Z-001.json'),
    Path('data/ai_inbox/taste/2026-08-31T1006Z-002.json'),
    Path('data/ai_inbox/taste/2026-08-31T1020Z-003.json'),
    Path('data/ai_inbox/taste/2026-08-31T1034Z-004.json'),
]
EXPECTED_RESULTS_PER_FILE = 100
EXPECTED_TOTAL_RESULTS = 400

REASON_ALIASES = {
    'include_strong_fit': 'include_strong',
    'include_moderate_fit': 'include_moderate',
    'exclude_insufficient_fit': 'exclude_insufficient',
}


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


def normalize_serialization(result, reason_semantics):
    before = copy.deepcopy(result)
    reason = result.get('reason_code')
    canonical_reason = REASON_ALIASES.get(reason, reason)
    if canonical_reason not in reason_semantics:
        raise SystemExit(
            f"Unexpected reason_code for {result.get('key')}: {reason!r}; "
            'one-shot repair refuses to invent a mapping'
        )

    spec = reason_semantics[canonical_reason]
    verdict = result.get('verdict')
    if verdict != spec.get('decision'):
        raise SystemExit(
            f"Verdict/reason mismatch for {result.get('key')}: "
            f"verdict={verdict!r} canonical_reason={canonical_reason!r}"
        )

    required_fit = spec.get('required_fit_level')
    current_fit = result.get('fit_level')
    allowed_alias_fit = (
        canonical_reason in {'exclude_insufficient', 'exclude_audited_below', 'exclude_direct_conflict'}
        and current_fit == 'weak'
        and required_fit == 'below_moderate'
    )
    if current_fit != required_fit and not allowed_alias_fit:
        raise SystemExit(
            f"Unexpected fit_level for {result.get('key')}: "
            f"fit={current_fit!r} canonical_required={required_fit!r}"
        )

    result['reason_code'] = canonical_reason
    result['fit_level'] = required_fit

    for field, value in before.items():
        if field in {'reason_code', 'fit_level'}:
            continue
        if result.get(field) != value:
            raise SystemExit(
                f"Serialization repair attempted to alter semantic field {field!r} "
                f"for {result.get('key')}"
            )
    return before != result


def prove_current_queue_context(queue_row):
    expected_context, _payload = candidate_context_digest(
        queue_row['taste_fingerprint'],
        queue_row.get('short_description'),
        queue_row.get('bundle_members') or [],
    )
    if expected_context != queue_row.get('candidate_context_sha256'):
        raise SystemExit(
            f"Current queue candidate context is internally inconsistent for "
            f"{queue_row.get('taste_subject_key')}"
        )


def repair_proven_identity_copy_error(result, queue_by_key):
    key = result.get('key')
    queue_row = queue_by_key.get(key)
    if queue_row is None:
        raise SystemExit(f'Repair key is not in current queue: {key}')
    if str(result.get('appid')) != str(queue_row.get('appid')):
        raise SystemExit(f'Appid mismatch cannot be repaired for {key}')
    if result.get('candidate_context_sha256') != queue_row.get('candidate_context_sha256'):
        raise SystemExit(f'Candidate context mismatch cannot be repaired for {key}')

    prove_current_queue_context(queue_row)

    submitted_fp = result.get('taste_fingerprint')
    current_fp = queue_row.get('taste_fingerprint')
    if submitted_fp == current_fp:
        return False

    # The semantic evidence binding is the exact current candidate-context digest.
    # Since that digest is recomputed above from the current canonical fingerprint,
    # a differing submission fingerprint is proven to be a copied identity typo,
    # not a different semantic context. Copy the exact queue identity verbatim.
    result['taste_fingerprint'] = current_fp
    return True


def main():
    projection = load(PROJECTION)
    if projection.get('status') != 'complete' or projection.get('complete_coverage') is not True:
        raise SystemExit('Current taste projection is not complete')
    bindings = expected_bindings(projection)

    queue = read_jsonl(QUEUE)
    queue_by_key = {row['taste_subject_key']: row for row in queue}
    if len(queue_by_key) != len(queue):
        raise SystemExit('Current taste queue contains duplicate taste_subject_key values')

    ledger = load(LEDGER_CONTRACT)
    reason_semantics = ledger.get('cache_reason_code_semantics') or {}
    if not reason_semantics:
        raise SystemExit('Taste ledger contract has no reason-code semantics')

    total = 0
    serialization_changed = 0
    identity_changed = 0
    per_file = {}
    docs = []

    for path in TARGETS:
        if not path.exists():
            raise SystemExit(f'Missing expected interrupted-run checkpoint: {path}')
        doc = load(path)
        if doc.get('schema_version') != 1:
            raise SystemExit(f'Unexpected schema_version in {path}')
        if doc.get('bindings') != bindings:
            raise SystemExit(
                f'Bindings changed for {path}; one-shot repair is no longer safe'
            )
        results = doc.get('results')
        if not isinstance(results, list) or len(results) != EXPECTED_RESULTS_PER_FILE:
            raise SystemExit(
                f'Expected exactly {EXPECTED_RESULTS_PER_FILE} results in {path}, '
                f'got {len(results) if isinstance(results, list) else None}'
            )

        file_serialization = 0
        file_identity = 0
        for result in results:
            if not isinstance(result, dict):
                raise SystemExit(f'Non-object result in {path}')

            semantic_before = {
                field: copy.deepcopy(result.get(field))
                for field in ('verdict', 'positive_evidence', 'negative_evidence', 'taste_factors')
            }
            if normalize_serialization(result, reason_semantics):
                serialization_changed += 1
                file_serialization += 1
            if repair_proven_identity_copy_error(result, queue_by_key):
                identity_changed += 1
                file_identity += 1

            semantic_after = {
                field: result.get(field)
                for field in ('verdict', 'positive_evidence', 'negative_evidence', 'taste_factors')
            }
            if semantic_before != semantic_after:
                raise SystemExit(
                    f'Repair attempted to alter semantic verdict/evidence/factors for {result.get("key")}'
                )

        total += len(results)
        per_file[path.name] = {
            'serialization_alias_rows': file_serialization,
            'proven_identity_copy_error_rows': file_identity,
        }
        docs.append((path, doc))

    if total != EXPECTED_TOTAL_RESULTS:
        raise SystemExit(f'Expected exactly {EXPECTED_TOTAL_RESULTS} results, got {total}')
    if serialization_changed == 0 and identity_changed == 0:
        raise SystemExit('No proven repair required; refusing no-op one-shot migration')

    # Write runner-local repaired files only after every row has passed the narrow proof.
    for path, doc in docs:
        path.write_text(
            json.dumps(doc, ensure_ascii=False, separators=(',', ':')) + '\n',
            encoding='utf-8',
        )

    # Canonical validator must accept every repaired checkpoint before any Git commit is allowed.
    for path, _doc in docs:
        subprocess.run(
            ['python', 'scripts/ingest_taste_results.py', '--input', str(path), '--dry-run'],
            check=True,
        )

    print(json.dumps({
        'status': 'validated',
        'scope': 'serialization_aliases_and_proven_identity_copy_errors_only',
        'files': [path.name for path, _ in docs],
        'result_count': total,
        'serialization_changed_result_count': serialization_changed,
        'identity_changed_result_count': identity_changed,
        'changed_per_file': per_file,
        'bindings_unchanged': True,
        'semantic_verdict_evidence_factors_unchanged': True,
        'canonical_dry_run_all_files': True,
    }, ensure_ascii=False, indent=2))
    print('TASTE_ALIAS_REPAIR=PASS')


if __name__ == '__main__':
    main()
