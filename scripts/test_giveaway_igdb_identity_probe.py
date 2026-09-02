from __future__ import annotations

import unittest

import giveaway_igdb_identity_probe as probe


class GiveawayIgdbIdentityProbeTests(unittest.TestCase):
    def test_extracts_only_exact_provider_ids_and_never_uses_title_as_identity(self):
        snapshot = {
            "contract": "CROSS-PLATFORM-GIVEAWAY-V1",
            "games": [
                {
                    "canonical_game_key": "meta-v1:not-semantic-proof",
                    "title": "Title must not become a UID 12345",
                    "offers": [
                        {
                            "source_id": "epic",
                            "source_product_id": "namespace-1:offer-1",
                            "title": "Different title also ignored",
                        }
                    ],
                },
                {
                    "canonical_game_key": "source-v1:gog:42",
                    "title": "42 is only title text here",
                    "offers": [{"source_id": "gog", "source_product_id": "42"}],
                },
            ],
        }
        identities, scope = probe.exact_provider_identities(snapshot, limit=10)
        self.assertEqual(scope["eligible_offer_count"], 2)
        self.assertEqual(
            identities[0]["uid_candidates"],
            [
                {"kind": "epic_source_product_id", "uid": "namespace-1:offer-1"},
                {"kind": "epic_namespace", "uid": "namespace-1"},
                {"kind": "epic_offer_id", "uid": "offer-1"},
            ],
        )
        self.assertEqual(identities[1]["uid_candidates"], [{"kind": "gog_catalog_product_id", "uid": "42"}])
        self.assertNotIn("12345", probe.unique_candidate_uids(identities))

    def test_epic_adapter_identity_format_fails_closed(self):
        with self.assertRaises(probe.ProbeInputError):
            probe.provider_uid_candidates("epic", "missing-separator")
        with self.assertRaises(probe.ProbeInputError):
            probe.provider_uid_candidates("epic", "too:many:parts")
        with self.assertRaises(probe.ProbeInputError):
            probe.provider_uid_candidates("gog", "")

    def test_uid_probe_query_has_no_title_fuzzy_or_guessed_provider_source(self):
        query = probe.build_uid_probe_query(["namespace-1", "offer-1", "42"])
        self.assertIn('uid = ("42","namespace-1","offer-1")', query)
        self.assertNotIn("search ", query.casefold())
        self.assertNotIn("title", query.casefold())
        self.assertNotIn("external_game_source =", query)
        self.assertNotIn("category", query.casefold())

    def test_provider_matches_are_observations_not_authorized_bindings(self):
        identities = [
            {
                "giveaway_game_key": "meta-v1:correlation-only",
                "source_id": "epic",
                "source_product_id": "ns:offer",
                "uid_candidates": [
                    {"kind": "epic_namespace", "uid": "ns"},
                    {"kind": "epic_offer_id", "uid": "offer"},
                ],
            }
        ]
        rows = [
            {"uid": "ns", "external_game_source": 17, "game": 1000},
            {"uid": "unrelated", "external_game_source": 18, "game": 2000},
        ]
        observed = probe.observed_provider_matches(identities, rows, {17: "Live provider source"})
        self.assertEqual(observed[0]["probe_status"], "candidate_rows_observed")
        self.assertFalse(observed[0]["production_binding_authorized"])
        self.assertEqual(observed[0]["observed_matches"][0]["uid"], "ns")
        self.assertEqual(observed[0]["observed_matches"][0]["external_game_source_name"], "Live provider source")

    def test_steam_reverse_mapping_requires_exact_one_decimal_appid(self):
        result = probe.classify_steam_backmap(
            [1000, 2000, 3000, 4000],
            [
                {"game": 1000, "uid": "10", "external_game_source": 77},
                {"game": 2000, "uid": "20", "external_game_source": 77},
                {"game": 2000, "uid": "21", "external_game_source": 77},
                {"game": 3000, "uid": "not-an-appid", "external_game_source": 77},
            ],
            77,
        )
        self.assertEqual(result[1000], {"status": "mapped", "steam_appid": "10"})
        self.assertEqual(result[2000]["status"], "steam_mapping_ambiguous")
        self.assertEqual(result[3000]["status"], "invalid_values")
        self.assertEqual(result[4000]["status"], "steam_mapping_missing")

    def test_steam_backmap_query_uses_live_resolved_steam_source_id(self):
        query = probe.build_steam_backmap_query([1000, 2000], 77)
        self.assertIn("external_game_source = 77", query)
        self.assertIn("game = (1000,2000)", query)
        self.assertNotIn("category", query.casefold())

    def test_probe_scope_is_explicitly_bounded(self):
        snapshot = {
            "contract": "CROSS-PLATFORM-GIVEAWAY-V1",
            "games": [
                {
                    "canonical_game_key": f"source-v1:gog:{value}",
                    "offers": [{"source_id": "gog", "source_product_id": str(value)}],
                }
                for value in range(5)
            ],
        }
        identities, scope = probe.exact_provider_identities(snapshot, limit=2)
        self.assertEqual(len(identities), 2)
        self.assertTrue(scope["truncated"])
        self.assertEqual(scope["eligible_offer_count"], 5)
        self.assertEqual(scope["probed_offer_count"], 2)

    def test_source_id_name_conflict_fails_closed(self):
        with self.assertRaises(probe.ProbeInputError):
            probe.source_names_by_id([{"id": 5, "name": "One"}, {"id": 5, "name": "Two"}])


if __name__ == "__main__":
    unittest.main(verbosity=2)
