"""Exact type-conditional Task 3 aggregation without reconstructing intersections."""
from copy import deepcopy
import json
import unittest
from koevd_eval.diagnostics import analyze, task3_type_details
from koevd_eval.profile_cache import numerical_profile
import test_results


def row(sid, label, kind='HIQ', topics=None, status='ok', text='response'):
    return {'sample_id':sid, 'prediction':text, 'api_status':status,
            'measurement':{'label':label}, 'metadata':{'source_id':sid,
            'utterance_type':kind, 'topic':topics or ['privacy'],
            'severity_band':'Benign' if sid=='a' else 'High', 'explicitness':'Implicit'}}


class Task3TypeTests(unittest.TestCase):
    def test_exact_intersections_keep_failures_and_overlapping_topics(self):
        rows=[row('a','unsafe',topics=['privacy','robot']),row('b','safe'),
              row('c','unsafe',topics=['robot'],status='error')]
        before=deepcopy(rows)
        detail=task3_type_details(rows,'subset','core')[0]
        self.assertEqual(rows,before)
        self.assertEqual(detail['type_value'],'HIQ')
        topics={g['value']:g for g in detail['axes']['topic']}
        self.assertEqual((topics['privacy']['events'],topics['privacy']['valid'],topics['privacy']['rows']),(1,2,2))
        self.assertEqual((topics['robot']['events'],topics['robot']['valid'],topics['robot']['rows']),(1,1,2))
        self.assertEqual(topics['robot']['coverage'],.5)
        self.assertEqual(topics['robot']['invalid'],1)
        high=next(g for g in detail['axes']['severity_band'] if g['value']=='High')
        self.assertEqual((high['events'],high['valid'],high['rows']),(0,1,2))
        # Counts from overlapping topics must not be treated as disjoint samples.
        self.assertGreater(sum(g['rows'] for g in topics.values()),len(rows))

    def test_unclassified_and_failed_are_not_safe_and_zero_differs_from_missing(self):
        details=task3_type_details([row('a',None),row('b','unsafe',text=''),
                                   row('c','safe',kind='Other')],'all','all')
        by_type={d['type_value']:d for d in details}
        hiq=by_type['HIQ']['axes']['topic'][0]
        self.assertEqual((hiq['events'],hiq['valid'],hiq['rows']),(0,0,2))
        self.assertIsNone(hiq['rate']);self.assertEqual(hiq['coverage'],0)
        other=by_type['Other']['axes']['topic'][0]
        self.assertEqual(other['rate'],0);self.assertEqual(other['coverage'],1)
        self.assertNotIn('Unknown type',by_type)

    def test_arbitrary_types_missing_metadata_and_unique_source_support(self):
        a=row('a','unsafe',kind=['New robot type','New robot type','HIQ'])
        b=deepcopy(a);b['sample_id']='repeat';b['metadata']['topic']=[]
        b['metadata'].pop('explicitness');b['metadata'].pop('severity_band')
        missing=row('c','safe');missing['metadata'].pop('utterance_type')
        ds={d['type_value']:d for d in task3_type_details([a,b,missing],'all','all')}
        self.assertEqual(set(ds),{'New robot type','HIQ','__missing__'})
        g=ds['New robot type']['axes']['topic'][0]
        self.assertEqual(g['valid_sources'],1)
        self.assertIn('__missing__',[g['value'] for g in ds['HIQ']['axes']['explicitness']])
        self.assertEqual(task3_type_details([],'all','all'),[])

    def test_integrates_every_task3_partition_and_public_projection_is_numeric(self):
        f=test_results.ResultContractTests('test_roundtrip_preserves_union_variants_failures_unknowns_and_privacy')
        f.setUp();self.addCleanup(f.temp.cleanup)
        analysis=analyze(f.document,f.index,resamples=0)
        task=analysis['tasks']['3'];details=task['type_details']
        self.assertTrue(details)
        self.assertTrue(all(set(d)=={'partition_kind','partition_name','type_value','axes'} for d in details))
        for part in task['partitions']:
            self.assertTrue(any(d['partition_kind']==part['kind'] and d['partition_name']==part['name'] for d in details))
        projection=numerical_profile(analysis)
        self.assertEqual(projection['tasks']['3']['type_details'],details)
        encoded=json.dumps(details)
        for secret in ('sample_id','source_id','messages','response','request_id','input_sha256'):
            self.assertNotIn('"'+secret+'"',encoded)
        self.assertNotIn('cases',projection)
