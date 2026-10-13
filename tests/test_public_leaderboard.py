"""CPU publication/policy fixtures; no real ratification or GPU attestation."""
from copy import deepcopy
import json
import unittest
import uuid
from unittest.mock import patch

import test_eligibility as admission_fixture
from koevd_eval.eligibility import RankPolicy, declaration_identity, leaderboard
from koevd_eval.generation_receipts import FORMAT, REQUIRED_KINDS
from koevd_eval.results import canonical_hash
from koevd_eval.storage import LocalSubmissionStore, StorageError
from koevd_eval.submissions import Principal, SubmissionService


class PublicLeaderboardTests(unittest.TestCase):
    def setUp(self):
        self.fixture=admission_fixture.AdmissionTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.index,self.document=self.fixture.index,self.fixture.doc
        self.store=LocalSubmissionStore(self.fixture.fixture.root/'board-store')
        self.author,self.reviewer,self.admin=[Principal(s,'operator_local') for s in ('owner','reviewer','admin')]
        self.service=SubmissionService(self.store,{'fixture':self.index},reviewers=['reviewer'],admins=['admin'],
                                       registry=self.fixture.registry)
        self.counter=0

    def key(self):
        self.counter+=1;return 'board-test-'+str(self.counter)

    def action(self,state,name,actor=None,**options):
        return self.service.action(actor or self.author,state['id'],name,expected_version=state['version'],
            reason='SYNTHETIC board test',key=self.key(),**options)

    def create(self,document=None):
        return self.service.create(self.author,document or self.document,'fixture',key=self.key())

    def publish(self,document=None):
        state=self.create(document)
        return self.publish_state(state)

    def publish_state(self,state):
        state=self.action(state,'request_review',consent={'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC permission only'})
        state=self.action(state,'start_review',self.reviewer)
        state=self.action(state,'approve',self.reviewer,rights_evidence='SYNTHETIC private review note')
        return self.action(state,'publish',self.admin)

    def accept(self,state,document=None):
        document=document or self.document
        receipt={'format':FORMAT,'artifact_sha256':document['content_sha256'],
            'input_index_sha256':self.index['content_sha256'],'declaration_sha256':declaration_identity(document),
            'generation_level':'operator_reproduced','execution_scope':'actual_gpu',
            'evidence_files':[{'kind':k,'sha256':canonical_hash('SYNTHETIC '+k),'bytes':1} for k in sorted(REQUIRED_KINDS)],
            'review_statement':'SYNTHETIC hypothetical GPU-scope receipt; no actual human or GPU evidence'}
        state=self.service.accept_generation_receipt(self.admin,state['id'],receipt,revision=state['head_revision'],
            expected_version=state['version'],key=self.key(),reason='SYNTHETIC local operator')
        return state,receipt

    def assert_changed(self,mutation):
        def during_compute(*args,**kwargs):
            mutation();return leaderboard(*args,**kwargs)
        with patch('koevd_eval.submissions.leaderboard',side_effect=during_compute):
            with self.assertRaises(StorageError) as error:self.service.public_leaderboard()
        self.assertEqual(error.exception.code,'publication_changed')

    def other_document(self):
        other=deepcopy(self.document);other['run']['model']['id']='SYNTHETIC-OTHER'
        return admission_fixture.seal(other)

    def test_default_complete_public_snapshot_has_exclusions_no_private_raw_or_rank(self):
        other=self.other_document();self.create(other) # Private draft must not leak.
        state=self.publish();self.accept(state)
        result=self.service.public_leaderboard()
        self.assertEqual(result['publication_count'],1)
        self.assertEqual(result['coverage'],'complete_current_publication_snapshot')
        self.assertEqual(result['boards'],[]);self.assertFalse(result['official_ranking_enabled'])
        self.assertTrue(result['excluded'])
        self.assertTrue(all('policy_not_ratified' in row['reasons'] for row in result['excluded']))
        raw=json.dumps(result)
        for text in ('SYNTHETIC-OTHER','fixture response','private review note','review_statement','evidence_files','"owner":'):
            self.assertNotIn(text,raw)

    def test_trusted_fixture_policy_and_exact_receipts_connect_only_eligible_metrics(self):
        self.service.rank_policy=self.fixture.policy # Hypothetical CPU fixture only.
        first,_=self.accept(self.publish())
        other=self.other_document();second,_=self.accept(self.publish(other),other)
        result=self.service.public_leaderboard()
        self.assertTrue(result['official_ranking_enabled']);self.assertTrue(result['boards'])
        task2=[b for b in result['boards'] if b['metric_id'].startswith('task2')]
        self.assertEqual(len(task2),4)
        self.assertTrue(all(len(b['rows'])==2 for b in task2))
        self.assertTrue(all(row['rank']==1 for b in task2 for row in b['rows']))
        self.assertFalse(any(b['metric_id'].startswith(('task3','task4')) for b in result['boards']))
        for state in (first,second):
            summary=self.service.public_summary(state['id'])
            self.assertTrue(summary['official_rank_eligible'])
            self.assertTrue(all(not m['rank_eligible'] for m in summary['rank_admission']['metrics'] if m['task'] in (3,4,'3+5')))

    def test_listing_admission_stays_unknown_under_ratified_policy_until_rescoring(self):
        first,_=self.accept(self.publish())
        other=self.other_document();second=self.publish(other) # No receipt: excluded.
        for item in self.service.public_list():
            self.assertIs(item['official_rank_eligible'],False)
            self.assertEqual(item['rank_eligibility_status'],'policy_not_ratified')
        self.service.rank_policy=self.fixture.policy # Hypothetical CPU policy only.
        self.assertTrue(self.service.public_summary(first['id'])['official_rank_eligible'])
        self.assertFalse(self.service.public_summary(second['id'])['official_rank_eligible'])
        listed=self.service.public_list();page=self.service.public_page(limit=1)
        self.assertEqual(page['items'],listed[:1])
        rest=self.service.public_page(after=page['next_cursor'],limit=1)
        self.assertEqual(rest['items'],listed[1:])
        for item in listed:
            self.assertIsNone(item['official_rank_eligible'])
            self.assertEqual(item['rank_eligibility_status'],'not_evaluated_in_listing')
            self.assertEqual(item['rank_policy_status'],'ratified')
        self.service.rank_policy=RankPolicy()
        self.assertTrue(all(i['official_rank_eligible'] is False for i in self.service.public_page()['items']))

    def test_withdrawal_during_scoring_is_committed_and_rejected_before_return(self):
        state=self.publish()
        self.assert_changed(lambda:self.action(state,'withdraw'))
        self.assertEqual(self.service.public_leaderboard()['publication_count'],0)

    def test_receipt_revocation_during_scoring_invalidates_snapshot(self):
        self.service.rank_policy=self.fixture.policy
        state,receipt=self.accept(self.publish())
        self.assert_changed(lambda:self.service.revoke_generation_receipt(self.admin,state['id'],revision=1,
            receipt_sha256=canonical_hash(receipt),expected_version=state['version'],reason='SYNTHETIC revoked',key=self.key()))
        self.assertEqual(self.service.public_leaderboard()['boards'],[])

    def test_new_publication_during_scoring_invalidates_complete_membership(self):
        self.publish()
        self.assert_changed(lambda:self.publish(self.other_document()))
        self.assertEqual(self.service.public_leaderboard()['publication_count'],2)

    def test_current_published_revision_not_private_head_and_receipt_not_inherited(self):
        self.service.rank_policy=self.fixture.policy
        state,_=self.accept(self.publish())
        other=deepcopy(self.document);other['run']['id']=str(uuid.uuid4())
        other=admission_fixture.seal(other)
        revised=self.service.revise(self.author,state['id'],other,expected_version=state['version'],
            kind='rerun',reason='SYNTHETIC private revision',key=self.key())
        board=self.service.public_leaderboard()
        self.assertEqual(board['publications'][0]['revision'],1)
        self.assertEqual(board['publications'][0]['model']['id'],self.document['run']['model']['id'])
        self.assertTrue(board['boards'])
        self.publish_state(revised)
        board=self.service.public_leaderboard()
        self.assertEqual(board['publications'][0]['revision'],2)
        self.assertEqual(board['boards'],[])
        self.assertTrue(all('independent_generation_evidence_missing' in row['reasons'] for row in board['excluded']))

    def test_capacity_is_explicit_never_a_partial_rank(self):
        self.publish()
        for key,value in (('MAX_LEADERBOARD_ENTRIES',0),('MAX_LEADERBOARD_BYTES',1)):
            with patch('koevd_eval.submissions.'+key,value),self.assertRaises(StorageError) as error:
                self.service.public_leaderboard()
            self.assertEqual(error.exception.code,'leaderboard_capacity')
            self.assertEqual(error.exception.status,503)

    def test_operator_policy_change_during_compute_is_not_returned_as_old_rank(self):
        self.publish()
        self.assert_changed(lambda:setattr(self.service,'rank_policy',RankPolicy(status='ratified',ratification_sha256='d'*64)))


if __name__=='__main__':unittest.main()
