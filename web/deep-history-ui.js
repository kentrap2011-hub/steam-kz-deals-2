/* Read-only Deep history presentation. All freshness/verdicts are producer-owned. */
(function(root){
  'use strict';
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const validDate=value=>{
    if(typeof value!=='string'||!value)return null;
    const date=new Date(value);
    if(Number.isNaN(date.getTime()))return null;
    return new Intl.DateTimeFormat('ru-RU',{day:'2-digit',month:'2-digit',year:'numeric',
      hour:'2-digit',minute:'2-digit',hourCycle:'h23',timeZone:'UTC'}).format(date)+' UTC';
  };
  const dateOrUnknown=value=>validDate(value)||'Дата версии профиля неизвестна';
  const shortVersion=value=>typeof value==='string'&&/^[a-f0-9]{64}$/.test(value)
    ?value.slice(0,10):'не подтверждена';
  function list(values){
    const entries=Array.isArray(values)?values.filter(v=>typeof v==='string'&&v.trim()):[];
    return entries.length?'<ul>'+entries.map(v=>'<li>'+esc(v)+'</li>').join('')+'</ul>':'';
  }
  function textFindings(values){
    return Array.isArray(values)?values.filter(v=>v&&typeof v.text_ru==='string')
      .map(v=>v.text_ru):[];
  }
  function detailHtml(game){
    const h=game&&game.deep_history;
    if(!h||!['current','outdated','never_completed'].includes(h.status))return '';
    const currentDate=dateOrUnknown(h.current_profile_version_at_utc);
    const currentVersion=shortVersion(h.current_profile_content_version_id);
    const header='<div class="deep-history-heading"><h3>История глубокого разбора</h3>'+
      '<div>Текущая версия профиля: <b>'+esc(currentVersion)+'</b> · '+esc(currentDate)+'</div></div>';
    if(h.status==='never_completed'||!h.last_completed_revision_id){
      return '<div class="deep-history-panel" data-deep-history-status="never_completed">'+header+
        '<p class="deep-history-never">Успешного глубокого разбора этой игры пока не было.</p></div>';
    }
    if(!['analyzed_fit','analyzed_not_fit'].includes(h.last_completed_outcome))return '';
    const current=h.status==='current';
    const label=current?'Актуальный разбор':'Устаревший разбор';
    const verdict=h.last_completed_outcome==='analyzed_fit'?'Подходит':'Не подходит';
    const accepted=validDate(h.last_completed_at_utc)||'Дата разбора не подтверждена';
    const pastVersion=shortVersion(h.last_completed_profile_content_version_id);
    const profileDate=dateOrUnknown(h.last_completed_profile_version_at_utc);
    let evidence='';
    const positive=list(h.last_completed_positive_evidence);
    const negative=list(h.last_completed_not_fit_evidence);
    const scored=list(textFindings(h.last_completed_score_findings));
    const assessment=list(textFindings(h.last_completed_negative_assessment?.findings));
    if(positive)evidence+='<h4>Что понравится</h4>'+positive;
    if(negative)evidence+='<h4>Почему может не подойти</h4>'+negative;
    if(scored)evidence+='<h4>Подтверждённые причины оценки</h4>'+scored;
    if(assessment)evidence+='<h4>Риски и оговорки</h4>'+assessment;
    if(!evidence)evidence='<p class="muted">Подробные доказательства в сохранённом разборе отсутствуют.</p>';
    return '<div class="deep-history-panel" data-deep-history-status="'+(current?'current':'outdated')+'">'+
      header+'<div class="deep-history-summary"><span class="deep-history-badge '+(current?'is-current':'is-outdated')+
      '">'+label+'</span><strong>Итог: '+esc(verdict)+'</strong></div>'+
      '<p>Разбор принят: <b>'+esc(accepted)+'</b></p>'+
      '<p>Версия профиля при разборе: <b>'+esc(pastVersion)+'</b> · '+esc(profileDate)+'</p>'+
      (!current?'<p class="deep-history-warning">Это сохранённый исторический вывод. Он не влияет на текущие баллы, рейтинг или рекомендацию.</p>':'')+
      evidence+'</div>';
  }
  root.DeepHistoryUI={detailHtml,shortVersion,dateOrUnknown,validDate};
})(typeof window!=='undefined'?window:globalThis);
