/*
 * Dossier Notes V2: connector-native, tokenless manual transport.
 * Paste this module's functions into a ChatGPT Code Mode tool call and call
 * connectorPreflight / connectorHandoff / connectorResumeHandoff /
 * connectorPublishItem using the connected GitHub tools.
 * No GH_TOKEN, hidden OAuth exchange, background worker or automatic retry.
 *
 * GitHub remains the control plane. This transport checks immutable issuer,
 * owner Actions, exact identities and Git object lineage. The existing Python
 * strict writer alone determines semantic/strict acceptance. No candidate or
 * typed receipt is an acceptance statement.
 */
const V2_REPOSITORY = "kentrap2011-hub/steam-kz-deals-2";
const V2_OWNER_LOGIN = "kentrap2011-hub";
const V2_OWNER_ID = 315790060;
const V2_ISSUE = ".github/workflows/issue-dossier-notes-v2-batch.yml";
const V2_AUTHORIZE = ".github/workflows/authorize-dossier-notes-v2-batch.yml";
const V2_API = "https://api.github.com/repos/" + V2_REPOSITORY + "/";
const V2_HEX = /^[0-9a-f]{40}$/;
const V2_TRIAL = /^dossier-notes-v2-[a-z0-9][a-z0-9-]{7,90}$/;

