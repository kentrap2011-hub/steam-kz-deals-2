#!/usr/bin/env python3
"""Phase 2A deterministic Director control plane. No real dispatch is implemented."""
from __future__ import annotations
import argparse, copy, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

HEX40=re.compile(r'^[0-9a-f]{40}$')
ALLOWED_WORKER_MODES={'READ_ONLY_RECON','AUDIT'}

class OrchestrationError(ValueError): pass

def req(ok: bool, msg: str) -> None:
    if not ok: raise OrchestrationError(msg)

def load_json(path: Path) -> dict[str,Any]:
    try: value=json.loads(path.read_text(encoding='utf-8'))
    except (OSError,json.JSONDecodeError) as exc: raise OrchestrationError(f'invalid JSON {path}: {exc}') from exc
    req(isinstance(value,dict),f'{path} must be object'); return value

def canonical_digest(value: dict[str,Any]) -> str:
    raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()

def parse_time(value: str) -> datetime:
    try: dt=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError as exc: raise OrchestrationError(f'invalid UTC timestamp {value!r}') from exc
    req(dt.tzinfo is not None,'timestamp must have timezone'); return dt.astimezone(timezone.utc)

def attempt_id(task_id: str, revision: int, number: int) -> str:
    return f'{task_id}:r{revision}:a{number}'

def validate_contract(contract: dict[str,Any]) -> None:
    req(contract.get('phase')=='2A','Phase 2A contract required')
    req(contract.get('dispatch_enabled') is False,'dispatch must remain disabled in Phase 2A')
    req(contract.get('state_persistence_enabled') is False,'state persistence must remain disabled in Phase 2A')
    req(contract.get('limits',{}).get('max_logical_slots')==2,'exactly two logical slots required')
    worker=contract.get('worker',{})
    req(set(worker.get('allowed_modes',[]))==ALLOWED_WORKER_MODES,'worker modes must be READ_ONLY_RECON/AUDIT only')
    for k in ('github_write_credential','repository_write_authority','state_write_authority','product_write_authority'):
        req(worker.get(k) is False,f'worker.{k} must be false')
    auth=contract.get('authority',{})
    req(auth.get('single_state_writer')=='scripts/director_orchestration_controller.py','single writer mismatch')
    req(auth.get('second_state_writer_allowed') is False,'second state writer forbidden')

def load_intakes(root: Path) -> dict[str,dict[str,Any]]:
    events={}
    for p in sorted((root/'orchestration/intake').glob('*.json')):
        e=load_json(p); eid=e.get('event_id')
        req(isinstance(eid,str) and eid,'intake event_id required')
        req(eid not in events,f'duplicate intake event_id {eid}')
        req(e.get('event_type')=='task_revision_intake','unknown intake event type')
        req(e.get('schema_version')==1,'unknown intake event schema')
        events[eid]=e
    return events

