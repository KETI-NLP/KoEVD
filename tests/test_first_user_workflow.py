"""First-user transport behavior; no external service, credentials or GPU."""
from importlib.resources import files
import os
import shutil
import subprocess
import unittest
from unittest.mock import patch

from koevd_eval.storage import StorageError
import test_submission_web
import test_durability


class ReadinessTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_submission_web.SubmissionHTTPTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)

    def test_ready_probe_checks_storage_without_creating_submission(self):
        f = self.fixture
        with patch.object(f.submissions, 'check_readiness', wraps=f.submissions.check_readiness) as check:
            response = f.author.get('/readyz')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ready', 'registration_enabled': True})
        check.assert_called_once_with()
        with f.submissions.store.connection() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM submissions').fetchone()[0], 0)

    def test_dependency_failure_is_not_liveness_failure_or_secret_disclosure(self):
        f = self.fixture
        for error in (StorageError('checkpoint_integrity', 'SYNTHETIC-private-detail', 503),
                      RuntimeError('SYNTHETIC-private-detail')):
            with self.subTest(error=type(error).__name__), patch.object(f.submissions, 'check_readiness', side_effect=error):
                response = f.author.get('/readyz')
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.json(), {'status': 'unavailable', 'registration_enabled': True})
                self.assertNotIn('SYNTHETIC', response.text)
                self.assertEqual(f.author.get('/healthz').status_code, 200)

    def test_closed_service_is_unavailable(self):
        f = self.fixture
        with patch.object(f.service, 'closed', True):
            self.assertEqual(f.author.get('/readyz').status_code, 503)

    def test_dirty_checkpoint_probe_cannot_acknowledge_or_repair_a_save(self):
        f = test_durability.DurabilityTests()
        f.setUp()
        self.addCleanup(f.doCleanups)
        before = f.sink.calls
        f.service.check_readiness()
        self.assertEqual(f.sink.calls, before)
        f.sink.fail = True
        with self.assertRaises(StorageError):
            f.create()
        attempts = f.sink.calls
        f.sink.fail = False
        with self.assertRaises(StorageError) as caught:
            f.service.check_readiness()
        self.assertEqual(caught.exception.code, 'durability_unavailable')
        self.assertEqual(f.sink.calls, attempts)
        f.create()  # Only the explicit operation may confirm the pending cut.
        f.service.check_readiness()

    def test_readiness_checks_remote_fence_and_recovery_gate(self):
        f = self.fixture
        with patch.object(f.submissions, '_recovery_ready', side_effect=StorageError('recovery_required', 'not ready', 503)):
            self.assertEqual(f.author.get('/readyz').status_code, 503)
        durable = test_durability.DurabilityTests()
        durable.setUp()
        self.addCleanup(durable.doCleanups)
        durable.sink.check_current = lambda receipt: (_ for _ in ()).throw(StorageError('checkpoint_stale', 'stale', 503))
        with self.assertRaises(StorageError) as caught:
            durable.service.check_readiness()
        self.assertEqual(caught.exception.code, 'checkpoint_stale')


class PublicReadRetryTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('KOEVD_TEST_NODE') or shutil.which('node'), 'Optional Node retry boundary checks')
    def test_bounded_public_retries_never_replay_mutations_or_integrity_failures(self):
        script = r"""
const assert=require('node:assert/strict');
const {request,explanation}=require(process.argv[1]);
function response(status,code){return new Response(JSON.stringify({error:{code}}),{status});}
async function attempt(path,method='GET',status=503,code='durability_unavailable',network=false){
  let calls=0,delays=[],notices=[];
  const result=await request(async()=>{calls++;if(network)throw new TypeError('network');return response(status,code);},
    {path,method,sleep:async ms=>delays.push(ms),onRetry:value=>notices.push(value)}).catch(e=>e);
  return {calls,delays,notices,result};
}
(async()=>{
  for(const path of ['/api/public/submissions','/api/public/leaderboard','/api/public/compare?left=a&right=b','/api/public/submissions/abc-123/profile']){
    const value=await attempt(path);assert.equal(value.calls,3);assert.deepEqual(value.delays,[1000,2500]);
    assert.equal(value.result.status,503);assert.deepEqual(value.notices.map(x=>x.attempt),[2,3]);
    assert.equal((await attempt(path,'GET',503,undefined,true)).calls,3);
  }
  for(const [path,method] of [['/api/public/submissions','POST'],['/api/submissions','GET'],['/api/identity','GET'],['/api/public/submissions/abc/result','GET'],['/api/public/compare/download?format=json','GET']])
    assert.equal((await attempt(path,method)).calls,1);
  for(const status of [400,401,403,404,409,413,422,429,500])assert.equal((await attempt('/api/public/submissions','GET',status)).calls,1);
  for(const code of ['checkpoint_integrity','checkpoint_stale','checkpoint_target_not_private','public_capacity','withdrawn'])
    assert.equal((await attempt('/api/public/submissions','GET',503,code)).calls,1);
  let count=0;
  const success=await request(async()=>++count===1?response(503,'registration_busy'):new Response('{}'),{path:'/api/public/leaderboard',sleep:async()=>{}});
  assert.equal(success.status,200);assert.equal(count,2);
  assert.match(explanation({code:'durability_unavailable'}),/not a rejection of your file/);
  assert.match(explanation(new TypeError('network')),/connection/);
})().catch(error=>{console.error(error);process.exitCode=1;});
"""
        subprocess.run([os.environ.get('KOEVD_TEST_NODE') or shutil.which('node'), '-e', script,
                        str(files('koevd_eval').joinpath('assets', 'public_reads.js'))],
                       check=True, capture_output=True, text=True, timeout=30)
