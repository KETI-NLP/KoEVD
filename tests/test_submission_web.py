"""CPU provider doubles: no actual HF login, GPU inference or publication."""
from copy import deepcopy
from hashlib import sha256
import json
import asyncio
import threading
from urllib.parse import parse_qs, urlsplit
import unittest
from unittest.mock import patch

from koevd_eval.oauth import HFOAuthProvider, IdentitySessions
from koevd_eval.storage import LocalSubmissionStore, StorageError
from koevd_eval.submissions import Principal, SubmissionService
from koevd_eval.submission_web import RegistrationWeb
from koevd_eval.spaces import create_app
from koevd_eval.results import _seal, canonical_hash
import test_spaces


class SyntheticProvider:
    client_id='SYNTHETIC-oauth-app'
    def __init__(self):self.calls=[]
    def exchange(self,code,verifier,redirect_uri):
        self.calls.append((code,verifier,redirect_uri))
        if code not in ('SYNTHETIC-author','SYNTHETIC-other','SYNTHETIC-reviewer','SYNTHETIC-admin'):
            raise StorageError('oauth_provider_failed','SYNTHETIC identity rejected',502)
        return {'sub':code,'preferred_username':code},120


def subject(name):return 'hf:'+sha256(name.encode()).hexdigest()


class OAuthTests(unittest.TestCase):
    def setUp(self):
        self.provider=SyntheticProvider();self.clock=[0]
        self.ids=IdentitySessions(self.provider,'http://127.0.0.1',clock=lambda:self.clock[0])
    def start(self):
        url,binding=self.ids.begin();query=parse_qs(urlsplit(url).query)
        return query,binding
    def complete(self):
        query,binding=self.start();return self.ids.complete(query['state'][0],binding,'SYNTHETIC-author')

    def test_pkce_state_is_bound_to_browser_and_consumed_once(self):
        query,binding=self.start()
        self.assertEqual(query['scope'],['openid profile']);self.assertEqual(query['code_challenge_method'],['S256'])
        with self.assertRaises(StorageError):self.ids.complete(query['state'][0],'another-browser','SYNTHETIC-author')
        self.assertEqual(self.provider.calls,[])
        token,ttl=self.ids.complete(query['state'][0],binding,'SYNTHETIC-author')
        self.assertEqual(ttl,120)
        entry=self.ids.get(token);self.assertEqual(entry['principal'],Principal(subject('SYNTHETIC-author'),'hf_oauth'))
        self.assertNotIn(token,self.ids.sessions)
        with self.assertRaises(StorageError):self.ids.complete(query['state'][0],binding,'SYNTHETIC-author')
        self.assertEqual(len(self.provider.calls),1)

    def test_expired_state_and_session_are_not_recreated_by_reads(self):
        query,binding=self.start();self.clock[0]=301
        with self.assertRaises(StorageError):self.ids.complete(query['state'][0],binding,'SYNTHETIC-author')
        token,_=self.complete();self.clock[0]+=121
        with self.assertRaises(StorageError):self.ids.get(token)
        self.assertEqual(self.ids.sessions,{})

    def test_rotation_csrf_logout_and_restart(self):
        token,_=self.complete();entry=self.ids.get(token)
        with self.assertRaises(StorageError):self.ids.logout(token,'incorrect')
        query,binding=self.start();replacement,_=self.ids.complete(query['state'][0],binding,'SYNTHETIC-author',previous_session=token)
        with self.assertRaises(StorageError):self.ids.get(token)
        self.ids.logout(replacement,self.ids.get(replacement)['csrf'])
        with self.assertRaises(StorageError):self.ids.get(replacement)
        token,_=self.complete();self.ids.close()
        with self.assertRaises(StorageError):self.ids.get(token)

    def test_provider_failure_consumes_callback_without_reflecting_token(self):
        query,binding=self.start()
        with self.assertRaises(StorageError):self.ids.complete(query['state'][0],binding,'unrecognized-code')
        with self.assertRaises(StorageError):self.ids.complete(query['state'][0],binding,'SYNTHETIC-author')
        self.assertEqual(len(self.provider.calls),1)

    def test_capacity_and_replaced_browser_attempt_are_bounded(self):
        ids=IdentitySessions(self.provider,'http://localhost',max_pending=1,max_sessions=1)
        url,binding=ids.begin()
        with self.assertRaises(StorageError):ids.begin()
        url2,binding2=ids.begin(binding)
        self.assertEqual(len(ids.pending),1)
        with self.assertRaises(StorageError):ids.complete(parse_qs(urlsplit(url).query)['state'][0],binding,'SYNTHETIC-author')
        ids.complete(parse_qs(urlsplit(url2).query)['state'][0],binding2,'SYNTHETIC-author')
        url3,binding3=ids.begin()
        with self.assertRaises(StorageError):ids.complete(parse_qs(urlsplit(url3).query)['state'][0],binding3,'SYNTHETIC-other')
        self.assertEqual(len(ids.sessions),1)

    def test_fixed_https_provider_exchanges_secret_only_server_side_and_uses_userinfo(self):
        provider=HFOAuthProvider('SYNTHETIC-client','SYNTHETIC-secret')
        responses=[{'access_token':'SYNTHETIC-access','expires_in':120,'token_type':'Bearer','id_token':'UNVERIFIED-and-ignored'},
                   {'sub':'SYNTHETIC-stable-sub','preferred_username':'fixture'}]
        with patch.object(HFOAuthProvider,'_json',side_effect=responses) as mocked:
            info,ttl=provider.exchange('SYNTHETIC-code','SYNTHETIC-verifier','http://localhost/auth/callback')
        self.assertEqual(info['sub'],'SYNTHETIC-stable-sub');self.assertEqual(ttl,120)
        token_req,user_req=[call.args[0] for call in mocked.call_args_list]
        self.assertEqual(token_req.full_url,'https://huggingface.co/oauth/token')
        self.assertEqual(user_req.full_url,'https://huggingface.co/oauth/userinfo')
        self.assertEqual(parse_qs(token_req.data.decode())['code_verifier'],['SYNTHETIC-verifier'])
        self.assertTrue(token_req.get_header('Authorization').startswith('Basic '))
        self.assertEqual(user_req.get_header('Authorization'),'Bearer SYNTHETIC-access')
        self.assertNotIn('SYNTHETIC-secret',repr(provider))

    def test_invalid_provider_token_or_subject_does_not_create_identity(self):
        provider=HFOAuthProvider('SYNTHETIC-client','SYNTHETIC-secret')
        for response in ({'access_token':'SYNTHETIC-access','token_type':'not-bearer','expires_in':20},
                         {'access_token':'bad\nvalue','token_type':'Bearer','expires_in':20}):
            with patch.object(HFOAuthProvider,'_json',return_value=response):
                with self.assertRaises(StorageError):provider.exchange('code','verifier','http://localhost/auth/callback')
        with patch.object(HFOAuthProvider,'_json',side_effect=[{'access_token':'SYNTHETIC-access','token_type':'Bearer','expires_in':20},{}]):
            with self.assertRaises(StorageError):provider.exchange('code','verifier','http://localhost/auth/callback')

    def test_public_client_requires_explicit_mode_and_rejects_secret_or_invalid_mode(self):
        for kwargs in ({}, {'client_type':'confidential'}, {'client_type':'automatic'},
                       {'client_type':'public','client_secret':'SYNTHETIC-secret'},
                       {'client_type':'public','client_secret':None}):
            with self.subTest(configuration=list(kwargs)):
                with self.assertRaises(ValueError):HFOAuthProvider('SYNTHETIC-client',**kwargs)
        for client_id in ('', 'bad\nclient'):
            with self.assertRaises(ValueError):HFOAuthProvider(client_id,client_type='public')

    def test_public_client_pkce_exchange_has_no_basic_or_secret_and_uses_verified_userinfo(self):
        provider=HFOAuthProvider('SYNTHETIC-client',client_type='public')
        ids=IdentitySessions(provider,'https://workspace.example')
        url,binding=ids.begin();query=parse_qs(urlsplit(url).query)
        responses=[{'access_token':'SYNTHETIC-access','expires_in':120,'token_type':'Bearer',
                    'id_token':'UNVERIFIED-admin-claim'}, {'sub':'SYNTHETIC-sub','preferred_username':'fixture'}]
        with patch.object(HFOAuthProvider,'_json',side_effect=responses) as mocked:
            with self.assertRaises(StorageError):ids.complete(query['state'][0],'wrong-browser','SYNTHETIC-code')
            mocked.assert_not_called()
            token,ttl=ids.complete(query['state'][0],binding,'SYNTHETIC-code')
            with self.assertRaises(StorageError):ids.complete(query['state'][0],binding,'SYNTHETIC-code')
        self.assertEqual(ttl,120)
        self.assertEqual(ids.get(token)['principal'],Principal(subject('SYNTHETIC-sub'),'hf_oauth'))
        token_req,user_req=[call.args[0] for call in mocked.call_args_list]
        form=parse_qs(token_req.data.decode())
        from base64 import urlsafe_b64encode
        expected=urlsafe_b64encode(sha256(form['code_verifier'][0].encode('ascii')).digest()).rstrip(b'=').decode('ascii')
        self.assertEqual(query['code_challenge'],[expected]);self.assertEqual(query['scope'],['openid profile'])
        self.assertEqual(form,{'client_id':['SYNTHETIC-client'],'code':['SYNTHETIC-code'],
                              'code_verifier':form['code_verifier'],'grant_type':['authorization_code'],
                              'redirect_uri':['https://workspace.example/auth/callback']})
        self.assertEqual(token_req.full_url,'https://huggingface.co/oauth/token')
        self.assertIsNone(token_req.get_header('Authorization'))
        self.assertEqual(user_req.full_url,'https://huggingface.co/oauth/userinfo')
        self.assertEqual(user_req.get_header('Authorization'),'Bearer SYNTHETIC-access')
        self.assertNotIn('SYNTHETIC-access',repr(ids.sessions))

    def test_public_client_missing_or_invalid_pkce_never_contacts_provider(self):
        provider=HFOAuthProvider('SYNTHETIC-client',client_type='public')
        for verifier in (None,'','a'*42,'a'*129,'a'*42+'!','a'*42+'é'):
            with self.subTest(verifier_type=type(verifier).__name__), patch.object(HFOAuthProvider,'_json') as mocked:
                with self.assertRaises(StorageError) as caught:provider.exchange('code',verifier,'http://localhost/auth/callback')
                self.assertEqual(caught.exception.code,'oauth_verifier_invalid');mocked.assert_not_called()

    def test_nonlocal_http_or_user_selected_redirect_is_rejected(self):
        for origin in ('http://unsafe.example','https://example.com/elsewhere','https://user@host','https://host?redirect=other'):
            with self.assertRaises(ValueError):IdentitySessions(self.provider,origin)


