"""Cookie-scope regression; synthetic cookies are not a real HF sign-in."""
from http.cookiejar import Cookie
from pathlib import Path
import sys
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_private_docker_hosting import checked_host, access_cookies


class DockerAccessTests(unittest.TestCase):
    def cookie(self, domain='org-dev.hf.space', path='/', secure=True, rest=None, name='spaces-jwt'):
        return Cookie(0, name, 'SYNTHETIC', None, False, domain, True, False, path, True,
                      secure, None, True, None, None, {'HttpOnly': None} if rest is None else rest, False)

    def test_exact_Docker_cookie_scope(self):
        value = access_cookies([self.cookie()], 'https://org-dev.hf.space')
        self.assertEqual(value[0]['name'], 'spaces-jwt')
        self.assertEqual(value[0]['domain'], 'org-dev.hf.space')

    def test_broad_missing_duplicate_or_nonsecure_cookie_rejected(self):
        for cookies in ([], [self.cookie(), self.cookie()], [self.cookie(domain='.hf.space')],
                        [self.cookie(path='/other')], [self.cookie(secure=False)],
                        [self.cookie(rest={})], [self.cookie(name='hf_jwt_'+'a'*64)]):
            with self.subTest(names=[cookie.name for cookie in cookies]):
                with self.assertRaises(ValueError):
                    access_cookies(cookies, 'https://org-dev.hf.space')

    def test_host_cannot_redirect_credentials(self):
        self.assertEqual(checked_host('https://org-dev.hf.space/'), 'https://org-dev.hf.space')
        for host in ('http://org-dev.hf.space', 'https://user@org-dev.hf.space',
                     'https://org-dev.hf.space.evil.example', 'https://org-dev.hf.space/?token=x',
                     'https://org-dev.hf.space:443', 'https://org-dev.hf.space/other'):
            with self.subTest(host=host):
                with self.assertRaises(ValueError):
                    checked_host(host)


if __name__ == '__main__':
    unittest.main()
