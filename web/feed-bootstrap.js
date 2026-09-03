(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root&&root.document&&root.fetch){
    const controller=api.createFeedBootstrapResilience({
      window:root,
      document:root.document,
      fetch:root.fetch.bind(root),
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
  const LOADING_TEXT='Загружаю игры…';
  const RETRY_TEXT='Повторяю загрузку игр…';
  const EMPTY_TEXT='Активных игр в этой очереди сейчас нет.';
  const ERROR_TEXT='Не удалось загрузить игры. Обновите страницу.';

  function createFeedBootstrapResilience(options={}){
    const win=options.window||null;
    const doc=options.document||null;
    const nativeFetch=options.fetch;
    const AbortCtor=options.AbortController||globalThis.AbortController;
    const schedule=options.setTimeout||setTimeout;
    const cancel=options.clearTimeout||clearTimeout;
    const logger=options.console||console;
    const timeoutMs=Number.isFinite(options.timeoutMs)?options.timeoutMs:DEFAULT_TIMEOUT_MS;
    const retryDelayMs=Number.isFinite(options.retryDelayMs)?options.retryDelayMs:DEFAULT_RETRY_DELAY_MS;
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
    };
    let bootstrapPromise=null;
    let currentController=null;
    let retryTrigger=null;
    let retryTimer=null;
    let sawHidden=false;
    let lifecycleAbort=false;

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
    function finalizeRender(payload){
      schedule(()=>{
        let renderState=classifyRender();
        const empty=el('emptyFeed');
        if(renderState==='empty'&&empty&&(empty.textContent===LOADING_TEXT||empty.textContent===RETRY_TEXT))empty.textContent=EMPTY_TEXT;
        if(renderState==='error'&&empty&&hidden(empty))showError();
        renderState=classifyRender();
        state.finalRender=renderState;
        if(renderState==='card'||renderState==='empty'){
          state.status='ready';
          state.retryable=false;
        }else{
          state.status='failed';
          state.retryable=false;
        }
        log('render-final',{state:renderState,queueLength:queueLengthFromDom(),itemsLength:Array.isArray(payload?.items)?payload.items.length:0});
      },0);
    }
    function responseWithPayload(response,payload){
      return new Proxy(response,{
        get(target,prop){
          if(prop==='json')return async function(){
            state.payloadDelivered=true;
            finalizeRender(payload);
            return payload;
          };
          const value=Reflect.get(target,prop,target);
          return typeof value==='function'?value.bind(target):value;
        },
      });
    }
    function makeError(kind,message,cause){
      const error=new Error(message||kind);
      error.feedBootstrapKind=kind;
      if(cause)error.cause=cause;
      return error;
    }
    async function fetchAttempt(input,init,attempt){
      state.attempt=attempt;
      state.status='loading';
      state.active=true;
      state.retryable=false;
      lifecycleAbort=false;
      currentController=new AbortCtor();
      const requestInit={...(init||{}),signal:currentController.signal};
      const url=resolvedUrl(input);
      log('bootstrap-attempt',{attempt,url,timeoutMs});
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
        log('fetch-resolved',{attempt,status:response.status,ok:response.ok});
        if(!response.ok)throw makeError('http',`feed bootstrap HTTP ${response.status}`);
        let payload;
        try{
          const parseSource=typeof response.clone==='function'?response.clone():response;
          payload=await parseSource.json();
        }catch(error){
          throw makeError('parse','feed bootstrap JSON parse failed',error);
        }
        log('json-parsed',{attempt,itemsLength:Array.isArray(payload?.items)?payload.items.length:0});
        return responseWithPayload(response,payload);
      }catch(error){
        if(timeoutId!=null)cancel(timeoutId);
        let kind=timedOut?'timeout':(error?.feedBootstrapKind||'network');
        if(lifecycleAbort&&!timedOut)kind='lifecycle-abort';
        warn(kind==='timeout'?'fetch-timeout':'fetch-rejected',{attempt,kind,message:String(error?.message||error)});
        throw makeError(kind,String(error?.message||kind),error);
      }finally{
        state.active=false;
        currentController=null;
      }
    }
    function waitForRetry(){
      state.status='failed';
      state.retryable=true;
      showLoading(RETRY_TEXT);
      return new Promise(resolve=>{
        let done=false;
        const finish=source=>{
          if(done)return;
          done=true;
          if(retryTimer!=null)cancel(retryTimer);
          retryTimer=null;
          retryTrigger=null;
          log('retry-triggered',{source,nextAttempt:2});
          resolve(source);
        };
        retryTrigger=finish;
        retryTimer=schedule(()=>finish('automatic'),retryDelayMs);
      });
    }
    async function runBootstrap(input,init){
      showLoading();
      log('bootstrap-start',{url:resolvedUrl(input)});
      try{
        return await fetchAttempt(input,init,1);
      }catch(firstError){
        state.retryUsed=true;
        await waitForRetry();
        try{
          return await fetchAttempt(input,init,2);
        }catch(secondError){
          state.status='failed';
          state.retryable=false;
          showError();
          log('render-final',{state:'error',queueLength:queueLengthFromDom(),itemsLength:0});
          throw secondError;
        }
      }
    }
    function wrappedFetch(input,init){
      if(!isDataRequest(input))return nativeFetch(input,init);
      if(bootstrapPromise)return bootstrapPromise;
      bootstrapPromise=runBootstrap(input,init);
      return bootstrapPromise;
    }
    function recover(source){
      if(state.status==='ready'||state.payloadDelivered){
        log('lifecycle-recovery-skip',{source,reason:'ready'});
        return;
      }
      if(state.active){
        if(state.attempt===1&&!state.retryUsed){
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
    function install(){
      if(state.installed)return;
      state.installed=true;
      showLoading();
      if(win)win.fetch=wrappedFetch;
      doc?.addEventListener?.('visibilitychange',onVisibility);
      win?.addEventListener?.('pageshow',onPageShow);
      log('installed',{timeoutMs,retryDelayMs});
    }
    function destroy(){
      if(!state.installed)return;
      state.installed=false;
      if(win&&win.fetch===wrappedFetch)win.fetch=nativeFetch;
      doc?.removeEventListener?.('visibilitychange',onVisibility);
      win?.removeEventListener?.('pageshow',onPageShow);
      if(retryTimer!=null)cancel(retryTimer);
      try{currentController?.abort()}catch{}
    }
    return {install,destroy,fetch:wrappedFetch,recover,state,constants:{LOADING_TEXT,RETRY_TEXT,EMPTY_TEXT,ERROR_TEXT,DEFAULT_TIMEOUT_MS}};
  }

  return {createFeedBootstrapResilience};
});