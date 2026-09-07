import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_pre_ai_deal_scenarios as builder


class PreAiDealContractGuardTest(unittest.TestCase):
    def setUp(self):
        self.canonical = json.loads(Path('config/deal_quality_contract.json').read_text(encoding='utf-8'))

    @staticmethod
    def _prerequisite_payload(path, contract):
        if path == builder.FAMILIES:
            return {
                'status': 'complete',
                'complete_coverage_of_nonexcluded_candidates': True,
                'families': [],
            }
        if path == builder.STORE:
            return {'status': 'complete', 'entries': {}}
        if path == builder.FX:
            return {'status': 'complete', 'complete_coverage': True, 'entries': {}}
        if path == builder.HISTORY:
            return {'status': 'complete', 'complete_coverage': True, 'entries': {}}
        if path == builder.CONTRACT:
            return contract
        raise AssertionError(f'unexpected load path: {path}')

    def _run_main(self, contract):
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / 'deal_scenarios.json'
            with patch.object(builder, 'OUT', out), patch.object(
                builder,
                'load',
                side_effect=lambda path: self._prerequisite_payload(path, contract),
            ):
                builder.main()
            return json.loads(out.read_text(encoding='utf-8'))

    def test_canonical_v15_is_accepted(self):
        self.assertEqual(self.canonical.get('version'), '1.5')
        output = self._run_main(self.canonical)
        self.assertEqual(output['status'], 'complete')
        self.assertEqual(output['family_count'], 0)
        self.assertEqual(output['scenario_count'], 0)

    def test_stale_v13_is_rejected_fail_closed(self):
        stale = dict(self.canonical)
        stale['version'] = '1.3'
        with self.assertRaisesRegex(SystemExit, 'Unexpected deal quality contract'):
            self._run_main(stale)

    def test_missing_version_is_rejected_fail_closed(self):
        missing = dict(self.canonical)
        missing.pop('version', None)
        with self.assertRaisesRegex(SystemExit, 'Unexpected deal quality contract'):
            self._run_main(missing)

    def test_malformed_contract_json_is_rejected_by_loader(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'deal_quality_contract.json'
            path.write_text('{"contract":', encoding='utf-8')
            with self.assertRaises(json.JSONDecodeError):
                builder.load(path)


if __name__ == '__main__':
    unittest.main()
