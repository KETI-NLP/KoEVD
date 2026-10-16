from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from koevd_eval.classify_responses import apply_classifier
from koevd_eval.common import write_jsonl
from koevd_eval.measurement_trace import (VERSION, hash_value, file_hash,
    observe_generate, single_reference_tokens, token_rows, write_trace, validate_trace)
from koevd_eval.results import canonical_hash


class Tensor:
    def __init__(self,rows): self.rows=deepcopy(rows)
    def detach(self): return self
    def cpu(self): return self
    def tolist(self): return deepcopy(self.rows)
    def to(self,device): return self
    @property
    def shape(self): return (len(self.rows),len(self.rows[0]))
    def __getitem__(self,key):
        if isinstance(key,tuple): return self.rows[key[0]][key[1]]
        return self.rows[key]


class Tokenizer:
    padding_side='right'
    model_max_length=128
    def apply_chat_template(self,messages,**kwargs):
        return Tensor([[1,len(messages[0]['content']),2]])
    def decode(self,tokens,skip_special_tokens=True): return 'safe'


class Model:
    def __init__(self):
        self.config=SimpleNamespace(max_position_embeddings=32)
        self.calls=[]
    def named_parameters(self):
        yield 'fixture',SimpleNamespace(dtype='FAKE.float32',numel=lambda:8)
    def generate(self,**kwargs):
        self.calls.append(kwargs)
        return Tensor([row+[7,9,9] for row in kwargs['input_ids'].tolist()])


class Classifier:
    def __init__(self): self.model=Model();self.tokenizer=Tokenizer()
    def load(self): return self
    def predict_batch(self,messages):
        tokens=[[0,1,len(formatter(m)),2] for m in messages]
        self.model.generate(input_ids=Tensor(tokens),attention_mask=Tensor([[0,1,1,1] for _ in tokens]),
            max_new_tokens=3,do_sample=False,pad_token_id=9,eos_token_id=9)
        return [{'result':{'label':'safe','raw_output':'safe'}} for _ in messages]
    def predict(self,messages):
        self.model.generate(input_ids=self.tokenizer.apply_chat_template([{'content':formatter(messages)}]),
            max_new_tokens=3,do_sample=False,pad_token_id=9,eos_token_id=9)
        return {'result':{'label':'safe','raw_output':'safe'}}


def formatter(messages): return '|'.join(m['content'] for m in messages)


def rows():
    return [{'sample_id':str(n),'messages':[{'role':'user','content':'question '+str(n)}],
             'prediction':'answer '+str(n),'api_status':'ok' if n!=1 else 'error'} for n in range(4)]


