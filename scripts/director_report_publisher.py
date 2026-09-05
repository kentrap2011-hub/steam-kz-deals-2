#!/usr/bin/env python3
"""Trusted deterministic publisher boundary for Phase 2 read-only worker reports."""
from __future__ import annotations
import json, re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from director_orchestration_controller import OrchestrationError, ALLOWED_WORKER_MODES, parse_time, req, validate_worker_request

SECRET_PATTERNS=[
    re.compile(r'\b'+re.escape('s'+'k-')+r'[A-Za-z0-9_-]{16,}\b'),
    re.compile(r'\b'+re.escape('github_'+'pat_')+r'[A-Za-z0-9_]{16,}\b'),
    re.compile(r'\b'+re.escape('g'+'hp_')+r'[A-Za-z0-9]{16,}\b'),
    re.compile(r'(?i)'+re.escape('OPENAI'+'_API_KEY')+r'\s*[:=]\s*\S+'),
    re.compile(r'(?i)'+re.escape('STEAM'+'_WEB_API_KEY')+r'\s*[:=]\s*\S+'),
    re.compile(r'(?i)Authorization:\s*Bearer\s+\S+'),
]
def validate_worker_result_shape(result: dict[str,Any]) -> None:
    req(result.get('schema_version')==1,'result schema version')
    req(result.get('mode') in ALLOWED_WORKER_MODES,'result mode forbidden')
    for k in ('task_id','attempt_id','lease_id','task_file','task_file_blob_sha','base_sha','report_path','status','report_content'):
        req(isinstance(result.get(k),str) and result[k],f'result missing {k}')
    req(isinstance(result.get('task_revision'),int) and result['task_revision']>=1,'bad result revision')
    req(isinstance(result.get('attempt_number'),int) and result['attempt_number']>=1,'bad result attempt number')
    req(result.get('requested_repository_mutations')==[],'worker result cannot request repository mutations')
    req(result.get('state_mutation_requested') is False,'worker cannot mutate state')
    req(result.get('product_mutation_requested') is False,'worker cannot mutate product')
    req(result.get('secret_values')==[],'worker result cannot carry secret values')

def _current_task_and_slot(state, request):
    task=next((t for t in state['tasks'] if t['task_id']==request['task_id']),None); req(task is not None,'task no longer exists')
    req(task['revision']==request['task_revision'],'stale result: task revision advanced')
    req(task['attempt_id']==request['attempt_id'] and task['attempt_number']==request['attempt_number'],'stale result: attempt advanced')
    req(task['assigned_slot'] is not None,'stale result: task no longer leased')
    slot=next((s for s in state['slots'] if s['slot_id']==task['assigned_slot']),None); req(slot is not None and slot['status']=='occupied','stale result: slot not occupied')
    lease=slot.get('lease'); req(isinstance(lease,dict),'stale result: lease absent')
    req(slot.get('occupancy_type')=='cloud_worker','worker result only publishable from cloud worker lease')
    req(lease.get('lease_id')==request['lease_id'],'stale result: lease id changed')
    req(lease.get('task_revision')==request['task_revision'] and lease.get('attempt_id')==request['attempt_id'],'stale result: lease binding changed')
    return task,slot

def validate_publication(request:dict[str,Any], result:dict[str,Any], state:dict[str,Any], now:datetime|None=None) -> dict[str,str]:
    validate_worker_request(request); validate_worker_result_shape(result)
    now=now or datetime.now(timezone.utc); task,slot=_current_task_and_slot(state,request)
    lease=slot['lease']; req(parse_time(lease['expires_at'])>now,'stale result: lease expired')
    exact_fields=['task_id','task_revision','attempt_number','attempt_id','lease_id','mode','task_file','task_file_blob_sha','base_sha']
    for field in exact_fields: req(result.get(field)==request.get(field),f'result binding mismatch: {field}')
    req(request['task_file_blob_sha']==task['task_file_blob_sha'],'request task blob no longer current')
    req(request['base_sha']==task['base_sha'],'request base SHA no longer current')
    req(request['expected_report_path']==task['expected_report'],'request expected report no longer current')
    req(result['report_path']==request['expected_report_path'],'publisher refuses wrong report path')
    req(result['status'] in task['allowed_result_statuses'],'result status not allowed for task revision')
    content=result['report_content']; req(len(content.encode('utf-8'))<=200_000,'report too large')
    for pat in SECRET_PATTERNS: req(not pat.search(content),'detectable secret material in report')
    path=Path(result['report_path'])
    req(not path.is_absolute() and '..' not in path.parts,'unsafe report path')
    req(path.parts[:2]==('reviews','worker_reports'),'publisher path must stay under reviews/worker_reports')
    return {'report_path':result['report_path'],'report_content':content,'status':result['status']}

def publish_exact_report(repo_root:Path, publication:dict[str,str]) -> Path:
    target=(repo_root/publication['report_path']).resolve(); allowed=(repo_root/'reviews/worker_reports').resolve()
    req(target.parent==allowed,'publisher can write only an exact direct worker report path')
    target.parent.mkdir(parents=True,exist_ok=True); target.write_text(publication['report_content'],encoding='utf-8')
    return target

def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def main(argv=None):
    import argparse, sys
    ap=argparse.ArgumentParser(); ap.add_argument('--request',required=True); ap.add_argument('--result',required=True); ap.add_argument('--state',default='orchestration/state.json'); ap.add_argument('--repo-root',default='.'); ap.add_argument('--write',action='store_true')
    a=ap.parse_args(argv)
    try:
        request=load(a.request); result=load(a.result); state=load(a.state); publication=validate_publication(request,result,state)
        if a.write:
            target=publish_exact_report(Path(a.repo_root).resolve(),publication); print(target.relative_to(Path(a.repo_root).resolve()))
        else: print(json.dumps({'validated':True,'report_path':publication['report_path'],'status':publication['status']},sort_keys=True))
    except (OrchestrationError,OSError,json.JSONDecodeError) as exc:
        print(f'publisher failed closed: {exc}',file=sys.stderr); return 2
    return 0
if __name__=='__main__': raise SystemExit(main())
