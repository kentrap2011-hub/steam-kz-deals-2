#!/usr/bin/env python3
"""Isolated Research→lean Assembly→Deep scoring compatibility; no owner writer or live Deep."""
import copy
import hashlib
import unittest
from datetime import datetime, timezone

import dossier_notes_v2_deep_compat as compat
import dossier_research_notes_v2 as v2
import progressive_pass2 as deep
import test_dossier_research_notes_v2 as research_fixture
from dossier_notes_v2_lean_final import validate_lean_final
from test_dossier_notes_v2_lean_final import make_lean_final
from taste_steam_review_dossier_test_fixture import web_dossier

NOW = datetime.now(timezone.utc).replace(microsecond=0)
APPID = "2124120"
TITLE = "SULFUR"

def sandbox_record(doc):
    return {
        "path": "data/control/dossier_notes_v2/batch_pilot_store/lean-pilot-20261119/App_" + doc["appid"] + ".json",
        "doc": doc,
        "content_sha256": deep.canonical_sha256(doc),
    }

class LeanDeepCompatibilityTests(unittest.TestCase):
    def test_noncanonical_lean_is_explicitly_rejected_by_normal_deep(self):
        doc=make_lean_final(now=NOW)
        args={"binding":{"appid":APPID},
              "semantic_input":{"title":TITLE,"release_date":"2024-01-01"},
              "dossier_record":sandbox_record(doc),
              "current_binding":compat.preview_binding(),"now":NOW}
        self.assertEqual(
            deep.dossier_is_eligible(**args),
            (False,"lean_dossier_is_not_canonical_deep_evidence"),
        )
        self.assertEqual(
            deep.dossier_is_eligible(**args,lean_sandbox_preview=True),
            (True,"eligible_lean_sandbox_preview_only"),
        )

    def test_sandbox_preview_checks_exact_identity_sha_path_and_expiry(self):
        doc=make_lean_final(now=NOW)
        record=sandbox_record(doc)
        common={"binding":{"appid":APPID},
                "semantic_input":{"title":TITLE},
                "dossier_record":record,
                "current_binding":compat.preview_binding(),"now":NOW}
        bad=copy.deepcopy(common)
        bad["binding"]["appid"]="99999"
        self.assertEqual(compat.lean_preview_eligibility(**bad)[1],"lean_preview_wrong_appid")
        bad=copy.deepcopy(common)
        bad["semantic_input"]["title"]="SULFUR Different Edition"
        self.assertEqual(compat.lean_preview_eligibility(**bad)[1],"lean_preview_wrong_title_or_edition")
        bad=copy.deepcopy(common)
        bad["dossier_record"]["content_sha256"]="0"*64
        self.assertEqual(compat.lean_preview_eligibility(**bad)[1],"lean_preview_dossier_digest_mismatch")
        bad=copy.deepcopy(common)
        bad["dossier_record"]["path"]="data/cache/taste_steam_review_dossiers/App_2124120.json"
        self.assertEqual(compat.lean_preview_eligibility(**bad)[1],"lean_preview_not_an_isolated_sandbox_path")
        bad=copy.deepcopy(common)
        bad["current_binding"]={"contract":"canonical-pretender"}
        self.assertEqual(compat.lean_preview_eligibility(**bad)[1],"lean_preview_binding_mismatch")
        bad=copy.deepcopy(common)
        bad["dossier_record"]["doc"]["game_identity"]["release_year"]=None
        bad["dossier_record"]["content_sha256"]=deep.canonical_sha256(bad["dossier_record"]["doc"])
        self.assertEqual(compat.lean_preview_eligibility(**bad)[1],"lean_preview_unresolved_original_release_year")

    def test_deep_uses_original_lean_observations_for_score_and_negative(self):
        doc=make_lean_final(now=NOW)
        record=sandbox_record(doc)
        work=compat.make_preview_work_item(
            {"appid":APPID},{"title":TITLE},record,now=NOW
        )
        factors={name:75 for name in deep.SCORE_FACTOR_IDS}
        row={
            "finding_id":"fit-mechanics-01",
            "text_ru":"Требовательная стрельба и движение дают освоение навыка, но маршруты повторяются.",
            "candidate_evidence_refs":[
                {"kind":"observation","index":0},
                {"kind":"observation","index":1},
            ],
            "profile_evidence_refs":[{
                "json_pointer":"/preferences/movement",
                "profile_value_sha256":"a"*64,
                "match_text_ru":"Важны изучаемые движения и развитие навыка",
            }],
            "factor_impacts":[
                {"factor_id":name, "effect":"supports","normalized_value":75}
                for name in deep.SCORE_FACTOR_IDS
            ],
        }
        scored=deep.normalize_score_findings([row],work,factors)
        self.assertEqual(scored[0]["candidate_evidence_refs"][0]["index"],0)
        neg=deep.normalize_negative_assessment({
            "status":"completed",
            "evaluated_candidate_refs":[{"kind":"observation","index":1}],
            "findings":[{
                "disposition":"caution","risk_code":None,
                "text_ru":"Игровые маршруты могут постепенно повторяться.",
                "evidence_refs":[{"kind":"observation","index":1}],
            }],
        },work)
        self.assertEqual(neg["status"],"completed")
        self.assertEqual(neg["findings"][0]["disposition"],"caution")
        # Without the explicit local preview mark, even the same digest is not Deep-ready.
        work["_sandbox_lean_preview"]=False
        with self.assertRaisesRegex(ValueError,"cannot be consumed as canonical"):
            deep.normalize_score_findings([row],work,factors)

    def test_legacy_strict_deep_eligibility_is_unchanged(self):
        doc=web_dossier(APPID,NOW,title=TITLE,release_year=2024)
        args={
            "binding":{"appid":APPID},
            "semantic_input":{"title":TITLE,"release_date":"2024-01-01"},
            "dossier_record":{
                "path":"data/cache/taste_steam_review_dossiers/App_2124120.json",
                "doc":doc,
                "content_sha256":deep.canonical_sha256(doc),
            },
            "current_binding":doc["web_evidence_contract_binding"],
            "now":NOW,
        }
        self.assertEqual(deep.dossier_is_eligible(**args),(True,"eligible"))
        self.assertEqual(deep.dossier_is_eligible(**args,lean_sandbox_preview=True),(True,"eligible"))

    def test_research_to_assembly_preflight_then_deep_preview_offline(self):
        fixture=research_fixture.NotesV2Tests(
            methodName="test_zero_evidence_research_passes_without_year_sources_or_dimensions"
        )
        fixture.setUp()
        try:
            doc=make_lean_final(APPID,TITLE,now=NOW)
            research=fixture.note(
                notes_text="Быстрые перестрелки сочетаются с повторяющимися маршрутами.",
                research_status="notes_recorded",
            )
            _,work=fixture.work(research)
            candidate=v2.candidate_assembly(
                work,outcome="assembled_candidate_ready",final_dossier=doc
            )
            preflight=v2.prepare_assembly_transport(fixture.repo,work,candidate)
            self.assertEqual(preflight["status"],"ready_for_create_only_submission")
            self.assertFalse(work["may_independently_discover"])
            self.assertEqual(validate_lean_final(doc,now=NOW),doc)
            # Staged object stands in for an isolated store; this does NOT call or
            # fake GitHub's owner-only writer acceptance or start a Deep worker.
            self.assertEqual(
                compat.lean_preview_eligibility(
                    binding={"appid":APPID},semantic_input={"title":TITLE},
                    dossier_record=sandbox_record(doc),
                    current_binding=compat.preview_binding(),now=NOW,
                )[0],True
            )
        finally:
            fixture.doCleanups()

if __name__=="__main__":
    unittest.main()