class MeasurementTraceTests(unittest.TestCase):
    def test_masked_tokens_hashes_and_legacy_canonical_binding(self):
        self.assertEqual(token_rows(Tensor([[9,1,2]]),Tensor([[0,1,1]])),[[1,2]])
        self.assertEqual(token_rows(Tensor([[9,1,2]]),Tensor([[False,True,True]])),[[1,2]])
        self.assertEqual(hash_value([1,2]),canonical_hash([1,2]))
        for mask in ([[1]],[[0,1,2]]):
            with self.assertRaises(ValueError): token_rows(Tensor([[9,1,2]]),Tensor(mask))

    def test_observes_once_without_changing_args_output_or_restored_method(self):
        model=Model();tokenizer=Tokenizer();captured=[]
        ids,mask=Tensor([[0,1,3,2]]),Tensor([[0,1,1,1]])
        with observe_generate(model,tokenizer,[[1,3,2]],['abc'],captured):
            result=model.generate(input_ids=ids,attention_mask=mask,max_new_tokens=3,
                                  do_sample=False,pad_token_id=9,eos_token_id=9)
        self.assertEqual(result.tolist(),[[0,1,3,2,7,9,9]])
        self.assertIs(model.calls[0]['input_ids'],ids)
        self.assertIs(model.calls[0]['attention_mask'],mask)
        self.assertEqual(len(model.calls),1)
        self.assertNotIn('generate',vars(model))
        t=captured[0]
        self.assertEqual(t['input_token_count'],3)
        self.assertEqual(t['padding_token_count'],1)
        self.assertTrue(t['single_template_tokens_equal'])
        self.assertEqual(t['generated_suffix_token_count_with_padding'],3)
        self.assertEqual(t['generated_tokens_through_first_eos'],2)
        self.assertEqual(t['first_eos_index'],1)
        self.assertFalse(t['reached_token_budget_without_eos'])

    def test_detects_tokenization_parity_difference_and_context_limit(self):
        model=Model();model.config.max_position_embeddings=2;captured=[]
        with observe_generate(model,Tokenizer(),[[1,2]],['p'],captured):
            model.generate(input_ids=Tensor([[1,3,2]]),max_new_tokens=3,eos_token_id=100)
        self.assertFalse(captured[0]['single_template_tokens_equal'])
        self.assertTrue(captured[0]['exceeds_declared_model_context'])
        self.assertTrue(captured[0]['reached_token_budget_without_eos'])

    def test_reverse_processing_preserves_original_output_and_records_actual_order(self):
        data=rows();original=deepcopy(data);classifier=Classifier();trace={}
        result=apply_classifier(data,classifier,batch_size=2,order='reverse',trace=trace,formatter=formatter)
        self.assertEqual(data,original)
        self.assertEqual([r['sample_id'] for r in result],['0','1','2','3'])
        self.assertEqual(trace['observed_call_order'],[[3,2],[0]])
        self.assertTrue(trace['completed'])
        self.assertEqual(trace['records'][1]['classification_status'],'not_applicable')
        self.assertIsNone(trace['records'][1]['observed_generate'])
        self.assertIsNone(result[1]['measurement'])
        self.assertEqual(trace['runtime']['parameter_dtype_elements'],{'FAKE.float32':8})
        self.assertEqual(trace['records'][3]['batch_slot'],0)
        self.assertEqual(trace['records'][2]['batch_slot'],1)

    def test_single_path_and_untraced_path_keep_results_without_new_payload_fields(self):
        data=rows();baseline=apply_classifier(data,Classifier(),batch_size=2)
        trace={}
        measured=apply_classifier(data,Classifier(),batch_size=2,inference_mode='single',trace=trace,formatter=formatter)
        self.assertEqual(measured,baseline)
        self.assertEqual(trace['observed_call_order'],[[0],[2],[3]])
        self.assertTrue(all(r['observed_generate']['single_template_tokens_equal']
            for r in trace['records'] if r['classification_status']=='reported'))
        self.assertNotIn('observed_generate',measured[0])

    def test_generation_failure_restores_method_and_retains_incomplete_observation(self):
        classifier=Classifier()
        def fails(**kwargs): raise RuntimeError('synthetic failure')
        classifier.model.generate=fails
        trace={}
        with self.assertRaisesRegex(RuntimeError,'synthetic failure'):
            apply_classifier(rows(),classifier,trace=trace,formatter=formatter)
        self.assertIs(classifier.model.generate,fails)
        self.assertFalse(trace['completed'])
        self.assertEqual(trace['error_type'],'RuntimeError')
        self.assertFalse(trace['records'][0]['observed_generate']['generation_returned'])

    def test_parser_failure_keeps_raw_outputs_and_no_success_claim(self):
        class ParseFailure(Classifier):
            def predict_batch(self,messages):
                super().predict_batch(messages)
                raise ValueError('synthetic parse failure')
        classifier=ParseFailure();trace={}
        with self.assertRaises(ValueError): apply_classifier(rows(),classifier,trace=trace,formatter=formatter)
        self.assertFalse(trace['completed'])
        self.assertEqual(trace['records'][0]['observed_generate']['raw_output'],'safe')
        self.assertEqual(trace['records'][0]['classification_status'],'pending')
        self.assertNotIn('generate',vars(classifier.model))

    def test_sidecar_no_replace_binding_and_stale_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);input_path=root/'in.jsonl';output_path=root/'out.jsonl'
            data=rows();write_jsonl(input_path,data);trace={'format':VERSION,'task':3,'batch_size':8,'input_order':'original','inference_mode':'batch','finished':True}
            measured=apply_classifier(data,Classifier(),trace=trace,formatter=formatter)
            write_jsonl(output_path,measured)
            trace.update(input_file_sha256=file_hash(input_path),output_file_sha256=file_hash(output_path))
            saved=write_trace(root/'trace.json',trace)
            self.assertEqual(validate_trace(saved,input_path,output_path,3),saved)
            with self.assertRaises(ValueError): write_trace(root/'trace.json',trace)
            self.assertFalse(list(root.glob('*.tmp-*')))
            measured[0]['measurement']={'label':'unsafe'};write_jsonl(output_path,measured)
            with self.assertRaisesRegex(ValueError,'stale'): validate_trace(saved,input_path,output_path,3)

    def test_actual_released_wrappers_with_fake_tensors_preserve_batch_single_results(self):
        from contextlib import nullcontext
        from unittest.mock import patch
        from koevd_classifiers.assistant_safe_classifier import AssistantSafeClassifier,format_openai_messages as safety_format
        from koevd_classifiers.response_strategy_classifier import StrategyClassifier,format_openai_messages as strategy_format
        class WrapperTokenizer(Tokenizer):
            pad_token_id=eos_token_id=9
            def __init__(self,text):self.text=text
            def apply_chat_template(self,messages,tokenize=True,**kwargs):
                prompt=messages[0]['content']
                return Tensor([[1,len(prompt),2]]) if tokenize else prompt
            def __call__(self,prompts,**kwargs):
                return {'input_ids':Tensor([[0,1,len(p),2] for p in prompts]),
                        'attention_mask':Tensor([[0,1,1,1] for _ in prompts])}
            def decode(self,tokens,**kwargs):return self.text
        fake_torch=SimpleNamespace(inference_mode=nullcontext,cuda=SimpleNamespace(is_available=lambda:False))
        for cls,format_fn,text in [(AssistantSafeClassifier,safety_format,'safe'),(StrategyClassifier,strategy_format,'c_reasoning')]:
            classifier=cls(adapter_path='SYNTHETIC-NO-WEIGHTS',base_model_name_or_path='SYNTHETIC-NO-BASE')
            classifier.model=Model();classifier.model.device='cpu';classifier.tokenizer=WrapperTokenizer(text)
            with patch.dict('sys.modules',{'torch':fake_torch}):
                baseline=apply_classifier(rows(),classifier,batch_size=2)
                trace={}
                measured=apply_classifier(rows(),classifier,batch_size=2,trace=trace,formatter=format_fn)
                single_trace={}
                singles=apply_classifier(rows(),classifier,inference_mode='single',trace=single_trace,formatter=format_fn)
            self.assertEqual(baseline,measured)
            self.assertEqual(baseline,singles)
            self.assertTrue(all(r['observed_generate']['single_template_tokens_equal']
                for r in trace['records'] if r['classification_status']=='reported'))
            self.assertNotIn('generate',vars(classifier.model))

    def test_resealed_order_or_raw_mismatch_is_rejected(self):
        from koevd_eval.results import _seal
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);a=root/'a.jsonl';b=root/'b.jsonl';data=rows();write_jsonl(a,data)
            trace={'format':VERSION,'task':3,'batch_size':8,'input_order':'original','inference_mode':'batch','finished':True}
            measured=apply_classifier(data,Classifier(),trace=trace,formatter=formatter);write_jsonl(b,measured)
            trace.update(input_file_sha256=file_hash(a),output_file_sha256=file_hash(b))
            wrong=deepcopy(trace);wrong['observed_call_order']=[[3,2,0]]
            with self.assertRaisesRegex(ValueError,'order differs'):validate_trace(_seal(wrong),a,b,3)
            wrong=deepcopy(trace);wrong['records'][0]['observed_generate']['raw_output']='unsafe'
            with self.assertRaisesRegex(ValueError,'raw output differs'):validate_trace(_seal(wrong),a,b,3)

    def test_empty_and_failed_rows_never_load_classifier(self):
        class NoLoad(Classifier):
            def load(self): raise AssertionError('must not load')
        data=rows();trace={}
        for r in data:r.update(prediction='',api_status='error')
        output=apply_classifier(data,NoLoad(),trace=trace,formatter=formatter)
        self.assertTrue(trace['completed']);self.assertIsNone(trace['runtime'])
        self.assertEqual(trace['observed_call_order'],[])
        self.assertTrue(all(r['measurement'] is None for r in output))


