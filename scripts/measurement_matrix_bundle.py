"""Pack or independently accept frozen-response measurement audit returns.

Integrity/stability evidence only: no classifier accuracy, generation
authentication, automatic gold, publication permission or rank promotion.
The original baseline and trusted input index must be supplied outside the ZIP.
"""
import argparse
import hashlib
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import re
import stat
import zipfile

FORMAT = 'koevd-frozen-measurement-matrix-bundle-v1'
MAX_TOTAL, MAX_FILE, MAX_FILES = 512*1024**2, 256*1024**2, 2000
VARIANTS = {
    'traced-repeat-b2': (2, 'original', 'batch', 'bfloat16', True),
    'untraced-b2': (2, 'original', 'batch', 'bfloat16', False),
    'traced-b1': (1, 'original', 'batch', 'bfloat16', True),
    'traced-b4': (4, 'original', 'batch', 'bfloat16', True),
    'traced-reverse-b2': (2, 'reverse', 'batch', 'bfloat16', True),
    'traced-single': (1, 'original', 'single', 'bfloat16', True),
    'traced-fp32-b2': (2, 'original', 'batch', 'float32', True),
}
spec = importlib.util.spec_from_file_location('koevd_return_path_checks',
    Path(__file__).with_name('accept_gpu_results_bundle.py'))
paths = importlib.util.module_from_spec(spec)
spec.loader.exec_module(paths)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    from koevd_eval.results import _unique_object
    return json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object)


def verify_envelope(snapshot, expected_sha256):
    if not isinstance(expected_sha256, str) or not re.fullmatch('[0-9a-f]{64}', expected_sha256):
        raise ValueError('Expected independent archive SHA-256')
    if len(snapshot) > MAX_TOTAL or sha(snapshot) != expected_sha256:
        raise ValueError('Archive size or external checksum mismatch')
    with zipfile.ZipFile(BytesIO(snapshot)) as archive:
        entries = archive.infolist()
        names = [paths.safe_name(e.filename) for e in entries]
        if (len(entries) > MAX_FILES+1 or sum(e.file_size for e in entries) > MAX_TOTAL
                or any(e.is_dir() or e.file_size > MAX_FILE or e.flag_bits & 1
                       or stat.S_ISLNK(e.external_attr >> 16) for e in entries)):
            raise ValueError('Unsupported archive entry or expansion limit')
        if len({n.casefold() for n in names}) != len(names):
            raise ValueError('Duplicate or case-colliding members')
        if 'bundle-manifest.json' not in names or archive.getinfo('bundle-manifest.json').file_size > 16*1024**2:
            raise ValueError('Missing or oversized manifest')
        manifest = parse(archive.read('bundle-manifest.json'))
        if (not isinstance(manifest, dict) or manifest.get('format') != FORMAT
                or not isinstance(manifest.get('files'), dict)):
            raise ValueError('Unsupported matrix bundle format')
        if set(names) != {'bundle-manifest.json', *manifest['files']}:
            raise ValueError('Manifest/archive file set differs')
        if any(not name.startswith('matrix/') or Path(name).suffix not in ('.json', '.jsonl', '.log')
               for name in manifest['files']):
            raise ValueError('Unexpected matrix artifact path/type')
        for name, value in manifest['files'].items():
            raw = archive.read(name)
            if (not isinstance(value, dict) or value.get('bytes') != len(raw)
                    or value.get('sha256') != sha(raw)):
                raise ValueError('Manifest checksum/size mismatch: '+name)
    return manifest


