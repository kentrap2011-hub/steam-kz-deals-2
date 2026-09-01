import copy
import unittest
from datetime import datetime, timezone

import giveaway_visual_handoff as handoff

NOW = datetime(2026, 9, 1, 20, 0, 0, tzinfo=timezone.utc)


def offer(source, offer_id, end='2026-09-03T15:00:00Z'):
    hosts = {
        'steam': 'https://store.steampowered.com/app/10/',
        'epic': 'https://store.epicgames.com/en-US/p/test-game',
        'gog': 'https://www.gog.com/en/game/test_game',
    }
    return {
        'storefront': source,
        'source_offer_id': offer_id,
        'source_product_id': f'product:{offer_id}',
        'claim_url': hosts[source],
        'promotion_end_utc': end,
    }


def snapshot(games=None):
    return {
        'contract': 'CROSS-PLATFORM-GIVEAWAY-V1',
        'schema_version': 1,
        'country_code': 'KZ',
        'generated_at_utc': '2026-09-01T19:30:00Z',
        'fresh_until_utc': '2026-09-03T01:30:00Z',
        'snapshot_status': 'complete',
        'required_sources': ['steam', 'epic', 'gog'],
        'source_health': {
            'steam': {'status': 'ok', 'complete': True},
            'epic': {'status': 'ok', 'complete': True},
            'gog': {'status': 'ok', 'complete': True},
        },
        'games': games or [],
    }


class GiveawayVisualHandoffTests(unittest.TestCase):
    def test_complete_fresh_active(self):
        raw = snapshot([{
            'canonical_game_key': 'g:1',
            'title': 'Example',
            'offers': [offer('epic', 'epic:1')],
        }])
        result = handoff.derive_giveaways(raw, NOW)
        self.assertEqual(result['state'], 'active')
        self.assertEqual(result['accepted_offer_count_at_build'], 1)
        self.assertEqual(result['games'][0]['offers'][0]['claim_url'], offer('epic', 'x')['claim_url'])

    def test_complete_fresh_zero_is_trusted_empty(self):
        result = handoff.derive_giveaways(snapshot([]), NOW)
        self.assertEqual(result['state'], 'empty')
        self.assertEqual(result['games'], [])

    def test_incomplete_is_unavailable(self):
        raw = snapshot([])
        raw['snapshot_status'] = 'incomplete'
        result = handoff.derive_giveaways(raw, NOW)
        self.assertEqual(result['state'], 'unavailable')
        self.assertEqual(result['games'], [])

    def test_stale_is_unavailable(self):
        raw = snapshot([])
        raw['fresh_until_utc'] = '2026-09-01T19:59:59Z'
        self.assertEqual(handoff.derive_giveaways(raw, NOW)['state'], 'unavailable')

    def test_wrong_contract_or_country_is_unavailable(self):
        raw = snapshot([])
        raw['contract'] = 'OTHER'
        self.assertEqual(handoff.derive_giveaways(raw, NOW)['state'], 'unavailable')
        raw = snapshot([])
        raw['country_code'] = 'US'
        self.assertEqual(handoff.derive_giveaways(raw, NOW)['state'], 'unavailable')

    def test_expired_offer_is_hidden(self):
        raw = snapshot([{
            'canonical_game_key': 'g:expired',
            'title': 'Expired',
            'offers': [offer('epic', 'epic:expired', '2026-09-01T19:59:59Z')],
        }])
        result = handoff.derive_giveaways(raw, NOW)
        self.assertEqual(result['state'], 'empty')
        self.assertEqual(result['accepted_offer_count_at_build'], 0)

    def test_multiple_storefront_offers_are_preserved(self):
        raw = snapshot([{
            'canonical_game_key': 'g:multi',
            'title': 'Multi',
            'offers': [offer('gog', 'gog:1'), offer('epic', 'epic:1')],
        }])
        result = handoff.derive_giveaways(raw, NOW)
        self.assertEqual(len(result['games']), 1)
        self.assertEqual(len(result['games'][0]['offers']), 2)
        self.assertEqual({o['storefront'] for o in result['games'][0]['offers']}, {'epic', 'gog'})

    def test_similar_titles_are_not_merged(self):
        raw = snapshot([
            {'canonical_game_key': 'g:a', 'title': 'Game', 'offers': [offer('epic', 'epic:a')]},
            {'canonical_game_key': 'g:b', 'title': 'Game ', 'offers': [offer('gog', 'gog:b')]},
        ])
        result = handoff.derive_giveaways(raw, NOW)
        self.assertEqual([g['game_key'] for g in result['games']], ['g:a', 'g:b'])

    def test_order_is_deadline_then_title_then_identity(self):
        raw = snapshot([
            {'canonical_game_key': 'g:z', 'title': 'Zulu', 'offers': [offer('epic', 'epic:z', '2026-09-04T10:00:00Z')]},
            {'canonical_game_key': 'g:b', 'title': 'Bravo', 'offers': [offer('gog', 'gog:b', '2026-09-03T10:00:00Z')]},
            {'canonical_game_key': 'g:a', 'title': 'Alpha', 'offers': [offer('steam', 'steam:a', '2026-09-03T10:00:00Z')]},
        ])
        result = handoff.derive_giveaways(raw, NOW)
        self.assertEqual([g['title'] for g in result['games']], ['Alpha', 'Bravo', 'Zulu'])

    def test_malformed_accepted_surface_fails_closed(self):
        raw = snapshot([{
            'canonical_game_key': 'g:bad',
            'title': 'Bad',
            'offers': [dict(offer('epic', 'epic:bad'), claim_url='http://example.invalid/')],
        }])
        self.assertEqual(handoff.derive_giveaways(raw, NOW)['state'], 'unavailable')

    def test_does_not_mutate_source(self):
        raw = snapshot([{
            'canonical_game_key': 'g:1',
            'title': 'Example',
            'offers': [offer('epic', 'epic:1')],
        }])
        before = copy.deepcopy(raw)
        handoff.derive_giveaways(raw, NOW)
        self.assertEqual(raw, before)


if __name__ == '__main__':
    unittest.main()
