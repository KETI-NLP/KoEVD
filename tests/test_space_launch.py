"""Development launcher configuration checks, not live HF/container evidence."""
import importlib.util
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

import koevd_eval.spaces


class DevelopmentSpaceLaunchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        source = Path(__file__).resolve().parents[1] / 'apps/spaces/launch.py'
        shutil.copyfile(source, self.root / 'launch.py')
        spec = importlib.util.spec_from_file_location('development_space_launch', self.root / 'launch.py')
        self.launch = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.launch)

    def test_provider_configuration_reaches_server_with_ephemeral_storage(self):
        # Credentials here are synthetic. No provider request or server starts.
        environment = {
            'SPACE_HOST': 'keti-nlp-koevd-explorer.hf.space',
            'OAUTH_CLIENT_ID': 'synthetic-client',
            'OAUTH_CLIENT_SECRET': 'synthetic-secret',
            'KOEVD_APP_ORIGIN': 'https://untrusted.example',
            'KOEVD_SUBMISSION_ROOT': '/untrusted/path',
            'KOEVD_ROLES_FILE': '/untrusted/roles.json',
            'KOEVD_POLICY_ROOT': '/untrusted/policy',
            'KOEVD_POLICY_HEAD_SHA256': 'a' * 64,
        }
        with patch.dict(os.environ, environment, clear=True), patch.object(sys, 'argv', []), \
                patch.object(koevd_eval.spaces, 'main') as serve:
            self.launch.main()
            serve.assert_called_once_with()
            self.assertEqual(os.environ['KOEVD_APP_ORIGIN'], 'https://keti-nlp-koevd-explorer.hf.space')
            self.assertEqual(os.environ['KOEVD_OAUTH_ORIGIN'], os.environ['KOEVD_APP_ORIGIN'])
            self.assertEqual(os.environ['KOEVD_SUBMISSION_ROOT'], '/tmp/koevd-development-submissions')
            self.assertEqual(Path(os.environ['KOEVD_ROLES_FILE']), self.root / 'operator-data/roles.json')
            self.assertEqual(Path(os.environ['KOEVD_SPACE_CATALOG']), self.root / 'operator-data/catalog.json')
            self.assertEqual(Path(os.environ['KOEVD_PROTOCOL_REGISTRY']), self.root / 'configs/protocols')
            self.assertNotIn('KOEVD_POLICY_ROOT', os.environ)
            self.assertNotIn('KOEVD_POLICY_HEAD_SHA256', os.environ)
            self.assertIn('may disappear', os.environ['KOEVD_DEPLOYMENT_NOTICE'])
            self.assertEqual(sys.argv, ['koevd-space', '--host', '0.0.0.0', '--port', '7860'])

    def test_invalid_provider_host_prevents_server_start(self):
        for host in (None, 'localhost', 'example.com', 'good.hf.space/other', 'good.hf.space:443'):
            with self.subTest(host=host):
                environment = {} if host is None else {'SPACE_HOST': host}
                with patch.dict(os.environ, environment, clear=True), \
                        patch.object(koevd_eval.spaces, 'main') as serve:
                    with self.assertRaises(ValueError):
                        self.launch.main()
                    serve.assert_not_called()

    def test_cli_token_cannot_substitute_for_native_oauth_credentials(self):
        for oauth in ({}, {'OAUTH_CLIENT_ID': 'synthetic-client'}, {'OAUTH_CLIENT_SECRET': 'synthetic-secret'}):
            with self.subTest(configured_fields=list(oauth)):
                environment = {'SPACE_HOST': 'keti-nlp-koevd-explorer.hf.space', 'HF_TOKEN': 'synthetic-cli-token', **oauth}
                with patch.dict(os.environ, environment, clear=True), \
                        patch.object(koevd_eval.spaces, 'main') as serve:
                    with self.assertRaisesRegex(ValueError, 'OAuth application credentials'):
                        self.launch.main()
                    serve.assert_not_called()

    def test_explicit_public_client_launcher_needs_client_id_and_no_secret(self):
        environment={'SPACE_HOST':'keti-nlp-koevd-explorer.hf.space',
                     'OAUTH_CLIENT_ID':'SYNTHETIC-client','KOEVD_OAUTH_CLIENT_TYPE':'public'}
        with patch.dict(os.environ,environment,clear=True), patch.object(sys,'argv',[]), \
                patch.object(koevd_eval.spaces,'main') as serve:
            self.launch.main();serve.assert_called_once_with()
            self.assertEqual(os.environ['KOEVD_OAUTH_CLIENT_TYPE'],'public')
            self.assertNotIn('OAUTH_CLIENT_SECRET',os.environ)
        for changes in ({'OAUTH_CLIENT_SECRET':'SYNTHETIC-secret'}, {'OAUTH_CLIENT_ID':''},
                        {'KOEVD_OAUTH_CLIENT_TYPE':'automatic'}):
            with self.subTest(configuration=list(changes)), patch.dict(os.environ,{**environment,**changes},clear=True), \
                    patch.object(koevd_eval.spaces,'main') as serve:
                with self.assertRaises(ValueError):self.launch.main()
                serve.assert_not_called()


if __name__ == '__main__':
    unittest.main()
