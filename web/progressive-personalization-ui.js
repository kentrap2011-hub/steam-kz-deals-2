(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ProgressivePersonalizationUI=api;
})(typeof window!=='undefined'?window:globalThis,function(){
  const LABELS={
    analyzed_fit:'Разобрана · подходит вам',
    analysis_incomplete:'Разбор не завершён',
    not_analyzed:'Ещё не разобрана',
  };
  const TIERS={analyzed_fit:1,analysis_incomplete:2,not_analyzed:3};

  function tierOf(game){
    const explicit=Number(game&&game.analysis_tier);
    if(Number.isFinite(explicit)&&explicit>0)return explicit;
    return TIERS[game&&game.analysis_state]||99;
  }
  function urgencyOf(game){
    const value=Number(game&&game.sale_expiry_urgency_rank);
    return Number.isFinite(value)?value:2;
  }
  function tierScore(game){
    const tier=tierOf(game);
    const value=Number(tier===1?game&&game.total_score:game&&game.deterministic_purchase_score);
    return Number.isFinite(value)?value:-Infinity;
  }
  function titleOf(game){return String(game&&game.title||'')}
  function compareGames(a,b,urgencyFirst=false){
    const tierDiff=tierOf(a)-tierOf(b);
    if(tierDiff)return tierDiff;
    if(urgencyFirst){
      const urgencyDiff=urgencyOf(a)-urgencyOf(b);
      if(urgencyDiff)return urgencyDiff;
    }
    const scoreDiff=tierScore(b)-tierScore(a);
    if(scoreDiff)return scoreDiff;
    return titleOf(a).localeCompare(titleOf(b),'ru',{sensitivity:'base'});
  }
  function sortItems(items,urgencyFirst=false){
    return [...(items||[])].sort((a,b)=>compareGames(a,b,urgencyFirst));
  }
  function labelFor(game){
    const state=game&&game.analysis_state;
    if(game&&game.analysis_resolution_pass==='pass2'){
      if(state==='analyzed_fit')return 'Разобрана · PASS 2';
      if(state==='analysis_incomplete')return 'Разбор не завершён · PASS 2';
    }
    return LABELS[state]||'Статус разбора неизвестен';
  }
  function processingLines(status){
    status=status||{};
    const n=key=>Number.isFinite(Number(status[key]))?Number(status[key]):0;
    return [
      ['Всего',n('total_current_candidates')],
      ['Разобрано',n('analyzed_success_count')],
      ['Подходит',n('analyzed_fit_count')],
      ['Не подходит',n('analyzed_not_fit_count')],
      ['Ошибки / не завершено',n('analysis_incomplete_count')],
      ['Ещё не разобрано',n('not_analyzed_count')],
    ];
  }
  return {tierOf,urgencyOf,tierScore,compareGames,sortItems,labelFor,processingLines};
});
