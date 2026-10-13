from copy import deepcopy
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_submissions as fixture
from koevd_eval.eligibility import RankPolicy
from koevd_eval.recovery import (checkpoint, compare, inspect_recovery, reconcile,
                                validate_checkpoint, mark_restore)
from koevd_eval.results import canonical_hash
from koevd_eval.snapshots import create_snapshot, restore_snapshot, file_digest
from koevd_eval.storage import LocalSubmissionStore, StorageError, encode
from koevd_eval.submissions import SubmissionService


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.f=fixture.SubmissionTests(); self.f.setUp(); self.addCleanup(self.f.doCleanups)
        self.root=self.f.fixture.root/'recovery'; self.root.mkdir()
        self.indexes={'fixture':self.f.index}

    def cut(self,store=None,policy=None):
        with (store or self.f.store).connection() as db:return checkpoint(db,self.indexes,policy=policy)

    def restore(self,service=None,name='restored'):
        source=service or self.f.service
        archive=self.root/(name+'.zip')
        saved=create_snapshot(source.store,self.indexes,archive)
        restore_snapshot(archive,saved['sha256'],self.root/name,self.indexes)
        return SubmissionService(LocalSubmissionStore(self.root/name/'store'),self.indexes,
                                 reviewers=['reviewer'],admins=['admin'])

    def release(self,service,cut=None,**kwargs):
        expected=cut or self.cut()
        return reconcile(service.store,expected,expected['content_sha256'],self.indexes,
                         actor=kwargs.pop('actor','admin'),administrators=['admin'],
                         statement=kwargs.pop('statement','SYNTHETIC external checkpoint comparison; no actual operator approval'),**kwargs)

    def code(self,code,function):
        with self.assertRaises(StorageError) as error:function()
        self.assertEqual(error.exception.code,code)

    def test_stale_published_restore_cannot_leak_or_mutate_and_reports_later_withdrawal(self):
        published=self.f.publish('responses'); old=self.cut(); restored=self.restore()
        withdrawn=self.f.action(published,'withdraw'); latest=self.cut()
        for method in (restored.public_list,restored.public_page,restored.public_leaderboard,
                       lambda:restored.public_result(published['id']),lambda:restored.public_summary(published['id'])):
            self.code('recovery_required',method)
        self.code('recovery_required',lambda:restored.create(self.f.author,self.f.document,'fixture',key='request-1'))
        self.code('recovery_required',lambda:restored.action(self.f.author,published['id'],'withdraw',
            expected_version=published['version'],reason='SYNTHETIC',key='blocked-withdraw'))
        self.assertEqual(restored.result(self.f.author,published['id']),self.f.document)
        report=compare(self.cut(restored.store),latest)
        self.assertFalse(report['matches']); self.assertEqual(report['changed_submissions'],[published['id']])
        self.assertIn('events',report['changed_tables']); self.assertIn('requests',report['changed_tables'])
        self.code('recovery_mismatch',lambda:self.release(restored,latest))
        with restored.store.connection() as db:self.assertIsNone(inspect_recovery(db)['release'])
        self.assertEqual(restored.get(self.f.author,published['id']),published)
        self.assertEqual(withdrawn['workflow'],'withdrawn')
        # The old checkpoint would match, hence its latest-state provenance must
        # be independently selected by the real operator, not this algorithm.
        self.assertTrue(compare(self.cut(restored.store),old)['matches'])

    def test_current_withdrawn_restore_reconciles_without_inventing_latest_authentication(self):
        published=self.f.publish(); withdrawn=self.f.action(published,'withdraw'); cut=self.cut()
        restored=self.restore(); result=self.release(restored,cut)
        self.assertFalse(result['latest_state_authenticated']); self.assertEqual(result['actor'],'admin')
        self.assertEqual(restored.get(self.f.author,published['id']),withdrawn)
        self.assertEqual(restored.public_list(),[]); self.assertEqual(restored.public_page()['items'],[])
        self.code('not_found',lambda:restored.public_result(published['id']))
        replay=restored.create(self.f.author,self.f.document,'fixture',key='request-1')
        self.assertEqual(replay['version'],1); self.assertEqual(replay['workflow'],'draft')
        self.assertEqual(self.release(restored,cut),result)
        self.code('recovery_release_conflict',lambda:self.release(restored,cut,statement='SYNTHETIC changed statement'))

    def test_rebackup_reconciled_store_and_second_restore_require_new_reconciliation(self):
        self.f.create(); cut=self.cut(); first=self.restore(name='first'); self.release(first,cut)
        second=self.restore(first,name='second')
        with second.store.connection() as db:
            context=inspect_recovery(db)
            self.assertEqual(context['sequence'],2); self.assertIsNone(context['release'])
        self.code('recovery_required',second.public_list)
        self.assertTrue(compare(self.cut(second.store),cut)['matches'])
        self.release(second,cut); self.assertEqual(second.public_list(),[])

    def test_policy_context_changed_cannot_reuse_a_reconciliation(self):
        state=self.f.publish(); restored=self.restore()
        policy=RankPolicy(status='ratified',ratification_sha256='a'*64)  # SYNTHETIC policy only.
        cut=self.cut(policy=policy)
        self.code('recovery_mismatch',lambda:self.release(restored,cut))
        self.release(restored,cut,policy=policy)
        self.code('recovery_policy_changed',restored.public_list)
        restored.rank_policy=policy
        self.assertEqual(restored.public_list()[0]['submission_id'],state['id'])
        # Unresolved classifier exclusions still reside in the shared admission engine.
        self.assertNotIn('task3_unsafe_rate',str(restored.public_leaderboard()['boards']))

    def test_admin_and_checkpoint_digest_and_bounds_are_required(self):
        self.f.create(); restored=self.restore(); cut=self.cut()
        self.code('admin_required',lambda:self.release(restored,cut,actor='author'))
        with self.assertRaises(ValueError):self.release(restored,cut,statement='')
        with self.assertRaisesRegex(ValueError,'selected digest'):
            reconcile(restored.store,cut,'0'*64,self.indexes,actor='admin',administrators=['admin'],statement='SYNTHETIC')
        changed=deepcopy(cut); changed['submissions'].clear()
        with self.assertRaisesRegex(ValueError,'content changed'):validate_checkpoint(changed)
        changed['content_sha256']=canonical_hash({k:v for k,v in changed.items() if k!='content_sha256'})
        with self.assertRaisesRegex(ValueError,'submission count'):validate_checkpoint(changed)
        with patch('koevd_eval.recovery.MAX_ROWS',1),self.assertRaisesRegex(ValueError,'row limit'):self.cut()
        with patch('koevd_eval.recovery.MAX_CHECKPOINT_BYTES',1),self.assertRaises(ValueError):validate_checkpoint(cut)

    def test_all_immutable_tables_affect_checkpoint_without_exporting_raw_results(self):
        self.f.create(); first=self.cut(); second=self.cut()
        self.assertTrue(compare(first,second)['matches'])
        raw=json.dumps(first)
        self.assertNotIn('response_text',raw); self.assertNotIn('rights_statement',raw)
        self.assertEqual(first['tables']['artifacts']['rows'],1)
        state=self.f.service.get(self.f.author,next(iter(first['submissions'])))
        self.f.action(state,'request_review',consent={'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC'})
        changed=self.cut(); report=compare(changed,first)
        self.assertFalse(report['matches']); self.assertIn('submissions',report['changed_tables'])
        self.assertIn('requests',report['changed_tables'])
        self.assertEqual(changed['tables']['artifacts'],first['tables']['artifacts'])

    def test_restore_metadata_tamper_or_unknown_key_fails_closed(self):
        self.f.create(); restored=self.restore(); self.release(restored)
        with restored.store.connection(write=True) as db:
            sql=db.execute("SELECT sql FROM sqlite_master WHERE name='meta_update'").fetchone()[0]
            db.execute('DROP TRIGGER meta_update')
            row=db.execute("SELECT value FROM meta WHERE key='recovery.guard.000001'").fetchone()
            value=json.loads(row[0]); value['snapshot_sha256']='f'*64
            db.execute("UPDATE meta SET value=? WHERE key='recovery.guard.000001'",(encode(value).decode('utf-8'),)); db.execute(sql)
        self.code('recovery_integrity',restored.public_list)
        other=self.restore(name='unknown')
        with other.store.connection(write=True) as db:db.execute('INSERT INTO meta VALUES(?,?)',('malicious_override','true'))
        self.code('recovery_integrity',other.public_list)
        with self.assertRaises(StorageError):create_snapshot(other.store,self.indexes,self.root/'unsafe.zip')

    def test_restore_history_limit_cannot_be_bypassed_by_old_release(self):
        self.f.create(); restored=self.restore()
        with patch('koevd_eval.recovery.MAX_RECOVERIES',1),self.assertRaisesRegex(ValueError,'history limit'):
            mark_restore(restored.store,'b'*64)
        self.code('recovery_required',restored.public_list)

    def test_cli_checkpoint_compare_reconcile_and_role_boundary(self):
        state=self.f.create(); restored=self.restore()
        index=self.root/'index.json'; index.write_bytes(encode(self.f.index))
        catalog=self.root/'catalog.json'; catalog.write_bytes(encode({'schema_version':'koevd-space-catalog-v1',
            'indexes':[{'id':'fixture','label':'Synthetic recovery fixture','mode':'synthetic_demo','path':'index.json','sha256':file_digest(index)}],'baselines':[]}))
        roles=self.root/'roles.json'; roles.write_bytes(encode({'admins':['admin'],'reviewers':[]}))
        common=[sys.executable,'-m','koevd_eval.recovery','--catalog',str(catalog),'--roles-file',str(roles),'--demo']
        source=common+['--actor','admin','--store-dir',str(self.f.store.root)]
        target=common+['--actor','admin','--store-dir',str(restored.store.root)]
        def run(args):return subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
        output=self.root/'outside-current.json'
        cp=run(source+['checkpoint','--output',str(output)]); self.assertEqual(cp.returncode,0,cp.stderr)
        digest=json.loads(cp.stdout)['result']['checkpoint_sha256']
        checked=run(target+['compare','--current-checkpoint',str(output),'--checkpoint-sha256',digest])
        self.assertEqual(checked.returncode,0,checked.stderr); self.assertTrue(json.loads(checked.stdout)['result']['matches'])
        denied=run(common+['--actor','author','--store-dir',str(restored.store.root),'status'])
        self.assertEqual(denied.returncode,2)
        released=run(target+['reconcile','--current-checkpoint',str(output),'--checkpoint-sha256',digest,'--statement','SYNTHETIC CPU outside checkpoint'])
        self.assertEqual(released.returncode,0,released.stderr)
        self.assertEqual(restored.public_list(),[])
        self.assertEqual(restored.get(self.f.author,state['id']),state)
        preserved=output.read_bytes(); self.assertEqual(run(source+['checkpoint','--output',str(output)]).returncode,2)
        self.assertEqual(output.read_bytes(),preserved)

    def test_http_quarantine_private_access_and_no_http_release_route(self):
        from test_submission_web import SubmissionHTTPTests
        from fastapi.testclient import TestClient
        from koevd_eval.spaces import create_app
        from koevd_eval.submission_web import RegistrationWeb
        f=SubmissionHTTPTests(); f.setUp(); self.addCleanup(f.doCleanups)
        published,_=f.publish('responses')
        indexes={'trusted-demo':f.index}; archive=f.root/'recovery.zip'
        saved=create_snapshot(f.submissions.store,indexes,archive)
        restore_snapshot(archive,saved['sha256'],f.root/'recovered',indexes)
        restored=SubmissionService(LocalSubmissionStore(f.root/'recovered/store'),indexes,
                                   reviewers=f.submissions.reviewers,admins=f.submissions.admins)
        app=create_app(f.service,origins=['http://127.0.0.1'],registration=RegistrationWeb(restored,f.ids))
        with TestClient(app,base_url='http://127.0.0.1',follow_redirects=False) as client:
            for path in ('/api/public/submissions','/api/public/leaderboard',
                         '/api/public/submissions/'+published['id'],'/api/public/submissions/'+published['id']+'/result'):
                response=client.get(path); self.assertEqual(response.status_code,503,response.text)
                self.assertEqual(response.json()['error']['code'],'recovery_required')
                self.assertNotIn('rights_statement',response.text)
            f.login(client,'SYNTHETIC-author')
            private=client.get('/api/submissions/'+published['id']+'/result')
            self.assertEqual(private.status_code,200,private.text)
            self.assertEqual(f.action(client,published,'withdraw').status_code,503)
            self.assertEqual(client.post('/api/recovery/reconcile',json={'admin':True}).status_code,404)


if __name__=='__main__':unittest.main()
