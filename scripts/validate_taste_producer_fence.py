import json
import tempfile
from pathlib import Path

from taste_producer_fence import (
    EXPECTED_CONTRACT,
    load_active_producer_fence,
    validate_taste_inbox,
    validate_taste_producer_envelope,
)


def expect_reject(doc, fence):
    try:
        validate_taste_producer_envelope(doc, source='<synthetic regression>', fence=fence)
    except SystemExit:
        return True
    raise AssertionError(f'producer fence unexpectedly accepted: {doc!r}')


def expect_inbox_reject(inbox_dir):
    try:
        validate_taste_inbox(inbox_dir)
    except SystemExit:
        return True
    raise AssertionError(f'Taste inbox unexpectedly accepted active invalid content: {inbox_dir}')


def validate_historical_archive_lifecycle(current, fence):
    stale = dict(
        current,
        producer_id='chatgpt_scheduled_task:historical-generation-1',
        producer_generation=max(1, fence['producer_generation'] - 1),
    )

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        active = root / 'data' / 'ai_inbox' / 'taste'
        archive = root / 'data' / 'ai_archive' / 'taste' / 'generation-1'
        active.mkdir(parents=True)
        archive.mkdir(parents=True)

        (active / 'current.json').write_text(json.dumps(current), encoding='utf-8')
        (archive / 'stale.json').write_text(json.dumps(stale), encoding='utf-8')

        _validated_fence, active_files = validate_taste_inbox(active)
        archive_does_not_enter_active_scan = [path.name for path in active_files] == ['current.json']
        if not archive_does_not_enter_active_scan:
            raise AssertionError('historical archive content entered active Taste inbox scan')

        active_stale = active / 'stale.json'
        active_stale.write_text(json.dumps(stale), encoding='utf-8')
        active_old_generation_rejected = expect_inbox_reject(active)
        active_stale.unlink()

        malformed = active / 'malformed.json'
        malformed.write_text('{not-json', encoding='utf-8')
        active_malformed_rejected = expect_inbox_reject(active)

    return {
        'historical_archive_excluded_from_active_scan': archive_does_not_enter_active_scan,
        'active_old_generation_still_rejected': active_old_generation_rejected,
        'active_malformed_file_still_rejected': active_malformed_rejected,
    }


def main():
    contract = json.loads(open('config/taste_result_contract.json', encoding='utf-8').read())
    assert contract.get('contract') == EXPECTED_CONTRACT

    fence = load_active_producer_fence()
    current = {
        'producer_id': fence['producer_id'],
        'producer_generation': fence['producer_generation'],
        'results': [{'key': 'synthetic-current-row'}],
    }
    validate_taste_producer_envelope(current, source='<synthetic regression>', fence=fence)

    wrong_id = dict(current, producer_id='chatgpt_scheduled_task:stale-or-wrong')
    missing_id = dict(current)
    missing_id.pop('producer_id')
    wrong_generation = dict(current, producer_generation=fence['producer_generation'] + 1)
    missing_generation = dict(current)
    missing_generation.pop('producer_generation')
    bool_generation = dict(current, producer_generation=True)

    rejected = {
        'wrong_producer_id': expect_reject(wrong_id, fence),
        'missing_legacy_producer_id': expect_reject(missing_id, fence),
        'wrong_producer_generation': expect_reject(wrong_generation, fence),
        'missing_legacy_producer_generation': expect_reject(missing_generation, fence),
        'bool_generation_not_equal_to_one': expect_reject(bool_generation, fence),
    }
    assert all(rejected.values())

    historical_archive_lifecycle = validate_historical_archive_lifecycle(current, fence)
    assert all(historical_archive_lifecycle.values())

    print(json.dumps({
        'status': 'PASS',
        'contract': contract['contract'],
        'correct_active_producer_accepted': True,
        'rejected': rejected,
        'historical_archive_lifecycle': historical_archive_lifecycle,
    }, indent=2))
    print('TASTE_PRODUCER_FENCE_REGRESSION=PASS')


if __name__ == '__main__':
    main()
