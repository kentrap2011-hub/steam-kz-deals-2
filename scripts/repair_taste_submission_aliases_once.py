import copy
import json
import subprocess
from pathlib import Path

PROJECTION = Path('data/production/pre_ai/taste_projection.json')
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


def expected_bindings(projection):
    return {
        'profile_blob_sha': projection['current_profile']['blob_sha'],
        'taste_model_version': projection['current_binding']['taste_model_version'],
        'taste_semantics_sha256': projection['current_binding']['taste_semantics_sha256'],
        'source_mailing_updated_at_utc': projection['source_mailing_updated_at_utc'],
    }


def without_serialization_fields(row):
    return {
        key: value
        for key, value in row.items()
        if key not in {'reason_code', 'fit_level'}
    }


def normalize_result(result, reason_semantics):
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

    if without_serialization_fields(before) != without_serialization_fields(result):
        raise SystemExit(
            f"Repair attempted to alter semantic content for {result.get('key')}"
        )
    return before != result


def main():
    projection = load(PROJECTION)
    if projection.get('status') != 'complete' or projection.get('complete_coverage') is not True:
        raise SystemExit('Current taste projection is not complete')
    bindings = expected_bindings(projection)

    ledger = load(LEDGER_CONTRACT)
    reason_semantics = ledger.get('cache_reason_code_semantics') or {}
    if not reason_semantics:
        raise SystemExit('Taste ledger contract has no reason-code semantics')

    total = 0
    changed = 0
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
                f'Bindings changed for {path}; one-shot serialization repair is no longer safe'
            )
        results = doc.get('results')
        if not isinstance(results, list) or len(results) != EXPECTED_RESULTS_PER_FILE:
            raise SystemExit(
                f'Expected exactly {EXPECTED_RESULTS_PER_FILE} results in {path}, '
                f'got {len(results) if isinstance(results, list) else None}'
            )

        file_changed = 0
        for result in results:
            if not isinstance(result, dict):
                raise SystemExit(f'Non-object result in {path}')
            if normalize_result(result, reason_semantics):
                changed += 1
                file_changed += 1
        total += len(results)
        per_file[path.name] = file_changed
        docs.append((path, doc))

    if total != EXPECTED_TOTAL_RESULTS:
        raise SystemExit(f'Expected exactly {EXPECTED_TOTAL_RESULTS} results, got {total}')
    if changed == 0:
        raise SystemExit('No serialization aliases required repair; refusing no-op one-shot migration')

    # Write runner-local normalized files only after every row has passed the narrow mapping.
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
        'scope': 'serialization_aliases_only',
        'files': [path.name for path, _ in docs],
        'result_count': total,
        'changed_result_count': changed,
        'changed_per_file': per_file,
        'bindings_unchanged': True,
        'semantic_fields_unchanged': True,
        'canonical_dry_run_all_files': True,
    }, ensure_ascii=False, indent=2))
    print('TASTE_ALIAS_REPAIR=PASS')


if __name__ == '__main__':
    main()
