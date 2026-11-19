#!/usr/bin/env python3
"""Local regressions for opt-in isolated Notes V2 lean finals. No live writes."""
import copy
import unittest
from datetime import datetime, timedelta, timezone

from dossier_notes_v2_lean_final import LEAN_SCHEMA, validate_lean_final
from taste_steam_review_dossier_strict import validate_dossier_strict
from taste_steam_review_dossier_strict import load_worker_schema

NOW = datetime.now(timezone.utc).replace(microsecond=0)

def make_lean_final(appid="2124120", title="SULFUR", now=None):
    now = (now or NOW).replace(microsecond=0)
    generated = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    expires = (now + timedelta(days=20)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "schema": LEAN_SCHEMA, "schema_version": 1,
        "appid": str(appid), "title": title,
        "generated_at_utc": generated, "expires_at_utc": expires, "ttl_days": 20,
        "game_identity": {"appid":str(appid),"work_title":title,"release_year":2024 if str(appid) == "2124120" else None},
        "summary": "Динамичный шутер с боевой добычей и значимыми тактическими компромиссами.",
        "observations": [
            {"category":"mechanics", "sentiment":"positive",
             "statement":"Бои требуют точного управления оружием и активного перемещения между укрытиями.",
             "evidence_status":"durable", "as_of":None, "source_indices":[1]},
            {"category":"repetition", "sentiment":"mixed",
             "statement":"Возвращение на знакомые уровни одновременно развивает навык и усиливает повторяемость.",
             "evidence_status":"uncertain", "as_of":None, "source_indices":[1]},
        ],
        "conflicts":[],
        "sources":[
            {"url":f"https://store.steampowered.com/app/{appid}/","kind":"identity"},
            {"url":f"https://steamcommunity.com/app/{appid}/reviews/","kind":"player_feedback"},
        ],
        "unknowns":["Частота и актуальность отдельных технических жалоб не подтверждены."],
        "confidence":"limited",
    }

class LeanFinalContractTests(unittest.TestCase):
    def check(self, doc):
        return validate_lean_final(doc,expected_appid="2124120",
                                   expected_title="SULFUR",expected_ttl_days=20,now=NOW)

    def test_minimal_final_has_no_review_record_archive_or_twelve_dimension_ledger(self):
        doc=make_lean_final()
        self.assertNotIn("provenance",doc)
        self.assertNotIn("player_feedback_records",doc)
        self.assertNotIn("evidence",doc)
        self.assertEqual(self.check(doc),doc)

    def test_wrong_appid_edition_or_identity_rejected(self):
        for key,val in (("appid","123"),("title","Other game")):
            doc=make_lean_final()
            doc[key]=val
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,"wrong frozen"):
                self.check(doc)
        doc=make_lean_final()
        doc["game_identity"]["work_title"]="Different edition"
        with self.assertRaisesRegex(ValueError,"conflicting game identity"):
            self.check(doc)

    def test_invalid_category_and_extra_review_ledger_rejected(self):
        doc=make_lean_final()
        doc["observations"][0]["category"]="controls_game_feel"
        with self.assertRaisesRegex(ValueError,"category"):
            self.check(doc)
        doc=make_lean_final()
        doc["provenance"]={"player_feedback_records":[]}
        with self.assertRaisesRegex(ValueError,"Additional properties"):
            self.check(doc)

    def test_missing_strength_or_tradeoff_rejected(self):
        doc=make_lean_final()
        for item in doc["observations"]: item["sentiment"]="positive"
        with self.assertRaisesRegex(ValueError,"trade-off"):
            self.check(doc)
        doc=make_lean_final()
        for item in doc["observations"]: item["sentiment"]="negative"
        with self.assertRaisesRegex(ValueError,"strength"):
            self.check(doc)

    def test_missing_central_gameplay_rejected(self):
        doc=make_lean_final()
        for item in doc["observations"]: item["category"]="localization"
        with self.assertRaisesRegex(ValueError,"central game-experience"):
            self.check(doc)

    def test_source_index_must_resolve(self):
        doc=make_lean_final()
        doc["observations"][0]["source_indices"]=[99]
        with self.assertRaisesRegex(ValueError,"unbound source"):
            self.check(doc)

    def test_temporal_claim_needs_actual_dated_source(self):
        doc=make_lean_final()
        doc["observations"][0]["evidence_status"]="current"
        with self.assertRaisesRegex(ValueError,"dated temporal"):
            self.check(doc)
        doc=make_lean_final()
        doc["observations"][0]["evidence_status"]="current"
        doc["observations"][0]["as_of"]="2020-01-01"
        with self.assertRaisesRegex(ValueError,"too old"):
            self.check(doc)
        doc=make_lean_final()
        doc["observations"][0]["evidence_status"]="historical"
        doc["observations"][0]["as_of"]="2020-01-01"
        with self.assertRaisesRegex(ValueError,"matching dated player source"):
            self.check(doc)
        doc["sources"][1]["published_on"]="2020-01-01"
        with self.assertRaisesRegex(ValueError,"matching dated player source"):
            self.check(doc)
        doc["sources"][1]["url"]="https://steamcommunity.com/app/2124120/discussions/0/999999999999999999/"
        self.check(doc)
        doc["observations"][0]["evidence_status"]="current"
        doc["observations"][0]["as_of"]=NOW.date().isoformat()
        doc["sources"][1]["published_on"]=NOW.date().isoformat()
        self.check(doc)
        doc["sources"][1]["kind"]="context"
        with self.assertRaisesRegex(ValueError,"matching dated player source"):
            self.check(doc)


    def test_unsafe_author_profile_and_duplicate_sources_rejected(self):
        doc=make_lean_final()
        doc["sources"][1]["url"]="https://steamcommunity.com/profiles/123456789/recommended/"
        with self.assertRaisesRegex(ValueError,"author/profile scoped"):
            self.check(doc)
        doc=make_lean_final()
        doc["sources"][1]["url"]=doc["sources"][0]["url"]
        with self.assertRaisesRegex(ValueError,"duplicate source URL"):
            self.check(doc)

    def test_temporal_source_date_and_exact_steam_appid(self):
        doc=make_lean_final()
        doc["sources"][1]["published_on"]="2026-02-30"
        with self.assertRaisesRegex(ValueError,"real calendar date"):
            self.check(doc)
        doc=make_lean_final()
        doc["sources"][1]["url"]="https://steamcommunity.com/app/999999/reviews/"
        with self.assertRaisesRegex(ValueError,"wrong AppID"):
            self.check(doc)
        doc=make_lean_final()
        doc["sources"][1]["url"] += "?token=secret"
        with self.assertRaisesRegex(ValueError,"sensitive query"):
            self.check(doc)

    def test_empty_source_requires_limited_confidence_and_uncertainty(self):
        doc=make_lean_final()
        doc["sources"]=[]
        for row in doc["observations"]:row["source_indices"]=[]
        self.check(doc)
        doc["confidence"]="moderate"
        with self.assertRaisesRegex(ValueError,"moderate"):
            self.check(doc)

    def test_existing_canonical_strict_validator_rejects_lean(self):
        doc=make_lean_final()
        with self.assertRaises(ValueError):
            validate_dossier_strict(doc,{},expected_appid="2124120",now=NOW)

if __name__ == "__main__":
    unittest.main()
