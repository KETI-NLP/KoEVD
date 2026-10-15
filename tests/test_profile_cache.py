"""Numerical cache and current publication checks; CPU fixtures only."""
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import unittest
from unittest.mock import patch

import test_public_registration_contract as fixture
from koevd_eval.profile_cache import NumericalProfileCache
from koevd_eval.diagnostics import analyze
from koevd_eval.eligibility import RankPolicy


class CacheTests(unittest.TestCase):
    def test_detached_value_and_identity(self):
        cache = NumericalProfileCache(); calls = []
        def compute():
            calls.append(1); return {'nested':[1]}
        first = cache.get_or_compute({'artifact':'one'}, compute)
        first['nested'].append(2)
        self.assertEqual(cache.get_or_compute({'artifact':'one'}, compute), {'nested':[1]})
        cache.get_or_compute({'artifact':'two'}, compute)
        self.assertEqual(len(calls), 2)

    def test_lru_and_oversized_values(self):
        cache = NumericalProfileCache(max_entries=1, max_bytes=40); calls=[]
        def get(key, value):
            return cache.get_or_compute({'key':key}, lambda:(calls.append(key) or {'value':value}))
        get('a',1);get('b',2);get('a',1)
        self.assertEqual(calls,['a','b','a'])
        get('large','x'*100);get('large','x'*100)
        self.assertEqual(calls[-2:],['large','large'])
        self.assertLessEqual(cache._size,40)

    def test_failed_compute_is_not_cached(self):
        cache=NumericalProfileCache()
        with self.assertRaisesRegex(ValueError,'failed'):
            cache.get_or_compute({},lambda:(_ for _ in ()).throw(ValueError('failed')))
        self.assertEqual(cache.get_or_compute({},lambda:{'retry':True}),{'retry':True})

    def test_concurrent_requests_share_compute(self):
        cache=NumericalProfileCache();started=Event();release=Event();calls=[]
        def compute():
            calls.append(1);started.set()
            if not release.wait(5):raise RuntimeError('test compute wait expired')
            return {'value':1}
        with ThreadPoolExecutor(max_workers=2) as pool:
            first=pool.submit(cache.get_or_compute,{},compute)
            self.assertTrue(started.wait(5))
            second=pool.submit(cache.get_or_compute,{},compute)
            release.set()
            self.assertEqual(first.result(),second.result())
        self.assertEqual(calls,[1])


class PublicProfileTests(unittest.TestCase):
    setUp=fixture.PublicRegistrationTests.setUp
    create=fixture.PublicRegistrationTests.create
    summary=fixture.PublicRegistrationTests.summary
    assert_code=fixture.PublicRegistrationTests.assert_code

    def test_profile_preserves_metrics_without_raw_cases_or_execution_ids(self):
        state=self.summary(self.create())
        raw=analyze(self.fixture.document,self.fixture.index,resamples=0)
        response=self.service.public_profile(state['id'])
        profile=response['analysis']
        for field in ('tasks','task3_task5','quality','charts','signals','statistics'):
            self.assertEqual(profile[field],raw[field])
        self.assertNotIn('cases',profile);self.assertNotIn('run',profile)
        self.assertNotIn('sources',profile['measurement_disagreement'])
        self.assert_code('responses_private',lambda:self.service.public_result(state['id']))

    def test_warm_profile_reuses_analysis_but_latest_display_is_returned(self):
        state=self.summary(self.create())
        with patch('koevd_eval.submissions.analyze', wraps=analyze) as compute:
            first=self.service.public_profile(state['id'])
            self.service.update_display(self.author,state['id'],display_name='SYNTHETIC renamed',
                                       expected_version=state['version'],key='rename')
            second=self.service.public_profile(state['id'])
            self.assertEqual(compute.call_count,1)
        self.assertEqual(first['analysis'],second['analysis'])
        self.assertEqual(second['display']['display_name'],'SYNTHETIC renamed')

    def test_warm_cache_does_not_serve_withdrawn_profile(self):
        state=self.summary(self.create());self.service.public_profile(state['id'])
        self.service.action(self.author,state['id'],'withdraw',expected_version=state['version'],
                            reason='SYNTHETIC withdrawal',key='withdraw')
        with patch('koevd_eval.submissions.analyze',side_effect=AssertionError('should not score')):
            self.assert_code('not_found',lambda:self.service.public_profile(state['id']))

    def test_policy_change_invalidates_cached_admission(self):
        state=self.summary(self.create())
        first=self.service.public_profile(state['id'])
        # Fictional fixture decision; never a production ratification.
        self.service.rank_policy=RankPolicy(status='ratified',ratification_sha256='1'*64)
        second=self.service.public_profile(state['id'])
        self.assertNotEqual(first['rank_admission']['policy_sha256'],second['rank_admission']['policy_sha256'])
        self.assertEqual(first['analysis']['tasks'],second['analysis']['tasks'])

    def test_withdrawal_during_warm_cache_read_is_rechecked(self):
        state=self.summary(self.create());self.service.public_profile(state['id'])
        original=self.service.profile_cache.get_or_compute
        def during(identity,compute):
            result=original(identity,compute)
            self.service.action(self.author,state['id'],'withdraw',expected_version=state['version'],
                                reason='SYNTHETIC concurrent withdrawal',key='withdraw')
            return result
        with patch.object(self.service.profile_cache,'get_or_compute',side_effect=during):
            self.assert_code('not_found',lambda:self.service.public_profile(state['id']))
