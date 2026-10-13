"""Pinned private CPU Space acceptance with an explicit result-transfer opt-in.

Default is preflight-only: no analysis session, upload, job, saved submission,
backup, publication, restart or resource change. Existing CLI/resource access
credentials stay in memory and never establish an application-user identity.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time

from validate_private_docker_hosting import checked_host, access_cookies
from validate_space_native_runtime import checked_context, digest

FILES = {'profile':'profile-v2.json','cases':'cases-v2.jsonl','csv':'metrics-v2.csv',
         'markdown':'report-v2.md','html':'report-v2.html'}


def input_plan(candidate, results, hashes, expected_dir, upload_bound, download_bound):
    manifest = checked_context(candidate)
    if manifest.get('storage') != 'ephemeral_development' or 'operator-data/managed.json' in manifest['files']:
        raise ValueError('Require the unactivated default development profile')
    if len(results) != 2 or len(hashes) != 2:
        raise ValueError('Two independently hashed actual results required')
    if type(upload_bound) is not int or upload_bound <= 0 or type(download_bound) is not int or download_bound <= 0:
        raise ValueError('Explicit positive upload/download byte bounds required')
    records=[]
    for path, expected in zip(results, hashes):
        if path.is_relative_to(candidate) or not re.fullmatch('[0-9a-f]{64}',expected) or digest(path)!=expected:
            raise ValueError('Require an outside original matching its independent byte hash')
        records.append({'bytes':path.stat().st_size,'sha256':expected})
    outputs={kind:{'bytes':(expected_dir/name).stat().st_size,'sha256':digest(expected_dir/name)}
             for kind,name in FILES.items()}
    if sum(i['bytes'] for i in records)>upload_bound or sum(i['bytes'] for i in outputs.values())>download_bound:
        raise ValueError('Accepted artifacts exceed explicit transfer bounds')
    return {'candidate_manifest_sha256':digest(candidate/'deployment-manifest.json'),
            'payload_files':len(manifest['files']),'inputs':records,'outputs':outputs,
            'upload_bytes':sum(i['bytes'] for i in records),'download_bytes':sum(i['bytes'] for i in outputs.values())}


def verify_chunks(chunks, expected_path, destination, max_bytes):
    """Direct byte comparison, exclusive destination, bounded partial kept on failure."""
    count=0;checksum=hashlib.sha256()
    with expected_path.open('rb') as expected, destination.open('xb') as saved:
        for chunk in chunks:
            count+=len(chunk)
            if count>max_bytes:
                raise ValueError('Download exceeded its accepted byte bound')
            if expected.read(len(chunk))!=chunk:
                raise ValueError('Downloaded bytes differ from independent native output')
            checksum.update(chunk);saved.write(chunk)
        if expected.read(1):
            raise ValueError('Download truncated before independent output EOF')
    return {'bytes':count,'sha256':checksum.hexdigest(),'native_bytes_exact':True}


def checked_limits(limits, plan):
    for name in ('upload_bytes','max_uploads','ttl_seconds','bootstrap_resamples','bootstrap_seed'):
        if type(limits.get(name)) is not int:
            raise ValueError('Server limits unavailable or malformed')
    if (limits['max_uploads']<2 or limits['ttl_seconds']<=0 or any(i['bytes']>limits['upload_bytes'] for i in plan['inputs'])
            or limits['bootstrap_resamples']!=100 or limits['bootstrap_seed']!=1729):
        raise ValueError('Server limits or analysis settings differ from accepted native output')
    return limits


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--space-id',required=True)
    p.add_argument('--revision',required=True)
    p.add_argument('--candidate',required=True)
    p.add_argument('--result',action='append',required=True)
    p.add_argument('--result-sha256',action='append',required=True)
    p.add_argument('--expected-dir',required=True,help='Independently accepted native five-file comparison')
    p.add_argument('--max-upload-bytes',type=int,required=True)
    p.add_argument('--max-download-bytes',type=int,required=True)
    p.add_argument('--approve-private-result-transfer',action='store_true',
                   help='Operator opt-in for exactly two uploads/one comparison; requires human authorization')
    p.add_argument('--output',required=True,help='Fresh private local evidence directory')
    a=p.parse_args()
    if not re.fullmatch('[A-Za-z0-9_-]+/[A-Za-z0-9_-]+',a.space_id) or not re.fullmatch('[0-9a-f]{40}',a.revision):
        p.error('Exact owner/Space and pinned commit required')
    candidate=Path(a.candidate).resolve(strict=True)
    originals=[Path(path).resolve(strict=True) for path in a.result]
    expected=Path(a.expected_dir).resolve(strict=True)
    plan=input_plan(candidate,originals,a.result_sha256,expected,a.max_upload_bytes,a.max_download_bytes)
    out=Path(a.output).resolve()
    if out.is_relative_to(candidate) or any(path.is_relative_to(out) for path in originals) or expected.is_relative_to(out):
        p.error('Fresh evidence path must be separate from inputs/candidate/native files')
    out.mkdir(mode=0o700,parents=True,exist_ok=False)
    # Lazy imports let CPU guards run without obtaining a credential or SDK client.
    import httpx
    from huggingface_hub import HfApi, get_token
    api=HfApi();client=httpx.Client(follow_redirects=False,timeout=180)
    sessions=[];started=time.monotonic();upload_bytes=0;acknowledged_upload_bytes=0;download_bytes=0
    receipt={'format':'koevd-hosted-private-analysis-v1','status':'checking',
        'observed_utc':datetime.now(timezone.utc).isoformat(),'space_id':a.space_id,'revision':a.revision,
        'transfer_opt_in':a.approve_private_result_transfer,'plan':plan,
        'credentials_persisted_or_printed':False,'actual_application_user_login':False,
        'new_inference':False,'saved_submission_or_Bucket_write':False,'public_or_resource_change':False,
        'default_preflight_has_no_analysis_POST_or_DELETE':True,'analysis_job_terminal_observed':False,'checks':[]}
    def request(method,path,**kwargs):
        if not path.startswith('/') or path.startswith('//'):
            raise ValueError('Fixed same-origin app path required')
        headers={'Origin':host,**kwargs.pop('headers',{})}
        return client.request(method,host+path,headers=headers,**kwargs)
    def guard_state():
        info=api.space_info(a.space_id);runtime=api.get_space_runtime(a.space_id)
        if (not info.private or info.sdk!='docker' or info.sha!=a.revision
                or str(runtime.stage)!='RUNNING' or str(runtime.hardware)!='cpu-basic'
                or runtime.raw.get('replicas')!={'current':1,'requested':1}):
            raise ValueError('Private pinned single CPU default runtime changed')
        return info
    try:
        info=guard_state();host=checked_host(info.host)
        receipt.update(host=host,hardware='cpu-basic',single_replica=True)
        secret=get_token()
        if not secret:
            raise ValueError('Existing authorized CLI resource access required')
        access=client.get('https://huggingface.co/api/spaces/'+a.space_id+'/jwt',
                          headers={'Authorization':'Bearer '+secret})
        if access.status_code!=200:
            raise ValueError('Private resource-access request failed')
        signed=client.get(host+'/',params={'__sign':access.json()['token']})
        if signed.status_code!=200:
            raise ValueError('Expected existing private Docker signed-access flow')
        access_cookies(client.cookies.jar,host)
        health=request('GET','/healthz');catalog=request('GET','/api/catalog');identity=request('GET','/api/identity')
        if (health.status_code!=200 or health.json()!={'status':'ready','registration_enabled':True}
                or catalog.status_code!=200 or identity.status_code!=200 or identity.json()!={'signed_in':False}):
            raise ValueError('Default readiness or anonymous app boundary differs')
        public=catalog.json();limits=checked_limits(public['limits'],plan)
        if public['baselines'] or public['official_rank_eligible']:
            raise ValueError('Require empty approved-reference catalog and disabled official ranks')
        receipt.update(server_limits=limits,resource_access_only_not_submitter_identity=True)
        receipt['checks'].append('private_pinned_CPU_resource_readiness_limits_and_no_rank')
        if not a.approve_private_result_transfer:
            receipt.update(status='preflight_only',result_body_bytes_sent=0,analysis_jobs_created=0)
            return
        guard_state()
        for _ in range(2):
            response=request('POST','/api/session')
            if response.status_code!=201:
                raise ValueError('Private session creation refused')
            value=response.json();sessions.append({'Authorization':'Bearer '+value['session_token'],
                                                   'X-Koevd-CSRF':value['csrf_token']})
        own,other=sessions;uploads=[]
        for path,expected_hash in zip(originals,a.result_sha256):
            guard_state()
            body=path.read_bytes()
            if hashlib.sha256(body).hexdigest()!=expected_hash:
                raise ValueError('Original changed between plan and transfer')
            # No retry: failed upload must not silently resubmit the accepted body.
            upload_bytes+=len(body)  # Conservative attempted body count even if transport fails.
            if upload_bytes>a.max_upload_bytes:
                raise ValueError('Aggregate attempted upload bound exceeded')
            response=request('POST','/api/uploads',content=body,
                headers={**own,'Content-Type':'application/json'})
            if response.status_code!=201:
                raise ValueError('Actual private result upload refused')
            acknowledged_upload_bytes+=len(body)
            uploads.append(response.json()['id'])
        if request('GET','/api/session',headers=other).json()['uploads']:
            raise ValueError('Other session observed private uploads')
        response=request('POST','/api/analyses',content=json.dumps({'upload_ids':uploads,'baseline_ids':[]}).encode(),
            headers={**own,'Content-Type':'application/json'})
        if response.status_code!=202:
            raise ValueError('Actual comparison job refused')
        job=response.json()['id']
        if not re.fullmatch('[A-Za-z0-9_-]+',job):
            raise ValueError('Unexpected job identifier')
        receipt['analysis_jobs_created']=1
        receipt['analysis_job_id']=job  # ID is not a credential; session tokens are never persisted.
        deadline=time.monotonic()+1200
        while True:
            state=request('GET','/api/analyses/'+job,headers=own)
            if state.status_code==200 and state.json()['status']=='failed':
                receipt['analysis_job_terminal_observed']=True
                raise ValueError('Actual hosted comparison failed')
            if state.status_code!=200:
                raise ValueError('Actual hosted comparison failed')
            if state.json()['status']=='complete':
                receipt['analysis_job_terminal_observed']=True
                break
            if time.monotonic()>deadline:
                raise TimeoutError('Observe same job before any retry; analysis deadline reached')
            time.sleep(2)
        guard_state();outputs={}
        for kind,name in FILES.items():
            with client.stream('GET',host+'/api/reports/'+job+'/'+kind,headers={'Origin':host,**own}) as response:
                if response.status_code!=200 or 'attachment' not in response.headers.get('content-disposition',''):
                    raise ValueError('Expected private download attachment')
                def observed_chunks():
                    nonlocal download_bytes
                    for chunk in response.iter_bytes(chunk_size=65536):
                        download_bytes+=len(chunk)
                        if download_bytes>a.max_download_bytes:
                            raise ValueError('Aggregate decoded output download bound exceeded')
                        yield chunk
                result=verify_chunks(observed_chunks(),expected/name,out/name,plan['outputs'][kind]['bytes'])
            if download_bytes>a.max_download_bytes:
                raise ValueError('Aggregate output download limit exceeded')
            if request('GET','/api/reports/'+job+'/'+kind,headers=other).status_code==200:
                raise ValueError('Other session accessed private output')
            outputs[kind]=result
        guard_state()
        receipt.update(status='passed_checks_cleanup_pending',outputs=outputs,
            five_files_native_bytes_exact=True,actual_hosted_accepted_artifact_sizes_checked=True,
            no_new_inference_or_accuracy_claim=True)
        receipt['checks'].append('two_private_uploads_one_comparison_five_files_isolation_native_bytes_exact')
    except Exception as error:
        receipt.update(status='failed',failure_type=type(error).__name__)
        # Never print provider error text, headers, cookies, signed URLs or private body.
    finally:
        cleanup=[]
        for credentials in sessions:
            try:cleanup.append(request('DELETE','/api/session',headers=credentials).status_code)
            except Exception:cleanup.append(None)
        client.close()
        receipt.update(upload_body_bytes_attempted=upload_bytes,upload_body_bytes_acknowledged=acknowledged_upload_bytes,
                       download_output_bytes_observed=download_bytes,
                       owned_session_cleanup_statuses=cleanup,seconds=round(time.monotonic()-started,3))
        receipt['owned_analysis_job_may_remain_pending']=bool(receipt.get('analysis_jobs_created') and not receipt['analysis_job_terminal_observed'])
        if receipt['status']=='passed_checks_cleanup_pending':
            receipt['status']='passed' if cleanup==[200,200] else 'failed_cleanup'
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':receipt['status'],'upload_body_bytes_attempted':upload_bytes,
            'download_output_bytes':download_bytes,'actual_application_user_login':False,'owned_session_cleanup_statuses':cleanup}))
    if receipt['status'] not in ('passed','preflight_only'):
        raise SystemExit(1)


if __name__=='__main__':main()
