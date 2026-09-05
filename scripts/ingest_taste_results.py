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
from taste_negative_contract import validate_negative_analysis
from taste_evidence_contract import (
    EVIDENCE_RESULT_FIELDS,
    current_evidence_contract_sha,
    validate_fit_evidence_fields,
)

QUEUE = Path('data/production/pre_ai/chatgpt_taste_queue.jsonl')
PROJECTION = Path('data/production/pre_ai/taste_projection.json')
SOURCE_CACHE = Path('data/cache/taste_fit.json')
OVERLAY = Path('data/cache/taste_fit.entry_overlay.json')
NEGATIVE_WORK_CODE = 'resolve_grounded_negative_analysis'

FULL_RESULT_FIELDS = {
    'key',
    'appid',
    'taste_fingerprint',
    'candidate_context_sha256',
    'verdict',
    'fit_level',
    'reason_code',
    'positive_evidence',
    'negative_analysis_status',
    'negative_findings',
    'negative_evidence',
}
NEGATIVE_ONLY_RESULT_FIELDS = {
    'key',
    'appid',
    'taste_fingerprint',
    'candidate_context_sha256',
    'negative_analysis_status',
    'negative_findings',
    'negative_evidence',
}
FULL_RESULT_FIELDS |= EVIDENCE_RESULT_FIELDS
NEGATIVE_ONLY_RESULT_FIELDS |= EVIDENCE_RESULT_FIELDS
OPTIONAL_FULL_RESULT_FIELDS = {'taste_factors'}
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


