'use strict';
const assert=require('node:assert/strict');
const {prepare,publish}=require('./director_registration_prewrite.js');
const SHA='a'.repeat(40), DAY='2026-10-28';
const make=(id,slot,patch={})=>Object.assign({
 id,title:'ЧАТ 7 — регистрационный тест',goal:'Проверить узкую регистрацию задания',
 status:'active',effort:'низкая',effort_reason:'Ограниченная техническая задача',
 urgency:'обычная',urgency_reason:'Нужна проверка',task_file:'WORKER_TASK_'+id.toUpperCase().replace(/-/g,'_')+'.md',
 worker_slot:slot,order:null,depends_on:[],blocker:'',updated_on:DAY,
 updated_at_utc:DAY+'T19:00:00Z',recent_completion:false},patch);
const oldA=make('old-completion-a','ЧАТ 1');
const oldB=make('old-completion-b','ЧАТ 2');
const unrelated=make('historic-third-item','ЧАТ 9',{status:'complete',recent_completion:true});
const board='# DIRECTOR TASK BOARD\n\n## ТЕКУЩИЕ НАЗНАЧЕНИЯ — старый список\n\n- старый\n\n## СДАННЫЙ АУДИТ\n\n- исторический блок не меняется\n';
const content=id=>'Repository: kentrap2011-hub/steam-kz-deals-2\nSource of truth: main\nTask ID: '+id+'\nПравила worker-а согласно источнику main.\n';
const section=ids=>'## ТЕКУЩИЕ НАЗНАЧЕНИЯ — новые\n\n'+ids.map(id=>'- '+id+' → '+make(id,'ЧАТ 7').task_file).join('\n')+'\n';
const plan={schema_version:1,contract:'DIRECTOR-FORWARD-TASK-REGISTRY-V1',source_board:'DIRECTOR_TASK_BOARD.md',
 last_curated_on:DAY,maintenance:'Canonical',items:[oldA,oldB,unrelated]};
const task=(id,slot='ЧАТ 7',patch={})=>({item:make(id,slot,patch),content:content(id)});
const transition=id=>({id,expectedStatus:'active',changes:{status:'complete',recent_completion:true,
 blocker:'Сдано для независимой проверки',updated_on:DAY,updated_at_utc:DAY+'T19:00:00Z'}});
const base=(records=[task('fresh-task-one')],more={})=>Object.assign({
 baseSha:SHA,currentMainSha:SHA,branch:'register/fresh-task-batch',plan,board,
 registrations:records,authorizedSlots:records.map(t=>t.item.worker_slot),
 boardSection:section(records.map(t=>t.item.id)),transitions:[],authorizedTransitionIds:[],curatedOn:DAY
},more);
const expectFail=(req,terms)=>{const r=prepare(req);assert.equal(r.ok,false);const msg=r.errors.join('\n');
 for(const term of terms)assert.match(msg,new RegExp(term),msg);return r;};
