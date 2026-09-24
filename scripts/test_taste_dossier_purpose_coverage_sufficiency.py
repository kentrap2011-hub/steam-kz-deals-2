#!/usr/bin/env python3
"""Focused COV-01..COV-15 regressions for Dossier purpose and coverage sufficiency."""
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier_strict import derive_dossier_summary, validate_dossier_strict
from taste_steam_review_dossier_test_fixture import web_dossier


ROOT = Path(__file__).resolve().parents[1]
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")
EVIDENCE = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / "config/taste_steam_review_dossier_schema.json").read_text(encoding="utf-8"))
CONTROL = json.loads((ROOT / "config/taste_steam_review_dossier_contract.json").read_text(encoding="utf-8"))
PERSISTENCE = json.loads((ROOT / "config/taste_steam_review_dossier_persistence_bridge.json").read_text(encoding="utf-8"))
OWNERSHIP = json.loads((ROOT / "config/execution_ownership_contract.json").read_text(encoding="utf-8"))

DIMENSIONS = EVIDENCE["coverage_sufficiency"]["dimensions"]


def set_coverage(doc, *, covered=None, unresolved=(), exhausted=(), closure="broad_neutral_picture"):
    covered = covered or {}
    unresolved = set(unresolved)
    exhausted = set(exhausted)
    entries = []
    for dimension in DIMENSIONS:
        if dimension in covered:
            state = "covered"
            indices = list(covered[dimension])
        elif dimension in unresolved:
            state = "materially_unresolved"
            indices = []
        elif dimension in exhausted:
            state = "exhausted_unavailable"
            indices = []
        else:
            state = "not_material_or_not_applicable"
            indices = []
        entries.append({
            "dimension": dimension,
            "state": state,
            "observation_indices": indices,
        })
    doc["evidence"]["coverage"] = {
        "dimensions": entries,
        "closure_basis": closure,
        "strengths_investigated": True,
        "weaknesses_tradeoffs_investigated": True,
    }


def single_observation_doc(appid, title, *, category, statement, sentiment, dimension, current=False):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    doc = web_dossier(appid, now, title=title)
    if current:
        source_id = "source-003"
        feedback_id = "feedback-004"
        language = "russian"
        evidence_status = "current"
        doc["evidence"]["russian_attempt"] = "found_and_used"
    else:
        source_id = "source-002"
        feedback_id = "feedback-001"
        language = "non_russian"
        evidence_status = "durable"
        doc["evidence"]["russian_attempt"] = "searched_no_existence_signal"
    doc["observations"] = [{
        "category": category,
        "statement": statement,
        "sentiment": sentiment,
        "recurrence": "anecdotal",
        "mention_count": 1,
        "evidence_languages": [language],
        "evidence_status": evidence_status,
        "source_ids": [source_id],
        "player_feedback_ids": [feedback_id],
    }]
    doc["conflicts"] = []
    doc["summary"] = derive_dossier_summary(doc["observations"], doc["conflicts"])
    doc["evidence"]["source_mix_status"] = "single_source_only"
    doc["evidence"]["single_source_reason"] = "Compact exact-product control uses one attributable player-feedback source."
    doc["evidence"]["overall_strength"] = "limited"
    set_coverage(doc, covered={dimension: [0]}, closure="compact_central_experience")
    return doc, now


