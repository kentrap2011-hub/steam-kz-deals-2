#!/usr/bin/env python3
"""Deterministic Director control plane for Phase 2A validation and one bounded Phase 2B pilot."""
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

def validate_phase2b_pilot_contract(contract: dict[str,Any]) -> None:
    req(contract.get('phase')=='2B_LIVE_READONLY_PILOT','Phase 2B pilot contract required')
    req(contract.get('state_persistence_enabled') is True,'Phase 2B pilot must explicitly enable controller state persistence')
    req(contract.get('general_dispatch_enabled') is False,'general dispatch must remain disabled')
    req(contract.get('automatic_next_dispatch') is False,'automatic next dispatch must remain disabled')
    req(contract.get('implement_dispatch_allowed') is False,'IMPLEMENT dispatch must remain disabled')
    req(contract.get('limits',{}).get('max_logical_slots')==2,'exactly two logical slots required')
    req(contract.get('limits',{}).get('max_live_attempts')==1,'live pilot is exactly one logical attempt')
    req(contract.get('limits',{}).get('max_same_attempt_recovery_executions')==2,'pre-model same-attempt recovery must be bounded to two executions')
    worker=contract.get('worker',{})
    req(worker.get('mode')=='READ_ONLY_RECON','pilot worker must be READ_ONLY_RECON')
    for k in ('github_write_credential','repository_write_authority','state_write_authority','product_write_authority','worker_can_choose_next_task'):
        req(worker.get(k) is False,f'pilot worker.{k} must be false')
    req(worker.get('web_search_config')=='web_search="live"','pilot web search config changed')
    req(contract.get('single_state_writer')=='scripts/director_orchestration_controller.py','Phase 2B single writer mismatch')
    pilot=contract.get('pilot',{})
    req(pilot.get('task_id')=='epic-ru-availability-source-probe-01','wrong live pilot task')
    req(pilot.get('task_file')=='WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_01.md','wrong live pilot task file')
    req(pilot.get('expected_report_path')=='reviews/worker_reports/epic-ru-availability-source-probe-01.md','wrong live pilot report')
    req(pilot.get('attempt_number')==1 and pilot.get('attempt_id')=='epic-ru-availability-source-probe-01:r1:a1','wrong live pilot attempt binding')
    req(pilot.get('lease_id')=='slot_2:epic-ru-availability-source-probe-01:r1:a1','wrong live pilot lease binding')
    recovery=contract.get('recovery',{})
    req(recovery.get('allowed') is True,'same-attempt recovery disabled')
    req(recovery.get('initial_reason')=='pre_model_codex_cli_argument_failure','unexpected initial recovery reason')
    req(recovery.get('second_reason')=='pre_model_invalid_output_schema','unexpected second recovery reason')
    req(recovery.get('must_reuse_same_attempt') is True and recovery.get('must_reuse_same_lease_identity') is True,'recovery must reuse attempt/lease')
    req(recovery.get('must_not_increment_retry_counter') is True and recovery.get('must_not_select_another_task') is True,'recovery must not dispatch another attempt/task')
    req(recovery.get('no_recovery_after_model_execution') is True,'recovery after model execution must be forbidden')
    manual=contract.get('manual_occupancy',{})
    req(manual.get('task_id')=='reconsideration-commercial-bridge-and-wishlist-implement-01','wrong current manual task')
    req(manual.get('task_file')=='WORKER_TASK_RECONSIDERATION_COMMERCIAL_BRIDGE_AND_WISHLIST_IMPLEMENT_01.md','wrong current manual task file')
    req(manual.get('completion_report')=='reviews/worker_reports/reconsideration-commercial-bridge-and-wishlist-implement-01.md','wrong manual completion report')

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
    detached_manual_ids=set()
    for s in slots:
        req(s.get('status') in {'free','occupied'},'invalid slot status')
        if s['status']=='free':
            req(s.get('occupancy_type') is None and s.get('task_id') is None and s.get('lease') is None,'free slot carries occupancy/lease'); req(s.get('conflict_keys')==[],'free slot carries conflict keys'); continue
        tid=s.get('task_id'); req(isinstance(tid,str) and tid,'occupied slot task id missing')
        req(tid not in assigned and tid not in detached_manual_ids,'task occupies multiple slots')
        req(s.get('occupancy_type') in {'external_manual','cloud_worker'},'invalid occupancy type')
        lease=s.get('lease'); req(isinstance(lease,dict),'occupied slot lease required')
        req(lease.get('task_id')==tid,'slot/lease task mismatch')
        req(lease.get('state_revision_acquired')<=state['state_revision'],'lease state revision from future')
        if s['occupancy_type']=='cloud_worker':
            req(tid in by_id,'cloud-worker slot task missing from authoritative task state')
            assigned[tid]=s['slot_id']; t=by_id[tid]
            req(t.get('assigned_slot')==s['slot_id'],'slot/task assignment mismatch')
            req(lease.get('task_revision')==t['revision'],'stale task revision cannot retain lease')
            req(lease.get('attempt_id')==t['attempt_id'],'stale attempt cannot retain lease')
            req(lease.get('status')=='active','cloud lease must be active')
            req(isinstance(lease.get('expires_at'),str),'cloud lease expiry required')
            req(t['mode'] in ALLOWED_WORKER_MODES,'cloud lease on forbidden mode')
        else:
            req(lease.get('status')=='active_external_manual','manual lease status invalid')
            req(lease.get('expires_at') is None,'manual external lease must not invent an expiry')
            if tid in by_id:
                assigned[tid]=s['slot_id']; t=by_id[tid]
                req(t.get('assigned_slot')==s['slot_id'],'slot/task assignment mismatch')
                req(lease.get('task_revision')==t['revision'],'manual task revision mismatch')
                req(lease.get('attempt_id')==t['attempt_id'],'manual task attempt mismatch')
            else:
                detached_manual_ids.add(tid)
                req(isinstance(lease.get('task_revision'),int) and lease['task_revision']>=1,'manual external task revision required')
                req(isinstance(lease.get('attempt_id'),str) and lease['attempt_id'],'manual external attempt id required')
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

