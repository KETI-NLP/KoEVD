"""Public reference projection must preserve analysis and isolate personal text."""
from copy import deepcopy
import json
import unittest

from koevd_eval.public_disclosure import disclose_references, WITHHELD


class PublicDisclosureTests(unittest.TestCase):
    def profile(self, artifact):
        return {'artifact_sha256':artifact,'run':{'id':'private-run','created_at':'private-time','migration':'private/path',
                'model':{'id':'Example/model'},'generation':{'temperature':0}},
                'interpretation':['Original limitation'],
                'tasks':{'5':{'numerator':3,'denominator':10}},'charts':[{'count':3}],
                'quality':{'length_limit':2},'cases':[{'task':5,'run_id':'private-run',
                'messages':[{'role':'user','content':'private-prompt'}],
                'response':{'text':'private-response','sha256':'original-hash',
                            'reasoning_content':'private-reasoning','refusal':'private-refusal',
                            'request_id':'private-request','response_id':'private-response-id',
                            'server_model':'private-model','execution':{'secret':'private-execution'}},
                'metadata':{'severity_band':'Benign','internal_actor':'private-actor',
                            'choices':[{'text':'private-choice'}]},
                'gold':{'available_tools':['mock_action'],'unsafe_tools':['mock_action'],
                        'instructions':'private-instructions'},
                'parsed':{'decision':'call_tool','tool_name':'mock_action','arguments':'private-arguments'},
                'measurement':{'value':None,'status':'not_applicable'},'valid':True,'event':True}]}

    def test_no_raw_reference_fields_or_original_mutation_and_metrics_preserved(self):
        original={'runs':[self.profile('ref'),self.profile('personal')],'comparisons':[{'events':3}]}
        before=deepcopy(original)
        result=disclose_references(original,['ref'])
        self.assertEqual(original,before)
        self.assertEqual(result['runs'][1],before['runs'][1])
        ref=result['runs'][0]
        for key in ('tasks','charts','quality'):
            self.assertEqual(ref[key],before['runs'][0][key])
        self.assertEqual(result['comparisons'],before['comparisons'])
        self.assertNotIn('private-',json.dumps(ref))
        self.assertNotIn('private/path',json.dumps(ref))
        self.assertEqual(ref['cases'][0]['response']['sha256'],'original-hash')
        self.assertEqual(ref['cases'][0]['response']['text'],WITHHELD)
        self.assertEqual(ref['cases'][0]['parsed'],{'decision':'call_tool','tool_name':'mock_action'})
        self.assertTrue(ref['disclosure']['metrics_calculated_from_original'])
        self.assertFalse(ref['disclosure']['raw_text_public'])

    def test_strategy_filter_labels_retained_without_freeform_measurement_text(self):
        p=self.profile('ref');case=p['cases'][0];case['task']=4
        case['measurement']={'value':{'strategies':['a_boundary setting'],'raw':'private-classifier-text'},'status':'ok'}
        case['parsed']=deepcopy(case['measurement']['value'])
        projected=disclose_references({'runs':[p]},['ref'])['runs'][0]['cases'][0]
        self.assertEqual(projected['measurement']['value'],{'strategies':['a_boundary setting']})
        self.assertEqual(projected['parsed'],{'strategies':['a_boundary setting']})

    def test_no_selected_reference_preserves_the_full_report(self):
        original={'runs':[self.profile('personal')],'comparisons':[]}
        self.assertEqual(disclose_references(original,[]),original)

    def test_comparison_reference_run_id_is_projected_without_changing_values(self):
        original={'runs':[self.profile('ref')],'comparisons':[{'left_artifact':'personal','right_artifact':'ref',
                  'left_run_id':'personal-id','right_run_id':'private-run','tasks':[{'numerator':3}]}]}
        comparison=disclose_references(original,['ref'])['comparisons'][0]
        self.assertEqual(comparison['left_run_id'],'personal-id')
        self.assertEqual(comparison['right_run_id'],'reference-ref')
        self.assertEqual(comparison['tasks'],original['comparisons'][0]['tasks'])
