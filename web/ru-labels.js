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

// Steam Mobile has its own URL scheme on Android. Prefer it there;
// do not auto-fallback to Chrome because that can mask a successful app launch.
openSteam=function(steamUrl,webUrl){
  if(!steamUrl&&!webUrl)return;
  if(/Android/i.test(navigator.userAgent)&&webUrl){
    location.href=`steammobile://openurl/${webUrl}`;
    return;
  }
  if(steamUrl){
    location.href=steamUrl;
    return;
  }
  if(webUrl){
    location.href=`steam://openurl/${webUrl}`;
  }
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
