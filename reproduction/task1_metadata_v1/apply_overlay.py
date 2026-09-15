"""Materialize a historical Task 1 metadata view; never edits the input corpus."""
import argparse
import hashlib
import json
from pathlib import Path


def materialize(corpus, overlay):
    raw = corpus.read_bytes()
    if hashlib.sha256(raw).hexdigest() != overlay['base_sha256']:
        raise ValueError('Base corpus SHA-256 mismatch; use the pinned original release file.')
    records = [json.loads(line) for line in raw.decode('utf-8').splitlines()]
    if len(records) != overlay['source_count']:
        raise ValueError('Unexpected corpus size.')
    patches = {p['source_id']: p for p in overlay['patches']}
    if len(patches) != len(overlay['patches']):
        raise ValueError('Duplicate patch source ID.')
    seen = set()
    result = []
    for record in records:
        sid = record['source_id']
        if sid in seen:
            raise ValueError('Duplicate corpus source ID.')
        seen.add(sid)
        labels = record['user_utterance']['labels']
        values = {k: labels[k] for k in ['severity_band', 'utterance_type']}
        if sid in patches:
            patch = patches[sid]
            if values != patch['before']:
                raise ValueError('Patch precondition mismatch: ' + sid)
            values = patch['after']
        result.append({'source_id': sid, 'analysis_version': overlay['version'],
                       'analysis_severity_band': values['severity_band'],
                       'analysis_utterance_type': values['utterance_type'].strip().replace('Biased Qs', 'Biased Questions'),
                       'task1_eval_eligible': values['severity_band'] != 'HD/borderline'})
    if not patches.keys() <= seen:
        raise ValueError('Patch source ID missing from corpus.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--corpus', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--overlay', type=Path, default=Path(__file__).with_name('overlay.json'))
    args = parser.parse_args()
    if args.output.resolve() in {args.corpus.resolve(), args.overlay.resolve()}:
        parser.error('Output must be a new metadata-view file, not an input file.')
    rows = materialize(args.corpus, json.loads(args.overlay.read_text(encoding='utf-8')))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects an existing analysis view from accidental replacement.
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')
    print(json.dumps({'sources': len(rows), 'eligible_sources': sum(r['task1_eval_eligible'] for r in rows),
                      'output_sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