def validate_state(contract: dict[str,Any], state: dict[str,Any], events: dict[str,dict[str,Any]]) -> None:
    validate_contract(contract)
    req(state.get('schema_version')==contract.get('state_schema_version') and state.get('security_boundary_schema_version')==contract.get('security_boundary_schema_version'),'unknown/malformed state schema')
    req(isinstance(state.get('state_revision'),int) and state['state_revision']>=1,'bad state_revision')
    req(state.get('dispatch_enabled') is False,'state dispatch_enabled must be false')
    req(state.get('authoritative_writer')==contract['authority']['single_state_writer'],'state writer mismatch')
    applied=state.get('applied_intake_events'); req(isinstance(applied,list),'applied_intake_events must be list')
    seen=set()
    for item in applied:
        req(isinstance(item,dict),'applied intake entry must be object')
        eid=item.get('event_id'); req(eid not in seen,'duplicate applied intake event'); seen.add(eid)
        req(eid in events,f'applied intake event missing: {eid}')
        req(item.get('digest_sha256')==canonical_digest(events[eid]),f'changed immutable intake event: {eid}')
    req(set(events)==seen,'unapplied intake event present; controller reconciliation required')
    slots=state.get('slots'); req(isinstance(slots,list) and len(slots)==2,'exactly two slots required')
    req({s.get('slot_id') for s in slots}=={'slot_1','slot_2'},'slot ids malformed')
    tasks=state.get('tasks'); req(isinstance(tasks,list),'tasks must be list')
    by_id={}
    for t in tasks:
        req(isinstance(t,dict),'task must be object'); tid=t.get('task_id'); req(isinstance(tid,str) and tid,'task_id required')
        req(tid not in by_id,f'duplicate task {tid}'); by_id[tid]=t
        for k in ('revision','mode','status','task_file','task_file_blob_sha','base_sha','expected_report','intake_event_id','retry','allowed_result_statuses'): req(k in t,f'task {tid} missing {k}')
        req(isinstance(t['revision'],int) and t['revision']>=1,f'bad revision for {tid}')
        req(bool(HEX40.fullmatch(t['task_file_blob_sha'])),f'bad task blob sha for {tid}')
        req(bool(HEX40.fullmatch(t['base_sha'])),f'bad base sha for {tid}')
        req(t['intake_event_id'] in events,f'unknown intake event for {tid}')
        latest=max((e for e in events.values() if e['task_id']==tid),key=lambda e:e['task_revision'])
        req(t['revision']==latest['task_revision'],f'stale task revision in state for {tid}')
        for field,efield in [('task_file','task_file'),('task_file_blob_sha','task_file_blob_sha'),('base_sha','base_sha'),('expected_report','expected_report_path'),('mode','mode')]: req(t[field]==latest[efield],f'task {tid} latest intake binding mismatch: {field}')
        req(t['allowed_result_statuses']==latest['allowed_result_statuses'],f'task {tid} result statuses mismatch')
        retry=t['retry']; req(isinstance(retry,dict) and retry.get('max_attempts')==contract['limits']['max_attempts_per_revision'],f'bad retry policy {tid}')
        req(isinstance(retry.get('next_attempt_number'),int) and retry['next_attempt_number']>=1,f'bad next attempt {tid}')
        an=t.get('attempt_number'); aid=t.get('attempt_id'); req(isinstance(an,int) and an>=0,f'bad attempt number {tid}')
        if an==0: req(aid is None,f'queued task {tid} cannot have attempt_id')
        else: req(aid==attempt_id(tid,t['revision'],an),f'attempt id mismatch {tid}')
        for dep in t.get('dependencies',[]): req(dep in by_id or any(x.get('task_id')==dep for x in tasks),f'missing dependency {dep}')
    assigned={}
    for s in slots:
        req(s.get('status') in {'free','occupied'},'invalid slot status')
        if s['status']=='free':
            req(s.get('occupancy_type') is None and s.get('task_id') is None and s.get('lease') is None,'free slot carries occupancy/lease'); req(s.get('conflict_keys')==[],'free slot carries conflict keys'); continue
        tid=s.get('task_id'); req(tid in by_id,'occupied slot task missing'); req(tid not in assigned,'task occupies multiple slots'); assigned[tid]=s['slot_id']
        req(s.get('occupancy_type') in {'external_manual','cloud_worker'},'invalid occupancy type'); lease=s.get('lease'); req(isinstance(lease,dict),'occupied slot lease required'); t=by_id[tid]
        req(t.get('assigned_slot')==s['slot_id'],'slot/task assignment mismatch')
        req(lease.get('task_id')==tid and lease.get('task_revision')==t['revision'],'stale task revision cannot retain lease')
        req(lease.get('attempt_id')==t['attempt_id'],'stale attempt cannot retain lease'); req(lease.get('state_revision_acquired')<=state['state_revision'],'lease state revision from future')
        if s['occupancy_type']=='cloud_worker':
            req(lease.get('status')=='active','cloud lease must be active'); req(isinstance(lease.get('expires_at'),str),'cloud lease expiry required'); req(t['mode'] in ALLOWED_WORKER_MODES,'cloud lease on forbidden mode')
        else: req(lease.get('status')=='active_external_manual','manual lease status invalid')
    for t in tasks:
        if t.get('assigned_slot') is not None: req(assigned.get(t['task_id'])==t['assigned_slot'],'assigned task lacks matching occupied slot')

