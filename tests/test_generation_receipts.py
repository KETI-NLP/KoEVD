"""Synthetic receipt/workflow tests; no real GPU or operator review evidence."""
from copy import deepcopy
import json
import shutil
import subprocess
import sys
from unittest.mock import patch
import unittest

import test_submissions as submission_fixture
from koevd_eval.eligibility import declaration_identity
from koevd_eval.generation_receipts import FORMAT, REQUIRED_KINDS
from koevd_eval.results import canonical_hash
from koevd_eval.storage import LocalSubmissionStore
from koevd_eval.submissions import Principal, SubmissionService


class GenerationReceiptTests(unittest.TestCase):
    def setUp(self):
        self.base = submission_fixture.SubmissionTests()
        self.base.setUp(); self.addCleanup(self.base.doCleanups)
        self.service = self.base.service

    def receipt(self, document=None, scope='cpu_fixture'):
        document = document or self.base.document
        return {'format':FORMAT, 'artifact_sha256':document['content_sha256'],
                'input_index_sha256':self.base.index['content_sha256'],
                'declaration_sha256':declaration_identity(document),
                'generation_level':'operator_reproduced', 'execution_scope':scope,
                'evidence_files':[{'kind':kind, 'sha256':canonical_hash('SYNTHETIC ' + kind), 'bytes':1}
                                  for kind in sorted(REQUIRED_KINDS)],
                'review_statement':'SYNTHETIC receipt fixture, no actual GPU or independent human review'}

    def accept(self, state, receipt=None, actor=None, key=None, revision=1):
        return self.service.accept_generation_receipt(actor or self.base.admin, state['id'],receipt or self.receipt(),
            revision=revision, expected_version=state['version'], reason='SYNTHETIC acceptance',key=key or self.base.key())

    def revoke(self, state, receipt):
        return self.service.revoke_generation_receipt(self.base.admin,state['id'],revision=1,
            receipt_sha256=canonical_hash(receipt),expected_version=state['version'],reason='SYNTHETIC revocation',key=self.base.key())

    def test_acceptance_is_private_immutable_and_restored_with_existing_store_format(self):
        state = self.base.create(); receipt = self.receipt(); accepted = self.accept(state,receipt)
        self.assertEqual(accepted['workflow'],'draft')
        self.assertEqual(self.service.public_list(),[])
        history = self.service.history(self.base.author,state['id'])
        self.assertEqual(history['events'][-1]['details']['receipt'],receipt)
        self.assertEqual(history['events'][-1]['actor']['subject'],'admin')
        backup = self.base.fixture.root/'receipt-backup.sqlite3'
        self.base.store.backup(backup)
        restored_root = self.base.fixture.root/'receipt-restored'; restored_root.mkdir()
        shutil.copyfile(backup,restored_root/'submissions.sqlite3')
        restored = SubmissionService(LocalSubmissionStore(restored_root),{'fixture':self.base.index},admins=['admin'])
        self.assertEqual(restored.history(self.base.author,state['id']),history)

    def test_intake_requires_independent_local_admin_not_owner_reviewer_or_hf_login(self):
        state = self.base.create()
        for actor in (self.base.author,self.base.reviewer,Principal('admin','hf_oauth')):
            with self.subTest(actor=actor):
                code = 'local_operator_required' if actor.authentication_source == 'hf_oauth' else 'independent_reviewer_required'
                self.base.assert_code(code,lambda:self.accept(state,actor=actor))
        owned = self.service.create(self.base.admin,self.base.document,'fixture',key=self.base.key())
        self.base.assert_code('independent_reviewer_required',lambda:self.accept(owned))
        self.assertEqual(len(self.service.history(self.base.author,state['id'])['events']),1)

    def test_binding_and_evidence_requirements_reject_without_changing_history(self):
        state = self.base.create()
        for field in ('artifact_sha256','input_index_sha256','declaration_sha256','extra','evidence_files','generation_level'):
            bad = self.receipt()
            if field == 'extra': bad['uploaded_score'] = 1
            elif field == 'evidence_files': bad[field] = bad[field][:-1]
            elif field == 'generation_level': bad[field] = 'measurement_rechecked'
            else: bad[field] = 'a'*64
            code = 'receipt_binding_mismatch' if field.endswith('sha256') else 'invalid_generation_receipt'
            with self.subTest(field=field):self.base.assert_code(code,lambda:self.accept(state,bad))
        self.assertEqual(self.service.get(self.base.author,state['id']),state)

    def test_replay_stale_version_and_duplicate_active_receipt(self):
        state=self.base.create(); receipt=self.receipt(); key=self.base.key()
        accepted=self.accept(state,receipt,key=key)
        self.assertEqual(self.accept(state,receipt,key=key),accepted)
        self.base.assert_code('stale_version',lambda:self.accept(state,receipt))
        self.base.assert_code('receipt_already_active',lambda:self.accept(accepted,receipt))
        changed=deepcopy(receipt);changed['review_statement']='Changed SYNTHETIC review'
        self.base.assert_code('idempotency_conflict',lambda:self.accept(state,changed,key=key))
        self.assertEqual(len(self.service.history(self.base.author,state['id'])['events']),2)

    def test_cpu_receipt_is_not_actual_gpu_and_private_notes_stay_private(self):
        state=self.base.publish('summary'); receipt=self.receipt(); accepted=self.accept(state,receipt)
        summary=self.service.public_summary(state['id'])
        self.assertFalse(summary['official_rank_eligible'])
        self.assertEqual(summary['verification']['generation'],'cpu_fixture_only')
        self.assertEqual(summary['verification']['measurement'],'measurement_limited')
        self.assertIsNone(summary['rank_admission']['operator_evidence_sha256'])
        self.assertNotIn(receipt['review_statement'],json.dumps(summary))
        revoked=self.revoke(accepted,receipt)
        self.assertEqual(self.service.public_summary(state['id'])['verification']['generation'],'user_reported')
        self.assertEqual(revoked['publication'],accepted['publication'])

    def test_gpu_scoped_synthetic_fixture_still_requires_policy_and_revocation_recheck(self):
        # The scope flag is a fixture to test rules; these hashes are not GPU evidence.
        state=self.base.publish('summary');receipt=self.receipt(scope='actual_gpu');accepted=self.accept(state,receipt)
        summary=self.service.public_summary(state['id'])
        self.assertFalse(summary['official_rank_eligible'])
        self.assertEqual(summary['rank_policy_status'],'candidate')
        self.assertEqual(summary['rank_admission']['operator_evidence_sha256'],canonical_hash(receipt))
        original_cache=self.service.profile_cache.get_or_compute
        def revoke_during_cache(*args,**kwargs):
            result=original_cache(*args,**kwargs)
            self.revoke(accepted,receipt)
            return result
        with patch.object(self.service.profile_cache,'get_or_compute',side_effect=revoke_during_cache):
            self.base.assert_code('publication_changed',lambda:self.service.public_summary(state['id']))
        self.assertIsNone(self.service.public_summary(state['id'])['rank_admission']['operator_evidence_sha256'])

    def test_receipt_revocation_during_first_analysis_is_rechecked(self):
        state=self.base.publish('summary');receipt=self.receipt();accepted=self.accept(state,receipt)
        original_analyze=submission_fixture.analyze
        def revoke_during_analysis(*args,**kwargs):
            self.revoke(accepted,receipt)
            return original_analyze(*args,**kwargs)
        with patch('koevd_eval.submissions.analyze',side_effect=revoke_during_analysis):
            self.base.assert_code('publication_changed',lambda:self.service.public_summary(state['id']))
        self.assertEqual(self.service.public_summary(state['id'])['verification']['generation'],'user_reported')

    def test_new_revision_does_not_inherit_generation_receipt_and_withdrawal_is_terminal(self):
        state=self.base.create();accepted=self.accept(state)
        revised=self.service.revise(self.base.author,state['id'],self.base.revised(),expected_version=accepted['version'],
            kind='measurement_recheck',reason='SYNTHETIC remeasurement',key=self.base.key())
        self.base.assert_code('receipt_binding_mismatch',lambda:self.accept(revised,self.receipt(),revision=2))
        withdrawn=self.base.action(revised,'withdraw')
        self.base.assert_code('withdrawn',lambda:self.accept(withdrawn))

    def test_operator_cli_accepts_and_revokes_against_existing_private_store(self):
        state=self.base.create();receipt=self.receipt();root=self.base.fixture.root
        for name,value in (('receipt.json',receipt),('operator-index.json',self.base.index),
                           ('operator-roles.json',{'reviewers':['reviewer'],'admins':['admin']})):
            (root/name).write_text(json.dumps(value),encoding='utf-8')
        base=[sys.executable,'-m','koevd_eval.submissions','--store-dir',str(self.base.root),
              '--trusted-index',str(root/'operator-index.json'),'--index-id','fixture',
              '--roles-file',str(root/'operator-roles.json'),'--actor','admin']
        def invoke(command):
            result=subprocess.run(base+command,capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(result.returncode,0,result.stderr)
            payload=json.loads(result.stdout)
            self.assertEqual(payload['execution_scope'],'operator_local_candidate')
            return payload['result']
        accepted=invoke(['accept-generation','--id',state['id'],'--revision','1',
                         '--receipt-file',str(root/'receipt.json'),'--expected-version',str(state['version']),
                         '--reason','SYNTHETIC CLI acceptance','--key','cli-accept'])
        history=invoke(['history','--id',state['id']])
        self.assertEqual(history['events'][-1]['details']['receipt'],receipt)
        revoked=invoke(['revoke-generation','--id',state['id'],'--revision','1',
                        '--receipt-sha256',canonical_hash(receipt),'--expected-version',str(accepted['version']),
                        '--reason','SYNTHETIC CLI revocation','--key','cli-revoke'])
        self.assertEqual(revoked['version'],accepted['version']+1)
        self.assertEqual(self.service.public_list(),[])


if __name__ == '__main__':unittest.main()
