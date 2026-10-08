"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const tasks=require("./tasks.js");
function node(tag){
  return {tag,children:[],attributes:{},className:"",id:"",textContent:"",
    appendChild(child){this.children.push(child);return child},
    replaceChildren(...children){this.children=children},
    setAttribute(k,v){this.attributes[k]=v}};
}
const elements={tasksMain:node("main"),tasksCounters:node("div"),tasksFreshness:node("div")};
const doc={createElement:node,getElementById:id=>elements[id]};
const base=(id,status)=>({id,title:"Проверка "+id,goal:"Показать результат",status,worker_slot:null,order:null,depends_on:[],blocker:"",effort:"низкая",effort_reason:"Одна страница",urgency:"обычная",urgency_reason:"Без блокеров",updated_on:"2026-10-08",updated_at_utc:"2026-10-08T10:36:42Z"});
const a=base("active-1","active");
const b=base("planned-1","planned");b.depends_on=["old-complete"];b.worker_slot=null;b.order={track:"Очередь",position:5};
const c=base("blocked-1","blocked");c.blocker="Ожидает подтверждения";
const d=base("old-complete","complete");
const groups=[["active",[a]],["planned",[b]],["blocked",[c]],["complete",[d]]].map(([status,list])=>({status,label:status,count:list.length,tasks:list}));
const payload={schema_version:1,contract:"SITE-DIRECTOR-TASKS-PUBLIC-V1",generated_at_utc:"2026-10-08T12:00:00Z",plan_updated_on:"2026-10-08",known_forward_count:3,groups,task_titles:Object.fromEntries([a,b,c,d].map(t=>[t.id,t.title]))};
assert.equal(tasks.validate(payload).length,4);
assert.equal(tasks.dateLabel("2026-10-08"),"08.10.2026");
tasks.render(doc,payload,new Date("2026-10-08T14:00:00Z"));
assert.equal(elements.tasksCounters.children.length,3);
assert.equal(elements.tasksMain.children.length,4);
const plannedCard=elements.tasksMain.children[1].children[1].children[0];
assert.equal(plannedCard.tag,"article");
assert.ok(JSON.stringify(plannedCard).includes("Проверка old-complete"));
assert.ok(JSON.stringify(plannedCard).includes("Одна страница"));
assert.ok(JSON.stringify(plannedCard).includes("Очередь"));
const bad=structuredClone(payload);bad.groups[1].tasks=[];
assert.throws(()=>tasks.validate(bad),/Неполная группировка/);
const badDep=structuredClone(payload);badDep.groups[1].tasks[0].depends_on=["missing"];
assert.throws(()=>tasks.validate(badDep),/зависимости/);
const raw=fs.readFileSync(__dirname+"/tasks.js","utf8");
assert.ok(!/innerHTML|outerHTML|eval\(/.test(raw));
console.log("SITE_TASKS_UI=PASS navigation, complete counts, dependencies and safe DOM rendering");
