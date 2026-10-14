"""Atomic initial reference intake and restored publication; fictional CPU data."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

import test_spaces as fixture_module
from test_remote_durability import S3Double
from types import SimpleNamespace
from koevd_eval.results import _seal
from koevd_eval.space_service import InputCatalog
from koevd_eval.remote_durability import HFS3StateObjects,RemoteCheckpointLedger
from koevd_eval.registration_runtime import bootstrap_registered_service,REFERENCE_OWNER
from koevd_eval.submissions import Principal,SubmissionService
from koevd_eval.durability import AcknowledgedSubmissionStore
from koevd_eval.storage import StorageError


class RegistrationBootstrapTests(unittest.TestCase):
    def setUp(self):
        f=fixture_module.SpaceServiceTests();f.setUp();self.addCleanup(f.doCleanups)
        self.fixture=f;self.root=f.root
        second=deepcopy(f.document);second['run']['model']['id']='SYNTHETIC-second'
        f.write('second.json',_seal({k:v for k,v in second.items() if k!='content_sha256'}))
        config=deepcopy(f.config);config['baselines'].append({**config['baselines'][0],
            'id':'second','label':'SYNTHETIC second','path':'second.json','sha256':f.sha('second.json')})
        f.write('pair-catalog.json',config)
        self.catalog=InputCatalog(self.root/'pair-catalog.json',allow_synthetic=True)
        self.s3=S3Double();self.objects=HFS3StateObjects('SYNTHETIC/state',
            api=SimpleNamespace(bucket_info=lambda name:SimpleNamespace(id=name,private=True)),client=self.s3)
        self.ledger=RemoteCheckpointLedger(self.objects,initialize_empty=True)
        self.roles={'reviewers':[],'admins':[]}
    def boot(self,destination):
        return bootstrap_registered_service(self.catalog,self.ledger,destination,roles=self.roles)
    def code(self,expected,fn):
        with self.assertRaises(StorageError) as caught:fn()
        self.assertEqual(caught.exception.code,expected)

    def test_two_references_are_one_acknowledged_cut_with_truthful_origin(self):
        service=self.boot(self.root/'first')
        self.assertEqual(self.ledger.head()['sequence'],1)
        page=service.public_page();self.assertEqual(len(page['items']),2)
        for item in page['items']:
            self.assertEqual(item['origin'],'operator_reference')
            summary=service.public_summary(item['submission_id'])
            self.assertEqual(summary['publication_environment'],'hosted_candidate')
            self.assertEqual(summary['verification']['generation'],'user_reported')
            self.assertFalse(summary['official_rank_eligible'])
            self.code('responses_private',lambda item=item:service.public_result(item['submission_id']))
        pair=service.public_comparison(page['items'][0]['submission_id'],page['items'][1]['submission_id'])
        self.assertFalse(pair['raw_cases_included'])

    def test_restart_preserves_ids_and_history_without_new_checkpoint(self):
        first=self.boot(self.root/'first');page=first.public_page();head=self.ledger.head()
        actor=Principal(REFERENCE_OWNER,'operator_local')
        history={item['submission_id']:first.history(actor,item['submission_id']) for item in page['items']}
        second=self.boot(self.root/'second')
        self.assertEqual(second.public_page(),page);self.assertEqual(self.ledger.head(),head)
        for sid,value in history.items():self.assertEqual(second.history(actor,sid),value)

    def test_withdrawn_operator_reference_is_not_republished_by_restart(self):
        first=self.boot(self.root/'first');actor=Principal(REFERENCE_OWNER,'operator_local')
        item=first.visible_list(actor)['items'][0]
        first.action(actor,item['id'],'withdraw',expected_version=item['version'],reason='SYNTHETIC',key='withdraw')
        head=self.ledger.head();second=self.boot(self.root/'second')
        self.assertEqual(len(second.public_page()['items']),1)
        self.code('not_found',lambda:second.public_summary(item['id']))
        self.assertEqual(self.ledger.head(),head)

    def test_changed_second_reference_prevents_any_first_upload(self):
        path=self.root/'second.json';path.write_bytes(path.read_bytes()+b' ')
        self.code('reference_changed',lambda:self.boot(self.root/'first'))
        self.assertEqual(self.s3.calls,[])

    def test_existing_state_without_reference_intake_is_not_automatically_changed(self):
        store=AcknowledgedSubmissionStore(self.root/'old',self.ledger)
        SubmissionService(store,{'trusted-demo':self.fixture.index})
        head=self.ledger.head()
        self.code('reference_intake_required',lambda:self.boot(self.root/'fresh'))
        self.assertEqual(self.ledger.head(),head)

    def test_initialization_requires_explicit_operator_opt_in(self):
        self.ledger.initialize_empty=False
        self.code('checkpoint_initialization_required',lambda:self.boot(self.root/'first'))
        self.assertEqual(self.s3.calls,[])


class RegisteredLauncherConfigurationTests(unittest.TestCase):
    def setUp(self):
        path=Path(__file__).resolve().parents[1]/'apps/spaces/registered_launch.py'
        spec=importlib.util.spec_from_file_location('registered_launcher',path)
        self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)
        self.env={'SPACE_HOST':'keti-nlp-SYNTHETIC.hf.space','OAUTH_CLIENT_ID':'SYNTHETIC-app',
            'OAUTH_CLIENT_SECRET':'SYNTHETIC-secret','KOEVD_REFERENCE_TOKEN':'SYNTHETIC-read',
            'KOEVD_STATE_TOKEN':'SYNTHETIC-state','KOEVD_STATE_ACCESS_KEY_ID':'SYNTHETIC-key',
            'KOEVD_STATE_SECRET_ACCESS_KEY':'SYNTHETIC-s3-secret','KOEVD_STATE_BUCKET':'SYNTHETIC/state'}
    def test_native_oauth_and_scoped_state_are_explicit(self):
        settings=self.module.captured_configuration(self.env)
        self.assertEqual(settings['origin'],'https://keti-nlp-synthetic.hf.space')
        self.assertEqual(settings['provider'].client_type,'confidential')
        self.assertFalse(settings['initialize'])
        self.assertNotIn('OAUTH_CLIENT_SECRET',settings)
        self.assertEqual(settings['environment'],'hosted_candidate')
    def test_no_partial_configuration_role_reuse_or_provider_redirect(self):
        cases=[{**self.env,'OAUTH_CLIENT_SECRET':''},{**self.env,'KOEVD_STATE_TOKEN':''},
            {**self.env,'KOEVD_STATE_TOKEN':self.env['KOEVD_REFERENCE_TOKEN']},
            {**self.env,'KOEVD_STATE_BUCKET':'KETI-NLP/KoEVD-Platform-Backups'},
            {**self.env,'KOEVD_STATE_BUCKET':'https://SYNTHETIC.bad/state'},
            {**self.env,'OPENID_PROVIDER_URL':'https://SYNTHETIC.bad'},
            {**self.env,'KOEVD_STATE_INITIALIZE':'true'},{**self.env,'SPACE_HOST':'SYNTHETIC.bad'}]
        for env in cases:
            with self.subTest(changes=[k for k in env if env[k]!=self.env.get(k)]),self.assertRaises(ValueError):
                self.module.captured_configuration(env)