class TraceExportTests(unittest.TestCase):
    def setUp(self):
        import test_results
        from koevd_eval.common import read_jsonl
        from koevd_eval.measurement_trace import write_trace
        fixture=test_results.ResultContractTests('test_roundtrip_preserves_union_variants_failures_unknowns_and_privacy')
        fixture.setUp();self.addCleanup(fixture.temp.cleanup)
        self.fixture=fixture
        self.input=fixture.run/'task3_predictions.jsonl'
        data=list(read_jsonl(self.input))
        self.manifest=deepcopy(fixture.manifest)
        self.manifest['measurements']={}
        for task in (3,4):
            classifier=Classifier()
            if task==4:
                classifier.tokenizer.decode=lambda tokens,**kw:'c_reasoning'
                original=classifier.predict_batch
                def strategies(messages,original=original):
                    values=original(messages)
                    for v in values:v['result']={'strategies':['c_reasoning'],'raw_output':'c_reasoning'}
                    return values
                classifier.predict_batch=strategies
            trace={'format':VERSION,'task':task,'finished':True,'batch_size':2,
                   'inference_mode':'batch','input_order':'original'}
            measured=apply_classifier(data,classifier,batch_size=2,trace=trace,formatter=formatter)
            output=fixture.run/f'task{task}_measured.jsonl';write_jsonl(output,measured)
            trace.update(input_file_sha256=file_hash(self.input),output_file_sha256=file_hash(output))
            trace_path=fixture.run/f'task{task}_measurement_trace.json';write_trace(trace_path,trace)
            self.manifest['measurements'][str(task)]={'prediction_sha256':file_hash(self.input),
                'output_sha256':file_hash(output),'trace_sha256':file_hash(trace_path),'batch_size':2,
                'adapter':{'SYNTHETIC-config.json':'a'*64},'base':{'SYNTHETIC-weights.bin':'b'*64}}
        self.save_manifest()

    def save_manifest(self):
        (self.fixture.run/'pipeline.json').write_text(json.dumps(self.manifest)+'\n',encoding='utf-8')

    def test_export_checks_trace_and_reports_dtype_without_truncation_accuracy_claim(self):
        from koevd_eval.results import export_run,validate_results
        document=export_run(self.fixture.run,self.fixture.index)
        validate_results(document,self.fixture.index)
        for task in ('3','4'):
            evidence=document['run']['measurements'][task]
            self.assertEqual(evidence['precision'],'reported_parameter_dtypes:FAKE.float32')
            self.assertIsNone(evidence['input_truncation'])
            self.assertEqual(evidence['accuracy_status'],'measurement_limited')
            self.assertEqual(evidence['verification'],'user_reported')

    def test_pipeline_propagates_trace_controls_and_records_each_sidecar(self):
        from unittest.mock import patch
        from koevd_eval.common import read_jsonl
        from koevd_eval.pipeline import classify_run
        from koevd_eval.results import export_run
        root=self.fixture.run.resolve()
        for task in (3,4):
            for name in (f'task{task}_measured.jsonl',f'task{task}_measurement_trace.json'):
                path=(root/name).resolve()
                self.assertTrue(path.is_relative_to(root));path.unlink()
        artifacts=[]
        for n in range(4):
            path=root/f'SYNTHETIC-artifact-{n}';path.mkdir()
            (path/'config.json').write_text('{}',encoding='utf-8')
            (path/'fake.safetensors').write_bytes(b'SYNTHETIC-NO-WEIGHTS')
            artifacts.append(path)
        def fake_process(command,check):
            self.assertTrue(check)
            value=lambda option:command[command.index(option)+1]
            self.assertEqual(value('--torch-dtype'),'float32')
            self.assertEqual(value('--input-order'),'reverse')
            self.assertEqual(value('--inference-mode'),'single')
            task=int(value('--task'));data=list(read_jsonl(value('--input')))
            cl=Classifier()
            if task==4:
                cl.tokenizer.decode=lambda tokens,**kw:'c_reasoning'
                original=cl.predict
                def strategy_predict(messages):
                    original(messages)
                    return {'result':{'strategies':['c_reasoning'],'raw_output':'c_reasoning'}}
                cl.predict=strategy_predict
            trace={'format':VERSION,'task':task,'finished':True,'batch_size':2,
                   'input_order':'reverse','inference_mode':'single'}
            measured=apply_classifier(data,cl,batch_size=2,order='reverse',inference_mode='single',trace=trace,formatter=formatter)
            write_jsonl(value('--output'),measured)
            trace.update(input_file_sha256=file_hash(value('--input')),output_file_sha256=file_hash(value('--output')))
            write_trace(value('--trace-output'),trace)
        manifest=deepcopy(self.fixture.manifest)
        manifest['measurements']={}
        with patch('koevd_eval.pipeline.subprocess.run',side_effect=fake_process):
            classify_run(root,manifest,*artifacts,batch_size=2,classifier_dtype='float32',
                         input_order='reverse',inference_mode='single',trace_measurements=True)
        with patch('koevd_eval.pipeline.subprocess.run',side_effect=AssertionError('completed traces must be reused')):
            classify_run(root,manifest,*artifacts,batch_size=2,classifier_dtype='float32',
                         input_order='reverse',inference_mode='single',trace_measurements=True)
        old_trace=file_hash(root/'task4_measurement_trace.json')
        with patch('koevd_eval.pipeline.subprocess.run',side_effect=fake_process):
            classify_run(root,manifest,*artifacts,batch_size=2,classifier_dtype='float32',
                         input_order='reverse',inference_mode='single',trace_measurements=True,
                         measurement_tasks=(4,),remeasure=True)
        previous=root/manifest['measurements']['4']['attempt']/'previous-task4_measurement_trace.json'
        self.assertEqual(file_hash(previous),old_trace)
        document=export_run(root,self.fixture.index)
        for task in ('3','4'):
            self.assertEqual(manifest['measurements'][task]['input_order'],'reverse')
            self.assertEqual(manifest['measurements'][task]['inference_mode'],'single')
            self.assertEqual(manifest['measurements'][task]['trace_sha256'],file_hash(root/f'task{task}_measurement_trace.json'))
            self.assertEqual(document['run']['measurements'][task]['verification'],'user_reported')

    def test_export_rejects_trace_tamper_even_after_updating_manifest_checksum(self):
        from koevd_eval.results import export_run,_seal
        path=self.fixture.run/'task3_measurement_trace.json'
        trace=json.loads(path.read_text(encoding='utf-8'))
        trace['records'][0]['observed_generate']['raw_output']='unsafe'
        trace=_seal({k:v for k,v in trace.items() if k!='content_sha256'})
        path.write_text(json.dumps(trace)+'\n',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'trace checksum'):export_run(self.fixture.run,self.fixture.index)
        self.manifest['measurements']['3']['trace_sha256']=file_hash(path);self.save_manifest()
        with self.assertRaisesRegex(ValueError,'raw output differs'):export_run(self.fixture.run,self.fixture.index)


