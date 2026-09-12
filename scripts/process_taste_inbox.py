import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from semantic_runtime_completion import build_runtime_status
from taste_pinned_work_unit import (
    ACTIVE_PIN,
    resolve_pinned_work_unit,
    transition_active_pin_after_success,
)

INBOX_DIR = Path('data/ai_inbox/taste')
RECEIPT_DIR = Path('data/cache/taste_ingest_receipts')
LATEST_RUNTIME_STATUS = RECEIPT_DIR / 'latest_runtime_status.json'
PROJECTION = Path('data/production/pre_ai/taste_projection.json')
MANIFEST = Path('data/production/pre_ai/chatgpt_payload.json')
QUEUE = Path('data/production/pre_ai/chatgpt_taste_queue.jsonl')
FAMILY_GRAPH = Path('data/production/pre_ai/family_graph.json')
DEALS = Path('data/production/pre_ai/deal_scenarios.json')
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


def expected_retained_work(
    key,
    result,
    baseline_row,
    after_projection,
    *,
    deterministically_excluded=False,
    deal_row=None,
):
    projection_row = (after_projection.get('entries') or {}).get(key) or {}
    cached = projection_row.get('cached_taste') or {}
    verdict = cached.get('verdict')

    # Canonical consumer gating removes non-INCLUDE rows before constructing
    # base-support work when the family has no eligibility bridge and is final.
    if verdict != 'INCLUDE' and deterministically_excluded:
        return []

    # For a valid cached INCLUDE, the consumer selects the precomputed deal
    # scenario for the resolved fit before constructing grounded-negative work.
    if verdict == 'INCLUDE':
        fit = cached.get('fit_level')
        scenario_name = {
            'strong': 'decision_if_strong',
            'moderate': 'decision_if_moderate',
        }.get(fit)
        selected = (deal_row or {}).get(scenario_name) if scenario_name else None
        if isinstance(selected, dict) and selected.get('final_disposition') != 'INCLUDE':
            return []

    incomplete = result.get('negative_analysis_status') == 'incomplete_no_confirmed_negative'
    work = []
    if verdict == 'INCLUDE' and incomplete:
        work.append(NEGATIVE_WORK_CODE)
    if BASE_SUPPORT_WORK_CODE in (baseline_row.get('work_required') or []):
        work.append(BASE_SUPPORT_WORK_CODE)
    return work


def _queue_identity(row):
    row = row or {}
    return {
        'appid': str(row.get('appid')),
        'taste_fingerprint': row.get('taste_fingerprint'),
        'candidate_context_sha256': row.get('candidate_context_sha256'),
        'work_required': list(row.get('work_required') or []),
    }


