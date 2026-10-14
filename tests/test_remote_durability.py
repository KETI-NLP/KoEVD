"""Fictional conditional object-store checks; never real HF/S3 credentials."""
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import test_results as fixture_module
from koevd_eval.durability import AcknowledgedSubmissionStore
from koevd_eval.remote_durability import HFS3StateObjects, RemoteCheckpointLedger, open_acknowledged_store
from koevd_eval.storage import StorageError
from koevd_eval.submissions import Principal, SubmissionService


class ProviderError(Exception):
    def __init__(self,code):
        super().__init__('SYNTHETIC private credential URL must not surface')
        self.response={'Error':{'Code':code}}


class S3Double:
    def __init__(self):
        self.objects={};self.calls=[];self.fail_head=False;self.lost_head=False;self.denied=False
    def get_object(self,**kwargs):
        if self.denied:raise ProviderError('AccessDenied')
        key=kwargs['Key']
        if key not in self.objects:raise ProviderError('NoSuchKey')
        value=self.objects[key]
        return {'Body':BytesIO(value),'ContentLength':len(value),'ETag':'"'+sha256(value).hexdigest()+'"'}
    def put_object(self,**kwargs):
        key=kwargs['Key'];self.calls.append({k:v for k,v in kwargs.items() if k!='Body'})
        if key.endswith('/HEAD.json') and self.fail_head:raise ProviderError('AccessDenied')
        old=self.objects.get(key)
        if kwargs.get('IfNoneMatch')=='*' and old is not None:raise ProviderError('PreconditionFailed')
        if 'IfMatch' in kwargs and (old is None or kwargs['IfMatch']!='"'+sha256(old).hexdigest()+'"'):
            raise ProviderError('PreconditionFailed')
        body=kwargs['Body'];self.objects[key]=body if isinstance(body,bytes) else body.read()
        if key.endswith('/HEAD.json') and self.lost_head:
            self.lost_head=False;raise ProviderError('ResponseLost')
        return {}
    def list_objects_v2(self,**kwargs):
        return {'Contents':[{'Key':k,'Size':len(v)} for k,v in self.objects.items() if k.startswith(kwargs['Prefix'])],
                'IsTruncated':False}


