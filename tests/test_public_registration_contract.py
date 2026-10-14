"""Owner metadata and opt-in summary publication; fictional CPU identities."""
from copy import deepcopy
import unittest

import test_results as fixture_module
import test_submission_web as web_fixture
from koevd_eval.results import canonical_hash
from koevd_eval.storage import LocalSubmissionStore, StorageError
from koevd_eval.submissions import Principal, SubmissionService


CONSENT = {'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC fixture publication permission'}


class PublicRegistrationTests(unittest.TestCase):
    def setUp(self):
        fixture=fixture_module.ResultContractTests();fixture.setUp();self.addCleanup(fixture.doCleanups)
        self.fixture=fixture
        self.store=LocalSubmissionStore(fixture.root/'public-service')
        self.author=Principal('SYNTHETIC-author','operator_local')
        self.other=Principal('SYNTHETIC-other','operator_local')
        self.admin=Principal('SYNTHETIC-admin','operator_local')
        self.reviewer=Principal('SYNTHETIC-reviewer','operator_local')
        self.service=SubmissionService(self.store,{'fixture':fixture.index},reviewers=[self.reviewer.subject],
                                       admins=[self.admin.subject],allow_self_reported_summaries=True)

    def create(self, **kwargs):
        return self.service.create(self.author,self.fixture.document,'fixture',key='create',**kwargs)

    def summary(self, state, **kwargs):
        values={'consent':CONSENT,'expected_version':state['version'],'reason':'SYNTHETIC summary consent','key':'summary'}
        values.update(kwargs)
        return self.service.publish_summary(self.author,state['id'],**values)

    def assert_code(self, code, operation):
        with self.assertRaises(StorageError) as caught:operation()
        self.assertEqual(caught.exception.code,code)

    def test_display_changes_do_not_change_original_model_or_artifact(self):
        state=self.create(display_name='로봇용 모델 실험',description='SYNTHETIC 한국어 설명')
        renamed=self.service.update_display(self.author,state['id'],display_name='실험 버전 2',
            description='<img src=x onerror=alert(1)>',expected_version=state['version'],key='rename')
        self.assertEqual(renamed['display']['display_name'],'실험 버전 2')
        self.assertEqual(self.service.result(self.author,state['id']),self.fixture.document)
        history=self.service.history(self.author,state['id'])
        self.assertEqual(len(history['revisions']),1)
        self.assertEqual(history['events'][-1]['action'],'update_display')
        self.assertEqual(history['events'][0]['state']['display']['display_name'],'로봇용 모델 실험')
        self.assert_code('not_found',lambda:self.service.update_display(self.other,state['id'],
            display_name='forged',expected_version=renamed['version'],key='foreign'))
        self.assert_code('stale_version',lambda:self.service.update_display(self.author,state['id'],
            display_name='stale',expected_version=state['version'],key='stale'))

    def test_default_create_keeps_legacy_request_fingerprint(self):
        self.create()
        expected=canonical_hash({'action':'create','artifact':self.fixture.document['content_sha256'],'index':'fixture'})
        with self.store.connection() as db:
            self.assertEqual(db.execute('SELECT fingerprint FROM requests WHERE key=?',('create',)).fetchone()[0],expected)

    def test_summary_is_public_without_claiming_review_or_rank(self):
        state=self.summary(self.create(display_name='SYNTHETIC measured run'))
        self.assertEqual(state['workflow'],'registered');self.assertIsNone(state['approval'])
        value=self.service.public_summary(state['id'])
        self.assertFalse(value['official_rank_eligible'])
        self.assertEqual(value['verification']['generation'],'user_reported')
        self.assertEqual(value['display']['display_name'],'SYNTHETIC measured run')
        self.assertEqual(value['model'],self.fixture.document['run']['model'])
        self.assertEqual(self.service.public_page()['items'][0]['display'],state['display'])
        self.assert_code('responses_private',lambda:self.service.public_result(state['id']))
        self.assertEqual(self.service.result(self.author,state['id']),self.fixture.document)
        self.assertEqual(self.service.public_leaderboard()['boards'],[])

    def test_summary_opt_in_defaults_off_and_requires_own_explicit_consent(self):
        state=self.create()
        default=SubmissionService(self.store,{'fixture':self.fixture.index})
        self.assert_code('summary_publication_disabled',lambda:default.publish_summary(self.author,state['id'],
            consent=CONSENT,expected_version=state['version'],reason='SYNTHETIC',key='disabled'))
        for changes in ({'accepted':False},{'accepted':'true'},{'scope':'responses'},{'rank_eligible':True}):
            self.assert_code('summary_consent_required',lambda changes=changes:self.summary(state,consent={**CONSENT,**changes}))
        self.assert_code('not_found',lambda:self.service.publish_summary(self.other,state['id'],consent=CONSENT,
            expected_version=state['version'],reason='SYNTHETIC forged consent',key='foreign'))
        self.assertEqual(self.service.public_list(),[])

    def test_summary_cannot_bypass_response_review_on_scope_upgrade(self):
        state=self.summary(self.create())
        state=self.service.action(self.author,state['id'],'request_review',expected_version=state['version'],
            reason='SYNTHETIC response request',key='review-request',consent={**CONSENT,'scope':'responses'})
        self.assertEqual(self.service.public_list()[0]['scope'],'summary')
        self.assert_code('invalid_transition',lambda:self.summary(state,key='bypass'))
        self.assert_code('responses_private',lambda:self.service.public_result(state['id']))
        for name,actor in [('start_review',self.reviewer),('approve',self.reviewer),('publish',self.admin)]:
            extras={'rights_evidence':'SYNTHETIC independent response permission'} if name=='approve' else {}
            state=self.service.action(actor,state['id'],name,expected_version=state['version'],
                reason='SYNTHETIC reviewed scope upgrade',key='upgrade-'+name,**extras)
        self.assertEqual(state['publication']['scope'],'responses')
        self.assertEqual(self.service.public_result(state['id']),self.fixture.document)

    def test_summary_replay_and_withdrawal_preserve_private_history(self):
        draft=self.create();published=self.summary(draft)
        self.assertEqual(self.summary(draft),published)
        withdrawn=self.service.action(self.author,published['id'],'withdraw',expected_version=published['version'],
            reason='SYNTHETIC withdrawal',key='withdraw')
        self.assertEqual(self.service.public_page()['items'],[])
        self.assertEqual(self.service.public_leaderboard()['publication_count'],0)
        self.assert_code('not_found',lambda:self.service.public_summary(published['id']))
        self.assert_code('withdrawn',lambda:self.summary(withdrawn,key='republish'))
        self.assertEqual(self.service.result(self.author,published['id']),self.fixture.document)
        self.assertEqual(self.service.history(self.author,published['id'])['state'],withdrawn)

    def test_metadata_bounds_and_idempotency_conflict(self):
        for name,description in [('', ''),('a'*201,''),('name','x'*2001),(42,'')]:
            self.assert_code('invalid_display_name' if name=='' or not isinstance(name,str) or len(name)>200 else 'invalid_description',
                lambda name=name,description=description:self.create(display_name=name,description=description))
        first=self.create(display_name='first')
        self.assertEqual(self.create(display_name='first'),first)
        self.assert_code('idempotency_conflict',lambda:self.create(display_name='second'))


