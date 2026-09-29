const assert=require('assert');
const fs=require('fs');
const ui=require('./progressive-personalization-ui.js');

const deep60={id:'deep60',title:'Deep 60',analysis_state:'analyzed_fit',analysis_tier:1,ranking_stage:'deep_fit',ranking_stage_rank:1,total_score:60,priority_rank:1,sale_expiry_urgency_rank:2};
const deep70={...deep60,id:'deep70',title:'Deep 70',total_score:70,priority_rank:1};
const fast99={id:'fast99',title:'Fast 99',analysis_state:'analyzed_fit',analysis_tier:1,ranking_stage:'fast_fit',ranking_stage_rank:2,total_score:99,priority_rank:2,sale_expiry_urgency_rank:0};
const fast80={...fast99,id:'fast80',title:'Fast 80',total_score:80,priority_rank:3,sale_expiry_urgency_rank:2};
const error={id:'error',title:'Error',analysis_state:'analysis_incomplete',analysis_tier:2,ranking_stage:'analysis_incomplete',ranking_stage_rank:3,deterministic_purchase_score:40,priority_rank:4,sale_expiry_urgency_rank:0};
const untouched={id:'untouched',title:'Untouched',analysis_state:'not_analyzed',analysis_tier:3,ranking_stage:'not_analyzed',ranking_stage_rank:4,deterministic_purchase_score:40,priority_rank:5,sale_expiry_urgency_rank:0};

assert.deepStrictEqual(ui.sortItems([fast99,deep60],false).map(x=>x.id),['deep60','fast99']);
assert.deepStrictEqual(ui.sortItems([fast99,deep60],true).map(x=>x.id),['deep60','fast99']);
assert.deepStrictEqual(ui.sortItems([deep60,deep70],false).map(x=>x.id),['deep70','deep60']);
assert.deepStrictEqual(ui.sortItems([fast80,fast99],false).map(x=>x.id),['fast99','fast80']);
assert.deepStrictEqual(ui.sortItems([untouched,error,fast99,deep60],false).map(x=>x.id),['deep60','fast99','error','untouched']);

// Known passed sale ends are a local visibility gate, independent of semantic stage/state.
const expiryNow=Date.parse('2026-09-29T07:00:00+00:00');
const expiryPast='2026-09-28T17:00:00+00:00';
const expiryExact='2026-09-29T07:00:00+00:00';
const expiryFuture='2026-09-30T07:00:00+00:00';
const expiredDeep={...deep60,id:'expired-deep',sale_end_utc:expiryPast};
const expiredFast={...fast99,id:'expired-fast',sale_end_utc:expiryPast};
const expiredUnresolved={...error,id:'expired-unresolved',sale_end_utc:expiryPast};
const expiredManual={...untouched,id:'expired-manual',sale_end_utc:expiryPast,manual_end_at:123};
for(const game of [expiredDeep,expiredFast,expiredUnresolved,expiredManual]){
  assert.strictEqual(ui.hasKnownExpiredSale(game,expiryNow),true,`${game.id} must be hidden after its known sale end`);
}
assert.strictEqual(ui.hasKnownExpiredSale({...deep60,sale_end_utc:expiryExact},expiryNow),true,'sale end exactly now must be hidden');
assert.strictEqual(ui.hasKnownExpiredSale({...deep60,sale_end_utc:expiryFuture},expiryNow),false,'future sale remains visible');
assert.strictEqual(ui.hasKnownExpiredSale({...deep60,sale_end_utc:null},expiryNow),false,'unknown sale end remains visible');
assert.strictEqual(ui.hasKnownExpiredSale({...deep60,sale_end_utc:'not-a-date'},expiryNow),false,'malformed sale end follows unknown-date semantics');
assert.strictEqual(ui.hasKnownExpiredSale({...deep60},expiryNow),false,'missing sale end remains visible');

const titanfall={...deep60,id:'1237970',title:'Titanfall® 2',sale_end_utc:'2026-09-28T17:00:00+00:00'};
assert.strictEqual(ui.filterActiveSaleItems([titanfall],expiryNow).length,0,'pinned Titanfall sale must not remain in active feed after expiry');

