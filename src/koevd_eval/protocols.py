"""Operator-controlled pinned protocols. Registry entries are never upload data."""
from __future__ import annotations

from copy import deepcopy
import inspect
from pathlib import Path, PurePosixPath

from . import prepare_tasks
from .pipeline import prepare_run, file_sha
from .results import build_index, canonical_hash, read_document, validate_index, _seal, _keys
from .run_openai_compatible import input_digest

PROTOCOL_SCHEMA = 'koevd-protocol-v1'


def preparation_identity():
    # Hash only preparation code: unrelated runner/UI improvements need not change inputs.
    values = {'prepare_run': inspect.getsource(prepare_run),
              'input_digest': inspect.getsource(input_digest),
              'prepare_tasks': inspect.getsource(prepare_tasks)}
    return canonical_hash({k:v.replace('\r\n','\n') for k,v in values.items()})


def _relative_file(root, name):
    if not isinstance(name, str) or '\\' in name:
        raise ValueError('Protocol file must use a relative POSIX path')
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or ':' in name or not relative.parts:
        raise ValueError('Protocol path traversal rejected')
    root = Path(root).resolve()
    path = root.joinpath(*relative.parts).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Protocol dataset path escapes directory')
    return path


def validate_definition(definition):
    _keys(definition, ('schema_version','id','status','dataset','selection','preparation_sha256',
                       'expected_inputs','decoding_policy','measurement_policy','scoring',
                       'metadata_view','denominators','content_sha256'), 'Protocol')
    if definition['schema_version'] != PROTOCOL_SCHEMA or definition['status'] != 'release_candidate':
        raise ValueError('Unsupported protocol definition/status')
    from .results import _verify_seal
    _verify_seal(definition)
    if not isinstance(definition['id'], str) or not definition['id'] or len(definition['id']) > 128:
        raise ValueError('Invalid protocol ID')
    dataset = definition['dataset']
    _keys(dataset, ('repo','revision','files'), 'Protocol dataset')
    revision = dataset['revision']
    if not isinstance(revision, str) or len(revision) != 40 or any(c not in '0123456789abcdef' for c in revision):
        raise ValueError('Protocol requires an immutable dataset commit')
    if not isinstance(dataset['repo'], str) or not dataset['repo'] or not isinstance(dataset['files'], dict):
        raise ValueError('Invalid protocol dataset')
    for name, checksum in dataset['files'].items():
        _relative_file(Path.cwd(), name)
        if not isinstance(checksum, str) or len(checksum) != 64 or any(c not in '0123456789abcdef' for c in checksum):
            raise ValueError('Invalid pinned dataset checksum')
    _keys(definition['selection'], ('split','limit_sources'), 'Protocol selection')
    selection = definition['selection']
    if selection['split'] != 'core' or selection['limit_sources'] is not None:
        raise ValueError('This protocol version requires complete core selection')
    for checksum in [definition['preparation_sha256'], *[v['sha256'] for v in definition['expected_inputs'].values() if isinstance(v,dict) and 'sha256' in v]]:
        if not isinstance(checksum,str) or len(checksum)!=64 or any(c not in '0123456789abcdef' for c in checksum):
            raise ValueError('Invalid expected input/preparation checksum')
    _keys(definition['denominators'], ('task1','task2','task3','task4','task5'), 'Protocol denominators')
    if any(not isinstance(value,str) or not value for value in definition['denominators'].values()):
        raise ValueError('Protocol denominators must be explained')
    _keys(definition['expected_inputs'], ('1','2','3','4','5'), 'Protocol expected tasks')
    for value in definition['expected_inputs'].values():
        _keys(value, ('rows','sha256'), 'Expected inputs')
        if type(value['rows']) is not int or value['rows'] < 1:
            raise ValueError('Invalid expected row count')
    if definition['expected_inputs']['3'] != definition['expected_inputs']['4']:
        raise ValueError('Task 4 must reuse Task 3 expected inputs')
    if definition['metadata_view'] != 'canonical-prepared':
        raise ValueError('Unsupported metadata view')
    if definition['scoring'] != {'historical':'koevd-0.2.0', 'diagnostic':'strict-profile-v1'}:
        raise ValueError('Unsupported protocol scoring version')
    if definition['decoding_policy'] != {'temperature':0.0, 'max_tokens':1024, 'seed':None}:
        raise ValueError('Unsupported protocol decoding policy')
    _keys(definition['measurement_policy'], ('3','4'), 'Protocol measurements')
    for task, value in definition['measurement_policy'].items():
        _keys(value, ('adapter','base','accuracy_status','official_ranking'), 'Measurement policy')
        if value['accuracy_status'] != 'measurement_limited' or value['official_ranking'] is not False:
            raise ValueError('Unresolved measurement metrics cannot assert official rank eligibility')
        for field in ('adapter','base'):
            _keys(value[field], ('repo','revision'), 'Measurement revision')
            rev=value[field]['revision']
            if not isinstance(rev,str) or len(rev)!=40 or any(c not in '0123456789abcdef' for c in rev):
                raise ValueError('Measurement revisions must be immutable')


