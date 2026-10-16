"""Recovery contracts exercised with synthetic CPU measurements and identities."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from koevd_eval.common import read_jsonl,write_jsonl
from koevd_eval.pipeline import classify_run,file_sha,save_json
from koevd_eval.results import export_run,validate_results
from koevd_eval.preflight import preflight
from koevd_eval.run_openai_compatible import make_config,APIResponse
import test_results
import test_submissions


class MeasurementRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.fixture=test_results.ResultContractTests();self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root=self.fixture.run;self.manifest=deepcopy(self.fixture.manifest)
        self.artifact=self.root/'SYNTHETIC-artifact';self.artifact.mkdir()
        (self.artifact/'config.json').write_text('{}')
        (self.artifact/'fake.safetensors').write_bytes(b'SYNTHETIC-no-weights')
        self.calls=[];self.fail_task=None

    def process(self,command,check):
        arg=lambda option:command[command.index(option)+1]
        task=int(arg('--task'));self.calls.append(task)
        if self.fail_task==task:
            Path(arg('--output')).write_text('SYNTHETIC partial output')
            raise subprocess.CalledProcessError(1,command)
        data=list(read_jsonl(arg('--input')))
        for row in data:
            row['measurement']=({'label':'safe'} if task==3 else {'strategies':['c_reasoning']}) if row['api_status']=='ok' else None
        write_jsonl(arg('--output'),data)

    def run_measure(self,**kwargs):
        with patch('koevd_eval.measurement_runs.subprocess.run',side_effect=self.process):
            classify_run(self.root,self.manifest,*([self.artifact]*4),**kwargs)

    def test_failed_task_preserves_success_and_retry_reuses_it(self):
        self.fail_task=4
        with self.assertRaises(subprocess.CalledProcessError):self.run_measure()
        disk=json.loads((self.root/'pipeline.json').read_text());self.assertEqual(set(disk['measurements']),{'3'})
        first=file_sha(self.root/'task3_measured.jsonl');self.manifest=disk;self.fail_task=None
        self.run_measure();self.assertEqual(self.calls,[3,4,4]);self.assertEqual(file_sha(self.root/'task3_measured.jsonl'),first)
        self.assertEqual(len(list((self.root/'measurement_attempts').glob('task4-*'))),2)
        validate_results(export_run(self.root,self.fixture.index),self.fixture.index)

    def test_changed_batch_only_retries_selected_task_and_requires_explicit_replacement(self):
        self.fail_task=4
        with self.assertRaises(subprocess.CalledProcessError):self.run_measure()
        self.fail_task=None;self.run_measure(measurement_tasks=(4,),batch_size=1)
        self.assertEqual(self.manifest['measurements']['3']['batch_size'],2)
        self.assertEqual(self.manifest['measurements']['4']['batch_size'],1)
        with self.assertRaisesRegex(ValueError,'settings changed'):self.run_measure(measurement_tasks=(3,),batch_size=1)
        self.run_measure(measurement_tasks=(3,),batch_size=1,remeasure=True)
        attempt=self.root/self.manifest['measurements']['3']['attempt']
        self.assertTrue((attempt/'previous-task3_measured.jsonl').is_file())

    def test_completed_tamper_is_not_silently_recomputed(self):
        self.run_measure();self.calls.clear()
        (self.root/'task3_measured.jsonl').write_text('tampered')
        with self.assertRaises(ValueError):self.run_measure(remeasure=True)
        self.assertEqual(self.calls,[])

    def test_pending_promotion_recovers_without_another_classifier_call(self):
        import koevd_eval.measurement_runs as module
        original=module.os.replace
        def fail_once(source,destination):
            if Path(destination).name=='task3_measured.jsonl':raise OSError('SYNTHETIC power-loss boundary')
            return original(source,destination)
        with patch.object(module.os,'replace',side_effect=fail_once):
            with self.assertRaises(OSError):self.run_measure(measurement_tasks=(3,))
        self.manifest=json.loads((self.root/'pipeline.json').read_text())
        self.assertIn('3',self.manifest['measurement_pending'])
        with self.assertRaisesRegex(ValueError,'promotion pending'):export_run(self.root,self.fixture.index)
        self.run_measure(measurement_tasks=(3,),remeasure=True);self.assertEqual(self.calls,[3])
        self.assertNotIn('measurement_pending',self.manifest)


class RegistrationRecoveryTests(unittest.TestCase):
    setUp=test_submissions.SubmissionTests.setUp
    key=test_submissions.SubmissionTests.key
    create=test_submissions.SubmissionTests.create
    action=test_submissions.SubmissionTests.action
    publish=test_submissions.SubmissionTests.publish
    assert_code=test_submissions.SubmissionTests.assert_code
    def summary(self,state):
        return self.service.publish_summary(self.author,state['id'],consent={'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC fresh consent'},
            reason='SYNTHETIC share',expected_version=state['version'],key=self.key())

    def test_disabled_review_and_cancel_old_pending(self):
        state=self.create();state=self.action(state,'request_review',consent={'scope':'responses','accepted':True,'rights_statement':'SYNTHETIC'})
        self.service.admins=frozenset();self.assertFalse(self.service.review_requests_enabled)
        self.assert_code('review_unavailable',lambda:self.action(state,'request_review',consent={'scope':'summary','accepted':True,'rights_statement':'SYNTHETIC'}))
        state=self.action(state,'cancel_review');self.assertEqual(state['workflow'],'draft');self.assertIsNone(state['consent'])
        self.service.allow_self_reported_summaries=True
        state=self.summary(state);self.assertEqual(state['publication']['scope'],'summary')

    def test_cancel_restores_prior_summary_consent_and_keeps_current_name(self):
        self.service.allow_self_reported_summaries=True
        original=self.summary(self.create())
        pending=self.action(original,'request_review',consent={'scope':'responses','accepted':True,'rights_statement':'SYNTHETIC new request'})
        state=self.action(pending,'cancel_review')
        self.assertEqual(state['workflow'],original['workflow']);self.assertEqual(state['consent'],original['consent'])
        self.assertEqual(state['publication'],original['publication'])

    def test_unpublish_and_republish_need_fresh_consent(self):
        state=self.publish('summary');sid=state['id'];self.service.public_summary(sid)
        self.assert_code('not_found',lambda:self.action(state,'unpublish',self.other))
        state=self.action(state,'unpublish');self.assertEqual(state['workflow'],'draft');self.assertIsNone(state['consent'])
        self.assertEqual(self.service.public_list(),[])
        self.assert_code('not_found',lambda:self.service.public_summary(sid))
        self.assertEqual(self.service.result(self.author,sid),self.document)
        self.service.allow_self_reported_summaries=True
        state=self.summary(state);self.assertEqual(state['publication']['status'],'published')
        self.assertEqual(state['publication']['scope'],'summary')
        self.assert_code('responses_private',lambda:self.service.public_result(sid))

    def test_legacy_withdraw_restores_private_without_recreating_original(self):
        state=self.action(self.publish('summary'),'withdraw');sid=state['id']
        self.assert_code('not_found',lambda:self.action(state,'reopen',self.other))
        state=self.action(state,'reopen');self.assertEqual(state['workflow'],'draft')
        self.assertIsNone(state['approval']);self.assertIsNone(state['consent']);self.assertEqual(self.service.public_list(),[])
        self.assertEqual(self.service.result(self.author,sid),self.document)
        self.assert_code('duplicate_submission',lambda:self.create())
        self.assert_code('invalid_transition',lambda:self.action(state,'reopen'))


class PreflightInputTests(unittest.TestCase):
    def inputs(self):return [{'sample_id':str(task),'task':task,'messages':[{'role':'user','content':'prompt '+str(task)}]} for task in (1,2,3,5)]
    def test_budget_rejects_before_network(self):
        class Tokenizer:
            def apply_chat_template(self,*args,**kw):return list(range(20))
        with patch('koevd_eval.preflight.urllib.request.urlopen') as network:
            with self.assertRaisesRegex(ValueError,'exceed context budget'):
                preflight(make_config('http://localhost:8000/v1','actual/model',max_tokens=10),self.inputs(),tokenizer=Tokenizer(),context_window=25)
            network.assert_not_called()

    def test_real_samples_use_actual_output_budget_and_omit_responses(self):
        class Inventory:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,*args):return b'{"data":[{"id":"actual/model"}]}'
        calls=[]
        def request(*args,**kwargs):calls.append(args);return APIResponse('SYNTHETIC PRIVATE CONTENT',finish_reason='stop')
        config=make_config('http://localhost:8000/v1','actual/model',max_tokens=1024)
        with patch('koevd_eval.preflight.urllib.request.urlopen',return_value=Inventory()),patch('koevd_eval.preflight.call_api',side_effect=request):
            result=preflight(config,self.inputs(),samples=4)
        self.assertEqual([c[5] for c in calls],[16,1024,1024,1024,1024])
        self.assertEqual([r['task'] for r in result['prepared_input_probes']],[1,2,3,5])
        self.assertFalse(result['probe_in_benchmark']);self.assertNotIn('SYNTHETIC PRIVATE CONTENT',json.dumps(result))

    def test_budget_forwards_only_explicit_template_options(self):
        class Tokenizer:
            def apply_chat_template(self,*args,**kwargs):
                self.kwargs=kwargs;return [1,2]
        tokenizer=Tokenizer()
        from koevd_eval.preflight import prompt_budget
        config=make_config('http://localhost:8000/v1','actual/model',max_tokens=10,extra_body={'chat_template_kwargs':{'enable_thinking':False}})
        result=prompt_budget(config,{r['sample_id']:r for r in self.inputs()},tokenizer,32)
        self.assertFalse(tokenizer.kwargs['enable_thinking']);self.assertTrue(result['all_fit_context'])


if __name__=='__main__':unittest.main()
