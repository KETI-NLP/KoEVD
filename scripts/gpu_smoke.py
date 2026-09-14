"""Download pinned artifacts and exercise both classifiers on a CUDA node."""
from __future__ import annotations

import argparse
import gc
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
import platform
import re
import time
import traceback


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha256(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def validate_lock(lock):
    for key in ('dataset', 'assistant', 'strategy', 'assistant_base', 'strategy_base'):
        item = lock.get(key) or {}
        if not isinstance(item.get('repo_id'), str) or '/' not in item['repo_id']:
            raise ValueError(f'{key}: set repo_id in the release lock')
        if not re.fullmatch(r'[0-9a-f]{40}', item.get('revision') or ''):
            raise ValueError(f'{key}: use an immutable 40-character commit SHA')


def select_cases(corpus, sources):
    """Deterministic smoke sample, not the historical held-out evaluation."""
    cases = []
    with corpus.open(encoding='utf-8') as stream:
        for index, line in enumerate(stream):
            if index >= sources:
                break
            source = json.loads(line)
            for tier in ('accepted', 'rejected', 'strongly_rejected'):
                responses = source['responses'].get(tier) or []
                if responses:
                    response = responses[0]
                    cases.append({'sample_id': response['response_id'], 'source_id': source['source_id'],
                        'tier': tier, 'api_status': 'ok', 'prediction': response['content'],
                        'messages': [{'role': 'user', 'content': source['user_utterance']['content']}]})
    if len(cases) < 2:
        raise ValueError('Need at least two response candidates for batch validation')
    return cases


def verify_manifest(folder, skip_review=False):
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    checked = 0
    for item in manifest['files']:
        if skip_review and item['path'].startswith('review_fp16/'):
            continue
        path = folder / item['path']
        # HF cache entries are symlinks; validate the logical path before reading.
        if Path(item['path']).is_absolute() or '..' in Path(item['path']).parts:
            raise ValueError('Manifest path escapes repository')
        if sha256(path) != item['sha256']:
            raise ValueError('Checksum mismatch: ' + item['path'])
        checked += 1
    return checked


def measure(kind, adapter, base, cases, args, output):
    import torch
    from koevd_eval.classify_responses import build_messages
    from koevd_eval.metrics import score_task3, score_task4
    if kind == 'assistant':
        from koevd_classifiers.assistant_safe_classifier import AssistantSafeClassifier as Classifier
        key, scorer = 'label', score_task3
    else:
        from koevd_classifiers.response_strategy_classifier import StrategyClassifier as Classifier
        key, scorer = 'strategies', score_task4
    torch.cuda.reset_peak_memory_stats()
    start = time.perf_counter()
    classifier = Classifier(adapter_path=str(adapter), base_model_name_or_path=str(base),
        local_files_only=True, device_map='cuda:0', torch_dtype=args.dtype)
    try:
        classifier.load()
        load_seconds = time.perf_counter() - start
        prompts = [build_messages(row) for row in cases]
        singles = [classifier.predict(messages)['result'] for messages in prompts]
        batches = []
        for index in range(0, len(prompts), args.batch_size):
            batches.extend(item['result'] for item in classifier.predict_batch(prompts[index:index+args.batch_size]))
        if len(batches) != len(cases):
            raise RuntimeError('Batch result count mismatch')
        valid = (lambda r: r.get(key) in ('safe', 'unsafe')) if kind == 'assistant' else (lambda r: bool(r.get(key)))
        parsed = sum(valid(row) for row in singles)
        parsed_batch = sum(valid(row) for row in batches)
        comparable = (lambda r: r.get(key)) if kind == 'assistant' else (lambda r: sorted(set(r.get(key, []))))
        differences = [cases[i]['sample_id'] for i, (a, b) in enumerate(zip(singles, batches)) if comparable(a) != comparable(b)]
        rows = [{'sample_id': case['sample_id'], 'source_id': case['source_id'], 'tier': case['tier'],
                 'measurement': single, 'batch_measurement': batch}
                for case, single, batch in zip(cases, singles, batches)]
        write_json(output / (kind + '_predictions.json'), rows)
        # Include a missing measurement to verify the all-prompt denominator.
        metrics = scorer(rows + [{'sample_id': 'smoke_missing_generation', 'measurement': None}])
        write_json(output / (kind + '_metrics.json'), metrics)
        denominator_key = 'prompted' if kind == 'assistant' else 'generated_responses'
        denominator_ok = metrics[denominator_key] == len(cases) + 1 and metrics['classified'] == len(cases)
        return {'status': 'passed' if parsed == parsed_batch == len(cases) and not differences and denominator_ok else 'needs_review',
            'cases': len(cases), 'single_parsed': parsed, 'batch_parsed': parsed_batch,
            'single_batch_differences': differences, 'denominator_check': denominator_ok,
            'load_seconds': load_seconds, 'total_seconds': time.perf_counter() - start,
            'peak_allocated_bytes': torch.cuda.max_memory_allocated(),
            'parameter_dtypes': sorted({str(p.dtype) for p in classifier.model.parameters()})}
    finally:
        del classifier
        gc.collect()
        torch.cuda.empty_cache()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', type=Path)
    parser.add_argument('--output', required=True, type=Path, help='New result directory; existing paths are rejected')
    parser.add_argument('--sources', type=int, default=4)
    parser.add_argument('--batch-size', type=int, default=2)
    parser.add_argument('--dtype', choices=('bfloat16', 'float16', 'float32'), default='bfloat16')
    parser.add_argument('--prepare-only', type=Path, metavar='LOCAL_CORPUS', help='CPU-only case selection; does not validate GPU inference')
    args = parser.parse_args()
    if args.sources < 1 or args.batch_size < 2:
        parser.error('sources must be positive and batch-size must be at least 2')
    if not args.prepare_only and not args.lock:
        parser.error('--lock is required for the GPU run')
    args.output.mkdir(parents=True, exist_ok=False)
    report = {'status': 'running', 'scope': 'installation_and_inference_smoke_test_not_paper_performance_reproduction',
              'python': platform.python_version(), 'platform': platform.platform(), 'dtype': args.dtype,
              'script_sha256': sha256(Path(__file__)), 'versions': {}, 'classifiers': {}}
    try:
        for package in ('koevd-eval', 'torch', 'transformers', 'peft', 'accelerate', 'huggingface-hub'):
            try:
                report['versions'][package] = version(package)
            except PackageNotFoundError:
                report['versions'][package] = None
        if args.prepare_only:
            corpus = args.prepare_only
        else:
            lock = json.loads(args.lock.read_text(encoding='utf-8'))
            validate_lock(lock)
            report['lock'] = lock
            import torch
            if not torch.cuda.is_available():
                raise RuntimeError('CUDA GPU is required; no model download was started')
            if args.dtype == 'bfloat16' and not torch.cuda.is_bf16_supported():
                raise RuntimeError('This GPU does not support BF16; explicitly select --dtype float16')
            report['gpu'] = {'name': torch.cuda.get_device_name(0), 'cuda': torch.version.cuda,
                             'total_memory_bytes': torch.cuda.get_device_properties(0).total_memory}
            from huggingface_hub import snapshot_download
            paths = {}
            for key, item in lock.items():
                if key not in ('dataset', 'assistant', 'strategy', 'assistant_base', 'strategy_base'):
                    continue
                paths[key] = Path(snapshot_download(repo_id=item['repo_id'], revision=item['revision'],
                    repo_type='dataset' if key == 'dataset' else 'model',
                    ignore_patterns=['review_fp16/*'] if key == 'strategy' else None))
            report['verified_manifest_files'] = {key: verify_manifest(paths[key], key == 'strategy') for key in ('dataset', 'assistant', 'strategy')}
            corpus = paths['dataset'] / 'full_eval/koevd_full_eval.jsonl'
        report['corpus_sha256'] = sha256(corpus)
        cases = select_cases(corpus, args.sources)
        write_json(args.output / 'sample_ids.json', [{'sample_id': r['sample_id'], 'source_id': r['source_id'], 'tier': r['tier']} for r in cases])
        if args.prepare_only:
            report['status'] = 'prepared_only_gpu_not_tested'
        else:
            for kind in ('assistant', 'strategy'):
                try:
                    report['classifiers'][kind] = measure(kind, paths[kind], paths[kind + '_base'], cases, args, args.output)
                except Exception:
                    report['classifiers'][kind] = {'status': 'failed', 'traceback': traceback.format_exc()}
            report['status'] = 'passed' if all(r['status'] == 'passed' for r in report['classifiers'].values()) else 'needs_review'
    except Exception:
        report['status'] = 'failed'
        report['traceback'] = traceback.format_exc()
    finally:
        write_json(args.output / 'summary.json', report)
    print('Status:', report['status'], '| Report:', args.output / 'summary.json')
    return 0 if report['status'] in ('passed', 'prepared_only_gpu_not_tested') else 1


if __name__ == '__main__':
    raise SystemExit(main())
