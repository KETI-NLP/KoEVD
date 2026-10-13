"""Token-container/counting CPU regression; tokenizer stub is not model evidence."""
from collections import UserDict
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('input_budget',Path(__file__).resolve().parents[1]/'scripts/check_gpu_input_budget.py')
budget=importlib.util.module_from_spec(spec);spec.loader.exec_module(budget)


class InputBudgetTests(unittest.TestCase):
    def test_mapping_keys_are_not_prompt_tokens(self):
        encoded=UserDict(input_ids=list(range(484)),attention_mask=[1]*484)
        self.assertEqual(len(encoded),2)
        class Tokenizer:
            def apply_chat_template(self,messages,**options):
                self.options=options;return encoded
        tokenizer=Tokenizer()
        self.assertEqual(budget.prompt_tokens(tokenizer,[{'role':'user','content':'CPU fixture'}]),484)
        self.assertTrue(tokenizer.options['return_dict'])
        self.assertFalse(tokenizer.options['enable_thinking'])

    def test_flat_and_single_batch_ids_and_rejection_of_ambiguous_shapes(self):
        for value in ([1,2,3],[[1,2,3]],UserDict(input_ids=[[1,2,3]])):
            self.assertEqual(budget.token_ids(value),[1,2,3])
        for value in ({'attention_mask':[1]},[],[True],[-1],['x'],[[1],[2]],'plain text',[[[1,2]]]):
            with self.subTest(value=value),self.assertRaises(ValueError):budget.token_ids(value)


if __name__=='__main__':unittest.main()
