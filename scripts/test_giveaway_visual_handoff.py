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

    def test_malformed_offer_isolated_while_valid_sibling_survives(self):
        raw = snapshot([
            {
                'canonical_game_key': 'g:bad',
                'title': 'Bad',
                'offers': [dict(offer('epic', 'epic:bad'), claim_url='http://example.invalid/')],
            },
            {
                'canonical_game_key': 'g:good',
                'title': 'Good',
                'offers': [offer('gog', 'gog:good')],
            },
        ])
        result, defects = handoff.derive_giveaways_with_diagnostics(raw, NOW)
        self.assertEqual(result['state'], 'active')
        self.assertEqual([game['game_key'] for game in result['games']], ['g:good'])
        self.assertEqual(len(defects), 1)
        self.assertEqual(defects[0]['object_id'], 'g:bad')
        self.assertEqual(defects[0]['reason_codes'], ['invalid_claim_url'])

    def test_missing_stable_game_identity_remains_fail_closed(self):
        raw = snapshot([{
            'canonical_game_key': '',
            'title': 'Bad',
            'offers': [offer('epic', 'epic:bad')],
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



class GiveawayCanonicalIdentityHandoffTests(unittest.TestCase):
    def _resolved(self):
        o = offer("epic", "epic:resolved")
        o["source_product_id"] = "a"*32 + ":" + "b"*32
        o["identity_resolution"] = {
            "schema_version": 1, "status": "resolved", "source_storefront": "epic",
            "source_product_id": o["source_product_id"], "identity_provider": "itad",
            "steam_appid": 738520
        }
        g = {
            "canonical_game_key": "meta-v1:grouping-only", "title": "Untrusted Title",
            "analysis_identity": {
                "status": "resolved", "steam_appid": 738520, "identity_provider": "itad"
            },
            "offers": [o],
        }
        doc = snapshot([g])
        doc["identity_provider"] = "itad"
        return doc

    def test_exact_provider_neutral_binding_and_credit(self):
        doc = self._resolved()
        view = handoff.derive_giveaways(doc, NOW)
        self.assertEqual(view["games"][0]["analysis_identity"]["steam_appid"], 738520)
        self.assertEqual(view["attribution"]["url"], "https://isthereanydeal.com/")

    def test_conflicting_receipt_or_unresolved_identity_never_authorizes_analysis(self):
        doc = self._resolved()
        doc["games"][0]["offers"][0]["identity_resolution"]["steam_appid"] = 10
        self.assertEqual(handoff.derive_giveaways(doc, NOW)["games"][0]
                         ["analysis_identity"]["status"], "unresolved")
        doc = self._resolved()
        doc["games"][0]["offers"][0]["identity_resolution"]["identity_provider"] = "igdb"
        self.assertEqual(handoff.derive_giveaways(doc, NOW)["games"][0]
                         ["analysis_identity"]["status"], "unresolved")
        doc = self._resolved()
        doc["identity_provider"] = "igdb"
        view = handoff.derive_giveaways(doc, NOW)
        self.assertEqual(view["games"][0]["analysis_identity"]["status"], "unresolved")
        self.assertIsNone(view.get("attribution"))

    def test_analysis_reuses_exact_ready_canonical_card_and_no_title_heuristics(self):
        import giveaway_analysis_reuse as reuse
        view = handoff.derive_giveaways(self._resolved(), NOW)
        canonical = [{
            "id": "family-738520", "title": "Different Steam title",
            "base_appids": ["738520"], "analysis_state": "analyzed_fit",
            "description_status": "ready_ru", "summary": "Русское описание",
            "why_fit": ["Обоснованный плюс"], "why_fit_status": {"grounding": "grounded"},
            "why_fit_provenance": [{"source": "taste"}],
            "risks": ["Подтверждённый риск"], "risk_status": {"grounding": "grounded"},
            "risk_provenance": [{"source": "taste_negative_evidence"}],
            "description_source_appid": "738520",
        }]
        reuse.attach(view, canonical)
        analysis = view["games"][0]["analysis"]
        self.assertEqual(analysis["status"], "ready")
        self.assertEqual(analysis["summary"], "Русское описание")
        self.assertEqual(analysis["risks"], ["Подтверждённый риск"])
        self.assertEqual(analysis["provenance"]["canonical_family_id"], "family-738520")
        unknown = handoff.derive_giveaways(self._resolved(), NOW)
        reuse.attach(unknown, [{**canonical[0], "base_appids": ["10"], "title": "Untrusted Title"}])
        self.assertEqual(unknown["games"][0]["analysis"]["status"], "incomplete")
        self.assertIsNone(unknown["games"][0]["analysis"]["summary"])
        conflicting = handoff.derive_giveaways(self._resolved(), NOW)
        reuse.attach(conflicting, [canonical[0], canonical[0]])
        self.assertEqual(conflicting["games"][0]["analysis"]["reason"], "canonical_card_missing_or_ambiguous")

if __name__ == '__main__':
    unittest.main()