function v2Assert(ok, why) { if (!ok) throw Error("BATCH_V2_CONNECTOR_STOP: " + why); }
function v2Canonical(value) {
  if (Array.isArray(value)) return "[" + value.map(v2Canonical).join(",") + "]";
  if (value !== null && typeof value === "object") return "{" +
    Object.keys(value).sort().map(k => JSON.stringify(k)+":"+v2Canonical(value[k])).join(",") + "}";
  return JSON.stringify(value);
}
function v2Utf8(s) {
  const out=[];
  for (const c of s) {
    const cp=c.codePointAt(0);
    if(cp<128) out.push(cp);
    else if(cp<2048) out.push(192|(cp>>6),128|(cp&63));
    else if(cp<65536) out.push(224|(cp>>12),128|((cp>>6)&63),128|(cp&63));
    else out.push(240|(cp>>18),128|((cp>>12)&63),128|((cp>>6)&63),128|(cp&63));
  }
  return out;
}
export function v2Sha256(input) {
  const k=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
  0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
  0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
  0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
  0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
  0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
  0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
  0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  const h=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  const b=v2Utf8(input),length=b.length*8;
  b.push(128);while(b.length%64!==56)b.push(0);
  const hi=Math.floor(length/4294967296),lo=length>>>0;
  for(let x=3;x>=0;x--)b.push((hi>>>(x*8))&255);
  for(let x=3;x>=0;x--)b.push((lo>>>(x*8))&255);
  for(let pos=0;pos<b.length;pos+=64){
    const w=new Array(64);
    for(let i=0;i<16;i++){const p=pos+i*4;w[i]=((b[p]<<24)|(b[p+1]<<16)|(b[p+2]<<8)|b[p+3])>>>0;}
    for(let i=16;i<64;i++){
      let x=w[i-15],y=w[i-2];
      let s0=((x>>>7)|(x<<25))^((x>>>18)|(x<<14))^(x>>>3);
      let s1=((y>>>17)|(y<<15))^((y>>>19)|(y<<13))^(y>>>10);
      w[i]=(w[i-16]+s0+w[i-7]+s1)>>>0;
    }
    let [a,c,d,e,f,g,j,z]=h;
    for(let i=0;i<64;i++){
      let s1=((f>>>6)|(f<<26))^((f>>>11)|(f<<21))^((f>>>25)|(f<<7));
      let ch=(f&g)^(~f&j);
      let t1=(z+s1+ch+k[i]+w[i])>>>0;
      let s0=((a>>>2)|(a<<30))^((a>>>13)|(a<<19))^((a>>>22)|(a<<10));
      let maj=(a&c)^(a&d)^(c&d);
      let t2=(s0+maj)>>>0;
      z=j;j=g;g=f;f=(e+t1)>>>0;e=d;d=c;c=a;a=(t1+t2)>>>0;
    }
    const next=[a,c,d,e,f,g,j,z];for(let i=0;i<8;i++)h[i]=(h[i]+next[i])>>>0;
  }
  return h.map(n=>n.toString(16).padStart(8,"0")).join("");
}
// Evaluate the exact existing Python-owned JSON schemas, not a new
// cohort-specific model. Only the keywords used by these V2 schemas are
// supported; unknown validation keywords fail closed rather than being ignored.
function v2SchemaCheck(value,schema,label="$") {
  v2Assert(schema && typeof schema==="object" && !Array.isArray(schema),
    "invalid canonical schema at "+label);
  const known=new Set(["$schema","title","description","type","additionalProperties",
    "required","properties","const","enum","minLength","maxLength",
    "minItems","maxItems","items","oneOf"]);
  v2Assert(Object.keys(schema).every(k=>known.has(k)),"unsupported canonical JSON schema keyword");
  const typeOf=value===null?"null":Array.isArray(value)?"array":typeof value;
  const isType=t=>t==="integer"?typeof value==="number"&&Number.isInteger(value):
    t==="number"?typeof value==="number"&&Number.isFinite(value):
    t===typeOf;
  if(schema.type!==undefined){
    const options=Array.isArray(schema.type)?schema.type:[schema.type];
    v2Assert(options.some(isType),"schema type mismatch at "+label);
  }
  if(Object.hasOwn(schema,"const"))
    v2Assert(v2Canonical(value)===v2Canonical(schema.const),"schema const mismatch at "+label);
  if(schema.enum!==undefined)
    v2Assert(Array.isArray(schema.enum)&&schema.enum.some(v=>
      v2Canonical(v)===v2Canonical(value)),"schema enum mismatch at "+label);
  if(schema.oneOf!==undefined){
    v2Assert(Array.isArray(schema.oneOf),"invalid oneOf canonical schema");
    let matches=0;
    for(const alt of schema.oneOf){
      try {v2SchemaCheck(value,alt,label);matches++;}
      catch(e){if(!String(e).includes("BATCH_V2_CONNECTOR_STOP"))throw e;}
    }
    v2Assert(matches===1,"schema oneOf mismatch at "+label);
  }
  if(typeOf==="string"){
    const len=[...value].length;
    if(schema.minLength!==undefined)v2Assert(len>=schema.minLength,"schema string too short at "+label);
    if(schema.maxLength!==undefined)v2Assert(len<=schema.maxLength,"schema string too long at "+label);
  }
  if(typeOf==="array"){
    if(schema.minItems!==undefined)v2Assert(value.length>=schema.minItems,"schema array too short at "+label);
    if(schema.maxItems!==undefined)v2Assert(value.length<=schema.maxItems,"schema array too long at "+label);
    if(schema.items)for(let i=0;i<value.length;i++)v2SchemaCheck(value[i],schema.items,label+"["+i+"]");
  }
  if(typeOf==="object"){
    const required=schema.required||[];
    v2Assert(required.every(k=>Object.hasOwn(value,k)),"schema required field missing at "+label);
    const props=schema.properties||{};
    if(schema.additionalProperties===false)
      v2Assert(Object.keys(value).every(k=>Object.hasOwn(props,k)),
        "schema unknown field at "+label);
    for(const key of Object.keys(props))
      if(Object.hasOwn(value,key))v2SchemaCheck(value[key],props[key],label+"."+key);
  }
}
function v2Json(o) {
  const doc=typeof o==="string"?JSON.parse(o):o;
  v2Assert(doc && typeof doc==="object" && !Array.isArray(doc),"GitHub JSON object required");
  return doc;
}
async function v2Get(api,endpoint) {
  const response=await api.fetch({url:V2_API+endpoint});
  return v2Json(response.result.content);
}
async function v2File(api,path,commit) {
  const response=await api.fetchFile({repository_full_name:V2_REPOSITORY,path,ref:commit});
  v2Assert(typeof response.result.content==="string" && V2_HEX.test(response.result.sha),"incomplete GitHub file");
  return response.result;
}
async function v2GitCommit(api,sha) {
  v2Assert(V2_HEX.test(sha),"invalid commit SHA");
  const doc=await v2Get(api,"git/commits/"+sha);
  v2Assert(doc.sha===sha && doc.tree && V2_HEX.test(doc.tree.sha) && Array.isArray(doc.parents),"GitHub Git commit malformed");
  return doc;
}
async function v2BranchTip(api,branch) {
  const ref=await v2Get(api,"git/ref/heads/"+branch);
  v2Assert(ref.ref==="refs/heads/"+branch && V2_HEX.test(ref.object?.sha),"ambiguous remote sandbox ref");
  return ref.object.sha;
}
function v2DocumentPath(phase,assignment) {
  const prefix=phase==="research"?"dossier_notes_v2":"dossier_assembly_v2";
  v2Assert(phase==="research"||phase==="assembly","unsupported phase");
  return "data/ai_inbox/"+prefix+"/"+assignment.trial_id+
    "/g"+String(assignment.group_sequence).padStart(6,"0")+
    "/"+assignment.appid+"--"+assignment.assignment_id+".json";
}
function v2ReceiptPath(phase,assignment) {
  return "data/control/dossier_notes_v2/receipts/"+assignment.trial_id+
    "/g"+String(assignment.group_sequence).padStart(6,"0")+
    "/"+assignment.appid+"--"+assignment.assignment_id+"--"+phase+".json";
}
// The strict GitHub writer audits every historical first-parent/one-add commit.
// During an interactive batch a single compare is sufficient to discover
// paths and detect a stale/unrelated sandbox, rather than re-reading 2*N
// historical commits before each item.
async function v2SandboxScope(api,head,authorizationCommit,trialId) {
  const found=new Map();
  if(head===authorizationCommit)return found;
  const cmp=await v2Get(api,"compare/"+authorizationCommit+"..."+head);
  v2Assert(cmp.status==="ahead" && cmp.base_commit?.sha===authorizationCommit &&
    (!cmp.head_commit || cmp.head_commit.sha===head) &&
    !cmp.too_large && Array.isArray(cmp.files) && cmp.files.length<=104,
    "sandbox does not descend from exact authorization or compare is incomplete");
  for(const file of cmp.files) {
    const p=file.filename;
    v2Assert(file.status==="added" && !found.has(p) &&
      (p.startsWith("data/ai_inbox/dossier_notes_v2/"+trialId+"/") ||
       p.startsWith("data/ai_inbox/dossier_assembly_v2/"+trialId+"/") ||
       p.startsWith("data/control/dossier_notes_v2/receipts/"+trialId+"/")),
      "sandbox contains unexpected/modified path: "+p);
    found.set(p,null);
  }
  return found;
}
function v2OwnerRun(doc,id,path,title,sha) {
  v2Assert(doc.id===Number(id) && doc.run_attempt===1 &&
   doc.status==="completed" && doc.conclusion==="success" &&
   doc.event==="workflow_dispatch" && doc.head_branch==="main" &&
   doc.path===path && doc.display_title===title &&
   doc.actor?.login===V2_OWNER_LOGIN && doc.actor?.id===V2_OWNER_ID &&
   doc.triggering_actor?.login===V2_OWNER_LOGIN &&
   doc.triggering_actor?.id===V2_OWNER_ID &&
   V2_HEX.test(doc.head_sha) && (!sha || doc.head_sha===sha),
   "authentic first-attempt owner GitHub Actions proof absent: "+path);
}
export async function connectorPreflight(api,{trialId,markerCommit,authorizationCommit,
  freezeRunId,expectedHead,phase="research"}) {
  v2Assert(V2_TRIAL.test(trialId) && !trialId.includes("original18"),"invalid/reused trial");
  v2Assert(["research","assembly"].includes(phase),"only isolated Research/Assembly allowed");
  v2Assert(V2_HEX.test(markerCommit) && V2_HEX.test(authorizationCommit) &&
    markerCommit!==authorizationCommit,"invalid issuer SHA");
  v2Assert(Number.isSafeInteger(Number(freezeRunId)) && Number(freezeRunId)>0,
    "freeze run ID required");
  v2Assert(V2_HEX.test(expectedHead),"explicit sandbox HEAD required");
  const branch="sandbox/"+trialId,paths={
    grant:"data/control/dossier_notes_v2/grants/"+trialId+".json",
    manifest:"data/control/dossier_notes_v2/manifests/"+trialId+".json",
    authorization:"data/control/dossier_notes_v2/authorizations/"+trialId+".json"
  };
  // Immutable issuer parent chain, once at invocation start.
  const authGit=await v2GitCommit(api,authorizationCommit);
  v2Assert(authGit.parents.length===1 && authGit.parents[0].sha===markerCommit,
    "authorization is not exact marker child");
  const marker=await v2GitCommit(api,markerCommit);
  v2Assert(marker.parents.length===1,"marker parent mismatch");
  const manifestCommit=marker.parents[0].sha;
  const manifestGit=await v2GitCommit(api,manifestCommit);
  v2Assert(manifestGit.parents.length===1,"manifest parent mismatch");
  const grantCommit=manifestGit.parents[0].sha;
  const grantGit=await v2GitCommit(api,grantCommit);
  v2Assert(grantGit.parents.length===1,"grant parent mismatch");
  const base=grantGit.parents[0].sha;
  const markerRest=await v2Get(api,"commits/"+markerCommit);
  v2Assert(markerRest.files?.length===1 &&
    markerRest.files[0].status==="added" &&
    /^data\/control\/dossier_notes_v2\/run_starts\/[0-9a-f]{32}\.json$/.test(markerRest.files[0].filename),
    "marker must introduce only exact nonce file");
  const nonce=markerRest.files[0].filename.split("/").pop().slice(0,-5);
  const markerDoc=v2Json((await v2File(api,markerRest.files[0].filename,markerCommit)).content);
  v2Assert(markerDoc.schema==="DOSSIER-NOTES-V2-RUN-START" &&
    markerDoc.schema_version===2 && markerDoc.trial_id===trialId &&
    markerDoc.nonce===nonce,"nonce marker mismatched");
  const grantFile=await v2File(api,paths.grant,grantCommit);
  const grant=v2Json(grantFile.content);
  const manifestFile=await v2File(api,paths.manifest,manifestCommit);
  const manifest=v2Json(manifestFile.content);
  const authFile=await v2File(api,paths.authorization,authorizationCommit);
  const auth=v2Json(authFile.content);
  v2Assert(grant.schema==="DOSSIER-NOTES-V2-BATCH-OWNER-GRANT" &&
    grant.schema_version===1 &&
    grant.scope==="one_git_owner_issued_reusable_batch_sandbox_only" &&
    grant.trial_id===trialId && grant.base_main_sha===base &&
    grant.manifest_path===paths.manifest &&
    grant.manifest_blob_sha===manifestFile.sha &&
    grant.source_pins && manifest.original_pins &&
    v2Canonical(grant.source_pins)===v2Canonical(manifest.original_pins) &&
    grant.owner_login===V2_OWNER_LOGIN && String(grant.owner_actor_id)===String(V2_OWNER_ID) &&
    grant.semantic_execution_approved===false && grant.production_approved===false &&
    grant.canonical_ingest_approved===false &&
    grant.cohort_contract_path==="config/dossier_notes_v2_batches/"+trialId+".json",
    "frozen owner grant inconsistent");
  v2Assert(auth.schema==="DOSSIER-NOTES-V2-BATCH-OWNER-AUTHORIZATION" &&
    auth.schema_version===1 && auth.scope==="one_manual_batch_research_assembly_sandbox_only" &&
    auth.trial_id===trialId && auth.marker_commit===markerCommit &&
    auth.marker_parent===manifestCommit && auth.human_grant_commit===grantCommit &&
    auth.human_grant_blob_sha===grantFile.sha && auth.manifest_blob_sha===manifestFile.sha &&
    auth.semantic_execution_authorized===true && auth.assembly_authorized===true &&
    auth.sandbox_writer_authorized===true && auth.production_authorized===false &&
    auth.canonical_acceptance===false && auth.owner_login===V2_OWNER_LOGIN &&
    String(auth.owner_actor_id)===String(V2_OWNER_ID),
    "authorization is not exact isolated owner grant");
  v2Assert(manifest.trial_id===trialId && manifest.schema==="DOSSIER-NOTES-V2-FROZEN-MANIFEST" &&
    manifest.schema_version===2 && Array.isArray(manifest.items) &&
    manifest.items.length>=1 && manifest.items.length<=24 &&
    new Set(manifest.items.map(i=>i.appid)).size===manifest.items.length &&
    manifest.items.every(i=>/^\d+$/.test(i.appid) && i.title && i.assignment_id &&
      Number.isInteger(i.group_sequence) && Number.isInteger(i.item_index)),
    "immutable manifest malformed");

  // GitHub Actions are the owner authority. Their reported success and identity
  // are checked once; unsigned Git committer names/timestamps add no proof.
  const freeze=await v2Get(api,"actions/runs/"+freezeRunId);
  const author=await v2Get(api,"actions/runs/"+auth.github_authorization_run_id);
  v2OwnerRun(freeze,freezeRunId,V2_ISSUE,
    "Issue one exact batch Dossier Notes V2 frozen sandbox (manual only)",base);
  v2OwnerRun(author,auth.github_authorization_run_id,V2_AUTHORIZE,
    "Authorize isolated Notes V2 batch "+trialId+" marker "+markerCommit);

  const current=await v2BranchTip(api,branch);
  v2Assert(current===expectedHead,"sandbox remote HEAD differs from explicit expected SHA");
  const existing=await v2SandboxScope(api,current,authorizationCommit,trialId);
  const headTree=current===authorizationCommit?authGit.tree.sha:
    (await v2GitCommit(api,current)).tree.sha;
  // Research must not download Assembly schema (and vice versa).
  const schemaPath=phase==="research"?
    "config/dossier_research_notes_v2.schema.json":
    "config/dossier_autonomous_assembly_result_v2.schema.json";
  const schemas={
    [phase]:v2Json((await v2File(api,schemaPath,base)).content),
    receipt:v2Json((await v2File(api,"config/dossier_notes_v2_item_receipt.schema.json",base)).content)
  };
  const anchor={
    trial_id:trialId,marker_commit:markerCommit,
    authorization_commit:authorizationCommit,
    authorization_blob_sha:authFile.sha,manifest_blob_sha:manifestFile.sha,
    human_grant_commit:grantCommit,base_main_sha:base,
    github_actor_id:String(V2_OWNER_ID),
    github_authorization_run_id:String(auth.github_authorization_run_id),
    semantic_execution_authorized:true,
    issuer_structural_only:true,github_run_authenticated:false
  };
  return {branch,phase,head:current,headTree,manifest,anchor,schemas,existing,
    github_owner_runs_authenticated:true,production_authorized:false};
}
// One create-only Git object and an expected-HEAD CAS. GitHub's existing strict
// sandbox writer later verifies original bytes and one-add ancestry.

