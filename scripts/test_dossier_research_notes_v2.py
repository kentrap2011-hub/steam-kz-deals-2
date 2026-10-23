#!/usr/bin/env python3
"""Synthetic adversarial Notes V2 proofs. No real Research/Assembly or GitHub writes."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import dossier_research_notes_v2 as v2
import dossier_two_stage_versioned as versions

C = json.loads(v2.CONTRACT_PATH.read_text(encoding="utf-8"))
TRIAL = "notes-v2-shadow-calibration-20261021"
NONCE = "a" * 32

def run(repo, *args):
    p = subprocess.run(["git","-C",str(repo),*args],check=True,
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return p.stdout.decode().strip()

def write(repo, path, doc):
    target=repo/path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(doc,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n",
                      encoding="utf-8")

def commit(repo, message):
    run(repo,"add","-A")
    run(repo,"commit","-m",message)
    return run(repo,"rev-parse","HEAD")

class NotesV2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo=Path(self.tmp.name)
        run(self.repo,"init","-q")
        run(self.repo,"config","user.name","Synthetic Fixture")
        run(self.repo,"config","user.email","synthetic@example.invalid")
        # Exact historical title, edition qualifier, Research assignment and
        # original work SHA are anchored by the authentic original Git blob.
        rows=copy.deepcopy(v2._original_rows())
        self.manifest={"schema":"DOSSIER-NOTES-V2-FROZEN-MANIFEST",
                       "schema_version":2,"trial_id":TRIAL,
                       "original_pins":C["immutable_original_pins"],"items":rows}
        write(self.repo,f"data/control/dossier_notes_v2/manifests/{TRIAL}.json",self.manifest)
        self.initial=commit(self.repo,"fixture: frozen manifest")
        write(self.repo,f"data/control/dossier_notes_v2/run_starts/{NONCE}.json",
              {"schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,
               "nonce":NONCE,"trial_id":TRIAL})
        self.marker=commit(self.repo,"fixture: create-only marker")
        self.appid="2124120"
        self.assignment=v2.frozen_assignment(self.repo,marker_commit=self.marker,
                                               trial_id=TRIAL,appid=self.appid)

    def note(self, **updates):
        doc={"schema":"DOSSIER-RESEARCH-NOTES-V2","schema_version":2,
             "assignment":copy.deepcopy(self.assignment),"notes_text":"",
             "source_log":[],"research_status":"no_verifiable_findings"}
        doc.update(updates)
        return doc

    def add_research(self, doc=None, extra_file=False):
        doc=doc if doc is not None else self.note()
        path=v2._path("research",self.assignment)
        write(self.repo,path,doc)
        if extra_file:
            write(self.repo,"unexpected-extra.json",{"bad":True})
        return commit(self.repo,"fixture: submitted Research")

    def work(self, doc=None):
        sha=self.add_research(doc)
        return sha,v2.assembly_work(self.repo,marker_commit=self.marker,
                                    trial_id=TRIAL,appid=self.appid,research_commit=sha)

    def test_zero_evidence_research_passes_without_year_sources_or_dimensions(self):
        p=v2.prepare_research(self.repo,marker_commit=self.marker,trial_id=TRIAL,
                              appid=self.appid,document=self.note())
        self.assertEqual(p["status"],"ready_for_create_only_submission")
        sha=self.add_research()
        d=v2.submitted_research(self.repo,marker_commit=self.marker,trial_id=TRIAL,
                               appid=self.appid,introduction_commit=sha)
        self.assertEqual(d["status"],"safe_incomplete_research")
        w=v2.assembly_work(self.repo,marker_commit=self.marker,trial_id=TRIAL,
                           appid=self.appid,research_commit=sha)
        self.assertEqual(w["status"],"ready_for_autonomous_assembly")
        self.assertTrue(w["may_independently_discover"])

    def test_SULFUR_role_conflict_is_stage2_problem_not_transport_rejection(self):
        doc=self.note(notes_text="SULFUR identity source role labeled current_state; identity uncertain",
                      unknowns_text="true identity corroboration absent")
        sha,work=self.work(doc)
        self.assertEqual(work["status"],"ready_for_autonomous_assembly")
        terminal=v2.candidate_assembly(work,outcome="assembly_missing_evidence",
                 operations=[{"kind":"identity_disambiguation","access":"search_result_only",
                              "summary":"Not verified as product identity"}],
                 diagnostic="identity source not independently confirmed")
        self.assertIsNone(terminal["final_dossier"])

    def test_Sifu_www_hostname_and_year_contradiction_pass_notes(self):
        self.appid="2138710"
        self.assignment=v2.frozen_assignment(self.repo,marker_commit=self.marker,
                                               trial_id=TRIAL,appid=self.appid)
        doc=self.note(notes_text="Sifu original year 2022 conflicts with old 2023 claim",
                      conflicts_text="Newly verify original work year, not original Research authority",
                      source_log=[{"locator":{"url":"https://www.sifugame.com/news"},
                                   "access":"unvisited_reference","observation":"unverified link"}],
                      research_status="limited_evidence")
        sha,work=self.work(doc)
        self.assertEqual(work["status"],"ready_for_autonomous_assembly")
        self.assertEqual(work["assignment"]["appid"],"2138710")

    def test_reject_private_locator_and_review_material(self):
        for url in ("http://example.org/reviews","https://127.0.0.1",
                    "https://10.0.0.1/reviews","https://example.org/profile/123456",
                    "https://example.org/?token=abc","https://user:pass@example.org",
                    "https://example.org:8080"):
            with self.subTest(url=url):
                doc=self.note(source_log=[{"locator":{"url":url},"access":"opened",
                                           "observation":"neutral"}])
                with self.assertRaises(v2.NotesV2Error):
                    v2.validate_notes(doc,self.assignment)
        doc=self.note(**{"raw_reviews":"Do not persist player bodies"})
        with self.assertRaises(v2.NotesV2Error): v2.validate_notes(doc,self.assignment)

    def test_wrong_appid_marker_manifest_blob_are_rejected(self):
        for key,value in (("appid","1"),("marker_commit","0"*40),("manifest_blob_sha","0"*40)):
            d=self.note()
            d["assignment"][key]=value
            with self.subTest(key=key),self.assertRaises(v2.NotesV2Error) as ctx:
                v2.validate_notes(d,self.assignment)
            self.assertEqual(ctx.exception.code,"wrong_binding")

    def test_missing_research_transport_does_not_claim_exhaustion_or_attempt(self):
        row=v2.assembly_work(self.repo,marker_commit=self.marker,trial_id=TRIAL,
                             appid=self.appid,research_commit=None)
        self.assertEqual(row["status"],"missing_research_transport")
        self.assertEqual(row["attempt_state"],"unknown")

    def test_one_add_git_proof_and_overwrite(self):
        sha=self.add_research(extra_file=True)
        out=v2.classify_research(self.repo,marker_commit=self.marker,trial_id=TRIAL,
                                 appid=self.appid,introduction_commit=sha)
        self.assertEqual(out["status"],"broken_git_provenance")
        self.assertFalse(out["canonical_acceptance"])

    def test_same_invocation_correction_cap_and_independent_operations(self):
        _,work=self.work()
        ops=[{"kind":"independent_discovery","access":"opened","summary":"New public independent source"}]
        d=v2.candidate_assembly(work,outcome="assembly_missing_evidence",
             operations=ops,diagnostic="Missing verified player reviews")
        self.assertEqual(d["operations"][0]["kind"],"independent_discovery")
        for kind in ("format","reference","normalization"):
            corrections=[{"kind":kind,"summary":"mechanical change"}]*3
            with self.assertRaises(v2.NotesV2Error):
                v2.candidate_assembly(work,outcome="assembly_technical_error",
                                      diagnostic="not enough",mechanical_corrections=corrections)

    def test_runtime_interruption_is_not_semantic_insufficiency(self):
        _,work=self.work()
        for status in ("runtime_or_tool_interrupted","assembly_semantic_conflict",
                       "assembly_missing_evidence","assembly_technical_error"):
            d=v2.candidate_assembly(work,outcome=status,diagnostic="synthetic scenario")
            self.assertEqual(d["outcome"],status)
            self.assertFalse(d["canonical_acceptance"])

    def test_strict_final_rejects_incomplete_dossier(self):
        sha,work=self.work()
        d=v2.candidate_assembly(work,outcome="assembled_candidate_ready",
                                 final_dossier={"appid":self.appid,"title":self.assignment["title"]})
        write(self.repo,work["output_path"],d)
        result_commit=commit(self.repo,"fixture: final invalid dossier")
        outcome=v2.inspect_assembly(self.repo,marker_commit=self.marker,trial_id=TRIAL,
                                    appid=self.appid,research_commit=sha,result_commit=result_commit)
        self.assertEqual(outcome["status"],"final_strict_or_group_rejected")

    def test_frozen_order_survives_two_sequential_publishes(self):
        order=["1517180","1533420","1590230"]
        states1={"1517180":"ready","1533420":"ready","1590230":"ready"}
        states2={"1517180":"candidate_already_submitted","1533420":"ready","1590230":"ready"}
        v2.checked_typed_publish_prefix(order,order[:1],"1517180",states1)
        p=v2.checked_typed_publish_prefix(order,order[:2],"1533420",states2)
        self.assertEqual(p["validated_typed_prefix"],order[:2])
        for typed,target,states in ((order[:2],"1517180",states2),
                                    (["1533420","1517180"],"1533420",states1),
                                    (["1517180","1517180"],"1533420",states1)):
            with self.subTest(typed=typed,target=target),self.assertRaises(v2.NotesV2Error):
                v2.checked_typed_publish_prefix(order,typed,target,states)

    def test_immutable_original_eighteen_and_atomic_group_readiness(self):
        self.assertEqual([g["group_sequence"] for g in C["original_groups"]],[3,8,13,15,18,20])
        all_appids=[a for g in C["original_groups"] for a in g["appids"]]
        self.assertEqual(len(all_appids),18)
        self.assertEqual(len(set(all_appids)),18)
        self.assertEqual(v2._original_rows()[1]["title"],"Mindcop")
        self.assertEqual(v2._original_rows()[12]["title"],"Saints Row IV: Re-Elected")
        group=C["original_groups"][0]
        full={a:"strict_item_valid_pending_existing_atomic_group_ingest" for a in group["appids"]}
        self.assertTrue(v2.original_group_readiness(3,full)["strict_three_ready"])
        full.pop(group["appids"][-1])
        self.assertFalse(v2.original_group_readiness(3,full)["strict_three_ready"])

    def test_reviewer_usernames_alone_cannot_establish_authority(self):
        roles={r:{"login":"example"+r,"github_id":i+100,
                  "appointment_ref":"immutable-owner-confirmation-"+r}
               for i,r in enumerate(("A","B","C"))}
        with self.assertRaises(v2.NotesV2Error):
            v2.verify_independent_reviewers(roles,None,None)
        lookup=lambda login:{"login":login,"id":roles[login[-1]]["github_id"]}
        approval=lambda role,gid,ref: ref.endswith(role)
        self.assertTrue(v2.verify_independent_reviewers(roles,lookup,approval))
        roles["B"]["github_id"]=roles["A"]["github_id"]
        with self.assertRaises(v2.NotesV2Error):
            v2.verify_independent_reviewers(roles,lookup,approval)

    def test_version_dispatch_refuses_unknown_or_implicit_v1_rebinding(self):
        with self.assertRaises(ValueError):
            versions.prepare_research_versioned("DOSSIER-RESEARCH-PACKAGE-V3")
        d=self.note()
        p=versions.prepare_research_versioned("DOSSIER-RESEARCH-NOTES-V2",repo=self.repo,
                         marker_commit=self.marker,trial_id=TRIAL,appid=self.appid,document=d)
        self.assertEqual(p["status"],"ready_for_create_only_submission")


    def test_future_manifest_builder_only_prepares_frozen_bytes(self):
        built=v2.manifest_blueprint(TRIAL,self.manifest["items"])
        self.assertEqual(json.loads(built["bytes"]),self.manifest)
        self.assertFalse(built["authorizes_semantic_execution"])
        broken=copy.deepcopy(self.manifest["items"])
        broken[0],broken[1]=broken[1],broken[0]
        with self.assertRaises(v2.NotesV2Error):
            v2.manifest_blueprint(TRIAL,broken)

    def test_github_receipt_proposal_never_claims_attempt_or_acceptance(self):
        doc=v2.item_receipt_blueprint(self.repo,marker_commit=self.marker,trial_id=TRIAL,
                                     appid=self.appid,phase="research",
                                     disposition="safe_incomplete_research")
        self.assertEqual(doc["semantic_attempt_state"],"unknown")
        self.assertFalse(doc["canonical_acceptance"])
        with self.assertRaises(v2.NotesV2Error):
            v2.item_receipt_blueprint(self.repo,marker_commit=self.marker,trial_id=TRIAL,
                                      appid=self.appid,phase="assembly",
                                      disposition="invented_green")

    def test_mutated_original_transport_fails_local_chain(self):
        sha=self.add_research()
        path=v2._path("research",self.assignment)
        write(self.repo,path,self.note(notes_text="tampered after introduction"))
        commit(self.repo,"fixture: illegally edit original transport")
        result=v2.classify_research(self.repo,marker_commit=self.marker,
                                    trial_id=TRIAL,appid=self.appid,
                                    introduction_commit=sha)
        self.assertEqual(result["status"],"broken_git_provenance")

    def test_nonexisting_research_commit_yields_local_provenance_diagnostic(self):
        result=v2.classify_research(self.repo,marker_commit=self.marker,
                                    trial_id=TRIAL,appid=self.appid,
                                    introduction_commit="f"*40)
        self.assertEqual(result["status"],"broken_git_provenance")

    def test_prepare_assembly_transport_checks_strict_before_publishing(self):
        _,work=self.work()
        invalid=v2.candidate_assembly(work,outcome="assembled_candidate_ready",
              final_dossier={"appid":self.appid,"title":self.assignment["title"]})
        with self.assertRaises(v2.NotesV2Error) as cm:
            v2.prepare_assembly_transport(self.repo,work,invalid)
        self.assertEqual(cm.exception.code,"final_strict_or_group_rejected")
        terminal=v2.candidate_assembly(work,outcome="runtime_or_tool_interrupted",
                 diagnostic="Synthetic access was interrupted")
        preview=v2.prepare_assembly_transport(self.repo,work,terminal)
        self.assertEqual(preview["status"],"ready_for_create_only_submission")
        self.assertFalse(preview["canonical_acceptance"])


    def test_pre_submission_rejects_original_document_forbidden_flags_and_fields(self):
        _,work=self.work()
        original=v2.candidate_assembly(work,outcome="assembly_missing_evidence",
                                       diagnostic="fixture insufficient evidence")
        mutations=(
            ("acceptance_true", {"canonical_acceptance":True}),
            ("staged_false", {"staged_only":False}),
            ("raw_reviews", {"raw_reviews":"private player review text"}),
            ("unknown_extra", {"invented_verified":True}),
            ("wrong_schema", {"schema":"DOSSIER-RESEARCH-NOTES-V2"}),
            ("unknown_outcome", {"outcome":"unauthorized_success"}),
            ("missing_required", {"diagnostic":None,"outcome":"assembly_missing_evidence"}),
        )
        for name,changes in mutations:
            with self.subTest(name=name):
                supplied=copy.deepcopy(original)
                supplied.update(changes)
                with self.assertRaises(v2.NotesV2Error) as cm:
                    v2.prepare_assembly_transport(self.repo,work,supplied)
                self.assertIn(cm.exception.code,("unparseable","unsafe_material","assembly_technical_error"))
                self.assertFalse((self.repo/work["output_path"]).exists(),
                                 "preflight must never create invalid transport")
                self.assertEqual(supplied,dict(original,**changes),
                                 "validation must not rewrite the submitted document")

    def test_pre_submission_validates_exact_original_payload_and_status(self):
        _,work=self.work()
        original=v2.candidate_assembly(
            work,outcome="assembly_missing_evidence",
            diagnostic="fixture lacked verification")
        prepared=v2.prepare_assembly_transport(self.repo,work,original)
        self.assertEqual(prepared["status"],"ready_for_create_only_submission")
        self.assertEqual(json.loads(prepared["bytes"]),original)
        self.assertFalse(prepared["canonical_acceptance"])
        for changes in (
            {"outcome":"assembled_candidate_ready","final_dossier":None},
            {"outcome":"runtime_or_tool_interrupted","final_dossier":{"appid":self.appid}},
            {"operations":[{"kind":"independent_discovery","access":"invalid_mode",
                            "summary":"not verified"}]},
            {"schema_version":1},
            {"canonical_acceptance":"false"},
        ):
            with self.subTest(changes=changes),self.assertRaises(v2.NotesV2Error):
                v2.prepare_assembly_transport(self.repo,work,dict(original,**changes))

    def test_immutable_marker_and_manifest_are_not_rewritten(self):
        path=f"data/control/dossier_notes_v2/manifests/{TRIAL}.json"
        mutated=copy.deepcopy(self.manifest)
        mutated["items"][0]["title"]="Tampered"
        write(self.repo,path,mutated)
        commit(self.repo,"fixture: illegally overwrite frozen manifest")
        with self.assertRaises(v2.NotesV2Error) as cm:
            v2.frozen_assignment(self.repo,marker_commit=self.marker,trial_id=TRIAL,
                                 appid=self.appid)
        self.assertEqual(cm.exception.code,"broken_git_provenance")

    def test_bad_marker_not_from_current_lineage_fails_closed(self):
        run(self.repo,"checkout","-b","independent")
        # This branch still has the marker; remove it from history by creating
        # an orphan branch, then the original marker is not in first-parent HEAD.
        run(self.repo,"checkout","--orphan","foreign")
        run(self.repo,"rm","-qr","--cached",".")
        write(self.repo,"foreign.json",{"unrelated":True})
        commit(self.repo,"fixture: foreign initial history")
        with self.assertRaises(v2.NotesV2Error) as cm:
            v2.frozen_assignment(self.repo,marker_commit=self.marker,trial_id=TRIAL,
                                 appid=self.appid)
        self.assertEqual(cm.exception.code,"broken_git_provenance")


    def test_wrong_title_edition_and_original_assignment_with_right_appids_fail(self):
        baseline=copy.deepcopy(self.manifest["items"])
        # All 18 identifiers and original pins are unchanged. Relabel only one.
        for field, replacement in (
                ("title","Totally Different Game"),
                ("title","Saints Row IV: Generic Edition"),
                ("assignment_id","shadow-03-1517180-forged"),
                ("original_assignment_sha256","0"*64)):
            rows=copy.deepcopy(baseline)
            i=12 if replacement.startswith("Saints Row") else 1
            rows[i][field]=replacement
            with self.subTest(field=field,replacement=replacement):
                with self.assertRaises(v2.NotesV2Error) as ctx:
                    v2.manifest_blueprint(TRIAL,rows)
                self.assertEqual(ctx.exception.code,"wrong_binding")
                # Reject even when a poisoned Git marker/manifest is published.
                tampered=copy.deepcopy(self.manifest)
                tampered["items"]=rows
                with tempfile.TemporaryDirectory() as td:
                    repo=Path(td)
                    run(repo,"init","-q")
                    run(repo,"config","user.name","Synthetic Fixture")
                    run(repo,"config","user.email","synthetic@example.invalid")
                    write(repo,f"data/control/dossier_notes_v2/manifests/{TRIAL}.json",tampered)
                    commit(repo,"fixture: forged original work identity")
                    write(repo,f"data/control/dossier_notes_v2/run_starts/{NONCE}.json",
                         {"schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,
                          "nonce":NONCE,"trial_id":TRIAL})
                    marker=commit(repo,"fixture: marker")
                    with self.assertRaises(v2.NotesV2Error):
                        v2.frozen_assignment(repo,marker_commit=marker,trial_id=TRIAL,
                                             appid=rows[i]["appid"])

    def test_unsafe_corrupt_a_cannot_stop_valid_b_and_c(self):
        group=C["original_groups"][0]
        commits={}
        for index,appid in enumerate(group["appids"]):
            assignment=v2.frozen_assignment(
                self.repo,marker_commit=self.marker,trial_id=TRIAL,appid=appid)
            note={"schema":"DOSSIER-RESEARCH-NOTES-V2","schema_version":2,
                  "assignment":assignment,"notes_text":"",
                  "source_log":[],"research_status":"no_verifiable_findings"}
            if index==0:
                note["source_log"]=[{"locator":{"url":"https://127.0.0.1/secret"},
                                     "access":"opened","observation":"unsafe"}]
            write(self.repo,v2._path("research",assignment),note)
            commits[appid]=commit(self.repo,"fixture: original item "+appid)
        rows=v2.frozen_assembly_traversal(
            self.repo,marker_commit=self.marker,trial_id=TRIAL,research_commits=commits)
        self.assertEqual(len(rows),18)
        self.assertEqual([r["appid"] for r in rows[:3]],group["appids"])
        self.assertEqual(rows[0]["status"],"unsafe_material")
        self.assertTrue(rows[0]["item_local_only"])
        self.assertEqual(rows[0]["attempt_state"],"unknown")
        self.assertFalse(rows[0]["canonical_acceptance"])
        for row in rows[1:3]:
            self.assertEqual(row["status"],"ready_for_autonomous_assembly")
            self.assertFalse(row["canonical_acceptance"])
        self.assertEqual(rows[3]["status"],"missing_research_transport")
        self.assertEqual(rows[3]["attempt_state"],"unknown")
        self.assertEqual(rows[-1]["appid"],C["original_groups"][-1]["appids"][-1])
        self.assertEqual([r["status"] for r in rows].count("ready_for_autonomous_assembly"),2)
        self.assertEqual([r["status"] for r in rows].count("missing_research_transport"),15)

    def test_invalid_binding_and_git_proof_are_item_local_at_assembly_entry(self):
        for kind in ("wrong_binding","broken_git_provenance"):
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as td:
                    repo=Path(td)
                    run(repo,"init","-q")
                    run(repo,"config","user.name","Synthetic Fixture")
                    run(repo,"config","user.email","synthetic@example.invalid")
                    write(repo,f"data/control/dossier_notes_v2/manifests/{TRIAL}.json",self.manifest)
                    commit(repo,"fixture: immutable manifest")
                    write(repo,f"data/control/dossier_notes_v2/run_starts/{NONCE}.json",
                         {"schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,"nonce":NONCE,"trial_id":TRIAL})
                    marker=commit(repo,"fixture: marker")
                    assignment=v2.frozen_assignment(repo,marker_commit=marker,
                                                   trial_id=TRIAL,appid="1508750")
                    note={"schema":"DOSSIER-RESEARCH-NOTES-V2","schema_version":2,
                          "assignment":assignment,"notes_text":"","source_log":[],
                          "research_status":"no_verifiable_findings"}
                    if kind=="wrong_binding":
                        note["assignment"]["title"]="unrelated game"
                    write(repo,v2._path("research",assignment),note)
                    if kind=="broken_git_provenance":
                        write(repo,"extra-unrelated.txt",{"extra":True})
                    commitsha=commit(repo,"fixture: failed Research")
                    item=v2.assembly_work(repo,marker_commit=marker,trial_id=TRIAL,
                                          appid="1508750",research_commit=commitsha)
                    self.assertEqual(item["status"],kind)
                    self.assertTrue(item["item_local_only"])
                    self.assertEqual(item["attempt_state"],"unknown")


    def test_invalid_utf8_research_A_does_not_stop_B_C_in_frozen_order(self):
        group=C["original_groups"][1]
        commits={}
        for index,appid in enumerate(group["appids"]):
            assignment=v2.frozen_assignment(
                self.repo,marker_commit=self.marker,trial_id=TRIAL,appid=appid)
            path=v2._path("research",assignment)
            if index==0:
                bad=self.repo/path
                bad.parent.mkdir(parents=True,exist_ok=True)
                bad.write_bytes(b"\xff\xfe\x00{\"invalid\":true}")
            else:
                write(self.repo,path,{"schema":"DOSSIER-RESEARCH-NOTES-V2",
                      "schema_version":2,"assignment":assignment,"notes_text":"",
                      "source_log":[],"research_status":"no_verifiable_findings"})
            commits[appid]=commit(self.repo,"fixture: original g8 item "+appid)
        rows=v2.frozen_assembly_traversal(
            self.repo,marker_commit=self.marker,trial_id=TRIAL,research_commits=commits)
        offset=3
        self.assertEqual([r["appid"] for r in rows[offset:offset+3]],group["appids"])
        self.assertEqual(rows[offset]["status"],"unparseable")
        self.assertTrue(rows[offset]["item_local_only"])
        self.assertEqual(rows[offset]["attempt_state"],"unknown")
        self.assertEqual([r["status"] for r in rows[offset+1:offset+3]],
                         ["ready_for_autonomous_assembly"]*2)
        self.assertEqual(len(rows),18)
        self.assertEqual([r["status"] for r in rows].count("ready_for_autonomous_assembly"),2)
        self.assertEqual([r["status"] for r in rows].count("missing_research_transport"),15)


    def test_mutate_then_restore_frozen_manifest_rejected_by_git_history(self):
        path=f"data/control/dossier_notes_v2/manifests/{TRIAL}.json"
        original=copy.deepcopy(self.manifest)
        changed=copy.deepcopy(original)
        changed["trial_id"]="another-trial-identifier"
        write(self.repo,path,changed)
        commit(self.repo,"fixture: tamper immutable manifest")
        write(self.repo,path,original)
        commit(self.repo,"fixture: restore manifest bytes")
        with self.assertRaises(v2.NotesV2Error) as cm:
            v2.frozen_assignment(self.repo,marker_commit=self.marker,
                                 trial_id=TRIAL,appid=self.appid)
        self.assertEqual(cm.exception.code,"broken_git_provenance")

    def test_mutate_then_restore_run_marker_rejected_by_git_history(self):
        path=f"data/control/dossier_notes_v2/run_starts/{NONCE}.json"
        original={"schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,
                  "nonce":NONCE,"trial_id":TRIAL}
        changed={**original,"nonce":"b"*32}
        write(self.repo,path,changed)
        commit(self.repo,"fixture: rewrite run-start marker")
        write(self.repo,path,original)
        commit(self.repo,"fixture: restore original marker bytes")
        with self.assertRaises(v2.NotesV2Error) as cm:
            v2.frozen_assignment(self.repo,marker_commit=self.marker,
                                 trial_id=TRIAL,appid=self.appid)
        self.assertEqual(cm.exception.code,"broken_git_provenance")

    def test_mutate_then_restore_research_rejected_not_accepted(self):
        original=self.note()
        sha=self.add_research(original)
        path=v2._path("research",self.assignment)
        write(self.repo,path,self.note(notes_text="illicit altered lead"))
        commit(self.repo,"fixture: rewrite research")
        write(self.repo,path,original)
        commit(self.repo,"fixture: restore research bytes")
        verdict=v2.classify_research(self.repo,marker_commit=self.marker,
                                    trial_id=TRIAL,appid=self.appid,
                                    introduction_commit=sha)
        self.assertEqual(verdict["status"],"broken_git_provenance")
        self.assertEqual(verdict["attempt_state"],"unknown")
        self.assertFalse(verdict["canonical_acceptance"])

    def test_mutate_then_restore_assembly_candidate_rejected(self):
        sha,work=self.work()
        original=v2.candidate_assembly(work,outcome="assembly_missing_evidence",
                                       diagnostic="Fixture insufficient")
        path=work["output_path"]
        write(self.repo,path,original)
        original_commit=commit(self.repo,"fixture: original assembly terminal")
        changed=copy.deepcopy(original)
        changed["diagnostic"]="Forged terminal status"
        write(self.repo,path,changed)
        commit(self.repo,"fixture: overwrite terminal")
        write(self.repo,path,original)
        commit(self.repo,"fixture: restore terminal")
        result=v2.inspect_assembly(self.repo,marker_commit=self.marker,
                                   trial_id=TRIAL,appid=self.appid,
                                   research_commit=sha,result_commit=original_commit)
        self.assertEqual(result["status"],"broken_git_provenance")
        self.assertFalse(result["canonical_acceptance"])

    def test_assembly_transport_rechecks_stale_research(self):
        sha,work=self.work()
        terminal=v2.candidate_assembly(work,outcome="assembly_missing_evidence",
                                       diagnostic="Fixture no sufficient evidence")
        path=v2._path("research",self.assignment)
        write(self.repo,path,self.note(notes_text="illicit later revision"))
        commit(self.repo,"fixture: invalid later edit")
        with self.assertRaises(v2.NotesV2Error) as cm:
            v2.prepare_assembly_transport(self.repo,work,terminal)
        self.assertEqual(cm.exception.code,"broken_git_provenance")
        self.assertFalse(v2.classify_research(
            self.repo,marker_commit=self.marker,trial_id=TRIAL,
            appid=self.appid,introduction_commit=sha)["canonical_acceptance"])

    def test_assembly_transport_rejects_forged_work_binding(self):
        sha,work=self.work()
        fake=copy.deepcopy(work)
        fake["source_notes_are_unverified_leads"]=False
        terminal=v2.candidate_assembly(fake,outcome="assembly_missing_evidence",
                                       diagnostic="Fixture")
        with self.assertRaises(v2.NotesV2Error) as cm:
            v2.prepare_assembly_transport(self.repo,fake,terminal)
        self.assertEqual(cm.exception.code,"broken_git_provenance")

    def test_typed_prefix_cannot_skip_next_item(self):
        order=["1517180","1533420","1590230"]
        for typed,target,states in [
            (["1517180"],"1590230",
             {"1517180":"ready","1533420":"ready","1590230":"ready"}),
            ([], "1517180", {"1517180":"ready"}),
            (["1517180","1533420"],"1533420",
             {"1517180":"ready","1533420":"ready"})]:
            with self.subTest(typed=typed,target=target):
                with self.assertRaises(v2.NotesV2Error) as cm:
                    v2.checked_typed_publish_prefix(order,typed,target,states)
                self.assertEqual(cm.exception.code,"wrong_binding")

    def test_receipt_phase_confusion_and_unsafe_source_rejected(self):
        for phase,disposition in [
            ("research","strict_item_valid_pending_existing_atomic_group_ingest"),
            ("research","assembly_semantic_conflict"),
            ("assembly","safe_incomplete_research")]:
            with self.subTest(phase=phase,disposition=disposition):
                with self.assertRaises(v2.NotesV2Error):
                    v2.item_receipt_blueprint(
                        self.repo,marker_commit=self.marker,trial_id=TRIAL,
                        appid=self.appid,phase=phase,disposition=disposition)
        with self.assertRaises(v2.NotesV2Error):
            v2.item_receipt_blueprint(
                self.repo,marker_commit=self.marker,trial_id=TRIAL,
                appid=self.appid,phase="assembly",disposition="missing_research_transport",
                source={"locator":"https://example.org/?token=secret",
                        "raw_reviews":"unsafe personal data"})

    def test_duplicate_reviewer_appointment_and_unverified_approval_rejected(self):
        roles={r:{"login":"fixture"+r,"github_id":i+101,
                  "appointment_ref":"synthetic-approval-"+r}
               for i,r in enumerate(("A","B","C"))}
        lookup=lambda login:{"login":login,"id":roles[login[-1]]["github_id"]}
        roles["C"]["appointment_ref"]=roles["A"]["appointment_ref"]
        with self.assertRaises(v2.NotesV2Error):
            v2.verify_independent_reviewers(roles,lookup,lambda *args: True)
        roles["C"]["appointment_ref"]="synthetic-approval-C"
        with self.assertRaises(v2.NotesV2Error):
            v2.verify_independent_reviewers(roles,lookup,lambda *args: "yes")

    def test_four_missing_slots_and_fourteen_synthetic_sparse_notes(self):
        # This is a disposable fixture, NOT a claim of actual historical
        # attempts or accepted evidence for the original fourteen transports.
        missing={"1508750","1607130","1849000","1857090"}
        commits={}
        for assignment in v2._original_rows():
            appid=assignment["appid"]
            if appid in missing:
                commits[appid]=None
                continue
            frozen=v2.frozen_assignment(self.repo,marker_commit=self.marker,
                                        trial_id=TRIAL,appid=appid)
            doc={"schema":"DOSSIER-RESEARCH-NOTES-V2","schema_version":2,
                 "assignment":frozen,"notes_text":"","source_log":[],
                 "research_status":"no_verifiable_findings"}
            write(self.repo,v2._path("research",frozen),doc)
            commits[appid]=commit(self.repo,"fixture: sparse "+appid)
        rows=v2.frozen_assembly_traversal(
            self.repo,marker_commit=self.marker,trial_id=TRIAL,
            research_commits=commits)
        self.assertEqual(len(rows),18)
        self.assertEqual({r["appid"] for r in rows if r["status"]=="missing_research_transport"},missing)
        self.assertEqual([r["status"] for r in rows].count("ready_for_autonomous_assembly"),14)
        self.assertTrue(all(r.get("attempt_state")=="unknown" for r in rows if r["appid"] in missing))
        self.assertTrue(all(r.get("canonical_acceptance") is False for r in rows))

if __name__=="__main__":
    unittest.main()
