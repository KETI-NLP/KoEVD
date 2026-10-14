"""CLI assembly with fictional OAuth values and local S3 doubles only."""
import contextlib
import io
import json
import unittest
from unittest.mock import patch

import test_spaces as fixture_module
from test_remote_durability import S3Double
from koevd_eval.remote_durability import HFS3StateObjects, RemoteCheckpointLedger
from koevd_eval.spaces import main
from types import SimpleNamespace


class RemoteStateCLITests(unittest.TestCase):
    def setUp(self):
        f=fixture_module.SpaceServiceTests();f.setUp();self.addCleanup(f.doCleanups)
        self.fixture=f;self.root=f.root
        self.roles=self.root/'roles.json';self.roles.write_text(json.dumps({'reviewers':[],'admins':[]}),encoding='utf-8')
        self.s3=S3Double()
        self.objects=HFS3StateObjects('SYNTHETIC/private-state',
            api=SimpleNamespace(bucket_info=lambda name:SimpleNamespace(id=name,private=True)),client=self.s3)
        self.env={'OAUTH_CLIENT_ID':'SYNTHETIC-app','OAUTH_CLIENT_SECRET':'SYNTHETIC-app-secret',
            'OPENID_PROVIDER_URL':'https://huggingface.co','KOEVD_STATE_BUCKET':'',
            'KOEVD_STATE_TOKEN':'SYNTHETIC-state-token','KOEVD_STATE_ACCESS_KEY_ID':'SYNTHETIC-state-key',
            'KOEVD_STATE_SECRET_ACCESS_KEY':'SYNTHETIC-state-secret','HF_TOKEN':'SYNTHETIC-admin-do-not-use'}
        self.base=['koevd-space','--catalog',str(self.root/'catalog.json'),'--demo',
            '--session-root',str(self.root/'cli-sessions'),'--origin','http://127.0.0.1',
            '--roles-file',str(self.roles),'--submission-root',str(self.root/'live')]

    def test_explicit_remote_cli_initializes_and_restores_same_head(self):
        args=self.base+['--state-bucket','SYNTHETIC/private-state','--initialize-state','--self-reported-summaries']
        with patch.dict('os.environ',self.env),patch('sys.argv',args), \
             patch.object(HFS3StateObjects,'from_secrets',return_value=self.objects) as factory, \
             patch('uvicorn.run') as server:
            main()
        self.assertEqual(server.call_count,1)
        self.assertEqual(factory.call_args.kwargs,{'hf_token':'SYNTHETIC-state-token',
            'access_key_id':'SYNTHETIC-state-key','secret_access_key':'SYNTHETIC-state-secret'})
        head=RemoteCheckpointLedger(self.objects).head()
        self.assertEqual(head['sequence'],1)
        second=self.root/'restored';args=self.base+['--state-bucket','SYNTHETIC/private-state']
        args[args.index('--submission-root')+1]=str(second)
        with patch.dict('os.environ',self.env),patch('sys.argv',args), \
             patch.object(HFS3StateObjects,'from_secrets',return_value=self.objects),patch('uvicorn.run'):
            main()
        self.assertTrue((second/'submissions.sqlite3').exists())
        self.assertEqual(RemoteCheckpointLedger(self.objects).head(),head)

    def test_partial_and_conflicting_configuration_never_opens_remote_clients(self):
        cases=[self.base+['--initialize-state'],self.base+['--state-prefix','custom'],
               self.base+['--state-bucket','SYNTHETIC/private-state','--checkpoint-root',str(self.root/'retained')]]
        for args in cases:
            with self.subTest(args=args[-2:]),patch.dict('os.environ',self.env),patch('sys.argv',args), \
                 patch.object(HFS3StateObjects,'from_secrets') as factory,patch('uvicorn.run') as server, \
                 contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):main()
                factory.assert_not_called();server.assert_not_called()

    def test_missing_state_secrets_never_use_cached_admin_token(self):
        env={**self.env,'KOEVD_STATE_SECRET_ACCESS_KEY':''}
        args=self.base+['--state-bucket','SYNTHETIC/private-state','--initialize-state']
        with patch.dict('os.environ',env),patch('sys.argv',args),patch('uvicorn.run') as server:
            with self.assertRaisesRegex(ValueError,'no cached fallback'):main()
            server.assert_not_called()
        self.assertFalse((self.root/'live').exists())
