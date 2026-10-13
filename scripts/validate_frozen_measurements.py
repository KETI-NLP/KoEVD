"""Private GPU measurement matrix on unchanged completed target generations.

Never generates target responses, edits baseline files, creates human gold or
changes ranking. CPU tests cover orchestration only; execution needs the node's
verified setup/artifacts and an idle explicitly selected GPU.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time


VARIANTS = {
    'traced-repeat-b2': (2, 'original', 'batch', 'bfloat16', True),
    'untraced-b2': (2, 'original', 'batch', 'bfloat16', False),
    'traced-b1': (1, 'original', 'batch', 'bfloat16', True),
    'traced-b4': (4, 'original', 'batch', 'bfloat16', True),
    'traced-reverse-b2': (2, 'reverse', 'batch', 'bfloat16', True),
    'traced-single': (1, 'original', 'single', 'bfloat16', True),
    'traced-fp32-b2': (2, 'original', 'batch', 'float32', True),
}


def sha(path):
    value=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):value.update(block)
    return value.hexdigest()


def frozen_files(run):
    """Only prepared inputs and generation outputs; no journal/old measurement."""
    run=Path(run)
    names={f'task{task}_{kind}.jsonl' for task in (1,2,3,5) for kind in ('input','predictions')}
    result={}
    for name in sorted(names):
        path=run/name
        if path.is_symlink() or not path.is_file():raise ValueError('Missing regular frozen generation file: '+name)
        result[name]=sha(path)
    return result


def clone_generation(source, destination):
    """Retain every generation byte/config, strip only measurement declarations."""
    from koevd_eval.pipeline import verify_prepared, verify_predictions
    from koevd_eval.results import read_document
    source,destination=Path(source),Path(destination).absolute()
    if any(p.is_symlink() for p in (destination,*destination.parents)):
        raise ValueError('Clone destination traverses a symlink')
    frozen=frozen_files(source)
    manifest=read_document(source/'pipeline.json')
    verify_prepared(source,manifest)
    for task in (1,2,3,5):verify_predictions(source,manifest,task)
    manifest['measurements']={}
    destination.mkdir(parents=True,exist_ok=False)
    for name in frozen:shutil.copyfile(source/name,destination/name)
    (destination/'pipeline.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if frozen_files(destination)!=frozen or frozen_files(source)!=frozen:
        raise ValueError('Frozen generation changed during clone')
    return frozen


def classifier_command(root, run, artifacts, variant):
    batch,order,mode,dtype,trace=VARIANTS[variant]
    args=[str(Path(root)/'envs/measure/bin/koevd-pipeline'),'--stage','classify','--output-dir',str(run),
        '--safety-adapter',artifacts['assistant']['snapshot'],'--safety-base',artifacts['assistant_base']['snapshot'],
        '--strategy-adapter',artifacts['strategy']['snapshot'],'--strategy-base',artifacts['strategy_base']['snapshot'],
        '--batch-size',str(batch),'--classifier-dtype',dtype,'--measurement-order',order,'--measurement-mode',mode]
    if trace:args.append('--trace-measurements')
    return args


def gpu_index(inventory, uuid):
    matches=[row[0].strip() for row in csv.reader(inventory.splitlines()) if len(row)==2 and row[1].strip()==uuid]
    if len(matches)!=1 or not matches[0].isascii() or not matches[0].isdigit():
        raise ValueError('GPU UUID does not uniquely select an integer device')
    return matches[0]


def main():
    from koevd_eval.results import read_document, export_run, validate_results
    from koevd_eval.measurement_audit import compare_measurements
    from koevd_eval.measurement_trace import validate_trace
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True)
    parser.add_argument('--baseline-attempt',required=True)
    parser.add_argument('--attempt',required=True)
    parser.add_argument('--gpu-uuid',required=True)
    parser.add_argument('--variant',action='append',choices=tuple(VARIANTS))
    args=parser.parse_args()
    for label in (args.baseline_attempt,args.attempt):
        if not re.fullmatch('[a-z0-9][a-z0-9-]{0,63}',label):parser.error('Invalid fresh attempt label')
    variants=args.variant or list(VARIANTS)
    if len(set(variants))!=len(variants):parser.error('Duplicate measurement variant')
    root=Path(args.root).resolve(strict=True)
    baseline=root/args.baseline_attempt
    state=read_document(baseline/'checks/status.json')
    if state.get('status')!='passed_generation_measurement_export_report_comparison':
        parser.error('Require a completed two-target baseline')
    targets=state.get('targets')
    if not isinstance(targets,list) or len(targets)!=2 or len({t['model'] for t in targets})!=2:
        parser.error('Require exactly two distinct targets')
    artifacts=read_document(root/'environment/artifact-receipt.json')
    if artifacts.get('status')!='passed':parser.error('Verified artifact receipt required')
    artifacts=artifacts['artifacts']
    out=root/('measurement-matrix-'+args.attempt)
    if any(p.is_symlink() for p in (out,*out.parents)):parser.error('Output traverses symlink')
    out.mkdir(exist_ok=False);logs=out/'checks';logs.mkdir()
    evidence={'scope':'two_actual_target_frozen_response_measurement_matrix','status':'running',
        'baseline_attempt':args.baseline_attempt,'variants':variants,'commands':[],'targets':[],
        'controller_sha256':sha(__file__),
        'human_gold_created':False,'classifier_accuracy_verified':False,'official_rank_eligible':False}
    env={**os.environ,'CUDA_DEVICE_ORDER':'PCI_BUS_ID','PYTHONDONTWRITEBYTECODE':'1','HF_HUB_OFFLINE':'1'}

    def save():
        p=logs/'status.json';tmp=p.with_suffix('.tmp')
        tmp.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(p)

    def idle():
        memory=subprocess.check_output(['nvidia-smi','--id='+args.gpu_uuid,'--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True)
        if int(memory.strip())>=256:raise RuntimeError('Selected GPU is occupied; no other process will be stopped')

    def execute(name, command):
        item={'name':name,'argv':command,'status':'running'};evidence['commands'].append(item);save()
        print('START '+name,flush=True);started=time.monotonic()
        with (logs/(name+'.log')).open('x') as stream:
            result=subprocess.run(command,env=env,stdout=stream,stderr=subprocess.STDOUT)
        item.update(exit_code=result.returncode,elapsed_seconds=time.monotonic()-started,
                    status='passed' if result.returncode==0 else 'failed');save()
        if result.returncode:raise RuntimeError('Measurement stage failed; preserved log: '+name)
        print('PASS '+name,flush=True)

    save()
    try:
        inventory=subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid','--format=csv,noheader'],text=True)
        env['CUDA_VISIBLE_DEVICES']=gpu_index(inventory,args.gpu_uuid);idle()
        probe='import torch,json;print(json.dumps({"uuid":str(torch.cuda.get_device_properties(0).uuid),"torch":torch.__version__,"cuda":torch.version.cuda,"matmul_allow_tf32":torch.backends.cuda.matmul.allow_tf32,"cudnn_allow_tf32":torch.backends.cudnn.allow_tf32,"float32_matmul_precision":torch.get_float32_matmul_precision()}))'
        runtime=json.loads(subprocess.check_output([str(root/'envs/measure/bin/python'),'-c',probe],env=env,text=True))
        if runtime['uuid'].removeprefix('GPU-')!=args.gpu_uuid.removeprefix('GPU-'):
            raise ValueError('Actual CUDA UUID differs from requested GPU')
        evidence['gpu_selection']={'requested_uuid':args.gpu_uuid,'mask':env['CUDA_VISIBLE_DEVICES'],'runtime_probe':runtime};save()
        for target in targets:
            name=target['model'].split('/')[-1]
            if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._-]{0,127}',name):raise ValueError('Invalid target folder name')
            folder=baseline/name
            index=read_document(folder/'trusted-input-index.json')
            original=read_document(folder/'results.json');validate_results(original,index)
            if (original['run']['model']['id']!=target['model']
                    or original['run']['model']['revision']!=target['revision']):
                raise ValueError('Baseline target identity differs from execution receipt')
            if original!=export_run(folder/'run',index):raise ValueError('Baseline raw re-export differs')
            frozen=frozen_files(folder/'run')
            for task in (1,2,3,5):
                if target.get('generation',{}).get(str(task),{}).get('prediction_sha256')!=frozen[f'task{task}_predictions.jsonl']:
                    raise ValueError('Frozen generation differs from completed execution receipt')
            report={'model':target['model'],'revision':target['revision'],'baseline_artifact_sha256':original['content_sha256'],
                    'frozen_file_sha256':frozen,'comparisons':[]}
            evidence['targets'].append(report);save()
            for variant in variants:
                idle();dest=out/name/variant
                clone_generation(folder/'run',dest/'run')
                execute(name+'-'+variant,classifier_command(root,dest/'run',artifacts,variant))
                if frozen_files(dest/'run')!=frozen or frozen_files(folder/'run')!=frozen:
                    raise ValueError('Original generation bytes changed during measurement')
                value=export_run(dest/'run',index)
                (dest/'results.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                comparison=compare_measurements(original,value,index,variant_id=variant)
                observations={}
                if VARIANTS[variant][-1]:
                    expected_dtype='torch.'+VARIANTS[variant][3]
                    for task in (3,4):
                        trace=read_document(dest/'run'/f'task{task}_measurement_trace.json')
                        validate_trace(trace,dest/'run/task3_predictions.jsonl',dest/'run'/f'task{task}_measured.jsonl',task)
                        counts=trace['runtime']['parameter_dtype_elements']
                        if not counts.get(expected_dtype,0):raise ValueError('Requested dtype absent from actual parameter observation')
                        observations[str(task)]={'parameter_dtype_elements':counts,
                            'observed_call_order':trace['observed_call_order'],'trace_file_sha256':sha(dest/'run'/f'task{task}_measurement_trace.json')}
                summary={'variant_id':variant,'artifact_sha256':value['content_sha256'],'comparison':comparison,
                         'trace_observations':observations,'status':'passed_frozen_measurement_export_compare'}
                (dest/'comparison.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                report['comparisons'].append(summary);save()
            if original!=read_document(folder/'results.json') or frozen_files(folder/'run')!=frozen:
                raise ValueError('Baseline changed while auditing')
        evidence['status']='passed_frozen_measurement_matrix'
        evidence['interpretation']='Stability on fixed responses only; no causal batch attribution, human accuracy certification or rank promotion'
    except BaseException as error:
        evidence.update(status='failed',error_type=type(error).__name__,error=str(error));raise
    finally:save()


if __name__=='__main__':main()
