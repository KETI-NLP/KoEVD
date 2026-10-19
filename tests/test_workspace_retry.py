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

    def test_partial_upload_retry_retains_successes(self):
        self.run_journey('partial_upload_journey.cjs')

    def test_private_and_public_revision_scope(self):
        self.run_journey('revision_scope_journey.cjs')

    def run_journey(self, name):
        node=os.environ.get('KOEVD_TEST_NODE') or shutil.which('node')
        if not node:self.skipTest('Node.js unavailable')
        root=Path(__file__).resolve().parents[1]
        subprocess.run([node,'tests/'+name],cwd=root,check=True,timeout=20)
