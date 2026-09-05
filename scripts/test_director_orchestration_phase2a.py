#!/usr/bin/env python3
from __future__ import annotations
import copy, json, tempfile, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from director_orchestration_controller import OrchestrationError, acquire_cloud_lease, load_intakes, load_json, staging_plan, validate_state, validate_worker_request
from director_report_publisher import validate_publication, publish_exact_report
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=load_json(ROOT/'config/director_orchestration_phase2a_contract.json')
STATE=load_json(ROOT/'orchestration/state.json')
EVENTS=load_intakes(ROOT)
NOW=datetime(2026,9,5,12,0,0,tzinfo=timezone.utc)

def leased_epic():
    validate_state(CONTRACT,copy.deepcopy(STATE),EVENTS)
    return acquire_cloud_lease(CONTRACT,copy.deepcopy(STATE),'epic-ru-availability-source-probe-01',1,NOW)

def result_for(request,status='blocked',content='# Report\n\nStatus: blocked\n'):
    return {'schema_version':1,'task_id':request['task_id'],'task_revision':request['task_revision'],'attempt_number':request['attempt_number'],'attempt_id':request['attempt_id'],'lease_id':request['lease_id'],'mode':request['mode'],'task_file':request['task_file'],'task_file_blob_sha':request['task_file_blob_sha'],'base_sha':request['base_sha'],'report_path':request['expected_report_path'],'status':status,'report_content':content,'requested_repository_mutations':[],'state_mutation_requested':False,'product_mutation_requested':False,'secret_values':[]}

