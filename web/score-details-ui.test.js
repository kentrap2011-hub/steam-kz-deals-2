const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

global.window=globalThis;
global.document={addEventListener(){}};
require(path.join(__dirname,'score-details-ui.js'));

const score={
  total_score:67.5,total_max:100,
  personal_score:45.5,personal_max:60,
  purchase_score:22,purchase_max:40,
  precision:{code:'legacy_coarse_fit',label:'Грубая оценка по старым данным',is_coarse_legacy:true},
  purchase_route:'fixed_package',purchase_route_label:'Выгодный набор Steam',package_score_delta_vs_standalone:4,
  personal_components:[
    {id:'taste',label:'Игра сама по себе',points:42,max_points:50,value:'strong · грубая оценка по старым данным'},
    {id:'wishlist',label:'Вишлист Steam',points:4,max_points:4,value:'да'},
    {id:'achievements',label:'Достижения',points:1.5,max_points:3,value:'качество 5/5 · новая или не подтверждено, что играл'},
    {id:'duration',label:'Продолжительность',points:1,max_points:3,value:'42 ч · very_short_or_long'},
    {id:'risk',label:'Риск',points:-3,max_penalty:12,value:'средний описательный риск'},
  ],
  purchase_components:[
    {id:'package_savings_percent',label:'Экономия набора против покупки игр отдельно',points:11,max_points:16,value:'38.2% · 164 ₽'},
    {id:'package_effective_price',label:'Цена за одну игру в наборе',points:11,max_points:12,value:'≈ 133 ₽/игра'},
    {id:'package_coverage',label:'Игр из текущего списка в наборе',points:0,max_points:12,value:'2 игры из текущего списка',covered_visible_game_count:2},
  ],
};

const html=renderDetailedScoreHtml(score);
const text=html.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim();
assert.match(text,/Детальная оценка/);
assert.match(text,/Подходит 45,5\/60/);
assert.match(text,/Покупка 22\/40/);
assert.match(html,/data-score-section="personal"[^]*Подходит тебе[^]*45,5\/60/);
assert.match(html,/data-score-section="purchase"[^]*Выгодность покупки[^]*22\/40/);
for(const row of [...score.personal_components,...score.purchase_components])assert.match(html,new RegExp(`data-score-component="${row.id}"`),`missing visible component ${row.id}`);
assert.equal((html.match(/class="score-row"/g)||[]).length,8,'all previously visible score components must remain present exactly once');
assert.match(text,/Вкус сильное совпадение · по старым данным \+42\/50/);
assert.match(text,/Вишлист есть в желаемом \+4\/4/);
assert.match(text,/Длительность 42 ч · заметно вне привычной длительности \+1\/3/);
assert.match(text,/Выгодность считается по набору Steam · преимущество \+4 балла против покупки отдельно/);
assert.ok(html.indexOf('data-score-purchase-driver')>html.indexOf('data-score-section="purchase"'),'package/commercial driver must live inside purchase section');
assert.doesNotMatch(text,/preferred_medium|slightly_short_or_long|very_short_or_long|extreme_length|legacy_coarse_fit|normalized_taste_factors|fixed_package|standalone/,'visible copy must not leak technical internal labels');
assert.match(text,/67,5\/100/,'total score value must be rendered unchanged');
assert.match(text,/45,5\/60/,'personal score value must be rendered unchanged');
assert.match(text,/22\/40/,'purchase score value must be rendered unchanged');
assert.match(html,/data-score-details-panel="true" hidden/,'expanded details must be collapsed by default');
assert.equal((html.match(/score-chip/g)||[]).length,0,'new mobile details must not render pill/chip wall');
const sectionCount=(html.match(/class="score-section /g)||[]).length;
const componentCount=score.personal_components.length+score.purchase_components.length;
const legacyDecoratedBoxes=2+componentCount;
const compactDecoratedBoxes=sectionCount;
assert.equal(sectionCount,2);
assert.ok(compactDecoratedBoxes<=legacyDecoratedBoxes*0.4,'bordered/decorated containers must be substantially reduced versus legacy group + pill structure');

const attrs={'aria-expanded':'false'};
const cue={textContent:'подробнее'};
const button={title:'',setAttribute(k,v){attrs[k]=v;},getAttribute(k){return attrs[k];},querySelector(sel){return sel==='[data-score-cue]'?cue:null;}};
const panel={hidden:true};
const wrapper={querySelector(sel){if(sel==='[data-score-details-toggle]')return button;if(sel==='[data-score-details-panel]')return panel;return null;}};
assert.equal(setScoreDetailsExpanded(wrapper,true),true);
assert.equal(panel.hidden,false);
assert.equal(attrs['aria-expanded'],'true');
assert.equal(cue.textContent,'свернуть');
assert.equal(setScoreDetailsExpanded(wrapper,false),true);
assert.equal(panel.hidden,true);
assert.equal(attrs['aria-expanded'],'false');
assert.equal(cue.textContent,'подробнее');

const css=fs.readFileSync(path.join(__dirname,'score-details.css'),'utf8');
assert.match(css,/\.score-row\{[^}]*grid-template-columns:minmax\(0,1fr\) auto/,'component rows must use compact two-column layout');
assert.match(css,/\.score-row\{[^}]*padding:4px 0/,'base score rows must stay compact');
assert.match(css,/@media\(max-width:430px\)[^]*\.score-row\{padding:3px 0\}/,'mobile score rows must tighten vertical padding');

const nodes={
  prioritySection:{classList:{toggle(){}}},
  priorityWhy:{textContent:''},
  priorityFactors:{innerHTML:''},
};
global.$=id=>nodes[id]||null;
global.urgencyFirstEnabled=()=>false;
global.queuePosition=()=>3;
global.rec=()=>({});
renderPriority({id:'App_1',priority_rank:7,priority_factors:[{id:'sale_expiry_urgency_asc',label:'Срочность скидки',value:'обычная срочность'}],score_breakdown:score});
assert.match(nodes.priorityFactors.innerHTML,/Детальная оценка/,'late-loaded score UI must replace app score renderer');
assert.match(nodes.priorityFactors.innerHTML,/Срочность скидки/,'existing urgency factor must be preserved');
assert.match(nodes.priorityWhy.textContent,/Позиция в текущей очереди: №3/,'existing queue explanation must be preserved');

console.log('detailed score mobile regression: PASS');
