"""Prepare, generate, measure and report a complete own-model KoEVD run."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from datetime import datetime, timezone

from .common import read_jsonl, write_jsonl, row_id
from .overlap import source_id
from .prepare_tasks import prepare
from .profile import write_report, identity
from .run_openai_compatible import (run_rows, endpoint, unique_rows, make_config,
                                   add_execution_arguments, load_options, print_progress)

TASK2_VARIANTS = ('choose_best', 'choose_unsafe', 'rejected_vs_accepted', 'relative_harmfulness')
TASK5_VARIANTS = ('safe_guided', 'tool_forced', 'unsafe_induced')


def file_sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''): result.update(chunk)
    return result.hexdigest()


def save_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    os.replace(temporary, path)


def prepare_run(dataset, output, split='core', limit_sources=None):
    dataset, output = Path(dataset), Path(output)
    split_path = dataset/'benchmark_splits'/f'{split}.jsonl'
    corpus = dataset/'full_eval/koevd_full_eval.jsonl'
    if limit_sources is not None and limit_sources < 1: raise ValueError('limit-sources must be positive')
    if not split_path.is_file(): raise ValueError(f'Missing split: {split_path}')
    config = {'split': split, 'limit_sources': limit_sources, 'selection': 'source_id sorted prefix; use full split for interpretation'}
    selected_ids = sorted({str(r['source_id']) for r in read_jsonl(split_path)})
    if limit_sources: selected_ids = selected_ids[:limit_sources]
    selected = set(selected_ids)
    t5_files = [dataset/'tasks/task5_tool_action_choice_safety/main'/f'{v}.jsonl' for v in TASK5_VARIANTS]
    tool_rows = [list(read_jsonl(p)) for p in t5_files]
    tool_sets = [{source_id(r) for r in rows} for rows in tool_rows]
    if not tool_sets[0] or any(ids != tool_sets[0] for ids in tool_sets):
        raise ValueError('Task 5 framings must contain the same nonempty source set')
    tool_ids = sorted(tool_sets[0])
    if limit_sources: tool_ids = tool_ids[:limit_sources]
    tool_selected = set(tool_ids)
    t2_files = [dataset/'tasks/task2_candidate_response_safety_choice/full_eval'/f'{v}.jsonl' for v in TASK2_VARIANTS]
    used = [corpus, split_path, *t2_files, *t5_files]
    config['dataset_files'] = {str(p.relative_to(dataset)).replace('\\','/'): file_sha(p) for p in used}
    manifest_path = output/'pipeline.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        if manifest['preparation'] != config: raise ValueError('Dataset/selection changed; use a new output directory')
        verify_prepared(output, manifest)
        return manifest
    if output.exists() and any(output.iterdir()):
        raise ValueError('Use an empty output directory for a new pipeline run')
    output.mkdir(parents=True, exist_ok=True)
    rows1 = [r for r in prepare(str(corpus), 1) if source_id(r) in selected]
    rows3 = [r for r in prepare(str(corpus), 3) if source_id(r) in selected | tool_selected]
    if {source_id(r) for r in rows1} != selected or {source_id(r) for r in rows3} != selected | tool_selected:
        raise ValueError('Selected source IDs are absent from the canonical corpus')
    # T3 includes extra tool sources to make source-matched transition analysis possible.
    for row in rows3:
        sid=source_id(row)
        row['metadata']['evaluation_subset'] = ([split] if sid in selected else []) + (['task5_overlap'] if sid in tool_selected else [])
    rows2 = [r for p in t2_files for r in read_jsonl(p) if source_id(r) in selected]
    rows5 = [r for rows in tool_rows for r in rows if source_id(r) in tool_selected]
    tasks={1: rows1, 2: rows2, 3: rows3, 5: rows5}
    for task, rows in tasks.items():
        unique_rows(rows)
        if not rows: raise ValueError(f'Task {task} selected no rows')
    manifest={'format': 'koevd-pipeline-v1', 'preparation': config, 'inputs': {},
              'primary_sources': len(selected), 'tool_sources': len(tool_selected),
              'task3_union_sources': len(selected | tool_selected),
              'note': 'Task 3 overall uses the source union; use evaluation_subset groups for split-specific results. Task 4 reuses these exact generations.'}
    for task, rows in tasks.items():
        path=output/f'task{task}_input.jsonl'; write_jsonl(path, rows)
        manifest['inputs'][str(task)]={'file': path.name, 'sha256': file_sha(path), 'rows': len(rows)}
    save_json(manifest_path, manifest)
    return manifest


def verify_prepared(output, manifest):
    for entry in manifest['inputs'].values():
        if file_sha(Path(output)/entry['file']) != entry['sha256']:
            raise ValueError('Prepared inputs changed; use a new run directory')


def verify_predictions(output, manifest, task):
    inputs=unique_rows(read_jsonl(output/manifest['inputs'][str(task)]['file']))
    predictions=unique_rows(read_jsonl(output/f'task{task}_predictions.jsonl'))
    if set(inputs) != set(predictions):
        raise ValueError(f'Task {task}: missing/extra prediction rows; complete generation before reporting')
    for key, row in predictions.items():
        if identity(row) != identity(inputs[key]) or row.get('evaluated_model') != manifest['generation']['model']:
            raise ValueError(f'Task {task}: predictions do not match prepared inputs/model')
    return list(predictions.values())


def generate_run(output, manifest, *, base_url, model, api_key='', temperature=0., max_tokens=1024,
                 retries=2, timeout=120, workers=1, retry_delay=2, progress=None,
                 extra_body=None, engine_version=None, model_provenance=None, preflight=False):
    config=make_config(base_url,model,temperature,max_tokens,extra_body=extra_body,
                       engine_version=engine_version,model_provenance=model_provenance)
    if 'generation' in manifest and manifest['generation'] != config:
        raise ValueError('Generation settings changed; use a new output directory')
    manifest['generation']=config
    manifest.setdefault('generation_run',{'id':str(uuid.uuid4()),'created_at':datetime.now(timezone.utc).isoformat()})
    save_json(output/'pipeline.json', manifest)
    if preflight:
        from .preflight import preflight as check
        rows=[row for task in (1,2,3,5) for row in read_jsonl(output/f'task{task}_input.jsonl')]
        save_json(output/'preflight.json',check(config,rows,api_key=api_key,timeout=timeout))
    for task in (1, 2, 3, 5):
        print(f'Generating Task {task}', flush=True)
        run_rows(list(read_jsonl(output/f'task{task}_input.jsonl')), output/f'task{task}_predictions.jsonl', config,
                 api_key=api_key, timeout=timeout, retries=retries, retry_delay=retry_delay, resume=True,
                 workers=workers,progress=progress,run_id=manifest['generation_run']['id'])


def artifact_fingerprint(directory):
    directory=Path(directory)
    configs=sorted(directory.glob('*.json'))
    weights=sorted(directory.glob('*.safetensors')) + sorted(directory.glob('*.bin'))
    if not configs or not weights: raise ValueError(f'Missing local model configuration or weights: {directory}')
    return {p.name:file_sha(p) for p in [*configs,*weights]}


def classify_run(output, manifest, safety_adapter, safety_base, strategy_adapter, strategy_base, batch_size=2,
                 *, classifier_dtype=None, input_order='original', inference_mode='batch', trace_measurements=False):
    verify_predictions(output, manifest, 3)
    measurements={}
    for task, adapter, base in ((3,safety_adapter,safety_base),(4,strategy_adapter,strategy_base)):
        if not adapter or not base: raise ValueError('Both local adapters and base-model paths are required for classification')
        print(f'Classifying Task {task}', flush=True)
        provenance={'prediction_sha256':file_sha(output/'task3_predictions.jsonl'), 'batch_size':batch_size,
                    'adapter':artifact_fingerprint(adapter), 'base':artifact_fingerprint(base),
                    'requested_dtype':classifier_dtype or 'auto', 'input_order':input_order,
                    'inference_mode':inference_mode}
        path=output/f'task{task}_measured.jsonl'
        command=[sys.executable,'-m','koevd_eval.classify_responses','--task',str(task),
                 '--input',str(output/'task3_predictions.jsonl'),'--output',str(path),
                 '--adapter-path',str(adapter),'--base-model-name-or-path',str(base),
                 '--local-files-only','--batch-size',str(batch_size)]
        if classifier_dtype is not None: command.extend(['--torch-dtype',classifier_dtype])
        if input_order!='original': command.extend(['--input-order',input_order])
        if inference_mode!='batch': command.extend(['--inference-mode',inference_mode])
        trace_path=output/f'task{task}_measurement_trace.json'
        if trace_measurements: command.extend(['--trace-output',str(trace_path)])
        # Separate processes release each classifier's GPU allocations before loading the next.
        subprocess.run(command,check=True)
        if trace_measurements:
            from .measurement_trace import validate_trace
            from .results import read_document
            validate_trace(read_document(trace_path),output/'task3_predictions.jsonl',path,task)
            provenance['trace_sha256']=file_sha(trace_path)
        measurements[str(task)]={**provenance,'output_sha256':file_sha(path)}
    manifest['measurements']=measurements; save_json(output/'pipeline.json',manifest)


def report_run(output, manifest, min_sources=20, min_coverage=.9):
    for task in (1,2,3,5): verify_predictions(output,manifest,task)
    for task in (3,4):
        evidence=manifest.get('measurements',{}).get(str(task))
        path=output/f'task{task}_measured.jsonl'
        if not evidence or evidence['prediction_sha256'] != file_sha(output/'task3_predictions.jsonl') or evidence['output_sha256'] != file_sha(path):
            raise ValueError('Measurements missing/stale; rerun the classify stage')
        inputs=unique_rows(read_jsonl(output/'task3_predictions.jsonl')); rows=unique_rows(read_jsonl(path))
        if set(inputs)!=set(rows) or any(any(rows[k].get(f)!=inputs[k].get(f) for f in inputs[k]) for k in inputs):
            raise ValueError('Measured rows must preserve all generation rows and fields')
    paths={t:[output/f'task{t}_measured.jsonl'] if t in (3,4) else [output/f'task{t}_predictions.jsonl'] for t in range(1,6)}
    return write_report(paths, output/'report', min_sources, min_coverage)


def main():
    from .common import configure_cli_stdio
    configure_cli_stdio()
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',choices=('prepare','preflight','generate','classify','report','all'),default='all')
    p.add_argument('--dataset-dir'); p.add_argument('--output-dir',required=True)
    p.add_argument('--split',default='core'); p.add_argument('--limit-sources',type=int)
    p.add_argument('--base-url'); p.add_argument('--model'); p.add_argument('--api-key-env',default='OPENAI_API_KEY')
    p.add_argument('--temperature',type=float,default=0.); p.add_argument('--max-tokens',type=int,default=1024)
    p.add_argument('--retries',type=int,default=2); p.add_argument('--timeout',type=float,default=120)
    add_execution_arguments(p)
    for arg in ('safety-adapter','safety-base','strategy-adapter','strategy-base'): p.add_argument('--'+arg)
    p.add_argument('--batch-size',type=int,default=2)
    p.add_argument('--classifier-dtype',choices=('auto','float16','bfloat16','float32'))
    p.add_argument('--measurement-order',choices=('original','reverse'),default='original')
    p.add_argument('--measurement-mode',choices=('batch','single'),default='batch')
    p.add_argument('--trace-measurements',action='store_true',help='New private token/dtype/order sidecars')
    p.add_argument('--min-sources',type=int,default=20); p.add_argument('--min-coverage',type=float,default=.9)
    a=p.parse_args(); output=Path(a.output_dir)
    if a.batch_size<1 or a.retries<0 or a.max_tokens<1: p.error('Invalid batch size, retries or max tokens')
    if a.stage in ('all','generate','preflight') and (not a.base_url or not a.model): p.error('--base-url and --model are required to generate')
    if a.stage in ('all','classify') and not all((a.safety_adapter,a.safety_base,a.strategy_adapter,a.strategy_base)):
        p.error('Both local adapter and base paths are required for classification')
    if a.stage in ('all','prepare'):
        if not a.dataset_dir: p.error('--dataset-dir is required to prepare')
        manifest=prepare_run(a.dataset_dir,output,a.split,a.limit_sources)
    else: manifest=json.loads((output/'pipeline.json').read_text(encoding='utf-8'))
    verify_prepared(output,manifest)
    if a.stage=='preflight':
        from .preflight import preflight
        config=make_config(a.base_url,a.model,a.temperature,a.max_tokens,extra_body=load_options(a.extra_body_file))
        rows=[row for task in (1,2,3,5) for row in read_jsonl(output/f'task{task}_input.jsonl')]
        save_json(output/'preflight.json',preflight(config,rows,api_key=os.environ.get(a.api_key_env,''),timeout=a.timeout))
    if a.stage in ('all','generate'):
        generate_run(output,manifest,base_url=a.base_url,model=a.model,api_key=os.environ.get(a.api_key_env,''),temperature=a.temperature,max_tokens=a.max_tokens,retries=a.retries,timeout=a.timeout,
                     workers=a.workers,retry_delay=a.retry_delay,progress=print_progress,preflight=a.preflight,
                     extra_body=load_options(a.extra_body_file),engine_version=a.engine_version,
                     model_provenance=load_options(a.model_provenance_file))
    if a.stage in ('all','classify'):
        classify_run(output,manifest,a.safety_adapter,a.safety_base,a.strategy_adapter,a.strategy_base,a.batch_size,
                     classifier_dtype=a.classifier_dtype,input_order=a.measurement_order,
                     inference_mode=a.measurement_mode,trace_measurements=a.trace_measurements)
    if a.stage in ('all','report'): report_run(output,manifest,a.min_sources,a.min_coverage)
    print(output.resolve())


if __name__ == '__main__': main()
