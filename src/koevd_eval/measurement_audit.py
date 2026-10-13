"""Frozen-response measurement audit and separately bound human review.

CPU tooling only: no classifier inference, automatic relabeling, accuracy claim,
public registration, or target-generation authenticity verification.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from copy import deepcopy
import argparse
import json
from pathlib import Path

from .common import configure_cli_stdio
from .diagnostics import STRATEGIES, analyze
from .results import (_keys, _seal, _verify_seal, canonical_hash, read_document,
                      validate_results)

VERSION = 'koevd-measurement-audit-v1'
REVIEW_VERSION = 'koevd-human-review-v1'
IMPORT_VERSION = 'koevd-review-import-v1'
KNOWN_SUSPECTS = ('new_template3_1st_13794', 'new_template3_1st_05843',
                  'new_template3_1st_05104')
NOTES = [
    'Selected audit cases are not a representative prevalence or held-out accuracy sample.',
    'Disagreement and sensitivity do not establish which classifier is correct.',
    'Human review is separate from original measurement; nothing is overwritten.',
    'Identity, inference settings and reviewer identity remain reported, not authenticated.',
    'No accuracy certification or rank promotion is conferred by this audit.',
]


def _text(value, description, limit=256):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError('Invalid ' + description)
    return value


def _guideline(value):
    _keys(value, ('id', 'version'), 'Guideline')
    for k in value: _text(value[k], 'guideline ' + k)
    return deepcopy(value)


def _identity(case, artifact):
    return canonical_hash({'artifact': artifact, 'task': 3,
                           'sample_id': case['sample_id'],
                           'input': case['input_sha256'],
                           'response': case['response']['sha256']})


def _snapshot(case, strategies, artifact):
    return {'case_id': _identity(case, artifact), 'sample_id': case['sample_id'],
            'source_id': case['source_id'], 'input_sha256': case['input_sha256'],
            'response_sha256': case['response']['sha256'],
            'messages': deepcopy(case['messages']), 'response': deepcopy(case['response']),
            'metadata': deepcopy(case['metadata']),
            'safety': {'valid': case['valid'], 'parsed': deepcopy(case['parsed']),
                       'measurement': deepcopy(case['measurement'])},
            'strategy': {'valid': strategies['valid'], 'parsed': deepcopy(strategies['parsed']),
                         'measurement': deepcopy(strategies['measurement'])}}


def _semantic(case):
    if not case['valid']: return None
    if case['task'] == 3: return case['parsed']
    return sorted(case['parsed']['strategies'])


def compare_measurements(baseline, variant, index, *, variant_id):
    """Allow identical artifacts (zero changes), unlike target-model comparison.

    All generations and declared target settings must be identical. Measurement
    provenance may vary; changes are observations, never attributed causes.
    """
    _text(variant_id, 'measurement variant ID', 128)
    validate_results(baseline, index)
    validate_results(variant, index)
    for key in ('model', 'generation'):
        if baseline['run'][key] != variant['run'][key]:
            raise ValueError('Frozen target ' + key + ' differs')
    left = {(r['task'], r['sample_id']): r for r in baseline['records']}
    right = {(r['task'], r['sample_id']): r for r in variant['records']}
    for key, record in left.items():
        other = right[key]
        for field in ('source_id', 'variant', 'input_sha256', 'response'):
            if record[field] != other[field]:
                raise ValueError('Frozen input/generation differs: ' + str(key))
    profiles = [analyze(d, index, resamples=0) for d in (baseline, variant)]
    cases = [{(c['task'], c['sample_id']): c for c in p['cases']} for p in profiles]
    result = {'variant_id': variant_id, 'baseline_sha256': baseline['content_sha256'],
              'variant_sha256': variant['content_sha256'], 'tasks': {},
              'target_identity_verification': 'reported_equal_not_authenticated',
              'order_verification': 'not_recorded_by_results_v1',
              'official_rank_eligible': False, 'interpretation': NOTES}
    for task in (3, 4):
        before = baseline['run']['measurements'][str(task)]
        after = variant['run']['measurements'][str(task)]
        fields = sorted(set(before or {}) | set(after or {}))
        different = [f for f in fields if (before or {}).get(f) != (after or {}).get(f)]
        unknown = [f for f in fields if (before or {}).get(f) is None or (after or {}).get(f) is None]
        counts = Counter(total=0, both_valid=0, baseline_valid=0, variant_valid=0,
                         semantic_changes=0, validity_changes=0, raw_output_changes=0,
                         raw_output_comparable=0, raw_output_presence_changes=0,
                         measurement_value_changes=0)
        changes = []
        for key in sorted(k for k in left if k[0] == task):
            a, b = cases[0][key], cases[1][key]
            counts['total'] += 1
            counts['baseline_valid'] += int(a['valid'])
            counts['variant_valid'] += int(b['valid'])
            both = a['valid'] and b['valid']
            counts['both_valid'] += int(both)
            semantic = bool(both and _semantic(a) != _semantic(b))
            validity = a['valid'] != b['valid']
            av, bv = a['measurement']['value'], b['measurement']['value']
            ar, br = (av or {}).get('raw_output'), (bv or {}).get('raw_output')
            raw_comparable = ar is not None and br is not None
            raw_presence = (ar is None) != (br is None)
            raw = bool(raw_comparable and ar != br)
            value = av != bv
            counts['semantic_changes'] += int(semantic)
            counts['validity_changes'] += int(validity)
            counts['raw_output_changes'] += int(raw)
            counts['raw_output_comparable'] += int(raw_comparable)
            counts['raw_output_presence_changes'] += int(raw_presence)
            counts['measurement_value_changes'] += int(value)
            if semantic or validity or raw or value:
                changes.append({'sample_id': key[1], 'source_id': a['source_id'],
                                'input_sha256': a['input_sha256'],
                                'response_sha256': a['response']['sha256'],
                                'baseline_valid': a['valid'], 'variant_valid': b['valid'],
                                'semantic_changed': semantic, 'validity_changed': validity,
                                'raw_output_changed': raw, 'raw_output_comparable': raw_comparable,
                                'raw_output_presence_changed': raw_presence, 'value_changed': value,
                                'baseline_measurement': deepcopy(a['measurement']),
                                'variant_measurement': deepcopy(b['measurement'])})
        result['tasks'][str(task)] = {
            'counts': dict(counts),
            'semantic_change_rate_on_both_valid': (counts['semantic_changes']/counts['both_valid']
                                                   if counts['both_valid'] else None),
            'raw_change_rate_on_recorded_pairs': (counts['raw_output_changes']/counts['raw_output_comparable']
                                                  if counts['raw_output_comparable'] else None),
            'provenance': {'baseline': deepcopy(before), 'variant': deepcopy(after),
                           'different_fields': different, 'unknown_fields': unknown},
            'changes': changes,
            'note': 'No causal attribution to batch/order/precision. Invalid states remain separate.'}
    return result


def _reasons(case, strategy, suspect_sources):
    reasons = (set(case['quality_flags']) | set(strategy['quality_flags'])) - {'finish_reason_unknown'}
    if case['source_id'] in suspect_sources: reasons.add('named_suspect_source')
    if not case['valid']: reasons.add('invalid_or_unmeasured_safety')
    if not strategy['valid']: reasons.add('invalid_or_unmeasured_strategy')
    if not reasons: reasons.add('metadata_coverage')
    return sorted(reasons)


def _priority(reasons):
    if 'named_suspect_source' in reasons: return 0
    if 'classifier_disagreement' in reasons: return 1
    if set(reasons) & {'length_limit', 'single_character_repetition'}: return 2
    if set(reasons) & {'invalid_or_unmeasured_safety', 'invalid_or_unmeasured_strategy'}: return 3
    if reasons != ['metadata_coverage']: return 4
    return 5


def _stratum(case):
    # Topics can overlap: this is a queue key, not independent statistical rows.
    return canonical_hash({k: case['metadata'].get(k) for k in
                           ('severity_band', 'explicitness', 'utterance_type', 'topic')})


def create_audit(document, index, *, guideline, limit=100, seed=1729,
                 suspect_sources=KNOWN_SUSPECTS, variants=()):
    if type(limit) is not int or not 1 <= limit <= 5000:
        raise ValueError('Audit limit must be 1..5000')
    if type(seed) is not int: raise ValueError('Audit seed must be an integer')
    guideline = _guideline(guideline)
    suspect_sources = list(suspect_sources)
    if len(suspect_sources) > 1000: raise ValueError('At most 1000 named suspect sources')
    suspects = sorted(set(_text(x, 'suspect source ID') for x in suspect_sources))
    profile = analyze(document, index, resamples=0)
    cases = [c for c in profile['cases'] if c['task'] == 3]
    strategies = {c['sample_id']: c for c in profile['cases'] if c['task'] == 4}
    if len({c['source_id'] for c in cases}) != len(cases):
        raise ValueError('Audit v1 requires one Task 3 generation per source')
    groups = defaultdict(list)
    reasons = {}
    for c in cases:
        reasons[c['sample_id']] = _reasons(c, strategies[c['sample_id']], suspects)
        groups[(_priority(reasons[c['sample_id']]), _stratum(c))].append(c)
    buckets = {}
    for key, values in groups.items():
        buckets[key] = deque(sorted(values, key=lambda c: canonical_hash(
            {'seed': seed, 'sample_id': c['sample_id'], 'input': c['input_sha256']})))
    selected = []
    for priority in sorted({key[0] for key in buckets}):
        active = deque(sorted(key for key in buckets if key[0] == priority))
        while active and len(selected) < limit:
            key = active.popleft()
            selected.append(buckets[key].popleft())
            if buckets[key]: active.append(key)
    variants = list(variants)
    if len(variants) > 16: raise ValueError('At most 16 measurement variants per audit')
    names, comparisons = set(), []
    for name, variant in variants:
        if name in names: raise ValueError('Duplicate measurement variant ID')
        names.add(name)
        comparisons.append(compare_measurements(document, variant, index, variant_id=name))
    present = {c['source_id'] for c in cases}
    output = {
        'format': VERSION, 'baseline_sha256': document['content_sha256'],
        'input_index_sha256': index['content_sha256'], 'guideline': guideline,
        'selection': {'policy': 'priority_then_metadata_round_robin_v1', 'limit': limit,
                      'seed': seed, 'suspect_sources': suspects,
                      'suspects_present': sorted(present & set(suspects)),
                      'suspects_missing': sorted(set(suspects) - present),
                      'representative_prevalence_sample': False},
        'universe': {'sources': len(cases), 'selected_sources': len(selected),
                     'valid_safety': sum(c['valid'] for c in cases),
                     'valid_strategy': sum(c['valid'] for c in strategies.values()),
                     'quality': deepcopy(profile['quality']),
                     'disagreement': deepcopy(profile['measurement_disagreement'])},
        'cases': [{**_snapshot(c, strategies[c['sample_id']], document['content_sha256']),
                   'selection_reasons': reasons[c['sample_id']]} for c in selected],
        'measurement_comparisons': comparisons,
        'interpretation': NOTES, 'accuracy_status': 'not_established',
        'official_rank_eligible': False,
    }
    return _seal(output)


def validate_audit(audit, document, index):
    _keys(audit, ('format', 'baseline_sha256', 'input_index_sha256', 'guideline',
                  'selection', 'universe', 'cases', 'measurement_comparisons',
                  'interpretation', 'accuracy_status', 'official_rank_eligible',
                  'content_sha256'), 'Audit')
    _verify_seal(audit)
    if (audit['format'] != VERSION or audit['baseline_sha256'] != document['content_sha256']
            or audit['input_index_sha256'] != index['content_sha256']):
        raise ValueError('Audit belongs to a different baseline/input index')
    if audit['official_rank_eligible'] is not False or audit['accuracy_status'] != 'not_established':
        raise ValueError('Audit cannot confer accuracy/rank')
    _guideline(audit['guideline'])
    selection = audit['selection']
    _keys(selection, ('policy', 'limit', 'seed', 'suspect_sources', 'suspects_present',
                      'suspects_missing', 'representative_prevalence_sample'), 'Audit selection')
    if not isinstance(selection['suspect_sources'], list):
        raise ValueError('Invalid audit suspect sources')
    expected = create_audit(document, index, guideline=audit['guideline'],
                            limit=selection['limit'], seed=selection['seed'],
                            suspect_sources=selection['suspect_sources'])
    # Measurement comparisons are separate observations, unused by human import.
    # Verify the entire selection, case content, universe and interpretation anew.
    for key in expected:
        if key not in ('content_sha256', 'measurement_comparisons') and audit[key] != expected[key]:
            raise ValueError('Audit case content differs from frozen baseline or selection')
    if not isinstance(audit['measurement_comparisons'], list) or len(audit['measurement_comparisons']) > 16:
        raise ValueError('Invalid audit comparison count')
    return {c['case_id']: c for c in audit['cases']}



def review_template(audit):
    """Blinded template: no model name, classifier labels, gold or selection flags."""
    return {'format': REVIEW_VERSION, 'audit_sha256': audit['content_sha256'],
            'reviewer': {'id': None, 'role': None}, 'guideline': deepcopy(audit['guideline']),
            'stage': 'independent_review',
            'reviews': [{'case_id': c['case_id'], 'input_sha256': c['input_sha256'],
                         'response_sha256': c['response_sha256'], 'safety_label': 'not_reviewed',
                         'strategies': None, 'rationale': None} for c in audit['cases']]}


def import_review(review, audit, document, index):
    cases = validate_audit(audit, document, index)
    _keys(review, ('format', 'audit_sha256', 'reviewer', 'guideline', 'stage', 'reviews'), 'Human review')
    if (review['format'] != REVIEW_VERSION or review['stage'] != 'independent_review'
            or review['audit_sha256'] != audit['content_sha256']):
        raise ValueError('Unknown/stale review or unsupported adjudication stage')
    if _guideline(review['guideline']) != audit['guideline']:
        raise ValueError('Review guideline differs from audit guideline')
    _keys(review['reviewer'], ('id', 'role'), 'Reviewer')
    for k in review['reviewer']: _text(review['reviewer'][k], 'reviewer ' + k)
    values = review['reviews']
    if not isinstance(values, list) or len(values) > len(cases):
        raise ValueError('Invalid review count')
    seen, imported, counts = set(), [], Counter()
    for r in values:
        _keys(r, ('case_id', 'input_sha256', 'response_sha256', 'safety_label',
                  'strategies', 'rationale'), 'Review case')
        cid = r['case_id']
        if not isinstance(cid, str) or cid not in cases or cid in seen:
            raise ValueError('Unknown/duplicate reviewed case')
        seen.add(cid)
        c = cases[cid]
        if any(r[k] != c[k] for k in ('input_sha256', 'response_sha256')):
            raise ValueError('Review binds to different input/response')
        label = r['safety_label']
        if label not in ('safe', 'unsafe', 'uncertain', 'abstain', 'not_reviewed'):
            raise ValueError('Invalid human safety decision')
        tags = r['strategies']
        if tags is not None and (not isinstance(tags, list) or len(tags) > 16
                or any(not isinstance(t, str) for t in tags)
                or len(set(tags)) != len(tags) or not set(tags) <= set(STRATEGIES) | {'unsafe'}):
            raise ValueError('Unknown/duplicate human strategy labels')
        if label != 'not_reviewed' or tags is not None:
            _text(r['rationale'], 'review rationale', 8192)
        elif r['rationale'] is not None:
            _text(r['rationale'], 'review rationale', 8192)
        usable = c['response']['status'] == 'ok' and bool(c['response']['text'].strip())
        if not usable and (label in ('safe', 'unsafe') or tags is not None):
            raise ValueError('Failed/empty generation cannot receive a response label')
        counts[label] += 1
        agreement = (label == c['safety']['parsed']
                     if label in ('safe', 'unsafe') and c['safety']['valid'] else None)
        imported.append({**deepcopy(r), 'source_id': c['source_id'],
                         'reported_classifier_agrees': agreement})
    counts['unreturned_cases'] = len(cases) - len(seen)
    result = {'format': IMPORT_VERSION, 'audit_sha256': audit['content_sha256'],
              'baseline_sha256': document['content_sha256'],
              'review_document_sha256': canonical_hash(review),
              'reviewer': deepcopy(review['reviewer']), 'reviewer_identity': 'reported_not_authenticated',
              'guideline': deepcopy(review['guideline']), 'stage': review['stage'],
              'counts': dict(sorted(counts.items())), 'reviews': imported,
              'accuracy_status': 'not_established', 'official_rank_eligible': False,
              'interpretation': NOTES + ['Independent reviews are not adjudicated gold. No global F1 is computed.']}
    return _seal(result)


def _json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
                          encoding='utf-8', newline='\n')


def write_audit(audit, output_dir):
    out = Path(output_dir)
    if out.exists() and any(out.iterdir()):
        raise ValueError('Use a new or empty audit output directory')
    out.mkdir(parents=True, exist_ok=True)
    _json(out/'audit.json', audit)
    _json(out/'review-template.json', review_template(audit))
    with (out/'blinded-cases.jsonl').open('w', encoding='utf-8', newline='\n') as handle:
        for c in audit['cases']:
            row = {'case_id': c['case_id'], 'input_sha256': c['input_sha256'],
                   'response_sha256': c['response_sha256'], 'messages': c['messages'],
                   'response_text': c['response']['text'],
                   'generation_status': c['response']['status'],
                   'review_context': 'Judge generated final response against the supplied messages and guideline.'}
            handle.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
    lines = ['# Measurement audit', '', 'Private CPU audit; no accuracy certification or rank promotion.', '',
             f"Selected sources: {len(audit['cases'])}/{audit['universe']['sources']}.",
             'Selection: priority then metadata round robin; not a representative sample.', '',
             'Give reviewers blinded-cases.jsonl, review-template.json and the actual guideline.',
             'Keep audit.json separate: it includes original classifier labels and selection reasons.', '',
             '## Frozen-response comparisons', '']
    for comparison in audit['measurement_comparisons']:
        for task, result in comparison['tasks'].items():
            c = result['counts']
            # Keep untrusted variant names in JSON; use a fixed hash in Markdown.
            variant_key = canonical_hash(comparison['variant_id'])[:12]
            lines.append(f"- Variant {variant_key} Task {task}: "
                         f"semantic changes {c['semantic_changes']}/{c['both_valid']} jointly valid; "
                         f"validity changes {c['validity_changes']}; recorded raw changes "
                         f"{c['raw_output_changes']}/{c['raw_output_comparable']}; "
                         f"raw presence changes {c['raw_output_presence_changes']}.")
    lines.extend(['', *['- ' + n for n in NOTES], ''])
    (out/'README.md').write_text('\n'.join(lines), encoding='utf-8', newline='\n')
    return out


def main():
    configure_cli_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    create = sub.add_parser('create')
    create.add_argument('--results', required=True)
    create.add_argument('--trusted-index', required=True)
    create.add_argument('--output-dir', required=True)
    create.add_argument('--guideline-id', required=True)
    create.add_argument('--guideline-version', required=True)
    create.add_argument('--limit', type=int, default=100)
    create.add_argument('--seed', type=int, default=1729)
    create.add_argument('--suspect-source', action='append', default=[])
    create.add_argument('--variant', action='append', default=[], metavar='ID=RESULTS_JSON')
    review = sub.add_parser('import-review')
    for name in ('review', 'audit', 'results', 'trusted-index', 'output'):
        review.add_argument('--' + name, required=True)
    args = parser.parse_args()
    try:
        document, index = read_document(args.results), read_document(args.trusted_index)
        if args.command == 'create':
            variants = []
            for spec in args.variant:
                name, sep, path = spec.partition('=')
                if not sep or not path: raise ValueError('Variant syntax: ID=RESULTS_JSON')
                variants.append((name, read_document(path)))
            audit = create_audit(document, index,
                guideline={'id': args.guideline_id, 'version': args.guideline_version},
                limit=args.limit, seed=args.seed,
                suspect_sources=(*KNOWN_SUSPECTS, *args.suspect_source), variants=variants)
            print(write_audit(audit, args.output_dir).resolve())
        else:
            out = Path(args.output)
            if out.exists(): raise ValueError('Review import must use a new output file')
            imported = import_review(read_document(args.review), read_document(args.audit), document, index)
            out.parent.mkdir(parents=True, exist_ok=True)
            _json(out, imported)
            print(out.resolve())
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
