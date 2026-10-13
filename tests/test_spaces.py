from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest

from koevd_eval.diagnostics import analyze_many, write_analysis
from koevd_eval.results import _seal
from koevd_eval.space_service import AnalysisService, InputCatalog, Limits, ServiceError
import test_results


class SpaceServiceTests(unittest.TestCase):
    def setUp(self):
        f=test_results.ResultContractTests('test_roundtrip_preserves_union_variants_failures_unknowns_and_privacy');f.setUp()
        self.addCleanup(f.temp.cleanup);self.index=f.index;self.document=f.document
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        for name,value in [('index.json',self.index),('result.json',self.document)]:self.write(name,value)
        self.config={'schema_version':'koevd-space-catalog-v1','indexes':[{'id':'trusted-demo','label':'SYNTHETIC input set','mode':'synthetic_demo','path':'index.json','sha256':self.sha('index.json')}],
                     'baselines':[{'id':'reference','label':'SYNTHETIC reference','index_id':'trusted-demo','path':'result.json','sha256':self.sha('result.json'),'scope':'synthetic_demo','publication_evidence':None}]}
        self.write('catalog.json',self.config)
        self.catalog=InputCatalog(self.root/'catalog.json',allow_synthetic=True)
        self.clock=[0.]
        self.service=AnalysisService(self.catalog,self.root/'sessions',limits=Limits(bootstrap_resamples=0),clock=lambda:self.clock[0]);self.addCleanup(self.service.close)
        self.token,self.info=self.service.create_session();self.csrf=self.info['csrf_token']
    def write(self,name,value):(self.root/name).write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
    def sha(self,name):return hashlib.sha256((self.root/name).read_bytes()).hexdigest()
    def upload(self,document=None,token=None,csrf=None):
        token=token or self.token;csrf=csrf or self.csrf
        s,path=self.service.begin_upload(token,csrf);path.write_text(json.dumps(document or self.document,ensure_ascii=False),encoding='utf-8')
        return self.service.finish_upload(token,s,path)
    def await_job(self,token,job):
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            value=self.service.job(token,job['id'])
            if value['status'] in ('complete','failed'):return value
            time.sleep(.01)
        self.fail('Analysis job did not finish')

    def test_operator_catalog_is_pinned_and_demo_cannot_auto_promote(self):
        with self.assertRaises(ValueError):InputCatalog(self.root/'catalog.json')
        self.config['indexes'][0]['mode']='standard';self.write('catalog.json',self.config)
        with self.assertRaises(ValueError):InputCatalog(self.root/'catalog.json',allow_synthetic=True)
        self.config['indexes'][0]['mode']='operator_custom';self.config['baselines']=[];self.write('catalog.json',self.config)
        c=InputCatalog(self.root/'catalog.json');self.assertFalse(c.public()['public_registration_enabled'])
        self.write('index.json',{'tampered':True})
        with self.assertRaises(ValueError):InputCatalog(self.root/'catalog.json')

    def test_unknown_indexes_gold_scores_and_duplicate_json_rejected(self):
        for change in ('input_index_sha256','gold','scores'):
            d=deepcopy(self.document)
            if change=='input_index_sha256':d[change]='a'*64
            else:d[change]={'fake':100}
            d=_seal({k:v for k,v in d.items() if k!='content_sha256'})
            with self.assertRaises(ServiceError):self.upload(d)
        s,path=self.service.begin_upload(self.token,self.csrf);path.write_bytes(b'{"a":1,"a":2}')
        with self.assertRaises(ServiceError):self.service.finish_upload(self.token,s,path)
        self.assertEqual(self.service.describe(self.token)['uploads'],[]);self.assertFalse(s.busy);self.assertEqual(self.service.reserved,0)

    def test_session_isolation_secret_hashing_csrf_and_paths(self):
        entry=self.upload();other,info=self.service.create_session()
        self.assertEqual(self.service.describe(other)['uploads'],[])
        with self.assertRaises(ServiceError):self.service.delete_upload(other,info['csrf_token'],entry['id'])
        with self.assertRaises(ServiceError):self.service.submit_analysis(other,info['csrf_token'],[entry['id']],[])
        with self.assertRaises(ServiceError):self.service.begin_upload(self.token,'wrong')
        with self.assertRaises(ServiceError):self.service.report_file(self.token,'../../outside','html')
        self.assertNotIn(self.token,self.service.sessions)
        self.assertNotIn(str(self.root),json.dumps(self.service.describe(self.token)))
        self.assertNotIn('path',entry)

    def test_shared_engine_equality_download_authorization_and_deletion(self):
        entry=self.upload();job=self.service.submit_analysis(self.token,self.csrf,[entry['id']],[])
        self.assertEqual(self.await_job(self.token,job)['status'],'complete')
        actual=json.loads(self.service.report_file(self.token,job['id'],'profile').read_text(encoding='utf-8'))
        expected=analyze_many([(self.document,self.index)],resamples=0,seed=1729)
        expected=write_analysis(expected,self.root/'local')
        self.assertEqual(actual,expected)
        other,info=self.service.create_session()
        with self.assertRaises(ServiceError):self.service.job(other,job['id'])
        with self.assertRaises(ServiceError):self.service.report_file(other,job['id'],'profile')
        self.service.delete_upload(self.token,self.csrf,entry['id'])
        with self.assertRaises(ServiceError):self.service.report_file(self.token,job['id'],'profile')
        self.assertEqual(self.service.describe(self.token)['uploads'],[])

    def test_reference_consent_duplicate_artifact_and_baseline_tamper(self):
        entry=self.upload()
        with self.assertRaises(ServiceError):self.service.submit_analysis(self.token,self.csrf,[entry['id']],['reference'])
        self.config['baselines'][0]['scope']='actual_target_outputs';self.write('catalog.json',self.config)
        with self.assertRaises(ValueError):InputCatalog(self.root/'catalog.json',allow_synthetic=True)
        # Baseline bytes checked again before an analysis; operator file mutation is not accepted.
        d=deepcopy(self.document);d['run']['id']='second-run';d=_seal({k:v for k,v in d.items() if k!='content_sha256'})
        other=self.upload(d);(self.root/'result.json').write_bytes(b'{}')
        job=self.service.submit_analysis(self.token,self.csrf,[other['id']],['reference'])
        self.assertEqual(self.await_job(self.token,job)['status'],'failed')
        self.assertNotIn(str(self.root),self.service.job(self.token,job['id'])['error'])

    def test_expiry_cleanup_capacity_busy_and_malformed_selection(self):
        entry=self.upload()
        for ids in ([],[['unhashable']],['missing','missing']):
            with self.assertRaises(ServiceError):self.service.submit_analysis(self.token,self.csrf,ids,[])
        s,path=self.service.begin_upload(self.token,self.csrf)
        with self.assertRaises(ServiceError):self.service.delete_session(self.token,self.csrf)
        self.clock[0]=self.service.limits.ttl_seconds+1;self.service.cleanup();self.assertTrue(s.directory.exists())
        self.service.abort_upload(s,path);self.assertFalse(s.directory.exists())
        with self.assertRaises(ServiceError):self.service.describe(self.token)
        self.assertEqual(self.service.reserved,0)

    def test_concurrent_session_analysis_queue_busy_and_recovery(self):
        import threading
        from unittest.mock import patch
        entry=self.upload();second,info=self.service.create_session();entry2=self.upload(token=second,csrf=info['csrf_token'])
        third,third_info=self.service.create_session();entry3=self.upload(token=third,csrf=third_info['csrf_token'])
        started=threading.Event();release=threading.Event()
        original=analyze_many
        def hold(*args,**kwargs):started.set();release.wait(5);return original(*args,**kwargs)
        with patch('koevd_eval.space_service.analyze_many',hold):
            first=self.service.submit_analysis(self.token,self.csrf,[entry['id']],[])
            self.assertTrue(started.wait(2))
            with self.assertRaises(ServiceError):self.service.begin_upload(self.token,self.csrf)
            second_job=self.service.submit_analysis(second,info['csrf_token'],[entry2['id']],[])
            with self.assertRaises(ServiceError) as exc:self.service.submit_analysis(third,third_info['csrf_token'],[entry3['id']],[])
            self.assertEqual(exc.exception.code,'analysis_capacity')
            release.set()
            self.assertEqual(self.await_job(self.token,first)['status'],'complete');self.assertEqual(self.await_job(second,second_job)['status'],'complete')
        self.assertEqual(self.service.reserved,0)
        third_job=self.service.submit_analysis(third,third_info['csrf_token'],[entry3['id']],[])
        self.assertEqual(self.await_job(third,third_job)['status'],'complete')

    def test_bounded_bytes_and_failed_upload_release_reservation(self):
        self.service.close()
        tiny=AnalysisService(self.catalog,self.root/'tiny',limits=Limits(upload_bytes=32,session_upload_bytes=64,global_bytes=4096,report_bytes=512,max_uploads=1,max_sessions=1,bootstrap_resamples=0))
        self.addCleanup(tiny.close);token,info=tiny.create_session()
        with self.assertRaises(ServiceError):tiny.create_session()
        s,path=tiny.begin_upload(token,info['csrf_token']);path.write_bytes(b'x'*33)
        with self.assertRaises(ServiceError):tiny.finish_upload(token,s,path)
        self.assertFalse(path.exists());self.assertEqual(tiny.reserved,0);self.assertFalse(s.busy)


