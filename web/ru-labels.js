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
