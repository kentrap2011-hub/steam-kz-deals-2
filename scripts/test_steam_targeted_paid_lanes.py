"""Deterministic Stage 1/3/4/5 tests: no global DLC, independent Sub value."""
import json
import tempfile
from pathlib import Path

import build_final_visual_payload as visual
import build_pre_ai_family_graph as families
import build_fixed_package_purchase_options as fixed
import priority_ranking
import steam_partial_publish_runner as collector
import steam_targeted_paid_lanes as targeted


def paid(key, *, reviews=8000, percent=95, price=1000, discount=75):
    return dict(
        key=key, appid=key.split('_', 1)[1], title='Test game',
        final_kzt=price, discount_percent=discount, tag_ids=[19, 4182],
        search_review_positive=percent, search_review_count=reviews,
        global_review_positive=percent, global_review_count=reviews,
        russian_review_positive=percent, russian_review_count=reviews,
        release_date='', url='',
    )


def check_base_targeted_dlc():
    core = collector.load_core()
    assert tuple(core['SEARCH_CATEGORY_TYPES']) == ('games',)
    assert core['SEARCH_CATEGORY_TYPES']['games'] == '998'
    assert core['PAID_DISCOVERY_POLICY']['dlc_discovery']['global_category1_21_traversal'] is False
    accepted = paid('App_100')
    low = paid('App_200', reviews=0)
    bases = targeted.suitable_base_ids([accepted, low], set(), core, __import__('datetime').date(2026, 10, 26))
    assert bases == ['100']

    observed = []
    fixtures = {
        '100': {'type': 'game', 'dlc': [300, 301, 302]},
        '300': {'type': 'dlc', 'name': 'Useful chapter',
                'fullgame': {'appid': 100},
                'price_overview': {'currency': 'KZT', 'final': 25000, 'discount_percent': 85}},
        '301': {'type': 'dlc', 'price_overview': {'currency': 'KZT', 'final': 550000, 'discount_percent': 90}},
        '302': {'type': 'dlc', 'price_overview': {'currency': 'KZT', 'final': 30000, 'discount_percent': 40}},
    }
    def fetch(appid):
        observed.append(appid)
        return fixtures[appid]
    dlc, stats = targeted.discover_dlc_for_bases(bases, core, fetch=fetch)
    assert sorted(dlc) == ['App_300']
    assert dlc['App_300']['verified_base_appids'] == ['100']
    assert stats['related_dlc_unique_ids'] == 3
    assert stats['dlc_rejected_after_paid_gate'] == 2
    assert set(observed) == set(fixtures)
    assert stats['relation_complete'] is True

    wrong = dict(fixtures)
    wrong['300'] = dict(fixtures['300'], fullgame={'appid': 999})
    try:
        targeted.discover_dlc_for_bases(bases, core, fetch=lambda key: wrong[key])
    except RuntimeError:
        pass
    else:
        raise AssertionError('contradictory parent relation accepted')
    try:
        targeted.discover_dlc_for_bases(bases, core, fetch=lambda key: (_ for _ in ()).throw(RuntimeError('429')))
    except RuntimeError:
        pass
    else:
        raise AssertionError('incomplete parent should fail closed')
    assert targeted.discover_dlc_for_bases([], core, fetch=lambda key: 1)[0] == {}


def check_conservative_obscure_rescue_and_package():
    assert targeted.candidate_needs_obscure_gate(paid('App_1', reviews=20, percent=85))
    assert not targeted.candidate_needs_obscure_gate(paid('App_1', reviews=11, percent=95))
    assert not targeted.candidate_needs_obscure_gate(paid('App_1', reviews=0, price=500, discount=95))
    assert not targeted.candidate_needs_obscure_gate({**paid('App_1'), 'search_review_count': None})
    core = collector.load_core()
    bundle = paid('Sub_42', reviews=0, percent=0, price=100, discount=95)
    packages, stats = targeted.classify_discounted_package_rows(
        [bundle, paid('App_33'), paid('Sub_43', price=4501)], core
    )
    assert list(packages) == ['Sub_42']
    assert stats['bundle_offers_seen'] == 2 and stats['bundle_offers_survived_cheap_gate'] == 1


