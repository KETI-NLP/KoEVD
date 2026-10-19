from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_results as result_fixture
from koevd_eval.diagnostics import analyze
from koevd_eval.results import canonical_hash, _seal, unknown_measurement_provenance
from koevd_eval.storage import LocalSubmissionStore, StorageError
from koevd_eval.submissions import Principal, SubmissionService


def reseal(value):
    value=deepcopy(value);value.pop('content_sha256',None);return _seal(value)


class SubmissionTests(unittest.TestCase):
    def setUp(self):
        fixture=result_fixture.ResultContractTests()
        fixture.setUp();self.addCleanup(fixture.doCleanups)
        self.fixture=fixture;self.index=fixture.index;self.document=fixture.document
        self.root=fixture.root/'submissions'
        self.store=LocalSubmissionStore(self.root)
        self.author=Principal('author','operator_local')
        self.reviewer=Principal('reviewer','operator_local')
        self.admin=Principal('admin','operator_local')
        self.other=Principal('other','operator_local')
        self.service=SubmissionService(self.store,{'fixture':self.index},reviewers=['reviewer'],admins=['admin'])
        self.counter=0

    def key(self):
        self.counter+=1;return f'request-{self.counter}'

    def create(self):
        return self.service.create(self.author,self.document,'fixture',key=self.key())

    def action(self,state,name,actor=None,**kwargs):
        return self.service.action(actor or self.author,state['id'],name,expected_version=state['version'],reason='SYNTHETIC test operation',key=self.key(),**kwargs)

    def publish(self,scope='responses'):
        state=self.create()
        state=self.action(state,'request_review',consent={'scope':scope,'rights_statement':'SYNTHETIC fixture only; no external publication','accepted':True})
        state=self.action(state,'start_review',self.reviewer)
        state=self.action(state,'approve',self.reviewer,rights_evidence='SYNTHETIC rights-review fixture, not human safety gold')
        return self.action(state,'publish',self.admin)

    def revised(self):
        value=deepcopy(self.document)
        value['run']['measurements']['3']=unknown_measurement_provenance()
        for r in value['records']:
            if r['task']==3 and r['response']['status']=='ok':
                r['measurement'].update(value={'label':'unsafe'},status='reported')
        return reseal(value)

    def assert_code(self,code,func):
        with self.assertRaises(StorageError) as error:func()
        self.assertEqual(error.exception.code,code)

    def test_draft_is_private_separate_from_registration_and_original_is_immutable(self):
        state=self.create()
        self.assertEqual(state['workflow'],'draft');self.assertEqual(state['publication']['status'],'unpublished')
        self.assertEqual(self.service.result(self.author,state['id']),self.document)
        self.assertEqual(self.service.public_list(),[])
        self.assert_code('not_found',lambda:self.service.get(self.other,state['id']))
        self.assert_code('not_found',lambda:self.service.public_result(state['id']))
        self.assertEqual(self.service.get(self.reviewer,state['id']),state)
        for table in ('artifacts','revisions','events','requests'):
            with self.subTest(table=table):
                with self.store.connection(write=True) as db:
                    with self.assertRaisesRegex(sqlite3.IntegrityError,'immutable'):
                        db.execute(f'DELETE FROM {table}')

    def test_upload_cannot_assert_roles_identity_or_untrusted_gold(self):
        for actor in (None,'author',{'subject':'admin'},Principal('admin','from_upload')):
            with self.subTest(actor=actor):
                self.assert_code('identity_required',lambda:self.service.create(actor,self.document,'fixture',key=self.key()))
        invalid=deepcopy(self.document);invalid['publication']['status']='published'
        with self.assertRaises(ValueError):self.service.create(self.author,reseal(invalid),'fixture',key=self.key())
        bad=deepcopy(self.document);bad['records'][0]['gold']={'label':'safe'}
        with self.assertRaises(ValueError):self.service.create(self.author,reseal(bad),'fixture',key=self.key())
        self.assert_code('unknown_operator_index',lambda:self.service.create(self.author,self.document,'uploaded-index',key=self.key()))

    def test_review_requires_opt_in_independent_reviewer_and_admin_publication(self):
        state=self.create()
        self.assert_code('consent_required',lambda:self.action(state,'request_review',consent={'accepted':False,'scope':'responses','rights_statement':'test'}))
        self.assert_code('invalid_transition',lambda:self.action(state,'approve',self.reviewer,rights_evidence='test'))
        state=self.action(state,'request_review',consent={'scope':'responses','rights_statement':'SYNTHETIC consent','accepted':True})
        self.assert_code('independent_reviewer_required',lambda:self.action(state,'start_review',self.author))
        state=self.action(state,'start_review',self.reviewer)
        self.assert_code('invalid_text',lambda:self.action(state,'approve',self.reviewer))
        state=self.action(state,'approve',self.reviewer,rights_evidence='SYNTHETIC reviewed permission')
        self.assertEqual(self.service.public_list(),[])
        self.assert_code('independent_reviewer_required',lambda:self.action(state,'publish',self.reviewer))
        state=self.action(state,'publish',self.admin)
        self.assertEqual(state['workflow'],'approved')
        self.assertEqual(self.service.public_result(state['id']),self.document)
        self.assert_code('already_published',lambda:self.action(state,'publish',self.admin))
        summary=self.service.public_summary(state['id'])
        self.assertFalse(summary['official_rank_eligible'])
        self.assertEqual(summary['verification']['generation'],'user_reported')
        self.assertEqual(summary['verification']['measurement'],'measurement_limited')
        self.assertEqual(summary['protocol_sha256'],canonical_hash(self.index['protocol']))
        self.assertEqual(summary['tasks'],analyze(self.document,self.index,resamples=0)['tasks'])

    def test_summary_only_consent_excludes_original_responses_and_private_review_notes(self):
        state=self.publish('summary')
        self.assert_code('responses_private',lambda:self.service.public_result(state['id']))
        summary=self.service.public_summary(state['id'])
        self.assertNotIn('cases',summary)
        raw=json.dumps(summary)
        for text in ('fixture response','SYNTHETIC rights-review','rights_statement','rights_evidence','actor'):
            self.assertNotIn(text,raw)
        self.assertEqual(summary['statistics']['resamples'],0)
        self.assertEqual(summary['publication_environment'],'local_candidate')

    def test_idempotent_replay_duplicate_original_and_stale_key_conflicts(self):
        key=self.key();state=self.service.create(self.author,self.document,'fixture',key=key)
        self.assertEqual(self.service.create(self.author,self.document,'fixture',key=key),state)
        self.assert_code('duplicate_submission',lambda:self.create())
        self.assert_code('idempotency_conflict',lambda:self.service.create(self.author,self.revised(),'fixture',key=key))
        consent={'scope':'summary','rights_statement':'SYNTHETIC consent','accepted':True}
        request_key=self.key()
        pending=self.service.action(self.author,state['id'],'request_review',expected_version=1,reason='test',consent=consent,key=request_key)
        self.assertEqual(self.service.action(self.author,state['id'],'request_review',expected_version=1,reason='test',consent=consent,key=request_key),pending)
        self.assert_code('stale_version',lambda:self.service.action(self.reviewer,state['id'],'start_review',expected_version=1,reason='test',key=self.key()))
        self.assertEqual(len(self.service.history(self.author,state['id'])['events']),2)

    def test_remeasurement_revision_preserves_original_and_prior_public_projection(self):
        published=self.publish()
        revised=self.service.revise(self.author,published['id'],self.revised(),expected_version=published['version'],kind='measurement_recheck',reason='SYNTHETIC remeasurement',key=self.key())
        self.assertEqual(revised['workflow'],'draft');self.assertIsNone(revised['consent'])
        self.assertEqual(revised['publication']['revision'],1)
        self.assertEqual(self.service.public_result(revised['id']),self.document)
        self.assertEqual(self.service.result(self.author,revised['id'],revision=1),self.document)
        self.assertEqual(self.service.result(self.author,revised['id'],revision=2),self.revised())
        history=self.service.history(self.author,revised['id'])
        self.assertEqual(history['revisions'][1]['parent'],1)
        for n,event in enumerate(history['events'],1):
            self.assertEqual(event['sequence'],n)
            if n>1:self.assertEqual(event['previous_sha256'],history['events'][n-2]['content_sha256'])
        for bad in (0,False,-1):
            self.assert_code('invalid_revision',lambda:self.service.result(self.author,revised['id'],revision=bad))

    def test_remeasurement_cannot_change_generation_or_target_identity(self):
        state=self.create()
        for field in ('response','generation','model'):
            value=self.revised()
            if field=='generation':value['run']['generation']['max_tokens']=64
            elif field=='model':value['run']['model']['id']='different-model'
            else:
                r=next(r for r in value['records'] if r['task']==1)
                r['response'].update(text='unsafe',sha256=canonical_hash('unsafe'))
            code='different_target' if field=='model' else 'generation_changed'
            with self.subTest(field=field):
                self.assert_code(code,lambda:self.service.revise(self.author,state['id'],reseal(value),expected_version=1,kind='measurement_recheck',reason='test',key=self.key()))
        self.assertEqual(self.service.get(self.author,state['id']),state)

    def test_withdrawal_removes_public_projection_but_retains_private_history_after_restart(self):
        state=self.publish()
        withdrawn=self.action(state,'withdraw')
        restarted=SubmissionService(LocalSubmissionStore(self.root),{'fixture':self.index},reviewers=['reviewer'],admins=['admin'])
        self.assertEqual(restarted.public_list(),[])
        for method in (restarted.public_result,restarted.public_summary):
            self.assert_code('not_found',lambda:method(state['id']))
        self.assertEqual(restarted.result(self.author,state['id']),self.document)
        self.assertEqual(restarted.history(self.author,state['id'])['events'][-1]['action'],'withdraw')
        self.assert_code('withdrawn',lambda:self.action(withdrawn,'request_review',consent={'scope':'summary','rights_statement':'test','accepted':True}))

    def test_withdrawal_during_cpu_summary_prevents_stale_result_without_holding_read_lock(self):
        state=self.publish()
        original=analyze
        def during(document,index,**kwargs):
            self.action(state,'withdraw')
            return original(document,index,**kwargs)
        with patch('koevd_eval.submissions.analyze',side_effect=during):
            self.assert_code('not_found',lambda:self.service.public_summary(state['id']))

    def test_atomic_rollback_keeps_no_orphan_artifact_revision_or_request(self):
        state=self.create()
        with patch.object(self.store,'event',side_effect=RuntimeError('SYNTHETIC commit failure')):
            with self.assertRaises(RuntimeError):
                self.service.revise(self.author,state['id'],self.revised(),expected_version=1,kind='measurement_recheck',reason='test',key='failed-request')
        self.assertEqual(self.service.get(self.author,state['id']),state)
        with self.store.connection() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM artifacts').fetchone()[0],1)
            self.assertEqual(db.execute('SELECT count(*) FROM revisions').fetchone()[0],1)
            self.assertIsNone(db.execute("SELECT key FROM requests WHERE key='failed-request'").fetchone())

    def test_concurrent_same_key_is_one_transaction_and_optimistic_updates_conflict(self):
        with ThreadPoolExecutor(max_workers=6) as pool:
            values=list(pool.map(lambda _:self.service.create(self.author,self.document,'fixture',key='same-request'),range(6)))
        self.assertTrue(all(state==values[0] for state in values))
        state=values[0]
        def request(n):
            try:return self.service.action(self.author,state['id'],'request_review',expected_version=1,reason='test',key=f'concurrent-{n}',consent={'scope':'summary','rights_statement':'test','accepted':True})
            except StorageError as error:return error.code
        with ThreadPoolExecutor(max_workers=4) as pool:values=list(pool.map(request,range(4)))
        self.assertEqual(sum(isinstance(v,dict) for v in values),1)
        self.assertEqual(values.count('stale_version'),3)

    def test_operator_index_cannot_change_on_restart_or_disappear(self):
        state=self.create();changed=deepcopy(self.index)
        changed['protocol']['metadata_view']='changed'
        changed=reseal(changed)
        self.assert_code('changed_operator_index',lambda:SubmissionService(self.store,{'fixture':changed}))
        self.assert_code('missing_operator_index',lambda:SubmissionService(self.store,{'other':self.index}))
        self.assertEqual(self.service.get(self.author,state['id']),state)

    def test_consistent_backup_restores_withdrawal_and_never_overwrites(self):
        state=self.action(self.publish(),'withdraw')
        restored_root=self.fixture.root/'restore';restored_root.mkdir()
        destination=restored_root/'submissions.sqlite3'
        receipt=self.store.backup(destination)
        self.assertGreater(receipt['bytes'],0)
        restored=SubmissionService(LocalSubmissionStore(restored_root),{'fixture':self.index})
        self.assertEqual(restored.get(self.author,state['id']),state)
        self.assertEqual(restored.public_list(),[])
        self.assert_code('backup_exists',lambda:self.store.backup(destination))
        self.assert_code('backup_location',lambda:self.store.backup(self.root/'backup.sqlite3'))

    def test_capacity_failure_is_atomic_and_mutable_projection_tamper_is_detected(self):
        small=LocalSubmissionStore(self.fixture.root/'small',capacity_bytes=65536)
        service=SubmissionService(small,{'fixture':self.index})
        value=deepcopy(self.document)
        for r in value['records']:
            if r['task']==1:r['response'].update(text='x'*100000,sha256=canonical_hash('x'*100000))
        self.assert_code('store_capacity',lambda:service.create(self.author,reseal(value),'fixture',key='too-big'))
        with small.connection() as db:self.assertEqual(db.execute('SELECT count(*) FROM artifacts').fetchone()[0],0)
        state=self.create()
        with self.store.connection(write=True) as db:
            bad=deepcopy(state);bad['workflow']='approved'
            db.execute('UPDATE submissions SET state=? WHERE id=?',(json.dumps(bad),state['id']))
        self.assert_code('store_integrity',lambda:self.service.get(self.author,state['id']))

    def test_abrupt_process_death_rolls_back_uncommitted_artifact(self):
        script="""import sys
from koevd_eval.storage import LocalSubmissionStore
store=LocalSubmissionStore(sys.argv[1])
with store.connection(write=True) as db:
 db.execute('INSERT INTO artifacts VALUES(?,?,?)',('d'*64,'e'*64,b'SYNTHETIC UNCOMMITTED'))
 print('READY',flush=True)
 sys.stdin.read(1)
"""
        process=subprocess.Popen([sys.executable,'-X','utf8','-c',script,str(self.root)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        self.addCleanup(lambda:process.kill() if process.poll() is None else None)
        self.assertEqual(process.stdout.readline().strip(),'READY')
        self.assertIsNone(process.poll());process.kill();process.communicate(timeout=10)
        recovered=LocalSubmissionStore(self.root)
        with recovered.connection() as db:
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertIsNone(db.execute('SELECT digest FROM artifacts WHERE digest=?',('d'*64,)).fetchone())

    def test_separate_process_writers_share_atomic_store_without_duplicate_artifacts(self):
        paths=[]
        for name,value in (('index',self.index),('result',self.document)):
            path=self.fixture.root/(name+'.json');path.write_text(json.dumps(value),encoding='utf-8');paths.append(path)
        script="""import json,sys
from koevd_eval.storage import LocalSubmissionStore
from koevd_eval.submissions import Principal,SubmissionService
service=SubmissionService(LocalSubmissionStore(sys.argv[1]),{'fixture':json.load(open(sys.argv[2],encoding='utf-8'))})
state=service.create(Principal(sys.argv[4],'operator_local'),json.load(open(sys.argv[3],encoding='utf-8')),'fixture',key='process-create')
print(state['id'])
"""
        processes=[]
        for n in range(4):
            p=subprocess.Popen([sys.executable,'-X','utf8','-c',script,str(self.root),*[str(p) for p in paths],f'process-author-{n}'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            processes.append(p)
            self.addCleanup(lambda p=p:p.kill() if p.poll() is None else None)
        ids=[]
        for p in processes:
            stdout,stderr=p.communicate(timeout=20)
            self.assertEqual(p.returncode,0,stderr);ids.append(stdout.strip())
        self.assertEqual(len(set(ids)),4)
        with self.store.connection() as db:
            for table,count in (('artifacts',1),('submissions',4),('revisions',4),('events',4),('requests',4)):
                self.assertEqual(db.execute(f'SELECT count(*) FROM {table}').fetchone()[0],count)

    def test_published_revision_changes_only_after_new_consent_review_and_publication(self):
        state=self.publish('summary')
        state=self.service.revise(self.author,state['id'],self.revised(),expected_version=state['version'],kind='measurement_recheck',reason='test',key=self.key())
        state=self.action(state,'request_review',consent={'scope':'responses','rights_statement':'new SYNTHETIC consent','accepted':True})
        self.assertEqual(self.service.public_list()[0]['revision'],1)
        state=self.action(state,'start_review',self.reviewer)
        state=self.action(state,'reject',self.reviewer)
        self.assertEqual(self.service.public_list()[0]['scope'],'summary')
        state=self.action(state,'request_review',consent={'scope':'responses','rights_statement':'revised SYNTHETIC consent','accepted':True})
        state=self.action(state,'start_review',self.reviewer)
        state=self.action(state,'approve',self.reviewer,rights_evidence='new SYNTHETIC reviewed rights')
        state=self.action(state,'publish',self.admin)
        self.assertEqual(self.service.public_list()[0]['revision'],2)
        self.assertEqual(self.service.public_result(state['id']),self.revised())
        self.assertEqual(self.service.result(self.author,state['id'],revision=1),self.document)

    def test_administrator_cannot_approve_own_submission_or_change_other_owners_revision(self):
        state=self.service.create(self.admin,self.document,'fixture',key=self.key())
        state=self.action(state,'request_review',self.admin,consent={'scope':'summary','rights_statement':'SYNTHETIC','accepted':True})
        self.assert_code('independent_reviewer_required',lambda:self.action(state,'start_review',self.admin))
        self.assert_code('owner_required',lambda:self.service.revise(self.reviewer,state['id'],self.revised(),expected_version=state['version'],kind='measurement_recheck',reason='test',key=self.key()))

    def test_stored_artifact_byte_tamper_is_detected_even_when_projection_is_unchanged(self):
        state=self.create()
        with self.store.connection(write=True) as db:
            db.execute('DROP TRIGGER artifacts_update')  # Simulated out-of-band operator disk change.
            db.execute('UPDATE artifacts SET data=?',(b'CHANGED STORED BYTES',))
        self.assert_code('store_integrity',lambda:self.service.result(self.author,state['id']))
        self.assert_code('store_integrity',lambda:LocalSubmissionStore(self.root))

    def test_operator_cli_preserves_original_output_and_labels_identity_as_local_assertion(self):
        from koevd_eval.submissions import main
        index=self.fixture.root/'cli-index.json';index.write_text(json.dumps(self.index),encoding='utf-8')
        roles=self.fixture.root/'cli-roles.json';roles.write_text(json.dumps({'reviewers':['reviewer'],'admins':['admin']}),encoding='utf-8')
        result=self.fixture.root/'cli-result.json';result.write_text(json.dumps(self.document),encoding='utf-8')
        base=['koevd-submissions','--store-dir',str(self.root),'--trusted-index',str(index),'--index-id','fixture','--roles-file',str(roles)]
        def invoke(arguments):
            output=StringIO()
            with patch('sys.argv',base+arguments),patch('sys.stdout',output):main()
            return json.loads(output.getvalue())
        response=invoke(['--actor','author','create','--input',str(result),'--key','cli-create'])
        self.assertEqual(response['execution_scope'],'operator_local_candidate');sid=response['result']['id']
        output=self.fixture.root/'cli-export.json'
        invoke(['--actor','author','result','--id',sid,'--output',str(output)])
        self.assertEqual(json.loads(output.read_text(encoding='utf-8')),self.document)
        with patch('sys.argv',base+['--actor','author','result','--id',sid,'--output',str(output)]),patch('sys.stderr',StringIO()):
            with self.assertRaises(SystemExit) as error:main()
            self.assertEqual(error.exception.code,2)
        with patch('sys.argv',base+['create','--input',str(result),'--key','no-actor']),patch('sys.stderr',StringIO()):
            with self.assertRaises(SystemExit) as error:main()
            self.assertEqual(error.exception.code,2)



    def test_private_correction_requires_fresh_summary_publication_and_updates_warm_comparison(self):
        self.service.allow_self_reported_summaries=True
        def share(state,accepted=True):
            return self.service.publish_summary(self.author,state['id'],
                consent={'scope':'summary','accepted':accepted,'rights_statement':'SYNTHETIC fresh permission'},
                reason='SYNTHETIC explicit share',expected_version=state['version'],key=self.key())
        original=share(self.create())
        other=deepcopy(self.document);other['run']['model']['id']='SYNTHETIC-reference'
        reference=share(self.service.create(self.author,reseal(other),'fixture',key=self.key()))
        self.assertEqual(self.service.public_comparison(original['id'],reference['id'])['left']['revision'],1)
        draft=self.service.revise(self.author,original['id'],self.revised(),expected_version=original['version'],
            kind='measurement_recheck',reason='SYNTHETIC correction',key=self.key())
        self.assertEqual(draft['head_revision'],2)
        self.assertEqual(self.service.public_profile(draft['id'])['revision'],1)
        self.assertEqual(self.service.public_comparison(draft['id'],reference['id'])['left']['revision'],1)
        self.assert_code('summary_consent_required',lambda:share(draft,False))
        shared=share(draft)
        self.assertEqual(shared['publication']['revision'],2)
        self.assertEqual(self.service.public_profile(shared['id'])['revision'],2)
        self.assertEqual(self.service.public_comparison(shared['id'],reference['id'])['left']['revision'],2)
        self.assertEqual(self.service.result(self.author,shared['id'],revision=1),self.document)


if __name__=='__main__':unittest.main()
