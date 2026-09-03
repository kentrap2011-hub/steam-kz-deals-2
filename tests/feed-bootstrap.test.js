const assert=require('node:assert/strict');
const {createFeedBootstrapResilience}=require('../web/feed-bootstrap.js');

class FakeClassList{
  constructor(...initial){this.values=new Set(initial)}
  add(v){this.values.add(v)}
  remove(v){this.values.delete(v)}
  contains(v){return this.values.has(v)}
}
class FakeTarget{
  constructor(){this.listeners=new Map()}
  addEventListener(type,fn){if(!this.listeners.has(type))this.listeners.set(type,new Set());this.listeners.get(type).add(fn)}
  removeEventListener(type,fn){this.listeners.get(type)?.delete(fn)}
  dispatchEvent(event){for(const fn of this.listeners.get(event.type)||[])fn(event)}
}
class FakeResponse{
  constructor(payload,{status=200,ok=status>=200&&status<300,parseError=null}={}){this.payload=payload;this.status=status;this.ok=ok;this.parseError=parseError}
  clone(){return new FakeResponse(this.payload,{status:this.status,ok:this.ok,parseError:this.parseError})}
  async json(){if(this.parseError)throw this.parseError;return this.payload}
}
class MemoryCache{
  constructor(){this.map=new Map();this.putCount=0;this.deleteCount=0;this.failMatch=false;this.failPut=false}
  async match(key){if(this.failMatch)throw new Error('cache match failed');const value=this.map.get(String(key));return value?value.clone():undefined}
  async put(key,response){if(this.failPut)throw new Error('cache put failed');this.putCount++;this.map.set(String(key),response.clone())}
  async delete(key){this.deleteCount++;return this.map.delete(String(key))}
}
class MemoryCaches{
  constructor(cache=new MemoryCache()){this.cache=cache;this.failOpen=false}
  async open(){if(this.failOpen)throw new Error('cache open failed');return this.cache}
}

function quietConsole(){return {info(){},warn(){},log(){}}}
function tick(ms=0){return new Promise(resolve=>setTimeout(resolve,ms))}
function payload(version,ids=['A']){return {schema_version:4,generated_at_utc:version,source_mailing_updated_at_utc:version,item_count:ids.length,items:ids.map(id=>({id,title:id}))}}
function makeEnv(){
  const win=new FakeTarget();win.location={href:'https://example.test/app/'};
  const doc=new FakeTarget();doc.visibilityState='visible';
  const elements={
    gameCard:{classList:new FakeClassList('hidden')},
    emptyFeed:{classList:new FakeClassList('hidden'),textContent:'Активных игр в этой очереди сейчас нет.'},
    feedCount:{textContent:''},freshness:{textContent:''},
  };
  doc.getElementById=id=>elements[id]||null;
  return {win,doc,elements};
}
function installFakeApp(win,elements,{throwAfterJson=false}={}){
  const app={applyCount:0,currentTab:'feed',payload:null};
  win.init=async function(){
    try{
      const res=await win.fetch('data/current.json',{cache:'no-store'});if(!res.ok)throw new Error('http');
      const next=await res.json();if(throwAfterJson)throw new Error('render failed');
      app.applyCount++;app.payload=next;
      const visible=(next.items||[]).filter(x=>x&&x.id);elements.feedCount.textContent=`(${visible.length})`;
      if(visible.length){elements.gameCard.classList.remove('hidden');elements.emptyFeed.classList.add('hidden')}
      else{elements.gameCard.classList.add('hidden');elements.emptyFeed.classList.remove('hidden');elements.emptyFeed.textContent='Активных игр в этой очереди сейчас нет.'}
    }catch{
      elements.gameCard.classList.add('hidden');elements.emptyFeed.classList.remove('hidden');elements.emptyFeed.textContent='Не удалось загрузить текущий список игр.';
    }
  };
  return app;
}
async function seed(cache,url,value){await cache.put(url,new FakeResponse(value));cache.putCount=0}
function makeController(env,fetchImpl,caches,extra={}){
  const ctl=createFeedBootstrapResilience({window:env.win,document:env.doc,fetch:fetchImpl,caches,AbortController,timeoutMs:extra.timeoutMs??30,retryDelayMs:extra.retryDelayMs??0,console:quietConsole()});
  ctl.install();return ctl;
}
const CACHE_URL='https://example.test/app/data/current.json';

