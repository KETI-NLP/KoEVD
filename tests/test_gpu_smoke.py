"""CPU orchestration checks; these do not exercise actual GPU inference."""
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

script=Path(__file__).resolve().parents[1]/'scripts/gpu_smoke.py'
spec=importlib.util.spec_from_file_location('gpu_smoke',script)
smoke=importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)

class GPUSmokeOrchestrationTests(unittest.TestCase):
    def test_floating_revisions_rejected(self):
        lock={k:{'repo_id':'org/repo','revision':'a'*40} for k in ('dataset','assistant','strategy','assistant_base','strategy_base')}
        smoke.validate_lock(lock)
        lock['strategy']['revision']='main'
        with self.assertRaises(ValueError): smoke.validate_lock(lock)

    def test_case_selection_is_source_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            corpus=Path(tmp)/'corpus.jsonl'
            rows=[{'source_id':str(i),'user_utterance':{'content':'hello'},'responses':{t:[{'response_id':str(i)+t,'content':'reply'}] for t in ('accepted','rejected')}} for i in range(2)]
            corpus.write_text('\n'.join(json.dumps(row) for row in rows),encoding='utf-8')
            cases=smoke.select_cases(corpus,1)
            self.assertEqual(len(cases),2)
            self.assertEqual({r['source_id'] for r in cases},{'0'})

    def test_manifest_corruption_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); data=root/'data.txt'; data.write_text('correct')
            (root/'manifest.json').write_text(json.dumps({'files':[{'path':'data.txt','sha256':smoke.sha256(data)}]}))
            self.assertEqual(smoke.verify_manifest(root),1)
            data.write_text('changed')
            with self.assertRaises(ValueError): smoke.verify_manifest(root)

    def test_both_metric_denominators_with_fake_classifiers(self):
        fake_torch=SimpleNamespace(cuda=SimpleNamespace(reset_peak_memory_stats=lambda:None,max_memory_allocated=lambda:0,empty_cache=lambda:None))
        class FakeClassifier:
            def __init__(self,**kwargs): self.model=SimpleNamespace(parameters=lambda:[])
            def load(self): return self
            def predict(self,messages): return {'result':{'label':'safe','strategies':['c_reasoning']}}
            def predict_batch(self,messages): return [self.predict(m) for m in messages]
        cases=[{'sample_id':str(i),'source_id':str(i),'tier':'accepted','messages':[],'prediction':'reply'} for i in range(2)]
        with tempfile.TemporaryDirectory() as tmp, patch.dict('sys.modules',{'torch':fake_torch}), patch('koevd_classifiers.assistant_safe_classifier.AssistantSafeClassifier',FakeClassifier), patch('koevd_classifiers.response_strategy_classifier.StrategyClassifier',FakeClassifier):
            for kind in ('assistant','strategy'):
                result=smoke.measure(kind,Path(tmp),Path(tmp),cases,SimpleNamespace(dtype='bfloat16',batch_size=2),Path(tmp))
                self.assertEqual(result['status'],'passed')
                self.assertTrue(result['denominator_check'])

if __name__=='__main__': unittest.main()