const preservedSemantic={...deep60,id:'preserved',sale_end_utc:expiryFuture,deep_stage_state:'completed',deep_stage_outcome:'fit',dossier_stage_state:'accepted',fast_stage_state:'completed',fast_stage_outcome:'fit'};
const preservedBefore=JSON.parse(JSON.stringify(preservedSemantic));
const visibleAfterFilter=ui.filterActiveSaleItems([
  expiredDeep,expiredFast,expiredUnresolved,expiredManual,
  {...deep60,id:'future',sale_end_utc:expiryFuture},
  {...deep60,id:'unknown',sale_end_utc:null},
  {...deep60,id:'malformed',sale_end_utc:'bad-date'},
  preservedSemantic,
],expiryNow);
assert.deepStrictEqual(visibleAfterFilter.map(x=>x.id),['future','unknown','malformed','preserved']);
assert.strictEqual(visibleAfterFilter[visibleAfterFilter.length-1],preservedSemantic,'visibility filter must preserve semantic object/result identity');
assert.deepStrictEqual(preservedSemantic,preservedBefore,'visibility filter must not mutate Taste/Fast/Deep/Dossier fields');

const laterSale={...titanfall,sale_end_utc:expiryFuture};
assert.strictEqual(ui.filterActiveSaleItems([laterSale],expiryNow).length,1,'fresh later sale with new future end becomes visible normally');

const currentExpired={...deep60,id:'current-expired',sale_end_utc:expiryPast,sale_expiry_urgency_rank:0};
const nextVisible={...deep60,id:'next-visible',sale_end_utc:expiryFuture,sale_expiry_urgency_rank:2};
const laterVisible={...fast99,id:'later-visible',sale_end_utc:null,sale_expiry_urgency_rank:2};
const visibleQueue=ui.filterActiveSaleItems([currentExpired,nextVisible,laterVisible],expiryNow);
assert.deepStrictEqual(visibleQueue.map(x=>x.id),['next-visible','later-visible']);
assert.strictEqual(visibleQueue.length,2,'visible feed count must exclude expired cards');
assert.strictEqual(ui.cursorForVisibleIds(['current-expired','next-visible','later-visible'],0,visibleQueue.map(x=>x.id)),0,'expired current card must advance to the next visible card');
assert.strictEqual(`${ui.cursorForVisibleIds(['current-expired','next-visible','later-visible'],0,visibleQueue.map(x=>x.id))+1} из ${visibleQueue.length}`,'1 из 2','position text inputs must use the filtered visible set');
assert.deepStrictEqual(ui.sortItems(ui.filterActiveSaleItems([currentExpired,nextVisible],expiryNow),true).map(x=>x.id),['next-visible'],'urgency mode must not resurrect an expired card');

// Urgency may reorder only inside the same producer-owned ranking stage.
const deepUrgentLow={...deep60,id:'deep-urgent-low',title:'Deep urgent low',total_score:40,priority_rank:2,sale_expiry_urgency_rank:0};
const deepLaterHigh={...deep60,id:'deep-later-high',title:'Deep later high',total_score:90,priority_rank:1,sale_expiry_urgency_rank:2};
assert.deepStrictEqual(ui.sortItems([deepUrgentLow,deepLaterHigh],false).map(x=>x.id),['deep-later-high','deep-urgent-low']);
assert.deepStrictEqual(ui.sortItems([deepUrgentLow,deepLaterHigh],true).map(x=>x.id),['deep-urgent-low','deep-later-high']);
assert.deepStrictEqual(ui.sortItems([fast99,deepLaterHigh],true).map(x=>x.id),['deep-later-high','fast99']);

