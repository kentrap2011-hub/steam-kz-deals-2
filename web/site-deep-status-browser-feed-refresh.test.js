'use strict';
// PR-only synthetic browser: actual app.js queue/render + actual feed-bootstrap.js,
// in-memory localStorage/CacheStorage, no Steam/GitHub requests or real browser data.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {createFeedBootstrapResilience} = require('./feed-bootstrap.js');
const progressive = require('./progressive-personalization-ui.js');
const appSource=fs.readFileSync(path.join(__dirname,'app.js'),'utf8');
const DATA_ENDPOINT='https://example.test/steam-kz-deals-2/data/current.json';
const STATUS_URL='https://example.test/steam-kz-deals-2/data/status.json';
const ID='game:1574580';
const stamp=(minute)=>`2026-10-11T12:${String(minute).padStart(2,'0')}:00Z`;
function clone(value){return JSON.parse(JSON.stringify(value))}
function response(payload){
  return {ok:true,status:200,clone(){return response(payload)},async json(){return clone(payload)}};
}
function deferred(){
  let resolve;const promise=new Promise(r=>resolve=r);
  return {promise,resolve};
}
function payload(minute,lit=false){
  return {
    generated_at_utc:stamp(minute),
    source_mailing_updated_at_utc:stamp(minute),
    production_contract:{source_giveaway_snapshot_blob_sha:'sha-1'},
    processing_status:{deep_completed_fit_count:lit?1:0},
    items:[
      {id:'game:other',title:'Other',analysis_state:'not_analyzed',ranking_stage:'not_analyzed',
       ranking_stage_rank:4,priority_rank:2,sale_end_utc:'2026-11-01T12:00:00Z',screenshots:[]},
      {id:ID,title:'Strange Horticulture',analysis_state:lit?'analyzed_fit':'not_analyzed',
       deep_stage_state:lit?'completed':'eligible_or_pending',deep_stage_outcome:lit?'fit':null,
       ranking_stage:lit?'deep_fit':'not_analyzed',ranking_stage_rank:lit?1:4,priority_rank:1,
       total_score:lit?88:null,sale_end_utc:'2026-11-01T12:00:00Z',screenshots:[]},
    ],
  };
}
function node(initialHidden=false){
  const flags=new Set(initialHidden?['hidden']:[]);
  const listeners={};
  return {
    textContent:'',innerHTML:'',value:'',style:{},dataset:{},disabled:false,
    classList:{
      contains(k){return flags.has(k)},add(k){flags.add(k)},remove(k){flags.delete(k)},
      toggle(k,force){const next=force===undefined?!flags.has(k):!!force;if(next)flags.add(k);else flags.delete(k);return next},
    },
    addEventListener(name,fn){listeners[name]=fn},
    removeEventListener(name,fn){if(listeners[name]===fn)delete listeners[name]},
    dispatch(name,arg={}){listeners[name]?.(arg)},
    setAttribute(){},removeAttribute(){},querySelector(){return null},focus(){},
  };
}
function createBrowser(cachedPayload, network, saved){
  const nodes=new Map();
  const get=id=>{
    if(!nodes.has(id))nodes.set(id,node(['gameCard','emptyFeed','feedSyncNotice'].includes(id)));
    return nodes.get(id);
  };
  const docListeners={};const winListeners={};
  const document={
    visibilityState:'visible',getElementById:get,querySelectorAll(){return []},
    addEventListener(name,fn){docListeners[name]=fn},removeEventListener(name){delete docListeners[name]},
    emit(name,arg){docListeners[name]?.(arg)},
  };
  const stored=new Map(saved?[['steam-deals-visual-state-v1',JSON.stringify(saved)]]:[]);
  let cachePayload=cachedPayload&&clone(cachedPayload);
  const cache={
    async match(){return cachePayload?response(cachePayload):undefined},
    async put(_,r){cachePayload=await r.json()},
    async delete(){cachePayload=null;return true},
  };
  const win={
    location:{href:'https://example.test/steam-kz-deals-2/'},
    ProgressivePersonalizationUI:progressive,
    addEventListener(name,fn){winListeners[name]=fn},
    removeEventListener(name){delete winListeners[name]},
    emit(name,arg){winListeners[name]?.(arg)},scrollTo(){},
  };
  const nativeFetch=async input=>{
    const target=String(input);
    if(target.endsWith('status.json')){
      return response({generated_at_utc:stamp(59),processing_status:{deep_completed_fit_count:99}});
    }
    assert.equal(new URL(target,win.location.href).href,DATA_ENDPOINT);
    return network();
  };
  const controller=createFeedBootstrapResilience({
    window:win,document,fetch:nativeFetch,caches:{async open(){return cache}},
    AbortController,retryDelayMs:0,timeoutMs:1500,
    console:{info(){},warn(...args){console.error('[synthetic bootstrap warning]',...args)},log(){}},
  });
  controller.install();
  const context=vm.createContext({
    window:win,document,console,Image:class{},Date,Intl,setTimeout,clearTimeout,
    localStorage:{getItem:k=>stored.get(k)||null,setItem:(k,v)=>stored.set(k,v)},
    fetch:(...args)=>win.fetch(...args),
  });
  vm.runInContext(appSource,context,{filename:'app.js',timeout:2000});
  win.init=()=>vm.runInContext('init()',context);
  const snapshot=()=>JSON.parse(vm.runInContext(`JSON.stringify({
    item:byId.get('${ID}'),ids:state.queue.ids,cursor:state.queue.cursor,
    games:state.games,settings:state.settings,
    statistics:siteStatus?.processing_status,
  })`,context));
  return {win,document,nodes:get,controller,cache:()=>cachePayload,stored,snapshot};
}
async function until(predicate,message){
  for(let i=0;i<90;i++){
    if(predicate())return;
    await new Promise(resolve=>setTimeout(resolve,10));
  }
  throw new Error('Timed out: '+(typeof message==='function'?message():message));
}
const saved={
  games:{
    [ID]:{status:'final',seen:7,first_source:'older',manual_end_at:3000},
    'game:other':{status:'liked',seen:3,first_source:'older'},
  },
  settings:{urgency_first:true},
  queue:{source:'older',signature:'previous',version:6,ids:['game:other',ID],cursor:1},
};
function assertSaved(browser){
  const snap=browser.snapshot();
  assert.equal(snap.games[ID].manual_end_at,3000,'manual end is never deleted');
  assert.equal(snap.games[ID].status,'final');
  assert.equal(snap.games[ID].seen,7);
  assert.equal(snap.games['game:other'].status,'liked');
  assert.equal(snap.settings.urgency_first,true);
  assert.equal(snap.ids.at(-1),ID,'intentional manual deferral survives Deep promotion');
  assert.equal(snap.ids[snap.cursor],ID,'open game survives queue rebuild');
}
async function cacheOldToFresh(){
  const gate=deferred();
  const browser=createBrowser(payload(1,false),()=>gate.promise,saved);
  await until(()=>browser.controller.state.source==='cache'&&browser.nodes('stageIndicators').innerHTML.includes('Глубокий разбор:'),'cached render');
  assert.match(browser.nodes('stageIndicators').innerHTML,/stage-indicator unlit/);
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'checking');
  assert.match(browser.nodes('feedSyncText').textContent,/Статистика может быть новее/);
  assert.equal(browser.snapshot().statistics.deep_completed_fit_count,99,'statistics is independently newer');
  assertSaved(browser);
  gate.resolve(response(payload(2,true)));
  await until(()=>browser.controller.state.refreshOutcome==='updated',()=>('background update: '+JSON.stringify(browser.controller.state)+' / DOM '+browser.nodes('stageIndicators').innerHTML.slice(0,400)));
  assert.match(browser.nodes('stageIndicators').innerHTML,/lit positive[^>]*title="Глубокий разбор: завершён — подходит"/);
  assert.equal(browser.controller.state.source,'refresh');
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'current');
  assertSaved(browser);
  assert.equal(browser.cache().items.find(x=>x.id===ID).deep_stage_state,'completed');
  await browser.win.init();
  assert.match(browser.nodes('stageIndicators').innerHTML,/Глубокий разбор: завершён — подходит/,'init re-entry does not replay older bootstrap cache');
  assertSaved(browser);
}
async function offlineRetryAndResume(){
  let offline=true;let calls=0;
  const browser=createBrowser(payload(1,false),async()=>{
    calls++;if(offline)throw Error('offline');return response(payload(2,true));
  },saved);
  await until(()=>browser.controller.state.refreshOutcome==='failed','offline refresh exhausted');
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'stale');
  assert.match(browser.nodes('feedSyncText').textContent,/отметки Deep могут устареть/);
  assert.equal(browser.snapshot().item.deep_stage_state,'eligible_or_pending');
  assertSaved(browser);
  offline=false;
  browser.nodes('feedRefreshBtn').dispatch('click');
  await until(()=>browser.controller.state.refreshOutcome==='updated','manual retry');
  assert.equal(browser.snapshot().item.deep_stage_state,'completed');
  assertSaved(browser);
  // Another offline cached session recovers on mobile tab resume.
  let interrupted=true;
  const reopened=createBrowser(payload(1,false),async()=>{
    if(interrupted)throw Error('suspended');return response(payload(3,true));
  },saved);
  await until(()=>reopened.controller.state.refreshOutcome==='failed','offline reopened');
  interrupted=false;
  reopened.document.visibilityState='hidden';
  reopened.document.emit('visibilitychange');
  reopened.document.visibilityState='visible';
  reopened.document.emit('visibilitychange');
  await until(()=>reopened.controller.state.refreshOutcome==='updated','visibility resume');
  assertSaved(reopened);
  assert.ok(calls>=3,'bounded retry and manual recovery both reach network');
}
async function downgradeRejectedAndBadData(){
  let networkPayload=payload(1,false);
  const browser=createBrowser(payload(3,true),async()=>response(networkPayload),saved);
  await until(()=>browser.controller.state.refreshOutcome==='older','older network rejected');
  assert.equal(browser.snapshot().item.deep_stage_state,'completed');
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'older');
  assertSaved(browser);
  networkPayload={...payload(4,true),items:[{...payload(4,true).items[0],id:''}]};
  await browser.controller.retry();
  assert.equal(browser.controller.state.refreshOutcome,'failed','invalid network shape rejected');
  assert.equal(browser.snapshot().item.deep_stage_state,'completed');
  networkPayload=payload(5,true);
  await browser.controller.retry();
  assert.equal(browser.controller.state.refreshOutcome,'updated');
  assertSaved(browser);
}
async function freshNetworkAndMalformedCache(){
  const browser=createBrowser(null,async()=>response(payload(4,true)),saved);
  await until(()=>browser.controller.state.source==='network','fresh network');
  assert.equal(browser.snapshot().item.deep_stage_state,'completed');
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'current');
  assertSaved(browser);
  const corrupt={...payload(1,false),generated_at_utc:'unknown'};
  const repaired=createBrowser(corrupt,async()=>response(payload(4,true)),saved);
  await until(()=>repaired.controller.state.source==='network','corrupt cache bypass');
  assert.equal(repaired.snapshot().item.deep_stage_state,'completed');
  assertSaved(repaired);
}
async function firstVisitOutageRetry(){
  let offline=true;
  const browser=createBrowser(null,async()=>{
    if(offline)throw Error('offline on first visit');
    return response(payload(5,true));
  },saved);
  await until(()=>browser.controller.state.status==='failed','first visit offline');
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'failed','offline-first visit must expose retry');
  assert.match(browser.nodes('feedSyncText').textContent,/Не удалось загрузить ленту/);
  offline=false;
  await browser.controller.retry();
  await until(()=>browser.controller.state.source==='network','first visit successful retry');
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'current');
  assert.equal(browser.snapshot().item.deep_stage_state,'completed');
  assertSaved(browser);
}
async function main(){
  await firstVisitOutageRetry();
  await cacheOldToFresh();
  await offlineRetryAndResume();
  await downgradeRejectedAndBadData();
  await freshNetworkAndMalformedCache();
  const direct=createFeedBootstrapResilience({fetch:async()=>response(payload(1)),AbortController});
  assert.equal(direct.validatePayload({...payload(1),generated_at_utc:'wrong'}),false);
  assert.equal(direct.validatePayload({...payload(1),items:[{id:ID},{id:ID}]}),false);
  assert.equal(progressive.stageIndicators(payload(2,true).items.find(x=>x.id===ID))[2].lit,true);
  console.log('PASS: stale Deep feed, user saved state, retry/resume, freshness/identity and init re-entry');
}
main().catch(error=>{console.error(error);process.exitCode=1});
