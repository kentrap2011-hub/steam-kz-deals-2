(()=>{
  const shot=document.getElementById('shot');
  if(!shot)return;

  const style=document.createElement('style');
  style.textContent=`
    .photo-viewer{position:fixed;inset:0;z-index:9999;background:#000;display:none;align-items:center;justify-content:center;touch-action:none;overscroll-behavior:none}
    .photo-viewer.open{display:flex}
    .photo-viewer:fullscreen{display:flex;width:100vw;height:100vh;background:#000}
    .photo-viewer img{width:100%;height:100%;object-fit:contain;user-select:none;-webkit-user-drag:none}
    .photo-viewer-close{position:absolute;top:max(12px,env(safe-area-inset-top));right:max(12px,env(safe-area-inset-right));z-index:2;width:44px;height:44px;border:0;border-radius:50%;background:rgba(0,0,0,.58);color:#fff;font-size:30px;line-height:1;display:grid;place-items:center}
    .photo-viewer-count{position:absolute;left:50%;bottom:max(12px,env(safe-area-inset-bottom));transform:translateX(-50%);z-index:2;padding:7px 11px;border-radius:999px;background:rgba(0,0,0,.58);color:#fff;font:600 14px/1 system-ui,sans-serif}
    #shot{cursor:zoom-in}
  `;
  document.head.appendChild(style);

  const viewer=document.createElement('div');
  viewer.className='photo-viewer';
  viewer.setAttribute('aria-hidden','true');
  viewer.innerHTML='<img alt=""><button class="photo-viewer-close" type="button" aria-label="Закрыть">×</button><div class="photo-viewer-count"></div>';
  document.body.appendChild(viewer);

  const image=viewer.querySelector('img');
  const closeBtn=viewer.querySelector('.photo-viewer-close');
  const count=viewer.querySelector('.photo-viewer-count');
  let openPointer=null;
  let viewerPointer=null;

  function updateViewer(){
    const g=currentGame();
    if(!g)return;
    const urls=shotUrls(g);
    if(!urls.length)return;
    image.src=urls[currentShot];
    image.alt=`${g.title}: скриншот ${currentShot+1}`;
    count.textContent=`${currentShot+1} / ${urls.length}`;
  }

  async function lockLandscape(){
    try{
      if(screen.orientation?.lock)await screen.orientation.lock('landscape');
    }catch{}
  }

  function unlockOrientation(){
    try{screen.orientation?.unlock?.()}catch{}
  }

  async function openViewer(){
    const g=currentGame();
    if(!g||!shotUrls(g).length)return;
    updateViewer();
    viewer.classList.add('open');
    viewer.setAttribute('aria-hidden','false');
    try{
      if(viewer.requestFullscreen){
        await viewer.requestFullscreen();
        await lockLandscape();
      }
    }catch{}
  }

  async function closeViewer(){
    if(document.fullscreenElement===viewer){
      try{await document.exitFullscreen()}catch{}
    }else{
      viewer.classList.remove('open');
      viewer.setAttribute('aria-hidden','true');
      unlockOrientation();
    }
  }

  shot.addEventListener('pointerdown',e=>{
    openPointer={id:e.pointerId,x:e.clientX,y:e.clientY};
  },true);
  shot.addEventListener('pointerup',e=>{
    if(!openPointer||openPointer.id!==e.pointerId)return;
    const dx=e.clientX-openPointer.x,dy=e.clientY-openPointer.y;
    openPointer=null;
    if(Math.hypot(dx,dy)<14)openViewer();
  },true);
  shot.addEventListener('pointercancel',()=>{openPointer=null},true);

  viewer.addEventListener('pointerdown',e=>{
    if(e.target.closest('.photo-viewer-close'))return;
    viewerPointer={id:e.pointerId,x:e.clientX,y:e.clientY};
  });
  viewer.addEventListener('pointerup',e=>{
    if(!viewerPointer||viewerPointer.id!==e.pointerId)return;
    const dx=e.clientX-viewerPointer.x,dy=e.clientY-viewerPointer.y;
    viewerPointer=null;
    if(Math.abs(dx)>45&&Math.abs(dx)>Math.abs(dy)*1.2){
      const g=currentGame();
      if(g){
        setShot(g,currentShot+(dx<0?1:-1));
        updateViewer();
      }
    }
  });
  viewer.addEventListener('pointercancel',()=>{viewerPointer=null});
  closeBtn.addEventListener('click',closeViewer);

  document.addEventListener('fullscreenchange',()=>{
    if(document.fullscreenElement!==viewer&&viewer.classList.contains('open')){
      viewer.classList.remove('open');
      viewer.setAttribute('aria-hidden','true');
      unlockOrientation();
    }
  });
})();
