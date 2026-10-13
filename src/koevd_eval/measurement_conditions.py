"""Portable, versioned declarations and observations of classifier conditions.

These fields describe submitted evidence. They cannot authenticate inference,
assert classifier accuracy, or certify absence of truncation.
"""
from copy import deepcopy

VERSION = 'koevd-measurement-conditions-v1'
PACKAGES = ('torch', 'transformers', 'peft', 'accelerate')
REQUESTS = ('requested_dtype', 'input_order', 'inference_mode', 'requested_max_new_tokens')


def _keys(value, fields, name):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ValueError('Invalid ' + name + ' fields')


def _positive(value, name, *, nullable=False):
    if value is None and nullable: return
    if type(value) is not int or value < 1: raise ValueError('Invalid ' + name)


def _text(value, name):
    if value is not None and (not isinstance(value, str) or not value or len(value) > 256):
        raise ValueError('Invalid ' + name)


def validate_options(options):
    _keys(options, ('max_new_tokens', 'do_sample', 'pad_token_id', 'eos_token_id'), 'generate options')
    _positive(options['max_new_tokens'], 'observed token budget')
    if type(options['do_sample']) is not bool: raise ValueError('Invalid observed sampling flag')
    for field in ('pad_token_id', 'eos_token_id'):
        value = options[field]
        if value is None: continue
        values = value if field == 'eos_token_id' and isinstance(value, list) else [value]
        if not values or len(values) > 64 or any(type(v) is not int or v < 0 for v in values):
            raise ValueError('Invalid observed special token IDs')


def validate_conditions(value, *, records=None):
    _keys(value, ('version', *REQUESTS, 'observation'), 'measurement conditions')
    if value['version'] != VERSION: raise ValueError('Unsupported measurement conditions version')
    if value['requested_dtype'] not in (None, 'auto', 'float16', 'bfloat16', 'float32'):
        raise ValueError('Invalid requested classifier dtype')
    if value['input_order'] not in (None, 'original', 'reverse') or value['inference_mode'] not in (None, 'batch', 'single'):
        raise ValueError('Invalid classifier scheduling declaration')
    _positive(value['requested_max_new_tokens'], 'requested classifier token budget', nullable=True)
    obs = value['observation']
    if obs is None: return
    _keys(obs, ('trace_version', 'trace_sha256', 'runtime', 'generate_options', 'counts'), 'measurement observation')
    if obs['trace_version'] != 'koevd-measurement-trace-v1': raise ValueError('Unsupported observation trace version')
    sha = obs['trace_sha256']
    if not isinstance(sha, str) or len(sha) != 64 or any(c not in '0123456789abcdef' for c in sha):
        raise ValueError('Invalid observation trace hash')
    runtime = obs['runtime']
    if runtime is not None:
        _keys(runtime, ('parameter_dtype_elements', 'model_config_max_position_embeddings',
                       'tokenizer_class', 'tokenizer_model_max_length', 'tokenizer_padding_side', 'package_versions'), 'portable runtime')
        dtypes = runtime['parameter_dtype_elements']
        if not isinstance(dtypes, dict) or not 1 <= len(dtypes) <= 32: raise ValueError('Invalid parameter dtype observations')
        for name, count in dtypes.items():
            if not isinstance(name, str): raise ValueError('Invalid parameter dtype name')
            _text(name, 'parameter dtype'); _positive(count, 'parameter dtype count')
        for field in ('model_config_max_position_embeddings', 'tokenizer_model_max_length'):
            _positive(runtime[field], field, nullable=True)
        _text(runtime['tokenizer_class'], 'tokenizer class')
        if runtime['tokenizer_padding_side'] not in (None, 'left', 'right'): raise ValueError('Invalid tokenizer padding side')
        _keys(runtime['package_versions'], PACKAGES, 'measurement package versions')
        for name, version in runtime['package_versions'].items(): _text(version, name + ' version')
    options = obs['generate_options']
    if not isinstance(options, list) or len(options) > 16: raise ValueError('Invalid observed generation options')
    from .results import canonical_hash
    hashes = set()
    for option in options:
        validate_options(option)
        digest = canonical_hash(option)
        if digest in hashes: raise ValueError('Duplicate observed generation options')
        hashes.add(digest)
        requested = value['requested_max_new_tokens']
        if requested is not None and option['max_new_tokens'] != requested:
            raise ValueError('Observed token budget differs from requested override')
    counts = obs['counts']
    _keys(counts, ('total', 'observed', 'not_applicable', 'token_parity_mismatch',
                  'context_exceeded', 'context_unknown', 'budget_without_eos', 'budget_unknown'), 'measurement observation counts')
    if any(type(n) is not int or not 0 <= n <= 100000 for n in counts.values()):
        raise ValueError('Invalid measurement observation count')
    observed = counts['observed']
    if counts['total'] != observed + counts['not_applicable'] or any(counts[k] > observed for k in counts if k not in ('total', 'not_applicable')):
        raise ValueError('Inconsistent measurement observation counts')
    if counts['context_exceeded'] + counts['context_unknown'] > observed or counts['budget_without_eos'] + counts['budget_unknown'] > observed:
        raise ValueError('Inconsistent measurement observation status counts')
    if bool(observed) != bool(options) or bool(observed) != (runtime is not None):
        raise ValueError('Observed rows require runtime and generate options')
    if records is not None:
        eligible = sum(r['response']['status'] == 'ok' and bool(r['response']['text'].strip()) for r in records)
        if counts['total'] != len(records) or observed != eligible:
            raise ValueError('Measurement observation coverage differs from frozen responses')
        if any(r['measurement']['status'] != 'reported' for r in records if r['response']['status'] == 'ok' and r['response']['text'].strip()):
            raise ValueError('Successful observation requires reported measurement rows')


