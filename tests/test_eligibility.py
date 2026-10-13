"""CPU policy fixtures only: these do not approve a real policy or GPU run."""
from copy import deepcopy
from pathlib import Path
import json
import unittest

import test_results
from koevd_eval.eligibility import (OperatorEvidence, RankPolicy, declaration_identity,
                                  evaluate_admission, leaderboard)
from koevd_eval.protocols import ProtocolRegistry, input_set_identity
from koevd_eval.results import canonical_hash, _seal


def seal(value):
    return _seal({k:deepcopy(v) for k,v in value.items() if k!='content_sha256'})


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        fixture=test_results.ResultContractTests();fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture=fixture
        # Tiny independent pinned protocol exercising policy paths. It is not
        # the actual full KoEVD index nor real GPU/ratification evidence.
        definition=json.loads((Path(__file__).resolve().parents[1]/'configs/protocols/koevd-core-canonical-v1.json').read_text())
        definition['id']='SYNTHETIC-policy-fixture'
        definition['expected_inputs']=input_set_identity(fixture.index)
        definition=seal(definition)
        directory=fixture.root/'policy-registry';directory.mkdir()
        (directory/'fixture.json').write_text(json.dumps(definition))
        self.registry=ProtocolRegistry(directory)
        self.index=deepcopy(fixture.index)
        self.index['protocol']={k:deepcopy(v) for k,v in definition.items()
                               if k not in ('expected_inputs','content_sha256','schema_version','status')}
        self.index['protocol'].update(kind='standard',definition_sha256=definition['content_sha256'])
        self.index=seal(self.index)
        self.doc=deepcopy(fixture.document)
        self.doc.update(input_index_sha256=self.index['content_sha256'],protocol_sha256=canonical_hash(self.index['protocol']))
        self.doc['run']['generation'].update(max_tokens=1024,engine_version='SYNTHETIC-engine-v1',seed=None)
        self.doc['run']['model'].update(revision='a'*40,chat_template='SYNTHETIC-template-v1',
            dtype='bfloat16',quantization='none',thinking='disabled')
        self.doc=seal(self.doc)
        # This trusted test config exercises a hypothetical approved state; no
        # operator decision or actual_gpu receipt exists outside this fixture.
        self.policy=RankPolicy(status='ratified',ratification_sha256='b'*64)

    def receipt(self,doc=None,**changes):
        doc=doc or self.doc
        values=dict(artifact_sha256=doc['content_sha256'],input_index_sha256=self.index['content_sha256'],
            declaration_sha256=declaration_identity(doc),receipt_sha256='c'*64,
            generation_level='operator_reproduced',execution_scope='actual_gpu')
        values.update(changes);return OperatorEvidence(**values)

    def report(self,doc=None,**kwargs):
        doc=doc or self.doc
        options=dict(registry=self.registry,policy=self.policy,evidence=self.receipt(doc))
        options.update(kwargs)
        return evaluate_admission(doc,self.index,**options)

    def metric(self,report,task,suffix):
        return next(m for m in report['metrics'] if m['task']==task and m['id'].endswith(suffix))

    def test_default_candidate_does_not_admit_any_metric(self):
        report=evaluate_admission(self.doc,self.index,registry=self.registry,evidence=self.receipt())
        self.assertEqual(report['eligible_metric_ids'],[])
        self.assertTrue(all('policy_not_ratified' in m['reasons'] for m in report['metrics']))

    def test_independent_pinned_index_decoding_and_evidence_allow_only_direct_metrics(self):
        report=self.report()
        self.assertTrue(self.metric(report,2,'accuracy_on_valid')['rank_eligible'])
        self.assertEqual(len([m for m in report['metrics'] if m['task']==2]),4)
        self.assertEqual(len([m for m in report['metrics'] if m['task']==5 and m['direction']]),6)
        self.assertTrue(all(not m['rank_eligible'] for m in report['metrics'] if m['task'] in (3,4,'3+5')))
        self.assertEqual(report['generation_verification'],'operator_reproduced')

    def test_self_claimed_protocol_without_operator_registry_is_excluded(self):
        report=self.report(registry=None)
        self.assertFalse(any(m['rank_eligible'] for m in report['metrics']))
        self.assertIn('unregistered_protocol_or_input_set',self.metric(report,2,'accuracy_on_valid')['reasons'])

    def test_custom_index_cannot_gain_standard_status_via_receipt(self):
        report=evaluate_admission(self.fixture.document,self.fixture.index,registry=self.registry,
                                  policy=self.policy,evidence=self.receipt())
        self.assertFalse(report['eligible_metric_ids'])
        reasons=self.metric(report,2,'accuracy_on_valid')['reasons']
        self.assertIn('nonstandard_evaluation',reasons)
        self.assertIn('unregistered_protocol_or_input_set',reasons)

    def test_measurement_recheck_or_cpu_receipt_is_not_target_gpu_reproduction(self):
        for field,value,reason in (('generation_level','measurement_rechecked','target_generation_not_operator_reproduced'),
                                   ('execution_scope','cpu_fixture','actual_gpu_evidence_missing')):
            with self.subTest(field=field):
                report=self.report(evidence=self.receipt(**{field:value}))
                self.assertEqual(report['eligible_metric_ids'],[])
                self.assertIn(reason,self.metric(report,2,'accuracy_on_valid')['reasons'])
                self.assertIsNone(report['operator_evidence_sha256'])

    def test_receipt_binds_artifact_index_and_target_declarations(self):
        for field in ('artifact_sha256','input_index_sha256','declaration_sha256'):
            report=self.report(evidence=self.receipt(**{field:'d'*64}))
            self.assertFalse(report['eligible_metric_ids'])
            self.assertIn('stale_or_mismatched_operator_evidence',self.metric(report,2,'accuracy_on_valid')['reasons'])
        changed=deepcopy(self.doc);changed['run']['model']['revision']='e'*40;changed=seal(changed)
        self.assertFalse(self.report(changed,evidence=self.receipt())['eligible_metric_ids'])

    def test_missing_conditions_and_decoding_mismatch_have_separate_reasons(self):
        changed=deepcopy(self.doc)
        changed['run']['model']['thinking']=None
        changed['run']['model']['revision']=None
        changed['run']['generation']['temperature']=.5;changed=seal(changed)
        report=self.report(changed)
        reasons=self.metric(report,2,'accuracy_on_valid')['reasons']
        for reason in ('generation_conditions_incomplete','immutable_target_revision_missing','decoding_policy_mismatch_or_unknown'):
            self.assertIn(reason,reasons)
        self.assertFalse(report['eligible_metric_ids'])

    def test_failed_task5_zero_events_cannot_rank_as_safe(self):
        changed=deepcopy(self.doc)
        for row in changed['records']:
            if row['task']==5:
                row['response'].update(status='error',text='',sha256=canonical_hash(''))
                row['measurement']['status']='not_applicable'
        changed=seal(changed)
        report=self.report(changed)
        rates=[m for m in report['metrics'] if m['task']==5 and m['direction']]
        self.assertTrue(rates)
        for metric in rates:
            self.assertFalse(metric['rank_eligible'])
            self.assertIn('incomplete_valid_outputs',metric['reasons'])
            if metric['id'].endswith('event_on_valid'):
                self.assertIsNone(metric['rate']['value'])
            else: self.assertEqual(metric['rate']['value'],0)
        self.assertTrue(self.metric(report,2,'accuracy_on_valid')['rank_eligible'])

    def test_undefined_task1_label_denominator_is_na_not_zero(self):
        report=self.report()
        candidates=[m for m in report['metrics'] if m['task']==1 and m['rate']['denominator']==0]
        self.assertEqual(len(candidates),1)
        self.assertIsNone(candidates[0]['rate']['value'])
        self.assertIn('undefined_denominator',candidates[0]['reasons'])

    def test_task4_and_label_conditioned_linked_metrics_remain_descriptive(self):
        report=self.report()
        for m in report['metrics']:
            if m['task'] in (4,'3+5'):
                self.assertIsNone(m['direction']);self.assertFalse(m['rank_eligible'])
                self.assertIn('descriptive_only',m['reasons'])
            if m['task']=='3+5':self.assertIn('model_dependent_conditioning',m['reasons'])
            if m['task']==3:self.assertIn('measurement_limited',m['reasons'])

    def test_invalid_or_injected_scores_evidence_are_rejected(self):
        for kwargs in ({'evidence':{'generation_level':'operator_reproduced'}},{'policy':{'status':'ratified'}}):
            with self.assertRaises(ValueError):self.report(**kwargs)
        changed=deepcopy(self.doc);changed['scores']={'task2':1.0};changed=seal(changed)
        with self.assertRaises(ValueError):self.report(changed)
        changed=deepcopy(self.doc);changed['records'].pop();changed=seal(changed)
        with self.assertRaises(ValueError):self.report(changed)

    def test_board_excludes_failed_and_na_rows_and_preserves_ties(self):
        entries=[(name,self.doc,self.index,self.receipt()) for name in ('z','a')]
        entries.append(('no-evidence',self.doc,self.index,None))
        report=leaderboard(entries,registry=self.registry,policy=self.policy)
        self.assertTrue(report['boards']);self.assertTrue(report['excluded'])
        for board in report['boards']:
            self.assertEqual([r['entry_id'] for r in board['rows']],['a','z'])
            self.assertEqual([r['rank'] for r in board['rows']],[1,1])
            self.assertNotIn('task4/',board['metric_id'])
        with self.assertRaises(ValueError):leaderboard(entries+entries[:1],registry=self.registry,policy=self.policy)

    def test_different_settings_are_distinct_cohorts_not_pooled(self):
        changed=deepcopy(self.doc);changed['run']['model']['dtype']='float16';changed=seal(changed)
        report=leaderboard([('a',self.doc,self.index,self.receipt()),('b',changed,self.index,self.receipt(changed))],
                           registry=self.registry,policy=self.policy)
        task2=[b for b in report['boards'] if b['metric_id'].startswith('task2/')]
        self.assertEqual(len(task2),8)
        self.assertTrue(all(len(b['rows'])==1 for b in task2))

    def test_accuracy_higher_and_unsafe_call_lower_sort_in_opposite_directions(self):
        changed=deepcopy(self.doc)
        for row in changed['records']:
            if row['task']==2:
                text='B'
            elif row['task']==5:
                tool=self.index['inputs']['5'][row['sample_id']]['row']['gold']['unsafe_tools'][0]
                text=json.dumps({'decision':'call_tool','tool_name':tool})
            else:continue
            row['response'].update(text=text,sha256=canonical_hash(text))
        changed=seal(changed)
        result=leaderboard([('safe-correct',self.doc,self.index,self.receipt()),
            ('unsafe-wrong',changed,self.index,self.receipt(changed))],registry=self.registry,policy=self.policy)
        for board in result['boards']:
            if board['metric_id'].startswith(('task2/','task5/')):
                self.assertEqual([r['entry_id'] for r in board['rows']],['safe-correct','unsafe-wrong'])
                self.assertEqual([r['rank'] for r in board['rows']],[1,2])

    def test_order_does_not_change_boards_or_mutate_originals(self):
        before=deepcopy(self.doc)
        entries=[('a',self.doc,self.index,self.receipt()),('b',self.doc,self.index,self.receipt())]
        first=leaderboard(entries,registry=self.registry,policy=self.policy)
        second=leaderboard(list(reversed(entries)),registry=self.registry,policy=self.policy)
        self.assertEqual(first['boards'],second['boards']);self.assertEqual(self.doc,before)

    def test_policy_ratification_requires_explicit_immutable_decision_reference(self):
        for options in ({'status':'ratified'},{'status':'ratified','ratification_sha256':'text'},
                        {'status':'candidate','ratification_sha256':'a'*64},{'version':'unknown'}):
            with self.assertRaises(ValueError):RankPolicy(**options)


if __name__=='__main__': unittest.main()
