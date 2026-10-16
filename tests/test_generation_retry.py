"""Recover failed generation after measurement without accepting stale evidence."""
from copy import deepcopy
import json
from pathlib import Path
from unittest.mock import patch

import unittest
import test_workflow_recovery
from koevd_eval.common import read_jsonl, write_jsonl
from koevd_eval.generation_recovery import resume_measured_generation
from koevd_eval.pipeline import generate_run, file_sha, report_run
from koevd_eval.results import export_run, validate_results
from test_runner_v2 import server


class GenerationRetryTests(unittest.TestCase):
    setUp=test_workflow_recovery.MeasurementRecoveryTests.setUp
    process=test_workflow_recovery.MeasurementRecoveryTests.process
    run_measure=test_workflow_recovery.MeasurementRecoveryTests.run_measure
    def repaired(self):
        rows=list(read_jsonl(self.root/'task3_predictions.jsonl'))
        for r in rows:
            if r['api_status']=='error':r.update(api_status='ok',prediction='SYNTHETIC repaired response',api_error=None)
        write_jsonl(self.root/'task3_predictions.jsonl',rows)

    def test_retry_archives_invalidates_and_remeasures_both_tasks(self):
        self.run_measure();old={p.name:file_sha(p) for p in self.root.glob('task*_measured.jsonl')}
        resume_measured_generation(self.root,self.manifest,self.repaired)
        self.assertEqual(self.manifest['measurements'],{})
        attempt=self.root/self.manifest['generation_retry_history'][-1]['attempt']
        for name,digest in old.items():
            self.assertFalse((self.root/name).exists());self.assertEqual(file_sha(attempt/'previous'/name),digest)
        self.fail_task=4
        with self.assertRaises(Exception):self.run_measure()
        self.fail_task=None;self.run_measure()
        self.assertEqual(self.calls,[3,4,3,4,4])
        rows=validate_results(export_run(self.root,self.fixture.index),self.fixture.index)
        self.assertTrue(all(r['measurement'] for r in rows[3]))

    def test_unchanged_generation_keeps_measurements(self):
        self.run_measure();old=deepcopy(self.manifest['measurements'])
        resume_measured_generation(self.root,self.manifest,lambda:None)
        self.assertEqual(old,self.manifest['measurements'])

    def test_tampered_measurement_rejects_before_generator(self):
        self.run_measure();(self.root/'task3_measured.jsonl').write_text('tamper')
        with patch.object(self,'repaired') as generate:
            with self.assertRaises(ValueError):resume_measured_generation(self.root,self.manifest,generate)
            generate.assert_not_called()

    def test_interrupted_invalidation_finishes_without_generation(self):
        self.run_measure();original=Path.unlink
        def interrupted(path,*args,**kw):
            if path.name=='task4_measured.jsonl':raise OSError('SYNTHETIC interruption after first removal')
            return original(path,*args,**kw)
        with patch.object(Path,'unlink',interrupted):
            with self.assertRaises(OSError):resume_measured_generation(self.root,self.manifest,self.repaired)
        self.manifest=json.loads((self.root/'pipeline.json').read_text())
        with self.assertRaisesRegex(ValueError,'Generation retry pending'):self.run_measure()
        with self.assertRaisesRegex(ValueError,'Generation retry pending'):export_run(self.root,self.fixture.index)
        with self.assertRaisesRegex(ValueError,'Generation retry pending'):report_run(self.root,self.manifest)
        with patch.object(self,'repaired') as generate:
            resume_measured_generation(self.root,self.manifest,generate);generate.assert_not_called()
        self.assertNotIn('generation_retry_pending',self.manifest)
        self.run_measure();validate_results(export_run(self.root,self.fixture.index),self.fixture.index)

    def test_interrupted_generator_and_changed_archive_rejected(self):
        self.run_measure()
        def interrupted():raise RuntimeError('SYNTHETIC generation interrupted')
        with self.assertRaises(RuntimeError):resume_measured_generation(self.root,self.manifest,interrupted)
        attempt=self.root/self.manifest['generation_retry_pending']
        (attempt/'previous/task3_measured.jsonl').write_text('tamper')
        with patch.object(self,'repaired') as generate:
            with self.assertRaisesRegex(ValueError,'Archived'):resume_measured_generation(self.root,self.manifest,generate)
            generate.assert_not_called()

    def test_actual_http_generate_retry_only_sends_failed_row_then_measure_export(self):
        # Use a fresh generation/config, preserving the prepared input identity.
        for task in (1,2,3,5):(self.root/f'task{task}_predictions.jsonl').unlink()
        self.manifest.pop('generation');failure={next(read_jsonl(self.root/'task3_input.jsonl'))['messages'][-1]['content']:500}
        with server(responses=failure) as (url,state):
            settings=dict(base_url=url,model='SYNTHETIC-http-model',retries=0,retry_delay=0)
            generate_run(self.root,self.manifest,**settings);self.run_measure()
            before=len(state['requests']);failure.clear();generate_run(self.root,self.manifest,**settings)
            self.assertEqual(len(state['requests'])-before,1)
        self.run_measure(remeasure=True)
        validate_results(export_run(self.root,self.fixture.index),self.fixture.index)

    def test_pending_classifier_promotion_blocks_generation_before_any_files_exist(self):
        self.manifest['measurement_pending']={'3':'measurement_attempts/SYNTHETIC'}
        with patch.object(self,'repaired') as generate:
            with self.assertRaisesRegex(ValueError,'Measurement promotion pending'):
                resume_measured_generation(self.root,self.manifest,generate)
            generate.assert_not_called()