def check_five_middling_games_package_below_individual_cutoff():
    # All five members are ordinary base games that are NOT on a standalone
    # current sale, but their exactly priced 95%-off bundle is one candidate.
    names = [f'Unpromoted member {i}' for i in range(5)]
    package_store = {
        'id': 42, 'name': 'Five strong-value games',
        'included_appids': [501, 502, 503, 504, 505],
        'purchase_options': [{
            'packageid': 42, 'discount_pct': 95,
            'final_price_in_cents': 10000, 'original_price_in_cents': 200000,
        }],
    }
    classified, reason = fixed.classify_package(
        42, package_store, set(), set(), 0
    )
    assert reason is None
    assert classified['independent_current_sale_package'] is True
    assert classified['included_appids'] == [501, 502, 503, 504, 505]
    assert len(classified['members_not_assumed_suitable']) == 5
    assert classified['member_semantic_evidence_required'] is True

    # Ranking uses the existing canonical score, never a hard top-100 cutoff
    # on Steam search or a fabricated vote for package members.
    games = [
        {
            'id': f'game:{i}', 'title': f'Candidate {i:03}',
            'fit': 'moderate',
            'discount_percent': 50, 'current_price_kzt': 2500,
            'current_price_rub': 500, 'original_price_rub': 600,
        } for i in range(105)
    ]
    package_game = {
        'id': 'package:Sub_42', 'title': 'Five strong-value games',
        'fit': 'moderate', 'current_price_rub': 10,
        'original_price_rub': 1000, 'discount_percent': 95,
        'current_price_kzt': 100,
    }
    ranked, _ = priority_ranking.apply_final_priority_order(games + [package_game])
    assert ranked[0]['id'] == 'package:Sub_42'
    data = {'items': ranked, 'processing_status': {'deep_total_current_coverage_target': 106}}
    visual.cap_visible_paid_offers(data, full_ranked_scope=True)
    assert data['item_count'] == 100
    assert data['items'][0]['id'] == 'package:Sub_42'
    assert data['visible_paid_publication']['hidden_below_visible_line_count'] == 6


def check_independent_package_family_needs_semantic_not_external_base():
    contract = json.loads(Path('config/offer_family_contract.json').read_text(encoding='utf-8'))
    rule = {'mechanical_kind': 'package',
            'package_appids': ['501','502','503','504','505'],
            'representative_appid': None}
    selected = families.resolve(
        {'Sub_42'},
        {'Sub_42': {'appid': '', 'title': 'Five excellent games'}},
        {'Sub_42': {
            'final_kzt': 100, 'discount_percent': 95,
            'discount_end_utc': None, 'discount_end_europe_berlin': None,
        }},
        {'Sub_42': {'store_name': 'Five excellent games'}},
        {'Sub_42': rule}, contract
    )
    assert len(selected) == 1
    assert selected[0]['family_type'] == 'package_without_candidate_base'
    assert selected[0]['requires_ai_base_support'] is False
    assert selected[0]['all_member_keys'] == ['Sub_42']
    assert selected[0]['primary_final_kzt'] == 100


def check_direct_subs_are_discoverable_without_current_app():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        file = root / 'chunk_001.tsv'
        file.write_text('Sub_42\t\nApp_100\t100\nSub_43\t\n', encoding='utf-8')
        index = {
            'columns': ['key', 'appid'], 'chunk_count': 1,
            'chunk_pattern': str(root / 'chunk_NNN.tsv'),
        }
        assert fixed.directly_discounted_subids(index) == [42, 43]


def main():
    check_base_targeted_dlc()
    check_conservative_obscure_rescue_and_package()
    check_five_middling_games_package_below_individual_cutoff()
    check_direct_subs_are_discoverable_without_current_app()
    check_independent_package_family_needs_semantic_not_external_base()
    print('targeted Steam KZ DLC and independent package 5/5 PASS')


if __name__ == '__main__':
    main()
