const DATA_URL='data/current.json';
const STORAGE_KEY='steam-deals-visual-state-v1';
const QUEUE_VERSION=5;
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

function defaultState(){return {games:{},settings:{urgency_first:false},queue:{source:null,signature:null,ids:[],cursor:0,version:QUEUE_VERSION}}}
function loadState(){
  try{
    const saved=JSON.parse(localStorage.getItem(STORAGE_KEY))||defaultState();
    if(!saved.games||typeof saved.games!=='object')saved.games={};
    if(!saved.settings||typeof saved.settings!=='object')saved.settings={};
    if(typeof saved.settings.urgency_first!=='boolean')saved.settings.urgency_first=false;
    if(!saved.queue||typeof saved.queue!=='object')saved.queue={source:null,signature:null,ids:[],cursor:0,version:QUEUE_VERSION};
    return saved;
  }catch{return defaultState()}
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
function urgencyFirstEnabled(){return !!state.settings?.urgency_first}
function scoreOf(g){const n=Number(g?.total_score);return Number.isFinite(n)?n:-Infinity}
function titleCompare(a,b){return String(a?.title||'').localeCompare(String(b?.title||''),'ru',{sensitivity:'base'})}
function automaticOrderGames(){
  const ordered=[...items];
  if(urgencyFirstEnabled()){
    return ordered.sort((a,b)=>{
      const ar=Number(a.priority_rank),br=Number(b.priority_rank);
      if(Number.isFinite(ar)&&Number.isFinite(br)&&ar!==br)return ar-br;
      const scoreDiff=scoreOf(b)-scoreOf(a);if(scoreDiff)return scoreDiff;
      return titleCompare(a,b);
    });
  }
  return ordered.sort((a,b)=>{const scoreDiff=scoreOf(b)-scoreOf(a);return scoreDiff||titleCompare(a,b)});
}
function rankingSignature(){return `urgency:${urgencyFirstEnabled()?1:0}|`+items.map(g=>`${g.id}:${g.priority_rank??''}:${g.total_score??''}`).join('|')}
function canonicalQueueIds(){
  const normal=[],manual=[];
  for(const g of automaticOrderGames()){
    const r=rec(g.id);
    if(r.manual_end_at)manual.push(g.id);else normal.push(g.id);
  }
  manual.sort((a,b)=>(Number(rec(a).manual_end_at)||0)-(Number(rec(b).manual_end_at)||0));
  return [...normal,...manual];
}
function buildQueue(){
  const source=data.source_mailing_updated_at_utc||'unknown';
  const signature=rankingSignature();
  const activeIds=new Set(items.map(x=>x.id));
  for(const id of activeIds) rec(id);
  const oldIds=state.queue?.ids||[];
  const oldCursor=Math.max(0,Math.min(Number(state.queue?.cursor)||0,Math.max(0,oldIds.length-1)));
  const currentId=oldIds[oldCursor]||null;
  if(state.queue?.source!==source||state.queue?.version!==QUEUE_VERSION||state.queue?.signature!==signature){
    const ids=canonicalQueueIds();
    const found=currentId?ids.indexOf(currentId):-1;
    state.queue={source,signature,ids,cursor:found>=0?found:0,version:QUEUE_VERSION};
    saveState();return;
  }
  let q=oldIds.filter(id=>activeIds.has(id));
  const present=new Set(q);
  const canonical=canonicalQueueIds();
  const missingNormal=canonical.filter(id=>!present.has(id)&&!rec(id).manual_end_at);
  const missingManual=canonical.filter(id=>!present.has(id)&&rec(id).manual_end_at);
  const existingNormal=q.filter(id=>!rec(id).manual_end_at);
  const existingManual=q.filter(id=>rec(id).manual_end_at);
  q=[...existingNormal,...missingNormal,...existingManual,...missingManual];
  const cursor=Math.max(0,Math.min(Number(state.queue.cursor)||0,Math.max(0,q.length-1)));
  state.queue={source,signature,ids:q,cursor,version:QUEUE_VERSION};saveState();
}
function currentIndex(){return Math.max(0,Math.min(Number(state.queue.cursor)||0,Math.max(0,state.queue.ids.length-1)))}
function currentGame(){return byId.get(state.queue.ids[currentIndex()])}
function queueCount(){return state.queue.ids.filter(id=>byId.has(id)).length}
function queuePosition(id){const i=state.queue.ids.indexOf(id);return i>=0?i+1:null}
function counts(){
  let liked=0,final=0,wishlist=0,newCount=0,repeat=0,unseen=0;
  for(const g of items){const r=rec(g.id);if(r.status==='liked')liked++;if(r.status==='final')final++;if(g.wishlist)wishlist++;if(isNew(g.id))newCount++;if((r.seen||0)>0)repeat++;else unseen++}
  return {liked,final,wishlist,newCount,repeat,unseen};
}
function renderStats(){
  const c=counts();
  $('stats').innerHTML=`<div class="stat"><b>${c.newCount}</b><span>🆕 новые</span></div><div class="stat"><b>${c.unseen}</b><span>не смотрел</span></div><div class="stat"><b>${c.liked}</b><span>♡ интересно</span></div><div class="stat"><b>${c.repeat}</b><span>🔁 видел</span></div>`;
  $('feedCount').textContent=`(${queueCount()})`;$('wishlistCount').textContent=c.wishlist?`(${c.wishlist})`:'';$('likedCount').textContent=c.liked?`(${c.liked})`:'';$('finalCount').textContent=c.final?`(${c.final})`:'';
  $('freshness').textContent=sourceLabel();
}
function renderTabs(){
  document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.tab===currentTab));
  $('feedView').classList.toggle('hidden',currentTab!=='feed');$('wishlistView').classList.toggle('hidden',currentTab!=='wishlist');$('likedView').classList.toggle('hidden',currentTab!=='liked');$('finalView').classList.toggle('hidden',currentTab!=='final');
}
function renderQueueMode(){
  const btn=$('urgencyBtn');if(!btn)return;
  const on=urgencyFirstEnabled();
  btn.textContent=on?'✓ Срочные':'⏱ Срочные';
  btn.setAttribute('aria-pressed',String(on));
  btn.title=on?'Срочные игры сейчас подняты вверх. Нажми, чтобы вернуться к порядку по баллам.':'Нажми, чтобы поднять игры, скидка на которые заканчивается сегодня или завтра.';
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
function renderRisk(g){
  const status=g.risk_status;
  const el=$('riskStatus');
  if(status&&status.label){
    const allowed=status.code==='serious_risk'?'serious':(status.code==='descriptive_risk'?'descriptive':'none');
    el.textContent=status.label;
    el.className=`risk-status ${allowed}`;
  }else{
    el.textContent='';
    el.className='risk-status hidden';
  }
  textList($('risks'),g.risks,'Риск пока не подготовлен.');
}
function renderPackageDeal(g){
  const p=g.better_purchase_option;
  if(!p||p.package_price_rub==null)return '';
  const count=Number(p.covered_visible_game_count)||0;
  const perGame=p.package_price_per_visible_game_rub!=null?Number(p.package_price_per_visible_game_rub):(count?Number(p.package_price_rub)/count:null);
  const standalone=p.standalone_total_rub;
  const savings=p.savings_rub;
  const savingsPct=p.savings_percent_vs_standalone;
  const titles=(p.covered_visible_titles||[]).filter(Boolean).map(escapeHtml).join(', ');
  const drivesRank=g.score_breakdown?.purchase_route==='fixed_package';
  const rankNote=drivesRank?'Этот набор сейчас определяет балл выгодности покупки и поднимает игру в рейтинге.':'Набор выгоднее покупки этих игр по отдельности, но текущий балл покупки выше или равен у одиночного варианта.';
  const economics=[
    standalone!=null?`по отдельности ${fmtRub(standalone)}`:null,
    savings!=null?`экономия ${fmtRub(savings)}`:null,
    savingsPct!=null?`${Number(savingsPct).toLocaleString('ru-RU',{maximumFractionDigits:1})}% дешевле`:null,
  ].filter(Boolean).join(' · ');
  return `<div class="offer" data-package-highlight="true" style="border-width:2px"><div class="offer-top"><div class="offer-title"><b>🎁 Выгодный набор Steam</b><br>${escapeHtml(p.package_title||'Набор Steam')}</div><div class="offer-price">${fmtRub(p.package_price_rub)}</div></div><div class="offer-meta"><b>${count} игр${perGame!=null?` · ≈ ${fmtRub(perGame)} за игру`:''}</b></div>${economics?`<div class="offer-meta">${economics}</div>`:''}${titles?`<div class="offer-meta">В наборе из текущего списка: ${titles}</div>`:''}<div class="offer-meta"><b>${escapeHtml(rankNote)}</b></div><div class="offer-actions"><button class="offer-link" type="button" data-open-web="${escapeHtml(p.web_url||'')}" data-open-steam="">Открыть набор в Steam</button></div></div>`;
}
function renderOffers(g){
  const packageHtml=renderPackageDeal(g);
  const offers=(g.offers||[]).filter(o=>o.current_price_rub!=null&&o.offer_kind!=='fixed_multi_game_package');
  const regularHtml=offers.map((o,i)=>{
    const hist=o.previously_free?'ранее бесплатно':(o.historical_minimum_rub!=null?`ист. минимум ${fmtRub(o.historical_minimum_rub)}`:'история не подтверждена');
    const old=`<span style="text-decoration:line-through">${fmtRub(o.original_price_rub)}</span>`;
    return `<div class="offer"><div class="offer-top"><div class="offer-title">${escapeHtml(o.title||g.title)}${i===0?' · основной':''}</div><div class="offer-price">${fmtRub(o.current_price_rub)}</div></div><div class="offer-meta">${old} · −${o.discount_percent}% · ${hist}</div><div class="offer-actions"><button class="offer-link" type="button" data-open-web="${escapeHtml(o.web_url||'')}" data-open-steam="${escapeHtml(o.steam_url||'')}">Открыть вариант в Steam</button></div></div>`;
  }).join('');
  $('offers').innerHTML=packageHtml+regularHtml||'<div class="muted small">Дополнительных вариантов сейчас нет.</div>';
}
function scoreComponentHtml(row){
  const points=Number(row?.points)||0;
  const sign=points>0?'+':'';
  const label=escapeHtml(row?.label||(row?.id==='savings'?'Экономия по акции':'Критерий'));
  const detail=row?.value?` · ${escapeHtml(row.value)}`:'';
  if(row?.id==='wishlist'){
    const status=points>0?'есть':'нет';
    return `<span class="score-chip"><span>${label}</span><b>${sign}${points.toLocaleString('ru-RU',{maximumFractionDigits:1})} · ${status}</b></span>`;
  }
  const max=row?.max_points!=null?`/${Number(row.max_points).toLocaleString('ru-RU',{maximumFractionDigits:1})}`:'';
  return `<span class="score-chip"><span>${label}${detail}</span><b>${sign}${points.toLocaleString('ru-RU',{maximumFractionDigits:1})}${max}</b></span>`;
}
function scoreGroupHtml(label,points,max,components){
  return `<div class="score-group"><div class="score-group-head"><span>${escapeHtml(label)}</span><b>${Number(points).toLocaleString('ru-RU',{maximumFractionDigits:1})}/${Number(max).toLocaleString('ru-RU',{maximumFractionDigits:0})}</b></div><div class="score-components">${(components||[]).map(scoreComponentHtml).join('')}</div></div>`;
}
function renderPriority(g){
  const factors=Array.isArray(g.priority_factors)?g.priority_factors:[];
  const score=g.score_breakdown||null;
  const section=$('prioritySection');
  section.classList.toggle('hidden',!factors.length&&!score);
  if(!factors.length&&!score){$('priorityWhy').textContent='';$('priorityFactors').innerHTML='';return}
  const urgencyMode=urgencyFirstEnabled();
  const vs=g.priority_vs_next||null;
  const rank=Number(g.priority_rank)||null;
  const localRank=queuePosition(g.id);
  const parts=[];
  if(localRank)parts.push(`Позиция в текущей очереди: №${localRank}.`);
  if(rec(g.id).manual_end_at){
    parts.push('Игра вручную отправлена в конец очереди.');
  }else if(urgencyMode){
    parts.push('Режим: срочные игры впереди.');
    if(rank&&rank!==localRank)parts.push(`Канонический рейтинг со срочностью: №${rank}.`);
    if(vs&&vs.next_game_title&&vs.explanation)parts.push(`Следующая по каноническому рейтингу — «${vs.next_game_title}». ${vs.explanation}`);
  }else{
    parts.push('Режим: порядок по итоговому баллу; срочность сейчас не меняет очередь.');
  }
  $('priorityWhy').textContent=parts.join(' ');

  const deciding=urgencyMode&&vs&&vs.deciding_factor_id;
  const urgency=factors.find(f=>f.id==='sale_expiry_urgency_asc');
  let html='';
  if(urgency){
    const urgencyNote=urgencyMode?'влияет на текущий порядок':'сейчас не влияет на порядок';
    html+=`<div class="priority-factor ${deciding==='sale_expiry_urgency_asc'?'deciding':''}"><span>${escapeHtml(urgency.label||'Срочность скидки')}</span><b>${escapeHtml(urgency.value??'—')} · ${urgencyNote}</b></div>`;
  }
  if(score){
  html+=`<button class="priority-factor score-total ${!urgencyMode||deciding==='total_score_desc'?'deciding':''}" type="button" data-score-toggle aria-expanded="false" title="Показать детализацию итогового балла"><span>Итоговый балл</span><b>${Number(score.total_score).toLocaleString('ru-RU',{maximumFractionDigits:1})}/${Number(score.total_max).toLocaleString('ru-RU',{maximumFractionDigits:0})}</b></button>`;
  let details='';
  if(score.precision?.label)details+=`<div class="muted small score-precision">Точность вкусовой части: ${escapeHtml(score.precision.label)}${score.precision.is_coarse_legacy?' — детализируем по мере обновления старых оценок.':''}</div>`;
  if(score.purchase_route_label)details+=`<div class="muted small">Покупка для рейтинга: <b>${escapeHtml(score.purchase_route_label)}</b>${score.purchase_route==='fixed_package'&&score.package_score_delta_vs_standalone>0?` · +${Number(score.package_score_delta_vs_standalone).toLocaleString('ru-RU',{maximumFractionDigits:1})} балла против покупки игры отдельно`:''}</div>`;
  details+=`<div class="score-groups">${scoreGroupHtml(score.personal_label||'Насколько подходит тебе',score.personal_score,score.personal_max,score.personal_components)}${scoreGroupHtml(score.purchase_label||'Выгодность покупки',score.purchase_score,score.purchase_max,score.purchase_components)}</div>`;
  html+=`<div class="score-details hidden" data-score-details>${details}</div>`;
}else{
    html+=factors.filter(f=>f.id!=='sale_expiry_urgency_asc').map(f=>`<div class="priority-factor ${f.id===deciding?'deciding':''}"><span>${escapeHtml(f.label||f.id||'Фактор')}</span><b>${escapeHtml(f.value??'—')}</b></div>`).join('');
  }
  $('priorityFactors').innerHTML=html;
}
function renderFeed(){
  const g=currentGame();const pos=currentIndex();
  $('emptyFeed').classList.toggle('hidden',!!g);card.classList.toggle('hidden',!g);$('position').textContent=g?`Приоритет: ${pos+1} из ${queueCount()}`:'';$('seenInfo').textContent=g?(rec(g.id).seen?`Показана раньше: ${rec(g.id).seen}×`:'Первый показ'):'';$('startBtn').classList.toggle('hidden',!g||pos===0);
  if(!g){$('prioritySection').classList.add('hidden');return}
  currentShot=0;setShot(g,0);preloadNearby();
  const r=rec(g.id);$('newBadge').classList.toggle('hidden',!isNew(g.id));$('repeatBadge').classList.toggle('hidden',!(r.seen>0));$('repeatBadge').textContent=r.seen?`🔁 Показ №${r.seen+1}`:'';
  const p=g.better_purchase_option;const packageBadge=p&&p.package_price_rub!=null?` · 🎁 ${Number(p.covered_visible_game_count)||0} игр за ${fmtRub(p.package_price_rub)}`:'';
  $('title').textContent=g.title;$('decision').textContent=`${g.decision||''}${packageBadge}`;$('price').textContent=fmtRub(g.current_price_rub);$('oldPrice').textContent=fmtRub(g.original_price_rub);$('discount').textContent=`−${g.discount_percent}%`;
  $('histPrice').textContent=g.previously_free?'Ранее была бесплатной':`Ист. минимум: ${g.historical_minimum_rub==null?'нет данных':fmtRub(g.historical_minimum_rub)}`;
  $('deadline').textContent=deadlineText(g.sale_end_utc);$('summary').textContent=g.summary||'Краткое описание пока недоступно.';
  const gp=(g.gameplay_points||[]).filter(Boolean);$('gameplaySection').classList.toggle('hidden',!gp.length);$('gameplay').innerHTML=gp.map(x=>`<li>${escapeHtml(x)}</li>`).join('');
  textList($('whyFit'),g.why_fit,'Персональная причина пока не подготовлена.');renderRisk(g);renderPriority(g);
  $('fit').textContent=`Соответствие вкусу: ${g.fit==='strong'?'сильное':'умеренное'}`;$('wishlist').classList.toggle('hidden',!g.wishlist);renderOffers(g);
  $('likeBtn').textContent=r.status==='liked'?'♡ Уже интересно':'♡ Интересно';
  $('finalBtn').textContent=r.status==='final'?'🏆 Уже в финале':'🏆 В финал';
}
function listPositionText(g){
  const q=queuePosition(g.id),p=Number(g.priority_rank)||null;
  if(q&&p&&q!==p)return `№${q} в ленте · рейтинг со срочностью №${p}`;
  if(q)return `№${q} в ленте`;
  if(p)return `рейтинг со срочностью №${p}`;
  return 'Позиция неизвестна';
}
function miniCard(g,status){
  const img=shotUrls(g)[0]||'';
  const place=status==='wishlist'?`★ В желаемом · ${listPositionText(g)} · `:'';
  const score=g.total_score!=null?` · ${Number(g.total_score).toLocaleString('ru-RU',{maximumFractionDigits:1})}/100`:'';
  const p=g.better_purchase_option;const packageText=p&&p.package_price_rub!=null?` · 🎁 ${Number(p.covered_visible_game_count)||0} игр за ${fmtRub(p.package_price_rub)}`:'';
  return `<div class="list-card"><img src="${escapeHtml(img)}" alt=""><div><div class="list-title">${escapeHtml(g.title)}</div><div class="list-meta">${place}${fmtRub(g.current_price_rub)} · −${g.discount_percent}%${score}${packageText} · ${escapeHtml(deadlineText(g.sale_end_utc))}</div><div class="list-actions">${status==='liked'?`<button class="small-btn" data-to-final="${escapeHtml(g.id)}" type="button">🏆 В финал</button>`:''}<button class="small-btn" data-focus="${escapeHtml(g.id)}" type="button">Показать в ленте</button></div></div></div>`;
}
function renderLists(){
  const wishlist=items.filter(g=>g.wishlist),liked=items.filter(g=>rec(g.id).status==='liked'),finals=items.filter(g=>rec(g.id).status==='final');
  $('wishlistList').innerHTML=wishlist.length?wishlist.map(g=>miniCard(g,'wishlist')).join(''):'<div class="empty">В текущем списке нет игр из вишлиста.</div>';
  $('likedList').innerHTML=liked.length?liked.map(g=>miniCard(g,'liked')).join(''):'<div class="empty">Пока пусто.</div>';
  $('finalList').innerHTML=finals.length?finals.map(g=>miniCard(g,'final')).join(''):'<div class="empty">Пока пусто.</div>';
}
function render(){renderTabs();renderStats();renderQueueMode();renderFeed();renderLists();saveState()}
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
  const g=currentGame();if(!g)return;const i=currentIndex();const r=rec(g.id);r.manual_end_at=Date.now();state.queue.ids.splice(i,1);state.queue.ids.push(g.id);state.queue.cursor=Math.min(i,state.queue.ids.length-1);markSeen(g);saveState();notify(`${g.title} → в конец очереди`);render();window.scrollTo({top:0,behavior:'smooth'});
}
function toggleUrgencyFirst(){
  state.settings.urgency_first=!urgencyFirstEnabled();
  buildQueue();
  saveState();
  render();
  notify(urgencyFirstEnabled()?'Срочные игры подняты вверх':'Срочность отключена — порядок по баллам');
}
function focusGame(id){
  const idx=state.queue.ids.indexOf(id);if(idx<0)return;state.queue.cursor=idx;currentTab='feed';$('searchDialog').open&&$('searchDialog').close();render();window.scrollTo({top:0,behavior:'smooth'});
}
function goToStart(){
  if(!state.queue.ids.length||currentIndex()===0)return;state.queue.cursor=0;currentTab='feed';saveState();render();window.scrollTo({top:0,behavior:'smooth'});
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
  $('searchResults').innerHTML=results.length?results.map(g=>{const p=g.better_purchase_option;const pkg=p&&p.package_price_rub!=null?` · 🎁 ${Number(p.covered_visible_game_count)||0} игр за ${fmtRub(p.package_price_rub)}`:'';return `<button class="search-item" type="button" data-search-focus="${escapeHtml(g.id)}"><b>${escapeHtml(g.title)}</b><span>${fmtRub(g.current_price_rub)} · −${g.discount_percent}%${pkg} · ${g.decision||''}</span></button>`}).join(''):'<div class="empty">В текущем активном списке такой игры нет.</div>';
}