class Phase2ASecurityTests(unittest.TestCase):
    def test_01_initial_state_is_valid_and_manual_occupancy_reserved(self):
        validate_state(CONTRACT,copy.deepcopy(STATE),EVENTS); occupied=[s for s in STATE['slots'] if s['status']=='occupied']; self.assertEqual(1,len(occupied)); self.assertEqual('external_manual',occupied[0]['occupancy_type']); self.assertEqual('play-role-and-start-priority-implement-01',occupied[0]['task_id'])
    def test_02_max_two_slots_fail_closed(self):
        s=copy.deepcopy(STATE); s['slots'].append({'slot_id':'slot_3','status':'free','occupancy_type':None,'task_id':None,'task_file':None,'conflict_keys':[],'lease':None})
        with self.assertRaises(OrchestrationError): validate_state(CONTRACT,s,EVENTS)
    def test_03_single_writer_manifest_and_phase2a_write_disabled(self):
        m=json.loads((ROOT/'orchestration/state_writer_manifest.json').read_text()); self.assertEqual('scripts/director_orchestration_controller.py',m['single_writer']); self.assertFalse(m['state_persistence_enabled_in_phase2a']); self.assertFalse(CONTRACT['state_persistence_enabled'])
        for p in (ROOT/'scripts').glob('*.py'):
            if p.name in {'director_orchestration_controller.py','test_director_orchestration_phase2a.py'}: continue
            self.assertNotIn('persist_state(',p.read_text(encoding='utf-8'))
    def test_04_stale_revision_cannot_acquire_lease(self):
        with self.assertRaises(OrchestrationError): acquire_cloud_lease(CONTRACT,copy.deepcopy(STATE),'epic-ru-availability-source-probe-01',0,NOW)
    def test_05_stale_revision_cannot_retain_lease(self):
        s,r=leased_epic(); slot=next(x for x in s['slots'] if x['occupancy_type']=='cloud_worker'); slot['lease']['task_revision']=0
        with self.assertRaises(OrchestrationError): validate_state(CONTRACT,s,EVENTS)
    def test_06_implement_mode_cannot_acquire_cloud_lease(self):
        with self.assertRaises(OrchestrationError): acquire_cloud_lease(CONTRACT,copy.deepcopy(STATE),'top-summary-filter-buttons-01',1,NOW)
    def test_07_worker_request_is_read_only_and_bound(self):
        _,r=leased_epic(); validate_worker_request(r); self.assertFalse(r['github_write_credential']); self.assertFalse(r['repository_write_authority']); self.assertEqual([],r['secret_values'])
    def test_08_stale_worker_result_rejected_after_attempt_advanced(self):
        s,r=leased_epic(); res=result_for(r); t=next(x for x in s['tasks'] if x['task_id']==r['task_id']); t['attempt_number']=2; t['attempt_id']=f"{t['task_id']}:r1:a2"
        with self.assertRaises(OrchestrationError): validate_publication(r,res,s,NOW+timedelta(minutes=1))
    def test_09_expired_worker_result_rejected(self):
        s,r=leased_epic(); res=result_for(r)
        with self.assertRaises(OrchestrationError): validate_publication(r,res,s,NOW+timedelta(hours=1))
    def test_10_wrong_report_path_rejected(self):
        s,r=leased_epic(); res=result_for(r); res['report_path']='reviews/worker_reports/other.md'
        with self.assertRaises(OrchestrationError): validate_publication(r,res,s,NOW+timedelta(minutes=1))
    def test_11_wrong_base_or_task_sha_rejected(self):
        s,r=leased_epic(); res=result_for(r); res['base_sha']='0'*40
        with self.assertRaises(OrchestrationError): validate_publication(r,res,s,NOW+timedelta(minutes=1))
        res=result_for(r); res['task_file_blob_sha']='0'*40
        with self.assertRaises(OrchestrationError): validate_publication(r,res,s,NOW+timedelta(minutes=1))
    def test_12_worker_cannot_request_product_or_state_mutation(self):
        s,r=leased_epic(); res=result_for(r); res['state_mutation_requested']=True
        with self.assertRaises(OrchestrationError): validate_publication(r,res,s,NOW+timedelta(minutes=1))
        res=result_for(r); res['requested_repository_mutations']=['web/app.js']
        with self.assertRaises(OrchestrationError): validate_publication(r,res,s,NOW+timedelta(minutes=1))
    def test_13_detectable_secret_material_rejected(self):
        s,r=leased_epic(); res=result_for(r,content='OPENAI'+'_API_KEY='+'s'+'k-'+'abcdefghijklmnopqrstuv')
        with self.assertRaises(OrchestrationError): validate_publication(r,res,s,NOW+timedelta(minutes=1))
    def test_14_trusted_publisher_writes_exact_report_only(self):
        s,r=leased_epic(); res=result_for(r); pub=validate_publication(r,res,s,NOW+timedelta(minutes=1))
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); target=publish_exact_report(root,pub); self.assertEqual(root/pub['report_path'],target); self.assertTrue(target.is_file()); self.assertEqual([target],list(root.rglob('*.md')))
    def test_15_changed_immutable_intake_event_fails_closed(self):
        ev=copy.deepcopy(EVENTS); key=next(iter(ev)); ev[key]['priority']='LOW'
        with self.assertRaises(OrchestrationError): validate_state(CONTRACT,copy.deepcopy(STATE),ev)
    def test_16_malformed_or_unknown_state_fails_closed(self):
        s=copy.deepcopy(STATE); s['schema_version']=999
        with self.assertRaises(OrchestrationError): validate_state(CONTRACT,s,EVENTS)
        s=copy.deepcopy(STATE); s.pop('slots')
        with self.assertRaises(OrchestrationError): validate_state(CONTRACT,s,EVENTS)
    def test_17_dispatch_disabled_yields_non_executable_staging_candidate(self):
        p=staging_plan(CONTRACT,copy.deepcopy(STATE),NOW); self.assertFalse(p['dispatch_enabled']); self.assertFalse(p['dispatch_performed']); self.assertFalse(p['openai_or_codex_invoked']); self.assertEqual('epic-ru-availability-source-probe-01',p['candidate']['task_id']); self.assertFalse(p['candidate']['executable'])
    def test_18_future_codex_template_has_minimal_worker_permissions_and_exact_pin(self):
        text=(ROOT/'orchestration/templates/future-read-only-codex-worker.yml.disabled').read_text(); worker=text.split('  worker:',1)[1].split('  publisher:',1)[0]; publisher=text.split('  publisher:',1)[1]
        self.assertIn('contents: read',worker); self.assertIn('persist-credentials: false',worker); self.assertIn('openai/codex-action@86365089eb2b84e0a8fb0717b304f8bdcb13b20e',worker); self.assertIn('allow-bot-users: github-actions[bot]',worker); self.assertIn('permission-profile: ":read-only"',worker); self.assertIn('safety-strategy: drop-sudo',worker); self.assertNotIn('contents: write',worker); self.assertNotIn('git push',worker); self.assertNotIn('STEAM_',worker); self.assertIn('contents: write',publisher); self.assertNotIn('openai/codex-action@',publisher); self.assertIn('director_report_publisher.py',publisher)
    def test_19_validation_workflow_needs_no_openai_secret_and_has_no_worker_dispatch(self):
        text=(ROOT/'.github/workflows/director-orchestration-phase2a-validation.yml').read_text(); self.assertIn('permissions:\n  contents: read',text); self.assertIn('persist-credentials: false',text); self.assertNotIn('OPENAI_API_KEY',text); self.assertNotIn('codex-action',text); self.assertNotIn('repository_dispatch',text); self.assertNotIn('workflow_call:',text); self.assertNotIn('contents: write',text)
if __name__=='__main__': unittest.main()
