(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ProgressivePersonalizationUI=api;
})(typeof window!=='undefined'?window:globalThis,function(){
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

  function fastIndicator(game){
    const state=game&&game.fast_stage_state;
    const outcome=game&&game.fast_stage_outcome;
    if(state==='completed'&&outcome==='fit')return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'positive',title:'Быстрый разбор: завершён — подходит'};
    if(state==='completed'&&outcome==='not_fit')return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'negative',title:'Быстрый разбор: завершён — не подходит'};
    if(state==='completed')return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'unknown',title:'Быстрый разбор: завершён — результат не указан'};
    if(state==='incomplete')return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'warning',title:'Быстрый разбор: не завершён'};
    if(state==='error')return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'error',title:'Быстрый разбор: ошибка'};
    if(state==='not_started')return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'idle',title:'Быстрый разбор: ещё не начат'};
    return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'unknown',title:'Быстрый разбор: состояние не опубликовано'};
  }

  function dossierIndicator(game){
    const state=game&&game.dossier_stage_state;
    if(state==='accepted')return {key:'dossier',symbol:'▤',label:'Подготовка досье',tone:'ready',title:'Подготовка досье: принято'};
    if(state==='failed_or_recovery')return {key:'dossier',symbol:'▤',label:'Подготовка досье',tone:'warning',title:'Подготовка досье: ошибка или восстановление'};
    if(state==='not_ready')return {key:'dossier',symbol:'▤',label:'Подготовка досье',tone:'idle',title:'Подготовка досье: ещё не готово'};
    return {key:'dossier',symbol:'▤',label:'Подготовка досье',tone:'unknown',title:'Подготовка досье: состояние не опубликовано'};
  }

  function deepIndicator(game){
    const state=game&&game.deep_stage_state;
    const outcome=game&&game.deep_stage_outcome;
    const recovery=game&&game.deep_recovery_state;
    if(state==='completed'&&outcome==='fit')return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'positive',title:'Глубокий разбор: завершён — подходит'};
    if(state==='completed'&&outcome==='not_fit')return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'negative',title:'Глубокий разбор: завершён — не подходит'};
    if(state==='completed')return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'unknown',title:'Глубокий разбор: завершён — результат не указан'};
    if(state==='waiting_for_dossier')return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'idle',title:'Глубокий разбор: ждёт досье'};
    if(state==='eligible_or_pending')return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'ready',title:'Глубокий разбор: готов или ожидает выполнения'};
    if(state==='incomplete_or_recovery'){
      const recoveryTitles={
        recovery_owned:'восстановление назначено',
        recovery_eligible:'доступно восстановление',
        recovery_pending:'восстановление ожидает выполнения',
        none:'не завершён',
      };
      return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'warning',title:`Глубокий разбор: ${recoveryTitles[recovery]||'не завершён / восстановление'}`};
    }
    if(state==='not_started')return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'idle',title:'Глубокий разбор: ещё не начат'};
    return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'unknown',title:'Глубокий разбор: состояние не опубликовано'};
  }

  function stageIndicators(game){
    return [fastIndicator(game),dossierIndicator(game),deepIndicator(game)];
  }

  function field(status,key){
    if(!status||!Object.prototype.hasOwnProperty.call(status,key))return null;
    const value=status[key];
    if(value===null||typeof value==='boolean')return value;
    const number=Number(value);
    return Number.isFinite(number)?number:value;
  }
  function statisticsSections(status){
    status=status||{};
    return [
      {
        key:'fast',
        title:'Быстрый разбор',
        scopeLabel:'Текущий Fast-scope',
        denominatorKey:'fast_total_current_scope',
        denominator:field(status,'fast_total_current_scope'),
        rows:[
          ['Попытки','fast_attempted_count'],
          ['Завершено: подходит','fast_completed_fit_count'],
          ['Завершено: не подходит','fast_completed_not_fit_count'],
          ['Не завершено','fast_incomplete_count'],
          ['Ошибки','fast_error_count'],
          ['Пропущено после authoritative Deep','fast_skipped_due_to_authoritative_deep_count'],
          ['Осталось','fast_remaining_count'],
        ].map(([label,key])=>({label,key,value:field(status,key)})),
      },
      {
        key:'dossier',
        title:'Подготовка досье',
        scopeLabel:'Текущий Dossier-scope',
        denominatorKey:'dossier_total_current_scope',
        denominator:field(status,'dossier_total_current_scope'),
        rows:[
          ['Принято','dossier_accepted_count'],
          ['Ожидает','dossier_pending_count'],
          ['Ошибка / восстановление','dossier_failed_or_recovery_count'],
          ['Нормальный первый проход завершён','dossier_normal_first_pass_complete'],
          ['Все приняты или восстановлены','dossier_all_accepted_or_recovered_complete'],
        ].map(([label,key])=>({label,key,value:field(status,key)})),
      },
      {
        key:'deep',
        title:'Глубокий разбор',
        scopeLabel:'Текущая цель Deep-покрытия',
        denominatorKey:'deep_total_current_coverage_target',
        denominator:field(status,'deep_total_current_coverage_target'),
        rows:[
          ['Попытка первого прохода','deep_first_pass_attempted_count'],
          ['Authoritative завершено','deep_authoritative_completed_count'],
          ['Завершено: подходит','deep_completed_fit_count'],
          ['Завершено: не подходит','deep_completed_not_fit_count'],
          ['Не завершено / восстановление','deep_incomplete_or_recovery_count'],
          ['Ждёт досье','deep_waiting_for_dossier_count'],
          ['Готово / ожидает выполнения','deep_ready_or_pending_count'],
          ['Осталось в первом проходе','deep_normal_first_pass_remaining_count'],
          ['Осталось до полного authoritative покрытия','deep_remaining_until_all_authoritative_count'],
          ['Нормальный первый проход завершён','deep_normal_first_pass_complete'],
          ['Все текущие игры authoritative завершены','deep_all_current_authoritative_complete'],
        ].map(([label,key])=>({label,key,value:field(status,key)})),
      },
    ];
  }

  return {tierOf,urgencyOf,tierScore,compareGames,sortItems,stageIndicators,statisticsSections};
});
