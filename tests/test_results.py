from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from koevd_eval.common import read_jsonl, write_jsonl
from koevd_eval.pipeline import prepare_run, save_json, file_sha
from koevd_eval.results import (build_index, export_run, validate_results, report_results,
                                canonical_hash, read_document, _seal)
from koevd_eval.profile import make_profile
from test_own_model_pipeline import dataset_fixture


class ResultContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        dataset_fixture(self.root / 'data')
        self.run = self.root / 'run'
        self.manifest = prepare_run(self.root / 'data', self.run)
        self.manifest['generation'] = {'model': 'cpu-fixture', 'endpoint': 'http://internal-secret-endpoint',
                                       'temperature': 0., 'max_tokens': 32}
        for task in (1, 2, 3, 5):
            rows = list(read_jsonl(self.run / f'task{task}_input.jsonl'))
            for i, row in enumerate(rows):
                text = {1: 'safe', 2: 'A', 3: 'fixture response', 5: '{"decision":"refuse"}'}[task]
                row.update(evaluated_model='cpu-fixture', api_status='ok', prediction=text,
                           run_config=self.manifest['generation'], api_error=None)
                if task == 3 and i == 1:
                    row.update(api_status='error', prediction='', api_error='secret C:/private/path')
            write_jsonl(self.run / f'task{task}_predictions.jsonl', rows)
        save_json(self.run / 'pipeline.json', self.manifest)
        self.index = build_index(self.run)
        self.document = export_run(self.run, self.index)

    def test_roundtrip_preserves_union_variants_failures_unknowns_and_privacy(self):
        rows = validate_results(self.document, self.index)
        self.assertEqual([len(rows[t]) for t in range(1, 6)], [1, 4, 2, 2, 3])
        self.assertEqual(rows[3][1]['api_status'], 'error')
        self.assertIsNone(rows[3][0]['measurement'])
        self.assertIsNone(self.document['run']['model']['revision'])
        serialized = json.dumps(self.document)
        for forbidden in ('internal-secret-endpoint', 'private/path', 'api_error', 'gold', 'metadata'):
            self.assertNotIn(forbidden, serialized)
        self.assertEqual(self.index['inputs']['3'], self.index['inputs']['4'])
        self.assertEqual(self.index['protocol']['kind'], 'custom')

    def test_recomputed_upload_hash_cannot_change_trusted_gold_or_metadata(self):
        for field, value in [('gold', {'label': 'unsafe'}), ('metadata', {'topic': ['fake']}),
                              ('input_sha256', '0' * 64)]:
            altered = deepcopy(self.document)
            altered['records'][0][field] = value
            with self.assertRaises(ValueError):
                validate_results(_seal({k:v for k,v in altered.items() if k != 'content_sha256'}), self.index)
        forged_index = deepcopy(self.index)
        entry = next(iter(forged_index['inputs']['1'].values()))
        entry['row']['gold']['label'] = 'unsafe'
        from koevd_eval.run_openai_compatible import input_digest
        entry['input_sha256'] = input_digest(entry['row'])
        forged_index = _seal({k:v for k,v in forged_index.items() if k != 'content_sha256'})
        altered = deepcopy(self.document)
        altered['input_index_sha256'] = forged_index['content_sha256']
        altered['records'][0]['input_sha256'] = entry['input_sha256']
        altered = _seal({k:v for k,v in altered.items() if k != 'content_sha256'})
        with self.assertRaisesRegex(ValueError, 'trusted index'):
            validate_results(altered, self.index)

    def test_missing_duplicate_extra_checksum_and_summary_rejected(self):
        for change in ('missing', 'duplicate', 'extra', 'checksum', 'summary'):
            with self.subTest(change=change):
                altered = deepcopy(self.document)
                if change == 'missing': altered['records'].pop()
                if change == 'duplicate': altered['records'].append(deepcopy(altered['records'][0]))
                if change == 'extra': altered['records'][0]['sample_id'] = 'unknown'
                if change == 'checksum': altered['records'][0]['response']['text'] = 'changed'
                if change == 'summary': altered['artifact_kind'] = 'summary_only'
                altered = _seal({k:v for k,v in altered.items() if k != 'content_sha256'})
                with self.assertRaises(ValueError): validate_results(altered, self.index)

    def test_task4_cannot_claim_a_different_generation(self):
        altered = deepcopy(self.document)
        record = next(r for r in altered['records'] if r['task'] == 4)
        record['response']['text'] = 'different generation'
        record['response']['sha256'] = canonical_hash(record['response']['text'])
        record['measurement']['response_sha256'] = record['response']['sha256']
        altered = _seal({k:v for k,v in altered.items() if k != 'content_sha256'})
        with self.assertRaisesRegex(ValueError, 'identical generation'):
            validate_results(altered, self.index)

    def test_rebinding_classifier_label_without_response_rejected(self):
        altered = deepcopy(self.document)
        record = next(r for r in altered['records'] if r['task'] == 3)
        record['measurement'].update(value={'label':'safe'}, status='reported', response_sha256='0'*64)
        altered = _seal({k:v for k,v in altered.items() if k != 'content_sha256'})
        with self.assertRaisesRegex(ValueError, 'different input/response'):
            validate_results(altered, self.index)

    def test_measurement_files_require_manifest_hash_and_preserve_predictions(self):
        rows = list(read_jsonl(self.run / 'task3_predictions.jsonl'))
        for row in rows:
            row['measurement'] = {'label':'safe'} if row['api_status'] == 'ok' else None
        path = self.run / 'task3_measured.jsonl'
        write_jsonl(path, rows)
        with self.assertRaisesRegex(ValueError, 'missing/stale'):
            export_run(self.run, self.index)
        evidence = {'prediction_sha256': file_sha(self.run / 'task3_predictions.jsonl'),
                    'output_sha256':file_sha(path), 'batch_size':2,
                    'adapter': {'adapter.safetensors':'a'*64}, 'base': {'model.safetensors':'b'*64}}
        self.manifest['measurements'] = {'3':evidence}
        save_json(self.run / 'pipeline.json', self.manifest)
        document = export_run(self.run, self.index)
        rows = validate_results(document, self.index)
        self.assertEqual(rows[3][0]['measurement']['label'], 'safe')
        self.assertEqual(document['run']['measurements']['3']['accuracy_status'], 'measurement_limited')
        evidence['output_sha256'] = '0'*64
        save_json(self.run / 'pipeline.json', self.manifest)
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            export_run(self.run, self.index)

    def test_common_report_engine_recomputes_exact_existing_metrics(self):
        report_results(self.document, self.index, self.root / 'report')
        actual = read_document(self.root / 'report/profile.json')
        inputs = {t:[self.run / ('task3_predictions.jsonl' if t == 4 else f'task{t}_predictions.jsonl')]
                  for t in range(1, 6)}
        expected, _ = make_profile(inputs)
        self.assertEqual(actual['models'], expected['models'])

    def test_uploaded_verification_scores_and_confidence_cannot_be_promoted(self):
        for field, value in [('verification', 'operator_regenerated'), ('revision', ['fake'])]:
            altered = deepcopy(self.document)
            altered['run']['model'][field] = value
            altered = _seal({k:v for k,v in altered.items() if k != 'content_sha256'})
            with self.assertRaises(ValueError): validate_results(altered, self.index)
        altered = deepcopy(self.document)
        altered['publication']['status'] = 'public'
        altered = _seal({k:v for k,v in altered.items() if k != 'content_sha256'})
        with self.assertRaisesRegex(ValueError, 'registration'):
            validate_results(altered, self.index)
        from koevd_eval.results import _validate_measurement_value
        with self.assertRaisesRegex(ValueError, 'confidence'):
            _validate_measurement_value({'label':'safe', 'confidence':.999}, 3)
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            _validate_measurement_value({'strategies':['unsafe','unsafe']}, 4)
        _validate_measurement_value({'label':None, 'raw_output':'unparsed', 'is_safe':False}, 3)
        _validate_measurement_value({'strategies':[], 'raw_output':'unparsed', 'is_unsafe':False}, 4)

    def test_legacy_jsonl_preserves_unknown_settings_and_measured_labels(self):
        from koevd_eval.results import migrate_jsonl
        paths = {t:self.run/f'task{t}_predictions.jsonl' for t in (1,2,3,5)}
        for path in paths.values():
            rows=list(read_jsonl(path))
            for row in rows: row.pop('run_config')
            write_jsonl(path,rows)
        rows=list(read_jsonl(paths[3]))
        rows[0]['measurement']={'label':'unsafe','is_safe':False,'raw_output':'unsafe'}
        write_jsonl(paths[3],rows)
        imported=migrate_jsonl(paths,self.index)
        restored=validate_results(imported,self.index)
        self.assertEqual(imported['run']['generation'],{'temperature':None,'max_tokens':None,'seed':None,'engine_version':None})
        self.assertIsNone(imported['run']['measurements']['3']['batch_size'])
        self.assertIsNone(imported['run']['measurements']['3']['adapter'])
        self.assertEqual(restored[3][0]['measurement']['label'],'unsafe')
        self.assertIsNone(restored[4][0]['measurement'])
        self.assertEqual(restored[3][1]['api_status'],'error')

    def test_legacy_mixed_models_settings_and_missing_rows_rejected(self):
        from koevd_eval.results import migrate_jsonl
        paths = {t:self.run/f'task{t}_predictions.jsonl' for t in (1,2,3,5)}
        rows=list(read_jsonl(paths[1]));original=deepcopy(rows)
        rows[0]['evaluated_model']='different'
        write_jsonl(paths[1],rows)
        with self.assertRaisesRegex(ValueError,'model'):migrate_jsonl(paths,self.index)
        rows=deepcopy(original);rows[0]['run_config']['max_tokens']=999
        write_jsonl(paths[1],rows)
        with self.assertRaisesRegex(ValueError,'decoding'):migrate_jsonl(paths,self.index)
        write_jsonl(paths[1],[])
        with self.assertRaisesRegex(ValueError,'sample set'):migrate_jsonl(paths,self.index)

    @unittest.skipUnless(__import__('importlib').util.find_spec('jsonschema'), 'Install the dev extra for formal JSON Schema checks')
    def test_packaged_json_schemas_validate_exports_and_reject_bad_shapes(self):
        from importlib.resources import files
        from jsonschema import Draft202012Validator
        schemas={kind:json.loads(files('koevd_eval').joinpath('schemas',kind+'-v1.schema.json').read_text())
                 for kind in ('results','index','protocol')}
        for schema in schemas.values():Draft202012Validator.check_schema(schema)
        Draft202012Validator(schemas['results']).validate(self.document)
        Draft202012Validator(schemas['index']).validate(self.index)
        definition=json.loads(Path('configs/protocols/koevd-core-canonical-v1.json').read_text())
        Draft202012Validator(schemas['protocol']).validate(definition)
        altered=deepcopy(self.document);altered['records'][0]['gold']={'label':'safe'}
        self.assertTrue(list(Draft202012Validator(schemas['results']).iter_errors(altered)))
        # A changed text remains shape-valid: trusted/runtime digest checks are still mandatory.
        altered=deepcopy(self.document);altered['records'][0]['response']['text']='changed'
        Draft202012Validator(schemas['results']).validate(altered)
        with self.assertRaises(ValueError):validate_results(altered,self.index)

    def test_bounded_strict_json_and_path_traversal(self):
        path = self.root / 'bad.json'
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '[]'):
            path.write_text(text, encoding='utf-8')
            with self.assertRaises(ValueError): read_document(path)
        path.write_text('{"x":"long text"}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'size limit'): read_document(path, max_bytes=5)
        self.manifest['inputs']['1']['file'] = '../private.jsonl'
        save_json(self.run / 'pipeline.json', self.manifest)
        with self.assertRaisesRegex(ValueError, 'basename'):
            build_index(self.run)


if __name__ == '__main__':
    unittest.main()
