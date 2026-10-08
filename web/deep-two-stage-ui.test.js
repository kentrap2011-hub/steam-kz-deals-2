const assert=require('assert');
const fs=require('fs');
require('./deep-two-stage-ui.js');
const deep=globalThis.DeepTwoStageUI;
const ui=require('./progressive-personalization-ui.js');
const contract='DEEP-TWO-STAGE-SITE-PROJECTION-V1';
const base={
  id:'game',title:'Example',deep_two_stage_site_contract:contract,
  dossier_status:'ready',stage1_status:'completed_fit',
  stage2_status:'awaiting_calibration',
  stage1_summary_ru:'Игра со сложной системой',
  stage1_positives:['Сильная механика'],
  stage1_negatives:['Неровный темп'],
  stage1_nuances:['Ниша'],
  stage1_point_breakdown:[{label_ru:'Глубина',direction:'positive',points:45.2,finding_reasons_ru:['Сильная механика']}],
  stage1_provisional_deep_fit_score_0_56:45.2,
  stage2_calibrated_deep_fit_score_0_56:null,stage2_calibration_delta:null,
  wishlist_bonus_0_or_4:4,purchase_score_0_40:30,
  personal_quality_score_0_60:null,total_score_0_100:null,
  priority_rank:17,fast_stage_state:'completed',
  score_breakdown:{total_score:99},total_score:99,
};
assert(deep.active(base));
assert(!deep.calibrated(base));
assert.strictEqual(deep.compactScore(base),'Ожидает сравнительной калибровки');
assert.strictEqual(deep.compactScore({...base,stage1_status:'pending',stage2_status:'not_eligible'}),'Ожидает анализа Stage 1');
assert.strictEqual(deep.compactScore({...base,stage1_status:'completed_not_fit',stage2_status:'not_eligible'}),'Анализ завершён: не подходит');
assert.strictEqual(deep.compactScore({...base,stage2_status:'diagnostic_incomplete'}),'Калибровка требует диагностики');
const pendingHtml=deep.detailHtml(base);
assert(pendingHtml.includes('45,20/56'));
assert(pendingHtml.includes('Сильная механика'));
assert(!pendingHtml.includes('99/100'),'legacy Fast total leaked');
assert(!pendingHtml.includes('49,2/60'),'Stage-1 provisional leaked as final');
const markers=[...pendingHtml.matchAll(/data-deep2-section="(\d+)"/g)].map(m=>Number(m[1]));
assert.deepStrictEqual(markers,[0,1,2,3,4,5]);
assert(pendingHtml.indexOf('Краткий вывод')<pendingHtml.indexOf('Плюсы'));
assert(pendingHtml.indexOf('Плюсы')<pendingHtml.indexOf('Минусы'));
assert(pendingHtml.indexOf('Минусы')<pendingHtml.indexOf('Прочее / нюансы'));
assert(pendingHtml.indexOf('Прочее / нюансы')<pendingHtml.indexOf('Изменение оценки'));
assert(pendingHtml.indexOf('Изменение оценки')<pendingHtml.indexOf('Почему выше / ниже'));
const indicators=ui.stageIndicators(base);
assert.deepStrictEqual(indicators.map(x=>x.key),['dossier','deep_stage1','deep_stage2']);
assert.deepStrictEqual(indicators.map(x=>x.lit),[true,true,false]);
assert(!indicators.some(x=>x.key==='fast'));
const calibrated={...base,stage2_status:'calibrated',
  stage2_calibrated_deep_fit_score_0_56:46.03,stage2_calibration_delta:.83,
  personal_quality_score_0_60:50.03,total_score_0_100:80.03,
  stage2_why_changed_ru:'Чуть выше ближайшей игры',
  stage2_neighbor_comparisons:[{anchor_id:'neighbor',relation:'near_tie_target_above',reasons_ru:['Сильнее в бою']}],
  stage2_why_above_ru:['Больше возможностей'],stage2_why_below_ru:['Слабее история'],
};
assert(deep.calibrated(calibrated));
assert(deep.compactScore(calibrated).includes('80,03/100'));
const finalHtml=deep.detailHtml(calibrated);
for(const x of ['46,03/56','50,03/60','80,03/100','+4','30/40','Чуть выше','Немного выше','Сильнее в бою','Больше возможностей','Слабее история']){
  assert(finalHtml.includes(x), 'missing '+x);
}
assert(ui.stageIndicators(calibrated)[2].lit);
const hostile={...calibrated,stage1_positives:['<script>alert(1)</script>'],
  stage2_neighbor_comparisons:[{anchor_id:'<img src=x onerror=alert(1)>',relation:'target_below',reasons_ru:['<b>unsafe</b>']}]};
const safe=deep.detailHtml(hostile);
assert(!safe.includes('<script>')&&!safe.includes('<img')&&!safe.includes('<b>unsafe</b>'));
assert(safe.includes('&lt;script&gt;'));
const stats=ui.statisticsSections({
  deep_two_stage_site_contract:contract,
  fast_total_current_scope:444,fast_completed_fit_count:5,
  dossier:{total_eligible:100,completed:30,pending:60,diagnostic_incomplete:10,
           last_attempt_at_utc:'2026-10-08T12:00:00Z',last_successful_result_at_utc:null,
           progress_percent:30},
  deep_stage1:{total_eligible:90,completed:40,completed_fit:35,completed_not_fit:5,
              pending:48,diagnostic_incomplete:2,progress_percent:44.4,
              last_attempt_at_utc:'2026-10-08T12:00:00Z',
              last_successful_result_at_utc:'2026-10-08T11:00:00Z'},
  deep_stage2:{stage1_fit_eligible:35,calibrated:17,awaiting_calibration:16,
              diagnostic_incomplete:2,progress_percent:48.6,
              last_attempt_at_utc:'2026-10-08T13:00:00Z',
              last_successful_calibration_at_utc:'2026-10-08T12:30:00Z'},
});
assert.deepStrictEqual(stats.map(x=>x.key),
 ['dossier','deep_stage1','deep_stage2','translation','publication']);
assert(!stats.some(x=>x.key==='fast'||x.key==='deep'));
assert.strictEqual(stats[1].denominator,90);
assert.strictEqual(stats[1].rows.find(r=>r.key==='pending').value,48);
assert.strictEqual(stats[1].rows.find(r=>r.key==='progress_percent').value,44.4);
assert.strictEqual(stats[2].rows.find(r=>r.key==='calibrated').value,17);
assert.strictEqual(stats[2].lastSuccessAtUtc,'2026-10-08T12:30:00Z');
assert(!ui.statisticsSections({}).some(s=>s.key==='deep_stage1'),'non-active mode leaked');
const app=fs.readFileSync('web/app.js','utf8');
const html=fs.readFileSync('web/index.html','utf8');
const wrapper=fs.readFileSync('web/score-details-ui.js','utf8');
assert(app.includes('DeepTwoStageUI.detailHtml(g)'));
assert(app.includes('DeepTwoStageUI.compactScore(g)'));
assert(app.includes('data.deep_two_stage_site_contract'));
assert(wrapper.includes('if(root.DeepTwoStageUI?.active(g))'));
assert(html.includes('id="deepTwoStageDetail"'));
assert(html.includes('deep-two-stage-ui.js'));
assert(html.includes('deep-two-stage.css'));
console.log('Deep two-stage site mirror UI regression: ok');
