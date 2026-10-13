"""File-only bridge for the unchanged analysis engine in a browser Python VM.

The deployment supplies index paths. Uploaded files cannot select or replace gold.
No model, tool, network, identity, storage or publication operation is performed.
"""
from pathlib import Path

from .diagnostics import analyze_many, write_analysis
from .results import MAX_BYTES, read_document, validate_index

OUTPUTS = ('profile-v2.json', 'cases-v2.jsonl', 'metrics-v2.csv',
           'report-v2.md', 'report-v2.html')
MAX_SESSION_BYTES = 256 * 1024 * 1024
MAX_OUTPUT_BYTES = 512 * 1024 * 1024


def analyze_files(result_paths, index_paths, output_dir, *, resamples=100, seed=1729):
    """Analyze original JSON text with operator-fixed inputs, using common Python.

    Avoid JS parse/stringify: Python's canonical seal distinguishes 0.0 and 0.
    Caller owns the disposable filesystem and must delete it after the job.
    """
    if not 1 <= len(result_paths) <= 4:
        raise ValueError('Select one to four result files')
    if sum(Path(p).stat().st_size for p in result_paths) > MAX_SESSION_BYTES:
        raise ValueError('Selected files exceed 256 MiB')
    indexes = {}
    for path in index_paths:
        index = read_document(path)
        validate_index(index)
        if index['content_sha256'] in indexes:
            raise ValueError('Duplicate configured input index')
        indexes[index['content_sha256']] = index
    pairs = []
    for path in result_paths:
        document = read_document(path, max_bytes=MAX_BYTES)
        index = indexes.get(document.get('input_index_sha256'))
        if index is None:
            raise ValueError('No deployment-configured input set matches this result')
        pairs.append((document, index))
    out = Path(output_dir)
    if out.exists():
        raise ValueError('Use a fresh disposable output directory')
    report = analyze_many(pairs, resamples=resamples, seed=seed)
    profile = write_analysis(report, out)
    size = sum((out / name).stat().st_size for name in OUTPUTS)
    if size > MAX_OUTPUT_BYTES:
        raise ValueError('Analysis exceeds 512 MiB; no successful report returned')
    return {'files': list(OUTPUTS), 'bytes': size,
            'artifacts': [r['artifact_sha256'] for r in profile['runs']],
            'records': [len(r['cases']) for r in report['runs']],
            'statistics': {'resamples': resamples, 'seed': seed},
            'official_rank_eligible': False, 'publication_performed': False}
