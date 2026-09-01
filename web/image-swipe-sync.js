(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ImageSwipeSync=api;
  if(typeof document==='undefined')return;
  if(typeof setShot!=='function'||typeof shotUrls!=='function'||typeof currentGame!=='function')return;

  const guard=api.createCommitGuard();

  function requestKey(g,index,url){return `${String(g?.id??'')}\u001f${index}\u001f${url||''}`}
  function stillCurrent(request,g,index,url){
    const active=currentGame();
    if(!guard.isCurrent(request)||!active)return false;
    if(String(active.id)!==String(g?.id))return false;
    if(currentShot!==index)return false;
    return shotUrls(active)[index]===url;
  }
  function clearVisual(shot,bg){
    shot.removeAttribute('src');
    shot.style.visibility='hidden';
    bg.style.backgroundImage='none';
  }

  setShot=function(g,index){
    const urls=shotUrls(g);
    currentShot=urls.length?((index%urls.length)+urls.length)%urls.length:0;
    const shotIndex=currentShot;
    const url=urls[shotIndex];
    const shot=$('shot'),bg=$('galleryBg');
    const request=guard.begin(requestKey(g,shotIndex,url));

    $('galleryCount').textContent=urls.length?`${shotIndex+1} / ${urls.length}`:'нет скриншотов';
    $('dots').innerHTML=urls.map((_,i)=>`<span class="dot ${i===shotIndex?'on':''}"></span>`).join('');

    if(!url){
      shot.removeAttribute('src');
      shot.style.visibility='';
      shot.alt='Скриншоты пока недоступны';
      bg.style.backgroundImage='none';
      return;
    }

    shot.alt=`${g.title}: скриншот ${shotIndex+1}`;
    clearVisual(shot,bg);

    const loader=new Image();
    loader.decoding='async';
    let committed=false;
    const commit=()=>{
      if(committed||!stillCurrent(request,g,shotIndex,url))return false;
      committed=true;
      shot.src=url;
      shot.style.visibility='';
      bg.style.backgroundImage=`url("${url.replaceAll('"','')}")`;
      return true;
    };
    loader.onload=commit;
    loader.onerror=()=>{
      if(!stillCurrent(request,g,shotIndex,url))return;
      shot.removeAttribute('src');
      shot.style.visibility='';
      bg.style.backgroundImage='none';
    };
    loader.src=url;
    if(loader.complete&&loader.naturalWidth>0)commit();
  };
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  function createCommitGuard(){
    let generation=0;
    let activeKey=null;
    return {
      begin(key){
        generation+=1;
        activeKey=String(key);
        return Object.freeze({generation,key:activeKey});
      },
      isCurrent(request){
        return !!request&&request.generation===generation&&request.key===activeKey;
      },
      invalidate(){
        generation+=1;
        activeKey=null;
      },
    };
  }
  return {createCommitGuard};
});