def reconcile_phase2b_manual_occupancy(state:dict[str,Any], contract:dict[str,Any], now:datetime) -> dict[str,Any]:
    validate_phase2b_pilot_contract(contract)
    st=copy.deepcopy(state)
    req(len(st.get('slots',[]))==2,'exactly two slots required before reconciliation')
    slot=next((s for s in st['slots'] if s.get('slot_id')==contract['manual_occupancy']['slot_id']),None)
    req(slot is not None,'configured manual slot missing')
    current=contract['manual_occupancy']
    if slot.get('occupancy_type')=='external_manual' and slot.get('task_id')==current['task_id']:
        return st
    req(slot.get('occupancy_type')=='external_manual','manual slot is not externally occupied')
    req(slot.get('task_id')==current['replaces_task_id'],'manual occupancy is ambiguous; refusing reconciliation')
    old=next((t for t in st['tasks'] if t['task_id']==current['replaces_task_id']),None)
    req(old is not None and old.get('assigned_slot')==slot['slot_id'],'stale manual task binding not found')
    old['assigned_slot']=None; old['status']='accepted'
    new_rev=st['state_revision']+1
    aid=f"{current['task_id']}:r{current['task_revision']}:a1"
    slot.update({'status':'occupied','occupancy_type':'external_manual','task_id':current['task_id'],'task_file':current['task_file'],'conflict_keys':list(current['conflict_keys']),'lease':{'lease_id':f"{slot['slot_id']}:{aid}",'owner':'external_manual:chat_1','status':'active_external_manual','task_id':current['task_id'],'task_revision':current['task_revision'],'attempt_id':aid,'acquired_at':now.isoformat().replace('+00:00','Z'),'expires_at':None,'state_revision_acquired':new_rev}})
    st['state_revision']=new_rev; st['source_refs']['active_manual_task']=current['task_file']
    return st

