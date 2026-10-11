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
function node(initialHidden=false,bubble){
  const flags=new Set(initialHidden?['hidden']:[]);
  const listeners={};
  return {
    textContent:'',innerHTML:'',value:'',style:{},dataset:{},disabled:false,attributes:{},parentElement:null,focusCount:0,
    classList:{
      contains(k){return flags.has(k)},add(k){flags.add(k)},remove(k){flags.delete(k)},
      toggle(k,force){const next=force===undefined?!flags.has(k):!!force;if(next)flags.add(k);else flags.delete(k);return next},
    },
    contains(target){for(let n=target;n;n=n.parentElement)if(n===this)return true;return false},
    closest(){return null}, // Delegated app.js card handlers, unrelated to these tap tests.
    addEventListener(name,fn){listeners[name]=fn},
    removeEventListener(name,fn){if(listeners[name]===fn)delete listeners[name]},
    localDispatch(name,event){listeners[name]?.(event)},
    dispatch(name,arg={}){
      const event={target:this,...arg};
      for(let n=this;n;n=n.parentElement)n.localDispatch(name,event);
      if(name==='click')bubble('click',event); // Real DOM bubbles touch-generated and opener clicks.
      return event;
    },
    setAttribute(k,v){this.attributes[k]=String(v)},getAttribute(k){return this.attributes[k]??null},removeAttribute(k){delete this.attributes[k]},querySelector(){return null},
    focus(){this.focusCount++},
  };
}
function createBrowser(cachedPayload, network, saved){
  const nodes=new Map();
  const get=id=>{
    if(!nodes.has(id)){
      const n=node(['gameCard','emptyFeed','feedSyncNotice'].includes(id),(name,event)=>document.emit(name,event));
      nodes.set(id,n);
      if(['feedSyncText','feedRefreshBtn'].includes(id))n.parentElement=get('feedSyncDetails');
      if(id==='feedSyncSymbol')n.parentElement=get('feedStatusToggle');
      if(['feedSyncDetails','feedStatusToggle','feedSyncLive'].includes(id))n.parentElement=get('feedSyncNotice');
    }
    return nodes.get(id);
  };
  const docListeners={};const winListeners={};
  const document={
    visibilityState:'visible',getElementById:get,
    querySelectorAll(selector){
      if(selector!=='.tab')return [];
      const feed=get('tabFeed'),giveaway=get('tabGiveaway');
      feed.dataset.tab='feed';giveaway.dataset.tab='giveaway';
      return [feed,giveaway];
    },
    addEventListener(name,fn){(docListeners[name]??=new Set()).add(fn)},
    removeEventListener(name,fn){docListeners[name]?.delete(fn)},
    emit(name,arg){for(const fn of [...(docListeners[name]||[])])fn(arg)},
    listenerCount(name){return docListeners[name]?.size||0},
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
    now:()=>Date.parse('2026-10-11T12:10:00Z'),
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
    item:byId.get('${ID}'),ids:state.queue.ids,cursor:state.queue.cursor,tab:currentTab,
    games:state.games,settings:state.settings,
    statistics:siteStatus?.processing_status,
  })`,context));
  return {win,document,nodes:get,controller,cache:()=>cachePayload,stored,snapshot,
    navigate:delta=>vm.runInContext('navigate('+Number(delta)+')',context)};
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
  assert.match(browser.nodes('feedSyncText').textContent,/Статистика загружается отдельно/);
  assert.equal(browser.snapshot().statistics.deep_completed_fit_count,99,'statistics is independently newer');
  assertSaved(browser);
  gate.resolve(response(payload(2,true)));
  await until(()=>browser.controller.state.refreshOutcome==='updated',()=>('background update: '+JSON.stringify(browser.controller.state)+' / DOM '+browser.nodes('stageIndicators').innerHTML.slice(0,400)));
  assert.match(browser.nodes('stageIndicators').innerHTML,/lit positive[^>]*title="Глубокий разбор: завершён — подходит"/);
  assert.equal(browser.controller.state.source,'refresh');
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'network_verified');
  assertSaved(browser);
  assert.equal(browser.cache().items.find(x=>x.id===ID).deep_stage_state,'completed');
  await browser.win.init();
  assert.match(browser.nodes('stageIndicators').innerHTML,/Глубокий разбор: завершён — подходит/,'init re-entry does not replay older bootstrap cache');
  assertSaved(browser);
  // Simulate the mobile swipe navigation path after applying a newer producer.
  browser.navigate(-1);
  assert.equal(browser.snapshot().ids[browser.snapshot().cursor],'game:other');
  browser.navigate(1);
  assert.equal(browser.snapshot().ids[browser.snapshot().cursor],ID);
  assert.equal(browser.snapshot().games[ID].manual_end_at,3000);
  assert.equal(browser.snapshot().games[ID].status,'final');
  assert.equal(browser.snapshot().games[ID].seen,8,'swipe-away marks seen once, never resets history');
  assert.equal(browser.snapshot().settings.urgency_first,true);
  assert.match(browser.nodes('stageIndicators').innerHTML,/Глубокий разбор: завершён — подходит/);
}
async function offlineRetryAndResume(){
  let offline=true;let calls=0;
  const browser=createBrowser(payload(1,false),async()=>{
    calls++;if(offline)throw Error('offline');return response(payload(2,true));
  },saved);
  await until(()=>browser.controller.state.refreshOutcome==='failed','offline refresh exhausted');
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'verification_failed');
  assert.match(browser.nodes('feedSyncText').textContent,/Проверка сети не удалась. Это не означает/);
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
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'confirmed_older_or_conflict');
  assert.equal(browser.nodes('feedRefreshBtn').disabled,false,'server-older conflict must retain an actionable retry');
  assertSaved(browser);
  networkPayload=payload(3,false); // same timestamp, different Deep material: never downgrade
  await browser.controller.retry();
  assert.equal(browser.controller.state.refreshOutcome,'ambiguous');
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'confirmed_older_or_conflict');
  assert.equal(browser.nodes('feedRefreshBtn').disabled,false,'same-time conflict remains retryable');
  assert.equal(browser.snapshot().item.deep_stage_state,'completed');
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
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'network_verified');
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
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'no_feed','offline-first visit must expose retry');
  assert.match(browser.nodes('feedSyncText').textContent,/Лента недоступна: загрузка не удалась/);
  offline=false;
  assert.equal(await browser.controller.retry(),true,'manual no-cache retry reports accepted render');
  await until(()=>browser.controller.state.source==='network','first visit successful retry');
  assert.equal(browser.nodes('feedSyncNotice').dataset.state,'network_verified');
  assert.equal(browser.snapshot().item.deep_stage_state,'completed');
  assertSaved(browser);
}
// Regression: a just-generated snapshot never becomes "outdated" on offline alone.
async function newlyGeneratedCacheVsOldProducer(){
  const recent=createBrowser(payload(9,false),async()=>{throw Error('network unavailable')},saved);
  await until(()=>recent.controller.state.refreshOutcome==='failed','recent cache verification failed');
  assert.equal(recent.controller.state.freshnessState,'verification_failed');
  assert.equal(recent.controller.state.lastVerifiedAt,null,'offline is not network verification');
  assert.match(recent.nodes('feedSyncText').textContent,/Это не означает, что лента устарела/);
  assert.doesNotMatch(recent.nodes('feedSyncText').textContent,/более суток/,'minutes-old cache is not aged');
  assertSaved(recent);

  const agedPayload=payload(9,false);
  agedPayload.generated_at_utc='2026-10-08T12:09:00Z';
  const aged=createBrowser(agedPayload,async()=>{throw Error('network unavailable')},saved);
  await until(()=>aged.controller.state.refreshOutcome==='failed','old cache verification failed');
  assert.equal(aged.controller.state.freshnessState,'verification_failed','age is not server-confirmed mismatch');
  assert.match(aged.nodes('feedSyncText').textContent,/Снимок создан более суток назад/);
  assertSaved(aged);
}
function assertPopover(browser,expanded,reason){
  assert.equal(browser.controller.state.statusExpanded,expanded,reason+' state');
  assert.equal(browser.nodes('feedStatusToggle').getAttribute('aria-expanded'),String(expanded),reason+' aria');
  assert.equal(browser.nodes('feedSyncDetails').classList.contains('hidden'),!expanded,reason+' visual');
}
async function equalNetworkAndInteractiveDetail(){
  const browser=createBrowser(payload(5,true),async()=>response(payload(5,true)),saved);
  await until(()=>browser.controller.state.refreshOutcome==='identical','verified equal');
  assert.equal(browser.controller.state.freshnessState,'network_verified');
  assert.equal(browser.controller.state.lastVerifiedAt,'2026-10-11T12:10:00.000Z');
  assert.match(browser.nodes('feedSyncText').textContent,/проверена по сети в/);
  assertPopover(browser,false,'initially collapsed');
  assert.match(browser.nodes('feedStatusToggle').getAttribute('aria-label'),/Показать подробности/);
  assert.equal(browser.document.listenerCount('click'),2,'app + one outside-dismiss listener');
  browser.controller.install();
  assert.equal(browser.document.listenerCount('click'),2,'repeated install does not duplicate handler');

  const toggle=browser.nodes('feedStatusToggle'),details=browser.nodes('feedSyncDetails');
  toggle.dispatch('click');
  assertPopover(browser,true,'opener click bubbles without closing');
  browser.nodes('feedSyncText').dispatch('click',{pointerType:'touch'});
  assertPopover(browser,true,'reading panel text');
  browser.nodes('feedRefreshBtn').dispatch('click',{pointerType:'touch'});
  assertPopover(browser,true,'retry button stays inside panel');
  await browser.controller.whenBackgroundIdle();
  assert.equal(browser.controller.state.refreshOutcome,'identical','inside retry checks data');
  assertPopover(browser,true,'refresh updates while open');
  browser.nodes('feedSyncSymbol').dispatch('click',{pointerType:'touch'});
  assertPopover(browser,false,'nested opener icon closes');

  toggle.dispatch('click');
  assertPopover(browser,true,'re-open');
  const backdrop=browser.nodes('blankBackground');
  const emptyTap=backdrop.dispatch('click',{pointerType:'touch'});
  assertPopover(browser,false,'touch click on empty background');
  assert.equal(emptyTap.defaultPrevented,undefined,'outside tap is not intercepted');
  toggle.dispatch('click');
  browser.nodes('gameCard').dispatch('click',{pointerType:'touch'});
  assertPopover(browser,false,'game card click dismisses');
  assertSaved(browser);

  toggle.dispatch('click');
  browser.nodes('tabGiveaway').dispatch('click',{pointerType:'touch'});
  assertPopover(browser,false,'navigation tab dismisses');
  assert.equal(browser.snapshot().tab,'giveaway','same click still navigates');
  browser.nodes('tabFeed').dispatch('click');
  toggle.dispatch('click');
  browser.nodes('statisticsBtn').dispatch('click');
  assertPopover(browser,false,'statistics navigation dismisses');
  assert.equal(browser.snapshot().tab,'statistics','same click still activates statistics');

  toggle.dispatch('click');
  toggle.dispatch('click');
  assertPopover(browser,false,'second toggle click closes');
  toggle.dispatch('click');
  const escape=details.dispatch('keydown',{key:'Escape',preventDefault(){this.defaultPrevented=true}});
  assertPopover(browser,false,'Escape closes');
  assert.equal(escape.defaultPrevented,true,'Escape prevents default');
  assert.equal(toggle.focusCount,1,'Escape restores opener focus');

  toggle.dispatch('click');
  browser.controller.destroy();
  assertPopover(browser,false,'destroy does not strand panel');
  assert.equal(browser.document.listenerCount('click'),1,'destroy retains app listener only');
  browser.controller.destroy();
  assert.equal(browser.document.listenerCount('click'),1,'repeated destroy remains idempotent');
  browser.controller.install();
  assert.equal(browser.document.listenerCount('click'),2,'reinstall adds one handler');
  toggle.dispatch('click');
  assertPopover(browser,true,'reinstalled controller opens once');
  backdrop.dispatch('click',{pointerType:'touch'});
  assertPopover(browser,false,'reinstalled outside handler dismisses');
  assertSaved(browser);
}
function compactMobileContract(){
  const html=fs.readFileSync(path.join(__dirname,'index.html'),'utf8');
  const css=fs.readFileSync(path.join(__dirname,'feed-sync.css'),'utf8');
  assert.match(html,/<meta name="viewport" content="width=device-width, initial-scale=1/);
  assert.match(html,/id="feedStatusToggle"[^>]*type="button"[\s\S]*?aria-expanded="false" aria-controls="feedSyncDetails"/);
  assert.match(html,/id="feedSyncLive"[^>]*role="status" aria-live="polite"/);
  assert.match(html,/id="feedSyncDetails"[^>]*class="feed-sync-details hidden"/);
  assert.match(html,/id="feedRefreshBtn"[^>]*type="button"/);
  assert.ok(html.indexOf('id="feedSyncNotice"')<html.indexOf('<nav class="tabs"'),'header indicator');
  assert.match(html,/feed-bootstrap.js\?v=popover-outside-dismiss-01/);
  assert.match(html,/feed-sync.css\?v=compact-freshness-ux-01/);
  assert.match(css,/width:44px;height:44px;min-width:44px;min-height:44px/,'touch target');
  assert.match(css,/\.feed-sync-details\{position:absolute;/,'detail never pushes cards down');
  assert.match(css,/@media\(max-width:430px\)/,'small screen incl. 350px');
  assert.doesNotMatch(css,/\.feed-sync\{[^}]*padding:7px/,'no persistent amber full-width card');
}
async function main(){
  compactMobileContract();
  await newlyGeneratedCacheVsOldProducer();
  await equalNetworkAndInteractiveDetail();
  await firstVisitOutageRetry();
  await cacheOldToFresh();
  await offlineRetryAndResume();
  await downgradeRejectedAndBadData();
  await freshNetworkAndMalformedCache();
  const direct=createFeedBootstrapResilience({fetch:async()=>response(payload(1)),AbortController});
  assert.equal(direct.validatePayload({...payload(1),generated_at_utc:'wrong'}),false);
  assert.equal(direct.validatePayload({...payload(1),items:[{id:ID},{id:ID}]}),false);
  assert.equal(progressive.stageIndicators(payload(2,true).items.find(x=>x.id===ID))[2].lit,true);
  console.log('PASS: Deep feed, mobile outside-tap dismissal, bubbling, navigation, lifecycle, accessibility, state, retry/resume and init re-entry');
}
main().catch(error=>{console.error(error);process.exitCode=1});
