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


if __name__ == "__main__":
    unittest.main()
