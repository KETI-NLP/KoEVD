"""Acknowledgement/restore contract with local fixtures, no HF transmission."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
import sqlite3
import unittest
from unittest.mock import patch

import test_results as fixture_module
from koevd_eval.durability import (AcknowledgedSubmissionStore, FileCheckpointLedger,
                                   checked_receipt, logical_digest)
from koevd_eval.storage import LocalSubmissionStore, StorageError
from koevd_eval.submissions import SubmissionService, Principal


class ControlledSink:
    def __init__(self, ledger):
        self.ledger = ledger
        self.fail = False
        self.lost_response = False
        self.calls = 0
        self.wrong_receipt = False

    def head(self):
        return self.ledger.head()

    def commit(self, store, logical, parent):
        self.calls += 1
        if self.fail:
            raise RuntimeError('private-token-value https://private.example/token')
        value = self.ledger.commit(store, logical, parent)
        if self.lost_response:
            self.lost_response = False
            raise RuntimeError('Response lost after checkpoint HEAD committed')
        if self.wrong_receipt:
            value = deepcopy(value); value['logical_sha256'] = '0'*64
        return value


class DurabilityTests(unittest.TestCase):
    def setUp(self):
        fixture = fixture_module.ResultContractTests()
        fixture.setUp(); self.addCleanup(fixture.doCleanups)
        self.fixture = fixture
        self.root = fixture.root
        self.ledger = FileCheckpointLedger(self.root/'retained')
        self.sink = ControlledSink(self.ledger)
        self.store = AcknowledgedSubmissionStore(self.root/'live', self.sink)
        self.service = SubmissionService(self.store, {'fixture':fixture.index})
        self.actor = Principal('fixture-author', 'operator_local')

    def create(self, key='create-1'):
        return self.service.create(self.actor, self.fixture.document, 'fixture', key=key)

    def assert_code(self, code, operation):
        with self.assertRaises(StorageError) as caught:
            operation()
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_success_is_restorable_after_loss_of_live_directory(self):
        state = self.create()
        before = self.service.history(self.actor, state['id'])
        receipt = self.ledger.restore(self.root/'restart')
        fresh = AcknowledgedSubmissionStore(self.root/'restart', ControlledSink(self.ledger))
        service = SubmissionService(fresh, {'fixture':self.fixture.index})
        self.assertEqual(service.result(self.actor, state['id']), self.fixture.document)
        self.assertEqual(service.history(self.actor, state['id']), before)
        self.assertEqual(fresh.last_checkpoint, receipt)
        self.assertEqual(self.create(), state)

    def test_sink_failure_is_not_success_or_a_readable_unconfirmed_cut(self):
        previous = self.ledger.head()
        self.sink.fail = True
        error = self.assert_code('durability_unavailable', self.create)
        self.assertNotIn('private-token', str(error))
        self.assertEqual(self.ledger.head(), previous)
        self.assert_code('durability_unavailable', lambda:self.service.visible_list(self.actor))
        self.sink.fail = False
        state = self.create()  # Same persisted request key, not another submission.
        self.assertEqual(len(self.service.visible_list(self.actor)['items']), 1)
        with self.store.connection() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM submissions').fetchone()[0], 1)
        self.assertEqual(self.create(), state)

    def test_lost_response_reconciles_same_checkpoint_without_duplicate(self):
        sequence = self.ledger.head()['sequence']
        self.sink.lost_response = True
        self.assert_code('durability_unavailable', self.create)
        committed = self.ledger.head()
        self.assertEqual(committed['sequence'], sequence+1)
        state = self.create()
        self.assertEqual(self.ledger.head(), committed)
        self.assertEqual(self.create(), state)

    def test_reopening_unconfirmed_local_cut_is_refused(self):
        self.sink.fail = True
        self.assert_code('durability_unavailable', self.create)
        self.assert_code('checkpoint_integrity',
                         lambda:AcknowledgedSubmissionStore(self.root/'live', ControlledSink(self.ledger)))
        self.ledger.restore(self.root/'confirmed-restart')
        fresh = AcknowledgedSubmissionStore(self.root/'confirmed-restart', ControlledSink(self.ledger))
        service = SubmissionService(fresh, {'fixture':self.fixture.index})
        self.assertEqual(service.visible_list(self.actor)['items'], [])

    def test_nonempty_ledger_cannot_initialize_an_empty_store(self):
        self.create()
        self.assert_code('checkpoint_restore_required',
                         lambda:AcknowledgedSubmissionStore(self.root/'empty-restart', self.sink))
        self.assertFalse((self.root/'empty-restart').exists())

    def test_wrong_checkpoint_receipt_is_not_acknowledged(self):
        self.sink.wrong_receipt = True
        self.assert_code('checkpoint_integrity', self.create)
        self.assert_code('checkpoint_integrity', lambda:self.service.visible_list(self.actor))
        self.sink.wrong_receipt = False
        self.create()
        self.assertEqual(len(self.service.visible_list(self.actor)['items']), 1)

    def test_parallel_replay_creates_one_submission_and_one_data_commit(self):
        sequence = self.ledger.head()['sequence']
        with ThreadPoolExecutor(max_workers=4) as executor:
            states = list(executor.map(lambda _:self.create(), range(4)))
        self.assertTrue(all(state == states[0] for state in states))
        self.assertEqual(self.ledger.head()['sequence'], sequence+1)

    def test_rollback_does_not_create_a_checkpoint(self):
        previous = self.ledger.head()
        with self.assertRaises(RuntimeError):
            with self.store.connection(write=True) as db:
                db.execute("INSERT INTO indexes VALUES('uncommitted',?)", ('0'*64,))
                raise RuntimeError('rollback')
        self.assertEqual(self.ledger.head(), previous)
        with self.store.connection() as db:
            self.assertIsNone(db.execute("SELECT id FROM indexes WHERE id='uncommitted'").fetchone())

    def test_manifest_and_database_tampering_are_detected(self):
        self.create(); head = self.ledger.head()
        raw = self.ledger.root/(head['database_sha256']+'.sqlite3')
        with raw.open('ab') as stream:
            stream.write(b'tamper')
        self.assert_code('checkpoint_integrity', self.ledger.head)
        self.assert_code('checkpoint_integrity', lambda:self.ledger.restore(self.root/'bad-restore'))
        bad = deepcopy(head); bad['sequence'] = True
        self.assert_code('checkpoint_integrity', lambda:checked_receipt(bad))

    def test_foreign_head_is_not_overwritten_by_a_stale_live_writer(self):
        self.ledger.restore(self.root/'second-live')
        second = AcknowledgedSubmissionStore(self.root/'second-live', ControlledSink(self.ledger))
        service = SubmissionService(second, {'fixture':self.fixture.index})
        self.create(); committed = self.ledger.head()
        actor = Principal('another-fixture-author', 'operator_local')
        self.assert_code('checkpoint_conflict',
                         lambda:service.create(actor, self.fixture.document, 'fixture', key='other'))
        self.assertEqual(self.ledger.head(), committed)

    def test_interrupted_first_checkpoint_is_not_assumed_empty(self):
        ledger = FileCheckpointLedger(self.root/'incomplete')
        (ledger.root/('0'*64+'.sqlite3')).write_bytes(b'partial')
        self.assert_code('checkpoint_initialization_required', ledger.head)

    def test_interrupted_object_copy_can_retry_without_corrupt_address(self):
        previous = self.ledger.head()
        import koevd_eval.durability as module
        copy = module.shutil.copyfileobj
        def interrupted(original, saved, **kwargs):
            saved.write(original.read(128)); raise OSError('SYNTHETIC interrupted copy')
        with patch.object(module.shutil, 'copyfileobj', side_effect=interrupted):
            self.assert_code('durability_unavailable', self.create)
        self.assertEqual(self.ledger.head(), previous)
        self.assertFalse(list(self.ledger.root.glob('*.pending')))
        state = self.create()
        self.ledger.restore(self.root/'copy-retry-restore')
        fresh = AcknowledgedSubmissionStore(self.root/'copy-retry-restore', self.sink)
        service = SubmissionService(fresh, {'fixture':self.fixture.index})
        self.assertEqual(service.result(self.actor,state['id']),self.fixture.document)

    def test_acknowledged_summary_and_withdrawal_restore_public_scope(self):
        self.service.allow_self_reported_summaries=True
        state=self.create()
        state=self.service.publish_summary(self.actor,state['id'],consent={
            'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC publication permission'},
            expected_version=state['version'],reason='SYNTHETIC summary',key='summary')
        self.ledger.restore(self.root/'published-restart')
        fresh=AcknowledgedSubmissionStore(self.root/'published-restart',self.sink)
        service=SubmissionService(fresh,{'fixture':self.fixture.index},allow_self_reported_summaries=True)
        self.assertEqual(service.public_page()['items'][0]['scope'],'summary')
        self.assert_code('responses_private',lambda:service.public_result(state['id']))
        state=service.action(self.actor,state['id'],'withdraw',expected_version=state['version'],
                             reason='SYNTHETIC withdrawal',key='withdraw')
        self.ledger.restore(self.root/'withdrawn-restart')
        restored=AcknowledgedSubmissionStore(self.root/'withdrawn-restart',self.sink)
        final=SubmissionService(restored,{'fixture':self.fixture.index},allow_self_reported_summaries=True)
        self.assertEqual(final.public_page()['items'],[])
        self.assert_code('not_found',lambda:final.public_summary(state['id']))
        self.assertEqual(final.history(self.actor,state['id'])['state'],state)

    def test_retained_quota_does_not_acknowledge_a_lost_checkpoint(self):
        previous=self.ledger.head()
        limited=FileCheckpointLedger(self.ledger.root,max_retained_bytes=65536)
        self.sink.ledger=limited
        self.assert_code('checkpoint_capacity',self.create)
        self.assertEqual(limited.head(),previous)