class TraceCLITests(unittest.TestCase):
    def test_new_cli_flags_and_failure_sidecar_do_not_claim_success(self):
        from unittest.mock import patch
        from koevd_eval.classify_responses import main
        class Stub(Classifier):
            kwargs=None
            def __init__(self,**kwargs):super().__init__();Stub.kwargs=kwargs
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);adapter=root/'adapter';adapter.mkdir()
            (adapter/'adapter_config.json').write_text('{}',encoding='utf-8')
            input_path=root/'input.jsonl';write_jsonl(input_path,rows())
            output_path=root/'output.jsonl';trace_path=root/'trace.json'
            args=['koevd-classify','--task','3','--input',str(input_path),'--output',str(output_path),
                  '--adapter-path',str(adapter),'--batch-size','2','--input-order','reverse',
                  '--torch-dtype','float32','--inference-mode','single','--trace-output',str(trace_path)]
            with patch('sys.argv',args),patch('koevd_classifiers.assistant_safe_classifier.AssistantSafeClassifier',Stub):main()
            trace=json.loads(trace_path.read_text(encoding='utf-8'))
            validate_trace(trace,input_path,output_path,3)
            self.assertEqual(Stub.kwargs['torch_dtype'],'float32')
            self.assertEqual(trace['observed_call_order'],[[3],[2],[0]])
            self.assertTrue(trace['finished'])
            class Fails(Stub):
                def predict(self,messages):
                    super().predict(messages)
                    raise ValueError('synthetic parse failure')
            failed=root/'failed.json';failed_output=root/'failed.jsonl'
            args[args.index(str(trace_path))]=str(failed)
            args[args.index(str(output_path))]=str(failed_output)
            with patch('sys.argv',args),patch('koevd_classifiers.assistant_safe_classifier.AssistantSafeClassifier',Fails):
                with self.assertRaises(ValueError):main()
            incomplete=json.loads(failed.read_text(encoding='utf-8'))
            self.assertFalse(incomplete['completed']);self.assertFalse(incomplete['finished'])
            self.assertFalse(failed_output.exists())
            self.assertIsNone(incomplete['output_file_sha256'])


if __name__=='__main__': unittest.main()
