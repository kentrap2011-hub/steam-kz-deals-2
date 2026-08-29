(()=>{
  const steamBtn=document.getElementById('steamBtn');
  if(!steamBtn||!/Android/i.test(navigator.userAgent))return;

  const style=document.createElement('style');
  style.textContent=`
    .steam-test{margin-top:10px;padding:12px;border:1px solid rgba(255,255,255,.12);border-radius:12px;background:rgba(255,255,255,.035)}
    .steam-test summary{cursor:pointer;font-weight:700}
    .steam-test-note{margin:8px 0 10px;font-size:13px;line-height:1.35;opacity:.78}
    .steam-test-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
    .steam-test-grid button{min-height:42px}
  `;
  document.head.appendChild(style);

  const box=document.createElement('details');
  box.className='steam-test';
  box.open=true;
  box.innerHTML=`
    <summary>Тест открытия в приложении Steam</summary>
    <div class="steam-test-note">Способы 1–5 уже проверены. Новые тесты 6–8 используют официальный короткий домен Steam s.team, который Android также связывает с приложением Steam.</div>
    <div class="steam-test-grid">
      <button class="btn" type="button" data-steam-test="mobile">1 · Steam Mobile</button>
      <button class="btn" type="button" data-steam-test="component">2 · Прямо в Steam</button>
      <button class="btn" type="button" data-steam-test="openurl">3 · Steam openurl</button>
      <button class="btn" type="button" data-steam-test="app">4 · Steam app</button>
      <button class="btn" type="button" data-steam-test="storeapp">5 · Steam store/app</button>
      <button class="btn" type="button" data-steam-test="steamshort">6 · s.team</button>
      <button class="btn" type="button" data-steam-test="steamshortintent">7 · s.team → Steam</button>
      <button class="btn" type="button" data-steam-test="steamshortmobile">8 · s.team внутри Steam</button>
    </div>`;
  steamBtn.parentElement.insertAdjacentElement('afterend',box);

  function currentTarget(){
    let g=null;try{g=currentGame()}catch{}
    if(!g)return null;
    const web=g.web_url||'';
    const m=web.match(/store\.steampowered\.com\/app\/(\d+)/i);
    const appid=(g.base_appids||[])[0]||(m&&m[1]);
    if(!appid)return null;
    return {appid:String(appid),web:`https://store.steampowered.com/app/${appid}`,short:`https://s.team/a/${appid}`};
  }

  box.addEventListener('click',e=>{
    const b=e.target.closest('[data-steam-test]');if(!b)return;
    const t=currentTarget();if(!t)return;
    const kind=b.dataset.steamTest;
    if(kind==='mobile') location.href=`steammobile://openurl/${t.web}`;
    if(kind==='component') location.href=`intent://openurl/${t.web}#Intent;scheme=steammobile;package=com.valvesoftware.android.steam.community;component=com.valvesoftware.android.steam.community/.activity.MainActivity;end`;
    if(kind==='openurl') location.href=`steam://openurl/${t.web}`;
    if(kind==='app') location.href=`steam://app/${t.appid}`;
    if(kind==='storeapp') location.href=`steam://store/app/${t.appid}`;
    if(kind==='steamshort') location.href=t.short;
    if(kind==='steamshortintent') location.href=`intent://s.team/a/${t.appid}#Intent;scheme=https;package=com.valvesoftware.android.steam.community;action=android.intent.action.VIEW;category=android.intent.category.BROWSABLE;end`;
    if(kind==='steamshortmobile') location.href=`steammobile://openurl/${t.short}`;
  });
})();
