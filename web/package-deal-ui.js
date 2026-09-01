window.renderPackageDeal=function(g){
  const p=g?.better_purchase_option;
  if(!p||p.package_price_rub==null)return '';
  const count=Number(p.covered_visible_game_count)||0;
  const perGame=p.package_price_per_visible_game_rub!=null?Number(p.package_price_per_visible_game_rub):(count?Number(p.package_price_rub)/count:null);
  const standalone=p.standalone_total_rub;
  const visibleGamesTotal=p.visible_standalone_game_total_rub;
  const incrementalTotal=p.verified_incremental_content_total_rub;
  const comparableTotal=p.comparable_entitlement_total_rub??standalone;
  const savings=p.savings_rub==null?null:Number(p.savings_rub);
  const savingsPct=p.savings_percent_vs_standalone==null?null:Number(p.savings_percent_vs_standalone);
  const strict=p.strict_current_price_savings===true||(Number.isFinite(savings)&&savings>0);
  const sourceAligned=p.comparison_source_aligned!==false;
  const delta=p.price_delta_vs_standalone_rub!=null?Number(p.price_delta_vs_standalone_rub):(
    p.package_price_rub!=null&&comparableTotal!=null?Number(p.package_price_rub)-Number(comparableTotal):null
  );
  const titles=(p.covered_visible_titles||[]).filter(Boolean).map(escapeHtml).join(', ');
  const included=(p.verified_included_content||[]).filter(x=>x&&x.title);
  const includedTitles=included.map(x=>escapeHtml(x.title)).join(', ');
  const incremental=(p.verified_incremental_content||[]).filter(x=>x&&x.title);
  const incrementalTitles=incremental.map(x=>escapeHtml(x.title)).join(', ');
  const unpriced=(p.verified_incremental_content_unpriced||[]).filter(x=>x&&x.title);
  const unpricedTitles=unpriced.map(x=>escapeHtml(x.title)).join(', ');
  const nonpersonalized=(p.verified_nonpersonalized_included_content||[]).filter(x=>x&&x.title);
  const nonpersonalizedTitles=nonpersonalized.map(x=>escapeHtml(x.title)).join(', ');
  const drivesRank=g.score_breakdown?.purchase_route==='fixed_package';
  const heading=strict?'🎁 Выгодный набор Steam':'🎁 Набор Steam';
  let rankNote='Набор показан как релевантный вариант покупки, но сам по себе не повышает рейтинг.';
  if(!sourceAligned){
    rankNote='Состав набора подтверждён. Сравнение выгоды и влияние на рейтинг обновятся после синхронизации цен.';
  }else if(drivesRank){
    rankNote='Этот набор сейчас определяет балл выгодности покупки и поднимает игру в рейтинге.';
  }else if(strict){
    rankNote='Набор дешевле сравнимого подтверждённого содержимого, но одиночный вариант сейчас получает не меньший балл покупки.';
  }
  const economics=[];
  if(sourceAligned&&visibleGamesTotal!=null)economics.push(`игры из списка отдельно ${fmtRub(visibleGamesTotal)}`);
  if(sourceAligned&&Number(incrementalTotal)>0)economics.push(`доп. контент отдельно ${fmtRub(incrementalTotal)}`);
  if(sourceAligned&&comparableTotal!=null&&Number(incrementalTotal)>0)economics.push(`сравнимая ценность ${fmtRub(comparableTotal)}`);
  if(sourceAligned&&visibleGamesTotal==null&&standalone!=null)economics.push(`сравнимое содержимое отдельно ${fmtRub(standalone)}`);
  if(sourceAligned&&strict&&Number.isFinite(savings))economics.push(`экономия ${fmtRub(savings)}`);
  if(sourceAligned&&strict&&Number.isFinite(savingsPct))economics.push(`${savingsPct.toLocaleString('ru-RU',{maximumFractionDigits:1})}% дешевле`);
  if(sourceAligned&&!strict&&Number.isFinite(delta)&&delta>0)economics.push(`на ${fmtRub(delta)} дороже сравнимого содержимого отдельно`);
  if(sourceAligned&&!strict&&Number.isFinite(delta)&&delta===0)economics.push('по той же цене, что и сравнимое содержимое отдельно');
  const equivalenceNote=p.uses_verified_purchase_equivalence?'Покрытие включает подтверждённую улучшенную версию одной из игр.':'';
  const fullContentNote=includedTitles?`<div class="offer-meta"><b>Состав Steam (${included.length}):</b> ${includedTitles}</div>`:'';
  const incrementalNote=incrementalTitles?`<div class="offer-meta"><b>Учтённый доп. контент:</b> ${incrementalTitles}</div>`:'';
  const unpricedNote=unpricedTitles?`<div class="offer-meta"><b>Есть в составе, но цену отдельно не выдумываю:</b> ${unpricedTitles}</div>`:'';
  const nonpersonalizedNote=nonpersonalizedTitles?`<div class="offer-meta"><b>Ещё входит, но не прибавляю персональную ценность:</b> ${nonpersonalizedTitles}</div>`:'';
  return `<div class="offer" data-package-highlight="true" style="border-width:2px"><div class="offer-top"><div class="offer-title"><b>${heading}</b><br>${escapeHtml(p.package_title||'Набор Steam')}</div><div class="offer-price">${fmtRub(p.package_price_rub)}</div></div><div class="offer-meta"><b>${count} игр из текущего списка${perGame!=null?` · ≈ ${fmtRub(perGame)} за игру`:''}</b></div>${economics.length?`<div class="offer-meta">${economics.join(' · ')}</div>`:''}${titles?`<div class="offer-meta">Покрывает из текущего списка: ${titles}</div>`:''}${fullContentNote}${incrementalNote}${unpricedNote}${nonpersonalizedNote}${equivalenceNote?`<div class="offer-meta">${escapeHtml(equivalenceNote)}</div>`:''}<div class="offer-meta"><b>${escapeHtml(rankNote)}</b></div><div class="offer-actions"><button class="offer-link" type="button" data-open-web="${escapeHtml(p.web_url||'')}" data-open-steam="">Открыть набор в Steam</button></div></div>`;
};
