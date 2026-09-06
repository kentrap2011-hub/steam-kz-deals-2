import json

from taste_producer_fence import (
    EXPECTED_CONTRACT,
    load_active_producer_fence,
    validate_taste_producer_envelope,
)


def expect_reject(doc, fence):
    try:
        validate_taste_producer_envelope(doc, source='<synthetic regression>', fence=fence)
    except SystemExit:
        return True
    raise AssertionError(f'producer fence unexpectedly accepted: {doc!r}')


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

    print(json.dumps({
        'status': 'PASS',
        'contract': contract['contract'],
        'correct_active_producer_accepted': True,
        'rejected': rejected,
    }, indent=2))
    print('TASTE_PRODUCER_FENCE_REGRESSION=PASS')


if __name__ == '__main__':
    main()
