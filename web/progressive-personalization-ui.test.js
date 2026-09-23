const assert=require('assert');
const fs=require('fs');
const ui=require('./progressive-personalization-ui.js');

const fit={id:'fit',title:'Fit',analysis_state:'analyzed_fit',analysis_tier:1,total_score:10,sale_expiry_urgency_rank:2};
const error={id:'error',title:'Error',analysis_state:'analysis_incomplete',analysis_tier:2,deterministic_purchase_score:40,sale_expiry_urgency_rank:0};
const untouched={id:'untouched',title:'Untouched',analysis_state:'not_analyzed',analysis_tier:3,deterministic_purchase_score:40,sale_expiry_urgency_rank:0};

assert.deepStrictEqual(ui.sortItems([untouched,error,fit],false).map(x=>x.id),['fit','error','untouched']);
assert.deepStrictEqual(ui.sortItems([untouched,error,fit],true).map(x=>x.id),['fit','error','untouched']);

const e1={...error,id:'e1',title:'E1',deterministic_purchase_score:10,sale_expiry_urgency_rank:0};
const e2={...error,id:'e2',title:'E2',deterministic_purchase_score:40,sale_expiry_urgency_rank:2};
assert.deepStrictEqual(ui.sortItems([e1,e2],false).map(x=>x.id),['e2','e1']);
assert.deepStrictEqual(ui.sortItems([e1,e2],true).map(x=>x.id),['e1','e2']);

// Stage indicators consume only the explicit producer-owned stage fields.
const stages=ui.stageIndicators({
  fast_stage_state:'completed',fast_stage_outcome:'fit',
  dossier_stage_state:'accepted',
  deep_stage_state:'completed',deep_stage_outcome:'fit',deep_recovery_state:'none',
});
assert.deepStrictEqual(stages.map(x=>x.key),['fast','dossier','deep']);
assert.deepStrictEqual(stages.map(x=>x.symbol),['⚡','▤','◆']);
assert.deepStrictEqual(stages.map(x=>x.lit),[true,true,true]);
assert.strictEqual(stages.length,3);
assert(stages[0].title.includes('Быстрый разбор'));
assert(stages[1].title.includes('Подготовка досье'));
assert(stages[2].title.includes('Глубокий разбор'));

// Lit means exact completed-stage truth only. Pending/incomplete/error/recovery/unknown stay dim.
const fastCases=[
  [{fast_stage_state:'completed',fast_stage_outcome:'fit'},true],
  [{fast_stage_state:'completed',fast_stage_outcome:'not_fit'},true],
  [{fast_stage_state:'completed',fast_stage_outcome:null},false],
  [{fast_stage_state:'incomplete',fast_stage_outcome:null},false],
  [{fast_stage_state:'error',fast_stage_outcome:null},false],
  [{fast_stage_state:'not_started',fast_stage_outcome:null},false],
  [{fast_stage_state:'unknown',fast_stage_outcome:null},false],
];
for(const [game,expected] of fastCases)assert.strictEqual(ui.stageIndicators(game)[0].lit,expected);

const dossierCases=[
  [{dossier_stage_state:'accepted'},true],
  [{dossier_stage_state:'failed_or_recovery'},false],
  [{dossier_stage_state:'not_ready'},false],
  [{dossier_stage_state:'unknown'},false],
];
for(const [game,expected] of dossierCases)assert.strictEqual(ui.stageIndicators(game)[1].lit,expected);

const deepCases=[
  [{deep_stage_state:'completed',deep_stage_outcome:'fit',deep_recovery_state:'none'},true],
  [{deep_stage_state:'completed',deep_stage_outcome:'not_fit',deep_recovery_state:'none'},true],
  [{deep_stage_state:'completed',deep_stage_outcome:null,deep_recovery_state:'none'},false],
  [{deep_stage_state:'waiting_for_dossier',deep_stage_outcome:null,deep_recovery_state:'none'},false],
  [{deep_stage_state:'eligible_or_pending',deep_stage_outcome:null,deep_recovery_state:'none'},false],
  [{deep_stage_state:'incomplete_or_recovery',deep_stage_outcome:null,deep_recovery_state:'recovery_owned'},false],
  [{deep_stage_state:'incomplete_or_recovery',deep_stage_outcome:null,deep_recovery_state:'recovery_eligible'},false],
  [{deep_stage_state:'incomplete_or_recovery',deep_stage_outcome:null,deep_recovery_state:'recovery_pending'},false],
  [{deep_stage_state:'not_started',deep_stage_outcome:null,deep_recovery_state:'none'},false],
  [{deep_stage_state:'unknown',deep_stage_outcome:null,deep_recovery_state:'none'},false],
];
for(const [game,expected] of deepCases)assert.strictEqual(ui.stageIndicators(game)[2].lit,expected);

