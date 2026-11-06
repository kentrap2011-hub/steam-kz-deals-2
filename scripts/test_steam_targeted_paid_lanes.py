"""Deterministic Stage 1/3/4/5 tests: no global DLC, independent Sub value."""
import io
import json
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
from unittest.mock import patch

import requests

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




def check_dlc_no_price_skips_only_verified_absence():
    """App_201877 fixture: no price is not foreign currency; siblings continue."""
    core = collector.load_core()
    sale = {
        'steam_appid': 300, 'type': 'dlc', 'name': 'On-sale story DLC',
        'fullgame': {'appid': 100},
        'price_overview': {'currency': 'KZT', 'final': 25000,
                           'discount_percent': 85},
    }
    parent = {'steam_appid': 100, 'type': 'game',
              'dlc': [201877, 300, 301, 302, 300]}
    no_price = {'steam_appid': 201877, 'type': 'dlc',
                'name': 'App_201877 (synthetic no-price fixture)',
                'fullgame': {'appid': 100}}
    fixtures = {
        '100': parent, '201877': no_price, '300': sale,
        '301': dict(sale, steam_appid=301,
                    price_overview={'currency': 'KZT', 'final': 550000,
                                    'discount_percent': 90}),
        '302': dict(sale, steam_appid=302,
                    price_overview={'currency': 'KZT', 'final': 30000,
                                    'discount_percent': 40}),
    }
    # Distinguish absent, explicit null and precisely empty object. No real
    # Steam appdetails body for 201877 was preserved in the failing live run.
    for variant in ('missing', 'null', 'empty'):
        child = dict(no_price)
        if variant == 'null':
            child['price_overview'] = None
        elif variant == 'empty':
            child['price_overview'] = {}
        current = dict(fixtures, **{'201877': child})
        calls = []
        def fetch(appid):
            calls.append(appid)
            return current[appid]
        dlc, stats = targeted.discover_dlc_for_bases(['100'], core, fetch=fetch)
        assert list(dlc) == ['App_300'], (variant, dlc)
        assert dlc['App_300']['final_kzt'] == 250
        assert dlc['App_300']['discount_percent'] == 85
        assert dlc['App_300']['verified_base_appids'] == ['100']
        assert calls.count('201877') == calls.count('300') == 1
        assert set(calls) == set(current)  # no early abort; complete child scope
        assert stats['admitted_base_count'] == stats['parent_relation_lookups'] == 1
        assert stats['related_dlc_unique_ids'] == stats['dlc_price_lookups'] == 4
        assert stats['dlc_accepted_after_paid_gate'] == 1
        assert stats['dlc_rejected_after_paid_gate'] == 3
        assert stats['relation_complete'] is True

    def must_fail(child, label, *, parent_override=None):
        data = dict(fixtures, **{'201877': child})
        if parent_override is not None:
            data['100'] = parent_override
        try:
            targeted.discover_dlc_for_bases(
                ['100'], core, fetch=lambda appid: data[appid]
            )
        except RuntimeError:
            return
        raise AssertionError(f'{label}: unsafe DLC data was treated as no-price')

    # A value/marker is NOT an empty price. Missing KZT fields, foreign currency,
    # wrong types (including bool which is an int subclass), and malformed
    # structures all retain the fail-closed collector behavior.
    unsafe_prices = [
        {'currency': 'RUB', 'final': 25000, 'discount_percent': 85},
        {'currency': 'USD', 'final': 25000, 'discount_percent': 85},
        {'currency': 'EUR'},
        {'final': 25000, 'discount_percent': 85},
        {'currency': 'KZT'},
        {'currency': 'KZT', 'final': 25000},
        {'currency': 'KZT', 'discount_percent': 85},
        {'currency': 'KZT', 'final': None, 'discount_percent': 85},
        {'currency': 'KZT', 'final': True, 'discount_percent': 85},
        {'currency': 'KZT', 'final': 25000, 'discount_percent': False},
        {'currency': 'KZT', 'final': 25000, 'discount_percent': '85'},
        [], 'not a price', 0, False,
    ]
    for price in unsafe_prices:
        must_fail(dict(no_price, price_overview=price), repr(price))
    # Identity, parent relationship and base-game type must also fail even
    # when the DLC is otherwise unpriced.
    must_fail(dict(no_price, steam_appid=999), 'incorrect child AppID')
    must_fail(dict(no_price, fullgame={'appid': 999}), 'contradictory fullgame')
    must_fail(dict(no_price, fullgame='malformed'), 'invalid fullgame type')
    must_fail(no_price, 'incorrect parent type',
              parent_override={'steam_appid': 100, 'type': 'dlc',
                               'dlc': [201877]})

