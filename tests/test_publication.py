import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError
from koevd_eval.common import read_jsonl, write_jsonl
from koevd_eval.metrics import score_task3, score_task4
from koevd_eval.analysis import corpus_stats, grouped_metrics, matched_analysis
from koevd_eval.run_openai_compatible import run_rows, unique_rows
from koevd_eval.classify_responses import build_messages
from koevd_classifiers.response_strategy_classifier.model import parse_strategies
from koevd_classifiers.assistant_safe_classifier.model import format_openai_messages

class PublicationTests(unittest.TestCase):
    def test_task3_missing_measurements_stay_in_all_denominator(self):
        m=score_task3([{'measurement':{'label':'unsafe'}},{'measurement':{'label':'safe'}},{'measurement':None}])
        self.assertEqual(m['unsafe_generation_rate_on_classified'],.5)
        self.assertEqual(m['unsafe_generation_rate_on_all_prompts'],1/3)

    def test_strategy_inclusion_is_a_set(self):
        m=score_task4([{'measurement':{'strategies':['c_reasoning','c_reasoning']}},{'measurement':{'strategies':['unsafe']}},{'measurement':None}])
        self.assertEqual(m['classified'],2)
        self.assertEqual(m['strategy_inclusion']['c_reasoning']['count'],1)
        self.assertEqual(m['strategy_inclusion']['c_reasoning']['rate_on_classified'],.5)

    def test_strategy_parser_preserves_distinct_order(self):
        self.assertEqual(parse_strategies('c_reasoning, a_boundary setting, c_reasoning'),['c_reasoning','a_boundary setting'])

    def test_classifier_messages_keep_context_and_target(self):
        row={'messages':[{'role':'user','content':'hello'}],'prediction':'hello back'}
        prompt=format_openai_messages(build_messages(row))
        self.assertIn('User: hello',prompt)
        self.assertIn('Assistant: hello back',prompt)

    def test_groups_keep_parse_failures(self):
        rows=[{'prediction':'unsafe','metadata':{'band':'A'}},{'prediction':'','metadata':{'band':'A'}}]
        m=grouped_metrics(rows,1,['metadata.band'])['groups'][0]['metrics']
        self.assertEqual(m['prompted'],2); self.assertEqual(m['parse_rate'],.5)

    def test_multilabel_groups_do_not_repeat_one_row(self):
        result=grouped_metrics([{'prediction':'safe','metadata':{'topic':['x','x','y']}}],1,['metadata.topic'])
        self.assertEqual(len(result['groups']),2)
        self.assertTrue(all(g['metrics']['prompted']==1 for g in result['groups']))

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError): unique_rows([{'sample_id':'a'},{'sample_id':'a'}])

    def test_resume_replaces_failure_and_clears_error(self):
        rows=[{'sample_id':'a','messages':[{'role':'user','content':'hello'}]}]
        config={'endpoint':'http://localhost/v1/chat/completions','model':'test','temperature':0,'max_tokens':5}
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'out.jsonl'
            with patch('koevd_eval.run_openai_compatible.call_api',side_effect=URLError('test')):
                run_rows(rows,out,config,retries=0)
            with patch('koevd_eval.run_openai_compatible.call_api',return_value='safe') as api:
                run_rows(rows,out,config,resume=True)
                api.assert_called_once()
            results=list(read_jsonl(out)); self.assertEqual(len(results),1)
            self.assertEqual(results[0]['api_status'],'ok'); self.assertIsNone(results[0]['api_error'])
            with patch('koevd_eval.run_openai_compatible.call_api') as api:
                run_rows(rows,out,config,resume=True); api.assert_not_called()
            with self.assertRaises(ValueError): run_rows(rows,out,{**config,'model':'other'},resume=True)

    def test_corpus_stats_candidates_and_distinct_strategies(self):
        rows=[{'source_id':'a','user_utterance':{'labels':{},'rationales':{'problem_reason':'reason'}},'responses':{'accepted':[{'strategies':['x','x','y']}],'rejected':[{}],'strongly_rejected':[]}}]
        m=corpus_stats(rows); self.assertEqual(m['candidates'],2)
        self.assertEqual(m['accepted_strategy_density']['2']['count'],1)
        with self.assertRaises(ValueError): corpus_stats(rows*2)

    def test_overlap_retains_all_matched_and_rejects_duplicates(self):
        t3=[{'source_id':'a','evaluated_model':'m','measurement':{'label':'safe'}}, {'source_id':'b','evaluated_model':'m','measurement':{'label':'unsafe'}}]
        t5=[{'source_id':'a','evaluated_model':'m','metadata':{'prompt_variant':'tool_forced'},'api_status':'ok','prediction':'{"decision":"call_tool","tool_name":"mock_bad"}','gold':{'unsafe_tools':['mock_bad']}}, {'source_id':'b','evaluated_model':'m','metadata':{'prompt_variant':'tool_forced'},'api_status':'ok','prediction':'invalid','gold':{}}]
        with tempfile.TemporaryDirectory() as tmp:
            x,y=Path(tmp)/'t3.jsonl',Path(tmp)/'t5.jsonl'; write_jsonl(x,t3); write_jsonl(y,t5)
            result=matched_analysis([x],[y]); s=result['summary']['all']
            self.assertEqual(s['matched_total'],2); self.assertEqual(s['unparsed_total'],1)
            self.assertEqual(s['p_task5_unsafe_given_task3_safe_all_matched_pct'],100)
            self.assertEqual(s['p_task5_unsafe_given_task3_unsafe_all_matched_pct'],0)
            write_jsonl(y,t5+t5[:1])
            with self.assertRaises(ValueError): matched_analysis([x],[y])

if __name__=='__main__': unittest.main()
