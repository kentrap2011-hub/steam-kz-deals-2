const DATA_URL='data/current.json';
const STORAGE_KEY='steam-deals-visual-state-v1';
const QUEUE_VERSION=3;
let data={items:[],source_mailing_updated_at_utc:null};
let items=[];
let byId=new Map();
let state=loadState();
let currentTab='feed';
let currentShot=0;
let galleryPointer=null;
let cardPointer=null;
let toastTimer=null;

const $=id=>document.getElementById(id);
const card=$('gameCard');
const gallery=$('gallery');

function loadState(){
  try{return JSON.parse(localStorage.getItem(STORAGE_KEY))||{games:{},queue:{source:null,ids:[],cursor:0,version:QUEUE_VERSION}}}
  catch{return {games:{},queue:{source:null,ids:[],cursor:0,version:QUEUE_VERSION}}}
}
function saveState(){localStorage.setItem(STORAGE_KEY,JSON.stringify(state))}
function rec(id){
  if(!state.games[id]) state.games[id]={status:'queue',seen:0,last_seen:null,first_source:data.source_mailing_updated_at_utc};
  return state.games[id];
}
function isNew(id){const r=rec(id);return r.first_source===data.source_mailing_updated_at_utc&&r.seen===0}
function notify(text){const t=$('toast');t.textContent=text;t.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.classList.remove('show'),1500)}
function fmtRub(v){return v==null?'—':`${Math.round(v).toLocaleString('ru-RU')} ₽`}
function fmtDate(value){
  if(!value)return null;
  const d=new Date(value);if(Number.isNaN(d.getTime()))return null;
  return new Intl.DateTimeFormat('ru-RU',{day:'numeric',month:'long',hour:'2-digit',minute:'2-digit'}).format(d);
}
function deadlineText(value){
  if(!value)return 'Срок скидки неизвестен';
  const d=new Date(value),ms=d-Date.now();
  if(ms<=0)return '⚠ Скидка закончилась';
  const hours=Math.ceil(ms/3600000);
  if(hours<=24)return `⚠ Заканчивается менее чем через ${hours} ч.`;
  const days=Math.ceil(ms/86400000);
  return `⏱ До ${fmtDate(value)} · осталось ${days} дн.`;
}
function sourceLabel(){
  if(!data.source_mailing_updated_at_utc)return '';
  const d=new Date(data.source_mailing_updated_at_utc);
  return `Данные: ${new Intl.DateTimeFormat('ru-RU',{day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'}).format(d)}`;
}
function buildQueue(){
  const source=data.source_mailing_updated_at_utc||'unknown';
  const activeIds=new Set(items.map(x=>x.id));
  for(const id of activeIds) rec(id);
  if(state.queue?.source!==source||state.queue?.version!==QUEUE_VERSION){
    state.queue={source,ids:items.map(x=>x.id),cursor:0,version:QUEUE_VERSION};
    saveState();return;
  }
  let q=(state.queue.ids||[]).filter(id=>activeIds.has(id));
  const missing=items.map(x=>x.id).filter(id=>!q.includes(id));
  q.push(...missing);
  const cursor=Math.max(0,Math.min(Number(state.queue.cursor)||0,Math.max(0,q.length-1)));
  state.queue={source,ids:q,cursor,version:QUEUE_VERSION};saveState();
}
function currentIndex(){return Math.max(0,Math.min(Number(state.queue.cursor)||0,Math.max(0,state.queue.ids.length-1)))}
function currentGame(){return byId.get(state.queue.ids[currentIndex()])}
function queueCount(){return state.queue.ids.filter(id=>byId.has(id)).length}
function counts(){
  let liked=0,final=0,newCount=0,repeat=0,unseen=0;
  for(const g of items){const r=rec(g.id);if(r.status==='liked')liked++;if(r.status==='final')final++;if(isNew(g.id))newCount++;if((r.seen||0)>0)repeat++;else unseen++}
  return {liked,final,newCount,repeat,unseen};
}
function renderStats(){
  const c=counts();
  $('stats').innerHTML=`<div class="stat"><b>${c.newCount}</b><span>🆕 новые</span></div><div class="stat"><b>${c.unseen}</b><span>не смотрел</span></div><div class="stat"><b>${c.liked}</b><span>♡ интересно</span></div><div class="stat"><b>${c.repeat}</b><span>🔁 видел</span></div>`;
  $('feedCount').textContent=`(${queueCount()})`;$('likedCount').textContent=c.liked?`(${c.liked})`:'';$('finalCount').textContent=c.final?`(${c.final})`:'';
  $('freshness').textContent=sourceLabel();
}
function renderTabs(){
  document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===currentTab));
  $('feedView').classList.toggle('hidden',currentTab!=='feed');$('likedView').classList.toggle('hidden',currentTab!=='liked');$('finalView').classList.toggle('hidden',currentTab!=='final');
}
function shotUrls(g){const arr=(g.screenshots||[]).filter(Boolean);if(!arr.length&&g.header_image)arr.push(g.header_image);return arr}
function preloadNearby(){
  const i=currentIndex();state.queue.ids.slice(i,Math.min(state.queue.ids.length,i+3)).forEach(id=>{const g=byId.get(id);if(!g)return;shotUrls(g).forEach(u=>{const im=new Image();im.decoding='async';im.src=u})});
}
function setShot(g,index){
  const urls=shotUrls(g);currentShot=urls.length?((index%urls.length)+urls.length)%urls.length:0;
  const url=urls[currentShot];
  if(url){$('shot').src=url;$('shot').alt=`${g.title}: скриншот ${currentShot+1}`;$('galleryBg').style.backgroundImage=`url("${url.replaceAll('"','')}")`}
  else{$('shot').removeAttribute('src');$('shot').alt='Скриншоты пока недоступны';$('galleryBg').style.backgroundImage='none'}
  $('galleryCount').textContent=urls.length?`${currentShot+1} / ${urls.length}`:'нет скриншотов';
  $('dots').innerHTML=urls.map((_,i)=>`<span class="dot ${i===currentShot?'on':''}"></span>`).join('');
}
function textList(el,values,empty){
  const arr=(values||[]).filter(Boolean);el.innerHTML=arr.length?arr.map(x=>`<div>${escapeHtml(x)}</div>`).join('<br>'):`<span class="muted">${escapeHtml(empty)}</span>`;
}
function escapeHtml(s){return String(s??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
function renderOffers(g){
  const offers=(g.offers||[]).filter(o=>o.current_price_rub!=null);
  $('offers').innerHTML=offers.map((o,i)=>{
    const hist=o.previously_free?'ранее бесплатно':(o.historical_minimum_rub!=null?`ист. минимум ${fmtRub(o.historical_minimum_rub)}`:'история не подтверждена');
    const old=`<span style="text-decoration:line-through">${fmtRub(o.original_price_rub)}</span>`;
    return `<div class="offer"><div class="offer-top"><div class="offer-title">${escapeHtml(o.title||g.title)}${i===0?' · основной':''}</div><div class="offer-price">${fmtRub(o.current_price_rub)}</div></div><div class="offer-meta">${old} · −${o.discount_percent}% · ${hist}</div><div class="offer-actions"><button class="offer-link" type="button" data-open-web="${escapeHtml(o.web_url||'')}" data-open-steam="${escapeHtml(o.steam_url||'')}">Открыть вариант в Steam</button></div></div>`;
  }).join('')||'<div class="muted small">Дополнительных вариантов сейчас нет.</div>';
}
function renderFeed(){
  const g=currentGame();const pos=currentIndex();
  $('emptyFeed').classList.toggle('hidden',!!g);card.classList.toggle('hidden',!g);$('position').textContent=g?`Приоритет: ${pos+1} из ${queueCount()}`:'';$('seenInfo').textContent=g?(rec(g.id).seen?`Показана раньше: ${rec(g.id).seen}×`:'Первый показ'):'';
  if(!g)return;
  currentShot=0;setShot(g,0);preloadNearby();
  const r=rec(g.id);$('newBadge').classList.toggle('hidden',!isNew(g.id));$('repeatBadge').classList.toggle('hidden',!(r.seen>0));$('repeatBadge').textContent=r.seen?`🔁 Показ №${r.seen+1}`:'';
  $('title').textContent=g.title;$('decision').textContent=g.decision||'';$('price').textContent=fmtRub(g.current_price_rub);$('oldPrice').textContent=fmtRub(g.original_price_rub);$('discount').textContent=`−${g.discount_percent}%`;
  $('histPrice').textContent=g.previously_free?'Ранее была бесплатной':`Ист. минимум: ${g.historical_minimum_rub==null?'нет данных':fmtRub(g.historical_minimum_rub)}`;
  $('deadline').textContent=deadlineText(g.sale_end_utc);$('summary').textContent=g.summary||'Краткое описание пока недоступно.';
  const gp=(g.gameplay_points||[]).filter(Boolean);$('gameplaySection').classList.toggle('hidden',!gp.length);$('gameplay').innerHTML=gp.map(x=>`<li>${escapeHtml(x)}</li>`).join('');
  textList($('whyFit'),g.why_fit,'Персональная причина пока не подготовлена.');textList($('risks'),g.risks,'Риск пока не подготовлен.');
  $('fit').textContent=`Соответствие вкусу: ${g.fit==='strong'?'сильное':'умеренное'}`;$('wishlist').classList.toggle('hidden',!g.wishlist);renderOffers(g);
  $('likeBtn').textContent=r.status==='liked'?'♡ Уже интересно':'♡ Интересно';
  $('finalBtn').textContent=r.status==='final'?'🏆 Уже в финале':'🏆 В финал';
}
function miniCard(g,status){
  const img=shotUrls(g)[0]||'';return `<div class="list-card"><img src="${escapeHtml(img)}" alt=""><div><div class="list-title">${escapeHtml(g.title)}</div><div class="list-meta">${fmtRub(g.current_price_rub)} · −${g.discount_percent}% · ${escapeHtml(deadlineText(g.sale_end_utc))}</div><div class="list-actions">${status==='liked'?`<button class="small-btn" data-to-final="${escapeHtml(g.id)}" type="button">🏆 В финал</button>`:''}<button class="small-btn" data-focus="${escapeHtml(g.id)}" type="button">Показать в ленте</button></div></div></div>`;
}
function renderLists(){
  const liked=items.filter(g=>rec(g.id).status==='liked'),finals=items.filter(g=>rec(g.id).status==='final');
  $('likedList').innerHTML=liked.length?liked.map(g=>miniCard(g,'liked')).join(''):'<div class="empty">Пока пусто.</div>';
  $('finalList').innerHTML=finals.length?finals.map(g=>miniCard(g,'final')).join(''):'<div class="empty">Пока пусто.</div>';
}
function render(){renderTabs();renderStats();renderFeed();renderLists();saveState()}
function markSeen(g){if(!g)return;const r=rec(g.id);r.seen=(r.seen||0)+1;r.last_seen=new Date().toISOString()}
function navigate(delta){
  const g=currentGame();const old=currentIndex();const next=Math.max(0,Math.min(state.queue.ids.length-1,old+delta));if(next===old)return;
  markSeen(g);state.queue.cursor=next;saveState();render();window.scrollTo({top:0,behavior:'smooth'});
}
function markCurrent(kind){
  const g=currentGame();if(!g)return;const r=rec(g.id);
  if(kind==='liked'){r.status='liked';notify(`${g.title} → интересно ♡`)}
  if(kind==='final'){r.status='final';notify(`${g.title} → финал 🏆`)}
  saveState();render();
}
function sendCurrentToEnd(){
  const g=currentGame();if(!g)return;const i=currentIndex();state.queue.ids.splice(i,1);state.queue.ids.push(g.id);state.queue.cursor=Math.min(i,state.queue.ids.length-1);markSeen(g);saveState();notify(`${g.title} → в конец очереди`);render();window.scrollTo({top:0,behavior:'smooth'});
}
function focusGame(id){
  const idx=state.queue.ids.indexOf(id);if(idx<0)return;state.queue.cursor=idx;currentTab='feed';$('searchDialog').open&&$('searchDialog').close();render();window.scrollTo({top:0,behavior:'smooth'});
}
function openSteam(steamUrl,webUrl){
  if(!webUrl&&!steamUrl)return;
  if(!steamUrl){location.href=webUrl;return}
  let hidden=false;const onVis=()=>{if(document.hidden)hidden=true};document.addEventListener('visibilitychange',onVis,{once:true});location.href=steamUrl;
  setTimeout(()=>{if(!hidden&&webUrl)location.href=webUrl},900);
}
function searchRender(){
  const q=$('searchInput').value.trim().toLocaleLowerCase('ru-RU');
  const results=q?items.filter(g=>g.title.toLocaleLowerCase('ru-RU').includes(q)).slice(0,50):items.slice(0,30);
  $('searchResults').innerHTML=results.length?results.map(g=>`<button class="search-item" type="button" data-search-focus="${escapeHtml(g.id)}"><b>${escapeHtml(g.title)}</b><span>${fmtRub(g.current_price_rub)} · −${g.discount_percent}% · ${g.decision||''}</span></button>`).join(''):'<div class="empty">В текущем активном списке такой игры нет.</div>';
}

async function init(){
  try{const res=await fetch(DATA_URL,{cache:'no-store'});if(!res.ok)throw new Error('data');data=await res.json();items=(data.items||[]).filter(x=>x&&x.id);byId=new Map(items.map(x=>[x.id,x]));buildQueue();render()}
  catch{$('emptyFeed').classList.remove('hidden');$('emptyFeed').textContent='Не удалось загрузить текущий список игр.';$('gameCard').classList.add('hidden')}
}

document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>{currentTab=b.dataset.tab;render()}));
$('likeBtn').addEventListener('click',()=>markCurrent('liked'));$('finalBtn').addEventListener('click',()=>markCurrent('final'));$('endBtn').addEventListener('click',sendCurrentToEnd);
$('steamBtn').addEventListener('click',()=>{const g=currentGame();if(g)openSteam(g.steam_url,g.web_url)});
$('searchBtn').addEventListener('click',()=>{$('searchDialog').showModal();$('searchInput').value='';searchRender();setTimeout(()=>$('searchInput').focus(),50)});$('searchInput').addEventListener('input',searchRender);

