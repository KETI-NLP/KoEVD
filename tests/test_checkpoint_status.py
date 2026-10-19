"""Actual durable runner interruption; model calls are synthetic and CPU-only."""
from copy import deepcopy
import json
from unittest.mock import patch
import unittest

import test_results
from koevd_eval.common import read_jsonl
from koevd_eval.pipeline import save_json
from koevd_eval.run_openai_compatible import make_config, run_rows
from koevd_eval.run_status import status_run


class CheckpointStatusTests(unittest.TestCase):
    def setUp(self):
        self.f=test_results.ResultContractTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.output=self.f.run/'task2_predictions.jsonl';self.output.unlink()
        self.config=make_config('http://localhost:8000/v1','cpu-fixture',0.,32)
        self.f.manifest['generation']=self.config;save_json(self.f.run/'pipeline.json',self.f.manifest)
        self.rows=list(read_jsonl(self.f.run/'task2_input.jsonl'))

    def interrupt(self, responses):
        with patch('koevd_eval.run_openai_compatible.call_api',side_effect=responses):
            with self.assertRaises(KeyboardInterrupt):run_rows(self.rows,self.output,self.config)

    def test_read_only_status_counts_retained_success_and_interrupted_attempt(self):
        self.interrupt(['A',KeyboardInterrupt])
        before={p.name:p.read_bytes() for p in self.f.run.iterdir() if p.is_file()}
        result=status_run(self.f.run);task=result['tasks']['2']
        self.assertEqual((task['api_ok'],task['failed'],task['interrupted_unknown'],task['pending']),(1,0,1,2))
        self.assertTrue(task['checkpoint_journal_present']);self.assertTrue(result['generation_checkpoint_pending'])
        self.assertFalse(result['all_generation_requests_succeeded']);self.assertIn('stage generate',result['next_action'])
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.f.run.iterdir() if p.is_file()})
        with patch('koevd_eval.run_openai_compatible.call_api',return_value='A') as api:
            run_rows(self.rows,self.output,self.config,resume=True)
        self.assertEqual(api.call_count,3)
        task=status_run(self.f.run)['tasks']['2']
        self.assertEqual((task['api_ok'],task['failed'],task['interrupted_unknown'],task['pending']),(4,0,0,0))
        self.assertFalse(task['checkpoint_journal_present'])

    def test_changed_checkpoint_identity_and_corrupt_journal_are_rejected_without_repair(self):
        self.interrupt(['A',KeyboardInterrupt])
        state=self.output.with_suffix('.jsonl.run.json');original=state.read_bytes()
        value=json.loads(original);value['config_sha256']='f'*64;save_json(state,value)
        with self.assertRaisesRegex(ValueError,'checkpoint does not match'):status_run(self.f.run)
        state.write_bytes(original)
        journal=self.output.with_suffix('.jsonl.progress.jsonl');raw=journal.read_bytes()
        journal.write_bytes(b'not-json\n'+raw)
        before=journal.read_bytes()
        with self.assertRaisesRegex(ValueError,'Corrupt generation journal'):status_run(self.f.run)
        self.assertEqual(journal.read_bytes(),before)

    def test_complete_journal_still_requires_generate_compaction(self):
        def progress(value):
            if value['state']=='running' and value['completed']==len(self.rows):raise KeyboardInterrupt
        with patch('koevd_eval.run_openai_compatible.call_api',return_value='A'):
            with self.assertRaises(KeyboardInterrupt):run_rows(self.rows,self.output,self.config,progress=progress)
        result=status_run(self.f.run)
        self.assertEqual(result['tasks']['2']['api_ok'],4)
        self.assertTrue(result['generation_checkpoint_pending']);self.assertIn('stage generate',result['next_action'])
        with patch('koevd_eval.run_openai_compatible.call_api') as api:
            run_rows(self.rows,self.output,self.config,resume=True)
        api.assert_not_called();self.assertTrue(self.output.exists())
