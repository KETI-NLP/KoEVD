"""Build a bounded private GPU return from completed runs; no cloud publication.

Include replay inputs/predictions/measurements/traces and stage logs. Independent
indexes, credentials, weights and duplicated HTML/case exports stay outside the
ZIP. Receiver must independently re-export and rebuild reports after intake.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

spec=importlib.util.spec_from_file_location('gpu_return_checks',Path(__file__).with_name('accept_gpu_results_bundle.py'))
intake=importlib.util.module_from_spec(spec);spec.loader.exec_module(intake)


def pack(root,output,index,*,registry=None,protocol_id=None):
    root=Path(root).resolve(strict=True);output=Path(output).absolute()
    if output.exists() or any(p.is_symlink() for p in (output,*output.parents)):
        raise ValueError('Use a fresh output path without symlink parents')
    files={}
    def add(relative):
        relative=intake.safe_name(relative);path=root/relative
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p!=root):raise ValueError('Symlink return member')
        if not path.is_file() or path.stat().st_size>intake.MAX_FILE:raise ValueError('Missing or oversized replay member')
        raw=path.read_bytes()
        if len(raw)>intake.MAX_FILE:raise ValueError('Replay member grew beyond limit')
        name=intake.safe_name(root.name+'/'+relative);files[name]=raw
        if len(files)>intake.MAX_FILES or sum(len(v) for v in files.values())>intake.MAX_TOTAL:
            raise ValueError('Private replay bundle exceeds intake limits')
    state=json.loads((root/'checks/status.json').read_text(encoding='utf-8'))
    if state.get('status')!='passed_generation_measurement_export_report_comparison':
        raise ValueError('Wait for terminal successful generation/measurement/export/report/comparison')
    targets=state.get('targets')
    if not isinstance(targets,list) or len(targets)!=2:raise ValueError('Two target runs required')
    add('checks/status.json')
    for target in targets:
        name=target['model'].split('/')[-1];intake.safe_name(name)
        add(name+'/results.json');add(name+'/run/pipeline.json')
        manifest=json.loads(files[root.name+'/'+name+'/run/pipeline.json'])
        for task in (1,2,3,5):
            add(name+f'/run/task{task}_input.jsonl');add(name+f'/run/task{task}_predictions.jsonl')
        for task in (3,4):
            if str(task) in manifest.get('measurements',{}) or (root/name/f'run/task{task}_measured.jsonl').exists():
                add(name+f'/run/task{task}_measured.jsonl')
                if manifest.get('measurements',{}).get(str(task),{}).get('trace_sha256') is not None:
                    add(name+f'/run/task{task}_measurement_trace.json')
        if (root/name/'model-provenance.json').is_file():add(name+'/model-provenance.json')
    for path in sorted((root/'checks').glob('*.log')):add('checks/'+path.name)
    manifest={'format':intake.FORMAT,'scope':'bounded_private_replay_only; reports must be rebuilt by receiver',
        'files':{name:{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()} for name,raw in files.items()}}
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        archive.writestr('bundle-manifest.json',json.dumps(manifest,indent=2)+'\n')
        for name,raw in files.items():archive.writestr(name,raw)
    checksum=hashlib.sha256(output.read_bytes()).hexdigest()
    _,receipt=intake.verify_bundle(output,checksum,index,registry=registry,protocol_id=protocol_id)
    return {'path':str(output),'bytes':output.stat().st_size,'sha256':checksum,'files':len(files),
            'expanded_bytes':sum(len(v) for v in files.values()),'outside_input_envelope_verified':True,
            'full_standard_inputs_verified':receipt['full_standard_inputs_verified'],
            'receiver_independent_reexport_required':True,'reports_included':False,'published':False,
            'generation_authenticity_verified':False,'classifier_accuracy_verified':False}


def main():
    from koevd_eval.results import read_document
    from koevd_eval.protocols import ProtocolRegistry
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-root',required=True)
    p.add_argument('--output',required=True);p.add_argument('--trusted-index',required=True)
    p.add_argument('--registry');p.add_argument('--protocol-id');args=p.parse_args()
    if bool(args.registry)!=bool(args.protocol_id):p.error('Supply outside registry and protocol ID together')
    receipt=pack(args.run_root,args.output,read_document(args.trusted_index),
        registry=ProtocolRegistry(args.registry) if args.registry else None,protocol_id=args.protocol_id)
    print(json.dumps(receipt))


if __name__=='__main__':main()
