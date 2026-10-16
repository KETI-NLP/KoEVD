"""Preserve validated measurements before resuming their source generations."""
from pathlib import Path
import shutil
import uuid

from .common import read_jsonl
from .run_openai_compatible import unique_rows


def require_complete(manifest):
    if manifest.get('generation_retry_pending'):
        raise ValueError('Generation retry pending; repeat the generate command with the same settings before classifying, reporting or exporting')


def resume_measured_generation(output, manifest, generate):
    """Called under the measurement-stage lock; never bless changed evidence."""
    from .pipeline import file_sha, save_json, verify_predictions
    from .results import _measurement_evidence, read_document
    output = Path(output)
    root = output/'generation_retries'
    pending = manifest.get('generation_retry_pending')
    evidence = manifest.get('measurements', {})
    names = [f'task{t}_{suffix}' for t in (3, 4)
             for suffix in ('measured.jsonl', 'measurement_trace.json')]
    if manifest.get('measurement_pending'):
        raise ValueError('Measurement promotion pending; finish the classify command before retrying generation')
    if not pending and not evidence and not any((output/n).exists() for n in names):
        generate()
        return
    if root.is_symlink():
        raise ValueError('Generation retry symlink rejected')
    root.mkdir(exist_ok=True)
    if pending:
        directory = output/pending
        if directory.is_symlink() or directory.parent.resolve() != root.resolve():
            raise ValueError('Invalid pending generation retry path')
        journal = read_document(directory/'retry.json')
        if journal['generation'] != manifest['generation']:
            raise ValueError('Finish the generation retry with the same settings')
    else:
        predictions = unique_rows(verify_predictions(output, manifest, 3))
        for task in (3, 4):
            present = any((output/f'task{task}_{suffix}').exists()
                          for suffix in ('measured.jsonl', 'measurement_trace.json'))
            if str(task) in evidence:
                _measurement_evidence(output, manifest, task, predictions)
            elif present:
                raise ValueError('Unbound measurement files; use a new run directory')
        directory = root/uuid.uuid4().hex
        previous = directory/'previous'
        previous.mkdir(parents=True)
        archived = {}
        for name in ['pipeline.json', 'task3_predictions.jsonl', *names]:
            path = output/name
            if path.is_symlink():
                raise ValueError('Canonical generation/measurement symlink rejected')
            if path.exists():
                archived[name] = file_sha(path)
                shutil.copyfile(path, previous/name)
        journal = {'format': 'koevd-generation-retry-v1', 'status': 'prepared',
                   'generation': manifest['generation'], 'files': archived,
                   'old_prediction_sha256': archived['task3_predictions.jsonl'],
                   'measurement_tasks': sorted(evidence)}
        save_json(directory/'retry.json', journal)
        manifest['generation_retry_pending'] = directory.relative_to(output).as_posix()
        save_json(output/'pipeline.json', manifest)
    for name, digest in journal['files'].items():
        path = directory/'previous'/name
        if path.is_symlink() or file_sha(path) != digest:
            raise ValueError('Archived generation retry evidence changed')
    if journal['status'] == 'prepared':
        generate()
        verify_predictions(output, manifest, 3)
        journal.update(status='generated', new_prediction_sha256=file_sha(output/'task3_predictions.jsonl'))
        save_json(directory/'retry.json', journal)
    if file_sha(output/'task3_predictions.jsonl') != journal['new_prediction_sha256']:
        raise ValueError('Retried predictions changed before measurement invalidation')
    changed = journal['old_prediction_sha256'] != journal['new_prediction_sha256']
    # Check every file before removing any. Missing files are allowed only while
    # completing this journaled invalidation after an interrupted invocation.
    for name in names:
        path = output/name
        if path.is_symlink():
            raise ValueError('Canonical measurement symlink rejected')
        if path.exists() and file_sha(path) != journal['files'].get(name):
            raise ValueError('Measurement changed during generation retry')
    if changed:
        for name in names:
            (output/name).unlink(missing_ok=True)
        for task in (3, 4):
            manifest.get('measurements', {}).pop(str(task), None)
    manifest.setdefault('generation_retry_history', []).append({
        'attempt': directory.relative_to(output).as_posix(),
        'old_prediction_sha256': journal['old_prediction_sha256'],
        'new_prediction_sha256': journal['new_prediction_sha256'],
        'invalidated_tasks': journal['measurement_tasks'] if changed else []})
    manifest.pop('generation_retry_pending', None)
    save_json(output/'pipeline.json', manifest)
    journal['status'] = 'completed'
    save_json(directory/'retry.json', journal)
