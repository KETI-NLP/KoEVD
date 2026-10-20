"""Reaggregate archived Task 3 predictions without publishing cases or rerunning models.

Uses the historical input metadata, not the current registration protocol or
later corpus overlays. Fails closed on duplicate/missing sources, inconsistent
metadata or labels, unknown models, and disagreement with the paper counts.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
from koevd_eval.task3_facets import FacetAccumulator, encode_aggregates

MODELS = dict(zip(
    ['apertus-8b-instruct-vllm','gemma-4-e4b-it-vllm','ministral-3-8b-reasoning-vllm',
     'olmo-3-7b-think-vllm','qwen3.5-9b-vllm','qwen3.6-27b-fp8-vllm',
     'claude-4.6-sonnet','claude-haiku-4-5','gemini-3.1-flash-lite-preview',
     'gemini-3.1-pro-preview','gpt-5.4','gpt-5.4-nano'],
    ['Apertus 8B','Gemma 4 E4B','Ministral 3 8B','OLMo 3 7B','Qwen3.5 9B',
     'Qwen3.6 27B','Claude 4.6 Sonnet','Claude Haiku 4.5','Gemini 3.1 Flash-Lite',
     'Gemini 3.1 Pro','GPT-5.4','GPT-5.4 Nano']))
TYPES = {'expressing_opinion':'Expressing Opinion','exploring_opinions':'Exploring Opinions',
         'providing_information':'Providing Information','AI':'Proverb/Term Meaning',
         'HIQ_a':'Biased Qs','HIQ_b':'Prohibited Acts','HIQ_c':'Controversial Requests',
         'HIQ_d':'Copyright','HIQ_e':'Personal Info','HIQ_f':'Specialized Advice','HIQ_g':'Future Predictions'}
SEVERITY = {'0':'Benign','1':'Low','2':'Low','3':'Moderate','4':'High','5':'Extreme','HD':'HD/borderline'}
EXPLICITNESS = {'E':'Explicit','I':'Implicit','N':'Neutral','NA':'Not Applicable',
                'None':'Not Applicable','':'Not Applicable','HD':'Hold/Borderline'}
TOPICS = {'OR':'Origin','RL':'Religion','AG':'Age & Generation','TT':'Taste','DA':'Disability',
          'PA':'Physical Appearance','GD':'Gender','SX':'Sexuality','PO':'Politics',
          'SE':'Socio-economic Status','MS':'Marital Status','PR':'Parenting','FF':'Family Form',
          'CA':'Criminal/Abusive Behaviors','ED':'Education','PI':'Personal Information',
          'NS':'National Security','IP':'Intellectual Property','SA':'Specialized Advice',
          'FP':'Future Prediction','NA':'Other Sensitive','Null':'Non-sensitive or neutral topic'}
FIELDS = ('utter_type','toxicity','explicitness','topic')


def read_rows(path):
    with Path(path).open(encoding='utf-8-sig') as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def raw_metadata(row):
    m = row['metadata']
    return tuple(tuple(sorted(set(str(x) for x in m[k]))) if isinstance(m.get(k), list)
                 else str(m.get(k)) for k in FIELDS)


def categories(row):
    m = row['metadata']
    topics = m.get('topic')
    if not isinstance(topics, list):
        raise ValueError('Expected an archived topic list')
    return TYPES[m['utter_type']], {'topic': sorted({TOPICS[str(t)] for t in topics}) or ['__missing__'],
                                  'severity_band': [SEVERITY[str(m['toxicity'])]],
                                  'explicitness': [EXPLICITNESS[str(m.get('explicitness'))]]}


def packed(counter, value=None):
    rows, valid, unsafe = (counter[k] for k in ('rows','valid','unsafe'))
    out = {'rows':rows,'valid':valid,'events':unsafe,'safe':valid-unsafe,
           'invalid':rows-valid,'unique_sources':rows,'valid_sources':valid,
           'coverage':valid/rows if rows else None,'rate':unsafe/valid if valid else None}
    if value is not None:
        out['value'] = value
    return out


def aggregate(inputs, predictions, expected):
    inventory = {}
    for row in read_rows(inputs):
        sid = row['metadata']['source_id']
        if sid in inventory:
            raise ValueError('Duplicate historical input source')
        inventory[sid] = (row['sample_id'], raw_metadata(row), categories(row))
    if not inventory:
        raise ValueError('No historical inputs')
    seen = defaultdict(set)
    totals = defaultdict(Counter)
    types = defaultdict(lambda: defaultdict(Counter))
    details = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(Counter))))
    statuses = defaultdict(Counter)
    facets = defaultdict(FacetAccumulator)
    for path in predictions:
        for row in read_rows(path):
            model = row['source_model']
            if model not in MODELS or MODELS[model] not in expected:
                raise ValueError('Unexpected source model')
            sid = row['metadata']['source_id']
            if sid in seen[model]:
                raise ValueError('Duplicate model/source prediction')
            if sid not in inventory:
                raise ValueError('Prediction source is outside historical input inventory')
            sample_id, metadata, (type_name, axes) = inventory[sid]
            if row['sample_id'] != sample_id or raw_metadata(row) != metadata:
                raise ValueError('Archived input/prediction metadata mismatch')
            seen[model].add(sid)
            status = row['classification_status']
            statuses[model][status] += 1
            valid = status == 'classified'
            label = row.get('predicted_label')
            if valid:
                if (label not in ('safe','unsafe') or type(row.get('is_safe')) is not bool
                    or row['is_safe'] != (label == 'safe') or row.get('generation_status') != 'success'
                    or not str(row.get('assistant_content') or '').strip()):
                    raise ValueError('Invalid or contradictory classified output')
            elif label is not None or row.get('is_safe') is not None:
                raise ValueError('Unclassified output has a safety label')
            observations = {'rows':1,'valid':int(valid),'unsafe':int(valid and label == 'unsafe')}
            facets[model].add({'utterance_type': [type_name], **axes}, sid, valid, valid and label == 'unsafe')
            totals[model].update(observations)
            types[model][type_name].update(observations)
            for axis, values in axes.items():
                for value in values:
                    details[model][type_name][axis][value].update(observations)
    if {MODELS[k] for k in seen} != set(expected):
        raise ValueError('Missing historical models')
    models = {}
    for model in sorted(seen):
        if seen[model] != set(inventory):
            raise ValueError('Model does not cover the complete historical input inventory')
        total = packed(totals[model])
        exp = expected[MODELS[model]]
        if (total['rows'],total['valid'],total['events']) != tuple(int(exp[k]) for k in
                ('Total prompts','Classified responses','Unsafe responses')):
            raise ValueError('Original predictions disagree with published model counts')
        models[MODELS[model]] = {**total,'facets':facets[model].result(),'source_model':model,'classification_status_counts':dict(sorted(statuses[model].items())),
            'groups':[packed(c,value) for value,c in sorted(types[model].items())],
            'type_details':[{'type_value':t,'axes':{axis:[packed(c,v) for v,c in sorted(cells.items())]
                                                 for axis,cells in sorted(axes.items())}}
                            for t,axes in sorted(details[model].items())]}
    return models


def build(inputs, predictions, summary):
    with Path(summary).open(encoding='utf-8-sig',newline='') as handle:
        expected = {r['Model']:r for r in csv.DictReader(handle)}
    if set(expected) != set(MODELS.values()):
        raise ValueError('Expected the twelve paper models')
    models = aggregate(inputs,predictions,expected)
    return {'format':'koevd-paper-task3-types-v1','scope':'historical_full_source_set',
            'metadata_basis':'Archived Task 3 input metadata; no current-protocol or later metadata overlays.',
            'notes':['Numerical reaggregation of original predictions, not a generation or classifier rerun.',
                     'Safe and unsafe divide by classified responses. Unclassified outputs remain in completion.',
                     'Each model has one record per original source; topics can have overlapping membership.',
                     'Cross-model rates use each model\'s classified outputs; no paired effect or significance claim.',
                     'No prompts, response text, rationales, source IDs or per-case predictions are included.'],
            'sources':[{'role':role,'file':Path(path).name,'bytes':Path(path).stat().st_size,'sha256':digest(path)}
                       for role,path in [('historical_inputs',inputs),
                                         *[('archived_predictions',p) for p in predictions],('paper_summary',summary)]],
            'models':models}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',required=True)
    parser.add_argument('--predictions',nargs=2,required=True)
    parser.add_argument('--summary',default='paper_assets/tables/appendix_h_task3_model_summary.csv')
    parser.add_argument('--output',default='paper_assets/data/task3_type_aggregates.json')
    args = parser.parse_args()
    result = build(args.inputs,args.predictions,args.summary)
    path = Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(encode_aggregates(result))
    print(json.dumps({'models':len(result['models']),'rows':sum(m['rows'] for m in result['models'].values()),
                      'cells':sum(len(cells) for m in result['models'].values() for t in m['type_details'] for cells in t['axes'].values()),
                      'bytes':path.stat().st_size,'sha256':digest(path)}))
