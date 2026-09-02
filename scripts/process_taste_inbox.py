import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

INBOX_DIR = Path('data/ai_inbox/taste')
RECEIPT_DIR = Path('data/cache/taste_ingest_receipts')
PROJECTION = Path('data/production/pre_ai/taste_projection.json')
MANIFEST = Path('data/production/pre_ai/chatgpt_payload.json')
QUEUE = Path('data/production/pre_ai/chatgpt_taste_queue.jsonl')
FAMILY_GRAPH = Path('data/production/pre_ai/family_graph.json')
NEGATIVE_WORK_CODE = 'resolve_grounded_negative_analysis'
BASE_SUPPORT_WORK_CODE = 'resolve_base_support_condition'


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def run(*args):
    try:
        subprocess.run(list(args), check=True)
    except subprocess.CalledProcessError:
        if len(args) >= 4 and args[1] == 'scripts/ingest_taste_results.py' and '--input' in args:
            input_path = Path(args[args.index('--input') + 1])
            queue_by_key = {row['taste_subject_key']: row for row in read_jsonl(QUEUE)}
            input_doc = load_json(input_path)
            mismatches = []
            for result in input_doc.get('results') or []:
                key = result.get('key')
                current = queue_by_key.get(key)
                if current is None:
                    continue
                if (
                    result.get('taste_fingerprint') != current.get('taste_fingerprint')
                    or result.get('candidate_context_sha256') != current.get('candidate_context_sha256')
                    or str(result.get('appid')) != str(current.get('appid'))
                ):
                    mismatches.append({
                        'key': key,
                        'input_appid': str(result.get('appid')),
                        'current_appid': str(current.get('appid')),
                        'input_taste_fingerprint': result.get('taste_fingerprint'),
                        'current_taste_fingerprint': current.get('taste_fingerprint'),
                        'input_candidate_context_sha256': result.get('candidate_context_sha256'),
                        'current_candidate_context_sha256': current.get('candidate_context_sha256'),
                        'current_title': current.get('title'),
                        'current_fit_tags': current.get('fit_tags'),
                        'current_core_fit_count': current.get('core_fit_count'),
                        'current_release_date': current.get('release_date'),
                    })
            print(json.dumps({
                'taste_ingest_runtime_identity_mismatches': mismatches,
                'mismatch_count': len(mismatches),
            }, ensure_ascii=False, indent=2))
        raise


def rebuild_taste_consumers():
    run('python', 'scripts/build_taste_cache_index.py')
    run('python', 'scripts/build_pre_ai_taste_projection.py')
    run('python', 'scripts/build_pre_ai_chatgpt_payload.py')


def sale_end_state_is_consistent(manifest):
    family_count = manifest.get('source_family_count')
    coverage = manifest.get('sale_end_coverage')
    missing_count = manifest.get('sale_end_missing_count')
    missing_keys = manifest.get('sale_end_missing_primary_keys')
    if not isinstance(family_count, int) or family_count < 0:
        return False
    if not isinstance(missing_count, int) or missing_count < 0:
        return False
    if not isinstance(missing_keys, list) or len(missing_keys) != missing_count:
        return False
    if len(set(missing_keys)) != len(missing_keys):
        return False
    if family_count == 0:
        expected_coverage = 1.0
    else:
        if missing_count > family_count:
            return False
        expected_coverage = round((family_count - missing_count) / family_count, 4)
    return coverage == expected_coverage


def expected_retained_work(key, result, baseline_row, after_projection):
    projection_row = (after_projection.get('entries') or {}).get(key) or {}
    cached = projection_row.get('cached_taste') or {}
    verdict = cached.get('verdict')
    incomplete = result.get('negative_analysis_status') == 'incomplete_no_confirmed_negative'
    work = []
    if verdict == 'INCLUDE' and incomplete:
        work.append(NEGATIVE_WORK_CODE)
    if BASE_SUPPORT_WORK_CODE in (baseline_row.get('work_required') or []):
        work.append(BASE_SUPPORT_WORK_CODE)
    return work


