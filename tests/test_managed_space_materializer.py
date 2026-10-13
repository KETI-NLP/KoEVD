"""Reject stale/mixed runtime contexts and accidentally inherited approvals."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

scripts = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(scripts))
try:
    spec = importlib.util.spec_from_file_location('managed_materializer', scripts / 'materialize_managed_space.py')
    materializer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(materializer)
finally:
    sys.path.pop(0)


class ManagedMaterializerTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.repo = self.root / 'repo'
        self.base = self.root / 'base'
        for name, raw in {'src/koevd_eval/__init__.py': b'# current analysis',
                          'src/koevd_classifiers/__init__.py': b'# current classifier',
                          'configs/protocols/core.json': b'{}', 'pyproject.toml': b'# current build'}.items():
            for root in (self.repo, self.base):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
        (self.base / 'operator-data').mkdir()
        self.roles = self.base / 'operator-data/roles.json'
        self.catalog = self.base / 'operator-data/catalog.json'
        self.roles.write_text('{"reviewers":[],"admins":[]}', encoding='utf-8')
        self.catalog.write_text('{"baselines":[]}', encoding='utf-8')
        self.save()

    def save(self):
        files = {p.relative_to(self.base).as_posix(): {'bytes': p.stat().st_size,
                 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                 for p in self.base.rglob('*') if p.is_file() and p.name != 'deployment-manifest.json'}
        manifest = {'format': 'koevd-private-development-space-v1', 'files': files,
                    'storage': 'ephemeral_development', 'credentials_included': False,
                    'actual_target_outputs_included': False, 'official_rank_eligible': False}
        (self.base / 'deployment-manifest.json').write_text(json.dumps(manifest), encoding='utf-8')

    def test_exact_unactivated_current_source_accepted(self):
        self.assertEqual(materializer.checked_base(self.repo, self.base)['storage'], 'ephemeral_development')

    def test_internally_valid_stale_runtime_is_rejected(self):
        for name in ('src/koevd_eval/__init__.py', 'src/koevd_classifiers/__init__.py',
                     'configs/protocols/core.json', 'pyproject.toml'):
            with self.subTest(name=name):
                path = self.base / name
                original = path.read_bytes()
                path.write_bytes(b'# stale but independently hashed')
                self.save()
                with self.assertRaisesRegex(ValueError, 'source bytes'):
                    materializer.checked_base(self.repo, self.base)
                path.write_bytes(original)
                self.save()

    def test_missing_current_module_rejected(self):
        (self.repo / 'src/koevd_eval/new_module.py').write_bytes(b'# newly required')
        with self.assertRaisesRegex(ValueError, 'inventory'):
            materializer.checked_base(self.repo, self.base)

    def test_actual_roles_or_references_cannot_be_inherited_as_unapproved(self):
        self.roles.write_text('{"reviewers":["actual-reviewer"],"admins":[]}', encoding='utf-8')
        self.save()
        with self.assertRaisesRegex(ValueError, 'web roles'):
            materializer.checked_base(self.repo, self.base)
        self.roles.write_text('{"reviewers":[],"admins":[]}', encoding='utf-8')
        self.catalog.write_text('{"baselines":[{"path":"private-result.json"}]}', encoding='utf-8')
        self.save()
        with self.assertRaisesRegex(ValueError, 'reference outputs'):
            materializer.checked_base(self.repo, self.base)

    def test_actual_managed_config_rejected_even_with_consistent_manifest(self):
        (self.base / 'operator-data/managed.json').write_text('{}', encoding='utf-8')
        self.save()
        with self.assertRaisesRegex(ValueError, 'managed configuration'):
            materializer.checked_base(self.repo, self.base)


if __name__ == '__main__':
    unittest.main()
