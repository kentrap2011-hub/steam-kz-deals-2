#!/usr/bin/env python3
"""Synthetic-only trial-wide authority tests; no actual Assembly or Git writes."""
import copy
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import dossier_shadow_18_trial_wide_semantic_gate as gate
from dossier_shadow_research_trial_publish import EXPECTED_APPIDS

ROOT = Path(__file__).resolve().parents[1]
CONFIG = "config/dossier_shadow_18_trial_wide_semantic_authority_v1.json"
ORIGINAL = "config/dossier_shadow_research_trial_contract_v1.json"
DECISION = ("reviews/dossier_shadow_offline/"
            "dossier_shadow_calibration_20261011_6x3_director_decision_v1.json")
PINS = "config/dossier_shadow_18_github_python_handoff_pins_v1.json"


class TrialWideGateTests(unittest.TestCase):
    def setUp(self):
        self.c = gate.load(ROOT / CONFIG)
        self.o = gate.load(ROOT / ORIGINAL)
        self.d = gate.load(ROOT / DECISION)
        self.p = gate.load(ROOT / PINS)
        self.appointments = {
            "schema": gate.APPOINTMENTS, "trial_id": gate.TRIAL,
            "appointed_for": "prospective_nonproduction_assembly",
            "director_approved": True,
            "reviewer_roles": {"A": "reviewer-one", "B": "reviewer-two",
                               "C": "reviewer-three"},
            "quality_review_completed": False,
            "source_privacy_rules": "strict_original_Stage_B_source_first_privacy",
        }
        self.s = {
            "rows": [{"appid": appid,
                      "status": ("research_not_submitted" if appid in gate.FIXED_MISSING
                                 else "research_transport_invalid" if appid in gate.INVALID
                                 else "ready")} for appid in EXPECTED_APPIDS],
            "semantic_attempts": 0, "canonical_acceptance": False, "deep_ready": False
        }
        self.ctx = {
            "event": "workflow_dispatch", "ref": "refs/heads/main",
            "repository": "kentrap2011-hub/steam-kz-deals-2",
            "actor": "kentrap2011-hub", "run_attempt": "1",
            "run_id": "123456789", "sha": "a" * 40,
        }

    def check(self):
        return gate.validate_authority(
            self.c, self.o, self.d, self.p, self.appointments, self.s,
            github_context=self.ctx)

    def denied(self):
        with self.assertRaisesRegex(ValueError, "SHADOW_GITHUB_PYTHON_HANDOFF_BLOCKED"):
            self.check()

    def test_01_all_twelve_in_exact_original_order_synthetic(self):
        r = self.check()
        self.assertEqual(len(r["original_order"]), 18)
        self.assertEqual(r["original_order"], EXPECTED_APPIDS)
        self.assertEqual(len(r["ready_appids_in_original_order"]), 12)
        self.assertEqual(r["invalid_appids"], ["2124120", "2138710"])
        self.assertEqual(r["missing_appids"],
                         ["1508750", "1607130", "1849000", "1857090"])
        self.assertEqual(r["ready_appids_in_original_order"][0], "1517180")
        self.assertIn("213610", r["ready_appids_in_original_order"])
        self.assertFalse(r["semantics_executed"])
        self.assertFalse(r["production_active"])
        self.assertEqual(r["github_main_sha"], "a"*40)

    def test_02_old_decision_and_Research_permission_do_not_authorize(self):
        self.appointments = None
        self.denied()
        self.appointments = {"schema": "reviewer-approved"}
        self.denied()

    def test_03_old_historical_flags_must_remain_blocked(self):
        for target, key, val in (
            (self.o, "no_assembly_activation", False),
            (self.o, "standalone_sandbox_semantics_approved", True),
            (self.o, "reviewer_roles_finalized", True),
            (self.o, "canonical_production_authority_active", True),
            (self.d["operator_authority"], "actual_semantic_execution_permitted_now", True),
            (self.d, "two_stage_production_active", True),
            (self.d, "automatic_trial_launch", True)):
            t = copy.deepcopy(target); target[key] = val
            self.denied()
            target.clear(); target.update(t)

    def test_04_wrong_trial_marker_commit_pins_and_branch(self):
        for key, bad in (("trial_id","other"),("original_assembly_marker","f"*40),
                         ("original_assembly_buffer_blob","f"*40),
                         ("research_marker","f"*40),
                         ("research_feasibility_commit","f"*40),
                         ("group_order",[3,8,13,15,20,18]),
                         ("handoff_branch","main"),
                         ("handoff_branch_initial_base","f"*40),
                         ("handoff_prefix","data/ai_inbox/")):
            old = self.c[key]; self.c[key] = bad; self.denied(); self.c[key] = old
        old = self.p["original_research_introduction_commits"]
        self.p["original_research_introduction_commits"] = dict(old, **{"1517180": "f"*40})
        self.denied()
        self.p["original_research_introduction_commits"] = old

    def test_05_no_appid_invention_reordering_or_status_forgery(self):
        self.s["rows"][0]["appid"] = "999"
        self.denied()
        self.s["rows"][0]["appid"] = EXPECTED_APPIDS[0]
        self.s["rows"][1]["status"] = "research_not_submitted"
        self.denied()
        self.s["rows"][1]["status"] = "ready"
        self.s["rows"][17]["status"] = "ready"
        self.denied()
        self.s["rows"][17]["status"] = "research_transport_invalid"
        self.s["semantic_attempts"] = 1
        self.denied()

    def test_06_reviewer_appointment_is_not_quality_verdict(self):
        for change in (
            {"reviewer_roles": {"A":"same","B":"same","C":"different"}},
            {"reviewer_roles": {"A":"x","B":"y"}},
            {"director_approved": False}, {"source_privacy_rules": "relaxed"},
            {"appointed_for": "other"}, {"reviewer_roles":
                  {"A":"valid","B":"valid-two","C":"bad space"}}):
            old = copy.deepcopy(self.appointments)
            self.appointments.update(change); self.denied()
            self.appointments = old
        # Review may occur later, but is NOT a prerequisite for processing.
        self.appointments["quality_review_completed"] = True
        self.assertEqual(len(self.check()["ready_appids_in_original_order"]), 12)

    def test_07_no_fake_Github_execution_run(self):
        for key, bad in (
            ("event","pull_request"), ("ref","refs/heads/testing"),
            ("repository","other/repo"), ("actor","other-user"),
            ("run_attempt","2"), ("run_id","bogus"), ("sha","bad")):
            old = self.ctx[key]; self.ctx[key] = bad; self.denied(); self.ctx[key] = old

    def test_08_automated_execution_retry_and_production_denied(self):
        for key, bad in (
            ("manual_one_shot", False), ("no_automatic_execution", False),
            ("no_recurring_schedule", False), ("no_retry", False),
            ("no_new_queue", False), ("no_batch_quota", False),
            ("canonical_acceptance",True), ("deep_ready",True),
            ("two_stage_production_active",True),
            ("one_stage_dossier_production_unchanged",False),
            ("publish_requires_separate_human_approval_per_appid",False),
            ("typed_result_exact_keys",["payload"])):
            old=self.c[key]; self.c[key]=bad; self.denied(); self.c[key]=old

    def test_09_publish_needs_independent_original_pr_owner_comment(self):
        sha="a"*40
        comment={
            "id": 111, "created_at":"2026-10-20T12:00:00Z",
            "issue_url":"https://api.github.com/repos/"
                        "kentrap2011-hub/steam-kz-deals-2/issues/230",
            "user":{"login":"kentrap2011-hub"},
            "body":("AUTHORIZE_SHADOW_ASSEMBLY_PUBLISH_V1 "
                    "trial_id=" + gate.TRIAL +
                    " appid=1517180 semantic_commit=" + sha)
        }
        self.assertTrue(gate.validate_publish_approval(
            comment, appid="1517180", semantic_commit=sha))
        for key,bad in (
            ("issue_url","https://api.github.com/repos/else/issues/230"),
            ("body","DIRECTOR_AUTHORIZED_SHADOW_ASSEMBLY_TYPED_HANDOFF"),
            ("body",comment["body"].replace("1517180","1533420")),
            ("body",comment["body"].replace(sha,"b"*40))):
            v=copy.deepcopy(comment);v[key]=bad
            with self.assertRaises(ValueError):
                gate.validate_publish_approval(v,appid="1517180",semantic_commit=sha)
        for login in ("random-user","github-actions[bot]"):
            v=copy.deepcopy(comment);v["user"]["login"]=login
            with self.assertRaises(ValueError):
                gate.validate_publish_approval(v,appid="1517180",semantic_commit=sha)
        with self.assertRaises(ValueError):
            gate.validate_publish_approval(comment,appid="2124120",semantic_commit=sha)

    def test_09b_github_run_and_receipt_must_be_independently_consistent(self):
        receipt=self.check()
        run={"id":123456789,"actor":{"login":"kentrap2011-hub"},
             "event":"workflow_dispatch", "run_attempt":1, "status":"completed",
             "conclusion":"success","head_branch":"main",
             "path":".github/workflows/validate-dossier-shadow-18-trial-wide-authority.yml",
             "head_sha":"a"*40}
        self.assertTrue(gate.validate_github_authority_receipt(
            run,receipt,appid="1517180"))
        for key,val in (("id",2),("event","push"),("run_attempt",2),
                        ("conclusion","failure"),("status","queued"),
                        ("head_branch","else"),("head_sha","b"*40),
                        ("path",".github/workflows/other.yml")):
            wrong=copy.deepcopy(run); wrong[key]=val
            with self.assertRaises(ValueError):
                gate.validate_github_authority_receipt(
                    wrong,receipt,appid="1517180")
        for key,val in (("issuer_run_id",0),("original_marker","b"*40),
                        ("ready_appids_in_original_order",[]),
                        ("production_active",True),("semantics_executed",True)):
            wrong=copy.deepcopy(receipt);wrong[key]=val
            with self.assertRaises(ValueError):
                gate.validate_github_authority_receipt(
                    run,wrong,appid="1517180")
        with self.assertRaises(ValueError):
            gate.validate_github_authority_receipt(run,receipt,appid="2124120")

    def test_10_resume_only_verified_Git_commits_prefix(self):
        ready=[r["appid"] for r in self.s["rows"] if r["status"]=="ready"]
        c1,c2="1"*40,"2"*40
        marker=gate.FIXED_MARKER
        tip=c2
        prefix=self.c["handoff_prefix"]
        paths={c1:prefix+"/"+ready[0]+".json", c2:prefix+"/"+ready[1]+".json"}
        class GitStage:
            def git(self, repo, *args):
                if args[:2]==("rev-parse","refs/remotes/origin/"+self_branch):
                    return SimpleNamespace(stdout=(tip+"\n").encode())
                if args[:2]==("rev-list","--reverse"):
                    return SimpleNamespace(stdout=(c1+"\n"+c2+"\n").encode())
                if args[:4]==("rev-list","--parents","-n","1"):
                    sha=args[4]; parent=marker if sha==c1 else c1
                    return SimpleNamespace(stdout=(sha+" "+parent+"\n").encode())
                if args[0]=="show":
                    return SimpleNamespace(stdout=b'{"outcome":"x","payload":{},"supplemental_operations":[]}')
                raise AssertionError(args)
            def first_parent_contains(self, repo, m, t): return m==marker and t==tip
            def require_only_new(self, repo, sha, p):
                gate.require(p==[paths[sha]],"not the next original eligible item")
            def blob(self, repo, sha, path): return "a"*40
        self_branch=self.c["handoff_branch"]
        fake=GitStage()
        with patch("dossier_shadow_18_github_python_handoff.remote_tip", return_value=tip), patch(
                "dossier_shadow_18_github_python_handoff.semantic_submission", return_value={}):
            result=gate.verified_handoff_progress(None,fake,self.c,self.s)
            self.assertEqual(result["verified_submitted_appids"],ready[:2])
            self.assertEqual(result["next_unsubmitted_appid"],ready[2])
            self.assertTrue(result["no_automatic_resume_for_uncommitted_attempt"])
            # A later sibling cannot be replayed/used as a replacement for earlier prefix.
            paths[c2]=prefix+"/"+ready[3]+".json"
            with self.assertRaises(ValueError):
                gate.verified_handoff_progress(None,fake,self.c,self.s)

if __name__=="__main__":
    unittest.main()