// A Code Mode invocation has a limit of 20 GitHub calls. A full immutable
// preflight (14) plus an item candidate+receipt (10) cannot fit together.
// This pure handoff preserves the result of a *completed real* preflight
// across two consecutive Code Mode calls in the SAME explicit manual session.
// Its digest detects accidental copy drift, not a malicious substitute:
// never accept a handoff from user text, web, other chat, or unverified file.
export function connectorHandoff(ctx) {
  v2Assert(ctx && ctx.github_owner_runs_authenticated===true &&
    ctx.production_authorized===false && V2_HEX.test(ctx.head) &&
    V2_HEX.test(ctx.headTree) && ctx.branch==="sandbox/"+ctx.anchor?.trial_id &&
    (ctx.phase==="research" || ctx.phase==="assembly") &&
    ctx.existing instanceof Map && ctx.schemas?.[ctx.phase] && ctx.schemas?.receipt &&
    Array.isArray(ctx.manifest?.items),"only verified preflight context may be handed off");
  const payload={
    branch:ctx.branch,phase:ctx.phase,head:ctx.head,headTree:ctx.headTree,
    manifest:ctx.manifest,anchor:ctx.anchor,schemas:ctx.schemas,
    existing:[...ctx.existing.entries()],
    github_owner_runs_authenticated:true,production_authorized:false
  };
  return {kind:"DOSSIER-NOTES-V2-SESSION-HANDOFF",version:1,
    sha256:v2Sha256(v2Canonical(payload)),payload};
}

