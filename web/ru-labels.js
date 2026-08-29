const migrationKey='steam-deals-visual-migration-v2';
if(!localStorage.getItem(migrationKey)){
  try{
    const key='steam-deals-visual-state-v1';
    const saved=JSON.parse(localStorage.getItem(key)||'null');
    if(saved&&saved.queue){saved.queue.source=null;localStorage.setItem(key,JSON.stringify(saved));}
    localStorage.setItem(migrationKey,'1');
    location.reload();
  }catch{localStorage.setItem(migrationKey,'1');}
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
  const renderPractical=()=>{
    let g=null;
    try{g=currentGame()}catch{}
    const p=g?.practical||{};
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
  new MutationObserver(renderPractical).observe(titleNode,{childList:true,characterData:true,subtree:true});
  renderPractical();
}
