#!/usr/bin/env python3
from __future__ import annotations
import copy, json, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from director_orchestration_controller import (
    OrchestrationError, continue_phase2b_live_pilot, load_intakes, load_json,
    validate_expected_head, validate_expected_state_revision, validate_phase2b_pilot_contract,
    validate_state,
)
from director_report_publisher import validate_publication

ROOT=Path(__file__).resolve().parents[1]
P2A=load_json(ROOT/'config/director_orchestration_phase2a_contract.json')
P2B=load_json(ROOT/'config/director_orchestration_phase2b_pilot_contract.json')
STATE=load_json(ROOT/'orchestration/state.json')
EVENTS=load_intakes(ROOT)
NOW=datetime(2026,9,5,17,30,0,tzinfo=timezone.utc)

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
    def continued(self):
        return continue_phase2b_live_pilot(ROOT,P2A,P2B,copy.deepcopy(STATE),EVENTS,NOW)

    def test_01_contract_is_one_logical_attempt_with_only_two_pre_model_recoveries(self):
        validate_phase2b_pilot_contract(P2B)
        self.assertFalse(P2B['general_dispatch_enabled']); self.assertFalse(P2B['automatic_next_dispatch']); self.assertFalse(P2B['implement_dispatch_allowed'])
        self.assertEqual(1,P2B['limits']['max_live_attempts']); self.assertEqual(2,P2B['limits']['max_same_attempt_recovery_executions']); self.assertEqual(2,P2B['limits']['max_logical_slots'])
        self.assertTrue(P2B['recovery']['no_recovery_after_model_execution'])
        self.assertEqual('epic-ru-availability-source-probe-01:r1:a1',P2B['pilot']['attempt_id']); self.assertEqual('slot_2:epic-ru-availability-source-probe-01:r1:a1',P2B['pilot']['lease_id'])

    def test_02_current_state_is_first_recovery_of_exact_r1a1(self):
        validate_state(P2A,copy.deepcopy(STATE),EVENTS)
        m=STATE.get('phase2b_recovery'); self.assertIsInstance(m,dict); self.assertEqual(1,m['resume_count']); self.assertEqual(P2B['recovery']['initial_reason'],m['reason'])
        slot1=next(x for x in STATE['slots'] if x['slot_id']=='slot_1'); slot2=next(x for x in STATE['slots'] if x['slot_id']=='slot_2')
        self.assertEqual('free',slot1['status']); self.assertEqual('cloud_worker',slot2['occupancy_type']); self.assertEqual(P2B['pilot']['lease_id'],slot2['lease']['lease_id'])

    def test_03_schema_continuation_reuses_attempt_lease_and_retry_counter(self):
        s,r=self.continued(); task=next(x for x in s['tasks'] if x['task_id']==r['task_id'])
        self.assertEqual(P2B['pilot']['attempt_id'],r['attempt_id']); self.assertEqual(P2B['pilot']['lease_id'],r['lease_id']); self.assertEqual(1,r['attempt_number']); self.assertEqual(2,task['retry']['next_attempt_number'])
        self.assertEqual(2,s['phase2b_recovery']['resume_count']); self.assertEqual(P2B['recovery']['second_reason'],s['phase2b_recovery']['second_reason']); self.assertEqual('READ_ONLY_RECON',r['mode'])

    def test_04_third_pre_model_continuation_is_structurally_refused(self):
        s,_=self.continued()
        with self.assertRaises(OrchestrationError): continue_phase2b_live_pilot(ROOT,P2A,P2B,s,EVENTS,NOW+timedelta(minutes=1))

    def test_05_expired_lease_cannot_be_continued(self):
        with self.assertRaises(OrchestrationError): continue_phase2b_live_pilot(ROOT,P2A,P2B,copy.deepcopy(STATE),EVENTS,NOW+timedelta(hours=1))

    def test_06_current_state_barrier_rejects_revision_advance(self):
        s,r=self.continued(); validate_publication(r,result_for(r),s,NOW+timedelta(minutes=1)); advanced=copy.deepcopy(s); advanced['state_revision']+=1
        with self.assertRaises(OrchestrationError): validate_expected_state_revision(s['state_revision'],advanced['state_revision'])

    def test_07_head_cas_conflict_fails_closed(self):
        validate_expected_head('a'*40,'a'*40)
        with self.assertRaises(OrchestrationError): validate_expected_head('a'*40,'b'*40)

    def test_08_wrong_report_path_and_expired_result_are_rejected(self):
        s,r=self.continued(); wrong=result_for(r); wrong['report_path']='reviews/worker_reports/not-the-pilot.md'
        with self.assertRaises(OrchestrationError): validate_publication(r,wrong,s,NOW+timedelta(minutes=1))
        with self.assertRaises(OrchestrationError): validate_publication(r,result_for(r),s,NOW+timedelta(hours=1))

    def test_09_implement_task_cannot_be_substituted(self):
        bad=copy.deepcopy(P2B); bad['pilot']['task_id']='top-summary-filter-buttons-01'
        with self.assertRaises(OrchestrationError): validate_phase2b_pilot_contract(bad)

    def test_10_worker_has_exact_readonly_boundary_pin_and_supported_web_search(self):
        text=(ROOT/'.github/workflows/director-orchestration-phase2b-live-readonly-pilot.yml').read_text(encoding='utf-8'); worker=text.split('  worker:',1)[1].split('  publisher:',1)[0]
        self.assertIn('permissions:\n      contents: read',worker); self.assertIn('persist-credentials: false',worker); self.assertIn('openai/codex-action@86365089eb2b84e0a8fb0717b304f8bdcb13b20e',worker); self.assertIn('permission-profile: ":read-only"',worker); self.assertIn('safety-strategy: drop-sudo',worker); self.assertIn('web_search=\\"live\\"',worker)
        self.assertNotIn('["--search"]',worker); self.assertNotIn('contents: write',worker); self.assertNotIn('git push',worker); self.assertNotIn('STEAM_',worker)

    def test_11_output_schema_uses_explicit_types_for_const_fields(self):
        text=(ROOT/'.github/workflows/director-orchestration-phase2b-live-readonly-pilot.yml').read_text(encoding='utf-8')
        for fragment in ('"schema_version":{"type":"integer","const":1}','"task_revision":{"type":"integer","const":1}','"attempt_id":{"type":"string","const":"epic-ru-availability-source-probe-01:r1:a1"}','"state_mutation_requested":{"type":"boolean","const":false}'):
            self.assertIn(fragment,text)

    def test_12_publisher_is_separate_exact_path_only_and_no_queue_draining(self):
        text=(ROOT/'.github/workflows/director-orchestration-phase2b-live-readonly-pilot.yml').read_text(encoding='utf-8'); publisher=text.split('  publisher:',1)[1]
        self.assertIn('contents: write',publisher); self.assertNotIn('openai/codex-action@',publisher); self.assertIn('director_report_publisher.py',publisher); self.assertIn('reviews/worker_reports/epic-ru-availability-source-probe-01.md',publisher); self.assertIn('git diff --name-only',publisher)
        self.assertNotIn('choose_task(',text); self.assertNotIn('workflow_dispatch:',text); self.assertNotIn('repository_dispatch',text); self.assertFalse(P2B['automatic_next_dispatch']); self.assertFalse(P2B['implement_dispatch_allowed']); self.assertTrue(P2B['recovery']['must_not_select_another_task'])

if __name__=='__main__': unittest.main()
