from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

import test_submissions as fixture
from koevd_eval.policy_decisions import PolicyArchive, FORMAT as POLICY_FORMAT
from koevd_eval.results import canonical_hash, _seal
from koevd_eval.snapshots import (HFBucketSnapshots, create_snapshot, restore_snapshot,
                                  file_digest, FORMAT, MAX_SNAPSHOT_BYTES)
from koevd_eval.storage import LocalSubmissionStore, StorageError, encode
from koevd_eval.submissions import SubmissionService


class FakeBucket:
    """In-memory provider contract only; no real HF authentication/storage."""
    def __init__(self): self.objects = {}; self.uploads = 0; self.private = True
    def bucket_info(self, name): return SimpleNamespace(id=name, private=self.private)
    def list_bucket_tree(self, name, prefix, recursive):
        return [SimpleNamespace(type='file', path=k, size=len(v)) for k,v in self.objects.items() if k.startswith(prefix)]
    def batch_bucket_files(self, name, add):
        self.uploads += 1
        for path, key in add: self.objects[key] = Path(path).read_bytes()
    def download_bucket_files(self, name, files, raise_on_missing_files):
        for item, path in files: Path(path).write_bytes(self.objects[item.path])


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.f = fixture.SubmissionTests(); self.f.setUp(); self.addCleanup(self.f.doCleanups)
        self.root = self.f.fixture.root / 'snapshots'; self.root.mkdir()
        self.indexes = {'fixture': self.f.index}
        self.archive = self.root / 'snapshot.zip'

    def make(self, **kwargs):
        return create_snapshot(self.f.store, self.indexes, self.archive, **kwargs)

    def restore(self, path=None, digest=None, destination=None, **kwargs):
        return restore_snapshot(path or self.archive, digest or file_digest(path or self.archive),
                                destination or self.root / 'restored', kwargs.pop('indexes', self.indexes), **kwargs)

    def changed_archive(self, name, transform, *, extra=None, duplicate=False):
        output = self.root / ('changed-' + str(len(list(self.root.iterdir()))) + '.zip')
        with zipfile.ZipFile(self.archive) as original, zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_STORED) as changed:
            values = {n: original.read(n) for n in original.namelist()}
            values[name] = transform(values[name])
            if name != 'manifest.json':
                manifest = json.loads(values['manifest.json'])
                manifest['files'][name] = {'sha256':sha256(values[name]).hexdigest(), 'bytes':len(values[name])}
                values['manifest.json'] = encode(manifest)
            for n, raw in values.items(): changed.writestr(n, raw)
            if extra: changed.writestr(extra, b'bad')
            if duplicate: changed.writestr(name, values[name])
        return output

    def test_restore_preserves_withdrawal_private_history_original_and_replay(self):
        state = self.f.publish('summary')
        state = self.f.action(state, 'withdraw')
        receipt = self.make()
        restored = self.restore(digest=receipt['sha256'])
        service = SubmissionService(LocalSubmissionStore(self.root/'restored'/'store'), self.indexes)
        self.assertEqual(service.get(self.f.author, state['id']), state)
        self.assertEqual(service.history(self.f.author, state['id']), self.f.service.history(self.f.author,state['id']))
        self.assertEqual(service.result(self.f.author, state['id']), self.f.document)
        with self.assertRaisesRegex(StorageError,'offline until operator reconciliation'): service.public_list()
        with service.store.connection() as after, self.f.store.connection() as before:
            self.assertEqual(list(map(tuple,after.execute('SELECT * FROM requests ORDER BY actor,key'))),
                             list(map(tuple,before.execute('SELECT * FROM requests ORDER BY actor,key'))))
        self.assertFalse(restored['automatic_activation']); self.assertFalse(restored['latest_state_verified'])
        self.assertTrue(restored['requires_withdrawal_reconciliation'])
        self.assertFalse((self.root/'restored'/'policy').exists())

    def test_selected_chain_ratify_revoke_is_preserved_without_activation_or_roles(self):
        self.f.create()
        policy = PolicyArchive(self.root/'live-policy', create=True)
        decision = {'format':POLICY_FORMAT,'admission_version':'koevd-rank-admission-v1','action':'ratify',
                    'actor':'admin','decided_at':'2026-10-08T00:00:00Z','reason':'SYNTHETIC CPU policy fixture','previous_sha256':None}
        head1 = policy.record(decision)
        head2 = policy.record(dict(decision,action='revoke',previous_sha256=head1,decided_at='2026-10-08T01:00:00Z'))
        # Unselected branch is intentionally not included, nor presented as latest.
        policy.record(dict(decision,reason='SYNTHETIC other branch'))
        result = self.make(policy_root=policy.root, policy_head=head2)
        self.assertEqual(result['policy_decisions'], 2)
        restored = self.restore()
        saved = PolicyArchive(self.root/'restored'/'policy')
        self.assertEqual(saved.history(head2), policy.history(head2))
        self.assertEqual(saved.policy(head2).status, 'candidate')
        self.assertEqual(restored['policy_head_sha256'], head2)
        self.assertFalse(restored['automatic_activation'])
        self.assertEqual(set(p.name for p in (self.root/'restored').iterdir()), {'store','policy','restore-receipt.json'})

    def test_operator_binding_digest_and_schema_fail_closed(self):
        self.f.create(); self.make()
        with self.assertRaisesRegex(ValueError, 'pinned'): self.restore(digest='0'*64)
        with self.assertRaisesRegex(ValueError, 'bindings'): self.restore(indexes={'renamed':self.f.index})
        def mutate(raw):
            path = self.root/'bad.sqlite3'; path.write_bytes(raw)
            with sqlite3.connect(path) as db: db.execute('CREATE VIEW hostile AS SELECT * FROM artifacts')
            return path.read_bytes()
        changed = self.changed_archive('submissions.sqlite3', mutate)
        with self.assertRaisesRegex(ValueError, 'SQL schema'): self.restore(path=changed)
        self.assertFalse((self.root/'restored').exists())

    def test_hash_resealed_database_cannot_hide_artifact_or_projection_damage(self):
        state = self.f.create(); self.make()
        def mutate(raw):
            path = self.root/'bad-artifact.sqlite3'; path.write_bytes(raw)
            with sqlite3.connect(path) as db:
                sql = db.execute("SELECT sql FROM sqlite_master WHERE name='artifacts_update'").fetchone()[0]
                db.execute('DROP TRIGGER artifacts_update')
                db.execute("UPDATE artifacts SET data=x'7b7d'")
                db.execute(sql)
            return path.read_bytes()
        changed = self.changed_archive('submissions.sqlite3', mutate)
        with self.assertRaisesRegex(StorageError,'artifact missing or changed'): self.restore(path=changed)
        def state_damage(raw):
            path=self.root/'bad-state.sqlite3'; path.write_bytes(raw)
            with sqlite3.connect(path) as db:
                changed_state = dict(state, workflow='withdrawn')
                db.execute('UPDATE submissions SET state=?', (encode(changed_state).decode('utf-8'),))
            return path.read_bytes()
        changed2 = self.changed_archive('submissions.sqlite3', state_damage)
        with self.assertRaisesRegex(StorageError,'audit history'): self.restore(path=changed2)
        self.assertFalse((self.root/'restored').exists())

    def test_duplicate_traversal_symlink_compression_and_manifest_tamper(self):
        self.make()
        for extra in ('../outside', 'policy/../../outside', 'credential.json'):
            changed = self.changed_archive('manifest.json',lambda x:x,extra=extra)
            with self.subTest(extra=extra), self.assertRaises(ValueError): self.restore(path=changed)
        with __import__('warnings').catch_warnings():
            __import__('warnings').simplefilter('ignore')
            duplicate = self.changed_archive('manifest.json',lambda x:x,duplicate=True)
        with self.assertRaisesRegex(ValueError,'Duplicate'): self.restore(path=duplicate)
        for compression, mode in ((zipfile.ZIP_DEFLATED,stat.S_IFREG),(zipfile.ZIP_STORED,stat.S_IFLNK)):
            path=self.root/('member-'+str(compression)+'-'+str(mode)+'.zip')
            with zipfile.ZipFile(path,'x') as out:
                item=zipfile.ZipInfo('manifest.json'); item.compress_type=compression; item.external_attr=mode<<16
                out.writestr(item,b'{}')
            with self.assertRaisesRegex(ValueError,'member type'): self.restore(path=path)
        bad = self.changed_archive('manifest.json',lambda raw:encode(dict(json.loads(raw),automatic_activation=True)))
        with self.assertRaises(ValueError): self.restore(path=bad)

    def test_policy_tamper_and_unselected_record_are_rejected(self):
        policy=PolicyArchive(self.root/'p',create=True)
        document={'format':POLICY_FORMAT,'admission_version':'koevd-rank-admission-v1','action':'ratify',
                  'actor':'admin','decided_at':'2026-10-08T00:00:00Z','reason':'SYNTHETIC','previous_sha256':None}
        head=policy.record(document); self.make(policy_root=policy.root,policy_head=head)
        changed=self.changed_archive('policy/'+head+'.json',lambda raw:encode(dict(json.loads(raw),reason='changed')))
        with self.assertRaisesRegex(ValueError,'selected digest'): self.restore(path=changed)
        with self.assertRaises(ValueError): self.make(policy_root=policy.root)

    def test_limits_missing_inputs_and_existing_paths_preserved(self):
        self.make(); raw=self.archive.read_bytes()
        with self.assertRaisesRegex(ValueError,'exists'): self.make()
        self.assertEqual(self.archive.read_bytes(),raw)
        destination=self.root/'existing'; destination.mkdir(); (destination/'keep').write_text('keep')
        with self.assertRaisesRegex(ValueError,'fresh'): self.restore(destination=destination)
        self.assertEqual((destination/'keep').read_text(),'keep')
        with patch('koevd_eval.snapshots.MAX_SNAPSHOT_BYTES',len(raw)-1), self.assertRaises(ValueError): self.restore()
        with patch('koevd_eval.snapshots.MAX_ROWS',1), self.assertRaisesRegex(ValueError,'row'): self.restore()
        with patch('koevd_eval.snapshots.MAX_MANIFEST_BYTES',1), self.assertRaises(ValueError): self.restore()
        with self.assertRaisesRegex(ValueError,'outside'): create_snapshot(self.f.store,self.indexes,self.f.root/'illegal.zip')

    def test_concurrent_restore_and_failed_publication_preserve_targets(self):
        self.make()
        def work():
            try: self.restore(); return 'ok'
            except (ValueError,OSError): return 'refused'
        with ThreadPoolExecutor(max_workers=2) as pool: outcomes=list(pool.map(lambda _:work(),range(2)))
        self.assertEqual(sorted(outcomes),['ok','refused'])
        self.assertTrue((self.root/'restored'/'restore-receipt.json').is_file())
        other=self.root/'failed'
        with patch('koevd_eval.snapshots.os.rename',side_effect=OSError('SYNTHETIC failed rename')), self.assertRaises(OSError): self.restore(destination=other)
        self.assertFalse(other.exists()); self.assertFalse((self.root/'.failed.restore-lock').exists())

    def test_bucket_contract_upload_readback_replay_and_fresh_restore(self):
        self.f.create(); snapshot=self.make()
        fake=FakeBucket(); repo=HFBucketSnapshots('private-org/fixture',api=fake)
        result=repo.put(self.archive,snapshot['sha256'])
        self.assertTrue(result['readback_verified']); self.assertFalse(result['atomic_conditional_write'])
        repo.put(self.archive,snapshot['sha256']); self.assertEqual(fake.uploads,1)
        fetched=self.root/'fetched.zip'; repo.fetch(snapshot['sha256'],fetched)
        self.assertEqual(fetched.read_bytes(),self.archive.read_bytes())
        self.restore(path=fetched)
        with self.assertRaises(ValueError): repo.fetch(snapshot['sha256'],fetched)

    def test_bucket_public_partial_changed_oversize_missing_and_errors_fail_closed(self):
        result=self.make(); digest=result['sha256']; fake=FakeBucket(); repo=HFBucketSnapshots('private-org/fixture',api=fake)
        fake.private=False
        with self.assertRaisesRegex(ValueError,'PRIVATE'): repo.put(self.archive,digest)
        self.assertEqual(fake.uploads,0)
        fake.private=True
        with self.assertRaisesRegex(ValueError,'missing'): repo.fetch(digest,self.root/'missing.zip')
        fake.objects[repo.key(digest)]=b'corrupt'
        with self.assertRaisesRegex(ValueError,'pinned'): repo.put(self.archive,digest)
        self.assertEqual(fake.uploads,0)
        fake.objects.clear()
        with patch.object(fake,'batch_bucket_files',side_effect=RuntimeError('SECRET should never print')):
            with self.assertRaisesRegex(ValueError,'bucket operation') as error: repo.put(self.archive,digest)
            self.assertNotIn('SECRET',str(error.exception))
        with patch.object(fake,'list_bucket_tree',return_value=[SimpleNamespace(path=repo.key(digest),type='file',size=MAX_SNAPSHOT_BYTES+1)]):
            with self.assertRaisesRegex(ValueError,'oversize'): repo.fetch(digest,self.root/'huge.zip')

    def test_standard_index_requires_outside_registry_and_exact_definition_binding(self):
        from test_protocols import ProtocolTests
        f = ProtocolTests(); f.setUp(); self.addCleanup(f.doCleanups)
        index = f.registry.prepare_index(f.definition['id'],f.data,f.root/'pinned-run')
        indexes = {'standard': index}
        store = LocalSubmissionStore(self.root/'standard-store'); SubmissionService(store,indexes,registry=f.registry)
        destination=self.root/'standard.zip'
        with self.assertRaisesRegex(ValueError,'outside registry'):
            create_snapshot(store,indexes,destination)
        result=create_snapshot(store,indexes,destination,registry=f.registry)
        with self.assertRaisesRegex(ValueError,'outside registry'):
            restore_snapshot(destination,result['sha256'],self.root/'standard-restored',indexes)
        restored=restore_snapshot(destination,result['sha256'],self.root/'standard-restored',indexes,registry=f.registry)
        self.assertEqual(restored['bindings']['protocols'],{f.definition['id']:f.definition['content_sha256']})

    def test_corrupt_upload_and_source_failure_return_no_success(self):
        result=self.make(); fake=FakeBucket(); repo=HFBucketSnapshots('private-org/fixture',api=fake)
        def corrupt(name,add):
            for path,key in add:fake.objects[key]=b'partial upload'
        with patch.object(fake,'batch_bucket_files',side_effect=corrupt), self.assertRaisesRegex(ValueError,'pinned'):
            repo.put(self.archive,result['sha256'])
        target=self.root/'failed-snapshot.zip'
        with patch('koevd_eval.snapshots.os.link',side_effect=OSError('SYNTHETIC hardlink failure')), self.assertRaises(OSError):
            create_snapshot(self.f.store,self.indexes,target)
        self.assertFalse(target.exists())

    def test_cli_admin_boundary_create_restore_and_default_candidate(self):
        state=self.f.create()
        index=self.root/'index.json'; index.write_bytes(encode(self.f.index))
        catalog=self.root/'catalog.json'; catalog.write_bytes(encode({'schema_version':'koevd-space-catalog-v1',
            'indexes':[{'id':'fixture','label':'Synthetic snapshot test','mode':'synthetic_demo','path':'index.json',
                        'sha256':file_digest(index)}],'baselines':[]}))
        roles=self.root/'roles.json'; roles.write_bytes(encode({'admins':['admin'],'reviewers':[]}))
        prefix=[sys.executable,'-m','koevd_eval.snapshots','--catalog',str(catalog),'--roles-file',str(roles),'--demo']
        create=['create','--store-dir',str(self.f.root),'--output',str(self.archive)]
        denied=subprocess.run(prefix+['--actor','author']+create,capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(denied.returncode,2); self.assertFalse(self.archive.exists())
        passed=subprocess.run(prefix+['--actor','admin']+create,capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(passed.returncode,0,passed.stderr); digest=json.loads(passed.stdout)['result']['sha256']
        restored=subprocess.run(prefix+['--actor','admin','restore','--input',str(self.archive),'--sha256',digest,
                                    '--destination',str(self.root/'cli-restored')],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(restored.returncode,0,restored.stderr)
        service=SubmissionService(LocalSubmissionStore(self.root/'cli-restored'/'store'),self.indexes)
        self.assertEqual(service.get(self.f.author,state['id']),state); self.assertEqual(service.rank_policy.status,'candidate')


if __name__=='__main__': unittest.main()