def build_transactional_proof_checks(
    *,
    all_keys,
    result_by_key,
    baseline_queue_by_key,
    baseline_safe_hits,
    baseline_ai_required,
    baseline_ai_queue,
    after_projection,
    after_manifest,
    after_queue,
):
    after_queue_by_key = {row.get('taste_subject_key'): row for row in after_queue}
    duplicate_after_keys = len(after_queue_by_key) != len(after_queue)
    full_eval_count = sum(
        'evaluate_taste_fit' in (baseline_queue_by_key[key].get('work_required') or [])
        for key in all_keys
    )

    expected_safe_hits = baseline_safe_hits + full_eval_count
    expected_ai_required = baseline_ai_required - full_eval_count
    retained = {}
    retention_mismatches = {}
    for key in all_keys:
        expected_work = expected_retained_work(
            key,
            result_by_key[key],
            baseline_queue_by_key[key],
            after_projection,
        )
        actual = after_queue_by_key.get(key)
        if expected_work:
            retained[key] = expected_work
            if actual is None or actual.get('work_required') != expected_work:
                retention_mismatches[key] = {
                    'expected_work_required': expected_work,
                    'actual_work_required': None if actual is None else actual.get('work_required'),
                }
        elif actual is not None:
            retention_mismatches[key] = {
                'expected_work_required': [],
                'actual_work_required': actual.get('work_required'),
            }

    expected_ai_queue = baseline_ai_queue - len(all_keys) + len(retained)
    checks = {
        'projection_complete': after_projection.get('complete_coverage') is True,
        'family_partition_complete': after_manifest.get('complete_family_partition') is True,
        'sale_end_state_consistent': sale_end_state_is_consistent(after_manifest),
        'missing_sale_end_is_nonblocking': (after_manifest.get('contract') or {}).get('missing_sale_end_does_not_exclude_candidate') is True,
        'safe_hits_increment_only_for_full_eval': after_projection.get('safe_cache_hit_count') == expected_safe_hits,
        'ai_required_decrement_only_for_full_eval': after_projection.get('ai_required_count') == expected_ai_required,
        'after_queue_has_unique_keys': not duplicate_after_keys,
        'ingested_key_retention_matches_negative_and_base_support_state': not retention_mismatches,
        'ai_queue_count_exact': after_manifest.get('ai_queue_count') == expected_ai_queue,
        'queue_file_count_exact': len(after_queue) == expected_ai_queue,
        'all_ingested_keys_are_fit_cache_hits': all(
            (after_projection.get('entries') or {}).get(key, {}).get('status') == 'cache_hit'
            for key in all_keys
        ),
    }
    return checks, retained, retention_mismatches, expected_ai_queue, full_eval_count


