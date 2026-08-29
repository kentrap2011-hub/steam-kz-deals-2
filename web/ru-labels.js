const STATE_KEY='steam-deals-visual-state-v1';
const RANKING_SIGNATURE_KEY='steam-deals-visual-ranking-signature-v1';

function currentRankingSignature(){
  try{
    if(!Array.isArray(items)||!items.length)return '';
    return items.map((g,i)=>`${g.id}:${g.priority_rank??i+1}`).join('|');
  }catch{return ''}
}

function syncPriorityQueue(){
  const signature=currentRankingSignature();
  if(!signature||localStorage.getItem(RANKING_SIGNATURE_KEY)===signature)return;
  try{
    const saved=JSON.parse(localStorage.getItem(STATE_KEY)||'null');
    if(saved&&saved.queue){
      saved.queue.source=null;
      saved.queue.ids=[];
      saved.queue.cursor=0;
      localStorage.setItem(STATE_KEY,JSON.stringify(saved));
    }
    localStorage.setItem(RANKING_SIGNATURE_KEY,signature);
    location.reload();
  }catch{
    localStorage.setItem(RANKING_SIGNATURE_KEY,signature);
  }
}

const fitNode=document.getElementById('fit');
if(fitNode){
  const translateFitLabel=()=>{
    if(fitNode.textContent.startsWith('Taste-fit:')){
      fitNode.textContent=fitNode.textContent.replace('Taste-fit:','Соответствие вкусу:');
    }
  };
  new MutationObserver(translateFitLabel).observe(fitNode,{childList:true,characterData:true,subtree:true});
  translateFitLabel();
}

// On this Android/Steam Mobile combination deep-links launch Steam but do not
// reliably navigate to the requested game. Prefer the exact Store page instead.
openSteam=function(steamUrl,webUrl){
  if(webUrl){
    location.href=webUrl;
    return;
  }
  if(steamUrl) location.href=steamUrl;
};

const titleNode=document.getElementById('title');
const windowsNode=document.getElementById('windows');
const achievementsNode=document.getElementById('achievements');
const risksNode=document.getElementById('risks');

function fallbackRisks(g){
  const existing=(Array.isArray(g?.risks)?g.risks:[]).filter(Boolean);
  const concrete=existing.filter(x=>!String(x).includes('нужно уточнить')&&!String(x).includes('пока не подтверждён'));
  if(concrete.length)return concrete.slice(0,2);

  const p=g?.practical||{};
  const text=String(g?.summary||'').toLowerCase();
  if(p.windows_status==='legacy')return ['Steam указывает только старые версии Windows; на современной системе может понадобиться дополнительная настройка.'];
  if(p.steam_achievements===false)return ['В Steam нет достижений — для тебя это минус по сравнению с похожей игрой с ачивками.'];
  if(/roguel|rogue-lite|roguelite|procedur|забег|процедур/.test(text))return ['Игра опирается на повторные забеги или процедурное повторение; однообразные повторы у тебя часто снижают интерес.'];
  if(/visual novel|point.?and.?click|dialogue|dialog-focused|диалог/.test(text))return ['Заметная часть игры строится на чтении, диалогах или пассивных эпизодах; если активного геймплея окажется мало, интерес может просесть.'];
  if(/management|managing|city-building|simulation|simulator|farming|craft|менедж|управлен|симулятор|крафт/.test(text))return ['Есть заметный слой менеджмента или рутины; если повторяющиеся действия начнут доминировать над новыми ситуациями, игра может утомить.'];
  if(/open world|roam the land as you please|explore as you please|открыт.{0,8}мир/.test(text))return ['Есть риск недостатка направления: тебе открытые пространства лучше заходят, когда постоянно понятно, зачем исследовать и что делать дальше.'];
  if(/turn-based|пошаг/.test(text))return ['Пошаговый темп может ощущаться медленнее привычного тебе активного геймплея, особенно если бои начнут повторяться.'];
  if(/puzzle|puzzler|головолом/.test(text))return ['Головоломки здесь заметная часть игры; если они начнут тормозить темп или повторять один тип решений, интерес может просесть.'];
  if(/platformer|platforming|платформ/.test(text))return ['Платформинг может потребовать повторных попыток на одних и тех же участках; для тебя это риск, если повторы станут важнее новых ситуаций.'];
  if(g?.decision==='ЛУЧШЕ ЖДАТЬ')return ['Даже при подходящей самой игре текущая покупка не оптимальна: коммерческий verdict — «ЛУЧШЕ ЖДАТЬ».'];
  if(g?.fit==='moderate')return ['Соответствие вкусу умеренное, а не сильное: игра прошла отбор, но риск разочарования выше, чем у strong-fit кандидатов.'];
  return existing.length?existing.slice(0,2):['По подтверждённым данным явный персональный минус пока не найден; лучше не выдумывать риск без фактов.'];
}

function renderRisk(g){
  if(!risksNode)return;
  const risks=fallbackRisks(g);
  risksNode.replaceChildren();
  risks.forEach(text=>{
    const row=document.createElement('div');
    row.textContent=text;
    risksNode.appendChild(row);
  });
}

if(titleNode){
  const refreshExtras=()=>{
    syncPriorityQueue();
    let g=null;
    try{g=currentGame()}catch{}
    if(!g)return;

    if(windowsNode&&achievementsNode){
      const p=g.practical||{};
      const labels={modern:'✓ Windows 10/11',older_but_plausible:'Windows 7/8+',legacy:'⚠ Старая Windows'};
      windowsNode.textContent=labels[p.windows_status]||'';
      windowsNode.classList.toggle('hidden',!labels[p.windows_status]);
      if(p.steam_achievements===true){
        achievementsNode.textContent=p.achievement_total?`🏆 ${p.achievement_total} достиж.`:'🏆 Достижения есть';
        achievementsNode.classList.remove('hidden');
      }else if(p.steam_achievements===false){
        achievementsNode.textContent='Без достижений';
        achievementsNode.classList.remove('hidden');
      }else{
        achievementsNode.textContent='';
        achievementsNode.classList.add('hidden');
      }
    }

    renderRisk(g);
  };
  new MutationObserver(refreshExtras).observe(titleNode,{childList:true,characterData:true,subtree:true});
  refreshExtras();
}
