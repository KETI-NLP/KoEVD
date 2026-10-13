"""CPU clone/config boundary fixtures; no classifier/GPU execution."""
import importlib.util
import json
from pathlib import Path
import unittest

import test_results as result_fixture
from koevd_eval.results import read_document
from koevd_eval.common import read_jsonl, write_jsonl


class FrozenMeasurementControllerTests(unittest.TestCase):
    def setUp(self):
        self.fixture=result_fixture.ResultContractTests();self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        script=Path(__file__).resolve().parents[1]/'scripts/validate_frozen_measurements.py'
        spec=importlib.util.spec_from_file_location('frozen_measurement_controller_test',script)
        self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)

    def test_clone_keeps_every_input_prediction_and_declaration_without_old_measurements(self):
        source=self.fixture.run;original=read_document(source/'pipeline.json')
        original['measurements']={'3':{'SYNTHETIC':'old measurement not a GPU trace'}}
        (source/'pipeline.json').write_text(json.dumps(original),encoding='utf-8')
        (source/'task3_measured.jsonl').write_text('SYNTHETIC old output',encoding='utf-8')
        (source/'task3_measurement_trace.json').write_text('{}',encoding='utf-8')
        before={p.name:p.read_bytes() for p in source.iterdir() if p.is_file()}
        dest=self.fixture.root/'clone'
        frozen=self.module.clone_generation(source,dest)
        self.assertEqual(self.module.frozen_files(source),frozen)
        self.assertEqual(self.module.frozen_files(dest),frozen)
        self.assertEqual(len(frozen),8)
        self.assertFalse((dest/'task3_measured.jsonl').exists())
        self.assertFalse((dest/'task3_measurement_trace.json').exists())
        copied=read_document(dest/'pipeline.json');self.assertEqual(copied['measurements'],{})
        self.assertEqual({k:v for k,v in copied.items() if k!='measurements'},
                         {k:v for k,v in original.items() if k!='measurements'})
        self.assertEqual(before,{p.name:p.read_bytes() for p in source.iterdir() if p.is_file()})
        with self.assertRaises(FileExistsError):self.module.clone_generation(source,dest)

    def test_invalid_prepared_input_and_missing_prediction_never_create_accepted_clone(self):
        source=self.fixture.run;dest=self.fixture.root/'bad-clone'
        rows=list(read_jsonl(source/'task3_predictions.jsonl'))
        rows[0]['messages'][0]['content']='changed input'
        write_jsonl(source/'task3_predictions.jsonl',rows)
        with self.assertRaises(ValueError):self.module.clone_generation(source,dest)
        self.assertFalse(dest.exists())
        (source/'task1_predictions.jsonl').unlink()
        with self.assertRaisesRegex(ValueError,'Missing regular frozen'):
            self.module.frozen_files(source)

    def test_variants_preserve_adapter_paths_and_target_never_generated(self):
        artifacts={k:{'snapshot':'/SYNTHETIC/'+k} for k in ('assistant','assistant_base','strategy','strategy_base')}
        for name,settings in self.module.VARIANTS.items():
            with self.subTest(name=name):
                args=self.module.classifier_command('/SYNTHETIC/root','/SYNTHETIC/clone',artifacts,name)
                def option(key):return args[args.index(key)+1]
                self.assertEqual(option('--stage'),'classify')
                self.assertEqual(option('--safety-adapter'),artifacts['assistant']['snapshot'])
                self.assertEqual(option('--strategy-base'),artifacts['strategy_base']['snapshot'])
                self.assertEqual((int(option('--batch-size')),option('--measurement-order'),
                                  option('--measurement-mode'),option('--classifier-dtype')),settings[:-1])
                self.assertEqual('--trace-measurements' in args,settings[-1])
                self.assertNotIn('--model',args)

    def test_gpu_uuid_missing_ambiguous_or_noninteger_is_rejected(self):
        self.assertEqual(self.module.gpu_index('1, GPU-other\n3, GPU-required\n','GPU-required'),'3')
        for text in ('1, GPU-other','1, GPU-required\n2, GPU-required','-1, GPU-required'):
            with self.subTest(text=text),self.assertRaises(ValueError):
                self.module.gpu_index(text,'GPU-required')


if __name__=='__main__':unittest.main()
