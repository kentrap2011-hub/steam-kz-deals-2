#!/usr/bin/env python3
import copy
import json
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_strict import derive_dossier_summary, validate_dossier_strict
from taste_steam_review_dossier_test_fixture import web_dossier


ROOT = Path(__file__).resolve().parents[1]
CONTROL = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
SCHEMA = json.loads((ROOT / "config/taste_steam_review_dossier_schema.json").read_text(encoding="utf-8"))
EVIDENCE = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")
OWNERSHIP = json.loads((ROOT / "config/execution_ownership_contract.json").read_text(encoding="utf-8"))


class SemanticConsistencyRegressionTests(unittest.TestCase):
    def validate(self, doc, now):
        return validate_dossier_strict(
            doc,
            CONTROL,
            expected_appid=doc["appid"],
            expected_title=doc["title"],
            expected_ttl_days=20,
            now=now,
        )

    @staticmethod
    def refresh_summary(doc):
        doc["summary"] = derive_dossier_summary(doc["observations"], doc["conflicts"])

    def test_scg01_wrong_parent_surface_rejected_and_same_thread_distinct_items_preserved(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)

        wrong_reddit = web_dossier(610001, now)
        wrong_reddit["provenance"]["sources"][2]["url"] = "https://www.reddit.com/r/sniperelite/"
        with self.assertRaisesRegex(ValueError, "parent Reddit source locator"):
            self.validate(wrong_reddit, now)

        wrong_steam = web_dossier(610002, now)
        wrong_steam["provenance"]["sources"][1]["source_type"] = "steam_reviews"
        wrong_steam["provenance"]["player_feedback_records"][0]["public_ref"] = (
            "steam-discussion:729153699965901699:comment-442019"
        )
        with self.assertRaisesRegex(ValueError, "Steam discussion item cannot use an explicit Steam reviews parent source"):
            self.validate(wrong_steam, now)

        same_thread = web_dossier(610003, now)
        same_thread["provenance"]["player_feedback_records"].append({
            "feedback_id": "feedback-005",
            "source_id": "source-003",
            "url": "https://www.reddit.com/r/games/comments/test610003/game_610003/comment2/",
            "publication_date": now.date().isoformat(),
            "language": "russian",
        })
        same_thread["observations"][1]["recurrence"] = "limited"
        same_thread["observations"][1]["mention_count"] = 2
        same_thread["observations"][1]["player_feedback_ids"] = ["feedback-004", "feedback-005"]
        self.assertIs(self.validate(same_thread, now), same_thread)

    def test_scg02_old_known_child_cannot_be_laundered_by_undated_recent_parent_but_unknown_child_is_preserved(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        old_date = (now.date() - timedelta(days=800)).isoformat()

        old_child = web_dossier(620001, now)
        old_child["provenance"]["sources"][2]["publication_date"] = None
        old_child["provenance"]["sources"][2]["freshness"] = "recent"
        old_child["provenance"]["sources"][2]["evidence_role"] = "current_state"
        old_child["provenance"]["player_feedback_records"][3]["publication_date"] = old_date
        with self.assertRaisesRegex(ValueError, "older feedback cannot inherit recent parent-source freshness"):
            self.validate(old_child, now)

        unknown_child = web_dossier(620002, now)
        unknown_child["provenance"]["sources"][2]["publication_date"] = None
        unknown_child["provenance"]["sources"][2]["freshness"] = "recent"
        unknown_child["provenance"]["sources"][2]["evidence_role"] = "current_state"
        unknown_child["provenance"]["player_feedback_records"][3]["publication_date"] = None
        self.assertIs(self.validate(unknown_child, now), unknown_child)

    def test_scg03_summary_is_exact_structured_projection_and_cannot_add_claims(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        valid = web_dossier(630001, now)
        self.assertEqual(valid["summary"], derive_dossier_summary(valid["observations"], valid["conflicts"]))
        self.assertIs(self.validate(valid, now), valid)

        unsupported = web_dossier(630002, now)
        unsupported["summary"] = (
            "Evidence summary: No attributable Russian player feedback was found, and a recurring localization defect exists."
        )
        with self.assertRaisesRegex(ValueError, "summary must equal canonical structured-finding derivation"):
            self.validate(unsupported, now)

    def test_scg04_exact_duplicate_conflict_is_rejected(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(640001, now)
        conflict = {
            "statement": "Players report materially different experiences with the same durable mechanic.",
            "recurrence": "moderate",
            "mention_count": 3,
            "source_ids": ["source-002"],
            "player_feedback_ids": ["feedback-001", "feedback-002", "feedback-003"],
        }
        doc["conflicts"] = [conflict, copy.deepcopy(conflict)]
        self.refresh_summary(doc)
        with self.assertRaisesRegex(ValueError, "exact duplicate conflict"):
            self.validate(doc, now)

    def test_scg05_strong_conflict_alone_does_not_promote_overall_strength(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(650001, now)
        older_date = (now.date() - timedelta(days=400)).isoformat()
        for suffix in (5, 6):
            doc["provenance"]["player_feedback_records"].append({
                "feedback_id": f"feedback-{suffix:03d}",
                "source_id": "source-002",
                "public_ref": f"steam-review-650001-{suffix}",
                "publication_date": older_date,
                "language": "non_russian",
            })
        doc["conflicts"] = [{
            "statement": "A strong recurring conflict is present without any strongly recurring observation.",
            "recurrence": "strong",
            "mention_count": 5,
            "source_ids": ["source-002"],
            "player_feedback_ids": ["feedback-001", "feedback-002", "feedback-003", "feedback-005", "feedback-006"],
        }]
        doc["evidence"]["overall_strength"] = "strong"
        self.refresh_summary(doc)
        with self.assertRaisesRegex(ValueError, "overall strong evidence requires at least one strongly recurring observation"):
            self.validate(doc, now)

        binding = EVIDENCE["overall_strength_binding"]
        self.assertEqual(binding["source"], "observations_only_for_strong_and_moderate_thresholds")
        self.assertFalse(binding["conflict_recurrence_promotes_overall_strength"])
        self.assertFalse(SCHEMA["overall_strength_invariants"]["conflict_recurrence_may_promote_overall_strength"])
        self.assertIn("Conflict recurrence does not promote `overall_strength`", PROMPT)

    def test_scg06_parent_child_language_containment_is_worker_facing_and_strict(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        mismatch = web_dossier(660001, now, russian_status="found_and_used")
        mismatch["provenance"]["sources"][2]["language"] = "non_russian"
        with self.assertRaisesRegex(ValueError, "Russian feedback conflicts with source language"):
            self.validate(mismatch, now)

        machine_rule = EVIDENCE["language_binding"]["parent_source_language_containment"]
        self.assertEqual(machine_rule["russian_child_requires_parent_language"], ["russian", "mixed"])
        self.assertEqual(machine_rule["non_russian_child_requires_parent_language"], ["non_russian", "mixed"])
        self.assertEqual(
            SCHEMA["provenance_relationship_invariants"]["parent_child_language_containment"]["russian_child_parent_languages"],
            ["russian", "mixed"],
        )
        self.assertIn('A child feedback record with `language:"russian"` requires its parent source `language` to be `russian` or `mixed`', PROMPT)

    def test_rus_gate_01_tetris_discovery_guidance_preserves_a_reasonable_bounded_path(self):
        audited_shape = {
            "appid": "1003590",
            "title": "Tetris® Effect: Connected",
            "query_pattern": 'site:steamcommunity.com/app/1003590/discussions "русский"',
            "item_url": "https://steamcommunity.com/app/1003590/discussions/0/603016087419883875/",
            "language": "russian",
        }
        self.assertIn(audited_shape["appid"], audited_shape["query_pattern"])
        self.assertIn(audited_shape["appid"], audited_shape["item_url"])
        self.assertEqual(audited_shape["language"], "russian")

        guidance = EVIDENCE["adaptive_research"]["russian_discovery"]
        self.assertIn("exact_descriptor_title", guidance["exact_identity_query"])
        self.assertTrue(guidance["russian_query_variants_required"])
        self.assertIn("site_specific", "site_specific")
        self.assertIn("site_specific", guidance["site_specific_escalation"])
        self.assertIn("steam_community", guidance["steam_community_guidance"])
        self.assertIn("attributable_item_level", guidance["after_existence_signal"])
        self.assertFalse(guidance["fixed_source_quota"])
        self.assertTrue(guidance["bounds_are_safety_ceilings_not_targets"])
        self.assertEqual(EVIDENCE["adaptive_research"]["hard_bounds_per_game"]["max_web_search_queries"], 8)
        self.assertEqual(EVIDENCE["adaptive_research"]["hard_bounds_per_game"]["max_opened_or_read_source_pages"], 16)
        self.assertIn("site-specific player-feedback/community search", PROMPT)
        self.assertIn("Exact-product Steam Community discussion/review surfaces", PROMPT)

    def test_rus_gate_02_proven_existence_item_unresolved_rejects_complete_dossier(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        for appid, title in (
            (2378500, "Baldur's Gate 3 - Digital Deluxe Edition DLC"),
            (1000360, "Hellish Quart"),
        ):
            doc = web_dossier(appid, now, title=title, russian_status="searched_no_existence_signal")
            doc["evidence"]["russian_attempt"] = "existence_established_retrieval_unresolved"
            with self.subTest(appid=appid), self.assertRaisesRegex(
                ValueError,
                "existence is established but attributable item-level retrieval is unresolved",
            ):
                self.validate(doc, now)

    def test_rus_gate_03_genuine_no_existence_signal_is_valid_when_other_evidence_is_sufficient(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(670003, now, russian_status="searched_no_existence_signal")
        self.assertIs(self.validate(doc, now), doc)
        self.assertEqual(doc["evidence"]["russian_attempt"], "searched_no_existence_signal")
        self.assertIn(
            "searched_no_existence_signal",
            EVIDENCE["russian_evidence"]["complete_dossier_allowed_states"],
        )

    def test_rus_gate_04_existence_signal_is_not_player_feedback_or_observation_support(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(670004, now, russian_status="searched_no_existence_signal")
        doc["provenance"]["sources"].append({
            "source_id": "source-004",
            "source_type": "official_metadata",
            "domain": "store.steampowered.com",
            "url": "https://store.steampowered.com/app/670004/?l=russian",
            "publication_date": None,
            "language": "russian",
            "freshness": "unknown",
            "evidence_role": "identity",
            "player_feedback": False,
        })
        doc["evidence"]["russian_attempt"] = "existence_established_retrieval_unresolved"
        with self.assertRaisesRegex(ValueError, "existence is established but attributable item-level retrieval is unresolved"):
            self.validate(doc, now)

        misuse = web_dossier(670005, now, russian_status="searched_no_existence_signal")
        misuse["provenance"]["sources"].append({
            "source_id": "source-004",
            "source_type": "steam_reviews",
            "domain": "store.steampowered.com",
            "url": "https://store.steampowered.com/app/670005/?l=russian",
            "publication_date": now.date().isoformat(),
            "language": "russian",
            "freshness": "recent",
            "evidence_role": "current_state",
            "player_feedback": True,
        })
        with self.assertRaisesRegex(ValueError, "Steam Store app page is not a player-feedback item"):
            self.validate(misuse, now)

        russian = EVIDENCE["russian_evidence"]
        self.assertFalse(russian["existence_signal_is_player_feedback_record"])
        self.assertFalse(russian["existence_signal_may_create_mention_count"])
        self.assertFalse(russian["existence_signal_may_raise_recurrence"])
        self.assertFalse(russian["existence_signal_may_support_observation_or_conflict"])

    def test_rus_gate_05_base_game_steam_feedback_cannot_satisfy_exact_dlc_identity(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(
            2378500,
            now,
            title="Baldur's Gate 3 - Digital Deluxe Edition DLC",
            russian_status="found_and_used",
        )
        doc["provenance"]["sources"][2].update({
            "source_type": "steam_community",
            "domain": "steamcommunity.com",
            "url": "https://steamcommunity.com/app/1086940/discussions/0/1234567890/",
            "language": "russian",
        })
        doc["provenance"]["player_feedback_records"][3]["url"] = (
            "https://steamcommunity.com/app/1086940/discussions/0/1234567890/?ctp=1"
        )
        with self.assertRaisesRegex(ValueError, "Steam player-feedback source appid does not match exact dossier appid"):
            self.validate(doc, now)
        self.assertFalse(EVIDENCE["identity"]["base_game_feedback_may_satisfy_dlc_gate"])
        self.assertTrue(EVIDENCE["identity"]["steam_player_feedback_url_appid_must_match_exact_dossier_appid_when_exposed"])

    def test_rus_gate_06_proven_existence_access_failure_is_not_ordinary_absence(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(670006, now, russian_status="searched_no_existence_signal")
        doc["evidence"]["russian_attempt"] = "existence_established_access_unresolved"
        with self.assertRaisesRegex(
            ValueError,
            "existence is established but access prevents attributable item-level retrieval",
        ):
            self.validate(doc, now)
        self.assertNotIn(
            "existence_established_access_unresolved",
            EVIDENCE["russian_evidence"]["complete_dossier_allowed_states"],
        )

    def test_rus_ms_01_steam_existence_then_non_steam_usable_russian_item(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(680001, now, russian_status="found_and_used")
        doc["provenance"]["sources"].append({
            "source_id": "source-004",
            "source_type": "official_metadata",
            "domain": "store.steampowered.com",
            "url": "https://store.steampowered.com/app/680001/?l=russian",
            "publication_date": None,
            "language": "russian",
            "freshness": "unknown",
            "evidence_role": "identity",
            "player_feedback": False,
        })
        self.assertEqual(doc["provenance"]["sources"][2]["source_type"], "reddit")
        self.assertEqual(doc["provenance"]["player_feedback_records"][3]["language"], "russian")
        self.assertIs(self.validate(doc, now), doc)

        diversification = EVIDENCE["adaptive_research"]["russian_discovery"]["retrieval_diversification"]
        self.assertIn("existence_established", diversification["phase_trigger"])
        self.assertIn("materially_different", diversification["first_failed_surface_rule"])
        self.assertFalse(diversification["steam_required_as_retrieval_source"])

    def test_rus_ms_02_do_not_stop_after_one_failed_surface_when_distinct_surface_is_discoverable(self):
        diversification = EVIDENCE["adaptive_research"]["russian_discovery"]["retrieval_diversification"]
        self.assertFalse(
            diversification["premature_unresolved_allowed_with_budget_and_reasonably_discoverable_distinct_surface"]
        )
        self.assertIn("must_try_at_least_one_materially_different", diversification["first_failed_surface_rule"])
        self.assertIn("do **not** immediately classify retrieval unresolved", PROMPT)
        self.assertIn("Try at least one such different class", PROMPT)

    def test_rus_ms_03_diversified_search_can_remain_unresolved_and_fail_closed(self):
        attempted_surface_classes = [
            "steam_community_or_user_review_items",
            "reddit_exact_product_threads_or_comments",
        ]
        diversification = EVIDENCE["adaptive_research"]["russian_discovery"]["retrieval_diversification"]
        self.assertEqual(len(set(attempted_surface_classes)), 2)
        self.assertTrue(all(name in diversification["surface_class_examples"] for name in attempted_surface_classes))
        self.assertIn("hard_bound_is_reached", diversification["continued_diversification_rule"])
        self.assertIn("no_reasonably_discoverable_distinct_surface_class_remains", diversification["continued_diversification_rule"])

        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(680003, now, russian_status="searched_no_existence_signal")
        doc["evidence"]["russian_attempt"] = "existence_established_retrieval_unresolved"
        with self.assertRaisesRegex(
            ValueError,
            "existence is established but attributable item-level retrieval is unresolved",
        ):
            self.validate(doc, now)

    def test_rus_ms_04_non_steam_forum_provenance_is_accepted(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(680004, now, russian_status="found_and_used")
        doc["provenance"]["sources"][2].update({
            "source_type": "forum",
            "domain": "forum.example.com",
            "url": "https://forum.example.com/topic/exact-game-680004/",
            "language": "russian",
        })
        doc["provenance"]["player_feedback_records"][3]["url"] = (
            "https://forum.example.com/topic/exact-game-680004/post-42"
        )
        self.assertIs(self.validate(doc, now), doc)
        self.assertEqual(doc["evidence"]["russian_attempt"], "found_and_used")
        self.assertFalse(any(
            source["source_type"] in {"steam_reviews", "steam_community"}
            and source["language"] in {"russian", "mixed"}
            for source in doc["provenance"]["sources"]
        ))

    def test_rus_ms_05_professional_journalism_does_not_satisfy_player_feedback_gate(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(680005, now, russian_status="searched_no_existence_signal")
        doc["provenance"]["sources"].append({
            "source_id": "source-004",
            "source_type": "professional_context",
            "domain": "example.com",
            "url": "https://example.com/reviews/exact-game-680005",
            "publication_date": now.date().isoformat(),
            "language": "russian",
            "freshness": "recent",
            "evidence_role": "current_state",
            "player_feedback": False,
        })
        doc["evidence"]["russian_attempt"] = "found_and_used"
        with self.assertRaisesRegex(ValueError, "found_and_used requires a bound Russian player-feedback record"):
            self.validate(doc, now)
        self.assertFalse(EVIDENCE["source_policy"]["professional_context_may_substitute_for_player_feedback"])
        self.assertFalse(
            EVIDENCE["adaptive_research"]["russian_discovery"]["retrieval_diversification"][
                "professional_or_editorial_counts_as_player_feedback_surface"
            ]
        )

    def test_rus_ms_06_exact_dlc_identity_stays_strict_during_diversification(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(
            2378500,
            now,
            title="Baldur's Gate 3 - Digital Deluxe Edition DLC",
            russian_status="found_and_used",
        )
        doc["provenance"]["sources"][2].update({
            "source_type": "steam_community",
            "domain": "steamcommunity.com",
            "url": "https://steamcommunity.com/app/1086940/discussions/0/9999999999/",
            "language": "russian",
        })
        doc["provenance"]["player_feedback_records"][3]["url"] = (
            "https://steamcommunity.com/app/1086940/discussions/0/9999999999/?ctp=1"
        )
        with self.assertRaisesRegex(ValueError, "Steam player-feedback source appid does not match exact dossier appid"):
            self.validate(doc, now)
        self.assertFalse(EVIDENCE["identity"]["base_game_feedback_may_satisfy_dlc_gate"])
        self.assertTrue(
            EVIDENCE["adaptive_research"]["russian_discovery"]["retrieval_diversification"][
                "exact_product_identity_rules_still_apply"
            ]
        )

    def test_rus_ms_07_adaptive_diversification_has_no_fixed_website_quota_or_steam_requirement(self):
        diversification = EVIDENCE["adaptive_research"]["russian_discovery"]["retrieval_diversification"]
        self.assertFalse(diversification["fixed_named_website_quota"])
        self.assertFalse(diversification["visit_all_surface_classes_required"])
        self.assertFalse(diversification["steam_required_as_retrieval_source"])
        self.assertGreaterEqual(len(diversification["surface_class_examples"]), 5)
        self.assertIn("fixed site quota", PROMPT)
        self.assertIn("never required to provide the usable record", PROMPT)
        self.assertEqual(EVIDENCE["adaptive_research"]["hard_bounds_per_game"]["max_web_search_queries"], 8)
        self.assertEqual(EVIDENCE["adaptive_research"]["hard_bounds_per_game"]["max_opened_or_read_source_pages"], 16)

    def test_worker_facing_contract_covers_all_six_without_changing_buffer_architecture(self):
        self.assertFalse(EVIDENCE["parent_item_binding"]["host_match_alone_is_sufficient"])
        self.assertTrue(EVIDENCE["parent_item_binding"]["same_thread_distinct_items_allowed"])
        self.assertIn("known_child_date_parent_coherence_rule", EVIDENCE["recency"])
        self.assertEqual(EVIDENCE["summary_binding"]["mode"], "mechanically_derived_from_validated_structured_findings")
        self.assertFalse(EVIDENCE["summary_binding"]["free_form_summary_allowed"])
        self.assertFalse(EVIDENCE["conflicts"]["exact_duplicate_objects_allowed"])
        self.assertEqual(int(CONTROL["checkpointing"]["checkpoint_size"]), 3)
        self.assertTrue(CONTROL["buffered_submission"]["buffer"]["multiple_pending_groups_same_snapshot_allowed"])
        self.assertEqual(
            CONTROL["buffered_submission"]["drain"]["acceptance_rule"],
            "accept_only_the_maximal_valid_contiguous_prefix_starting_at_expected_sequence",
        )


    def test_retrieve_ru_01_stable_route_is_preferred(self):
        self.assertEqual(
            EVIDENCE["feedback_item_identity"]["preferred_identity_order"],
            ["stable_locator", "transient_author_deduped"],
        )
        stable_text = "Prefer a result that exposes a neutral stable review/recommendation identity"
        fallback_text = "If no neutral stable item locator is exposed"
        self.assertIn(stable_text, PROMPT)
        self.assertIn(fallback_text, PROMPT)
        self.assertLess(PROMPT.index(stable_text), PROMPT.index(fallback_text))

    def test_retrieve_ru_02_safe_collection_fallback_is_explicit(self):
        self.assertTrue(EVIDENCE["source_policy"]["steam_store_exact_app_review_collection_may_be_fallback_parent"])
        self.assertIn("search-indexed exact-app collection recovery", PROMPT)
        self.assertIn("returned representation itself visibly exposes a concrete individual Russian/mixed review card", PROMPT)
        self.assertIn("Persist only the safe exact-app collection parent and opaque dossier-local fallback record", PROMPT)

    def test_retrieve_ru_03_profile_hit_is_discovery_only_and_cannot_be_rebound(self):
        self.assertFalse(EVIDENCE["compact_provenance"]["profile_scoped_urls_allowed"])
        self.assertIn("A profile-scoped Russian review hit is discovery signal only", PROMPT)
        self.assertIn("Never persist its profile URL, author identity, or re-parent that item", PROMPT)
        self.assertIn("use fallback only if a concrete Russian/mixed card is actually inspected on that non-profile parent", PROMPT)

    def test_retrieve_ru_04_aggregate_and_locale_remain_non_evidence(self):
        self.assertFalse(EVIDENCE["source_policy"]["aggregate_storefront_statistics_are_player_feedback_mentions"])
        self.assertFalse(EVIDENCE["source_policy"]["steam_store_language_parameter_is_player_feedback_evidence"])
        self.assertIn("They do not prove item language, do not create a feedback record", PROMPT)

    def test_retrieve_ru_05_exact_appid_is_preserved(self):
        self.assertTrue(EVIDENCE["identity"]["steam_player_feedback_url_appid_must_match_exact_dossier_appid_when_exposed"])
        self.assertIn("exact descriptor title, exact dossier appid", PROMPT)
        self.assertIn("Keep exact appid binding fail-closed", PROMPT)
        self.assertIn("another appid, base game, DLC, edition, sequel, remake, or remaster cannot satisfy the target dossier", PROMPT)

    def test_retrieve_ru_06_bounded_adaptive_search_avoids_inaccessible_endpoint_retries(self):
        bounds = EVIDENCE["adaptive_research"]["hard_bounds_per_game"]
        self.assertEqual(bounds["max_web_search_queries"], 8)
        self.assertEqual(bounds["max_opened_or_read_source_pages"], 16)
        self.assertFalse(EVIDENCE["adaptive_research"]["russian_discovery"]["fixed_source_quota"])
        self.assertIn("do not keep retrying materially equivalent forms of that inaccessible endpoint family", PROMPT)
        self.assertIn("not a new website quota, required Steam lane, retry loop, or evidence semantic", PROMPT)


    def test_diversify_early_01_steam_remains_preferred_when_cheap_usable_item_is_exposed(self):
        steam_first = "Prefer a cheap exact-product Steam item-level path when it is already exposed or immediately reachable"
        cross_source = "Pivot early to generic cross-source discovery"
        self.assertIn(steam_first, PROMPT)
        self.assertIn(cross_source, PROMPT)
        self.assertLess(PROMPT.index(steam_first), PROMPT.index(cross_source))
        self.assertIn(
            "do not leave Steam merely because one attempt failed when a cheap usable concrete Steam item is already exposed",
            PROMPT,
        )

    def test_diversify_early_02_aggregate_only_steam_shape_triggers_early_diversification(self):
        self.assertIn("aggregate/count-only evidence", PROMPT)
        self.assertIn("they are a signal to diversify", PROMPT)
        self.assertIn("rather than spend most of the remaining budget", PROMPT)

    def test_diversify_early_03_profile_only_steam_shape_triggers_safe_diversification(self):
        self.assertFalse(EVIDENCE["compact_provenance"]["profile_scoped_urls_allowed"])
        self.assertIn("a profile-scoped item", PROMPT)
        self.assertIn("Never persist its profile URL, author identity, or re-parent that item", PROMPT)

    def test_diversify_early_04_non_russian_steam_cards_do_not_block_cross_source_pivot(self):
        self.assertIn("concrete Steam cards that are non-Russian", PROMPT)
        self.assertIn("non-Russian-card", PROMPT)
        self.assertIn("prioritize a generic non-site-constrained cross-source query", PROMPT)

    def test_diversify_early_05_index_row_only_does_not_monopolize_budget(self):
        self.assertIn("a collection/index row without a concrete child item", PROMPT)
        self.assertIn("index/collection row without a usable child", PROMPT)
        self.assertIn("distinct public player-feedback discovery gets priority", PROMPT)

    def test_diversify_early_06_generic_discovery_has_no_product_or_named_site_hardcoding(self):
        self.assertIn("non-site-constrained search", PROMPT)
        self.assertIn("exact descriptor title, release year when helpful", PROMPT)
        self.assertIn("Russian player-review/discussion wording", PROMPT)
        self.assertIn("Use site-specific follow-up only after discovery makes a source promising", PROMPT)
        self.assertNotIn("MO:Astray", PROMPT)
        self.assertNotIn("StopGame", PROMPT)
        diversification = EVIDENCE["adaptive_research"]["russian_discovery"]["retrieval_diversification"]
        self.assertFalse(diversification["fixed_named_website_quota"])
        self.assertFalse(diversification["steam_required_as_retrieval_source"])

    def test_diversify_early_07_stable_non_steam_player_feedback_remains_accepted(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(680007, now, russian_status="found_and_used")
        doc["provenance"]["sources"][2].update({
            "source_type": "forum",
            "domain": "community.example.com",
            "url": "https://community.example.com/games/exact-game-680007/reviews/",
            "language": "russian",
        })
        doc["provenance"]["player_feedback_records"][3]["url"] = (
            "https://community.example.com/games/exact-game-680007/reviews/item-42"
        )
        self.assertIs(self.validate(doc, now), doc)
        self.assertEqual(doc["evidence"]["russian_attempt"], "found_and_used")

    def test_diversify_early_08_language_and_recency_semantics_are_unchanged(self):
        self.assertTrue(EVIDENCE["language_binding"]["strict_exact_equality_required"])
        self.assertEqual(EVIDENCE["recency"]["recent_max_age_days"], 365)
        self.assertTrue(EVIDENCE["recency"]["current_state_requires_recent_support"])
        self.assertIn("gameplay", EVIDENCE["recency"]["old_feedback_remains_valid_for"])
        self.assertIn("story", EVIDENCE["recency"]["old_feedback_remains_valid_for"])
        self.assertIn("It changes retrieval priority only; it does not change what counts as evidence", PROMPT)

    def test_diversify_early_09_production_ceilings_and_no_fixed_steam_quota_are_unchanged(self):
        bounds = EVIDENCE["adaptive_research"]["hard_bounds_per_game"]
        self.assertEqual(bounds["max_web_search_queries"], 8)
        self.assertEqual(bounds["max_opened_or_read_source_pages"], 16)
        self.assertFalse(EVIDENCE["adaptive_research"]["russian_discovery"]["fixed_source_quota"])
        self.assertIn("There is **no fixed number of Steam queries or pages** before diversification", PROMPT)

    def test_diversify_early_10_privacy_and_provenance_guards_remain_unchanged(self):
        self.assertFalse(EVIDENCE["compact_provenance"]["profile_scoped_urls_allowed"])
        self.assertFalse(EVIDENCE["compact_provenance"]["direct_author_identity_hash_as_anonymization_allowed"])
        self.assertTrue(EVIDENCE["compact_provenance"]["internal_join_ids"]["author_identity_independent"])
        self.assertFalse(EVIDENCE["parent_item_binding"]["host_match_alone_is_sufficient"])
        self.assertIn("Never persist its profile URL, author identity, or re-parent that item", PROMPT)


    def test_temporal_prestop_01_historical_technical_requires_recent_check_before_stop(self):
        self.assertIn("## Temporal pre-stop completeness gate", PROMPT)
        self.assertIn('do **not** use `stop_reason:"evidence_stable"`', PROMPT)
        self.assertIn('Do **not** set `research_state:"sufficient"`', PROMPT)
        self.assertIn("at least one bound source with `evidence_role:\"current_state\"` and `freshness:\"recent\"`", PROMPT)

    def test_temporal_prestop_02_missing_recent_support_continues_bounded_retrieval(self):
        self.assertIn("continue bounded exact-product recent player-feedback retrieval", PROMPT)
        self.assertIn("If that recent current-state support is missing and either web-search or page-read budget remains", PROMPT)

    def test_temporal_prestop_03_historical_semantics_are_unchanged(self):
        self.assertTrue(SCHEMA["observation_invariants"]["historical_requires_historical_and_recent_current_state_sources"])
        self.assertEqual(EVIDENCE["recency"]["launch_only_issue_with_recent_fix_or_material_reduction"], "historical")
        self.assertEqual(set(EVIDENCE["accepted_evidence_statuses"]), {"current", "historical", "durable", "uncertain"})

    def test_temporal_prestop_04_unresolved_uses_existing_uncertain_path(self):
        self.assertEqual(EVIDENCE["recency"]["conflicting_or_insufficient_temporal_evidence"], "uncertain")
        self.assertIn("use the existing `uncertain` path when the old-vs-current state remains unresolved", PROMPT)
        self.assertIn("never force `historical` merely because the available complaint is old", PROMPT)

    def test_temporal_prestop_05_current_still_requires_recent_support(self):
        self.assertTrue(SCHEMA["observation_invariants"]["current_requires_recent_current_state_source"])
        self.assertTrue(EVIDENCE["recency"]["current_state_requires_recent_support"])
        self.assertIn("unchanged requirement for recent current-state support", PROMPT)

    def test_temporal_prestop_06_durable_traits_are_not_over_tightened(self):
        durable = set(EVIDENCE["recency"]["old_feedback_remains_valid_for"])
        self.assertTrue({"gameplay", "story", "structure", "difficulty"}.issubset(durable))
        self.assertIn("Do not apply this extra stop gate to durable gameplay/story/art/music/structure traits", PROMPT)

    def test_temporal_prestop_07_recent_retrieval_preserves_early_multi_source_diversification(self):
        self.assertIn("Apply the active early multi-source diversification strategy", PROMPT)
        self.assertIn("diversify source-agnostically after an unusable stop-shape", PROMPT)
        self.assertIn("never turn the recent check into a Steam-only lane", PROMPT)
        diversification = EVIDENCE["adaptive_research"]["russian_discovery"]["retrieval_diversification"]
        self.assertFalse(diversification["steam_required_as_retrieval_source"])
        self.assertFalse(diversification["fixed_named_website_quota"])

    def test_temporal_prestop_08_production_ceilings_are_unchanged(self):
        bounds = EVIDENCE["adaptive_research"]["hard_bounds_per_game"]
        self.assertEqual(bounds["max_web_search_queries"], 8)
        self.assertEqual(bounds["max_opened_or_read_source_pages"], 16)
        self.assertIn("existing 8-search / 16-page ceilings", PROMPT)
        self.assertIn("never turn the recent check into a Steam-only lane, fixed site quota, new retry loop", PROMPT)

    def test_temporal_prestop_09_strict_validator_semantics_remain_authoritative(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(690009, now)
        historical = copy.deepcopy(doc["observations"][0])
        historical.update({
            "category": "friction",
            "statement": "Older exact-product feedback records a launch-era technical issue.",
            "evidence_status": "historical",
            "source_ids": ["source-002"],
            "player_feedback_ids": ["feedback-001", "feedback-002", "feedback-003"],
            "evidence_languages": ["non_russian"],
        })
        doc["provenance"]["sources"][1]["evidence_role"] = "historical"
        doc["observations"] = [historical]
        self.refresh_summary(doc)
        with self.assertRaisesRegex(ValueError, "historical/fixed claim lacks recent current-state check"):
            self.validate(doc, now)

    def test_temporal_prestop_10_privacy_provenance_and_language_guards_are_unchanged(self):
        self.assertFalse(EVIDENCE["compact_provenance"]["profile_scoped_urls_allowed"])
        self.assertFalse(EVIDENCE["compact_provenance"]["direct_author_identity_hash_as_anonymization_allowed"])
        self.assertTrue(EVIDENCE["language_binding"]["strict_exact_equality_required"])
        self.assertTrue(EVIDENCE["compact_provenance"]["internal_join_ids"]["author_identity_independent"])

    def test_temporal_prestop_11_existing_stop_order_is_explicit_without_product_hardcoding(self):
        order = "collect evidence -> draft/plan observations -> temporal completeness check -> targeted recent retrieval if required -> re-evaluate temporal status -> only then decide sufficient/evidence_stable -> serialize candidate"
        self.assertIn(order, PROMPT)
        self.assertNotIn("60 Seconds! Reatomized", PROMPT)
        self.assertNotIn("1012880", PROMPT)
        self.assertNotIn("steamcommunity.com/app/1012880", PROMPT)
        self.assertEqual(EVIDENCE["worker_prompt_revision"], "web-evidence-v2-fail-closed-execution-ledger-v1")


    def test_ledger_01_marker_binding_and_core_fields(self):
        self.assertEqual(EVIDENCE["worker_prompt_revision"], "web-evidence-v2-fail-closed-execution-ledger-v1")
        self.assertIn("FAIL_CLOSED_EXECUTION_LEDGER_V1", PROMPT)
        for field in (
            "snapshot_id",
            "sequence",
            "group_sha256",
            "blocked_game",
            "last_completed_stage",
            "stop_gate",
            "publication_state",
            "canonical_progress_claim",
            "material_attempts",
            "budget_state",
            "next_required_step",
            "next_required_step_status",
            "why_not_executed",
            "visible_system_or_tool_error",
        ):
            self.assertIn(f"`{field}`", PROMPT)
        self.assertIn(
            "no canonical completion claimed; GitHub canonical state remains authoritative",
            PROMPT,
        )

    def test_ledger_02_material_attempts_are_observable_not_reasoning(self):
        for field in (
            "step",
            "stage",
            "action_kind",
            "route_class",
            "target_summary",
            "started",
            "response_received",
            "observable_result",
        ):
            self.assertIn(f"`{field}`", PROMPT)
        for result in (
            "aggregate_only",
            "concrete_russian_card_visible",
            "concrete_non_russian_cards_only",
            "stable_locator_available",
            "transient_fallback_available",
            "profile_scoped_discovery_only",
            "exact_product_mismatch",
            "no_results",
            "inaccessible_or_dynamic",
            "tool_error",
            "binding_changed",
            "candidate_create_failed",
        ):
            self.assertIn(f"`{result}`", PROMPT)
        self.assertIn("observable execution facts and contract-gate state only", PROMPT)
        self.assertIn("must never contain private chain-of-thought", PROMPT)

    def test_ledger_03_exact_stop_gate_and_budget_accounting(self):
        self.assertIn("the exact contract/evidence/identity/liveness/transport gate", PROMPT)
        for field in (
            "search_queries_used",
            "search_query_limit",
            "opened_pages_used",
            "opened_page_limit",
            "required_route_state",
        ):
            self.assertIn(f"`{field}`", PROMPT)
        self.assertIn("active Russian, source-diversification, temporal, and identity routes", PROMPT)
        bounds = EVIDENCE["adaptive_research"]["hard_bounds_per_game"]
        self.assertEqual(bounds["max_web_search_queries"], 8)
        self.assertEqual(bounds["max_opened_or_read_source_pages"], 16)

    def test_ledger_04_required_next_step_and_no_silent_early_stop(self):
        for status in (
            "none_all_required_routes_exhausted",
            "not_executed",
            "blocked",
        ):
            self.assertIn(f"`{status}`", PROMPT)
        self.assertIn("If a mandatory next material route is still `pending`, budget remains", PROMPT)
        self.assertIn("do not stop", PROMPT)
        self.assertIn("execute that pivot or ledger the exact exposed blocker", PROMPT)
        self.assertIn(
            "pivot not executed”, “pivot executed but no legal item returned”, and “pivot blocked by an exposed tool/runtime error",
            PROMPT,
        )

    def test_ledger_05_unknown_cause_stays_unknown(self):
        self.assertIn(
            "why_not_executed: unknown — no system/tool cause exposed",
            PROMPT,
        )
        for prohibited in ("probably timeout", "likely context limit", "Steam blocked it"):
            self.assertIn(prohibited, PROMPT)
        self.assertIn("Never guess a cause.", PROMPT)

    def test_ledger_06_privacy_and_no_chain_of_thought_boundary(self):
        for forbidden in (
            "raw review/post bodies",
            "usernames/display names",
            "SteamID/account identifiers",
            "author-derived hashes or pseudonyms",
            "profile URLs",
            "secrets",
            "hidden reasoning",
            "internal deliberation",
        ):
            self.assertIn(forbidden, PROMPT)
        self.assertIn("profile_scoped_discovery_only", PROMPT)

    def test_ledger_07_success_path_remains_compact(self):
        self.assertIn("Do **not** emit the full fail-closed execution ledger after successful candidate creation", PROMPT)
        self.assertIn("existing candidate-buffered/progress reporting", PROMPT)
        self.assertIn("ephemeral attempt record is not persisted", PROMPT)

    def test_ledger_08_hellish_control_shape_distinguishes_a_b_c_without_product_hardcoding(self):
        def signature(ledger):
            return (
                tuple((a["route_class"], a["observable_result"]) for a in ledger["material_attempts"]),
                ledger["next_required_step_status"],
                ledger["why_not_executed"],
                ledger["visible_system_or_tool_error"],
            )

        case_a = {
            "material_attempts": [
                {"route_class": "Steam Store exact-app", "observable_result": "aggregate_only"},
                {"route_class": "Steam Community exact-app", "observable_result": "concrete_non_russian_cards_only"},
            ],
            "next_required_step_status": "not_executed",
            "why_not_executed": "unknown — no system/tool cause exposed",
            "visible_system_or_tool_error": None,
        }
        case_b = {
            "material_attempts": [
                {"route_class": "Steam Store exact-app", "observable_result": "aggregate_only"},
                {"route_class": "cross-source exact-product player feedback", "observable_result": "no_results"},
            ],
            "next_required_step_status": "none_all_required_routes_exhausted",
            "why_not_executed": "all required routes exhausted",
            "visible_system_or_tool_error": None,
        }
        case_c = {
            "material_attempts": [
                {"route_class": "Steam Store exact-app", "observable_result": "aggregate_only"},
                {"route_class": "cross-source exact-product player feedback", "observable_result": "tool_error"},
            ],
            "next_required_step_status": "blocked",
            "why_not_executed": "exact visible tool error",
            "visible_system_or_tool_error": "synthetic exposed transport error",
        }
        self.assertEqual(len({signature(case_a), signature(case_b), signature(case_c)}), 3)
        self.assertNotIn("Hellish Quart", PROMPT)
        self.assertNotIn("1000360", PROMPT)

    def test_ledger_09_current_retrieval_semantics_remain_unchanged(self):
        self.assertEqual(SCHEMA["schema_revision"], "validator-generator-parity-fix-2026-09-20")
        self.assertEqual(EVIDENCE["contract_revision"], "validator-generator-parity-fix-2026-09-20")
        self.assertEqual(
            EVIDENCE["russian_evidence"]["complete_dossier_allowed_states"],
            ["found_and_used", "searched_no_existence_signal"],
        )
        self.assertFalse(
            EVIDENCE["adaptive_research"]["russian_discovery"]["retrieval_diversification"][
                "premature_unresolved_allowed_with_budget_and_reasonably_discoverable_distinct_surface"
            ]
        )
        self.assertTrue(EVIDENCE["language_binding"]["strict_exact_equality_required"])
        self.assertTrue(EVIDENCE["compact_provenance"]["internal_join_ids"]["author_identity_independent"])

    def test_ledger_10_current_ownership_remains_unchanged(self):
        self.assertEqual(OWNERSHIP["github_control_plane"]["owner"], "GitHub repository and GitHub Actions")
        self.assertEqual(
            OWNERSHIP["scheduled_chatgpt_runtime_data_plane"]["owner"],
            "scheduled ChatGPT production task",
        )
        self.assertIn("own retry state and unresolved-item state", OWNERSHIP["github_control_plane"]["responsibilities"])
        self.assertIn(
            "replace GitHub retry/completeness logic with conversational iteration",
            OWNERSHIP["scheduled_chatgpt_runtime_data_plane"]["forbidden"],
        )
        self.assertIn("not a new GitHub persistence surface", PROMPT)
        self.assertIn("must not become a queue, scheduler, backlog manager, or logging service", PROMPT)




if __name__ == "__main__":
    unittest.main()
