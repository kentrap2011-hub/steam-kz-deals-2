import copy
import hashlib
import json
import re
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from taste_steam_review_dossier_buffered import validate_buffer_artifact
from taste_steam_review_dossier_daily import BUFFER_GROUP_SCHEMA, build_daily_work_manifest, load_contract
from taste_steam_review_dossier_prepublication import validate_prepublication_artifact
from taste_steam_review_dossier_strict import validate_dossier_strict
from taste_steam_review_dossier_test_fixture import web_dossier


ROOT = Path(__file__).resolve().parents[1]
CONTROL = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
SCHEMA = json.loads((ROOT / "config/taste_steam_review_dossier_schema.json").read_text(encoding="utf-8"))
EVIDENCE = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")


def queue(appids):
    rows = []
    for i, appid in enumerate(appids):
        appid = str(appid)
        rows.append({
            "taste_subject_key": f"App_{appid}_{i}",
            "appid": appid,
            "title": f"Game {appid}",
            "taste_fingerprint": hashlib.sha256(f"taste:{appid}:{i}".encode()).hexdigest(),
            "candidate_context_sha256": hashlib.sha256(f"ctx:{appid}:{i}".encode()).hexdigest(),
            "work_required": ["resolve_grounded_negative_analysis"],
        })
    return rows


def build_group(work, generated):
    descriptor = work["submission_group_plan"]["groups"][0]
    return {
        "schema": BUFFER_GROUP_SCHEMA,
        "schema_version": 1,
        **copy.deepcopy(descriptor),
        "dossiers": [
            web_dossier(item["appid"], generated, title=item["title"])
            for item in descriptor["items"]
        ],
    }


class IdentityProvenanceGenerationFixTests(unittest.TestCase):
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

    def test_id_prov_01_non_identity_only_identity_sources_remain_rejected(self):
        doc = web_dossier("910001", self.now)
        doc["game_identity"]["identity_source_ids"] = ["source-002"]
        self.assertEqual(doc["provenance"]["sources"][1]["evidence_role"], "durable_trait")
        with self.assertRaisesRegex(ValueError, "identity-role provenance source"):
            self.validate(doc)

    def test_id_prov_02_worker_contract_explicitly_requires_identity_role_source(self):
        rules = SCHEMA["identity_rules"]
        self.assertTrue(rules["identity_source_ids_require_at_least_one_identity_role_source"])
        self.assertTrue(rules["identity_role_source_must_resolve_to_exact_intended_product"])
        self.assertTrue(rules["identity_role_source_must_support_resolved_title_release_year_and_appid_under_current_rules"])
        self.assertTrue(rules["ordinary_player_feedback_source_must_not_masquerade_as_identity_provenance"])
        self.assertFalse(rules["identity_only_source_may_count_as_player_feedback_support"])
        self.assertIn(
            'Every resolved game identity must reference at least one provenance source with `evidence_role:"identity"`.',
            PROMPT,
        )
        self.assertIn("never relabel an ordinary player-feedback source as `identity` merely to satisfy validation", PROMPT)
        self.assertEqual(
            EVIDENCE["worker_prompt_revision"],
            "web-evidence-v2-validator-generator-parity-fix-v1",
        )

    def test_id_prov_03_valid_identity_source_passes_strict_prepublication_and_buffered_validation(self):
        doc = web_dossier("910003", self.now)
        self.assertEqual(doc["game_identity"]["identity_source_ids"], ["source-001"])
        self.assertEqual(doc["provenance"]["sources"][0]["evidence_role"], "identity")
        self.assertIs(self.validate(doc), doc)

        with tempfile.TemporaryDirectory() as td:
            work = build_daily_work_manifest(
                queue(["910031", "910032", "910033"]),
                CONTROL,
                Path(td) / "store",
                now=self.now,
            )
            descriptor = work["submission_group_plan"]["groups"][0]
            artifact = build_group(work, self.now)
            prepub = validate_prepublication_artifact(copy.deepcopy(artifact), work, CONTROL)
            buffered = validate_buffer_artifact(copy.deepcopy(artifact), descriptor, work, CONTROL)
            self.assertEqual(prepub["status"], "valid")
            self.assertEqual(len(buffered), 3)

    def test_id_prov_04_identity_only_metadata_cannot_be_used_as_feedback_support(self):
        doc = web_dossier("910004", self.now)
        identity_source = doc["provenance"]["sources"][0]
        self.assertEqual(identity_source["evidence_role"], "identity")
        self.assertFalse(identity_source["player_feedback"])
        self.assertTrue(all(r["source_id"] != "source-001" for r in doc["provenance"]["player_feedback_records"]))

        doc["provenance"]["player_feedback_records"][0]["source_id"] = "source-001"
        with self.assertRaisesRegex(ValueError, "must resolve to a player-feedback source"):
            self.validate(doc)

    def test_id_prov_05_title_appid_and_identity_source_stay_on_exact_product(self):
        appid = "910005"
        doc = web_dossier(appid, self.now)
        identity_source = doc["provenance"]["sources"][0]
        self.assertEqual(identity_source["url"], f"https://store.steampowered.com/app/{appid}/")
        self.assertEqual(doc["game_identity"]["work_title"], doc["title"])
        self.assertIn({"kind": "appid", "value": appid}, doc["game_identity"]["corroborators"])

        wrong_title = copy.deepcopy(doc)
        wrong_title["game_identity"]["work_title"] = "Different release"
        with self.assertRaisesRegex(ValueError, "work_title must exactly equal dossier title"):
            self.validate(wrong_title)

        wrong_appid = copy.deepcopy(doc)
        wrong_appid["game_identity"]["corroborators"] = [{"kind": "appid", "value": "999999"}]
        with self.assertRaisesRegex(ValueError, "exact work-item appid"):
            self.validate(wrong_appid)

    def test_id_prov_06_internal_ids_and_privacy_guards_remain_intact(self):
        doc = web_dossier("910006", self.now)
        self.assertEqual(
            [s["source_id"] for s in doc["provenance"]["sources"]],
            ["source-001", "source-002", "source-003"],
        )
        self.assertTrue(all(re.fullmatch(r"feedback-[0-9]{3}", r["feedback_id"]) for r in doc["provenance"]["player_feedback_records"]))

        leaked = copy.deepcopy(doc)
        leaked["provenance"]["sources"][0]["source_id"] = "profile-76561198000000000"
        leaked["game_identity"]["identity_source_ids"] = ["profile-76561198000000000"]
        with self.assertRaisesRegex(ValueError, "dossier-local source-NNN"):
            self.validate(leaked)

    def test_id_prov_07_existing_evidence_semantics_are_unchanged(self):
        self.assertEqual(EVIDENCE["contract_revision"], "validator-generator-parity-fix-2026-09-20")
        self.assertTrue(EVIDENCE["language_binding"]["strict_exact_equality_required"])
        self.assertEqual(EVIDENCE["transient_author_fallback"]["status"], "active")
        self.assertTrue(EVIDENCE["source_policy"]["steam_store_exact_app_review_collection_may_be_fallback_parent"])
        self.assertEqual(EVIDENCE["adaptive_research"]["hard_bounds_per_game"], {
            "max_web_search_queries": 8,
            "max_opened_or_read_source_pages": 16,
        })


if __name__ == "__main__":
    unittest.main()