const recovery=ui.stageIndicators({
  fast_stage_state:'incomplete',fast_stage_outcome:null,
  dossier_stage_state:'failed_or_recovery',
  deep_stage_state:'incomplete_or_recovery',deep_stage_outcome:null,deep_recovery_state:'recovery_pending',
});
assert.deepStrictEqual(recovery.map(x=>x.lit),[false,false,false]);
assert(recovery[2].title.includes('восстановление ожидает выполнения'));

// Generic analysis state must never be used as a fallback for stage truth.
const noStageFallback=ui.stageIndicators({analysis_state:'analyzed_fit',analysis_resolution_pass:'pass2'});
assert.deepStrictEqual(noStageFallback.map(x=>x.lit),[false,false,false]);
assert.deepStrictEqual(noStageFallback.map(x=>x.tone),['unknown','unknown','unknown']);

// Statistics keep Fast, Dossier and Deep on their own canonical scopes.
const stats=ui.statisticsSections({
  fast_total_current_scope:511,fast_attempted_count:86,fast_completed_fit_count:10,fast_completed_not_fit_count:4,
  fast_incomplete_count:68,fast_error_count:4,fast_skipped_due_to_authoritative_deep_count:7,fast_remaining_count:418,
  dossier_total_current_scope:187,dossier_accepted_count:12,dossier_pending_count:170,dossier_failed_or_recovery_count:5,
  dossier_normal_first_pass_complete:false,dossier_all_accepted_or_recovered_complete:false,
  deep_total_current_coverage_target:499,deep_first_pass_attempted_count:2,deep_authoritative_completed_count:1,
  deep_completed_fit_count:1,deep_completed_not_fit_count:0,deep_incomplete_or_recovery_count:1,
  deep_waiting_for_dossier_count:470,deep_ready_or_pending_count:27,deep_normal_first_pass_remaining_count:497,
  deep_remaining_until_all_authoritative_count:498,deep_normal_first_pass_complete:false,deep_all_current_authoritative_complete:false,
});
assert.deepStrictEqual(stats.map(x=>x.key),['fast','dossier','deep']);
assert.deepStrictEqual(stats.map(x=>x.denominator),[511,187,499]);
assert.deepStrictEqual(stats.map(x=>x.scopeLabel),[
  'Всего игр для быстрого разбора','Всего игр для подготовки досье','Всего игр для глубокого разбора'
]);
assert.deepStrictEqual(stats.map(x=>x.denominatorKey),[
  'fast_total_current_scope','dossier_total_current_scope','deep_total_current_coverage_target'
]);

const fastRows=Object.fromEntries(stats[0].rows.map(row=>[row.key,row.label]));
assert.strictEqual(fastRows.fast_attempted_count,'Обработано');
assert.strictEqual(fastRows.fast_incomplete_count,'Не удалось сделать вывод');
assert.strictEqual(fastRows.fast_error_count,'Ошибки');
assert.strictEqual(fastRows.fast_skipped_due_to_authoritative_deep_count,'Не требовался: есть готовый глубокий разбор');
assert(stats[0].note.includes('Это сумма'));
assert(stats[0].note.includes('надёжных данных'));
assert(stats[0].note.includes('технический'));

assert.deepStrictEqual(stats[1].rows.map(row=>row.key),[
  'dossier_accepted_count','dossier_pending_count','dossier_failed_or_recovery_count'
]);
assert.deepStrictEqual(stats[1].rows.map(row=>row.label),['Готово','Ожидает','Требует восстановления']);
assert(!stats[1].rows.some(row=>/подходит/i.test(row.label)),'Dossier must remain neutral, not fit/not-fit');