class SubmissionHTTPTests(unittest.TestCase):
    setUpFixture=test_spaces.SpaceServiceTests.setUp
    write=test_spaces.SpaceServiceTests.write
    sha=test_spaces.SpaceServiceTests.sha
    upload=test_spaces.SpaceServiceTests.upload
    def setUp(self):
        self.setUpFixture()
        from fastapi.testclient import TestClient
        self.provider=SyntheticProvider();self.ids=IdentitySessions(self.provider,'http://127.0.0.1',clock=lambda:self.clock[0])
        self.submissions=SubmissionService(LocalSubmissionStore(self.root/'persistent'),{'trusted-demo':self.index},
            reviewers=[subject('SYNTHETIC-reviewer')],admins=[subject('SYNTHETIC-admin')])
        self.registration=RegistrationWeb(self.submissions,self.ids)
        self.app=create_app(self.service,origins=['http://127.0.0.1'],registration=self.registration)
        self.clients=[TestClient(self.app,base_url='http://127.0.0.1',follow_redirects=False) for _ in range(4)]
        for client in self.clients:self.addCleanup(client.close)
        self.author,self.other,self.reviewer,self.admin=self.clients
        self.counter=0

    def login(self,client,code):
        response=client.get('/auth/login');self.assertEqual(response.status_code,302)
        state=parse_qs(urlsplit(response.headers['location']).query)['state'][0]
        response=client.get('/auth/callback',params={'state':state,'code':code});self.assertEqual(response.status_code,303)
        info=client.get('/api/identity').json();self.assertTrue(info['signed_in']);return info

    def headers(self,client,*,analysis=True):
        info=client.get('/api/identity').json()
        value={'origin':'http://127.0.0.1','X-Koevd-Auth-CSRF':info.get('csrf_token','')}
        if analysis:value.update(Authorization='Bearer '+self.token,**{'X-Koevd-CSRF':self.csrf})
        return value

    def create(self):
        self.login(self.author,'SYNTHETIC-author');entry=self.upload()
        response=self.author.post('/api/submissions',json={'upload_id':entry['id'],'key':'create-1'},headers=self.headers(self.author))
        self.assertEqual(response.status_code,201,response.text);return response.json(),entry

    def action(self,client,state,name,**extras):
        self.counter+=1
        return client.post('/api/submissions/'+state['id']+'/actions',json={'name':name,'key':'action-'+str(self.counter),
            'reason':'SYNTHETIC permission operation','expected_version':state['version'],**extras},headers=self.headers(client,analysis=False))

    def publish(self,scope='summary'):
        state,entry=self.create();self.login(self.reviewer,'SYNTHETIC-reviewer');self.login(self.admin,'SYNTHETIC-admin')
        for client,name,kwargs in ((self.author,'request_review',{'consent':{'scope':scope,'accepted':True,'rights_statement':'SYNTHETIC permission fixture'}}),
                                   (self.reviewer,'start_review',{}),(self.reviewer,'approve',{'rights_evidence':'SYNTHETIC permission fixture'}),(self.admin,'publish',{})):
            response=self.action(client,state,name,**kwargs);self.assertEqual(response.status_code,200,response.text);state=response.json()
        return state,entry

    def test_anonymous_analysis_cannot_claim_identity_or_role(self):
        entry=self.upload()
        response=self.author.post('/api/submissions',json={'upload_id':entry['id'],'key':'anonymous'},headers={'origin':'http://127.0.0.1','Authorization':'Bearer '+self.token,'X-Koevd-CSRF':self.csrf})
        self.assertEqual(response.status_code,401)
        self.login(self.author,'SYNTHETIC-author')
        for field,value in (('owner',subject('SYNTHETIC-admin')),('role','admin'),('index_id','uploaded-index'),('gold',{})):
            response=self.author.post('/api/submissions',json={'upload_id':entry['id'],'key':'claim-'+field,field:value},headers=self.headers(self.author))
            self.assertEqual(response.status_code,400)
        self.assertEqual(self.author.get('/api/submissions').json()['items'],[])

    def test_public_oauth_http_identity_keeps_private_ownership_and_review_permissions(self):
        self.ids.provider=HFOAuthProvider('SYNTHETIC-client',client_type='public')
        requests=[]
        def response(request):
            requests.append(request)
            if request.full_url.endswith('/oauth/token'):
                self.assertIsNone(request.get_header('Authorization'))
                form=parse_qs(request.data.decode());self.assertNotIn('client_secret',form)
                return {'access_token':form['code'][0],'token_type':'Bearer','expires_in':120}
            return {'sub':request.get_header('Authorization').removeprefix('Bearer ')}
        with patch.object(HFOAuthProvider,'_json',side_effect=response):
            state,entry=self.create();self.login(self.other,'SYNTHETIC-other')
            self.assertEqual(self.other.get('/api/submissions').json()['items'],[])
            denied=self.action(self.other,state,'start_review')
            self.assertEqual(denied.status_code,404)
            self.assertEqual(self.action(self.author,state,'start_review').status_code,403)
            public=self.author.get('/api/public/submissions').json()
            self.assertEqual(public['items'],[])
            own=self.author.get('/api/submissions/'+state['id']).json()
            self.assertEqual(own['workflow'],'draft')
        self.assertEqual(len(requests),4)

    def test_origin_csrf_cookie_and_session_source_are_independent(self):
        state,entry=self.create();headers=self.headers(self.author)
        for change in ({'origin':'https://other.example'},{'origin':''},{'X-Koevd-Auth-CSRF':'wrong'},{'X-Koevd-CSRF':'wrong'}):
            value={**headers,**change}
            response=self.author.post('/api/submissions',json={'upload_id':entry['id'],'key':'try'},headers=value)
            self.assertEqual(response.status_code,403)
        token,info=self.service.create_session()
        value={**headers,'Authorization':'Bearer '+token,'X-Koevd-CSRF':info['csrf_token']}
        self.assertEqual(self.author.post('/api/submissions',json={'upload_id':entry['id'],'key':'try'},headers=value).status_code,404)
        self.assertEqual(self.author.post('/api/submissions',json={'upload_id':entry['id'],'key':'try','actor':'other'},headers=headers).status_code,400)

    def test_draft_acl_exact_retry_history_and_original(self):
        state,entry=self.create();self.login(self.other,'SYNTHETIC-other')
        replay=self.author.post('/api/submissions',json={'upload_id':entry['id'],'key':'create-1'},headers=self.headers(self.author))
        self.assertEqual(replay.json(),state)
        for suffix in ('','/history','/result'):
            self.assertEqual(self.other.get('/api/submissions/'+state['id']+suffix).status_code,404)
        self.assertEqual(self.other.get('/api/submissions').json()['items'],[])
        self.assertEqual(self.author.get('/api/submissions/'+state['id']+'/result').json(),self.document)
        self.assertEqual(self.author.get('/api/submissions/'+state['id']+'/history').json()['events'][0]['action'],'create')
        self.assertEqual(self.author.get('/api/public/submissions').json()['items'],[])

    def test_summary_review_publish_metric_limits_and_withdrawal_http(self):
        state,_=self.publish('summary');url='/api/public/submissions/'+state['id']
        summary=self.other.get(url).json();self.assertEqual(summary['rank_policy_status'],'candidate')
        self.assertEqual(summary['rank_admission']['eligible_metric_ids'],[])
        self.assertEqual(self.other.get(url+'/result').status_code,403)
        self.assertNotIn('SYNTHETIC permission',json.dumps(summary))
        response=self.action(self.author,state,'withdraw');self.assertEqual(response.status_code,200)
        self.assertEqual(self.other.get(url).status_code,404)
        self.assertEqual(self.other.get(url+'/result').status_code,404)
        self.assertEqual(self.other.get('/api/public/submissions').json()['items'],[])
        self.assertEqual(self.author.get('/api/submissions/'+state['id']+'/result').json(),self.document)

    def test_raw_scope_is_explicit_and_source_can_be_reimported_for_private_comparison(self):
        state,_=self.publish('responses')
        original=self.other.get('/api/public/submissions/'+state['id']+'/result').json()
        self.assertEqual(original,self.document)
        token,info=self.service.create_session();session,path=self.service.begin_upload(token,info['csrf_token'])
        path.write_text(json.dumps(original),encoding='utf-8')
        entry=self.service.finish_upload(token,session,path)
        restored,index_id=self.service.submission_source(token,info['csrf_token'],entry['id'])
        self.assertEqual(restored,original);self.assertEqual(index_id,'trusted-demo')

    def test_complete_public_metric_projection_has_no_uploaded_policy_or_private_rows(self):
        empty=self.other.get('/api/public/leaderboard').json()
        self.assertEqual(empty['publication_count'],0)
        state,_=self.create() # A saved private original must stay outside the board.
        self.assertEqual(self.other.get('/api/public/leaderboard').json()['publication_count'],0)
        self.login(self.reviewer,'SYNTHETIC-reviewer');self.login(self.admin,'SYNTHETIC-admin')
        for client,name,options in ((self.author,'request_review',{'consent':{'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC permission fixture'}}),
                (self.reviewer,'start_review',{}),(self.reviewer,'approve',{'rights_evidence':'SYNTHETIC permission fixture'}),(self.admin,'publish',{})):
            response=self.action(client,state,name,**options);self.assertEqual(response.status_code,200,response.text);state=response.json()
        published=state
        response=self.other.get('/api/public/leaderboard?rank_policy=ratified&execution_scope=actual_gpu')
        self.assertEqual(response.status_code,200,response.text)
        result=response.json();self.assertEqual(result['publication_count'],1)
        self.assertEqual(result['policy_status'],'candidate');self.assertFalse(result['official_ranking_enabled'])
        self.assertEqual(result['boards'],[]);self.assertTrue(result['excluded'])
        self.assertEqual({p['submission_id'] for p in result['publications']},{published['id']})
        for text in ('review_statement','evidence_files','SYNTHETIC permission fixture','"owner":'):
            self.assertNotIn(text,json.dumps(result))
        self.assertEqual(self.other.post('/api/public/leaderboard',json={'policy':'ratified'}).status_code,405)
        self.assertEqual(self.action(self.author,published,'withdraw').status_code,200)
        self.assertEqual(self.other.get('/api/public/leaderboard').json()['publication_count'],0)

    def test_owner_cannot_review_and_reviewer_cannot_publish(self):
        state,_=self.create()
        consent={'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC permission'}
        state=self.action(self.author,state,'request_review',consent=consent).json()
        self.assertEqual(self.action(self.author,state,'start_review').status_code,403)
        self.login(self.reviewer,'SYNTHETIC-reviewer')
        state=self.action(self.reviewer,state,'start_review').json()
        state=self.action(self.reviewer,state,'approve',rights_evidence='SYNTHETIC review').json()
        self.assertEqual(self.action(self.reviewer,state,'publish').status_code,403)

    def test_stale_action_and_generation_preserving_revisions_remain_enforced(self):
        state,_=self.create();consent={'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC permission'}
        current=self.action(self.author,state,'request_review',consent=consent).json()
        self.assertEqual(self.action(self.author,state,'withdraw').status_code,409)
        changed=deepcopy(self.document);changed['run']['created_at']='SYNTHETIC-new-time'
        changed=_seal({k:v for k,v in changed.items() if k!='content_sha256'})
        entry=self.upload(changed)
        response=self.author.post('/api/submissions/'+state['id']+'/revisions',json={'upload_id':entry['id'],'expected_version':current['version'],
            'kind':'measurement_recheck','reason':'SYNTHETIC measurement only','key':'revision-1'},headers=self.headers(self.author))
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()['head_revision'],2)
        self.assertEqual(self.author.get('/api/submissions/'+state['id']+'/result',params={'revision':1}).json(),self.document)

    def test_state_binding_replay_duplicate_query_and_cancel_errors_are_bounded(self):
        response=self.author.get('/auth/login');state=parse_qs(urlsplit(response.headers['location']).query)['state'][0]
        self.assertEqual(self.other.get('/auth/callback',params={'state':state,'code':'SYNTHETIC-author'}).status_code,401)
        self.assertEqual(self.author.get('/auth/callback?state='+state+'&state=other&code=SYNTHETIC-author').status_code,401)
        self.assertEqual(self.author.get('/auth/callback',params={'state':state,'code':'SYNTHETIC-author'}).status_code,303)
        self.assertEqual(self.author.get('/auth/callback',params={'state':state,'code':'SYNTHETIC-author'}).status_code,401)
        response=self.author.get('/auth/callback?error=denied&error_description=PRIVATE-CODE')
        self.assertNotIn('PRIVATE-CODE',response.text);self.assertEqual(response.status_code,401)

    def test_identity_cookie_attributes_logout_and_restart_preserve_originals(self):
        state,_=self.create()
        response=self.author.get('/auth/login');query=parse_qs(urlsplit(response.headers['location']).query)
        response=self.author.get('/auth/callback',params={'state':query['state'][0],'code':'SYNTHETIC-author'})
        cookies=response.headers.get_list('set-cookie')
        self.assertTrue(any('HttpOnly' in c and 'SameSite=lax' in c and 'koevd_identity=' in c for c in cookies))
        response=self.author.post('/api/identity/logout',json={},headers=self.headers(self.author,analysis=False))
        self.assertEqual(response.status_code,200);self.assertFalse(self.author.get('/api/identity').json()['signed_in'])
        self.assertEqual(self.author.get('/api/submissions/'+state['id']).status_code,401)
        self.login(self.author,'SYNTHETIC-author');self.ids.close()
        self.assertEqual(self.author.get('/api/submissions/'+state['id']).status_code,401)
        restarted=SubmissionService(LocalSubmissionStore(self.root/'persistent'),{'trusted-demo':self.index})
        self.assertEqual(restarted.result(Principal(subject('SYNTHETIC-author'),'hf_oauth'),state['id']),self.document)

    def test_pagination_and_operator_index_mismatch(self):
        self.create();self.login(self.other,'SYNTHETIC-other')
        self.assertEqual(self.other.get('/api/submissions?limit=1').json()['items'],[])
        self.assertEqual(self.author.get('/api/submissions?limit=101').status_code,400)
        self.assertEqual(self.author.get('/api/public/submissions?limit=101').status_code,400)
        self.assertEqual(self.author.get('/api/submissions?after=../../escape').status_code,400)
        wrong=SubmissionService(LocalSubmissionStore(self.root/'different-persistent'),{'another':self.index})
        with self.assertRaises(ValueError):create_app(self.service,origins=['http://127.0.0.1'],registration=RegistrationWeb(wrong,self.ids))

    def test_disabled_registration_assets_and_bounded_operation_body(self):
        self.login(self.author,'SYNTHETIC-author')
        body=b'{"upload_id":"x","key":"same","key":"duplicate"}'
        headers={**self.headers(self.author),'content-type':'application/json'}
        self.assertEqual(self.author.post('/api/submissions',content=body,headers=headers).status_code,400)
        self.assertEqual(self.author.post('/api/submissions',content=b'x'*16385,headers=headers).status_code,413)
        self.assertEqual(self.author.get('/assets/registration.js').status_code,200)
        self.assertEqual(self.author.get('/assets/navigation.js').status_code,200)
        self.assertEqual(self.author.get('/submit').status_code,200)
        self.assertTrue(self.author.get('/api/registration').json()['review_requests_enabled'])
        self.assertIn('no-store',self.author.get('/api/identity').headers['cache-control'])
        app=create_app(self.service,origins=['http://127.0.0.1'])
        from fastapi.testclient import TestClient
        with TestClient(app,base_url='http://127.0.0.1') as client:
            self.assertFalse(client.get('/api/registration').json()['enabled'])
            self.assertEqual(client.get('/auth/login').status_code,404)

    def test_upload_id_types_are_rejected_before_session_dictionary_lookup(self):
        self.login(self.author,'SYNTHETIC-author')
        for value in (None,[],{},123,'../../private-file'):
            response=self.author.post('/api/submissions',json={'upload_id':value,'key':'bad-upload-id'},headers=self.headers(self.author))
            self.assertEqual(response.status_code,400,response.text)

    def test_https_cookie_uses_host_prefix_secure_and_same_origin_callback(self):
        from fastapi.testclient import TestClient
        identities=IdentitySessions(self.provider,'https://koevd.example')
        app=create_app(self.service,origins=['https://koevd.example'],registration=RegistrationWeb(self.submissions,identities))
        with TestClient(app,base_url='https://koevd.example',follow_redirects=False) as client:
            response=client.get('/auth/login');query=parse_qs(urlsplit(response.headers['location']).query)
            self.assertEqual(query['redirect_uri'],['https://koevd.example/auth/callback'])
            response=client.get('/auth/callback',params={'state':query['state'][0],'code':'SYNTHETIC-author'})
            self.assertEqual(response.status_code,303)
            self.assertTrue(any('__Host-koevd_identity=' in value and 'Secure' in value and 'HttpOnly' in value and 'Path=/' in value for value in response.headers.get_list('set-cookie')))
            self.assertTrue(client.get('/api/identity').json()['signed_in'])

    def test_bounded_operation_queue_accepts_three_waiters_and_rejects_overflow(self):
        import httpx
        entered,release=threading.Event(),threading.Event();calls=[]
        def slow(**kwargs):
            calls.append(1);entered.set()
            if not release.wait(5):raise RuntimeError('Fixture release timed out')
            return {'items':[],'next_cursor':None}
        async def check():
            transport=httpx.ASGITransport(app=self.app)
            async with httpx.AsyncClient(transport=transport,base_url='http://127.0.0.1') as client:
                first=asyncio.create_task(client.get('/api/public/submissions'))
                self.assertTrue(await asyncio.to_thread(entered.wait,2))
                waiters=[asyncio.create_task(client.get('/api/public/submissions')) for _ in range(3)]
                await asyncio.sleep(.05)
                overflow=await client.get('/api/public/submissions')
                self.assertEqual(overflow.status_code,503);self.assertEqual(len(calls),1)
                release.set()
                self.assertTrue(all(r.status_code==200 for r in await asyncio.gather(first,*waiters)))
                self.assertEqual(len(calls),4)
        with patch.object(self.submissions,'public_page',side_effect=slow):
            try:asyncio.run(check())
            finally:release.set()


if __name__=='__main__':unittest.main()
