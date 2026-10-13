from copy import deepcopy
from datetime import datetime,timezone,timedelta
import json
import io
from contextlib import redirect_stdout
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_submissions as fixture
from test_snapshots import FakeBucket
from koevd_eval.backups import BackupManager,derive_checkpoint,atomic_json,await_final_snapshot_release
from koevd_eval.recovery import checkpoint,compare
from koevd_eval.snapshots import HFBucketSnapshots,create_snapshot,restore_snapshot,file_digest
from koevd_eval.storage import LocalSubmissionStore,StorageError,encode
from koevd_eval.submissions import SubmissionService


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.f=fixture.SubmissionTests();self.f.setUp();self.addCleanup(self.f.doCleanups)
        self.root=self.f.fixture.root/'backups'
        self.indexes={'fixture':self.f.index}
        self.clock=[datetime(2026,10,8,12,tzinfo=timezone.utc)]
        self.manager=BackupManager(self.f.store,self.indexes,self.root,actor='admin',clock=lambda:self.clock[0])

    def cut(self):
        with self.f.store.connection() as db:return checkpoint(db,self.indexes)

    def test_unknown_status_then_same_cut_pair_and_later_withdrawal_delta(self):
        empty=self.manager.status()
        self.assertIsNone(empty['changes_pending']);self.assertIsNone(empty['events_since_verified_backup'])
        self.assertIsNone(empty['rpo_guaranteed_seconds']);self.assertFalse(empty['remote_readback_verified'])
        state=self.f.publish();result=self.manager.cycle();self.assertTrue(result['success'])
        status=self.manager.status();self.assertFalse(status['changes_pending']);self.assertEqual(status['events_since_verified_backup'],0)
        self.assertFalse(status['remote_readback_verified']);self.assertIsNone(status['rpo_guaranteed_seconds'])
        self.clock[0]+=timedelta(seconds=7)
        withdrawn=self.f.action(state,'withdraw');status=self.manager.status()
        self.assertTrue(status['changes_pending']);self.assertEqual(status['events_since_verified_backup'],1)
        self.assertEqual(status['seconds_since_backup_started'],7)
        self.assertEqual(status['comparison']['changed_submissions'],[state['id']])
        self.assertEqual(withdrawn['workflow'],'withdrawn')

    def test_mutation_after_snapshot_cannot_be_mislabeled_as_covered(self):
        state=self.f.publish(); captured=[]
        def raced(*args,**kwargs):
            value=create_snapshot(*args,**kwargs)
            captured.append(self.f.action(state,'withdraw'))
            return value
        with patch('koevd_eval.backups.create_snapshot',side_effect=raced):result=self.manager.cycle()
        self.assertTrue(result['success']);self.assertEqual(captured[0]['workflow'],'withdrawn')
        path=self.manager.attempts()[0][1]
        cp=json.loads((path/'checkpoint.json').read_text(encoding='utf-8'))
        self.assertEqual(cp['submissions'][state['id']]['workflow'],'approved')
        status=self.manager.status();self.assertTrue(status['changes_pending']);self.assertEqual(status['events_since_verified_backup'],1)

    def test_failed_attempt_preserves_last_success_and_never_promotes_partial_pair(self):
        self.f.create();self.manager.cycle();first=self.manager.attempts()[0][1]
        original=(first/'COMPLETED.json').read_bytes()
        with patch('koevd_eval.backups.derive_checkpoint',side_effect=ValueError('SYNTHETIC secret URL')):
            failed=self.manager.cycle()
        self.assertFalse(failed['success']);self.assertEqual((first/'COMPLETED.json').read_bytes(),original)
        partial=self.manager.attempts()[1][1]
        self.assertTrue((partial/'snapshot.zip').exists());self.assertFalse((partial/'COMPLETED.json').exists())
        self.assertNotIn('secret',(partial/'FAILURE.json').read_text())
        status=self.manager.status();self.assertEqual(status['last_verified_sequence'],1);self.assertEqual(status['failed_attempts'],[2])

    def test_remote_scope_readback_failure_and_local_copy_not_remote_success(self):
        self.f.create();self.manager.cycle()
        fake=FakeBucket();transport=HFBucketSnapshots('private-org/fixture',api=fake)
        remote=BackupManager(self.f.store,self.indexes,self.root,actor='admin',transport=transport)
        self.assertIsNone(remote.status()['last_verified_sequence'])
        with patch.object(fake,'batch_bucket_files',side_effect=RuntimeError('SYNTHETIC secret')):
            failed=remote.cycle()
        self.assertFalse(failed['success']);self.assertIsNone(remote.status()['last_verified_sequence'])
        self.assertEqual(self.manager.status()['last_verified_sequence'],1)
        passed=remote.cycle();self.assertTrue(passed['success']);self.assertTrue(passed['remote_readback_verified'])
        status=remote.status();self.assertTrue(status['remote_readback_verified']);self.assertIsNone(status['rpo_guaranteed_seconds'])
        path=remote.attempts()[-1][1]
        downloaded=self.f.fixture.root/'downloaded.zip';transport.fetch(passed['snapshot_sha256'],downloaded)
        cp=derive_checkpoint(downloaded,passed['snapshot_sha256'],self.indexes)
        self.assertEqual(cp['content_sha256'],passed['checkpoint_sha256'])
        # Fake provider contract only, never a real HF acceptance result.
        self.assertEqual(self.manager.status()['last_verified_sequence'],1)

    def test_periodic_runner_waits_retries_and_excludes_failed_cycles(self):
        self.f.create();emitted=[];waits=[]
        real=self.manager._cycle;count=[0]
        def one_failure():
            count[0]+=1
            if count[0]==1:
                with patch('koevd_eval.backups.create_snapshot',side_effect=OSError('SYNTHETIC disk failure')):return real()
            return real()
        with patch.object(self.manager,'_cycle',side_effect=one_failure):
            result=self.manager.run(cycles=2,interval_seconds=2,wait=waits.append,emit=emitted.append)
        self.assertEqual(result['failures'],1);self.assertEqual(result['cycles'],2);self.assertEqual(waits,[1,1])
        self.assertEqual([v['success'] for v in emitted],[False,True])
        self.assertEqual(self.manager.status()['last_verified_sequence'],2);self.assertFalse((self.root/'.worker-lock').exists())

    def test_final_capture_follows_gate_and_preserves_last_committed_change(self):
        state=self.f.publish();gates=[]
        def gate():
            self.assertEqual(len(self.manager.attempts()),1)
            gates.append(self.f.action(state,'withdraw'))
        result=self.manager.run(cycles=2,interval_seconds=1,wait=lambda delay:None,before_final_cycle=gate)
        self.assertEqual(result['failures'],0);self.assertEqual(len(gates),1)
        self.assertFalse(self.manager.status()['changes_pending'])
        latest=self.manager.attempts()[-1][1]
        saved=json.loads((latest/'COMPLETED.json').read_text(encoding='utf-8'))
        target=self.f.fixture.root/'final-gated-restore'
        restore_snapshot(latest/'snapshot.zip',saved['snapshot_sha256'],target,self.indexes)
        restored=SubmissionService(LocalSubmissionStore(target/'store'),self.indexes)
        self.assertEqual(restored.history(self.f.author,state['id']),self.f.service.history(self.f.author,state['id']))

    def test_missing_final_gate_does_not_capture_or_promote_a_final_pair(self):
        self.f.create()
        def refused():raise ValueError('Shutdown was not confirmed')
        with self.assertRaisesRegex(ValueError,'Shutdown'):
            self.manager.run(cycles=2,interval_seconds=1,wait=lambda delay:None,before_final_cycle=refused)
        self.assertEqual(len(self.manager.attempts()),1)
        self.assertTrue((self.manager.attempts()[0][1]/'COMPLETED.json').is_file())
        self.assertFalse((self.root/'.worker-lock').exists())
        with self.assertRaises(ValueError):self.manager.run(cycles=0,before_final_cycle=lambda:None)

    def test_final_release_protocol_requires_exact_control_and_hides_untrusted_input(self):
        for value,accepted in [('FINAL_SNAPSHOT\n',True),('',False),('SYNTHETIC private text\n',False)]:
            output=io.StringIO()
            with patch('sys.stdin',io.StringIO(value)),redirect_stdout(output):
                if accepted:await_final_snapshot_release()
                else:
                    with self.assertRaisesRegex(ValueError,'shutdown is not confirmed'):await_final_snapshot_release()
            self.assertEqual(json.loads(output.getvalue()),{'execution_scope':'operator_private_backup','event':'awaiting_final_snapshot_release'})
            self.assertNotIn('private text',output.getvalue())

    def test_restart_lock_and_retained_quota_do_not_erase_good_copy(self):
        self.f.create();self.manager.cycle();restart=BackupManager(self.f.store,self.indexes,self.root,actor='admin')
        self.assertEqual(restart.status()['last_verified_sequence'],1)
        with self.manager.worker_lock(),self.assertRaises(FileExistsError):restart.cycle()
        restart.max_bytes=65536;failed=restart.cycle()
        self.assertFalse(failed['success']);self.assertEqual(failed['error_code'],'backup_capacity')
        self.assertEqual(restart.status()['last_verified_sequence'],1)
        self.assertTrue((restart.attempts()[0][1]/'snapshot.zip').is_file())

    def test_tamper_checkpoint_or_receipt_fails_closed_instead_of_old_success_fallback(self):
        self.f.create();self.manager.cycle();self.manager.cycle()
        latest=self.manager.attempts()[-1][1]
        original=(latest/'checkpoint.json').read_bytes();(latest/'checkpoint.json').write_bytes(b'{}')
        with self.assertRaisesRegex(ValueError,'bytes changed'):self.manager.status()
        (latest/'checkpoint.json').write_bytes(original)
        receipt=json.loads((latest/'COMPLETED.json').read_text(encoding='utf-8'));receipt['target']={'kind':'hf_private_bucket','bucket_id':'other/org'}
        (latest/'COMPLETED.json').write_bytes(encode(receipt))
        with self.assertRaisesRegex(ValueError,'target/sequence changed'):self.manager.status()

    def test_clock_regression_is_unknown_age_and_restore_remains_quarantined(self):
        self.f.create();result=self.manager.cycle();self.clock[0]-=timedelta(seconds=1)
        status=self.manager.status();self.assertFalse(status['clock_valid']);self.assertIsNone(status['seconds_since_backup_started'])
        path=self.manager.attempts()[0][1];target=self.f.fixture.root/'restore'
        restore_snapshot(path/'snapshot.zip',result['snapshot_sha256'],target,self.indexes)
        restored=SubmissionService(LocalSubmissionStore(target/'store'),self.indexes)
        with self.assertRaises(StorageError) as error:restored.public_list()
        self.assertEqual(error.exception.code,'recovery_required')
        self.assertIsNone(status['rpo_guaranteed_seconds'])

    def test_incomplete_attempt_and_invalid_setup_not_counted_as_success(self):
        self.f.create()
        with patch('koevd_eval.backups.atomic_json',side_effect=OSError('SYNTHETIC initial record failure')),self.assertRaises(OSError):self.manager.cycle()
        status=self.manager.status();self.assertIsNone(status['last_verified_sequence']);self.assertEqual(status['incomplete_attempts'],[1])
        with self.assertRaisesRegex(ValueError,'separate'):BackupManager(self.f.store,self.indexes,self.f.store.root/'bad',actor='admin')
        with self.assertRaises(ValueError):self.manager.run(cycles=-1)
        with self.assertRaises(ValueError):self.manager.run(interval_seconds=0)

    def test_cli_two_cycles_status_admin_and_remote_opt_in_boundaries(self):
        self.f.create();root=self.f.fixture.root/'cli';root.mkdir()
        index=root/'index.json';index.write_bytes(encode(self.f.index))
        catalog=root/'catalog.json';catalog.write_bytes(encode({'schema_version':'koevd-space-catalog-v1',
            'indexes':[{'id':'fixture','label':'Synthetic backup test','mode':'synthetic_demo','path':'index.json','sha256':file_digest(index)}],'baselines':[]}))
        roles=root/'roles.json';roles.write_bytes(encode({'reviewers':[],'admins':['admin']}))
        common=[sys.executable,'-m','koevd_eval.backups','--store-dir',str(self.f.store.root),'--backup-root',str(root/'copies'),
                '--catalog',str(catalog),'--roles-file',str(roles),'--demo']
        def run(args):return subprocess.run(args,capture_output=True,text=True,encoding='utf-8')
        denied=run(common+['--actor','author','run']);self.assertEqual(denied.returncode,2)
        passed=run(common+['--actor','admin','run','--cycles','2','--interval-seconds','1'])
        self.assertEqual(passed.returncode,0,passed.stderr);lines=[json.loads(v) for v in passed.stdout.splitlines()]
        self.assertEqual([v['cycle']['success'] for v in lines[:-1]],[True,True])
        status=run(common+['--actor','admin','status']);self.assertEqual(status.returncode,0,status.stderr)
        value=json.loads(status.stdout)['result'];self.assertEqual(value['last_verified_sequence'],2);self.assertFalse(value['remote_readback_verified'])
        denied=run(common+['--actor','admin','--bucket','private-org/fixture','run'])
        self.assertEqual(denied.returncode,2);self.assertNotIn('Traceback',denied.stderr)


if __name__=='__main__':unittest.main()