let result=prepare(base());
assert.equal(result.ok,true,result.errors.join('; '));
assert.deepEqual(result.writePaths.sort(),['DIRECTOR_TASK_BOARD.md','WORKER_TASK_FRESH_TASK_ONE.md','config/director_task_plan.json'].sort());
assert.match(result.files['DIRECTOR_TASK_BOARD.md'],/## СДАННЫЙ АУДИТ\n\n- исторический блок не меняется/);
assert.deepEqual(JSON.parse(result.files['config/director_task_plan.json']).items.slice(0,3),plan.items);
const pair=[task('fresh-task-one','ЧАТ 7'),task('fresh-task-two','ЧАТ 8',{depends_on:['fresh-task-one']})];
result=prepare(base(pair,{transitions:[transition(oldA.id),transition(oldB.id)],
 authorizedTransitionIds:[oldA.id,oldB.id]}));
assert.equal(result.ok,true,result.errors.join('; '));
const rows=JSON.parse(result.files['config/director_task_plan.json']).items;
assert.deepEqual(rows.find(t=>t.id===unrelated.id),unrelated);
assert.equal(rows.find(t=>t.id===oldA.id).status,'complete');
assert.equal(rows.find(t=>t.id===oldB.id).status,'complete');
// #338: both different defects MUST be reported in one preflight, without any write.
const wrong=[task('fresh-task-one','ЧАТ 7',{effort:'малая',blocker:'PR #338'}),
 task('fresh-task-two','ЧАТ 8',{effort:'малая',urgency_reason:'PR #338'})];
expectFail(base(wrong,{transitions:[transition(oldA.id),transition(oldB.id)],
 authorizedTransitionIds:[oldA.id,oldB.id]}),['invalid effort','forbidden public blocker','forbidden public urgency_reason']);
// #317: unauthorized older transitions and old public PR # must fail before publication.
expectFail(base([task('fresh-task-one','ЧАТ 7',{goal:'PR #311'})],
 {transitions:[transition(oldA.id),transition(oldB.id)]}),['forbidden public goal','UNAUTHORIZED existing ID transition']);
for(const [change,reason] of [
 [r=>{r.registrations[0].item.id='BAD_ID';},'invalid ID'],
 [r=>{r.registrations[0].item.task_file='WORKER_TASK_DIFFERENT.md';},'mismatched ID/file'],
 [r=>{r.registrations[0].item.goal='https://private.example';},'forbidden public goal'],
 [r=>{r.registrations[0].item.blocker='api_key=super-secret';},'forbidden public blocker'],
 [r=>{r.registrations[0].item.worker_slot='ЧАТ 0';},'invalid worker_slot'],
 [r=>{r.registrations[0].item.depends_on=['no-such-task'];},'Unknown dependency'],
 [r=>{r.registrations[0].item.updated_at_utc='2026-10-27T19:00:00Z';},'UTC timestamp'],
 [r=>{r.currentMainSha='b'.repeat(40);},'EXACT_BASE_MISMATCH'],
 [r=>{r.registrations[0].content+='\\ngithub_pat_ABCDEFGHIJKLMNOPQRSTUVWXYZ012345';},'secret in task content']
]){const r=base();change(r);expectFail(r,[reason]);}
function mock(req,mainSeq){
 let writes=0,gets=0;
 const repoObj={result:{content:JSON.stringify({object:{sha:SHA}})}};
 const tools={
  mcp__GitHub__fetch:async ({url})=>{
    if(url.endsWith('/git/ref/heads/main')){const ref=mainSeq[Math.min(gets++,mainSeq.length-1)];return {result:{content:JSON.stringify({object:{sha:ref}})}};}
    if(url.includes('/git/commits/'))return {result:{content:JSON.stringify({tree:{sha:'c'.repeat(40)}})}};
    if(url.includes('/git/ref/heads/'))throw Error('NOT_FOUND 404');
    return repoObj;
  },
  mcp__GitHub__fetch_file:async ({path})=>{
   if(path==='config/director_task_plan.json')return {result:{content:JSON.stringify(plan)}};
   if(path==='DIRECTOR_TASK_BOARD.md')return {result:{content:board}};
   throw Error('NOT_FOUND 404');
  },
  mcp__GitHub__create_tree:async()=>{writes++;return {result:{sha:'d'.repeat(40)}};},
  mcp__GitHub__create_commit:async()=>{writes++;return {result:{sha:'e'.repeat(40)}};},
  mcp__GitHub__create_branch:async()=>{writes++;return {result:{branch:req.branch}};}
 };
 return {tools,getWrites:()=>writes};
}
(async()=>{
 let bad=base(wrong,{transitions:[transition(oldA.id),transition(oldB.id)],authorizedTransitionIds:[oldA.id,oldB.id]});
 let m=mock(bad,[SHA,SHA,SHA]);let v=await publish(m.tools,bad);assert.equal(v.ok,false);assert.equal(m.getWrites(),0);
 bad=base([task('fresh-task-one','ЧАТ 7',{goal:'PR #311'})],{transitions:[transition(oldA.id)]});
 m=mock(bad,[SHA,SHA,SHA]);v=await publish(m.tools,bad);assert.equal(v.ok,false);assert.equal(m.getWrites(),0);
 m=mock(base(),[SHA,SHA,'b'.repeat(40)]);v=await publish(m.tools,base());assert.equal(v.ok,false);assert.equal(m.getWrites(),0);
 m=mock(base(),[SHA,SHA,SHA]);v=await publish(m.tools,base(),{dryRun:true});assert.equal(v.ok,true);assert.equal(m.getWrites(),0);
 m=mock(base(),[SHA,SHA,SHA]);v=await publish(m.tools,base());assert.equal(v.ok,true);assert.equal(m.getWrites(),3);
 console.log('DIRECTOR_REGISTER_PREWRITE_TESTS=PASS');
})().catch(e=>{console.error(e);process.exitCode=1;});
