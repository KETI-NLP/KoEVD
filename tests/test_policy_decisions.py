"""CPU/SYNTHETIC approvals only: no actual operator ratification or HF login."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from koevd_eval.eligibility import RankPolicy, VERSION
from koevd_eval.policy_decisions import (FORMAT, PolicyArchive, configured_policy,
                                         validate_decision)
from koevd_eval.results import canonical_hash
from koevd_eval.storage import StorageError
import koevd_eval.spaces as spaces
import test_public_leaderboard as board_fixture
import test_spaces as space_fixture


class PolicyDecisionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.archive = PolicyArchive(self.root / 'policy', create=True)
        self.decision = {'format': FORMAT, 'admission_version': VERSION, 'action': 'ratify',
            'actor': 'admin', 'decided_at': '2026-10-08T09:00:00Z',
            'reason': 'SYNTHETIC approval for CPU test only', 'previous_sha256': None}
        self.roles = self.root / 'roles.json'
        self.roles.write_text(json.dumps({'reviewers': ['reviewer'], 'admins': ['admin']}), encoding='utf-8')

    def cli(self, *args, actor='admin'):
        return subprocess.run([sys.executable, '-m', 'koevd_eval.policy_decisions',
            '--policy-root', str(self.archive.root), '--roles-file', str(self.roles),
            '--actor', actor, *map(str, args)], capture_output=True, text=True, encoding='utf-8')

    def test_candidate_default_and_explicit_pair_no_silent_fallback(self):
        self.assertEqual(configured_policy(), RankPolicy())
        for pair in ((self.archive.root, None), (None, 'a'*64), ('', ''), (self.archive.root, 'latest')):
            with self.subTest(pair=pair), self.assertRaises(ValueError): configured_policy(*pair)
        with self.assertRaises((ValueError, OSError)): configured_policy(self.archive.root, 'a'*64)

    def test_selected_chain_revoke_reapprove_idempotency_preserves_original_bytes(self):
        first = self.archive.record(self.decision)
        original = (self.archive.root / (first+'.json')).read_bytes()
        self.assertEqual(self.archive.record(deepcopy(self.decision)), first)
        revoked = {**self.decision, 'action': 'revoke', 'previous_sha256': first,
                   'decided_at': '2026-10-08T09:01:00Z', 'reason': 'SYNTHETIC revocation'}
        second = self.archive.record(revoked)
        self.assertEqual(configured_policy(self.archive.root, second), RankPolicy())
        self.assertEqual(configured_policy(self.archive.root, first).ratification_sha256, first)
        third = self.archive.record({**self.decision, 'previous_sha256': second,
                                    'decided_at': '2026-10-08T09:02:00Z'})
        self.assertEqual(configured_policy(self.archive.root, third).ratification_sha256, third)
        self.assertEqual(len(self.archive.history(third)), 3)
        self.assertEqual((self.archive.root / (first+'.json')).read_bytes(), original)

    def test_modified_head_or_parent_fails_closed_never_overwrites(self):
        first = self.archive.record(self.decision)
        second = self.archive.record({**self.decision, 'action': 'revoke', 'previous_sha256': first})
        p = self.archive.root / (first+'.json')
        p.write_text(json.dumps({**self.decision, 'reason': 'tampered'}), encoding='utf-8')
        for digest in (first, second):
            with self.assertRaisesRegex(ValueError, 'differs'): configured_policy(self.archive.root, digest)
        with self.assertRaisesRegex(ValueError, 'differs'): self.archive.record(self.decision)
        self.assertIn('tampered', p.read_text(encoding='utf-8'))

    def test_unsupported_fields_versions_and_history_dates_rejected_before_publish(self):
        for changes in ({'policy': {'allow_task4': True}}, {'admission_version': 'other'},
                        {'action': 'approve_upload'}, {'reason': ''}, {'reason': 'x'*4097},
                        {'decided_at': '2026-02-30T00:00:00Z'}, {'decided_at': '2026-10-08T09:00:00+00:00'},
                        {'previous_sha256': '../escape'}):
            with self.subTest(changes=list(changes)), self.assertRaises((ValueError, StorageError)):
                validate_decision({**self.decision, **changes})
        first = self.archive.record(self.decision)
        for changes in ({'previous_sha256': 'a'*64}, {'previous_sha256': first, 'decided_at': '2026-10-08T08:00:00Z'}):
            with self.assertRaises((ValueError, OSError)): self.archive.record({**self.decision, **changes})
        self.assertEqual(len(list(self.archive.root.glob('*.json'))), 1)

    def test_concurrent_same_record_atomic_and_failed_link_leaves_no_partial_decision(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            values = list(pool.map(self.archive.record, [deepcopy(self.decision), deepcopy(self.decision)]))
        self.assertEqual(values[0], values[1]); self.assertEqual(len(list(self.archive.root.iterdir())), 1)
        other = {**self.decision, 'reason': 'SYNTHETIC changed reason'}
        with patch('koevd_eval.policy_decisions.os.link', side_effect=OSError('SYNTHETIC link failure')):
            with self.assertRaises(OSError): self.archive.record(other)
        self.assertEqual(len(list(self.archive.root.iterdir())), 1)
        self.assertFalse((self.archive.root / (canonical_hash(other)+'.json')).exists())

    def test_bounded_snapshot_duplicate_json_symlink_and_history_limit(self):
        digest = self.archive.record(self.decision); path = self.archive.root / (digest+'.json')
        path.write_text('{"format":"one","format":"two"}', encoding='utf-8')
        with self.assertRaises(ValueError): self.archive.read(digest)
        path.write_bytes(b'x'*16385)
        with self.assertRaises(ValueError): self.archive.read(digest)
        with patch.object(Path, 'is_symlink', return_value=True):
            with self.assertRaises(ValueError): PolicyArchive(self.archive.root)
        path.unlink(); digest = self.archive.record(self.decision)
        with patch('koevd_eval.policy_decisions.MAX_HISTORY', 1):
            with self.assertRaisesRegex(ValueError, 'limit'):
                self.archive.record({**self.decision, 'previous_sha256': digest})

    def test_real_module_cli_checks_independent_admin_actor_and_keeps_private_history(self):
        source = self.root / 'decision.json'; source.write_text(json.dumps(self.decision), encoding='utf-8')
        denied = self.cli('archive', '--decision-file', source, actor='reviewer')
        self.assertEqual(denied.returncode, 2); self.assertIn('administrator', denied.stderr)
        forged = {**self.decision, 'actor': 'other'}; source.write_text(json.dumps(forged), encoding='utf-8')
        self.assertEqual(self.cli('archive', '--decision-file', source).returncode, 2)
        source.write_text(json.dumps(self.decision), encoding='utf-8')
        passed = self.cli('archive', '--decision-file', source)
        self.assertEqual(passed.returncode, 0, passed.stderr); value = json.loads(passed.stdout)
        self.assertFalse(value['human_approval_authenticated']); self.assertFalse(value['server_configuration_changed'])
        self.assertNotIn('reason', passed.stdout)
        history = self.cli('history', '--head-sha256', value['decision_sha256'])
        self.assertEqual(history.returncode, 0, history.stderr)
        self.assertEqual(json.loads(history.stdout)['private_history'][0]['decision'], self.decision)

    def test_submission_cli_loads_pinned_policy_then_revocation_with_metrics_still_recomputed(self):
        f = board_fixture.PublicLeaderboardTests(); f.setUp(); self.addCleanup(f.doCleanups)
        f.accept(f.publish()) # SYNTHETIC GPU-scope receipt, not actual execution evidence.
        index = self.root / 'index.json'; index.write_text(json.dumps(f.index), encoding='utf-8')
        digest = self.archive.record(self.decision)
        base = [sys.executable, '-m', 'koevd_eval.submissions', '--store-dir', str(f.store.root),
            '--trusted-index', str(index), '--index-id', 'fixture', '--roles-file', str(self.roles),
            '--protocol-registry', str(f.fixture.fixture.root/'policy-registry'), '--policy-root', str(self.archive.root)]
        def board(head):
            result = subprocess.run(base+['--policy-head-sha256', head, 'public-leaderboard'], capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)['result']
        approved = board(digest); self.assertTrue(approved['boards'])
        self.assertFalse(any(b['metric_id'].startswith(('task3', 'task4')) for b in approved['boards']))
        revoked = self.archive.record({**self.decision, 'action': 'revoke', 'previous_sha256': digest})
        self.assertEqual(board(revoked)['boards'], [])

    def test_space_startup_uses_operator_chain_and_rejects_incomplete_policy_configuration(self):
        f = space_fixture.SpaceServiceTests(); f.setUp(); self.addCleanup(f.doCleanups)
        digest = self.archive.record(self.decision)
        args = ['koevd-space', '--catalog', str(f.root/'catalog.json'), '--demo', '--roles-file', str(self.roles),
            '--submission-root', str(self.root/'submissions'), '--policy-root', str(self.archive.root),
            '--policy-head-sha256', digest]
        env = {'OAUTH_CLIENT_ID': 'SYNTHETIC-client', 'OAUTH_CLIENT_SECRET': 'SYNTHETIC-secret'}
        for selected in (args, args[:-2]):
            with patch.dict(os.environ, env, clear=True), patch.object(sys, 'argv', selected), \
                    patch.object(spaces, 'create_app', return_value=object()) as create, patch('uvicorn.run') as run:
                if selected is args:
                    spaces.main(); run.assert_called_once()
                    self.assertEqual(create.call_args.kwargs['registration'].submissions.rank_policy.ratification_sha256, digest)
                else:
                    with self.assertRaisesRegex(ValueError, 'configured together'): spaces.main()
                    run.assert_not_called()


if __name__ == '__main__': unittest.main()