def from_evidence(evidence, trace=None):
    """Allowlist only; paths, device names, prompts and raw outputs stay private."""
    value = {'version': VERSION, **{k: deepcopy(evidence.get(k)) for k in REQUESTS}, 'observation': None}
    if trace is not None:
        for key in REQUESTS:
            actual = trace.get(key)
            if key in evidence and key in trace and evidence[key] != actual:
                raise ValueError('Trace disagrees with manifest classifier ' + key)
            if key in trace: value[key] = deepcopy(actual)
        if evidence.get('batch_size') != trace['batch_size']:
            raise ValueError('Trace disagrees with manifest classifier batch size')
        runtime = trace.get('runtime')
        fields = ('parameter_dtype_elements', 'model_config_max_position_embeddings', 'tokenizer_class',
                  'tokenizer_model_max_length', 'tokenizer_padding_side', 'package_versions')
        observations = [r['observed_generate'] for r in trace['records'] if r['observed_generate'] is not None]
        from .results import canonical_hash
        unique = {canonical_hash(o['generation_kwargs']): deepcopy(o['generation_kwargs']) for o in observations}
        counts = {'total': len(trace['records']), 'observed': len(observations),
                  'not_applicable': len(trace['records']) - len(observations),
                  'token_parity_mismatch': sum(o['single_template_tokens_equal'] is False for o in observations),
                  'context_exceeded': sum(o.get('exceeds_declared_model_context') is True for o in observations),
                  'context_unknown': sum(o.get('exceeds_declared_model_context') is None for o in observations),
                  'budget_without_eos': sum(o.get('reached_token_budget_without_eos') is True for o in observations),
                  'budget_unknown': sum(o.get('reached_token_budget_without_eos') is None for o in observations)}
        value['observation'] = {'trace_version': trace['format'], 'trace_sha256': evidence['trace_sha256'],
                                'runtime': {k: deepcopy(runtime.get(k)) for k in fields} if runtime is not None else None,
                                'generate_options': [unique[k] for k in sorted(unique)], 'counts': counts}
    validate_conditions(value)
    return value


def comparison_fields(evidence):
    """Conditions only; trace identity and response-dependent counts are not settings."""
    value = evidence.get('conditions') or {}
    fields = {key: value.get(key) for key in REQUESTS}
    obs = value.get('observation') or {}
    fields['observed_generate_options'] = obs.get('generate_options') or None
    runtime = obs.get('runtime') or {}
    for key in ('tokenizer_class', 'tokenizer_model_max_length', 'tokenizer_padding_side', 'model_config_max_position_embeddings'):
        fields[key] = runtime.get(key)
    # Dtype proportions and token lengths vary with target responses, not classifier settings.
    fields['observed_parameter_dtypes'] = sorted(runtime['parameter_dtype_elements']) if runtime.get('parameter_dtype_elements') else None
    for package in PACKAGES: fields['package_versions.' + package] = (runtime.get('package_versions') or {}).get(package)
    return fields
