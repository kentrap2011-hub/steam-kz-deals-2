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

  const TWO_STAGE_CONTRACT='DEEP-TWO-STAGE-SITE-PROJECTION-V1';
  function twoStageIndicator(key,symbol,label,state,completeStates,negativeStates,descriptions){
    const completed=completeStates.includes(state);
    const negative=negativeStates.includes(state);
    return {key,symbol,label,lit:completed,tone:completed?(negative?'negative':'positive'):'idle',
      title:label+': '+(descriptions[state]||'состояние не опубликовано')};
  }
  function stageIndicators(game){
    if(game&&game.deep_two_stage_site_contract===TWO_STAGE_CONTRACT){
      return [
        twoStageIndicator('dossier','▤','Досье',game.dossier_status,['ready'],[],
          {ready:'готово',pending:'ожидает',failed_or_recovery:'требуется восстановление',not_required:'не требуется'}),
        twoStageIndicator('deep_stage1','Ⅰ','Deep Stage 1 — Анализ игры',game.stage1_status,
          ['completed_fit','completed_not_fit'],['completed_not_fit'],
          {not_ready:'ещё не готов',pending:'ожидает анализа',completed_fit:'подходит',
           completed_not_fit:'не подходит',diagnostic_incomplete:'требуется диагностика'}),
        twoStageIndicator('deep_stage2','Ⅱ','Deep Stage 2 — Сравнительная калибровка',game.stage2_status,
          ['calibrated'],[],
          {not_eligible:'не требуется',awaiting_calibration:'ожидает калибровки',
           calibrated:'готово',diagnostic_incomplete:'требуется диагностика'}),
      ];
    }
    return [fastIndicator(game),dossierIndicator(game),deepIndicator(game)];
  }
  function twoStageStatisticsSections(status){
    const dossier=status.dossier||{};
    const first=status.deep_stage1||{};
    const second=status.deep_stage2||{};
    const datum=(source,key)=>field(source,key);
    const rows=(source,pairs)=>pairs.map(([label,key])=>({
      label,key,value:datum(source,key),
    }));
    const sections=[
      {
        key:'dossier',title:'Досье',scopeLabel:'Игр для подготовки досье',
        denominator:datum(dossier,'total_eligible'),
        lastWriteAtUtc:dossier.last_attempt_at_utc??null,
        lastSuccessAtUtc:dossier.last_successful_result_at_utc??null,
        rows:rows(dossier,[['Готово','completed'],['Ожидает','pending'],
          ['Требует восстановления','diagnostic_incomplete']]),
      },
      {
        key:'deep_stage1',title:'Deep Stage 1 — Анализ игры',
        scopeLabel:'Игр для анализа',denominator:datum(first,'total_eligible'),
        lastWriteAtUtc:first.last_attempt_at_utc??null,
        lastSuccessAtUtc:first.last_successful_result_at_utc??null,
        rows:rows(first,[['Завершено','completed'],['Подходит','completed_fit'],
          ['Не подходит','completed_not_fit'],['Ожидает','pending'],
          ['Требует диагностики','diagnostic_incomplete'],
          ['Прогресс, %','progress_percent']]),
      },
      {
        key:'deep_stage2',title:'Deep Stage 2 — Сравнительная калибровка',
        scopeLabel:'Игр после Stage 1',denominator:datum(second,'stage1_fit_eligible'),
        lastWriteAtUtc:second.last_attempt_at_utc??null,
        lastSuccessAtUtc:second.last_successful_calibration_at_utc??null,
        rows:rows(second,[['Откалибровано','calibrated'],
          ['Ожидает калибровки','awaiting_calibration'],
          ['Требует диагностики','diagnostic_incomplete'],
          ['Прогресс, %','progress_percent']]),
      },
    ];
    // Keep independent translation and publication diagnostics; Fast/legacy Deep
    // are not current two-stage semantic stages.
    const auxiliary=statisticsSections({...status,deep_two_stage_site_contract:null}).slice(3);
    return sections.concat(auxiliary);
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
  function quarantineCategoryLabel(key){
    const labels={
      card_explanation:'Текст персонального объяснения',
      description:'Описание игры',
      grounded_negative:'Отображение персональных рисков',
      card_binding:'Карточка с неподтверждённой привязкой',
      giveaway_offer:'Предложение бесплатной раздачи',
    };
    return labels[String(key||'')]||'Другая локальная проблема';
  }
  function quarantineRows(status){
    const counts=(status&&status.site_quarantine_category_counts)||{};
    return Object.entries(counts)
      .filter(([,value])=>Number(value)>0)
      .sort(([a],[b])=>String(a).localeCompare(String(b),'ru'))
      .map(([key,value])=>({
        label:quarantineCategoryLabel(key),
        key:`site_quarantine_category_${key}`,
        value:Number(value),
      }));
  }
  function statisticsSections(status){
    status=status||{};
    if(status.deep_two_stage_site_contract===TWO_STAGE_CONTRACT){
      return twoStageStatisticsSections(status);
    }
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
      {
        key:'publication',
        title:'Диагностика публикации',
        lastWriteAtUtc:status.site_status_generated_at_utc??null,
        scopeLabel:'Ожидает исправления или диагностики',
        denominatorKey:'site_quarantine_pending_count',
        denominator:field(status,'site_quarantine_pending_count'),
        rows:quarantineRows(status),
        note:'Локальная проблема одной карточки или текста изолируется и не должна останавливать обновление остальных актуальных данных сайта.',
      },
    ];
  }

  return {tierOf,rankingStageOf,rankingStageRank,urgencyOf,stageScore,compareGames,sortItems,saleEndTimeMs,hasKnownExpiredSale,filterActiveSaleItems,cursorForVisibleIds,stageIndicators,formatLastWriteAt,quarantineRows,statisticsSections};
});