def validate_price_blind_text(name, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be a non-empty string')
    folded = value.casefold()
    hit = next((fragment for fragment in FORBIDDEN_EVIDENCE_FRAGMENTS if fragment in folded), None)
    if hit is not None:
        raise ValueError(f'{name} contains forbidden non-taste evidence fragment: {hit!r}')


def validate_evidence_list(name, values):
    if not isinstance(values, list):
        raise ValueError(f'{name} must be an array')
    for index, value in enumerate(values):
        validate_price_blind_text(f'{name}[{index}]', value)


def load_overlay():
    doc = load_json(OVERLAY)
    if doc.get('schema_version') != 1 or doc.get('entry_schema_version') not in {2, 3, 4, 5}:
        raise ValueError('Unexpected taste overlay schema')
    entries = doc.get('entries')
    if not isinstance(entries, dict):
        raise ValueError('Taste overlay entries must be an object')
    if doc.get('entry_count') != len(entries):
        raise ValueError('Taste overlay entry_count mismatch')
    return doc


def cache_entries(doc):
    entries = doc.get('entries') if isinstance(doc, dict) else None
    return entries if isinstance(entries, dict) else {}


def effective_entries(overlay):
    merged = dict(cache_entries(load_json(SOURCE_CACHE)))
    merged.update(cache_entries(overlay))
    return merged


def validate_negative_result_fields(result):
    findings = validate_negative_analysis(
        result.get('negative_analysis_status'),
        result.get('negative_findings'),
        result.get('negative_evidence'),
        require_v5=True,
    )
    validate_evidence_list('negative_evidence', result['negative_evidence'])
    for index, finding in enumerate(findings):
        validate_price_blind_text(f'negative_findings[{index}].evidence', finding['evidence'])
        validate_price_blind_text(f'negative_findings[{index}].risk_text_ru', finding['risk_text_ru'])
    return findings


def validate_noncommercial_quality_text(name, value):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be a non-empty string')
    forbidden = [
        'price', 'discount', 'wishlist', 'steamdb', 'historical price', 'sale price',
        'rub', 'kzt', 'цена', 'скидк', 'вишлист', 'историческ', 'руб.', 'рублей', 'тенге', 'распродаж',
    ]
    folded = value.casefold()
    hit = next((fragment for fragment in forbidden if fragment in folded), None)
    if hit is not None:
        raise ValueError(f'{name} contains forbidden commercial evidence fragment: {hit!r}')


def validate_current_base_entry(key, entry, queue_row, projection):
    if not isinstance(entry, dict):
        raise ValueError(f'Negative-only backfill has no accepted cache entry for {key}')
    expected = {
        'appid': str(queue_row['appid']),
        'taste_fingerprint': queue_row['taste_fingerprint'],
        'candidate_context_sha256': queue_row.get('candidate_context_sha256'),
        'profile_blob_sha': projection['current_profile']['blob_sha'],
        'taste_model_version': projection['current_binding']['taste_model_version'],
        'taste_semantics_sha256': projection['current_binding']['taste_semantics_sha256'],
    }
    for field, value in expected.items():
        actual = str(entry.get(field)) if field == 'appid' else entry.get(field)
        if actual != value:
            raise ValueError(
                f'Negative-only backfill base binding mismatch for {key}.{field}: '
                f'entry={actual!r} current={value!r}'
            )
    return entry


def validate_input(doc, queue_by_key, projection, current_entries):
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

        key = result.get('key')
        if not isinstance(key, str) or not key:
            raise ValueError('Every ingest result requires a non-empty key')
        if key in seen:
            raise ValueError(f'Duplicate ingest key: {key}')
        seen.add(key)

        queue_row = queue_by_key.get(key)
        if queue_row is None:
            raise ValueError(f'Ingest key is not in current ChatGPT taste queue: {key}')
        work_required = queue_row.get('work_required') or []
        full_eval = 'evaluate_taste_fit' in work_required
        negative_requested = NEGATIVE_WORK_CODE in work_required
        if not negative_requested:
            raise ValueError(f'Current queue row does not require grounded negative analysis: {key}')

        if full_eval:
            allowed = FULL_RESULT_FIELDS | OPTIONAL_FULL_RESULT_FIELDS
            required = FULL_RESULT_FIELDS
        else:
            allowed = NEGATIVE_ONLY_RESULT_FIELDS
            required = NEGATIVE_ONLY_RESULT_FIELDS

        unknown = set(result) - allowed
        missing = required - set(result)
        if unknown:
            if not full_eval:
                raise ValueError(
                    f'Negative-only result attempted to rewrite accepted Taste semantics for {key}: '
                    f'{sorted(unknown)}'
                )
            raise ValueError(f'Unexpected result fields: {sorted(unknown)}')
        if missing:
            raise ValueError(f'Missing result fields: {sorted(missing)}')

        if str(result['appid']) != str(queue_row['appid']):
            raise ValueError(f'Appid mismatch for {key}')
        if result['taste_fingerprint'] != queue_row['taste_fingerprint']:
            raise ValueError(f'Taste fingerprint mismatch for {key}')
        context_sha = result['candidate_context_sha256']
        if not isinstance(context_sha, str) or len(context_sha) != 64:
            raise ValueError(f'Invalid candidate_context_sha256 for {key}')
        if context_sha != queue_row.get('candidate_context_sha256'):
            raise ValueError(f'Candidate context mismatch for {key}')

        validate_negative_result_fields(result)
        for q_index, finding in enumerate(result.get('candidate_quality_findings') or []):
            validate_noncommercial_quality_text(f'candidate_quality_findings[{q_index}].evidence', finding['evidence'])
            validate_noncommercial_quality_text(f'candidate_quality_findings[{q_index}].risk_text_ru', finding['risk_text_ru'])

        if full_eval:
            validate_fit_evidence_fields(result, require_v5=True)
            factors_required = 'evaluate_normalized_taste_factors' in work_required
            if factors_required and 'taste_factors' not in result:
                raise ValueError(f'Current queue row requires taste_factors: {key}')
            if 'taste_factors' in result:
                validate_taste_factors(result['taste_factors'])
            validate_verdict_shape(result['verdict'], result['fit_level'], result['reason_code'])
            validate_evidence_list('positive_evidence', result['positive_evidence'])
            if result['verdict'] == 'INCLUDE' and len(result['positive_evidence']) < 2:
                raise ValueError(f'INCLUDE result requires at least two explicit positive evidence items: {key}')
            if (
                result['reason_code'] == 'exclude_direct_conflict'
                and result['fit_evidence_state'] == 'confirmed_negative'
                and not result['negative_evidence']
            ):
                raise ValueError(f'confirmed exclude_direct_conflict requires explicit negative evidence: {key}')
            base_entry = None
        else:
            base_entry = validate_current_base_entry(
                key,
                current_entries.get(key),
                queue_row,
                projection,
            )
            evidence_view = dict(base_entry)
            evidence_view.update(result)
            validate_fit_evidence_fields(evidence_view, require_v5=True)

        validated.append({
            'result': result,
            'full_eval': full_eval,
            'base_entry': base_entry,
        })

    return bindings, validated


def build_full_entry(result, bindings, evaluated_at):
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
        'negative_analysis_status': result['negative_analysis_status'],
        'negative_findings': result['negative_findings'],
        'negative_evidence': result['negative_evidence'],
        'evidence_contract_sha': current_evidence_contract_sha(),
        'fit_evidence_state': result['fit_evidence_state'],
        'fit_evidence_confidence': result['fit_evidence_confidence'],
        'fit_evidence_basis': result['fit_evidence_basis'],
        'historical_negative_context': result['historical_negative_context'],
        'candidate_quality_findings': result['candidate_quality_findings'],
        'evaluated_at_utc': evaluated_at,
    }
    if 'taste_factors' in result:
        entry['taste_factors'] = result['taste_factors']
    return entry


