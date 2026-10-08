(function(root,factory){
  const api=factory();
  if(typeof module==="object"&&module.exports)module.exports=api;
  if(root&&root.document&&typeof root.fetch==="function"){
    root.document.addEventListener("DOMContentLoaded",()=>api.load({document:root.document,fetch:root.fetch.bind(root),now:()=>new Date()}));
  }
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  const STATUSES=["active","planned","blocked","complete"];
  const STATUS_LABEL={active:"В работе",planned:"Запланировано",blocked:"Ожидает",complete:"Завершено"};

  function validate(payload){
    if(!payload||payload.schema_version!==1||payload.contract!=="SITE-DIRECTOR-TASKS-PUBLIC-V1"||!Array.isArray(payload.groups))throw new Error("Некорректный формат задач");
    if(payload.groups.length!==4||payload.groups.some((g,i)=>g.status!==STATUSES[i]||!Array.isArray(g.tasks)||g.count!==g.tasks.length))throw new Error("Неполная группировка задач");
    const tasks=payload.groups.flatMap(g=>g.tasks);
    if(new Set(tasks.map(t=>t.id)).size!==tasks.length)throw new Error("Повторяющиеся задачи");
    if(tasks.some(t=>!t.id||!t.title||!t.goal||!t.effort_reason||!t.urgency_reason||!t.updated_on||!Array.isArray(t.depends_on)))throw new Error("Некорректная задача");
    if(tasks.filter(t=>t.status!=="complete").length!==payload.known_forward_count)throw new Error("Неполный список");
    return tasks;
  }
  function dateLabel(value){
    if(!/^\d{4}-\d\d-\d\d$/.test(String(value||"")))return String(value||"неизвестно");
    const [y,m,d]=value.split("-");
    return d+"."+m+"."+y;
  }
  function el(doc,tag,className,text){
    const node=doc.createElement(tag);
    if(className)node.className=className;
    if(text!==undefined)node.textContent=String(text);
    return node;
  }
  function addText(parent,doc,tag,cls,text){
    const item=el(doc,tag,cls,text);parent.appendChild(item);return item;
  }
  function card(doc,task,titles){
    const article=el(doc,"article","task-card");
    article.id="task-"+task.id;
    const flags=el(doc,"div","task-flags");
    addText(flags,doc,"span","task-pill "+task.status,STATUS_LABEL[task.status]||task.status);
    if(task.order)addText(flags,doc,"span","task-pill",task.order.track+" · №"+task.order.position);
    if(task.worker_slot)addText(flags,doc,"span","task-pill",task.worker_slot);
    article.appendChild(flags);
    addText(article,doc,"h3","",task.title);
    addText(article,doc,"p","task-goal",task.goal);
    article.appendChild(el(doc,"hr","task-separator"));
    const factors=el(doc,"dl","task-factors");
    for(const [label,value,reason] of [["Трудоёмкость",task.effort,task.effort_reason],["Срочность",task.urgency,task.urgency_reason]]){
      const field=el(doc,"div","task-factor");
      addText(field,doc,"dt","",label+": "+value);
      addText(field,doc,"dd","",reason);
      factors.appendChild(field);
    }
    article.appendChild(factors);
    const meta=el(doc,"div","task-details");
    addText(meta,doc,"div","", "Обновлено: "+dateLabel(task.updated_on));
    if(task.depends_on.length){
      const deps=task.depends_on.map(id=>titles.get(id)||"Неизвестная задача ("+id+")");
      addText(meta,doc,"div","task-dependency","После: "+deps.join("; "));
    }
    if(task.blocker)addText(meta,doc,"div","task-dependency","Условие / препятствие: "+task.blocker);
    article.appendChild(meta);
    return article;
  }
  function render(doc,payload,now=new Date()){
    const all=validate(payload);
    const mount=doc.getElementById("tasksMain");
    const counters=doc.getElementById("tasksCounters");
    const freshness=doc.getElementById("tasksFreshness");
    if(!mount||!counters||!freshness)throw new Error("Нет контейнеров страницы задач");
    mount.replaceChildren();counters.replaceChildren();
    const titles=new Map(all.map(t=>[t.id,t.title]));
    for(const group of payload.groups){
      if(group.status!=="complete"){
        const c=el(doc,"div","tasks-counter");
        addText(c,doc,"b","",group.count);
        addText(c,doc,"span","",group.label);
        counters.appendChild(c);
      }
      if(!group.tasks.length)continue;
      const section=el(doc,"section","tasks-group");
      section.setAttribute("aria-label",group.label);
      const heading=el(doc,"div","tasks-group-title");
      addText(heading,doc,"h2","",group.label);
      addText(heading,doc,"span","",group.count+" задач");
      section.appendChild(heading);
      const grid=el(doc,"div","tasks-grid");
      for(const task of group.tasks)grid.appendChild(card(doc,task,titles));
      section.appendChild(grid);mount.appendChild(section);
    }
    const planDate=new Date(payload.plan_updated_on+"T00:00:00Z");
    const ageDays=(now.getTime()-planDate.getTime())/86400000;
    const stale=Number.isFinite(ageDays)&&ageDays>8;
    freshness.className="tasks-freshness"+(stale?" stale":"");
    const built=new Date(payload.generated_at_utc);
    const builtTime=Number.isNaN(built.getTime())?"неизвестно":built.toLocaleString("ru-RU");
    freshness.textContent="План обновлён: "+dateLabel(payload.plan_updated_on)+
      " · Статический снимок сайта: "+builtTime+
      " · Всего известных незавершённых задач: "+payload.known_forward_count+
      (stale?" · Внимание: план давно не пересматривался.":"");
  }
  async function load({document:doc,fetch:read,now}){
    try{
      const response=await read("data/tasks.json",{cache:"no-store"});
      if(!response.ok)throw new Error("HTTP "+response.status);
      const data=await response.json();
      render(doc,data,now());
    }catch(error){
      const mount=doc.getElementById("tasksMain");
      if(mount)mount.replaceChildren(el(doc,"p","tasks-error","Не удалось загрузить проверенный список задач. Попробуйте обновить страницу."));
      const freshness=doc.getElementById("tasksFreshness");
      if(freshness)freshness.textContent="Не удалось проверить свежесть плана.";
    }
  }
  return {validate,dateLabel,render,load};
});