async function init(){
  try{const res=await fetch(DATA_URL,{cache:'no-store'});if(!res.ok)throw new Error('data');data=await res.json();items=(data.items||[]).filter(x=>x&&x.id);byId=new Map(items.map(x=>[x.id,x]));buildQueue();render()}
  catch{$('emptyFeed').classList.remove('hidden');$('emptyFeed').textContent='Не удалось загрузить текущий список игр.';$('gameCard').classList.add('hidden')}
}

document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>{currentTab=b.dataset.tab;render()}));
$('likeBtn').addEventListener('click',()=>markCurrent('liked'));$('finalBtn').addEventListener('click',()=>markCurrent('final'));$('endBtn').addEventListener('click',sendCurrentToEnd);$('startBtn').addEventListener('click',goToStart);$('urgencyBtn').addEventListener('click',toggleUrgencyFirst);
$('steamBtn').addEventListener('click',()=>{const g=currentGame();if(g)openSteam(g.steam_url,g.web_url)});
$('searchBtn').addEventListener('click',()=>{$('searchDialog').showModal();$('searchInput').value='';searchRender();setTimeout(()=>$('searchInput').focus(),50)});$('searchInput').addEventListener('input',searchRender);

document.addEventListener('click',e=>{
  const scoreToggle=e.target.closest('[data-score-toggle]');
  if(scoreToggle){
    const details=scoreToggle.parentElement?.querySelector('[data-score-details]');
    if(details){const expanded=scoreToggle.getAttribute('aria-expanded')==='true';scoreToggle.setAttribute('aria-expanded',String(!expanded));scoreToggle.title=expanded?'Показать детализацию итогового балла':'Свернуть детализацию итогового балла';details.classList.toggle('hidden',expanded)}
    return;
  }
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