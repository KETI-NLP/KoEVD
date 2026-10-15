"""Actual gzip streams, quota cleanup and unchanged result/report bytes."""
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from koevd_eval.transfer import receive_result
from koevd_eval.space_service import AnalysisService,Limits,ServiceError


class Body:
    def __init__(self,raw,chunk=65536):self.raw,self.chunk=raw,chunk
    async def stream(self):
        for i in range(0,len(self.raw),self.chunk):yield self.raw[i:i+self.chunk]


class CompressedBodyTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory();self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name)

    async def test_chunk_boundaries_preserve_exact_utf8_bytes_and_identity_fallback(self):
        raw=json.dumps({'text':'한국어 내용\n'*1000},ensure_ascii=False).encode('utf-8')
        for encoding in ('identity','gzip'):
            wire=gzip.compress(raw,mtime=0) if encoding=='gzip' else raw
            for chunk in (1,7,65536):
                path=self.root/(encoding+str(chunk))
                await receive_result(Body(wire,chunk),path,limit=len(raw)+1024,
                    encoding=encoding,expected_length=len(wire))
                self.assertEqual(path.read_bytes(),raw)

    async def test_expansion_is_bounded_before_oversized_bytes_reach_disk(self):
        wire=gzip.compress(b'x'*1024**2,mtime=0)
        self.assertLess(len(wire),2048)
        path=self.root/'expanded'
        with self.assertRaises(ServiceError) as caught:
            await receive_result(Body(wire),path,limit=2048,encoding='gzip')
        self.assertEqual(caught.exception.status,413)
        self.assertLessEqual(path.stat().st_size,2048)

    async def test_large_valid_member_crosses_output_chunks_at_exact_limit(self):
        raw=bytes(range(256))*2048
        wire=gzip.compress(raw,mtime=0)
        for chunk in (17,len(wire)):
            path=self.root/str(chunk)
            await receive_result(Body(wire,chunk),path,limit=len(raw),encoding='gzip')
            self.assertEqual(path.read_bytes(),raw)

    async def test_damaged_truncated_multiple_members_and_trailing_data_are_rejected(self):
        valid=gzip.compress(b'{"valid":true}',mtime=0)
        bad=[b'not gzip',valid[:-1],valid[:-8]+b'badcrc!!',valid+valid,valid+b'trailing']
        for i,raw in enumerate(bad):
            for chunk in (1,65536):
                with self.subTest(case=i,chunk=chunk),self.assertRaises(ServiceError) as caught:
                    await receive_result(Body(raw,chunk),self.root/f'bad-{i}-{chunk}',limit=4096,encoding='gzip')
                self.assertEqual(caught.exception.code,'invalid_gzip')

    async def test_wire_length_and_unknown_encoding_have_separate_guards(self):
        for encoding in ('identity','gzip'):
            with self.assertRaises(ServiceError) as caught:
                await receive_result(Body(b'x'*33),self.root/encoding,limit=32,encoding=encoding)
            self.assertEqual(caught.exception.status,413)
        with self.assertRaises(ServiceError) as caught:
            await receive_result(Body(b'{}'),self.root/'length',limit=128,encoding='identity',expected_length=3)
        self.assertEqual(caught.exception.code,'length')
        with self.assertRaises(ServiceError):
            await receive_result(Body(b'{}'),self.root/'unknown',limit=128,encoding='br')
        self.assertFalse((self.root/'unknown').exists())


