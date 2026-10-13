"""Synthetic launcher contracts; no listening server or actual provider login."""
import os
import sys
import unittest
from unittest.mock import patch

import koevd_eval.spaces as spaces
import test_spaces


class OAuthClientConfigurationTests(unittest.TestCase):
    write=test_spaces.SpaceServiceTests.write
    sha=test_spaces.SpaceServiceTests.sha

    def setUp(self):
        test_spaces.SpaceServiceTests.setUp(self)
        self.write('roles.json',{'reviewers':[],'admins':[]})
        self.arguments=['koevd-space','--catalog',str(self.root/'catalog.json'),'--demo',
                        '--session-root',str(self.root/'cli-sessions'),
                        '--submission-root',str(self.root/'submissions'),
                        '--roles-file',str(self.root/'roles.json')]

    def test_explicit_cli_and_environment_public_mode_reach_registration(self):
        for cli,env in ((['--oauth-client-type','public'],{}),
                        ([],{'KOEVD_OAUTH_CLIENT_TYPE':'public'}),
                        (['--oauth-client-type','public'],{'KOEVD_OAUTH_CLIENT_TYPE':'confidential'})):
            with self.subTest(cli=cli,env=env), patch.dict(os.environ,{'OAUTH_CLIENT_ID':'SYNTHETIC-client',**env},clear=True), \
                    patch.object(sys,'argv',self.arguments+cli), patch.object(spaces,'create_app') as app, \
                    patch('uvicorn.run') as serve:
                spaces.main();serve.assert_called_once()
                provider=app.call_args.kwargs['registration'].identities.provider
                self.assertEqual(provider.client_type,'public');self.assertEqual(provider.client_secret,'')

    def test_confidential_default_keeps_secret_and_public_misconfiguration_fails_before_server(self):
        with patch.dict(os.environ,{'OAUTH_CLIENT_ID':'SYNTHETIC-client','OAUTH_CLIENT_SECRET':'SYNTHETIC-secret'},clear=True), \
                patch.object(sys,'argv',self.arguments), patch.object(spaces,'create_app') as app, patch('uvicorn.run') as serve:
            spaces.main();serve.assert_called_once()
            self.assertEqual(app.call_args.kwargs['registration'].identities.provider.client_type,'confidential')
        for env in ({'OAUTH_CLIENT_ID':'SYNTHETIC-client'},
                    {'OAUTH_CLIENT_ID':'SYNTHETIC-client','KOEVD_OAUTH_CLIENT_TYPE':'public','OAUTH_CLIENT_SECRET':'SYNTHETIC-secret'},
                    {'KOEVD_OAUTH_CLIENT_TYPE':'public','HF_TOKEN':'SYNTHETIC-cli-token'},
                    {'OAUTH_CLIENT_ID':'SYNTHETIC-client','KOEVD_OAUTH_CLIENT_TYPE':'automatic'}):
            with self.subTest(configured_fields=list(env)), patch.dict(os.environ,env,clear=True), \
                    patch.object(sys,'argv',self.arguments), patch('uvicorn.run') as serve:
                with self.assertRaises(ValueError):spaces.main()
                serve.assert_not_called()

    def test_public_configuration_without_submission_store_is_rejected(self):
        argv=['koevd-space','--catalog',str(self.root/'catalog.json'),'--demo',
              '--session-root',str(self.root/'cli-sessions'),'--oauth-client-type','public']
        with patch.dict(os.environ,{},clear=True), patch.object(sys,'argv',argv), patch('uvicorn.run') as serve:
            with self.assertRaises(SystemExit) as caught:spaces.main()
            self.assertEqual(caught.exception.code,2);serve.assert_not_called()


if __name__=='__main__':unittest.main()
