const assert=require('node:assert/strict');
const path=require('node:path');

global.window=globalThis;
global.escapeHtml=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
global.fmtRub=value=>`${Number(value).toLocaleString('ru-RU')} ₽`;
global.document={addEventListener(){}};
require(path.join(__dirname,'package-deal-ui.js'));

function fixture(route='fixed_package'){
  return {
    title:'BioShock Infinite',
    score_breakdown:{purchase_route:route},
    offers:[
      {title:'BioShock Infinite',current_price_rub:256,original_price_rub:1279,discount_percent:80,historical_minimum_rub:199,web_url:'https://store/1',steam_url:'steam://1'},
      {title:'BioShock Infinite - Season Pass',current_price_rub:173,original_price_rub:699,discount_percent:75,historical_minimum_rub:149,web_url:'https://store/2',steam_url:'steam://2'},
    ],
    better_purchase_option:{
      package_title:'BioShock: The Collection',package_price_rub:265,covered_visible_game_count:2,package_price_per_visible_game_rub:132.5,
      standalone_total_rub:429,visible_standalone_game_total_rub:256,verified_incremental_content_total_rub:173,comparable_entitlement_total_rub:429,
      savings_rub:164,savings_percent_vs_standalone:38.2,strict_current_price_savings:true,comparison_source_aligned:true,
      covered_visible_titles:['BioShock Remastered','BioShock 2 Remastered'],
      verified_included_content:[
        {title:'BioShock Remastered'},{title:'BioShock 2 Remastered'},{title:'BioShock Infinite'},{title:'BioShock Infinite - Season Pass'},{title:'Clash in the Clouds'},{title:'Burial at Sea'},
      ],
      verified_incremental_content:[{title:'BioShock Infinite - Season Pass'}],
      verified_incremental_content_unpriced:[{title:'Museum of Orphaned Concepts'}],
      verified_nonpersonalized_included_content:[{title:'BioShock 2 Multiplayer'}],
      uses_verified_purchase_equivalence:true,web_url:'https://store/package',
    },
  };
}

function visibleText(html){
  return html.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
}

const fixed=fixture('fixed_package');
const compact=renderPackageDeal(fixed,{compact:true});
const full=renderPackageDeal(fixed);
assert.match(compact,/BioShock: The Collection/);
assert.match(compact,/Сейчас это рекомендуемый способ покупки/);
assert.doesNotMatch(compact,/Состав Steam|Учтённый доп\. контент|Покрывает из текущего списка/,'collapsed package must omit long composition details');
assert.match(full,/Состав Steam \(6\)/);
assert.match(full,/BioShock Infinite - Season Pass/);
assert.match(full,/Museum of Orphaned Concepts/);
assert.match(full,/BioShock 2 Multiplayer/);
assert.match(full,/Покрытие включает подтверждённую улучшенную версию/);
assert.doesNotMatch(`${compact}${full}`,/балл покупки|получает не меньший|поднимает игру в рейтинге|влияние на рейтинг/,'visible copy must not expose internal score/rank terminology');
assert.ok(visibleText(compact).length<visibleText(full).length*0.6,'mobile collapsed package snapshot must be substantially shorter than expanded detail text');

const fixedMarkup=renderPurchaseOptions(fixed);
const fixedBeforeMore=fixedMarkup.split('<div class="purchase-more"')[0];
assert.equal((fixedBeforeMore.match(/class="offer(?: |")/g)||[]).length,1,'collapsed mobile state must show exactly one purchase card');
assert.match(fixedBeforeMore,/data-purchase-kind="fixed_package"/,'producer-owned fixed_package route must stay primary');
assert.match(fixedMarkup,/Показать ещё 2 варианта/);
assert.match(fixedMarkup,/data-purchase-more="true" hidden/,'other options must be collapsed by default');
assert.match(fixedMarkup,/Что входит и почему это выгодно/);
assert.match(fixedMarkup,/Состав Steam \(6\)/,'expanded content must retain full package composition');
assert.match(fixedMarkup,/BioShock Infinite/);
assert.match(fixedMarkup,/BioShock Infinite - Season Pass/);

const target={innerHTML:''};
global.$=id=>id==='offers'?target:null;
renderOffers(fixed);
assert.equal(target.innerHTML,fixedMarkup,'late-loaded package UI must replace the app purchase renderer with compact markup');

const standalone=fixture('standalone');
standalone.better_purchase_option.package_price_rub=1;
standalone.better_purchase_option.savings_rub=428;
const standaloneMarkup=renderPurchaseOptions(standalone);
const standaloneBeforeMore=standaloneMarkup.split('<div class="purchase-more"')[0];
assert.match(standaloneBeforeMore,/data-purchase-kind="standalone"/,'UI must obey producer route even if package price looks cheaper');
assert.match(standaloneBeforeMore,/BioShock Infinite · рекомендуемый/);
assert.doesNotMatch(standaloneBeforeMore,/BioShock: The Collection/,'package must not displace producer-selected standalone route');
assert.match(standaloneMarkup,/BioShock: The Collection/,'expanded state must still expose package alternative');
assert.match(standaloneMarkup,/отдельная покупка сейчас не хуже по совокупной выгоде/);

const forcedPackage=fixture('fixed_package');
forcedPackage.better_purchase_option.package_price_rub=9999;
const forcedPackageMarkup=renderPurchaseOptions(forcedPackage);
assert.match(forcedPackageMarkup.split('<div class="purchase-more"')[0],/data-purchase-kind="fixed_package"/,'UI must not re-rank a producer-selected package from local price math');

const panel={hidden:true};
const attrs={};
const button={dataset:{collapsedLabel:'Показать ещё 2 варианта'},textContent:'Показать ещё 2 варианта',setAttribute(k,v){attrs[k]=v;}};
const wrapper={querySelector(selector){return selector==='[data-purchase-toggle]'?button:selector==='[data-purchase-more]'?panel:null;}};
assert.equal(setPurchaseOptionsExpanded(wrapper,true),true);
assert.equal(panel.hidden,false);
assert.equal(attrs['aria-expanded'],'true');
assert.equal(button.textContent,'Свернуть варианты');
setPurchaseOptionsExpanded(wrapper,false);
assert.equal(panel.hidden,true);
assert.equal(attrs['aria-expanded'],'false');
assert.equal(button.textContent,'Показать ещё 2 варианта');

console.log('compact purchase options mobile regression: PASS');
