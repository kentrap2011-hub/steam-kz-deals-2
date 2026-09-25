#!/usr/bin/env python3
"""PRAG-01..PRAG-15 regressions for pragmatic Dossier evidence semantics."""
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
EXECUTION = json.loads((ROOT / "config/execution_ownership_contract.json").read_text(encoding="utf-8"))
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")
STRICT_TEXT = (ROOT / "scripts/taste_steam_review_dossier_strict.py").read_text(encoding="utf-8")


def _refresh_summary(doc):
    doc["summary"] = derive_dossier_summary(doc["observations"], doc["conflicts"])
    return doc


def observed_russian_dossier(
    appid,
    now,
    *,
    title=None,
    release_year=2020,
    acquisition_mode="search_result_observation",
):
    """Replace the fixture's Russian stable child with a locatorless observed-feedback support record."""
    appid = str(appid)
    doc = web_dossier(
        appid,
        now,
        title=title,
        release_year=release_year,
        russian_status="found_and_used",
    )
    title = doc["title"]
    if acquisition_mode == "search_result_observation":
        source = {
            "source_id": "source-003",
            "source_type": "other_player_feedback",
            "domain": "steamstat.io",
            "url": f"https://steamstat.io/ru/app/{appid}",
            "publication_date": now.date().isoformat(),
            "language": "russian",
            "freshness": "recent",
            "evidence_role": "current_state",
            "player_feedback": True,
            "feedback_surface_mode": "search_result_representation",
            "acquisition_mode": "search_result_observation",
            "exact_product_binding": {
                "appid": appid,
                "title": title,
                "release_year": release_year,
                "binding_basis": "result_metadata",
            },
        }
    elif acquisition_mode == "inspected_collection_item":
        source = {
            "source_id": "source-003",
            "source_type": "steam_reviews",
            "domain": "store.steampowered.com",
            "url": f"https://store.steampowered.com/app/{appid}/?l=russian",
            "publication_date": now.date().isoformat(),
            "language": "russian",
            "freshness": "recent",
            "evidence_role": "current_state",
            "player_feedback": True,
            "feedback_surface_mode": "concrete_item_collection",
            "acquisition_mode": "inspected_collection_item",
            "exact_product_binding": {
                "appid": appid,
                "title": title,
                "release_year": release_year,
                "binding_basis": "url_appid",
            },
        }
    else:
        raise AssertionError(f"unsupported test acquisition mode: {acquisition_mode}")

    record = {
        "feedback_id": "observation-001",
        "source_id": "source-003",
        "publication_date": now.date().isoformat(),
        "language": "russian",
        "identity_mode": "source_observation",
    }
    doc["provenance"]["sources"][2] = source
    doc["provenance"]["player_feedback_records"][3] = record
    russian_observation = doc["observations"][1]
    russian_observation["source_ids"] = ["source-003"]
    russian_observation["player_feedback_ids"] = ["observation-001"]
    russian_observation["mention_count"] = 1
    russian_observation["evidence_languages"] = ["russian"]
    return _refresh_summary(doc)


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

    def test_prag_01_tiny_snow_search_result_russian_feedback_survives_missing_locator_and_direct_open_failure(self):
        doc = observed_russian_dossier(
            "1002560",
            self.now,
            title="Tiny Snow",
            release_year=2019,
            acquisition_mode="search_result_observation",
        )
        record = doc["provenance"]["player_feedback_records"][3]
        self.assertEqual(record["identity_mode"], "source_observation")
        self.assertNotIn("url", record)
        self.assertNotIn("public_ref", record)
        self.assertEqual(doc["evidence"]["russian_attempt"], "found_and_used")
        self.assertIs(self.validate(doc), doc)
        self.assertFalse(EVIDENCE["pragmatic_observed_feedback"]["target_page_open_required_for_search_result_evidence"])
        self.assertIn("later failure to open/read the target page does not erase that evidence", PROMPT)

    def test_prag_02_collection_card_without_stable_locator_or_author_is_usable(self):
        doc = observed_russian_dossier(
            "930002",
            self.now,
            acquisition_mode="inspected_collection_item",
        )
        record = doc["provenance"]["player_feedback_records"][3]
        self.assertEqual(record["identity_mode"], "source_observation")
        self.assertNotIn("url", record)
        self.assertNotIn("public_ref", record)
        self.assertNotIn("author", json.dumps(doc).lower())
        self.assertIs(self.validate(doc), doc)

    def test_prag_03_stable_item_locator_remains_preferred_and_valid(self):
        doc = web_dossier("930003", self.now)
        self.assertIs(self.validate(doc), doc)
        self.assertEqual(EVIDENCE["feedback_item_identity"]["preferred_identity_order"][0], "stable_locator")
        self.assertFalse(EVIDENCE["feedback_item_identity"]["stable_locator_required_for_evidence_usability"])

    def test_prag_04_aggregate_only_or_non_player_surface_cannot_become_feedback(self):
        doc = observed_russian_dossier("930004", self.now)
        source = doc["provenance"]["sources"][2]
        source["source_type"] = "professional_context"
        source["player_feedback"] = False
        source["acquisition_mode"] = "context_only"
        source.pop("feedback_surface_mode")
        source.pop("exact_product_binding")
        with self.assertRaisesRegex(ValueError, "source_id must resolve to a player-feedback source"):
            self.validate(doc)
        self.assertFalse(EVIDENCE["source_policy"]["aggregate_rating_or_count_alone_is_concrete_player_feedback"])

    def test_prag_05_query_text_alone_cannot_establish_exact_product_binding(self):
        doc = observed_russian_dossier("930005", self.now)
        doc["provenance"]["sources"][2]["exact_product_binding"]["binding_basis"] = "query_only"
        with self.assertRaisesRegex(ValueError, "binding_basis is invalid or query-only"):
            self.validate(doc)
        self.assertTrue(EVIDENCE["pragmatic_observed_feedback"]["query_only_binding_forbidden"])

    def test_prag_06_wrong_appid_release_or_product_variant_remains_fail_closed(self):
        cases = [
            ("appid", "999999", "appid does not match exact dossier appid"),
            ("title", "Game 930006 - DLC", "title does not match exact dossier title"),
            ("release_year", 2021, "release_year does not match exact dossier release"),
        ]
        for field, value, message in cases:
            with self.subTest(field=field):
                doc = observed_russian_dossier("930006", self.now, release_year=2020)
                doc["provenance"]["sources"][2]["exact_product_binding"][field] = value
                with self.assertRaisesRegex(ValueError, message):
                    self.validate(doc)

    def test_prag_07_raw_feedback_and_author_profile_identity_remain_forbidden(self):
        quoted = observed_russian_dossier("930007", self.now)
        quoted["quote"] = "verbatim player feedback must not persist"
        with self.assertRaisesRegex(ValueError, "body-like raw-text field"):
            self.validate(quoted)

        authored = observed_russian_dossier("930017", self.now)
        authored["author"] = "visible-reviewer"
        with self.assertRaisesRegex(ValueError, "forbidden author identity field"):
            self.validate(authored)

        profiled = observed_russian_dossier("930027", self.now)
        profiled["profile_url"] = "https://steamcommunity.com/id/visible-reviewer/"
        with self.assertRaisesRegex(ValueError, "forbidden author/profile URL"):
            self.validate(profiled)

    def test_prag_08_equivalent_locatorless_surfacing_cannot_inflate_support(self):
        doc = observed_russian_dossier("930008", self.now)
        duplicate = copy.deepcopy(doc["provenance"]["player_feedback_records"][3])
        duplicate["feedback_id"] = "observation-002"
        doc["provenance"]["player_feedback_records"].append(duplicate)
        obs = doc["observations"][1]
        obs["player_feedback_ids"] = ["observation-001", "observation-002"]
        obs["mention_count"] = 2
        with self.assertRaisesRegex(ValueError, "duplicate or aliased attributable player-feedback item"):
            self.validate(doc)

    def test_prag_09_no_hidden_stable_locator_count_controls_recurrence(self):
        doc = observed_russian_dossier("930009", self.now)
        obs = doc["observations"][1]
        obs["recurrence"] = "strong"
        obs["mention_count"] = 1
        doc["evidence"]["overall_strength"] = "strong"
        self.assertIs(self.validate(doc), doc)
        self.assertFalse(SCHEMA["observation_invariants"]["recurrence_numeric_record_threshold_required"])
        self.assertFalse(SCHEMA["observation_invariants"]["stable_locator_count_threshold_for_recurrence"])
        self.assertNotIn("stable_locator_moderate_minimum", STRICT_TEXT)
        self.assertNotIn("stable_locator_strong_minimum", STRICT_TEXT)

    def test_prag_10_russian_found_and_used_accepts_both_locatorless_observation_modes(self):
        for mode in ("search_result_observation", "inspected_collection_item"):
            with self.subTest(mode=mode):
                doc = observed_russian_dossier("930010", self.now, acquisition_mode=mode)
                self.assertEqual(doc["evidence"]["russian_attempt"], "found_and_used")
                self.assertIs(self.validate(doc), doc)

    def test_prag_11_unresolved_states_mean_content_unavailable_not_locator_missing(self):
        usable = observed_russian_dossier("930011", self.now)
        self.assertIs(self.validate(usable), usable)

        missing_content = web_dossier(
            "930111",
            self.now,
            russian_status="searched_no_existence_signal",
        )
        missing_content["evidence"]["russian_attempt"] = "existence_established_retrieval_unresolved"
        with self.assertRaisesRegex(ValueError, "usable concrete player-feedback content was not observed"):
            self.validate(missing_content)

        blocked_content = web_dossier(
            "930211",
            self.now,
            russian_status="searched_no_existence_signal",
        )
        blocked_content["evidence"]["russian_attempt"] = "existence_established_access_unresolved"
        with self.assertRaisesRegex(ValueError, "access prevents observing usable concrete player-feedback content"):
            self.validate(blocked_content)

    def test_prag_12_coverage_sufficiency_gate_remains_fail_closed(self):
        doc = observed_russian_dossier("930012", self.now)
        for dimension in doc["evidence"]["coverage"]["dimensions"]:
            if dimension["dimension"] == "core_play_mechanics":
                dimension["state"] = "materially_unresolved"
                dimension["observation_indices"] = []
                break
        with self.assertRaisesRegex(ValueError, "materially unresolved game-experience coverage"):
            self.validate(doc)

    def test_prag_13_temporal_current_state_guard_remains_fail_closed(self):
        doc = web_dossier("930013", self.now)
        doc["observations"][0]["evidence_status"] = "historical"
        doc["provenance"]["sources"][1]["evidence_role"] = "historical"
        _refresh_summary(doc)
        with self.assertRaisesRegex(ValueError, "historical/fixed claim lacks recent current-state check"):
            self.validate(doc)

    def test_prag_14_no_scheduler_queue_retry_crawler_or_author_registry_is_introduced(self):
        ownership = EXECUTION["taste_steam_review_dossier_nonblocking_progress"]
        self.assertEqual(ownership["owner"], "github_control_plane")
        self.assertFalse(ownership["new_queue_retry_loop_or_scheduler_created"])
        self.assertFalse(ownership["scheduled_worker_may_edit_own_schedule"])
        self.assertFalse(EVIDENCE["compact_provenance"]["author_identity_allowed"])
        self.assertFalse(EVIDENCE["compact_provenance"]["profile_scoped_urls_allowed"])
        self.assertFalse(EVIDENCE["pragmatic_observed_feedback"]["author_or_profile_identity_persistence_forbidden"] is False)

    def test_prag_15_buffered_group_validation_traversal_persistence_recovery_ownership_unchanged(self):
        self.assertEqual(CONTROL["checkpointing"]["checkpoint_size"], 3)
        self.assertEqual(CONTROL["checkpointing"]["owner"], "github_control_plane")
        self.assertEqual(CONTROL["buffered_submission"]["buffer"]["role"], "transport_only")
        self.assertFalse(CONTROL["buffered_submission"]["buffer"]["canonical_progress"])
        self.assertEqual(CONTROL["buffered_submission"]["drain"]["owner"], "github_control_plane")
        self.assertIn(
            "strict_validate_each_present_pending_group_independently",
            CONTROL["buffered_submission"]["drain"]["acceptance_rule"],
        )
        self.assertIn("manage_queue_or_retry_policy", CONTROL["ownership"]["forbidden"])


if __name__ == "__main__":
    unittest.main()
