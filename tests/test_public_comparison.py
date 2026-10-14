"""Public paired numerical comparisons; fictional CPU runs and permissions."""
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

import test_public_leaderboard as fixture
import test_eligibility as admission_fixture
from koevd_eval.diagnostics import analyze, compare
from koevd_eval.eligibility import evaluate_admission, leaderboard
from koevd_eval.profile_cache import numerical_comparison
from koevd_eval.storage import StorageError


class PublicComparisonTests(unittest.TestCase):
    setUp=fixture.PublicLeaderboardTests.setUp
    key=fixture.PublicLeaderboardTests.key
    action=fixture.PublicLeaderboardTests.action
    create=fixture.PublicLeaderboardTests.create
    publish=fixture.PublicLeaderboardTests.publish
    publish_state=fixture.PublicLeaderboardTests.publish_state
    other_document=fixture.PublicLeaderboardTests.other_document

    def pair(self):
        other=self.other_document()
        return self.publish(),self.publish(other),other

    def code(self,expected,operation):
        with self.assertRaises(StorageError) as caught:operation()
        self.assertEqual(caught.exception.code,expected)

    def test_summary_scope_has_exact_paired_rates_without_raw_identities(self):
        left,right,other=self.pair()
        response=self.service.public_comparison(left['id'],right['id'])
        expected=compare(self.document,self.index,other,self.index,resamples=0)
        self.assertEqual(response['comparison'],numerical_comparison(expected))
        self.assertFalse(response['raw_cases_included'])
        self.assertFalse(response['approved_originals_available'])
        self.assertEqual(response['left']['analysis']['tasks'],analyze(self.document,self.index,resamples=0)['tasks'])
        text=json.dumps(response)
        for private in ('"sample_ids"','"left_run_id"','"right_run_id"','"cases"','"owner"','"review_statement"','fixture response'):
            self.assertNotIn(private,text)
        for side in (left,right):
            self.code('responses_private',lambda side=side:self.service.public_result(side['id']))

    def test_warm_board_and_pair_share_analysis_and_admission(self):
        left,right,other=self.pair()
        with patch('koevd_eval.submissions.analyze',wraps=analyze) as scoring, \
             patch('koevd_eval.submissions.evaluate_admission',wraps=evaluate_admission) as admission, \
             patch('koevd_eval.submissions.compare',wraps=compare) as paired:
            first=self.service.public_leaderboard()
            response=self.service.public_comparison(left['id'],right['id'])
            self.assertEqual(first,self.service.public_leaderboard())
            self.assertEqual(response,self.service.public_comparison(left['id'],right['id']))
            self.assertEqual((scoring.call_count,admission.call_count,paired.call_count),(2,2,1))
        expected=leaderboard([(left['id'],self.document,self.index,None),(right['id'],other,self.index,None)],
                             registry=self.service.registry,policy=self.service.rank_policy,resamples=0)
        self.assertEqual(first['boards'],expected['boards'])
        self.assertEqual(first['excluded'],expected['excluded'])

    def test_withdrawn_or_private_run_cannot_use_warm_pair(self):
        left,right,other=self.pair()
        self.service.public_comparison(left['id'],right['id'])
        self.action(right,'withdraw')
        self.code('not_found',lambda:self.service.public_comparison(left['id'],right['id']))
        third=deepcopy(other);third['run']['model']['id']='SYNTHETIC-PRIVATE'
        draft=self.create(admission_fixture.seal(third))
        self.code('not_found',lambda:self.service.public_comparison(left['id'],draft['id']))

    def test_withdrawal_during_pair_scoring_discards_response(self):
        left,right,_=self.pair()
        def during(*args,**kwargs):
            self.action(left,'withdraw')
            return compare(*args,**kwargs)
        with patch('koevd_eval.submissions.compare',side_effect=during):
            self.code('publication_changed',lambda:self.service.public_comparison(left['id'],right['id']))

    def test_withdrawal_during_warm_pair_read_discards_response(self):
        left,right,_=self.pair();self.service.public_comparison(left['id'],right['id'])
        original=self.service.profile_cache.get_or_compute
        def during(identity,compute):
            result=original(identity,compute)
            if identity.get('kind')=='public_pair':self.action(right,'withdraw')
            return result
        with patch.object(self.service.profile_cache,'get_or_compute',side_effect=during):
            self.code('publication_changed',lambda:self.service.public_comparison(left['id'],right['id']))

    def test_changed_generation_is_exploratory_and_not_a_formal_rank(self):
        left=self.publish();other=self.other_document();other['run']['model']['dtype']='float16'
        right=self.publish(admission_fixture.seal(other))
        response=self.service.public_comparison(left['id'],right['id'])
        for task in response['comparison']['tasks']:
            self.assertEqual(task['compatibility']['level'],'common_inputs_exploratory')
            self.assertFalse(task['compatibility']['official_rank_eligible'])
            self.assertTrue(any(r['field']=='model.dtype' for r in task['compatibility']['reasons']))

    def test_identical_registration_and_duplicate_artifacts_are_rejected(self):
        left=self.publish()
        self.code('distinct_runs_required',lambda:self.service.public_comparison(left['id'],left['id']))
        second=self.service.create(self.reviewer,self.document,'fixture',key=self.key())
        self.service.allow_self_reported_summaries=True
        second=self.service.publish_summary(self.reviewer,second['id'],consent={
            'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC permission'},
            expected_version=second['version'],reason='SYNTHETIC duplicate',key=self.key())
        self.code('duplicate_artifacts',lambda:self.service.public_comparison(left['id'],second['id']))
        board=self.service.public_leaderboard()
        self.assertEqual(board['publication_count'],2)
        self.assertEqual(board['distinct_artifact_count'],1)
        self.assertEqual({r['entry_id'] for r in board['excluded']},{left['id']})
        alias=next(p for p in board['publications'] if p['submission_id']==second['id'])
        self.assertEqual(alias['duplicate_of'],left['id'])

    def test_capacity_fails_without_partial_comparison(self):
        left,right,_=self.pair()
        with patch('koevd_eval.submissions.MAX_PUBLIC_COMPARISON_BYTES',1):
            self.code('comparison_capacity',lambda:self.service.public_comparison(left['id'],right['id']))
