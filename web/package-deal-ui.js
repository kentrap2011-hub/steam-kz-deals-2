window.renderPackageDeal=function(g){
  const p=g?.better_purchase_option;
  if(!p||p.package_price_rub==null)return '';
  const count=Number(p.covered_visible_game_count)||0;
  const perGame=p.package_price_per_visible_game_rub!=null?Number(p.package_price_per_visible_game_rub):(count?Number(p.package_price_rub)/count:null);
  const standalone=p.standalone_total_rub;
  const savings=Number(p.savings_rub);
  const savingsPct=Number(p.savings_percent_vs_standalone);
  const strict=p.strict_current_price_savings===true||(Number.isFinite(savings)&&savings>0);
  const delta=p.price_delta_vs_standalone_rub!=null?Number(p.price_delta_vs_standalone_rub):(
    p.package_price_rub!=null&&standalone!=null?Number(p.package_price_rub)-Number(standalone):null
  );
  const titles=(p.covered_visible_titles||[]).filter(Boolean).map(escapeHtml).join(', ');
  const drivesRank=g.score_breakdown?.purchase_route==='fixed_package';
  const heading=strict?'🎁 Выгодный набор Steam':'🎁 Набор Steam';
  let rankNote='Набор показан как релевантный вариант покупки, но сам по себе не повышает рейтинг.';
  if(drivesRank){
    rankNote='Этот набор сейчас определяет балл выгодности покупки и поднимает игру в рейтинге.';
  }else if(strict){
    rankNote='Набор дешевле покупки этих игр по отдельности, но одиночный вариант сейчас получает не меньший балл покупки.';
  }
  const economics=[];
  if(standalone!=null)economics.push(`по отдельности ${fmtRub(standalone)}`);
  if(strict&&Number.isFinite(savings))economics.push(`экономия ${fmtRub(savings)}`);
  if(strict&&Number.isFinite(savingsPct))economics.push(`${savingsPct.toLocaleString('ru-RU',{maximumFractionDigits:1})}% дешевле`);
  if(!strict&&Number.isFinite(delta)&&delta>0)economics.push(`на ${fmtRub(delta)} дороже этих игр отдельно`);
  if(!strict&&Number.isFinite(delta)&&delta===0)economics.push('по той же цене, что и эти игры отдельно');
  const equivalenceNote=p.uses_verified_purchase_equivalence?'Покрытие включает подтверждённую улучшенную версию одной из игр.':'';
  return `<div class="offer" data-package-highlight="true" style="border-width:2px"><div class="offer-top"><div class="offer-title"><b>${heading}</b><br>${escapeHtml(p.package_title||'Набор Steam')}</div><div class="offer-price">${fmtRub(p.package_price_rub)}</div></div><div class="offer-meta"><b>${count} игр${perGame!=null?` · ≈ ${fmtRub(perGame)} за игру`:''}</b></div>${economics.length?`<div class="offer-meta">${economics.join(' · ')}</div>`:''}${titles?`<div class="offer-meta">Из текущего списка: ${titles}</div>`:''}${equivalenceNote?`<div class="offer-meta">${escapeHtml(equivalenceNote)}</div>`:''}<div class="offer-meta"><b>${escapeHtml(rankNote)}</b></div><div class="offer-actions"><button class="offer-link" type="button" data-open-web="${escapeHtml(p.web_url||'')}" data-open-steam="">Открыть набор в Steam</button></div></div>`;
};