export async function connectorResumeHandoff(api,handoff) {
  v2Assert(handoff?.kind==="DOSSIER-NOTES-V2-SESSION-HANDOFF" &&
    handoff.version===1 && typeof handoff.sha256==="string" &&
    handoff.sha256===v2Sha256(v2Canonical(handoff.payload)),
    "missing or changed session handoff");
  const p=handoff.payload;
  v2Assert(p && p.github_owner_runs_authenticated===true &&
    p.production_authorized===false && V2_HEX.test(p.head) &&
    V2_HEX.test(p.headTree) && V2_HEX.test(p.anchor?.authorization_commit) &&
    V2_TRIAL.test(p.anchor?.trial_id) && !p.anchor.trial_id.includes("original18") &&
    p.branch==="sandbox/"+p.anchor.trial_id &&
    (p.phase==="research" || p.phase==="assembly") &&
    p.manifest?.trial_id===p.anchor.trial_id &&
    Array.isArray(p.manifest.items) && p.schemas?.[p.phase] && p.schemas?.receipt &&
    Array.isArray(p.existing) &&
    p.existing.every(row=>Array.isArray(row) && row.length===2 &&
      typeof row[0]==="string" && (row[1]===null || V2_HEX.test(row[1]))) &&
    new Set(p.existing.map(row=>row[0])).size===p.existing.length,
    "session handoff not a valid isolated original preflight");
  // One GitHub read prevents continuing from stale/parallel branch state.
  v2Assert(await v2BranchTip(api,p.branch)===p.head,
    "session handoff HEAD no longer current");
  return {...p,existing:new Map(p.existing)};
}

