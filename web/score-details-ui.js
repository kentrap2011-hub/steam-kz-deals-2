(function(root){
  const LABELS={
    taste:'Вкус',
    wishlist:'Вишлист',
    achievements:'Достижения',
    duration:'Длительность',
    risk:'Риски',
    savings:'Экономия',
    price:'Цена сейчас',
    history:'История цены',
    package_savings_percent:'Экономия набора',
    package_effective_price:'Цена за игру',
    package_coverage:'Игры в наборе',
  };
  const DURATION_BANDS={
    preferred_medium:'подходит по длительности',
    slightly_short_or_long:'слегка вне привычной длительности',
    very_short_or_long:'заметно вне привычной длительности',
    extreme_length:'очень необычная длительность',
    unknown:'длительность не подтверждена',
  };

  function escape(value){
    return String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  }
  function number(value,digits=1){
    const n=Number(value);
    if(!Number.isFinite(n))return '0';
    return n.toLocaleString('ru-RU',{maximumFractionDigits:digits});
  }
  function pointsText(row){
    const points=Number(row?.points)||0;
    const sign=points>0?'+':'';
    const max=row?.max_points!=null?`/${number(row.max_points)}`:'';
    return `${sign}${number(points)}${max}`;
  }
  function componentLabel(row){
    return LABELS[row?.id]||row?.label||'Критерий';
  }
  function durationDetail(value){
    const text=String(value??'');
    for(const [code,label] of Object.entries(DURATION_BANDS)){
      if(text===code)return label;
      if(text.endsWith(` · ${code}`))return `${text.slice(0,-(` · ${code}`).length)} · ${label}`;
    }
    return text;
  }
  function componentDetail(row){
    let value=String(row?.value??'').trim();
    if(row?.id==='wishlist')return Number(row?.points)>0?'есть в желаемом':'не в желаемом';
    if(row?.id==='duration')return durationDetail(value);
    if(row?.id==='taste'){
      value=value
        .replace(/^strong\s*·\s*грубая оценка по старым данным$/i,'сильное совпадение · по старым данным')
        .replace(/^moderate\s*·\s*грубая оценка по старым данным$/i,'умеренное совпадение · по старым данным')
        .replace(/детальная нормализованная оценка/gi,'по детальному профилю вкуса');
    }
    if(row?.id==='achievements')value=value.replace(/новая или не подтверждено, что играл/gi,'нет подтверждения, что играл');
    if(row?.id==='package_coverage'&&row?.covered_visible_game_count!=null)return `${Number(row.covered_visible_game_count)} из текущего списка`;
    return value
      .replace(/\bpreferred_medium\b/g,DURATION_BANDS.preferred_medium)
      .replace(/\bslightly_short_or_long\b/g,DURATION_BANDS.slightly_short_or_long)
      .replace(/\bvery_short_or_long\b/g,DURATION_BANDS.very_short_or_long)
      .replace(/\bextreme_length\b/g,DURATION_BANDS.extreme_length)
      .replace(/\blegacy_coarse_fit\b/g,'оценка по старым данным')
      .replace(/\bnormalized_taste_factors\b/g,'детальный профиль вкуса')
      .replace(/\bfixed_package\b/g,'набор Steam')
      .replace(/\bstandalone\b/g,'игра отдельно');
  }
  function componentHtml(row){
    const detail=componentDetail(row);
    return `<div class="score-row" data-score-component="${escape(row?.id||'unknown')}"><div class="score-row-copy"><span class="score-row-label">${escape(componentLabel(row))}</span>${detail?`<span class="score-row-detail">${escape(detail)}</span>`:''}</div><b class="score-row-points">${escape(pointsText(row))}</b></div>`;
  }
  function precisionHtml(score){
    const precision=score?.precision;
    if(!precision?.label)return '';
    const suffix=precision.is_coarse_legacy?' · уточняется по мере обновления данных':'';
    return `<div class="score-note" data-score-precision="true">Данные вкуса: ${escape(precision.label)}${escape(suffix)}</div>`;
  }
  function purchaseDriverHtml(score){
    const route=score?.purchase_route;
    if(route==='fixed_package'){
      const delta=Number(score?.package_score_delta_vs_standalone);
      const extra=Number.isFinite(delta)&&delta>0?` · преимущество +${number(delta)} балла против покупки отдельно`:'';
      return `<div class="score-note score-purchase-driver" data-score-purchase-driver="true">Выгодность считается по набору Steam${escape(extra)}</div>`;
    }
    if(route==='standalone')return '<div class="score-note score-purchase-driver" data-score-purchase-driver="true">Выгодность считается по покупке игры отдельно</div>';
    if(score?.purchase_route_label)return `<div class="score-note score-purchase-driver" data-score-purchase-driver="true">Основа расчёта: ${escape(score.purchase_route_label)}</div>`;
    return '';
  }
  function sectionHtml(kind,title,scoreValue,maxValue,components,note=''){
    return `<section class="score-section score-section-${escape(kind)}" data-score-section="${escape(kind)}"><div class="score-section-head"><span>${escape(title)}</span><b>${number(scoreValue)}/${number(maxValue,0)}</b></div>${note}<div class="score-rows">${(components||[]).map(componentHtml).join('')}</div></section>`;
  }
  function renderDetailedScoreHtml(score){
    if(!score)return '';
    const total=`${number(score.total_score)}/${number(score.total_max,0)}`;
    const personal=`${number(score.personal_score)}/${number(score.personal_max,0)}`;
    const purchase=`${number(score.purchase_score)}/${number(score.purchase_max,0)}`;
    const details=sectionHtml('personal','Подходит тебе',score.personal_score,score.personal_max,score.personal_components,precisionHtml(score))+
      sectionHtml('purchase','Выгодность покупки',score.purchase_score,score.purchase_max,score.purchase_components,purchaseDriverHtml(score));
    return `<div class="score-breakdown" data-score-breakdown="true"><button class="priority-factor score-summary" type="button" data-score-details-toggle="true" aria-expanded="false" title="Показать детальную оценку"><span class="score-summary-copy"><strong>Детальная оценка</strong><small><span>Подходит ${personal}</span><span>Покупка ${purchase}</span><span data-score-cue="true">подробнее</span></small></span><b>${total}</b></button><div class="score-details-compact" data-score-details-panel="true" hidden>${details}</div></div>`;
  }
  function setScoreDetailsExpanded(wrapper,expanded){
    if(!wrapper)return false;
    const button=wrapper.querySelector?.('[data-score-details-toggle]');
    const panel=wrapper.querySelector?.('[data-score-details-panel]');
    if(!button||!panel)return false;
    const open=expanded===true;
    panel.hidden=!open;
    button.setAttribute('aria-expanded',String(open));
    button.title=open?'Свернуть детальную оценку':'Показать детальную оценку';
    const cue=button.querySelector?.('[data-score-cue]');
    if(cue)cue.textContent=open?'свернуть':'подробнее';
    return true;
  }

  const baseRenderPriority=typeof root.renderPriority==='function'?root.renderPriority:null;
  root.renderDetailedScoreHtml=renderDetailedScoreHtml;
  root.setScoreDetailsExpanded=setScoreDetailsExpanded;
  root.renderPriority=function(g){
    const factors=Array.isArray(g?.priority_factors)?g.priority_factors:[];
    const score=g?.score_breakdown||null;
    const section=typeof $==='function'?$('prioritySection'):null;
    const why=typeof $==='function'?$('priorityWhy'):null;
    const target=typeof $==='function'?$('priorityFactors'):null;
    if(!section||!why||!target){if(baseRenderPriority)return baseRenderPriority(g);return;}
    section.classList.toggle('hidden',!factors.length&&!score);
    if(!factors.length&&!score){why.textContent='';target.innerHTML='';return;}
    const urgencyMode=typeof urgencyFirstEnabled==='function'?urgencyFirstEnabled():false;
    const vs=g.priority_vs_next||null;
    const rank=Number(g.priority_rank)||null;
    const localRank=typeof queuePosition==='function'?queuePosition(g.id):null;
    const parts=[];
    if(localRank)parts.push(`Позиция в текущей очереди: №${localRank}.`);
    const record=typeof rec==='function'?rec(g.id):null;
    if(record?.manual_end_at){
      parts.push('Игра вручную отправлена в конец очереди.');
    }else if(urgencyMode){
      parts.push('Режим: срочные игры впереди.');
      if(rank&&rank!==localRank)parts.push(`Канонический рейтинг со срочностью: №${rank}.`);
      if(vs&&vs.next_game_title&&vs.explanation)parts.push(`Следующая по каноническому рейтингу — «${vs.next_game_title}». ${vs.explanation}`);
    }else{
      parts.push('Режим: порядок по итоговому баллу; срочность сейчас не меняет очередь.');
    }
    why.textContent=parts.join(' ');

    const deciding=urgencyMode&&vs&&vs.deciding_factor_id;
    const urgency=factors.find(f=>f.id==='sale_expiry_urgency_asc');
    let markup='';
    if(urgency){
      const urgencyNote=urgencyMode?'влияет на текущий порядок':'сейчас не влияет на порядок';
      markup+=`<div class="priority-factor ${deciding==='sale_expiry_urgency_asc'?'deciding':''}"><span>${escape(urgency.label||'Срочность скидки')}</span><b>${escape(urgency.value??'—')} · ${urgencyNote}</b></div>`;
    }
    if(score){
      markup+=renderDetailedScoreHtml(score);
    }else{
      markup+=factors.filter(f=>f.id!=='sale_expiry_urgency_asc').map(f=>`<div class="priority-factor ${f.id===deciding?'deciding':''}"><span>${escape(f.label||f.id||'Фактор')}</span><b>${escape(f.value??'—')}</b></div>`).join('');
    }
    target.innerHTML=markup;
  };

  if(typeof currentGame==='function'){
    try{const game=currentGame();if(game)root.renderPriority(game);}catch{}
  }
  if(typeof document!=='undefined'&&document.addEventListener){
    document.addEventListener('click',event=>{
      const button=event.target?.closest?.('[data-score-details-toggle]');
      if(!button)return;
      const wrapper=button.closest?.('[data-score-breakdown]');
      const expanded=button.getAttribute('aria-expanded')==='true';
      setScoreDetailsExpanded(wrapper,!expanded);
    });
  }
})(typeof window!=='undefined'?window:globalThis);
