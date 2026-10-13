"""Lock contract tests; no downloads, model inference or GPU evidence."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


class ArtifactLockTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location('prepare_gpu_artifacts', root / 'scripts/prepare_gpu_artifacts.py')
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.lock = json.loads((root / 'configs/validation/platform-gpu-candidate-v1.json').read_text(encoding='utf-8'))

    def test_actual_release_and_target_lock_resolves_without_changing_revisions(self):
        original = deepcopy(self.lock)
        resources = self.module.pinned_resources(self.lock)
        self.assertEqual(self.lock, original)
        self.assertEqual(len(resources), 7)
        for target in self.lock['target_models']:
            resource = resources['target-' + target['id'].split('/')[-1]]
            self.assertEqual(resource['repo_id'], target['id'])
            self.assertEqual(resource['revision'], target['revision'])
        self.assertEqual(resources['strategy_base']['revision'], resources['target-Qwen3-8B']['revision'])

    def test_conflicting_ids_and_mutable_revision_rejected_before_download(self):
        conflict = deepcopy(self.lock)
        conflict['target_models'][0]['repo_id'] = 'other/model'
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            self.module.pinned_resources(conflict)
        mutable = deepcopy(self.lock)
        mutable['target_models'][1]['revision'] = 'main'
        with self.assertRaisesRegex(ValueError, 'Immutable'):
            self.module.pinned_resources(mutable)


if __name__ == '__main__':
    unittest.main()
