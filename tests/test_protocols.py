"""Pinned registry CPU checks. The tiny definition is synthetic, not official data."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from koevd_eval.common import read_jsonl, write_jsonl
from koevd_eval.pipeline import prepare_run, save_json
from koevd_eval.protocols import (ProtocolRegistry, preparation_identity,
                                  input_set_identity, validate_definition)
from koevd_eval.results import build_index, _seal, read_document
from test_own_model_pipeline import dataset_fixture


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name); self.data=self.root/'data'
        dataset_fixture(self.data)
        prepared=self.root/'reference'
        manifest=prepare_run(self.data,prepared)
        index=build_index(prepared)
        self.definition=read_document('configs/protocols/koevd-core-canonical-v1.json')
        self.definition.update(id='SYNTHETIC-REGISTRY-FIXTURE',
                               dataset={'repo':'SYNTHETIC/fixture','revision':'a'*40,
                                        'files':manifest['preparation']['dataset_files']},
                               expected_inputs=input_set_identity(index),
                               preparation_sha256=preparation_identity())
        self.definition=_seal({k:v for k,v in self.definition.items() if k!='content_sha256'})
        self.registry_dir=self.root/'registry';self.registry_dir.mkdir()
        save_json(self.registry_dir/'fixture.json',self.definition)
        self.registry=ProtocolRegistry(self.registry_dir)

    def test_pinned_registry_prepares_and_checks_expected_set(self):
        index=self.registry.prepare_index(self.definition['id'],self.data,self.root/'run')
        self.registry.validate_index(self.definition['id'],index)
        self.assertEqual(index['protocol']['kind'],'standard')
        self.assertFalse(index['protocol']['measurement_policy']['3']['official_ranking'])
        self.assertFalse(index['protocol']['measurement_policy']['4']['official_ranking'])
        self.assertEqual([len(index['inputs'][str(t)]) for t in range(1,6)],[1,4,2,2,3])
        entry=next(iter(index['inputs']['1'].values()))
        entry['row']['gold']['label']='unsafe'
        from koevd_eval.run_openai_compatible import input_digest
        entry['input_sha256']=input_digest(entry['row'])
        altered=_seal({k:v for k,v in index.items() if k!='content_sha256'})
        with self.assertRaisesRegex(ValueError,'registered pinned'):
            self.registry.validate_index(self.definition['id'],altered)

    def test_dataset_tampering_rejected_before_prepare(self):
        path=self.data/'benchmark_splits/core.jsonl'
        with path.open('a',encoding='utf-8') as handle:handle.write('\n')
        with self.assertRaisesRegex(ValueError,'Dataset checksum'):
            self.registry.prepare_index(self.definition['id'],self.data,self.root/'run')
        self.assertFalse((self.root/'run').exists())

    def test_code_expected_counts_and_path_changes_rejected(self):
        with patch('koevd_eval.protocols.preparation_identity',return_value='0'*64):
            with self.assertRaisesRegex(ValueError,'Preparation code'):
                self.registry.prepare_index(self.definition['id'],self.data,self.root/'code-run')
        altered=deepcopy(self.definition);altered['expected_inputs']['1']['rows']+=1
        save_json(self.registry_dir/'fixture.json',_seal({k:v for k,v in altered.items() if k!='content_sha256'}))
        with self.assertRaisesRegex(ValueError,'expected set'):
            ProtocolRegistry(self.registry_dir).prepare_index(altered['id'],self.data,self.root/'count-run')
        altered=deepcopy(self.definition)
        altered['dataset']['files']['../private.jsonl']='a'*64
        with self.assertRaisesRegex(ValueError,'traversal'):
            validate_definition(_seal({k:v for k,v in altered.items() if k!='content_sha256'}))

    def test_unknown_duplicate_and_mutable_revisions_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unknown'):
            self.registry.get('../another-protocol')
        save_json(self.registry_dir/'duplicate.json',self.definition)
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            ProtocolRegistry(self.registry_dir)
        for field in ('dataset','measurement'):
            altered=deepcopy(self.definition)
            if field=='dataset':altered['dataset']['revision']='main'
            else:altered['measurement_policy']['3']['adapter']['revision']='main'
            with self.assertRaises(ValueError):
                validate_definition(_seal({k:v for k,v in altered.items() if k!='content_sha256'}))


if __name__=='__main__':unittest.main()
