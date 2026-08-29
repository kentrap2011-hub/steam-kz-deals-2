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


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def read_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def run(*args):
    subprocess.run(list(args), check=True)


def rebuild_taste_consumers():
    run('python', 'scripts/build_taste_cache_index.py')
    run('python', 'scripts/build_pre_ai_taste_projection.py')
    run('python', 'scripts/build_pre_ai_chatgpt_payload.py')


def main():
    inbox_files = sorted(INBOX_DIR.glob('*.json')) if INBOX_DIR.exists() else []
    if not inbox_files:
        raise SystemExit('No taste inbox JSON files found')

    # Synchronize the local baseline first. This deliberately consumes any canonical
    # cache commit that may not have triggered a downstream workflow because it was
    # written by GITHUB_TOKEN.
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

    # Each file is validated by the canonical ingest contract. Any failure happens
    # before git commit, so runner-local partial writes are discarded automatically.
    for path, _doc, _keys in batch_docs:
        run('python', 'scripts/ingest_taste_results.py', '--input', str(path))

    rebuild_taste_consumers()

    after_projection = load_json(PROJECTION)
    after_manifest = load_json(MANIFEST)
    after_queue = read_jsonl(QUEUE)
    after_queue_keys = {row['taste_subject_key'] for row in after_queue}

    expected_safe_hits = baseline_safe_hits + total_results
    expected_ai_required = baseline_ai_required - total_results
    expected_ai_queue = baseline_ai_queue - total_results

    checks = {
        'projection_complete': after_projection.get('complete_coverage') is True,
        'family_partition_complete': after_manifest.get('complete_family_partition') is True,
        'sale_end_complete': after_manifest.get('mandatory_sale_end_coverage') == 1.0,
        'safe_hits_increment_exact': after_projection.get('safe_cache_hit_count') == expected_safe_hits,
        'ai_required_decrement_exact': after_projection.get('ai_required_count') == expected_ai_required,
        'ai_queue_decrement_exact': after_manifest.get('ai_queue_count') == expected_ai_queue,
        'queue_file_count_exact': len(after_queue) == expected_ai_queue,
        'all_ingested_keys_removed_from_queue': not (set(all_keys) & after_queue_keys),
        'all_ingested_keys_are_cache_hits': all(
            (after_projection.get('entries') or {}).get(key, {}).get('status') == 'cache_hit'
            for key in all_keys
        ),
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        raise SystemExit(f'Taste inbox transactional proof failed: {failed}')

    batch_id = digest.hexdigest()[:20]
    receipt = {
        'schema_version': 1,
        'status': 'complete',
        'batch_id': batch_id,
        'processed_at_utc': datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        'source_mailing_updated_at_utc': after_projection.get('source_mailing_updated_at_utc'),
        'input_files': [path.name for path in inbox_files],
        'result_count': total_results,
        'keys': all_keys,
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
            'deterministically_excluded_without_ai_count': after_manifest.get('deterministically_excluded_without_ai_count'),
            'mandatory_sale_end_coverage': after_manifest.get('mandatory_sale_end_coverage'),
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
