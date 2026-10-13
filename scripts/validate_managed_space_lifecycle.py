"""Real local server/worker/HTTP lifecycle using explicit HF/OAuth test doubles.

Uses existing original results; performs no inference, HF request, approval,
public posting or actual managed-HF/container acceptance. Keeps all evidence.
"""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from urllib.parse import parse_qs, urlsplit

import httpx
from koevd_eval.results import read_document, validate_results
from koevd_eval.snapshots import file_digest
from materialize_managed_space import checked_base


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-candidate', required=True)
    parser.add_argument('--result', action='append', required=True)
    parser.add_argument('--result-sha256', action='append', required=True)
    parser.add_argument('--initialization-baseline-digest', action='append', default=[],
                        help='Seed metadata-only local provider doubles; never actual remote archives')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    if len(args.result) != 2 or len(args.result_sha256) != 2:
        parser.error('Exactly two independently hashed existing originals required')
    from koevd_eval.snapshots import require_digest
    if len(args.initialization_baseline_digest) > 1000 or len(set(args.initialization_baseline_digest)) != len(args.initialization_baseline_digest):
        parser.error('Explicit unique bounded local inventory digests required')
    for digest in args.initialization_baseline_digest:
        require_digest(digest)
    repo = Path(__file__).resolve().parents[1]
    base = Path(args.base_candidate).resolve(strict=True)
    checked_base(repo, base)
    catalog = read_document(base / 'operator-data/catalog.json')
    entry = next(e for e in catalog['indexes'] if e['id'] == 'koevd-prefix-4')
    index_path = base / 'operator-data' / entry['path']
    if file_digest(index_path) != entry['sha256']:
        raise ValueError('Independent input file changed')
    index = read_document(index_path)
    results = [Path(p).resolve(strict=True) for p in args.result]
    documents = []
    for path, expected in zip(results, args.result_sha256):
        if file_digest(path) != expected:
            raise ValueError('Original result byte digest changed')
        document = read_document(path)
        validate_results(document, index)
        documents.append(document)
    out = Path(args.output).resolve()
    out.mkdir(mode=0o700, parents=True, exist_ok=False)
    data = out / 'operator-data'
    data.mkdir()
    shutil.copyfile(index_path, data / entry['path'])
    write(data / 'catalog.json', {'schema_version': 'koevd-space-catalog-v1', 'indexes': [entry], 'baselines': []})
    write(data / 'web-roles.json', {'reviewers': [], 'admins': []})
    write(data / 'backup-roles.json', {'reviewers': [], 'admins': ['SYNTHETIC-managed-backup']})
    hooks = out / 'python-hooks'
    hooks.mkdir()
    (hooks / 'sitecustomize.py').write_text('from managed_lifecycle_fixture import install\ninstall()\n', encoding='utf-8')
    config = {'format': 'koevd-managed-space-v2', 'catalog': str(data / 'catalog.json'),
        'protocol_registry': str(repo / 'configs/protocols'), 'web_roles': str(data / 'web-roles.json'),
        'backup_roles': str(data / 'backup-roles.json'), 'backup_actor': 'SYNTHETIC-managed-backup',
        'bucket': 'Fixture/Managed-Local-Only', 'store_root': str(out / 'live-store'),
        'backup_root': str(out / 'backup-copies'), 'mode': 'initialize', 'restore_root': None,
        'initialization_baseline_snapshot_sha256': args.initialization_baseline_digest,
        'snapshot_sha256': None, 'interval_seconds': 20, 'cycles': 2, 'retained_quota_bytes': 128 * 1024**2}
    env = {k: v for k, v in os.environ.items() if not k.startswith(('KOEVD_', 'OAUTH_', 'HF_', 'HUGGING_FACE_'))
           and k not in ('PYTHONPATH', 'PYTHONHOME', 'OPENID_PROVIDER_URL')}
    env.update(PYTHONPATH=os.pathsep.join((str(hooks), str(repo / 'scripts'))),
        PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1',
        KOEVD_BACKUP_TOKEN='SYNTHETIC-LOCAL-BUCKET-TOKEN',
        OAUTH_CLIENT_ID='SYNTHETIC-local-lifecycle', OAUTH_CLIENT_SECRET='SYNTHETIC-local-OAuth-secret',
        SPACE_HOST='keti-nlp-koevd-platform-dev.hf.space')
    phases, states = [], []
    started = time.monotonic()
    def launch(name, *, expected_rejection=False):
        root = out / name
        root.mkdir()
        write(root / 'fixture-scope.json', {'scope': 'local_CPU_process_integration', 'HF_and_OAuth_are_test_doubles': True})
        provider_root = root / 'provider-double'
        if phases:
            shutil.copytree(phases[0]['root'] / 'provider-double', provider_root)
        elif args.initialization_baseline_digest:
            provider_root.mkdir()
            for digest in args.initialization_baseline_digest:
                (provider_root / (digest + '.zip')).write_bytes(b'SYNTHETIC baseline metadata only; not an actual snapshot ZIP')
        phase_env = dict(env, KOEVD_LIFECYCLE_FIXTURE_ROOT=str(root))
        cfg = root / 'managed.json'
        write(cfg, config)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        log = (root / 'server-worker.log').open('wb')
        argv = [sys.executable, '-c', 'from pathlib import Path;import sys;from managed_lifecycle_fixture import run_launcher;'
                'raise SystemExit(run_launcher(Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3]),int(sys.argv[4])))',
                str(cfg), str(repo / 'apps/spaces/managed_launch.py'), str(root), str(port)]
        process = subprocess.Popen(argv, env=phase_env, stdout=log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        phase = {'root': root, 'process': process, 'log': log, 'origin': 'http://127.0.0.1:' + str(port)}
        phases.append(phase)
        client = httpx.Client(base_url=phase['origin'], trust_env=False, timeout=10, follow_redirects=False)
        deadline = time.monotonic() + 30
        while True:
            if process.poll() is not None:
                if expected_rejection:
                    client.close()
                    log.close()
                    ended = read_document(root / 'exit-receipt.json')
                    assert process.returncode == 2 and ended['all_owned_children_terminal']
                    assert ended['children'] == [] and not ended['watchdog_expired']
                    return phase, None
                raise ValueError('Launcher stopped before real server readiness; inspect retained log')
            try:
                health = client.get('/healthz')
                if health.status_code == 200 and health.json() == {'status': 'ready', 'registration_enabled': True}:
                    break
            except httpx.TransportError:
                pass
            if time.monotonic() >= deadline:
                raise TimeoutError('Readiness observation expired; same owned process will be stopped by fixture watchdog')
            time.sleep(.1)
        return phase, client
    def signed_in(client):
        login = client.get('/auth/login')
        assert login.status_code in (302, 303, 307)
        state = parse_qs(urlsplit(login.headers['location']).query)['state'][0]
        callback = client.get('/auth/callback', params={'state': state, 'code': 'SYNTHETIC-managed-owner'})
        assert callback.status_code in (302, 303)
        identity = client.get('/api/identity').json()
        assert identity['signed_in'] and not identity['reviewer'] and not identity['admin']
        return identity
    def stop(phase):
        (phase['root'] / 'stop-owned-children').touch()
        code = phase['process'].wait(timeout=20)
        phase['log'].close()
        ended = read_document(phase['root'] / 'exit-receipt.json')
        assert not ended['watchdog_expired'] and ended['all_owned_children_terminal']
        return code, ended
    try:
        phase, client = launch('initialize')
        with closing(client):
            identity = signed_in(client)
            session = client.post('/api/session', json={}).json()
            headers = {'Origin': phase['origin'], 'Authorization': 'Bearer ' + session['session_token'],
                'X-KoEVD-CSRF': session['csrf_token'], 'X-KoEVD-Auth-CSRF': identity['csrf_token']}
            for i, (path, document) in enumerate(zip(results, documents)):
                upload = client.post('/api/uploads', content=path.read_bytes(), headers={**headers, 'Content-Type': 'application/json'})
                assert upload.status_code == 201
                created = client.post('/api/submissions', json={'upload_id': upload.json()['id'], 'key': 'local-managed-' + str(i)}, headers=headers)
                assert created.status_code == 201
                saved = created.json()
                states.append(saved)
                assert client.get('/api/submissions/' + saved['id'] + '/result').json() == document
            histories = [client.get('/api/submissions/' + s['id'] + '/history').json() for s in states]
            assert not client.get('/api/registration').json()['official_ranking_enabled']
        # Two actual worker cycles, in addition to the initial first-backup gate.
        assert phase['process'].wait(timeout=35) == 0
        phase['log'].close()
        ended = read_document(phase['root'] / 'exit-receipt.json')
        assert ended['all_owned_children_terminal'] and not ended['watchdog_expired']
        final_capture = read_document(phase['root'] / 'final-capture-producer-stopped.json')
        assert final_capture['actual_server_terminal_before_SQLite_capture']
        with httpx.Client(trust_env=False,timeout=2) as late_client:
            try:
                late_client.post(phase['origin']+'/api/submissions',json={'upload_id':'not-admitted-after-shutdown','key':'late-after-final'})
            except httpx.TransportError: pass
            else: raise ValueError('Stopped producer accepted a connection after final capture')
        copies = sorted((out / 'backup-copies').glob('attempt-*/COMPLETED.json'))
        assert len(copies) == 3
        baseline_names = {digest + '.zip' for digest in args.initialization_baseline_digest}
        new_objects = {p.name for p in (phase['root'] / 'provider-double').glob('*.zip')} - baseline_names
        assert len(new_objects) == 3
        last = read_document(copies[-1])
        from koevd_eval.backups import BackupManager
        from koevd_eval.storage import LocalSubmissionStore
        from koevd_eval.protocols import ProtocolRegistry
        from koevd_eval.snapshots import HFBucketSnapshots
        registry = ProtocolRegistry(repo / 'configs/protocols')
        indexes = {entry['id']: index}
        # Status inspects the local completed pair, never calls this API object.
        with_bucket_double = HFBucketSnapshots('Fixture/Managed-Local-Only', api=object())
        status = BackupManager(LocalSubmissionStore(out / 'live-store'), indexes, out / 'backup-copies',
            actor=config['backup_actor'], registry=registry, transport=with_bucket_double, max_bytes=config['retained_quota_bytes']).status()
        assert status['last_verified_sequence'] == 3 and status['changes_pending'] is False
        # Model a platform replacing the local disk while retaining the remote
        # snapshots. A new empty root must fail before any server or upload.
        config.update(store_root=str(out / 'restarted-empty-store'), backup_root=str(out / 'restarted-empty-backups'))
        rejected, unused_client = launch('fresh-host-restart-refused', expected_rejection=True)
        assert unused_client is None and not (out / 'restarted-empty-store').exists()
        before_objects = {p.name: p.read_bytes() for p in (phases[0]['root'] / 'provider-double').glob('*.zip')}
        after_objects = {p.name: p.read_bytes() for p in (rejected['root'] / 'provider-double').glob('*.zip')}
        assert before_objects == after_objects
        config.update(mode='restore', initialization_baseline_snapshot_sha256=None, restore_root=str(out / 'restored'), store_root=str(out / 'restored/store'), snapshot_sha256=last['snapshot_sha256'])
        phase, client = launch('restore')
        with closing(client):
            identity = signed_in(client)
            for saved, document, history in zip(states, documents, histories):
                assert client.get('/api/submissions/' + saved['id'] + '/result').json() == document
                assert client.get('/api/submissions/' + saved['id'] + '/history').json() == history
            for path in ('/api/public/submissions', '/api/public/leaderboard'):
                response = client.get(path)
                assert response.status_code == 503 and response.json()['error']['code'] == 'recovery_required'
            session = client.post('/api/session', json={}).json()
            headers = {'Origin': phase['origin'], 'Authorization': 'Bearer ' + session['session_token'],
                'X-KoEVD-CSRF': session['csrf_token'], 'X-KoEVD-Auth-CSRF': identity['csrf_token']}
            upload = client.post('/api/uploads', content=results[0].read_bytes(), headers={**headers, 'Content-Type': 'application/json'})
            assert upload.status_code == 201
            refused = client.post('/api/submissions', json={'upload_id': upload.json()['id'], 'key': 'restore-must-not-create'}, headers=headers)
            assert refused.status_code == 503 and refused.json()['error']['code'] == 'recovery_required'
            page = client.get('/').text
            assert 'periodic backup worker is not running' in page
        # Restart requires a new identity session; originals/history are independent.
        code, restored_end = stop(phase)
        traces = [read_document(p) for phase in phases for p in phase['root'].glob('process-*.json')]
        servers = [t for t in traces if t['role'] == 'server']
        workers = [t for t in traces if t['role'] == 'worker']
        assert len(servers) == 2 and len(workers) == 1
        assert all(not t['backup_token_present'] and not t['HF_TOKEN_present'] and t['OAuth_secret_present'] for t in servers)
        assert all(t['HF_TOKEN_present'] and not t['OAuth_secret_present'] for t in workers)
        # No synthetic or actual credential/session value is serialized in receipts.
        evidence = {'status': 'passed', 'scope': 'local_CPU_real_owned_server_worker_HTTP_lifecycle',
            'observed_utc': datetime.now(timezone.utc).isoformat(), 'seconds': round(time.monotonic() - started, 3),
            'records': [len(d['records']) for d in documents], 'original_byte_sha256': args.result_sha256,
            'HF_and_OAuth_are_explicit_test_doubles': True, 'actual_HF_login_or_container': False,
            'test_only_loopback_binding_and_watchdog': True, 'external_network_connections_refused_in_children': True,
            'first_backup_plus_worker_cycles': 3, 'last_verified_sequence': status['last_verified_sequence'],
            'initialization_baseline_count': len(args.initialization_baseline_digest),
            'baseline_objects_are_metadata_only_local_doubles': True,
            'new_snapshot_objects': len(new_objects),
            'changes_pending': status['changes_pending'], 'originals_and_histories_equal_after_pinned_restore': True,
            'restored_public_read_and_submission_mutation_blocked': True, 'restore_worker_not_started': True,
            'fresh_host_restart_refused_before_new_store_children_or_upload': True,
            'actual_HTTP_producer_terminal_before_final_SQLite_capture': True,
            'late_write_after_shutdown_connection_refused': True,
            'credential_environment_separation_proven_in_real_children': True, 'all_owned_children_terminal': True,
            'new_inference': False, 'real_Bucket_write': False, 'official_rank_or_recovery_approval': False}
        write(out / 'evidence.json', evidence)
        print(json.dumps(evidence))
    except Exception:
        write(out / 'failure.json', {'status': 'failed', 'scope': 'local_CPU_real_owned_process_lifecycle',
            'details_in_retained_local_logs': True, 'actual_HF_acceptance_claimed': False})
        raise
    finally:
        for phase in phases:
            if phase['process'].poll() is None:
                try: stop(phase)
                except Exception:
                    # The fixture watchdog owns the children; wait for its bounded cleanup.
                    phase['process'].wait(timeout=50)
            if not phase['log'].closed:
                phase['log'].close()


if __name__ == '__main__':
    main()
