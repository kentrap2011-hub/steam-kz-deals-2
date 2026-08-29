(()=>{
  const steamBtn=document.getElementById('steamBtn');
  if(!steamBtn||!/Android/i.test(navigator.userAgent))return;

  steamBtn.addEventListener('click',e=>{
    let g=null;try{g=currentGame()}catch{}
    if(!g)return;

    const web=g.web_url||'';
    const match=web.match(/store\.steampowered\.com\/app\/(\d+)/i);
    const appid=(g.base_appids||[])[0]||(match&&match[1]);
    if(!appid)return;

    e.preventDefault();
    e.stopImmediatePropagation();
    location.href=`https://s.team/a/${appid}`;
  },true);
})();
