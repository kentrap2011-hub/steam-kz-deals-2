(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.GiveawayUI=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const STORE_LABELS={steam:'Steam',epic:'Epic Games',gog:'GOG'};
  const EMPTY_COPY='Сейчас активных раздач не найдено.';
  const UNAVAILABLE_COPY='Раздачи временно не удалось проверить полностью.';
  const UPDATING_COPY='Текущие раздачи закончились, данные обновляются.';
  const ANALYSIS_INCOMPLETE_COPY='Описание, плюсы и минусы пока недоступны: нет подтверждённой связи этой версии игры с каноническим анализом. По одному совпадению названия данные не подставляем.';

  let lastPayload=null;
  let selectedGameKey=null;
  let returnTab='feed';
  let browserBound=false;
  let boundaryTimer=null;

  function escapeHtml(value){
    return String(value==null?'':value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  }
  function parseTime(value){
    if(typeof value!=='string'||!value)return NaN;
    return Date.parse(value);
  }
  function validClaimUrl(value){
    if(typeof value!=='string')return false;
    try{return new URL(value).protocol==='https:'}catch{return false}
  }
  function storeLabel(storefront){return STORE_LABELS[storefront]||storefront||'Магазин'}
  function deadlineText(value){
    const ms=parseTime(value);if(!Number.isFinite(ms))return '';
    return new Intl.DateTimeFormat('ru-RU',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}).format(new Date(ms));
  }
  function remainingText(value,nowMs=Date.now()){
    const end=parseTime(value);
    if(!Number.isFinite(end)||end<=nowMs)return 'завершено';
    const minutes=Math.ceil((end-nowMs)/60000);
    if(minutes<60)return `осталось ${minutes} мин.`;
    const hours=Math.ceil(minutes/60);
    if(hours<24)return `осталось ${hours} ч.`;
    const days=Math.floor(hours/24);
    const rest=hours%24;
    return rest?`осталось ${days} д. ${rest} ч.`:`осталось ${days} д.`;
  }

  function viewModel(payload,nowMs=Date.now()){
    const data=payload&&typeof payload==='object'?payload:{};
    const freshUntil=parseTime(data.fresh_until_utc);
    if(data.schema_version!==1||data.source_contract!=='CROSS-PLATFORM-GIVEAWAY-V1'||!Number.isFinite(freshUntil)||freshUntil<=nowMs){
      return {state:'unavailable',message:UNAVAILABLE_COPY,games:[],fresh_until_utc:data.fresh_until_utc||null};
    }
    if(data.state==='unavailable')return {state:'unavailable',message:UNAVAILABLE_COPY,games:[],fresh_until_utc:data.fresh_until_utc};
    if(data.state==='empty')return {state:'empty',message:EMPTY_COPY,games:[],fresh_until_utc:data.fresh_until_utc};
    if(data.state!=='active')return {state:'unavailable',message:UNAVAILABLE_COPY,games:[],fresh_until_utc:data.fresh_until_utc};

    const games=[];
    for(const rawGame of Array.isArray(data.games)?data.games:[]){
      if(!rawGame||typeof rawGame!=='object')continue;
      const activeOffers=[];
      for(const rawOffer of Array.isArray(rawGame.offers)?rawGame.offers:[]){
        if(!rawOffer||typeof rawOffer!=='object')continue;
        const end=parseTime(rawOffer.promotion_end_utc);
        if(!Number.isFinite(end)||end<=nowMs||!validClaimUrl(rawOffer.claim_url))continue;
        activeOffers.push({...rawOffer,_end:end});
      }
      activeOffers.sort((a,b)=>a._end-b._end||String(a.storefront||'').localeCompare(String(b.storefront||''))||String(a.source_offer_id||'').localeCompare(String(b.source_offer_id||'')));
      if(activeOffers.length)games.push({game_key:rawGame.game_key,title:rawGame.title,offers:activeOffers});
    }
    if(!games.length)return {state:'updating',message:UPDATING_COPY,games:[],fresh_until_utc:data.fresh_until_utc};
    return {state:'active',message:null,games,fresh_until_utc:data.fresh_until_utc};
  }

  function navState(payload,nowMs=Date.now()){
    const view=viewModel(payload,nowMs);
    if(view.state==='active')return {state:'active',count:view.games.length,label:`(${view.games.length})`,title:`Активных раздач: ${view.games.length}`};
    if(view.state==='empty')return {state:'empty',count:0,label:'(0)',title:EMPTY_COPY};
    if(view.state==='updating')return {state:'updating',count:null,label:'(!)',title:UPDATING_COPY};
    return {state:'unavailable',count:null,label:'(!)',title:UNAVAILABLE_COPY};
  }

  function offerMarkup(offer,nowMs,{compact=false}={}){
    const label=storeLabel(offer.storefront);
    const deadline=`до ${deadlineText(offer.promotion_end_utc)} · ${remainingText(offer.promotion_end_utc,nowMs)}`;
    const claimText=compact?'Забрать':`Забрать в ${label}`;
    return `<div class="giveaway-offer ${compact?'giveaway-offer-compact':''}"><div class="giveaway-offer-meta"><span class="giveaway-store">${escapeHtml(label)}</span><span class="giveaway-deadline">${escapeHtml(deadline)}</span></div><a class="giveaway-claim" href="${escapeHtml(offer.claim_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(claimText)}</a></div>`;
  }

  function buildListMarkup(payload,nowMs=Date.now()){
    const view=viewModel(payload,nowMs);
    if(view.state!=='active')return `<div class="giveaway-state giveaway-state-${escapeHtml(view.state)}">${escapeHtml(view.message)}</div>`;
    return `<div class="giveaway-list">${view.games.map(game=>{
      const offers=game.offers.map(offer=>offerMarkup(offer,nowMs,{compact:true})).join('');
      return `<article class="giveaway-list-card" data-giveaway-key="${escapeHtml(game.game_key)}"><div class="giveaway-list-main"><div class="giveaway-list-title">${escapeHtml(game.title)}</div><div class="giveaway-list-offers">${offers}</div></div><button class="small-btn giveaway-details" type="button" data-giveaway-detail="${escapeHtml(game.game_key)}">Подробнее</button></article>`;
    }).join('')}</div>`;
  }

  function buildDetailMarkup(payload,gameKey,nowMs=Date.now()){
    const view=viewModel(payload,nowMs);
    const back='<button class="small-btn giveaway-detail-back" type="button" data-giveaway-detail-back>← К раздачам</button>';
    if(view.state!=='active')return `${back}<div class="giveaway-state giveaway-state-${escapeHtml(view.state)}">${escapeHtml(view.message)}</div>`;
    const game=view.games.find(row=>String(row.game_key)===String(gameKey));
    if(!game)return `${back}<div class="giveaway-state giveaway-state-updating">${escapeHtml(UPDATING_COPY)}</div>`;
    const offers=game.offers.map(offer=>offerMarkup(offer,nowMs)).join('');
    return `${back}<article class="giveaway-detail-card" data-giveaway-detail-key="${escapeHtml(game.game_key)}"><h2>${escapeHtml(game.title)}</h2><div class="giveaway-detail-offers">${offers}</div><section class="giveaway-analysis-incomplete" aria-label="Описание, плюсы и минусы пока недоступны"><div class="giveaway-analysis-labels"><span>Описание</span><span>Плюсы</span><span>Минусы</span></div><p>${escapeHtml(ANALYSIS_INCOMPLETE_COPY)}</p></section></article>`;
  }

  function nextBoundaryMs(payload,nowMs=Date.now()){
    const candidates=[];
    const fresh=parseTime(payload&&payload.fresh_until_utc);
    if(Number.isFinite(fresh)&&fresh>nowMs)candidates.push(fresh);
    for(const game of Array.isArray(payload&&payload.games)?payload.games:[]){
      for(const offer of Array.isArray(game&&game.offers)?game.offers:[]){
        const end=parseTime(offer&&offer.promotion_end_utc);
        if(Number.isFinite(end)&&end>nowMs)candidates.push(end);
      }
    }
    return candidates.length?Math.min(...candidates):null;
  }

  function scheduleBoundaryRefresh(nowMs=Date.now()){
    if(typeof window==='undefined'||typeof window.setTimeout!=='function')return;
    if(boundaryTimer)window.clearTimeout(boundaryTimer);
    boundaryTimer=null;
    const boundary=nextBoundaryMs(lastPayload,nowMs);
    if(!boundary)return;
    const delay=Math.min(2147480000,Math.max(250,boundary-nowMs+100));
    boundaryTimer=window.setTimeout(()=>renderSurface(Date.now()),delay);
  }

  function renderSurface(nowMs=Date.now()){
    if(typeof document==='undefined')return;
    const nav=navState(lastPayload,nowMs);
    const count=document.getElementById('giveawayCount');
    const tab=document.querySelector('.tab[data-tab="giveaway"]');
    if(count)count.textContent=nav.label;
    if(tab){tab.title=nav.title;tab.dataset.giveawayState=nav.state}
    const list=document.getElementById('giveawayList');
    if(list)list.innerHTML=buildListMarkup(lastPayload,nowMs);
    if(selectedGameKey){
      const detail=document.getElementById('giveawayDetail');
      if(detail)detail.innerHTML=buildDetailMarkup(lastPayload,selectedGameKey,nowMs);
    }
    scheduleBoundaryRefresh(nowMs);
  }

  function showList(){
    if(typeof document==='undefined')return;
    selectedGameKey=null;
    document.getElementById('giveawayListPanel')?.classList.remove('hidden');
    document.getElementById('giveawayDetailPanel')?.classList.add('hidden');
  }
  function showDetail(gameKey,nowMs=Date.now()){
    if(typeof document==='undefined')return false;
    const view=viewModel(lastPayload,nowMs);
    if(view.state!=='active'||!view.games.some(game=>String(game.game_key)===String(gameKey)))return false;
    selectedGameKey=String(gameKey);
    const detail=document.getElementById('giveawayDetail');
    if(detail)detail.innerHTML=buildDetailMarkup(lastPayload,selectedGameKey,nowMs);
    document.getElementById('giveawayListPanel')?.classList.add('hidden');
    document.getElementById('giveawayDetailPanel')?.classList.remove('hidden');
    if(typeof window!=='undefined'&&typeof window.scrollTo==='function')window.scrollTo({top:0,behavior:'smooth'});
    return true;
  }
  function openView(nowMs=Date.now()){
    if(typeof document==='undefined')return;
    renderSurface(nowMs);
    showList();
    document.getElementById('giveawayView')?.classList.remove('hidden');
  }
  function closeView(){
    if(typeof document==='undefined')return;
    document.getElementById('giveawayView')?.classList.add('hidden');
    showList();
  }
  function exitView(){
    if(typeof document==='undefined')return;
    const target=returnTab&&returnTab!=='giveaway'?returnTab:'feed';
    const button=document.querySelector(`.tab[data-tab="${target}"]`)||document.querySelector('.tab[data-tab="feed"]');
    if(button&&typeof button.click==='function')button.click();
  }

  function bindBrowser(){
    if(browserBound||typeof document==='undefined')return;
    browserBound=true;
    document.querySelectorAll('.tab').forEach(button=>{
      button.addEventListener('click',()=>{
        if(button.dataset.tab==='giveaway'){
          const active=document.querySelector('.tab.active');
          if(active&&active.dataset.tab&&active.dataset.tab!=='giveaway')returnTab=active.dataset.tab;
          openView(Date.now());
        }else{
          closeView();
        }
      },true);
    });
    document.addEventListener('click',event=>{
      const detailButton=event.target.closest('[data-giveaway-detail]');
      if(detailButton){showDetail(detailButton.dataset.giveawayDetail,Date.now());return}
      if(event.target.closest('[data-giveaway-detail-back]')){showList();return}
      if(event.target.closest('[data-giveaway-exit]')){exitView()}
    });
  }

  function render(payload,_legacyElement,nowMs=Date.now()){
    lastPayload=payload&&typeof payload==='object'?payload:null;
    selectedGameKey=null;
    bindBrowser();
    renderSurface(nowMs);
    showList();
  }

  return {viewModel,navState,buildListMarkup,buildDetailMarkup,render,showList,showDetail,openView,closeView,remainingText,deadlineText,validClaimUrl,EMPTY_COPY,UNAVAILABLE_COPY,UPDATING_COPY,ANALYSIS_INCOMPLETE_COPY};
});
