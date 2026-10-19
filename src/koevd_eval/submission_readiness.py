"""Compare a portable export with its retained pipeline, without modifying either."""
from copy import deepcopy
from pathlib import Path

from .pipeline import file_sha
from .results import canonical_hash, export_run, read_document, validate_results


def _snapshot(root):
    paths = {root / 'pipeline.json'}
    for pattern in ('task*_input.jsonl', 'task*_predictions.jsonl',
                    'task*_measured.jsonl', '*.progress.jsonl'):
        paths.update(root.glob(pattern))
    return {p.name: file_sha(p) for p in sorted(paths) if p.is_file()}


def _basis(document, stable_identity):
    run = deepcopy(document['run'])
    # Code metadata may describe the original export. A documentation update is
    # not a changed response or measurement. Legacy pipelines lack stable IDs.
    run.pop('code_revision', None)
    if not stable_identity:
        run.pop('id', None)
        run.pop('created_at', None)
    return {'run': run, 'protocol_sha256': document['protocol_sha256'],
            'input_index_sha256': document['input_index_sha256'],
            'records': sorted(document['records'], key=lambda r: (r['task'], r['sample_id']))}


def check_run(run_dir, document, index, *, registry=None, protocol_id=None):
    """Return consistency, not generation authenticity, parsing success or accuracy.

    Failed requests and unmeasured responses remain valid, explicit observations.
    Re-exporting is never performed as a side effect of this read-only check.
    """
    if bool(registry) != bool(protocol_id):
        raise ValueError('Supply --registry and --protocol-id together')
    rows = validate_results(document, index)
    if registry:
        from .protocols import ProtocolRegistry
        ProtocolRegistry(registry).validate_index(protocol_id, index)
    root = Path(run_dir)
    before = _snapshot(root)
    manifest = read_document(root / 'pipeline.json')
    latest = export_run(root, index, code_revision=document['run']['code_revision'])
    if before != _snapshot(root):
        raise ValueError('Run files changed during the check. Wait for generation/measurement to finish, then check again.')
    stable_identity = bool(manifest.get('generation_run'))
    actual, expected = _basis(document, stable_identity), _basis(latest, stable_identity)
    changed = [name for name in expected if actual[name] != expected[name]]
    failed = sum(r['response']['status'] == 'error' for r in document['records'] if r['task'] != 4)
    unmeasured = {str(t): sum(r['measurement']['status'] == 'unmeasured'
                             for r in document['records'] if r['task'] == t) for t in (3, 4)}
    warnings = []
    if failed:
        warnings.append('failed_generation_requests_retained')
    if any(unmeasured.values()):
        warnings.append('some_usable_responses_are_unmeasured')
    if not stable_identity:
        warnings.append('legacy_run_identity_unavailable_contents_and_settings_compared')
    current = not changed
    return {'format': 'koevd-export-readiness-v1', 'current': current,
            'status': ('current_with_warnings' if warnings else 'current') if current else 'stale_export',
            'changed_sections': changed,
            'record_counts': {str(t): len(v) for t, v in rows.items()},
            'failed_generation_requests': failed, 'unmeasured_usable_responses': unmeasured,
            'warnings': warnings, 'stable_run_identity_checked': stable_identity,
            'input_scope': 'registered_protocol_checked' if registry else 'supplied_index_only',
            'comparison_sha256': canonical_hash(actual),
            'next_action': ('Use this JSON after reviewing failures, measurement warnings and your local diagnostic report.'
                            if current else 'Re-export and validate from this run directory using the same trusted index; then repeat check-run.'),
            'interpretation': 'Matches retained local records and settings only. No GPU inference, model authenticity, task parsing accuracy or universal safety is established. The hosted server cannot inspect your local run directory.'}


def check_file(run_dir, input_path, index_path, **kwargs):
    try:
        return check_run(run_dir, read_document(input_path), read_document(index_path), **kwargs)
    except (ValueError, OSError) as exc:
        return {'format': 'koevd-export-readiness-v1', 'current': False,
                'status': 'check_failed', 'message': str(exc),
                'next_action': 'Inspect the retained run/index/result and finish any pending recovery. Do not edit checksums. Repeat check-run after repair.'}
