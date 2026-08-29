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
if(titleNode&&windowsNode&&achievementsNode){
  const refreshExtras=()=>{
    syncPriorityQueue();
    let g=null;
    try{g=currentGame()}catch{}
    if(!g)return;
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
  };
  new MutationObserver(refreshExtras).observe(titleNode,{childList:true,characterData:true,subtree:true});
  refreshExtras();
}else{
  syncPriorityQueue();
}
