#!/usr/bin/env python3
"""PRAG-01..PRAG-15 regressions for pragmatic exact-product observed evidence."""
import copy
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_strict import derive_dossier_summary, validate_dossier_strict
from taste_steam_review_dossier_test_fixture import web_dossier


ROOT = Path(__file__).resolve().parents[1]
CONTROL = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
SCHEMA = json.loads((ROOT / "config/taste_steam_review_dossier_schema.json").read_text(encoding="utf-8"))
EVIDENCE = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
OWNERSHIP = json.loads((ROOT / "config/execution_ownership_contract.json").read_text(encoding="utf-8"))
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")


def search_result_dossier(appid, now, *, title=None, release_year=2020, language="russian"):
    appid = str(appid)
    title = title or f"Game {appid}"
    base = web_dossier(
        appid,
        now,
        title=title,
        release_year=release_year,
        russian_status="searched_no_existence_signal",
    )
    identity = copy.deepcopy(base["provenance"]["sources"][0])
    source = {
        "source_id": "source-002",
        "source_type": "steam_reviews",
        "domain": "steamcommunity.com",
        "url": f"https://steamcommunity.com/app/{appid}/reviews/",
        "publication_date": None,
        "language": language,
        "freshness": "unknown",
        "evidence_role": "durable_trait",
        "player_feedback": True,
        "feedback_surface_mode": "search_result_representation",
        "exact_product_binding": {
            "basis": "source_appid",
            "appid": appid,
            "title": None,
            "release_year": None,
        },
    }
    record = {
        "feedback_id": "feedback-001",
        "source_id": "source-002",
        "publication_date": None,
        "language": language,
        "acquisition_mode": "search_result_observation",
    }
    observation = {
        "category": "mechanics",
        "statement": "Observed player feedback describes a central gameplay characteristic without storing source text.",
        "sentiment": "mixed",
        "recurrence": "anecdotal",
        "mention_count": 1,
        "evidence_languages": ["russian"] if language == "russian" else ["non_russian"],
        "evidence_status": "durable",
        "source_ids": ["source-002"],
        "player_feedback_ids": ["feedback-001"],
    }
    coverage = []
    covered = {"core_play_mechanics", "recurring_strengths", "recurring_complaints_tradeoffs"}
    for dimension in EVIDENCE["coverage_sufficiency"]["dimensions"]:
        coverage.append({
            "dimension": dimension,
            "state": "covered" if dimension in covered else "not_material_or_not_applicable",
            "observation_indices": [0] if dimension in covered else [],
        })
    base["observations"] = [observation]
    base["conflicts"] = []
    base["summary"] = derive_dossier_summary(base["observations"], base["conflicts"])
    base["evidence"] = {
        "strategy": "adaptive_multi_source_web",
        "research_state": "sufficient",
        "source_mix_status": "single_source_only",
        "single_source_reason": "One exact-product observed-feedback source directly characterizes the compact central experience fixture.",
        "russian_attempt": "found_and_used" if language in {"russian", "mixed"} else "searched_no_existence_signal",
        "overall_strength": "limited",
        "stop_reason": "evidence_stable",
        "coverage": {
            "dimensions": coverage,
            "closure_basis": "compact_central_experience",
            "strengths_investigated": True,
            "weaknesses_tradeoffs_investigated": True,
        },
    }
    base["provenance"] = {"sources": [identity, source], "player_feedback_records": [record]}
    return base


class PragmaticEvidenceModelRegressionTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime.now(timezone.utc).replace(microsecond=0)

    def validate(self, doc):
        return validate_dossier_strict(
            doc,
            CONTROL,
            expected_appid=doc["appid"],
            expected_title=doc["title"],
            expected_ttl_days=20,
            now=self.now,
        )

    def test_prag_01_tiny_snow_search_result_russian_survives_missing_locator_and_436(self):
        doc = search_result_dossier("1002560", self.now, title="Tiny Snow", release_year=2019)
        observed_target_open = {"status": 436, "body_used": False}
        record = doc["provenance"]["player_feedback_records"][0]
        self.assertEqual(observed_target_open["status"], 436)
        self.assertNotIn("url", record)
        self.assertNotIn("public_ref", record)
        self.assertEqual(record["acquisition_mode"], "search_result_observation")
        self.assertEqual(doc["evidence"]["russian_attempt"], "found_and_used")
        self.assertIs(self.validate(doc), doc)
        self.assertIn("Tiny Snow", PROMPT)
        self.assertIn("1002560", PROMPT)
        self.assertIn("HTTP 436", PROMPT)
        self.assertFalse(EVIDENCE["source_policy"]["target_page_open_success_required_after_usable_search_result_observation"])

    def test_prag_02_exact_product_collection_card_needs_no_locator_or_author(self):
        doc = search_result_dossier("1002561", self.now)
        source = doc["provenance"]["sources"][1]
        source["feedback_surface_mode"] = "concrete_item_collection"
        record = doc["provenance"]["player_feedback_records"][0]
        record["acquisition_mode"] = "inspected_collection_item"
        self.assertNotIn("url", record)
        self.assertNotIn("public_ref", record)
        self.assertIs(self.validate(doc), doc)

    def test_prag_03_stable_item_still_works_and_is_preferred_auditability(self):
        doc = web_dossier("1002562", self.now)
        self.assertTrue(all(r["acquisition_mode"] == "stable_item" for r in doc["provenance"]["player_feedback_records"]))
        self.assertEqual(EVIDENCE["feedback_item_identity"]["preferred_auditability_order"][0], "stable_item")
        self.assertIs(self.validate(doc), doc)

    def test_prag_04_aggregate_only_russian_activity_is_not_player_feedback(self):
        doc = search_result_dossier("1002563", self.now)
        doc["provenance"]["player_feedback_records"] = []
        with self.assertRaisesRegex(ValueError, "player_feedback_records must be a non-empty list"):
            self.validate(doc)
        self.assertFalse(EVIDENCE["russian_evidence"]["aggregate_activity_alone_may_satisfy_found_and_used"])

    def test_prag_05_query_text_alone_cannot_bind_result_to_product(self):
        doc = search_result_dossier("1002564", self.now)
        doc["provenance"]["sources"][1].pop("exact_product_binding")
        with self.assertRaisesRegex(ValueError, "exact_product_binding is required"):
            self.validate(doc)
        self.assertFalse(EVIDENCE["exact_product_observation_binding"]["query_text_is_binding_evidence"])

    def test_prag_06_wrong_product_release_and_generic_result_fail_closed(self):
        cases = []

        wrong_appid = search_result_dossier("1002565", self.now)
        wrong_appid["provenance"]["sources"][1]["exact_product_binding"]["appid"] = "999999"
        cases.append(("wrong_appid", wrong_appid))

        wrong_dlc = search_result_dossier("2378500", self.now, title="Baldur's Gate 3 - Digital Deluxe Edition DLC")
        source = wrong_dlc["provenance"]["sources"][1]
        source["url"] = "https://steamcommunity.com/app/1086940/reviews/"
        source["exact_product_binding"]["appid"] = "1086940"
        cases.append(("base_for_dlc", wrong_dlc))

        wrong_release = search_result_dossier("1002566", self.now, title="Tiny Snow Remastered", release_year=2026)
        source = wrong_release["provenance"]["sources"][1]
        source.update({"domain": "example.org", "url": "https://example.org/reviews/tiny-snow-remastered"})
        source["exact_product_binding"] = {
            "basis": "source_title_release",
            "appid": None,
            "title": "Tiny Snow Remastered",
            "release_year": 2019,
        }
        cases.append(("old_for_remaster", wrong_release))

        sequel = search_result_dossier("1002567", self.now, title="Example Game", release_year=2020)
        source = sequel["provenance"]["sources"][1]
        source.update({"domain": "example.org", "url": "https://example.org/reviews/example-game-2"})
        source["exact_product_binding"] = {
            "basis": "source_title_release",
            "appid": None,
            "title": "Example Game 2",
            "release_year": 2020,
        }
        cases.append(("sequel", sequel))

        similar = search_result_dossier("1002568", self.now, title="Tiny Snow", release_year=2019)
        source = similar["provenance"]["sources"][1]
        source.update({"domain": "example.org", "url": "https://example.org/reviews/tiny-snowfall"})
        source["exact_product_binding"] = {
            "basis": "source_title_release",
            "appid": None,
            "title": "Tiny Snowfall",
            "release_year": 2019,
        }
        cases.append(("similar_name", similar))

        generic = search_result_dossier("1002569", self.now)
        source = generic["provenance"]["sources"][1]
        source.update({"domain": "example.org", "url": "https://example.org/reviews/"})
        source.pop("exact_product_binding")
        cases.append(("generic_domain", generic))

        for label, doc in cases:
            with self.subTest(label=label), self.assertRaisesRegex(ValueError, "exact_product_binding|appid does not match exact dossier appid"):
                self.validate(doc)

    def test_prag_07_raw_quote_snippet_author_and_profile_identity_do_not_persist(self):
        for field, value in (("snippet", "raw visible review text"), ("author", "player-name")):
            doc = search_result_dossier("1002570", self.now)
            doc["provenance"]["player_feedback_records"][0][field] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "unsupported fields|raw|author"):
                self.validate(doc)

        profile = search_result_dossier("1002571", self.now)
        source = profile["provenance"]["sources"][1]
        source["domain"] = "steamcommunity.com"
        source["url"] = "https://steamcommunity.com/id/private-player/recommended/1002571/"
        with self.assertRaisesRegex(ValueError, "author/profile"):
            self.validate(profile)

    def test_prag_08_duplicate_equivalent_stable_surfacing_cannot_inflate_support(self):
        doc = web_dossier("1002572", self.now)
        original = doc["provenance"]["player_feedback_records"][3]
        doc["provenance"]["player_feedback_records"].append({
            "feedback_id": "feedback-005",
            "source_id": original["source_id"],
            "url": original["url"] + "?utm_source=duplicate#same",
            "publication_date": original["publication_date"],
            "language": original["language"],
            "acquisition_mode": "stable_item",
        })
        with self.assertRaisesRegex(ValueError, "duplicate or aliased attributable player-feedback item"):
            self.validate(doc)
        self.assertIn("obvious equivalent resurfacing", EVIDENCE["feedback_item_identity"]["duplicate_alias_rule"])

    def test_prag_09_no_hidden_minimum_stable_locator_count(self):
        doc = search_result_dossier("1002573", self.now)
        doc["provenance"]["player_feedback_records"].append({
            "feedback_id": "feedback-002",
            "source_id": "source-002",
            "publication_date": None,
            "language": "russian",
            "acquisition_mode": "search_result_observation",
        })
        obs = doc["observations"][0]
        obs["player_feedback_ids"] = ["feedback-001", "feedback-002"]
        obs["mention_count"] = 2
        obs["recurrence"] = "moderate"
        doc["evidence"]["overall_strength"] = "moderate"
        self.assertFalse(any("url" in r or "public_ref" in r for r in doc["provenance"]["player_feedback_records"]))
        self.assertFalse(EVIDENCE["mention_binding"]["recurrence_identity_strength"]["stable_locator_thresholds_active"])
        self.assertFalse(SCHEMA["observation_invariants"]["recurrence_identity_strength"]["fixed_numeric_thresholds_above_single_item_active"])
        self.assertIs(self.validate(doc), doc)

    def test_prag_10_russian_found_and_used_accepts_search_and_collection_modes(self):
        for mode, surface in (
            ("search_result_observation", "search_result_representation"),
            ("inspected_collection_item", "concrete_item_collection"),
        ):
            doc = search_result_dossier("1002574", self.now)
            doc["provenance"]["sources"][1]["feedback_surface_mode"] = surface
            doc["provenance"]["player_feedback_records"][0]["acquisition_mode"] = mode
            with self.subTest(mode=mode):
                self.assertEqual(doc["evidence"]["russian_attempt"], "found_and_used")
                self.assertIs(self.validate(doc), doc)

    def test_prag_11_unresolved_is_content_unavailable_not_locator_unavailable(self):
        usable = search_result_dossier("1002575", self.now)
        usable["evidence"]["russian_attempt"] = "existence_established_retrieval_unresolved"
        with self.assertRaisesRegex(ValueError, "cannot coexist with used concrete Russian feedback"):
            self.validate(usable)

        no_russian = web_dossier("1002576", self.now, russian_status="searched_no_existence_signal")
        no_russian["evidence"]["russian_attempt"] = "existence_established_retrieval_unresolved"
        with self.assertRaisesRegex(ValueError, "usable concrete player-feedback content was not observed"):
            self.validate(no_russian)

        self.assertFalse(EVIDENCE["russian_evidence"]["missing_item_locator_may_force_unresolved"])
        self.assertFalse(EVIDENCE["russian_evidence"]["target_open_failure_after_usable_result_observation_may_force_unresolved"])

    def test_prag_12_taste_015_coverage_still_rejects_narrow_dossier(self):
        doc = search_result_dossier("1002577", self.now)
        for item in doc["evidence"]["coverage"]["dimensions"]:
            if item["dimension"] == "core_play_mechanics":
                item["state"] = "materially_unresolved"
                item["observation_indices"] = []
        with self.assertRaisesRegex(ValueError, "materially unresolved game-experience coverage"):
            self.validate(doc)
        self.assertTrue(EVIDENCE["coverage_sufficiency"]["materially_unresolved_forbids_persisted_sufficient_or_evidence_stable"])

    def test_prag_13_taste_012_temporal_checks_remain_intact(self):
        doc = web_dossier("1002578", self.now)
        doc["observations"][0]["evidence_status"] = "historical"
        doc["provenance"]["sources"][1]["evidence_role"] = "historical"
        with self.assertRaisesRegex(ValueError, "historical/fixed claim lacks recent current-state check"):
            self.validate(doc)

    def test_prag_14_no_scheduler_queue_retry_crawler_or_author_registry_added(self):
        ownership = OWNERSHIP["taste_steam_review_dossier_nonblocking_progress"]
        self.assertEqual(ownership["owner"], "github_control_plane")
        self.assertEqual(ownership["scheduled_chatgpt_role"], "bounded_semantic_candidate_generation_and_create_only_transport_only")
        self.assertFalse(ownership["new_queue_retry_loop_or_scheduler_created"])
        self.assertFalse(ownership["scheduled_worker_may_edit_own_schedule"])
        self.assertFalse(EVIDENCE["transient_author_fallback"]["persistent_author_registry_allowed"])
        bounds = EVIDENCE["adaptive_research"]["hard_bounds_per_game"]
        self.assertFalse(bounds["numeric_limits_active"])
        self.assertFalse(bounds["counts_are_semantic_stop_gates"])

    def test_prag_15_buffered_validation_and_github_persistence_recovery_ownership_unchanged(self):
        self.assertEqual(CONTROL["ownership"]["control_plane"], "github")
        self.assertEqual(int(CONTROL["checkpointing"]["checkpoint_size"]), 3)
        self.assertTrue(CONTROL["buffered_submission"]["buffer"]["multiple_pending_groups_same_snapshot_allowed"])
        self.assertEqual(
            CONTROL["buffered_submission"]["drain"]["acceptance_rule"],
            "strict_validate_each_present_pending_group_independently;persist_valid_groups_and_classify_invalid_groups_failed_or_invalid_pending_recovery",
        )
        self.assertEqual(
            OWNERSHIP["taste_steam_review_dossier_nonblocking_progress"]["github_owns"],
            [
                "immutable_group_plan",
                "per_group_pending_accepted_failed_state",
                "strict_validation",
                "canonical_dossier_persistence",
                "failed_group_quarantine_and_recovery_eligibility",
                "next_pending_projection",
                "normal_first_pass_completeness",
                "all_groups_accepted_completeness",
            ],
        )


if __name__ == "__main__":
    unittest.main()
