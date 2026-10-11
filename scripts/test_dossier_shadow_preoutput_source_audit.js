"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const audit=require("./dossier_shadow_preoutput_source_audit.js");
function fixture(id="999001", sources=null){
  return {
    appid:id,observations:[
      {category:"mechanics",sentiment:"positive"},
      {category:"localization",sentiment:"negative"},
      {category:"difficulty",sentiment:"mixed"}
    ],conflicts:[],
    provenance:{
      sources:sources||[
        {source_id:"source-001",source_type:"steam_reviews",domain:"steamcommunity.com",url:"https://steamcommunity.com/app/"+id+"/positivereviews/?l=russian",player_feedback:true,publication_date:null,language:"mixed"},
        {source_id:"source-002",source_type:"steam_reviews",domain:"steamcommunity.com",url:"https://steamcommunity.com/app/"+id+"/negativereviews/?p=1",player_feedback:true,publication_date:null,language:"non_russian"},
        {source_id:"source-003",source_type:"forum",domain:"ptt.cc",url:"https://www.ptt.cc/bbs/Steam/M.12345678.html",player_feedback:true,publication_date:"2025-10-11",language:"russian"},
        {source_id:"source-004",source_type:"forum",domain:"reddit.com",url:"https://www.reddit.com/r/games/comments/synthetic",player_feedback:true,publication_date:"2020-01-01",language:"unknown"}
      ],
      player_feedback_records:[
        {source_id:"source-001",language:"russian",publication_date:"2025-10-11",acquisition_mode:"inspected_collection_item"},
        {source_id:"source-003",language:"non_russian",publication_date:"2025-10-10",acquisition_mode:"search_result_observation"},
        {source_id:"source-004",language:"unknown",publication_date:null,acquisition_mode:"stable_item"}
      ]
    },
    evidence:{russian_attempt:"found_and_used",research_state:"evidence_stable",
      coverage:{dimensions:[{state:"unknown"},{state:"covered"},{state:"not_material_or_not_applicable"}]}}
  };
}
test("PIN-01 exact immutable source frame",()=>{
 assert.equal(audit.PIN,"95a4bf4990a60082ecb3302da5bc7f23b618d93e");
 assert.equal(audit.CAP,2);
});
test("TIME-02 date buckets fixed observation-day boundary",()=>{
 assert.equal(audit.bucket("2025-10-10"),"older");
 assert.equal(audit.bucket("2025-10-11"),"recent");
 assert.equal(audit.bucket("2026-10-12"),"unknown");
 assert.equal(audit.bucket(null),"unknown");
 assert.equal(audit.bucket("2025-02-30"),"unknown");
});
test("PARENT-03 positive and negative filter aliases not independent physical sources",()=>{
 const g=audit.projectGame(fixture(),"999001","abc",1);
 assert.equal(g.source_claims.claimed_distinct_physical_parents,3);
 assert.deepEqual(g.external_source_checks.probes.map(x=>x.source_id),["source-001","source-003"]);
 assert.equal(g.external_source_checks.skipped_due_to_cap,1);
 assert.equal(g.external_source_checks.checked,0);
 assert.equal(g.external_source_checks.verified_distinct_parents,null);
});
test("PRIV-04 redact personal locator even on otherwise public platform",()=>{
 const s=fixture("999002");
 s.provenance.sources[0].url="https://steamcommunity.com/profiles/76561198000000001";
 const g=audit.projectGame(s,"999002","abc",1);
 assert.equal(g.source_claims.sources[0].privacy_limited,true);
 assert.equal(g.external_source_checks.probes[0].status,"privacy_limited");
 const serialized=JSON.stringify(g);
 assert.equal(serialized.includes("76561198000000001"),false);
 assert.equal(serialized.includes("https://"),false);
 assert.equal(serialized.includes("synthetic"),false);
});
test("LOCALE-05 claimed Russian not externally corroborated",()=>{
 const g=audit.projectGame(fixture(),"999001","abc",1);
 assert.equal(g.source_claims.russian_feedback_language,"claimed_present");
 assert.equal(g.limits.independent_russian_feedback_language,"unknown");
 assert.deepEqual(g.source_claims.feedback_date_buckets,{older:1,recent:1,unknown:1});
 assert.equal(g.source_claims.negative_observations,1);
 assert.equal(g.source_claims.mixed_observations,1);
});
test("IDENT-06 wrong AppID and duplicate local IDs fail closed",()=>{
 assert.throws(()=>audit.projectGame(fixture(),"123","abc",1));
 const f=fixture();f.provenance.sources[1].source_id="source-001";
 assert.throws(()=>audit.projectGame(f,"999001","abc",1));
});
test("ORDER-07 missing game, duplicates and exclusions do not pass complete-frame gate",()=>{
 const r={groups:[{sequence:1,appids:["1","2","3"]}],games:[]};
 assert.throws(()=>audit.finish(r),/not all original 60/);
});
test("WEB-08 probe receipt applies to exact original source local key only",()=>{
 const f=fixture("1119710");
 const x=audit.projectGame(f,"1119710","abc",1);
 assert.equal(x.external_source_checks.checked,0); // its synthetic IDs are NOT real checked URLs
 // The receipt for source-002 is explicitly not_verifiable, not a fabricated pass.
 assert.equal(x.external_source_checks.probes[0].status,"not_measured");
});
