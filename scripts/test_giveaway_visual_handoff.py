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
        not_grounded = handoff.derive_giveaways(self._resolved(), NOW)
        untrusted = {**canonical[0], "risk_provenance": [{"source": "derived"}]}
        reuse.attach(not_grounded, [untrusted])
        self.assertEqual(not_grounded["games"][0]["analysis"]["status"], "incomplete")
        self.assertEqual(not_grounded["games"][0]["analysis"]["risks"], [])
        unknown = handoff.derive_giveaways(self._resolved(), NOW)
        reuse.attach(unknown, [{**canonical[0], "base_appids": ["10"], "title": "Untrusted Title"}])
        self.assertEqual(unknown["games"][0]["analysis"]["status"], "incomplete")
        self.assertIsNone(unknown["games"][0]["analysis"]["summary"])
        conflicting = handoff.derive_giveaways(self._resolved(), NOW)
        reuse.attach(conflicting, [canonical[0], canonical[0]])
        self.assertEqual(conflicting["games"][0]["analysis"]["reason"], "canonical_card_missing_or_ambiguous")


class GiveawayOffscreenTop100CompatibilityTests(unittest.TestCase):
    """Joint PR #311/#312 regression: pre-cap source survives all producer paths."""

    @staticmethod
    def _canonical():
        offscreen = {
            'id': 'family-738520', 'base_appids': ['738520'],
            'analysis_state': 'analyzed_fit', 'description_status': 'ready_ru',
            'summary': 'Проверенное русское описание',
            'why_fit': ['Подтверждено Taste'],
            'why_fit_status': {'grounding': 'grounded'},
            'why_fit_provenance': [{'source': 'taste'}],
            'risks': ['Обоснованное ограничение'],
            'risk_status': {'grounding': 'grounded'},
            'risk_provenance': [{'source': 'taste_negative_evidence'}],
            'description_source_appid': '738520',
        }
        # All 100 other paid cards are visible; the resolved analyzed game
        # is rank 101 and therefore cannot be found in the paid UI list.
        visible = [
            {'id': f'visible-{i}', 'base_appids': [str(900000 + i)],
             'analysis_state': 'unresolved'}
            for i in range(100)
        ]
        return visible, visible + [offscreen]

    @staticmethod
    def _giveaway(appid=738520):
        fixture = GiveawayCanonicalIdentityHandoffTests()._resolved()
        fixture['games'][0]['analysis_identity']['steam_appid'] = appid
        fixture['games'][0]['offers'][0]['identity_resolution']['steam_appid'] = appid
        return handoff.derive_giveaways(fixture, NOW)

    def test_full_precap_and_partial_refreshes_keep_exact_offscreen_analysis(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        import build_final_visual_payload as producer
        import giveaway_analysis_reuse as reuse

        visible, all_ranked = self._canonical()
        bound = {'canonical_semantic_inputs': 'sha-of-accepted-full-scope'}
        ready = {
            'items': copy.deepcopy(visible),
            'giveaway_analysis_source': reuse.capture_canonical_sources(all_ranked, bound),
            'production_contract': {},
        }
        self.assertEqual(len(ready['items']), 100)
        # Equivalent to full producer at the exact point after the paid cap.
        with patch.object(producer, 'giveaway_semantic_source_binding', return_value=bound), \
             patch.object(producer.giveaway_visual_handoff, 'derive_from_path',
                          side_effect=lambda: self._giveaway()):
            full = producer.attach_precomputed_giveaway_analysis(ready)
        self.assertEqual(full['games'][0]['analysis']['status'], 'ready')
        self.assertEqual(full['games'][0]['analysis']['steam_appid'], 738520)
        self.assertEqual(full['games'][0]['analysis']['summary'], 'Проверенное русское описание')

        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / 'visual.json'
            out.write_text(__import__('json').dumps(ready, ensure_ascii=False), encoding='utf-8')
            with patch.object(producer, 'OUT', out), \
                 patch.object(producer, 'giveaway_semantic_source_binding', return_value=bound), \
                 patch.object(producer.giveaway_visual_handoff, 'derive_from_path',
                              side_effect=lambda: self._giveaway()), \
                 patch.object(producer.base_builder, 'git_sha', return_value='sha'):
                changed, state, count = producer.refresh_existing_giveaways_only()
            self.assertTrue(changed)
            self.assertEqual(state, 'active')
            after_giveaway = __import__('json').loads(out.read_text(encoding='utf-8'))
            self.assertEqual(len(after_giveaway['items']), 100)
            self.assertEqual(after_giveaway['items'], ready['items'])
            self.assertEqual(after_giveaway['giveaways']['games'][0]['analysis']['status'], 'ready')

            # Force-media deterministic refresh uses the already persisted
            # bounded canonical index, not only the paid visible 100.
            with patch.object(producer, 'OUT', out), \
                 patch.object(producer, 'giveaway_semantic_source_binding', return_value=bound), \
                 patch.object(producer.giveaway_visual_handoff, 'derive_from_path',
                              side_effect=lambda: self._giveaway()), \
                 patch.object(producer.base_builder, 'git_sha', return_value='sha'), \
                 patch.object(producer, 'apply_visual_semantic_status'), \
                 patch.object(producer, 'load_duration_entries', return_value={}), \
                 patch.object(producer, 'current_explanation_context',
                              return_value=({}, {}, {})), \
                 patch.object(producer.base_builder.visual_builder,
                              'load_translation_cache', return_value={}), \
                 patch.object(producer.base_builder.visual_builder,
                              'load_content_metadata_by_appid', return_value={}), \
                 patch.object(producer.base_builder.visual_builder,
                              'resolve_description_for_appids', return_value={}), \
                 patch.object(producer.progressive_personalization,
                              'strip_unresolved_personalization'), \
                 patch.object(producer, 'apply_deterministic_purchase_refresh',
                              return_value=({}, False)):
                changed, touched, media_count, stats = producer.refresh_existing_media()
            after_media = __import__('json').loads(out.read_text(encoding='utf-8'))
            self.assertEqual(len(after_media['items']), 100)
            self.assertEqual(after_media['giveaways']['games'][0]['analysis']['status'], 'ready')

            # No title-based carry-over when the exact resolved identity changes.
            with patch.object(producer, 'OUT', out), \
                 patch.object(producer, 'giveaway_semantic_source_binding', return_value=bound), \
                 patch.object(producer.giveaway_visual_handoff, 'derive_from_path',
                              side_effect=lambda: self._giveaway(99999999)), \
                 patch.object(producer.base_builder, 'git_sha', return_value='sha'):
                producer.refresh_existing_giveaways_only()
            changed_identity = __import__('json').loads(out.read_text(encoding='utf-8'))
            self.assertEqual(changed_identity['giveaways']['games'][0]['analysis']['status'], 'incomplete')
            self.assertIsNone(changed_identity['giveaways']['games'][0]['analysis']['summary'])

    def test_changed_semantic_source_or_ambiguous_appid_never_reuses_saved_data(self):
        import giveaway_analysis_reuse as reuse
        visible, all_ranked = self._canonical()
        bound = {'semantic': 'accepted'}
        saved = reuse.capture_canonical_sources(all_ranked, bound)
        no_longer_bound = reuse.canonical_sources_for_refresh(saved, visible, {'semantic': 'updated'})
        fresh = self._giveaway()
        reuse.attach(fresh, no_longer_bound)
        self.assertEqual(fresh['games'][0]['analysis']['status'], 'incomplete')
        self.assertIsNone(fresh['games'][0]['analysis']['summary'])

        duplicate = dict(all_ranked[-1], id='a-second-family', base_appids=['738520'])
        saved = reuse.capture_canonical_sources(all_ranked + [duplicate], bound)
        ambiguous = self._giveaway()
        reuse.attach(ambiguous, reuse.canonical_sources_for_refresh(saved, visible, bound))
        self.assertEqual(
            ambiguous['games'][0]['analysis']['reason'],
            'canonical_card_missing_or_ambiguous',
        )


if __name__ == '__main__':
    unittest.main()