async function v2Add(api,ctx,path,document,expectedHead,description) {
  v2Assert(expectedHead===ctx.head,"stale sandbox HEAD");
  v2Assert(!ctx.existing.has(path),"create-only path already exists: "+path);
  const raw=v2Canonical(document);
  const created=await api.createBlob({repository_full_name:V2_REPOSITORY,
    content:raw,encoding:"utf-8"});
  const blob=created.result.sha;
  v2Assert(V2_HEX.test(blob),"GitHub blob creation missing SHA");
  const tree=await api.createTree({repository_full_name:V2_REPOSITORY,
    base_tree_sha:ctx.headTree,
    tree_elements:[{path,mode:"100644",type:"blob",sha:blob}]});
  v2Assert(V2_HEX.test(tree.result.sha),"Git tree not confirmed");
  const commit=await api.createCommit({repository_full_name:V2_REPOSITORY,
    message:description,tree_sha:tree.result.sha,parent_sha:expectedHead});
  const newSha=commit.result.sha;
  v2Assert(V2_HEX.test(newSha),"new commit SHA not available");
  // This lease is the concurrency protection. Do not replace with force push.
  const update=await api.updateRef({repository_full_name:V2_REPOSITORY,
    branch_name:ctx.branch,sha:newSha,expected_sha:expectedHead,force:false});
  v2Assert(update.result.success===true,"GitHub compare-and-swap rejected");
  // One readback confirms publication; full original bytes are checked by
  // the independent GitHub writer, not re-fetched by ChatGPT on every write.
  v2Assert(await v2BranchTip(api,ctx.branch)===newSha,
    "GitHub post-write branch readback mismatch");
  ctx.head=newSha;
  ctx.headTree=tree.result.sha;
  ctx.existing.set(path,newSha);
  return {commit:newSha,path,blob,raw,raw_sha256:v2Sha256(raw)};
}
function v2Assignment(ctx,appid){
  const row=ctx.manifest.items.find(i=>i.appid===String(appid));
  v2Assert(row,"AppID not on exact GitHub-frozen manifest");
  return {...row,trial_id:ctx.anchor.trial_id,
    marker_commit:ctx.anchor.marker_commit,
    manifest_blob_sha:ctx.anchor.manifest_blob_sha};
}
function v2DocumentCheck(doc,assignment,phase,schema) {
  v2SchemaCheck(doc,schema);
  v2Assert(v2Canonical(doc.assignment)===v2Canonical(assignment),
    "candidate frozen assignment mismatch");
}
function v2Receipt(assignment,phase,disposition,source) {
  return {schema:"DOSSIER-NOTES-V2-ITEM-RECEIPT",schema_version:2,
    trial_id:assignment.trial_id,appid:assignment.appid,assignment,
    phase,disposition,source,semantic_attempt_state:"unknown",
    staged_only:true,canonical_acceptance:false};
}
export async function connectorPublishItem(api,ctx,{phase,appid,document,researchCommit,expectedHead}) {
  v2Assert(["research","assembly"].includes(phase),"only Research or Assembly");
  v2Assert(expectedHead===ctx.head,"stale sandbox HEAD");
  v2Assert(phase===ctx.phase,"phase differs from authorized preflight");
  const assignment=v2Assignment(ctx,appid);
  v2DocumentCheck(document,assignment,phase,ctx.schemas[phase]);
  let researchTransport=null,disposition=null;
  if(phase==="assembly"){
    const researchPath=v2DocumentPath("research",assignment);
    const researchReceiptPath=v2ReceiptPath("research",assignment);
    v2Assert(V2_HEX.test(researchCommit) &&
      ctx.existing.has(researchPath) && ctx.existing.has(researchReceiptPath),
      "Assembly requires previously submitted original Research and receipt");
    let receiptCommit=ctx.existing.get(researchReceiptPath);
    if(!V2_HEX.test(receiptCommit)){
      // Resumed, separate Assembly session: find only this receipt, not all
      // historical commits. The strict writer verifies first introduction.
      const response=await api.fetch({url:V2_API+"commits?sha="+
        encodeURIComponent(ctx.branch)+"&path="+encodeURIComponent(researchReceiptPath)+
        "&per_page=1"});
      const commits=JSON.parse(response.result.content);
      v2Assert(Array.isArray(commits) && commits.length===1 &&
        V2_HEX.test(commits[0].sha),"typed Research receipt commit unavailable");
      receiptCommit=commits[0].sha;
    }
    const research=await v2File(api,researchPath,researchCommit);
    const typed=v2Json((await v2File(api,researchReceiptPath,receiptCommit)).content);
    const researchSha=v2Sha256(research.content);
    researchTransport={
      research_package_git_commit:researchCommit,
      research_package_path:researchPath,
      research_package_blob_sha:research.sha,
      research_package_raw_sha256:researchSha,
      research_package_sha256:researchSha
    };
    v2Assert(typed.phase==="research" && typed.disposition==="safe_incomplete_research" &&
      typed.appid===String(appid) && typed.source?.candidate?.commit===researchCommit &&
      typed.source?.candidate?.blob_sha===research.sha &&
      typed.source?.candidate?.raw_sha256===researchSha,
      "Research typed receipt not exact/eligible");
    v2Assert(v2Canonical(document.research_transport)===v2Canonical(researchTransport),
      "Assembly research binding mismatch");
    const outcomes=new Set(["assembled_candidate_ready","assembly_missing_evidence",
      "assembly_semantic_conflict","runtime_or_tool_interrupted","assembly_technical_error"]);
    v2Assert(outcomes.has(document.outcome),"invalid Assembly outcome");
    v2Assert((document.outcome==="assembled_candidate_ready") ===
      (document.final_dossier!==null),"final Dossier/terminal mismatch");
    disposition=document.outcome==="assembled_candidate_ready"
      ?"strict_item_valid_pending_existing_atomic_group_ingest":document.outcome;
  }else{
    disposition="safe_incomplete_research";
  }
  const candidatePath=v2DocumentPath(phase,assignment);
  const receiptPath=v2ReceiptPath(phase,assignment);
  v2Assert(!ctx.existing.has(candidatePath) && !ctx.existing.has(receiptPath),
    "candidate or receipt already exists; no alternate path permitted");
  // A submitted candidate is never a semantic acceptance or canonical result.
  const candidate=await v2Add(api,ctx,candidatePath,document,expectedHead,
    "dossier notes v2: create-only connector "+phase+" item "+appid);
  let source;
  if(phase==="research"){
    source={issuer:ctx.anchor,receipt_parent_commit:candidate.commit,
      introduction_commit:candidate.commit,candidate_status:disposition,
      transport_technically_verified:true,github_receipt_confirmed:false,
      candidate:{path:candidate.path,commit:candidate.commit,blob_sha:candidate.blob,
        raw_sha256:candidate.raw_sha256,canonical_sha256:candidate.raw_sha256}};
  }else{
    source={issuer:ctx.anchor,receipt_parent_commit:candidate.commit,
      research_commit:researchCommit,assembly_commit:candidate.commit,
      candidate_status:disposition,canonical_acceptance:false};
  }
  const receiptDoc=v2Receipt(assignment,phase,disposition,source);
  v2SchemaCheck(receiptDoc,ctx.schemas.receipt);
  // If this second write fails, DO NOT re-publish the candidate. Inspect GitHub,
  // report unpaired state, stop; no implicit attempt/auto-retry.
  const receipt=await v2Add(api,ctx,receiptPath,receiptDoc,candidate.commit,
    "dossier notes v2: create-only connector "+phase+" receipt "+appid);
  return {phase,appid:String(appid),candidate_commit:candidate.commit,
    receipt_commit:receipt.commit,candidate_path:candidate.path,
    receipt_path:receipt.path,disposition,github_branch_readback_confirmed:true,
    github_owner_runs_authenticated:true,semantic_quality_accepted:false,
    canonical_acceptance:false};
}
