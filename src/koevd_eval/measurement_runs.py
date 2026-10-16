"""Task-level measurement recovery; immutable attempts precede canonical outputs."""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import uuid

from .common import read_jsonl
from .run_openai_compatible import _output_lock, unique_rows


def _check_rows(predictions, path):
    original=unique_rows(predictions); measured=unique_rows(read_jsonl(path))
    if set(original)!=set(measured) or any(
            any(measured[k].get(f)!=v for f,v in row.items()) for k,row in original.items()):
        raise ValueError('Measured rows must preserve all prediction rows and fields')


def classify_run(output, manifest, safety_adapter, safety_base, strategy_adapter, strategy_base,
                 batch_size=2, *, classifier_dtype=None, input_order='original',
                 inference_mode='batch', trace_measurements=False, measurement_tasks=(3,4), remeasure=False):
    from .pipeline import verify_predictions, artifact_fingerprint, file_sha, save_json
    from .results import read_document, _measurement_evidence
    from .measurement_trace import validate_trace
    from .generation_recovery import require_complete
    require_complete(manifest)
    output=Path(output)
    tasks=tuple(measurement_tasks)
    if not tasks or len(set(tasks))!=len(tasks) or any(t not in (3,4) for t in tasks):
        raise ValueError('Select distinct measurement tasks 3 and/or 4')
    predictions=verify_predictions(output,manifest,3)
    inputs=output/'task3_predictions.jsonl'
    weights={3:(safety_adapter,safety_base),4:(strategy_adapter,strategy_base)}
    root=output/'measurement_attempts'
    if root.is_symlink():raise ValueError('Measurement attempt symlink rejected')
    root.mkdir(exist_ok=True)

    def complete(task, directory, evidence):
        # A pending pointer is committed before changing canonical files. A crash
        # during either replace can therefore finish from this validated attempt.
        directory=directory.resolve(strict=True)
        if not directory.is_relative_to(root.resolve()) or directory.is_symlink():
            raise ValueError('Measurement attempt escapes the run directory')
        source=directory/f'task{task}_measured.jsonl'
        _check_rows(predictions,source)
        if file_sha(source)!=evidence['output_sha256']:raise ValueError('Attempt output changed')
        names=[source.name]
        if evidence.get('trace_sha256'):
            trace=directory/f'task{task}_measurement_trace.json'
            if file_sha(trace)!=evidence['trace_sha256']:raise ValueError('Attempt trace changed')
            validate_trace(read_document(trace),inputs,source,task);names.append(trace.name)
        elif (output/f'task{task}_measurement_trace.json').exists():
            # Preserve an older traced attempt even when explicitly remeasuring
            # without tracing; it no longer describes the canonical output.
            previous=directory/f'previous-task{task}_measurement_trace.json'
            if not previous.exists():shutil.copyfile(output/f'task{task}_measurement_trace.json',previous)
        for name in names:
            destination=output/name
            if destination.is_symlink():raise ValueError('Canonical measurement symlink rejected')
            previous=directory/('previous-'+name)
            if destination.exists() and not previous.exists():shutil.copyfile(destination,previous)
            temporary=output/(name+'.'+uuid.uuid4().hex+'.tmp')
            shutil.copyfile(directory/name,temporary);os.replace(temporary,destination)
        if not evidence.get('trace_sha256'):
            obsolete=output/f'task{task}_measurement_trace.json'
            if obsolete.is_symlink():raise ValueError('Canonical measurement symlink rejected')
            if obsolete.exists():obsolete.unlink()
        manifest.setdefault('measurements',{})[str(task)]=evidence
        manifest.get('measurement_pending',{}).pop(str(task),None)
        if not manifest.get('measurement_pending'):manifest.pop('measurement_pending',None)
        save_json(output/'pipeline.json',manifest)

    with _output_lock(output/'measurement-stage'):
        for task in tasks:
            adapter,base=weights[task]
            if not adapter or not base:raise ValueError('Selected task requires local adapter and base paths')
            config={'prediction_sha256':file_sha(inputs),'batch_size':batch_size,
                'adapter':artifact_fingerprint(adapter),'base':artifact_fingerprint(base),
                'requested_dtype':classifier_dtype or 'auto','input_order':input_order,'inference_mode':inference_mode}
            pending=manifest.get('measurement_pending',{}).get(str(task))
            recovered=bool(pending)
            if pending:
                directory=output/pending
                if not directory.resolve().is_relative_to(root.resolve()):raise ValueError('Invalid pending measurement path')
                journal=read_document(directory/'attempt.json')
                if journal['config']!=config or journal['trace_requested']!=trace_measurements:
                    raise ValueError('Finish the pending measurement with the same settings first')
                complete(task,directory,journal['evidence'])
            existing=manifest.get('measurements',{}).get(str(task))
            if existing:
                # Never turn an integrity failure into an implicit recomputation.
                _measurement_evidence(output,manifest,task,unique_rows(predictions))
                same=all(existing.get(k)==v for k,v in config.items()) and bool(existing.get('trace_sha256'))==trace_measurements
                if same and (not remeasure or recovered):
                    print(f'Reusing completed Task {task} measurements',flush=True);continue
                if not same and not remeasure:
                    raise ValueError('Measurement settings changed; select the failed task with --measurement-tasks or use --remeasure')
            directory=root/f'task{task}-{uuid.uuid4().hex}';directory.mkdir()
            journal={'format':'koevd-measurement-attempt-v1','task':task,'config':config,
                     'trace_requested':trace_measurements,'status':'started'}
            save_json(directory/'attempt.json',journal)
            path=directory/f'task{task}_measured.jsonl';trace=directory/f'task{task}_measurement_trace.json'
            command=[sys.executable,'-m','koevd_eval.classify_responses','--task',str(task),
                '--input',str(inputs),'--output',str(path),'--adapter-path',str(adapter),
                '--base-model-name-or-path',str(base),'--local-files-only','--batch-size',str(batch_size)]
            if classifier_dtype is not None:command.extend(['--torch-dtype',classifier_dtype])
            if input_order!='original':command.extend(['--input-order',input_order])
            if inference_mode!='batch':command.extend(['--inference-mode',inference_mode])
            if trace_measurements:command.extend(['--trace-output',str(trace)])
            print(f'Classifying Task {task}; attempt {directory.name}',flush=True)
            try:
                subprocess.run(command,check=True)
                _check_rows(predictions,path)
                evidence={**config,'output_sha256':file_sha(path),'attempt':directory.relative_to(output).as_posix()}
                if trace_measurements:
                    validate_trace(read_document(trace),inputs,path,task);evidence['trace_sha256']=file_sha(trace)
                journal.update(status='validated',evidence=evidence);save_json(directory/'attempt.json',journal)
                manifest.setdefault('measurement_pending',{})[str(task)]=directory.relative_to(output).as_posix()
                save_json(output/'pipeline.json',manifest)
                complete(task,directory,evidence)
                journal['status']='completed';save_json(directory/'attempt.json',journal)
            except BaseException as exc:
                # Keep partial outputs and traces; a new invocation gets a fresh
                # attempt. A validated pending promotion remains recoverable.
                journal.update(status='interrupted' if isinstance(exc,KeyboardInterrupt) else 'failed',error_type=type(exc).__name__)
                save_json(directory/'attempt.json',journal)
                raise
