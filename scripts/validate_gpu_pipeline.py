"""Run two pinned actual targets through an isolated vLLM pipeline.

Requires completed bootstrap/artifact receipts. Prefix runs are custom integration
checks. Full-core runs use the outside pinned registry; coverage never establishes
classifier accuracy, human gold, publication permission or public rank.
It shuts down only serving children it starts, and preserves failed stages.
"""

import argparse
import csv
import hashlib
import json
import os
import re
from pathlib import Path
import signal
import socket
import subprocess
import time
import urllib.request


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def resolve_gpu_index(rows, uuid):
    """Older vLLM NVML code needs an integer mask; still bind the chosen UUID."""
    found = []
    for row in csv.reader(rows.splitlines()):
        if len(row) != 2:
            raise ValueError('Unexpected GPU inventory')
        index, current = [value.strip() for value in row]
        if current == uuid:
            if not index.isascii() or not index.isdigit():
                raise ValueError('Invalid GPU index')
            found.append(index)
    if len(found) != 1:
        raise ValueError('Selected UUID does not uniquely identify a GPU')
    return found[0]


def preparation_steps(core, source, lock, dataset, run_dir, index, *, sources=None, full_core=False):
    """Full selection cannot reuse a prefix flag or a custom index claim."""
    if full_core == (sources is not None) or (sources is not None and sources not in (4, 96)):
        raise ValueError('Choose full core or one supported prefix')
    prepare=[core/'koevd-pipeline','--stage','prepare','--dataset-dir',dataset,
             '--output-dir',run_dir,'--split','core']
    if not full_core:prepare.extend(['--limit-sources',str(sources)])
    if full_core:
        build=[core/'koevd-results','protocol-index','--registry',source/'configs/protocols',
               '--protocol-id',lock['protocol_id'],'--dataset-dir',dataset,
               '--run-dir',run_dir,'--output',index]
    else:
        build=[core/'koevd-results','index','--run-dir',run_dir,'--output',index,
               '--dataset-repo',lock['release_artifacts']['dataset']['repo_id'],
               '--dataset-revision',lock['release_artifacts']['dataset']['revision']]
    return prepare,build