def verify_repository_bindings(root: Path, state: dict[str,Any]) -> None:
    for t in state['tasks']:
        p=root/t['task_file']; req(p.is_file(),f"task file missing: {t['task_file']}")
        req(git_blob_sha(p.read_bytes())==t['task_file_blob_sha'],f"current task file changed without revision: {t['task_id']}")
        try: base_blob=subprocess.check_output(['git','rev-parse',f"{t['base_sha']}:{t['task_file']}"],cwd=root,text=True,stderr=subprocess.STDOUT).strip()
        except subprocess.CalledProcessError as exc: raise OrchestrationError(f"cannot resolve base binding for {t['task_id']}: {exc.output.strip()}") from exc
        req(base_blob==t['task_file_blob_sha'],f"base SHA/task blob binding mismatch: {t['task_id']}")

def _eligible(contract,state,t):
    if t['status']!='queued' or t['mode'] not in ALLOWED_WORKER_MODES: return False
    if t.get('user_gate') not in {'none','resolved'} or t.get('review_gate') not in {'none','not_applicable','clear'}: return False
    by={x['task_id']:x for x in state['tasks']}
    if any(by[d]['status']!='accepted' for d in t.get('dependencies',[])): return False
    active={k for s in state['slots'] if s['status']=='occupied' for k in s.get('conflict_keys',[])}
    return not (set(t.get('conflict_keys',[])) & active)

def choose_task(contract,state):
    weights={'VERY_HIGH':400,'HIGH':300,'NORMAL':200,'LOW':100}; candidates=[t for t in state['tasks'] if _eligible(contract,state,t)]; candidates.sort(key=lambda t:(-weights[t['priority']],t['queue_sequence'],t['task_id'])); return candidates[0] if candidates else None

def acquire_cloud_lease(contract,state,task_id:str,requested_revision:int,now:datetime):
    st=copy.deepcopy(state); by={t['task_id']:t for t in st['tasks']}; req(task_id in by,'unknown task'); t=by[task_id]
    req(requested_revision==t['revision'],'stale task revision cannot acquire lease'); req(t['mode'] in ALLOWED_WORKER_MODES,'IMPLEMENT/unknown mode cannot acquire cloud lease'); req(t['status']=='queued','task must be queued')
    free=next((s for s in st['slots'] if s['status']=='free'),None); req(free is not None,'no logical slot available'); n=t['retry']['next_attempt_number']; req(n<=t['retry']['max_attempts'],'retry budget exhausted')
    aid=attempt_id(task_id,t['revision'],n); new_rev=st['state_revision']+1; expires=now+timedelta(seconds=contract['limits']['cloud_lease_seconds']); lid=f"{free['slot_id']}:{aid}"
    t['attempt_number']=n; t['attempt_id']=aid; t['status']='assigned'; t['assigned_slot']=free['slot_id']; t['retry']['next_attempt_number']=n+1
    free.update({'status':'occupied','occupancy_type':'cloud_worker','task_id':task_id,'task_file':t['task_file'],'conflict_keys':list(t['conflict_keys']),'lease':{'lease_id':lid,'owner':'director-controller','status':'active','task_id':task_id,'task_revision':t['revision'],'attempt_id':aid,'acquired_at':now.isoformat().replace('+00:00','Z'),'expires_at':expires.isoformat().replace('+00:00','Z'),'state_revision_acquired':new_rev}}); st['state_revision']=new_rev
    request={'schema_version':1,'task_id':task_id,'task_revision':t['revision'],'attempt_number':n,'attempt_id':aid,'lease_id':lid,'lease_expires_at':free['lease']['expires_at'],'mode':t['mode'],'task_file':t['task_file'],'task_file_blob_sha':t['task_file_blob_sha'],'base_sha':t['base_sha'],'allowed_input_refs':list(t['allowed_input_refs']),'expected_report_path':t['expected_report'],'allowed_result_statuses':list(t['allowed_result_statuses']),'repository_write_authority':False,'github_write_credential':False,'state_write_authority':False,'product_write_authority':False,'worker_can_choose_next_task':False,'secret_values':[]}; validate_worker_request(request); return st,request

