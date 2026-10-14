/* Bounded UI regression: historical evidence is display-only, never a score. */
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const window={};
vm.runInNewContext(fs.readFileSync('web/deep-history-ui.js','utf8'),{window,Intl,Date});
vm.runInNewContext(fs.readFileSync('web/progressive-personalization-ui.js','utf8'),{window,Date,Intl});
const history=window.DeepHistoryUI, ui=window.ProgressivePersonalizationUI;
const currentVersion='a'.repeat(64), previousVersion='b'.repeat(64);
const base={
  analysis_state:'analyzed_fit',total_score:91,ranking_stage:'fast_fit',ranking_stage_rank:2,
  deep_stage_state:'incomplete_or_recovery',deep_stage_outcome:null,
  deep_history:{
    status:'outdated',reason:'profile_content_version_changed',current_compatible:false,
    current_profile_content_version_id:currentVersion,
    current_profile_version_at_utc:null,
    last_completed_revision_id:'completed:1',last_completed_at_utc:'2026-10-11T05:11:09Z',
    last_completed_profile_content_version_id:previousVersion,
    last_completed_profile_version_at_utc:'2026-10-01T10:11:00Z',
    last_completed_outcome:'analyzed_not_fit',last_completed_appid:'111',
    last_completed_not_fit_evidence:['<unsafe> Not for me'],
    last_completed_positive_evidence:[],last_completed_score_findings:[],
    last_completed_negative_assessment:{findings:[{text_ru:'Недостаточно свободного времени'}]},
  }
};
let html=history.detailHtml(base);
assert(html.includes('Устаревший разбор'));
assert(html.includes('Не подходит'));
assert(html.includes('11.10.2026'));
assert(html.includes('Дата версии профиля неизвестна'));
assert(html.includes('&lt;unsafe&gt;'));
assert(html.includes('Недостаточно свободного времени'));
assert(html.includes('не влияет на текущие баллы'));
assert(!html.includes('Рейтинг: 91'));
assert.strictEqual(base.total_score,91);
const current=JSON.parse(JSON.stringify(base));
current.deep_history.status='current';
current.deep_history.last_completed_outcome='analyzed_fit';
current.deep_history.last_completed_positive_evidence=['Original positive evidence'];
current.deep_history.last_completed_not_fit_evidence=[];
html=history.detailHtml(current);
assert(html.includes('Актуальный разбор')&&html.includes('Original positive evidence'));
assert(!html.includes('не влияет на текущие баллы'));
const never=JSON.parse(JSON.stringify(base));
never.deep_history={status:'never_completed',current_profile_content_version_id:currentVersion,
  current_profile_version_at_utc:null,last_completed_revision_id:null};
html=history.detailHtml(never);
assert(html.includes('Успешного глубокого разбора этой игры пока не было'));
const noProjection={...base};delete noProjection.deep_history;
assert.strictEqual(history.detailHtml(noProjection),'');
const source={...base,ranking_stage:'fast_fit',ranking_stage_rank:2,priority_rank:1};
const highHistorical={...base,ranking_stage:'not_analyzed',ranking_stage_rank:4,
  total_score:null,priority_rank:2};
assert(ui.compareGames(source,highHistorical)<0); // historical Deep cannot promote rank
const status={
  deep_completed_history_contract:'PROGRESSIVE-DEEP-COMPLETED-HISTORY-V1',
  deep_current_profile_content_version_id:currentVersion,
  deep_current_profile_version_at_utc:null,deep_current_version_target:3,
  deep_current_version_completed_count:1,
  deep_historical_only_not_current_compatible_count:1,
  deep_never_completed_count:1,deep_current_version_remaining_count:2,
  deep_profile_version_unique_game_counts:{[currentVersion]:1,[previousVersion]:1,
    'legacy-unverified:pin:old':1}
};
const sections=ui.statisticsSections(status);
const section=sections.find(s=>s.key==='deep_history');
assert(section);
assert.strictEqual(section.denominator,3);
assert(section.rows.some(x=>x.key==='deep_current_version_completed_count'&&x.value===1));
assert(section.rows.some(x=>x.key==='deep_historical_only_not_current_compatible_count'&&x.value===1));
assert(section.rows.some(x=>x.key==='deep_never_completed_count'&&x.value===1));
assert(section.rows.some(x=>x.value==='Дата версии профиля неизвестна'));
assert.strictEqual(section.rows.filter(x=>x.key.startsWith('deep_profile_version_')).length,3);
assert(section.note.includes('суммировать строки версий нельзя'));
assert(!ui.statisticsSections({}).some(s=>s.key==='deep_history'));
console.log('Deep history UI: old/current/never, evidence, null dates, unique version stats and score separation: OK');
