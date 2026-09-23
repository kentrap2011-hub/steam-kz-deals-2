import json
import subprocess
import sys
from pathlib import Path

PAYLOAD = Path('data/production/pre_ai/chatgpt_payload.json')
STORE = Path('data/production/pre_ai/store_snapshot.json')
FAMILY = Path('data/production/pre_ai/family_graph.json')
PROGRESSIVE_CONTEXT = Path('data/production/pre_ai/progressive_candidate_context.jsonl')
VISUAL = Path('data/production/visual/current.json')
PROGRESSIVE_CONTRACT = Path('config/progressive_personalization_contract.json')
PASS1_STATE = Path('data/cache/progressive_pass1_state.json')
PASS2_STATE = Path('data/cache/progressive_pass2_state.json')

VISIBLE_STATES = {'analyzed_fit', 'analysis_incomplete', 'not_analyzed'}


def _read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _line_count(path):
    return sum(1 for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip())


def _blob(path):
    return subprocess.check_output(
        ['git', 'rev-parse', f'HEAD:{path}'],
        text=True,
    ).strip()


def source_integrity_ok(payload, store, family):
    source = payload.get('source_mailing_updated_at_utc')
    return bool(
        source
        and store.get('status') == 'complete'
        and family.get('status') == 'complete'
        and store.get('discovery_source_updated_at_utc') == source
        and family.get('source_updated_at_utc') == source
    )


def processing_status_valid(status, visible_count):
    if not isinstance(status, dict):
        return False
    if status.get('contract') != 'PROGRESSIVE-PERSONALIZED-DEALS-V1':
        return False
    if status.get('phase') != 'phase_b':
        return False
    required = (
        'total_current_candidates',
        'analyzed_success_count',
        'analyzed_fit_count',
        'analyzed_not_fit_count',
        'analysis_incomplete_count',
        'not_analyzed_count',
        'normal_visible_count',
        'pass1_total_scope',
        'pass1_attempted_count',
        'pass1_remaining_count',
        'fast_total_current_scope',
        'fast_attempted_count',
        'fast_completed_fit_count',
        'fast_completed_not_fit_count',
        'fast_incomplete_count',
        'fast_error_count',
        'fast_skipped_due_to_authoritative_deep_count',
        'fast_remaining_count',
        'deep_total_current_coverage_target',
        'deep_first_pass_attempted_count',
        'deep_authoritative_completed_count',
        'deep_completed_fit_count',
        'deep_completed_not_fit_count',
        'deep_incomplete_or_recovery_count',
        'deep_waiting_for_dossier_count',
        'deep_ready_or_pending_count',
        'deep_normal_first_pass_remaining_count',
        'deep_remaining_until_all_authoritative_count',
    )
    try:
        values = {key: int(status[key]) for key in required}
    except (KeyError, TypeError, ValueError):
        return False
    if values['total_current_candidates'] != (
        values['analyzed_fit_count']
        + values['analyzed_not_fit_count']
        + values['analysis_incomplete_count']
        + values['not_analyzed_count']
    ):
        return False
    if values['analyzed_success_count'] != (
        values['analyzed_fit_count'] + values['analyzed_not_fit_count']
    ):
        return False
    if values['normal_visible_count'] != (
        values['analyzed_fit_count']
        + values['analysis_incomplete_count']
        + values['not_analyzed_count']
    ):
        return False
    if values['pass1_total_scope'] != (
        values['pass1_attempted_count'] + values['pass1_remaining_count']
    ):
        return False
    if values['fast_total_current_scope'] != (
        values['fast_attempted_count']
        + values['fast_skipped_due_to_authoritative_deep_count']
        + values['fast_remaining_count']
    ):
        return False
    if values['fast_attempted_count'] != (
        values['fast_completed_fit_count']
        + values['fast_completed_not_fit_count']
        + values['fast_incomplete_count']
        + values['fast_error_count']
    ):
        return False
    if values['deep_first_pass_attempted_count'] + values['deep_normal_first_pass_remaining_count'] != (
        values['deep_total_current_coverage_target']
    ):
        return False
    if values['deep_authoritative_completed_count'] + values['deep_remaining_until_all_authoritative_count'] != (
        values['deep_total_current_coverage_target']
    ):
        return False
    if values['deep_authoritative_completed_count'] != (
        values['deep_completed_fit_count'] + values['deep_completed_not_fit_count']
    ):
        return False
    if bool(status.get('deep_normal_first_pass_complete')) != (
        values['deep_normal_first_pass_remaining_count'] == 0
    ):
        return False
    if bool(status.get('deep_all_current_authoritative_complete')) != (
        values['deep_remaining_until_all_authoritative_count'] == 0
    ):
        return False

    dossier_total = status.get('dossier_total_current_scope')
    if dossier_total is not None:
        try:
            if int(dossier_total) != (
                int(status['dossier_accepted_count'])
                + int(status['dossier_pending_count'])
                + int(status['dossier_failed_or_recovery_count'])
            ):
                return False
        except (KeyError, TypeError, ValueError):
            return False

    if status.get('pass1_active') is not True or status.get('pass2_active') is not True:
        return False
    return values['normal_visible_count'] == int(visible_count)