assert.deepStrictEqual(stats[2].rows.map(row=>row.key),[
  'deep_authoritative_completed_count','deep_completed_fit_count','deep_completed_not_fit_count',
  'deep_incomplete_or_recovery_count','deep_waiting_for_dossier_count','deep_ready_or_pending_count',
  'deep_remaining_until_all_authoritative_count'
]);
assert.strictEqual(stats[2].rows[0].label,'Окончательно разобрано');
assert.strictEqual(stats[2].rows[stats[2].rows.length-1].label,'Осталось до окончательного разбора');
assert(stats[2].note.includes('глубокий разбор завершён'));

const userFacingStats=stats.flatMap(section=>[section.scopeLabel,section.note||'',...section.rows.map(row=>row.label)]).join(' ');
for(const jargon of ['authoritative','Fast-scope','Dossier-scope','Deep-покрытие']){
  assert(!userFacingStats.includes(jargon),`user-facing statistics jargon remains: ${jargon}`);
}
for(const removedKey of [
  'dossier_normal_first_pass_complete','dossier_all_accepted_or_recovered_complete',
  'deep_first_pass_attempted_count','deep_normal_first_pass_remaining_count',
  'deep_normal_first_pass_complete','deep_all_current_authoritative_complete'
]){
  assert(!stats.flatMap(section=>section.rows).some(row=>row.key===removedKey),`technical statistics row remains: ${removedKey}`);
}

const app=fs.readFileSync('web/app.js','utf8');
assert(app.includes("if(r.manual_end_at)manual.push(g.id);else normal.push(g.id);"));
assert(app.includes("return [...normal,...manual];"));
assert(app.includes("r.manual_end_at=Date.now();"));
assert(app.includes("progressiveUi().sortItems(items,urgencyFirstEnabled())"));
assert(app.includes("data.processing_status||{}"));
assert(app.includes("progressiveUi().statisticsSections"));
assert(app.includes("progressiveUi().stageIndicators"));
assert(app.includes("ind.lit===true"));
assert(app.includes("'unlit'"));
assert(app.includes('statistics-note'));
assert(app.includes("$('decision').classList.toggle('hidden',!personalized)"));
for(const stale of ['analysisBadge','processingStats','processingUpdated','progressiveUi().labelFor','progressiveUi().processingLines']){
  assert(!app.includes(stale),`stale large-status hook remains: ${stale}`);
}

const html=fs.readFileSync('web/index.html','utf8');
assert(html.includes('Быстрый разбор, подготовка досье и глубокий разбор считаются отдельно — у каждого свой объём работы.'));
for(const id of ['statisticsBtn','statisticsView','stageStatistics','stageIndicators','personalizationSection']){
  assert(html.includes(`id="${id}"`));
}
for(const removed of ['id="stats"','id="processingStats"','id="processingUpdated"','id="analysisBadge"']){
  assert(!html.includes(removed),`old always-visible status UI remains: ${removed}`);
}
for(const label of ['Подходит вам','Не подходит','Нужен дополнительный разбор','Ещё не проверена']){
  assert(!html.includes(label));
  assert(!app.includes(label));
}

const css=fs.readFileSync('web/styles.css','utf8');
assert(css.includes('.stage-indicators{'));
assert(css.includes('.statistics-stage-list{'));
assert(css.includes('@media(max-width:430px)'));
assert(css.includes('.statistics-metrics{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))'));
assert(css.includes('.stage-indicator{display:inline-flex;align-items:center;justify-content:center;width:27px;height:24px'));
assert(css.includes('.stage-indicator.unlit{'));
assert(css.includes('.stage-indicator.lit.ready{'));
assert(css.includes('.stage-indicator.lit.positive{'));
assert(css.includes('.stage-indicator.lit.negative{'));
assert(css.includes('.statistics-note{'));
assert(css.includes('.list-card-head{display:flex;align-items:flex-start;justify-content:space-between;gap:8px;min-width:0}'));

console.log('progressive personalization stage/statistics UI regression: ok');
