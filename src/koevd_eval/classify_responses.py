"""Apply released measurement classifiers; optional frozen-response trace sidecar."""
from __future__ import annotations

import argparse
from pathlib import Path
import time
from typing import Any, Iterable

from .common import configure_cli_stdio, prediction_text, read_jsonl, row_id, write_jsonl


def chunks(values: list[Any], size: int) -> Iterable[list[Any]]:
    for start in range(0, len(values), size):
        yield values[start:start + size]


def build_messages(row: dict[str, Any]) -> list[dict[str, str]]:
    messages = [dict(message) for message in row.get('messages', [])]
    return messages + [{'role': 'assistant', 'content': prediction_text(row)}]


def apply_classifier(rows, classifier, *, batch_size=8, order='original',
                     inference_mode='batch', trace=None, formatter=None):
    if type(batch_size) is not int or batch_size < 1:
        raise ValueError('Classifier batch size must be positive')
    if order not in ('original', 'reverse') or inference_mode not in ('batch', 'single'):
        raise ValueError('Unknown classifier order or inference mode')
    if trace is not None and formatter is None: raise ValueError('Trace requires original formatter')
    processing=list(range(len(rows)))
    if order=='reverse': processing.reverse()
    results, records, calls = {}, {}, 0
    loaded=False
    started=time.perf_counter()
    if trace is not None:
        from .measurement_trace import hash_value, observe_generate, runtime_info, single_reference_tokens
        trace.update(records=[],observed_call_order=[],runtime=None,completed=False)
    try:
        for positions in chunks(processing,batch_size):
            eligible=[p for p in positions if rows[p].get('api_status')=='ok' and prediction_text(rows[p]).strip()]
            for position in positions:
                if trace is not None:
                    records[position]={'original_position':position,'sample_id':row_id(rows[position]),
                        'input_row_sha256':hash_value(rows[position]),
                        'response_sha256':hash_value(prediction_text(rows[position])),
                        'classification_status':'not_applicable' if position not in eligible else 'pending',
                        'observed_generate':None,'measurement_value_sha256':None}
            measured=[]
            groups=[eligible] if inference_mode=='batch' else [[p] for p in eligible]
            for group in groups:
                if not group: continue
                messages=[build_messages(rows[p]) for p in group]
                captured=[]
                if trace is not None:
                    if not loaded:
                        classifier.load();loaded=True
                    prompts=[formatter(m) for m in messages]
                    references=[single_reference_tokens(classifier.tokenizer,p) for p in prompts]
                    calls+=1
                    trace['observed_call_order'].append(list(group))
                    try:
                        with observe_generate(classifier.model,classifier.tokenizer,references,prompts,captured):
                            values=(classifier.predict_batch(messages) if inference_mode=='batch'
                                    else [classifier.predict(messages[0])])
                    finally:
                        for slot,position in enumerate(group):
                            records[position]['generation_call']=calls
                            records[position]['batch_slot']=slot
                            records[position]['observed_generate']=captured[slot] if slot<len(captured) else None
                else:
                    values=(classifier.predict_batch(messages) if inference_mode=='batch'
                            else [classifier.predict(messages[0])])
                if len(values)!=len(group):
                    raise RuntimeError('Classifier returned a different number of results than eligible inputs')
                measured.extend(values)
            by_position={position:value['result'] for position,value in zip(eligible,measured)}
            for position in positions:
                result=dict(rows[position])
                result['measurement']=by_position.get(position)
                result['measurement_error']=None if position in by_position else 'missing_or_failed_generation'
                results[position]=result
                if trace is not None:
                    records[position]['classification_status']='reported' if position in by_position else 'not_applicable'
                    records[position]['measurement_value_sha256']=hash_value(result['measurement'])
        if trace is not None: trace['completed']=True
    except Exception as exc:
        if trace is not None: trace['error_type']=type(exc).__name__
        raise
    finally:
        if trace is not None:
            trace['records']=[records[p] for p in sorted(records)]
            trace['elapsed_seconds_including_observation']=time.perf_counter()-started
            if loaded: trace['runtime']=runtime_info(classifier)
    return [results[p] for p in range(len(rows))]


