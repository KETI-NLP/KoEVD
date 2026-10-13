"""Verify and accept a GPU return bundle against independently supplied inputs.

Checks file consistency and reported execution/coverage, not cryptographic model
authenticity, classifier accuracy, publication permission or official ranking.
Never runs archive code or trusts an archived index as operator gold.
"""
import argparse
import hashlib
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

FORMAT = 'koevd-platform-gpu-results-bundle-v1'
MAX_TOTAL, MAX_FILE, MAX_FILES = 512*1024**2, 256*1024**2, 2000


def safe_name(name):
    p=PurePosixPath(name)
    reserved={'con','prn','aux','nul',*[f'com{i}' for i in range(1,10)],*[f'lpt{i}' for i in range(1,10)]}
    if (not name or p.is_absolute() or p.as_posix()!=name or '..' in p.parts or '\\' in name or ':' in name
            or any(ord(c)<32 for c in name)
            or any(part.endswith(('.', ' ')) or part.split('.')[0].casefold() in reserved for part in p.parts)):
        raise ValueError('Unsafe archive member path')
    return name


def read_snapshot(path):
    with Path(path).open('rb') as stream:
        raw=stream.read(MAX_TOTAL+1)
    if len(raw)>MAX_TOTAL:raise ValueError('Archive exceeds intake limit')
    return raw


def verify_bundle(path, expected_sha256, trusted_index, *, archive_bytes=None, registry=None, protocol_id=None):
    from koevd_eval.results import _unique_object, validate_results
    if not re.fullmatch('[0-9a-f]{64}',expected_sha256):raise ValueError('Expected an independent SHA-256')
    raw_archive=read_snapshot(path) if archive_bytes is None else archive_bytes
    if len(raw_archive)>MAX_TOTAL:raise ValueError('Archive exceeds intake limit')
    if hashlib.sha256(raw_archive).hexdigest()!=expected_sha256:raise ValueError('External archive SHA-256 mismatch')
    parse=lambda raw:json.loads(raw.decode('utf-8'),object_pairs_hook=_unique_object)
    with zipfile.ZipFile(BytesIO(raw_archive)) as archive:
        entries=archive.infolist();names=[safe_name(e.filename) for e in entries]
        if (len(entries)>MAX_FILES+1 or sum(e.file_size for e in entries)>MAX_TOTAL
                or any(e.is_dir() or e.file_size>MAX_FILE or e.flag_bits&1 or stat.S_ISLNK(e.external_attr>>16) for e in entries)):
            raise ValueError('Unsupported archive entries or expansion limit')
        if len({n.casefold() for n in names})!=len(names):raise ValueError('Duplicate or case-colliding archive members')
        if 'bundle-manifest.json' not in names or archive.getinfo('bundle-manifest.json').file_size>16*1024**2:
            raise ValueError('Missing or oversized bundle manifest')
        manifest=parse(archive.read('bundle-manifest.json'))
        if not isinstance(manifest,dict) or manifest.get('format')!=FORMAT or not isinstance(manifest.get('files'),dict):
            raise ValueError('Unsupported GPU result bundle')
        if set(names)!={'bundle-manifest.json',*manifest['files']}:raise ValueError('Archive/manifest file set mismatch')
        for name,evidence in manifest['files'].items():
            raw=archive.read(name)
            if (not isinstance(evidence,dict) or evidence.get('bytes')!=len(raw)
                    or evidence.get('sha256')!=hashlib.sha256(raw).hexdigest()):
                raise ValueError('Manifest file checksum/size mismatch: '+name)
        states=[n for n in manifest['files'] if n.endswith('/checks/status.json')]
        results=[n for n in manifest['files'] if n.endswith('/results.json')]
        if len(states)!=1 or len(results)!=2:raise ValueError('Expected one execution receipt and exactly two target results')
        state=parse(archive.read(states[0]))
        if state.get('status')!='passed_generation_measurement_export_report_comparison':raise ValueError('Reported execution did not pass')
        if (registry is None)!=(protocol_id is None):raise ValueError('Supply outside registry and protocol ID together')
        full_claim=(state.get('scope')=='two_actual_targets_registered_full_core_pipeline'
                    or state.get('full_core_requested') is True or trusted_index.get('protocol',{}).get('kind')=='standard')
        registered=None
        if full_claim and registry is None:raise ValueError('Full standard intake requires an outside pinned registry')
        if registry is not None:registered=registry.validate_index(protocol_id,trusted_index)
        if full_claim:
            counts={task:len(rows) for task,rows in trusted_index['inputs'].items()}
            if (state.get('scope')!='two_actual_targets_registered_full_core_pipeline'
                    or state.get('full_core_requested') is not True or state.get('registered_full_inputs_validated') is not True
                    or state.get('sources_per_prefix') is not None or state.get('full_input_counts')!=counts
                    or state.get('protocol_id')!=protocol_id or state.get('protocol_sha256')!=registered['content_sha256']):
                raise ValueError('Full standard execution scope differs from outside registered inputs')
        commands=state.get('commands')
        if (not isinstance(commands,list) or not commands or any(c.get('status')!='passed' or c.get('exit_code')!=0 for c in commands)
                or not any(c.get('name')=='two-target-comparison' for c in commands)):
            raise ValueError('Incomplete stage exit receipts')
        targets=state.get('targets')
        if not isinstance(targets,list) or len(targets)!=2:raise ValueError('Expected two target execution records')
        required={'two-target-comparison',*[t['model'].split('/')[-1]+'-'+stage
                  for t in targets for stage in ('prepare','index','generate','measure','export','diagnose')]}
        if len(commands)!=len(required) or {c['name'] for c in commands}!=required:
            raise ValueError('Required target stage receipts are missing or duplicated')
        accepted=[]
        for name in sorted(results):
            document=parse(archive.read(name));validate_results(document,trusted_index)
            model=document['run']['model']
            matching=[t for t in targets if t.get('model')==model['id'] and t.get('revision')==model['revision']]
            if len(matching)!=1:raise ValueError('Result model differs from execution receipt')
            target=matching[0];folder=PurePosixPath(name).parent
            for task in (1,2,3,5):
                prediction=(folder/'run'/f'task{task}_predictions.jsonl').as_posix()
                if prediction not in manifest['files']:raise ValueError('Missing frozen generation output')
                summary=target.get('generation',{}).get(str(task),{})
                raw=archive.read(prediction)
                rows=[parse(line) for line in raw.splitlines() if line.strip()]
                count=sum(r['task']==task for r in document['records'])
                if (summary.get('prediction_sha256')!=hashlib.sha256(raw).hexdigest()
                        or summary.get('expected')!=count or summary.get('actual')!=count
                        or summary.get('api_failures')!=0 or len(rows)!=count or any(row.get('api_status')!='ok' for row in rows)):
                    raise ValueError('Frozen generation coverage/receipt mismatch')
            accepted.append({'model':model,'path':name,'artifact_sha256':document['content_sha256'],
                             'records':len(document['records']),'task_rows':{str(t):sum(r['task']==t for r in document['records']) for t in range(1,6)}})
        if len({r['model']['id'] for r in accepted})!=2:raise ValueError('Expected two distinct target models')
    return manifest,{'scope':'gpu_return_integrity_and_independent_input_acceptance','archive_sha256':expected_sha256,
                     'files':len(manifest['files']),'targets':accepted,'execution_status':state['status'],
                     'official_rank_eligible':False,'cryptographic_generation_authenticity':False,
                     'classifier_accuracy_verified':False,'public_posting':False,
                     'full_standard_inputs_verified':full_claim,
                     'outside_protocol_sha256':registered['content_sha256'] if registered else None}