def check_dlc_membership_identity_regressions():
    """Duplicate exact membership is safe; malformed/contradictory identity is not."""
    core = collector.load_core()
    valid_dlc = {
        'type': 'dlc', 'steam_appid': 300, 'name': 'Verified chapter',
        'fullgame': {'appid': 100},
        'price_overview': {'currency': 'KZT', 'final': 25000, 'discount_percent': 85},
    }
    fixtures = {
        '100': {'type': 'game', 'steam_appid': 100,
                'dlc': [301, 300, 300, '300', 301]},
        '200': {'type': 'game', 'steam_appid': 200, 'dlc': [300, '300']},
        '300': valid_dlc,
        '301': dict(valid_dlc, steam_appid=301, fullgame={'appid': 100}),
    }
    calls = []

    def fetch(appid):
        calls.append(appid)
        return fixtures[appid]

    dlc, stats = targeted.discover_dlc_for_bases(['200', '100'], core, fetch=fetch)
    assert list(sorted(dlc)) == ['App_300', 'App_301']
    assert dlc['App_300']['verified_base_appids'] == ['100', '200']
    assert dlc['App_301']['verified_base_appids'] == ['100']
    assert stats['parent_relation_lookups'] == 2
    assert stats['related_dlc_unique_ids'] == stats['dlc_price_lookups'] == 2
    assert stats['relation_complete'] is True
    assert calls.count('300') == calls.count('301') == 1

    def fails_closed(parents, overrides, *, failure=None):
        data = dict(fixtures, **overrides)

        def checked_fetch(appid):
            if appid == failure:
                raise RuntimeError('upstream access failure (429)')
            return data[appid]

        try:
            targeted.discover_dlc_for_bases(parents, core, fetch=checked_fetch)
        except RuntimeError:
            return
        raise AssertionError('unsafe DLC identity/relationship was accepted')

    # Do not silently filter a bad identity even when valid siblings exist.
    for bad in (-1, 0, True, 300.0, None, '0300', '+300',
                '٣٠٠', {'appid': 300}):
        fails_closed(['100'], {
            '100': {'type': 'game', 'dlc': [300, bad]}
        })
    for raw in (None, '300', {'appid': 300}, False):
        fails_closed(['100'], {
            '100': {'type': 'game', 'dlc': raw}
        })
    for base in ('0', '-100', '0100', True, 100.0):
        fails_closed([base], {})
    fails_closed(['100'], {'100': {'type': 'dlc', 'dlc': [300]}})
    fails_closed(['100'], {'100': {'type': 'game', 'steam_appid': 999,
                                   'dlc': [300]}})
    fails_closed(['100'], {'300': dict(valid_dlc, steam_appid=999)})
    fails_closed(['100'], {'300': dict(valid_dlc, fullgame={'appid': 999})})
    fails_closed(['100'], {'300': dict(valid_dlc, fullgame={'appid': '0100'})})
    fails_closed(['100'], {'300': dict(valid_dlc, fullgame='wrong type')})
    fails_closed(['100'], {}, failure='100')
    fails_closed(['100'], {}, failure='300')

    # A non-DLC app in a parent list is not converted into a verified DLC.
    not_dlc = dict(valid_dlc, type='music')
    safe, stats = targeted.discover_dlc_for_bases(
        ['100'], core, fetch=lambda key: (
            {'type': 'game', 'dlc': [300]} if key == '100' else not_dlc
        )
    )
    assert safe == {}
    assert stats['dlc_accepted_after_paid_gate'] == 0
    assert stats['dlc_rejected_after_paid_gate'] == 1