def main():
    inbox_files = sorted(INBOX_DIR.glob('*.json')) if INBOX_DIR.exists() else []
    if not inbox_files:
        raise SystemExit('No taste inbox JSON files found')

    # Synchronize the local baseline first. This consumes canonical cache changes
    # that may not have triggered a downstream workflow because they were written
    # by GITHUB_TOKEN, and it re-derives grounded-negative queue readiness.
    rebuild_taste_consumers()

    baseline_projection = load_json(PROJECTION)
    baseline_manifest = load_json(MANIFEST)
    baseline_queue = read_jsonl(QUEUE)
    baseline_queue_by_key = {row['taste_subject_key']: row for row in baseline_queue}
    if len(baseline_queue_by_key) != len(baseline_queue):
        raise SystemExit('Baseline ChatGPT taste queue contains duplicate taste_subject_key values')

    all_keys = []
    total_results = 0
    batch_docs = []
    result_by_key = {}
    digest = hashlib.sha256()
    for path in inbox_files:
        raw = path.read_bytes()
        digest.update(path.name.encode('utf-8'))
        digest.update(b'\0')
        digest.update(raw)
        digest.update(b'\0')
        doc = json.loads(raw.decode('utf-8'))
        results = doc.get('results')
        if not isinstance(results, list) or not results:
            raise SystemExit(f'{path} has no non-empty results array')
        if len(results) > 100:
            raise SystemExit(f'{path} exceeds the 100-result ingest limit')
        keys = [row.get('key') for row in results]
        if any(not isinstance(key, str) or not key for key in keys):
            raise SystemExit(f'{path} contains an invalid result key')
        batch_docs.append((path, doc, keys))
        for result in results:
            result_by_key[result['key']] = result
        all_keys.extend(keys)
        total_results += len(results)

    if len(set(all_keys)) != len(all_keys):
        raise SystemExit('Duplicate taste key across inbox files')
    missing_from_queue = sorted(set(all_keys) - set(baseline_queue_by_key))
    if missing_from_queue:
        raise SystemExit(f'Inbox keys are not in the synchronized current taste queue: {missing_from_queue[:20]}')

    baseline_safe_hits = baseline_projection.get('safe_cache_hit_count')
    baseline_ai_required = baseline_projection.get('ai_required_count')
    baseline_ai_queue = baseline_manifest.get('ai_queue_count')
    if baseline_ai_queue != len(baseline_queue):
        raise SystemExit('Baseline manifest ai_queue_count does not match JSONL line count')

    # Each file is validated by the canonical ingest contract. Negative-only rows
    # cannot rewrite fit semantics because their accepted result shape omits them.
    for path, _doc, _keys in batch_docs:
        run('python', 'scripts/ingest_taste_results.py', '--input', str(path))

    rebuild_taste_consumers()

    after_projection = load_json(PROJECTION)
    after_manifest = load_json(MANIFEST)
    after_queue = read_jsonl(QUEUE)

    checks, retained, retention_mismatches, expected_ai_queue, full_eval_count = build_transactional_proof_checks(
        all_keys=all_keys,
        result_by_key=result_by_key,
        baseline_queue_by_key=baseline_queue_by_key,
        baseline_safe_hits=baseline_safe_hits,
        baseline_ai_required=baseline_ai_required,
        baseline_ai_queue=baseline_ai_queue,
        after_projection=after_projection,
        after_manifest=after_manifest,
        after_queue=after_queue,
    )
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print(json.dumps({
            'retained_ingest_keys': retained,
            'retention_mismatches': retention_mismatches,
            'expected_ai_queue_count': expected_ai_queue,
            'actual_ai_queue_count': after_manifest.get('ai_queue_count'),
        }, ensure_ascii=False, indent=2))
        raise SystemExit(f'Taste inbox transactional proof failed: {failed}')

    batch_id = digest.hexdigest()[:20]
    receipt = {
        'schema_version': 2,
        'status': 'complete',
        'batch_id': batch_id,
        'processed_at_utc': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        'source_mailing_updated_at_utc': after_projection.get('source_mailing_updated_at_utc'),
        'input_files': [path.name for path in inbox_files],
        'result_count': total_results,
        'full_evaluation_result_count': full_eval_count,
        'negative_only_result_count': total_results - full_eval_count,
        'incomplete_negative_result_count': sum(
            result_by_key[key].get('negative_analysis_status') == 'incomplete_no_confirmed_negative'
            for key in all_keys
        ),
        'keys': all_keys,
        'retained_work_after_ingest': retained,
        'baseline': {
            'safe_cache_hit_count': baseline_safe_hits,
            'ai_required_count': baseline_ai_required,
            'ai_queue_count': baseline_ai_queue,
        },
        'after': {
            'safe_cache_hit_count': after_projection.get('safe_cache_hit_count'),
            'ai_required_count': after_projection.get('ai_required_count'),
            'ai_queue_count': after_manifest.get('ai_queue_count'),
            'ready_without_ai_count': after_manifest.get('ready_without_ai_count'),
            'negative_analysis': after_manifest.get('negative_analysis'),
            'deterministically_excluded_without_ai_count': after_manifest.get('deterministically_excluded_without_ai_count'),
            'sale_end_coverage': after_manifest.get('sale_end_coverage'),
            'sale_end_missing_count': after_manifest.get('sale_end_missing_count'),
        },
        'checks': checks,
    }
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = RECEIPT_DIR / f'{batch_id}.json'
    if receipt_path.exists():
        raise SystemExit(f'Receipt already exists for this exact batch: {receipt_path}')
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    for path in inbox_files:
        path.unlink()

    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    print('TASTE_INBOX_TRANSACTION=PASS')


if __name__ == '__main__':
    main()
