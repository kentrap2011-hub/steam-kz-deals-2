#!/usr/bin/env python3
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")
RUNTIME = (ROOT / "config/taste_steam_review_dossier_runtime_prompt.md").read_text(encoding="utf-8")
REGULATION = (ROOT / "config/taste_steam_review_dossier_scheduled_task_regulation.md").read_text(encoding="utf-8")
EVIDENCE = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
SCHEMA = json.loads((ROOT / "config/taste_steam_review_dossier_schema.json").read_text(encoding="utf-8"))
CONTROL = json.loads((ROOT / "config/taste_steam_review_dossier_contract.json").read_text(encoding="utf-8"))
PERSISTENCE = json.loads((ROOT / "config/taste_steam_review_dossier_persistence_bridge.json").read_text(encoding="utf-8"))
OWNERSHIP = json.loads((ROOT / "config/execution_ownership_contract.json").read_text(encoding="utf-8"))


class SemanticBoundedRetrievalRegressionTests(unittest.TestCase):
    @staticmethod
    def _count_only_stop(searches, pages):
        bounds = EVIDENCE["adaptive_research"]["hard_bounds_per_game"]
        if not bounds["counts_are_semantic_stop_gates"]:
            return False
        search_limit = bounds["max_web_search_queries"]
        page_limit = bounds["max_opened_or_read_source_pages"]
        return (
            (search_limit is not None and searches >= search_limit)
            or (page_limit is not None and pages >= page_limit)
        )

    def test_sembound_01_no_active_eight_search_ceiling(self):
        bounds = EVIDENCE["adaptive_research"]["hard_bounds_per_game"]
        self.assertIsNone(bounds["max_web_search_queries"])
        self.assertFalse(bounds["numeric_limits_active"])
        self.assertFalse(bounds["counts_are_semantic_stop_gates"])
        old_phrase = "at most **" + "8 web-search queries" + "**"
        self.assertNotIn(old_phrase, PROMPT)
        active_text = "\n".join((PROMPT, RUNTIME, REGULATION))
        self.assertNotIn("8-search / " + "16-page ceilings", active_text)

    def test_sembound_02_no_active_sixteen_page_ceiling(self):
        bounds = EVIDENCE["adaptive_research"]["hard_bounds_per_game"]
        self.assertIsNone(bounds["max_opened_or_read_source_pages"])
        old_phrase = "at most **" + "16 opened/read source pages" + "**"
        self.assertNotIn(old_phrase, PROMPT)
        self.assertIn("there is no finite numeric per-game limit to fabricate", PROMPT)

    def test_sembound_03_search_ordinal_above_eight_is_not_a_stop_gate(self):
        self.assertFalse(self._count_only_stop(9, 2))
        self.assertFalse(self._count_only_stop(11, 2))
        self.assertFalse(EVIDENCE["adaptive_research"]["semantic_boundedness"]["numeric_query_or_page_count_is_stop_gate"])

    def test_sembound_04_page_ordinal_above_sixteen_is_not_a_stop_gate(self):
        self.assertFalse(self._count_only_stop(2, 17))
        self.assertFalse(self._count_only_stop(11, 17))

    def test_sembound_05_evidence_sufficient_still_stops_early(self):
        self.assertIn("evidence_is_sufficient", EVIDENCE["adaptive_research"]["stop_when"])
        self.assertIn("evidence_stable", EVIDENCE["adaptive_research"]["accepted_stop_reasons"])
        self.assertIn("Stop immediately when evidence is sufficient.", PROMPT)

    def test_sembound_06_equivalent_route_repetition_remains_forbidden(self):
        semantic = EVIDENCE["adaptive_research"]["semantic_boundedness"]
        self.assertTrue(semantic["materially_equivalent_route_retry_forbidden"])
        self.assertTrue(semantic["route_revisit_requires_material_new_factual_lead"])
        self.assertIn("A materially equivalent query wording, locale, endpoint variant", PROMPT)
        self.assertIn("A route may be revisited only when a materially new factual lead changes what is being queried", PROMPT)

    def test_sembound_07_required_distinct_routes_execute_while_discoverable_and_safe(self):
        diversification = EVIDENCE["adaptive_research"]["russian_discovery"]["retrieval_diversification"]
        self.assertFalse(diversification["premature_unresolved_allowed_with_reasonably_discoverable_distinct_surface"])
        self.assertIn(
            "If a mandatory next material route is still `pending`, remains reasonably discoverable/materially distinct",
            PROMPT,
        )
        self.assertIn("Execute that required route first.", PROMPT)
        self.assertFalse(diversification["visit_all_surface_classes_required"])
        self.assertFalse(diversification["fixed_named_website_quota"])

    def test_sembound_08_exhausted_distinct_routes_with_insufficient_evidence_fail_closed(self):
        semantic = EVIDENCE["adaptive_research"]["semantic_boundedness"]
        self.assertIn("all_reasonably_discoverable_mandatory_materially_distinct_routes_are_exhausted", semantic["fail_closed_rule"])
        self.assertEqual(EVIDENCE["adaptive_research"]["critical_insufficiency_behavior"], "fail_closed_no_dossier")
        self.assertIn("fail closed and publish nothing", PROMPT)

    def test_sembound_09_ledger_counts_are_diagnostic_not_budget_exhaustion(self):
        self.assertIn("`search_query_limit:null`", PROMPT)
        self.assertIn("`opened_page_limit:null`", PROMPT)
        self.assertIn("These counters are observability only and must never by themselves justify", PROMPT)
        self.assertNotIn("search budget exhausted", PROMPT)
        self.assertNotIn("page/open budget exhausted", PROMPT)
        self.assertIn("Numeric search-query/page counts are never a valid reason by themselves.", PROMPT)

    def test_sembound_10_no_scheduler_queue_retry_checkpoint_or_persistence_owner_added(self):
        dossier_owner = OWNERSHIP["taste_steam_review_dossier_nonblocking_progress"]
        self.assertEqual(dossier_owner["owner"], "github_control_plane")
        self.assertEqual(
            dossier_owner["scheduled_chatgpt_role"],
            "bounded_semantic_candidate_generation_and_create_only_transport_only",
        )
        self.assertFalse(dossier_owner["new_queue_retry_loop_or_scheduler_created"])
        self.assertIn("second_dossier_scheduler", PERSISTENCE["forbidden"])
        self.assertIn("independent_dossier_queue", PERSISTENCE["forbidden"])
        self.assertEqual(PERSISTENCE["buffered_transport"]["mode"], "immutable_create_only_one_file_per_predeclared_group")

    def test_sembound_11_existing_v2_identity_privacy_russian_and_transport_guards_remain(self):
        self.assertEqual(SCHEMA["schema"], "TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2")
        self.assertEqual(SCHEMA["version"], 2)
        self.assertTrue(EVIDENCE["identity"]["steam_player_feedback_url_appid_must_match_exact_dossier_appid_when_exposed"])
        self.assertFalse(EVIDENCE["identity"]["base_game_feedback_may_satisfy_dlc_gate"])
        self.assertFalse(EVIDENCE["compact_provenance"]["author_identity_allowed"])
        self.assertFalse(EVIDENCE["compact_provenance"]["profile_scoped_urls_allowed"])
        self.assertTrue(EVIDENCE["russian_evidence"]["attempt_required"])
        self.assertEqual(CONTROL["ownership"]["control_plane"], "github")
        self.assertEqual(PERSISTENCE["buffered_transport"]["action"], "github_contents_create_file")
        self.assertFalse(PERSISTENCE["buffered_transport"]["worker_overwrite_update_delete_allowed"])
        self.assertEqual(EVIDENCE["worker_prompt_revision"], "web-evidence-v2-semantic-bounded-retrieval-v1")
        self.assertEqual(EVIDENCE["contract_revision"], "semantic-bounded-retrieval-2026-09-23")


if __name__ == "__main__":
    unittest.main()