def prepare_phase2b_live_pilot(root:Path, phase2a:dict[str,Any], phase2b:dict[str,Any], state:dict[str,Any], events:dict[str,dict[str,Any]], now:datetime):
    validate_phase2b_pilot_contract(phase2b); validate_state(phase2a,state,events); verify_repository_bindings(root,state)
    st=reconcile_phase2b_manual_occupancy(state,phase2b,now); validate_state(phase2a,st,events); pilot=phase2b['pilot']
    task=next((t for t in st['tasks'] if t['task_id']==pilot['task_id']),None); req(task is not None,'pilot task missing')
    req(task['mode']=='READ_ONLY_RECON','pilot mode changed'); req(task['status']=='queued' and task['attempt_number']==0 and task['attempt_id'] is None,'pilot already attempted or not queued; second live attempt forbidden')
    req(task['retry']['next_attempt_number']==1,'pilot retry counter is not at first attempt'); req(task['revision']==pilot['task_revision'],'pilot revision changed')
    for field,expected in [('task_file',pilot['task_file']),('task_file_blob_sha',pilot['task_file_blob_sha']),('base_sha',pilot['base_sha']),('expected_report',pilot['expected_report_path'])]: req(task[field]==expected,f'pilot binding changed: {field}')
    req(sum(1 for s in st['slots'] if s['status']=='free')==1,'expected exactly one free slot after manual reconciliation')
    lease_contract={'limits':{'cloud_lease_seconds':phase2b['limits']['cloud_lease_seconds']}}; leased,request=acquire_cloud_lease(lease_contract,st,pilot['task_id'],pilot['task_revision'],now)
    req(request['attempt_number']==1,'pilot must use exactly attempt 1'); req(request['mode']=='READ_ONLY_RECON','pilot request mode changed'); req(request['expected_report_path']==pilot['expected_report_path'],'pilot request report path changed')
    req(len(leased['slots'])==2,'slot count changed'); manual=next(s for s in leased['slots'] if s['slot_id']==phase2b['manual_occupancy']['slot_id']); cloud=next(s for s in leased['slots'] if s.get('occupancy_type')=='cloud_worker')
    req(manual.get('task_id')==phase2b['manual_occupancy']['task_id'],'current manual occupancy lost'); req(cloud.get('task_id')==pilot['task_id'],'wrong cloud task leased')
    leased['orchestration_phase']='phase_2b_live_readonly_pilot_attempt_1'; leased['dispatch_enabled']=False; validate_state(phase2a,leased,events); return leased,request

def _manual_completion_is_durable(root:Path, phase2b:dict[str,Any]) -> bool:
    report=root/phase2b['manual_occupancy']['completion_report']
    if not report.is_file(): return False
    head=report.read_text(encoding='utf-8')[:4000]
    return re.search(r'(?m)^## 1\. Status\s*\n+\s*`complete`\s*$',head) is not None

def _same_attempt_request(task:dict[str,Any], lease:dict[str,Any]) -> dict[str,Any]:
    r={'schema_version':1,'task_id':task['task_id'],'task_revision':task['revision'],'attempt_number':task['attempt_number'],'attempt_id':task['attempt_id'],'lease_id':lease['lease_id'],'lease_expires_at':lease['expires_at'],'mode':task['mode'],'task_file':task['task_file'],'task_file_blob_sha':task['task_file_blob_sha'],'base_sha':task['base_sha'],'allowed_input_refs':list(task['allowed_input_refs']),'expected_report_path':task['expected_report'],'allowed_result_statuses':list(task['allowed_result_statuses']),'repository_write_authority':False,'github_write_credential':False,'state_write_authority':False,'product_write_authority':False,'worker_can_choose_next_task':False,'secret_values':[]}
    validate_worker_request(r); return r

def _validate_same_epic_attempt(root:Path, phase2b:dict[str,Any], state:dict[str,Any], now:datetime):
    pilot=phase2b['pilot']; req(not (root/pilot['expected_report_path']).exists(),'worker report already exists; continuation forbidden')
    task=next((t for t in state['tasks'] if t['task_id']==pilot['task_id']),None); req(task is not None,'pilot task missing')
    req(task['mode']=='READ_ONLY_RECON' and task['status']=='assigned','pilot is not the assigned read-only task'); req(task['revision']==pilot['task_revision'],'pilot revision changed')
    req(task['attempt_number']==pilot['attempt_number'] and task['attempt_id']==pilot['attempt_id'],'continuation would change attempt identity'); req(task['retry']['next_attempt_number']==2,'retry counter changed; refusing same-attempt continuation')
    for field,expected in [('task_file',pilot['task_file']),('task_file_blob_sha',pilot['task_file_blob_sha']),('base_sha',pilot['base_sha']),('expected_report',pilot['expected_report_path'])]: req(task[field]==expected,f'pilot binding changed: {field}')
    slot=next((s for s in state['slots'] if s.get('occupancy_type')=='cloud_worker'),None); req(slot is not None and slot.get('slot_id')=='slot_2' and slot.get('task_id')==pilot['task_id'],'exact pilot cloud slot missing')
    lease=slot['lease']; req(lease.get('lease_id')==pilot['lease_id'],'continuation would change lease identity'); req(lease.get('attempt_id')==pilot['attempt_id'] and lease.get('task_revision')==pilot['task_revision'],'lease binding changed'); req(parse_time(lease['expires_at'])>now,'pilot lease expired before continuation; fail closed')
    return task,slot,lease

