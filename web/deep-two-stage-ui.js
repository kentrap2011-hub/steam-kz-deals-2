/* Dormant two-stage Deep presentation; enabled only by producer-owned V1 projection. */
(function(root){
  'use strict';
  const CONTRACT='DEEP-TWO-STAGE-SITE-PROJECTION-V1';
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const numeric=value=>typeof value==='number'&&Number.isFinite(value);
  const score=(v,max)=>numeric(v)?v.toLocaleString('ru-RU',{minimumFractionDigits:max===56?2:0,maximumFractionDigits:2})+'/'+max:'—';
  const text=(v,missing='Данных пока нет.')=>esc(v||missing);
  function active(game){return game?.deep_two_stage_site_contract===CONTRACT}
  function calibrated(game){return active(game)&&game.stage2_status==='calibrated'&&numeric(game.stage2_calibrated_deep_fit_score_0_56)&&numeric(game.personal_quality_score_0_60)&&numeric(game.total_score_0_100)}
  function compactScore(game){
    if(!active(game))return '';
    return calibrated(game)
      ? 'Личное: '+score(game.personal_quality_score_0_60,60)+' · Итог: '+score(game.total_score_0_100,100)
      : 'Ожидает сравнительной калибровки';
  }
  function values(rows,empty='Данных пока нет.'){
    if(!Array.isArray(rows)||!rows.length)return '<p class="muted">'+esc(empty)+'</p>';
    return '<ul class="deep2-finding-list">'+rows.map(row=>'<li>'+esc(row)+'</li>').join('')+'</ul>';
  }
  const st1={
    not_ready:'Ещё не готов',pending:'Ожидает анализа',completed_fit:'Анализ завершён: подходит',
    completed_not_fit:'Анализ завершён: не подходит',diagnostic_incomplete:'Требуется диагностика'
  };
  const st2={
    not_eligible:'Не требуется',awaiting_calibration:'Ожидает сравнительной калибровки',
    calibrated:'Сравнительная калибровка завершена',diagnostic_incomplete:'Требуется диагностика'
  };
  function scoreEvolution(game){
    const breakdown=(game.stage1_point_breakdown||[]).map(row=>{
      const reasons=Array.isArray(row.finding_reasons_ru)?row.finding_reasons_ru:[];
      return '<li><div><span>'+esc(row.label_ru)+'</span>'+
        (reasons.length?'<small>'+reasons.map(esc).join('; ')+'</small>':'')+
        '</div><b>'+esc(row.direction||'')+' '+esc(row.points)+'</b></li>';
    }).join('');
    const evolution='<p>Stage 1 (предварительно): <b>'+score(game.stage1_provisional_deep_fit_score_0_56,56)+
      '</b> → Stage 2 (итог): <b>'+score(game.stage2_calibrated_deep_fit_score_0_56,56)+'</b></p>';
    const delta=numeric(game.stage2_calibration_delta)
      ? '<p>Коррекция после сравнения: <b>'+esc(game.stage2_calibration_delta.toLocaleString('ru-RU',{maximumFractionDigits:2}))+'</b></p>':'';
    return evolution+delta+(breakdown?'<h4>Из чего сложился предварительный анализ</h4><ul class="deep2-breakdown">'+breakdown+'</ul>':'')+
      '<p>'+text(game.stage2_why_changed_ru,'Калибровка пока не завершена.')+'</p>';
  }
  function neighbors(game){
    const rows=Array.isArray(game.stage2_neighbor_comparisons)?game.stage2_neighbor_comparisons:[];
    const reasons=rows.map(row=>{
      const comparison={'target_above':'Выше','near_tie_target_above':'Немного выше','target_below':'Ниже','near_tie_target_below':'Немного ниже'}[row.relation]||'Сравнение';
      return '<li><b>'+esc(comparison)+'</b> · '+esc(row.anchor_title_ru||row.anchor_id||'Соседняя игра')+
        values(row.reasons_ru||[],'Причина не опубликована.')+'</li>';
    });
    return '<p><b>Почему выше:</b></p>'+values(game.stage2_why_above_ru,'Пока нет сравнения с играми ниже.')+
      '<p><b>Почему ниже:</b></p>'+values(game.stage2_why_below_ru,'Пока нет сравнения с играми выше.')+
      (reasons.length?'<ul class="deep2-neighbors">'+reasons.join('')+'</ul>':'');
  }
  function detailHtml(game){
    if(!active(game))return '';
    const ready=calibrated(game);
    const verdict=game.stage1_status==='completed_not_fit'?'Не подходит':
      game.stage1_status==='completed_fit'?(ready?'Оценка откалибрована':'Предварительно подходит'):
      'Персональный анализ ещё не завершён';
    const total=ready?score(game.total_score_0_100,100):'—';
    const summary='<p><b>'+esc(verdict)+'</b>. '+text(game.stage1_summary_ru,'Итог анализа ещё не получен.')+'</p>'+
      '<div class="deep2-score-grid">'+[
        ['Stage 1 /56 (предварительно)',score(game.stage1_provisional_deep_fit_score_0_56,56)],
        ['Stage 2 /56 (итог)',score(game.stage2_calibrated_deep_fit_score_0_56,56)],
        ['Wishlist',numeric(game.wishlist_bonus_0_or_4)?'+'+esc(game.wishlist_bonus_0_or_4):'—'],
        ['Личное /60',score(game.personal_quality_score_0_60,60)],
        ['Покупка /40',score(game.purchase_score_0_40,40)],
        ['Вместе /100',total],
        ['Позиция',ready&&game.priority_rank!=null?'№'+esc(game.priority_rank):'—']
      ].map(([k,v])=>'<div><span>'+esc(k)+'</span><b>'+v+'</b></div>').join('')+'</div>'+
      '<p class="muted">Досье: '+esc(game.dossier_status||'—')+
      ' · Stage 1: '+esc(st1[game.stage1_status]||'—')+
      ' · Stage 2: '+esc(st2[game.stage2_status]||'—')+'</p>';
    const sections=[
      ['Краткий вывод',summary],
      ['Плюсы',values(game.stage1_positives)],
      ['Минусы',values(game.stage1_negatives)],
      ['Прочее / нюансы',values(game.stage1_nuances)],
      ['Изменение оценки Stage 1 → Stage 2',scoreEvolution(game)],
      ['Почему выше / ниже соседних игр',ready?neighbors(game):'<p class="muted">Сравнительная калибровка пока не завершена.</p>'],
    ];
    return sections.map(([title,body],i)=>
      '<section class="deep2-detail-part" data-deep2-section="'+i+'"><h3>'+esc(title)+'</h3>'+body+'</section>').join('');
  }
  root.DeepTwoStageUI={active,calibrated,compactScore,detailHtml,scoreEvolution};
})(typeof window!=='undefined'?window:globalThis);
