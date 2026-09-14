"""Analytical invariants and HTTP integration; classifiers below are CPU doubles."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from koevd_eval.common import read_jsonl, write_jsonl
from koevd_eval.pipeline import (prepare_run, generate_run, classify_run, report_run,
                                verify_predictions, save_json, TASK2_VARIANTS, TASK5_VARIANTS)
from koevd_eval.profile import make_profile, write_report
from koevd_eval.run_openai_compatible import run_rows


def row(sid, task=3, *, model='own-model', topic='A', prediction='reply', label='safe'):
    return {'sample_id': f'{sid}:task{task}', 'source_id': sid, 'task': f'task{task}',
            'evaluated_model': model, 'metadata': {'source_id': sid, 'topic': [topic, topic], 'severity_band': 'High'},
            'messages': [{'role':'user','content':sid}], 'gold': {'label':'unsafe'},
            'prediction':prediction,'api_status':'ok','measurement': {'label': label}}


class ProfileTests(unittest.TestCase):
    def test_missing_is_not_strength_and_topics_are_distinct(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'t3.jsonl'
            write_jsonl(p,[row('a',prediction=''),row('b',topic='B',label='unsafe')])
            report,_=make_profile({3:[p]},min_sources=1)
            m=report['models']['own-model']; s=m['tasks']['3']['overall']
            self.assertEqual((s['rows'],s['valid'],s['events']),(2,1,1))
            self.assertEqual(s['event_rate_on_all'],.5)
            self.assertEqual(m['signals'],[])
            groups=[g for g in m['tasks']['3']['groups'] if g['axis']=='topic']
            self.assertEqual([g['rows'] for g in groups],[1,1])

    def test_unique_source_threshold_and_same_variant_contrasts(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'t2.jsonl'; rows=[]
            for i in range(25):
                for sid,topic,answer in [('a','A','B'),('b','B','A')]:
                    r=row(sid,2,topic=topic,prediction=answer); r['sample_id']+=str(i)
                    r['gold']={'answer':'A'}; r['metadata'].update(choices=[{'letter':'A'},{'letter':'B'}],task_variant='choose_best')
                    rows.append(r)
            write_jsonl(p,rows)
            report,_=make_profile({2:[p]})
            self.assertEqual(report['models']['own-model']['signals'],[])

    def test_model_comparison_excludes_different_prompts(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'all.jsonl'; a=row('a'); b=row('a',model='other'); b['messages']=[{'role':'user','content':'different'}]
            write_jsonl(p,[a,b]); report,_=make_profile({3:[p]})
            self.assertEqual(report['comparisons'][0]['matched_identical_inputs'],0)
            self.assertEqual(report['comparisons'][0]['shared_ids_with_different_inputs'],1)

    def test_partial_task5_and_failed_import_are_not_safe_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'t5.jsonl'; a=row('a',5,prediction='{"safety_label":"safe"}')
            a['gold']={'available_tools':['x'],'unsafe_tools':['x']}; a['metadata']['prompt_variant']='safe_guided'
            b=row('b',5,prediction='{"decision":"call_tool","tool_name":"x"}')
            b['gold']=a['gold']; b['api_status']='error'; b['metadata']['prompt_variant']='safe_guided'
            write_jsonl(p,[a,b]); report,_=make_profile({5:[p]})
            s=report['models']['own-model']['tasks']['5']['overall']
            self.assertEqual(s['valid'],0); self.assertIsNone(s['event_rate_on_valid'])
            self.assertEqual(s['metrics']['parsed'],1)

    def test_html_escapes_outputs_and_reports_all_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'t3.jsonl'; write_jsonl(p,[row('a',model='<script>alert(1)</script>')])
            out=Path(d)/'report'; write_report({3:[p]},out)
            self.assertEqual({f.name for f in out.iterdir()},{'profile.json','report.md','report.html','groups.csv','strategies.csv','cases.jsonl'})
            self.assertNotIn('<script>alert(1)</script>',(out/'report.html').read_text(encoding='utf-8'))


def dataset_fixture(root):
    corpus=[]
    for sid in ('core-a','tool-b'):
        corpus.append({'source_id':sid,'user_utterance':{'content':'hello '+sid,'labels':{'severity_band':'Benign','topic':['test'],'explicitness':'Explicit','utterance_type':'Question'},'rationales':{}}})
    write_jsonl(root/'full_eval/koevd_full_eval.jsonl',corpus)
    write_jsonl(root/'benchmark_splits/core.jsonl',[{'source_id':'core-a'}])
    for v in TASK2_VARIANTS:
        r=row('core-a',2); r['sample_id']+=':'+v; r['metadata'].update(choices=[{'letter':'A'},{'letter':'B'}],task_variant=v)
        r['gold']={'answer':'A'}; r['messages']=[{'role':'user','content':'choose an answer'}]
        for k in ('prediction','api_status','measurement','evaluated_model'): r.pop(k)
        write_jsonl(root/'tasks/task2_candidate_response_safety_choice/full_eval'/f'{v}.jsonl',[r])
    for v in TASK5_VARIANTS:
        r=row('tool-b',5); r['sample_id']+=':'+v; r['metadata']['prompt_variant']=v
        r['gold']={'available_tools':['mock_bad'],'unsafe_tools':['mock_bad'],'allowed_tools':[], 'expected_decision':'refuse','gold_unsafe_tool_call':True}
        r['messages']=[{'role':'user','content':'select a mock tool'}]
        for k in ('prediction','api_status','measurement','evaluated_model'): r.pop(k)
        write_jsonl(root/'tasks/task5_tool_action_choice_safety/main'/f'{v}.jsonl',[r])


class PipelineIntegrationTests(unittest.TestCase):
    def test_interrupted_generation_reuses_journal_without_duplicate_requests(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'predictions.jsonl'
            rows=[{'sample_id':str(i),'messages':[]} for i in range(3)]
            config={'endpoint':'http://unused','model':'m','temperature':0,'max_tokens':8}
            with patch('koevd_eval.run_openai_compatible.call_api',side_effect=['first',KeyboardInterrupt]):
                with self.assertRaises(KeyboardInterrupt): run_rows(rows,out,config)
            journal=out.with_suffix('.jsonl.progress.jsonl')
            with journal.open('a',encoding='utf-8') as f:f.write('{"truncated":')
            with patch('koevd_eval.run_openai_compatible.call_api',return_value='remaining') as api:
                run_rows(rows,out,config,resume=True)
                self.assertEqual(api.call_count,2)
            saved=list(read_jsonl(out)); self.assertEqual(len(saved),3)
            self.assertEqual(saved[0]['prediction'],'first'); self.assertFalse(journal.exists())

    def test_prepare_preserves_framing_and_union_and_blocks_stale_data(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); dataset_fixture(root/'data')
            out=root/'run'; m=prepare_run(root/'data',out)
            self.assertEqual([m['inputs'][str(t)]['rows'] for t in (1,2,3,5)],[1,4,2,3])
            self.assertEqual(m,prepare_run(root/'data',out))
            rows=list(read_jsonl(out/'task3_input.jsonl'))
            self.assertEqual({r['metadata']['source_id'] for r in rows},{'core-a','tool-b'})
            self.assertEqual(rows[1]['metadata']['evaluation_subset'],['task5_overlap'])
            with self.assertRaises(ValueError): prepare_run(root/'data',out,limit_sources=1)

    def test_http_generation_classify_glue_report_and_resume(self):
        requests=[]
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body=json.loads(self.rfile.read(int(self.headers['Content-Length']))); requests.append(body)
                self.server.test.assertEqual(set(body),{'model','messages','temperature','max_tokens'})
                text=body['messages'][-1]['content']
                answer='A' if 'choose an answer' in text else ('{"decision":"refuse"}' if 'mock tool' in text else ('safe' if 'exactly one label' in text else 'A helpful reply'))
                data=json.dumps({'choices':[{'message':{'content':answer}}]}).encode()
                self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(data)
            def log_message(self,*args): pass
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler); server.test=self
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d); dataset_fixture(root/'data'); out=root/'run'; m=prepare_run(root/'data',out)
                options={'base_url':f'http://127.0.0.1:{server.server_port}/v1','model':'own-model','retries':0}
                generate_run(out,m,**options); self.assertEqual(len(requests),10)
                generate_run(out,m,**options); self.assertEqual(len(requests),10)
                artifact=root/'artifact'; artifact.mkdir()
                (artifact/'adapter_config.json').write_text('{}'); (artifact/'model.safetensors').write_bytes(b'CPU test fixture, not a model')
                def classify_subprocess(command,check):
                    from koevd_eval.classify_responses import main
                    class Fake:
                        def __init__(self,**kwargs): pass
                        def predict_batch(self,messages): return [{'result':{'label':'safe','strategies':['c_info providing']}} for _ in messages]
                    with patch('sys.argv',command[2:]), patch('koevd_classifiers.assistant_safe_classifier.AssistantSafeClassifier',Fake), patch('koevd_classifiers.response_strategy_classifier.StrategyClassifier',Fake): main()
                with patch('koevd_eval.pipeline.subprocess.run',side_effect=classify_subprocess):
                    classify_run(out,m,artifact,artifact,artifact,artifact)
                report=report_run(out,m)
                self.assertEqual(report['models']['own-model']['task3_task5']['matched_rows'],3)
                self.assertEqual(report['models']['own-model']['tasks']['2']['overall']['event_rate_on_valid'],0)
                # An altered generation invalidates classifier results, even with the same IDs.
                rows=list(read_jsonl(out/'task3_predictions.jsonl')); rows[0]['prediction']='changed'; write_jsonl(out/'task3_predictions.jsonl',rows)
                with self.assertRaisesRegex(ValueError,'stale'): report_run(out,m)
                rows.pop(); write_jsonl(out/'task3_predictions.jsonl',rows)
                with self.assertRaisesRegex(ValueError,'missing/extra'): verify_predictions(out,m,3)
        finally:
            server.shutdown(); server.server_close(); thread.join()


if __name__=='__main__': unittest.main()
