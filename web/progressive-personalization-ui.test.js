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

assert.strictEqual(ui.labelFor(fit),'Разобрана · подходит вам');
assert.strictEqual(ui.labelFor(error),'Разбор не завершён');
assert.strictEqual(ui.labelFor(untouched),'Ещё не разобрана');
assert.strictEqual(ui.labelFor({...fit,analysis_resolution_pass:'pass2'}),'Разобрана · PASS 2');
assert.strictEqual(ui.labelFor({...error,analysis_resolution_pass:'pass2'}),'Разбор не завершён · PASS 2');
// Browser labels consume the explicit GitHub-generated provenance field and do
// not infer PASS 2 from semantic source/history.
assert.strictEqual(ui.labelFor({...fit,analysis_semantic_source:'progressive_pass2'}),'Разобрана · подходит вам');

const lines=ui.processingLines({
  total_current_candidates:734,analyzed_success_count:10,analyzed_fit_count:7,
  analyzed_not_fit_count:3,analysis_incomplete_count:4,not_analyzed_count:720
});
assert.deepStrictEqual(lines.map(x=>x[0]),[
  'Всего','Разобрано','Подходит','Не подходит','Ошибки / не завершено','Ещё не разобрано'
]);

const app=fs.readFileSync('web/app.js','utf8');
assert(app.includes("if(r.manual_end_at)manual.push(g.id);else normal.push(g.id);"));
assert(app.includes("return [...normal,...manual];"));
assert(app.includes("r.manual_end_at=Date.now();"));
assert(app.includes("progressiveUi().sortItems(items,urgencyFirstEnabled())"));
assert(app.includes("data.processing_status||{}"));

const html=fs.readFileSync('web/index.html','utf8');
for(const id of ['processingStats','processingUpdated','analysisBadge','personalizationSection']){
  assert(html.includes(`id="${id}"`));
}
console.log('progressive personalization UI regression: ok');