def build_negative_only_entry(result, base_entry):
    entry = dict(base_entry)
    entry['negative_analysis_status'] = result['negative_analysis_status']
    entry['negative_findings'] = result['negative_findings']
    entry['negative_evidence'] = result['negative_evidence']
    entry['evidence_contract_sha'] = current_evidence_contract_sha()
    for field in EVIDENCE_RESULT_FIELDS:
        entry[field] = result[field]
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

    try:
        overlay = load_overlay()
        current_entries = effective_entries(overlay)
        ingest = load_json(args.input)
        bindings, validated = validate_input(ingest, queue_by_key, projection, current_entries)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    contract = load_json(ENTRY_CONTRACT)
    base_required = contract.get('base_required_entry_fields') or contract['schema_v2_required_entry_fields']
    v5_required = contract.get('schema_v5_required_entry_fields') or contract.get('schema_v4_required_entry_fields') or base_required
    evaluated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    entries = dict(overlay['entries'])
    inserted = 0
    replaced = 0
    unchanged = 0
    full_result_count = 0
    negative_only_result_count = 0
    incomplete_negative_count = 0

    for row in validated:
        result = row['result']
        if row['full_eval']:
            entry = build_full_entry(result, bindings, evaluated_at)
            full_result_count += 1
            required_fields = v5_required
            require_factors = True
        else:
            entry = build_negative_only_entry(result, row['base_entry'])
            negative_only_result_count += 1
            required_fields = base_required
            require_factors = False

        incomplete_negative_count += int(
            result['negative_analysis_status'] == 'incomplete_no_confirmed_negative'
        )

        try:
            validate_cache_entry(
                entry,
                result['key'],
                required_fields,
                require_taste_factors=require_factors,
                require_v4_negative_fields=True,
                require_v5_evidence_fields=True,
            )
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc

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
    updated['entry_schema_version'] = 5
    updated['entry_count'] = len(entries)
    updated['entries'] = entries

    if not args.dry_run:
        OVERLAY.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print(json.dumps({
        'status': 'validated',
        'dry_run': args.dry_run,
        'batch_result_count': len(validated),
        'full_result_count': full_result_count,
        'negative_only_result_count': negative_only_result_count,
        'incomplete_negative_count': incomplete_negative_count,
        'overlay_before_count': len(overlay['entries']),
        'overlay_after_count': len(entries),
        'inserted_count': inserted,
        'replaced_count': replaced,
        'unchanged_count': unchanged,
        'profile_blob_sha': bindings['profile_blob_sha'],
        'taste_model_version': bindings['taste_model_version'],
        'taste_semantics_sha256': bindings['taste_semantics_sha256'],
        'candidate_context_required': True,
        'negative_only_fit_semantics_immutable': True,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
