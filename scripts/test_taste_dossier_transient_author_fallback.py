#!/usr/bin/env python3
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
PROMPT = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")


def fallback_dossier(appid, now, *, title=None, transient_author_tokens=("ephemeral-a",)):
    """Model worker-memory dedupe, then return only the privacy-safe serialized dossier."""
    appid = str(appid)
    doc = web_dossier(appid, now, title=title, russian_status="searched_no_existence_signal")
    metadata = copy.deepcopy(doc["provenance"]["sources"][0])

    seen = set()
    unique_item_count = 0
    for token in transient_author_tokens:
        if token in seen:
            continue
        seen.add(token)
        unique_item_count += 1

    collection = {
        "source_id": "source-002",
        "source_type": "steam_reviews",
        "domain": "store.steampowered.com",
        "url": f"https://store.steampowered.com/app/{appid}/?l=russian",
        "publication_date": None,
        "language": "russian",
        "freshness": "unknown",
        "evidence_role": "durable_trait",
        "player_feedback": True,
        "feedback_surface_mode": "concrete_item_collection",
    }
    records = [
        {
            "feedback_id": f"fallback-{index:03d}",
            "source_id": "source-002",
            "publication_date": now.date().isoformat(),
            "language": "russian",
            "identity_mode": "transient_author_deduped",
        }
        for index in range(1, unique_item_count + 1)
    ]
    recurrence = "anecdotal" if unique_item_count == 1 else "limited"
    observation = {
        "category": "mechanics",
        "statement": "Concrete Russian player feedback describes a durable gameplay characteristic.",
        "sentiment": "mixed",
        "recurrence": recurrence,
        "mention_count": unique_item_count,
        "evidence_languages": ["russian"],
        "evidence_status": "durable",
        "source_ids": ["source-002"],
        "player_feedback_ids": [record["feedback_id"] for record in records],
    }
    doc["observations"] = [observation]
    doc["conflicts"] = []
    doc["summary"] = derive_dossier_summary(doc["observations"], doc["conflicts"])
    doc["evidence"] = {
        "strategy": "adaptive_multi_source_web",
        "research_state": "sufficient",
        "source_mix_status": "single_source_only",
        "single_source_reason": "Only one exact-product concrete player-feedback collection was needed for this fixture.",
        "russian_attempt": "found_and_used",
        "overall_strength": "limited",
        "stop_reason": "evidence_stable",
        "coverage": {
            "dimensions": [
                {
                    "dimension": dimension,
                    "state": "covered" if dimension in {
                        "core_play_mechanics",
                        "recurring_strengths",
                        "recurring_complaints_tradeoffs",
                    } else "not_material_or_not_applicable",
                    "observation_indices": [0] if dimension in {
                        "core_play_mechanics",
                        "recurring_strengths",
                        "recurring_complaints_tradeoffs",
                    } else [],
                }
                for dimension in EVIDENCE["coverage_sufficiency"]["dimensions"]
            ],
            "closure_basis": "compact_central_experience",
            "strengths_investigated": True,
            "weaknesses_tradeoffs_investigated": True,
        },
    }
    doc["provenance"] = {"sources": [metadata, collection], "player_feedback_records": records}
    return doc


def add_stable_records(doc, appid, now, count):
    source = {
        "source_id": "source-003",
        "source_type": "steam_community",
        "domain": "steamcommunity.com",
        "url": f"https://steamcommunity.com/app/{appid}/reviews/",
        "publication_date": None,
        "language": "russian",
        "freshness": "unknown",
        "evidence_role": "durable_trait",
        "player_feedback": True,
    }
    doc["provenance"]["sources"].append(source)
    stable_ids = []
    for index in range(1, count + 1):
        feedback_id = f"feedback-{index:03d}"
        stable_ids.append(feedback_id)
        doc["provenance"]["player_feedback_records"].append({
            "feedback_id": feedback_id,
            "source_id": "source-003",
            "public_ref": f"steam-recommendation:{appid}{index:03d}",
            "publication_date": now.date().isoformat(),
            "language": "russian",
            "identity_mode": "stable_locator",
        })
    observation = doc["observations"][0]
    observation["source_ids"].append("source-003")
    observation["player_feedback_ids"] = stable_ids + observation["player_feedback_ids"]
    observation["mention_count"] = len(observation["player_feedback_ids"])
    doc["evidence"]["source_mix_status"] = "multi_source"
    doc["evidence"]["single_source_reason"] = None
    return stable_ids