const e1={...error,id:'e1',title:'E1',deterministic_purchase_score:10,priority_rank:5,sale_expiry_urgency_rank:0};
const e2={...error,id:'e2',title:'E2',deterministic_purchase_score:40,priority_rank:4,sale_expiry_urgency_rank:2};
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
const stageTimes={
  fast:'2026-09-27T11:03:00+00:00',
  dossier:'2026-09-27T10:05:00+00:00',
  deep:'2026-09-27T12:04:00+00:00',
  translationSuccess:'2026-09-29T07:20:00+00:00',
  translationAttempt:'2026-09-29T08:15:00+00:00',
};
const stats=ui.statisticsSections({
  fast_last_write_at_utc:stageTimes.fast,
  dossier_last_write_at_utc:stageTimes.dossier,
  deep_last_write_at_utc:stageTimes.deep,
  fast_total_current_scope:511,fast_attempted_count:86,fast_completed_fit_count:10,fast_completed_not_fit_count:4,
  fast_incomplete_count:68,fast_error_count:4,fast_skipped_due_to_authoritative_deep_count:7,fast_remaining_count:418,
  dossier_total_current_scope:187,dossier_accepted_count:12,dossier_pending_count:170,dossier_failed_or_recovery_count:5,
  dossier_normal_first_pass_complete:false,dossier_all_accepted_or_recovered_complete:false,
  deep_total_current_coverage_target:499,deep_first_pass_attempted_count:2,deep_authoritative_completed_count:1,
  deep_completed_fit_count:1,deep_completed_not_fit_count:0,deep_incomplete_or_recovery_count:1,
  deep_waiting_for_dossier_count:470,deep_ready_or_pending_count:27,deep_normal_first_pass_remaining_count:497,
  deep_remaining_until_all_authoritative_count:498,deep_normal_first_pass_complete:false,deep_all_current_authoritative_complete:false,
  untranslated_game_count:71,
  last_successful_translation_at_utc:stageTimes.translationSuccess,
  last_translation_attempt_at_utc:stageTimes.translationAttempt,
});
assert.deepStrictEqual(stats.map(x=>x.key),['fast','dossier','deep','translation']);
assert.deepStrictEqual(stats.map(x=>x.lastWriteAtUtc),[
  stageTimes.fast,stageTimes.dossier,stageTimes.deep,null
]);
const noWriteStats=ui.statisticsSections({});
assert.deepStrictEqual(noWriteStats.map(x=>x.lastWriteAtUtc),[null,null,null,null]);
assert.strictEqual(ui.formatLastWriteAt(null),'ещё не было записей');
assert.strictEqual(ui.formatLastWriteAt(''),'ещё не было записей');
assert.strictEqual(ui.formatLastWriteAt('not-a-date'),'ещё не было записей');
assert.notStrictEqual(ui.formatLastWriteAt(stageTimes.fast),'ещё не было записей');
assert(!ui.formatLastWriteAt.toString().includes('Date.now'),'timestamp formatter must not infer a heartbeat');
assert.deepStrictEqual(stats.map(x=>x.denominator),[511,187,499,71]);
assert.deepStrictEqual(stats.map(x=>x.scopeLabel),[
  'Всего игр для быстрого разбора','Всего игр для подготовки досье','Всего игр для глубокого разбора','Игр без перевода:'
]);
assert.deepStrictEqual(stats.map(x=>x.denominatorKey),[
  'fast_total_current_scope','dossier_total_current_scope','deep_total_current_coverage_target','untranslated_game_count'
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

const translationSection=stats[3];
assert.strictEqual(translationSection.title,'Переводы описаний');
assert.strictEqual(translationSection.showLastWrite,false);
assert.deepStrictEqual(translationSection.rows.map(row=>row.key),[
  'last_successful_translation_at_utc','last_translation_attempt_at_utc'
]);
assert.deepStrictEqual(translationSection.rows.map(row=>row.label),[
  'Последний успешный перевод','Последняя попытка перевода'
]);
assert.strictEqual(translationSection.rows[0].value,ui.formatLastWriteAt(stageTimes.translationSuccess));
assert.strictEqual(translationSection.rows[1].value,ui.formatLastWriteAt(stageTimes.translationAttempt));
assert(translationSection.note.includes('не останавливает публикацию'));
const noTranslationHistory=ui.statisticsSections({untranslated_game_count:5})[3];
assert.strictEqual(noTranslationHistory.rows[0].value,'ещё не было записей');
assert.strictEqual(noTranslationHistory.rows[1].value,'ещё не было записей');
assert(!ui.statisticsSections.toString().includes('Date.now'),'Statistics must not invent translation timestamps');

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
assert(app.includes("items=progressiveUi().filterActiveSaleItems(payloadItems(),nowMs);"));
assert(app.includes("function render(){buildQueue();"));
assert(app.includes("function searchRender(){\n  buildQueue();"));
assert(app.includes("progressiveUi().cursorForVisibleIds(oldIds,oldCursor,ids)"));
assert(app.includes("if(Number.isNaN(d.getTime()))return 'Срок скидки неизвестен';"));
assert(app.indexOf("items=progressiveUi().filterActiveSaleItems(payloadItems(),nowMs);")<app.indexOf("const activeIds=new Set(items.map(x=>x.id));"),'expiry filtering must happen before queue/manual-end reconciliation');
assert(app.includes("data.processing_status||{}"));
assert(app.includes("progressiveUi().statisticsSections"));
assert(app.includes("progressiveUi().formatLastWriteAt(section.lastWriteAtUtc)"));
assert(app.includes("section.showLastWrite===false"));
assert(app.includes('Последняя запись:'));
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
assert(css.includes('.statistics-last-write{'));
assert(css.includes('.list-card-head{display:flex;align-items:flex-start;justify-content:space-between;gap:8px;min-width:0}'));

console.log('progressive personalization stage/statistics UI regression: ok');
