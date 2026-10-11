"use strict";
// Offline, pre-output, metadata-only projection. NEVER reads review prose semantically,
// NEVER sends requests, and NEVER prints any source URL, handle or public_ref.
const PIN = "95a4bf4990a60082ecb3302da5bc7f23b618d93e";
const WORK_BLOB = "ef40fc186aabc79dfd24c72864dbe43817a56039";
const AUDIT_BLOB = "8dbf4437d7ba439942f58a6f36d89d6a7ddeec7b";
const DATE = "2026-10-11", CUTOFF = "2025-10-11", CAP = 2;
const PUBLIC_DOMAINS = new Set(["steamcommunity.com","store.steampowered.com","stopgame.ru","reddit.com","ptt.cc","gog.com","steamdb.info"]);
const MANUAL_CHECKS = Object.freeze({
  "1119710:source-002": {status:"not_verifiable",reason:"WEB_TOOL_UNABLE_TO_ACCESS_ORIGINAL_LOCATOR"},
  "1119710:source-004": {status:"checked",reason:"PUBLIC_EXACT_APP_DISCUSSION_PARENT_VISIBLE",page_date_metadata:"2020-02-06"},
  "1202690:source-002": {status:"checked",reason:"PUBLIC_EXACT_GAME_USER_REVIEW_PARENT_VISIBLE",page_date_metadata:"2025-09-23"},
  "1202690:source-003": {status:"not_verifiable",reason:"PUBLIC_SITE_LOGIN_REQUIRED"}
});
function bucket(value) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return "unknown";
  const t=Date.parse(value+"T00:00:00Z");
  if (!Number.isFinite(t) || new Date(t).toISOString().slice(0,10)!==value || value>DATE) return "unknown";
  return value>=CUTOFF?"recent":"older";
}
function count(values) { const out={};for(const x of values){out[x]=(out[x]||0)+1}return Object.fromEntries(Object.keys(out).sort().map(k=>[k,out[k]]));}
function domainOf(s) {
  const d=String(s.domain||"").toLowerCase().replace(/^www\./,"").replace(/\.$/,"");
  return PUBLIC_DOMAINS.has(d)?d:"other_public_domain";
}
function privateLocator(s) {
  const loc=String(s.url||s.public_ref||"");
  if (/\/(id|profiles?|users?|u|authors?)\/[^/]+/i.test(loc) || /(?:\?|&)(user|user_id|username|steamid|profile|author|author_id)=/i.test(loc)) return true;
  if (/\b(?:username|display.name|author|contributor|profile)\s*[:=]|(?:^|\s)@[A-Za-z0-9_]{2,}/i.test(loc)) return true;
  return false;
}
function parentKey(s) {
  // Used only transiently for claim-level alias collapse, never emitted or hashed as person ID.
  if(s.url) {
    try {
      const match=String(s.url).match(/^https:\/\/([^\/?#]+)(\/[^?#]*)?/i);
      if(!match) return "invalid:"+s.source_id;
      let host=match[1].toLowerCase().replace(/^www\./,"");
      let path=(match[2]||"/").toLowerCase().replace(/\/+$/,"");
      if(host==="steamcommunity.com" && /^\/app\/\d+\/(?:positive|negative)?reviews$/.test(path))
        path=path.replace(/\/(?:positive|negative)?reviews$/,"/reviews");
      return host+path;
    } catch { return "invalid:"+s.source_id; }
  }
  return "ref:"+String(s.public_ref||s.source_id).trim().toLowerCase();
}
function projectGame(d, appid, sha, sequence) {
  if(String(d.appid)!==String(appid) || !Array.isArray(d.provenance?.sources) ||
     !Array.isArray(d.provenance?.player_feedback_records) || !Array.isArray(d.observations)) throw Error("invalid pinned dossier "+appid);
  const src=d.provenance.sources, records=d.provenance.player_feedback_records;
  const ids=new Set(), parents=new Map();
  const sources=src.map((s,i)=>{
    if(!s.source_id || ids.has(s.source_id)) throw Error("duplicate/missing source ID "+appid);
    ids.add(s.source_id);
    const isPlayer=s.player_feedback===true;
    let physical=null;
    if(isPlayer) {
      const key=parentKey(s);
      if(!parents.has(key))parents.set(key,"parent-"+String(parents.size+1).padStart(3,"0"));
      physical=parents.get(key);
    }
    return {source_id:s.source_id,source_type:String(s.source_type||"unknown"),domain:domainOf(s),
      locator_kind:s.url?"url":s.public_ref?"public_ref":"missing",
      player_feedback_claimed:isPlayer,physical_parent_local:physical,
      source_date_bucket:bucket(s.publication_date),language_claim:String(s.language||"unknown"),
      privacy_limited:privateLocator(s)};
  });
  const seen=new Set(),probes=[];let skipped=0;
  for(const s of sources.filter(x=>x.player_feedback_claimed)) {
    if(seen.has(s.physical_parent_local))continue;
    seen.add(s.physical_parent_local);
    if(probes.length>=CAP){skipped++;continue}
    const manual=MANUAL_CHECKS[String(appid)+":"+s.source_id];
    const status=s.privacy_limited?"privacy_limited":manual?manual.status:"not_measured";
    const reason=s.privacy_limited?"PERSON_SCOPED_LOCATOR":manual?manual.reason:"BOUNDED_PUBLIC_RETRIEVAL_NOT_PERFORMED";
    const p={source_id:s.source_id,physical_parent_local:s.physical_parent_local,source_type:s.source_type,
      domain:s.domain,status,reason,checked_on_utc:manual?DATE:null};
    if(manual?.page_date_metadata && status==="checked")p.page_date_metadata=manual.page_date_metadata;
    probes.push(p);
  }
  const sentiments=d.observations.map((o,i)=>({index:i,sentiment:o.sentiment,category:o.category}));
  const negatives=sentiments.filter(x=>x.sentiment==="negative"||x.sentiment==="mixed")
    .map(x=>({observation_index:x.index,sentiment:x.sentiment,category:x.category}));
  const russian=records.some(r=>r.language==="russian")?"claimed_present":
    d.evidence?.russian_attempt==="no_existence_signal"?"claimed_absent":"unknown";
  const check=probes.filter(p=>p.status==="checked").length;
  const attempted=probes.filter(p=>p.checked_on_utc!==null).length;
  return {
    sequence,appid:String(appid),dossier_git_blob_sha:sha,
    source_claims:{
      total_sources:src.length,claimed_player_source_rows:sources.filter(s=>s.player_feedback_claimed).length,
      claimed_distinct_physical_parents:parents.size,source_types:count(sources.map(s=>s.source_type)),
      source_link_kinds:count(sources.map(s=>s.locator_kind)),source_date_buckets:count(sources.map(s=>s.source_date_bucket)),
      feedback_records:records.length,feedback_date_buckets:count(records.map(r=>bucket(r.publication_date))),
      feedback_acquisition_modes:count(records.map(r=>r.acquisition_mode||"unknown")),
      feedback_languages:count(records.map(r=>r.language||"unknown")),russian_feedback_language:russian,
      negative_observations:negatives.filter(x=>x.sentiment==="negative").length,
      mixed_observations:negatives.filter(x=>x.sentiment==="mixed").length,
      negative_mixed_observation_refs:negatives,
      conflict_rows:Array.isArray(d.conflicts)?d.conflicts.length:0,
      technical_or_localization_category_rows:sentiments.filter(x=>/^(?:technical|performance|compatibility|localization|regional)$/.test(x.category)).length,
      coverage_unknown_dimensions:(d.evidence?.coverage?.dimensions||[]).filter(x=>!["covered","not_material_or_not_applicable"].includes(x.state)).length,
      research_state_claim:String(d.evidence?.research_state||"unknown"),
      russian_attempt_claim:String(d.evidence?.russian_attempt||"unknown"),
      sources
    },
    external_source_checks:{
      cap:CAP,eligible_distinct_claimed_parents:parents.size,selected_for_probe:probes.length,
      skipped_due_to_cap:skipped,attempted,checked:check,
      verified_distinct_parents:check>0?check:null,
      status:check?"partially_checked":attempted?"not_verifiable":"not_measured",
      probes
    },
    limits:{source_claims_are_not_independent_authenticity:true,semantic_contents_not_evaluated:true,
      independent_russian_feedback_language:"unknown",independent_negative_mixed_truth:"not_evaluated"}
  };
}
function finish(report){
 const expected=report.groups.flatMap(g=>g.appids.map(id=>g.sequence+":"+id));
 const seen=new Set(report.games.map(g=>g.sequence+":"+g.appid));
 if(expected.length!==60 || seen.size!==60 || expected.some(k=>!seen.has(k)) || report.games.length!==60)throw Error("not all original 60 games inspected");
 const byKey=new Map(report.games.map(g=>[g.sequence+":"+g.appid,g]));
 report.games=expected.map(k=>byKey.get(k));
 for(const grp of report.groups){
   const games=report.games.filter(g=>g.sequence===grp.sequence);
   const checked=games.reduce((n,g)=>n+g.external_source_checks.checked,0);
   grp.metadata_games_inspected=games.length;
   grp.claimed_player_parents=games.reduce((n,g)=>n+g.source_claims.claimed_distinct_physical_parents,0);
   grp.source_claim_rows=games.reduce((n,g)=>n+g.source_claims.total_sources,0);
   grp.player_record_claim_rows=games.reduce((n,g)=>n+g.source_claims.feedback_records,0);
   grp.claimed_negative_mixed_observations=games.reduce((n,g)=>n+g.source_claims.negative_observations+g.source_claims.mixed_observations,0);
   grp.any_claimed_russian=games.some(g=>g.source_claims.russian_feedback_language==="claimed_present");
   grp.feedback_date_buckets=count(games.flatMap(g=>Object.entries(g.source_claims.feedback_date_buckets).flatMap(([k,v])=>Array(v).fill(k))));
   grp.probes_checked=checked;
   grp.probes_selected=games.reduce((n,g)=>n+g.external_source_checks.selected_for_probe,0);
   grp.provenance_stratum=checked?"partially_checked_external_metadata_only":"claims_only_external_not_measured";
 }
 const arr=report.games;
 report.totals={
   original_groups:20,original_games:60,metadata_games_inspected:60,
   claimed_sources:arr.reduce((n,g)=>n+g.source_claims.total_sources,0),
   claimed_player_source_rows:arr.reduce((n,g)=>n+g.source_claims.claimed_player_source_rows,0),
   claimed_distinct_parent_sum_not_independent:arr.reduce((n,g)=>n+g.source_claims.claimed_distinct_physical_parents,0),
   claimed_feedback_records:arr.reduce((n,g)=>n+g.source_claims.feedback_records,0),
   claimed_negative_observations:arr.reduce((n,g)=>n+g.source_claims.negative_observations,0),
   claimed_mixed_observations:arr.reduce((n,g)=>n+g.source_claims.mixed_observations,0),
   claimed_russian_games:arr.filter(g=>g.source_claims.russian_feedback_language==="claimed_present").length,
   feedback_date_buckets:count(arr.flatMap(g=>Object.entries(g.source_claims.feedback_date_buckets).flatMap(([k,v])=>Array(v).fill(k)))),
   candidate_parent_probes_selected:arr.reduce((n,g)=>n+g.external_source_checks.selected_for_probe,0),
   candidate_parent_probes_skipped_due_to_cap:arr.reduce((n,g)=>n+g.external_source_checks.skipped_due_to_cap,0),
   independent_attempted:arr.reduce((n,g)=>n+g.external_source_checks.attempted,0),
   independently_checked_available:arr.reduce((n,g)=>n+g.external_source_checks.checked,0),
   unverified_or_blocked_attempts:arr.reduce((n,g)=>n+g.external_source_checks.attempted-g.external_source_checks.checked,0),
   probes_not_measured:arr.reduce((n,g)=>n+g.external_source_checks.probes.filter(p=>p.status==="not_measured").length,0),
   probes_privacy_limited:arr.reduce((n,g)=>n+g.external_source_checks.probes.filter(p=>p.status==="privacy_limited").length,0),
   independently_checked_games:arr.filter(g=>g.external_source_checks.checked>0).length,
   groups_with_any_independent_parent_check:report.groups.filter(g=>g.probes_checked>0).length,
   semantically_verified_reviews:0,
   pilot_authorized:false,trial_cohort_finalized:false,semantic_quality_verified:false
 };
 report.status="complete_metadata_claims_external_partially_measured";
 return report;
}
module.exports={PIN,WORK_BLOB,AUDIT_BLOB,DATE,CUTOFF,CAP,bucket,privateLocator,parentKey,projectGame,finish};
if(typeof require!=="undefined" && typeof process!=="undefined" && require.main===module){
  const cp=require("node:child_process"),fs=require("node:fs");
  function git(args){return cp.execFileSync("git",args,{encoding:"utf8",maxBuffer:5*1024*1024}).trimEnd()}
  if(process.argv.length!==4){console.error("Usage: node dossier_shadow_preoutput_source_audit.js <pinned_repo_dir> <committed_json_path>");process.exit(2)}
  const repo=process.argv[2],report=JSON.parse(fs.readFileSync(process.argv[3],"utf8"));
  function run(...args){return git(["-C",repo,...args])}
  if(run("rev-parse",PIN+":data/production/pre_ai/taste_steam_review_dossier_work.json")!==WORK_BLOB||
     run("rev-parse",PIN+":data/audit/taste_steam_review_dossier_frozen_invocations.jsonl")!==AUDIT_BLOB)throw Error("historical pinned blobs changed");
  const work=JSON.parse(run("show",PIN+":data/production/pre_ai/taste_steam_review_dossier_work.json"));
  const accepted=new Set(work.group_progress.groups.filter(x=>x.state==="accepted").map(x=>x.sequence));
  const frame=work.submission_group_plan.groups.filter(g=>accepted.has(g.sequence));
  if(frame.length!==20 || frame.map(g=>g.sequence).join(",")!==report.groups.map(g=>g.sequence).join(","))throw Error("wrong historical group frame");
  const expected=new Map();
  for(const g of frame)for(const id of g.appids) {
    const path="data/cache/taste_steam_review_dossiers/App_"+id+".json";
    expected.set(g.sequence+":"+id,projectGame(JSON.parse(run("show",PIN+":"+path)),id,run("rev-parse",PIN+":"+path),g.sequence));
  }
  for(const item of report.games)if(JSON.stringify(expected.get(item.sequence+":"+item.appid))!==JSON.stringify(item))throw Error("game projection drift "+item.appid);
  const fresh=finish({...report,groups:report.groups.map(g=>({sequence:g.sequence,group_sha256:g.group_sha256,appids:g.appids,metadata_games_inspected:0,provenance_stratum:"not_measured"})),games:Array.from(expected.values())});
  if(JSON.stringify(fresh.totals)!==JSON.stringify(report.totals))throw Error("aggregate drift");
  console.log("PASS historical frozen source metadata frame 20 groups/60 games; no HTTP or semantic analysis");
}
