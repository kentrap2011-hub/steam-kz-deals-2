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
function makeEnv(){
  const win=new FakeTarget();
  win.location={href:'https://example.test/app/'};
  const doc=new FakeTarget();
  doc.visibilityState='visible';
  const elements={
    gameCard:{classList:new FakeClassList('hidden')},
    emptyFeed:{classList:new FakeClassList('hidden'),textContent:'Активных игр в этой очереди сейчас нет.'},
    feedCount:{textContent:''},
  };
  doc.getElementById=id=>elements[id]||null;
  return {win,doc,elements};
}
function response(payload,{status=200,ok=true,parseError=null}={}){
  const make=()=>({
    status,ok,
    clone(){return make()},
    async json(){if(parseError)throw parseError;return payload},
  });
  return make();
}
function quietConsole(){return {info(){},warn(){},log(){}}}
function tick(ms=0){return new Promise(resolve=>setTimeout(resolve,ms))}

async function successfulFetchRendersCard(){
  const {win,doc,elements}=makeEnv();
  let calls=0;
  const ctl=createFeedBootstrapResilience({window:win,document:doc,fetch:async()=>{calls++;return response({items:[{id:'A'}]})},AbortController,timeoutMs:50,retryDelayMs:0,console:quietConsole()});
  ctl.install();
  assert.equal(elements.emptyFeed.textContent,'Загружаю игры…');
  assert.equal(elements.emptyFeed.classList.contains('hidden'),false);
  const res=await win.fetch('data/current.json',{cache:'no-store'});
  const payload=await res.json();
  assert.equal(payload.items[0].id,'A','payload must pass through unchanged');
  elements.gameCard.classList.remove('hidden');
  elements.emptyFeed.classList.add('hidden');
  elements.feedCount.textContent='(1)';
  await tick();
  assert.equal(ctl.state.status,'ready');
  assert.equal(ctl.state.finalRender,'card');
  assert.equal(calls,1);
  ctl.destroy();
}

async function zeroResultShowsEmpty(){
  const {win,doc,elements}=makeEnv();
  const ctl=createFeedBootstrapResilience({window:win,document:doc,fetch:async()=>response({items:[]}),AbortController,timeoutMs:50,retryDelayMs:0,console:quietConsole()});
  ctl.install();
  const res=await win.fetch('data/current.json');
  await res.json();
  elements.gameCard.classList.add('hidden');
  elements.emptyFeed.classList.remove('hidden');
  elements.feedCount.textContent='(0)';
  await tick();
  assert.equal(ctl.state.status,'ready');
  assert.equal(ctl.state.finalRender,'empty');
  assert.equal(elements.emptyFeed.textContent,'Активных игр в этой очереди сейчас нет.');
  ctl.destroy();
}

async function terminalFailuresAreExplicit(){
  for(const mode of ['network','http','parse']){
    const {win,doc,elements}=makeEnv();
    let calls=0;
    const fetchImpl=async()=>{
      calls++;
      if(mode==='network')throw new Error('offline');
      if(mode==='http')return response({}, {status:503,ok:false});
      return response({}, {parseError:new SyntaxError('bad json')});
    };
    const ctl=createFeedBootstrapResilience({window:win,document:doc,fetch:fetchImpl,AbortController,timeoutMs:50,retryDelayMs:0,console:quietConsole()});
    ctl.install();
    await assert.rejects(()=>win.fetch('data/current.json'));
    assert.equal(calls,2,`${mode}: exactly two bounded attempts`);
    assert.equal(ctl.state.status,'failed');
    assert.equal(ctl.state.retryable,false);
    assert.equal(elements.emptyFeed.classList.contains('hidden'),false);
    assert.match(elements.emptyFeed.textContent,/Не удалось загрузить игры/);
    ctl.destroy();
  }
}

async function pendingRequestTimesOut(){
  const {win,doc,elements}=makeEnv();
  let calls=0;
  const fetchImpl=(_url,{signal})=>new Promise((resolve,reject)=>{
    calls++;
    signal.addEventListener('abort',()=>reject(new Error('aborted')),{once:true});
  });
  const ctl=createFeedBootstrapResilience({window:win,document:doc,fetch:fetchImpl,AbortController,timeoutMs:10,retryDelayMs:0,console:quietConsole()});
  ctl.install();
  await assert.rejects(()=>win.fetch('data/current.json'));
  assert.equal(calls,2);
  assert.equal(ctl.state.status,'failed');
  assert.match(elements.emptyFeed.textContent,/Не удалось загрузить игры/);
  ctl.destroy();
}

async function lifecycleDoesNotDuplicateActiveRequest(){
  const {win,doc}=makeEnv();
  let calls=0;
  let resolveFirst;
  const fetchImpl=()=>new Promise(resolve=>{calls++;resolveFirst=resolve});
  const ctl=createFeedBootstrapResilience({window:win,document:doc,fetch:fetchImpl,AbortController,timeoutMs:100,retryDelayMs:0,console:quietConsole()});
  ctl.install();
  const pending=win.fetch('data/current.json');
  win.dispatchEvent({type:'pageshow',persisted:false});
  doc.dispatchEvent({type:'visibilitychange'});
  await tick();
  assert.equal(calls,1,'ordinary foreground signals during active request must not duplicate fetch');
  resolveFirst(response({items:[{id:'A'}]}));
  const res=await pending;await res.json();
  ctl.destroy();
}

