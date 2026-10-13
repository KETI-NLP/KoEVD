"""CPU transfer guards; these do not authorize or prove actual HF transfers."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from http.cookiejar import Cookie
import io
from types import SimpleNamespace
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parents[1]/'scripts'))
import validate_hosted_private_analysis as hosted


class HostedPrivateTransferGuards(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.candidate=self.root/'candidate';self.candidate.mkdir()
        payload=b'public source';(self.candidate/'source.txt').write_bytes(payload)
        manifest={'format':'koevd-private-development-space-v1','storage':'ephemeral_development',
            'credentials_included':False,'actual_target_outputs_included':False,'official_rank_eligible':False,
            'files':{'source.txt':{'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest()}}}
        (self.candidate/'deployment-manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
        self.results=[self.root/'first.json',self.root/'second.json']
        for i,path in enumerate(self.results):path.write_bytes(b'SYNTHETIC private original'+bytes([48+i]))
        self.hashes=[hosted.digest(path) for path in self.results]
        self.expected=self.root/'native';self.expected.mkdir()
        for name in hosted.FILES.values():(self.expected/name).write_bytes('한글 <unsafe>\n'.encode())
        self.plan=hosted.input_plan(self.candidate,self.results,self.hashes,self.expected,1024,1024)

    def test_hash_or_total_bound_failure_precedes_transfer(self):
        for hashes,up,down in [(self.hashes,1,1024),(self.hashes,1024,1),(['f'*64,self.hashes[1]],1024,1024)]:
            with self.subTest(up=up,down=down),self.assertRaises(ValueError):
                hosted.input_plan(self.candidate,self.results,hashes,self.expected,up,down)
        self.assertEqual(self.plan['upload_bytes'],sum(p.stat().st_size for p in self.results))

    def test_managed_or_stale_candidate_cannot_be_used_as_default(self):
        path=self.candidate/'deployment-manifest.json';m=json.loads(path.read_text())
        m['storage']='managed';path.write_text(json.dumps(m))
        with self.assertRaises(ValueError):hosted.input_plan(self.candidate,self.results,self.hashes,self.expected,1024,1024)

    def test_download_matches_direct_bytes_across_utf8_chunk_boundaries(self):
        path=self.expected/'report-v2.html';raw=path.read_bytes();dest=self.root/'download.html'
        result=hosted.verify_chunks((raw[:1],raw[1:4],raw[4:]),path,dest,len(raw))
        self.assertTrue(result['native_bytes_exact']);self.assertEqual(dest.read_bytes(),raw)

    def test_truncated_tampered_or_oversize_download_keeps_partial_without_pass(self):
        path=self.expected/'report-v2.html';raw=path.read_bytes()
        for i,chunks in enumerate(([raw[:4]],[b'changed'],[raw, b'extra'])):
            with self.subTest(i=i),self.assertRaises(ValueError):
                hosted.verify_chunks(chunks,path,self.root/('bad-'+str(i)),len(raw))
        dest=self.root/'existing';dest.write_bytes(b'KEEP')
        with self.assertRaises(FileExistsError):hosted.verify_chunks([raw],path,dest,len(raw))
        self.assertEqual(dest.read_bytes(),b'KEEP')

    def test_server_limits_must_match_native_bootstrap_and_upload_budget(self):
        limits={'upload_bytes':1024,'max_uploads':4,'ttl_seconds':7200,'bootstrap_resamples':100,'bootstrap_seed':1729}
        hosted.checked_limits(limits,self.plan)
        for field,value in [('upload_bytes',1),('max_uploads',1),('bootstrap_resamples',0),('bootstrap_seed',1),('ttl_seconds',None),('ttl_seconds',0)]:
            with self.subTest(field=field),self.assertRaises(ValueError):
                hosted.checked_limits(dict(limits,**{field:value}),self.plan)

    def test_default_preflight_never_POSTs_or_SERIALIZES_credentials(self):
        host='https://fixture-dev.hf.space';calls=[]
        cookie=Cookie(0,'spaces-jwt','SYNTHETIC-cookie-value',None,False,'fixture-dev.hf.space',True,False,
                      '/',True,True,None,True,None,None,{'HttpOnly':None},False)
        def response(value):return SimpleNamespace(status_code=200,json=lambda:value)
        class Client:
            cookies=SimpleNamespace(jar=[cookie])
            def __init__(self,**kwargs):pass
            def get(self,url,**kwargs):
                calls.append(('GET',url.split('?',1)[0]))
                return response({'token':'SYNTHETIC-resource-token'}) if url.endswith('/jwt') else response({})
            def request(self,method,url,**kwargs):
                calls.append((method,url))
                if url.endswith('/healthz'):return response({'status':'ready','registration_enabled':True})
                if url.endswith('/api/identity'):return response({'signed_in':False})
                if url.endswith('/api/catalog'):
                    return response({'baselines':[],'official_rank_eligible':False,
                        'limits':{'upload_bytes':1024,'max_uploads':4,'ttl_seconds':7200,'bootstrap_resamples':100,'bootstrap_seed':1729}})
                raise AssertionError('Unexpected state-changing or data request')
            def close(self):pass
        api=SimpleNamespace(space_info=lambda target:SimpleNamespace(private=True,sdk='docker',sha='a'*40,host=host),
            get_space_runtime=lambda target:SimpleNamespace(stage='RUNNING',hardware='cpu-basic',raw={'replicas':{'current':1,'requested':1}}))
        out=self.root/'preflight'
        argv=['check','--space-id','Fixture/Dev','--revision','a'*40,'--candidate',str(self.candidate),
              '--expected-dir',str(self.expected),'--max-upload-bytes','1024','--max-download-bytes','1024','--output',str(out)]
        for path,checksum in zip(self.results,self.hashes):argv.extend(['--result',str(path),'--result-sha256',checksum])
        modules={'httpx':SimpleNamespace(Client=Client),
                 'huggingface_hub':SimpleNamespace(HfApi=lambda:api,get_token=lambda:'SYNTHETIC-cli-token')}
        with patch('sys.argv',argv),patch.dict(sys.modules,modules),redirect_stdout(io.StringIO()):hosted.main()
        self.assertTrue(all(method=='GET' for method,_ in calls))
        raw=(out/'receipt.json').read_text(encoding='utf-8');receipt=json.loads(raw)
        self.assertEqual(receipt['status'],'preflight_only');self.assertEqual(receipt['upload_body_bytes_attempted'],0)
        self.assertEqual(receipt['analysis_jobs_created'],0);self.assertEqual(receipt['owned_session_cleanup_statuses'],[])
        for value in ('SYNTHETIC-cli-token','SYNTHETIC-resource-token','SYNTHETIC-cookie-value'):
            self.assertNotIn(value,raw)


if __name__=='__main__':unittest.main()