def pack(matrix, output):
    matrix = Path(matrix).absolute()
    if any(p.is_symlink() for p in (matrix, *matrix.parents)):
        raise ValueError('Matrix root traverses symlink')
    state = parse((matrix/'checks/status.json').read_bytes())
    if state.get('status') != 'passed_frozen_measurement_matrix':
        raise ValueError('Only a terminal passed matrix can be packed')
    files = {}
    for p in sorted(matrix.rglob('*')):
        if p.is_symlink():
            raise ValueError('Matrix contains a symlink')
        if not p.is_file():
            continue
        if p.suffix not in ('.json', '.jsonl', '.log'):
            raise ValueError('Unexpected matrix artifact type')
        if p.stat().st_size > MAX_FILE:
            raise ValueError('Matrix file exceeds limit')
        name = paths.safe_name('matrix/'+p.relative_to(matrix).as_posix())
        raw = p.read_bytes()
        if re.search(rb'(?:hf_[A-Za-z0-9]{30,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|sk-(?:proj-)?[A-Za-z0-9_-]{32,})', raw):
            raise ValueError('Credential-like bytes detected; not packed')
        files[name] = raw
    if len(files) > MAX_FILES or sum(map(len, files.values())) > MAX_TOTAL-16*1024**2:
        raise ValueError('Matrix return exceeds intake limits')
    manifest = {'format': FORMAT, 'files': {name: {'bytes': len(raw), 'sha256': sha(raw)}
                 for name, raw in files.items()}, 'official_rank_eligible': False,
                'classifier_accuracy_verified': False, 'credentials_included': False}
    output = Path(output).absolute()
    if output.resolve().is_relative_to(matrix.resolve()) or any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError('Archive must use a new path outside matrix')
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.writestr('bundle-manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
        for name, raw in files.items():
            archive.writestr(name, raw)
    snapshot = paths.read_snapshot(output)
    verify_envelope(snapshot, sha(snapshot))
    return {'path': str(output), 'sha256': sha(snapshot), 'bytes': len(snapshot), 'files': len(files)}


def frozen(run):
    return {f'task{t}_{kind}.jsonl': sha((run/f'task{t}_{kind}.jsonl').read_bytes())
            for t in (1, 2, 3, 5) for kind in ('input', 'predictions')}


def dtype_realization(requested, counts):
    """Parameter storage observations, never a claim about kernel arithmetic."""
    uniform = len(counts) == 1 and 'torch.'+requested in counts
    return {'requested_dtype': requested, 'parameter_dtype_elements': counts,
        'all_parameters_in_requested_dtype': uniform,
        'fp32_request_fully_realized_in_parameters': uniform if requested == 'float32' else None,
        'caveat': 'requested_fp32_not_fully_realized' if requested == 'float32' and not uniform else None,
        'interpretation': 'Observed parameter storage only; kernel arithmetic and causal attribution are not certified.'}


def verify_matrix(matrix, baseline, index, *, required_variants=None):
    from koevd_eval.results import read_document, export_run, validate_results
    from koevd_eval.measurement_audit import compare_measurements
    from koevd_eval.measurement_trace import validate_trace
    matrix, baseline = Path(matrix), Path(baseline)
    required = list(VARIANTS) if required_variants is None else list(required_variants)
    if not required or len(set(required)) != len(required) or any(v not in VARIANTS for v in required):
        raise ValueError('Select unique known required variants')
    state = read_document(matrix/'checks/status.json')
    if (state.get('status') != 'passed_frozen_measurement_matrix'
            or state.get('scope') != 'two_actual_target_frozen_response_measurement_matrix'
            or set(state.get('variants', [])) != set(required)
            or len(state['variants']) != len(required)):
        raise ValueError('Incomplete matrix status or required variant set')
    controller_sha = state.get('controller_sha256')
    if not isinstance(controller_sha, str) or not re.fullmatch('[0-9a-f]{64}', controller_sha):
        raise ValueError('Missing controller digest')
    targets = state.get('targets')
    if not isinstance(targets, list) or len(targets) != 2 or len({t.get('model') for t in targets}) != 2:
        raise ValueError('Require two distinct baseline targets')
    names = []
    for t in targets:
        if not isinstance(t.get('model'), str):
            raise ValueError('Invalid target model')
        name = t['model'].split('/')[-1]
        if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._-]{0,127}', name):
            raise ValueError('Invalid model folder')
        names.append(name)
    if len(set(names)) != 2:
        raise ValueError('Target folder collision')
    commands = state.get('commands')
    expected = {n+'-'+v for n in names for v in required}
    if (not isinstance(commands, list) or len(commands) != len(expected)
            or {c.get('name') for c in commands} != expected
            or any(c.get('status') != 'passed' or c.get('exit_code') != 0 for c in commands)):
        raise ValueError('Incomplete classifier command receipts')
    summaries = []
    for target, name in zip(targets, names):
        original = read_document(baseline/name/'results.json')
        validate_results(original, index)
        original_run = baseline/name/'run'
        if original != export_run(original_run, index):
            raise ValueError('Independent baseline re-export differs')
        if (target['model'] != original['run']['model']['id']
                or target.get('revision') != original['run']['model']['revision']
                or target.get('baseline_artifact_sha256') != original['content_sha256']
                or target.get('frozen_file_sha256') != frozen(original_run)):
            raise ValueError('Matrix baseline binding differs')
        claimed = target.get('comparisons')
        if (not isinstance(claimed, list) or len(claimed) != len(required)
                or {c.get('variant_id') for c in claimed} != set(required)):
            raise ValueError('Missing or duplicate target comparisons')
        for variant in required:
            batch, order, mode, dtype, traced = VARIANTS[variant]
            folder = matrix/name/variant
            result = read_document(folder/'results.json')
            if frozen(folder/'run') != frozen(original_run):
                raise ValueError('Frozen input/prediction bytes changed')
            if result != export_run(folder/'run', index):
                raise ValueError('Variant raw re-export differs')
            comparison = compare_measurements(original, result, index, variant_id=variant)
            observations, precision = {}, {}
            for task in (3, 4):
                before = original['run']['measurements'][str(task)]
                after = result['run']['measurements'][str(task)]
                if before is None or after is None:
                    raise ValueError('Missing classifier provenance')
                if any(before.get(k) != after.get(k) for k in ('adapter', 'base', 'revision')):
                    raise ValueError('Classifier artifact changed during fixed-artifact matrix')
                if after.get('batch_size') != batch:
                    raise ValueError('Classifier batch declaration differs')
                conditions = after.get('conditions')
                if (not isinstance(conditions, dict) or conditions.get('requested_dtype') != dtype
                        or conditions.get('input_order') != order or conditions.get('inference_mode') != mode):
                    raise ValueError('Classifier conditions declaration differs')
                trace_path = folder/'run'/f'task{task}_measurement_trace.json'
                if traced:
                    trace = read_document(trace_path)
                    validate_trace(trace, folder/'run/task3_predictions.jsonl',
                                   folder/'run'/f'task{task}_measured.jsonl', task)
                    counts = trace['runtime']['parameter_dtype_elements']
                    if (trace.get('requested_dtype') != dtype or trace.get('input_order') != order
                            or trace.get('inference_mode') != mode or not counts.get('torch.'+dtype, 0)):
                        raise ValueError('Actual trace conditions or parameter dtype differ')
                    observations[str(task)] = {'parameter_dtype_elements': counts,
                        'observed_call_order': trace['observed_call_order'], 'trace_file_sha256': sha(trace_path.read_bytes())}
                    precision[str(task)] = dtype_realization(dtype, counts)
                elif trace_path.exists() or conditions.get('observation') is not None:
                    raise ValueError('Untraced variant unexpectedly claims trace conditions')
            expected_summary = {'variant_id': variant, 'artifact_sha256': result['content_sha256'],
                'comparison': comparison, 'trace_observations': observations,
                'status': 'passed_frozen_measurement_export_compare'}
            if (read_document(folder/'comparison.json') != expected_summary
                    or next(c for c in claimed if c['variant_id'] == variant) != expected_summary):
                raise ValueError('Returned comparison/trace summary differs from independent recomputation')
            command = next(c for c in commands if c['name'] == name+'-'+variant)
            args = command.get('argv')
            if not isinstance(args, list):
                raise ValueError('Missing execution arguments')
            for flag, value in (('--stage', 'classify'), ('--batch-size', str(batch)),
                    ('--classifier-dtype', dtype), ('--measurement-order', order), ('--measurement-mode', mode)):
                if args.count(flag) != 1 or args.index(flag)+1 >= len(args) or args[args.index(flag)+1] != value:
                    raise ValueError('Classifier execution argument mismatch')
            if ('--trace-measurements' in args) != traced or '--model' in args:
                raise ValueError('Unexpected trace/generation command')
            summaries.append({'model': target['model'], 'variant': variant,
                'artifact_sha256': result['content_sha256'],
                'counts': {k: v['counts'] for k, v in comparison['tasks'].items()},
                'trace_observations': observations, 'parameter_dtype_realization': precision})
    return {'scope': 'independent_frozen_measurement_matrix_acceptance', 'variants': required,
        'full_seven_variant_matrix': set(required) == set(VARIANTS), 'targets': [t['model'] for t in targets],
        'comparisons': summaries, 'independent_reexport_and_comparison_exact': True,
        'official_rank_eligible': False, 'classifier_accuracy_verified': False,
        'cryptographic_generation_authenticity': False, 'public_posting': False}


