"""CPU prompt-token budget check using an explicit local tokenizer; no generation.

Count input_ids, never BatchEncoding keys. Input/output budgets do not establish
generation coverage, classifier correctness or inference authenticity.
"""
from collections.abc import Mapping
import argparse
import hashlib
import json
from pathlib import Path


def token_ids(encoded):
    value=encoded.get('input_ids') if isinstance(encoded,Mapping) else encoded
    if isinstance(value,list) and len(value)==1 and isinstance(value[0],list):value=value[0]
    if not isinstance(value,list) or not value or any(type(v) is not int or v<0 for v in value):
        raise ValueError('Expected one nonempty sequence of integer token IDs')
    return value


def prompt_tokens(tokenizer,messages,*,thinking=False):
    encoded=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,
        enable_thinking=thinking,return_dict=True)
    return len(token_ids(encoded))


def measure_budget(index,tokenizer,*,context_window,max_tokens,thinking=False):
    from koevd_eval.results import validate_index
    validate_index(index)
    if type(context_window) is not int or context_window<1 or type(max_tokens) is not int or not 1<=max_tokens<context_window:
        raise ValueError('Invalid context/output token budget')
    summary={}
    for task in ('1','2','3','5'):
        maximum,oversized=0,0
        for value in index['inputs'][task].values():
            count=prompt_tokens(tokenizer,value['row']['messages'],thinking=thinking)
            maximum=max(maximum,count);oversized+=count+max_tokens>context_window
        summary[task]={'rows':len(index['inputs'][task]),'max_prompt_tokens':maximum,'over_budget_rows':oversized}
    return {'format':'koevd-local-prompt-budget-v1','scope':'CPU local tokenizer; no model/classifier inference',
            'index_content_sha256':index['content_sha256'],'context_window':context_window,'max_output_tokens':max_tokens,
            'thinking':thinking,'task_prompt_budgets':summary,'all_fit_context':not any(v['over_budget_rows'] for v in summary.values()),
            'generation_verified':False,'classifier_accuracy_verified':False}


def main():
    from koevd_eval.results import read_document
    from transformers import AutoTokenizer,__version__
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trusted-index',required=True);p.add_argument('--tokenizer-dir',required=True)
    p.add_argument('--context-window',type=int,required=True);p.add_argument('--max-tokens',type=int,required=True)
    p.add_argument('--enable-thinking',action='store_true');p.add_argument('--output',required=True)
    args=p.parse_args();out=Path(args.output).absolute();folder=Path(args.tokenizer_dir).resolve(strict=True)
    if out.exists() or any(v.is_symlink() for v in (out,*out.parents)):p.error('Use a fresh output file without symlink parents')
    if not folder.is_dir():p.error('Local tokenizer directory required')
    tokenizer=AutoTokenizer.from_pretrained(folder,local_files_only=True)
    report=measure_budget(read_document(args.trusted_index),tokenizer,context_window=args.context_window,
        max_tokens=args.max_tokens,thinking=args.enable_thinking)
    report['transformers_version']=__version__
    report['tokenizer_file_sha256']={name:hashlib.sha256((folder/name).read_bytes()).hexdigest()
        for name in ('tokenizer_config.json','tokenizer.json') if (folder/name).is_file()}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
    if not report['all_fit_context']:raise SystemExit(2)


if __name__=='__main__':main()