def input_set_identity(index):
    return {task:{'rows':len(entries), 'sha256':canonical_hash(entries)}
            for task, entries in index['inputs'].items()}


def build_protocol_index(dataset_dir, definition, output_dir):
    """Independently prepare expected inputs from pinned local data; never uploaded gold."""
    validate_definition(definition)
    if preparation_identity() != definition['preparation_sha256']:
        raise ValueError('Preparation code differs from pinned protocol')
    root = Path(dataset_dir)
    for name, expected in definition['dataset']['files'].items():
        if file_sha(_relative_file(root, name)) != expected:
            raise ValueError(f'Dataset checksum differs from pinned protocol: {name}')
    manifest = prepare_run(root, Path(output_dir), split=definition['selection']['split'])
    if manifest['preparation']['dataset_files'] != definition['dataset']['files']:
        raise ValueError('Prepared dataset file set differs from pinned protocol')
    index = build_index(output_dir, dataset_repo=definition['dataset']['repo'],
                        dataset_revision=definition['dataset']['revision'])
    if input_set_identity(index) != definition['expected_inputs']:
        raise ValueError('Prepared inputs differ from pinned expected set')
    protocol = {k:deepcopy(v) for k,v in definition.items() if k not in ('expected_inputs','content_sha256','schema_version','status')}
    protocol.update(kind='standard', definition_sha256=definition['content_sha256'],
                    selection=deepcopy(definition['selection']))
    index['protocol'] = protocol
    index = _seal({k:v for k,v in index.items() if k != 'content_sha256'})
    validate_index(index)
    return index


class ProtocolRegistry:
    """An operator-selected directory of immutable definitions (no path from upload)."""
    def __init__(self, directory):
        self.definitions = {}
        for path in sorted(Path(directory).glob('*.json')):
            definition = read_document(path)
            validate_definition(definition)
            key = definition['id']
            if key in self.definitions:
                raise ValueError('Duplicate protocol ID in registry')
            self.definitions[key] = definition
        if not self.definitions:
            raise ValueError('Protocol registry is empty')

    def get(self, protocol_id):
        if protocol_id not in self.definitions:
            raise ValueError('Unknown registered protocol ID')
        return deepcopy(self.definitions[protocol_id])

    def prepare_index(self, protocol_id, dataset_dir, output_dir):
        return build_protocol_index(dataset_dir, self.get(protocol_id), output_dir)

    def validate_index(self, protocol_id, index):
        validate_index(index)
        definition = self.get(protocol_id)
        expected_protocol = {k:deepcopy(v) for k,v in definition.items()
                             if k not in ('expected_inputs','content_sha256','schema_version','status')}
        expected_protocol.update(kind='standard', definition_sha256=definition['content_sha256'],
                                 selection=deepcopy(definition['selection']))
        if index['protocol'] != expected_protocol or input_set_identity(index) != definition['expected_inputs']:
            raise ValueError('Index is not the registered pinned input/protocol set')
        return definition
