"""GPU selection/full-index CPU boundaries only; no model execution evidence."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class GPUSelectorTests(unittest.TestCase):
    def setUp(self):
        source=Path(__file__).resolve().parents[1]/'scripts/validate_gpu_pipeline.py'
        spec=importlib.util.spec_from_file_location('gpu_pipeline_controller',source)
        self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)

    def test_uuid_selects_current_integer_without_assuming_initial_index(self):
        self.assertEqual(self.module.resolve_gpu_index('0, GPU-other\n2, GPU-requested\n','GPU-requested'),'2')
        self.assertEqual(self.module.resolve_gpu_index('5, GPU-requested\n1, GPU-other\n','GPU-requested'),'5')

    def test_missing_duplicate_and_noninteger_gpu_selection_rejected(self):
        for rows in ('0, GPU-other\n','0, GPU-requested\n1, GPU-requested\n','-1, GPU-requested\n','x, GPU-requested\n'):
            with self.subTest(rows=rows),self.assertRaises(ValueError):
                self.module.resolve_gpu_index(rows,'GPU-requested')

    def test_full_selection_is_explicit_and_mutually_exclusive(self):
        for extra in ([],['--sources','4','--full-core']):
            result=subprocess.run([sys.executable,str(Path(self.module.__file__)),'--root','DOES_NOT_EXIST',
                '--gpu-uuid','GPU-CPU-ONLY',*extra],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertNotIn('Traceback',result.stderr)
        for values in ({},{'sources':4,'full_core':True},{'sources':5}):
            with self.assertRaises(ValueError):self.module.preparation_steps(Path('bin'),Path('source'),{},'data','run','index',**values)

    def test_real_full_preparation_cli_registers_only_independently_checked_inputs(self):
        from koevd_eval.pipeline import prepare_run,save_json
        from koevd_eval.protocols import preparation_identity,input_set_identity
        from koevd_eval.results import build_index,read_document,_seal
        from test_own_model_pipeline import dataset_fixture
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);data=root/'data';dataset_fixture(data)
            reference=root/'reference';manifest=prepare_run(data,reference)
            definition=read_document('configs/protocols/koevd-core-canonical-v1.json')
            definition.update(id='SYNTHETIC-FULL-CPU-CHECK',
                dataset={'repo':'SYNTHETIC/fixture','revision':'a'*40,'files':manifest['preparation']['dataset_files']},
                expected_inputs=input_set_identity(build_index(reference)),preparation_sha256=preparation_identity())
            definition=_seal({k:v for k,v in definition.items() if k!='content_sha256'})
            registry=root/'configs/protocols';registry.mkdir(parents=True);save_json(registry/'fixture.json',definition)
            lock={'protocol_id':definition['id'],'protocol_sha256':definition['content_sha256'],
                  'release_artifacts':{'dataset':{'repo_id':'SYNTHETIC/fixture','revision':'a'*40}}}
            run=root/'actual-cli-run';index=root/'full-index.json'
            env={**os.environ,'PYTHONUTF8':'1'};env.pop('PYTHONPATH',None)
            # Console programs must be present in the tested noneditable installation.
            for command in self.module.preparation_steps(Path(sys.executable).parent,root,lock,data,run,index,full_core=True):
                result=subprocess.run([str(v) for v in command],capture_output=True,text=True,encoding='utf-8',env=env)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            registered=read_document(index)
            self.assertEqual(self.module.validate_full_index(registered,root,lock),{'1':1,'2':4,'3':2,'4':2,'5':3})
            self.assertEqual(registered['protocol']['kind'],'standard')
            self.assertIsNone(read_document(run/'pipeline.json')['preparation']['limit_sources'])
            with self.assertRaisesRegex(ValueError,'GPU lock'):
                self.module.validate_full_index(registered,root,{**lock,'protocol_sha256':'0'*64})
            custom=build_index(run)
            with self.assertRaisesRegex(ValueError,'registered pinned'):
                self.module.validate_full_index(custom,root,lock)
            changed=deepcopy(registered)
            changed['inputs']['1'][next(iter(changed['inputs']['1']))]['row']['gold']['label']='unsafe'
            changed=_seal({k:v for k,v in changed.items() if k!='content_sha256'})
            with self.assertRaises(ValueError):self.module.validate_full_index(changed,root,lock)


if __name__=='__main__':unittest.main()
