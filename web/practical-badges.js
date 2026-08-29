(()=>{
  const windows=document.getElementById('windows');
  const achievements=document.getElementById('achievements');
  const title=document.getElementById('title');
  if(!windows||!achievements||!title)return;
  function render(){
    let g=null;try{g=currentGame()}catch{}
    const p=g?.practical||{};
    const ws=p.windows_status;
    const labels={modern:'✓ Windows 10/11',older_but_plausible:'Windows 7/8+',legacy:'⚠ Старая Windows'};
    windows.textContent=labels[ws]||'';
    windows.classList.toggle('hidden',!labels[ws]);
    if(p.steam_achievements===true){
      achievements.textContent=p.achievement_total?`🏆 ${p.achievement_total} достиж.`:'🏆 Достижения есть';
      achievements.classList.remove('hidden');
    }else if(p.steam_achievements===false){
      achievements.textContent='Без достижений';
      achievements.classList.remove('hidden');
    }else{
      achievements.textContent='';
      achievements.classList.add('hidden');
    }
  }
  new MutationObserver(render).observe(title,{childList:true,characterData:true,subtree:true});
  render();
})();
