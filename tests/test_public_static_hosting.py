"""Anonymous preflight must not silently accept private or changed deployments."""
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_public_static_hosting import anonymous_access


class PublicStaticHostingTests(unittest.TestCase):
    def test_anonymous_access_has_no_credentials(self):
        info = SimpleNamespace(private=False, sdk='static', sha='a'*40,
                               host='org-model.static.hf.space')
        access = anonymous_access(info, 'a'*40)
        self.assertEqual(access, {'origin': 'https://org-model.static.hf.space',
                                 'revision': 'a'*40, 'mode': 'anonymous', 'cookies': []})

    def test_private_wrong_revision_or_runtime_is_rejected(self):
        for private, sdk, sha in ((True, 'static', 'a'*40), (False, 'docker', 'a'*40),
                                  (False, 'static', 'b'*40)):
            with self.subTest(private=private, sdk=sdk, sha=sha):
                with self.assertRaises(ValueError):
                    anonymous_access(SimpleNamespace(private=private, sdk=sdk, sha=sha,
                                      host='org-model.static.hf.space'), 'a'*40)

    def test_anonymous_host_still_rejects_queries_credentials_and_other_origins(self):
        for host in ('https://evil.example', 'https://user@org-model.static.hf.space',
                     'https://org-model.static.hf.space/?token=unexpected'):
            with self.subTest(host=host):
                with self.assertRaises(ValueError):
                    anonymous_access(SimpleNamespace(private=False, sdk='static', sha='a'*40,
                                      host=host), 'a'*40)


if __name__ == '__main__':
    unittest.main()
