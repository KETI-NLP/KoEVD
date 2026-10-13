import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec=importlib.util.spec_from_file_location('gpu_source_bundle_test',
    Path(__file__).resolve().parents[1]/'scripts'/'gpu_source_bundle.py')
bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)


class GPUSourceBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.repo=self.root/'repo';self.repo.mkdir()
        (self.repo/'pyproject.toml').write_text('[project]\nname="synthetic"\n',encoding='utf-8')
        source=self.repo/'src'/'koevd_eval';source.mkdir(parents=True)
        (source/'classify_responses.py').write_text('# synthetic source fixture only\n',encoding='utf-8')
        self.zip=self.root/'source.zip'

    def build(self):return bundle.build_source_zip(self.repo,self.zip,head='a'*40)

    def test_explicit_ci_workflow_is_carried_without_other_hidden_files(self):
        workflow=self.repo/'.github/workflows/test.yml'
        workflow.parent.mkdir(parents=True)
        workflow.write_text('name: CPU checks\n',encoding='utf-8')
        (self.repo/'.github/private.txt').write_text('PRIVATE FIXTURE',encoding='utf-8')
        (self.repo/'.env').write_text('PRIVATE FIXTURE',encoding='utf-8')
        self.build()
        with zipfile.ZipFile(self.zip) as archive:
            self.assertEqual(archive.read('.github/workflows/test.yml'),workflow.read_bytes())
            self.assertNotIn('.github/private.txt',archive.namelist())
            self.assertNotIn('.env',archive.namelist())

    def test_roundtrip_excludes_generated_weights_environment_and_git(self):
        for name in ('generated','.git'):
            p=self.repo/name;p.mkdir();(p/'private.json').write_text('{}',encoding='utf-8')
        (self.repo/'.env').write_text('NO_REAL_SECRET=fixture',encoding='utf-8')
        (self.repo/'src'/'fake-weights.safetensors').write_bytes(b'FAKE')
        m=self.build();checksum=bundle.sha(self.zip.read_bytes())
        self.assertEqual(bundle.verify_source_zip(self.zip,checksum),m)
        self.assertEqual(set(m['files']),{'pyproject.toml','src/koevd_eval/classify_responses.py'})
        with self.assertRaises(FileExistsError):self.build()
        with self.assertRaisesRegex(ValueError,'independent expected'):bundle.verify_source_zip(self.zip,'0'*64)

    def test_required_deployment_recipes_survive_source_handoff_without_unlisted_recipes(self):
        root=self.repo/'apps/spaces';root.mkdir(parents=True)
        for name in ('Dockerfile','managed.Dockerfile','private.Dockerfile'):
            (root/name).write_text('# SYNTHETIC build recipe '+name+'\n',encoding='utf-8')
        manifest=self.build()
        with zipfile.ZipFile(self.zip) as archive:
            for name in ('Dockerfile','managed.Dockerfile'):
                relative='apps/spaces/'+name
                self.assertIn(relative,manifest['files'])
                self.assertEqual(archive.read(relative),(root/name).read_bytes())
            self.assertNotIn('apps/spaces/private.Dockerfile',manifest['files'])

    def test_changed_source_bytes_rejected_without_extraction(self):
        self.build()
        with zipfile.ZipFile(self.zip) as archive:contents={n:archive.read(n) for n in archive.namelist()}
        contents['src/koevd_eval/classify_responses.py']=b'# changed fixture'
        changed=self.root/'changed.zip'
        with zipfile.ZipFile(changed,'x') as archive:
            for n,v in contents.items():archive.writestr(n,v)
        with self.assertRaisesRegex(ValueError,'checksum/size'):bundle.verify_source_zip(changed)
        self.assertFalse((self.root/'src').exists())

    def test_build_metadata_changes_do_not_change_source_inventory_or_remove_real_source(self):
        real=self.repo/'src/koevd_eval/build_metadata_notes.py'
        real.write_text('# actual source fixture\n',encoding='utf-8')
        expected=bundle.collect_sources(self.repo)
        metadata=[]
        for name in ('src/koevd_eval.egg-info/SOURCES.txt',
                     'src/koevd_eval-0.2.0.dist-info/entry_points.txt',
                     'src/koevd_eval/cache/generated.EGG-INFO/build.json',
                     'tests/generated.DIST-INFO/manifest.json'):
            p=self.repo/name;p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text('SYNTHETIC build metadata v1\n',encoding='utf-8');metadata.append(p)
        self.assertEqual(bundle.collect_sources(self.repo),expected)
        for p in metadata:p.write_text('SYNTHETIC build metadata v2 changed\n',encoding='utf-8')
        manifest=self.build()
        self.assertEqual(set(manifest['files']),set(expected))
        self.assertIn('src/koevd_eval/build_metadata_notes.py',manifest['files'])
        self.assertTrue(all(p.is_file() for p in metadata))
        with zipfile.ZipFile(self.zip) as archive:
            for name,raw in expected.items():self.assertEqual(archive.read(name),raw)

    def test_unsafe_and_case_duplicate_entries_rejected(self):
        for name in ('../outside','/absolute','C:/absolute','src\\path','src//path'):
            with self.assertRaises(ValueError):bundle.safe_name(name)
        self.build()
        with zipfile.ZipFile(self.zip,'a') as archive:archive.writestr('PYPROJECT.TOML',b'collision')
        with self.assertRaisesRegex(ValueError,'case-colliding'):bundle.verify_source_zip(self.zip)

    def test_bounded_expansion_and_nonobject_manifest_rejected(self):
        self.build()
        with patch.object(bundle,'MAX_TOTAL',16):
            with self.assertRaisesRegex(ValueError,'size limit'):bundle.verify_source_zip(self.zip)
        invalid=self.root/'invalid.zip'
        with zipfile.ZipFile(invalid,'x') as archive:archive.writestr('bundle-manifest.json','[]')
        with self.assertRaisesRegex(ValueError,'Unsupported'):bundle.verify_source_zip(invalid)

    def test_credential_like_source_literal_rejected_without_value_in_error(self):
        token='hf_'+'A'*32
        (self.repo/'src'/'token.json').write_text('{"fixture":"'+token+'"}',encoding='utf-8')
        with self.assertRaises(ValueError) as ctx:bundle.collect_sources(self.repo)
        self.assertNotIn(token,str(ctx.exception))
        self.assertIn('src/token.json',str(ctx.exception))


if __name__=='__main__':unittest.main()
