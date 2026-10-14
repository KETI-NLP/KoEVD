"""Authenticated submission HTTP routes attached to the existing Spaces app.

This transport enables a local candidate publication projection only. The OAuth
provider and persistent local store are operator configuration, never uploads.
"""
import asyncio
import json

from .oauth import IdentitySessions
from .results import _unique_object
from .storage import StorageError
from .submissions import SubmissionService


class RegistrationWeb:
    def __init__(self, submissions, identities):
        if not isinstance(submissions,SubmissionService) or not isinstance(identities,IdentitySessions):
            raise ValueError('Configured submission store and identity sessions required')
        self.submissions,self.identities=submissions,identities

    def cleanup(self):self.identities.cleanup()
    def close(self):self.identities.close()


def install_routes(app, analysis, registration, *, allowed_origins, bounded_body):
    from fastapi import Request
    from fastapi.responses import JSONResponse, RedirectResponse, Response
    from starlette.concurrency import run_in_threadpool
    globals()['Request']=Request
    identities,submissions=registration.identities,registration.submissions
    if identities.origin not in allowed_origins:raise ValueError('OAuth canonical origin must be an allowed app origin')
    expected={name:item['index']['content_sha256'] for name,item in analysis.catalog.indexes.items()}
    actual={name:index['content_sha256'] for name,index in submissions.indexes.items()}
    if expected!=actual:raise ValueError('Submission and analysis operator indexes must match')
    gate=asyncio.Semaphore(1)
    slots=asyncio.Semaphore(4)  # one active CPU operation plus at most three waiters

    @app.exception_handler(StorageError)
    async def storage_error(request,exc):
        return JSONResponse({'error':{'code':exc.code,'message':str(exc)}},status_code=exc.status)

    def actor(request, mutate=False):
        if mutate and request.headers.get('origin') not in allowed_origins:
            raise StorageError('identity_origin','Same-origin submission request required.',403)
        entry=identities.get(request.cookies.get(identities.cookie_name),
                             request.headers.get('x-koevd-auth-csrf','') if mutate else None)
        return entry['principal']

    async def fields(request, required, optional=()):
        if request.headers.get('content-type','').split(';')[0].lower()!='application/json':
            raise StorageError('content_type','Use a bounded JSON operation request.',415)
        try:
            body=await asyncio.wait_for(bounded_body(request,16384),timeout=30)
            value=json.loads(body.decode('utf-8'),object_pairs_hook=_unique_object)
            if not isinstance(value,dict) or not set(required)<=set(value) or set(value)-set(required)-set(optional):raise ValueError('Unexpected fields')
            return value
        except (ValueError,UnicodeError,TypeError):
            raise StorageError('operation_body','Invalid submission operation. Identity, roles, gold and scores are not accepted.',400) from None
        except asyncio.TimeoutError:raise StorageError('operation_timeout','Operation body timed out.',408) from None

    async def invoke(function,*args,**kwargs):
        # No unbounded CPU queue of repeated public summaries/DB writes. The
        # thread finishes before the slot is released, even on disconnect.
        if slots.locked():raise StorageError('registration_busy','Submission operation capacity reached. Try later.',503)
        await slots.acquire()
        try:
            async with gate:
                task=asyncio.create_task(run_in_threadpool(function,*args,**kwargs))
                try:return await asyncio.shield(task)
                except asyncio.CancelledError:
                    try:await task
                    finally:raise
                except ValueError:
                    raise StorageError('result_invalid','Result did not match the operator-selected input contract.',400) from None
        finally:slots.release()

    def analysis_credentials(request):
        header=request.headers.get('authorization','')
        if not header.startswith('Bearer ') or len(header)>300:
            raise StorageError('analysis_session_required','Select a result from your private analysis session.',401)
        return header[7:],request.headers.get('x-koevd-csrf','')

    @app.get('/auth/login')
    async def login(request:Request):
        if request.headers.get('sec-fetch-site')=='cross-site' or request.headers.get('origin') not in (None,*allowed_origins):
            raise StorageError('identity_origin','Open sign-in from your KoEVD workspace.',403)
        url,binding=identities.begin(request.cookies.get(identities.binding_cookie))
        response=RedirectResponse(url,status_code=302)
        response.set_cookie(identities.binding_cookie,binding,max_age=identities.pending_ttl,secure=identities.secure,httponly=True,samesite='lax',path='/')
        return response

    @app.get('/auth/callback')
    async def callback(request:Request):
        pairs=list(request.query_params.multi_items())
        if len(pairs)!=len(dict(pairs)) or set(dict(pairs))-{'code','state','error','error_description'}:
            raise StorageError('oauth_state_invalid','Invalid sign-in callback.',401)
        if 'error' in request.query_params:
            # Provider errors and descriptions are never reflected to the page.
            raise StorageError('oauth_cancelled','Sign-in was cancelled. Start sign-in again.',401)
        token,ttl=await invoke(identities.complete,request.query_params.get('state'),request.cookies.get(identities.binding_cookie),
            request.query_params.get('code'),previous_session=request.cookies.get(identities.cookie_name))
        response=RedirectResponse(identities.origin+'/auth/done',status_code=303)
        response.delete_cookie(identities.binding_cookie,path='/',secure=identities.secure,httponly=True,samesite='lax')
        response.set_cookie(identities.cookie_name,token,max_age=ttl,secure=identities.secure,httponly=True,samesite='lax',path='/')
        return response

    @app.get('/auth/done')
    async def done():
        return Response('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>KoEVD sign-in</title><h1>Sign-in complete</h1><p>Return to your KoEVD workspace and select “Check sign-in”.</p><p>If the embedded view blocks sign-in cookies, open the workspace in this tab.</p><a href="/">Open KoEVD workspace</a></html>',media_type='text/html')

    @app.get('/api/identity')
    async def identity(request:Request):
        try:entry=identities.get(request.cookies.get(identities.cookie_name))
        except StorageError as exc:
            if exc.code=='identity_required':return {'signed_in':False}
            raise
        principal=entry['principal']
        return {'signed_in':True,'subject':principal.subject,'username':entry['username'],'csrf_token':entry['csrf'],
            'reviewer':principal.subject in submissions.reviewers | submissions.admins,'admin':principal.subject in submissions.admins,
            'generation_verification':'user_reported','publication_environment':'local_candidate'}

    @app.post('/api/identity/logout')
    async def logout(request:Request):
        actor(request,True);await fields(request,())
        identities.logout(request.cookies.get(identities.cookie_name),request.headers.get('x-koevd-auth-csrf'))
        response=JSONResponse({'signed_in':False})
        response.delete_cookie(identities.cookie_name,path='/',secure=identities.secure,httponly=True,samesite='lax')
        return response

    @app.get('/api/submissions')
    async def listing(request:Request,after:str='',limit:int=50):
        return await invoke(submissions.visible_list,actor(request),after=after,limit=limit)

    @app.post('/api/submissions')
    async def create(request:Request):
        principal=actor(request,True);body=await fields(request,('upload_id','key'),('display_name','description'))
        token,csrf=analysis_credentials(request)
        def operation():
            document,index_id=analysis.submission_source(token,csrf,body['upload_id'])
            return submissions.create(principal,document,index_id,key=body['key'],
                                      display_name=body.get('display_name'),description=body.get('description',''))
        return JSONResponse(await invoke(operation),status_code=201)

    @app.post('/api/submissions/{submission_id}/metadata')
    async def metadata(submission_id:str,request:Request):
        principal=actor(request,True)
        body=await fields(request,('display_name','expected_version','key'),('description',))
        return await invoke(submissions.update_display,principal,submission_id,
                            display_name=body['display_name'],description=body.get('description',''),
                            expected_version=body['expected_version'],key=body['key'])

    @app.get('/api/submissions/{submission_id}')
    async def get(submission_id:str,request:Request):return await invoke(submissions.get,actor(request),submission_id)

    @app.get('/api/submissions/{submission_id}/history')
    async def history(submission_id:str,request:Request):return await invoke(submissions.history,actor(request),submission_id)

    @app.get('/api/submissions/{submission_id}/result')
    async def original(submission_id:str,request:Request,revision:int|None=None):
        return await invoke(submissions.result,actor(request),submission_id,revision=revision)

    @app.post('/api/submissions/{submission_id}/revisions')
    async def revise(submission_id:str,request:Request):
        principal=actor(request,True);body=await fields(request,('upload_id','key','expected_version','kind','reason'))
        token,csrf=analysis_credentials(request)
        def operation():
            document,index_id=analysis.submission_source(token,csrf,body['upload_id'])
            state=submissions.get(principal,submission_id)
            if index_id!=state['index_id']:raise StorageError('index_changed','Revision must use the same operator index.',409)
            return submissions.revise(principal,submission_id,document,key=body['key'],expected_version=body['expected_version'],kind=body['kind'],reason=body['reason'])
        return await invoke(operation)

    @app.post('/api/submissions/{submission_id}/actions')
    async def action(submission_id:str,request:Request):
        principal=actor(request,True)
        body=await fields(request,('name','key','expected_version','reason'),('consent','rights_evidence'))
        if body['name'] == 'publish_summary':
            if body.get('rights_evidence') is not None:
                raise StorageError('unexpected_rights_evidence', 'User summary publication cannot assert operator review')
            return await invoke(submissions.publish_summary,principal,submission_id,
                                consent=body.get('consent'),key=body['key'],expected_version=body['expected_version'],
                                reason=body['reason'])
        return await invoke(submissions.action,principal,submission_id,body['name'],key=body['key'],expected_version=body['expected_version'],
                            reason=body['reason'],consent=body.get('consent'),rights_evidence=body.get('rights_evidence'))

    @app.get('/api/public/submissions')
    async def public(after:str='',limit:int=50):
        return {**await invoke(submissions.public_page,after=after,limit=limit),'publication_environment':'local_candidate',
                'official_ranking_enabled':submissions.rank_policy.status=='ratified'}

    @app.get('/api/public/leaderboard')
    async def public_leaderboard():return await invoke(submissions.public_leaderboard)

    @app.get('/api/public/submissions/{submission_id}')
    async def public_summary(submission_id:str):return await invoke(submissions.public_summary,submission_id)

    @app.get('/api/public/submissions/{submission_id}/result')
    async def public_result(submission_id:str):return await invoke(submissions.public_result,submission_id)
