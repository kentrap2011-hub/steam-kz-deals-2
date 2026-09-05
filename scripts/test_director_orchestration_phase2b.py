#!/usr/bin/env python3
from __future__ import annotations
import copy, json, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from director_orchestration_controller import (
    OrchestrationError, load_intakes, load_json, resume_phase2b_live_pilot,
    validate_expected_head, validate_expected_state_revision, validate_phase2b_pilot_contract,
    validate_state,
)
from director_report_publisher import validate_publication

ROOT=Path(__file__).resolve().parents[1]
P2A=load_json(ROOT/'config/director_orchestration_phase2a_contract.json')
P2B=load_json(ROOT/'config/director_orchestration_phase2b_pilot_contract.json')
STATE=load_json(ROOT/'orchestration/state.json')
EVENTS=load_intakes(ROOT)
NOW=datetime(2026,9,5,17,15,0,tzinfo=timezone.utc)

def result_for(request,status='blocked',content='# Epic RU availability source probe\n\nStatus: blocked\n'):
    return {
        'schema_version':1,'task_id':request['task_id'],'task_revision':request['task_revision'],
        'attempt_number':request['attempt_number'],'attempt_id':request['attempt_id'],'lease_id':request['lease_id'],
        'mode':request['mode'],'task_file':request['task_file'],'task_file_blob_sha':request['task_file_blob_sha'],
        'base_sha':request['base_sha'],'report_path':request['expected_report_path'],'status':status,
        'report_content':content,'requested_repository_mutations':[],'state_mutation_requested':False,
        'product_mutation_requested':False,'secret_values':[],
    }