def main():
    from koevd_eval.results import read_document, export_run
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip',required=True);parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--trusted-index',required=True,help='Independently prepared operator file outside the archive')
    parser.add_argument('--registry',help='Outside operator registry; required for full standard intake')
    parser.add_argument('--protocol-id')
    parser.add_argument('--output',required=True,help='Fresh private directory')
    args=parser.parse_args()
    index=read_document(args.trusted_index)
    if bool(args.registry)!=bool(args.protocol_id):parser.error('Supply --registry and --protocol-id together')
    from koevd_eval.protocols import ProtocolRegistry
    registry=ProtocolRegistry(args.registry) if args.registry else None
    snapshot=read_snapshot(args.zip)
    manifest,receipt=verify_bundle(args.zip,args.expected_sha256,index,archive_bytes=snapshot,
                                  registry=registry,protocol_id=args.protocol_id)
    output=Path(args.output).absolute()
    if any(p.is_symlink() for p in (output,*output.parents)):raise ValueError('Intake destination traverses a symlink')
    output.mkdir(parents=True,exist_ok=False)
    with zipfile.ZipFile(BytesIO(snapshot)) as archive:
        for name in ['bundle-manifest.json',*manifest['files']]:
            dest=output/name;dest.parent.mkdir(parents=True,exist_ok=True)
            with dest.open('xb') as stream:stream.write(archive.read(name))
    for target in receipt['targets']:
        original=read_document(output/target['path'])
        rebuilt=export_run((output/target['path']).parent/'run',index)
        if original!=rebuilt:raise ValueError('Independent portable re-export differs from returned result')
        target['independent_reexport_exact_match']=True
    (output/'intake-receipt.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))


if __name__=='__main__':main()
