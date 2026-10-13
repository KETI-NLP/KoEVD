"""Opt-in observation of existing classifier generate calls, without prompt edits.

The sidecar reports observations, not inference authenticity or accuracy. The
model's original generate method is called once and restored after observation.
"""
from __future__ import annotations

from collections import Counter
from contextlib import contextmanager
from collections.abc import Mapping
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import uuid

VERSION = 'koevd-measurement-trace-v1'


def hash_value(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def file_hash(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def _rows(value, *, allow_bool=False):
    if hasattr(value, 'detach'): value=value.detach()
    if hasattr(value, 'cpu'): value=value.cpu()
    if hasattr(value, 'tolist'): value=value.tolist()
    if not isinstance(value, list) or any(not isinstance(row, list) for row in value):
        raise ValueError('Observed tensor must be a two-dimensional token list')
    if any(type(token) is not int and not (allow_bool and type(token) is bool) for row in value for token in row):
        raise ValueError('Observed token IDs must be integers')
    return value


def token_rows(ids, mask=None):
    rows=_rows(ids)
    if mask is None: return rows
    masks=_rows(mask,allow_bool=True)
    if len(rows)!=len(masks) or any(len(a)!=len(b) for a,b in zip(rows,masks)):
        raise ValueError('Observed input/mask shapes differ')
    if any(m not in (0,1) for row in masks for m in row):
        raise ValueError('Observed attention mask is not binary')
    return [[token for token, active in zip(row, flags) if active] for row,flags in zip(rows,masks)]


def single_reference_tokens(tokenizer, prompt):
    encoded=tokenizer.apply_chat_template([{'role':'user','content':prompt}],
        tokenize=True, add_generation_prompt=True, return_tensors='pt')
    if isinstance(encoded, Mapping):
        rows=token_rows(encoded['input_ids'],encoded.get('attention_mask'))
    else: rows=token_rows(encoded)
    if len(rows)!=1: raise ValueError('Single template reference returned multiple rows')
    return rows[0]


def runtime_info(classifier):
    counts=Counter()
    for _, parameter in classifier.model.named_parameters():
        counts[str(parameter.dtype)] += int(parameter.numel())
    config=getattr(classifier.model,'config',None)
    max_positions=getattr(config,'max_position_embeddings',None)
    if type(max_positions) is not int or max_positions<1: max_positions=None
    versions={}
    for package in ('torch','transformers','peft','accelerate'):
        try: versions[package]=importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError: versions[package]=None
    torch=sys.modules.get('torch')
    gpu=None
    if torch is not None:
        available=bool(torch.cuda.is_available())
        gpu={'cuda_available':available,'devices':[]}
        if available:
            for n in range(torch.cuda.device_count()):
                prop=torch.cuda.get_device_properties(n)
                gpu['devices'].append({'index':n,'name':prop.name,'total_memory_bytes':prop.total_memory,
                    'allocated_bytes':torch.cuda.memory_allocated(n),
                    'peak_allocated_bytes_without_reset':torch.cuda.max_memory_allocated(n)})
    return {'parameter_dtype_elements':dict(sorted(counts.items())),
            'model_config_max_position_embeddings':max_positions,
            'tokenizer_class':type(classifier.tokenizer).__name__,
            'tokenizer_model_max_length':getattr(classifier.tokenizer,'model_max_length',None),
            'tokenizer_padding_side':getattr(classifier.tokenizer,'padding_side',None),
            'package_versions':versions,'gpu':gpu}


@contextmanager
def observe_generate(model, tokenizer, references, formatted_prompts, captured):
    """Capture actual input/output IDs; do not alter generate args or output."""
    original=model.generate
    had_instance_method='generate' in vars(model)
    previous_instance_method=vars(model).get('generate')
    calls=0

    def observed(*args, **kwargs):
        nonlocal calls
        calls+=1
        if calls!=1: raise ValueError('Expected one generate call per observed prediction')
        ids=kwargs.get('input_ids')
        if ids is None and args: ids=args[0]
        actual=token_rows(ids,kwargs.get('attention_mask'))
        padded=_rows(ids)
        if len(actual)!=len(references) or len(formatted_prompts)!=len(actual):
            raise ValueError('Observed batch count differs from references')
        width=len(padded[0]) if padded else 0
        if any(len(row)!=width for row in padded): raise ValueError('Ragged observed input tensor')
        for n,tokens in enumerate(actual):
            limit=getattr(getattr(model,'config',None),'max_position_embeddings',None)
            known_limit=type(limit) is int and limit>0
            captured.append({'input_token_count':len(tokens),'padded_input_width':width,
                'padding_token_count':width-len(tokens),'input_token_sha256':hash_value(tokens),
                'single_template_token_count':len(references[n]),
                'single_template_token_sha256':hash_value(references[n]),
                'single_template_tokens_equal':tokens==references[n],
                'formatted_prompt_sha256':hash_value(formatted_prompts[n]),
                'truncation_requested':False,
                'exceeds_declared_model_context':len(tokens)>limit if known_limit else None,
                'generation_kwargs':{k:kwargs.get(k) for k in ('max_new_tokens','do_sample','pad_token_id','eos_token_id')},
                'generation_returned':False})
        output=original(*args,**kwargs)
        output_rows=_rows(output)
        if len(output_rows)!=len(actual): raise ValueError('Observed output batch size differs')
        eos=kwargs.get('eos_token_id')
        eos_ids={eos} if type(eos) is int else set(eos or [])
        for n,row in enumerate(output_rows):
            generated=row[width:]
            first_eos=next((i for i,t in enumerate(generated) if t in eos_ids),None)
            max_new=kwargs.get('max_new_tokens')
            through_eos=generated if first_eos is None else generated[:first_eos+1]
            captured[n].update(generation_returned=True,
                generated_suffix_token_count_with_padding=len(generated),
                generated_token_sha256_with_padding=hash_value(generated),
                generated_tokens_through_first_eos=len(through_eos),first_eos_index=first_eos,
                reached_token_budget_without_eos=(len(generated)>=max_new if type(max_new) is int else None)
                    if first_eos is None else False,
                raw_output=tokenizer.decode(generated,skip_special_tokens=True).strip())
        return output

    model.generate=observed
    try:
        yield
    finally:
        if had_instance_method: model.generate=previous_instance_method
        else: delattr(model,'generate')


def write_trace(path, document):
    path=Path(path)
    if path.exists(): raise ValueError('Trace output already exists')
    path.parent.mkdir(parents=True,exist_ok=True)
    payload=dict(document)
    payload['content_sha256']=hash_value(payload)
    raw=(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')
    temporary=path.with_name(path.name+'.tmp-'+uuid.uuid4().hex)
    try:
        with temporary.open('xb') as handle:
            handle.write(raw);handle.flush();os.fsync(handle.fileno())
        # Hard link provides atomic no-replace publication on the same filesystem.
        os.link(temporary,path)
    finally:
        if temporary.exists(): temporary.unlink()
    return payload


def validate_trace(trace, input_path, output_path, task):
    from .results import _verify_seal
    _verify_seal(trace)
    if (trace.get('format')!=VERSION or trace.get('task')!=task or trace.get('completed') is not True or trace.get('finished') is not True
            or trace.get('input_file_sha256')!=file_hash(input_path)
            or trace.get('output_file_sha256')!=file_hash(output_path)):
        raise ValueError('Missing, incomplete or stale measurement trace')
    from .common import read_jsonl, prediction_text
    originals=list(read_jsonl(input_path));measured=list(read_jsonl(output_path))
    rows=trace.get('records')
    if not isinstance(rows,list) or len(rows)!=len(originals) or len(measured)!=len(originals):
        raise ValueError('Trace record count differs from frozen inputs')
    batch_size=trace.get('batch_size')
    mode,order=trace.get('inference_mode'),trace.get('input_order')
    if type(batch_size) is not int or batch_size<1 or mode not in ('single','batch') or order not in ('original','reverse'):
        raise ValueError('Invalid observed classifier scheduling')
    positions=list(range(len(originals)))
    if order=='reverse':positions.reverse()
    groups=[]
    for start in range(0,len(positions),batch_size):
        eligible=[p for p in positions[start:start+batch_size]
                  if originals[p].get('api_status')=='ok' and prediction_text(originals[p]).strip()]
        if eligible:groups.extend([eligible] if mode=='batch' else [[p] for p in eligible])
    if trace.get('observed_call_order')!=groups:
        raise ValueError('Observed generate order differs from declared scheduling')
    membership={position:(number,slot) for number,group in enumerate(groups,1) for slot,position in enumerate(group)}
    for position,(a,b,record) in enumerate(zip(originals,measured,rows)):
        if not isinstance(record,dict):raise ValueError('Invalid trace record')
        if any(b.get(k)!=v for k,v in a.items() if k not in ('measurement','measurement_error')):
            raise ValueError('Measured rows changed frozen generation fields')
        if (record.get('original_position')!=position or record.get('input_row_sha256')!=hash_value(a)
                or record.get('response_sha256')!=hash_value(prediction_text(a))
                or record.get('measurement_value_sha256')!=hash_value(b.get('measurement'))):
            raise ValueError('Trace input/response/measurement binding differs')
        observed=record.get('observed_generate')
        if position not in membership:
            if observed is not None or record.get('classification_status')!='not_applicable' or b.get('measurement') is not None:
                raise ValueError('Failed/empty generation has unexpected observation')
            continue
        if (record.get('generation_call'),record.get('batch_slot'))!=membership[position]:
            raise ValueError('Observed call/slot binding differs')
        if record.get('classification_status')!='reported' or not isinstance(observed,dict) or observed.get('generation_returned') is not True:
            raise ValueError('Missing successful generate observation')
        for field in ('input_token_count','padded_input_width','padding_token_count',
                      'single_template_token_count','generated_suffix_token_count_with_padding','generated_tokens_through_first_eos'):
            if type(observed.get(field)) is not int or observed[field]<0:
                raise ValueError('Invalid observed token count')
        if observed['padded_input_width']-observed['input_token_count']!=observed['padding_token_count']:
            raise ValueError('Inconsistent padding count')
        for field in ('input_token_sha256','single_template_token_sha256','formatted_prompt_sha256','generated_token_sha256_with_padding'):
            check=observed.get(field)
            if not isinstance(check,str) or len(check)!=64 or any(c not in '0123456789abcdef' for c in check):
                raise ValueError('Invalid observed token hash')
        equal=(observed['input_token_sha256']==observed['single_template_token_sha256']
               and observed['input_token_count']==observed['single_template_token_count'])
        if type(observed.get('single_template_tokens_equal')) is not bool or observed['single_template_tokens_equal']!=equal:
            raise ValueError('Inconsistent token parity observation')
        from .measurement_conditions import validate_options
        validate_options(observed.get('generation_kwargs'))
        if observed.get('truncation_requested') is not False:
            raise ValueError('Unexpected truncation request in original wrapper observation')
        context = observed.get('exceeds_declared_model_context')
        if context is not None and type(context) is not bool:
            raise ValueError('Invalid observed context status')
        suffix, through = observed['generated_suffix_token_count_with_padding'], observed['generated_tokens_through_first_eos']
        eos = observed.get('first_eos_index')
        if eos is not None and (type(eos) is not int or not 0 <= eos < suffix):
            raise ValueError('Invalid observed first EOS position')
        if through != (suffix if eos is None else eos + 1):
            raise ValueError('Inconsistent observed generated token count')
        budget = observed['generation_kwargs']['max_new_tokens']
        expected_budget = eos is None and suffix >= budget
        if type(observed.get('reached_token_budget_without_eos')) is not bool or observed['reached_token_budget_without_eos'] != expected_budget:
            raise ValueError('Inconsistent observed token budget status')
        requested = trace.get('requested_max_new_tokens')
        if requested is not None and budget != requested:
            raise ValueError('Observed generate budget differs from requested override')
        raw=observed.get('raw_output')
        if not isinstance(raw,str):raise ValueError('Missing observed raw output')
        value=b.get('measurement')
        if isinstance(value,dict) and 'raw_output' in value and value['raw_output']!=raw:
            raise ValueError('Observed raw output differs from reported measurement')
    return trace