def check_verified_listed_base_alias_1697640():
    """The real Steam identity pair is a root alias, never a new priced DLC."""
    core = collector.load_core()
    # Identity-bearing fields copied from the user-observed KZ response. The
    # price is deliberately adversarial: it must never be offered as alias DLC.
    alias = {
        'steam_appid': 239140, 'type': 'game', 'name': 'Dying Light',
        'dlc': [325724, 1697640, 1702060, 1697640],
        'price_overview': {
            'currency': 'KZT', 'final': 10000, 'discount_percent': 95,
        },
    }
    fixtures = {
        '239140': {'steam_appid': 239140, 'type': 'game',
                   'dlc': [1697640, 1700000, '1697640']},
        '1697640': alias,
        '1700000': {'steam_appid': 1700000, 'type': 'dlc',
                    'fullgame': {'appid': 239140},
                    'name': 'Real priced DLC',
                    'price_overview': {
                        'currency': 'KZT', 'final': 25000,
                        'discount_percent': 85,
                    }},
    }
    calls = []

    def controlled_fetch(appid, *, verified_base_aliases=()):
        # Simulate the *production* caller/fetch contract, not just a raw
        # injected fixture which would bypass get_appdetails strict identity.
        calls.append((appid, set(verified_base_aliases)))
        data = fixtures[appid]
        if not targeted._is_verified_listed_base_alias(
                data, appid, verified_base_aliases):
            targeted._check_fetched_identity(data, appid, f'KZ App_{appid}')
        return data

    with patch.object(targeted, 'get_appdetails', controlled_fetch):
        result, stats = targeted.discover_dlc_for_bases(
            ['239140'], core, fetch=controlled_fetch
        )
    assert sorted(result) == ['App_1700000']
    assert result['App_1700000']['verified_parent_chains'] == [
        ['239140', '1700000']
    ]
    assert result['App_1700000']['final_kzt'] == 250
    assert calls == [
        ('239140', set()), ('1697640', {'239140'}),
        ('1700000', {'239140'}),
    ]
    assert stats['related_dlc_unique_ids'] == 1
    assert stats['dlc_price_lookups'] == 2
    assert stats['verified_base_game_alias_exclusions'] == 1
    assert stats['dlc_accepted_after_paid_gate'] == 1
    assert stats['dlc_rejected_after_paid_gate'] == 0
    assert stats['relation_complete'] is True

    # Prove the concrete network-level identity check is bypassed ONLY for a
    # validated first-hop root alias. No new request, retry or price shortcut.
    def getter(url, **kwargs):
        assert url == targeted.APPDETAILS_URL
        assert kwargs['params'] == {
            'appids': '1697640', 'cc': 'kz', 'l': 'english',
        }
        return _FakeResponse(200, appid='1697640', data=alias)

    def read_api(**kwargs):
        clock = _FakeClock()
        return targeted.get_appdetails(
            '1697640', getter=getter,
            pacer=targeted._SharedAppdetailsPacer(),
            clock=clock.clock, sleeper=clock.sleep, **kwargs
        )

    with redirect_stdout(io.StringIO()):
        assert read_api(verified_base_aliases={'239140'}) is alias
        for allowed in ((), {'999999'}, {'239140', '999999'}):
            try:
                read_api(verified_base_aliases=allowed)
            except RuntimeError as exc:
                assert 'contradicts requested AppID' in str(exc)
            else:
                raise AssertionError('unverified alias bypassed appdetails')

    def must_reject(label, altered_alias, *, roots=('239140',),
                    other_roots=None):
        records = dict(fixtures, **{'1697640': altered_alias})
        if other_roots:
            records.update(other_roots)
        try:
            targeted.discover_dlc_for_bases(
                list(roots), core, fetch=lambda appid: records[appid]
            )
        except RuntimeError:
            return
        raise AssertionError(f'{label}: unsafe AppID alias silently accepted')

    must_reject('foreign canonical game', dict(alias, steam_appid=999999))
    must_reject('different alias type', dict(alias, type='dlc'))
    must_reject('missing alias echo', dict(alias, dlc=[325724, 1702060]))
    must_reject('invalid alias dlc list', dict(alias, dlc='1697640'))
    must_reject('invalid alias dlc member', dict(alias, dlc=[1697640, True]))
    must_reject('foreign fullgame proof', dict(
        alias, fullgame={'appid': 999999}
    ))
    must_reject('two roots listing one ambiguous alias', alias,
                roots=('239140', '239141'), other_roots={
                    '239141': {'steam_appid': 239141, 'type': 'game',
                               'dlc': [1697640]},
                })
    for bad_id in (None, True, 239140.0, '0239140', '-239140'):
        must_reject(f'malformed inner ID {bad_id!r}', dict(
            alias, steam_appid=bad_id
        ))

    # The alias may not be reintroduced as a nested-child path.
    must_reject('nested alias overlap', alias, other_roots={
        '239140': {'steam_appid': 239140, 'type': 'game',
                   'dlc': [1697640, 1700000, 1700001]},
        '1700001': {'steam_appid': 1700001, 'type': 'dlc',
                    'fullgame': {'appid': 239140}, 'dlc': [1697640]},
    })


