'use strict';
// Director REGISTER gate: pure, exhaustive preflight before ANY GitHub write.
// For functions.exec: fetch and verify this exact source from GitHub, then
// evaluate with Function('module', source + ';return module.exports;')({exports:{}}).
// It is NOT a native import and must not be represented as such.
const REPO='kentrap2011-hub/steam-kz-deals-2';
const PLAN='config/director_task_plan.json',BOARD='DIRECTOR_TASK_BOARD.md';
const FIELDS=['id','title','goal','status','effort','effort_reason','urgency','urgency_reason','task_file','worker_slot','order','depends_on','blocker','updated_on','updated_at_utc','recent_completion'];
const PUBLIC=['id','title','goal','status','worker_slot','order','depends_on','blocker','effort','effort_reason','urgency','urgency_reason','updated_on','updated_at_utc'];
const STATUSES=['active','planned','blocked','complete'],EFFORT=['низкая','средняя','высокая'],URGENCY=['критическая','высокая','обычная','низкая'];
const UNSAFE=/https?:\/\/|[\w.+-]+@[\w.-]+\.[a-z]{2,}|api[_ -]?key|access[_ -]?token|private[_ -]?url|PR\s*#/i;
const SECRET=/(?:gh[pousr]_[A-Za-z0-9_]{12,}|github_pat_[A-Za-z0-9_]{12,}|sk-[A-Za-z0-9]{16,}|BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY|(?:api[_ -]?key|access[_ -]?token)\s*[:=]\s*['"]?\S{12,})/i;
const ID=/^[a-z0-9-]{3,64}$/,FILE=/^WORKER_TASK_[A-Z0-9_]+\.md$/,SLOT=/^ЧАТ [1-9]\d*$/;
const SHA=/^[0-9a-f]{40}$/,BRANCH=/^register\/[a-z0-9][a-z0-9-]{2,75}$/,UTC=/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z$/;
const obj=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
const cp=x=>JSON.parse(JSON.stringify(x));
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function itemCheck(x,where,e){
  if(!obj(x)){e.push(where+': item not object');return;}
  if(!eq(Object.keys(x).sort(),[...FIELDS].sort()))e.push(where+': wrong field set');
  if(typeof x.id!=='string'||!ID.test(x.id))e.push(where+': invalid ID');
  if(!STATUSES.includes(x.status))e.push(where+': invalid status');
  if(!EFFORT.includes(x.effort))e.push(where+': invalid effort ('+EFFORT.join(', ')+')');
  if(!URGENCY.includes(x.urgency))e.push(where+': invalid urgency');
  for(const k of PUBLIC){
    const v=x[k];
    if(['title','goal','effort_reason','urgency_reason'].includes(k)&&
       (typeof v!=='string'||!v.trim()||v.length>500))e.push(where+': invalid public '+k);
    if(['blocker','worker_slot'].includes(k)&&!(k==='worker_slot'&&v===null)&&
       (typeof v!=='string'||v.length>300))e.push(where+': invalid public '+k);
    if(typeof v==='string'&&UNSAFE.test(v))e.push(where+': forbidden public '+k+' (URL/secret/PR #)');
  }
  if(x.worker_slot!==null&&(typeof x.worker_slot!=='string'||!SLOT.test(x.worker_slot)))e.push(where+': invalid worker_slot');
  if(typeof x.task_file!=='string'||!FILE.test(x.task_file))e.push(where+': invalid task_file');
  if(!Array.isArray(x.depends_on)||x.depends_on.some(d=>typeof d!=='string'||!ID.test(d))||
     new Set(x.depends_on).size!==x.depends_on.length)e.push(where+': invalid dependencies');
  if(x.order!==null&&(!obj(x.order)||!eq(Object.keys(x.order).sort(),['position','track'])||
     typeof x.order.track!=='string'||!x.order.track.trim()||UNSAFE.test(x.order.track)||
     !Number.isInteger(x.order.position)||x.order.position<=0))e.push(where+': invalid order');
  if(typeof x.recent_completion!=='boolean')e.push(where+': invalid recent_completion');
  if(typeof x.updated_on!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(x.updated_on)||
     !Number.isFinite(Date.parse(x.updated_on+'T00:00:00Z')))e.push(where+': invalid updated_on');
  if(typeof x.updated_at_utc!=='string'||!UTC.test(x.updated_at_utc)||
     !Number.isFinite(Date.parse(x.updated_at_utc))||
     new Date(x.updated_at_utc).toISOString().slice(0,10)!==x.updated_on)e.push(where+': invalid UTC timestamp/date');
}
function graphCheck(rows,e){
  const ids=new Map(),files=new Set(),positions=new Set();
  for(const x of rows){
    if(!obj(x)||typeof x.id!=='string'){e.push('Invalid registry item');continue;}
    if(ids.has(x.id))e.push('Duplicate task ID: '+x.id);ids.set(x.id,x);
    if(x.task_file!==null){if(files.has(x.task_file))e.push('Duplicate task file: '+x.task_file);files.add(x.task_file);}
    if(obj(x.order)){const k=JSON.stringify([x.order.track,x.order.position]);if(positions.has(k))e.push('Duplicate task order: '+k);positions.add(k);}
  }
  const done=new Set(),stack=new Set();
  function visit(id){
    if(done.has(id))return;
    if(stack.has(id)){e.push('Dependency cycle: '+id);return;}
    if(!ids.has(id)){e.push('Unknown dependency: '+id);return;}
    stack.add(id);
    const x=ids.get(id);
    for(const dep of Array.isArray(x.depends_on)?x.depends_on:[]) {
      if(dep===id)e.push('Self dependency: '+id);else visit(dep);
    }
    stack.delete(id);done.add(id);
  }
  for(const id of ids.keys())visit(id);
}
function boardParts(board,e){
  if(typeof board!=='string'){e.push('Board must be text');return null;}
  const heads=[...board.matchAll(/^## .+$/gm)];
  if(!heads.length||!/^## ТЕКУЩИЕ НАЗНАЧЕНИЯ(?:\s|$)/.test(heads[0][0])){
    e.push('Board first section must be current assignments');return null;
  }
  const start=heads[0].index,end=heads[1]?heads[1].index:board.length;
  return {before:board.slice(0,start),after:board.slice(end)};
}
function prepare(x){
  const e=[],plan=x&&x.plan;
  if(!x||!SHA.test(x.baseSha||'')||x.currentMainSha!==x.baseSha)e.push('EXACT_BASE_MISMATCH');
  if(!x||!BRANCH.test(x.branch||''))e.push('Invalid registration branch');
  if(!obj(plan)||plan.schema_version!==1||plan.contract!=='DIRECTOR-FORWARD-TASK-REGISTRY-V1'||
     plan.source_board!==BOARD||!Array.isArray(plan.items))e.push('Invalid baseline registry');
  if(!Array.isArray(x?.registrations)||!x.registrations.length||x.registrations.length>10)e.push('Requires 1..10 new registrations');
  if(!Array.isArray(x?.transitions)||!Array.isArray(x?.authorizedTransitionIds))e.push('Explicit transitions and authorizedTransitionIds required');
  if(!Array.isArray(x?.authorizedSlots)||x.authorizedSlots.some(s=>typeof s!=='string'||!SLOT.test(s))||
     new Set(x.authorizedSlots).size!==x.authorizedSlots.length)e.push('Invalid authorizedSlots');
  const bp=boardParts(x?.board,e),section=x?.boardSection;
  if(typeof section!=='string'||!/^## ТЕКУЩИЕ НАЗНАЧЕНИЯ(?:\s|$)/.test(section)||
     (section.match(/^## /gm)||[]).length!==1||section.includes('\0'))e.push('Invalid current Board section');
  const rows=Array.isArray(plan?.items)?cp(plan.items):[];
  const old=new Map(rows.filter(obj).map(v=>[v.id,cp(v)]));
  const ids=new Set(),paths={},slots=new Set();
  for(const v of Array.isArray(x?.registrations)?x.registrations:[]){
    const item=v?.item,content=v?.content,name=obj(item)?String(item.id):'<invalid>';
    itemCheck(item,'new '+name,e);
    if(!obj(item))continue;
    if(old.has(item.id)||ids.has(item.id))e.push('New ID collides: '+name);
    ids.add(item.id);
    if(item.status==='complete')e.push(name+': new task cannot start complete');
    if(item.task_file!=='WORKER_TASK_'+String(item.id).toUpperCase().replace(/-/g,'_')+'.md')e.push(name+': mismatched ID/file');
    if(item.worker_slot===null||!Array.isArray(x.authorizedSlots)||!x.authorizedSlots.includes(item.worker_slot))e.push(name+': slot not explicitly authorized');
    if(slots.has(item.worker_slot))e.push('Duplicate new slot: '+item.worker_slot);
    slots.add(item.worker_slot);
    if(typeof content!=='string'||content.length<90||content.length>100000||
       !content.includes('Task ID: '+item.id)||!content.includes(REPO)||!/\bmain\b/.test(content))e.push(name+': invalid task content binding');
    if(typeof content==='string'&&SECRET.test(content))e.push(name+': secret in task content');
    if(typeof item.task_file==='string'&&FILE.test(item.task_file))paths[item.task_file]=content;
    if(typeof section==='string'&&(!section.includes(item.id)||!section.includes(item.task_file)))e.push('Board missing ID/file: '+name);
    rows.push(cp(item));
  }
  if(Array.isArray(x?.authorizedSlots)&&!eq([...slots].sort(),[...x.authorizedSlots].sort()))e.push('Slot authorization set mismatch');
  const changed=new Set(),auth=Array.isArray(x?.authorizedTransitionIds)?x.authorizedTransitionIds:[];
  if(new Set(auth).size!==auth.length||auth.some(id=>typeof id!=='string'||!ID.test(id)))e.push('Invalid authorizedTransitionIds');
  for(const t of Array.isArray(x?.transitions)?x.transitions:[]){
    const id=t?.id;
    if(typeof id!=='string'||!ID.test(id)||ids.has(id)||!old.has(id)||changed.has(id)){
      e.push('Invalid/duplicate old transition ID: '+String(id));continue;
    }
    changed.add(id);
    if(!auth.includes(id))e.push(id+': UNAUTHORIZED existing ID transition');
    const before=old.get(id),patch=t.changes;
    if(before.status!==t.expectedStatus)e.push(id+': stale transition expectedStatus');
    if(!obj(patch)||Object.keys(patch).some(k=>!['status','blocker','worker_slot','recent_completion','updated_on','updated_at_utc'].includes(k))||
       !['active','planned','blocked'].includes(before.status)||patch.status!=='complete'||patch.recent_completion!==true||
       !Object.hasOwn(patch,'updated_on')||!Object.hasOwn(patch,'updated_at_utc')) {
      e.push(id+': invalid completion transition');continue;
    }
    const pos=rows.findIndex(z=>z.id===id);
    rows[pos]=Object.assign({},before,patch);
    itemCheck(rows[pos],'transition '+id,e);
  }
  if(!eq([...changed].sort(),[...auth].sort()))e.push('Transition authorization set mismatch');
  for(const v of rows)if(old.has(v.id)&&!changed.has(v.id)&&!eq(v,old.get(v.id)))e.push('Unrelated ID changed: '+v.id);
  graphCheck(rows,e);
  if(typeof x?.curatedOn!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(x.curatedOn))e.push('Invalid curatedOn');
  for(const v of rows)if(ids.has(v.id)||changed.has(v.id))if(v.updated_on!==x.curatedOn)e.push(v.id+': UTC curated date mismatch');
  const proposed=obj(plan)?Object.assign({},cp(plan),{items:rows,last_curated_on:x?.curatedOn}):{};
  const newBoard=bp&&typeof section==='string'?bp.before+section.replace(/\s*$/,'\n\n')+bp.after:'';
  const files=Object.assign({},paths,{[PLAN]:JSON.stringify(proposed,null,2)+'\n',[BOARD]:newBoard});
  const expected=[PLAN,BOARD,...Object.keys(paths)].sort();
  if(!eq(Object.keys(files).sort(),expected))e.push('Unexpected write-set');
  return {ok:e.length===0,errors:e,files,writePaths:expected,newIds:[...ids],completedIds:[...changed]};
}
function parsed(res){if(!res?.result||typeof res.result.content!=='string')throw Error('Bad GitHub response');return JSON.parse(res.result.content);}
const missing=e=>/(?:\b404\b|NOT_FOUND)/.test(String(e?.message||e));
async function mainSha(tools){
  return parsed(await tools.mcp__GitHub__fetch({url:'https://api.github.com/repos/'+REPO+'/git/ref/heads/main'})).object.sha;
}
async function publish(tools,req,opts={}){
  const base=req?.baseSha;
  if(!SHA.test(base||''))return {ok:false,errors:['Missing valid pinned base'],writeCalls:0};
  if(await mainSha(tools)!==base)return {ok:false,errors:['EXACT_BASE_MISMATCH before reads'],writeCalls:0};
  const [p,b,c]=await Promise.all([
    tools.mcp__GitHub__fetch_file({repository_full_name:REPO,path:PLAN,ref:base}),
    tools.mcp__GitHub__fetch_file({repository_full_name:REPO,path:BOARD,ref:base}),
    tools.mcp__GitHub__fetch({url:'https://api.github.com/repos/'+REPO+'/git/commits/'+base})
  ]);
  const prepared=prepare(Object.assign({},req,{plan:JSON.parse(p.result.content),board:b.result.content,currentMainSha:await mainSha(tools)}));
  if(!prepared.ok)return {ok:false,errors:prepared.errors,writeCalls:0};
  for(const file of prepared.writePaths.filter(s=>s.startsWith('WORKER_TASK_'))) {
    try{await tools.mcp__GitHub__fetch_file({repository_full_name:REPO,path:file,ref:base});
      return {ok:false,errors:['Task file already exists: '+file],writeCalls:0};
    }catch(ex){if(!missing(ex))throw ex;}
  }
  try{await tools.mcp__GitHub__fetch({url:'https://api.github.com/repos/'+REPO+'/git/ref/heads/'+req.branch});
    return {ok:false,errors:['Branch already exists'],writeCalls:0};
  }catch(ex){if(!missing(ex))throw ex;}
  if(await mainSha(tools)!==base)return {ok:false,errors:['EXACT_BASE_RACE before first write'],writeCalls:0};
  if(opts.dryRun)return {ok:true,errors:[],writeCalls:0,paths:prepared.writePaths};
  const parent=parsed(c);
  if(!SHA.test(parent.tree?.sha||''))throw Error('Cannot verify exact base tree');
  const elements=prepared.writePaths.map(path=>({path,mode:'100644',type:'blob',content:prepared.files[path]}));
  const tree=await tools.mcp__GitHub__create_tree({repository_full_name:REPO,base_tree_sha:parent.tree.sha,tree_elements:elements});
  const commit=await tools.mcp__GitHub__create_commit({repository_full_name:REPO,tree_sha:tree.result.sha,parent_sha:base,message:'Director REGISTER: typed validated atomic batch'});
  await tools.mcp__GitHub__create_branch({repository_full_name:REPO,branch_name:req.branch,sha:commit.result.sha});
  return {ok:true,writeCalls:3,sha:commit.result.sha,branch:req.branch,paths:prepared.writePaths,
    note:'One validated commit. Recheck main, PR exact HEAD and existing CI; no worker launch before merge.'};
}
if(typeof module!=='undefined'&&module.exports)module.exports={prepare,publish};
