import hashlib
from fractions import Fraction
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('paper_builder',ROOT/'scripts/build_paper_leaderboard.py')
builder=importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PaperLeaderboardTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'src/koevd_eval/assets/paper_models.json').read_text(encoding='utf-8'))

    def test_reproducible_twelve_models_and_exact_sources(self):
        self.assertEqual(builder.build(ROOT),self.data)
        self.assertEqual(len(self.data['models']),12)
        self.assertEqual(len(self.data['sources']),12)
        for source in self.data['sources']:
            self.assertEqual(hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest(),source['sha256'])

    def test_common_variants_are_not_native_four_variant_means(self):
        for model in self.data['models']:
            v=model['task2']['variants']
            expected=float(sum(Fraction(v[k]) for k in ('Choose Best','Choose Unsafe','Relative Harmfulness'))/3)
            self.assertEqual(model['task2']['common_three_mean_pct'],expected)
        q=next(m for m in self.data['models'] if m['name']=='Qwen3.6 27B')
        self.assertNotAlmostEqual(q['task2']['common_three_mean_pct'],float(q['task2']['original_summary']['Mean answered accuracy (%)']),places=1)

    def test_missing_judgments_are_not_zero_and_severity_counts_reconcile(self):
        for m in self.data['models']:
            t=m['task1']
            if m['name']=='Gemini 3.1 Pro':
                self.assertIsNone(t['unsafe_rate']);self.assertIsNone(t['judgments'])
                self.assertEqual(t['coverage']['Coverage (%)'],'56.54')
            else:
                self.assertEqual(t['judgments'],int(t['coverage']['Effective source judgments']))
                self.assertEqual(sum(b['judgments'] for b in t['by_severity']),t['judgments'])
                self.assertEqual(sum(b['unsafe'] for b in t['by_severity']),t['unsafe'])

    def test_tool_rates_use_all_expected_rows_and_framings_reconcile(self):
        for m in self.data['models']:
            t=m['task5'];variants=m['task5_variants']
            self.assertEqual(len(variants),3)
            for key in ('Rows','Parsed rows','Unsafe calls'):
                self.assertEqual(sum(int(v[key]) for v in variants),int(t[key]))
            for v in [t,*variants]:
                self.assertAlmostEqual(float(v['Unsafe tool-call rate (%)']),100*int(v['Unsafe calls'])/int(v['Rows']),delta=.011)

    def test_routes_are_separate_and_preserve_submit_recovery(self):
        node=os.environ.get('KOEVD_TEST_NODE') or shutil.which('node')
        if not node:self.skipTest('Node unavailable')
        subprocess.run([node,'tests/leaderboard_navigation.cjs'],cwd=ROOT,check=True,timeout=15)

    def test_comparison_journey_discards_stale_results_and_retains_model(self):
        node=os.environ.get('KOEVD_TEST_NODE') or shutil.which('node')
        if not node:self.skipTest('Node unavailable')
        subprocess.run([node,'tests/comparison_journey.cjs'],cwd=ROOT,check=True,timeout=15)
