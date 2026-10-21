from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

from koevd_eval.behavior_facets import BehaviorAccumulator, STRATEGIES, OUTCOMES
from koevd_eval.diagnostics import analyze
from koevd_eval.profile_cache import numerical_profile
import test_results

ROOT = Path(__file__).resolve().parents[1]


class BehaviorFacetTests(unittest.TestCase):
    def test_multilabel_counts_and_responses_do_not_duplicate_topic_intersections(self):
        acc = BehaviorAccumulator(4)
        labels = {'topic':['Gender','Taste'], 'severity_band':['High']}
        acc.add(labels,'private-a',True,strategies=[STRATEGIES[0],STRATEGIES[1],'unsafe'],response_label='safe')
        acc.add(labels,'private-b',False,response_label='unclassified',eligible=False)
        b = acc.result()['buckets'][0]
        self.assertEqual((b['rows'],b['valid'],b['eligible']),(2,1,1))
        self.assertEqual(b['pairs'],{'0:0':1,'0:1':1,'1:1':1})
        self.assertEqual(b['responses']['safe'][STRATEGIES[0]],1)
        self.assertEqual(b['responses']['unclassified']['valid'],0)
        self.assertNotIn('private-a',json.dumps(acc.result()))
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            acc.add(labels,'private-a',True)
        with self.assertRaisesRegex(ValueError,'Invalid strategy'):
            BehaviorAccumulator(4).add({},'x',False,strategies=['unsafe'])

    def test_normalization_exclusions_remain_invalid_without_erasing_archival_counts(self):
        acc=BehaviorAccumulator(5)
        acc.add({},'x',False,outcome='invalid',response_label='safe',
                archived_parsed=True,archived_decision_valid=True)
        b=acc.result()['buckets'][0]
        self.assertEqual(b['valid'],0)
        self.assertEqual(b['archived_parsed'],1)
        self.assertEqual(b['legacy_exclusions'],{'safe':1})
        self.assertEqual(b['outcomes'],{'invalid':1})
        with self.assertRaisesRegex(ValueError,'disagree'):
            BehaviorAccumulator(5).add({},'x',True,outcome='invalid')

    def test_registered_partitions_reconcile_with_existing_scores_and_stay_numerical(self):
        f=test_results.ResultContractTests();f.setUp();self.addCleanup(f.temp.cleanup)
        report=analyze(f.document,f.index,resamples=0)
        for task in (4,5):
            for cube in report['tasks'][str(task)]['behavior_facets']:
                p=next(p for p in report['tasks'][str(task)]['partitions']
                    if p['kind']==cube['partition_kind'] and p['name']==cube['partition_name'])
                self.assertEqual(sum(b['rows'] for b in cube['buckets']),p['rows'])
                self.assertEqual(sum(b['valid'] for b in cube['buckets']),p['valid'])
                counts=Counter()
                for b in cube['buckets']:counts.update(b['strategies' if task==4 else 'outcomes'])
                if task==4:
                    self.assertEqual({k:counts[k] for k in STRATEGIES},{k:v['count'] for k,v in p['strategy_inclusion'].items()})
                    self.assertEqual(counts['unsafe'],p['unsafe_marker']['count'])
                else:self.assertEqual({k:counts[k] for k in OUTCOMES},p['strict_outcomes'])
            projection=numerical_profile(report)['tasks'][str(task)]['behavior_facets']
            self.assertEqual(projection,report['tasks'][str(task)]['behavior_facets'])
            for field in ('source_id','sample_id','messages','prediction','response','private-a'):
                self.assertNotIn('"'+field+'"',json.dumps(projection))

    def test_twelve_archived_models_conserve_exact_counts_and_lazy_assets(self):
        raw=(ROOT/'paper_assets/data/behavior_aggregates.json').read_bytes()
        archive=json.loads(raw)
        paper=json.loads((ROOT/'src/koevd_eval/assets/paper_models.json').read_text(encoding='utf8'))
        self.assertEqual(len(archive['models']),12)
        self.assertEqual(sum(archive['historical_decisions_without_available_tools'].values()),2)
        with (ROOT/'paper_assets/tables/appendix_j_task5_model_variant_summary.csv').open(encoding='utf-8-sig',newline='') as f:
            expected={(r['Model'],r['Variant'].lower().replace('-','_')):r for r in csv.DictReader(f)}
        rows=0
        for m in paper['models']:
            self.assertNotIn('behavior',m,'Large details must not slow the initial leaderboard')
            lazy=json.loads((ROOT/'src/koevd_eval/assets'/m['behavior_asset']).read_text(encoding='utf8'))
            self.assertEqual(lazy['model'],m['name'])
            self.assertEqual(lazy['source_sha256'],hashlib.sha256(raw).hexdigest())
            self.assertEqual(lazy['tasks'],archive['models'][m['name']])
            b4=lazy['tasks']['4'][0]['buckets']
            self.assertEqual(sum(b['rows'] for b in b4),13552)
            self.assertEqual(sum(b['valid'] for b in b4),int(m['task4_measurements']['Strategy-classified responses']))
            for p in lazy['tasks']['5']:
                b=p['buckets'];ref=expected[m['name'],p['partition_name']]
                self.assertEqual(sum(x['rows'] for x in b),int(ref['Rows']))
                self.assertEqual(sum(x['archived_parsed'] for x in b),int(ref['Parsed rows']))
                self.assertEqual(sum(x['outcomes'].get('unsafe_tool',0) for x in b),int(ref['Unsafe calls']))
                self.assertEqual(sum(sum(x['outcomes'].values()) for x in b),784)
                self.assertEqual(sum(sum(sum(v.values()) for v in x['responses'].values()) for x in b),784)
                rows+=sum(x['rows'] for x in b)
        self.assertEqual(rows,28224)

    def test_renderer_exact_filters_semantic_order_and_correspondence(self):
        node=os.environ.get('KOEVD_TEST_NODE') or shutil.which('node')
        if not node:self.skipTest('Node unavailable')
        subprocess.run([node,'tests/behavior_analysis.cjs'],cwd=ROOT,check=True,timeout=60)


if __name__=='__main__':unittest.main()