def check_nested_dlc_exact_parent_proof():
    """Synthetic cc=kz fixtures: actual 2026 API payload is not preserved."""
    core = collector.load_core()
    sale = {'currency': 'KZT', 'final': 25000, 'discount_percent': 85}
    root = {'steam_appid': 2820, 'type': 'game',
            'dlc': [201310, 235960, 600, 201310]}
    middle = {'steam_appid': 201310, 'type': 'dlc',
              'fullgame': {'appid': 2820}, 'dlc': [235960, 601, 601]}
    fixtures = {
        '2820': root,
        '201310': middle,
        '235960': {'steam_appid': 235960, 'type': 'dlc',
                   'fullgame': {'appid': 201310}},
        '600': {'steam_appid': 600, 'type': 'dlc',
                'fullgame': {'appid': 2820}, 'price_overview': sale},
        '601': {'steam_appid': 601, 'type': 'dlc',
                'fullgame': {'appid': 201310}, 'price_overview': sale},
    }

    def run(data, bases=('2820',)):
        calls = []
        def fetch(appid):
            calls.append(appid)
            return data[appid]
        result, stats = targeted.discover_dlc_for_bases(
            list(bases), core, fetch=fetch
        )
        return result, stats, calls

    result, stats, calls = run(fixtures)
    assert sorted(result) == ['App_600', 'App_601']
    assert result['App_600']['verified_parent_chains'] == [['2820', '600']]
    assert result['App_601']['verified_parent_chains'] == [
        ['2820', '201310', '601']
    ]
    assert stats['related_dlc_unique_ids'] == 4
    assert stats['dlc_price_lookups'] == 4
    assert stats['nested_intermediate_unique_ids'] == 1
    assert stats['nested_child_unique_ids'] == 2
    assert stats['relation_complete'] is True
    assert set(calls) == set(fixtures) and len(calls) == len(fixtures)
    # Free/no price nested App_235960 never becomes a paid card, regardless
    # of whether its price field is absent, null or the empty object.
    for price in ('missing', None, {}):
        child = dict(fixtures['235960'])
        if price != 'missing':
            child['price_overview'] = price
        updated = dict(fixtures, **{'235960': child})
        assert sorted(run(updated)[0]) == ['App_600', 'App_601']
    # The root may list only the intermediate, not the grandchild; the
    # intermediate's own list still gives finite exact second-hop coverage.
    nested_only = dict(fixtures, **{
        '2820': dict(root, dlc=[201310, 600])
    })
    assert sorted(run(nested_only)[0]) == ['App_600', 'App_601']
    # Steam Store labels Albion Prelude as DLC; Store metadata can surface
    # a game-type intermediate, which remains only a link, never a DLC offer.
    game_middle = dict(fixtures, **{
        '201310': {'type': 'game', 'steam_appid': 201310,
                   'dlc': [235960, 601]}
    })
    assert sorted(run(game_middle)[0]) == ['App_600', 'App_601']

    def must_fail(label, data, bases=('2820',)):
        try:
            run(data, bases)
        except RuntimeError:
            return
        raise AssertionError(f'{label}: unsafe nested DLC proof passed')

    def variant(appid, **changes):
        return dict(fixtures, **{
            appid: dict(fixtures[appid], **changes)
        })

    must_fail('foreign fullgame', variant('235960', fullgame={'appid': 999}))
    must_fail('missing intermediate', dict(fixtures, **{
        '2820': dict(root, dlc=[235960, 600]),
    }))
    must_fail('missing intermediate child listing', variant(
        '201310', dlc=[601]
    ))
    must_fail('forged nested child identity', variant(
        '235960', steam_appid=999
    ))
    must_fail('forged intermediate identity', variant(
        '201310', steam_appid=999
    ))
    must_fail('wrong intermediate type', variant('201310', type='music'))
    must_fail('wrong root type', variant('2820', type='dlc'))
    must_fail('intermediate with foreign base', variant(
        '201310', fullgame={'appid': 999}
    ))
    must_fail('self-referential root', variant(
        '2820', dlc=[2820, 201310]
    ))
    must_fail('self-referential intermediate', variant(
        '201310', dlc=[201310, 235960]
    ))
    must_fail('nested edge back to base', variant(
        '201310', dlc=[2820, 235960]
    ))
    must_fail('two-node cycle', variant(
        '235960', dlc=[201310]
    ))
    for bad in (None, '235960', {'appid': 235960}, [True]):
        must_fail('bad intermediate membership', variant('201310', dlc=bad))
    for bad in (False, 0, '0201310', {}, 'other'):
        must_fail('bad grandchild fullgame', variant(
            '235960', fullgame={'appid': bad}
        ))
    # A second root must not acquire a child through an intermediate whose
    # own fullgame explicitly says it belongs to the first root.
    must_fail('cross-base intermediate', dict(fixtures, **{
        '9990': {'steam_appid': 9990, 'type': 'game', 'dlc': [201310]},
    }), bases=('2820', '9990'))

    # Paid genuine nested DLC uses the same KZT final-minor-unit cap and
    # discount, with no shortcut through a no-price/free intermediate.
    for bad in ({'currency': 'USD', 'final': 1000, 'discount_percent': 80},
                {'currency': 'KZT', 'final': 1000},
                {'currency': 'KZT', 'final': True, 'discount_percent': 80},
                {'currency': 'KZT', 'final': 1000, 'discount_percent': False},
                ['bad'], 'bad'):
        must_fail('malformed KZT nested price', variant(
            '601', price_overview=bad
        ))
    low_price = variant('601', price_overview={
        'currency': 'KZT', 'final': 450001, 'discount_percent': 80
    })
    assert sorted(run(low_price)[0]) == ['App_600']
    small_discount = variant('601', price_overview={
        'currency': 'KZT', 'final': 10000, 'discount_percent': 49
    })
    assert sorted(run(small_discount)[0]) == ['App_600']
    # No implicit third hop, no repeated request, and no pretending that a
    # partially expanded nested subtree is complete.
    must_fail('unsupported third hop', dict(fixtures, **{
        '601': dict(fixtures['601'], dlc=[700]),
    }))
    assert run(fixtures)[1]['dlc_price_lookups'] == len(fixtures) - 1


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


class _FakeClock:
    def __init__(self):
        self.now = 0.0
        self.waits = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        assert seconds > 0
        self.waits.append(seconds)
        self.now += seconds


class _FakeResponse:
    def __init__(self, status, appid='750920', retry_after=None, data=None):
        self.status_code = status
        self.headers = {} if retry_after is None else {'Retry-After': retry_after}
        self.payload = {appid: {
            'success': True,
            'data': data if data is not None else {
                'steam_appid': int(appid), 'type': 'game', 'dlc': []
            },
        }}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f'HTTP {self.status_code}')

    def json(self):
        return self.payload


