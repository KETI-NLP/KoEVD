"""Optional FastAPI/Docker Spaces transport for the shared CPU analysis service."""
from __future__ import annotations
import argparse
import asyncio
from contextlib import asynccontextmanager
from importlib.resources import files
from html import escape
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlsplit

from .space_service import AnalysisService, InputCatalog, Limits, ServiceError


def create_app(service, *, origins, frame_ancestors=("'self'",), registration=None, deployment_notice=None):
    try:
        from fastapi import FastAPI, Request
        from fastapi.responses import Response, JSONResponse, FileResponse
        from starlette.concurrency import run_in_threadpool
        from starlette.middleware.trustedhost import TrustedHostMiddleware
    except ImportError as exc:raise RuntimeError('Install koevd-eval[serve] for the Spaces app') from exc
    # Future annotations must resolve Request in FastAPI's endpoint module scope.
    globals()['Request']=Request
    allowed=set()
    hosts=[]
    for origin in origins:
        parsed=urlsplit(origin)
        if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password or parsed.path not in ('','/') or parsed.query or parsed.fragment:raise ValueError('Explicit HTTP(S) app origin required')
        if parsed.scheme=='http' and parsed.hostname not in ('127.0.0.1','localhost','::1'):raise ValueError('Non-local origins require HTTPS')
        normalized=origin.rstrip('/');allowed.add(normalized);hosts.append(parsed.hostname)
    if not allowed:raise ValueError('At least one explicit app origin is required')
    if deployment_notice is not None and (not isinstance(deployment_notice,str) or len(deployment_notice)>512):
        raise ValueError('Deployment notice must be bounded text')
    if registration is not None:
        from .submission_web import RegistrationWeb
        if not isinstance(registration,RegistrationWeb):raise ValueError('Expected operator-configured registration service')
    if any(not isinstance(a,str) or any(c in a for c in '\r\n;') for a in frame_ancestors):raise ValueError('Invalid frame ancestor policy')

    @asynccontextmanager
    async def lifespan(app):
        async def sweep():
            while True:
                await asyncio.sleep(30)
                await run_in_threadpool(service.cleanup)
                if registration is not None:registration.cleanup()
        worker=asyncio.create_task(sweep())
        try:yield
        finally:
            worker.cancel()
            try:await worker
            except asyncio.CancelledError:pass
            await run_in_threadpool(service.close)
            if registration is not None:registration.close()

    app=FastAPI(title='KoEVD private analysis candidate',docs_url=None,redoc_url=None,openapi_url=None,lifespan=lifespan)
    app.state.service=service
    app.state.registration=registration
    app.add_middleware(TrustedHostMiddleware,allowed_hosts=hosts)
    from .transfer import ResultCompressionMiddleware
    app.add_middleware(ResultCompressionMiddleware)

    @app.exception_handler(ServiceError)
    async def service_error(request,exc):return JSONResponse({'error':{'code':exc.code,'message':exc.message}},status_code=exc.status)

    from .reports import _hash
    report_script_hash=_hash(files('koevd_eval').joinpath('assets','report.js').read_text(encoding='utf-8'))
    report_style_hash=_hash(files('koevd_eval').joinpath('assets','report.css').read_text(encoding='utf-8'))

    @app.middleware('http')
    async def boundary(request,call_next):
        origin=request.headers.get('origin')
        if request.url.path.startswith('/api/') and (origin and origin not in allowed or request.headers.get('sec-fetch-site')=='cross-site'):
            response=JSONResponse({'error':{'code':'origin_rejected','message':'Cross-origin requests are not accepted.'}},status_code=403)
        else:response=await call_next(request)
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Content-Security-Policy']=f"default-src 'none'; script-src 'self' 'sha256-{report_script_hash}'; style-src 'self' 'sha256-{report_style_hash}'; connect-src 'self'; img-src 'none'; frame-src blob:; base-uri 'none'; object-src 'none'; form-action 'none'; frame-ancestors "+' '.join(frame_ancestors)
        return response

    def credentials(request,mutate=False):
        header=request.headers.get('authorization','')
        if not header.startswith('Bearer ') or len(header)>300:raise ServiceError('session_required','Create a private session first.',401)
        token=header[7:]
        if mutate:
            csrf=request.headers.get('x-koevd-csrf','')
            with service.lock:service._lookup(token,csrf)
            return token,csrf
        with service.lock:service._lookup(token)
        return token

    async def bounded_body(request,limit):
        count=0;pieces=[]
        async for chunk in request.stream():
            count+=len(chunk)
            if count>limit:raise ServiceError('body_size','Request exceeds the size limit.',413)
            pieces.append(chunk)
        return b''.join(pieces)

    @app.get('/')
    @app.get('/submit')
    @app.get('/models')
    @app.get('/compare')
    async def landing():
        content=files('koevd_eval').joinpath('assets','space.html').read_text(encoding='utf-8')
        if deployment_notice:
            content=content.replace('<body><main>','<body><main><details class="deployment-notice"><summary>Research use · measurement and sharing limits</summary><p>'+escape(deployment_notice)+'</p></details>',1)
        return Response(content,media_type='text/html')

    @app.get('/assets/{name}')
    async def assets(name:str):
        if name not in ('space.js','space.css','registration.js','public_reads.js','navigation.js','metric_labels.js','home.js','leaderboard.js','paper_models.json','paper_results.json'):raise ServiceError('not_found','Asset not found.',404)
        return Response(files('koevd_eval').joinpath('assets',name).read_text(encoding='utf-8'),media_type='text/javascript' if name.endswith('.js') else 'application/json' if name.endswith('.json') else 'text/css')

    @app.get('/healthz')
    async def health():return {'status':'ready','registration_enabled':registration is not None}

    readiness_gate=asyncio.Semaphore(1)

    @app.get('/readyz')
    async def readiness():
        # /healthz is process liveness. This explicit dependency probe neither
        # starts a background worker nor confirms an unacknowledged mutation.
        enabled=registration is not None
        if service.closed or readiness_gate.locked():
            return JSONResponse({'status':'unavailable','registration_enabled':enabled},status_code=503)
        async with readiness_gate:
            try:
                if enabled:await run_in_threadpool(registration.submissions.check_readiness)
            except Exception:
                return JSONResponse({'status':'unavailable','registration_enabled':enabled},status_code=503)
        return {'status':'ready','registration_enabled':enabled}

    @app.get('/api/registration')
    async def registration_status():
        value={'enabled':registration is not None,'publication_environment':registration.submissions.publication_environment if registration is not None else 'local_candidate',
               'official_ranking_enabled':registration is not None and registration.submissions.rank_policy.status=='ratified'}
        value['review_requests_enabled']=registration is not None and registration.submissions.review_requests_enabled
        if registration is not None and registration.submissions.allow_self_reported_summaries:
            value['self_reported_summaries_enabled']=True
        return value

    @app.get('/api/catalog')
    async def catalog():return {**service.catalog.public(),'limits':{'upload_bytes':service.limits.upload_bytes,'max_uploads':service.limits.max_uploads,'ttl_seconds':service.limits.ttl_seconds,'bootstrap_resamples':service.limits.bootstrap_resamples,'bootstrap_seed':service.limits.bootstrap_seed}}

    @app.post('/api/session')
    async def start_session(request:Request):
        body=await bounded_body(request,16)
        if body not in (b'',b'{}'):raise ServiceError('body','Session creation does not accept identity or paths.')
        token,info=service.create_session()
        return JSONResponse({**info,'session_token':token},status_code=201)

    @app.get('/api/session')
    async def session(request:Request):return service.describe(credentials(request))

    @app.delete('/api/session')
    async def delete_session(request:Request):
        token,csrf=credentials(request,True);service.delete_session(token,csrf)
        return {'deleted':True}

    @app.post('/api/uploads')
    async def upload(request:Request):
        token,csrf=credentials(request,True)
        if request.headers.get('content-type','').split(';')[0].strip().lower()!='application/json':raise ServiceError('content_type','Upload one result JSON document; HTML, ZIP and index uploads are not accepted.',415)
        encoding=request.headers.get('content-encoding','identity').strip().lower()
        if encoding not in ('identity','gzip'):raise ServiceError('content_encoding','Use an uncompressed or gzip JSON body.',415)
        length=request.headers.get('content-length')
        if length is not None:
            if not length.isascii() or not length.isdigit():raise ServiceError('length','Invalid Content-Length.')
            if int(length)>service.limits.upload_bytes:raise ServiceError('upload_size','Result exceeds the upload limit.',413)
        s,path=service.begin_upload(token,csrf);handed_off=False
        from .transfer import receive_result
        try:
            await asyncio.wait_for(receive_result(request,path,limit=service.limits.upload_bytes,
                encoding=encoding,expected_length=int(length) if length is not None else None),
                timeout=600 if encoding=='gzip' else 120)
            handed_off=True
            entry=await run_in_threadpool(service.finish_upload,token,s,path)
            return JSONResponse(entry,status_code=201)
        except asyncio.TimeoutError:raise ServiceError('upload_timeout','Upload timed out.',408) from None
        finally:
            if not handed_off:service.abort_upload(s,path)

    @app.delete('/api/uploads/{upload_id}')
    async def delete_upload(upload_id:str,request:Request):
        token,csrf=credentials(request,True);service.delete_upload(token,csrf,upload_id);return {'deleted':True}

    @app.get('/api/uploads/{upload_id}/declaration')
    async def upload_declaration(upload_id:str,request:Request):
        return await run_in_threadpool(service.upload_declaration,credentials(request),upload_id)

    @app.post('/api/analyses')
    async def analyze(request:Request):
        token,csrf=credentials(request,True)
        try:
            from .results import _unique_object
            body=json.loads((await bounded_body(request,8192)).decode('utf-8'),object_pairs_hook=_unique_object)
            if not isinstance(body,dict) or set(body)!={'upload_ids','baseline_ids'}:raise ValueError('Unexpected selection fields')
            job=service.submit_analysis(token,csrf,body['upload_ids'],body['baseline_ids'])
        except (ValueError,UnicodeDecodeError,TypeError):raise ServiceError('selection','Invalid analysis selection.') from None
        return JSONResponse(job,status_code=202)

    @app.get('/api/analyses/{job_id}')
    async def job(job_id:str,request:Request):return service.job(credentials(request),job_id)

    @app.get('/api/reports/{job_id}/{kind}')
    async def download(job_id:str,kind:str,request:Request):
        path=service.report_file(credentials(request),job_id,kind)
        return FileResponse(path,media_type={'html':'text/html','profile':'application/json','cases':'application/x-ndjson','csv':'text/csv','markdown':'text/markdown'}[kind],filename=path.name)
    if registration is not None:
        from .submission_web import install_routes
        install_routes(app,service,registration,allowed_origins=allowed,bounded_body=bounded_body)
    return app


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog',default=os.environ.get('KOEVD_SPACE_CATALOG'))
    parser.add_argument('--host',default='127.0.0.1');parser.add_argument('--port',type=int,default=7860)
    parser.add_argument('--origin',action='append');parser.add_argument('--demo',action='store_true')
    parser.add_argument('--public-reference-disclosure',action='store_true',
                        help='Withhold configured reference raw text after analysis; personal session results remain intact')
    parser.add_argument('--session-root',default=os.environ.get('KOEVD_SESSION_ROOT'))
    parser.add_argument('--submission-root',default=os.environ.get('KOEVD_SUBMISSION_ROOT'))
    parser.add_argument('--checkpoint-root',default=os.environ.get('KOEVD_CHECKPOINT_ROOT'),
                        help='Separate retained filesystem ledger: confirm each mutation before success; not an HF Bucket')
    parser.add_argument('--state-bucket',default=os.environ.get('KOEVD_STATE_BUCKET'),
                        help='Explicit existing private HF Bucket for conditional acknowledged state; dedicated S3 secrets required')
    parser.add_argument('--state-prefix',default='koevd-state-v1')
    parser.add_argument('--initialize-state',action='store_true',
                        help='Explicitly permit a verified empty remote namespace; never overwrite an existing cut')
    parser.add_argument('--self-reported-summaries',action='store_true',
                        help='Allow owners to explicitly publish numerical summaries; no response review or official rank implied')
    parser.add_argument('--roles-file',default=os.environ.get('KOEVD_ROLES_FILE'))
    parser.add_argument('--protocol-registry',default=os.environ.get('KOEVD_PROTOCOL_REGISTRY'),
                        help='Operator protocol directory for published metric admission')
    parser.add_argument('--policy-root',default=os.environ.get('KOEVD_POLICY_ROOT'),
                        help='Independent operator decision archive, never uploaded policy')
    parser.add_argument('--policy-head-sha256',default=os.environ.get('KOEVD_POLICY_HEAD_SHA256'),
                        help='Explicit pinned operator policy decision; default is candidate')
    parser.add_argument('--oauth-origin',default=os.environ.get('KOEVD_OAUTH_ORIGIN'))
    parser.add_argument('--oauth-client-type',choices=('confidential','public'),
                        default=os.environ.get('KOEVD_OAUTH_CLIENT_TYPE','confidential'),
                        help='Explicit public app uses client ID and PKCE without a secret; default confidential requires a secret')
    args=parser.parse_args()
    if not args.catalog:parser.error('An operator-controlled --catalog is required')
    origins=args.origin or ([os.environ['KOEVD_APP_ORIGIN']] if os.environ.get('KOEVD_APP_ORIGIN') else None)
    if origins is None:
        if args.host not in ('127.0.0.1','localhost','::1'):parser.error('Non-local listening requires an explicit HTTPS --origin or KOEVD_APP_ORIGIN')
        origins=[f'http://127.0.0.1:{args.port}',f'http://localhost:{args.port}']
    catalog=InputCatalog(args.catalog,allow_synthetic=args.demo,
                         public_reference_disclosure=args.public_reference_disclosure)
    temporary=None
    if args.session_root:root=Path(args.session_root)
    else:temporary=tempfile.TemporaryDirectory(prefix='koevd-private-sessions-');root=Path(temporary.name)
    service=AnalysisService(catalog,root)
    registration=None
    try:
        if args.submission_root:
            if not args.roles_file:parser.error('Registration requires an operator --roles-file')
            from .results import read_document, _keys
            from .storage import LocalSubmissionStore
            from .submissions import SubmissionService
            from .oauth import HFOAuthProvider,IdentitySessions,ISSUER
            from .submission_web import RegistrationWeb
            roles=read_document(args.roles_file);_keys(roles,('reviewers','admins'),'Operator roles')
            if not all(isinstance(v,list) and all(isinstance(s,str) for s in v) for v in roles.values()):parser.error('Role subjects must be operator lists')
            provider_url=os.environ.get('OPENID_PROVIDER_URL',ISSUER).rstrip('/')
            if provider_url!=ISSUER:parser.error('Only the fixed HF OAuth provider is supported')
            provider=HFOAuthProvider(os.environ.get('OAUTH_CLIENT_ID',''),os.environ.get('OAUTH_CLIENT_SECRET',''),
                                     client_type=args.oauth_client_type)
            identities=IdentitySessions(provider,args.oauth_origin or origins[0])
            from .protocols import ProtocolRegistry
            registry=ProtocolRegistry(args.protocol_registry) if args.protocol_registry else None
            from .policy_decisions import configured_policy
            policy=configured_policy(args.policy_root,args.policy_head_sha256)
            if args.checkpoint_root and args.state_bucket:
                parser.error('Select either retained filesystem or remote state checkpoints')
            if args.state_bucket:
                from .remote_durability import HFS3StateObjects,RemoteCheckpointLedger,open_acknowledged_store
                objects=HFS3StateObjects.from_secrets(args.state_bucket,
                    hf_token=os.environ.get('KOEVD_STATE_TOKEN',''),
                    access_key_id=os.environ.get('KOEVD_STATE_ACCESS_KEY_ID',''),
                    secret_access_key=os.environ.get('KOEVD_STATE_SECRET_ACCESS_KEY',''))
                ledger=RemoteCheckpointLedger(objects,prefix=args.state_prefix,initialize_empty=args.initialize_state)
                store=open_acknowledged_store(args.submission_root,ledger)
            elif args.initialize_state or args.state_prefix!='koevd-state-v1':
                parser.error('Remote initialization/prefix requires --state-bucket')
            elif args.checkpoint_root:
                from .durability import AcknowledgedSubmissionStore, FileCheckpointLedger
                ledger=FileCheckpointLedger(args.checkpoint_root)
                # Restore is an explicit operator action, not silent empty initialization.
                store=AcknowledgedSubmissionStore(args.submission_root,ledger)
            else:
                store=LocalSubmissionStore(args.submission_root)
            persistent=SubmissionService(store,{k:v['index'] for k,v in catalog.indexes.items()},registry=registry,rank_policy=policy,
                                         allow_self_reported_summaries=args.self_reported_summaries,**roles)
            registration=RegistrationWeb(persistent,identities)
        elif args.self_reported_summaries or args.checkpoint_root or args.state_bucket or args.initialize_state or args.state_prefix!='koevd-state-v1' or args.roles_file or args.oauth_origin or args.protocol_registry or args.policy_root or args.policy_head_sha256 or args.oauth_client_type!='confidential':parser.error('OAuth/roles/admission configuration requires --submission-root')
        import uvicorn
        app=create_app(service,origins=origins,frame_ancestors=("'self'",'https://huggingface.co'),registration=registration,
                       deployment_notice=os.environ.get('KOEVD_DEPLOYMENT_NOTICE'))
        uvicorn.run(app,host=args.host,port=args.port,access_log=False,workers=1)
    finally:
        if not service.closed:service.close()
        if registration is not None:registration.close()
        if temporary:temporary.cleanup()


if __name__=='__main__':main()
