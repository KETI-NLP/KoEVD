"""Real local HTTP, interruption and journal tests. No GPU/model is invoked."""
from collections import Counter
from contextlib import contextmanager
from copy import deepcopy
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import importlib.util
import subprocess
import sys
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
import urllib.error

from koevd_eval.common import read_jsonl, write_jsonl
from koevd_eval.pipeline import prepare_run, generate_run
from koevd_eval.preflight import preflight
from koevd_eval.results import build_index, export_run, validate_results, validate_execution
from koevd_eval.run_openai_compatible import (APIResponse, call_api, make_config, run_rows,
                                             input_digest, _output_lock, validate_extra_body, _atomic_json)
from test_own_model_pipeline import dataset_fixture


@contextmanager
def server(*,responses=None,delays=None,models=('cpu-http-target',),reject_extra=False):
    state={'requests':[],'counts':Counter(),'active':0,'peak':0,'completed':[],'lock':threading.Lock()}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if models is None:
                self.send_error(404);return
            self.send_response(200);self.end_headers()
            self.wfile.write(json.dumps({'data':[{'id':m} for m in models]}).encode())
        def do_POST(self):
            body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            text=body['messages'][-1]['content'] if body['messages'] else ''
            with state['lock']:
                state['requests'].append((body,dict(self.headers)))
                state['counts'][text]+=1;ordinal=state['counts'][text]
                state['active']+=1;state['peak']=max(state['peak'],state['active'])
            try:
                if delays:time.sleep(delays.get(text,0))
                outcome=(responses or {}).get(text)
                if isinstance(outcome,list):outcome=outcome[min(ordinal-1,len(outcome)-1)]
                if reject_extra and 'top_k' in body:outcome=400
                if isinstance(outcome,int):
                    self.send_response(outcome);self.end_headers()
                    self.wfile.write(b'SYNTHETIC_KEY_TEST_TOKEN http://internal/path')
                    return
                if outcome is None:
                    answer='A' if 'choose an answer' in text else ('{"decision":"refuse"}' if 'mock tool' in text else ('safe' if 'exactly one label' in text else 'HTTP fixture response'))
                    outcome={'content':answer}
                message={'role':'assistant',**outcome}
                finish=message.pop('_finish','stop')
                self.send_response(200);self.send_header('x-request-id','server-request-'+str(len(state['requests'])));self.end_headers()
                self.wfile.write(json.dumps({'id':'response-fixture','model':'server-declared-model',
                    'choices':[{'message':message,'finish_reason':finish}],
                    'usage':{'prompt_tokens':5,'completion_tokens':3,'total_tokens':8,'untrusted_extra':'discard'}},ensure_ascii=False).encode())
            finally:
                with state['lock']:state['active']-=1;state['completed'].append(text)
        def log_message(self,*args):pass
    http=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=http.serve_forever,daemon=True);thread.start()
    try:yield f'http://127.0.0.1:{http.server_port}/v1',state
    finally:http.shutdown();http.server_close();thread.join()


def rows(count):
    return [{'sample_id':str(i),'messages':[{'role':'user','content':str(i)}],
             'gold':{'label':'unsafe'},'metadata':{'secret_gold':'never_send'}} for i in range(count)]