class PublicRegistrationHTTPTests(unittest.TestCase):
    setUp=web_fixture.SubmissionHTTPTests.setUp
    setUpFixture=web_fixture.SubmissionHTTPTests.setUpFixture
    write=web_fixture.SubmissionHTTPTests.write
    sha=web_fixture.SubmissionHTTPTests.sha
    upload=web_fixture.SubmissionHTTPTests.upload
    login=web_fixture.SubmissionHTTPTests.login
    headers=web_fixture.SubmissionHTTPTests.headers

    def test_http_metadata_and_summary_are_owned_and_never_accept_roles(self):
        self.submissions.allow_self_reported_summaries=True  # Operator fixture, not an HTTP setting.
        self.login(self.author,'SYNTHETIC-author');entry=self.upload()
        response=self.author.post('/api/submissions',headers=self.headers(self.author),json={
            'upload_id':entry['id'],'key':'named-create','display_name':'한국어 시험 모델','description':'SYNTHETIC'})
        self.assertEqual(response.status_code,201,response.text);state=response.json()
        self.assertTrue(self.author.get('/api/registration').json()['self_reported_summaries_enabled'])
        url='/api/submissions/'+state['id']+'/metadata'
        body={'display_name':'수정된 이름','expected_version':state['version'],'key':'metadata'}
        forged=self.author.post(url,headers=self.headers(self.author,analysis=False),json={**body,'owner':'SYNTHETIC-admin'})
        self.assertEqual(forged.status_code,400)
        changed=self.author.post(url,headers=self.headers(self.author,analysis=False),json=body)
        self.assertEqual(changed.status_code,200,changed.text);state=changed.json()
        self.login(self.other,'SYNTHETIC-other')
        self.assertEqual(self.other.post(url,headers=self.headers(self.other,analysis=False),json={**body,'key':'forged'}).status_code,404)
        response=self.author.post('/api/submissions/'+state['id']+'/actions',headers=self.headers(self.author,analysis=False),
            json={'name':'publish_summary','key':'summary','reason':'SYNTHETIC consent','expected_version':state['version'],'consent':CONSENT})
        self.assertEqual(response.status_code,200,response.text)
        listing=self.other.get('/api/public/submissions').json()
        self.assertEqual(listing['items'][0]['display']['display_name'],'수정된 이름')
        self.assertEqual(self.other.get('/api/public/submissions/'+state['id']+'/result').status_code,403)
        self.assertEqual(self.other.get('/api/submissions/'+state['id']+'/result').status_code,404)
        summary=self.other.get('/api/public/submissions/'+state['id']).json()
        self.assertFalse(summary['official_rank_eligible'])
        self.assertEqual(summary['scope'],'summary')
