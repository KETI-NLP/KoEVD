import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

import test_results
import test_submissions
import test_workflow_recovery
from koevd_eval.common import read_jsonl,write_jsonl
from koevd_eval.pipeline import save_json
from koevd_eval.run_status import status_run


class PaperAggregateTests(unittest.TestCase):
    def test_shipped_tables_exactly_match_public_sources_and_scope(self):
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'src/koevd_eval/assets/paper_results.json').read_text(encoding='utf-8'))
        self.assertEqual(data['scope'],'historical_aggregate_only')
        self.assertEqual([t['task'] for t in data['tables']],[1,2,3,4,5])
        for table in data['tables']:
            source=root/table['source']
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(),table['source_sha256'])
            self.assertEqual(list(csv.DictReader(source.open(encoding='utf-8-sig',newline=''))),table['rows'])
        self.assertEqual(len(data['tables'][2]['rows']),12)
        self.assertTrue(all(r['Total prompts']=='13552' for r in data['tables'][2]['rows']))
        self.assertEqual(len(data['tables'][4]['rows']),3)

    def test_public_startup_independence_and_projections(self):
        node=os.environ.get('KOEVD_TEST_NODE') or shutil.which('node')
        if not node:self.skipTest('Node.js unavailable')
        subprocess.run([node,'tests/home_startup.cjs'],cwd=Path(__file__).resolve().parents[1],check=True,timeout=10)


class StrategyProjectionTests(unittest.TestCase):
    def test_public_board_strategy_projection_matches_profile_and_withdrawal(self):
        f=test_submissions.SubmissionTests();f.setUp();self.addCleanup(f.doCleanups)
        state=f.publish('summary');summary=f.service.public_summary(state['id'])
        expected=next(p['strategy_inclusion'] for p in summary['tasks']['4']['partitions'] if p['kind']=='all')
        board=f.service.public_leaderboard()
        self.assertEqual(board['publications'][0]['strategy_inclusion'],expected)
        self.assertEqual(set(next(iter(expected.values()))),{'count','classified','rate_on_classified'})
        f.action(state,'withdraw')
        self.assertEqual(f.service.public_leaderboard()['publications'],[])


class RunStatusTests(unittest.TestCase):
    def setUp(self):
        self.f=test_workflow_recovery.MeasurementRecoveryTests();self.f.setUp();self.addCleanup(self.f.doCleanups)

    def test_failures_and_missing_rows_recommend_resume_without_mutation(self):
        f=self.f;before=(f.root/'pipeline.json').read_bytes();s=status_run(f.root)
        self.assertEqual(s['failed_generation_rows'],1);self.assertIn('original --stage generate',s['next_action'])
        self.assertEqual((f.root/'pipeline.json').read_bytes(),before)
        (f.root/'task1_predictions.jsonl').unlink();s=status_run(f.root)
        self.assertEqual(s['pending_generation_rows'],1)

    def test_pending_measurement_finishes_before_generation_retry(self):
        f=self.f;f.manifest['measurement_pending']='measurement_runs/SYNTHETIC'
        save_json(f.root/'pipeline.json',f.manifest)
        s=status_run(f.root)
        self.assertEqual(s['failed_generation_rows'],1)
        self.assertIn('classify command',s['next_action'])
        self.assertIn('before retrying generation',s['next_action'])

    def test_complete_measurement_and_integrity_failure_are_distinct(self):
        f=self.f;rows=list(read_jsonl(f.root/'task3_predictions.jsonl'))
        for r in rows:r.update(api_status='ok',prediction='SYNTHETIC successful response',api_error=None)
        write_jsonl(f.root/'task3_predictions.jsonl',rows);f.run_measure()
        s=status_run(f.root);self.assertTrue(s['all_generation_requests_succeeded'])
        self.assertEqual(s['measurements']['3']['status'],'complete');self.assertIn('export and validate',s['next_action'])
        (f.root/'task4_measured.jsonl').write_text('SYNTHETIC tamper')
        s=status_run(f.root);self.assertEqual(s['measurements']['4']['status'],'invalid');self.assertIn('integrity',s['next_action'])

    def test_pending_generation_and_foreign_prediction_never_report_ready(self):
        f=self.f;f.manifest['generation_retry_pending']='generation_retries/SYNTHETIC';save_json(f.root/'pipeline.json',f.manifest)
        self.assertTrue(status_run(f.root)['generation_retry_pending'])
        rows=list(read_jsonl(f.root/'task1_predictions.jsonl'));rows[0]['evaluated_model']='OTHER'
        write_jsonl(f.root/'task1_predictions.jsonl',rows)
        with self.assertRaisesRegex(ValueError,'do not match'):status_run(f.root)