class PurposeCoverageSufficiencyTests(unittest.TestCase):
    def validate(self, doc, now):
        return validate_dossier_strict(
            doc,
            CONTROL,
            expected_appid=doc["appid"],
            expected_title=doc["title"],
            expected_ttl_days=20,
            now=now,
        )

    def test_cov_01_jurassic_world_evolution_2_localization_only_cannot_close_with_material_gap(self):
        doc, now = single_observation_doc(
            1244460,
            "Jurassic World Evolution 2",
            category="localization",
            statement="A Russian player reports a menu-language behavior without describing the wider game experience.",
            sentiment="neutral",
            dimension="technical_performance_localization_regional",
            current=True,
        )
        set_coverage(
            doc,
            covered={"technical_performance_localization_regional": [0]},
            unresolved=("core_play_mechanics", "progression_development_unlocks", "variety_repetition_over_time"),
        )
        with self.assertRaisesRegex(ValueError, "materially unresolved game-experience coverage"):
            self.validate(doc, now)

    def test_cov_02_rubber_bandits_generic_social_fun_cannot_hide_unknown_repetition(self):
        doc, now = single_observation_doc(
            1206610,
            "Rubber Bandits",
            category="coop",
            statement="A player says the game is fun with friends without describing sustained variety over time.",
            sentiment="positive",
            dimension="multiplayer_coop_dependence",
            current=True,
        )
        set_coverage(
            doc,
            covered={"multiplayer_coop_dependence": [0], "recurring_strengths": [0]},
            unresolved=("variety_repetition_over_time",),
        )
        with self.assertRaisesRegex(ValueError, "materially unresolved game-experience coverage"):
            self.validate(doc, now)

    def test_cov_03_retrowave_one_repetition_complaint_cannot_close_before_broader_coverage(self):
        doc, now = single_observation_doc(
            1239690,
            "Retrowave",
            category="repetition",
            statement="One player describes repetition, without broader corroborating driving or variation context.",
            sentiment="negative",
            dimension="variety_repetition_over_time",
        )
        set_coverage(
            doc,
            covered={"variety_repetition_over_time": [0], "recurring_complaints_tradeoffs": [0]},
            unresolved=("core_play_mechanics",),
        )
        with self.assertRaisesRegex(ValueError, "materially unresolved game-experience coverage"):
            self.validate(doc, now)

    def test_cov_04_terraformers_one_core_loop_anecdote_cannot_skip_progression_and_variety(self):
        doc, now = single_observation_doc(
            1244800,
            "Terraformers",
            category="mechanics",
            statement="One player describes the immediate core loop without long-horizon progression or variety context.",
            sentiment="neutral",
            dimension="core_play_mechanics",
        )
        set_coverage(
            doc,
            covered={"core_play_mechanics": [0]},
            unresolved=("progression_development_unlocks", "variety_repetition_over_time"),
        )
        with self.assertRaisesRegex(ValueError, "materially unresolved game-experience coverage"):
            self.validate(doc, now)

    def test_cov_05_final_fantasy_vi_story_pacing_slice_cannot_skip_combat_progression_variety(self):
        doc, now = single_observation_doc(
            1173820,
            "FINAL FANTASY VI",
            category="pacing",
            statement="A player comments on the opening pace and party/story framing without covering combat or progression.",
            sentiment="mixed",
            dimension="pacing_structure_direction",
        )
        set_coverage(
            doc,
            covered={"pacing_structure_direction": [0], "story_characters_identity_hooks": [0]},
            unresolved=("core_play_mechanics", "progression_development_unlocks", "variety_repetition_over_time"),
        )
        with self.assertRaisesRegex(ValueError, "materially unresolved game-experience coverage"):
            self.validate(doc, now)

    def test_cov_06_exact_product_identity_survives_broader_coverage_for_three_controls(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        for appid, title in (
            (1227690, "Severed Steel"),
            (1222680, "Need for Speed Heat"),
            (1196090, "Scars Above"),
        ):
            with self.subTest(appid=appid):
                doc = web_dossier(appid, now, title=title)
                self.assertEqual(doc["appid"], str(appid))
                self.assertEqual(doc["title"], title)
                self.assertEqual(doc["game_identity"]["corroborators"][0]["value"], str(appid))
                self.assertIs(self.validate(doc, now), doc)

    def test_cov_07_lake_compact_core_loop_can_still_be_sufficient(self):
        doc, now = single_observation_doc(
            1118240,
            "Lake",
            category="mechanics",
            statement="A player directly characterizes the central delivery-and-driving loop.",
            sentiment="mixed",
            dimension="core_play_mechanics",
        )
        set_coverage(
            doc,
            covered={
                "core_play_mechanics": [0],
                "recurring_strengths": [0],
                "recurring_complaints_tradeoffs": [0],
            },
            closure="compact_central_experience",
        )
        self.assertIs(self.validate(doc, now), doc)
        self.assertEqual(len(doc["observations"]), 1)
        self.assertEqual(doc["observations"][0]["mention_count"], 1)

    def test_cov_08_potion_craft_compact_long_horizon_repetition_property_can_be_sufficient(self):
        doc, now = single_observation_doc(
            1210320,
            "Potion Craft",
            category="repetition",
            statement="A player directly describes the long-horizon progression loop becoming repetitive.",
            sentiment="mixed",
            dimension="variety_repetition_over_time",
        )
        set_coverage(
            doc,
            covered={
                "progression_development_unlocks": [0],
                "variety_repetition_over_time": [0],
                "recurring_strengths": [0],
                "recurring_complaints_tradeoffs": [0],
            },
            closure="compact_central_experience",
        )
        self.assertIs(self.validate(doc, now), doc)
        self.assertEqual(len(doc["observations"]), 1)
        self.assertEqual(doc["observations"][0]["mention_count"], 1)

    def test_cov_09_no_fixed_minimum_sources_reviews_searches_pages_or_coverage_score(self):
        no_min = EVIDENCE["coverage_sufficiency"]["no_fixed_minimum"]
        self.assertTrue(all(value is False for value in no_min.values()))
        bounds = EVIDENCE["adaptive_research"]["hard_bounds_per_game"]
        self.assertIsNone(bounds["max_web_search_queries"])
        self.assertIsNone(bounds["max_opened_or_read_source_pages"])
        self.assertFalse(bounds["counts_are_semantic_stop_gates"])
        self.assertIn("There is no minimum number of observations, reviews, sources, searches, pages or covered dimensions", PROMPT)

    def test_cov_10_dossier_remains_profile_agnostic_without_personal_fit_judgment(self):
        purpose = EVIDENCE["downstream_purpose"]
        self.assertEqual(purpose["dossier_role"], "neutral_profile_agnostic_evidence_package")
        self.assertEqual(purpose["user_taste_profile_use"], "forbidden_for_evidence_selection_synthesis_or_stop_decisions")
        self.assertIn("Remain strictly profile-agnostic", PROMPT)
        self.assertIn("Downstream Deep/Taste analysis owns all personal interpretation.", PROMPT)
        self.assertIn("score_personal_fit", CONTROL["ownership"]["forbidden"])

    def test_cov_11_russian_provenance_privacy_and_exact_product_guards_remain_strict(self):
        self.assertTrue(EVIDENCE["russian_evidence"]["attempt_required"])
        self.assertTrue(EVIDENCE["identity"]["steam_player_feedback_url_appid_must_match_exact_dossier_appid_when_exposed"])
        self.assertFalse(EVIDENCE["identity"]["base_game_feedback_may_satisfy_dlc_gate"])
        self.assertFalse(EVIDENCE["compact_provenance"]["author_identity_allowed"])
        self.assertFalse(EVIDENCE["compact_provenance"]["profile_scoped_urls_allowed"])
        self.assertTrue(EVIDENCE["language_binding"]["strict_exact_equality_required"])

    def test_cov_12_temporal_completeness_behavior_remains_intact(self):
        self.assertTrue(SCHEMA["observation_invariants"]["historical_requires_historical_and_recent_current_state_sources"])
        self.assertIn("## Temporal pre-stop completeness gate", PROMPT)
        self.assertIn("continue bounded exact-product recent player-feedback retrieval", PROMPT)

    def test_cov_13_no_new_scheduler_queue_retry_or_backlog_owner(self):
        owner = OWNERSHIP["taste_steam_review_dossier_nonblocking_progress"]
        self.assertEqual(owner["owner"], "github_control_plane")
        self.assertEqual(owner["scheduled_chatgpt_role"], "bounded_semantic_candidate_generation_and_create_only_transport_only")
        self.assertFalse(owner["new_queue_retry_loop_or_scheduler_created"])
        self.assertIn("second_dossier_scheduler", PERSISTENCE["forbidden"])
        self.assertIn("independent_dossier_queue", PERSISTENCE["forbidden"])

    def test_cov_14_buffered_traversal_persistence_and_recovery_ownership_unchanged(self):
        self.assertEqual(CONTROL["checkpointing"]["owner"], "github_control_plane")
        self.assertEqual(CONTROL["checkpointing"]["semantics"], "internal_durability_boundary_not_scope_quota")
        self.assertEqual(PERSISTENCE["buffered_transport"]["mode"], "immutable_create_only_one_file_per_predeclared_group")
        self.assertFalse(PERSISTENCE["buffered_transport"]["worker_overwrite_update_delete_allowed"])
        self.assertIn("own_failed_group_recovery_projection_and_recovery_eligibility", CONTROL["ownership"]["github_responsibilities"])

    def test_cov_15_completeness_over_speed_remains_semantically_bounded(self):
        bounded = EVIDENCE["adaptive_research"]["semantic_boundedness"]
        self.assertTrue(bounded["completeness_over_speed"])
        self.assertFalse(bounded["throughput_or_latency_is_semantic_stop_gate"])
        self.assertFalse(bounded["one_valid_observation_is_completion_gate"])
        self.assertTrue(bounded["materially_equivalent_route_retry_forbidden"])
        self.assertIn("ordinary_invocation_runtime_ended", bounded["safe_invocation_stop_conditions"])
        self.assertIn("This priority does not authorize unbounded crawling", PROMPT)


if __name__ == "__main__":
    unittest.main()
