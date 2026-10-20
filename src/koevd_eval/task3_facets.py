"""Disjoint metadata buckets for exact Task 3 filtering; no source IDs in output."""
from collections import Counter
import json
import re

AXES = ('utterance_type', 'topic', 'severity_band', 'explicitness')
FORMAT = 'koevd-task3-facets-v1'


def encode_aggregates(value):
    """Keep each numeric bucket on one line for compact, reviewable releases."""
    raw = json.dumps(value, ensure_ascii=False, indent=2)
    replacements = []
    decoder = json.JSONDecoder()
    for match in re.finditer(r'(?m)^(\s*)"buckets": \[', raw):
        start = match.end() - 1
        buckets, end = decoder.raw_decode(raw, start)
        indent = match.group(1)
        text = '[\n' + ',\n'.join(indent + '  ' + json.dumps(b, ensure_ascii=False, separators=(',', ':'))
                                   for b in buckets) + '\n' + indent + ']'
        replacements.append((start, end, text))
    for start, end, text in reversed(replacements):
        raw = raw[:start] + text + raw[end:]
    return (raw + '\n').encode('utf8')


class FacetAccumulator:
    def __init__(self):
        self.buckets = {}
        self.source_keys = {}

    def add(self, labels, source, valid, unsafe):
        key = tuple(tuple(sorted(set(str(v) for v in labels.get(axis, []) if v is not None)))
                    or ('__missing__',) for axis in AXES)
        # Source counts are additive only when a source belongs to one bucket.
        if source in self.source_keys and self.source_keys[source] != key:
            raise ValueError('Task 3 source has inconsistent input metadata')
        self.source_keys[source] = key
        if unsafe and not valid:
            raise ValueError('Unsafe event requires a valid Task 3 measurement')
        counter, sources, measured = self.buckets.setdefault(key, (Counter(), set(), set()))
        counter.update(rows=1, valid=int(valid), events=int(unsafe))
        sources.add(source)
        if valid:
            measured.add(source)

    def result(self):
        return {'format': FORMAT, 'axes': list(AXES), 'buckets': [
            {'labels': dict(zip(AXES, map(list, key))), **dict(counter),
             'unique_sources': len(sources), 'valid_sources': len(measured)}
            for key, (counter, sources, measured) in sorted(self.buckets.items())],
            'note': 'Disjoint input-metadata buckets. Match each bucket once; category memberships can overlap. '
                    'Counts retain failed/unclassified outputs. No cases or source identities are exposed.'}
