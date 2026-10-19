"""Hosted introduction must not point users to a stale first-user guide."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class RegisteredGuideLinkTests(unittest.TestCase):
    def test_generated_introduction_tracks_runtime_release(self):
        scripts = ROOT / 'scripts'
        sys.path.insert(0, str(scripts))
        try:
            spec = importlib.util.spec_from_file_location('registered_guide_link', scripts / 'materialize_registered_space.py')
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        finally:
            sys.path.pop(0)

        def prepare_stub(repo, base, references, output):
            (output / 'apps/spaces').mkdir(parents=True)
            (output / 'operator-data').mkdir()

        for version, tag in [('0.3.0rc8', 'v0.3.0-rc.8'), ('0.4.0rc12', 'v0.4.0-rc.12')]:
            with self.subTest(version=version), tempfile.TemporaryDirectory() as temp:
                output = Path(temp) / 'out'
                with patch.object(module, 'public_context', prepare_stub), patch.object(module, '__version__', version):
                    manifest = module.build(ROOT, Path(temp), Path(temp) / 'unused.json', output, profile='hosted_service')
                readme = (output / 'README.md').read_text(encoding='utf-8')
                self.assertIn('beta ' + version, readme)
                self.assertIn('compare (' + tag + ')', readme)
                self.assertIn('/blob/' + tag + '/docs/GETTING_STARTED.md', readme)
                self.assertEqual(manifest['version'], version)
