"""CPU archive/input-boundary tests; these fixtures never prove GPU inference."""
from contextlib import redirect_stdout
from copy import deepcopy
import hashlib
import importlib.util
from io import StringIO
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid
import zipfile

from koevd_eval.common import read_jsonl, write_jsonl
from koevd_eval.pipeline import prepare_run, save_json
from koevd_eval.results import build_index, export_run, _seal
from test_own_model_pipeline import dataset_fixture

spec = importlib.util.spec_from_file_location('gpu_results_intake_test',
    Path(__file__).resolve().parents[1] / 'scripts' / 'accept_gpu_results_bundle.py')
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False) + '\n').encode('utf-8')


class GPUResultsIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        dataset_fixture(self.root / 'data')
        self.files, targets, commands = {}, [], []
        for name in ('CPU-FIXTURE-A', 'CPU-FIXTURE-B'):
            run = self.root / name / 'run'
            manifest = prepare_run(self.root / 'data', run)
            manifest['generation'] = {'model': name, 'temperature': 0., 'max_tokens': 32,
                'model_provenance': {'revision': 'synthetic-revision'}}
            manifest['generation_run'] = {'id': str(uuid.uuid4()), 'created_at': '2026-10-08T00:00:00+00:00'}
            generation = {}
            for task in (1, 2, 3, 5):
                rows = list(read_jsonl(run / f'task{task}_input.jsonl'))
                for row in rows:
                    row.update(evaluated_model=name, api_status='ok',
                        prediction={1: 'safe', 2: 'A', 3: 'CPU fixture response',
                                    5: '{"decision":"refuse"}'}[task],
                        run_config=manifest['generation'], api_error=None)
                prediction = run / f'task{task}_predictions.jsonl'
                write_jsonl(prediction, rows)
                generation[str(task)] = {'expected': len(rows), 'actual': len(rows),
                    'api_failures': 0, 'prediction_sha256': hashlib.sha256(prediction.read_bytes()).hexdigest()}
            save_json(run / 'pipeline.json', manifest)
            self.index = build_index(run)
            document = export_run(run, self.index)
            self.files[f'smoke/{name}/results.json'] = encoded(document)
            for p in run.rglob('*'):
                if p.is_file():
                    self.files[f'smoke/{name}/run/{p.relative_to(run).as_posix()}'] = p.read_bytes()
            targets.append({'model': name, 'revision': 'synthetic-revision', 'generation': generation})
            commands.extend({'name': name + '-' + stage, 'status': 'passed', 'exit_code': 0}
                for stage in ('prepare', 'index', 'generate', 'measure', 'export', 'diagnose'))
        commands.append({'name': 'two-target-comparison', 'status': 'passed', 'exit_code': 0})
        self.state_path = 'smoke/checks/status.json'
        self.state = {'status': 'passed_generation_measurement_export_report_comparison',
                      'targets': targets, 'commands': commands}
        self.files[self.state_path] = encoded(self.state)
        self.zip = self.root / 'return.zip'
        self.index_path = self.root / 'independently-prepared-index.json'
        save_json(self.index_path, self.index)

    def archive(self, files=None, extras=(), manifest_change=None):
        files = self.files if files is None else files
        manifest = {'format': intake.FORMAT, 'files': {name: {'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()} for name, raw in files.items()}}
        if manifest_change:
            manifest_change(manifest)
        with zipfile.ZipFile(self.zip, 'w') as archive:
            archive.writestr('bundle-manifest.json', encoded(manifest))
            for name, raw in files.items():
                archive.writestr(name, raw)
            for name, raw in extras:
                archive.writestr(name, raw)
        return hashlib.sha256(self.zip.read_bytes()).hexdigest()

    def accept(self, checksum, output, *, registry=None,protocol_id=None):
        argv = ['accept_gpu_results_bundle', '--zip', str(self.zip), '--expected-sha256', checksum,
                '--trusted-index', str(self.index_path), '--output', str(output)]
        if registry is not None:argv.extend(['--registry',str(registry),'--protocol-id',protocol_id])
        with patch.object(sys, 'argv', argv), redirect_stdout(StringIO()):
            intake.main()

    def test_independent_reexport_and_fresh_destination(self):
        checksum = self.archive()
        _, receipt = intake.verify_bundle(self.zip, checksum, self.index)
        self.assertEqual(len(receipt['targets']), 2)
        self.assertFalse(receipt['cryptographic_generation_authenticity'])
        output = self.root / 'accepted'
        self.accept(checksum, output)
        receipt = json.loads((output / 'intake-receipt.json').read_text())
        self.assertTrue(all(t['independent_reexport_exact_match'] for t in receipt['targets']))
        with self.assertRaises(FileExistsError):
            self.accept(checksum, output)

    def test_external_and_internal_checksums_are_separate_boundaries(self):
        checksum = self.archive()
        with self.assertRaisesRegex(ValueError, 'External archive'):
            intake.verify_bundle(self.zip, '0' * 64, self.index)
        checksum = self.archive(manifest_change=lambda m: m['files'][self.state_path].update(sha256='0' * 64))
        with self.assertRaisesRegex(ValueError, 'Manifest file checksum'):
            intake.verify_bundle(self.zip, checksum, self.index)

    def test_paths_case_collisions_symlinks_and_size_limits(self):
        for name in ('../outside', '/outside', 'C:/outside', 'x\\outside', 'x//outside',
                     'aux.txt', 'folder/COM1.log', 'folder/trailing.', 'folder/line\n'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                intake.safe_name(name)
        checksum = self.archive(extras=[('SMOKE/CHECKS/STATUS.JSON', b'{}')])
        with self.assertRaisesRegex(ValueError, 'case-colliding'):
            intake.verify_bundle(self.zip, checksum, self.index)
        link = zipfile.ZipInfo('unsafe-link')
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        checksum = self.archive(extras=[(link, b'../outside')])
        with self.assertRaisesRegex(ValueError, 'Unsupported archive'):
            intake.verify_bundle(self.zip, checksum, self.index)
        checksum = self.archive()
        with patch.object(intake, 'MAX_TOTAL', 16), self.assertRaisesRegex(ValueError, 'limit'):
            intake.verify_bundle(self.zip, checksum, self.index)

    def test_missing_stage_failure_and_archived_index_cannot_replace_operator(self):
        for mode in ('missing', 'failed'):
            state = deepcopy(self.state)
            if mode == 'missing':
                state['commands'].pop(0)
            else:
                state['commands'][0].update(status='failed', exit_code=1)
            checksum = self.archive({**self.files, self.state_path: encoded(state)})
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'stage'):
                intake.verify_bundle(self.zip, checksum, self.index)
        altered = deepcopy(self.index)
        altered['inputs']['1'][next(iter(altered['inputs']['1']))]['row']['messages'][0]['content'] = 'other input'
        altered = _seal({k: v for k, v in altered.items() if k != 'content_sha256'})
        checksum = self.archive({**self.files, 'smoke/claimed-trusted-index.json': encoded(self.index)})
        with self.assertRaises(ValueError):
            intake.verify_bundle(self.zip, checksum, altered)

    def test_failed_generation_cannot_be_reported_as_complete(self):
        files = dict(self.files)
        prediction = 'smoke/CPU-FIXTURE-A/run/task1_predictions.jsonl'
        rows = [json.loads(line) for line in files[prediction].splitlines()]
        rows[0]['api_status'] = 'error'
        files[prediction] = b''.join(encoded(row) for row in rows)
        state = deepcopy(self.state)
        state['targets'][0]['generation']['1']['prediction_sha256'] = hashlib.sha256(files[prediction]).hexdigest()
        files[self.state_path] = encoded(state)
        checksum = self.archive(files)
        with self.assertRaisesRegex(ValueError, 'generation coverage'):
            intake.verify_bundle(self.zip, checksum, self.index)

    def test_returned_response_must_equal_reexport_no_receipt_on_failure(self):
        files = dict(self.files)
        prediction = 'smoke/CPU-FIXTURE-A/run/task1_predictions.jsonl'
        rows = [json.loads(line) for line in files[prediction].splitlines()]
        rows[0]['prediction'] = 'unsafe'
        files[prediction] = b''.join(encoded(row) for row in rows)
        state = deepcopy(self.state)
        state['targets'][0]['generation']['1']['prediction_sha256'] = hashlib.sha256(files[prediction]).hexdigest()
        files[self.state_path] = encoded(state)
        checksum = self.archive(files)
        output = self.root / 'partial-failure'
        with self.assertRaisesRegex(ValueError, 're-export differs'):
            self.accept(checksum, output)
        self.assertTrue(output.exists())
        self.assertFalse((output / 'intake-receipt.json').exists())

    def test_verified_snapshot_is_used_after_source_path_changes(self):
        checksum = self.archive()
        original = intake.read_snapshot
        def replaced_after_read(path):
            raw = original(path)
            self.zip.write_bytes(b'changed after bounded snapshot')
            return raw
        output = self.root / 'snapshot-intake'
        with patch.object(intake, 'read_snapshot', side_effect=replaced_after_read):
            self.accept(checksum, output)
        self.assertTrue((output / 'intake-receipt.json').exists())

    def test_full_claim_requires_outside_registry(self):
        state=deepcopy(self.state);state.update(full_core_requested=True)
        checksum=self.archive({**self.files,self.state_path:encoded(state)})
        with self.assertRaisesRegex(ValueError,'outside pinned registry'):
            intake.verify_bundle(self.zip,checksum,self.index)

    def test_registered_full_inputs_and_scope_then_independent_reexport(self):
        from koevd_eval.protocols import ProtocolRegistry,preparation_identity,input_set_identity
        from koevd_eval.results import read_document
        definition=read_document('configs/protocols/koevd-core-canonical-v1.json')
        manifest=read_document(self.root/'CPU-FIXTURE-A/run/pipeline.json')
        definition.update(id='SYNTHETIC-FULL-INTAKE',
            dataset={'repo':'SYNTHETIC/fixture','revision':'a'*40,'files':manifest['preparation']['dataset_files']},
            expected_inputs=input_set_identity(self.index),preparation_sha256=preparation_identity())
        definition=_seal({k:v for k,v in definition.items() if k!='content_sha256'})
        registry_dir=self.root/'outside-registry';registry_dir.mkdir();save_json(registry_dir/'fixture.json',definition)
        registry=ProtocolRegistry(registry_dir)
        index=registry.prepare_index(definition['id'],self.root/'data',self.root/'outside-full-prepared')
        save_json(self.index_path,index)
        files=dict(self.files)
        for name in ('CPU-FIXTURE-A','CPU-FIXTURE-B'):
            files[f'smoke/{name}/results.json']=encoded(export_run(self.root/name/'run',index))
        state=deepcopy(self.state);state.update(scope='two_actual_targets_registered_full_core_pipeline',
            full_core_requested=True,registered_full_inputs_validated=True,sources_per_prefix=None,
            full_input_counts={task:len(rows) for task,rows in index['inputs'].items()},
            protocol_id=definition['id'],protocol_sha256=definition['content_sha256'])
        files[self.state_path]=encoded(state);checksum=self.archive(files)
        _,receipt=intake.verify_bundle(self.zip,checksum,index,registry=registry,protocol_id=definition['id'])
        self.assertTrue(receipt['full_standard_inputs_verified']);self.assertFalse(receipt['classifier_accuracy_verified'])
        output=self.root/'accepted-full';self.accept(checksum,output,registry=registry_dir,protocol_id=definition['id'])
        self.assertTrue(all(v['independent_reexport_exact_match'] for v in read_document(output/'intake-receipt.json')['targets']))
        for change in ({'full_input_counts':{'1':4}},{'protocol_sha256':'0'*64},{'registered_full_inputs_validated':False},
                       {'scope':'two_actual_targets_custom_prefix_pipeline'},{'sources_per_prefix':96}):
            bad={**state,**change};checksum=self.archive({**files,self.state_path:encoded(bad)})
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,'execution scope'):
                intake.verify_bundle(self.zip,checksum,index,registry=registry,protocol_id=definition['id'])


if __name__ == '__main__':
    unittest.main()
