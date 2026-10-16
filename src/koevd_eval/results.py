"""Portable result contract. Trusted inputs are supplied separately by the operator.

Hashes check consistency, not model identity, accuracy, or generation authenticity.
No uploaded gold, metadata, or aggregate is used for scoring.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import uuid

from .common import read_jsonl, row_id, write_jsonl
from .overlap import source_id
from .pipeline import file_sha, save_json, verify_prepared, verify_predictions
from .profile import identity, variant, write_report
from .run_openai_compatible import input_digest, unique_rows

SCHEMA = 'koevd-results-v1'
INDEX_SCHEMA = 'koevd-input-index-v1'
TASKS = (1, 2, 3, 4, 5)
MAX_BYTES = 128 * 1024 * 1024
MAX_RECORDS = 100_000
MAX_TEXT_BYTES = 1024 * 1024


def canonical_hash(value):
    data = json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def read_document(path, max_bytes=MAX_BYTES):
    """Bound reads and reject ambiguous JSON, duplicate keys, NaN and Infinity."""
    with Path(path).open('rb') as handle:
        raw = handle.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError('JSON exceeds upload size limit')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Nonfinite JSON number')))
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('Invalid UTF-8 JSON document') from exc
    if not isinstance(value, dict):
        raise ValueError('Expected a JSON object')
    return value


def _keys(obj, expected, description, optional=()):
    expected=set(expected)
    if not isinstance(obj, dict) or not expected <= set(obj) or not set(obj) <= expected | set(optional):
        raise ValueError(f'{description}: unexpected or missing fields')


def _seal(document):
    document = deepcopy(document)
    document['content_sha256'] = canonical_hash(document)
    return document


def _verify_seal(document):
    payload = {k: v for k, v in document.items() if k != 'content_sha256'}
    if document.get('content_sha256') != canonical_hash(payload):
        raise ValueError('Content checksum mismatch')


def _prepared_path(run_dir, entry):
    # Local manifests cannot use traversal to read unrelated files during export.
    name = entry.get('file')
    if not isinstance(name, str) or Path(name).name != name or '/' in name or '\\' in name:
        raise ValueError('Prepared input filename must be a basename')
    root = Path(run_dir).resolve()
    path = (root / name).resolve()
    if path.parent != root:
        raise ValueError('Prepared input escapes run directory')
    return path


def build_index(run_dir, *, dataset_repo=None, dataset_revision=None, code_revision=None):
    """Create a LOCAL index; callers must independently decide whether to trust it.

    A self-uploaded index must never be promoted to an official registry index.
    Full-run selection alone does not establish a standard protocol.
    """
    root = Path(run_dir)
    manifest = read_document(root / 'pipeline.json')
    for entry in manifest['inputs'].values():
        _prepared_path(root, entry)
    verify_prepared(root, manifest)
    preparation = manifest['preparation']
    protocol = {
        'dataset': {'repo': dataset_repo, 'revision': dataset_revision,
                    'files': deepcopy(preparation['dataset_files'])},
        'split': preparation['split'], 'limit_sources': preparation['limit_sources'],
        'kind': 'smoke' if preparation['limit_sources'] is not None else 'custom',
        'metadata_view': 'canonical-prepared',
        'scoring': {'historical': 'koevd-0.2.0', 'diagnostic': 'strict-profile-v1'},
        'preparation_code_revision': code_revision,
    }
    inputs = {}
    for task in TASKS:
        entry = manifest['inputs'][str(3 if task == 4 else task)]
        rows = unique_rows(read_jsonl(_prepared_path(root, entry)))
        if len(rows) != entry['rows']:
            raise ValueError('Prepared row count mismatch')
        inputs[str(task)] = {key: {'input_sha256': input_digest(row), 'row': row}
                             for key, row in sorted(rows.items())}
    return _seal({'schema_version': INDEX_SCHEMA, 'protocol': protocol, 'inputs': inputs})


def validate_index(index):
    _keys(index, ('schema_version', 'protocol', 'inputs', 'content_sha256'), 'Index')
    if index['schema_version'] != INDEX_SCHEMA:
        raise ValueError('Unsupported input index version')
    _verify_seal(index)
    _keys(index['inputs'], map(str, TASKS), 'Index tasks')
    if not isinstance(index['protocol'], dict):
        raise ValueError('Index protocol must be an object')
    for entries in index['inputs'].values():
        if not isinstance(entries, dict) or not entries or len(entries) > MAX_RECORDS:
            raise ValueError('Invalid input index entries')
        for key, entry in entries.items():
            _keys(entry, ('input_sha256', 'row'), 'Index entry')
            row = entry['row']
            if not isinstance(row, dict) or row_id(row) != key or not source_id(row):
                raise ValueError('Invalid index sample/source identity')
            if entry['input_sha256'] != input_digest(row):
                raise ValueError('Index input checksum mismatch')
    if index['inputs']['3'] != index['inputs']['4']:
        raise ValueError('Task 4 must reuse Task 3 inputs')


def _measurement_evidence(root, manifest, task, predictions):
    if manifest.get('measurement_pending',{}).get(str(task)):
        raise ValueError('Measurement promotion pending; repeat the classify command before export')
    path = root / f'task{task}_measured.jsonl'
    evidence = manifest.get('measurements', {}).get(str(task))
    if not evidence or evidence.get('prediction_sha256') != file_sha(root / 'task3_predictions.jsonl'):
        raise ValueError('Measurements missing/stale; rerun classify')
    if evidence.get('output_sha256') != file_sha(path):
        raise ValueError('Measurement output checksum mismatch')
    rows = unique_rows(read_jsonl(path))
    if set(rows) != set(predictions) or any(
        any(rows[key].get(field) != value for field, value in original.items())
        for key, original in predictions.items()
    ):
        raise ValueError('Measurements changed or omitted generation fields')
    # Allowlist avoids raw errors, endpoint and local absolute paths.
    portable = {k: deepcopy(evidence.get(k)) for k in ('batch_size', 'adapter', 'base')}
    portable.update(revision=None, precision=None, input_truncation=None,
                    verification='user_reported', accuracy_status='measurement_limited')
    trace = None
    if evidence.get('trace_sha256') is not None:
        from .measurement_trace import validate_trace
        trace_path=root/f'task{task}_measurement_trace.json'
        if file_sha(trace_path)!=evidence['trace_sha256']:
            raise ValueError('Measurement trace checksum mismatch')
        trace=validate_trace(read_document(trace_path),root/'task3_predictions.jsonl',path,task)
        dtypes=(trace.get('runtime') or {}).get('parameter_dtype_elements')
        if dtypes:
            portable['precision']='reported_parameter_dtypes:'+','.join(sorted(dtypes))
        # No inference-authenticity, revision or no-truncation certification is inferred.
    if trace is not None or any(k in evidence for k in ('requested_dtype', 'input_order', 'inference_mode', 'requested_max_new_tokens')):
        from .measurement_conditions import from_evidence
        portable['conditions'] = from_evidence(evidence, trace)
    return rows, portable


def export_run(run_dir, index, *, code_revision=None):
    """Migrate the existing pipeline, retaining unknown provenance as null.

    Completed generation is required; API failure rows remain in the denominator.
    Absent classifier files become explicit unmeasured records, not safe labels.
    """
    validate_index(index)
    root = Path(run_dir)
    manifest = read_document(root / 'pipeline.json')
    for entry in manifest['inputs'].values():
        _prepared_path(root, entry)
    verify_prepared(root, manifest)
    model = manifest.get('generation', {}).get('model')
    if not isinstance(model, str) or not model.strip():
        raise ValueError('Generation model is missing')
    predictions = {task: unique_rows(verify_predictions(root, manifest, task))
                   for task in (1, 2, 3, 5)}
    if manifest.get('measurement_pending'):
        raise ValueError('Measurement promotion pending; repeat the classify command before export')
    measured, provenance = {}, {}
    for task in (3, 4):
        if (root / f'task{task}_measured.jsonl').exists() or str(task) in manifest.get('measurements', {}):
            measured[task], provenance[str(task)] = _measurement_evidence(root, manifest, task, predictions[3])
        else:
            provenance[str(task)] = None
    task_rows = {task: measured.get(task, predictions[3 if task == 4 else task]) for task in TASKS}
    # Do not reuse the safety measurement as a strategy result when Task 4 is absent.
    for task in (3, 4):
        if task not in measured:
            task_rows[task] = {k:{**row, 'measurement':None} for k,row in task_rows[task].items()}
    generation = manifest['generation']
    decoding={'temperature':generation.get('temperature'),'max_tokens':generation.get('max_tokens'),
              'seed':(generation.get('extra_body') or {}).get('seed'),
              'engine_version':generation.get('engine_version')}
    if generation.get('extra_body'):decoding['extra_body']=deepcopy(generation['extra_body'])
    return assemble_results(task_rows,index,model=model,generation=decoding,measurements=provenance,
                            code_revision=code_revision,migration='koevd-pipeline-v1',
                            run_identity=manifest.get('generation_run'),
                            model_provenance=generation.get('model_provenance'))


def unknown_measurement_provenance():
    return {'batch_size':None, 'adapter':None, 'base':None, 'revision':None,
            'precision':None, 'input_truncation':None, 'verification':'user_reported',
            'accuracy_status':'measurement_limited'}


def assemble_results(task_rows, index, *, model, generation, measurements,
                     code_revision=None, migration=None, run_identity=None, model_provenance=None):
    """One shared export path; restoration and scoring always use the trusted index."""
    validate_index(index)
    records = []
    for task in TASKS:
        rows = task_rows[task]
        entries = index['inputs'][str(task)]
        if set(rows) != set(entries):
            raise ValueError('Run does not match trusted expected sample set')
        for key in sorted(entries):
            row, entry = rows[key], entries[key]
            original = entry['row']
            if identity(row) != identity(original) or source_id(row) != source_id(original):
                raise ValueError('Run input differs from trusted index')
            if row.get('input_sha256') not in (None, entry['input_sha256']):
                raise ValueError('Generation input checksum mismatch')
            if row.get('evaluated_model') not in (None, model):
                raise ValueError('Imported rows mix target models; migrate each run separately')
            text = row.get('prediction')
            measurement = row.get('measurement') if task in (3, 4) else None
            records.append({
                'task':task, 'sample_id':key, 'source_id':source_id(original),
                'variant':variant(original, task), 'input_sha256':entry['input_sha256'],
                'response':portable_response(row),
                'measurement':{'value':measurement,
                               'status':('reported' if measurement is not None else 'unmeasured') if row.get('api_status') == 'ok' and text and text.strip() else 'not_applicable',
                               'response_sha256':canonical_hash(text) if task in (3,4) else None,
                               'input_sha256':entry['input_sha256'] if task in (3,4) else None},
            })
    payload = _seal({
        'schema_version':SCHEMA, 'artifact_kind':'full_records',
        'run':{'id':run_identity['id'] if run_identity else str(uuid.uuid4()),
               'created_at':run_identity['created_at'] if run_identity else datetime.now(timezone.utc).isoformat(),
               'code_revision':code_revision, 'migration':migration,
               'model':{'id':model, 'revision':None, 'chat_template':None, 'dtype':None,
                        'quantization':None, 'thinking':None, **(model_provenance or {}),'verification':'user_reported'},
               'generation':deepcopy(generation), 'measurements':deepcopy(measurements)},
        'protocol_sha256':canonical_hash(index['protocol']),
        'input_index_sha256':index['content_sha256'],
        'publication':{'status':'local', 'response_scope':'included'}, 'records':records,
    })
    validate_results(payload, index)
    return payload


def migrate_jsonl(paths, index, *, model=None, code_revision=None):
    """Import prepared-row JSONL without inventing missing execution provenance.

    Files must retain original inputs and failures. Changed or partial input sets
    cannot be repaired by an upload. Missing Task 4 becomes explicit unmeasured
    reuse of Task 3; supplied classifier results remain measurement-limited.
    """
    validate_index(index)
    if not set(paths) <= set(TASKS) or not {1,2,3,5} <= set(paths):
        raise ValueError('Migration requires Task 1, 2, 3 and 5 prediction files')
    rows = {task:unique_rows(read_jsonl(path)) for task,path in paths.items()}
    models = {row.get('evaluated_model') for values in rows.values() for row in values.values()
              if row.get('evaluated_model') is not None}
    if model is None:
        if len(models) != 1:
            raise ValueError('Specify one target model ID when legacy identity is absent')
        model = next(iter(models))
    if models - {model}:
        raise ValueError('Imported rows mix target models; migrate each run separately')
    if 4 not in rows:
        rows[4] = {key:{**row, 'measurement':None} for key,row in rows[3].items()}
    provenance = {str(task):unknown_measurement_provenance() if any(
        row.get('measurement') is not None for row in rows[task].values()) else None for task in (3,4)}
    # Only assert shared decoding fields recorded on every original generation row.
    generated = [row for task in (1,2,3,5) for row in rows[task].values()]
    generation = {'temperature':None, 'max_tokens':None, 'seed':None, 'engine_version':None}
    for field in ('temperature','max_tokens'):
        values = [row.get('run_config', {}).get(field) for row in generated]
        known = {v for v in values if v is not None}
        if len(known) > 1:
            raise ValueError('Legacy files mix decoding settings; import runs separately')
        if all(v is not None for v in values):
            generation[field] = values[0]
    return assemble_results(rows, index, model=model, generation=generation,
                            measurements=provenance, code_revision=code_revision,
                            migration='legacy-prepared-jsonl-v1')


def portable_response(row):
    text=row.get('prediction')
    observed=row.get('generation') or {}
    response={'text':text,'sha256':canonical_hash(text),'status':row.get('api_status'),
              'finish_reason':observed.get('finish_reason'),'usage':deepcopy(observed.get('usage')),
              'request_id':observed.get('request_id')}
    if observed:
        for key in ('response_id','server_model','reasoning_content','refusal'):
            response[key]=observed.get(key)
        response['execution']={key:deepcopy(observed.get(key)) for key in
                               ('run_id','selection_policy','selected_attempt_id','attempts','parameter_status')}
        # Failure/interruption has no parameter acceptance evidence.
        if response['execution']['parameter_status'] is None:
            response['execution']['parameter_status']='requested_unverified'
    return response


def validate_execution(execution, api_status):
    _keys(execution, ('run_id','selection_policy','selected_attempt_id','attempts','parameter_status'), 'Execution')
    if not isinstance(execution['run_id'],str) or not execution['run_id'] or len(execution['run_id'])>128:
        raise ValueError('Invalid execution run ID')
    if execution['selection_policy']!='first_accepted_api_response' or execution['parameter_status']!='requested_unverified':
        raise ValueError('Unsupported execution selection/parameter assertion')
    attempts=execution['attempts']
    if not isinstance(attempts,list) or len(attempts)>1000:
        raise ValueError('Invalid attempt ledger')
    seen=set();previous=0;successful=[]
    for attempt in attempts:
        _keys(attempt, ('id','ordinal','started_at','status','finished_at','latency_seconds','error_kind','http_status'), 'Attempt',optional=('client_controls',))
        if 'client_controls' in attempt:
            controls=attempt['client_controls']
            _keys(controls, ('workers','timeout_seconds','retries','retry_delay_seconds'), 'Client controls')
            if type(controls['workers']) is not int or not 1<=controls['workers']<=64 or type(controls['retries']) is not int or controls['retries']<0:
                raise ValueError('Invalid recorded workers/retries')
            for field in ('timeout_seconds','retry_delay_seconds'):
                value=controls[field]
                if type(value) not in (int,float) or value<0 or field=='timeout_seconds' and value==0:
                    raise ValueError('Invalid recorded client timeout/backoff')
        key=attempt['id']
        if not isinstance(key,str) or not key or len(key)>128 or key in seen:
            raise ValueError('Invalid/duplicate attempt identity')
        seen.add(key)
        if type(attempt['ordinal']) is not int or attempt['ordinal']<=previous:
            raise ValueError('Attempt order must be increasing')
        previous=attempt['ordinal']
        if attempt['status'] not in ('ok','error','interrupted_unknown'):
            raise ValueError('Invalid attempt status')
        for field in ('started_at','finished_at','error_kind'):
            value=attempt[field]
            if value is not None and (not isinstance(value,str) or len(value)>128):
                raise ValueError('Invalid attempt metadata')
        if not attempt['started_at']:raise ValueError('Attempt start time is required')
        latency=attempt['latency_seconds']
        if latency is not None and (type(latency) not in (int,float) or latency<0):
            raise ValueError('Invalid request latency')
        status=attempt['http_status']
        if status is not None and (type(status) is not int or not 100<=status<=599):
            raise ValueError('Invalid attempt HTTP status')
        if attempt['status']=='ok':successful.append(key)
    selected=execution['selected_attempt_id']
    if api_status=='ok':
        if len(successful)!=1 or selected!=successful[0] or attempts[-1]['id']!=selected:
            raise ValueError('Selected response must be the first/only accepted attempt')
    elif selected is not None or successful:
        raise ValueError('Failed response cannot select a successful attempt')


def _validate_run(run):
    _keys(run, ('id', 'created_at', 'code_revision', 'migration', 'model', 'generation', 'measurements'), 'Run')
    for field in ('id', 'created_at'):
        if not isinstance(run[field], str) or not run[field] or len(run[field]) > 128:
            raise ValueError('Invalid run identity/timestamp')
    for field in ('code_revision', 'migration'):
        if run[field] is not None and (not isinstance(run[field], str) or len(run[field]) > 256):
            raise ValueError('Invalid optional run provenance')
    _keys(run['model'], ('id', 'revision', 'chat_template', 'dtype', 'quantization', 'thinking', 'verification'), 'Model')
    if run['model']['verification'] != 'user_reported':
        raise ValueError('Uploaded model identity cannot assert verification')
    for field in ('revision', 'chat_template', 'dtype', 'quantization', 'thinking'):
        if run['model'][field] is not None and (not isinstance(run['model'][field], str) or len(run['model'][field]) > 4096):
            raise ValueError('Invalid optional model provenance')
    _keys(run['generation'], ('temperature', 'max_tokens', 'seed', 'engine_version'), 'Generation', optional=('extra_body',))
    generation = run['generation']
    if generation['temperature'] is not None and (type(generation['temperature']) not in (float, int) or generation['temperature'] < 0):
        raise ValueError('Invalid generation temperature')
    if generation['max_tokens'] is not None and (type(generation['max_tokens']) is not int or generation['max_tokens'] < 1):
        raise ValueError('Invalid generation token limit')
    if generation['seed'] is not None and type(generation['seed']) is not int:
        raise ValueError('Invalid seed')
    if generation['engine_version'] is not None and not isinstance(generation['engine_version'], str):
        raise ValueError('Invalid engine version')
    if 'extra_body' in generation:
        from .run_openai_compatible import validate_extra_body
        validate_extra_body(generation['extra_body'])
        if generation['seed'] != generation['extra_body'].get('seed'):
            raise ValueError('Conflicting recorded generation seed')
    _keys(run['measurements'], ('3', '4'), 'Classifier provenance')
    for evidence in run['measurements'].values():
        if evidence is None:
            continue
        _keys(evidence, ('batch_size', 'adapter', 'base', 'revision', 'precision',
                         'input_truncation', 'verification', 'accuracy_status'), 'Classifier evidence', optional=('conditions',))
        if 'conditions' in evidence:
            from .measurement_conditions import validate_conditions
            validate_conditions(evidence['conditions'])
        if evidence['verification'] != 'user_reported' or evidence['accuracy_status'] != 'measurement_limited':
            raise ValueError('Uploaded classifier provenance cannot assert accuracy/verification')
        if evidence['batch_size'] is not None and (type(evidence['batch_size']) is not int or evidence['batch_size'] < 1):
            raise ValueError('Invalid classifier batch size')
        for field in ('adapter', 'base'):
            fingerprints = evidence[field]
            if fingerprints is None:
                continue
            if not isinstance(fingerprints, dict) or not fingerprints:
                raise ValueError('Missing classifier artifact fingerprints')
            for name, checksum in fingerprints.items():
                if (Path(name).name != name or '/' in name or '\\' in name or ':' in name
                        or not isinstance(checksum, str) or len(checksum) != 64
                        or any(c not in '0123456789abcdef' for c in checksum)):
                    raise ValueError('Invalid classifier fingerprint')
        for field in ('revision', 'precision', 'input_truncation'):
            if evidence[field] is not None and not isinstance(evidence[field], str):
                raise ValueError('Invalid optional classifier provenance')


def _validate_measurement_value(value, task):
    if value is None:
        return
    allowed = {'label', 'is_safe', 'raw_output'} if task == 3 else {'strategies', 'is_unsafe', 'raw_output'}
    if not isinstance(value, dict) or not set(value) <= allowed:
        raise ValueError('Unknown classifier fields; confidence is not supplied by these classifiers')
    if 'raw_output' in value and (not isinstance(value['raw_output'], str)
            or len(value['raw_output'].encode('utf-8')) > MAX_TEXT_BYTES):
        raise ValueError('Invalid classifier raw output')
    if task == 3:
        if 'label' not in value or value['label'] not in ('safe', 'unsafe', None):
            raise ValueError('Invalid safety label')
        if 'is_safe' in value and (type(value['is_safe']) is not bool or value['is_safe'] != (value['label'] == 'safe')):
            raise ValueError('Inconsistent safety indicator')
    else:
        strategies = value.get('strategies')
        if not isinstance(strategies, list) or len(strategies) > 16 or any(not isinstance(s, str) for s in strategies):
            raise ValueError('Invalid strategy labels')
        known = {'a_boundary setting', 'a_detouring q', 'a_evaluation', 'a_providing definitions',
                 'a_reiteration', 'b_agreeing speech', 'b_counter speech', 'b_neutral speech',
                 'c_educating', 'c_info providing', 'c_reasoning', 'd_redirecting',
                 'd_social expressions', 'd_summation', 'e_humour', 'unsafe'}
        if len(set(strategies)) != len(strategies) or not set(strategies) <= known:
            raise ValueError('Unknown/duplicate strategy label')
        if 'is_unsafe' in value and (type(value['is_unsafe']) is not bool or value['is_unsafe'] != ('unsafe' in strategies)):
            raise ValueError('Inconsistent strategy unsafe marker')


def validate_results(document, trusted_index):
    """Validate against an operator-supplied index and reconstruct scoring rows.

    No uploaded aggregate is read. Result authenticity remains user-reported.
    """
    validate_index(trusted_index)
    _keys(document, ('schema_version', 'artifact_kind', 'run', 'protocol_sha256',
                     'input_index_sha256', 'publication', 'records', 'content_sha256'), 'Results')
    if document['schema_version'] != SCHEMA or document['artifact_kind'] != 'full_records':
        raise ValueError('Unsupported result format; summary-only cannot be rescored')
    _verify_seal(document)
    if document['input_index_sha256'] != trusted_index['content_sha256'] or document['protocol_sha256'] != canonical_hash(trusted_index['protocol']):
        raise ValueError('Result protocol/input index differs from trusted index')
    run = document['run']
    _validate_run(run)
    _keys(document['publication'], ('status', 'response_scope'), 'Publication')
    if document['publication'] != {'status': 'local', 'response_scope': 'included'}:
        raise ValueError('Uploaded results cannot assert public registration')
    model = run['model']['id']
    if not isinstance(model, str) or not model.strip() or len(model) > 1024:
        raise ValueError('Invalid target model identifier')
    if run['model']['verification'] != 'user_reported':
        raise ValueError('Uploaded model identity cannot assert verification')
    records = document['records']
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise ValueError('Invalid record count')
    restored, seen, responses = {t: [] for t in TASKS}, set(), {}
    for record in records:
        _keys(record, ('task', 'sample_id', 'source_id', 'variant', 'input_sha256', 'response', 'measurement'), 'Record')
        task, sid = record['task'], record['sample_id']
        if type(task) is not int or task not in TASKS or not isinstance(sid, str):
            raise ValueError('Invalid task/sample identity')
        key = (task, sid)
        if key in seen:
            raise ValueError('Duplicate task/sample record')
        seen.add(key)
        entry = trusted_index['inputs'][str(task)].get(sid)
        if entry is None:
            raise ValueError('Extra sample outside trusted index')
        original = entry['row']
        if (record['input_sha256'] != entry['input_sha256'] or record['source_id'] != source_id(original)
                or record['variant'] != variant(original, task)):
            raise ValueError('Record input identity mismatch')
        response, measurement = record['response'], record['measurement']
        _keys(response, ('text', 'sha256', 'status', 'finish_reason', 'usage', 'request_id'), 'Response',
              optional=('response_id','server_model','reasoning_content','refusal','execution'))
        for field in ('finish_reason','request_id','response_id','server_model'):
            if response.get(field) is not None and (not isinstance(response.get(field),str) or len(response[field]) > 4096):
                raise ValueError('Invalid optional response provenance')
        if response['usage'] is not None and not isinstance(response['usage'],dict):
            raise ValueError('Response usage must be an object or null')
        for field in ('reasoning_content','refusal'):
            value=response.get(field)
            if value is not None and (not isinstance(value,str) or len(value.encode('utf-8'))>MAX_TEXT_BYTES):
                raise ValueError('Invalid optional response content')
        if 'execution' in response:validate_execution(response['execution'],response['status'])
        text = response['text']
        if not isinstance(text, str) or len(text.encode('utf-8')) > MAX_TEXT_BYTES:
            raise ValueError('Invalid/oversized response text')
        if response['status'] not in ('ok', 'error') or response['sha256'] != canonical_hash(text):
            raise ValueError('Invalid response status/checksum')
        _keys(measurement, ('value', 'status', 'response_sha256', 'input_sha256'), 'Measurement')
        value = measurement['value']
        usable = response['status'] == 'ok' and bool(text.strip())
        if task not in (3, 4):
            if value is not None or measurement['response_sha256'] is not None or measurement['input_sha256'] is not None:
                raise ValueError('Unexpected classifier measurement')
        elif (measurement['response_sha256'] != response['sha256'] or measurement['input_sha256'] != record['input_sha256']):
            raise ValueError('Measurement bound to a different input/response')
        expected_status = ('reported' if value is not None else 'unmeasured') if usable else 'not_applicable'
        if measurement['status'] != expected_status or (not usable and value is not None):
            raise ValueError('Inconsistent measurement status')
        if task in (3, 4):
            _validate_measurement_value(value, task)
            if value is not None and run['measurements'][str(task)] is None:
                raise ValueError('Reported measurement requires classifier provenance')
        row = deepcopy(original)
        row.update(evaluated_model=model, prediction=text if usable else '',
                   api_status=response['status'], measurement=deepcopy(value))
        restored[task].append(row)
        if task in (3, 4):
            previous = responses.setdefault(sid, response)
            if previous != response:
                raise ValueError('Task 3/4 must reuse the identical generation')
    expected = {(task, sid) for task in TASKS for sid in trusted_index['inputs'][str(task)]}
    if seen != expected:
        raise ValueError('Missing expected records; retain failed/unmeasured rows')
    for task in (3, 4):
        evidence = run['measurements'][str(task)]
        if evidence is not None and 'conditions' in evidence:
            from .measurement_conditions import validate_conditions
            validate_conditions(evidence['conditions'], records=[r for r in records if r['task'] == task])
    return restored


def report_results(document, trusted_index, output_dir, min_sources=20, min_coverage=.9):
    rows = validate_results(document, trusted_index)
    with tempfile.TemporaryDirectory(prefix='koevd-validated-') as directory:
        inputs = {}
        for task, values in rows.items():
            path = Path(directory) / f'task{task}.jsonl'
            write_jsonl(path, values)
            inputs[task] = [path]
        return write_report(inputs, Path(output_dir), min_sources, min_coverage)


def main():
    from .common import configure_cli_stdio
    configure_cli_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    index_parser = commands.add_parser('index', help='Create a local input index, not an official registration')
    index_parser.add_argument('--run-dir', required=True)
    index_parser.add_argument('--output', required=True)
    index_parser.add_argument('--dataset-repo')
    index_parser.add_argument('--dataset-revision')
    index_parser.add_argument('--code-revision')
    export_parser = commands.add_parser('export')
    export_parser.add_argument('--run-dir', required=True)
    export_parser.add_argument('--trusted-index', required=True)
    export_parser.add_argument('--output', required=True)
    export_parser.add_argument('--code-revision')
    migrate_parser = commands.add_parser('migrate', help='Import original prepared-row JSONL')
    for task in TASKS:
        migrate_parser.add_argument('--task'+str(task), required=task != 4)
    migrate_parser.add_argument('--trusted-index', required=True)
    migrate_parser.add_argument('--output', required=True)
    migrate_parser.add_argument('--model')
    migrate_parser.add_argument('--code-revision')
    protocol_parser = commands.add_parser('protocol-index', help='Prepare independently from a registered pinned dataset')
    protocol_parser.add_argument('--registry', required=True)
    protocol_parser.add_argument('--protocol-id', required=True)
    protocol_parser.add_argument('--dataset-dir', required=True)
    protocol_parser.add_argument('--run-dir', required=True)
    protocol_parser.add_argument('--output', required=True)
    schema_parser = commands.add_parser('schema', help='Print a packaged JSON Schema')
    schema_parser.add_argument('--kind', choices=('results','index','protocol'), default='results')
    for command in ('validate', 'report'):
        sub = commands.add_parser(command)
        sub.add_argument('--input', required=True)
        sub.add_argument('--trusted-index', required=True)
        sub.add_argument('--registry')
        sub.add_argument('--protocol-id')
        if command == 'report':
            sub.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    if args.command == 'schema':
        from importlib.resources import files
        print(files('koevd_eval').joinpath('schemas', args.kind+'-v1.schema.json').read_text(encoding='utf-8'))
    elif args.command == 'protocol-index':
        from .protocols import ProtocolRegistry
        index = ProtocolRegistry(args.registry).prepare_index(args.protocol_id, args.dataset_dir, args.run_dir)
        save_json(Path(args.output), index)
    elif args.command == 'index':
        value = build_index(args.run_dir, dataset_repo=args.dataset_repo,
                            dataset_revision=args.dataset_revision, code_revision=args.code_revision)
        validate_index(value)
        save_json(Path(args.output), value)
    else:
        index = read_document(args.trusted_index)
        if args.command == 'migrate':
            paths = {t:Path(getattr(args, 'task'+str(t))) for t in TASKS if getattr(args, 'task'+str(t))}
            save_json(Path(args.output), migrate_jsonl(paths, index, model=args.model, code_revision=args.code_revision))
        elif args.command == 'export':
            save_json(Path(args.output), export_run(args.run_dir, index, code_revision=args.code_revision))
        else:
            result = read_document(args.input)
            if bool(args.registry) != bool(args.protocol_id):
                parser.error('--registry and --protocol-id must be supplied together')
            if args.registry:
                from .protocols import ProtocolRegistry
                ProtocolRegistry(args.registry).validate_index(args.protocol_id, index)
            if args.command == 'report':
                report_results(result, index, args.output_dir)
            else:
                rows = validate_results(result, index)
                print(json.dumps({'status': 'structurally_validated_against_supplied_index',
                                  'rows': {str(t): len(v) for t, v in rows.items()},
                                  'generation_authenticity': 'user_reported',
                                  'official_rank_eligible': False}))


if __name__ == '__main__':
    main()
