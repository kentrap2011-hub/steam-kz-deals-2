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