class RunnerTests(unittest.TestCase):
    def test_status_replace_retries_transient_windows_failure_without_truncating_old_status(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'status.json';_atomic_json(path,{'stage':'old'})
            actual=os.replace;calls=[];waits=[]
            def transient(source,destination):
                self.assertEqual(json.loads(path.read_text()),{'stage':'old'})
                calls.append(True)
                if len(calls)<3:
                    error=PermissionError('SYNTHETIC replacement unavailable');error.winerror=5;raise error
                return actual(source,destination)
            with patch('koevd_eval.run_openai_compatible.os.name','nt'), \
                    patch('koevd_eval.run_openai_compatible.os.replace',side_effect=transient), \
                    patch('koevd_eval.run_openai_compatible.time.sleep',side_effect=waits.append):
                _atomic_json(path,{'stage':'new'})
            self.assertEqual(json.loads(path.read_text()),{'stage':'new'})
            self.assertEqual(waits,[.02,.04]);self.assertEqual(len(calls),3)

    def test_persistent_or_non_windows_replace_error_keeps_old_status_and_remains_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'status.json';_atomic_json(path,{'stage':'old'})
            error=PermissionError('SYNTHETIC denied');error.winerror=5
            for platform,expected_calls in (('nt',6),('posix',1)):
                with patch('koevd_eval.run_openai_compatible.os.name',platform), \
                        patch('koevd_eval.run_openai_compatible.os.replace',side_effect=error) as replaced, \
                        patch('koevd_eval.run_openai_compatible.time.sleep') as wait:
                    with self.assertRaises(PermissionError):_atomic_json(path,{'stage':'new'})
                    self.assertEqual(replaced.call_count,expected_calls)
                    self.assertEqual(wait.call_count,expected_calls-1)
                self.assertEqual(json.loads(path.read_text()),{'stage':'old'})
                self.assertEqual(json.loads(path.with_suffix('.json.tmp').read_text()),{'stage':'new'})

    def test_parallel_out_of_order_stable_output_and_resume_identity(self):
        with tempfile.TemporaryDirectory() as d,server(delays={'0':.08,'1':.005}) as (base,state):
            out=Path(d)/'result.jsonl';config=make_config(base,'cpu-http-target');events=[]
            result=run_rows(rows(6),out,config,workers=2,progress=events.append)
            self.assertEqual([r['sample_id'] for r in read_jsonl(out)],list(map(str,range(6))))
            self.assertLessEqual(state['peak'],2);self.assertGreaterEqual(state['peak'],2)
            self.assertNotEqual(state['completed'][0],'0')
            identity=json.loads(out.with_suffix('.jsonl.run.json').read_text())['run_id']
            with patch('koevd_eval.run_openai_compatible.call_api') as api:
                run_rows(rows(6),out,config,workers=1,resume=True);api.assert_not_called()
            self.assertEqual(identity,result['0']['generation']['run_id'])
            self.assertEqual(events[-1]['completed'],6);self.assertEqual(events[-1]['pending'],0)
            self.assertEqual(events[-1]['state'],'completed')
            for body,headers in state['requests']:
                self.assertEqual(set(body),{'model','messages','temperature','max_tokens'})
                self.assertIn('X-Request-Id',headers)
            with self.assertRaisesRegex(ValueError,'input order'):
                run_rows(list(reversed(rows(6))),out,config,resume=True)

    def test_retry_history_and_nonretryable_errors_redact_credentials(self):
        with tempfile.TemporaryDirectory() as d,server(responses={'0':[429,{'content':'accepted'}],'1':401}) as (base,state):
            out=Path(d)/'result.jsonl'
            result=run_rows(rows(2),out,make_config(base,'cpu-http-target'),api_key='SYNTHETIC_KEY_TEST_TOKEN',retries=3,retry_delay=0)
            self.assertEqual(state['counts']['0'],2);self.assertEqual(state['counts']['1'],1)
            self.assertEqual([a['status'] for a in result['0']['generation']['attempts']],['error','ok'])
            self.assertEqual(result['0']['generation']['attempts'][0]['http_status'],429)
            self.assertIsNone(result['0']['api_error']);self.assertEqual(result['1']['api_status'],'error')
            self.assertNotIn(b'SYNTHETIC_KEY_TEST_TOKEN',b''.join(p.read_bytes() for p in Path(d).iterdir()))
            self.assertNotIn(b'http://internal/path',out.read_bytes())

    def test_interrupt_attempt_is_durable_and_success_is_not_regenerated(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'result.jsonl';config=make_config('http://unused/v1','cpu-http-target')
            with patch('koevd_eval.run_openai_compatible.call_api',side_effect=['first',KeyboardInterrupt]):
                with self.assertRaises(KeyboardInterrupt):run_rows(rows(3),out,config)
            journal=out.with_suffix('.jsonl.progress.jsonl')
            events=list(read_jsonl(journal))
            self.assertEqual(events[-1]['event'],'attempt_started')
            original_id=events[-1]['attempt']['id']
            with journal.open('a',encoding='utf-8') as handle:handle.write('{"partial":')
            with patch('koevd_eval.run_openai_compatible.call_api',return_value='resumed') as api:
                saved=run_rows(rows(3),out,config,resume=True);self.assertEqual(api.call_count,2)
            history=saved['1']['generation']['attempts']
            self.assertEqual(history[0]['id'],original_id)
            self.assertEqual([a['status'] for a in history],['interrupted_unknown','ok'])
            self.assertFalse(journal.exists())
            self.assertEqual(json.loads(out.with_suffix('.jsonl.status.json').read_text())['state'],'completed')

    def test_parallel_interrupt_keeps_active_response_checkpoints(self):
        with tempfile.TemporaryDirectory() as d,server(delays={'0':.01,'1':.04}) as (base,state):
            out=Path(d)/'result.jsonl';config=make_config(base,'cpu-http-target')
            def interrupt(value):
                if value['state']=='running' and value['completed']==1:raise KeyboardInterrupt
            with self.assertRaises(KeyboardInterrupt):run_rows(rows(4),out,config,workers=2,progress=interrupt)
            self.assertLessEqual(len(state['requests']),2)
            run_rows(rows(4),out,config,workers=2,resume=True)
            self.assertEqual(len(state['requests']),4)
            self.assertEqual(len(list(read_jsonl(out))),4)
            self.assertEqual(set(state['counts'].values()),{1})

    def test_legacy_journal_adoption_does_not_invent_past_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'result.jsonl';config=make_config('http://unused/v1','cpu-http-target')
            original={**rows(2)[0],'prediction':'legacy','api_status':'ok','api_error':None,
                      'evaluated_model':'cpu-http-target','run_config':config,'input_sha256':input_digest(rows(2)[0])}
            write_jsonl(out.with_suffix('.jsonl.progress.jsonl'),[original])
            with patch('koevd_eval.run_openai_compatible.call_api',return_value='new') as api:
                saved=run_rows(rows(2),out,config,resume=True);self.assertEqual(api.call_count,1)
            self.assertNotIn('generation',saved['0']);self.assertIn('generation',saved['1'])

    def test_process_lock_and_existing_file_guards(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'result.jsonl'
            with _output_lock(out):
                with self.assertRaisesRegex(ValueError,'holds this output lock'):
                    run_rows([],out,make_config('http://unused','m'))
            with _output_lock(out):pass  # leftover file is not evidence of a live owner
            out.write_text('{}\n')
            with self.assertRaisesRegex(ValueError,'already exists'):
                run_rows([],out,make_config('http://unused','m'))

    def test_extra_parameters_preserved_and_rejection_has_no_fallback(self):
        with tempfile.TemporaryDirectory() as d,server(reject_extra=True) as (base,state):
            config=make_config(base,'cpu-http-target',extra_body={'top_k':10,'seed':17,'chat_template_kwargs':{'enable_thinking':False}})
            result=run_rows(rows(1),Path(d)/'out.jsonl',config,retries=3,retry_delay=0)
            self.assertEqual(len(state['requests']),1)
            self.assertEqual(state['requests'][0][0]['top_k'],10)
            self.assertEqual(result['0']['api_status'],'error')
            with self.assertRaisesRegex(ValueError,'Chat probe rejected'):
                preflight(config,rows(1))
            for extra in ({'messages':[]},{'user':'ignored'},{'tools':[]},{'seed':.1},{'chat_template_kwargs':{'enable_thinking':'false'}}):
                with self.assertRaises(ValueError):validate_extra_body(extra)
            with self.assertRaises(ValueError):make_config('http://host/v1?api_key=secret','m')

    def test_reasoning_empty_refusal_and_length_do_not_trigger_regeneration(self):
        with tempfile.TemporaryDirectory() as d,server(responses={'0':{'content':None,'reasoning_content':'reasoning only','_finish':'length'},
                                                               '1':{'content':None,'refusal':'blocked'}}) as (base,state):
            result=run_rows(rows(2),Path(d)/'out.jsonl',make_config(base,'cpu-http-target'))
            self.assertEqual(len(state['requests']),2)
            self.assertEqual(result['0']['prediction'],'')
            self.assertEqual(result['0']['generation']['finish_reason'],'length')
            self.assertEqual(result['0']['generation']['reasoning_content'],'reasoning only')
            self.assertEqual(result['1']['generation']['refusal'],'blocked')
            self.assertEqual(result['0']['api_status'],'ok')
            self.assertEqual(result['0']['generation']['usage'],{'prompt_tokens':5,'completion_tokens':3,'total_tokens':8})

    def test_preflight_model_inventory_and_probe_denominator(self):
        with server() as (base,state):
            config=make_config(base,'cpu-http-target')
            evidence=preflight(config,rows(3))
            self.assertEqual(evidence['expected_rows'],3)
            self.assertFalse(evidence['probe_in_benchmark'])
            self.assertEqual(evidence['model_inventory_check'],'listed_by_server')
            self.assertEqual(evidence['parameter_effect'],'unverified')
            with self.assertRaisesRegex(ValueError,'absent from server'):
                preflight(make_config(base,'missing'),rows(3))
            self.assertEqual(len(state['requests']),1)
        with server(models=None) as (base,state):
            self.assertEqual(preflight(make_config(base,'cpu-http-target'))['model_inventory_check'],'not_available')

    def test_cli_utf8_paths_under_legacy_windows_pipe_encoding(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'한국어-로봇-🤖';root.mkdir()
            dataset_fixture(root/'data')
            env=dict(os.environ);env['PYTHONIOENCODING']='cp949'
            result=subprocess.run([sys.executable,'-m','koevd_eval.pipeline','--stage','prepare',
                                   '--dataset-dir',str(root/'data'),'--output-dir',str(root/'run')],
                                  env=env,capture_output=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stderr.decode('utf-8',errors='replace'))
            self.assertIn('한국어-로봇-🤖',result.stdout.decode('utf-8'))

    def test_hard_process_exit_releases_lock_and_preserves_attempt(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'result.jsonl'
            script="""import os,sys
from pathlib import Path
from unittest.mock import patch
from koevd_eval.run_openai_compatible import run_rows,make_config
count=0
def call(*args,**kwargs):
    global count
    count+=1
    if count==2:os._exit(73)
    return 'checkpointed'
rows=[{'sample_id':str(i),'messages':[{'role':'user','content':str(i)}],'gold':{'label':'unsafe'},'metadata':{'secret_gold':'never_send'}} for i in range(3)]
with patch('koevd_eval.run_openai_compatible.call_api',side_effect=call):
    run_rows(rows,Path(sys.argv[1]),make_config('http://unused/v1','cpu-http-target'))
"""
            child=subprocess.run([sys.executable,'-c',script,str(out)],capture_output=True,timeout=20)
            self.assertEqual(child.returncode,73,child.stderr.decode(errors='replace'))
            journal=list(read_jsonl(out.with_suffix('.jsonl.progress.jsonl')))
            self.assertEqual(journal[-1]['event'],'attempt_started')
            with patch('koevd_eval.run_openai_compatible.call_api',return_value='resumed') as api:
                saved=run_rows(rows(3),out,make_config('http://unused/v1','cpu-http-target'),resume=True)
                self.assertEqual(api.call_count,2)
            self.assertEqual(saved['0']['prediction'],'checkpointed')
            self.assertEqual(saved['1']['generation']['attempts'][0]['status'],'interrupted_unknown')

    def test_changed_preserved_input_fields_and_extra_settings_fail_resume(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'result.jsonl';config=make_config('http://unused/v1','cpu-http-target')
            with patch('koevd_eval.run_openai_compatible.call_api',return_value='ok'):
                run_rows(rows(1),out,config)
            saved=list(read_jsonl(out));saved[0]['messages'][0]['content']='changed-but-old-hash'
            write_jsonl(out,saved)
            with self.assertRaisesRegex(ValueError,'same input rows'):
                run_rows(rows(1),out,config,resume=True)
            with self.assertRaisesRegex(ValueError,'configuration changed'):
                run_rows(rows(1),out,{**config,'extra_body':{'seed':3}},resume=True)

    def test_pipeline_export_carries_metadata_and_stable_run_identity(self):
        with tempfile.TemporaryDirectory() as d,server() as (base,state):
            root=Path(d);dataset_fixture(root/'data');out=root/'run'
            manifest=prepare_run(root/'data',out);index=build_index(out)
            generate_run(out,manifest,base_url=base,model='cpu-http-target',workers=2,preflight=True,
                         extra_body={'seed':7,'top_p':.9},engine_version='SYNTHETIC-ENGINE',
                         model_provenance={'revision':'declared-test-revision','dtype':'declared-fp16'})
            first=export_run(out,index);second=export_run(out,index)
            self.assertEqual(first['run']['id'],second['run']['id'])
            self.assertEqual(first['run']['id'],manifest['generation_run']['id'])
            self.assertEqual(first['run']['generation']['seed'],7)
            self.assertEqual(first['run']['generation']['extra_body'],{'seed':7,'top_p':.9})
            self.assertEqual(first['run']['model']['revision'],'declared-test-revision')
            self.assertEqual(first['run']['model']['verification'],'user_reported')
            response=first['records'][0]['response']
            self.assertEqual(response['response_id'],'response-fixture')
            self.assertEqual(response['usage']['total_tokens'],8)
            self.assertEqual(response['execution']['parameter_status'],'requested_unverified')
            self.assertEqual(response['execution']['attempts'][0]['client_controls']['workers'],2)
            validate_results(first,index)
            from importlib.resources import files
            if importlib.util.find_spec('jsonschema'):
                from jsonschema import Draft202012Validator
                Draft202012Validator(json.loads(files('koevd_eval').joinpath('schemas/results-v1.schema.json').read_text())).validate(first)
            validate_execution(response['execution'],'ok')
            altered=deepcopy(response['execution']);altered['selected_attempt_id']='fabricated'
            with self.assertRaisesRegex(ValueError,'Selected response'):validate_execution(altered,'ok')
            self.assertEqual(len(state['requests']),11)  # 10 expected generation rows + separate probe
            self.assertEqual(len(first['records']),12)


if __name__=='__main__':unittest.main()