def main() -> None:
    configure_cli_stdio()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task',type=int,choices=(3,4),required=True)
    parser.add_argument('--input',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--batch-size',type=int,default=8)
    parser.add_argument('--base-model-name-or-path')
    parser.add_argument('--local-files-only',action='store_true')
    parser.add_argument('--torch-dtype',choices=('auto','float16','bfloat16','float32'))
    parser.add_argument('--classifier-max-new-tokens',type=int)
    parser.add_argument('--input-order',choices=('original','reverse'),default='original')
    parser.add_argument('--inference-mode',choices=('batch','single'),default='batch')
    parser.add_argument('--trace-output',help='New private JSON sidecar; observes existing generate calls')
    adapter=parser.add_mutually_exclusive_group(required=True)
    adapter.add_argument('--adapter-path',help='Local HF adapter directory')
    adapter.add_argument('--adapter-repo',help='HF model repo ID')
    parser.add_argument('--revision',help='Required with --adapter-repo')
    args=parser.parse_args()
    if args.batch_size<1 or (args.classifier_max_new_tokens is not None and args.classifier_max_new_tokens<1):
        parser.error('Invalid classifier batch size or token budget')
    input_path,output_path=Path(args.input).resolve(),Path(args.output).resolve()
    if input_path==output_path: parser.error('Measurement output must differ from original predictions')
    if args.trace_output:
        trace_path=Path(args.trace_output).resolve()
        if trace_path in (input_path,output_path) or trace_path.exists() or output_path.exists():
            parser.error('Traced measurements require distinct new trace and output files')
    if args.adapter_repo:
        from .hub import download
        if not args.revision: parser.error('--revision is required with --adapter-repo')
        args.adapter_path=str(download(args.adapter_repo,args.revision,local_files_only=args.local_files_only))
    if not (Path(args.adapter_path)/'adapter_config.json').is_file():
        parser.error('--adapter-path must contain adapter_config.json')
    if args.task==3:
        from koevd_classifiers.assistant_safe_classifier import AssistantSafeClassifier as Classifier, format_openai_messages
    else:
        from koevd_classifiers.response_strategy_classifier import StrategyClassifier as Classifier, format_openai_messages
    kwargs={'local_files_only':args.local_files_only,'adapter_path':args.adapter_path}
    if args.base_model_name_or_path: kwargs['base_model_name_or_path']=args.base_model_name_or_path
    if args.torch_dtype is not None: kwargs['torch_dtype']=args.torch_dtype
    if args.classifier_max_new_tokens is not None: kwargs['max_new_tokens']=args.classifier_max_new_tokens
    rows=list(read_jsonl(args.input))
    classifier=Classifier(**kwargs)
    trace=None
    if args.trace_output:
        from .measurement_trace import VERSION, file_hash, write_trace
        trace={'format':VERSION,'task':args.task,'input_file_sha256':file_hash(args.input),
               'output_file_sha256':None,'batch_size':args.batch_size,'input_order':args.input_order,
               'inference_mode':args.inference_mode,'requested_dtype':args.torch_dtype or 'auto',
               'requested_max_new_tokens':args.classifier_max_new_tokens,
               'interpretation':'Reported generate-call observation, not accuracy or inference authenticity.',
               'finished':False}
    try:
        output_rows=apply_classifier(rows,classifier,batch_size=args.batch_size,order=args.input_order,
            inference_mode=args.inference_mode,trace=trace,formatter=format_openai_messages)
        write_jsonl(args.output,output_rows)
        if trace is not None:
            trace['output_file_sha256']=file_hash(args.output)
            trace['finished']=True
    except Exception as exc:
        if trace is not None:
            trace['completed']=False
            trace['error_type']=type(exc).__name__
        raise
    finally:
        if trace is not None: write_trace(args.trace_output,trace)


if __name__=='__main__': main()
