#!/usr/bin/env python3
from __future__ import annotations
import copy, json, unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from director_orchestration_controller import (
    OrchestrationError, load_intakes, load_json, prepare_phase2b_live_pilot,
    reconcile_phase2b_manual_occupancy, validate_expected_head, validate_expected_state_revision,
    validate_phase2b_pilot_contract, validate_state,
)
from director_report_publisher import validate_publication

ROOT=Path(__file__).resolve().parents[1]
P2A=load_json(ROOT/'config/director_orchestration_phase2a_contract.json')
P2B=load_json(ROOT/'config/director_orchestration_phase2b_pilot_contract.json')
STATE=load_json(ROOT/'orchestration/state.json')
EVENTS=load_intakes(ROOT)
NOW=datetime(2026,9,5,17,0,0,tzinfo=timezone.utc)

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
    def test_01_contract_is_one_bounded_readonly_pilot(self):
        validate_phase2b_pilot_contract(P2B)
        self.assertFalse(P2B['general_dispatch_enabled'])
        self.assertFalse(P2B['automatic_next_dispatch'])
        self.assertFalse(P2B['implement_dispatch_allowed'])
        self.assertEqual(1,P2B['limits']['max_live_attempts'])
        self.assertEqual(2,P2B['limits']['max_logical_slots'])
        self.assertEqual('READ_ONLY_RECON',P2B['worker']['mode'])

    def test_02_current_manual_occupancy_replaces_only_stale_play_role_slot(self):
        s=reconcile_phase2b_manual_occupancy(copy.deepcopy(STATE),P2B,NOW)
        self.assertEqual(2,len(s['slots']))
        slot=next(x for x in s['slots'] if x['slot_id']=='slot_1')
        self.assertEqual('external_manual',slot['occupancy_type'])
        self.assertEqual('reconsideration-commercial-bridge-and-wishlist-implement-01',slot['task_id'])
        old=next(x for x in s['tasks'] if x['task_id']=='play-role-and-start-priority-implement-01')
        self.assertIsNone(old['assigned_slot'])
        self.assertEqual('accepted',old['status'])
        validate_state(P2A,s,EVENTS)

    def test_03_exact_epic_pilot_only_acquires_second_slot(self):
        s,r=prepare_phase2b_live_pilot(ROOT,P2A,P2B,copy.deepcopy(STATE),EVENTS,NOW)
        self.assertEqual('epic-ru-availability-source-probe-01',r['task_id'])
        self.assertEqual('READ_ONLY_RECON',r['mode'])
        self.assertEqual(1,r['attempt_number'])
        self.assertEqual('reviews/worker_reports/epic-ru-availability-source-probe-01.md',r['expected_report_path'])
        occupied=[x for x in s['slots'] if x['status']=='occupied']
        self.assertEqual(2,len(occupied))
        self.assertEqual({'external_manual','cloud_worker'},{x['occupancy_type'] for x in occupied})

    def test_04_second_live_attempt_is_structurally_refused(self):
        s,_=prepare_phase2b_live_pilot(ROOT,P2A,P2B,copy.deepcopy(STATE),EVENTS,NOW)
        with self.assertRaises(OrchestrationError):
            prepare_phase2b_live_pilot(ROOT,P2A,P2B,s,EVENTS,NOW+timedelta(minutes=1))

    def test_05_implement_task_cannot_be_substituted(self):
        bad=copy.deepcopy(P2B)
        bad['pilot']['task_id']='top-summary-filter-buttons-01'
        with self.assertRaises(OrchestrationError): validate_phase2b_pilot_contract(bad)

    def test_06_concurrent_state_revision_is_rejected(self):
        s,r=prepare_phase2b_live_pilot(ROOT,P2A,P2B,copy.deepcopy(STATE),EVENTS,NOW)
        res=result_for(r)
        advanced=copy.deepcopy(s); advanced['state_revision']+=1
        with self.assertRaises(OrchestrationError):
            validate_expected_state_revision(s['state_revision'],advanced['state_revision'])
        validate_expected_state_revision(s['state_revision'],s['state_revision'])
        validate_publication(r,res,s,NOW+timedelta(minutes=1))

    def test_07_expected_head_cas_conflict_fails_closed(self):
        validate_expected_head('a'*40,'a'*40)
        with self.assertRaises(OrchestrationError): validate_expected_head('a'*40,'b'*40)
        with self.assertRaises(OrchestrationError): validate_expected_state_revision(4,5)

    def test_08_expired_lease_is_rejected(self):
        s,r=prepare_phase2b_live_pilot(ROOT,P2A,P2B,copy.deepcopy(STATE),EVENTS,NOW)
        with self.assertRaises(OrchestrationError):
            validate_publication(r,result_for(r),s,NOW+timedelta(hours=1))

    def test_09_wrong_report_path_is_rejected(self):
        s,r=prepare_phase2b_live_pilot(ROOT,P2A,P2B,copy.deepcopy(STATE),EVENTS,NOW)
        res=result_for(r); res['report_path']='reviews/worker_reports/not-the-pilot.md'
        with self.assertRaises(OrchestrationError): validate_publication(r,res,s,NOW+timedelta(minutes=1))

    def test_10_worker_job_has_no_write_credential_and_exact_codex_pin(self):
        text=(ROOT/'.github/workflows/director-orchestration-phase2b-live-readonly-pilot.yml').read_text(encoding='utf-8')
        worker=text.split('  worker:',1)[1].split('  publisher:',1)[0]
        self.assertIn('permissions:\n      contents: read',worker)
        self.assertIn('persist-credentials: false',worker)
        self.assertIn('openai/codex-action@86365089eb2b84e0a8fb0717b304f8bdcb13b20e',worker)
        self.assertIn('permission-profile: ":read-only"',worker)
        self.assertIn('safety-strategy: drop-sudo',worker)
        self.assertNotIn('contents: write',worker)
        self.assertNotIn('git push',worker)
        self.assertNotIn('STEAM_',worker)
        self.assertNotIn('provider',worker.lower())

    def test_11_publisher_is_separate_and_exact_path_only(self):
        text=(ROOT/'.github/workflows/director-orchestration-phase2b-live-readonly-pilot.yml').read_text(encoding='utf-8')
        publisher=text.split('  publisher:',1)[1]
        self.assertIn('contents: write',publisher)
        self.assertNotIn('openai/codex-action@',publisher)
        self.assertIn('director_report_publisher.py',publisher)
        self.assertIn('reviews/worker_reports/epic-ru-availability-source-probe-01.md',publisher)
        self.assertIn('git diff --name-only',publisher)

    def test_12_no_queue_draining_or_automatic_next_dispatch(self):
        text=(ROOT/'.github/workflows/director-orchestration-phase2b-live-readonly-pilot.yml').read_text(encoding='utf-8')
        self.assertNotIn('choose_task(',text)
        self.assertNotIn('workflow_dispatch:',text)
        self.assertNotIn('repository_dispatch',text)
        self.assertIn('automatic_next_dispatch',json.dumps(P2B))
        self.assertFalse(P2B['automatic_next_dispatch'])

if __name__=='__main__': unittest.main()
