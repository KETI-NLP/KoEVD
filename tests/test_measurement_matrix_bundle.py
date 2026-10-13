"""CPU archive/frozen-data fixtures; no actual classifier or GPU inference."""
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
import importlib.util
from io import BytesIO, StringIO
import json
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zipfile

import test_gpu_results_intake as baseline_fixture
import test_measurement_trace as trace_fixture
from koevd_eval.classify_responses import apply_classifier
from koevd_eval.common import read_jsonl, write_jsonl
from koevd_eval.measurement_audit import compare_measurements
from koevd_eval.pipeline import save_json
from koevd_eval.results import export_run, read_document, _seal
from koevd_eval.measurement_trace import VERSION, write_trace


class MeasurementMatrixBundleTests(unittest.TestCase):
    def setUp(self):
        self.fixture = baseline_fixture.GPUResultsIntakeTests()
        self.fixture.setUp(); self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        path = Path(__file__).resolve().parents[1]/'scripts/measurement_matrix_bundle.py'
        spec = importlib.util.spec_from_file_location('matrix_bundle_test', path)
        self.module = importlib.util.module_from_spec(spec); spec.loader.exec_module(self.module)
        self.matrix = self.root/'matrix'
        self.names = ('CPU-FIXTURE-A', 'CPU-FIXTURE-B')
        self.index = self.fixture.index
        targets, commands = [], []
        for name in self.names:
            run = self.root/name/'run'
            manifest = read_document(run/'pipeline.json')
            self.measure(run, manifest)
            original = export_run(run, self.index)
            save_json(self.root/name/'results.json', original)
            folder = self.matrix/name/'untraced-b2'
            shutil.copytree(run, folder/'run')
            result = export_run(folder/'run', self.index)
            save_json(folder/'results.json', result)
            summary = {'variant_id': 'untraced-b2', 'artifact_sha256': result['content_sha256'],
                'comparison': compare_measurements(original, result, self.index, variant_id='untraced-b2'),
                'trace_observations': {}, 'status': 'passed_frozen_measurement_export_compare'}
            save_json(folder/'comparison.json', summary)
            targets.append({'model': name, 'revision': original['run']['model']['revision'],
                'baseline_artifact_sha256': original['content_sha256'],
                'frozen_file_sha256': self.module.frozen(run), 'comparisons': [summary]})
            commands.append({'name': name+'-untraced-b2', 'status': 'passed', 'exit_code': 0,
                'argv': ['CPU-FIXTURE-only', '--stage', 'classify', '--batch-size', '2',
                    '--classifier-dtype', 'bfloat16', '--measurement-order', 'original', '--measurement-mode', 'batch']})
        self.state = {'scope': 'two_actual_target_frozen_response_measurement_matrix',
            'status': 'passed_frozen_measurement_matrix', 'variants': ['untraced-b2'],
            'controller_sha256': 'c'*64, 'commands': commands, 'targets': targets}
        (self.matrix/'checks').mkdir()
        save_json(self.matrix/'checks/status.json', self.state)
        self.index_path = self.root/'independent-index.json'; save_json(self.index_path, self.index)
        self.archive = self.root/'matrix.zip'

    def measure(self, run, manifest):
        for task in (3, 4):
            rows = list(read_jsonl(run/'task3_predictions.jsonl'))
            for row in rows:
                row['measurement'] = ({'label': 'safe', 'raw_output': 'safe'} if task == 3
                    else {'strategies': ['c_reasoning'], 'is_unsafe': False, 'raw_output': 'c_reasoning'})
            output = run/f'task{task}_measured.jsonl'; write_jsonl(output, rows)
            manifest.setdefault('measurements', {})[str(task)] = {
                'prediction_sha256': hashlib.sha256((run/'task3_predictions.jsonl').read_bytes()).hexdigest(),
                'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                'batch_size': 2, 'adapter': {'fixture.json': 'a'*64}, 'base': {'fixture.json': 'b'*64},
                'requested_dtype': 'bfloat16', 'input_order': 'original', 'inference_mode': 'batch'}
        save_json(run/'pipeline.json', manifest)

    def verify(self, **kwargs):
        return self.module.verify_matrix(self.matrix, self.root, self.index,
                                        required_variants=['untraced-b2'], **kwargs)

    def pack(self):
        return self.module.pack(self.matrix, self.archive)

    def accept(self, checksum, output, variants=True):
        argv = ['matrix-bundle', 'accept', '--zip', str(self.archive), '--expected-sha256', checksum,
            '--baseline', str(self.root), '--trusted-index', str(self.index_path), '--output', str(output)]
        if variants: argv += ['--required-variant', 'untraced-b2']
        with patch.object(sys, 'argv', argv), redirect_stdout(StringIO()): self.module.main()

    def test_explicit_subset_roundtrip_never_claims_full_matrix_or_accuracy(self):
        receipt = self.verify()
        self.assertEqual(len(receipt['comparisons']), 2)
        self.assertFalse(receipt['full_seven_variant_matrix'])
        self.assertFalse(receipt['classifier_accuracy_verified'])
        packed = self.pack(); dest = self.root/'accepted'
        self.accept(packed['sha256'], dest)
        receipt = read_document(dest/'intake-receipt.json')
        self.assertTrue(receipt['independent_reexport_and_comparison_exact'])
        with self.assertRaises(FileExistsError): self.accept(packed['sha256'], dest)
        failed = self.root/'full-required'
        with self.assertRaisesRegex(ValueError, 'required variant'): self.accept(packed['sha256'], failed, variants=False)
        self.assertFalse((failed/'intake-receipt.json').exists())

    def test_changed_frozen_output_rejected_even_with_recomputed_result(self):
        run = self.matrix/self.names[0]/'untraced-b2/run'
        rows = list(read_jsonl(run/'task1_predictions.jsonl')); rows[0]['prediction'] = 'unsafe'
        write_jsonl(run/'task1_predictions.jsonl', rows)
        with self.assertRaisesRegex(ValueError, 'Frozen input/prediction'): self.verify()

    def test_forged_comparison_does_not_override_independent_calculation(self):
        folder = self.matrix/self.names[0]/'untraced-b2'
        comparison = read_document(folder/'comparison.json')
        comparison['comparison']['tasks']['3']['counts']['semantic_changes'] = 900
        save_json(folder/'comparison.json', comparison)
        with self.assertRaisesRegex(ValueError, 'independent recomputation'): self.verify()

    def test_execution_variants_missing_failures_and_false_trace_claims_rejected(self):
        for mode in ('failed', 'missing', 'dtype'):
            state = deepcopy(self.state)
            if mode == 'failed': state['commands'][0]['exit_code'] = 1
            if mode == 'missing': state['commands'].pop()
            if mode == 'dtype': state['commands'][0]['argv'][6] = 'float32'
            save_json(self.matrix/'checks/status.json', state)
            with self.subTest(mode=mode), self.assertRaises(ValueError): self.verify()
        save_json(self.matrix/'checks/status.json', self.state)
        save_json(self.matrix/self.names[0]/'untraced-b2/run/task3_measurement_trace.json', {})
        with self.assertRaisesRegex(ValueError, 'Untraced variant'): self.verify()

    def test_pack_requires_terminal_status_and_does_not_overwrite(self):
        self.pack()
        with self.assertRaises(FileExistsError): self.pack()
        self.state['status'] = 'running'; save_json(self.matrix/'checks/status.json', self.state)
        with self.assertRaisesRegex(ValueError, 'terminal'): self.module.pack(self.matrix, self.root/'running.zip')
        self.assertFalse((self.root/'running.zip').exists())

    def test_archive_limits_paths_hashes_and_case_collisions(self):
        packed = self.pack(); raw = self.archive.read_bytes()
        with self.assertRaisesRegex(ValueError, 'external checksum'): self.module.verify_envelope(raw, '0'*64)
        with patch.object(self.module, 'MAX_TOTAL', 16), self.assertRaisesRegex(ValueError, 'size'):
            self.module.verify_envelope(raw, packed['sha256'])
        for name in ('../outside.json', 'matrix/COM1.json', 'matrix/trailing.', 'intake-receipt.json',
                     'MATRIX/checks/status.json', 'matrix/extra.py'):
            with zipfile.ZipFile(BytesIO(raw)) as source:
                files = {n: source.read(n) for n in source.namelist()}
            manifest = json.loads(files['bundle-manifest.json'])
            files[name] = b'{}'; manifest['files'][name] = {'bytes': 2, 'sha256': hashlib.sha256(b'{}').hexdigest()}
            files['bundle-manifest.json'] = json.dumps(manifest).encode()
            stream = BytesIO()
            with zipfile.ZipFile(stream, 'w') as archive:
                for n, value in files.items(): archive.writestr(n, value)
            changed = stream.getvalue()
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.module.verify_envelope(changed, hashlib.sha256(changed).hexdigest())

    def test_single_verified_byte_snapshot_survives_source_path_change(self):
        packed = self.pack(); original = self.module.paths.read_snapshot
        def replaced(path):
            value = original(path); self.archive.write_bytes(b'replaced after snapshot'); return value
        with patch.object(self.module.paths, 'read_snapshot', side_effect=replaced):
            self.accept(packed['sha256'], self.root/'snapshot')
        self.assertTrue((self.root/'snapshot/intake-receipt.json').exists())

    def test_archive_index_cannot_replace_outside_operator_inputs(self):
        packed = self.pack()
        other = deepcopy(self.index)
        other['inputs']['1'][next(iter(other['inputs']['1']))]['row']['messages'][0]['content'] = 'other input'
        save_json(self.index_path, _seal({k: v for k, v in other.items() if k != 'content_sha256'}))
        dest = self.root/'wrong-index'
        with self.assertRaises(ValueError): self.accept(packed['sha256'], dest)
        self.assertFalse((dest/'intake-receipt.json').exists())

    def test_fp32_presence_does_not_certify_mixed_parameters_as_full_fp32(self):
        observed = self.module.dtype_realization('float32', {'torch.bfloat16': 752393024, 'torch.float32': 6389760})
        self.assertFalse(observed['fp32_request_fully_realized_in_parameters'])
        self.assertEqual(observed['caveat'], 'requested_fp32_not_fully_realized')
        uniform = self.module.dtype_realization('float32', {'torch.float32': 8234382336})
        self.assertTrue(uniform['fp32_request_fully_realized_in_parameters'])
        self.assertIsNone(uniform['caveat'])
        self.assertIn('kernel arithmetic', uniform['interpretation'])

    def test_cpu_tensor_traces_are_independently_bound_and_observed_dtype_is_checked(self):
        variant = 'traced-repeat-b2'
        state = deepcopy(self.state); state['variants'] = [variant]
        for number, name in enumerate(self.names):
            folder = self.matrix/name/variant
            shutil.copytree(self.root/name/'run', folder/'run')
            run = folder/'run'; manifest = read_document(run/'pipeline.json')
            observations = {}
            for task in (3, 4):
                classifier = trace_fixture.Classifier()
                classifier.model.named_parameters = lambda: iter([
                    ('CPU-TENSOR-FIXTURE', SimpleNamespace(dtype='torch.bfloat16', numel=lambda: 8))])
                if task == 4:
                    classifier.tokenizer.decode = lambda tokens, **kw: 'c_reasoning'
                    original_predict = classifier.predict_batch
                    def strategy(messages, original_predict=original_predict):
                        values = original_predict(messages)
                        return [{'result': {'strategies': ['c_reasoning'], 'is_unsafe': False,
                                            'raw_output': 'c_reasoning'}} for _ in values]
                    classifier.predict_batch = strategy
                trace = {'format': VERSION, 'task': task, 'batch_size': 2, 'input_order': 'original',
                    'inference_mode': 'batch', 'requested_dtype': 'bfloat16', 'requested_max_new_tokens': None,
                    'finished': True}
                input_path = run/'task3_predictions.jsonl'; output = run/f'task{task}_measured.jsonl'
                measured = apply_classifier(list(read_jsonl(input_path)), classifier, batch_size=2,
                    trace=trace, formatter=trace_fixture.formatter)
                write_jsonl(output, measured)
                trace.update(input_file_sha256=hashlib.sha256(input_path.read_bytes()).hexdigest(),
                             output_file_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
                trace_path = run/f'task{task}_measurement_trace.json'; saved = write_trace(trace_path, trace)
                trace_sha = hashlib.sha256(trace_path.read_bytes()).hexdigest()
                manifest['measurements'][str(task)].update(output_sha256=trace['output_file_sha256'],
                    trace_sha256=trace_sha, requested_max_new_tokens=None)
                observations[str(task)] = {'parameter_dtype_elements': saved['runtime']['parameter_dtype_elements'],
                    'observed_call_order': saved['observed_call_order'], 'trace_file_sha256': trace_sha}
            save_json(run/'pipeline.json', manifest)
            result = export_run(run, self.index); save_json(folder/'results.json', result)
            summary = {'variant_id': variant, 'artifact_sha256': result['content_sha256'],
                'comparison': compare_measurements(read_document(self.root/name/'results.json'), result,
                                                  self.index, variant_id=variant),
                'trace_observations': observations, 'status': 'passed_frozen_measurement_export_compare'}
            save_json(folder/'comparison.json', summary); state['targets'][number]['comparisons'] = [summary]
            state['commands'][number]['name'] = name+'-'+variant
            state['commands'][number]['argv'].append('--trace-measurements')
        save_json(self.matrix/'checks/status.json', state)
        receipt = self.module.verify_matrix(self.matrix, self.root, self.index, required_variants=[variant])
        self.assertTrue(receipt['independent_reexport_and_comparison_exact'])
        self.assertFalse(receipt['classifier_accuracy_verified'])
        for comparison in receipt['comparisons']:
            self.assertEqual(comparison['trace_observations']['3']['parameter_dtype_elements'], {'torch.bfloat16': 8})
        # Internally re-seal changed observation to test semantic binding, not just ZIP hashing.
        run = self.matrix/self.names[0]/variant/'run'
        trace_path = run/'task3_measurement_trace.json'; changed = read_document(trace_path)
        changed['runtime']['parameter_dtype_elements'] = {'CPU-WRONG-DTYPE': 8}
        save_json(trace_path, _seal({k: v for k, v in changed.items() if k != 'content_sha256'}))
        manifest = read_document(run/'pipeline.json')
        manifest['measurements']['3']['trace_sha256'] = hashlib.sha256(trace_path.read_bytes()).hexdigest()
        save_json(run/'pipeline.json', manifest)
        save_json(run.parent/'results.json', export_run(run, self.index))
        with self.assertRaisesRegex(ValueError, 'parameter dtype'):
            self.module.verify_matrix(self.matrix, self.root, self.index, required_variants=[variant])


if __name__ == '__main__': unittest.main()
