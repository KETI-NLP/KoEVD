from copy import deepcopy
from importlib.resources import files
import json
import unittest

import test_results as legacy_fixture
import test_measurement_trace as trace_fixture
from koevd_eval.results import export_run, validate_results, _seal
from koevd_eval.measurement_conditions import VERSION, validate_conditions, comparison_fields
from koevd_eval.measurement_trace import file_hash
from koevd_eval.diagnostics import compatibility, compare, analyze


def reseal(value):
    value = deepcopy(value)
    value.pop('content_sha256', None)
    return _seal(value)


class PortableMeasurementTests(unittest.TestCase):
    def setUp(self):
        self.fixture = trace_fixture.TraceExportTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.index = self.fixture.fixture.index
        self.root = self.fixture.fixture.run
        self.document = export_run(self.root, self.index)

    def test_export_preserves_conditions_observations_and_failure_denominator(self):
        for task in ('3', '4'):
            evidence = self.document['run']['measurements'][task]
            c = evidence['conditions']
            self.assertEqual(c['version'], VERSION)
            self.assertEqual((c['input_order'], c['inference_mode']), ('original', 'batch'))
            self.assertIsNone(c['requested_dtype'])
            self.assertIsNone(c['requested_max_new_tokens'])
            obs = c['observation']
            self.assertEqual(obs['trace_sha256'], file_hash(self.root / f'task{task}_measurement_trace.json'))
            records = [r for r in self.document['records'] if str(r['task']) == task]
            self.assertEqual(obs['counts']['total'], len(records))
            self.assertEqual(obs['counts']['observed'], len(records) - 1)
            self.assertEqual(obs['counts']['not_applicable'], 1)
            self.assertEqual(obs['generate_options'][0]['max_new_tokens'], 3)
            self.assertEqual(obs['runtime']['parameter_dtype_elements'], {'FAKE.float32': 8})
            self.assertNotIn('gpu', obs['runtime'])
            self.assertIsNone(evidence['input_truncation'])
            self.assertEqual(evidence['accuracy_status'], 'measurement_limited')
        self.assertEqual(validate_results(self.document, self.index)[3][1]['api_status'], 'error')

    def test_old_evidence_remains_valid_and_unknown_without_invented_defaults(self):
        old = deepcopy(self.document)
        for evidence in old['run']['measurements'].values(): evidence.pop('conditions')
        old = reseal(old)
        validate_results(old, self.index)
        reasons = compatibility(old, self.index, old, self.index, 3)['reasons']
        self.assertIn('measurement.conditions.input_order', [r['field'] for r in reasons if r['code'] == 'unknown'])
        self.assertIn('measurement.conditions.observed_generate_options', [r['field'] for r in reasons if r['code'] == 'unknown'])
        self.assertFalse(compatibility(old, self.index, old, self.index, 3)['official_rank_eligible'])

    def test_untraced_pipeline_declarations_do_not_claim_observed_conditions(self):
        manifest = deepcopy(self.fixture.manifest)
        for task, evidence in manifest['measurements'].items():
            evidence.pop('trace_sha256')
            evidence.update(requested_dtype='bfloat16', input_order='reverse', inference_mode='single')
        (self.root / 'pipeline.json').write_text(json.dumps(manifest), encoding='utf-8')
        doc = export_run(self.root, self.index)
        for evidence in doc['run']['measurements'].values():
            self.assertEqual(evidence['conditions']['requested_dtype'], 'bfloat16')
            self.assertIsNone(evidence['conditions']['observation'])
            self.assertIsNone(evidence['precision'])
        reasons = compatibility(doc, self.index, doc, self.index, 3)['reasons']
        self.assertIn('measurement.conditions.tokenizer_padding_side', [r['field'] for r in reasons if r['code'] == 'unknown'])

    def test_manifest_trace_scheduling_disagreement_is_rejected(self):
        for field, value in (('input_order', 'reverse'), ('inference_mode', 'single'), ('batch_size', 4)):
            with self.subTest(field=field):
                manifest = deepcopy(self.fixture.manifest)
                manifest['measurements']['3'][field] = value
                (self.root / 'pipeline.json').write_text(json.dumps(manifest), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'disagrees'): export_run(self.root, self.index)

    def test_resealed_invalid_conditions_and_inflated_coverage_are_rejected(self):
        changes = [lambda c: c.update(version='new-unsupported'), lambda c: c.update(input_order='random'),
                   lambda c: c.update(requested_dtype='verified-bf16'), lambda c: c.update(requested_max_new_tokens=True),
                   lambda c: c.update(extra='unexpected'), lambda c: c['observation'].update(trace_sha256='bad'),
                   lambda c: c['observation']['runtime'].update(gpu={'name':'private'}),
                   lambda c: c['observation']['runtime']['parameter_dtype_elements'].update({'FAKE.float32':True}),
                   lambda c: c['observation']['counts'].update(total=100, observed=99, not_applicable=1),
                   lambda c: c['observation']['generate_options'][0].update(max_new_tokens=False),
                   lambda c: c.update(requested_max_new_tokens=16),
                   lambda c: c['observation']['generate_options'].append(deepcopy(c['observation']['generate_options'][0]))]
        for n, change in enumerate(changes):
            with self.subTest(n=n):
                doc = deepcopy(self.document); change(doc['run']['measurements']['3']['conditions'])
                with self.assertRaises(ValueError): validate_results(reseal(doc), self.index)

    def test_order_mode_options_and_package_changes_only_affect_measured_tasks(self):
        changes = [lambda c: c.update(input_order='reverse'), lambda c: c.update(inference_mode='single'),
                   lambda c: c['observation']['generate_options'][0].update(max_new_tokens=4),
                   lambda c: c['observation']['runtime']['package_versions'].update(transformers='different')]
        expected = ['input_order', 'inference_mode', 'observed_generate_options', 'package_versions.transformers']
        for change, field in zip(changes, expected):
            with self.subTest(field=field):
                baseline = deepcopy(self.document)
                if field == 'package_versions.transformers':
                    for evidence in baseline['run']['measurements'].values():
                        evidence['conditions']['observation']['runtime']['package_versions']['transformers'] = 'FAKE.version-a'
                baseline = reseal(baseline)
                other = deepcopy(baseline)
                for evidence in other['run']['measurements'].values(): change(evidence['conditions'])
                other = reseal(other)
                result = compare(baseline, self.index, other, self.index, resamples=0)
                for task in (1, 2, 5):
                    self.assertFalse(any(r['field'].startswith('measurement.') for r in result['tasks'][task-1]['compatibility']['reasons']))
                for task in (3, 4):
                    reasons = result['tasks'][task-1]['compatibility']['reasons']
                    self.assertIn('measurement.conditions.' + field, [r['field'] for r in reasons if r['code'] == 'different'])
                    self.assertFalse(result['tasks'][task-1]['compatibility']['official_rank_eligible'])

    def test_trace_identity_and_response_dependent_counts_are_not_settings(self):
        other = deepcopy(self.document)
        for evidence in other['run']['measurements'].values():
            obs = evidence['conditions']['observation']
            obs['trace_sha256'] = 'e' * 64
            obs['counts']['token_parity_mismatch'] = 0
            obs['runtime']['parameter_dtype_elements']['FAKE.float32'] = 999
        other = reseal(other); validate_results(other, self.index)
        reasons = compatibility(self.document, self.index, other, self.index, 3)['reasons']
        self.assertFalse(any(r['code'] == 'different' for r in reasons))
        self.assertEqual(comparison_fields(self.document['run']['measurements']['3']), comparison_fields(other['run']['measurements']['3']))
        # Submission consistency is not authenticity: the changed self-report cannot promote rank.
        self.assertFalse(compatibility(self.document, self.index, other, self.index, 3)['official_rank_eligible'])

    def test_trace_eos_budget_and_option_tamper_rejected_after_resealing(self):
        path = self.root / 'task3_measurement_trace.json'
        original = json.loads(path.read_text(encoding='utf-8'))
        changes = [lambda o: o.update(first_eos_index=True), lambda o: o.update(generated_tokens_through_first_eos=999),
                   lambda o: o.update(reached_token_budget_without_eos=True),
                   lambda o: o['generation_kwargs'].update(do_sample='false'),
                   lambda o: o.update(exceeds_declared_model_context='no')]
        for n, change in enumerate(changes):
            with self.subTest(n=n):
                trace = deepcopy(original); change(trace['records'][0]['observed_generate'])
                path.write_text(json.dumps(reseal(trace)), encoding='utf-8')
                manifest = deepcopy(self.fixture.manifest); manifest['measurements']['3']['trace_sha256'] = file_hash(path)
                (self.root / 'pipeline.json').write_text(json.dumps(manifest), encoding='utf-8')
                with self.assertRaises(ValueError): export_run(self.root, self.index)

    def test_formal_schema_accepts_old_and_new_and_rejects_unknown_condition_fields(self):
        from jsonschema import Draft202012Validator
        schema = json.loads(files('koevd_eval').joinpath('schemas/results-v1.schema.json').read_text())
        Draft202012Validator.check_schema(schema); validator = Draft202012Validator(schema)
        validator.validate(self.document)
        old = deepcopy(self.document)
        for evidence in old['run']['measurements'].values(): evidence.pop('conditions')
        validator.validate(reseal(old))
        bad = deepcopy(self.document); bad['run']['measurements']['3']['conditions']['rank_verified'] = True
        self.assertTrue(list(validator.iter_errors(reseal(bad))))

    def test_analysis_remains_numerically_identical_when_conditions_are_added(self):
        old = deepcopy(self.document)
        for evidence in old['run']['measurements'].values(): evidence.pop('conditions')
        a = analyze(self.document, self.index, resamples=0)
        b = analyze(reseal(old), self.index, resamples=0)
        for key in ('tasks', 'task3_task5', 'quality', 'measurement_disagreement', 'signals'):
            self.assertEqual(a[key], b[key], key)
        def without_artifact(value):
            if isinstance(value, dict): return {k: without_artifact(v) for k, v in value.items() if k != 'artifact_sha256'}
            if isinstance(value, list): return [without_artifact(v) for v in value]
            return value
        # Navigation IDs bind the artifact and therefore should change after metadata changes.
        for key in ('charts', 'cases'):
            left, right = without_artifact(a[key]), without_artifact(b[key])
            if key == 'charts':
                for chart in left + right: chart.pop('id')
            self.assertEqual(left, right, key)



if __name__ == '__main__': unittest.main()
