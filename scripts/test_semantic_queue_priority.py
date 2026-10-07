import copy
import json
from pathlib import Path

import build_progressive_pass2_work as producer


CONTRACT = json.loads(
    Path('config/progressive_pass2_contract.json').read_text(encoding='utf-8')
)


def context(
    family_id,
    *,
    rating=90.0,
    reviews=1000,
    price=500,
    discount=50,
    wishlist=False,
    family_type='game',
):
    return {
        'family_id': family_id,
        'family_type': family_type,
        'purchase': {
            'current_price_rub_display': price,
            'discount_percent': discount,
        },
        'context_only': {
            'wishlist': wishlist,
            'reviews': {
                'global_positive_percent': rating,
                'global_count': reviews,
            },
        },
    }


def priority(row):
    return producer.semantic_queue_priority(row, CONTRACT['ordering'])


def item(family_id, work_id=None):
    return {
        'family_id': family_id,
        'work_id': work_id or ('work:' + family_id),
        'work_mode': 'normal_first_pass',
        'authorization_id': 'auth:' + family_id,
    }


def main():
    ordering = CONTRACT['ordering']
    assert ordering['owner'] == 'github'
    assert ordering['policy_id'] == 'semantic_queue_priority_v1'
    assert ordering['changes_eligibility_or_scope'] is False
    assert ordering['hard_top_n'] is False
    assert ordering['sale_expiry_used_for_priority'] is False
    assert ordering['changes_site_ranking'] is False
    assert ordering['priority_score']['personal_taste_signal_used'] is False

    # QUEUE-01: pure ordering preserves the exact eligible candidate set and bindings.
    source_items = [
        item('game:z'),
        item('game:a'),
        item('game:m'),
    ]
    contexts = {
        row['family_id']: context(row['family_id'])
        for row in source_items
    }
    before = copy.deepcopy(source_items)
    ordered = producer.order_normal_items(
        source_items,
        contexts,
        {'entries': {}},
        CONTRACT,
    )
    assert len(ordered) == len(source_items)
    assert {row['family_id'] for row in ordered} == {row['family_id'] for row in source_items}
    assert {row['work_id'] for row in ordered} == {row['work_id'] for row in source_items}
    assert source_items == before
    assert all('deferred_reserve' not in row for row in ordered)
    assert all('excluded' not in row for row in ordered)
    assert [row['sequence'] for row in ordered] == list(range(1, len(ordered) + 1))

    # QUEUE-02: no-authoritative-Deep-history cohort always precedes a family with
    # accepted authoritative Deep history when commercial/quality inputs are equal.
    history_state = {
        'entries': {
            'game:seen-fit': {
                'authoritative_completed': True,
                'outcome': 'analyzed_fit',
            },
            'game:seen-not-fit': {
                'authoritative_completed': True,
                'outcome': 'analyzed_not_fit',
            },
            'game:incomplete': {
                'authoritative_completed': False,
                'outcome': 'analysis_incomplete',
                'recovery_owned': True,
            },
            'game:legacy-revision': {
                'authoritative_completed': False,
                'outcome': 'analysis_incomplete',
                'revision_history': [
                    {
                        'revision_kind': 'pre_legacy_full_reanalysis',
                        'state': {
                            'authoritative_completed': True,
                            'outcome': 'analyzed_fit',
                        },
                    }
                ],
            },
        },
    }
    assert producer.has_authoritative_deep_history(history_state, 'game:seen-fit') is True
    assert producer.has_authoritative_deep_history(history_state, 'game:seen-not-fit') is True
    assert producer.has_authoritative_deep_history(history_state, 'game:legacy-revision') is True
    assert producer.has_authoritative_deep_history(history_state, 'game:incomplete') is False
    assert producer.has_authoritative_deep_history(history_state, 'game:transport-failed') is False

    equal_contexts = {
        family_id: context(family_id)
        for family_id in ('game:never', 'game:seen-fit')
    }
    cohort_order = producer.order_normal_items(
        [item('game:seen-fit'), item('game:never')],
        equal_contexts,
        history_state,
        CONTRACT,
    )
    assert [row['family_id'] for row in cohort_order] == ['game:never', 'game:seen-fit']

    # QUEUE-03: Steam rating is monotonic.
    low_rating = priority(context('rating-low', rating=80.0))
    high_rating = priority(context('rating-high', rating=90.0))
    assert high_rating['components']['steam_positive_rating'] > low_rating['components']['steam_positive_rating']
    assert high_rating['score'] > low_rating['score']

    # QUEUE-04: review evidence is monotonic and logarithmically bounded, not linear popularity.
    r100 = priority(context('r100', reviews=100))
    r1000 = priority(context('r1000', reviews=1000))
    r10000 = priority(context('r10000', reviews=10000))
    assert r1000['components']['steam_review_confidence'] > r100['components']['steam_review_confidence']
    assert r10000['components']['steam_review_confidence'] > r1000['components']['steam_review_confidence']
    assert r10000['components']['steam_review_confidence'] / r100['components']['steam_review_confidence'] < 3.0
    assert priority(context('rcap', reviews=10_000_000))['components']['steam_review_confidence'] == 1.0

    # QUEUE-05: lower current price never worsens priority; use the existing canonical
    # price bands rather than inventing a second purchase-price scale.
    cheap = priority(context('cheap', price=100))
    expensive = priority(context('expensive', price=700))
    assert cheap['components']['current_price'] > expensive['components']['current_price']
    assert cheap['score'] > expensive['score']

    # QUEUE-06: higher current discount is monotonic.
    d50 = priority(context('d50', discount=50))
    d75 = priority(context('d75', discount=75))
    assert d75['components']['current_discount'] > d50['components']['current_discount']
    assert d75['score'] > d50['score']

    # QUEUE-07: exact ties use stable family_id ascending.
    tie_contexts = {
        'game:b': context('game:b'),
        'game:a': context('game:a'),
    }
    tied = producer.order_normal_items(
        [item('game:b'), item('game:a')],
        tie_contexts,
        {'entries': {}},
        CONTRACT,
    )
    assert [row['family_id'] for row in tied] == ['game:a', 'game:b']

    # QUEUE-08: Wishlist/package/DLC lanes are not scope gates here. The orderer
    # receives and returns every already-eligible item exactly once.
    lane_items = [
        item('wishlist:game'),
        item('package:sub'),
        item('dlc:story'),
    ]
    lane_contexts = {
        'wishlist:game': context('wishlist:game', wishlist=True),
        'package:sub': context('package:sub', family_type='package'),
        'dlc:story': context('dlc:story', family_type='dlc'),
    }
    lane_ordered = producer.order_normal_items(
        lane_items,
        lane_contexts,
        {'entries': {}},
        CONTRACT,
    )
    assert {row['family_id'] for row in lane_ordered} == {
        'wishlist:game',
        'package:sub',
        'dlc:story',
    }

    # QUEUE-09: authoritative fit/not-fit state is read-only input to ordering.
    state_before = copy.deepcopy(history_state)
    producer.order_normal_items(
        [item('game:seen-fit'), item('game:seen-not-fit'), item('game:incomplete')],
        {
            'game:seen-fit': context('game:seen-fit'),
            'game:seen-not-fit': context('game:seen-not-fit'),
            'game:incomplete': context('game:incomplete'),
        },
        history_state,
        CONTRACT,
    )
    assert history_state == state_before

    # QUEUE-10: operational ordering does not reach into frozen Deep Stage 1/2
    # contracts or worker prompts.
    producer_text = Path('scripts/build_progressive_pass2_work.py').read_text(encoding='utf-8')
    for forbidden in (
        'deep_stage1_contract.json',
        'deep_stage2_contract.json',
        'deep_stage1_manual_worker_prompt',
        'deep_stage2_manual_worker_prompt',
    ):
        assert forbidden not in producer_text

    print('semantic queue priority QUEUE-01..10: ok')


if __name__ == '__main__':
    main()
