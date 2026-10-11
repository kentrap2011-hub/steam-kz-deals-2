(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document&&root.fetch){
    const controller=api.createFeedBootstrapResilience({
      window:root,
      document:root.document,
      fetch:root.fetch.bind(root),
      caches:root.caches,
      AbortController:root.AbortController,
      setTimeout:root.setTimeout.bind(root),
      clearTimeout:root.clearTimeout.bind(root),
      console:root.console,
    });
    root.FeedBootstrapResilience=controller;
    controller.install();
  }
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const DEFAULT_TIMEOUT_MS=9000;
  const DEFAULT_RETRY_DELAY_MS=200;
  const CACHE_NAME='steam-deals-feed-lkg-v1';
  const LOADING_TEXT='Загружаю игры…';
  const RETRY_TEXT='Повторяю загрузку игр…';
  const EMPTY_TEXT='Активных игр в этой очереди сейчас нет.';
  const ERROR_TEXT='Не удалось загрузить игры. Обновите страницу.';

  function createFeedBootstrapResilience(options={}){
    const win=options.window||null;
    const doc=options.document||null;
    const nativeFetch=options.fetch;
    const cacheStorage=options.caches||win?.caches||null;
    const AbortCtor=options.AbortController||globalThis.AbortController;
    const schedule=options.setTimeout||setTimeout;
    const cancel=options.clearTimeout||clearTimeout;
    const logger=options.console||console;
    const now=options.now||Date.now;
    const timeoutMs=Number.isFinite(options.timeoutMs)?options.timeoutMs:DEFAULT_TIMEOUT_MS;
    const retryDelayMs=Number.isFinite(options.retryDelayMs)?options.retryDelayMs:DEFAULT_RETRY_DELAY_MS;
    const cacheName=options.cacheName||CACHE_NAME;
    const dataUrlSuffix=options.dataUrlSuffix||'/data/current.json';

    if(typeof nativeFetch!=='function')throw new TypeError('feed bootstrap requires fetch');
    if(typeof AbortCtor!=='function')throw new TypeError('feed bootstrap requires AbortController');

    const state={
      status:'idle',
      attempt:0,
      active:false,
      retryUsed:false,
      retryable:false,
      payloadDelivered:false,
      installed:false,
      finalRender:null,
      source:null,
      cacheAvailable:null,
      currentIdentity:null,
      refreshActive:false,
      refreshOutcome:null,
      currentGeneratedAt:null,
      freshnessState:null,
      lastVerifiedAt:null,
      statusExpanded:false,
    };

    let bootstrapPromise=null;
    let refreshPromise=null;
    let injectedResponse=null;
    let currentController=null;
    let retryTrigger=null;
    let retryTimer=null;
    let sawHidden=false;
    let lifecycleAbort=false;
    let activeBlocking=false;
    let initialRenderResolve=null;
    let initialRenderPromise=null;
    let latestPayload=null;
    let latestResponse=null;
    let lastInput=null;
    let lastInit=null;

    function el(id){return doc&&typeof doc.getElementById==='function'?doc.getElementById(id):null}
    function hidden(node){return !node||node.classList?.contains('hidden')}
    function show(node){node?.classList?.remove('hidden')}
    function hide(node){node?.classList?.add('hidden')}
    function log(event,details={}){
      if(logger&&typeof logger.info==='function')logger.info('[feed-bootstrap]',event,details);
      else if(logger&&typeof logger.log==='function')logger.log('[feed-bootstrap]',event,details);
    }
    function warn(event,details={}){
      if(logger&&typeof logger.warn==='function')logger.warn('[feed-bootstrap]',event,details);
      else log(event,details);
    }
    function showLoading(text=LOADING_TEXT){
      const card=el('gameCard'),empty=el('emptyFeed');
      hide(card);
      if(empty){empty.textContent=text;show(empty)}
    }
    function showError(){
      const card=el('gameCard'),empty=el('emptyFeed');
      hide(card);
      if(empty){empty.textContent=ERROR_TEXT;show(empty)}
    }
    function resolvedUrl(input){
      const raw=typeof input==='string'?input:(input&&input.url)||String(input||'');
      try{return new URL(raw,win?.location?.href||'https://local.invalid/').href}catch{return raw}
    }
    function isDataRequest(input){
      const url=resolvedUrl(input);
      try{return new URL(url).pathname.endsWith(dataUrlSuffix)}catch{return String(url).split(/[?#]/,1)[0].endsWith(dataUrlSuffix)}
    }
    // A cached object without a parseable producer timestamp or stable item keys
    // cannot safely be ordered against a newer producer. Fail closed.
    function validatePayload(payload){
      if(!payload||typeof payload!=='object'||Array.isArray(payload)||!Array.isArray(payload.items))return false;
      if(typeof payload.generated_at_utc!=='string'||!Number.isFinite(Date.parse(payload.generated_at_utc)))return false;
      const ids=new Set();
      for(const item of payload.items){
        if(!item||typeof item!=='object'||typeof item.id!=='string'||!item.id.trim()||ids.has(item.id))return false;
        ids.add(item.id);
      }
      return true;
    }
    function generationTime(payload){return Date.parse(payload.generated_at_utc)}
    function samePayload(a,b){return JSON.stringify(a)===JSON.stringify(b)}
    // Verification failure does not prove staleness. Generation and check times differ.
    function freshnessNotice(mode,payload){
      const banner=el('feedSyncNotice'),toggle=el('feedStatusToggle'),icon=el('feedSyncSymbol');
      const details=el('feedSyncDetails'),message=el('feedSyncText'),live=el('feedSyncLive'),button=el('feedRefreshBtn');
      if(!banner||!toggle||!icon||!details||!message||!button)return;
      const source=payload||latestPayload,g=source?.generated_at_utc;
      const valid=typeof g==='string'&&Number.isFinite(Date.parse(g));
      const stamp=valid?new Date(g).toLocaleString('ru-RU',{dateStyle:'short',timeStyle:'short'}):'неизвестно';
      // Daily cadence: age >36h is an informational hint, not verified divergence.
      const age=valid&&now()-Date.parse(g)>36*3600000?' Снимок создан более суток назад.':'';
      if(mode==='network_verified')state.lastVerifiedAt=new Date(now()).toISOString();
      state.freshnessState=mode;
      const verified=state.lastVerifiedAt?new Date(state.lastVerifiedAt).toLocaleTimeString('ru-RU',{hour:'2-digit',minute:'2-digit'}):null;
      const labels={
        checking:source?`Сохранённая лента от ${stamp}. Проверяем обновления. Статистика загружается отдельно.`:'Проверяем ленту по сети.',
        cached_unverified:`Сохранённая лента от ${stamp}. Проверка ещё не завершена; свежесть не подтверждена.${age} Статистика загружается отдельно.`,
        verification_failed:`Сохранённая лента от ${stamp}. Проверка сети не удалась. Это не означает, что лента устарела.${age} Статистика загружается отдельно.`,
        confirmed_older_or_conflict:`Сервер вернул более старую или неоднозначную версию. Сохранена надёжная лента от ${stamp}; отметки Deep не понижены. Статистика загружается отдельно.`,
        network_verified:`Лента проверена по сети${verified?' в '+verified:''}. Снимок создан ${stamp}.${age} Время обновления скидок указано отдельно. Статистика загружается отдельно.`,
        no_feed:'Лента недоступна: загрузка не удалась и подходящей сохранённой копии нет. Повторная проверка не удалит очередь или настройки.',
      };
      const short={checking:'Проверка ленты',cached_unverified:'Сохранённая лента не проверена',verification_failed:'Не удалось проверить ленту',confirmed_older_or_conflict:'Версии ленты расходятся',network_verified:'Лента проверена',no_feed:'Лента недоступна'};
      const icons={checking:'◌',cached_unverified:'ⓘ',verification_failed:'!',confirmed_older_or_conflict:'!',network_verified:'✓',no_feed:'!'};
      const description=short[mode]||short.cached_unverified;
      banner.classList.remove('hidden');
      banner.dataset.state=mode;
      if(icon.textContent!==icons[mode])icon.textContent=icons[mode]||'ⓘ';
      toggle.setAttribute('aria-label',description+'. Показать подробности и повторить проверку.');
      toggle.setAttribute('title',description+'. Подробности.');
      if(message.textContent!==labels[mode])message.textContent=labels[mode]||labels.cached_unverified;
      if(live&&live.textContent!==description)live.textContent=description;
      button.disabled=!!state.refreshActive;
      button.textContent=state.refreshActive?'Проверяем…':'Повторить проверку ленты';
      details.classList.toggle('hidden',!state.statusExpanded);
      toggle.setAttribute('aria-expanded',String(state.statusExpanded));
    }
    function toggleStatusDetails(){
      state.statusExpanded=!state.statusExpanded;
      el('feedSyncDetails')?.classList.toggle('hidden',!state.statusExpanded);
      el('feedStatusToggle')?.setAttribute('aria-expanded',String(state.statusExpanded));
    }
    function onStatusEscape(event){
      if(event?.key!=='Escape'||!state.statusExpanded)return;
      event.preventDefault?.();toggleStatusDetails();el('feedStatusToggle')?.focus?.();
    }
    function cachedFreshnessMode(){
      if(state.refreshOutcome==='failed')return 'verification_failed';
      if(state.refreshOutcome==='older'||state.refreshOutcome==='ambiguous')return 'confirmed_older_or_conflict';
      if(state.refreshOutcome==='identical'||state.refreshOutcome==='updated')return 'network_verified';
      return state.refreshActive?'checking':'cached_unverified';
    }
    function reusableResponse(response,payload){
      return new Proxy(response,{
        get(target,prop){
          if(prop==='json')return async()=>payload;
          const value=Reflect.get(target,prop,target);
          return typeof value==='function'?value.bind(target):value;
        },
      });
    }
    function payloadIdentity(payload){
      const generatedAt=typeof payload?.generated_at_utc==='string'?payload.generated_at_utc.trim():'';
      const giveawaySnapshotBlobSha=typeof payload?.production_contract?.source_giveaway_snapshot_blob_sha==='string'
        ?payload.production_contract.source_giveaway_snapshot_blob_sha.trim()
        :'';
      if(generatedAt||giveawaySnapshotBlobSha){
        return `published:${JSON.stringify([generatedAt,giveawaySnapshotBlobSha])}`;
      }
      try{return `json:${JSON.stringify(payload)}`}catch{return null}
    }
    function queueLengthFromDom(){
      const text=String(el('feedCount')?.textContent||'');
      const match=text.match(/\d+/);
      return match?Number(match[0]):null;
    }
    function classifyRender(){
      const card=el('gameCard'),empty=el('emptyFeed');
      const cardVisible=card&&!hidden(card);
      const emptyVisible=empty&&!hidden(empty);
      if(cardVisible)return 'card';
      if(emptyVisible){
        const text=String(empty.textContent||'');
        if(text.includes('Не удалось'))return 'error';
        return 'empty';
      }
      return 'error';
    }
    function renderableState(renderState){return renderState==='card'||renderState==='empty'}
    function makeError(kind,message,cause){
      const error=new Error(message||kind);
      error.feedBootstrapKind=kind;
      if(cause)error.cause=cause;
      return error;
    }
    function cloneResponse(response){
      try{return typeof response?.clone==='function'?response.clone():null}catch{return null}
    }

    async function openLocalCache(){
      if(!cacheStorage||typeof cacheStorage.open!=='function'){
        state.cacheAvailable=false;
        return null;
      }
      try{
        const cache=await cacheStorage.open(cacheName);
        state.cacheAvailable=true;
        return cache;
      }catch(error){
        state.cacheAvailable=false;
        warn('cache-open-failed',{message:String(error?.message||error)});
        return null;
      }
    }
    async function readLastGood(url){
      const cache=await openLocalCache();
      if(!cache)return null;
      try{
        const response=await cache.match(url);
        if(!response){log('cache-miss',{url});return null}
        let payload;
        try{payload=await (cloneResponse(response)||response).json()}catch(error){
          warn('cache-corrupt',{reason:'parse',message:String(error?.message||error)});
          try{await cache.delete(url)}catch{}
          return null;
        }
        if(!validatePayload(payload)){
          warn('cache-corrupt',{reason:'shape'});
          try{await cache.delete(url)}catch{}
          return null;
        }
        const identity=payloadIdentity(payload);
        log('cache-hit',{url,identity,itemsLength:payload.items.length});
        return {response,payload,identity};
      }catch(error){
        warn('cache-read-failed',{message:String(error?.message||error)});
        return null;
      }
    }
    async function writeLastGood(url,response,payload,identity){
      if(!validatePayload(payload))return false;
      const cache=await openLocalCache();
      if(!cache)return false;
      const clone=cloneResponse(response);
      if(!clone){warn('cache-write-skipped',{reason:'response-not-cloneable'});return false}
      try{
        await cache.put(url,clone);
        log('cache-write',{url,identity,itemsLength:payload.items.length});
        return true;
      }catch(error){
        warn('cache-write-failed',{message:String(error?.message||error)});
        return false;
      }
    }

    function resolveInitialRender(result){
      if(initialRenderResolve){
        const resolve=initialRenderResolve;
        initialRenderResolve=null;
        resolve(result);
      }
    }
    function finalizeRender(payload,{source,identity,cacheCandidate,url,response,onRendered}={}){
      schedule(async()=>{
        let renderState=classifyRender();
        const empty=el('emptyFeed');
        if(renderState==='empty'&&empty&&(empty.textContent===LOADING_TEXT||empty.textContent===RETRY_TEXT))empty.textContent=EMPTY_TEXT;
        if(renderState==='error'&&source!=='cache'&&empty&&hidden(empty))showError();
        renderState=classifyRender();
        state.finalRender=renderState;
        const renderable=renderableState(renderState);
        if(renderable){
          state.status='ready';
          state.retryable=false;
          state.source=source||state.source;
          state.currentIdentity=identity||state.currentIdentity;
          state.currentGeneratedAt=payload.generated_at_utc;
          latestPayload=payload;
          if(response)latestResponse=reusableResponse(response,payload);
          if(source!=='cache')freshnessNotice('network_verified',payload);
          else freshnessNotice(cachedFreshnessMode(),payload);
        }else if(state.status!=='ready'){
          state.status='failed';
          state.retryable=false;
        }
        log('render-final',{source,state:renderState,queueLength:queueLengthFromDom(),itemsLength:Array.isArray(payload?.items)?payload.items.length:0,identity});
        if(renderable&&cacheCandidate&&url&&response)await writeLastGood(url,response,payload,identity);
        if(source==='cache')resolveInitialRender({renderable,renderState});
        if(typeof onRendered==='function')onRendered({renderable,renderState});
      },0);
    }
    function responseWithPayload(response,payload,meta={}){
      return new Proxy(response,{
        get(target,prop){
          if(prop==='json')return async function(){
            state.payloadDelivered=true;
            finalizeRender(payload,{...meta,response:target});
            return payload;
          };
          const value=Reflect.get(target,prop,target);
          return typeof value==='function'?value.bind(target):value;
        },
      });
    }

    async function fetchAttempt(input,init,attempt,{blocking,phase}){
      state.attempt=attempt;
      state.active=true;
      activeBlocking=!!blocking;
      if(blocking){state.status='loading';state.retryable=false}
      lifecycleAbort=false;
      currentController=new AbortCtor();
      const requestInit={...(init||{}),signal:currentController.signal};
      const url=resolvedUrl(input);
      log('network-attempt',{phase,attempt,url,timeoutMs,blocking:!!blocking});
      let timeoutId=null;
      let timedOut=false;
      const timeoutPromise=new Promise((_,reject)=>{
        timeoutId=schedule(()=>{
          timedOut=true;
          try{currentController?.abort()}catch{}
          reject(makeError('timeout',`feed bootstrap timed out after ${timeoutMs}ms`));
        },timeoutMs);
      });
      try{
        const response=await Promise.race([
          Promise.resolve().then(()=>nativeFetch(input,requestInit)),
          timeoutPromise,
        ]);
        if(timeoutId!=null)cancel(timeoutId);
        log('fetch-resolved',{phase,attempt,status:response.status,ok:response.ok});
        if(!response.ok)throw makeError('http',`feed bootstrap HTTP ${response.status}`);
        let payload;
        try{payload=await (cloneResponse(response)||response).json()}catch(error){
          throw makeError('parse','feed bootstrap JSON parse failed',error);
        }
        if(!validatePayload(payload))throw makeError('shape','feed bootstrap payload shape invalid');
        const identity=payloadIdentity(payload);
        log('json-parsed',{phase,attempt,itemsLength:payload.items.length,identity});
        return {response,payload,identity,url};
      }catch(error){
        if(timeoutId!=null)cancel(timeoutId);
        let kind=timedOut?'timeout':(error?.feedBootstrapKind||'network');
        if(lifecycleAbort&&!timedOut)kind='lifecycle-abort';
        warn(kind==='timeout'?'fetch-timeout':'fetch-rejected',{phase,attempt,kind,message:String(error?.message||error)});
        throw makeError(kind,String(error?.message||kind),error);
      }finally{
        state.active=false;
        activeBlocking=false;
        currentController=null;
      }
    }
    function waitForRetry({blocking,phase}){
      if(blocking){state.status='failed';state.retryable=true;showLoading(RETRY_TEXT)}
      return new Promise(resolve=>{
        let done=false;
        const finish=source=>{
          if(done)return;
          done=true;
          if(retryTimer!=null)cancel(retryTimer);
          retryTimer=null;
          retryTrigger=null;
          log('retry-triggered',{phase,source,nextAttempt:2});
          resolve(source);
        };
        retryTrigger=blocking?finish:null;
        retryTimer=schedule(()=>finish('automatic'),retryDelayMs);
      });
    }
    async function runBoundedNetwork(input,init,{blocking,phase}){
      state.retryUsed=false;
      try{
        return await fetchAttempt(input,init,1,{blocking,phase});
      }catch(firstError){
        state.retryUsed=true;
        await waitForRetry({blocking,phase});
        try{
          return await fetchAttempt(input,init,2,{blocking,phase});
        }catch(secondError){
          if(blocking){
            state.status='failed';
            state.retryable=false;
            showError();
            log('render-final',{source:'network',state:'error',queueLength:queueLengthFromDom(),itemsLength:0});
          }
          throw secondError;
        }
      }
    }

    async function applyBackgroundPayload(result){
      if(typeof win?.init!=='function'){
        warn('refresh-apply-skipped',{reason:'app-init-unavailable',identity:result.identity});
        return false;
      }
      let renderedResolve;
      const rendered=new Promise(resolve=>{renderedResolve=resolve});
      injectedResponse=responseWithPayload(result.response,result.payload,{
        source:'refresh',
        identity:result.identity,
        cacheCandidate:true,
        url:result.url,
        onRendered:renderedResolve,
      });
      log('refresh-apply',{identity:result.identity});
      try{await win.init()}catch(error){
        injectedResponse=null;
        warn('refresh-apply-failed',{message:String(error?.message||error)});
        return false;
      }
      const outcome=await rendered;
      if(outcome.renderable){
        state.refreshOutcome='updated';
        return true;
      }
      warn('refresh-apply-failed',{reason:'non-renderable'});
      return false;
    }
    async function startBackgroundRefresh(input,init,cached){
      if(refreshPromise)return refreshPromise;
      state.refreshActive=true;
      state.refreshOutcome='pending';
      freshnessNotice('checking',latestPayload||cached.payload);
      refreshPromise=(async()=>{
        try{
          const fresh=await runBoundedNetwork(input,init,{blocking:false,phase:'refresh'});
          if(initialRenderPromise){
            const pending=initialRenderPromise;
            const initial=await pending;
            initialRenderPromise=null;
            if(!initial?.renderable)throw makeError('render','cached render unavailable');
          }
          const baseline=latestPayload||cached.payload;
          if(generationTime(fresh.payload)<generationTime(baseline)){
            state.refreshOutcome='older';
            warn('refresh-older-rejected',{network:fresh.payload.generated_at_utc,current:baseline.generated_at_utc});
            freshnessNotice('confirmed_older_or_conflict',baseline);
            return;
          }
          if(samePayload(fresh.payload,baseline)){
            state.refreshOutcome='identical';
            state.source='network';
            log('refresh-identical',{identity:fresh.identity});
            freshnessNotice('network_verified',baseline);
            return;
          }
          if(generationTime(fresh.payload)===generationTime(baseline)){
            // A giveaway-only republish can retain feed generated_at_utc.
            // Unknown same-time changes are not ordered: reject instead of downgrading Deep.
            const sameItems=samePayload(fresh.payload.items,baseline.items);
            const changedGiveaway=String(fresh.payload.production_contract?.source_giveaway_snapshot_blob_sha||'')
              !==String(baseline.production_contract?.source_giveaway_snapshot_blob_sha||'');
            if(!sameItems||!changedGiveaway){
              state.refreshOutcome='ambiguous';
              warn('refresh-ambiguous-rejected',{identity:fresh.identity});
              freshnessNotice('confirmed_older_or_conflict',baseline);
              return;
            }
          }
          if(!await applyBackgroundPayload(fresh))throw makeError('render','fresh feed render failed');
        }catch(error){
          state.refreshOutcome='failed';
          warn('refresh-failed',{kind:error?.feedBootstrapKind||'network',message:String(error?.message||error)});
          freshnessNotice('verification_failed',latestPayload||cached.payload);
        }finally{
          state.refreshActive=false;
          if(state.refreshOutcome==='updated'||state.refreshOutcome==='identical')freshnessNotice('network_verified',latestPayload||cached.payload);
          else if(state.refreshOutcome==='failed')freshnessNotice('verification_failed',latestPayload||cached.payload);
          refreshPromise=null;
        }
      })();
      return refreshPromise;
    }

    async function runInitial(input,init){
      const url=resolvedUrl(input);
      lastInput=input;
      lastInit=init;
      log('bootstrap-start',{url});
      const cached=await readLastGood(url);
      if(cached){
        state.source='cache';
        state.currentIdentity=cached.identity;
        state.currentGeneratedAt=cached.payload.generated_at_utc;
        state.status='loading';
        freshnessNotice('cached_unverified',cached.payload);
        initialRenderPromise=new Promise(resolve=>{initialRenderResolve=resolve});
        startBackgroundRefresh(input,init,cached);
        return responseWithPayload(cached.response,cached.payload,{source:'cache',identity:cached.identity,url});
      }
      showLoading();
      try{
        const fresh=await runBoundedNetwork(input,init,{blocking:true,phase:'bootstrap'});
        return responseWithPayload(fresh.response,fresh.payload,{
          source:'network',
          identity:fresh.identity,
          cacheCandidate:true,
          url:fresh.url,
        });
      }catch(error){
        freshnessNotice('no_feed');
        throw error;
      }
    }
    function wrappedFetch(input,init){
      if(!isDataRequest(input))return nativeFetch(input,init);
      if(injectedResponse){
        const response=injectedResponse;
        injectedResponse=null;
        return Promise.resolve(response);
      }
      if(latestResponse)return Promise.resolve(latestResponse);
      if(bootstrapPromise)return bootstrapPromise;
      bootstrapPromise=runInitial(input,init);
      return bootstrapPromise;
    }

    function recover(source){
      if(latestPayload&&state.source==='cache'&&!state.refreshActive){
        log('lifecycle-recovery',{source,action:'refresh-stale-cache'});
        retry();
        return;
      }
      if(state.status==='ready'||state.source==='cache'||state.payloadDelivered){
        log('lifecycle-recovery-skip',{source,reason:'visible-feed-ready-or-delivered'});
        return;
      }
      if(state.active){
        if(activeBlocking&&state.attempt===1&&!state.retryUsed){
          lifecycleAbort=true;
          state.retryUsed=true;
          log('lifecycle-recovery',{source,action:'abort-first-attempt-for-retry'});
          try{currentController?.abort()}catch{}
        }else{
          log('lifecycle-recovery-skip',{source,reason:'active'});
        }
        return;
      }
      if(state.retryable&&retryTrigger){
        log('lifecycle-recovery',{source,action:'trigger-retry'});
        retryTrigger(source);
      }else{
        log('lifecycle-recovery-skip',{source,reason:'not-retryable'});
      }
    }
    function onVisibility(){
      if(!doc)return;
      if(doc.visibilityState==='hidden'){
        sawHidden=true;
        return;
      }
      if(doc.visibilityState==='visible'&&sawHidden){
        sawHidden=false;
        recover('visibilitychange');
      }
    }
    function onPageShow(event){
      if(event&&event.persisted)recover('pageshow');
    }
    async function retry(){
      if(refreshPromise)return refreshPromise;
      if(lastInput&&latestPayload){
        return startBackgroundRefresh(lastInput,lastInit,{payload:latestPayload,identity:state.currentIdentity});
      }
      // Nothing usable was cached: re-run ordinary init with the same saved localStorage.
      if(!lastInput||typeof win?.init!=='function')return false;
      bootstrapPromise=null;
      state.payloadDelivered=false;
      state.status='loading';
      freshnessNotice('checking');
      await win.init();
      // app.init() can resolve before the deferred render status callback runs.
      // Do not briefly report no feed after an accepted network response.
      if(state.payloadDelivered&&state.status!=='ready')await new Promise(resolve=>schedule(resolve,0));
      if(state.status!=='ready')freshnessNotice('no_feed');
      return state.status==='ready';
    }
    function onRetryClick(){retry().catch(error=>warn('retry-failed',{message:String(error?.message||error)}))}
    function install(){
      if(state.installed)return;
      state.installed=true;
      if(win)win.fetch=wrappedFetch;
      doc?.addEventListener?.('visibilitychange',onVisibility);
      el('feedRefreshBtn')?.addEventListener?.('click',onRetryClick);
      el('feedStatusToggle')?.addEventListener?.('click',toggleStatusDetails);
      el('feedStatusToggle')?.addEventListener?.('keydown',onStatusEscape);
      el('feedSyncDetails')?.addEventListener?.('keydown',onStatusEscape);
      win?.addEventListener?.('pageshow',onPageShow);
      log('installed',{timeoutMs,retryDelayMs,cacheName,cacheStorage:!!cacheStorage});
    }
    function destroy(){
      if(!state.installed)return;
      state.installed=false;
      if(win&&win.fetch===wrappedFetch)win.fetch=nativeFetch;
      doc?.removeEventListener?.('visibilitychange',onVisibility);
      el('feedRefreshBtn')?.removeEventListener?.('click',onRetryClick);
      el('feedStatusToggle')?.removeEventListener?.('click',toggleStatusDetails);
      el('feedStatusToggle')?.removeEventListener?.('keydown',onStatusEscape);
      el('feedSyncDetails')?.removeEventListener?.('keydown',onStatusEscape);
      win?.removeEventListener?.('pageshow',onPageShow);
      if(retryTimer!=null)cancel(retryTimer);
      try{currentController?.abort()}catch{}
    }
    function whenBackgroundIdle(){return refreshPromise||Promise.resolve()}

    return {
      install,destroy,fetch:wrappedFetch,recover,retry,state,whenBackgroundIdle,
      constants:{LOADING_TEXT,RETRY_TEXT,EMPTY_TEXT,ERROR_TEXT,DEFAULT_TIMEOUT_MS,CACHE_NAME},
      validatePayload,payloadIdentity,
    };
  }

  return {createFeedBootstrapResilience};
});