async function foregroundCanTriggerSingleRecovery(){
  const {win,doc,elements}=makeEnv();
  let calls=0;
  const fetchImpl=async()=>{
    calls++;
    if(calls===1)throw new Error('first failed');
    return response({items:[{id:'B'}]});
  };
  const ctl=createFeedBootstrapResilience({window:win,document:doc,fetch:fetchImpl,AbortController,timeoutMs:100,retryDelayMs:1000,console:quietConsole()});
  ctl.install();
  const pending=win.fetch('data/current.json');
  await tick();
  assert.equal(ctl.state.status,'failed');
  assert.equal(ctl.state.retryable,true);
  assert.equal(calls,1);
  doc.visibilityState='hidden';doc.dispatchEvent({type:'visibilitychange'});
  doc.visibilityState='visible';doc.dispatchEvent({type:'visibilitychange'});
  const res=await pending;await res.json();
  elements.gameCard.classList.remove('hidden');elements.emptyFeed.classList.add('hidden');elements.feedCount.textContent='(1)';
  await tick();
  assert.equal(calls,2,'foreground recovery uses only the single remaining retry');
  assert.equal(ctl.state.status,'ready');
  ctl.destroy();
}

async function activeForegroundRecoveryAbortsThenRetriesWithoutParallelism(){
  const {win,doc,elements}=makeEnv();
  let calls=0,active=0,maxActive=0;
  const fetchImpl=(_url,{signal})=>new Promise((resolve,reject)=>{
    calls++;active++;maxActive=Math.max(maxActive,active);
    if(calls===1){
      signal.addEventListener('abort',()=>{active--;reject(new Error('aborted for foreground recovery'))},{once:true});
    }else{
      active--;resolve(response({items:[{id:'C'}]}));
    }
  });
  const ctl=createFeedBootstrapResilience({window:win,document:doc,fetch:fetchImpl,AbortController,timeoutMs:100,retryDelayMs:1000,console:quietConsole()});
  ctl.install();
  const pending=win.fetch('data/current.json');
  await tick();
  doc.visibilityState='hidden';doc.dispatchEvent({type:'visibilitychange'});
  doc.visibilityState='visible';doc.dispatchEvent({type:'visibilitychange'});
  const res=await pending;await res.json();
  elements.gameCard.classList.remove('hidden');elements.emptyFeed.classList.add('hidden');elements.feedCount.textContent='(1)';
  await tick();
  assert.equal(calls,2);
  assert.equal(maxActive,1,'foreground recovery must never overlap requests');
  assert.equal(ctl.state.status,'ready');
  ctl.destroy();
}

async function readyLifecycleDoesNotReload(){
  const {win,doc,elements}=makeEnv();
  let calls=0;
  const ctl=createFeedBootstrapResilience({window:win,document:doc,fetch:async()=>{calls++;return response({items:[{id:'A'}]})},AbortController,timeoutMs:50,retryDelayMs:0,console:quietConsole()});
  ctl.install();
  const res=await win.fetch('data/current.json');await res.json();
  elements.gameCard.classList.remove('hidden');elements.emptyFeed.classList.add('hidden');elements.feedCount.textContent='(1)';
  await tick();
  doc.visibilityState='hidden';doc.dispatchEvent({type:'visibilitychange'});
  doc.visibilityState='visible';doc.dispatchEvent({type:'visibilitychange'});
  win.dispatchEvent({type:'pageshow',persisted:true});
  await tick();
  assert.equal(calls,1,'ready feed must not refetch/reset on lifecycle events');
  assert.equal(ctl.state.status,'ready');
  ctl.destroy();
}

async function unrelatedFetchAndPayloadSemanticsStayUntouched(){
  const {win,doc}=makeEnv();
  const calls=[];
  const original={ok:true,status:200,json:async()=>({untouched:true})};
  const ctl=createFeedBootstrapResilience({window:win,document:doc,fetch:async(url)=>{calls.push(url);return original},AbortController,timeoutMs:50,retryDelayMs:0,console:quietConsole()});
  ctl.install();
  const res=await win.fetch('other.json');
  assert.equal(res,original,'non-feed fetch behavior must remain unchanged');
  assert.deepEqual(await res.json(),{untouched:true});
  assert.deepEqual(calls,['other.json']);
  ctl.destroy();
}

(async()=>{
  await successfulFetchRendersCard();
  await zeroResultShowsEmpty();
  await terminalFailuresAreExplicit();
  await pendingRequestTimesOut();
  await lifecycleDoesNotDuplicateActiveRequest();
  await foregroundCanTriggerSingleRecovery();
  await activeForegroundRecoveryAbortsThenRetriesWithoutParallelism();
  await readyLifecycleDoesNotReload();
  await unrelatedFetchAndPayloadSemanticsStayUntouched();
  console.log('feed bootstrap regression: PASS');
})().catch(error=>{console.error(error);process.exitCode=1});