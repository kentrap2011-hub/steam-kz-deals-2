#!/usr/bin/env python3
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/'.github/workflows/director-copilot-cli-zero-cost-live-readonly-pilot-02.yml'
CONTRACT=ROOT/'config/director_orchestration_copilot_cli_pilot02_contract.json'

class Pilot02ContractTests(unittest.TestCase):
    def setUp(self):
        self.text=WORKFLOW.read_text(encoding='utf-8')
        self.contract=json.loads(CONTRACT.read_text(encoding='utf-8'))

    def test_zero_cost_contract(self):
        c=self.contract
        for key in ('additional_payment_allowed','paid_overage_allowed','paid_fallback_allowed','pat_allowed','openai_api_key_allowed'):
            self.assertFalse(c['cost_gate'][key])
        self.assertEqual('GITHUB_TOKEN',c['cost_gate']['authentication'])
        self.assertEqual(1,c['limits']['max_live_attempts'])
        self.assertFalse(c['automatic_next_dispatch'])
        self.assertFalse(c['implement_dispatch_allowed'])

    def test_worker_permission_boundary(self):
        worker=self.text.split('  worker:',1)[1].split('  publisher:',1)[0]
        self.assertIn('contents: read',worker)
        self.assertIn('copilot-requests: write',worker)
        self.assertNotIn('contents: write',worker)
        self.assertIn('persist-credentials: false',worker)
        self.assertIn('--disable-builtin-mcps',worker)
        self.assertIn("--available-tools='view,glob,grep,web_fetch'",worker)
        self.assertNotIn('--yolo',worker)
        self.assertNotIn('--allow-all',worker)
        self.assertNotIn('git push',worker)
        self.assertNotIn('${{ secrets.',worker)

    def test_one_invocation_no_retry(self):
        worker=self.text.split('  worker:',1)[1].split('  publisher:',1)[0]
        self.assertEqual(1,worker.count('copilot -s -p'))
        self.assertNotIn('rerun',worker.lower())
        self.assertNotIn('while ',worker.lower())
        self.assertIn("e['copilot_invocation_count']=1",worker)
        self.assertIn("provider_unavailable_zero_cost_gate",worker)

    def test_exact_binding_and_publisher(self):
        self.assertIn('epic-ru-availability-source-probe-02:r1:a1',self.text)
        self.assertIn('slot_2:epic-ru-availability-source-probe-02:r1:a1',self.text)
        self.assertIn('8270487fb3019135adc5662d0b67f0f37e189bed',self.text)
        self.assertIn('reviews/worker_reports/epic-ru-availability-source-probe-02.md',self.text)
        publisher=self.text.split('  publisher:',1)[1]
        perms=publisher.split('    steps:',1)[0]
        self.assertIn('contents: write',perms)
        self.assertNotIn('copilot-requests: write',perms)
        self.assertIn('copilot_cli_pilot02_control.py finalize',publisher)

    def test_implement_and_next_dispatch_excluded(self):
        self.assertIn("impl['mode']=='IMPLEMENT' and impl['attempt_number']==0",self.text)
        self.assertFalse(self.contract['implement_dispatch_allowed'])
        self.assertFalse(self.contract['automatic_next_dispatch'])

    def test_quota_gate_requires_no_overage(self):
        worker=self.text.split('  worker:',1)[1].split('  publisher:',1)[0]
        self.assertIn('premium_interactions',worker)
        self.assertIn('overageAllowedWithExhaustedQuota===false',worker)
        self.assertIn('safeForZeroAdditionalPayment',worker)

if __name__=='__main__': unittest.main()
