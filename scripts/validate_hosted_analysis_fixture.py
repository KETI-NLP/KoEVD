"""Local real HTTP transfer-path acceptance with explicit HF access doubles.

Separate test-only harness, never a production authentication/host override.
Scrubs actual credentials, blocks external socket connections in both processes,
binds only loopback, and retains private outputs plus exact owned-child cleanup.
"""
import argparse
from contextlib import redirect_stdout
from http.cookiejar import Cookie
import io
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import urlsplit

import httpx
import validate_hosted_private_analysis as hosted

ORIGIN='https://fixture-dev.hf.space'
REVISION='c'*40


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate',required=True)
    p.add_argument('--result',action='append',required=True)
    p.add_argument('--result-sha256',action='append',required=True)
    p.add_argument('--expected-dir',required=True)
    p.add_argument('--output',required=True)
    a=p.parse_args()
    if len(a.result)!=2 or len(a.result_sha256)!=2:p.error('Exactly two independent originals required')
    candidate=Path(a.candidate).resolve(strict=True);results=[Path(f).resolve(strict=True) for f in a.result]
    native=Path(a.expected_dir).resolve(strict=True);out=Path(a.output).resolve();out.mkdir(mode=0o700,parents=True,exist_ok=False)
    plan=hosted.input_plan(candidate,results,a.result_sha256,native,256*1024**2,512*1024**2)
    env={k:v for k,v in os.environ.items() if not k.startswith(('KOEVD_','OAUTH_','HF_','HUGGING_FACE_'))
         and k not in ('PYTHONPATH','PYTHONHOME','OPENID_PROVIDER_URL')}
    env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',
        OAUTH_CLIENT_ID='SYNTHETIC-local-hosted-fixture',OAUTH_CLIENT_SECRET='SYNTHETIC-local-hosted-fixture')
    hooks=out/'hooks';hooks.mkdir()
    # Only this fresh fixture process sees the hook. No production SDK altered.
    hook=('import json,os,socket\nfrom pathlib import Path\n'
        'Path(os.environ["LOCAL_HOSTED_FIXTURE_PID"]).write_text(json.dumps({"pid":os.getpid()}))\n'
        '_connect=socket.socket.connect\n'
        'def local_connect(self,address):\n'
        '    if isinstance(address,tuple) and address[0] not in ("127.0.0.1","::1"):\n'
        '        raise ValueError("Fixture refuses external network")\n'
        '    return _connect(self,address)\n'
        'socket.socket.connect=local_connect\n')
    (hooks/'sitecustomize.py').write_text(hook,encoding='utf-8')
    server_python=sys.executable
    if os.name=='nt':
        # A Windows venv executable can be a redirector rather than the HTTP
        # interpreter process. Own the real base executable and explicitly
        # load this already installed (noneditable) fixture package path.
        server_python=getattr(sys,'_base_executable',sys.executable)
        package_path=Path(importlib.util.find_spec('koevd_eval').origin).parent.parent.resolve(strict=True)
        if 'site-packages' not in package_path.parts:
            raise ValueError('Fixture requires an installed package, never source imports')
        env['PYTHONPATH']=os.pathsep.join((str(hooks),str(package_path)))
    else:
        env['PYTHONPATH']=str(hooks)
    env['LOCAL_HOSTED_FIXTURE_PID']=str(out/'server-pid.json')
    with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    base='http://127.0.0.1:'+str(port)
    argv=[server_python,'-m','koevd_eval.spaces','--host','127.0.0.1','--port',str(port),
        '--origin',ORIGIN,'--oauth-origin',ORIGIN,'--catalog',str(candidate/'operator-data/catalog.json'),
        '--roles-file',str(candidate/'operator-data/roles.json'),'--protocol-registry',str(candidate/'configs/protocols'),
        '--session-root',str(out/'sessions'),'--submission-root',str(out/'submissions')]
    calls=[];server=None;started=time.monotonic();inner_code=None;terminal=False
    real_client=httpx.Client(follow_redirects=False,timeout=180,trust_env=False)
    cookie=Cookie(0,'spaces-jwt','SYNTHETIC-resource-cookie',None,False,'fixture-dev.hf.space',True,False,
                  '/',True,True,None,True,None,None,{'HttpOnly':None},False)
    class LocalClient:
        cookies=SimpleNamespace(jar=[cookie])
        def __init__(self,**kwargs):pass
        def mapped(self,url,headers):
            value=urlsplit(url)
            if not url.startswith(ORIGIN+'/') or value.query or value.fragment:
                raise ValueError('Fixture refuses unexpected external destination')
            return base+value.path,{'Host':'fixture-dev.hf.space',**(headers or {})}
        def get(self,url,**kwargs):
            if url=='https://huggingface.co/api/spaces/Fixture/Hosted-Local-Only/jwt':
                return httpx.Response(200,json={'token':'SYNTHETIC-resource-token'})
            if url==ORIGIN+'/' and kwargs.get('params')=={'__sign':'SYNTHETIC-resource-token'}:
                return httpx.Response(200,text='SYNTHETIC resource proxy')
            raise ValueError('Only exact in-memory resource-access double allowed')
        def request(self,method,url,**kwargs):
            local,headers=self.mapped(url,kwargs.pop('headers',None));calls.append({'method':method,'path':urlsplit(url).path})
            return real_client.request(method,local,headers=headers,**kwargs)
        def stream(self,method,url,**kwargs):
            local,headers=self.mapped(url,kwargs.pop('headers',None));calls.append({'method':method,'path':urlsplit(url).path})
            return real_client.stream(method,local,headers=headers,**kwargs)
        def close(self):pass
    provider=SimpleNamespace(space_info=lambda target:SimpleNamespace(private=True,sdk='docker',sha=REVISION,host=ORIGIN),
        get_space_runtime=lambda target:SimpleNamespace(stage='RUNNING',hardware='cpu-basic',raw={'replicas':{'current':1,'requested':1}}))
    original_connect=socket.socket.connect
    def local_connect(sock,address):
        if isinstance(address,tuple) and address[0] not in ('127.0.0.1','::1'):
            raise ValueError('Parent fixture refuses external network')
        return original_connect(sock,address)
    with (out/'server.log').open('w',encoding='utf-8') as log:
        try:
            server=subprocess.Popen(argv,env=env,cwd=out,stdout=log,stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            deadline=time.monotonic()+60
            while True:
                if server.poll() is not None:raise RuntimeError('Owned local fixture server exited before readiness')
                try:
                    response=real_client.get(base+'/healthz',headers={'Host':'fixture-dev.hf.space'})
                    if response.status_code==200:break
                except httpx.TransportError:pass
                if time.monotonic()>deadline:raise TimeoutError('Owned local server readiness timeout')
                time.sleep(.1)
            child_pid=json.loads((out/'server-pid.json').read_text(encoding='utf-8'))['pid']
            if child_pid!=server.pid:
                raise ValueError('Fixture handle does not own the actual HTTP interpreter')
            command=['hosted-check','--space-id','Fixture/Hosted-Local-Only','--revision',REVISION,
                '--candidate',str(candidate),'--expected-dir',str(native),'--max-upload-bytes',str(plan['upload_bytes']),
                '--max-download-bytes',str(plan['download_bytes']),'--approve-private-result-transfer','--output',str(out/'driver')]
            for path,checksum in zip(results,a.result_sha256):command.extend(['--result',str(path),'--result-sha256',checksum])
            modules={'huggingface_hub':SimpleNamespace(HfApi=lambda:provider,get_token=lambda:'SYNTHETIC-cli-token')}
            stdout=io.StringIO()
            with patch('sys.argv',command),patch.dict(sys.modules,modules),patch.object(httpx,'Client',LocalClient),\
                    patch.object(socket.socket,'connect',local_connect),redirect_stdout(stdout):
                hosted.main()
            inner_code=0
            (out/'driver-stdout.txt').write_text(stdout.getvalue(),encoding='utf-8')
            inner=json.loads((out/'driver/receipt.json').read_text(encoding='utf-8'))
            assert inner['status']=='passed' and inner['owned_session_cleanup_statuses']==[200,200]
            assert inner['analysis_job_terminal_observed'] and not inner['owned_analysis_job_may_remain_pending']
            assert inner['upload_body_bytes_acknowledged']==plan['upload_bytes']
            assert inner['download_output_bytes_observed']==plan['download_bytes']
            assert len([c for c in calls if c['method']=='POST' and c['path']=='/api/uploads'])==2
            assert len([c for c in calls if c['method']=='POST' and c['path']=='/api/analyses'])==1
            assert len([c for c in calls if c['method']=='DELETE'])==2
        finally:
            if server is not None:
                if server.poll() is None:
                    server.terminate()
                    try:server.wait(timeout=15)
                    except subprocess.TimeoutExpired:server.kill();server.wait(timeout=15)
                terminal=server.poll() is not None
            real_client.close()
            reachable=False
            with socket.socket() as check:check.settimeout(1);reachable=check.connect_ex(('127.0.0.1',port))==0
            result={'status':'passed' if inner_code==0 and terminal and not reachable else 'failed',
                'scope':'local_real_HTTP_transfer_branch_with_explicit_HF_access_doubles',
                'seconds':round(time.monotonic()-started,3),'HF_requests_or_private_transmissions':0,
                'actual_HF_or_OAuth_or_Docker_verified':False,'new_inference':False,
                'owned_server_handle_terminal':terminal,'owned_server_port_connection_refused':not reachable,
                'owned_server_exit_code':None if server is None else server.returncode,
                'actual_server_pid_equals_owned_handle':server is not None and (out/'server-pid.json').is_file() and
                    json.loads((out/'server-pid.json').read_text(encoding='utf-8'))['pid']==server.pid,
                'local_input_bytes':plan['upload_bytes'],'local_output_bytes':plan['download_bytes'],'requests':calls}
            (out/'fixture-receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
            print(json.dumps({k:v for k,v in result.items() if k!='requests'}))
    if result['status']!='passed':raise SystemExit(1)


if __name__=='__main__':main()
