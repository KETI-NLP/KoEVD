from pathlib import Path
import os
import shutil
import subprocess
import unittest


class WorkspaceRetryTests(unittest.TestCase):
    def test_shipped_javascript_recovery_and_discovery(self):
        node=os.environ.get('KOEVD_TEST_NODE') or shutil.which('node')
        if not node:self.skipTest('Node.js unavailable; browser CPU acceptance is separate')
        root=Path(__file__).resolve().parents[1]
        subprocess.run([node,'tests/workspace_retry.cjs'],cwd=root,check=True,timeout=20)