def _run_fake_appdetails(responses, clock, *, appid='750920',
                         pacer=None, wall_clock=None):
    seen = []
    scripted = iter(responses)

    def getter(url, **kwargs):
        seen.append((url, kwargs))
        return next(scripted)

    result = targeted.get_appdetails(
        appid, getter=getter,
        pacer=pacer or targeted._SharedAppdetailsPacer(),
        clock=clock.clock, sleeper=clock.sleep,
        wall_clock=wall_clock or (lambda: datetime(2026, 11, 4, tzinfo=timezone.utc))
    )
    return result, seen


def check_appdetails_429_retries_exact_kz_identity():
    clock = _FakeClock()
    result, seen = _run_fake_appdetails([
        _FakeResponse(429), _FakeResponse(200)
    ], clock)
    assert result['steam_appid'] == 750920
    assert len(seen) == 2
    assert clock.now >= targeted.APPDETAILS_BACKOFF_SECONDS[0]
    for url, args in seen:
        assert url == targeted.APPDETAILS_URL
        assert args['params'] == {
            'appids': '750920', 'cc': 'kz', 'l': 'english'
        }
        assert args['timeout'] == 25

    # Success never launders a changed/missing original AppID identity.
    try:
        _run_fake_appdetails([
            _FakeResponse(429),
            _FakeResponse(200, data={'steam_appid': 999, 'type': 'game'})
        ], _FakeClock())
    except RuntimeError:
        pass
    else:
        raise AssertionError('retry accepted contradictory Steam AppID')


def check_appdetails_429_persistent_fail_closed_and_budget():
    clock = _FakeClock()
    seen = []
    responses = iter([_FakeResponse(429) for _ in range(5)])

    def getter(url, **kwargs):
        seen.append(kwargs['params']['appids'])
        return next(responses)

    try:
        targeted.get_appdetails(
            '750920', getter=getter, pacer=targeted._SharedAppdetailsPacer(),
            clock=clock.clock, sleeper=clock.sleep
        )
    except requests.HTTPError:
        pass
    else:
        raise AssertionError('persistent HTTP 429 should fail closed')
    assert seen == ['750920'] * targeted.APPDETAILS_MAX_ATTEMPTS
    assert clock.now <= targeted.APPDETAILS_MAX_WAIT_SECONDS

    # Even valid server Retry-After headers cannot create an unbounded wait.
    clock = _FakeClock()
    seen = []
    def capped_getter(url, **kwargs):
        seen.append(kwargs['params']['appids'])
        return _FakeResponse(429, retry_after='999999999')

    try:
        targeted.get_appdetails(
            '750920', getter=capped_getter,
            pacer=targeted._SharedAppdetailsPacer(),
            clock=clock.clock, sleeper=clock.sleep
        )
    except RuntimeError as exc:
        assert 'wait budget' in str(exc)
    else:
        raise AssertionError('Retry-After exceeded bounded retry budget')
    assert len(seen) == 3  # fourth request cannot be sent past 120s
    assert clock.now == targeted.APPDETAILS_MAX_WAIT_SECONDS


def check_appdetails_retry_after_and_non429_fail_closed():
    origin = datetime(2026, 11, 4, tzinfo=timezone.utc)
    header_date = format_datetime(origin + timedelta(seconds=12), usegmt=True)
    for header, minimum, maximum in [
        ('7', 7, 7),
        (header_date, 12, 12),
        ('invalid', targeted.APPDETAILS_BACKOFF_SECONDS[0],
         targeted.APPDETAILS_BACKOFF_SECONDS[0]),
        ('999999', targeted.APPDETAILS_MAX_RETRY_AFTER_SECONDS,
         targeted.APPDETAILS_MAX_RETRY_AFTER_SECONDS),
    ]:
        clock = _FakeClock()
        _, seen = _run_fake_appdetails([
            _FakeResponse(429, retry_after=header), _FakeResponse(200)
        ], clock, wall_clock=lambda: origin)
        assert len(seen) == 2
        assert minimum <= clock.now <= maximum + targeted.REQUEST_SPACING_SECONDS

    # 503 and transport exceptions do not become a false positive DLC set.
    for exception in (requests.HTTPError, requests.Timeout):
        clock = _FakeClock()
        calls = []
        def getter(url, **kwargs):
            calls.append(kwargs)
            if exception is requests.Timeout:
                raise requests.Timeout('network failed')
            return _FakeResponse(503)
        try:
            targeted.get_appdetails(
                '750920', getter=getter,
                pacer=targeted._SharedAppdetailsPacer(),
                clock=clock.clock, sleeper=clock.sleep
            )
        except exception:
            pass
        else:
            raise AssertionError('non-429 failure was recovered as success')
        assert len(calls) == 1