def resume_phase2b_live_pilot(root:Path, phase2a:dict[str,Any], phase2b:dict[str,Any], state:dict[str,Any], events:dict[str,dict[str,Any]], now:datetime):
    validate_phase2b_pilot_contract(phase2b); validate_state(phase2a,state,events); verify_repository_bindings(root,state); req(state.get('phase2b_recovery') is None,'first same-attempt recovery already consumed')
    recovery=phase2b['recovery']; task,slot,lease=_validate_same_epic_attempt(root,phase2b,state,now)
    st=copy.deepcopy(state); manual_slot=next(s for s in st['slots'] if s['slot_id']==phase2b['manual_occupancy']['slot_id'])
    if _manual_completion_is_durable(root,phase2b):
        req(manual_slot.get('status') in {'free','occupied'},'manual slot status malformed')
        if manual_slot.get('status')=='occupied':
            req(manual_slot.get('occupancy_type')=='external_manual' and manual_slot.get('task_id')==phase2b['manual_occupancy']['task_id'],'completed manual occupancy is ambiguous'); manual_slot.update({'status':'free','occupancy_type':None,'task_id':None,'task_file':None,'conflict_keys':[],'lease':None})
        st['source_refs'].pop('active_manual_task',None); st['source_refs']['completed_manual_task_report']=phase2b['manual_occupancy']['completion_report']
    else: req(manual_slot.get('occupancy_type')=='external_manual' and manual_slot.get('task_id')==phase2b['manual_occupancy']['task_id'],'current manual task not durably complete and occupancy missing')
    new_rev=st['state_revision']+1; cloud=next(s for s in st['slots'] if s.get('occupancy_type')=='cloud_worker'); cloud['lease']['resumed_at']=now.isoformat().replace('+00:00','Z'); cloud['lease']['expires_at']=(now+timedelta(seconds=phase2b['limits']['cloud_lease_seconds'])).isoformat().replace('+00:00','Z'); cloud['lease']['state_revision_acquired']=new_rev
    st['state_revision']=new_rev; st['phase2b_recovery']={'resume_count':1,'reason':recovery['initial_reason'],'attempt_id':phase2b['pilot']['attempt_id'],'lease_id':phase2b['pilot']['lease_id'],'resumed_at':cloud['lease']['resumed_at']}; st['orchestration_phase']='phase_2b_live_readonly_pilot_attempt_1_recovery'; st['dispatch_enabled']=False
    request=_same_attempt_request(next(t for t in st['tasks'] if t['task_id']==phase2b['pilot']['task_id']),cloud['lease']); validate_state(phase2a,st,events); return st,request

def continue_phase2b_live_pilot(root:Path, phase2a:dict[str,Any], phase2b:dict[str,Any], state:dict[str,Any], events:dict[str,dict[str,Any]], now:datetime):
    """One final pre-model continuation for the same r1:a1 after the server rejected only the output schema."""
    validate_phase2b_pilot_contract(phase2b); validate_state(phase2a,state,events); verify_repository_bindings(root,state)
    recovery=phase2b['recovery']; marker=state.get('phase2b_recovery'); req(isinstance(marker,dict),'first recovery state missing')
    req(marker.get('resume_count')==1,'second pre-model continuation already consumed or malformed'); req(marker.get('reason')==recovery['initial_reason'],'unexpected first recovery reason'); req(marker.get('attempt_id')==phase2b['pilot']['attempt_id'] and marker.get('lease_id')==phase2b['pilot']['lease_id'],'first recovery identity changed')
    task,slot,lease=_validate_same_epic_attempt(root,phase2b,state,now); st=copy.deepcopy(state); new_rev=st['state_revision']+1; cloud=next(s for s in st['slots'] if s.get('occupancy_type')=='cloud_worker')
    continued_at=now.isoformat().replace('+00:00','Z'); cloud['lease']['continued_at']=continued_at; cloud['lease']['expires_at']=(now+timedelta(seconds=phase2b['limits']['cloud_lease_seconds'])).isoformat().replace('+00:00','Z'); cloud['lease']['state_revision_acquired']=new_rev
    st['state_revision']=new_rev; st['phase2b_recovery']['resume_count']=2; st['phase2b_recovery']['second_reason']=recovery['second_reason']; st['phase2b_recovery']['continued_at']=continued_at; st['orchestration_phase']='phase_2b_live_readonly_pilot_attempt_1_schema_continuation'; st['dispatch_enabled']=False
    request=_same_attempt_request(next(t for t in st['tasks'] if t['task_id']==phase2b['pilot']['task_id']),cloud['lease']); validate_state(phase2a,st,events); return st,request