@unittest.skipUnless(importlib.util.find_spec('fastapi') and importlib.util.find_spec('httpx'),'optional HTTP dependencies')
class CompressedHTTPTests(unittest.TestCase):
    def setUp(self):
        from test_spaces import SpaceHTTPTests
        self.fixture=SpaceHTTPTests('test_http_streaming_auth_origin_limits_and_private_headers')
        self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.client=self.fixture.client
        self.headers={**self.fixture.headers,'Content-Type':'application/json','Content-Encoding':'gzip'}
        self.raw=json.dumps(self.fixture.document,ensure_ascii=False).encode('utf-8')

    def test_compressed_upload_preserves_model_original_and_session_isolation(self):
        response=self.client.post('/api/uploads',content=gzip.compress(self.raw,mtime=0),headers=self.headers)
        self.assertEqual(response.status_code,201)
        uid=response.json()['id']
        document,index_id=self.fixture.service.submission_source(self.fixture.token,self.fixture.csrf,uid)
        self.assertEqual(document,self.fixture.document)
        self.assertEqual(index_id,'trusted-demo')
        with self.fixture.service.lock:
            entry=self.fixture.service._lookup(self.fixture.token).uploads[uid]
            self.assertEqual(entry['path'].read_bytes(),self.raw)
        self.assertEqual(self.client.get('/api/session').status_code,401)

    def test_rejected_encoding_and_bad_gzip_release_all_session_reservations(self):
        for body,encoding,status in ((b'bad','gzip',422),(gzip.compress(self.raw)[:-1],'gzip',422),
                                    (gzip.compress(self.raw)+b'x','gzip',422),(b'{}','br',415)):
            response=self.client.post('/api/uploads',content=body,headers={**self.headers,'Content-Encoding':encoding})
            self.assertEqual(response.status_code,status)
            self.assertEqual(self.fixture.service.reserved,0)
            self.assertEqual(self.fixture.service.describe(self.fixture.token)['uploads'],[])
            self.assertFalse(self.fixture.service._lookup(self.fixture.token).busy)

    def test_expanded_http_body_limit_returns_413_and_cleans_staging(self):
        from fastapi.testclient import TestClient
        from koevd_eval.spaces import create_app
        f=self.fixture
        tiny=AnalysisService(f.catalog,f.root/'gzip-tiny',limits=Limits(upload_bytes=2048,
            session_upload_bytes=4096,global_bytes=32768,report_bytes=4096,bootstrap_resamples=0))
        self.addCleanup(tiny.close);token,info=tiny.create_session()
        headers={**self.headers,'Authorization':'Bearer '+token,'X-Koevd-CSRF':info['csrf_token']}
        with TestClient(create_app(tiny,origins=['http://127.0.0.1:7860']),base_url='http://127.0.0.1:7860') as client:
            response=client.post('/api/uploads',content=gzip.compress(b'x'*1024**2,mtime=0),headers=headers)
            self.assertEqual(response.status_code,413)
            self.assertEqual(tiny.reserved,0)
            self.assertFalse(list(tiny.root.rglob('*.upload')))

    def test_download_negotiation_preserves_reports_and_authorization(self):
        f=self.fixture;c=self.client
        uid=c.post('/api/uploads',content=gzip.compress(self.raw),headers=self.headers).json()['id']
        response=c.post('/api/analyses',json={'upload_ids':[uid],'baseline_ids':[]},headers=f.headers)
        job=response.json();self.assertEqual(f.await_job(f.token,job)['status'],'complete')
        url='/api/reports/'+job['id']+'/html'
        identity=c.get(url,headers={**f.headers,'Accept-Encoding':'identity'})
        compressed=c.get(url,headers={**f.headers,'Accept-Encoding':'gzip'})
        self.assertEqual(compressed.content,identity.content)
        self.assertEqual(compressed.headers.get('content-encoding'),'gzip')
        self.assertNotIn('content-encoding',identity.headers)
        self.assertIn('accept-encoding',compressed.headers['vary'].lower())
        self.assertEqual(compressed.headers['cache-control'],'no-store')
        self.assertIn('attachment',compressed.headers['content-disposition'])
        self.assertEqual(c.get(url,headers={'Accept-Encoding':'gzip'}).status_code,401)
        ranged=c.get(url,headers={**f.headers,'Accept-Encoding':'gzip','Range':'bytes=0-63'})
        self.assertEqual(ranged.status_code,206)
        self.assertEqual(ranged.content,identity.content[:64])
        self.assertNotIn('content-encoding',ranged.headers)

    def test_public_reports_are_compressed_but_identity_and_raw_public_paths_are_excluded(self):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from koevd_eval.transfer import ResultCompressionMiddleware
        app=FastAPI();app.add_middleware(ResultCompressionMiddleware)
        @app.get('/api/public/submissions/synthetic/profile')
        @app.get('/api/identity')
        @app.get('/api/public/submissions/synthetic/result')
        def sample():return {'synthetic':'not a real credential or model result '*1000}
        with TestClient(app) as client:
            response=client.get('/api/public/submissions/synthetic/profile',headers={'Accept-Encoding':'gzip'})
            self.assertEqual(response.headers.get('content-encoding'),'gzip')
            for path in ('/api/identity','/api/public/submissions/synthetic/result'):
                self.assertNotIn('content-encoding',client.get(path,headers={'Accept-Encoding':'gzip'}).headers)
