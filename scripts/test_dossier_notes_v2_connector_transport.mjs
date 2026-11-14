#!/usr/bin/env node
/* Synthetic disposable GitHub API fixture. Never connects to GitHub or runs semantics. */
import test from "node:test";
import assert from "node:assert/strict";
import {createHash} from "node:crypto";
import {readFileSync} from "node:fs";
import {connectorPreflight,connectorPublishItem,v2Sha256} from "./dossier_notes_v2_connector_transport.mjs";

const REPO="kentrap2011-hub/steam-kz-deals-2";
const sha=n=>n.toString(16).padStart(40,"0");
const blob=s=>createHash("sha1").update("blob "+Buffer.byteLength(s)+"\0"+s).digest("hex");
const canonical=o=>JSON.stringify(o,Object.keys(o).sort());
const TRIAL="dossier-notes-v2-fresh6-20261111-first",MARKER=sha(13),AUTH=sha(14);
const FREEZE_ID=43466039520,AUTHOR_ID=43467293841;

function makeFixture(n=6) {
  const f={files:new Map(),commits:new Map(),runs:new Map(),calls:[],sequence:40,
    head:AUTH,mutateHeadOnUpdate:false,malformReadback:false};
  const all=[
    ["1000010","Crown Trick"],["102600","Orcs Must Die!"],
    ["1029690","Sniper Elite 5"],["49520","Borderlands 2"],
    ["499180","Braid, Anniversary Edition"],["501590","Bulletstorm: Full Clip Edition"]
  ];
  const items=all.slice(0,n).map(([appid,title],i)=>({
    group_sequence:Math.floor(i/3)+1,item_index:i%3,
    appid,title,assignment_id:"batch-"+String(i+1).padStart(24,"0"),
    original_assignment_sha256:String(i+1).padStart(64,"0")
  }));
  const base=sha(10),grant=sha(11),manifestCommit=sha(12);
  const cp=(id,parent,path)=>f.commits.set(id,{
    committer:{name:"github-actions[bot]",
      email:"41898282+github-actions[bot]@users.noreply.github.com",
      date:id===AUTH?"2026-11-13T16:54:14Z":"2026-11-13T16:46:29Z"},
    sha:id,tree:{sha:sha(100+Number.parseInt(id,16))},
    parents:parent?[{sha:parent}]:[],files:path?[{filename:path,status:"added"}]:[]
  });
  cp(base,null);
  const paths={
    grant:"data/control/dossier_notes_v2/grants/"+TRIAL+".json",
    manifest:"data/control/dossier_notes_v2/manifests/"+TRIAL+".json",
    authorization:"data/control/dossier_notes_v2/authorizations/"+TRIAL+".json",
    nonce:"data/control/dossier_notes_v2/run_starts/"+"ab".repeat(16)+".json",
  };
  cp(grant,base,paths.grant);cp(manifestCommit,grant,paths.manifest);
  cp(MARKER,manifestCommit,paths.nonce);cp(AUTH,MARKER,paths.authorization);
  const setFile=(id,path,o)=>{
    const raw=typeof o==="string"?o:JSON.stringify(o);
    f.files.set(id+"|"+path,{content:raw,sha:blob(raw)});
  };
  setFile(MARKER,paths.nonce,{schema:"DOSSIER-NOTES-V2-RUN-START",schema_version:2,
    trial_id:TRIAL,nonce:"ab".repeat(16)});
  const sourcePins={source_main_sha:base,source_snapshot_id:"synthetic",
    source_queue_sha256:"a".repeat(64)};
  const m={schema:"DOSSIER-NOTES-V2-FROZEN-MANIFEST",schema_version:2,
    trial_id:TRIAL,original_pins:sourcePins,items};
  setFile(manifestCommit,paths.manifest,m);
  const gf=f.files.get(manifestCommit+"|"+paths.manifest);
  const g={schema:"DOSSIER-NOTES-V2-BATCH-OWNER-GRANT",schema_version:1,
    scope:"one_git_owner_issued_reusable_batch_sandbox_only",
    manifest_path:paths.manifest,source_pins:sourcePins,
    trial_id:TRIAL,base_main_sha:base,owner_login:"kentrap2011-hub",
    owner_actor_id:"315790060",manifest_blob_sha:gf.sha,
    semantic_execution_approved:false,production_approved:false,
    canonical_ingest_approved:false,
    cohort_contract_path:"config/dossier_notes_v2_batches/"+TRIAL+".json"};
  setFile(grant,paths.grant,g);
  const af=f.files.get(grant+"|"+paths.grant);
  for(const file of [
    "dossier_research_notes_v2.schema.json",
    "dossier_autonomous_assembly_result_v2.schema.json",
    "dossier_notes_v2_item_receipt.schema.json"
  ]){
    const path="config/"+file;
    setFile(base,path,readFileSync(new URL("../config/"+file,import.meta.url),"utf8"));
  }
  setFile(AUTH,paths.authorization,{
    schema:"DOSSIER-NOTES-V2-BATCH-OWNER-AUTHORIZATION",schema_version:1,
    scope:"one_manual_batch_research_assembly_sandbox_only",
    trial_id:TRIAL,marker_commit:MARKER,marker_parent:manifestCommit,
    human_grant_commit:grant,human_grant_blob_sha:af.sha,
    manifest_blob_sha:gf.sha,github_authorization_run_id:String(AUTHOR_ID),
    semantic_execution_authorized:true,assembly_authorized:true,
    sandbox_writer_authorized:true,production_authorized:false,
    canonical_acceptance:false,owner_login:"kentrap2011-hub",
    owner_actor_id:"315790060"});
  const makeRun=(id,path,title)=>({id,run_attempt:1,
    run_started_at:id===FREEZE_ID?"2026-11-13T16:46:11Z":"2026-11-13T16:53:47Z",
    updated_at:id===FREEZE_ID?"2026-11-13T16:46:34Z":"2026-11-13T16:54:22Z",
    status:"completed",
    conclusion:"success",event:"workflow_dispatch",head_branch:"main",head_sha:base,
    path,display_title:title,
    actor:{login:"kentrap2011-hub",id:315790060},
    triggering_actor:{login:"kentrap2011-hub",id:315790060}});
  f.runs.set(FREEZE_ID,makeRun(FREEZE_ID,
    ".github/workflows/issue-dossier-notes-v2-batch.yml",
    "Issue one exact batch Dossier Notes V2 frozen sandbox (manual only)"));
  f.runs.set(AUTHOR_ID,makeRun(AUTHOR_ID,
    ".github/workflows/authorize-dossier-notes-v2-batch.yml",
    "Authorize isolated Notes V2 batch "+TRIAL+" marker "+MARKER));
  f.api={
    async fetch({url}){
      f.calls.push(["fetch",url]);
      const prefix="https://api.github.com/repos/"+REPO+"/";
      assert.ok(url.startsWith(prefix),"wrong repository");
      const ep=url.slice(prefix.length);
      let value;
      if(ep.startsWith("git/commits/")){value=f.commits.get(ep.slice(12));}
      else if(ep.startsWith("commits/")){
        const c=f.commits.get(ep.slice(8));
        if(c)value={sha:c.sha,files:c.files};
      }
      else if(ep.startsWith("actions/runs/")){value=f.runs.get(Number(ep.slice(13)));}
      else if(ep.startsWith("git/ref/heads/")){
        value={ref:"refs/heads/sandbox/"+TRIAL,
          object:{sha:f.malformReadback &&
            f.calls.some(x=>x[0]==="updateRef")?sha(999):f.head}};
      }
      else if(ep.startsWith("compare/")){
        const files=[];
        let tip=f.head;
        while(tip!==AUTH){
          const c=f.commits.get(tip);
          assert.ok(c,"broken synthetic commit ancestry");
          files.push(...c.files);
          tip=c.parents[0].sha;
        }
        value={status:files.length?"ahead":"identical",base_commit:{sha:AUTH},
          head_commit:{sha:f.head},files};
      }
      else if(ep.startsWith("commits?")){
        const search=new URL(url).searchParams;
        const path=search.get("path");
        const match=[...f.commits.values()].reverse().find(c=>
          c.files.some(x=>x.filename===path));
        value=match?[{sha:match.sha}]:[];
      }
      assert.ok(value,"missing fixture GitHub "+ep);
      return {result:{content:JSON.stringify(value)}};
    },
    async fetchFile({repository_full_name,path,ref}){
      f.calls.push(["fetchFile",path,ref]);
      assert.equal(repository_full_name,REPO);
      const data=f.files.get(ref+"|"+path);
      if(!data)throw Error("NOT_FOUND: 404");
      return {result:{content:f.malformReadback?"tampered":data.content,sha:data.sha}};
    },
    async createBlob({repository_full_name,content,encoding}){
      assert.equal(repository_full_name,REPO);assert.equal(encoding,"utf-8");
      f.blob={content,sha:blob(content)};
      f.calls.push(["createBlob",f.blob.sha]);
      return {result:{sha:f.blob.sha}};
    },
    async createTree({repository_full_name,base_tree_sha,tree_elements}){
      assert.equal(repository_full_name,REPO);
      assert.equal(tree_elements.length,1);
      const entry=tree_elements[0];
      assert.equal(entry.sha,f.blob.sha);assert.equal(entry.mode,"100644");
      assert.ok([...f.commits.values()].some(c=>c.tree.sha===base_tree_sha));
      f.tree={sha:sha(f.sequence++),entry,base_tree_sha};
      f.calls.push(["createTree",entry.path]);
      return {result:{sha:f.tree.sha}};
    },
    async createCommit({repository_full_name,tree_sha,parent_sha,message}){
      assert.equal(repository_full_name,REPO);assert.equal(tree_sha,f.tree.sha);
      const id=sha(f.sequence++);
      f.commits.set(id,{sha:id,tree:{sha:tree_sha},parents:[{sha:parent_sha}],
        files:[{filename:f.tree.entry.path,status:"added"}]});
      f.files.set(id+"|"+f.tree.entry.path,{content:f.blob.content,sha:f.blob.sha});
      f.calls.push(["createCommit",id,message]);
      return {result:{sha:id}};
    },
    async updateRef({repository_full_name,branch_name,sha:next,force,expected_sha}){
      assert.equal(repository_full_name,REPO);
      assert.equal(branch_name,"sandbox/"+TRIAL);assert.equal(force,false);
      f.calls.push(["updateRef",expected_sha,next]);
      if(f.mutateHeadOnUpdate)f.head=sha(999);
      if(f.head!==expected_sha)throw Error("GitHub CAS rejected stale expected_sha");
      f.head=next;return {result:{success:true}};
    }
  };
  return f;
}
async function preflight(f,opts={}){
  return connectorPreflight(f.api,{trialId:TRIAL,markerCommit:MARKER,
    authorizationCommit:AUTH,freezeRunId:FREEZE_ID,expectedHead:AUTH,...opts});
}
function researchDoc(ctx,appid){
  const row=ctx.manifest.items.find(r=>r.appid===appid);
  return {schema:"DOSSIER-RESEARCH-NOTES-V2",schema_version:2,
    assignment:{...row,trial_id:TRIAL,marker_commit:MARKER,
      manifest_blob_sha:ctx.anchor.manifest_blob_sha},notes_text:"No verifiable sources",source_log:[],
    research_status:"no_verifiable_findings"};
}
test("portable SHA256 equals standard UTF-8 digest",()=>{
  for(const raw of ["","hello","Braid, Anniversary Edition","中文 русский 😀",JSON.stringify({a:1})])
    assert.equal(v2Sha256(raw),createHash("sha256").update(raw).digest("hex"));
});
test("first six exact frozen identities and authenticated two owner runs",async()=>{
  const f=makeFixture(),ctx=await preflight(f);
  assert.deepEqual(ctx.manifest.items.map(x=>x.appid),
    ["1000010","102600","1029690","49520","499180","501590"]);
  assert.equal(ctx.github_owner_runs_authenticated,true);
  assert.equal(ctx.production_authorized,false);
});
test("second arbitrary cohort-size fixture proves no six-only runtime",async()=>{
  const f=makeFixture(1),ctx=await preflight(f);
  assert.equal(ctx.manifest.items.length,1);
  assert.equal(ctx.manifest.items[0].appid,"1000010");
});
test("Research candidate and typed receipt are separate one-add CAS commits",async()=>{
  const f=makeFixture(),ctx=await preflight(f);
  const out=await connectorPublishItem(f.api,ctx,{phase:"research",appid:"1000010",
    expectedHead:AUTH,document:researchDoc(ctx,"1000010")});
  assert.notEqual(out.candidate_commit,out.receipt_commit);
  assert.equal(out.github_branch_readback_confirmed,true);
  assert.equal(out.canonical_acceptance,false);
  const adds=f.calls.filter(a=>a[0]==="updateRef");
  assert.equal(adds.length,2);
  assert.equal(adds[0][1],AUTH);assert.equal(adds[1][1],out.candidate_commit);
  assert.equal(f.commits.get(out.candidate_commit).files[0].status,"added");
  assert.equal(f.commits.get(out.receipt_commit).files[0].status,"added");
  const typed=JSON.parse(f.files.get(out.receipt_commit+"|"+out.receipt_path).content);
  assert.equal(typed.disposition,"safe_incomplete_research");
  assert.equal(typed.source.candidate.raw_sha256,
    createHash("sha256").update(f.files.get(out.candidate_commit+"|"+out.candidate_path).content).digest("hex"));
});
test("Assembly requires original candidate and typed Research receipt, terminal stays isolated",async()=>{
  const f=makeFixture(),ctx=await preflight(f);
  const research=await connectorPublishItem(f.api,ctx,{phase:"research",appid:"1000010",
    expectedHead:AUTH,document:researchDoc(ctx,"1000010")});
  const a=researchDoc(ctx,"1000010").assignment;
  const researchFile=f.files.get(research.candidate_commit+"|"+research.candidate_path);
  const sha2=createHash("sha256").update(researchFile.content).digest("hex");
  const doc={schema:"DOSSIER-AUTONOMOUS-ASSEMBLY-RESULT-V2",schema_version:2,
    assignment:a,research_transport:{
      research_package_git_commit:research.candidate_commit,
      research_package_path:research.candidate_path,
      research_package_blob_sha:researchFile.sha,
      research_package_raw_sha256:sha2,research_package_sha256:sha2},
    outcome:"assembly_missing_evidence",final_dossier:null,
    operations:[],mechanical_corrections:[],diagnostic:"insufficient evidence",
    staged_only:true,canonical_acceptance:false};
  const assemblyCtx=await preflight(f,{phase:"assembly",expectedHead:research.receipt_commit});
  const result=await connectorPublishItem(f.api,assemblyCtx,{phase:"assembly",appid:"1000010",
    researchCommit:research.candidate_commit,expectedHead:research.receipt_commit,
    document:doc});
  assert.equal(result.disposition,"assembly_missing_evidence");
  const receipt=JSON.parse(f.files.get(result.receipt_commit+"|"+result.receipt_path).content);
  assert.equal(receipt.source.research_commit,research.candidate_commit);
  assert.equal(receipt.canonical_acceptance,false);
});
test("wrong actor, attempt, workflow, marker, run-name and ref all stop preflight",async()=>{
  for(const key of ["actor","run_attempt","path","display_title","head_branch","conclusion","triggering_actor"]){
    const f=makeFixture(),r=f.runs.get(AUTHOR_ID);
    if(key==="actor")r.actor={login:"somebody",id:5};
    else if(key==="triggering_actor")r.triggering_actor={login:"somebody",id:5};
    else r[key]=key==="run_attempt"?2:"wrong";
    await assert.rejects(()=>preflight(f),/BATCH_V2_CONNECTOR_STOP/);
  }
  for(const key of ["actor","run_attempt","path","head_branch","head_sha"]){
    const f=makeFixture(),r=f.runs.get(FREEZE_ID);
    r[key]=key==="run_attempt"?2:key==="actor"?{login:"other",id:1}:"wrong";
    await assert.rejects(()=>preflight(f),/BATCH_V2_CONNECTOR_STOP/);
  }
  const f=makeFixture();
  f.head=sha(999);
  await assert.rejects(()=>preflight(f),/BATCH_V2_CONNECTOR_STOP/);
  // Untrusted Git committer timestamps must not block valid owner Actions.
  const g=makeFixture();
  g.commits.get(AUTH).committer.date="2026-11-13T00:00:00Z";
  g.runs.get(FREEZE_ID).run_started_at="2026-11-13T16:46:31Z";
  await preflight(g);
});
test("wrong AppID or edition fails before Git object is created",async()=>{
  const f=makeFixture(),ctx=await preflight(f);
  await assert.rejects(()=>connectorPublishItem(f.api,ctx,{
    phase:"research",appid:"9999",expectedHead:AUTH,document:researchDoc(ctx,"1000010")
  }),/BATCH_V2_CONNECTOR_STOP/);
  const doc=researchDoc(ctx,"1000010");doc.assignment.title="Wrong Edition";
  await assert.rejects(()=>connectorPublishItem(f.api,ctx,{
    phase:"research",appid:"1000010",expectedHead:AUTH,document:doc
  }),/BATCH_V2_CONNECTOR_STOP/);
  const missing=researchDoc(ctx,"1000010");delete missing.notes_text;
  await assert.rejects(()=>connectorPublishItem(f.api,ctx,{
    phase:"research",appid:"1000010",expectedHead:AUTH,document:missing
  }),/schema required field/);
  const extra=researchDoc(ctx,"1000010");extra.unapproved_field="bad";
  await assert.rejects(()=>connectorPublishItem(f.api,ctx,{
    phase:"research",appid:"1000010",expectedHead:AUTH,document:extra
  }),/schema unknown field/);
  const malformed=researchDoc(ctx,"1000010");
  malformed.source_log=[{locator:{url:"a",public_ref:"foo"},access:"opened",observation:"test"}];
  await assert.rejects(()=>connectorPublishItem(f.api,ctx,{
    phase:"research",appid:"1000010",expectedHead:AUTH,document:malformed
  }),/schema oneOf mismatch/);
  assert.equal(f.calls.some(x=>x[0]==="createBlob"),false);
});
test("parallel branch movement rejects CAS; never retries candidate or publishes receipt",async()=>{
  const f=makeFixture(),ctx=await preflight(f);
  f.mutateHeadOnUpdate=true;
  await assert.rejects(()=>connectorPublishItem(f.api,ctx,{
    phase:"research",appid:"1000010",expectedHead:AUTH,document:researchDoc(ctx,"1000010")
  }),/CAS rejected/);
  assert.equal(f.calls.filter(x=>x[0]==="createCommit").length,1);
  assert.equal(f.calls.filter(x=>x[0]==="updateRef").length,1);
});
test("duplicate create-only path and stale expected head do not write",async()=>{
  const f=makeFixture(),ctx=await preflight(f);
  const first=await connectorPublishItem(f.api,ctx,{phase:"research",appid:"1000010",
    expectedHead:AUTH,document:researchDoc(ctx,"1000010")});
  await assert.rejects(()=>connectorPublishItem(f.api,ctx,{phase:"research",appid:"1000010",
    expectedHead:first.receipt_commit,document:researchDoc(ctx,"1000010")}),/create-only|already exists/);
  await assert.rejects(()=>connectorPublishItem(f.api,ctx,{phase:"research",appid:"102600",
    expectedHead:AUTH,document:researchDoc(ctx,"102600")}),/stale/);
});
test("incomplete A is not sibling B blocker; bad B is refused before write",async()=>{
  const f=makeFixture(),ctx=await preflight(f);
  const a=await connectorPublishItem(f.api,ctx,{phase:"research",appid:"1000010",
    expectedHead:AUTH,document:researchDoc(ctx,"1000010")});
  const malformed=researchDoc(ctx,"102600");malformed.assignment.appid="666";
  await assert.rejects(()=>connectorPublishItem(f.api,ctx,{phase:"research",appid:"102600",
    expectedHead:a.receipt_commit,document:malformed}),/frozen assignment/);
  const b=await connectorPublishItem(f.api,ctx,{phase:"research",appid:"102600",
    expectedHead:a.receipt_commit,document:researchDoc(ctx,"102600")});
  assert.ok(b.receipt_commit);
});
test("ambiguous GitHub branch readback fails closed with no second write",async()=>{
  const f=makeFixture(),ctx=await preflight(f);
  f.malformReadback=true;
  await assert.rejects(()=>connectorPublishItem(f.api,ctx,{phase:"research",appid:"1000010",
    expectedHead:AUTH,document:researchDoc(ctx,"1000010")}),/readback mismatch/);
  assert.equal(f.calls.filter(x=>x[0]==="updateRef").length,1);
});
test("no canonical, production or original18 publication interface exists",async()=>{
  const f=makeFixture();
  await assert.rejects(()=>preflight(f,{trialId:"dossier-notes-v2-original18-first"}),/invalid\/reused/);
  const ctx=await preflight(f);
  assert.equal(typeof ctx.production_authorized,"boolean");
  assert.equal(ctx.production_authorized,false);
  const doc=researchDoc(ctx,"1000010");
  const out=await connectorPublishItem(f.api,ctx,{phase:"research",appid:"1000010",
    expectedHead:AUTH,document:doc});
  assert.match(out.candidate_path,/^data\/ai_inbox\/dossier_notes_v2\//);
  assert.match(out.receipt_path,/^data\/control\/dossier_notes_v2\/receipts\//);
});


test("lean preflight and constant-cost Research publication",async()=>{
  const f=makeFixture(),ctx=await preflight(f);
  const callsBefore=f.calls.length;
  assert.equal(f.calls.filter(x=>x[0]==="fetchFile").length,6);
  assert.equal(f.calls.some(x=>x[0]==="getRepo"),false);
  for(const row of ctx.manifest.items){
    const before=f.calls.length,head=ctx.head;
    const out=await connectorPublishItem(f.api,ctx,{
      phase:"research",appid:row.appid,expectedHead:head,
      document:researchDoc(ctx,row.appid)
    });
    const latest=f.calls.slice(before);
    assert.equal(latest.length,10);
    assert.equal(latest.filter(x=>x[0]==="fetchFile").length,0);
    assert.equal(latest.filter(x=>x[0]==="fetch" &&
      x[1].includes("/git/ref/heads/")).length,2);
    assert.equal(ctx.head,out.receipt_commit);
  }
  assert.equal(f.calls.length-callsBefore,60);
  assert.equal(f.calls.filter(x=>x[0]==="updateRef").length,12);
  assert.equal(ctx.existing.size,12);
});

test("resumed batch uses one compare, skips per-commit history reads",async()=>{
  const f=makeFixture(),ctx=await preflight(f);
  const out=await connectorPublishItem(f.api,ctx,{
    phase:"research",appid:"1000010",expectedHead:AUTH,
    document:researchDoc(ctx,"1000010")
  });
  const before=f.calls.length;
  const resumed=await preflight(f,{expectedHead:out.receipt_commit});
  const rest=f.calls.slice(before);
  assert.equal(rest.filter(x=>x[0]==="fetch" &&
    x[1].includes("/compare/")).length,1);
  assert.equal(resumed.existing.size,2);
  await assert.rejects(()=>connectorPublishItem(f.api,resumed,{
    phase:"research",appid:"1000010",expectedHead:out.receipt_commit,
    document:researchDoc(resumed,"1000010")
  }),/already exists/);
});

test("Assembly preflight requires Research+receipt and no Research schema read",async()=>{
  const f=makeFixture(),ctx=await preflight(f);
  const research=await connectorPublishItem(f.api,ctx,{
    phase:"research",appid:"1000010",expectedHead:AUTH,
    document:researchDoc(ctx,"1000010")
  });
  const before=f.calls.length;
  const assembly=await preflight(f,{phase:"assembly",expectedHead:research.receipt_commit});
  assert.ok(assembly.existing.has(research.candidate_path));
  assert.ok(assembly.existing.has(research.receipt_path));
  assert.equal(f.calls.slice(before).filter(x=>x[0]==="fetchFile" &&
    x[1].includes("dossier_research_notes_v2.schema.json")).length,0);
  await assert.rejects(()=>connectorPublishItem(f.api,assembly,{
    phase:"research",appid:"1000010",expectedHead:research.receipt_commit,
    document:researchDoc(assembly,"1000010")
  }),/phase differs/);
});