class TransientAuthorFallbackRegressionTests(unittest.TestCase):
    def validate(self, doc, now):
        return validate_dossier_strict(
            doc,
            CONTROL,
            expected_appid=doc["appid"],
            expected_title=doc["title"],
            expected_ttl_days=20,
            now=now,
        )

    def test_author_fb_01_recommendationid_remains_preferred_stable_path(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(710001, now)
        doc["provenance"]["player_feedback_records"][0].update({
            "identity_mode": "stable_locator",
            "public_ref": "steam-recommendation:185290437",
        })
        self.assertIs(self.validate(doc, now), doc)
        self.assertEqual(
            EVIDENCE["feedback_item_identity"]["preferred_identity_order"],
            ["stable_locator", "transient_author_deduped"],
        )
        self.assertTrue(EVIDENCE["feedback_item_identity"]["fallback_forbidden_when_neutral_item_locator_available"])
        self.assertIn("Preferred stable path", PROMPT)

    def test_author_fb_02_transient_author_fallback_accepted_without_author_data(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(710002, now, transient_author_tokens=("ephemeral-a",))
        self.assertIs(self.validate(doc, now), doc)
        payload = json.dumps(doc, ensure_ascii=False)
        self.assertNotIn("ephemeral-a", payload)
        record = doc["provenance"]["player_feedback_records"][0]
        self.assertEqual(record["identity_mode"], "transient_author_deduped")
        self.assertNotIn("url", record)
        self.assertNotIn("public_ref", record)

    def test_author_fb_03_same_transient_author_dedupes_before_serialization(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(
            710003,
            now,
            transient_author_tokens=("ephemeral-same", "ephemeral-same"),
        )
        self.assertEqual(len(doc["provenance"]["player_feedback_records"]), 1)
        self.assertEqual(doc["observations"][0]["mention_count"], 1)
        self.assertEqual(doc["observations"][0]["recurrence"], "anecdotal")
        self.assertNotIn("ephemeral-same", json.dumps(doc))
        self.assertIs(self.validate(doc, now), doc)

    def test_author_fb_04_two_distinct_authors_produce_limited_local_fallback_records(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(
            710004,
            now,
            transient_author_tokens=("ephemeral-a", "ephemeral-b"),
        )
        self.assertEqual(
            [record["feedback_id"] for record in doc["provenance"]["player_feedback_records"]],
            ["fallback-001", "fallback-002"],
        )
        self.assertEqual(doc["observations"][0]["recurrence"], "limited")
        self.assertEqual(doc["observations"][0]["mention_count"], 2)
        self.assertIs(self.validate(doc, now), doc)

    def test_author_fb_05_fallback_only_recurrence_is_capped_at_limited(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        moderate = fallback_dossier(
            710005,
            now,
            transient_author_tokens=("a", "b", "c"),
        )
        moderate["observations"][0]["recurrence"] = "moderate"
        moderate["evidence"]["overall_strength"] = "moderate"
        with self.assertRaisesRegex(ValueError, "moderate recurrence requires at least three stable-locator records"):
            self.validate(moderate, now)

        strong = fallback_dossier(
            710006,
            now,
            transient_author_tokens=("a", "b", "c", "d", "e"),
        )
        strong["observations"][0]["recurrence"] = "strong"
        strong["evidence"]["overall_strength"] = "strong"
        with self.assertRaisesRegex(ValueError, "strong recurrence requires at least five stable-locator records"):
            self.validate(strong, now)

    def test_author_fb_06_mixed_stable_and_fallback_uses_stable_threshold_for_moderate(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)

        rejected = fallback_dossier(710007, now, transient_author_tokens=("a", "b", "c"))
        add_stable_records(rejected, "710007", now, 2)
        rejected["observations"][0]["recurrence"] = "moderate"
        rejected["evidence"]["overall_strength"] = "moderate"
        with self.assertRaisesRegex(ValueError, "moderate recurrence requires at least three stable-locator records"):
            self.validate(rejected, now)

        accepted = fallback_dossier(710008, now, transient_author_tokens=("a", "b"))
        add_stable_records(accepted, "710008", now, 3)
        accepted["observations"][0]["recurrence"] = "moderate"
        accepted["evidence"]["overall_strength"] = "moderate"
        self.assertEqual(accepted["observations"][0]["mention_count"], 5)
        self.assertIs(self.validate(accepted, now), accepted)

    def test_author_fb_07_profile_scoped_review_may_be_inspected_but_profile_never_persists(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        transient_profile_url = "https://steamcommunity.com/id/ephemeral-profile/recommended/1000360/"
        doc = fallback_dossier(
            1000360,
            now,
            title="Hellish Quart",
            transient_author_tokens=(transient_profile_url,),
        )
        payload = json.dumps(doc, ensure_ascii=False)
        self.assertNotIn("ephemeral-profile", payload)
        self.assertNotIn("/id/", payload)
        self.assertIs(self.validate(doc, now), doc)

        leaked = copy.deepcopy(doc)
        leaked["provenance"]["sources"][1]["domain"] = "steamcommunity.com"
        leaked["provenance"]["sources"][1]["url"] = transient_profile_url
        with self.assertRaisesRegex(ValueError, "author/profile"):
            self.validate(leaked, now)

    def test_author_fb_08_aggregate_page_without_concrete_item_mode_is_invalid(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(710009, now)
        del doc["provenance"]["sources"][1]["feedback_surface_mode"]
        with self.assertRaisesRegex(ValueError, "Steam Store app page is not a player-feedback item"):
            self.validate(doc, now)

    def test_author_fb_09_valid_russian_fallback_satisfies_found_and_used(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(710010, now)
        self.assertEqual(doc["evidence"]["russian_attempt"], "found_and_used")
        self.assertEqual(doc["provenance"]["player_feedback_records"][0]["language"], "russian")
        self.assertIs(self.validate(doc, now), doc)

    def test_author_fb_10_exact_product_identity_remains_fail_closed(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(710011, now)
        doc["provenance"]["sources"][1]["url"] = "https://store.steampowered.com/app/999999/?l=russian"
        with self.assertRaisesRegex(ValueError, "appid does not match exact dossier appid"):
            self.validate(doc, now)

    def test_author_fb_11_direct_hash_or_identity_derived_local_ids_are_rejected(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = fallback_dossier(710012, now)
        doc["provenance"]["player_feedback_records"][0]["feedback_id"] = "a" * 64
        doc["observations"][0]["player_feedback_ids"] = ["a" * 64]
        with self.assertRaisesRegex(ValueError, "fallback-NNN"):
            self.validate(doc, now)

        source_hash = fallback_dossier(710013, now)
        direct_hash = "b" * 64
        source_hash["provenance"]["sources"][1]["source_id"] = direct_hash
        source_hash["provenance"]["player_feedback_records"][0]["source_id"] = direct_hash
        source_hash["observations"][0]["source_ids"] = [direct_hash]
        with self.assertRaisesRegex(ValueError, "source-NNN"):
            self.validate(source_hash, now)

    def test_author_fb_12_current_g000001_collection_card_shapes_are_usable_without_identity_persistence(self):
        work = json.loads(
            (ROOT / "data/production/pre_ai/taste_steam_review_dossier_work.json").read_text(encoding="utf-8")
        )
        first_group = work["submission_group_plan"]["groups"][0]
        self.assertGreaterEqual(len(first_group["items"]), 2)

        now = datetime.now(timezone.utc).replace(microsecond=0)
        docs = []
        transient_tokens = []
        for index, item in enumerate(first_group["items"][:2], start=1):
            tokens = (f"ephemeral-current-{index}-a", f"ephemeral-current-{index}-b")
            transient_tokens.extend(tokens)
            doc = fallback_dossier(
                item["appid"],
                now,
                title=item["title"],
                transient_author_tokens=tokens,
            )
            self.assertIs(self.validate(doc, now), doc)
            docs.append(doc)

        serialized = json.dumps(docs, ensure_ascii=False)
        for token in transient_tokens:
            self.assertNotIn(token, serialized)


if __name__ == "__main__":
    unittest.main()
