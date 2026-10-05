(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ProgressivePersonalizationUI=api;
})(typeof window!=='undefined'?window:globalThis,function(){
  const TIERS={analyzed_fit:1,analysis_incomplete:2,not_analyzed:3};
  const RANKING_STAGES={deep_fit:1,fast_fit:2,analysis_incomplete:3,not_analyzed:4};

  function tierOf(game){
    const explicit=Number(game&&game.analysis_tier);
    if(Number.isFinite(explicit)&&explicit>0)return explicit;
    return TIERS[game&&game.analysis_state]||99;
  }
  function rankingStageOf(game){
    const stage=String(game&&game.ranking_stage||'');
    return Object.prototype.hasOwnProperty.call(RANKING_STAGES,stage)?stage:null;
  }
  function rankingStageRank(game){
    const explicit=Number(game&&game.ranking_stage_rank);
    return Number.isFinite(explicit)&&explicit>0?explicit:99;
  }
  function urgencyOf(game){
    const value=Number(game&&game.sale_expiry_urgency_rank);
    return Number.isFinite(value)?value:2;
  }
  function stageScore(game){
    const stage=rankingStageOf(game);
    const value=Number(stage==='deep_fit'||stage==='fast_fit'
      ?game&&game.total_score
      :game&&game.deterministic_purchase_score);
    return Number.isFinite(value)?value:-Infinity;
  }
  function canonicalRank(game){
    const value=Number(game&&game.priority_rank);
    return Number.isFinite(value)&&value>0?value:Infinity;
  }
  function titleOf(game){return String(game&&game.title||'')}
  function idOf(game){return String(game&&game.id||'')}
  function deterministicTie(a,b){
    const title=titleOf(a).localeCompare(titleOf(b),'ru',{sensitivity:'base'});
    return title||idOf(a).localeCompare(idOf(b),'ru',{sensitivity:'base'});
  }
  function compareGames(a,b,urgencyFirst=false){
    if(!urgencyFirst){
      const canonicalDiff=canonicalRank(a)-canonicalRank(b);
      if(Number.isFinite(canonicalDiff)&&canonicalDiff)return canonicalDiff;
    }
    const stageDiff=rankingStageRank(a)-rankingStageRank(b);
    if(stageDiff)return stageDiff;
    if(urgencyFirst){
      const urgencyDiff=urgencyOf(a)-urgencyOf(b);
      if(urgencyDiff)return urgencyDiff;
    }
    const scoreDiff=stageScore(b)-stageScore(a);
    if(scoreDiff)return scoreDiff;
    return deterministicTie(a,b);
  }
  function sortItems(items,urgencyFirst=false){
    return [...(items||[])].sort((a,b)=>compareGames(a,b,urgencyFirst));
  }
  function saleEndTimeMs(value){
    if(value===null||value===undefined)return null;
    if(typeof value==='string'&&!value.trim())return null;
    const ms=new Date(value).getTime();
    return Number.isFinite(ms)?ms:null;
  }
  function hasKnownExpiredSale(game,nowMs=Date.now()){
    const endMs=saleEndTimeMs(game&&game.sale_end_utc);
    const now=Number(nowMs);
    if(endMs===null||!Number.isFinite(now))return false;
    return endMs<=now;
  }
  function filterActiveSaleItems(items,nowMs=Date.now()){
    return [...(items||[])].filter(game=>!hasKnownExpiredSale(game,nowMs));
  }
  function cursorForVisibleIds(oldIds,oldCursor,visibleIds){
    const old=[...(oldIds||[])];
    const visible=[...(visibleIds||[])];
    const cursor=Math.max(0,Math.min(Number(oldCursor)||0,Math.max(0,old.length-1)));
    const currentId=old[cursor]||null;
    const found=currentId?visible.indexOf(currentId):-1;
    return found>=0?found:Math.min(cursor,Math.max(0,visible.length-1));
  }

  function fastIndicator(game){
    const state=game&&game.fast_stage_state;
    const outcome=game&&game.fast_stage_outcome;
    if(state==='completed'&&outcome==='fit')return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'positive',lit:true,title:'Быстрый разбор: завершён — подходит'};
    if(state==='completed'&&outcome==='not_fit')return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'negative',lit:true,title:'Быстрый разбор: завершён — не подходит'};
    if(state==='completed')return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'unknown',lit:false,title:'Быстрый разбор: завершён, но итог не опубликован'};
    if(state==='incomplete')return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'warning',lit:false,title:'Быстрый разбор: не удалось сделать вывод'};
    if(state==='error')return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'error',lit:false,title:'Быстрый разбор: ошибка'};
    if(state==='not_started')return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'idle',lit:false,title:'Быстрый разбор: ещё не начат'};
    return {key:'fast',symbol:'⚡',label:'Быстрый разбор',tone:'unknown',lit:false,title:'Быстрый разбор: состояние не опубликовано'};
  }

  function dossierIndicator(game){
    const state=game&&game.dossier_stage_state;
    if(state==='accepted')return {key:'dossier',symbol:'▤',label:'Подготовка досье',tone:'ready',lit:true,title:'Подготовка досье: готово'};
    if(state==='failed_or_recovery')return {key:'dossier',symbol:'▤',label:'Подготовка досье',tone:'warning',lit:false,title:'Подготовка досье: требует восстановления'};
    if(state==='not_ready')return {key:'dossier',symbol:'▤',label:'Подготовка досье',tone:'idle',lit:false,title:'Подготовка досье: ожидает подготовки'};
    return {key:'dossier',symbol:'▤',label:'Подготовка досье',tone:'unknown',lit:false,title:'Подготовка досье: состояние не опубликовано'};
  }

  function deepIndicator(game){
    const state=game&&game.deep_stage_state;
    const outcome=game&&game.deep_stage_outcome;
    const recovery=game&&game.deep_recovery_state;
    if(state==='completed'&&outcome==='fit')return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'positive',lit:true,title:'Глубокий разбор: завершён — подходит'};
    if(state==='completed'&&outcome==='not_fit')return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'negative',lit:true,title:'Глубокий разбор: завершён — не подходит'};
    if(state==='completed')return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'unknown',lit:false,title:'Глубокий разбор: завершён, но итог не опубликован'};
    if(state==='waiting_for_dossier')return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'idle',lit:false,title:'Глубокий разбор: ждёт досье'};
    if(state==='eligible_or_pending')return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'ready',lit:false,title:'Глубокий разбор: готов к разбору или ожидает выполнения'};
    if(state==='incomplete_or_recovery'){
      const recoveryTitles={
        recovery_owned:'требует восстановления',
        recovery_eligible:'восстановление доступно',
        recovery_pending:'восстановление ожидает выполнения',
        none:'не удалось завершить',
      };
      return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'warning',lit:false,title:`Глубокий разбор: ${recoveryTitles[recovery]||'не удалось завершить / требуется восстановление'}`};
    }
    if(state==='not_started')return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'idle',lit:false,title:'Глубокий разбор: ещё не начат'};
    return {key:'deep',symbol:'◆',label:'Глубокий разбор',tone:'unknown',lit:false,title:'Глубокий разбор: состояние не опубликовано'};
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
  function formatLastWriteAt(value){
    if(value===null||value===undefined||value==='')return 'ещё не было записей';
    const date=new Date(value);
    if(Number.isNaN(date.getTime()))return 'ещё не было записей';
    return date.toLocaleString('ru-RU',{dateStyle:'short',timeStyle:'short'});
  }
  function statisticsSections(status){
    status=status||{};
    return [
      {
        key:'fast',
        title:'Быстрый разбор',
        lastWriteAtUtc:status.fast_last_write_at_utc??null,
        scopeLabel:'Всего игр для быстрого разбора',
        denominatorKey:'fast_total_current_scope',
        denominator:field(status,'fast_total_current_scope'),
        rows:[
          ['Обработано','fast_attempted_count'],
          ['Завершено: подходит','fast_completed_fit_count'],
          ['Завершено: не подходит','fast_completed_not_fit_count'],
          ['Не удалось сделать вывод','fast_incomplete_count'],
          ['Ошибки','fast_error_count'],
          ['Не требовался: есть готовый глубокий разбор','fast_skipped_due_to_authoritative_deep_count'],
          ['Осталось','fast_remaining_count'],
        ].map(([label,key])=>({label,key,value:field(status,key)})),
        note:'«Обработано» — быстрый разбор запускался для этого числа игр. Это сумма завершённых «подходит» и «не подходит», случаев «не удалось сделать вывод» и ошибок. «Не удалось сделать вывод» означает, что надёжных данных для итога не хватило; «Ошибка» — технический или некорректный результат.',
      },
      {
        key:'dossier',
        title:'Подготовка досье',
        lastWriteAtUtc:status.dossier_last_write_at_utc??null,
        scopeLabel:'Всего игр для подготовки досье',
        denominatorKey:'dossier_total_current_scope',
        denominator:field(status,'dossier_total_current_scope'),
        rows:[
          ['Готово','dossier_accepted_count'],
          ['Ожидает','dossier_pending_count'],
          ['Требует восстановления','dossier_failed_or_recovery_count'],
        ].map(([label,key])=>({label,key,value:field(status,key)})),
      },
      {
        key:'deep',
        title:'Глубокий разбор',
        lastWriteAtUtc:status.deep_last_write_at_utc??null,
        scopeLabel:'Всего игр для глубокого разбора',
        denominatorKey:'deep_total_current_coverage_target',
        denominator:field(status,'deep_total_current_coverage_target'),
        rows:[
          ['Окончательно разобрано','deep_authoritative_completed_count'],
          ['Завершено: подходит','deep_completed_fit_count'],
          ['Завершено: не подходит','deep_completed_not_fit_count'],
          ['Не удалось завершить / требуется восстановление','deep_incomplete_or_recovery_count'],
          ['Ждёт досье','deep_waiting_for_dossier_count'],
          ['Готово к разбору / ожидает','deep_ready_or_pending_count'],
          ['Осталось до окончательного разбора','deep_remaining_until_all_authoritative_count'],
        ].map(([label,key])=>({label,key,value:field(status,key)})),
        note:'«Окончательно разобрано» — глубокий разбор завершён с итогом «подходит» или «не подходит».',
      },
      {
        key:'translation',
        title:'Переводы описаний',
        showLastWrite:false,
        lastWriteAtUtc:null,
        scopeLabel:'Игр без перевода:',
        denominatorKey:'untranslated_game_count',
        denominator:field(status,'untranslated_game_count'),
        rows:[
          {
            label:'На диагностике перевода',
            key:'translation_diagnostic_count',
            value:field(status,'translation_diagnostic_count'),
          },
          {
            label:'Последний успешный перевод',
            key:'last_successful_translation_at_utc',
            value:formatLastWriteAt(status.last_successful_translation_at_utc??null),
          },
          {
            label:'Последняя попытка перевода',
            key:'last_translation_attempt_at_utc',
            value:formatLastWriteAt(status.last_translation_attempt_at_utc??null),
          },
        ],
        note:'Игры на диагностике перевода не возвращаются автоматически в обычную очередь перевода. Игры без перевода остаются видимыми и учитываются отдельно; отсутствие перевода не останавливает публикацию.',
      },
    ];
  }

  return {tierOf,rankingStageOf,rankingStageRank,urgencyOf,stageScore,compareGames,sortItems,saleEndTimeMs,hasKnownExpiredSale,filterActiveSaleItems,cursorForVisibleIds,stageIndicators,formatLastWriteAt,statisticsSections};
});
