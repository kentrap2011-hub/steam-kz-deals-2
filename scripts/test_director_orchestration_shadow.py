#!/usr/bin/env python3
from __future__ import annotations
import copy, json, unittest
from pathlib import Path
from director_orchestration_shadow import ShadowPlanError, plan_shadow
ROOT=Path(__file__).resolve().parents[1]
CONTRACT=json.loads((ROOT/'config/director_orchestration_contract.json').read_text())
STATE=json.loads((ROOT/'orchestration/state.json').read_text())

def task(task_id,priority='NORMAL',sequence=100,conflicts=None,deps=None,status='queued'):
    return {'task_id':task_id,'revision':1,'mode':'READ_ONLY_RECON','priority':priority,'domain':task_id,'conflict_keys':list(conflicts or []),'status':status,'task_file':f'WORKER_TASK_{task_id}.md','expected_report':f'reviews/worker_reports/{task_id}.md','dependencies':list(deps or []),'assigned_slot':None,'queue_sequence':sequence,'user_gate':'none','review_gate':'none'}

def state_with(tasks):
    return {'schema_version':1,'state_revision':99,'phase':'shadow_observer','slots':[{'slot_id':'slot_1','status':'free','occupancy_type':None,'task_id':None,'task_file':None,'conflict_keys':[]},{'slot_id':'slot_2','status':'free','occupancy_type':None,'task_id':None,'task_file':None,'conflict_keys':[]}],'tasks':tasks}

class ShadowPlannerTests(unittest.TestCase):
    def test_initial_state_reserves_chat1_and_fills_only_one_slot(self):
        p=plan_shadow(CONTRACT,copy.deepcopy(STATE)); self.assertEqual(1,len(p['occupied_slots'])); self.assertEqual('play-role-and-start-priority-implement-01',p['occupied_slots'][0]['task_id']); self.assertEqual('external_manual',p['occupied_slots'][0]['occupancy_type']); self.assertEqual('slot_2',p['would_assign'][0]['would_assign_slot']); self.assertLessEqual(p['assertions']['total_occupied_or_would_assign'],2)
    def test_conflicting_taste_ranking_task_not_selected(self):
        p=plan_shadow(CONTRACT,copy.deepcopy(STATE)); self.assertNotIn('wishlist-good-deal-override-recon-01',[x['task_id'] for x in p['would_assign']]); b=next(x for x in p['blocked_by_conflict'] if x['task_id']=='wishlist-good-deal-override-recon-01'); self.assertIn('taste-ranking-policy',b['overlapping_keys'])
    def test_unrelated_safe_task_selected_for_free_slot(self):
        self.assertEqual('epic-ru-availability-source-probe-01',plan_shadow(CONTRACT,copy.deepcopy(STATE))['would_assign'][0]['task_id'])
    def test_unmet_dependency_blocks_assignment(self):
        p=plan_shadow(CONTRACT,copy.deepcopy(STATE)); b=next(x for x in p['blocked_by_dependency'] if x['task_id']=='wishlist-good-deal-override-recon-01'); self.assertEqual(['play-role-and-start-priority-implement-01'],b['unsatisfied_dependencies'])
    def test_higher_explicit_priority_wins_when_both_safe(self):
        p=plan_shadow(CONTRACT,state_with([task('low','LOW',1),task('high','HIGH',2),task('normal','NORMAL',0)])); self.assertEqual(['high','normal'],[x['task_id'] for x in p['would_assign']])
    def test_dependency_unblocking_value_breaks_equal_priority(self):
        p=plan_shadow(CONTRACT,state_with([task('plain','HIGH',1),task('unblocker','HIGH',2),task('dependent','LOW',3,deps=['unblocker'])])); self.assertEqual('unblocker',p['would_assign'][0]['task_id'])
    def test_stale_cancelled_deferred_tasks_not_selected(self):
        p=plan_shadow(CONTRACT,state_with([task('stale',status='stale'),task('cancelled',status='cancelled'),task('deferred',status='deferred')])); self.assertEqual([],p['would_assign']); self.assertEqual({'stale','cancelled','deferred'},{x['task_id'] for x in p['ineligible']})
    def test_malformed_or_ambiguous_state_fails_closed(self):
        s=copy.deepcopy(STATE); s['slots'][0]['task_id']='different-task'
        with self.assertRaises(ShadowPlanError): plan_shadow(CONTRACT,s)
    def test_missing_dependency_fails_closed(self):
        s=copy.deepcopy(STATE); s['tasks'][2]['dependencies']=['missing-task']
        with self.assertRaises(ShadowPlanError): plan_shadow(CONTRACT,s)
    def test_selected_tasks_conflict_with_each_other(self):
        p=plan_shadow(CONTRACT,state_with([task('first','HIGH',1,['frontend-feed']),task('second','NORMAL',2,['frontend-feed']),task('third','LOW',3,['provider-authority:epic'])])); self.assertEqual(['first','third'],[x['task_id'] for x in p['would_assign']]); self.assertIn('second',[x['task_id'] for x in p['blocked_by_conflict']])
if __name__=='__main__': unittest.main()
