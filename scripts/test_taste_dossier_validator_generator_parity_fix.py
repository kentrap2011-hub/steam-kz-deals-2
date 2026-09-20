#!/usr/bin/env python3
import copy
import hashlib
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from taste_steam_review_dossier_daily import load_contract
from taste_steam_review_dossier_strict import validate_dossier_strict
from taste_steam_review_dossier_test_fixture import web_dossier
from test_taste_dossier_transient_author_fallback import fallback_dossier


ROOT = Path(__file__).resolve().parents[1]
CONTROL = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
SCHEMA = json.loads((ROOT / "config/taste_steam_review_dossier_schema.json").read_text(encoding="utf-8"))
EVIDENCE = json.loads((ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json").read_text(encoding="utf-8"))
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")
STRICT_PATH = ROOT / "scripts/taste_steam_review_dossier_strict.py"
PRE_FIX_STRICT_GIT_BLOB_SHA = "81126b87db7542512221a82f1ece4b846abe1af7"


def normalize_domain(value):
    text = str(value or "").strip().lower().rstrip(".")
    if text.startswith("www."):
        text = text[4:]
    return text


def generator_source_contract_accepts(source):
    inv = SCHEMA["provenance_source_invariants"]
    if inv["locator_cardinality"] != "exactly_one":
        return False
    url = source.get("url")
    public_ref = source.get("public_ref")
    if bool(url) == bool(public_ref):
        return False
    if url:
        parsed = urlparse(str(url))
        if parsed.scheme != "https" or not parsed.netloc:
            return False
        if normalize_domain(parsed.hostname) != normalize_domain(source.get("domain")):
            return False
    elif not isinstance(public_ref, str) or not 3 <= len(public_ref) <= 500:
        return False

    if (
        url
        and normalize_domain(urlparse(url).hostname) == "store.steampowered.com"
        and urlparse(url).path.startswith("/app/")
        and source.get("player_feedback") is True
        and source.get("feedback_surface_mode") == "concrete_item_collection"
    ):
        allowed = set(inv["steam_store_exact_app_fallback_parent_allowed_source_types"])
        if source.get("source_type") not in allowed:
            return False
    return True


def generator_evidence_contract_accepts(evidence, *, distinct_used_player_sources):
    inv = SCHEMA["evidence_invariants"]
    if evidence.get("source_mix_status") == "multi_source":
        return (
            distinct_used_player_sources >= 2
            and inv["multi_source_requires_single_source_reason_null"]
            and evidence.get("single_source_reason") is None
        )
    if evidence.get("source_mix_status") == "single_source_only":
        reason = evidence.get("single_source_reason")
        return (
            distinct_used_player_sources == 1
            and inv["single_source_only_requires_reason"]
            and isinstance(reason, str)
            and bool(reason.strip())
            and len(reason) <= 500
        )
    return False


def git_blob_sha(path):
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


class ValidatorGeneratorParityFixTests(unittest.TestCase):
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

    def test_parity_fix_01_locator_cardinality(self):
        valid = web_dossier("920001", self.now)
        source = valid["provenance"]["sources"][0]
        self.assertTrue(generator_source_contract_accepts(source))
        self.assertIs(self.validate(valid), valid)

        both = copy.deepcopy(valid)
        both_source = both["provenance"]["sources"][0]
        both_source["public_ref"] = "steam-app:920001"
        self.assertFalse(generator_source_contract_accepts(both_source))
        with self.assertRaisesRegex(ValueError, "exactly one of url or public_ref"):
            self.validate(both)

        neither = copy.deepcopy(valid)
        neither_source = neither["provenance"]["sources"][0]
        neither_source.pop("url")
        self.assertFalse(generator_source_contract_accepts(neither_source))
        with self.assertRaisesRegex(ValueError, "exactly one of url or public_ref"):
            self.validate(neither)

        source_schema = SCHEMA["json_schema"]["properties"]["provenance"]["properties"]["sources"]["items"]
        self.assertEqual(len(source_schema["oneOf"]), 2)

    def test_parity_fix_02_https_requirement(self):
        valid = web_dossier("920002", self.now)
        self.assertTrue(generator_source_contract_accepts(valid["provenance"]["sources"][0]))

        http_doc = copy.deepcopy(valid)
        source = http_doc["provenance"]["sources"][0]
        source["url"] = source["url"].replace("https://", "http://", 1)
        self.assertFalse(generator_source_contract_accepts(source))
        with self.assertRaisesRegex(ValueError, "HTTPS public URL"):
            self.validate(http_doc)

        self.assertTrue(SCHEMA["provenance_source_invariants"]["url_requires_public_https"])
        self.assertTrue(EVIDENCE["source_policy"]["provenance_source_locator"]["url_requires_public_https"])

    def test_parity_fix_03_exact_normalized_host_equality(self):
        valid = web_dossier("920003", self.now)
        self.assertTrue(generator_source_contract_accepts(valid["provenance"]["sources"][0]))

        mismatch = copy.deepcopy(valid)
        mismatch["provenance"]["sources"][0]["domain"] = "steampowered.com"
        self.assertFalse(generator_source_contract_accepts(mismatch["provenance"]["sources"][0]))
        with self.assertRaisesRegex(ValueError, "domain must match URL host"):
            self.validate(mismatch)

        normalized = copy.deepcopy(valid)
        normalized["provenance"]["sources"][0]["domain"] = "WWW.STORE.STEAMPOWERED.COM."
        self.assertTrue(generator_source_contract_accepts(normalized["provenance"]["sources"][0]))
        self.assertIs(self.validate(normalized), normalized)
        self.assertTrue(SCHEMA["provenance_source_invariants"]["url_domain_must_equal_normalized_hostname_exactly"])

    def test_parity_fix_04_multi_source_reason_must_be_null(self):
        valid = web_dossier("920004", self.now)
        self.assertTrue(generator_evidence_contract_accepts(valid["evidence"], distinct_used_player_sources=2))
        self.assertIs(self.validate(valid), valid)

        invalid = copy.deepcopy(valid)
        invalid["evidence"]["single_source_reason"] = "Two independent sources were used."
        self.assertFalse(generator_evidence_contract_accepts(invalid["evidence"], distinct_used_player_sources=2))
        with self.assertRaisesRegex(ValueError, "multi_source evidence must not carry a single-source reason"):
            self.validate(invalid)

        self.assertTrue(EVIDENCE["source_mix_policy"]["multi_source_requires_single_source_reason_null"])

    def test_parity_fix_05_single_source_semantics_preserved(self):
        valid = fallback_dossier("920005", self.now)
        self.assertTrue(generator_evidence_contract_accepts(valid["evidence"], distinct_used_player_sources=1))
        self.assertIs(self.validate(valid), valid)

        invalid = copy.deepcopy(valid)
        invalid["evidence"]["single_source_reason"] = None
        self.assertFalse(generator_evidence_contract_accepts(invalid["evidence"], distinct_used_player_sources=1))
        with self.assertRaisesRegex(ValueError, "single_source_only evidence requires a compact reason"):
            self.validate(invalid)

    def test_parity_fix_06_steam_store_allowed_types(self):
        allowed = SCHEMA["provenance_source_invariants"]["steam_store_exact_app_fallback_parent_allowed_source_types"]
        self.assertEqual(allowed, ["steam_reviews", "store_user_reviews"])
        self.assertEqual(EVIDENCE["source_policy"]["steam_store_exact_app_fallback_parent_allowed_source_types"], allowed)

        steam_reviews = fallback_dossier("920006", self.now)
        self.assertTrue(generator_source_contract_accepts(steam_reviews["provenance"]["sources"][1]))
        self.assertIs(self.validate(steam_reviews), steam_reviews)

        store_reviews = fallback_dossier("920016", self.now)
        store_reviews["provenance"]["sources"][1]["source_type"] = "store_user_reviews"
        self.assertTrue(generator_source_contract_accepts(store_reviews["provenance"]["sources"][1]))
        self.assertIs(self.validate(store_reviews), store_reviews)

    def test_parity_fix_07_steam_store_disallowed_type(self):
        invalid = fallback_dossier("920007", self.now)
        parent = invalid["provenance"]["sources"][1]
        parent["source_type"] = "other_player_feedback"
        self.assertFalse(generator_source_contract_accepts(parent))
        with self.assertRaisesRegex(ValueError, "Steam Store concrete-item fallback parent must use a review-surface source type"):
            self.validate(invalid)
        self.assertTrue(SCHEMA["provenance_source_invariants"]["steam_store_exact_app_fallback_parent_source_type_set_is_exclusive"])
        self.assertTrue(EVIDENCE["source_policy"]["steam_store_exact_app_fallback_parent_source_type_set_is_exclusive"])

    def test_parity_fix_08_strict_validator_file_is_unchanged(self):
        self.assertEqual(git_blob_sha(STRICT_PATH), PRE_FIX_STRICT_GIT_BLOB_SHA)

    def test_parity_fix_09_identity_provenance_remains_aligned(self):
        doc = web_dossier("920009", self.now)
        self.assertEqual(doc["game_identity"]["identity_source_ids"], ["source-001"])
        self.assertEqual(doc["provenance"]["sources"][0]["evidence_role"], "identity")
        self.assertTrue(SCHEMA["identity_rules"]["identity_source_ids_require_at_least_one_identity_role_source"])
        self.assertIn(
            'Every resolved game identity must reference at least one provenance source with `evidence_role:"identity"`.',
            PROMPT,
        )
        self.assertIs(self.validate(doc), doc)

    def test_generator_facing_prompt_and_json_schema_are_explicit(self):
        self.assertIn("**exactly one** locator (`url` or stable `public_ref`, never both and never neither)", PROMPT)
        self.assertIn('persist `source_mix_status:"multi_source"` and **always** set `single_source_reason:null`', PROMPT)
        self.assertIn('source_type` is **exclusively** one of `steam_reviews` or `store_user_reviews`', PROMPT)
        self.assertNotIn('normally `source_type:"steam_reviews"` or `store_user_reviews`', PROMPT)

        evidence_schema = SCHEMA["json_schema"]["properties"]["evidence"]
        self.assertEqual(evidence_schema["allOf"][0]["then"]["properties"]["single_source_reason"]["const"], None)
        source_schema = SCHEMA["json_schema"]["properties"]["provenance"]["properties"]["sources"]["items"]
        store_type_enum = source_schema["allOf"][0]["then"]["properties"]["source_type"]["enum"]
        self.assertEqual(store_type_enum, ["steam_reviews", "store_user_reviews"])


if __name__ == "__main__":
    unittest.main()
