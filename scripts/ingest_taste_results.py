import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from taste_cache_common import (
    ENTRY_CONTRACT,
    load_json,
    validate_cache_entry,
    validate_taste_factors,
    validate_verdict_shape,
)

QUEUE = Path('data/production/pre_ai/chatgpt_taste_queue.jsonl')
PROJECTION = Path('data/production/pre_ai/taste_projection.json')
OVERLAY = Path('data/cache/taste_fit.entry_overlay.json')

BASE_RESULT_FIELDS = {
    'key',
    'appid',
    'taste_fingerprint',
    'candidate_context_sha256',
    'verdict',
    'fit_level',
    'reason_code',
    'positive_evidence',
    'negative_evidence',
}
OPTIONAL_RESULT_FIELDS = {'taste_factors'}
FORBIDDEN_EVIDENCE_FRAGMENTS = [
    'price', 'discount', 'wishlist', 'steam review', 'global review', 'russian review',
    'steamdb', 'historical price', 'sale price', 'rub', 'kzt',
    'цена', 'скидк', 'вишлист', 'список желаем', 'отзывы steam', 'историческ',
    'руб.', 'рублей', 'тенге', 'распродаж',
]


def read_jsonl(path):
    rows = []
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f'Invalid JSONL at {path}:{number}: {exc}') from exc
    return rows


def validate_evidence_list(name, values):
    if not isinstance(values, list):
        raise ValueError(f'{name} must be an array')
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{name}[{index}] must be a non-empty string')
        folded = value.casefold()
        hit = next((fragment for fragment in FORBIDDEN_EVIDENCE_FRAGMENTS if fragment in folded), None)
        if hit is not None:
            raise ValueError(f'{name}[{index}] contains forbidden non-taste evidence fragment: {hit!r}')


def load_overlay():
    doc = load_json(OVERLAY)
    if doc.get('schema_version') != 1 or doc.get('entry_schema_version') not in {2, 3}:
        raise ValueError('Unexpected taste overlay schema')
    entries = doc.get('entries')
    if not isinstance(entries, dict):
        raise ValueError('Taste overlay entries must be an object')
    if doc.get('entry_count') != len(entries):
        raise ValueError('Taste overlay entry_count mismatch')
    return doc


def validate_input(doc, queue_by_key, projection):
    if doc.get('schema_version') != 1:
        raise ValueError('Unexpected ingest schema_version')
    bindings = doc.get('bindings')
    if not isinstance(bindings, dict):
        raise ValueError('Ingest bindings must be an object')

    current_profile = projection['current_profile']['blob_sha']
    current_model = projection['current_binding']['taste_model_version']
    current_semantics = projection['current_binding']['taste_semantics_sha256']
    current_source = projection['source_mailing_updated_at_utc']
    expected = {
        'profile_blob_sha': current_profile,
        'taste_model_version': current_model,
        'taste_semantics_sha256': current_semantics,
        'source_mailing_updated_at_utc': current_source,
    }
    for field, value in expected.items():
        if bindings.get(field) != value:
            raise ValueError(
                f'Ingest binding mismatch for {field}: input={bindings.get(field)!r} current={value!r}'
            )

    results = doc.get('results')
    if not isinstance(results, list) or not results:
        raise ValueError('Ingest results must be a non-empty array')
    if len(results) > 100:
        raise ValueError('A single taste ingest batch may contain at most 100 results')

    seen = set()
    validated = []
    for result in results:
        if not isinstance(result, dict):
            raise ValueError('Every ingest result must be an object')
        unknown = set(result) - (BASE_RESULT_FIELDS | OPTIONAL_RESULT_FIELDS)
        missing = BASE_RESULT_FIELDS - set(result)
        if unknown:
            raise ValueError(f'Unexpected result fields: {sorted(unknown)}')
        if missing:
            raise ValueError(f'Missing result fields: {sorted(missing)}')

        key = result['key']
        if key in seen:
            raise ValueError(f'Duplicate ingest key: {key}')
        seen.add(key)
        queue_row = queue_by_key.get(key)
        if queue_row is None:
            raise ValueError(f'Ingest key is not in current ChatGPT taste queue: {key}')
        work_required = queue_row.get('work_required') or []
        if 'evaluate_taste_fit' not in work_required:
            raise ValueError(f'Current queue row does not require taste evaluation: {key}')
        factors_required = 'evaluate_normalized_taste_factors' in work_required
        if factors_required and 'taste_factors' not in result:
            raise ValueError(f'Current queue row requires taste_factors: {key}')
        if 'taste_factors' in result:
            validate_taste_factors(result['taste_factors'])
        if str(result['appid']) != str(queue_row['appid']):
            raise ValueError(f'Appid mismatch for {key}')
        if result['taste_fingerprint'] != queue_row['taste_fingerprint']:
            raise ValueError(f'Taste fingerprint mismatch for {key}')
        context_sha = result['candidate_context_sha256']
        if not isinstance(context_sha, str) or len(context_sha) != 64:
            raise ValueError(f'Invalid candidate_context_sha256 for {key}')
        if context_sha != queue_row.get('candidate_context_sha256'):
            raise ValueError(f'Candidate context mismatch for {key}')

        validate_verdict_shape(result['verdict'], result['fit_level'], result['reason_code'])
        validate_evidence_list('positive_evidence', result['positive_evidence'])
        validate_evidence_list('negative_evidence', result['negative_evidence'])
        if result['verdict'] == 'INCLUDE' and len(result['positive_evidence']) < 2:
            raise ValueError(f'INCLUDE result requires at least two explicit positive evidence items: {key}')
        if result['reason_code'] == 'exclude_direct_conflict' and not result['negative_evidence']:
            raise ValueError(f'exclude_direct_conflict requires explicit negative evidence: {key}')

        validated.append(result)

    return bindings, validated


