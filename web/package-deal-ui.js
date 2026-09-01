(function(root){
  function packageView(g){
    const p=g?.better_purchase_option;
    if(!p||p.package_price_rub==null)return null;
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
    const preferred=g?.score_breakdown?.purchase_route==='fixed_package';
    const heading=strict?'🎁 Выгодный набор Steam':'🎁 Набор Steam';
    let recommendation='Набор доступен как альтернативный способ покупки; отдельная покупка сейчас практичнее по совокупной выгоде.';
    if(!sourceAligned){
      recommendation='Состав набора подтверждён, но сравнение цен ещё синхронизируется; пока не считаю набор более выгодным.';
    }else if(preferred){
      recommendation='Сейчас это рекомендуемый способ покупки: набор даёт лучшую совокупную выгоду.';
    }else if(strict){
      recommendation='Набор дешевле сравнимого подтверждённого содержимого, но отдельная покупка сейчас не хуже по совокупной выгоде.';
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
    const compactEconomics=[];
    if(sourceAligned&&strict&&Number.isFinite(savings))compactEconomics.push(`экономия ${fmtRub(savings)}`);
    if(sourceAligned&&strict&&Number.isFinite(savingsPct))compactEconomics.push(`${savingsPct.toLocaleString('ru-RU',{maximumFractionDigits:1})}% дешевле`);
    const equivalenceNote=p.uses_verified_purchase_equivalence?'Покрытие включает подтверждённую улучшенную версию одной из игр.':'';
    return {p,count,perGame,strict,heading,recommendation,economics,compactEconomics,titles,included,includedTitles,incrementalTitles,unpricedTitles,nonpersonalizedTitles,equivalenceNote};
  }

  function packageDetailsHtml(view){
    return `${view.economics.length?`<div class="offer-meta">${view.economics.join(' · ')}</div>`:''}${view.titles?`<div class="offer-meta">Покрывает из текущего списка: ${view.titles}</div>`:''}${view.includedTitles?`<div class="offer-meta"><b>Состав Steam (${view.included.length}):</b> ${view.includedTitles}</div>`:''}${view.incrementalTitles?`<div class="offer-meta"><b>Учтённый доп. контент:</b> ${view.incrementalTitles}</div>`:''}${view.unpricedTitles?`<div class="offer-meta"><b>Есть в составе, но цену отдельно не выдумываю:</b> ${view.unpricedTitles}</div>`:''}${view.nonpersonalizedTitles?`<div class="offer-meta"><b>Ещё входит, но не прибавляю персональную ценность:</b> ${view.nonpersonalizedTitles}</div>`:''}${view.equivalenceNote?`<div class="offer-meta">${escapeHtml(view.equivalenceNote)}</div>`:''}<div class="offer-meta"><b>${escapeHtml(view.recommendation)}</b></div>`;
  }

  function renderPackageDeal(g,options={}){
    const view=packageView(g);
    if(!view)return '';
    const compact=options.compact===true;
    if(compact){
      return `<div class="offer purchase-package-compact" data-package-highlight="true" data-purchase-kind="fixed_package" style="border-width:2px"><div class="offer-top"><div class="offer-title"><b>${view.heading}</b><br>${escapeHtml(view.p.package_title||'Набор Steam')}</div><div class="offer-price">${fmtRub(view.p.package_price_rub)}</div></div><div class="offer-meta"><b>${view.count} игр из текущего списка${view.perGame!=null?` · ≈ ${fmtRub(view.perGame)} за игру`:''}</b></div>${view.compactEconomics.length?`<div class="offer-meta">${view.compactEconomics.join(' · ')}</div>`:''}<div class="offer-meta"><b>${escapeHtml(view.recommendation)}</b></div><div class="offer-actions"><button class="offer-link" type="button" data-open-web="${escapeHtml(view.p.web_url||'')}" data-open-steam="">Открыть набор в Steam</button></div></div>`;
    }
    return `<div class="offer" data-package-highlight="true" data-purchase-kind="fixed_package" style="border-width:2px"><div class="offer-top"><div class="offer-title"><b>${view.heading}</b><br>${escapeHtml(view.p.package_title||'Набор Steam')}</div><div class="offer-price">${fmtRub(view.p.package_price_rub)}</div></div><div class="offer-meta"><b>${view.count} игр из текущего списка${view.perGame!=null?` · ≈ ${fmtRub(view.perGame)} за игру`:''}</b></div>${packageDetailsHtml(view)}<div class="offer-actions"><button class="offer-link" type="button" data-open-web="${escapeHtml(view.p.web_url||'')}" data-open-steam="">Открыть набор в Steam</button></div></div>`;
  }

  function renderPackagePrimaryDetails(g){
    const view=packageView(g);
    if(!view)return '';
    return `<div class="purchase-package-details" data-package-details="true"><div class="purchase-detail-title">Что входит и почему это выгодно</div>${packageDetailsHtml(view)}</div>`;
  }

  function standaloneRecommendation(g){
    const p=g?.better_purchase_option;
    if(!p)return 'Рекомендуемый вариант покупки.';
    if(p.comparison_source_aligned===false)return 'Рекомендуемый вариант: отдельная покупка остаётся основным выбором, пока сравнение цен набора синхронизируется.';
    return 'Рекомендуемый вариант: отдельная покупка сейчас не хуже по совокупной выгоде.';
  }

  function renderRegularOffer(o,g,{recommended=false}={}){
    const hist=o.previously_free?'ранее бесплатно':(o.historical_minimum_rub!=null?`ист. минимум ${fmtRub(o.historical_minimum_rub)}`:'история не подтверждена');
    const old=`<span style="text-decoration:line-through">${fmtRub(o.original_price_rub)}</span>`;
    const note=recommended?standaloneRecommendation(g):'';
    return `<div class="offer" data-purchase-kind="standalone"><div class="offer-top"><div class="offer-title">${escapeHtml(o.title||g.title)}${recommended?' · рекомендуемый':''}</div><div class="offer-price">${fmtRub(o.current_price_rub)}</div></div><div class="offer-meta">${old} · −${o.discount_percent}% · ${hist}</div>${note?`<div class="offer-meta"><b>${escapeHtml(note)}</b></div>`:''}<div class="offer-actions"><button class="offer-link" type="button" data-open-web="${escapeHtml(o.web_url||'')}" data-open-steam="${escapeHtml(o.steam_url||'')}">Открыть вариант в Steam</button></div></div>`;
  }

  function optionWord(n){
    const mod100=n%100;
    const mod10=n%10;
    if(mod100>=11&&mod100<=14)return 'вариантов';
    if(mod10===1)return 'вариант';
    if(mod10>=2&&mod10<=4)return 'варианта';
    return 'вариантов';
  }

  function renderPurchaseOptions(g){
    const regular=(g?.offers||[]).filter(o=>o&&o.current_price_rub!=null&&o.offer_kind!=='fixed_multi_game_package');
    const packageFull=renderPackageDeal(g);
    const hasPackage=Boolean(packageFull);
    const total=regular.length+(hasPackage?1:0);
    if(total===0)return '';
    if(total===1)return hasPackage?packageFull:renderRegularOffer(regular[0],g,{recommended:true});

    const packagePreferred=hasPackage&&g?.score_breakdown?.purchase_route==='fixed_package';
    const primary=packagePreferred?renderPackageDeal(g,{compact:true}):renderRegularOffer(regular[0],g,{recommended:true});
    const otherCount=total-1;
    const collapsedLabel=`Показать ещё ${otherCount} ${optionWord(otherCount)}`;
    const extras=packagePreferred
      ?`${renderPackagePrimaryDetails(g)}${regular.map(o=>renderRegularOffer(o,g)).join('')}`
      :`${hasPackage?packageFull:''}${regular.slice(1).map(o=>renderRegularOffer(o,g)).join('')}`;
    return `<div class="purchase-options" data-purchase-options="true"><div class="purchase-primary" data-purchase-primary="true">${primary}</div><button class="purchase-toggle" type="button" data-purchase-toggle="true" data-collapsed-label="${escapeHtml(collapsedLabel)}" aria-expanded="false">${escapeHtml(collapsedLabel)}</button><div class="purchase-more" data-purchase-more="true" hidden>${extras}</div></div>`;
  }

  function setPurchaseOptionsExpanded(wrapper,expanded){
    if(!wrapper)return false;
    const button=wrapper.querySelector?.('[data-purchase-toggle]');
    const more=wrapper.querySelector?.('[data-purchase-more]');
    if(!button||!more)return false;
    const open=expanded===true;
    more.hidden=!open;
    button.setAttribute('aria-expanded',String(open));
    button.textContent=open?'Свернуть варианты':(button.dataset.collapsedLabel||'Показать другие варианты');
    return true;
  }

  root.renderPackageDeal=renderPackageDeal;
  root.renderPurchaseOptions=renderPurchaseOptions;
  root.setPurchaseOptionsExpanded=setPurchaseOptionsExpanded;
  root.renderOffers=function(g){
    const target=typeof $==='function'?$('offers'):null;
    if(!target)return;
    target.innerHTML=renderPurchaseOptions(g)||'<div class="muted small">Дополнительных вариантов сейчас нет.</div>';
  };

  if(typeof currentGame==='function'){
    try{const g=currentGame();if(g)root.renderOffers(g);}catch{}
  }

  if(typeof document!=='undefined'&&document.addEventListener){
    document.addEventListener('click',event=>{
      const button=event.target?.closest?.('[data-purchase-toggle]');
      if(!button)return;
      const wrapper=button.closest('[data-purchase-options]');
      const expanded=button.getAttribute('aria-expanded')==='true';
      setPurchaseOptionsExpanded(wrapper,!expanded);
    });
  }
})(typeof window!=='undefined'?window:globalThis);