class Phase2BLivePilotTests(unittest.TestCase):
    def resumed(self):
        return resume_phase2b_live_pilot(ROOT,P2A,P2B,copy.deepcopy(STATE),EVENTS,NOW)

    def test_01_contract_is_one_bounded_readonly_attempt(self):
        validate_phase2b_pilot_contract(P2B)
        self.assertFalse(P2B['general_dispatch_enabled'])
        self.assertFalse(P2B['automatic_next_dispatch'])
        self.assertFalse(P2B['implement_dispatch_allowed'])
        self.assertEqual(1,P2B['limits']['max_live_attempts'])
        self.assertEqual(1,P2B['limits']['max_same_attempt_recovery_executions'])
        self.assertEqual(2,P2B['limits']['max_logical_slots'])
        self.assertEqual('epic-ru-availability-source-probe-01:r1:a1',P2B['pilot']['attempt_id'])
        self.assertEqual('slot_2:epic-ru-availability-source-probe-01:r1:a1',P2B['pilot']['lease_id'])

    def test_02_current_manual_completion_frees_slot_without_new_dispatch(self):
        report=ROOT/P2B['manual_occupancy']['completion_report']
        self.assertTrue(report.is_file())
        self.assertIn('`complete`',report.read_text(encoding='utf-8')[:4000])
        s,r=self.resumed()
        slot1=next(x for x in s['slots'] if x['slot_id']=='slot_1')
        slot2=next(x for x in s['slots'] if x['slot_id']=='slot_2')
        self.assertEqual('free',slot1['status'])
        self.assertIsNone(slot1['task_id'])
        self.assertEqual('cloud_worker',slot2['occupancy_type'])
        self.assertEqual('epic-ru-availability-source-probe-01',slot2['task_id'])
        self.assertEqual(2,len(s['slots']))
        validate_state(P2A,s,EVENTS)

    def test_03_recovery_reuses_exact_attempt_lease_and_retry_counter(self):
        s,r=self.resumed()
        task=next(x for x in s['tasks'] if x['task_id']==r['task_id'])
        self.assertEqual('epic-ru-availability-source-probe-01:r1:a1',r['attempt_id'])
        self.assertEqual('slot_2:epic-ru-availability-source-probe-01:r1:a1',r['lease_id'])
        self.assertEqual(1,r['attempt_number'])
        self.assertEqual(2,task['retry']['next_attempt_number'])
        self.assertEqual(1,s['phase2b_recovery']['resume_count'])
        self.assertEqual('READ_ONLY_RECON',r['mode'])
        self.assertEqual('reviews/worker_reports/epic-ru-availability-source-probe-01.md',r['expected_report_path'])

    def test_04_second_recovery_execution_is_structurally_refused(self):
        s,_=self.resumed()
        with self.assertRaises(OrchestrationError):
            resume_phase2b_live_pilot(ROOT,P2A,P2B,s,EVENTS,NOW+timedelta(minutes=1))

    def test_05_expired_original_lease_cannot_be_recovered(self):
        with self.assertRaises(OrchestrationError):
            resume_phase2b_live_pilot(ROOT,P2A,P2B,copy.deepcopy(STATE),EVENTS,NOW+timedelta(minutes=30))

    def test_06_concurrent_state_revision_rejects_result(self):
        s,r=self.resumed(); res=result_for(r)
        validate_publication(r,res,s,NOW+timedelta(minutes=1))
        advanced=copy.deepcopy(s); advanced['state_revision']+=1
        with self.assertRaises(OrchestrationError):
            validate_expected_state_revision(s['state_revision'],advanced['state_revision'])

    def test_07_expected_head_cas_conflict_fails_closed(self):
        validate_expected_head('a'*40,'a'*40)
        with self.assertRaises(OrchestrationError): validate_expected_head('a'*40,'b'*40)
        with self.assertRaises(OrchestrationError): validate_expected_state_revision(5,6)

    def test_08_expired_worker_result_is_rejected(self):
        s,r=self.resumed()
        with self.assertRaises(OrchestrationError):
            validate_publication(r,result_for(r),s,NOW+timedelta(hours=1))

    def test_09_wrong_report_path_is_rejected(self):
        s,r=self.resumed(); res=result_for(r); res['report_path']='reviews/worker_reports/not-the-pilot.md'
        with self.assertRaises(OrchestrationError): validate_publication(r,res,s,NOW+timedelta(minutes=1))

    def test_10_implement_task_cannot_be_substituted(self):
        bad=copy.deepcopy(P2B); bad['pilot']['task_id']='top-summary-filter-buttons-01'
        with self.assertRaises(OrchestrationError): validate_phase2b_pilot_contract(bad)

    def test_11_worker_job_has_exact_readonly_boundary_and_supported_web_search_config(self):
        text=(ROOT/'.github/workflows/director-orchestration-phase2b-live-readonly-pilot.yml').read_text(encoding='utf-8')
        worker=text.split('  worker:',1)[1].split('  publisher:',1)[0]
        self.assertIn('permissions:\n      contents: read',worker)
        self.assertIn('persist-credentials: false',worker)
        self.assertIn('openai/codex-action@86365089eb2b84e0a8fb0717b304f8bdcb13b20e',worker)
        self.assertIn('permission-profile: ":read-only"',worker)
        self.assertIn('safety-strategy: drop-sudo',worker)
        self.assertIn('web_search=\\"live\\"',worker)
        self.assertNotIn('["--search"]',worker)
        self.assertNotIn('contents: write',worker)
        self.assertNotIn('git push',worker)
        self.assertNotIn('STEAM_',worker)

    def test_12_publisher_is_separate_and_exact_path_only(self):
        text=(ROOT/'.github/workflows/director-orchestration-phase2b-live-readonly-pilot.yml').read_text(encoding='utf-8')
        publisher=text.split('  publisher:',1)[1]
        self.assertIn('contents: write',publisher)
        self.assertNotIn('openai/codex-action@',publisher)
        self.assertIn('director_report_publisher.py',publisher)
        self.assertIn('reviews/worker_reports/epic-ru-availability-source-probe-01.md',publisher)
        self.assertIn('git diff --name-only',publisher)

    def test_13_no_queue_draining_second_task_or_automatic_implement(self):
        text=(ROOT/'.github/workflows/director-orchestration-phase2b-live-readonly-pilot.yml').read_text(encoding='utf-8')
        self.assertNotIn('choose_task(',text)
        self.assertNotIn('workflow_dispatch:',text)
        self.assertNotIn('repository_dispatch',text)
        self.assertFalse(P2B['automatic_next_dispatch'])
        self.assertFalse(P2B['implement_dispatch_allowed'])
        self.assertTrue(P2B['recovery']['must_not_select_another_task'])

if __name__=='__main__': unittest.main()