def check_appdetails_concurrent_shared_cooldown_no_fanout():
    cooldown_set = threading.Event()
    seen = []
    seen_lock = threading.Lock()

    class SignalPacer(targeted._SharedAppdetailsPacer):
        def throttle(self, seconds, *, clock):
            super().throttle(seconds, clock=clock)
            cooldown_set.set()

    pacer = SignalPacer(spacing_seconds=0.025)
    first_calls = []

    def first_getter(url, **kwargs):
        with seen_lock:
            seen.append((time.monotonic(), kwargs['params']['appids']))
        first_calls.append(True)
        return _FakeResponse(429 if len(first_calls) == 1 else 200,
                             appid='750920')

    def second_getter(url, **kwargs):
        with seen_lock:
            seen.append((time.monotonic(), kwargs['params']['appids']))
        return _FakeResponse(200, appid='750921')

    with patch.object(targeted, 'APPDETAILS_BACKOFF_SECONDS', (0.12, 0.12, 0.12)):
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(
                targeted.get_appdetails, '750920',
                getter=first_getter, pacer=pacer
            )
            assert cooldown_set.wait(timeout=2), 'no HTTP 429 cooldown registered'
            cooldown_at = time.monotonic()
            second = pool.submit(
                targeted.get_appdetails, '750921',
                getter=second_getter, pacer=pacer
            )
            assert first.result(timeout=3)['steam_appid'] == 750920
            assert second.result(timeout=3)['steam_appid'] == 750921

    assert len(first_calls) == 2 and len(seen) == 3
    sorted_seen = sorted(seen)
    assert all(t >= cooldown_at + 0.09 for t, _ in sorted_seen[1:])
    # Shared pacing staggers the two post-throttle network calls; no burst.
    assert sorted_seen[2][0] - sorted_seen[1][0] >= 0.017


def check_appdetails_429_diagnostics_are_passive_and_safe():
    """Capture response/window evidence without altering existing request logic."""
    clock = _FakeClock()
    diagnostics = targeted._AppdetailsDiagnostics()
    diagnostics.set_stage('parent_relations')
    output = io.StringIO()
    seen = []
    replies = iter([
        _FakeResponse(429, retry_after='7'),
        _FakeResponse(200),
        _FakeResponse(403),
    ])

    def getter(url, **kwargs):
        seen.append((url, kwargs['params'].copy()))
        return next(replies)

    with redirect_stdout(output):
        result = targeted.get_appdetails(
            '750920', getter=getter,
            pacer=targeted._SharedAppdetailsPacer(),
            clock=clock.clock, sleeper=clock.sleep,
            diagnostics=diagnostics,
        )
        assert result['steam_appid'] == 750920
        diagnostics.set_stage('dlc_price')
        try:
            targeted.get_appdetails(
                '750920', getter=getter,
                pacer=targeted._SharedAppdetailsPacer(),
                clock=clock.clock, sleeper=clock.sleep,
                diagnostics=diagnostics,
            )
        except requests.HTTPError:
            pass
        else:
            raise AssertionError('403 must still fail closed')

    events = []
    for line in output.getvalue().splitlines():
        prefix = '[steam-appdetails-diagnostic] '
        assert line.startswith(prefix)
        events.append(json.loads(line[len(prefix):]))
    assert [x['status'] for x in events] == [429, 200, 403]
    assert [x['attempt'] for x in events] == [1, 2, 1]
    assert [x['rolling_300s_request_starts'] for x in events] == [1, 2, 3]
    assert [x['stage'] for x in events] == [
        'parent_relations', 'parent_relations', 'dlc_price'
    ]
    assert [x['first_429'] for x in events] == [True, False, False]
    assert events[0]['retry_after_present'] is True
    assert events[0]['retry_after_seconds'] == 7
    assert events[0]['applied_cooldown_seconds'] == 7
    assert len(seen) == 3
    assert all(url == targeted.APPDETAILS_URL for url, _ in seen)
    assert all(params == {'appids': '750920', 'cc': 'kz', 'l': 'english'}
               for _, params in seen)
    assert diagnostics.snapshot() == {
        'request_starts': 3,
        'response_status_counts': {'429': 1, '200': 1, '403': 1},
        'first_429_seen': True,
    }
    # Only safe, allowlisted metadata are emitted; no URL or raw headers.
    assert 'store.steampowered.com' not in output.getvalue()
    assert "'Retry-After':" not in output.getvalue()

    # A bounded in-memory rolling window expires starts; not a Valve quota.
    rolling = targeted._AppdetailsDiagnostics()
    assert rolling.started(0.0)['rolling_300s_request_starts'] == 1
    assert rolling.started(299.0)['rolling_300s_request_starts'] == 2
    assert rolling.started(301.0)['rolling_300s_request_starts'] == 2

    # Network-error logging must preserve failure and redact raw exception.
    output = io.StringIO()
    def failing_getter(url, **kwargs):
        raise requests.Timeout('PRIVATE-MESSAGE-MUST-NOT-APPEAR')
    with redirect_stdout(output):
        try:
            targeted.get_appdetails(
                '750920', getter=failing_getter,
                pacer=targeted._SharedAppdetailsPacer(),
                clock=clock.clock, sleeper=clock.sleep,
                diagnostics=diagnostics,
            )
        except requests.Timeout:
            pass
        else:
            raise AssertionError('transport error was suppressed')
    assert 'PRIVATE-MESSAGE' not in output.getvalue()
    event = json.loads(output.getvalue().split('] ', 1)[1])
    assert event['status'] == 'transport_error'
    assert event['transport_error_class'] == 'Timeout'