@unittest.skipUnless(importlib.util.find_spec('fastapi') and importlib.util.find_spec('httpx'),'optional serve/dev dependencies')
class SpaceHTTPTests(unittest.TestCase):
    write=SpaceServiceTests.write
    sha=SpaceServiceTests.sha
    await_job=SpaceServiceTests.await_job
    def setUp(self):
        SpaceServiceTests.setUp(self)
        from koevd_eval.spaces import create_app
        from fastapi.testclient import TestClient
        self.client=TestClient(create_app(self.service,origins=['http://127.0.0.1:7860']),base_url='http://127.0.0.1:7860')
        self.addCleanup(self.client.close)
        self.headers={'Authorization':'Bearer '+self.token,'X-Koevd-CSRF':self.csrf}
    def test_http_streaming_size_limit_without_content_length(self):
        from koevd_eval.spaces import create_app
        from fastapi.testclient import TestClient
        tiny=AnalysisService(self.catalog,self.root/'stream-tiny',limits=Limits(upload_bytes=32,session_upload_bytes=64,global_bytes=4096,report_bytes=512,bootstrap_resamples=0))
        self.addCleanup(tiny.close);token,info=tiny.create_session()
        headers={'Authorization':'Bearer '+token,'X-Koevd-CSRF':info['csrf_token'],'Content-Type':'application/json'}
        with TestClient(create_app(tiny,origins=['http://127.0.0.1:7860']),base_url='http://127.0.0.1:7860') as client:
            response=client.post('/api/uploads',content=iter([b'x'*16,b'x'*17]),headers=headers)
            self.assertEqual(response.status_code,413);self.assertEqual(tiny.reserved,0)
            self.assertEqual(tiny.describe(token)['uploads'],[])
            self.assertEqual(client.post('/api/uploads',content=b'{}',headers={**headers,'Content-Length':'33'}).status_code,413)

    def test_deployment_retention_notice_is_visible_bounded_and_escaped(self):
        from koevd_eval.spaces import create_app
        from fastapi.testclient import TestClient
        notice='Submissions may disappear after rebuild. <script>bad()</script>'
        app=create_app(self.service,origins=['http://127.0.0.1:7860'],deployment_notice=notice)
        client=TestClient(app,base_url='http://127.0.0.1:7860');self.addCleanup(client.close)
        response=client.get('/')
        self.assertIn('Submissions may disappear after rebuild.',response.text)
        self.assertIn('&lt;script&gt;bad()&lt;/script&gt;',response.text)
        self.assertNotIn('<script>bad()',response.text)
        self.assertNotIn('unsafe-inline',response.headers['content-security-policy'])
        self.assertNotIn('Submissions may disappear after rebuild.',self.client.get('/').text)
        with self.assertRaises(ValueError):
            create_app(self.service,origins=['http://127.0.0.1:7860'],deployment_notice='x'*513)

    def test_http_streaming_auth_origin_limits_and_private_headers(self):
        c=self.client
        self.assertEqual(c.get('/api/session').status_code,401)
        self.assertEqual(c.post('/api/uploads',content=b'{}',headers=self.headers).status_code,415)
        self.assertEqual(c.post('/api/session',headers={'Origin':'https://attacker.invalid'}).status_code,403)
        self.assertEqual(c.post('/api/session',headers={'Sec-Fetch-Site':'cross-site'}).status_code,403)
        self.assertEqual(c.get('/',headers={'Host':'attacker.invalid'}).status_code,400)
        self.assertEqual(c.get('/',headers={'Sec-Fetch-Site':'cross-site'}).status_code,200)
        self.assertEqual(c.get('/api/session',headers={**self.headers,'Sec-Fetch-Site':'cross-site'}).status_code,403)
        r=c.get('/');self.assertEqual(r.status_code,200);self.assertIn("script-src 'self' 'sha256-",r.headers['content-security-policy']);self.assertEqual(r.headers['cache-control'],'no-store')
        self.assertNotIn('unsafe-inline',r.headers['content-security-policy']);self.assertNotIn('set-cookie',r.headers)
        r=c.post('/api/uploads',content=json.dumps(self.document),headers={**self.headers,'Content-Type':'application/json'});self.assertEqual(r.status_code,201)
        uid=r.json()['id']
        self.assertEqual(c.post('/api/uploads',content=json.dumps(self.document),headers={**self.headers,'Content-Type':'application/json'}).status_code,409)
        r=c.post('/api/analyses',json={'upload_ids':[uid],'baseline_ids':[]},headers=self.headers);self.assertEqual(r.status_code,202)
        job=r.json();self.assertEqual(self.await_job(self.token,job)['status'],'complete')
        download=c.get('/api/reports/'+job['id']+'/html',headers=self.headers);self.assertEqual(download.status_code,200);self.assertIn('attachment',download.headers['content-disposition'])
        self.assertEqual(c.get('/api/reports/'+job['id']+'/html').status_code,401)
        self.assertEqual(c.get('/api/reports/'+job['id']+'/../../catalog.json',headers=self.headers).status_code,404)
        self.assertEqual(c.delete('/api/session',headers=self.headers).status_code,200);self.assertEqual(c.get('/api/session',headers=self.headers).status_code,401)
