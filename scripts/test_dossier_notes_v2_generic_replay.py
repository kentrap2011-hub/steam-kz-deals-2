#!/usr/bin/env python3
"""Disposable Git-only regressions. NEVER triggers a real owner request/Assembly."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_dossier_notes_v2_batch_route import add, git, source_copy
from test_dossier_notes_v2_owner_push import common_env, event_document
import dossier_notes_v2_generic_replay as generic
import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_batch_issuer as issuer
import dossier_notes_v2_assembly_replay_seed as seed
import dossier_notes_v2_per_item_receipts as receipts
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import blob, parent, require_only_new

OLD = "dossier-notes-v2-fresh6-20261114-rerun1"
SIX = [("1000010", "Crown Trick", 1, 0),
       ("102600", "Orcs Must Die!", 1, 1),
       ("1029690", "Sniper Elite 5", 1, 2),
       ("49520", "Borderlands 2", 70, 0),
       ("499180", "Braid, Anniversary Edition", 70, 1),
       ("501590", "Bulletstorm: Full Clip Edition", 70, 2)]


def fake_sha(value):
    return hashlib.sha1(str(value).encode("utf-8")).hexdigest()


def synth(nonce, selected=SIX):
    tr = generic.trial(nonce)
    pins = {
        "source_trial_id": OLD, "source_sandbox_head": fake_sha("old-head"),
        "source_marker_commit": fake_sha("old-marker"),
        "source_authorization_commit": fake_sha("old-auth"),
        "source_manifest_blob_sha": fake_sha("old-manifest"),
        "source_manifest_pins": {"source_main_sha":fake_sha("old-main")},
        "request_commit": fake_sha("request-"+nonce),
        "request_blob_sha":fake_sha("request-blob-"+nonce),
        "request_nonce":nonce,
        "source_research":[{
            "appid":a,"title":title,"group_sequence":g,"item_index":i,
            "source_assignment_id":"batch-"+fake_sha(a)[:24],
            "research_commit":fake_sha("Research-"+a),
            "research_blob_sha":fake_sha("Research-blob-"+a),
            "research_receipt_commit":fake_sha("Receipt-"+a),
            "research_receipt_blob_sha":fake_sha("Receipt-blob-"+a),
        } for a,title,g,i in selected]
    }
    req = {"nonce":nonce,"trial_id":tr,
           "base_main_sha":None,"request_ref":"refs/heads/dossier-assembly-requests/"+nonce,
           "request_commit":pins["request_commit"],
           "request_blob_sha":pins["request_blob_sha"]}
    return req,pins


def issue_fixture(repo, nonce, selected=SIX, copies=True):
    base = git(repo,"rev-parse","HEAD")
    req,pins = synth(nonce,selected)
    req["base_main_sha"] = base
    tr = req["trial_id"]
    grant,manifest = generic.expected_grant(repo,req,pins)
    path = batch.paths(tr)
    gc = add(repo,path["grant"],grant,"fixture owner request grant")
    mc = add(repo,path["manifest"],batch.canonical(manifest),"fixture frozen subset")
    marker = add(repo, "data/control/dossier_notes_v2/run_starts/"+nonce+".json",{
        "schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,
        "trial_id":tr,"nonce":nonce},"fixture nonce marker")
    auth = add(repo,path["authorization"],generic.expected_authorization(
        repo,tr,marker,gc,"1234567"),"fixture direct owner authorization")
    anchor = generic.issuer_structure(repo,trial_id=tr,
        marker_commit=marker,authorization_commit=auth)
    assert anchor["semantic_execution_authorized"]
    issued=[]
    if copies:
        for row in manifest["items"]:
            a = v2.frozen_assignment(repo,marker_commit=marker,trial_id=tr,
                                     appid=row["appid"])
            doc = {"schema":"DOSSIER-RESEARCH-NOTES-V2","schema_version":2,
                "assignment":a,"research_status":"limited_evidence",
                "notes_text":"Synthetic balanced preexisting Research only, no new semantics."}
            plan = receipts.prepare_candidate(repo,marker_commit=marker,
                trial_id=tr,appid=row["appid"],authorization_commit=auth,document=doc)
            candidate = seed.single_add(repo,plan["output_path"],plan["bytes"],
                                        "fixture copied Research")
            rp = receipts.prepare_receipt(repo,marker_commit=marker,trial_id=tr,
                appid=row["appid"],authorization_commit=auth,
                introduction_commit=candidate)
            rc = seed.single_add(repo,rp["receipt_path"],rp["receipt_bytes"],
                                 "fixture typed Research receipt")
            assert receipts.inspect_receipt_commit(repo,marker_commit=marker,
                trial_id=tr,appid=row["appid"],authorization_commit=auth,
                introduction_commit=candidate,receipt_commit=rc)["disposition"] == (
                    "safe_incomplete_research")
            issued.append((row["appid"],candidate,rc))
    return {"trial":tr,"grant":gc,"manifest":mc,"marker":marker,"auth":auth,
            "issued":issued,"rows":manifest["items"],"anchor":anchor,
            "head":git(repo,"rev-parse","HEAD"),"base":base}


class GenericOwnerReplayTests(unittest.TestCase):
    def test_contract_no_auto_merge_workflow_or_production(self):
        temp,repo=source_copy()
        try:
            p=generic.policy(repo)
            self.assertTrue(p["enabled_for_explicit_owner_request"])
            self.assertFalse(p["automatic_launch_on_source_merge"])
            self.assertFalse(p["production_enabled"])
            self.assertFalse(p["allow_automatic_semantic_retry"])
            workflow=(repo/generic.WORKFLOW).read_text(encoding="utf-8")
            self.assertIn("dossier-assembly-requests/**",workflow)
            self.assertIn("replay_requests/*.json",workflow)
            self.assertIn("github.run_attempt == 1",workflow)
            for bad in ("schedule:", "workflow_dispatch:", "branches: [main]"):
                self.assertNotIn(bad,workflow)
            self.assertEqual(generic.request_doc("ab"*16,OLD,["1000010"])["appids"],["1000010"])
            for source in ("dossier-notes-v2-assembly-replay-"+"ff"*16,
                           "dossier-notes-v2-original18-first", "../outside"):
                with self.subTest(source=source),self.assertRaises(ValueError):
                    generic.request_doc("ab"*16,source,["1000010"])
        finally:
            temp.cleanup()

    def test_first_and_second_owner_requests_need_no_code_or_cohort_changes(self):
        temp,repo=source_copy()
        try:
            base=git(repo,"rev-parse","HEAD")
            outcomes=[]
            for nonce in ("ab"*16,"cd"*16):
                git(repo,"checkout","-B","fixture/generic-"+nonce,base)
                outcome=issue_fixture(repo,nonce)
                outcomes.append(outcome)
                self.assertEqual(len(outcome["issued"]),6)
                self.assertEqual([a for a,_,_ in outcome["issued"]],
                    [row[0] for row in SIX])
                for appid,candidate,receipt in outcome["issued"]:
                    self.assertEqual(len(git(repo,"diff-tree","--no-commit-id",
                                "--name-only","-r",candidate).splitlines()),1)
                    self.assertEqual(len(git(repo,"diff-tree","--no-commit-id",
                                "--name-only","-r",receipt).splitlines()),1)
                    work=v2.assembly_work(repo,marker_commit=outcome["marker"],
                        trial_id=outcome["trial"],appid=appid,research_commit=candidate)
                    self.assertEqual(work["status"],"ready_for_autonomous_assembly")
                self.assertEqual(git(repo,"rev-parse",outcome["grant"]+"^"),base)
            self.assertNotEqual(outcomes[0]["trial"],outcomes[1]["trial"])
            self.assertTrue(set(r["assignment_id"] for r in outcomes[0]["rows"])
                              .isdisjoint(set(r["assignment_id"] for r in outcomes[1]["rows"])))
            self.assertEqual(git(repo,"rev-parse","HEAD"),outcomes[-1]["head"])
            with self.assertRaises(ValueError):
                issue_fixture(repo,"cd"*16)
            for old in ("data/ai_inbox/dossier_notes_v2/"+OLD,
                        "data/ai_inbox/dossier_assembly_v2/"+OLD,
                        "data/cache/taste_steam_review_dossiers",
                        "data/cache/progressive_pass2_state.json"):
                self.assertEqual(git(repo,"diff","--name-only",base,"HEAD","--",old),"",old)
        finally:
            temp.cleanup()

    def test_subset_order_wrong_edition_appid_source_and_missing_receipt(self):
        temp,repo=source_copy()
        try:
            base=git(repo,"rev-parse","HEAD")
            req,pins=synth("ab"*16,SIX[3:])
            req["base_main_sha"]=base
            _,m=generic.expected_grant(repo,req,pins)
            self.assertEqual([x["appid"] for x in m["items"]],["49520","499180","501590"])
            bad=copy.deepcopy(pins)
            bad["source_research"][0]["title"]="Wrong Edition"
            self.assertNotEqual(generic.rows_from_pins(req["trial_id"],bad),m["items"])
            bad=copy.deepcopy(pins)
            bad["source_research"][1]["appid"]="49520"
            with self.assertRaises(ValueError):
                generic.rows_from_pins(req["trial_id"],bad)
            bad=copy.deepcopy(pins)
            bad["source_research"][1]["research_receipt_commit"]="not_a_sha"
            with self.assertRaises(ValueError):
                generic.rows_from_pins(req["trial_id"],bad)
            bad=copy.deepcopy(pins)
            bad["source_research"].reverse()
            with self.assertRaises(ValueError):
                generic.rows_from_pins(req["trial_id"],bad)
            bad=copy.deepcopy(pins)
            bad["source_research"][1]["research_receipt_blob_sha"]="0"*40
            # Assignment identity remains based on the original Research commit;
            # runtime owner source attestation must verify the separate receipt blob.
            self.assertEqual(generic.rows_from_pins(req["trial_id"],bad),
                             generic.rows_from_pins(req["trial_id"],pins))
            for badids in (["999999999"],["49520","49520"],[],["Braid"]):
                with self.assertRaises(ValueError):
                    generic.request_doc("ab"*16,OLD,badids)
        finally:
            temp.cleanup()

    def test_owner_branch_first_push_provenance_forgery_and_reused_attempt(self):
        temp,repo=source_copy()
        try:
            nonce="ab"*16
            start=git(repo,"rev-parse","HEAD")
            branch=generic.REQUEST_BRANCH+nonce
            git(repo,"checkout","-b",branch)
            request=generic.request_doc(nonce,OLD,[row[0] for row in SIX])
            commit=add(repo,generic.request_path(nonce),request,"fixture operator create-only request")
            git(repo,"remote","set-url","origin","https://github.com/"+batch.REPOSITORY+".git")
            with tempfile.TemporaryDirectory() as d:
                e=Path(d)/"event.json"
                doc=event_document("refs/heads/"+branch,start,commit)
                e.write_text(json.dumps(doc))
                env=common_env(generic.WORKFLOW,"refs/heads/"+branch,commit,e)
                def remote(_,ref):
                    if ref=="refs/heads/main":return start
                    if ref=="refs/heads/"+branch:return commit
                    return None
                with patch.object(issuer,"remote",side_effect=remote):
                    approved=generic.request_guard(repo,env)
                    self.assertEqual(approved["trial_id"],generic.trial(nonce))
                    for patchenv in (
                        {"GITHUB_ACTOR_ID":"0"},{"GITHUB_RUN_ATTEMPT":"2"},
                        {"GITHUB_REF":"refs/heads/main"},
                        {"GITHUB_WORKFLOW_REF":"wrong"},
                        {"GITHUB_EVENT_NAME":"workflow_dispatch"},
                    ):
                        with self.subTest(patch=patchenv),self.assertRaises(ValueError):
                            generic.request_guard(repo,{**env,**patchenv})
                    for patchdoc in ({"before":"0"*40},{"forced":True},
                                     {"sender":{"id":0}},
                                     {"ref":"refs/heads/main"}):
                        e.write_text(json.dumps({**doc,**patchdoc}))
                        with self.assertRaises(ValueError):
                            generic.request_guard(repo,env)
                    e.write_text(json.dumps(doc))
                    with patch.object(issuer,"remote",return_value=commit):
                        with self.assertRaises(ValueError):
                            generic.request_guard(repo,env)
        finally:
            temp.cleanup()

    def test_real_completed_owner_run_gate_and_wrong_token_scope(self):
        temp,repo=source_copy()
        try:
            f=issue_fixture(repo,"ab"*16,selected=SIX[:1],copies=False)
            a=f["anchor"]
            name=generic.REQUEST_BRANCH+"ab"*16
            action={
                "id":1234567,"event":"push","status":"completed",
                "conclusion":"success","run_attempt":1,"head_branch":name,
                "head_sha":a["request_commit"],"path":generic.WORKFLOW,
                "display_title":"Authorize Assembly replay "+name+
                    " at "+a["request_commit"],
                "actor":{"id":int(batch.OWNER_ID),"login":batch.OWNER_LOGIN},
                "triggering_actor":{"id":int(batch.OWNER_ID),"login":batch.OWNER_LOGIN},
            }
            with patch.object(receipts,"_github_get",return_value=action):
                self.assertTrue(generic.authenticated_owner_run(
                    a,"synthetic-token",batch.REPOSITORY))
            for key,wrong in (("status","in_progress"),("conclusion","failure"),
                              ("run_attempt",2),("head_sha","a"*40),
                              ("head_branch","main"),("event","workflow_dispatch"),
                              ("path","other"),("display_title","forged"),
                              ("actor",{"id":0,"login":"different"})):
                with self.subTest(key=key), patch.object(
                    receipts,"_github_get",return_value={**action,key:wrong}):
                    with self.assertRaises(ValueError):
                        generic.authenticated_owner_run(a,"synthetic-token",batch.REPOSITORY)
            with self.assertRaises(ValueError):
                generic.authenticated_owner_run(a,None,batch.REPOSITORY)
        finally:
            temp.cleanup()


if __name__=="__main__":
    unittest.main()