def persist_state(contract,path:Path,state):
    req(contract.get('state_persistence_enabled') is True,'state persistence disabled; Phase 2A cannot write state'); req(path.as_posix().endswith('orchestration/state.json'),'controller may write only orchestration/state.json'); tmp=path.with_suffix('.json.tmp'); tmp.write_text(json.dumps(state,indent=2,sort_keys=True)+'\n',encoding='utf-8'); os.replace(tmp,path)

def current_git_head(root:Path) -> str:
    try: value=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True,stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as exc: raise OrchestrationError(f'cannot resolve current git head: {exc.output.strip()}') from exc
    req(bool(HEX40.fullmatch(value)),'current git head malformed'); return value

def validate_expected_head(expected_head:str,current_head:str) -> None:
    req(bool(HEX40.fullmatch(expected_head)) and bool(HEX40.fullmatch(current_head)),'expected/current head malformed'); req(expected_head==current_head,'concurrent repository head advance; fail closed')

def validate_expected_state_revision(expected_revision:int,current_revision:int) -> None:
    req(isinstance(expected_revision,int) and expected_revision>=1,'expected state revision invalid'); req(isinstance(current_revision,int) and current_revision>=1,'current state revision invalid'); req(expected_revision==current_revision,'concurrent authoritative state revision advance; fail closed')

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--output',required=True); ap.add_argument('--now'); ap.add_argument('--phase2b-live-pilot',action='store_true'); ap.add_argument('--phase2b-resume-pilot',action='store_true'); ap.add_argument('--phase2b-continue-pilot',action='store_true'); ap.add_argument('--expected-head'); a=ap.parse_args(argv); root=Path(a.root).resolve()
    try:
        req(sum(bool(x) for x in (a.phase2b_live_pilot,a.phase2b_resume_pilot,a.phase2b_continue_pilot))<=1,'choose only one Phase 2B operation')
        phase2a=load_json(root/'config/director_orchestration_phase2a_contract.json'); state=load_json(root/'orchestration/state.json'); events=load_intakes(root); now=parse_time(a.now) if a.now else datetime.now(timezone.utc)
        if a.phase2b_live_pilot or a.phase2b_resume_pilot or a.phase2b_continue_pilot:
            phase2b=load_json(root/'config/director_orchestration_phase2b_pilot_contract.json'); validate_phase2b_pilot_contract(phase2b)
            if a.expected_head: validate_expected_head(a.expected_head,current_git_head(root))
            if a.phase2b_continue_pilot: next_state,request=continue_phase2b_live_pilot(root,phase2a,phase2b,state,events,now); dispatch_scope='exact_epic_pilot_same_attempt_schema_continuation_only'
            elif a.phase2b_resume_pilot: next_state,request=resume_phase2b_live_pilot(root,phase2a,phase2b,state,events,now); dispatch_scope='exact_epic_pilot_same_attempt_recovery_only'
            else: next_state,request=prepare_phase2b_live_pilot(root,phase2a,phase2b,state,events,now); dispatch_scope='exact_epic_pilot_only'
            persist_state(phase2b,root/'orchestration/state.json',next_state); payload={'schema_version':1,'phase':'2B_LIVE_READONLY_PILOT','dispatch_scope':dispatch_scope,'automatic_next_dispatch':False,'state_revision':next_state['state_revision'],'request':request}; Path(a.output).write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps(payload,indent=2,sort_keys=True))
        else:
            validate_state(phase2a,state,events); verify_repository_bindings(root,state); plan=staging_plan(phase2a,state,now); Path(a.output).write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n',encoding='utf-8'); print(json.dumps(plan,indent=2,sort_keys=True))
    except OrchestrationError as exc:
        label='Phase 2B pilot controller' if (a.phase2b_live_pilot or a.phase2b_resume_pilot or a.phase2b_continue_pilot) else 'Phase 2A controller'; print(f'{label} failed closed: {exc}',file=sys.stderr); return 2
    return 0
if __name__=='__main__': raise SystemExit(main())