class RemoteDurabilityTests(unittest.TestCase):
    def setUp(self):
        f=fixture_module.ResultContractTests();f.setUp();self.addCleanup(f.doCleanups)
        self.fixture=f;self.root=f.root;self.s3=S3Double()
        self.api=SimpleNamespace(bucket_info=lambda name:SimpleNamespace(id=name,private=True))
        self.objects=HFS3StateObjects('SYNTHETIC/private-state',api=self.api,client=self.s3)
        self.ledger=RemoteCheckpointLedger(self.objects,initialize_empty=True)
        self.store=AcknowledgedSubmissionStore(self.root/'live',self.ledger)
        self.service=SubmissionService(self.store,{'fixture':f.index},allow_self_reported_summaries=True)
        self.actor=Principal('SYNTHETIC-owner','operator_local')

    def create(self,key='create'):
        return self.service.create(self.actor,self.fixture.document,'fixture',key=key)

    def code(self,expected,operation):
        with self.assertRaises(StorageError) as caught:operation()
        self.assertEqual(caught.exception.code,expected)
        self.assertNotIn('credential',str(caught.exception))

    def reopen(self,destination):
        ledger=RemoteCheckpointLedger(self.objects)
        ledger.restore(destination)
        return SubmissionService(AcknowledgedSubmissionStore(destination,ledger),{'fixture':self.fixture.index},
                                 allow_self_reported_summaries=True)

    def test_confirmed_registration_restores_original_and_history(self):
        state=self.create();restored=self.reopen(self.root/'restored')
        self.assertEqual(restored.result(self.actor,state['id']),self.fixture.document)
        self.assertEqual(restored.history(self.actor,state['id']),self.service.history(self.actor,state['id']))
        heads=[c for c in self.s3.calls if c['Key'].endswith('/HEAD.json')]
        self.assertEqual(heads[0]['IfNoneMatch'],'*')
        self.assertIn('IfMatch',heads[-1])
        self.assertTrue(all('IfNoneMatch' in c for c in self.s3.calls if '/objects/' in c['Key']))

    def test_head_failure_never_acknowledges_and_exact_retry_confirms(self):
        self.s3.fail_head=True
        self.code('durability_unavailable',self.create)
        self.code('durability_unavailable',lambda:self.service.visible_list(self.actor))
        self.s3.fail_head=False
        state=self.create();self.assertEqual(len(self.service.visible_list(self.actor)['items']),1)
        self.assertEqual(self.create(),state)

    def test_lost_head_response_reconciles_same_cut(self):
        before=self.ledger.head()['sequence'];self.s3.lost_head=True
        self.code('durability_unavailable',self.create)
        state=self.create()
        self.assertEqual(self.ledger.head()['sequence'],before+1)
        self.assertEqual(self.create(),state)

    def test_stale_instance_cannot_read_after_another_writer_withdraws(self):
        state=self.create();state=self.service.publish_summary(self.actor,state['id'],consent={
            'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC fixture scope'},
            expected_version=state['version'],reason='SYNTHETIC permission',key='publish')
        second=self.reopen(self.root/'second')
        second.action(self.actor,state['id'],'withdraw',expected_version=state['version'],
                      reason='SYNTHETIC withdrawal',key='withdraw')
        self.code('checkpoint_stale',lambda:self.service.public_summary(state['id']))
        self.code('checkpoint_stale',lambda:self.service.visible_list(self.actor))
        third=self.reopen(self.root/'third')
        self.code('not_found',lambda:third.public_summary(state['id']))
        self.assertEqual(third.result(self.actor,state['id']),self.fixture.document)

    def test_stale_writer_is_fenced_before_a_new_local_mutation(self):
        self.create();second=self.reopen(self.root/'second')
        state=second.visible_list(self.actor)['items'][0]
        second.update_display(self.actor,state['id'],display_name='SYNTHETIC newer',expected_version=state['version'],key='newer')
        self.code('checkpoint_stale',lambda:self.service.update_display(self.actor,state['id'],
            display_name='stale',expected_version=state['version'],key='stale'))

    def test_no_secret_or_cli_fallback_and_target_must_stay_private(self):
        for missing in ('hf_token','access_key_id','secret_access_key'):
            values={'hf_token':'SYNTHETIC','access_key_id':'SYNTHETIC','secret_access_key':'SYNTHETIC'}
            values[missing]=''
            with self.assertRaises(ValueError):HFS3StateObjects.from_secrets('SYNTHETIC/private-state',**values)
        self.api.bucket_info=lambda name:SimpleNamespace(id=name,private=False)
        self.code('checkpoint_target_not_private',self.create)

    def test_access_denial_is_not_empty_initialization(self):
        self.s3.denied=True
        self.code('durability_unavailable',self.ledger.head)

    def test_empty_namespace_requires_explicit_initialization(self):
        objects=HFS3StateObjects('SYNTHETIC/empty',api=self.api,client=S3Double())
        self.code('checkpoint_initialization_required',RemoteCheckpointLedger(objects).head)
        self.assertIsNone(RemoteCheckpointLedger(objects,initialize_empty=True).head())

    def test_orphan_namespace_and_malformed_head_refuse_initialization(self):
        orphan=S3Double();orphan.objects['koevd-state-v1/objects/orphan']=b'partial'
        objects=HFS3StateObjects('SYNTHETIC/empty',api=self.api,client=orphan)
        self.code('checkpoint_initialization_required',RemoteCheckpointLedger(objects,initialize_empty=True).head)
        self.s3.objects['koevd-state-v1/HEAD.json']=b'{"format":"bad"}'
        self.code('checkpoint_integrity',self.ledger.head)

    def test_corrupt_database_never_appears_as_a_restored_store(self):
        self.create();head=self.ledger.head()
        key='koevd-state-v1/objects/'+head['database_sha256']+'.sqlite3'
        raw=self.s3.objects[key];self.s3.objects[key]=raw[:-1]+bytes([raw[-1]^1])
        destination=self.root/'bad-restore'
        self.code('checkpoint_integrity',lambda:self.ledger.restore(destination))
        self.assertFalse(destination.exists())

    def test_existing_object_with_wrong_bytes_is_not_silently_overwritten(self):
        key='koevd-state-v1/objects/'+sha256(b'expected').hexdigest()+'.json'
        self.s3.objects[key]=b'corrupt'
        stage=self.root/'object-test';stage.mkdir()
        self.code('checkpoint_integrity',lambda:self.ledger._immutable(key,b'expected',8,sha256(b'expected').hexdigest(),stage))
        self.assertEqual(self.s3.objects[key],b'corrupt')

    def test_remote_quota_fails_before_acknowledgement(self):
        self.ledger.max_retained_bytes=65536
        self.code('checkpoint_capacity',self.create)

    def test_sequence_budget_stops_new_writes_before_upload(self):
        self.ledger.max_sequence=1
        before=len(self.s3.calls)
        self.code('checkpoint_capacity',self.create)
        self.assertEqual(len(self.s3.calls),before)

    def test_conditional_conflict_is_never_unconditional_overwrite(self):
        old=self.objects.read('koevd-state-v1/HEAD.json',8192)
        self.create();current=deepcopy(self.s3.objects)
        self.assertFalse(self.objects.put('koevd-state-v1/HEAD.json',b'old',etag=old[1]))
        self.assertEqual(self.s3.objects,current)

    def test_runtime_helper_restores_head_but_preserves_divergent_existing_disk(self):
        state=self.create()
        restored=open_acknowledged_store(self.root/'runtime',RemoteCheckpointLedger(self.objects))
        service=SubmissionService(restored,{'fixture':self.fixture.index})
        changed=service.update_display(self.actor,state['id'],display_name='newer',expected_version=state['version'],key='newer')
        self.code('checkpoint_integrity',lambda:open_acknowledged_store(self.root/'live',RemoteCheckpointLedger(self.objects)))
        self.assertTrue(self.store.path.exists())
        newest=open_acknowledged_store(self.root/'newest',RemoteCheckpointLedger(self.objects))
        newest_service=SubmissionService(newest,{'fixture':self.fixture.index})
        self.assertEqual(newest_service.get(self.actor,state['id']),changed)

    def test_runtime_helper_requires_explicit_empty_initialization(self):
        empty=HFS3StateObjects('SYNTHETIC/fresh',api=self.api,client=S3Double())
        self.code('checkpoint_initialization_required',lambda:open_acknowledged_store(self.root/'fresh',RemoteCheckpointLedger(empty)))
        store=open_acknowledged_store(self.root/'fresh',RemoteCheckpointLedger(empty,initialize_empty=True))
        SubmissionService(store,{'fixture':self.fixture.index})
        self.assertIsNotNone(store.last_checkpoint)

    def test_s3_factory_passes_explicit_credentials_and_fixed_hf_gateway(self):
        try:import boto3
        except ImportError:self.skipTest('Optional storage SDK not installed')
        with patch.dict('os.environ',{'HF_ENDPOINT':'https://SYNTHETIC-not-hf.example'}), \
             patch('boto3.client',return_value=self.s3) as client,patch('huggingface_hub.HfApi',return_value=self.api) as api:
            objects=HFS3StateObjects.from_secrets('SYNTHETIC/private-state',hf_token='SYNTHETIC-state-token',
                access_key_id='SYNTHETIC-state-key',secret_access_key='SYNTHETIC-state-secret')
        self.assertEqual(objects.bucket_id,'SYNTHETIC/private-state')
        self.assertEqual(api.call_args.kwargs,{'token':'SYNTHETIC-state-token','endpoint':'https://huggingface.co'})
        supplied=client.call_args.kwargs
        self.assertEqual(supplied['endpoint_url'],'https://s3.hf.co/SYNTHETIC')
        self.assertEqual(supplied['aws_access_key_id'],'SYNTHETIC-state-key')
        self.assertEqual(supplied['aws_secret_access_key'],'SYNTHETIC-state-secret')
        self.assertEqual(supplied['config'].retries,{'total_max_attempts':1})