def validate_worker_request(r):
    req(r.get('schema_version')==1,'worker request schema'); req(r.get('mode') in ALLOWED_WORKER_MODES,'worker mode forbidden'); req(isinstance(r.get('task_revision'),int) and r['task_revision']>=1,'bad request revision')
    req(r.get('attempt_id')==attempt_id(r.get('task_id',''),r['task_revision'],r.get('attempt_number',0)),'request attempt binding mismatch'); req(bool(HEX40.fullmatch(r.get('task_file_blob_sha',''))),'request task blob sha invalid'); req(bool(HEX40.fullmatch(r.get('base_sha',''))),'request base sha invalid')
    req(isinstance(r.get('expected_report_path'),str) and r['expected_report_path'].startswith('reviews/worker_reports/'),'request report path invalid')
    for k in ('repository_write_authority','github_write_credential','state_write_authority','product_write_authority','worker_can_choose_next_task'): req(r.get(k) is False,f'worker authority {k} must be false')
    req(r.get('secret_values')==[],'worker request cannot carry secret values')

def staging_plan(contract,state,now):
    req(contract['dispatch_enabled'] is False and state['dispatch_enabled'] is False,'dispatch unexpectedly enabled'); task=choose_task(contract,state); free=next((s for s in state['slots'] if s['status']=='free'),None); candidate=None
    if task and free:
        n=task['retry']['next_attempt_number']; candidate={'task_id':task['task_id'],'task_revision':task['revision'],'proposed_attempt_id':attempt_id(task['task_id'],task['revision'],n),'proposed_slot':free['slot_id'],'task_file':task['task_file'],'task_file_blob_sha':task['task_file_blob_sha'],'base_sha':task['base_sha'],'expected_report_path':task['expected_report'],'mode':task['mode'],'executable':False}
    return {'schema_version':1,'phase':'2A','dispatch_enabled':False,'dispatch_performed':False,'openai_or_codex_invoked':False,'product_mutation_performed':False,'state_mutation_performed':False,'generated_at_utc':now.isoformat().replace('+00:00','Z'),'candidate':candidate}

def reconcile_expired_leases(contract,state,now):
    st=copy.deepcopy(state); changed=False
    for s in st['slots']:
        if s['status']!='occupied' or s.get('occupancy_type')!='cloud_worker': continue
        lease=s['lease']
        if parse_time(lease['expires_at'])>now: continue
        t=next(t for t in st['tasks'] if t['task_id']==s['task_id']); req(lease['task_revision']==t['revision'] and lease['attempt_id']==t['attempt_id'],'stale lease cannot be reconciled')
        t['status']='queued' if t['retry']['next_attempt_number']<=t['retry']['max_attempts'] else 'blocked'; t['assigned_slot']=None; s.update({'status':'free','occupancy_type':None,'task_id':None,'task_file':None,'conflict_keys':[],'lease':None}); changed=True
    if changed: st['state_revision']+=1
    return st,changed

def persist_state(contract,path:Path,state):
    req(contract.get('state_persistence_enabled') is True,'state persistence disabled; Phase 2A cannot write state'); req(path.as_posix().endswith('orchestration/state.json'),'controller may write only orchestration/state.json'); tmp=path.with_suffix('.json.tmp'); tmp.write_text(json.dumps(state,indent=2,sort_keys=True)+'\n',encoding='utf-8'); os.replace(tmp,path)

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--output',required=True); ap.add_argument('--now'); a=ap.parse_args(argv); root=Path(a.root).resolve()
    try:
        c=load_json(root/'config/director_orchestration_phase2a_contract.json'); s=load_json(root/'orchestration/state.json'); e=load_intakes(root); validate_state(c,s,e); verify_repository_bindings(root,s); now=parse_time(a.now) if a.now else datetime.now(timezone.utc); plan=staging_plan(c,s,now); Path(a.output).write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps(plan,indent=2,sort_keys=True))
    except OrchestrationError as exc: print(f'Phase 2A controller failed closed: {exc}',file=sys.stderr); return 2
    return 0
if __name__=='__main__': raise SystemExit(main())
