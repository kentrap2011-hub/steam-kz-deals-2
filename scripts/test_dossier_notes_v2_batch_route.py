#!/usr/bin/env python3
"""Offline regression against ACTUAL reusable V2 issuer, transport and strict writer.

All Git history and evidence are synthetic disposable test fixtures. These tests
never authorize owner workflows, research real games or touch canonical caches.
"""
import copy
import itertools
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
import dossier_notes_v2_batch_preflight as scope
import dossier_notes_v2_batch_route as batch
import dossier_notes_v2_batch_issuer as issuer
import dossier_notes_v2_batch_pilot as pilot
import dossier_notes_v2_per_item_receipts as receipts
import dossier_research_notes_v2 as v2
from dossier_two_stage_staging import blob, parent


def git(repo,*args):
    p=subprocess.run(["git","-C",str(repo),*args],capture_output=True,text=True,check=True)
    return p.stdout.strip()


def add(repo, path, doc, message):
    target=Path(repo)/path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(batch.canonical(doc) if type(doc) is dict else doc)
    git(repo,"add","--",path)
    git(repo,"commit","-m",message)
    return git(repo,"rev-parse","HEAD")


def source_copy():
    temp=tempfile.TemporaryDirectory(prefix="notes-v2-reusable-")
    repo=Path(temp.name)/"sandbox"
    subprocess.run(["git","clone","--quiet","--shared",str(ROOT),str(repo)],
                   check=True,capture_output=True)
    git(repo,"config","user.name","synthetic")
    git(repo,"config","user.email","synthetic@example.invalid")
    git(repo,"checkout","-b","fixture/batch")
    return temp,repo


def synthetic_issuer(repo,trial_id,run_id="1234567"):
    bp=batch.manifest_blueprint(repo,trial_id)
    ps=batch.paths(trial_id)
    base=git(repo,"rev-parse","HEAD")
    grant=add(repo,ps["grant"],batch.expected_grant(repo,trial_id,base),
              "fixture: GitHub-only one-use grant")
    manifest=add(repo,ps["manifest"],bp["bytes"],
                 "fixture: immutable cohort manifest")
    nonce="ca" * 16
    marker=add(repo,"data/control/dossier_notes_v2/run_starts/"+nonce+".json",
               {"schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,
                "trial_id":trial_id,"nonce":nonce},
               "fixture: one-add nonce marker")
    authorization=add(repo,ps["authorization"],
                      batch.expected_authorization(repo,trial_id,marker,grant,run_id),
                      "fixture: separate owner Actions authorization")
    return {"base":base,"grant":grant,"manifest":manifest,
            "marker":marker,"auth":authorization,"rows":batch.rows(repo,trial_id)}


class ReusableBatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp,cls.repo=source_copy()
        cls.trial="dossier-notes-v2-fresh6-20261111-first"
        cls.fixture=synthetic_issuer(cls.repo,cls.trial)
        cls.ids=[x["appid"] for x in cls.fixture["rows"]]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_first_six_exact_titles_editions_pins_and_auth_chain(self):
        self.assertEqual(self.ids,
            ["1000010","102600","1029690","49520","499180","501590"])
        self.assertEqual([x["title"] for x in self.fixture["rows"]][-2:],
            ["Braid, Anniversary Edition","Bulletstorm: Full Clip Edition"])
        self.assertEqual(len({r["assignment_id"] for r in self.fixture["rows"]}),6)
        self.assertEqual(parent(self.repo,self.fixture["marker"]),self.fixture["manifest"])
        self.assertEqual(parent(self.repo,self.fixture["auth"]),self.fixture["marker"])
        anchor=batch.issuer_structure(self.repo,trial_id=self.trial,
            marker_commit=self.fixture["marker"],authorization_commit=self.fixture["auth"])
        self.assertTrue(anchor["semantic_execution_authorized"])
        self.assertFalse(anchor["github_run_authenticated"])
        self.assertEqual(anchor["manifest_blob_sha"],
                         batch.manifest_blueprint(self.repo,self.trial)["blob_sha"])
        manifest,sha=v2._manifest(self.repo,self.fixture["marker"],self.trial)
        self.assertEqual(manifest["items"],self.fixture["rows"])
        self.assertEqual(sha,anchor["manifest_blob_sha"])
        r=receipts.issuer_structure(self.repo,marker_commit=self.fixture["marker"],
             trial_id=self.trial,authorization_commit=self.fixture["auth"])
        self.assertEqual(r["authorization_commit"],self.fixture["auth"])

    def test_second_independent_batch_requires_no_code_changes_1_of_n(self):
        temp,repo=source_copy()
        try:
            trial="dossier-notes-v2-independent2-test-20261112"
            c=copy.deepcopy(batch.scope(repo,self.trial))
            c["trial_id"]=trial
            c["proposed_sandbox_branch"]="sandbox/"+trial
            c["candidates"]=c["candidates"][3:4]
            c["provenance"]["group_descriptors"]=c["provenance"]["group_descriptors"][1:2]
            add(repo,batch.paths(trial)["contract"],c,"fixture: second GitHub-reviewed cohort data")
            self.assertEqual(batch.scope(repo,trial)["trial_id"],trial)
            issuer2=synthetic_issuer(repo,trial)
            self.assertEqual(len(issuer2["rows"]),1)
            self.assertEqual(issuer2["rows"][0]["appid"],"49520")
            self.assertNotEqual(issuer2["rows"][0]["assignment_id"],
                                self.fixture["rows"][3]["assignment_id"])
            anchor=batch.issuer_structure(repo,trial_id=trial,
                marker_commit=issuer2["marker"],authorization_commit=issuer2["auth"])
            self.assertEqual(anchor["trial_id"],trial)
            m,_=v2._manifest(repo,issuer2["marker"],trial)
            self.assertEqual([x["appid"] for x in m["items"]],["49520"])
            with self.assertRaises(v2.NotesV2Error):
                v2.frozen_assignment(repo,marker_commit=issuer2["marker"],
                                     trial_id=trial,appid="499180")
            # A one-off freeze helper and a hardcoded allowlist would fail this test.
            self.assertEqual(git(repo,"status","--porcelain"),"")
        finally:
            temp.cleanup()

    def test_partial_group_batch_two_of_three_immutable_identity(self):
        temp,repo=source_copy()
        try:
            trial="dossier-notes-v2-independent3-test-20261112"
            c=copy.deepcopy(batch.scope(repo,self.trial))
            c["trial_id"]=trial
            c["proposed_sandbox_branch"]="sandbox/"+trial
            c["candidates"]=c["candidates"][:2]
            c["provenance"]["group_descriptors"]=c["provenance"]["group_descriptors"][:1]
            add(repo,batch.paths(trial)["contract"],c,"fixture: partial group")
            self.assertEqual([r["appid"] for r in batch.rows(repo,trial)],
                             ["1000010","102600"])
            with self.assertRaises(ValueError):
                bad=copy.deepcopy(c)
                bad["candidates"][1]["title"]="Wrong Edition"
                scope.validate_scope(bad,*self._prepared(repo,trial),scope.policy(repo))
        finally:
            temp.cleanup()

    @staticmethod
    def _prepared(repo, trial_id):
        c=batch.scope(repo,trial_id)
        pin=c["provenance"]
        base=pin["main_commit"]
        index=scope.parse_json(scope.read_pinned(
             repo,base,pin["worker_index_path"],pin["worker_index_blob_sha"]),"index")
        docs={g["sequence"]:scope.parse_json(scope.read_pinned(
             repo,base,g["path"],g["blob_sha"]),"descriptor")
             for g in pin["group_descriptors"]}
        old=json.loads(git(repo,"show",base+":config/dossier_research_notes_v2_contract.json"))
        return index,docs,old

    def test_reject_original18_marker_and_offscope_AppID(self):
        with self.assertRaises((ValueError,v2.NotesV2Error)):
            batch.issuer_structure(self.repo,trial_id=self.trial,
                marker_commit="bb63cc291eba5aa8fc56e2920ef84d131ac28a4f",
                authorization_commit=self.fixture["auth"])
        with self.assertRaises((ValueError,v2.NotesV2Error)):
            batch.issuer_structure(self.repo,trial_id=self.trial,
                marker_commit=self.fixture["marker"],authorization_commit=self.fixture["marker"])
        with self.assertRaises(v2.NotesV2Error):
            v2.frozen_assignment(self.repo,marker_commit=self.fixture["marker"],
                 trial_id=self.trial,appid="2138710")
        with self.assertRaises(ValueError):
            batch.paths("dossier-notes-v2-original18-first")
        with self.assertRaises(ValueError):
            batch.paths("../../data/cache")
        with self.assertRaises(ValueError):
            batch.paths("dossier-notes-v2-INVALID")

    def test_forged_source_grant_and_immutable_assignment_drift_refused(self):
        fixture=self.fixture
        # A non-committed edit cannot change frozen semantic scope.
        path=self.repo/batch.paths(self.trial)["contract"]
        original=path.read_bytes()
        try:
            modified=json.loads(original)
            modified["candidates"][4]["title"]="Braid"
            path.write_bytes(batch.canonical(modified))
            with self.assertRaises((ValueError,v2.NotesV2Error)):
                batch.issuer_structure(self.repo,trial_id=self.trial,
                    marker_commit=fixture["marker"],authorization_commit=fixture["auth"])
        finally:
            path.write_bytes(original)
        with self.assertRaises((ValueError,v2.NotesV2Error)):
            batch.issuer_structure(self.repo,trial_id=self.trial,
                marker_commit=fixture["marker"],authorization_commit=fixture["grant"])

    def test_real_owner_run_api_required_fake_actor_run_head_path_attempt_refused(self):
        f=self.fixture
        anchor=batch.issuer_structure(self.repo,trial_id=self.trial,
            marker_commit=f["marker"],authorization_commit=f["auth"])
        event={"id":1234567,"event":"workflow_dispatch","head_branch":"main",
               "status":"completed","conclusion":"success","run_attempt":1,
               "path":batch.AUTHORIZE_WORKFLOW,
               "actor":{"id":int(batch.OWNER_ID),"login":batch.OWNER_LOGIN},
               "head_sha":f["base"],
               "display_title":"Authorize isolated Notes V2 batch "
                               + self.trial + " marker " + f["marker"]}
        with patch.object(receipts,"_github_get",return_value=event):
            self.assertTrue(receipts.verify_scoped_semantic_run(self.repo,
                marker_commit=f["marker"],trial_id=self.trial,
                authorization_commit=f["auth"],
                github_repository=batch.REPOSITORY,github_token="mock-no-network")["github_run_authenticated"])
        for change in (
            {"actor":{"id":1,"login":"forger"}},{"run_attempt":2},{"event":"push"},
            {"path":"wrong_workflow.yml"},{"head_branch":"sandbox/forged"},
            {"status":"in_progress"},{"conclusion":"failure"},{"head_sha":"fake"},
            {"display_title":"Authorize isolated Notes V2 batch another marker "+f["marker"]},
        ):
            with self.subTest(change=change):
                with patch.object(receipts,"_github_get",return_value={**event,**change}):
                    with self.assertRaises(ValueError):
                        batch.authenticated_owner_run(anchor,"mock-no-network")
        with self.assertRaises(ValueError):
            batch.authenticated_owner_run(anchor,None)

    def test_transport_wrong_branch_and_writer_canonical_path_refused(self):
        exact=batch.paths(self.trial)["branch"]
        receipts._require_batch_target(self.repo,self.trial,exact)
        with self.assertRaises(v2.NotesV2Error):
            receipts._require_batch_target(self.repo,self.trial,
                                             "sandbox/dossier-notes-v2-original18-first")
        from taste_steam_review_dossier_buffered import drain_buffered_groups
        opts={"repo":self.repo,"marker_commit":self.fixture["marker"],
              "trial_id":self.trial,"item_commits":{},
              "store_dir":self.repo/"data/cache/taste_steam_review_dossiers",
              "accepted_dir":self.repo/"data/control/dossier_notes_v2/canonical_accepted",
              "offline_fixture":False,"trial_sandbox":True}
        with self.assertRaises(ValueError):
            drain_buffered_groups(notes_v2=opts)

    def test_actual_bash_manual_mode_matrix(self):
        yaml=(ROOT/".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml").read_text()
        shell=yaml.split("      - name: Reject ambiguous manual V2 writer selections",1)[1].split(
            "      - name: Drain separately authorized V2 items",1)[0].split("        run: |\n",1)[1]
        for flags in itertools.product(("false","true"),repeat=3):
            with self.subTest(flags=flags):
                proc=subprocess.run(["bash","-euc",textwrap.dedent(shell)],
                    env={**os.environ,"CANONICAL_WRITER":flags[0],"PILOT_WRITER":flags[1],
                         "BATCH_WRITER":flags[2]},
                    capture_output=True,text=True)
                self.assertEqual(proc.returncode==0,flags.count("true")==1,
                    proc.stdout+"\n"+proc.stderr)

    def test_exact_sandbox_isolation_mixed_strict_ready_and_incomplete(self):
        from taste_steam_review_dossier_test_fixture import web_dossier
        from taste_steam_review_dossier_buffered import drain_buffered_groups
        f=self.fixture
        # Reuse the disposable issuer clone where its Git commits exist.
        repo=self.repo
        try:
            git(repo,"checkout","-B",batch.paths(self.trial)["branch"],f["auth"])
            first,second=f["rows"][:2]
            entries={}
            for item in (first,second):
                a=v2.frozen_assignment(repo,marker_commit=f["marker"],
                                       trial_id=self.trial,appid=item["appid"])
                doc={"schema":"DOSSIER-RESEARCH-NOTES-V2","schema_version":2,
                     "assignment":a,"notes_text":"","source_log":[],
                     "research_status":"no_verifiable_findings"}
                entries[item["appid"]]={"research_commit":add(repo,v2._path("research",a),doc,
                                          "fixture Research "+item["appid"]),
                                         "assembly_commit":None}
            w=v2.assembly_work(repo,marker_commit=f["marker"],trial_id=self.trial,
                  appid=first["appid"],research_commit=entries[first["appid"]]["research_commit"])
            dossier=web_dossier(first["appid"],datetime.now(timezone.utc),title=first["title"])
            with self.assertRaises(v2.NotesV2Error):
                v2.candidate_assembly(w,outcome="invented_assembly_enum",
                                      diagnostic="synthetic invalid terminal")
            ready=v2.candidate_assembly(w,outcome="assembled_candidate_ready",final_dossier=dossier)
            entries[first["appid"]]["assembly_commit"]=add(repo,w["output_path"],ready,"fixture strict")
            w=v2.assembly_work(repo,marker_commit=f["marker"],trial_id=self.trial,
                  appid=second["appid"],research_commit=entries[second["appid"]]["research_commit"])
            incomplete=v2.candidate_assembly(w,outcome="assembly_missing_evidence",
                         diagnostic="Synthetic unavailable independent evidence")
            entries[second["appid"]]["assembly_commit"]=add(repo,w["output_path"],incomplete,"fixture incomplete")
            ps=batch.paths(self.trial)
            env={
                "GITHUB_ACTIONS":"true","GITHUB_EVENT_NAME":"workflow_dispatch",
                "GITHUB_REF":"refs/heads/main",
                "GITHUB_WORKFLOW_REF":batch.REPOSITORY+"/"+batch.WRITER_WORKFLOW+"@refs/heads/main",
                "GITHUB_REPOSITORY":batch.REPOSITORY,
                "GITHUB_ACTOR_ID":batch.OWNER_ID,"GITHUB_REPOSITORY_OWNER_ID":batch.OWNER_ID,
                "GITHUB_ACTOR":batch.OWNER_LOGIN,"GITHUB_TRIGGERING_ACTOR":batch.OWNER_LOGIN,
                "GITHUB_RUN_ATTEMPT":"1","GITHUB_RUN_ID":"2233445566",
                "GITHUB_TOKEN":"synthetic-only"}
            opts={"repo":repo,"marker_commit":f["marker"],"trial_id":self.trial,
                  "item_commits":entries,"store_dir":repo/ps["store"],
                  "accepted_dir":repo/ps["accepted"],
                  "offline_fixture":False,"trial_sandbox":True}
            with patch.dict(os.environ,env),patch.object(batch,"authenticated_owner_run",return_value=True):
                done=drain_buffered_groups(notes_v2=opts)
            by={x["appid"]:x for x in done["items"]}
            self.assertEqual(len(by),6)
            self.assertEqual(by[first["appid"]]["status"],"persisted_pending_github_commit")
            self.assertEqual(by[second["appid"]]["status"],"invalid")
            self.assertTrue(all(x["status"]=="missing" for x in done["items"][2:]))
            self.assertFalse(done["canonical_acceptance"])
            self.assertTrue((repo/ps["store"]/("App_"+first["appid"]+".json")).is_file())
            self.assertFalse((repo/ps["store"]/("App_"+second["appid"]+".json")).exists())
            receipt=repo/ps["accepted"]/self.trial/f"g{first['group_sequence']:06d}"/(
                first["appid"]+"--"+first["assignment_id"]+".json")
            self.assertTrue(receipt.is_file())
            git(repo,"add","--",ps["store"],ps["accepted"])
            staged=git(repo,"diff","--cached","--name-only").splitlines()
            self.assertEqual(len(staged),2)
            self.assertTrue(all(x.startswith("data/control/dossier_notes_v2/batch_pilot_") for x in staged))
            git(repo,"commit","-m","fixture: accepted one strict batch item")
            with patch.dict(os.environ,env),patch.object(batch,"authenticated_owner_run",return_value=True):
                repeated=drain_buffered_groups(notes_v2=opts)
            self.assertEqual(repeated["items"][0]["status"],"already_persisted_same_binding")
            self.assertEqual(git(repo,"status","--porcelain"),"")
        finally:
            git(repo,"checkout","fixture/batch")

    def test_two_manual_owner_dispatches_no_reissue_disposable_remote(self):
        with tempfile.TemporaryDirectory(prefix="batch-owner-issuer-") as tmp:
            origin=Path(tmp)/"origin.git"
            repo=Path(tmp)/"work"
            subprocess.run(["git","init","--bare","--quiet",str(origin)],check=True,capture_output=True)
            subprocess.run(["git","clone","--quiet","--shared",str(ROOT),str(repo)],
                           check=True,capture_output=True)
            git(repo,"config","user.name","fixture")
            git(repo,"config","user.email","fixture@example.invalid")
            git(repo,"remote","set-url","origin",str(origin))
            git(repo,"checkout","-B","main")
            base=git(repo,"rev-parse","HEAD")
            git(repo,"push","origin","HEAD:refs/heads/main")
            result=issuer.freeze(repo,base,self.trial)
            self.assertFalse(result["semantic_execution_authorized"])
            with self.assertRaises(ValueError):
                issuer.freeze(repo,base,self.trial)
            git(repo,"checkout","main")
            result2=issuer.authorize(repo,base,self.trial,result["marker_commit"],
                                    {"GITHUB_RUN_ID":"22334455"})
            self.assertTrue(result2["semantic_execution_authorized"])
            self.assertEqual(git(repo,"ls-remote","origin",
                "refs/heads/"+batch.paths(self.trial)["branch"]).split()[0],
                result2["authorization_commit"])
            git(repo,"checkout","main")
            with self.assertRaises(ValueError):
                issuer.authorize(repo,base,self.trial,result["marker_commit"],
                                 {"GITHUB_RUN_ID":"22334456"})
            fake={
                "GITHUB_ACTIONS":"true","GITHUB_EVENT_NAME":"workflow_dispatch",
                "GITHUB_REPOSITORY":batch.REPOSITORY,
                "GITHUB_REPOSITORY_OWNER_ID":batch.OWNER_ID,
                "GITHUB_ACTOR_ID":batch.OWNER_ID,
                "GITHUB_ACTOR":batch.OWNER_LOGIN,
                "GITHUB_TRIGGERING_ACTOR":batch.OWNER_LOGIN,
                "GITHUB_REF":"refs/heads/main",
                "GITHUB_WORKFLOW_REF":batch.REPOSITORY+"/"+batch.ISSUE_WORKFLOW+"@refs/heads/main",
                "GITHUB_SHA":base,
                "GITHUB_RUN_ATTEMPT":"1","GITHUB_RUN_ID":"123456"}
            with self.assertRaisesRegex(ValueError,"noncanonical GitHub remote"):
                issuer.guard(repo,"freeze",self.trial,base,
                             issuer.FREEZE_CONFIRM+self.trial,fake)

    def test_owner_guard_stale_main_actor_attempt_and_confirmation_fail_closed(self):
        temp,repo=source_copy()
        try:
            git(repo,"checkout","-B","main")
            sha=git(repo,"rev-parse","HEAD")
            git(repo,"remote","set-url","origin","https://github.com/"+batch.REPOSITORY+".git")
            env={
                "GITHUB_ACTIONS":"true","GITHUB_EVENT_NAME":"workflow_dispatch",
                "GITHUB_REPOSITORY":batch.REPOSITORY,
                "GITHUB_REPOSITORY_OWNER_ID":batch.OWNER_ID,
                "GITHUB_ACTOR_ID":batch.OWNER_ID,
                "GITHUB_ACTOR":batch.OWNER_LOGIN,
                "GITHUB_TRIGGERING_ACTOR":batch.OWNER_LOGIN,
                "GITHUB_REF":"refs/heads/main",
                "GITHUB_WORKFLOW_REF":batch.REPOSITORY+"/"+batch.ISSUE_WORKFLOW+"@refs/heads/main",
                "GITHUB_SHA":sha,
                "GITHUB_RUN_ATTEMPT":"1","GITHUB_RUN_ID":"99887766"}
            confirm=issuer.FREEZE_CONFIRM+self.trial
            with patch.object(issuer,"remote",return_value=sha):
                issuer.guard(repo,"freeze",self.trial,sha,confirm,env)
                with self.assertRaises(ValueError):
                    issuer.guard(repo,"freeze",self.trial,"0"*40,confirm,env)
                with self.assertRaises(ValueError):
                    issuer.guard(repo,"freeze",self.trial,sha,confirm,{**env,"GITHUB_ACTOR_ID":"4"})
                with self.assertRaises(ValueError):
                    issuer.guard(repo,"freeze",self.trial,sha,confirm,{**env,"GITHUB_RUN_ATTEMPT":"2"})
                with self.assertRaises(ValueError):
                    issuer.guard(repo,"freeze",self.trial,sha,confirm+"again",env)
                with self.assertRaises(ValueError):
                    issuer.guard(repo,"authorize",self.trial,sha,
                                 issuer.AUTH_CONFIRM+self.trial,env)
            with patch.object(issuer,"remote",return_value="1"*40):
                with self.assertRaises(ValueError):
                    issuer.guard(repo,"freeze",self.trial,sha,confirm,env)
        finally:
            temp.cleanup()

    def test_reject_wrong_descriptor_blob_original18_and_unbounded_cohort(self):
        temp,repo=source_copy()
        try:
            c=batch.scope(repo,self.trial)
            index,docs,original=self._prepared(repo,self.trial)
            policy=scope.policy(repo)
            bad=copy.deepcopy(c)
            bad["candidates"]=bad["candidates"]*5
            with self.assertRaises(ValueError):
                scope.validate_scope(bad,index,docs,original,policy)
            bad=copy.deepcopy(c)
            bad["candidates"][0]["appid"]="2124120"
            with self.assertRaises(ValueError):
                scope.validate_scope(bad,index,docs,original,policy)
            bad=copy.deepcopy(c)
            bad["provenance"]["group_descriptors"][0]["blob_sha"]="a"*40
            path=repo/batch.paths(self.trial)["contract"]
            raw=path.read_bytes()
            try:
                path.write_bytes(batch.canonical(bad))
                with self.assertRaises(ValueError):
                    batch.scope(repo,self.trial)
            finally:
                path.write_bytes(raw)
            # The original cohort remains byte-for-byte equal to the reviewed contract.
            self.assertEqual(batch.scope(repo,self.trial),c)
        finally:
            temp.cleanup()

    def test_no_authority_from_contract_flags(self):
        c=batch.scope(self.repo,self.trial)
        p=scope.policy(self.repo)
        self.assertTrue(all(c[k] is False for k in scope.OFF_FLAGS))
        self.assertFalse(p["production_enabled"])
        self.assertFalse(p["automatic_retry"])
        self.assertFalse(p["active"])


if __name__=="__main__":
    unittest.main()