def _assert_rolling_start_cap(starts, *, cap=180, window=300.0):
    """Every half-open 300s suffix, not just fixed calendar buckets."""
    ordered = sorted(starts)
    left = 0
    for right, now in enumerate(ordered):
        while now - ordered[left] >= window:
            left += 1
        assert right - left + 1 <= cap, (right, now, ordered[left])
    return ordered


def check_appdetails_sliding_window_boundary_and_overlaps():
    """180/300, exact t=300 expiry and overlapping non-aligned windows."""
    assert targeted.APPDETAILS_MAX_STARTS_PER_WINDOW == 180
    assert targeted.APPDETAILS_WINDOW_SECONDS == 300.0
    clock = _FakeClock()
    pacer = targeted._SharedAppdetailsPacer(spacing_seconds=0)
    starts = []
    for _ in range(120):
        starts.append(pacer.acquire(
            clock=clock.clock, sleeper=clock.sleep, deadline=900.0
        ))
    clock.now = 100.0
    for _ in range(60):
        starts.append(pacer.acquire(
            clock=clock.clock, sleeper=clock.sleep, deadline=900.0
        ))
    assert starts == [0.0] * 120 + [100.0] * 60
    # The 181st attempt at t=100 must wait for the oldest exact 300s edge.
    starts.append(pacer.acquire(
        clock=clock.clock, sleeper=clock.sleep, deadline=900.0
    ))
    assert starts[-1] == 300.0
    assert clock.waits == [200.0]
    for _ in range(119):
        starts.append(pacer.acquire(
            clock=clock.clock, sleeper=clock.sleep, deadline=900.0
        ))
    assert starts[-120:] == [300.0] * 120
    # Now the remaining 60 t=100 calls still occupy the moving window.
    starts.append(pacer.acquire(
        clock=clock.clock, sleeper=clock.sleep, deadline=900.0
    ))
    assert starts[-1] == 400.0
    assert clock.waits[-1] == 100.0
    _assert_rolling_start_cap(starts)
    assert max(starts) == 400.0

    # Production spacing also applies: conservative sliding window cannot be
    # replaced by a simple average at the 180th physical request.
    clock = _FakeClock()
    pacer = targeted._SharedAppdetailsPacer()
    starts = [pacer.acquire(
        clock=clock.clock, sleeper=clock.sleep, deadline=900.0
    ) for _ in range(181)]
    assert abs(starts[179] - (179 * 0.9)) < 1e-6
    assert abs(starts[180] - 300.0) < 1e-6
    _assert_rolling_start_cap(starts)


def check_appdetails_sliding_window_three_threads_and_fairness():
    """Three concurrent independent GETs cannot bypass an atomic start gate."""
    class SharedClock:
        def __init__(self):
            self.now = 0.0
            self.lock = threading.Lock()
            self.waits = []

        def clock(self):
            with self.lock:
                return self.now

        def sleep(self, seconds):
            assert seconds > 0
            with self.lock:
                self.waits.append(seconds)
                self.now += seconds

    class RecordedPacer(targeted._SharedAppdetailsPacer):
        def __init__(self):
            super().__init__(spacing_seconds=0)
            self.record_lock = threading.Lock()
            self.reservations = []

        def acquire(self, **kwargs):
            t = super().acquire(**kwargs)
            with self.record_lock:
                self.reservations.append(t)
            return t

    clock = SharedClock()
    pacer = RecordedPacer()
    barrier = threading.Barrier(3)
    results = []
    result_lock = threading.Lock()

    def getter(url, **kwargs):
        appid = kwargs['params']['appids']
        assert kwargs['params']['cc'] == 'kz'
        return _FakeResponse(200, appid=appid)

    def worker(first_id):
        barrier.wait()
        for offset in range(85):
            appid = str(first_id + offset)
            data = targeted.get_appdetails(
                appid, getter=getter, pacer=pacer, clock=clock.clock,
                sleeper=clock.sleep
            )
            with result_lock:
                results.append(data['steam_appid'])

    # Avoid 255 diagnostic stdout events obscuring the deterministic assertion.
    with redirect_stdout(io.StringIO()):
        with ThreadPoolExecutor(max_workers=3) as pool:
            jobs = [pool.submit(worker, 1000 + i * 100) for i in range(3)]
            for job in jobs:
                job.result(timeout=10)
    assert len(results) == 255 and len(set(results)) == 255
    assert len(pacer.reservations) == 255
    times = _assert_rolling_start_cap(pacer.reservations)
    assert times[:180] == [0.0] * 180
    assert times[180:] == [300.0] * 75