def build_entry(result, bindings, evaluated_at):
    entry = {
        'key': result['key'],
        'appid': str(result['appid']),
        'profile_blob_sha': bindings['profile_blob_sha'],
        'taste_model_version': bindings['taste_model_version'],
        'taste_semantics_sha256': bindings['taste_semantics_sha256'],
        'candidate_context_sha256': result['candidate_context_sha256'],
        'taste_fingerprint': result['taste_fingerprint'],
        'verdict': result['verdict'],
        'fit_level': result['fit_level'],
        'reason_code': result['reason_code'],
        'positive_evidence': result['positive_evidence'],
        'negative_evidence': result['negative_evidence'],
        'evaluated_at_utc': evaluated_at,
    }
    if 'taste_factors' in result:
        entry['taste_factors'] = result['taste_factors']
    return entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    projection = load_json(PROJECTION)
    if projection.get('status') != 'complete' or not projection.get('complete_coverage'):
        raise SystemExit('Current taste projection is incomplete')
    if not (projection.get('cache_binding') or {}).get('index_integrity_ok'):
        raise SystemExit('Current per-entry taste index integrity is not proven')

    queue = read_jsonl(QUEUE)
    queue_by_key = {row['taste_subject_key']: row for row in queue}
    if len(queue_by_key) != len(queue):
        raise SystemExit('Current ChatGPT taste queue has duplicate taste_subject_key values')

    ingest = load_json(args.input)
    try:
        bindings, results = validate_input(ingest, queue_by_key, projection)
        overlay = load_overlay()
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    contract = load_json(ENTRY_CONTRACT)
    base_required = contract.get('base_required_entry_fields') or contract['schema_v2_required_entry_fields']
    v3_required = contract.get('schema_v3_required_entry_fields') or base_required
    evaluated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    entries = dict(overlay['entries'])
    inserted = 0
    replaced = 0
    unchanged = 0
    v3_result_count = 0

    for result in results:
        entry = build_entry(result, bindings, evaluated_at)
        is_v3 = 'taste_factors' in result
        try:
            validate_cache_entry(
                entry,
                result['key'],
                v3_required if is_v3 else base_required,
                require_taste_factors=is_v3,
            )
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        v3_result_count += int(is_v3)

        old = entries.get(result['key'])
        if old is None:
            inserted += 1
        else:
            comparable_old = {k: v for k, v in old.items() if k != 'evaluated_at_utc'}
            comparable_new = {k: v for k, v in entry.items() if k != 'evaluated_at_utc'}
            if comparable_old == comparable_new:
                unchanged += 1
                continue
            replaced += 1
        entries[result['key']] = entry

    updated = dict(overlay)
    if v3_result_count:
        updated['entry_schema_version'] = 3
    updated['entry_count'] = len(entries)
    updated['entries'] = entries

    if not args.dry_run:
        OVERLAY.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print(json.dumps({
        'status': 'validated',
        'dry_run': args.dry_run,
        'batch_result_count': len(results),
        'v3_result_count': v3_result_count,
        'overlay_before_count': len(overlay['entries']),
        'overlay_after_count': len(entries),
        'inserted_count': inserted,
        'replaced_count': replaced,
        'unchanged_count': unchanged,
        'profile_blob_sha': bindings['profile_blob_sha'],
        'taste_model_version': bindings['taste_model_version'],
        'taste_semantics_sha256': bindings['taste_semantics_sha256'],
        'candidate_context_required': True,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
