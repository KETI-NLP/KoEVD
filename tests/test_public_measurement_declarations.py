from copy import deepcopy
import json
import unittest

import test_measurement_conditions
from koevd_eval.measurement_conditions import public_declaration
from koevd_eval.results import _seal
from koevd_eval.storage import LocalSubmissionStore
from koevd_eval.submissions import Principal, SubmissionService
from koevd_eval.public_exports import projection


class PublicMeasurementDeclarationTests(unittest.TestCase):
    def setUp(self):
        self.f=test_measurement_conditions.PortableMeasurementTests();self.f.setUp();self.addCleanup(self.f.doCleanups)

    def test_condition_digest_excludes_trace_identity_and_response_dependent_counts(self):
        evidence=self.f.document['run']['measurements']['4']
        changed=deepcopy(evidence);changed['conditions']['observation']['trace_sha256']='f'*64
        changed['conditions']['observation']['counts']['budget_unknown']+=1
        self.assertEqual(public_declaration(evidence),public_declaration(changed))
        changed['batch_size']=4
        self.assertNotEqual(public_declaration(evidence)['conditions_sha256'],public_declaration(changed)['conditions_sha256'])
        self.assertEqual(public_declaration(None),{'status':'unknown','conditions':None,'conditions_sha256':None})

    def test_public_projection_discloses_task_conditions_without_changing_metric_groups(self):
        f=self.f
        service=SubmissionService(LocalSubmissionStore(f.root/'declaration-store'),{'fixture':f.index},allow_self_reported_summaries=True)
        actor=Principal('SYNTHETIC-owner','operator_local')
        def publish(document,key):
            state=service.create(actor,document,'fixture',key=key+'-create')
            return service.publish_summary(actor,state['id'],expected_version=state['version'],reason='SYNTHETIC conditions test',key=key+'-publish',consent={'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC fixture only'})
        left=publish(f.document,'left')
        changed=deepcopy(f.document);changed.pop('content_sha256');changed['run']['model']['id']='SYNTHETIC-other';changed['run']['measurements']['4']['batch_size']=4
        right=publish(_seal(changed),'right')
        board=service.public_leaderboard();pubs={p['submission_id']:p for p in board['publications']}
        a,b=pubs[left['id']],pubs[right['id']]
        self.assertEqual(a['measurements']['3'],b['measurements']['3'])
        self.assertNotEqual(a['measurements']['4']['conditions_sha256'],b['measurements']['4']['conditions_sha256'])
        self.assertEqual(a['measurements']['4']['conditions']['batch_size'],2)
        self.assertEqual(b['measurements']['4']['conditions']['batch_size'],4)
        # Generation-based cohorts remain stable; Task-specific UI filtering is separate.
        cohorts={row['metric']['cohort_sha256'] for row in board['excluded'] if row['metric']['task']==4}
        self.assertEqual(len(cohorts),1)
        profile=service.public_profile(left['id'])
        self.assertEqual(profile['measurements'],a['measurements'])
        self.assertEqual(projection(profile)['measurements'],a['measurements'])
        raw=json.dumps(board)
        for private in ('trace_sha256','parameter_dtype_elements','input_file_sha256','fixture response','"cases"','"owner"'):
            self.assertNotIn(private,raw)
