"""Credential boundary checks; synthetic cookies do not establish HF login."""
from http.cookiejar import Cookie
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

sys.path.append(str(Path(__file__).resolve().parents[1] / 'scripts'))
from validate_private_static_hosting import checked_host, normalized_index, redirect_index, access_cookies


class PrivateStaticHostingTests(unittest.TestCase):
    def test_host_and_redirect_cannot_escape_credentials_origin(self):
        host = checked_host('org-model.static.hf.space')
        self.assertEqual(host, 'https://org-model.static.hf.space')
        for invalid in ('http://org-model.static.hf.space', 'https://evil.example',
                        'https://org-model.static.hf.space.evil.example',
                        'https://user@org-model.static.hf.space',
                        'https://org-model.static.hf.space/?token=x',
                        'https://org-model.static.hf.space:444'):
            with self.assertRaises(ValueError): checked_host(invalid)
        self.assertEqual(redirect_index(host, SimpleNamespace(status_code=302, headers={'location': '/index.html'})), host+'/index.html')
        for location in ('https://evil.example/index.html', '//evil.example/index.html',
                         '/index.html?token=x', '/index.html#fragment', '/other'):
            with self.assertRaises(ValueError): redirect_index(host, SimpleNamespace(status_code=302, headers={'location': location}))

    def test_normalization_preserves_other_markup_and_rejects_unknown_variables(self):
        injection=b'<script>window.huggingface={variables:{"SPACE_CREATOR_USER_ID":"000000000000000000000000"}};</script>'
        original=b'<head><meta>\n</head>'
        self.assertEqual(normalized_index(b'<head>'+injection+b'<meta>\n</head>'),original)
        for bad in (original, injection+injection, injection.replace(b'SPACE_CREATOR_USER_ID',b'OAUTH_CLIENT_SECRET'),
                    injection.replace(b'000000000000000000000000',b'not-a-creator-id')):
            with self.assertRaises(ValueError):normalized_index(bad)
        self.assertTrue(normalized_index(injection+b'<script>evil()</script>').endswith(b'<script>evil()</script>'))

    def test_cookie_scope_and_properties_are_required(self):
        host='https://org-model.static.hf.space'
        def cookie(domain='org-model.static.hf.space',path='/',secure=True,rest=None):
            return Cookie(0,'hf_jwt_'+'a'*64,'synthetic-cookie',None,False,domain,True,False,
                          path,True,secure,None,True,None,None,rest if rest is not None else {'HttpOnly':None},False)
        self.assertEqual(access_cookies([cookie()],host)[0]['domain'],'org-model.static.hf.space')
        for jar in ([],[cookie(),cookie()],[cookie(domain='.hf.space')],
                    [cookie(path='/other')],[cookie(secure=False)],[cookie(rest={})]):
            with self.assertRaises(ValueError):access_cookies(jar,host)


if __name__ == '__main__': unittest.main()
