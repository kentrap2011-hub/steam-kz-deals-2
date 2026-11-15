#!/usr/bin/env python3
"""Synthetic only: strict owner push evidence, six-item binding and receipt CAS."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_dossier_notes_v2_batch_route import source_copy, git, add
import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_batch_issuer as issuer
import dossier_notes_v2_research_receipt_ingest as ingest
import dossier_notes_v2_per_item_receipts as receipts
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import parent, require_only_new

TRIAL = batch.OWNER_PUSH_TRIAL
OLD = "dossier-notes-v2-fresh6-20261111-first"


def event_document(ref, before, after):
    return {
        "ref": ref, "before": before, "after": after,
        "created": False, "deleted": False, "forced": False,
        "head_commit": {"id": after},
        "repository": {"full_name": batch.REPOSITORY,
                       "owner": {"id": int(batch.OWNER_ID)}},
        "sender": {"id": int(batch.OWNER_ID)},
    }


def common_env(workflow, ref, sha, event_file):
    return {
        "GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "push",
        "GITHUB_REPOSITORY": batch.REPOSITORY,
        "GITHUB_REPOSITORY_OWNER_ID": batch.OWNER_ID,
        "GITHUB_ACTOR_ID": batch.OWNER_ID,
        "GITHUB_ACTOR": batch.OWNER_LOGIN,
        "GITHUB_TRIGGERING_ACTOR": batch.OWNER_LOGIN,
        "GITHUB_REF": ref, "GITHUB_WORKFLOW_REF":
            batch.REPOSITORY + "/" + workflow + "@" + ref,
        "GITHUB_SHA": sha,
        "GITHUB_RUN_ATTEMPT": "1",
        "GITHUB_RUN_ID": "919100011",
        "GITHUB_EVENT_PATH": str(event_file),
    }


def synthetic_push_issuer(repo, trial=TRIAL, run_id="919100011"):
    ps=batch.paths(trial)
    base=git(repo,"rev-parse","HEAD")
    grant=add(repo,ps["grant"],batch.expected_grant(repo,trial,base),
              "fixture owner push grant")
    manifest=add(repo,ps["manifest"],batch.manifest_blueprint(repo,trial)["bytes"],
                 "fixture owner push manifest")
    nonce="fa" * 16
    marker=add(repo,"data/control/dossier_notes_v2/run_starts/"+nonce+".json",
               {"schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,
                "trial_id":trial,"nonce":nonce}, "fixture one-use marker")
    auth=add(repo,ps["authorization"],
             batch.expected_authorization(repo,trial,marker,grant,run_id,
                                           "owner_main_push"),
             "fixture push run authorization")
    return {"base":base,"grant":grant,"manifest":manifest,"marker":marker,
            "auth":auth,"rows":batch.rows(repo,trial)}


class OwnerPushNoUIRegression(unittest.TestCase):
    def test_six_new_exact_historical_pins_and_old_immutable_independent(self):
        temp,repo=source_copy()
        try:
            old=batch.scope(repo,OLD)
            new=batch.scope(repo,TRIAL)
            self.assertEqual(new["provenance"],old["provenance"])
            self.assertEqual([r["appid"] for r in batch.rows(repo,TRIAL)],
                             ["1000010","102600","1029690","49520","499180","501590"])
            self.assertEqual([r["title"] for r in batch.rows(repo,TRIAL)][-2:],
                             ["Braid, Anniversary Edition","Bulletstorm: Full Clip Edition"])
            self.assertEqual(new["provenance"]["prepared_for_date"],"2026-11-11")
            self.assertEqual([x["title"] for x in new["candidates"]],
                             [x["title"] for x in old["candidates"]])
            self.assertTrue(set(r["assignment_id"] for r in batch.rows(repo,OLD)).isdisjoint(
                set(r["assignment_id"] for r in batch.rows(repo,TRIAL))))
            self.assertEqual(new["original18_unchanged"],True)
            with self.assertRaises(ValueError):
                batch.expected_authorization(repo,OLD,"0"*40,"0"*40,"1","owner_main_push")
            path=repo/batch.paths(TRIAL)["contract"]
            saved=path.read_bytes()
            wrong=json.loads(saved)
            wrong["candidates"][4]["title"]="Braid"
            path.write_bytes(batch.canonical(wrong))
            try:
                with self.assertRaises(ValueError):
                    batch.scope(repo,TRIAL)
            finally:
                path.write_bytes(saved)
        finally:
            temp.cleanup()

    def test_main_source_introduction_actor_ref_event_and_one_use(self):
        temp,repo=source_copy()
        try:
            path=batch.paths(TRIAL)["contract"]
            raw=(repo/path).read_bytes()
            git(repo,"checkout","-B","main")
            git(repo,"rm","--",path)
            git(repo,"commit","-m","synthetic remove cohort for first-introduction fixture")
            source=repo/path
            source.parent.mkdir(parents=True,exist_ok=True)
            source.write_bytes(raw)
            git(repo,"add","--",path)
            git(repo,"commit","-m","synthetic owner first source introduction")
            sha=git(repo,"rev-parse","HEAD")
            before=parent(repo,sha)
            git(repo,"remote","set-url","origin",
                "https://github.com/"+batch.REPOSITORY+".git")
            with tempfile.TemporaryDirectory() as d:
                payload=Path(d)/"event.json"
                doc=event_document("refs/heads/main",before,sha)
                payload.write_text(json.dumps(doc))
                env=common_env(batch.OWNER_PUSH_WORKFLOW,"refs/heads/main",sha,payload)
                def remote(_,ref):
                    return sha if ref=="refs/heads/main" else None
                with patch.object(issuer,"remote",side_effect=remote):
                    issuer.guard_owner_push(repo,TRIAL,sha,env)
                    for change in (
                        {"GITHUB_ACTOR_ID":"0"},
                        {"GITHUB_RUN_ATTEMPT":"2"},
                        {"GITHUB_REF":"refs/heads/sandbox/"+TRIAL},
                        {"GITHUB_EVENT_NAME":"workflow_dispatch"},
                        {"GITHUB_WORKFLOW_REF":"forged"},
                        {"GITHUB_SHA":"1"*40},
                    ):
                        with self.subTest(change=change), self.assertRaises(ValueError):
                            issuer.guard_owner_push(repo,TRIAL,sha,{**env,**change})
                    for change in (
                        {"sender":{"id":0}},{"before":"0"*40},
                        {"forced":True},{"ref":"refs/heads/not-main"},
                    ):
                        with self.subTest(payload=change),self.assertRaises(ValueError):
                            payload.write_text(json.dumps({**doc,**change}))
                            issuer.guard_owner_push(repo,TRIAL,sha,env)
                    payload.write_text(json.dumps(doc))
                    with self.assertRaises(ValueError):
                        issuer.guard_owner_push(repo,OLD,sha,env)
                    with patch.object(issuer,"remote",return_value=sha):
                        with self.assertRaises(ValueError):
                            issuer.guard_owner_push(repo,TRIAL,sha,env)
        finally:
            temp.cleanup()

    def test_push_issued_strict_chain_and_actual_successful_run_required(self):
        temp,repo=source_copy()
        try:
            f=synthetic_push_issuer(repo)
            anchor=batch.issuer_structure(repo,trial_id=TRIAL,
                marker_commit=f["marker"],authorization_commit=f["auth"])
            self.assertEqual(anchor["authority_origin"],"owner_main_push")
            self.assertEqual(parent(repo,f["marker"]),f["manifest"])
            self.assertEqual(parent(repo,f["auth"]),f["marker"])
            doc={
                "id":919100011,"event":"push","status":"completed",
                "conclusion":"success","run_attempt":1,"head_branch":"main",
                "head_sha":f["base"],"path":batch.OWNER_PUSH_WORKFLOW,
                "actor":{"id":int(batch.OWNER_ID),"login":batch.OWNER_LOGIN},
                "display_title":"Issue and authorize Notes V2 rerun "+TRIAL+
                                " source "+f["base"],
            }
            with patch.object(receipts,"_github_get",return_value=doc):
                self.assertTrue(batch.authenticated_owner_run(anchor,"synthetic-token"))
            for change in (
                {"event":"workflow_dispatch"},{"head_sha":"f"*40},
                {"actor":{"id":0,"login":"other"}},{"run_attempt":2},
                {"path":batch.AUTHORIZE_WORKFLOW},{"status":"in_progress"},
                {"conclusion":"failure"},{"head_branch":"sandbox/"+TRIAL},
                {"display_title":"some other source"},
            ):
                with self.subTest(change=change),patch.object(
                        receipts,"_github_get",return_value={**doc,**change}):
                    with self.assertRaises(ValueError):
                        batch.authenticated_owner_run(anchor,"synthetic-token")
            git(repo,"checkout","-B","sandbox/"+TRIAL,f["auth"])
            self.assertEqual(ingest.issuer_from_sandbox(repo,TRIAL)["authority_origin"],
                             "owner_main_push")
        finally:
            temp.cleanup()

    def test_owner_candidate_push_serial_receipt_strict_first_parent_and_sibling(self):
        temp,repo=source_copy()
        try:
            f=synthetic_push_issuer(repo)
            git(repo,"checkout","-B","sandbox/"+TRIAL,f["auth"])
            candidates=[]
            for row in f["rows"][:2]:
                appid=row["appid"]
                assignment=v2.frozen_assignment(repo,marker_commit=f["marker"],
                                                 trial_id=TRIAL,appid=appid)
                candidate={
                    "schema":"DOSSIER-RESEARCH-NOTES-V2","schema_version":2,
                    "assignment":assignment,"research_status":"limited_evidence",
                    "notes_text":"Synthetic balanced public opinion, no personal text."
                }
                commit=add(repo,v2._path("research",assignment),candidate,
                           "fixture owner GitHub connector create_file")
                candidates.append((appid,assignment,commit))
            with tempfile.TemporaryDirectory() as d:
                payload=Path(d)/"push.json"
                for appid,assignment,commit in candidates:
                    ref="refs/heads/sandbox/"+TRIAL
                    doc=event_document(ref,parent(repo,commit),commit)
                    payload.write_text(json.dumps(doc))
                    env=common_env(ingest.AUTO_WORKFLOW,ref,commit,payload)
                    self.assertEqual(ingest._owner_push_candidate_gate(repo,TRIAL,env),
                                     v2._path("research",assignment))
                    for change in ({"GITHUB_ACTOR_ID":"4"},{"GITHUB_RUN_ATTEMPT":"2"},
                                   {"GITHUB_WORKFLOW_REF":"fake"},
                                   {"GITHUB_REF":"refs/heads/main"}):
                        with self.subTest(change=change),self.assertRaises(ValueError):
                            ingest._owner_push_candidate_gate(repo,TRIAL,{**env,**change})
                    doc["forced"]=True
                    payload.write_text(json.dumps(doc))
                    with self.assertRaises(ValueError):
                        ingest._owner_push_candidate_gate(repo,TRIAL,env)
                result=ingest.ingest_local(repo,trial_id=TRIAL,
                                          anchor=ingest.issuer_from_sandbox(repo,TRIAL))
                self.assertEqual(result["receipts_created"],2,result)
                self.assertEqual(ingest.ingest_local(
                    repo,trial_id=TRIAL,
                    anchor=ingest.issuer_from_sandbox(repo,TRIAL))["receipts_created"],0)
                appid,assignment,commit=candidates[0]
                ref="refs/heads/sandbox/"+TRIAL
                payload.write_text(json.dumps(
                    event_document(ref,parent(repo,commit),commit)))
                env=common_env(ingest.AUTO_WORKFLOW,ref,commit,payload)
                self.assertEqual(ingest._owner_push_candidate_gate(repo,TRIAL,env),
                                 v2._path("research",assignment))
                p=receipts.require_batch_research_receipt(
                    repo,marker_commit=f["marker"],trial_id=TRIAL,appid=appid,
                    authorization_commit=f["auth"],research_commit=commit)
                self.assertEqual(len(p),40)
                other=v2.assembly_work(repo,marker_commit=f["marker"],
                           trial_id=TRIAL,appid=candidates[1][0],
                           research_commit=candidates[1][2])
                self.assertEqual(other["status"],"ready_for_autonomous_assembly")
        finally:
            temp.cleanup()

    def test_no_arbitrary_push_workflows_or_retry_loop(self):
        root=Path(__file__).resolve().parents[1]
        issuer_yaml=(root/batch.OWNER_PUSH_WORKFLOW).read_text()
        receipt_yaml=(root/ingest.AUTO_WORKFLOW).read_text()
        self.assertIn("on:\n  push:\n    branches:\n      - main",issuer_yaml)
        self.assertIn("config/dossier_notes_v2_batches/"+TRIAL+".json",issuer_yaml)
        self.assertIn("on:\n  push:\n    branches:\n      - sandbox/"+TRIAL,receipt_yaml)
        self.assertIn("cancel-in-progress: false",receipt_yaml)
        self.assertIn("contents: write",receipt_yaml)
        self.assertNotIn("schedule:",issuer_yaml+receipt_yaml)
        self.assertNotIn("pull_request:",issuer_yaml+receipt_yaml)
        self.assertNotIn("workflow_dispatch:",issuer_yaml+receipt_yaml)


if __name__=="__main__":
    unittest.main()