def main():
    from koevd_eval.results import read_document
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    packer = commands.add_parser('pack')
    packer.add_argument('--matrix', required=True); packer.add_argument('--output', required=True)
    accept = commands.add_parser('accept')
    accept.add_argument('--zip', required=True); accept.add_argument('--expected-sha256', required=True)
    accept.add_argument('--baseline', required=True, help='Previously accepted baseline outside this ZIP')
    accept.add_argument('--trusted-index', required=True, help='Independent operator inputs outside ZIP')
    accept.add_argument('--output', required=True, help='New private extraction directory')
    accept.add_argument('--required-variant', action='append', choices=tuple(VARIANTS),
                        help='Explicit subset only; default requires all seven variants')
    args = parser.parse_args()
    if args.command == 'pack':
        receipt = pack(args.matrix, args.output)
    else:
        snapshot = paths.read_snapshot(args.zip)
        manifest = verify_envelope(snapshot, args.expected_sha256)
        output = Path(args.output).absolute()
        if (any(p.is_symlink() for p in (output, *output.parents))
                or Path(args.baseline).resolve().is_relative_to(output.resolve())
                or Path(args.trusted_index).resolve().is_relative_to(output.resolve())):
            raise ValueError('Independent inputs must remain outside safe intake directory')
        output.mkdir(parents=True, exist_ok=False)
        with zipfile.ZipFile(BytesIO(snapshot)) as archive:
            for name in ('bundle-manifest.json', *manifest['files']):
                dest = output/name; dest.parent.mkdir(parents=True, exist_ok=True)
                with dest.open('xb') as stream: stream.write(archive.read(name))
        receipt = verify_matrix(output/'matrix', args.baseline, read_document(args.trusted_index),
                                required_variants=args.required_variant)
        receipt.update(archive_sha256=args.expected_sha256, files=len(manifest['files']))
        with (output/'intake-receipt.json').open('x', encoding='utf-8') as stream:
            json.dump(receipt, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__': main()
