from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from koevd_eval.measurement_audit import (create_audit, compare_measurements,
    import_review, review_template, write_audit, validate_audit)
from koevd_eval.results import _seal, canonical_hash

spec = importlib.util.spec_from_file_location('audit_demo_fixture',
    Path(__file__).resolve().parents[1]/'examples'/'make_demo_diagnostics.py')
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


def reseal(value):
    return _seal({k:v for k,v in value.items() if k != 'content_sha256'})


class MeasurementAuditTests(unittest.TestCase):
    def setUp(self):
        self.index, (self.base, _) = fixture.make_fixture()
        self.guideline = {'id':'SYNTHETIC-review-guideline', 'version':'fixture-v1'}

    def audit(self, **kw):
        return create_audit(self.base, self.index, guideline=self.guideline, **kw)

    def review(self, audit):
        review = review_template(audit)
        review['reviewer'] = {'id':'TEST-reviewer-1','role':'test_annotator'}
        return review

    def record(self, document, task, source='synthetic-001'):
        return next(r for r in document['records'] if r['task']==task and r['source_id']==source)

    def test_frozen_semantic_raw_validity_counts_and_no_overwrite(self):
        original = deepcopy(self.base)
        variant = deepcopy(self.base)
        variant['run']['measurements']['3']['batch_size'] = 4
        r = self.record(variant, 3)
        r['measurement']['value'] = {'label':'unsafe', 'raw_output':'unsafe'}
        r = self.record(variant, 3, 'synthetic-002')
        r['measurement'].update(value=None,status='unmeasured')
        result = compare_measurements(self.base, reseal(variant), self.index, variant_id='batch4-reported')
        c = result['tasks']['3']['counts']
        self.assertEqual(c['total'],80)
        self.assertEqual(c['both_valid'],73)
        self.assertEqual(c['semantic_changes'],1)
        self.assertEqual(c['validity_changes'],1)
        self.assertEqual(c['raw_output_changes'],0)
        self.assertEqual(c['raw_output_presence_changes'],1)
        self.assertEqual(c['raw_output_comparable'],0)
        self.assertIsNone(result['tasks']['3']['raw_change_rate_on_recorded_pairs'])
        self.assertEqual(c['measurement_value_changes'],2)
        self.assertEqual(result['tasks']['3']['semantic_change_rate_on_both_valid'],1/73)
        self.assertIn('batch_size',result['tasks']['3']['provenance']['different_fields'])
        self.assertIn('precision',result['tasks']['3']['provenance']['unknown_fields'])
        self.assertFalse(result['official_rank_eligible'])
        self.assertEqual(self.base,original)

    def test_raw_output_comparison_requires_both_recorded_values(self):
        a=deepcopy(self.base);b=deepcopy(self.base)
        self.record(a,3)['measurement']['value']['raw_output']='safe'
        self.record(b,3)['measurement']['value']['raw_output']=' SAFE '
        result=compare_measurements(reseal(a),reseal(b),self.index,variant_id='raw-change')
        c=result['tasks']['3']['counts']
        self.assertEqual(c['raw_output_changes'],1)
        self.assertEqual(c['raw_output_comparable'],1)
        self.assertEqual(c['semantic_changes'],0)
        self.assertEqual(result['tasks']['3']['raw_change_rate_on_recorded_pairs'],1.)

    def test_identical_artifact_is_zero_change_not_duplicate_target(self):
        result = compare_measurements(self.base,self.base,self.index,variant_id='repeat-identical')
        for t in ('3','4'):
            self.assertEqual(result['tasks'][t]['counts']['semantic_changes'],0)
            self.assertEqual(result['tasks'][t]['counts']['measurement_value_changes'],0)

    def test_strategy_label_order_is_not_semantic_change(self):
        variant=deepcopy(self.base)
        value=self.record(variant,4)['measurement']['value']
        value['strategies'].reverse()
        result=compare_measurements(self.base,reseal(variant),self.index,variant_id='order-only')
        self.assertEqual(result['tasks']['4']['counts']['semantic_changes'],0)
        self.assertEqual(result['tasks']['4']['counts']['measurement_value_changes'],1)

    def test_reject_changed_target_settings_and_any_generation(self):
        for section,field,value in [('model','id','different-target'),('generation','max_tokens',2048)]:
            variant=deepcopy(self.base);variant['run'][section][field]=value
            with self.assertRaisesRegex(ValueError,'Frozen target'):
                compare_measurements(self.base,reseal(variant),self.index,variant_id='bad')
        variant=deepcopy(self.base)
        r=self.record(variant,1)
        r['response']['text']='different';r['response']['sha256']=canonical_hash('different')
        with self.assertRaisesRegex(ValueError,'Frozen input/generation'):
            compare_measurements(self.base,reseal(variant),self.index,variant_id='bad')

    def test_no_valid_measurements_remains_none_not_zero(self):
        d=deepcopy(self.base)
        for r in d['records']:
            if r['task'] in (3,4) and r['response']['status']=='ok':
                r['measurement'].update(value=None,status='unmeasured')
        d=reseal(d)
        result=compare_measurements(d,d,self.index,variant_id='unmeasured')
        self.assertIsNone(result['tasks']['3']['semantic_change_rate_on_both_valid'])
        self.assertEqual(result['tasks']['3']['counts']['both_valid'],0)

    def test_selection_is_deterministic_prioritizes_named_sources_and_reports_universe(self):
        args={'limit':5,'seed':42,'suspect_sources':['synthetic-005','missing-source']}
        a=self.audit(**args)
        b=deepcopy(self.base);b['records'].reverse();b=reseal(b)
        c=create_audit(b,self.index,guideline=self.guideline,**args)
        self.assertEqual([x['sample_id'] for x in a['cases']],[x['sample_id'] for x in c['cases']])
        self.assertEqual(a['cases'][0]['source_id'],'synthetic-005')
        self.assertEqual(a['selection']['suspects_missing'],['missing-source'])
        self.assertEqual(a['universe']['sources'],80)
        self.assertEqual(a['universe']['valid_safety'],74)
        self.assertEqual(a['universe']['valid_strategy'],79)
        self.assertEqual(a['universe']['selected_sources'],5)
        self.assertFalse(a['selection']['representative_prevalence_sample'])
        self.assertEqual(a,self.audit(**args))

    def test_strategy_missing_is_selected_for_audit(self):
        d=deepcopy(self.base)
        r=self.record(d,4)
        r['measurement'].update(value=None,status='unmeasured')
        a=create_audit(reseal(d),self.index,guideline=self.guideline,limit=80)
        c=next(c for c in a['cases'] if c['source_id']=='synthetic-001')
        self.assertIn('invalid_or_unmeasured_strategy',c['selection_reasons'])

    def test_blinded_files_and_new_output_only(self):
        audit=self.audit(limit=5)
        with tempfile.TemporaryDirectory() as tmp:
            write_audit(audit,tmp)
            rows=[json.loads(x) for x in (Path(tmp)/'blinded-cases.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(rows),5)
            for row in rows:
                for key in ('model','metadata','gold','measurement','safety','strategy','selection_reasons','sample_id'):
                    self.assertNotIn(key,row)
            template=json.loads((Path(tmp)/'review-template.json').read_text(encoding='utf-8'))
            self.assertEqual(template,review_template(audit))
            self.assertTrue(all(x['safety_label']=='not_reviewed' for x in template['reviews']))
            self.assertIsNone(template['reviewer']['id'])
            with self.assertRaisesRegex(ValueError,'new or empty'): write_audit(audit,tmp)

    def test_reviews_stay_separate_unknowns_and_partial_return_are_explicit(self):
        audit=self.audit(limit=80)
        review=self.review(audit)
        r=next(r for r in review['reviews'] if r['case_id']==next(c['case_id'] for c in audit['cases'] if c['source_id']=='synthetic-001'))
        review['reviews']=[r]
        r.update(safety_label='unsafe',strategies=['c_reasoning','unsafe'],rationale='Fixture judgment, not real human evidence.')
        before=deepcopy(self.base)
        result=import_review(review,audit,self.base,self.index)
        self.assertFalse(result['reviews'][0]['reported_classifier_agrees'])
        self.assertEqual(result['counts']['unreturned_cases'],79)
        self.assertFalse(result['official_rank_eligible'])
        self.assertEqual(result['accuracy_status'],'not_established')
        self.assertEqual(self.base,before)
        for label in ('uncertain','abstain','not_reviewed'):
            r.update(safety_label=label,strategies=None)
            imported=import_review(review,audit,self.base,self.index)
            self.assertIsNone(imported['reviews'][0]['reported_classifier_agrees'])

    def test_stale_duplicate_tampered_or_unguided_review_rejected(self):
        audit=self.audit(limit=3);original=self.review(audit)
        mutations=[lambda d:d.update(audit_sha256='a'*64),
                   lambda d:d['guideline'].update(version='wrong'),
                   lambda d:d['reviews'].append(deepcopy(d['reviews'][0])),
                   lambda d:d['reviews'][0].update(response_sha256='a'*64),
                   lambda d:d['reviews'][0].update(safety_label='safe',rationale=None),
                   lambda d:d['reviews'][0].update(strategies=['unknown'],rationale='x'),
                   lambda d:d['reviewer'].update(id=None),
                   lambda d:d.update(stage='adjudicated_gold')]
        for mutate in mutations:
            d=deepcopy(original);mutate(d)
            with self.assertRaises(ValueError): import_review(d,audit,self.base,self.index)
        d=deepcopy(audit);d['cases'][0]['messages'][0]['content']='tampered'
        with self.assertRaisesRegex(ValueError,'content differs'):
            import_review(original,reseal(d),self.base,self.index)

    def test_failed_generation_cannot_receive_safe_or_strategy_label(self):
        audit=self.audit(limit=80);review=self.review(audit)
        failed=next(c for c in audit['cases'] if c['source_id']=='synthetic-079')
        r=next(r for r in review['reviews'] if r['case_id']==failed['case_id'])
        r.update(safety_label='safe',rationale='Do not mistake missing output for safety.')
        with self.assertRaisesRegex(ValueError,'Failed/empty'):
            import_review(review,audit,self.base,self.index)
        r.update(safety_label='abstain',strategies=None)
        result=import_review(review,audit,self.base,self.index)
        self.assertEqual(result['counts']['abstain'],1)

    def test_bounded_options_variant_names_and_literal_malicious_text(self):
        for limit in (0,True,5001):
            with self.assertRaises(ValueError): self.audit(limit=limit)
        with self.assertRaises(ValueError): self.audit(seed=True)
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            self.audit(variants=[('repeat',self.base),('repeat',self.base)])
        index,(d,_)=fixture.make_fixture(adversarial=True)
        audit=create_audit(d,index,guideline=self.guideline,limit=80)
        c=next(c for c in audit['cases'] if c['source_id']=='synthetic-050')
        self.assertIn('</script>',c['response']['text'])
        self.assertEqual(len(validate_audit(audit,d,index)),80)


if __name__=='__main__': unittest.main()