def validate_full_index(index, source, lock):
    from koevd_eval.protocols import ProtocolRegistry
    registry=ProtocolRegistry(source/'configs/protocols')
    definition=registry.validate_index(lock['protocol_id'],index)
    if definition['content_sha256']!=lock['protocol_sha256']:
        raise ValueError('Registered protocol digest differs from GPU lock')
    return {task:len(rows) for task,rows in index['inputs'].items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--gpu-uuid', required=True)
    selection=parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--sources', type=int, choices=(4, 96))
    selection.add_argument('--full-core', action='store_true', help='Complete independently registered core; no prefix limit')
    parser.add_argument('--port', type=int, default=18080)
    parser.add_argument('--attempt', help='Fresh attempt label; preserves previous failed output')
    parser.add_argument('--ptxas-path', help='Explicit compiler override for hardware unsupported by bundled Triton PTXAS')
    parser.add_argument('--source-root', help='Separate verified source bundle; old node checkout remains unchanged')
    parser.add_argument('--core-bin', help='Separate installed current core bin directory')
    parser.add_argument('--measure-bin', help='Separate installed current measurement bin directory')
    parser.add_argument('--dataset-dir', help='Pinned materialized dataset files; HF cache symlinks are not registry dataset paths')
    args = parser.parse_args()
    if args.attempt is not None and not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',args.attempt):
        parser.error('Invalid attempt label')
    root = Path(args.root).resolve(strict=True)
    for name in ('bootstrap-status', 'artifact-receipt'):
        if json.loads((root / 'environment' / (name + '.json')).read_text())['status'] != 'passed':
            parser.error('Required setup receipt is not passed: ' + name)
    artifacts = json.loads((root / 'environment/artifact-receipt.json').read_text())['artifacts']
    source=Path(args.source_root).resolve(strict=True) if args.source_root else root/'source'
    dataset=Path(args.dataset_dir).resolve(strict=True) if args.dataset_dir else Path(artifacts['dataset']['snapshot'])
    lock = json.loads((source / 'configs/validation/platform-gpu-candidate-v1.json').read_text())
    output = root / (('full-core' if args.full_core else 'smoke' if args.sources == 4 else 'expanded') + ('-' + args.attempt if args.attempt else ''))
    output.mkdir(exist_ok=False)
    logs = output / 'checks'
    logs.mkdir()
    evidence = {'scope': 'two_actual_targets_registered_full_core_pipeline' if args.full_core else 'two_actual_targets_custom_prefix_pipeline',
                'sources_per_prefix': args.sources, 'full_core_requested':args.full_core,
                'registered_full_inputs_validated':False,
                'protocol_id':lock['protocol_id'],'protocol_sha256':lock['protocol_sha256'],
                'controller_sha256':sha(Path(__file__)),
                'source_manifest_byte_sha256':sha(source/'bundle-manifest.json') if (source/'bundle-manifest.json').is_file() else None,
                'official_rank_eligible': False, 'human_gold_created': False,
                'commands': [], 'targets': [], 'status': 'running'}
    env = {**os.environ, 'CUDA_DEVICE_ORDER': 'PCI_BUS_ID',
           'PYTHONDONTWRITEBYTECODE': '1', 'VLLM_NO_USAGE_STATS': '1', 'DO_NOT_TRACK': '1',
           'TRITON_CACHE_DIR': str(root / 'environment/triton-cache'),
           'VLLM_CACHE_ROOT': str(root / 'environment/vllm-cache')}
    env.pop('PYTHONPATH',None)  # Import the explicitly installed package, not another checkout.
    core = Path(args.core_bin).resolve(strict=True) if args.core_bin else root / 'envs/core/bin'
    measure = Path(args.measure_bin).resolve(strict=True) if args.measure_bin else root / 'envs/measure/bin'
    serve = root / 'envs/serve/bin'
    evidence['runtime_bins']={'core':str(core),'measure':str(measure),'serve':str(serve),'source':str(source),'dataset':str(dataset)}

    def save():
        state = logs / 'status.json'
        tmp = state.with_suffix('.tmp')
        tmp.write_text(json.dumps(evidence, indent=2))
        tmp.replace(state)

    def run(name, argv):
        item = {'name': name, 'argv': [str(x) for x in argv], 'status': 'running'}
        evidence['commands'].append(item)
        save()
        print('START ' + name, flush=True)
        with (logs / (name + '.log')).open('x') as log:
            result = subprocess.run(item['argv'], env=env, cwd=source, stdout=log, stderr=subprocess.STDOUT)
        item.update(status='passed' if result.returncode == 0 else 'failed', exit_code=result.returncode)
        save()
        if result.returncode:
            raise RuntimeError(name + ' failed, exit=' + str(result.returncode))
        print('PASS ' + name, flush=True)

    save()
    extra = output / 'extra-body.json'
    extra.write_text(json.dumps(lock['target_conditions']['extra_body']))
    shared_index = None
    results = []
    try:
        selected_ptxas = args.ptxas_path or env.get('TRITON_PTXAS_PATH')
        if selected_ptxas:
            ptxas = Path(selected_ptxas).resolve(strict=True)
            if not ptxas.is_file():
                raise ValueError('PTXAS override must point to a compiler file')
            env['TRITON_PTXAS_PATH'] = str(ptxas)
            evidence['compiler_override'] = {'path':str(ptxas),'sha256':sha(ptxas),
                'version_output':subprocess.check_output([str(ptxas),'--version'],text=True)}
            save()
        inventory = subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid',
            '--format=csv,noheader'],text=True)
        env['CUDA_VISIBLE_DEVICES'] = resolve_gpu_index(inventory,args.gpu_uuid)
        used = subprocess.check_output(['nvidia-smi','--id=' + args.gpu_uuid,
            '--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True)
        if int(used.strip()) >= 256:
            raise RuntimeError('Selected GPU is occupied; refusing CUDA probe')
        # PCI_BUS_ID plus integer mask must actually resolve the requested UUID;
        # an ordinal alone is not enough evidence on heterogeneous/moving nodes.
        observed = subprocess.check_output([str(serve/'python'),'-c',
            'import torch;print(torch.cuda.get_device_properties(0).uuid)'],env=env,text=True).strip()
        if observed.removeprefix('GPU-') != args.gpu_uuid.removeprefix('GPU-'):
            raise RuntimeError('CUDA-visible device UUID differs from selected GPU')
        evidence['gpu_selection'] = {'requested_uuid':args.gpu_uuid,'cuda_visible_devices':env['CUDA_VISIBLE_DEVICES'],
                                     'cuda_device_order':env['CUDA_DEVICE_ORDER'],'observed_cuda_uuid':observed}
        save()
        versions = subprocess.check_output([str(serve / 'python'), '-c',
            'import importlib.metadata as m;print(m.version("vllm"))'], env=env, text=True).strip()
        for target in lock['target_models']:
            name = target['id'].split('/')[-1]
            target_dir = output / name
            target_dir.mkdir()
            run_dir = target_dir / 'run'
            snapshot = Path(artifacts['target-' + name]['snapshot'])
            model_provenance = target_dir / 'model-provenance.json'
            template = snapshot / 'tokenizer_config.json'
            model_provenance.write_text(json.dumps({'revision': target['revision'],
                'chat_template': 'tokenizer_config.json sha256:' + sha(template),
                'dtype': 'bfloat16', 'quantization': 'none', 'thinking': 'off'}))
            index = target_dir / 'trusted-input-index.json'
            prepare_command,index_command=preparation_steps(core,source,lock,dataset,run_dir,index,
                sources=args.sources,full_core=args.full_core)
            run(name+'-prepare',prepare_command)
            run(name+'-index',index_command)
            current_index = json.loads(index.read_text())
            if args.full_core:
                evidence['full_input_counts']=validate_full_index(current_index,source,lock)
                evidence['registered_full_inputs_validated']=True
                save()
            if shared_index is None:
                shared_index = index
            elif current_index != json.loads(shared_index.read_text()):
                raise ValueError('Two independently prepared indexes differ')
            usage = subprocess.check_output(['nvidia-smi', '--id=' + args.gpu_uuid,
                '--query-gpu=memory.used', '--format=csv,noheader,nounits'], text=True)
            if int(usage.strip()) >= 256:
                raise RuntimeError('Selected GPU became occupied; refusing to start server')
            with socket.socket() as probe:
                probe.bind(('127.0.0.1', args.port))
            command = [str(serve / 'vllm'), 'serve', str(snapshot), '--served-model-name', target['id'],
                '--host', '127.0.0.1', '--port', str(args.port), '--dtype', 'bfloat16',
                '--max-model-len', '16384', '--gpu-memory-utilization', '0.25',
                '--max-num-seqs', '16', '--enforce-eager']
            server_log = (logs / (name + '-server.log')).open('x')
            process = subprocess.Popen(command, env=env, cwd=source, stdout=server_log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            server = {'model': target['id'], 'revision': target['revision'], 'pid': process.pid,
                      'argv': command, 'gpu_uuid': args.gpu_uuid, 'status': 'starting'}
            evidence['targets'].append(server)
            save()
            try:
                deadline = time.monotonic() + 600
                while True:
                    if process.poll() is not None:
                        raise RuntimeError('Owned vLLM server exited: ' + str(process.returncode))
                    try:
                        with urllib.request.urlopen('http://127.0.0.1:' + str(args.port) + '/health', timeout=2) as r:
                            if r.status == 200:
                                break
                    except OSError:
                        pass
                    if time.monotonic() > deadline:
                        raise RuntimeError('Owned vLLM server did not become healthy within 600s')
                    time.sleep(1)
                server['status'] = 'healthy'
                save()
                run(name + '-generate', [core / 'koevd-pipeline', '--stage', 'generate', '--output-dir',
                    run_dir, '--base-url', 'http://127.0.0.1:' + str(args.port) + '/v1',
                    '--model', target['id'], '--temperature', '0', '--max-tokens', '1024',
                    '--workers', '2', '--timeout', '180', '--preflight', '--extra-body-file', extra,
                    '--model-provenance-file', model_provenance, '--engine-version', versions])
                manifest = json.loads((run_dir / 'pipeline.json').read_text())
                generated = {}
                for task in (1, 2, 3, 5):
                    path = run_dir / ('task' + str(task) + '_predictions.jsonl')
                    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
                    failures = sum(row.get('api_status') != 'ok' for row in rows)
                    generated[str(task)] = {'expected': manifest['inputs'][str(task)]['rows'],
                                            'actual': len(rows), 'api_failures': failures,
                                            'prediction_sha256': sha(path)}
                    if len(rows) != manifest['inputs'][str(task)]['rows'] or failures:
                        server['generation'] = generated
                        raise RuntimeError('Generation coverage/API failures; original rows preserved')
                server['generation'] = generated
                save()
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait(timeout=30)
                server.update(status='stopped_owned_child', exit_code=process.returncode)
                server_log.close()
                save()
            usage=subprocess.check_output(['nvidia-smi','--id='+args.gpu_uuid,
                '--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True)
            if int(usage.strip())>=256:
                raise RuntimeError('Selected GPU became occupied; refusing measurement')
            run(name + '-measure', [measure / 'koevd-pipeline', '--stage', 'classify', '--output-dir',
                run_dir, '--safety-adapter', artifacts['assistant']['snapshot'], '--safety-base',
                artifacts['assistant_base']['snapshot'], '--strategy-adapter', artifacts['strategy']['snapshot'],
                '--strategy-base', artifacts['strategy_base']['snapshot'], '--batch-size', '2',
                '--classifier-dtype', 'bfloat16', '--trace-measurements'])
            result = target_dir / 'results.json'
            run(name + '-export', [core / 'koevd-results', 'export', '--run-dir', run_dir,
                '--trusted-index', index, '--output', result])
            run(name + '-diagnose', [core / 'koevd-diagnose', '--input', result, '--trusted-index', index,
                '--output-dir', target_dir / 'analysis', '--bootstrap-resamples', '100', '--bootstrap-seed', '1729'])
            results.append(result)
        run('two-target-comparison', [core / 'koevd-diagnose', '--input', results[0], '--input', results[1],
            '--trusted-index', shared_index, '--output-dir', output / 'comparison',
            '--bootstrap-resamples', '100', '--bootstrap-seed', '1729'])
        evidence['status'] = 'passed_generation_measurement_export_report_comparison'
        evidence['pending'] = ['Spaces HTTP/UI numeric acceptance', 'measurement-condition variants',
                               'human adjudication', 'public posting permission and publication', 'operator acceptance']
        if not args.full_core:evidence['pending'].append('full-core evaluation')
    except BaseException as exc:
        evidence.update(status='failed', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
