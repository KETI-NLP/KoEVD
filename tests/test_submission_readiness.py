from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_results
import test_workflow_recovery
from koevd_eval.common import read_jsonl, write_jsonl
from koevd_eval.pipeline import save_json
from koevd_eval.results import export_run, _seal
from koevd_eval.submission_readiness import check_run, check_file


class SubmissionReadinessTests(unittest.TestCase):
    def setUp(self):
        self.f = test_results.ResultContractTests()
        self.f.setUp()
        self.addCleanup(self.f.doCleanups)

    def test_current_contents_keep_failures_and_unmeasured_warnings_without_mutation(self):
        f = self.f
        before = {p.name: p.read_bytes() for p in f.run.iterdir() if p.is_file()}
        result = check_run(f.run, f.document, f.index)
        self.assertTrue(result['current'])
        self.assertEqual(result['status'], 'current_with_warnings')
        self.assertEqual(result['failed_generation_requests'], 1)
        self.assertEqual(result['unmeasured_usable_responses'], {'3': 1, '4': 1})
        self.assertFalse(result['stable_run_identity_checked'])
        self.assertEqual(before, {p.name: p.read_bytes() for p in f.run.iterdir() if p.is_file()})

    def test_changed_response_is_stale_even_though_old_json_remains_structurally_valid(self):
        f = self.f
        rows = list(read_jsonl(f.run / 'task1_predictions.jsonl'))
        rows[0]['prediction'] = 'unsafe'
        write_jsonl(f.run / 'task1_predictions.jsonl', rows)
        result = check_run(f.run, f.document, f.index)
        self.assertFalse(result['current'])
        self.assertEqual(result['changed_sections'], ['records'])
        self.assertTrue(check_run(f.run, export_run(f.run, f.index), f.index)['current'])

    def test_measurement_completion_invalidates_the_earlier_export(self):
        f = test_workflow_recovery.MeasurementRecoveryTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        before = export_run(f.root, f.fixture.index)
        f.run_measure()
        result = check_run(f.root, before, f.fixture.index)
        self.assertFalse(result['current'])
        self.assertIn('run', result['changed_sections'])
        self.assertIn('records', result['changed_sections'])
        self.assertTrue(check_run(f.root, export_run(f.root, f.fixture.index), f.fixture.index)['current'])

    def test_stable_identity_and_settings_are_checked_order_and_code_metadata_are_not(self):
        f = self.f
        f.manifest['generation_run'] = {'id': 'SYNTHETIC-stable', 'created_at': '2026-10-19T00:00:00Z'}
        save_json(f.run / 'pipeline.json', f.manifest)
        exported = export_run(f.run, f.index, code_revision='SYNTHETIC-original-code')
        moved = deepcopy(exported)
        moved['records'].reverse()
        moved['run']['code_revision'] = 'SYNTHETIC-doc-only-commit'
        moved = _seal({k: v for k, v in moved.items() if k != 'content_sha256'})
        self.assertTrue(check_run(f.run, moved, f.index)['current'])
        self.assertTrue(check_run(f.run, moved, f.index)['stable_run_identity_checked'])
        moved['run']['model']['dtype'] = 'SYNTHETIC-different-setting'
        moved = _seal({k: v for k, v in moved.items() if k != 'content_sha256'})
        self.assertEqual(check_run(f.run, moved, f.index)['changed_sections'], ['run'])
        f.manifest['generation_run']['id'] = 'SYNTHETIC-other-run'
        save_json(f.run / 'pipeline.json', f.manifest)
        self.assertFalse(check_run(f.run, exported, f.index)['current'])

    def test_pending_recovery_and_concurrent_changes_do_not_claim_current(self):
        f = self.f
        with patch('koevd_eval.submission_readiness._snapshot', side_effect=[{'a': 'old'}, {'a': 'new'}]):
            with self.assertRaisesRegex(ValueError, 'changed during'):
                check_run(f.run, f.document, f.index)
        f.manifest['generation_retry_pending'] = 'SYNTHETIC-pending'
        save_json(f.run / 'pipeline.json', f.manifest)
        with self.assertRaises(ValueError):
            check_run(f.run, f.document, f.index)

    def test_cli_reports_current_stale_and_invalid_with_exit_status(self):
        f = self.f
        result_path, index_path = f.root / 'results.json', f.root / 'index.json'
        save_json(result_path, f.document)
        save_json(index_path, f.index)
        command = [sys.executable, '-m', 'koevd_eval.results', 'check-run', '--run-dir', str(f.run),
                   '--input', str(result_path), '--trusted-index', str(index_path)]
        current = subprocess.run(command, capture_output=True, text=True, timeout=20)
        self.assertEqual(current.returncode, 0, current.stderr)
        self.assertTrue(json.loads(current.stdout)['current'])
        rows = list(read_jsonl(f.run / 'task1_predictions.jsonl'))
        rows[0]['prediction'] = 'unsafe'
        write_jsonl(f.run / 'task1_predictions.jsonl', rows)
        stale = subprocess.run(command, capture_output=True, text=True, timeout=20)
        self.assertEqual(stale.returncode, 2)
        self.assertEqual(json.loads(stale.stdout)['status'], 'stale_export')
        result_path.write_text('SYNTHETIC invalid JSON')
        self.assertEqual(check_file(f.run, result_path, index_path)['status'], 'check_failed')
        invalid = subprocess.run(command, capture_output=True, text=True, timeout=20)
        self.assertEqual(invalid.returncode, 2)
        self.assertFalse(json.loads(invalid.stdout)['current'])