async function firstVisitLoadsAndCaches(){
  const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache);let calls=0;const network=payload('2026-09-03T10:00:00Z',['A']);
  const ctl=makeController(env,async()=>{calls++;return new FakeResponse(network)},caches);const app=installFakeApp(env.win,env.elements);
  await env.win.init();await tick(5);
  assert.equal(calls,1);assert.equal(app.applyCount,1);assert.equal(ctl.state.status,'ready');assert.equal(cache.putCount,1);
  assert.equal((await (await cache.match(CACHE_URL)).json()).generated_at_utc,network.generated_at_utc);ctl.destroy();
}
async function cachedRepeatRendersBeforeSlowNetwork(){
  const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache),old=payload('2026-09-03T10:00:00Z',['A']);await seed(cache,CACHE_URL,old);
  let calls=0,resolveNetwork;const ctl=makeController(env,()=>{calls++;return new Promise(resolve=>{resolveNetwork=resolve})},caches,{timeoutMs:1000});const app=installFakeApp(env.win,env.elements);
  await env.win.init();await tick();
  assert.equal(app.applyCount,1);assert.equal(app.payload.items[0].id,'A');assert.equal(env.elements.gameCard.classList.contains('hidden'),false);assert.equal(env.elements.emptyFeed.classList.contains('hidden'),true);assert.equal(calls,1);
  resolveNetwork(new FakeResponse(old));await ctl.whenBackgroundIdle();await tick();ctl.destroy();
}
async function identicalRefreshDoesNotRerender(){
  const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache),old=payload('2026-09-03T10:00:00Z',['A']);await seed(cache,CACHE_URL,old);
  const ctl=makeController(env,async()=>new FakeResponse(old),caches);const app=installFakeApp(env.win,env.elements);
  await env.win.init();await ctl.whenBackgroundIdle();await tick();assert.equal(app.applyCount,1);assert.equal(ctl.state.refreshOutcome,'identical');ctl.destroy();
}
async function newerRefreshUpdatesInPlaceAndCache(){
  const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache),old=payload('2026-09-03T10:00:00Z',['A']),fresh=payload('2026-09-03T11:00:00Z',['B','C']);await seed(cache,CACHE_URL,old);
  const ctl=makeController(env,async()=>new FakeResponse(fresh),caches);const app=installFakeApp(env.win,env.elements);app.currentTab='wishlist';
  await env.win.init();await ctl.whenBackgroundIdle();await tick(5);
  assert.equal(app.applyCount,2);assert.equal(app.payload.items[0].id,'B');assert.equal(app.currentTab,'wishlist');assert.equal(ctl.state.refreshOutcome,'updated');
  assert.equal((await (await cache.match(CACHE_URL)).json()).generated_at_utc,fresh.generated_at_utc);ctl.destroy();
}
async function cachedFeedSurvivesRefreshFailure(){
  const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache),old=payload('2026-09-03T10:00:00Z',['A']);await seed(cache,CACHE_URL,old);let calls=0;
  const ctl=makeController(env,async()=>{calls++;throw new Error('offline')},caches);const app=installFakeApp(env.win,env.elements);
  await env.win.init();await ctl.whenBackgroundIdle();await tick();
  assert.equal(calls,2);assert.equal(app.applyCount,1);assert.equal(app.payload.items[0].id,'A');assert.equal(env.elements.gameCard.classList.contains('hidden'),false);assert.equal(/Не удалось загрузить игры/.test(env.elements.emptyFeed.textContent),false);assert.equal(ctl.state.status,'ready');assert.equal(ctl.state.refreshOutcome,'failed');ctl.destroy();
}
async function corruptCacheFallsBackToNetwork(){
  const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache);cache.map.set(CACHE_URL,new FakeResponse({bad:true}));const fresh=payload('2026-09-03T11:00:00Z',['N']);let calls=0;
  const ctl=makeController(env,async()=>{calls++;return new FakeResponse(fresh)},caches);const app=installFakeApp(env.win,env.elements);
  await env.win.init();await tick(5);assert.equal(calls,1);assert.equal(app.payload.items[0].id,'N');assert.equal(cache.deleteCount,1);assert.equal(cache.putCount,1);ctl.destroy();
}
async function malformedNetworkNeverReplacesCache(){
  for(const networkResponse of [new FakeResponse({}, {parseError:new SyntaxError('bad json')}),new FakeResponse({bad:true})]){
    const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache),old=payload('2026-09-03T10:00:00Z',['A']);await seed(cache,CACHE_URL,old);
    const ctl=makeController(env,async()=>networkResponse,caches);const app=installFakeApp(env.win,env.elements);
    await env.win.init();await ctl.whenBackgroundIdle();await tick();assert.equal(app.applyCount,1);assert.equal(app.payload.items[0].id,'A');assert.equal((await (await cache.match(CACHE_URL)).json()).generated_at_utc,old.generated_at_utc);ctl.destroy();
  }
}
async function cacheFailuresFailOpen(){
  {
    const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache);caches.failOpen=true;const fresh=payload('2026-09-03T11:00:00Z',['A']);
    const ctl=makeController(env,async()=>new FakeResponse(fresh),caches);const app=installFakeApp(env.win,env.elements);await env.win.init();await tick();assert.equal(app.applyCount,1);assert.equal(app.payload.items[0].id,'A');ctl.destroy();
  }
  {
    const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache);cache.failPut=true;const fresh=payload('2026-09-03T11:00:00Z',['A']);
    const ctl=makeController(env,async()=>new FakeResponse(fresh),caches);const app=installFakeApp(env.win,env.elements);await env.win.init();await tick(5);assert.equal(app.applyCount,1);assert.equal(ctl.state.status,'ready');ctl.destroy();
  }
}
async function lifecycleDoesNotDuplicateRefreshOrBlankCache(){
  const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache),old=payload('2026-09-03T10:00:00Z',['A']);await seed(cache,CACHE_URL,old);let calls=0,resolveNetwork;
  const ctl=makeController(env,()=>{calls++;return new Promise(resolve=>{resolveNetwork=resolve})},caches,{timeoutMs:1000});installFakeApp(env.win,env.elements);
  await env.win.init();await tick();env.doc.visibilityState='hidden';env.doc.dispatchEvent({type:'visibilitychange'});env.doc.visibilityState='visible';env.doc.dispatchEvent({type:'visibilitychange'});env.win.dispatchEvent({type:'pageshow',persisted:true});await tick();
  assert.equal(calls,1);assert.equal(env.elements.gameCard.classList.contains('hidden'),false);resolveNetwork(new FakeResponse(old));await ctl.whenBackgroundIdle();ctl.destroy();
}
async function coldTimeoutStillEndsExplicitly(){
  const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache);let calls=0;
  const ctl=makeController(env,(_url,{signal})=>new Promise((resolve,reject)=>{calls++;signal.addEventListener('abort',()=>reject(new Error('aborted')),{once:true})}),caches,{timeoutMs:8});installFakeApp(env.win,env.elements);
  await env.win.init();await tick();assert.equal(calls,2);assert.equal(ctl.state.status,'failed');assert.match(env.elements.emptyFeed.textContent,/Не удалось/);ctl.destroy();
}
async function cacheWriteRequiresRenderableState(){
  const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache),fresh=payload('2026-09-03T11:00:00Z',['A']);
  const ctl=makeController(env,async()=>new FakeResponse(fresh),caches);installFakeApp(env.win,env.elements,{throwAfterJson:true});await env.win.init();await tick(5);
  assert.equal(cache.putCount,0);assert.equal(await cache.match(CACHE_URL),undefined);ctl.destroy();
}
async function payloadAndNonFeedSemanticsStayUntouched(){
  const env=makeEnv(),cache=new MemoryCache(),caches=new MemoryCaches(cache),fresh=payload('2026-09-03T11:00:00Z',['A','B']),other=new FakeResponse({other:true});
  const ctl=makeController(env,async url=>url==='other.json'?other:new FakeResponse(fresh),caches);const app=installFakeApp(env.win,env.elements);
  const otherResult=await env.win.fetch('other.json');assert.equal(otherResult,other);assert.deepEqual(await otherResult.json(),{other:true});await env.win.init();await tick(5);assert.deepEqual(app.payload,fresh);ctl.destroy();
}

(async()=>{
  await firstVisitLoadsAndCaches();
  await cachedRepeatRendersBeforeSlowNetwork();
  await identicalRefreshDoesNotRerender();
  await newerRefreshUpdatesInPlaceAndCache();
  await cachedFeedSurvivesRefreshFailure();
  await corruptCacheFallsBackToNetwork();
  await malformedNetworkNeverReplacesCache();
  await cacheFailuresFailOpen();
  await lifecycleDoesNotDuplicateRefreshOrBlankCache();
  await coldTimeoutStillEndsExplicitly();
  await cacheWriteRequiresRenderableState();
  await payloadAndNonFeedSemanticsStayUntouched();
  console.log('feed instant cache regression: PASS');
})().catch(error=>{console.error(error);process.exitCode=1});