def progressive_visual_compatible(
    *,
    payload,
    store,
    family,
    visual,
    progressive_context_count,
    progressive_context_blob,
    progressive_contract_blob,
    pass1_state_blob,
    pass2_state_blob,
):
    if not source_integrity_ok(payload, store, family):
        return False, 'source_integrity_invalid'

    try:
        expected_count = int(payload.get('progressive_candidate_count'))
    except (TypeError, ValueError):
        return False, 'progressive_candidate_count_invalid'
    if expected_count != int(progressive_context_count):
        return False, 'progressive_candidate_context_count_mismatch'

    source = payload.get('source_mailing_updated_at_utc')
    if visual.get('source_mailing_updated_at_utc') != source:
        return False, 'visual_progressive_source_mismatch'

    progressive = visual.get('progressive_personalization')
    if not isinstance(progressive, dict):
        return False, 'progressive_state_block_missing'
    if (
        progressive.get('contract') != 'PROGRESSIVE-PERSONALIZED-DEALS-V1'
        or progressive.get('phase') != 'phase_b'
        or progressive.get('pass1_active') is not True
        or progressive.get('pass2_implemented') is not True
        or progressive.get('pass2_active') is not True
    ):
        return False, 'progressive_state_block_incompatible'

    items = visual.get('items')
    if not isinstance(items, list):
        return False, 'visual_items_invalid'
    if not processing_status_valid(visual.get('processing_status'), len(items)):
        return False, 'progressive_processing_status_invalid'

    for item in items:
        if not isinstance(item, dict):
            return False, 'visual_item_invalid'
        state = item.get('analysis_state')
        if state not in VISIBLE_STATES:
            return False, 'visible_analysis_state_missing_or_invalid'
        expected_tier = {'analyzed_fit': 1, 'analysis_incomplete': 2, 'not_analyzed': 3}[state]
        if item.get('analysis_tier') != expected_tier:
            return False, 'visible_analysis_tier_invalid'
        for field in (
            'fast_stage_state',
            'fast_stage_outcome',
            'dossier_stage_state',
            'deep_stage_state',
            'deep_stage_outcome',
            'deep_recovery_state',
            'effective_analysis_source',
        ):
            if field not in item:
                return False, f'visible_stage_field_missing:{field}'

    contract = visual.get('production_contract') or {}
    if contract.get('source_progressive_candidate_context_blob_sha') != progressive_context_blob:
        return False, 'progressive_context_provenance_mismatch'
    if contract.get('progressive_personalization_contract_blob_sha') != progressive_contract_blob:
        return False, 'progressive_contract_provenance_mismatch'
    if contract.get('progressive_pass1_state_blob_sha') != pass1_state_blob:
        return False, 'progressive_pass1_state_provenance_mismatch'
    if contract.get('progressive_pass2_state_blob_sha') != pass2_state_blob:
        return False, 'progressive_pass2_state_provenance_mismatch'

    return True, 'compatible_progressive_visual'


def classify_current_files():
    try:
        payload = _read(PAYLOAD)
        store = _read(STORE)
        family = _read(FAMILY)
        visual = _read(VISUAL)
        context_count = _line_count(PROGRESSIVE_CONTEXT)
        context_blob = _blob(PROGRESSIVE_CONTEXT)
        contract_blob = _blob(PROGRESSIVE_CONTRACT)
        pass1_state_blob = _blob(PASS1_STATE)
        pass2_state_blob = _blob(PASS2_STATE)
    except Exception as exc:
        return {
            'source_integrity_ok': False,
            'compatible': False,
            'full_progressive_build_required': False,
            'reason': f'classification_input_error:{type(exc).__name__}',
        }

    integrity = source_integrity_ok(payload, store, family)
    compatible, reason = progressive_visual_compatible(
        payload=payload,
        store=store,
        family=family,
        visual=visual,
        progressive_context_count=context_count,
        progressive_context_blob=context_blob,
        progressive_contract_blob=contract_blob,
        pass1_state_blob=pass1_state_blob,
        pass2_state_blob=pass2_state_blob,
    )
    return {
        'source_integrity_ok': integrity,
        'compatible': compatible,
        # Invalid deterministic source must fail in the normal producer path;
        # this helper must not convert malformed source state into a bounded refresh.
        'full_progressive_build_required': bool(integrity and not compatible),
        'reason': reason,
    }


def main():
    result = classify_current_files()
    print(
        'PROGRESSIVE_SCOPE '
        f"source_integrity_ok={str(result['source_integrity_ok']).lower()} "
        f"compatible={str(result['compatible']).lower()} "
        f"full_progressive_build_required={str(result['full_progressive_build_required']).lower()} "
        f"reason={result['reason']}",
        file=sys.stderr,
    )
    print('true' if result['full_progressive_build_required'] else 'false')


if __name__ == '__main__':
    main()