def result_is_reusable_for_current_projection(result, pinned_work_unit, current_projection, current_queue_row):
    current_profile = current_projection.get('current_profile') or {}
    current_binding = current_projection.get('current_binding') or {}
    pinned_binding = pinned_work_unit.get('bindings') or {}
    pinned_rows = {
        row.get('key'): row
        for row in (pinned_work_unit.get('ordered_rows') or [])
        if row.get('key')
    }
    pinned_row = pinned_rows.get(result.get('key')) or {}
    return bool(
        current_queue_row
        and pinned_binding.get('profile_blob_sha') == current_profile.get('blob_sha')
        and pinned_binding.get('taste_model_version') == current_binding.get('taste_model_version')
        and pinned_binding.get('taste_semantics_sha256') == current_binding.get('taste_semantics_sha256')
        and str(result.get('appid')) == str(current_queue_row.get('appid')) == str(pinned_row.get('appid'))
        and result.get('taste_fingerprint') == current_queue_row.get('taste_fingerprint') == pinned_row.get('taste_fingerprint')
        and result.get('candidate_context_sha256') == current_queue_row.get('candidate_context_sha256') == pinned_row.get('candidate_context_sha256')
        and list(current_queue_row.get('work_required') or []) == list(pinned_row.get('work_required') or [])
    )


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
    after_family_graph=None,
    after_deals=None,
    baseline_projection=None,
    current_reusable_by_key=None,
    baseline_current_queue_by_key=None,
):
    after_queue_by_key = {row.get('taste_subject_key'): row for row in after_queue}
    duplicate_after_keys = len(after_queue_by_key) != len(after_queue)
    if current_reusable_by_key is None:
        current_reusable_by_key = {key: True for key in all_keys}
    if set(current_reusable_by_key) != set(all_keys):
        raise ValueError('Current-reuse proof must cover every ingested Taste key exactly')
    if baseline_current_queue_by_key is None:
        baseline_current_queue_by_key = baseline_queue_by_key

    full_eval_count = sum(
        'evaluate_taste_fit' in (baseline_queue_by_key[key].get('work_required') or [])
        for key in all_keys
    )
    current_reusable_full_eval_count = sum(
        current_reusable_by_key[key]
        and 'evaluate_taste_fit' in (baseline_queue_by_key[key].get('work_required') or [])
        for key in all_keys
    )

    family_by_taste_key = {
        row.get('taste_subject_key'): row
        for row in ((after_family_graph or {}).get('families') or [])
        if row.get('taste_subject_key')
    }
    deal_entries = (after_deals or {}).get('entries') or {}
    excluded_primary_keys = set(after_manifest.get('deterministically_excluded_primary_keys') or [])

    expected_safe_hits = baseline_safe_hits + current_reusable_full_eval_count
    expected_ai_required = baseline_ai_required - current_reusable_full_eval_count
    retained = {}
    retention_mismatches = {}
    for key in all_keys:
        current_baseline_row = baseline_current_queue_by_key.get(key)
        if not current_reusable_by_key[key]:
            # A pre-semantic pinned result remains historically valid even when
            # newer live source/profile state has removed the key from the
            # current queue. In that case ingest must not resurrect old work.
            if current_baseline_row is None:
                actual = after_queue_by_key.get(key)
                if actual is not None:
                    retention_mismatches[key] = {
                        'expected_work_required': [],
                        'actual_work_required': actual.get('work_required'),
                        'reason': 'newer_live_state_removed_pinned_key_but_ingest_resurrected_it',
                    }
                continue

            expected_work = list(current_baseline_row.get('work_required') or [])
            retained[key] = expected_work
            actual = after_queue_by_key.get(key)
            if actual is None or _queue_identity(actual) != _queue_identity(current_baseline_row):
                retention_mismatches[key] = {
                    'expected_work_required': expected_work,
                    'actual_work_required': None if actual is None else actual.get('work_required'),
                    'reason': 'pinned_result_is_valid_but_not_reusable_for_current_live_identity',
                }
            continue

        family = family_by_taste_key.get(key) or {}
        primary_key = family.get('primary_key') or key
        expected_work = expected_retained_work(
            key,
            result_by_key[key],
            current_baseline_row,
            after_projection,
            deterministically_excluded=primary_key in excluded_primary_keys,
            deal_row=deal_entries.get(primary_key) or {},
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

    baseline_present_key_count = sum(key in baseline_current_queue_by_key for key in all_keys)
    expected_ai_queue = baseline_ai_queue - baseline_present_key_count + len(retained)
    baseline_entries = (baseline_projection or {}).get('entries') or {}
    after_entries = after_projection.get('entries') or {}
    stale_keys = [key for key in all_keys if not current_reusable_by_key[key]]
    reusable_keys = [key for key in all_keys if current_reusable_by_key[key]]

    stale_projection_unchanged = all(
        (after_entries.get(key) or {}).get('status') == (baseline_entries.get(key) or {}).get('status')
        for key in stale_keys
    ) if baseline_projection is not None else not stale_keys
    stale_not_promoted_to_current_hit = all(
        (after_entries.get(key) or {}).get('status') != 'cache_hit'
        for key in stale_keys
    )
    stale_queue_exact = all(
        (
            key not in baseline_current_queue_by_key
            and key not in after_queue_by_key
        )
        or (
            key in baseline_current_queue_by_key
            and key in after_queue_by_key
            and _queue_identity(after_queue_by_key[key]) == _queue_identity(baseline_current_queue_by_key[key])
        )
        for key in stale_keys
    )
    reusable_are_hits = all(
        (after_entries.get(key) or {}).get('status') == 'cache_hit'
        for key in reusable_keys
    )

    checks = {
        'projection_complete': after_projection.get('complete_coverage') is True,
        'family_partition_complete': after_manifest.get('complete_family_partition') is True,
        'sale_end_state_consistent': sale_end_state_is_consistent(after_manifest),
        'missing_sale_end_is_nonblocking': (after_manifest.get('contract') or {}).get('missing_sale_end_does_not_exclude_candidate') is True,
        'safe_hits_increment_only_for_current_reusable_full_eval': after_projection.get('safe_cache_hit_count') == expected_safe_hits,
        'ai_required_decrement_only_for_current_reusable_full_eval': after_projection.get('ai_required_count') == expected_ai_required,
        'after_queue_has_unique_keys': not duplicate_after_keys,
        'ingested_key_retention_matches_negative_base_support_or_newer_live_state': not retention_mismatches,
        'ai_queue_count_exact': after_manifest.get('ai_queue_count') == expected_ai_queue,
        'queue_file_count_exact': len(after_queue) == expected_ai_queue,
        'current_reusable_ingested_keys_are_fit_cache_hits': reusable_are_hits,
        'older_pinned_result_does_not_become_current_live_cache_hit': stale_not_promoted_to_current_hit,
        'newer_live_projection_state_is_preserved_for_older_pinned_results': stale_projection_unchanged,
        'newer_live_work_remains_exact_for_next_work_unit': stale_queue_exact,
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
    resolved_pin_by_key = {}
    resolved_pinned_row_by_key = {}
    resolved_batch_pins = []
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
        try:
            resolved_pin, _pinned_projection, pinned_rows = resolve_pinned_work_unit(
                path,
                PROJECTION,
                QUEUE,
                ACTIVE_PIN,
                Path('.'),
            )
        except (ValueError, OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f'Pinned Taste work-unit proof failed for {path}: {exc}') from exc
        pinned_rows_by_key = {row['taste_subject_key']: row for row in pinned_rows}
        resolved_batch_pins.append(resolved_pin)
        batch_docs.append((path, doc, keys, resolved_pin))
        for result in results:
            key = result['key']
            result_by_key[key] = result
            resolved_pin_by_key[key] = resolved_pin
            pinned_row = pinned_rows_by_key.get(key)
            if pinned_row is None:
                raise SystemExit(f'Pinned Taste work-unit rows missing result key: {key}')
            resolved_pinned_row_by_key[key] = pinned_row
        all_keys.extend(keys)
        total_results += len(results)

    if len(set(all_keys)) != len(all_keys):
        raise SystemExit('Duplicate taste key across inbox files')

    proof_queue_by_key = dict(baseline_queue_by_key)
    for key in all_keys:
        proof_queue_by_key.setdefault(key, resolved_pinned_row_by_key[key])

    current_reusable_by_key = {
        key: result_is_reusable_for_current_projection(
            result_by_key[key],
            resolved_pin_by_key[key],
            baseline_projection,
            baseline_queue_by_key.get(key),
        )
        for key in all_keys
    }

    baseline_safe_hits = baseline_projection.get('safe_cache_hit_count')
    baseline_ai_required = baseline_projection.get('ai_required_count')
    baseline_ai_queue = baseline_manifest.get('ai_queue_count')
    if baseline_ai_queue != len(baseline_queue):
        raise SystemExit('Baseline manifest ai_queue_count does not match JSONL line count')

    # Each file is validated by the canonical ingest contract. Negative-only rows
    # cannot rewrite fit semantics because their accepted result shape omits them.
    for path, _doc, _keys, _pin in batch_docs:
        run('python', 'scripts/ingest_taste_results.py', '--input', str(path))

    rebuild_taste_consumers()

    after_projection = load_json(PROJECTION)
    after_manifest = load_json(MANIFEST)
    after_queue = read_jsonl(QUEUE)
    after_family_graph = load_json(FAMILY_GRAPH)
    after_deals = load_json(DEALS)

    checks, retained, retention_mismatches, expected_ai_queue, full_eval_count = build_transactional_proof_checks(
        all_keys=all_keys,
        result_by_key=result_by_key,
        baseline_queue_by_key=proof_queue_by_key,
        baseline_safe_hits=baseline_safe_hits,
        baseline_ai_required=baseline_ai_required,
        baseline_ai_queue=baseline_ai_queue,
        after_projection=after_projection,
        after_manifest=after_manifest,
        after_queue=after_queue,
        after_family_graph=after_family_graph,
        after_deals=after_deals,
        baseline_projection=baseline_projection,
        current_reusable_by_key=current_reusable_by_key,
        baseline_current_queue_by_key=baseline_queue_by_key,
    )
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print(json.dumps({
            'retained_ingest_keys': retained,
            'retention_mismatches': retention_mismatches,
            'current_reusable_by_key': current_reusable_by_key,
            'expected_ai_queue_count': expected_ai_queue,
            'actual_ai_queue_count': after_manifest.get('ai_queue_count'),
        }, ensure_ascii=False, indent=2))
        raise SystemExit(f'Taste inbox transactional proof failed: {failed}')

    normal_active_pins = [
        p for p in resolved_batch_pins
        if not p.get('grandfathered_legacy_package')
    ]
    completed_active_pin = None
    if normal_active_pins:
        hashes = {p.get('ordered_work_unit_sha256') for p in normal_active_pins}
        authorities = {p.get('authority_commit') for p in normal_active_pins}
        if len(hashes) != 1 or len(authorities) != 1:
            raise SystemExit('A single Taste transaction cannot retire multiple active pinned work-units')
        completed_active_pin = normal_active_pins[0]

    try:
        pin_transition = transition_active_pin_after_success(
            completed_active_pin,
            PROJECTION,
            QUEUE,
            None,
            ACTIVE_PIN,
        )
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f'Taste active pin retirement/next-pin preparation failed: {exc}') from exc

    batch_id = digest.hexdigest()[:20]
    next_pin = pin_transition.get('next_pin')
    retired_pin = pin_transition.get('retired_pin')
    receipt = {
        'schema_version': 3,
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
        'current_reusable_result_count': sum(bool(current_reusable_by_key[key]) for key in all_keys),
        'newer_live_pending_result_count': sum(not current_reusable_by_key[key] for key in all_keys),
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
        'pin_lifecycle': {
            'transition_status': pin_transition.get('status'),
            'retired_work_unit_sha256': None if retired_pin is None else retired_pin.get('ordered_work_unit_sha256'),
            'retired_profile_blob_sha': None if retired_pin is None else (retired_pin.get('bindings') or {}).get('profile_blob_sha'),
            'next_work_unit_sha256': None if next_pin is None else next_pin.get('ordered_work_unit_sha256'),
            'next_profile_blob_sha': None if next_pin is None else (next_pin.get('bindings') or {}).get('profile_blob_sha'),
            'legacy_grandfathered_input_does_not_retire_unrelated_active_pin': completed_active_pin is None,
        },
        'checks': checks,
    }
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = RECEIPT_DIR / f'{batch_id}.json'
    if receipt_path.exists():
        raise SystemExit(f'Receipt already exists for this exact batch: {receipt_path}')
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    previous_runtime_status = load_json(LATEST_RUNTIME_STATUS) if LATEST_RUNTIME_STATUS.exists() else None
    latest_runtime_status = build_runtime_status(receipt, previous_runtime_status)
    LATEST_RUNTIME_STATUS.write_text(
        json.dumps(latest_runtime_status, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8',
    )

    for path in inbox_files:
        path.unlink()

    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    print('TASTE_INBOX_TRANSACTION=PASS')


if __name__ == '__main__':
    main()