def check_appdetails_parent_child_and_retry_share_window():
    """Parent retries and deduplicated DLC child GETs use the same pacer."""
    clock = _FakeClock()
    pacer = targeted._SharedAppdetailsPacer(spacing_seconds=0)
    calls = []
    lock = threading.Lock()
    def getter(url, **kwargs):
        appid = kwargs['params']['appids']
        with lock:
            calls.append(appid)
            first_parent_100 = appid == '100' and calls.count('100') == 1
        if first_parent_100:
            return _FakeResponse(429, appid=appid, retry_after='7')
        if appid in ('100', '200'):
            return _FakeResponse(
                200, appid=appid,
                data={'steam_appid': int(appid), 'type': 'game',
                      'dlc': [300, 300]},
            )
        return _FakeResponse(
            200, appid=appid,
            data={'steam_appid': 300, 'type': 'dlc',
                  'fullgame': {'appid': 100}, 'name': 'Chapter',
                  'price_overview': {'currency': 'KZT',
                                     'final': 30000, 'discount_percent': 75}},
        )

    def fetch(appid):
        return targeted.get_appdetails(
            appid, getter=getter, pacer=pacer,
            clock=clock.clock, sleeper=clock.sleep
        )
    with redirect_stdout(io.StringIO()):
        dlc, stats = targeted.discover_dlc_for_bases(
            ['100', '200'], collector.load_core(), fetch=fetch
        )
    assert sorted(calls) == ['100', '100', '200', '300']
    assert stats['parent_relation_lookups'] == 2
    assert stats['dlc_price_lookups'] == 1
    assert stats['related_dlc_unique_ids'] == 1
    assert dlc['App_300']['verified_base_appids'] == ['100', '200']
    assert len(pacer._starts) == 4  # 2 parents, one 429 retry, one child

    # Planned quota wait beyond 120s is not a retry failure; Retry-After
    # and the shared cooldown also must not shortcut the sliding gate.
    clock = _FakeClock()
    pacer = targeted._SharedAppdetailsPacer(spacing_seconds=0)
    for _ in range(180):
        pacer.acquire(clock=clock.clock, sleeper=clock.sleep, deadline=900.0)
    seen = []
    responses = iter([_FakeResponse(429, retry_after='60'),
                      _FakeResponse(200)])
    def capped_getter(url, **kwargs):
        seen.append(clock.clock())
        return next(responses)
    with redirect_stdout(io.StringIO()):
        result = targeted.get_appdetails(
            '750920', getter=capped_getter, pacer=pacer,
            clock=clock.clock, sleeper=clock.sleep
        )
    assert result['steam_appid'] == 750920
    assert seen == [300.0, 360.0] and clock.now == 360.0
    assert clock.waits[0] == 300.0
    _assert_rolling_start_cap([0.0] * 180 + seen)


def check_appdetails_429_sliding_window_non429_fail_closed():
    """The cap never converts 403, 503 or network errors into empty/success."""
    for status in (403, 503, 'network'):
        clock = _FakeClock()
        pacer = targeted._SharedAppdetailsPacer(spacing_seconds=0)
        for _ in range(180):
            pacer.acquire(clock=clock.clock, sleeper=clock.sleep,
                          deadline=900.0)
        seen = []
        def getter(url, **kwargs):
            seen.append(clock.clock())
            if status == 'network':
                raise requests.Timeout('not a successful DLC lookup')
            return _FakeResponse(status)
        with redirect_stdout(io.StringIO()):
            try:
                targeted.get_appdetails(
                    '750920', getter=getter, pacer=pacer,
                    clock=clock.clock, sleeper=clock.sleep,
                )
            except (requests.HTTPError, requests.Timeout):
                pass
            else:
                raise AssertionError('non-429 failure bypassed fail-closed')
        assert seen == [300.0], (status, seen)


def main():
    check_base_targeted_dlc()
    check_dlc_no_price_skips_only_verified_absence()
    check_dlc_membership_identity_regressions()
    check_verified_listed_base_alias_1697640()
    check_nested_dlc_exact_parent_proof()
    check_conservative_obscure_rescue_and_package()
    check_five_middling_games_package_below_individual_cutoff()
    check_direct_subs_are_discoverable_without_current_app()
    check_independent_package_family_needs_semantic_not_external_base()
    check_appdetails_429_retries_exact_kz_identity()
    check_appdetails_429_persistent_fail_closed_and_budget()
    check_appdetails_retry_after_and_non429_fail_closed()
    check_appdetails_concurrent_shared_cooldown_no_fanout()
    check_appdetails_429_diagnostics_are_passive_and_safe()
    check_appdetails_sliding_window_boundary_and_overlaps()
    check_appdetails_sliding_window_three_threads_and_fairness()
    check_appdetails_parent_child_and_retry_share_window()
    check_appdetails_429_sliding_window_non429_fail_closed()
    print('targeted Steam KZ DLC and independent package 18/18 PASS')


if __name__ == '__main__':
    main()
