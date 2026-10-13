"""Deployment-context guards; these CPU checks do not prove container/HF operation."""
import hashlib
import importlib.util
from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('space_native_runtime',
    Path(__file__).resolve().parents[1] / 'scripts/validate_space_native_runtime.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class NativeRuntimeContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        data = b'public candidate source'
        (self.root / 'source.txt').write_bytes(data)
        self.manifest = {'format': 'koevd-private-development-space-v1',
            'files': {'source.txt': {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}},
            'credentials_included': False, 'actual_target_outputs_included': False, 'official_rank_eligible': False}
        self.save()

    def save(self):
        (self.root / 'deployment-manifest.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def test_exact_context_accepted(self):
        self.assertEqual(runtime.checked_context(self.root), self.manifest)

    def test_build_artifacts_or_private_result_extras_rejected(self):
        (self.root / 'build').mkdir()
        (self.root / 'build/unlisted.txt').write_bytes(b'extra')
        with self.assertRaisesRegex(ValueError, 'file set'):
            runtime.checked_context(self.root)

    def test_same_size_changed_source_rejected(self):
        path = self.root / 'source.txt'
        path.write_bytes(b'X' * path.stat().st_size)
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            runtime.checked_context(self.root)

    def test_unsafe_manifest_path_rejected(self):
        item = self.manifest['files'].pop('source.txt')
        self.manifest['files']['../source.txt'] = item
        self.save()
        with self.assertRaises(ValueError):
            runtime.checked_context(self.root)

    def test_credential_output_or_rank_claim_rejected(self):
        for field in ('credentials_included', 'actual_target_outputs_included', 'official_rank_eligible'):
            with self.subTest(field=field):
                self.manifest[field] = True
                self.save()
                with self.assertRaisesRegex(ValueError, 'unpublished'):
                    runtime.checked_context(self.root)
                self.manifest[field] = False

    def test_single_result_cannot_claim_a_comparison_only_check(self):
        output = self.root / 'must-not-be-created'
        argv = ['runtime-check', '--candidate', str(self.root), '--python', 'not-needed',
                '--result', 'not-needed', '--result-sha256', 'a' * 64,
                '--comparison-only', '--output', str(output)]
        with patch('sys.argv', argv), redirect_stderr(io.StringIO()) as stderr:
            with self.assertRaises(SystemExit) as failure:
                runtime.main()
        self.assertEqual(failure.exception.code, 2)
        self.assertIn('two or more results', stderr.getvalue())
        self.assertFalse(output.exists())

    def test_invalid_existing_port_rejected_before_output_creation(self):
        output = self.root / 'must-not-be-created'
        argv = ['runtime-check', '--candidate', str(self.root), '--python', 'not-needed',
                '--result', 'not-needed', '--result-sha256', 'a' * 64,
                '--existing-loopback-port', '65536', '--output', str(output)]
        with patch('sys.argv', argv), redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as failure:
                runtime.main()
        self.assertEqual(failure.exception.code, 2)
        self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
