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
    if status.get('phase') != 'phase_a':
        return False
    required = (
        'total_current_candidates',
        'analyzed_success_count',
        'analyzed_fit_count',
        'analyzed_not_fit_count',
        'analysis_incomplete_count',
        'not_analyzed_count',
        'normal_visible_count',
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
        or progressive.get('phase') != 'phase_a'
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

    contract = visual.get('production_contract') or {}
    if contract.get('source_progressive_candidate_context_blob_sha') != progressive_context_blob:
        return False, 'progressive_context_provenance_mismatch'
    if contract.get('progressive_personalization_contract_blob_sha') != progressive_contract_blob:
        return False, 'progressive_contract_provenance_mismatch'

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
