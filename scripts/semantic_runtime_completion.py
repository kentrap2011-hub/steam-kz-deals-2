from datetime import datetime, timezone

RUNTIME_OWNER = 'scheduled ChatGPT production task'
OWNER_CONTRACT_REF = 'config/execution_ownership_contract.json#scheduled_chatgpt_runtime_data_plane'
PLATFORM_STATE_UNKNOWN = 'not_exposed_to_repository'


def _parse_utc(value):
    if not value:
        return None
    text = str(value).strip()
    if text.endswith('Z'):
        text = text[:-1] + '+00:00'
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_semantic_completeness(payload, now=None):
    unresolved = int(payload.get('ai_queue_count') or 0)
    resolved = int(payload.get('ready_without_ai_count') or 0)
    total_relevant = unresolved + resolved
    partition_complete = payload.get('complete_family_partition') is True
    source_stamp = payload.get('source_mailing_updated_at_utc')
    sufficiently_complete = partition_complete and unresolved == 0
    status = 'complete' if sufficiently_complete else 'degraded'

    age_seconds = None
    if unresolved and source_stamp:
        source_time = _parse_utc(source_stamp)
        current_time = now or datetime.now(timezone.utc)
        if current_time.tzinfo is None:
            current_time = current_time.replace(tzinfo=timezone.utc)
        current_time = current_time.astimezone(timezone.utc)
        if source_time is not None:
            age_seconds = max(0, int((current_time - source_time).total_seconds()))

    return {
        'status': status,
        'scope_partition_complete': partition_complete,
        'sufficiently_complete_for_publication': sufficiently_complete,
        'unresolved_semantic_count': unresolved,
        'resolved_semantic_count': resolved,
        'total_relevant_semantic_scope': total_relevant,
        'source_family_count': int(payload.get('source_family_count') or 0),
        'unresolved_scope_source_mailing_updated_at_utc': source_stamp if unresolved else None,
        'unresolved_scope_age_seconds': age_seconds,
        'unresolved_age_basis': 'source_mailing_updated_at_utc' if unresolved and source_stamp else None,
    }


def build_runtime_status(receipt, previous=None):
    checks = receipt.get('checks') or {}
    checks_ok = bool(checks) and all(value is True for value in checks.values())
    if receipt.get('status') != 'complete' or not checks_ok:
        raise ValueError('Runtime status requires a successfully validated transactional receipt')

    processed_at = receipt.get('processed_at_utc')
    if not processed_at:
        raise ValueError('Runtime receipt requires processed_at_utc')

    baseline = receipt.get('baseline') or {}
    after = receipt.get('after') or {}
    queue_before = baseline.get('ai_queue_count')
    queue_after = after.get('ai_queue_count')
    queue_delta = None
    if isinstance(queue_before, int) and isinstance(queue_after, int):
        queue_delta = queue_before - queue_after

    result_count = int(receipt.get('result_count') or 0)
    accepted_progress = result_count > 0
    previous = previous if isinstance(previous, dict) else {}

    last_progress_at = previous.get('last_accepted_semantic_progress_at_utc')
    last_progress_source = previous.get('last_accepted_source_mailing_updated_at_utc')
    last_progress_batch = previous.get('last_accepted_batch_id')
    if accepted_progress:
        last_progress_at = processed_at
        last_progress_source = receipt.get('source_mailing_updated_at_utc')
        last_progress_batch = receipt.get('batch_id')

    return {
        'schema_version': 1,
        'status': 'observed',
        'runtime_owner': RUNTIME_OWNER,
        'owner_contract_ref': OWNER_CONTRACT_REF,
        'owner_expected_by_contract': True,
        'scheduler_platform_enabled_state': PLATFORM_STATE_UNKNOWN,
        'expected_cadence_or_next_run_state': PLATFORM_STATE_UNKNOWN,
        'last_successful_semantic_execution_at_utc': processed_at,
        'last_successful_batch_id': receipt.get('batch_id'),
        'last_successful_source_mailing_updated_at_utc': receipt.get('source_mailing_updated_at_utc'),
        'last_accepted_semantic_progress_at_utc': last_progress_at,
        'last_accepted_batch_id': last_progress_batch,
        'last_accepted_source_mailing_updated_at_utc': last_progress_source,
        'last_accepted_result_count': result_count if accepted_progress else 0,
        'last_queue_before_count': queue_before,
        'last_queue_after_count': queue_after,
        'last_queue_delta_count': queue_delta,
        'transactional_checks_all_passed': checks_ok,
        'accepted_progress_in_last_execution': accepted_progress,
        'queue_presence_is_not_heartbeat': True,
    }


def build_runtime_observability(latest_status, current_source_stamp):
    latest = latest_status if isinstance(latest_status, dict) else {}
    last_progress_source = latest.get('last_accepted_source_mailing_updated_at_utc')
    current_scope_progress = bool(
        latest.get('last_accepted_semantic_progress_at_utc')
        and current_source_stamp
        and last_progress_source == current_source_stamp
    )
    return {
        'status': 'current_scope_progress_observed' if current_scope_progress else 'no_current_scope_progress_observed',
        'runtime_owner': latest.get('runtime_owner') or RUNTIME_OWNER,
        'owner_contract_ref': latest.get('owner_contract_ref') or OWNER_CONTRACT_REF,
        'owner_expected_by_contract': True,
        'scheduler_platform_enabled_state': latest.get('scheduler_platform_enabled_state') or PLATFORM_STATE_UNKNOWN,
        'expected_cadence_or_next_run_state': latest.get('expected_cadence_or_next_run_state') or PLATFORM_STATE_UNKNOWN,
        'latest_runtime_status_path': 'data/cache/taste_ingest_receipts/latest_runtime_status.json',
        'last_successful_semantic_execution_at_utc': latest.get('last_successful_semantic_execution_at_utc'),
        'last_accepted_semantic_progress_at_utc': latest.get('last_accepted_semantic_progress_at_utc'),
        'last_accepted_source_mailing_updated_at_utc': last_progress_source,
        'current_scope_source_mailing_updated_at_utc': current_source_stamp,
        'current_scope_progress_observed': current_scope_progress,
        'last_queue_before_count': latest.get('last_queue_before_count'),
        'last_queue_after_count': latest.get('last_queue_after_count'),
        'last_queue_delta_count': latest.get('last_queue_delta_count'),
        'queue_presence_is_not_heartbeat': True,
    }


def apply_payload_status(payload, latest_runtime_status=None, now=None):
    semantic = build_semantic_completeness(payload, now=now)
    payload['schema_version'] = max(int(payload.get('schema_version') or 0), 5)
    payload['status'] = semantic['status']
    payload['semantic_completeness'] = semantic
    payload['semantic_runtime_observability'] = build_runtime_observability(
        latest_runtime_status,
        payload.get('source_mailing_updated_at_utc'),
    )
    return payload


def apply_visual_semantic_status(visual, payload):
    semantic = payload.get('semantic_completeness') if isinstance(payload, dict) else None
    if not isinstance(semantic, dict):
        semantic = build_semantic_completeness(payload or {})
    runtime = payload.get('semantic_runtime_observability') if isinstance(payload, dict) else None
    visual['schema_version'] = max(int(visual.get('schema_version') or 0), 4)
    visual['status'] = 'complete' if semantic.get('sufficiently_complete_for_publication') is True else 'degraded'
    visual['semantic_completeness'] = semantic
    visual['semantic_runtime_observability'] = runtime or build_runtime_observability(
        None,
        (payload or {}).get('source_mailing_updated_at_utc'),
    )
    return visual
