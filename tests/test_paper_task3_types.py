import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('paper_types', ROOT/'scripts/build_paper_task3_types.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PaperTask3TypeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.inputs = [{'sample_id':f's{i}:task3_response_generation',
                        'metadata':{'source_id':f's{i}','utter_type':'HIQ_e','toxicity':'2',
                                    'explicitness':'I','topic':['GD','PA','GD']}} for i in range(3)]
        self.rows = [{**copy.deepcopy(row),'source_model':'gpt-5.4',
                      'classification_status':'classified','predicted_label':label,
                      'is_safe':label=='safe','generation_status':'success','assistant_content':'fixture'}
                     for row,label in zip(self.inputs,['safe','unsafe','safe'])]
        self.rows[2].update(classification_status='skipped_generation',predicted_label=None,
                            is_safe=None,generation_status='error',assistant_content='')
        self.expected = {'GPT-5.4':{'Total prompts':3,'Classified responses':2,'Unsafe responses':1}}

    def aggregate(self, rows=None, expected=None):
        inputs=self.folder/'inputs.jsonl';predictions=self.folder/'predictions.jsonl'
        for path,data in [(inputs,self.inputs),(predictions,self.rows if rows is None else rows)]:
            path.write_text(''.join(json.dumps(r)+'\n' for r in data),encoding='utf-8')
        return builder.aggregate(inputs,[predictions],self.expected if expected is None else expected)

    def test_invalid_outputs_and_overlapping_topics(self):
        m=self.aggregate()['GPT-5.4']
        self.assertEqual((m['rows'],m['valid'],m['safe'],m['events'],m['invalid']),(3,2,1,1,1))
        self.assertEqual(m['coverage'],2/3)
        self.assertEqual(m['groups'][0]['value'],'Personal Info')
        cells=m['type_details'][0]['axes']
        self.assertEqual(len(cells['topic']),2)
        self.assertTrue(all(c['rows']==3 and c['safe']==1 for c in cells['topic']))
        self.assertEqual(cells['severity_band'][0]['value'],'Low')
        self.assertNotIn('assistant_content',json.dumps(m))
        self.assertNotIn('source_id',json.dumps(m))

    def test_reject_duplicate_missing_unknown_and_mismatched_metadata(self):
        bad=copy.deepcopy(self.rows);bad.append(bad[0])
        with self.assertRaisesRegex(ValueError,'Duplicate'):self.aggregate(bad)
        with self.assertRaisesRegex(ValueError,'complete historical'):self.aggregate(self.rows[:-1])
        bad=copy.deepcopy(self.rows);bad[0]['source_model']='unrecognized-model'
        with self.assertRaisesRegex(ValueError,'Unexpected source model'):self.aggregate(bad)
        bad=copy.deepcopy(self.rows);bad[0]['metadata']['utter_type']='HIQ_a'
        with self.assertRaisesRegex(ValueError,'metadata mismatch'):self.aggregate(bad)

    def test_reject_contradictory_labels_and_changed_paper_totals(self):
        bad=copy.deepcopy(self.rows);bad[0]['is_safe']=False
        with self.assertRaisesRegex(ValueError,'contradictory'):self.aggregate(bad)
        bad=copy.deepcopy(self.rows);bad[2]['predicted_label']='safe'
        with self.assertRaisesRegex(ValueError,'Unclassified output'):self.aggregate(bad)
        bad=copy.deepcopy(self.rows);bad[0]['assistant_content']=''
        with self.assertRaisesRegex(ValueError,'contradictory'):self.aggregate(bad)
        expected=copy.deepcopy(self.expected);expected['GPT-5.4']['Unsafe responses']=0
        with self.assertRaisesRegex(ValueError,'published model counts'):self.aggregate(expected=expected)

    def test_shipped_counts_reconcile_and_only_aggregate_fields_are_exposed(self):
        data=json.loads((ROOT/'paper_assets/data/task3_type_aggregates.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data['models']),12)
        self.assertEqual(sum(m['rows'] for m in data['models'].values()),162624)
        permitted={'rows','valid','events','safe','invalid','unique_sources','valid_sources','coverage','rate','value'}
        for m in data['models'].values():
            self.assertEqual(sum(g['rows'] for g in m['groups']),m['rows'])
            self.assertEqual(sum(g['valid'] for g in m['groups']),m['valid'])
            self.assertEqual(sum(g['events'] for g in m['groups']),m['events'])
            for cell in [*m['groups'],*[c for t in m['type_details'] for cells in t['axes'].values() for c in cells]]:
                self.assertLessEqual(set(cell),permitted)
                self.assertEqual(cell['safe']+cell['events'],cell['valid'])
                self.assertEqual(cell['invalid']+cell['valid'],cell['rows'])
        self.assertEqual(data['models']['GPT-5.4']['invalid'],2733)
