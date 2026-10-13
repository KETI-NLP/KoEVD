"""Provider doubles only; pinning and private reference transport boundaries."""
from pathlib import Path
import hashlib
import importlib.util
import json
from types import SimpleNamespace
import tempfile
import unittest

script=Path(__file__).resolve().parents[1]/'apps/spaces/public_launch.py'
spec=importlib.util.spec_from_file_location('public_launch',script)
public_launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(public_launch)


class PublicReferenceAssetTests(unittest.TestCase):
    def fixture(self, root, *, private=True):
        raw=[b'{"example":1}',b'{"example":2}'];entries=[]
        for number,value in enumerate(raw):
            digest=hashlib.sha256(value).hexdigest()
            entries.append({'id':'ref-'+str(number),'label':'fixture','path':'references/'+digest+'.json',
                            'sha256':digest,'bytes':len(value)})
        config=root/'config.json';config.write_text(json.dumps({'format':'koevd-reference-assets-v1',
               'bucket_id':'KETI-NLP/KoEVD-Platform-Backups','references':entries}))
        class API:
            downloads=0
            def bucket_info(self,bucket):return SimpleNamespace(id=bucket,private=private)
            def list_bucket_tree(self,bucket,prefix,recursive):
                return [SimpleNamespace(path=e['path'],size=e['bytes']) for e in entries if e['path']==prefix]
            def download_bucket_files(self,bucket,files,raise_on_missing_files):
                self.downloads+=1
                for item,dest in files:
                    dest.write_bytes(raw[next(i for i,e in enumerate(entries) if e['path']==item.path)])
        return config,API(),entries

    def test_private_exact_bytes_and_cached_hash_recheck(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);config,api,entries=self.fixture(root)
            result=public_launch.pinned_reference_assets(config,root/'local',api=api)
            self.assertEqual(api.downloads,2)
            self.assertEqual([e['sha256'] for e in result],[e['sha256'] for e in entries])
            public_launch.pinned_reference_assets(config,root/'local',api=api)
            self.assertEqual(api.downloads,2)
            Path(result[0]['local_path']).write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError,'Local reference bytes differ'):
                public_launch.pinned_reference_assets(config,root/'local',api=api)
            self.assertEqual(api.downloads,2)

    def test_public_bucket_refused_before_object_download(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);config,api,_=self.fixture(root,private=False)
            with self.assertRaisesRegex(ValueError,'remain private'):
                public_launch.pinned_reference_assets(config,root/'local',api=api)
            self.assertEqual(api.downloads,0)

    def test_object_key_override_and_changed_remote_bytes_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);config,api,entries=self.fixture(root)
            doc=json.loads(config.read_text());doc['references'][0]['path']='outside.json'
            config.write_text(json.dumps(doc))
            with self.assertRaisesRegex(ValueError,'Unexpected object key'):
                public_launch.pinned_reference_assets(config,root/'local',api=api)
            self.assertEqual(api.downloads,0)

    def test_missing_read_token_has_no_cli_admin_fallback(self):
        from unittest.mock import patch
        with patch.dict('os.environ',{'SPACE_HOST':'keti-nlp-koevd-platform.hf.space'},clear=True):
            with self.assertRaisesRegex(ValueError,'read-only Bucket-scoped'):
                public_launch.main()

    def test_startup_error_logs_only_class_and_integer_status(self):
        from unittest.mock import Mock, patch
        api=Mock()
        class TransportError(Exception):
            response=SimpleNamespace(status_code=404)
        error=TransportError('secret-value https://private.example/?token=secret-value')
        with patch.dict('os.environ',{'SPACE_HOST':'keti-nlp-koevd-platform.hf.space',
                                    'KOEVD_REFERENCE_TOKEN':'secret-value'},clear=True), \
             patch.dict('sys.modules',{'huggingface_hub':SimpleNamespace(HfApi=api)}), \
             patch.object(public_launch,'pinned_reference_assets',side_effect=error):
            with self.assertRaises(ValueError) as caught:
                public_launch.main()
            self.assertEqual(str(caught.exception),
                'Pinned private reference initialization failed (TransportError; HTTP 404)')
            self.assertNotIn('secret-value',str(caught.exception))
            self.assertIsNone(caught.exception.__cause__)
            api.assert_called_once_with(token='secret-value')
            import os
            self.assertNotIn('KOEVD_REFERENCE_TOKEN',os.environ)
