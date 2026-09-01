(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.GiveawayUI=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  const STORE_LABELS={steam:'Steam',epic:'Epic Games',gog:'GOG'};
  const EMPTY_COPY='Сейчас активных раздач не найдено.';
  const UNAVAILABLE_COPY='Раздачи временно не удалось проверить полностью.';
  const UPDATING_COPY='Текущие раздачи закончились, данные обновляются.';

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

  function viewModel(payload,nowMs=Date.now()){
    const data=payload&&typeof payload==='object'?payload:{};
    const freshUntil=parseTime(data.fresh_until_utc);
    if(data.schema_version!==1||data.source_contract!=='CROSS-PLATFORM-GIVEAWAY-V1'||!Number.isFinite(freshUntil)||freshUntil<=nowMs){
      return {state:'unavailable',message:UNAVAILABLE_COPY,games:[]};
    }
    if(data.state==='unavailable')return {state:'unavailable',message:UNAVAILABLE_COPY,games:[]};
    if(data.state==='empty')return {state:'empty',message:EMPTY_COPY,games:[]};
    if(data.state!=='active')return {state:'unavailable',message:UNAVAILABLE_COPY,games:[]};

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
    if(!games.length)return {state:'updating',message:UPDATING_COPY,games:[]};
    return {state:'active',message:null,games};
  }

  function buildMarkup(payload,nowMs=Date.now()){
    const view=viewModel(payload,nowMs);
    const heading='<div class="giveaway-heading"><div><h2>Бесплатные раздачи</h2><p>Заберите до указанного срока — после получения игра остаётся в библиотеке.</p></div></div>';
    if(view.state!=='active'){
      return `${heading}<div class="giveaway-state giveaway-state-${escapeHtml(view.state)}">${escapeHtml(view.message)}</div>`;
    }
    const cards=view.games.map(game=>{
      const offers=game.offers.map(offer=>{
        const label=storeLabel(offer.storefront);
        return `<div class="giveaway-offer"><div class="giveaway-offer-meta"><span class="giveaway-store">${escapeHtml(label)}</span><span class="giveaway-deadline">до ${escapeHtml(deadlineText(offer.promotion_end_utc))}</span></div><a class="giveaway-claim" href="${escapeHtml(offer.claim_url)}" target="_blank" rel="noopener noreferrer">Забрать в ${escapeHtml(label)}</a></div>`;
      }).join('');
      return `<article class="giveaway-card" data-giveaway-key="${escapeHtml(game.game_key)}"><h3>${escapeHtml(game.title)}</h3>${offers}</article>`;
    }).join('');
    return `${heading}<div class="giveaway-list">${cards}</div>`;
  }

  function render(payload,element,nowMs=Date.now()){
    if(!element)return;
    element.innerHTML=buildMarkup(payload,nowMs);
    element.classList.remove('hidden');
  }

  return {viewModel,buildMarkup,render,deadlineText,validClaimUrl,EMPTY_COPY,UNAVAILABLE_COPY,UPDATING_COPY};
});
