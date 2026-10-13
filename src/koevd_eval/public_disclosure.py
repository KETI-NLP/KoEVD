"""Disclosure projection AFTER analysis; never changes scoring or original data.

Configured reference originals stay private. This public beta exposes every
measured record and numeric comparison without redistributing unreviewed freeform
responses, prompts, mock tool arguments or execution/request identifiers.
"""
from copy import deepcopy

POLICY = 'koevd-public-reference-disclosure-v1'
WITHHELD = '[Reference text withheld in the public beta; measured labels and metrics are retained.]'


def disclose_references(report, artifact_ids):
    """Project ONLY configured references. Personal session outputs stay intact."""
    references = set(artifact_ids)
    projected = deepcopy(report)
    for profile in projected['runs']:
        if profile['artifact_sha256'] not in references:
            continue
        profile['disclosure'] = {
            'policy': POLICY, 'original_artifact_sha256': profile['artifact_sha256'],
            'raw_text_public': False, 'metrics_calculated_from_original': True,
            'note': 'All records and numerical measurements use the unchanged original. Reference prompts, freeform responses, tool arguments and request IDs are withheld. This report is not a portable original result.'}
        profile['interpretation'] = [*profile['interpretation'], profile['disclosure']['note']]
        run = profile['run']
        run['id'] = 'reference-' + profile['artifact_sha256'][:16]
        run['created_at'] = '[withheld]'
        run['migration'] = None
        for case in profile['cases']:
            case['run_id'] = run['id']
            case['disclosure'] = {'policy': POLICY, 'raw_text_public': False}
            case['messages'] = [{'role': 'user', 'content': WITHHELD}]
            response = case['response']
            for field in ('text', 'reasoning_content', 'refusal'):
                response[field] = WITHHELD if field == 'text' else None
            for field in ('request_id', 'response_id', 'server_model', 'execution'):
                response[field] = None
            # Keep the ORIGINAL response hash: the projected display is not a
            # replacement response or a newly sealed portable result.
            case['metadata'] = {key: value for key, value in case['metadata'].items()
                                if key in ('severity_band', 'explicitness', 'utterance_type',
                                           'topic', 'risk_category', 'evaluation_subset',
                                           'task_variant', 'prompt_variant')}
            gold = case['gold'] or {}
            case['gold'] = {key: value for key, value in gold.items()
                            if key in ('label', 'answer', 'available_tools', 'unsafe_tools')}
            if case['task'] == 5 and isinstance(case['parsed'], dict):
                case['parsed'] = {key: value for key, value in case['parsed'].items()
                                  if key in ('decision', 'tool_name')}
            if case['task'] == 4:
                value = (case['measurement'] or {}).get('value')
                if isinstance(value, dict):
                    value = {'strategies': value.get('strategies', [])}
                    case['measurement']['value'] = value
                    case['parsed'] = deepcopy(value)
    for comparison in projected.get('comparisons', []):
        for side in ('left','right'):
            if comparison.get(side+'_artifact') in references:
                comparison[side+'_run_id']='reference-'+comparison[side+'_artifact'][:16]
    return projected