document.addEventListener('click',e=>{
  const o=e.target.closest('[data-open-web]');if(o){openSteam(o.dataset.openSteam||null,o.dataset.openWeb||null);return}
  const f=e.target.closest('[data-focus]');if(f){focusGame(f.dataset.focus);return}
  const sf=e.target.closest('[data-search-focus]');if(sf){focusGame(sf.dataset.searchFocus);return}
  const tf=e.target.closest('[data-to-final]');if(tf){rec(tf.dataset.toFinal).status='final';render();return}
});

gallery.addEventListener('pointerdown',e=>{galleryPointer={id:e.pointerId,x:e.clientX,y:e.clientY}});
gallery.addEventListener('pointerup',e=>{if(!galleryPointer||galleryPointer.id!==e.pointerId)return;const dx=e.clientX-galleryPointer.x,dy=e.clientY-galleryPointer.y;galleryPointer=null;if(Math.abs(dx)>45&&Math.abs(dx)>Math.abs(dy)*1.2){const g=currentGame();if(g)setShot(g,currentShot+(dx<0?1:-1))}});gallery.addEventListener('pointercancel',()=>galleryPointer=null);

card.addEventListener('pointerdown',e=>{if(e.target.closest('.gallery,button,a,input'))return;cardPointer={id:e.pointerId,x:e.clientX,y:e.clientY,dx:0,drag:false}});
card.addEventListener('pointermove',e=>{if(!cardPointer||cardPointer.id!==e.pointerId)return;const dx=e.clientX-cardPointer.x,dy=e.clientY-cardPointer.y;cardPointer.dx=dx;if(!cardPointer.drag&&Math.abs(dx)>10&&Math.abs(dx)>Math.abs(dy)*1.25){cardPointer.drag=true;card.classList.add('dragging')}if(cardPointer.drag){const lim=Math.max(-90,Math.min(90,dx));card.style.transform=`translateX(${lim}px)`;card.style.opacity=String(1-Math.min(.18,Math.abs(lim)/500))}});
function endCard(e){if(!cardPointer||cardPointer.id!==e.pointerId)return;const {dx,drag}=cardPointer;cardPointer=null;card.classList.remove('dragging');card.style.transform='';card.style.opacity='';if(drag&&Math.abs(dx)>70)navigate(dx<0?1:-1)}
card.addEventListener('pointerup',endCard);card.addEventListener('pointercancel',()=>{cardPointer=null;card.classList.remove('dragging');card.style.transform='';card.style.opacity='' });

init();
