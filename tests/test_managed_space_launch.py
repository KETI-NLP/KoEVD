"""Candidate startup guards and real owned-child cleanup, not live HF acceptance."""
import importlib.util
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import os
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location('managed_space_candidate', Path(__file__).resolve().parents[1] / 'apps/spaces/managed_launch.py')
managed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(managed)


class ManagedSpaceTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / 'registry').mkdir()
        (self.root / 'catalog.json').write_text('{}', encoding='utf-8')
        (self.root / 'web.json').write_text('{"reviewers":[],"admins":[]}', encoding='utf-8')
        (self.root / 'backup.json').write_text('{"reviewers":[],"admins":["validation-backup-actor"]}', encoding='utf-8')
        self.config = {'format': 'koevd-managed-space-v2', 'catalog': 'catalog.json',
                       'protocol_registry': 'registry', 'web_roles': 'web.json', 'backup_roles': 'backup.json',
                       'backup_actor': 'validation-backup-actor', 'bucket': 'KETI-NLP/KoEVD-Platform-Backups-Dev',
                       'store_root': 'new-store', 'backup_root': 'backups', 'mode': 'initialize',
                       'initialization_baseline_snapshot_sha256': [],
                       'restore_root': None, 'snapshot_sha256': None, 'interval_seconds': 300,
                       'cycles': 2, 'retained_quota_bytes': 1073741824}
        self.env = {'SPACE_HOST': 'keti-nlp-koevd-platform-dev.hf.space'}
        self.path = self.root / 'managed.json'

    def plan(self):
        self.path.write_text(json.dumps(self.config), encoding='utf-8')
        return managed.plan(self.path, self.env)

    def test_missing_existing_store_and_reinitialization_fail_before_any_server(self):
        p = self.plan()
        self.assertIn('--enable-remote-backup', p['worker_argv'])
        self.assertEqual(p['origin'], 'https://keti-nlp-koevd-platform-dev.hf.space')
        self.config['mode'] = 'existing'
        with self.assertRaises(ValueError):
            self.plan()
        self.config['mode'] = 'initialize'
        (self.root / 'new-store').mkdir()
        with self.assertRaises(ValueError):
            self.plan()

    def test_restore_requires_independent_digest_fresh_exact_root_and_separate_backup(self):
        self.config.update(mode='restore', initialization_baseline_snapshot_sha256=None,
                           restore_root='fresh-restore', store_root='fresh-restore/store', snapshot_sha256='a' * 64)
        self.assertEqual(self.plan()['restore'], self.root / 'fresh-restore')
        self.config['snapshot_sha256'] = 'invalid'
        with self.assertRaises(ValueError):
            self.plan()
        self.config['snapshot_sha256'] = 'a' * 64
        self.config['store_root'] = 'other-store'
        with self.assertRaises(ValueError):
            self.plan()
        self.config['store_root'] = 'fresh-restore/store'
        self.config['backup_root'] = 'fresh-restore/backups'
        with self.assertRaises(ValueError):
            self.plan()

    def test_web_role_does_not_authorize_backup_actor_and_ambient_cli_token_is_not_used(self):
        self.config['backup_actor'] = 'not-authorized'
        with self.assertRaises(ValueError):
            self.plan()
        with self.assertRaises(ValueError):
            managed.child_environments({'HF_TOKEN': 'SYNTHETIC-CLI-TOKEN'})

    def test_credentials_are_separated_and_absent_from_child_arguments(self):
        p = self.plan()
        env = {**os.environ, **self.env, 'KOEVD_BACKUP_TOKEN': 'SYNTHETIC-BUCKET-TOKEN',
               'HF_TOKEN': 'SYNTHETIC-BROAD-TOKEN', 'OAUTH_CLIENT_ID': 'SYNTHETIC-CLIENT',
               'OAUTH_CLIENT_SECRET': 'SYNTHETIC-OAUTH-SECRET', 'HF_ENDPOINT': 'https://untrusted.invalid',
               'KOEVD_POLICY_ROOT': '/unapproved', 'KOEVD_POLICY_HEAD_SHA256': 'b' * 64}
        server, worker = managed.child_environments(env)
        self.assertNotIn('HF_TOKEN', server)
        self.assertNotIn('KOEVD_BACKUP_TOKEN', server)
        self.assertNotIn('OAUTH_CLIENT_SECRET', worker)
        self.assertNotIn('OAUTH_CLIENT_ID', worker)
        self.assertEqual(worker['HF_TOKEN'], 'SYNTHETIC-BUCKET-TOKEN')
        self.assertEqual(worker['HF_ENDPOINT'], 'https://huggingface.co')
        self.assertNotIn('KOEVD_POLICY_ROOT', server)
        argv = ' '.join(p['server_argv'] + p['worker_argv'])
        self.assertNotIn('TOKEN', argv)
        self.assertNotIn('SECRET', argv)

    def test_initial_backup_failure_prevents_starting_children(self):
        self.plan()
        env = {**self.env, 'KOEVD_BACKUP_TOKEN': 'SYNTHETIC-BUCKET-TOKEN',
               'OAUTH_CLIENT_ID': 'SYNTHETIC-CLIENT', 'OAUTH_CLIENT_SECRET': 'SYNTHETIC-SECRET'}
        with patch.dict(os.environ, env, clear=True), patch.object(sys, 'argv', ['managed', '--config', str(self.path)]), \
                patch.object(managed, 'prepare_storage', side_effect=ValueError('SYNTHETIC provider failure')), \
                patch.object(managed, 'supervise') as children:
            self.assertEqual(managed.main(), 2)
            children.assert_not_called()

    def test_restore_notice_does_not_claim_a_running_backup_worker(self):
        server, worker = managed.child_environments({'KOEVD_BACKUP_TOKEN': 'SYNTHETIC-BUCKET-TOKEN'}, restoring=True)
        self.assertIn('periodic backup worker is not running', server['KOEVD_DEPLOYMENT_NOTICE'])
        self.assertIn('recovery quarantine', server['KOEVD_DEPLOYMENT_NOTICE'])
        self.assertNotIn('HF_TOKEN', server)

    def test_termination_handler_unwinds_prepare_and_restores_prior_handler(self):
        self.plan()
        env = {**self.env, 'KOEVD_BACKUP_TOKEN': 'SYNTHETIC-BUCKET-TOKEN',
               'OAUTH_CLIENT_ID': 'SYNTHETIC-CLIENT', 'OAUTH_CLIENT_SECRET': 'SYNTHETIC-SECRET'}
        previous = managed.signal.getsignal(managed.signal.SIGTERM)
        def interrupted(*args):
            self.assertIs(managed.signal.getsignal(managed.signal.SIGTERM), managed.termination_requested)
            managed.termination_requested(managed.signal.SIGTERM, None)
        with patch.dict(os.environ, env, clear=True), patch.object(sys, 'argv', ['managed', '--config', str(self.path)]), \
                patch.object(managed, 'prepare_storage', side_effect=interrupted), patch.object(managed, 'supervise') as children:
            self.assertEqual(managed.main(), 0)
            children.assert_not_called()
        self.assertIs(managed.signal.getsignal(managed.signal.SIGTERM), previous)

    def test_restore_interruption_reaps_real_owned_server(self):
        actual = subprocess.Popen
        children = []
        def start(*args, **kwargs):
            child = actual(*args, **kwargs)
            children.append(child)
            real_wait = child.wait
            calls = []
            def wait(*args, **kwargs):
                if not calls:
                    calls.append(True)
                    raise KeyboardInterrupt
                return real_wait(*args, **kwargs)
            child.wait = wait
            return child
        argv = [sys.executable, '-c', 'import time;time.sleep(60)']
        with patch.object(managed.subprocess, 'Popen', side_effect=start):
            self.assertEqual(managed.run_restored_server(argv, dict(os.environ)), 0)
        self.assertEqual(len(children), 1)
        self.assertIsNotNone(children[0].poll())

    def test_failed_worker_stops_real_owned_server_process(self):
        actual = subprocess.Popen
        children = []
        def start(*args, **kwargs):
            child = actual(*args, **kwargs)
            children.append(child)
            return child
        server = [sys.executable, '-c', 'import time;time.sleep(60)']
        worker = [sys.executable, '-c', 'import time;time.sleep(.25);raise SystemExit(7)']
        with patch.object(managed.subprocess, 'Popen', side_effect=start):
            self.assertEqual(managed.supervise(server, worker, dict(os.environ), dict(os.environ)), 7)
        self.assertEqual(len(children), 2)
        self.assertTrue(all(child.poll() is not None for child in children))

    def test_second_spawn_failure_stops_already_started_real_worker(self):
        actual = subprocess.Popen
        children = []
        def start(*args, **kwargs):
            if children:
                raise OSError('SYNTHETIC second child creation failure')
            child = actual(*args, **kwargs)
            children.append(child)
            return child
        argv = [sys.executable, '-c', 'import time;time.sleep(60)']
        with patch.object(managed.subprocess, 'Popen', side_effect=start):
            with self.assertRaises(OSError):
                managed.supervise(argv, argv, dict(os.environ), dict(os.environ))
        self.assertTrue(all(child.poll() is not None for child in children))

    def storage_fixture(self):
        import test_results
        from koevd_eval.protocols import ProtocolRegistry
        from koevd_eval.snapshots import file_digest
        from test_snapshots import FakeBucket
        fixture = test_results.ResultContractTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        index_file = self.root / 'index.json'
        index_file.write_text(json.dumps(fixture.index), encoding='utf-8')
        catalog = {'schema_version': 'koevd-space-catalog-v1',
                   'indexes': [{'id': 'fixture', 'label': 'SYNTHETIC CPU startup fixture',
                                'mode': 'operator_custom', 'path': 'index.json', 'sha256': file_digest(index_file)}],
                   'baselines': []}
        (self.root / 'catalog.json').write_text(json.dumps(catalog), encoding='utf-8')
        registry_dir = Path(__file__).resolve().parents[1] / 'configs/protocols'
        self.config['protocol_registry'] = str(registry_dir)
        return fixture, FakeBucket(), ProtocolRegistry(registry_dir)

    def test_real_empty_store_backup_and_pinned_restore_remain_quarantined_with_provider_double(self):
        from koevd_eval.snapshots import create_snapshot, HFBucketSnapshots
        from koevd_eval.storage import LocalSubmissionStore, StorageError
        from koevd_eval.submissions import SubmissionService, Principal
        fixture, provider, registry = self.storage_fixture()
        p = self.plan()
        sdk = SimpleNamespace(HfApi=lambda **kwargs: provider)
        with patch.dict(sys.modules, {'huggingface_hub': sdk}):
            managed.prepare_storage(p, 'SYNTHETIC-DEDICATED-TOKEN')
        self.assertEqual(provider.uploads, 1)
        self.assertTrue((p['store'] / 'submissions.sqlite3').is_file())
        self.assertEqual(len(list(p['backup'].glob('attempt-*/COMPLETED.json'))), 1)
        indexes = {'fixture': fixture.index}
        service = SubmissionService(LocalSubmissionStore(p['store']), indexes, registry=registry)
        actor = Principal('synthetic-author', 'operator_local')
        state = service.create(actor, fixture.document, 'fixture', key='startup-fixture-create')
        snap = self.root / 'source-snapshot.zip'
        receipt = create_snapshot(service.store, indexes, snap, registry=registry)
        HFBucketSnapshots(self.config['bucket'], api=provider).put(snap, receipt['sha256'])
        self.config.update(mode='restore', initialization_baseline_snapshot_sha256=None,
                           restore_root='fresh-restore', store_root='fresh-restore/store', snapshot_sha256=receipt['sha256'])
        restored_plan = self.plan()
        before = provider.uploads
        with patch.dict(sys.modules, {'huggingface_hub': sdk}):
            managed.prepare_storage(restored_plan, 'SYNTHETIC-DEDICATED-TOKEN')
        self.assertEqual(provider.uploads, before)  # No backup activation of old restored state.
        restored = SubmissionService(LocalSubmissionStore(restored_plan['store']), indexes, registry=registry)
        self.assertEqual(restored.result(actor, state['id']), fixture.document)
        self.assertEqual(len(restored.history(actor, state['id'])['events']), 1)
        with self.assertRaises(StorageError) as stopped:
            restored.public_list()
        self.assertEqual(stopped.exception.code, 'recovery_required')

    def test_public_bucket_fails_before_initializing_local_store_with_provider_double(self):
        fixture, provider, registry = self.storage_fixture()
        provider.private = False
        p = self.plan()
        with patch.dict(sys.modules, {'huggingface_hub': SimpleNamespace(HfApi=lambda **kwargs: provider)}):
            with self.assertRaises(ValueError):
                managed.prepare_storage(p, 'SYNTHETIC-DEDICATED-TOKEN')
        self.assertFalse(p['store'].exists())
        self.assertEqual(provider.uploads, 0)

    def test_store_appearing_after_plan_is_preserved_and_never_opened(self):
        fixture, provider, registry = self.storage_fixture()
        p = self.plan()
        p['store'].mkdir()
        sentinel = p['store'] / 'preserve.txt'
        sentinel.write_text('Existing operator data', encoding='utf-8')
        with patch.dict(sys.modules, {'huggingface_hub': SimpleNamespace(HfApi=lambda **kwargs: provider)}):
            with self.assertRaises(FileExistsError):
                managed.prepare_storage(p, 'SYNTHETIC-DEDICATED-TOKEN')
        self.assertEqual(sentinel.read_text(encoding='utf-8'), 'Existing operator data')
        self.assertFalse((p['store'] / 'submissions.sqlite3').exists())
        self.assertEqual(provider.uploads, 0)

    def test_fresh_host_disk_after_success_cannot_silently_initialize_again(self):
        fixture, provider, registry = self.storage_fixture()
        first = self.plan()
        sdk = SimpleNamespace(HfApi=lambda **kwargs: provider)
        with patch.dict(sys.modules, {'huggingface_hub': sdk}):
            managed.prepare_storage(first, 'SYNTHETIC-DEDICATED-TOKEN')
        self.assertEqual(provider.uploads, 1)
        self.config.update(store_root='second-host-empty-disk', backup_root='second-host-backups')
        second = self.plan()
        with patch.dict(sys.modules, {'huggingface_hub': sdk}):
            with self.assertRaisesRegex(ValueError, 'initialization baseline'):
                managed.prepare_storage(second, 'SYNTHETIC-DEDICATED-TOKEN')
        self.assertFalse(second['store'].exists())
        self.assertEqual(provider.uploads, 1)
        self.assertTrue((first['store'] / 'submissions.sqlite3').is_file())

    def test_explicit_remote_baseline_must_match_and_is_never_auto_extended(self):
        from koevd_eval.snapshots import HFBucketSnapshots
        fixture, provider, registry = self.storage_fixture()
        known = 'a' * 64
        provider.objects['koevd-snapshots/' + known + '.zip'] = b'SYNTHETIC baseline metadata fixture'
        transport = HFBucketSnapshots(self.config['bucket'], api=provider)
        managed.require_initialization_inventory(transport, [known])
        provider.objects['koevd-snapshots/' + 'b' * 64 + '.zip'] = b'SYNTHETIC unexpected later snapshot'
        with self.assertRaisesRegex(ValueError, 'initialization baseline'):
            managed.require_initialization_inventory(transport, [known])
        self.assertEqual(provider.uploads, 0)

    def test_legacy_initialize_and_duplicate_or_unknown_baseline_rejected(self):
        self.config['format'] = 'koevd-managed-space-v1'
        del self.config['initialization_baseline_snapshot_sha256']
        with self.assertRaisesRegex(ValueError, 'Legacy initialization'):
            self.plan()
        self.config.update(format='koevd-managed-space-v2', initialization_baseline_snapshot_sha256=['a' * 64] * 2)
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            self.plan()
        self.config['initialization_baseline_snapshot_sha256'] = ['unknown']
        with self.assertRaises(ValueError):
            self.plan()

    def test_legacy_pinned_restore_remains_supported_without_baseline_guessing(self):
        self.config.update(format='koevd-managed-space-v1', mode='restore', restore_root='legacy-restore',
                           store_root='legacy-restore/store', snapshot_sha256='a' * 64)
        del self.config['initialization_baseline_snapshot_sha256']
        self.assertEqual(self.plan()['restore'], self.root / 'legacy-restore')

    def test_inventory_refusal_is_distinct_without_private_provider_details(self):
        self.plan()
        env = {**self.env, 'KOEVD_BACKUP_TOKEN': 'SYNTHETIC-BUCKET-TOKEN',
               'OAUTH_CLIENT_ID': 'SYNTHETIC-CLIENT', 'OAUTH_CLIENT_SECRET': 'SYNTHETIC-SECRET'}
        output = io.StringIO()
        with patch.dict(os.environ, env, clear=True), patch.object(sys, 'argv', ['managed', '--config', str(self.path)]), \
                patch.object(managed, 'prepare_storage', side_effect=managed.InitializationInventoryMismatch('SYNTHETIC private provider details')), \
                patch.object(managed, 'supervise') as children, redirect_stderr(output):
            self.assertEqual(managed.main(), 2)
            children.assert_not_called()
        self.assertEqual(json.loads(output.getvalue()), {'startup': 'refused', 'code': 'initialization_inventory_mismatch',
            'database_root_created_by_this_attempt': False, 'server_or_worker_spawned_by_this_attempt': False})
        self.assertNotIn('private provider details', output.getvalue())

    def test_read_only_baseline_check_never_initializes_even_when_inventory_matches(self):
        fixture, provider, registry = self.storage_fixture()
        known = 'a' * 64
        provider.objects['koevd-snapshots/' + known + '.zip'] = b'SYNTHETIC inventory fixture'
        sdk = SimpleNamespace(HfApi=lambda **kwargs: provider)
        # No OAuth configuration: this checks Bucket access, never starts an app.
        env = {**self.env, 'KOEVD_BACKUP_TOKEN': 'SYNTHETIC-DEDICATED-TOKEN'}
        for baseline, code in (([], 2), ([known], 0)):
            with self.subTest(inventory_matches=bool(baseline)):
                self.config['initialization_baseline_snapshot_sha256'] = baseline
                p = self.plan()
                stdout, stderr = io.StringIO(), io.StringIO()
                with patch.dict(sys.modules, {'huggingface_hub': sdk}), patch.dict(os.environ, env, clear=True), \
                        patch.object(sys, 'argv', ['managed', '--config', str(self.path), '--check-initialization-baseline']), \
                        patch.object(managed, 'prepare_storage') as prepare, patch.object(managed, 'supervise') as children, \
                        redirect_stdout(stdout), redirect_stderr(stderr):
                    self.assertEqual(managed.main(), code)
                    prepare.assert_not_called()
                    children.assert_not_called()
                self.assertFalse(p['store'].exists())
                self.assertFalse(p['backup'].exists())
                self.assertEqual(provider.uploads, 0)
                if code == 0:
                    self.assertEqual(json.loads(stdout.getvalue()), {'initialization_baseline_matches': True,
                        'database_root_created_by_this_attempt': False,
                        'server_or_worker_spawned_by_this_attempt': False, 'remote_snapshot_writes': False})
                    self.assertEqual(stderr.getvalue(), '')
                else:
                    self.assertEqual(json.loads(stderr.getvalue())['code'], 'initialization_inventory_mismatch')
                    self.assertEqual(stdout.getvalue(), '')

    def test_read_only_baseline_check_rejects_other_modes(self):
        self.config.update(mode='restore', initialization_baseline_snapshot_sha256=None,
                           restore_root='fresh-restore', store_root='fresh-restore/store', snapshot_sha256='a' * 64)
        with patch.object(managed, 'checked_transport') as transport:
            with self.assertRaisesRegex(ValueError, 'requires initialize mode'):
                managed.check_initialization_baseline(self.plan(), 'SYNTHETIC-DEDICATED-TOKEN')
            transport.assert_not_called()

    def test_existing_initialization_root_is_distinct_before_credentials_or_children(self):
        self.plan()
        store = self.root / 'new-store'
        store.mkdir()
        sentinel = store / 'existing-operator-data.txt'
        sentinel.write_text('Preserve operator data', encoding='utf-8')
        output = io.StringIO()
        with patch.dict(os.environ, self.env, clear=True), patch.object(sys, 'argv', ['managed', '--config', str(self.path)]), \
                patch.object(managed, 'child_environments') as credentials, patch.object(managed, 'prepare_storage') as storage, \
                patch.object(managed, 'supervise') as children, redirect_stderr(output):
            self.assertEqual(managed.main(), 2)
            credentials.assert_not_called()
            storage.assert_not_called()
            children.assert_not_called()
        self.assertEqual(json.loads(output.getvalue()), {'startup': 'refused', 'code': 'initialization_store_root_exists',
            'database_root_created_by_this_attempt': False, 'server_or_worker_spawned_by_this_attempt': False})
        self.assertEqual(sentinel.read_text(encoding='utf-8'), 'Preserve operator data')
        self.assertFalse((store / 'submissions.sqlite3').exists())

    def test_only_finite_profiles_require_the_final_capture_release(self):
        self.assertIn('--await-final-snapshot-release',self.plan()['worker_argv'])
        self.config['cycles']=0
        self.assertNotIn('--await-final-snapshot-release',self.plan()['worker_argv'])

    def test_real_coordinator_stops_owned_server_before_final_release_and_drains_logs(self):
        from contextlib import redirect_stdout
        ready=self.root/'actual-server.pid';proof=self.root/'final-release.json'
        # Base interpreter avoids an extra Windows venv redirector in this
        # process-control unit test. Installed HTTP lifecycle is tested separately.
        python=getattr(sys,'_base_executable',sys.executable)
        server=[python,'-c','from pathlib import Path;import os,sys,time;Path(sys.argv[1]).write_text(str(os.getpid()));time.sleep(60)',str(ready)]
        program='''import ctypes,json,os,sys,time
from pathlib import Path
ready=Path(sys.argv[1]);deadline=time.monotonic()+5
while not ready.exists():
 if time.monotonic()>deadline:raise SystemExit(8)
 time.sleep(.01)
pid=int(ready.read_text())
print(json.dumps({'execution_scope':'operator_private_backup','event':'awaiting_final_snapshot_release'}),flush=True)
assert sys.stdin.readline()=='FINAL_SNAPSHOT\\n'
if os.name=='nt':
 kernel=ctypes.WinDLL('kernel32',use_last_error=True)
 kernel.OpenProcess.restype=ctypes.c_void_p
 kernel.WaitForSingleObject.argtypes=[ctypes.c_void_p,ctypes.c_uint32]
 kernel.CloseHandle.argtypes=[ctypes.c_void_p]
 handle=kernel.OpenProcess(0x100000,False,pid)
 ended=not handle or kernel.WaitForSingleObject(handle,0)==0
 if handle:kernel.CloseHandle(handle)
else:
 try:os.kill(pid,0);ended=False
 except ProcessLookupError:ended=True
assert ended
Path(sys.argv[2]).write_text(json.dumps({'server_terminal_before_release':ended}))
print(json.dumps({'execution_scope':'operator_private_backup','result':{'cycles':2,'failures':0}}),flush=True)
'''
        worker=[python,'-c',program,str(ready),str(proof),'--await-final-snapshot-release']
        output=io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(managed.supervise(server,worker,dict(os.environ),dict(os.environ)),0)
        self.assertTrue(json.loads(proof.read_text())['server_terminal_before_release'])
        records=[json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(records[0]['event'],'server_stopped_before_final_snapshot')
        self.assertEqual(records[-1]['result'],{'cycles':2,'failures':0})

    def test_coordinated_worker_failure_without_release_cleans_both_owned_processes(self):
        actual=subprocess.Popen;children=[]
        def start(*args,**kwargs):
            child=actual(*args,**kwargs);children.append(child);return child
        python=getattr(sys,'_base_executable',sys.executable)
        server=[python,'-c','import time;time.sleep(60)']
        worker=[python,'-c','import time;time.sleep(.1);raise SystemExit(7)','--await-final-snapshot-release']
        with patch.object(managed.subprocess,'Popen',side_effect=start):
            self.assertEqual(managed.supervise(server,worker,dict(os.environ),dict(os.environ)),7)
        self.assertEqual(len(children),2)
        self.assertTrue(all(child.poll() is not None for child in children))


if __name__ == '__main__':
    unittest.main()
