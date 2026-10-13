"""Private minimal replay-builder CPU checks; all target outputs are fixtures."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
import zipfile

import test_gpu_results_intake as fixtures

spec=importlib.util.spec_from_file_location('return_builder',Path(__file__).resolve().parents[1]/'scripts/build_gpu_results_bundle.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)


class PrivateReturnBuilderTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.GPUResultsIntakeTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        for name,raw in self.fixture.files.items():
            path=self.fixture.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        self.root=self.fixture.root/'smoke'

    def test_allowlisted_raw_replay_and_receiver_reexport(self):
        (self.root/'.env').write_text('CPU fixture excluded private file')
        (self.root/'claimed-index.json').write_text('Uploader-controlled index must stay outside')
        extra=self.root/'CPU-FIXTURE-A/analysis';extra.mkdir();(extra/'report-v2.html').write_text('Excluded duplicate report')
        output=self.fixture.root/'private-replay.zip';receipt=builder.pack(self.root,output,self.fixture.index)
        self.assertEqual(receipt['files'],21);self.assertFalse(receipt['reports_included']);self.assertFalse(receipt['published'])
        with zipfile.ZipFile(output) as archive:
            names=archive.namelist();self.assertFalse(any(n.endswith(('.env','.html','claimed-index.json')) for n in names))
            self.assertEqual(archive.read('smoke/CPU-FIXTURE-A/run/task3_predictions.jsonl'),self.fixture.files['smoke/CPU-FIXTURE-A/run/task3_predictions.jsonl'])
        self.fixture.zip=output;accepted=self.fixture.root/'independently-reexported'
        self.fixture.accept(receipt['sha256'],accepted)
        self.assertTrue(all(t['independent_reexport_exact_match'] for t in json.loads((accepted/'intake-receipt.json').read_text())['targets']))
        with self.assertRaises(ValueError):builder.pack(self.root,output,self.fixture.index)

    def test_running_or_oversized_returns_are_not_completed(self):
        state=self.root/'checks/status.json';original=state.read_bytes()
        state.write_text(json.dumps({**self.fixture.state,'status':'running'}))
        output=self.fixture.root/'not-complete.zip'
        with self.assertRaisesRegex(ValueError,'terminal'):builder.pack(self.root,output,self.fixture.index)
        self.assertFalse(output.exists());state.write_bytes(original)
        with patch.object(builder.intake,'MAX_TOTAL',16),self.assertRaisesRegex(ValueError,'limits'):
            builder.pack(self.root,output,self.fixture.index)
        self.assertFalse(output.exists())

    def test_missing_measurement_file_rejects_without_inventing_labels(self):
        manifest_path=self.root/'CPU-FIXTURE-A/run/pipeline.json';manifest=json.loads(manifest_path.read_text())
        manifest['measurements']={'3':{'trace_sha256':'0'*64}};manifest_path.write_text(json.dumps(manifest))
        output=self.fixture.root/'missing-measurement.zip'
        with self.assertRaisesRegex(ValueError,'Missing'):builder.pack(self.root,output,self.fixture.index)
        self.assertFalse(output.exists())


if __name__=='__main__':unittest.main()
