"""Opt-in server/backup lifecycle candidate; never selected by the dev Dockerfile.

Requires an operator config and a dedicated Bucket token at execution time.
No token creation, billing, Bucket creation, live SQLite mount, publication,
policy ratification or recovery release. Restored stores stay quarantined.
"""
import argparse
import os
from pathlib import Path
import subprocess
import signal
import sys
import time

from koevd_eval.results import read_document, _keys
from koevd_eval.snapshots import safe_path, require_digest
from koevd_eval.storage import token


class InitializationInventoryMismatch(ValueError):
    """Refused before this attempt creates storage or spawns children."""
    code = 'initialization_inventory_mismatch'


class InitializationRootAlreadyExists(ValueError):
    """Existing local data must be preserved and explicitly opened/restored."""
    code = 'initialization_store_root_exists'


def plan(config_path, environ):
    config_path = Path(config_path).resolve()
    c = read_document(config_path, max_bytes=65536)
    required = ('format', 'catalog', 'protocol_registry', 'web_roles', 'backup_roles',
              'backup_actor', 'bucket', 'store_root', 'backup_root', 'mode',
              'restore_root', 'snapshot_sha256', 'interval_seconds', 'cycles',
              'retained_quota_bytes')
    if c.get('format') == 'koevd-managed-space-v2':
        required += ('initialization_baseline_snapshot_sha256',)
    _keys(c, required, 'Managed Space configuration')
    if c['format'] not in ('koevd-managed-space-v1', 'koevd-managed-space-v2'):
        raise ValueError('Unsupported managed configuration')
    host = environ.get('SPACE_HOST', '').lower()
    if (not host.endswith('.hf.space') or
            any(char not in 'abcdefghijklmnopqrstuvwxyz0123456789-.' for char in host)):
        raise ValueError('Canonical HF SPACE_HOST required')
    origin = 'https://' + host

    def path(name, *, file=False):
        value = c[name]
        if not isinstance(value, str) or not value:
            raise ValueError('Explicit operator path required')
        p = Path(value)
        p = safe_path(p if p.is_absolute() else config_path.parent / p)
        if file and not p.is_file():
            raise ValueError('Operator input file missing')
        return p

    files = {name: path(name, file=True) for name in ('catalog', 'web_roles', 'backup_roles')}
    registry = path('protocol_registry')
    if not registry.is_dir():
        raise ValueError('Operator registry directory missing')
    for name in ('web_roles', 'backup_roles'):
        roles = read_document(files[name], max_bytes=1048576)
        _keys(roles, ('reviewers', 'admins'), 'Operator roles')
        if any(not isinstance(v, list) or any(not isinstance(s, str) for s in v) for v in roles.values()):
            raise ValueError('Explicit role lists required')
        if name == 'backup_roles' and c['backup_actor'] not in roles['admins']:
            raise ValueError('Backup actor must be explicitly authorized in separate backup roles')
    token(c['backup_actor'], 'backup operator actor')
    # Validate syntax without creating an SDK client or using a cached login.
    import re
    if not isinstance(c['bucket'], str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*/[A-Za-z0-9][A-Za-z0-9._-]*', c['bucket']):
        raise ValueError('Exact private Bucket owner/name required')
    if type(c['interval_seconds']) is not int or not 1 <= c['interval_seconds'] <= 86400:
        raise ValueError('Invalid backup interval')
    if type(c['cycles']) is not int or not 0 <= c['cycles'] <= 1000:
        raise ValueError('Invalid explicit cycle count')
    if type(c['retained_quota_bytes']) is not int or not 65536 <= c['retained_quota_bytes'] <= 8 * 1024**3:
        raise ValueError('Invalid retained backup bound')
    store, backup = path('store_root'), path('backup_root')
    if store.is_relative_to(backup) or backup.is_relative_to(store):
        raise ValueError('Store and backups must have separate roots')
    mode = c['mode']
    if mode not in ('existing', 'initialize', 'restore'):
        raise ValueError('Choose existing, initialize or pinned restore explicitly')
    baseline = c.get('initialization_baseline_snapshot_sha256')
    if mode == 'initialize':
        if c['format'] != 'koevd-managed-space-v2':
            raise ValueError('Legacy initialization is unsafe across host restarts; supply an independent v2 baseline')
        if not isinstance(baseline, list) or len(baseline) > 1000:
            raise ValueError('Explicit bounded initialization snapshot baseline required')
        for digest in baseline:
            require_digest(digest)
        if len(set(baseline)) != len(baseline):
            raise ValueError('Duplicate initialization snapshot digest')
    elif baseline is not None:
        raise ValueError('Initialization baseline is only used in initialize mode')
    restore = None
    if mode == 'existing':
        if not (store / 'submissions.sqlite3').is_file():
            raise ValueError('Existing store missing; never silently initialize')
    elif mode == 'initialize':
        if store.exists():
            raise InitializationRootAlreadyExists('Initialization requires a new store root')
    else:
        restore = path('restore_root')
        require_digest(c['snapshot_sha256'])
        if restore.exists() or store != restore / 'store':
            raise ValueError('Restore must use a fresh directory and its exact store child')
        if backup.is_relative_to(restore) or restore.is_relative_to(backup):
            raise ValueError('Restore and backups must have separate roots')
    if mode != 'restore' and (c['restore_root'] is not None or c['snapshot_sha256'] is not None):
        raise ValueError('Restore settings require explicit restore mode')
    server = [sys.executable, '-m', 'koevd_eval.spaces', '--catalog', str(files['catalog']),
              '--protocol-registry', str(registry), '--roles-file', str(files['web_roles']),
              '--submission-root', str(store), '--origin', origin, '--oauth-origin', origin,
              '--host', '0.0.0.0', '--port', '7860']
    worker = [sys.executable, '-m', 'koevd_eval.backups', '--store-dir', str(store),
              '--backup-root', str(backup), '--catalog', str(files['catalog']),
              '--protocol-registry', str(registry), '--roles-file', str(files['backup_roles']),
              '--actor', c['backup_actor'], '--bucket', c['bucket'], '--enable-remote-backup',
              '--retained-quota-bytes', str(c['retained_quota_bytes']), 'run',
              '--interval-seconds', str(c['interval_seconds']), '--cycles', str(c['cycles'])]
    if c['cycles'] > 0:
        worker.append('--await-final-snapshot-release')
    return {'config': c, 'files': files, 'registry': registry, 'store': store, 'backup': backup,
            'restore': restore, 'origin': origin, 'server_argv': server, 'worker_argv': worker}


def child_environments(environ, *, restoring=False):
    secret = environ.get('KOEVD_BACKUP_TOKEN')
    if not secret or not secret.strip():
        raise ValueError('Dedicated KOEVD_BACKUP_TOKEN required; no CLI-token fallback')
    server = dict(environ)
    for name in ('KOEVD_BACKUP_TOKEN', 'HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN',
                 'KOEVD_POLICY_ROOT', 'KOEVD_POLICY_HEAD_SHA256'):
        server.pop(name, None)
    worker = dict(server)
    for name in ('OAUTH_CLIENT_ID', 'OAUTH_CLIENT_SECRET', 'OPENID_PROVIDER_URL'):
        worker.pop(name, None)
    worker['HF_TOKEN'] = secret
    worker['HF_ENDPOINT'] = 'https://huggingface.co'
    server['KOEVD_DEPLOYMENT_NOTICE'] = (
        'Managed development candidate: periodic remote snapshots are configured, '
        'but changes after the last verified backup can be lost. Keep your original '
        'JSON locally. Recovery approval and official ranking remain disabled.')
    if restoring:
        server['KOEVD_DEPLOYMENT_NOTICE'] = (
            'Restored development candidate: recovery quarantine remains in force '
            'and the periodic backup worker is not running. The pinned snapshot '
            'does not authenticate the latest state. Keep your original JSON locally. '
            'Recovery approval and official ranking remain disabled.')
    return server, worker


def checked_transport(p, secret):
    """Validate independent inputs and the private Bucket without creating storage."""
    from huggingface_hub import HfApi
    from koevd_eval.space_service import InputCatalog
    from koevd_eval.protocols import ProtocolRegistry
    from koevd_eval.snapshots import HFBucketSnapshots
    catalog = InputCatalog(p['files']['catalog'])
    registry = ProtocolRegistry(p['registry'])
    transport = HFBucketSnapshots(p['config']['bucket'], api=HfApi(endpoint='https://huggingface.co', token=secret))
    transport.private()
    return catalog, registry, transport


def check_initialization_baseline(p, secret):
    """Read-only diagnostic; equality never creates a DB, snapshot or child."""
    if p['config']['mode'] != 'initialize':
        raise ValueError('The initialization baseline check requires initialize mode')
    _, _, transport = checked_transport(p, secret)
    require_initialization_inventory(transport, p['config']['initialization_baseline_snapshot_sha256'])


def prepare_storage(p, secret):
    from koevd_eval.snapshots import restore_snapshot
    from koevd_eval.storage import LocalSubmissionStore
    from koevd_eval.submissions import SubmissionService
    from koevd_eval.backups import BackupManager
    catalog, registry, transport = checked_transport(p, secret)
    indexes = {name: value['index'] for name, value in catalog.indexes.items()}
    if p['config']['mode'] == 'initialize':
        require_initialization_inventory(transport, p['config']['initialization_baseline_snapshot_sha256'])
        # Claim the fresh root atomically; a second startup must not silently
        # open storage created between structural validation and execution.
        p['store'].mkdir(mode=0o700, parents=True, exist_ok=False)
    elif p['config']['mode'] == 'existing' and not (p['store'] / 'submissions.sqlite3').is_file():
        raise ValueError('Existing database disappeared; no empty-store fallback')
    if p['config']['mode'] == 'restore':
        archive = p['restore'].with_name(p['restore'].name + '.pinned-download.zip')
        if archive.exists():
            raise ValueError('Preserve existing download; choose a fresh restore path')
        transport.fetch(p['config']['snapshot_sha256'], archive)
        restored = restore_snapshot(archive, p['config']['snapshot_sha256'], p['restore'], indexes, registry=registry)
        if restored['policy_head_sha256'] is not None:
            raise ValueError('This candidate cannot activate a restored operator policy; store stays quarantined')
    store = LocalSubmissionStore(p['store'])
    SubmissionService(store, indexes, registry=registry)  # Validate/create independent index bindings; no user events.
    if p['config']['mode'] != 'restore':
        # Existing/empty local storage must have a verified first snapshot before
        # a new server accepts writes. Restores stay offline/quarantined instead.
        manager = BackupManager(store, indexes, p['backup'], actor=p['config']['backup_actor'],
                                registry=registry, transport=transport, max_bytes=p['config']['retained_quota_bytes'])
        result = manager.run(cycles=1)
        if result['failures']:
            raise ValueError('Initial remote backup failed; server not started')
        if p['config']['mode'] == 'initialize':
            completed = read_document(manager.attempts()[-1][1] / 'COMPLETED.json', max_bytes=8192)
            if completed['snapshot_sha256'] in p['config']['initialization_baseline_snapshot_sha256']:
                raise ValueError('Initial backup must add a new snapshot; no restart guard would be established')


def require_initialization_inventory(transport, expected):
    """Fail closed when a fresh local disk meets snapshots outside its baseline.

The baseline is operator supplied, never discovered and auto-approved at boot.
This is not an atomic remote lock or protection against a malicious Bucket owner.
"""
    from koevd_eval.snapshots import MAX_SNAPSHOT_BYTES
    import re
    seen = set()
    for item in transport.call('list_bucket_tree', transport.bucket_id,
                               prefix='koevd-snapshots/', recursive=False):
        match = re.fullmatch(r'koevd-snapshots/([0-9a-f]{64})\.zip', item.path)
        if (match is None or item.type != 'file' or type(item.size) is not int
                or not 0 < item.size <= MAX_SNAPSHOT_BYTES or len(seen) >= 1000):
            raise ValueError('Unexpected initialization snapshot inventory')
        digest = match[1]
        if digest in seen:
            raise ValueError('Duplicate remote initialization snapshot')
        seen.add(digest)
    if seen != set(expected):
        raise InitializationInventoryMismatch('Remote snapshots differ from initialization baseline; never silently create an empty replacement store')


def stop_owned(process):
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def supervise(server_argv, worker_argv, server_env, worker_env):
    if '--await-final-snapshot-release' in worker_argv:
        return supervise_finite(server_argv, worker_argv, server_env, worker_env)
    children = []
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        for argv, env in ((worker_argv, worker_env), (server_argv, server_env)):
            children.append(subprocess.Popen(argv, env=env, shell=False, creationflags=flags))
        while True:
            for child in children:
                code = child.poll()
                if code is not None:
                    return code
            time.sleep(.1)
    except KeyboardInterrupt:
        return 0
    finally:
        for child in reversed(children):
            stop_owned(child)


def supervise_finite(server_argv, worker_argv, server_env, worker_env):
    """Stop the producer before releasing the worker's last capture.

    SIGTERM gets a bounded grace period; remaining unacknowledged work can be
    aborted. Committed transactions precede HTTP success and remain in SQLite.
    This does not cover crashes, periodic lag or malicious/local extra writers.
    """
    import json
    import queue
    import threading
    children, worker, reader = [], None, None
    messages = queue.Queue(maxsize=1024)
    final_released = False
    stream_closed = False
    no_message = object()
    def read_messages():
        try:
            while True:
                line = worker.stdout.readline(4097)
                if not line: break
                messages.put(line if len(line)<=4096 else False)
                if len(line)>4096: break
        finally:
            messages.put(None)
    try:
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        worker = subprocess.Popen(worker_argv, env=worker_env, shell=False, creationflags=flags,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding='utf-8')
        children.append(worker)
        server = subprocess.Popen(server_argv, env=server_env, shell=False, creationflags=flags)
        children.append(server)
        reader = threading.Thread(target=read_messages, daemon=True)
        reader.start()
        while True:
            try: line = messages.get(timeout=.1)
            except queue.Empty: line = no_message
            if line is None: stream_closed = True
            if line is False: raise ValueError('Worker protocol line exceeds bound')
            if isinstance(line,str) and line:
                value = json.loads(line)
                if (not isinstance(value,dict) or value.get('execution_scope')!='operator_private_backup'
                        or set(value)-{'execution_scope','event','cycle','result','published'}):
                    raise ValueError('Unexpected worker protocol')
                if 'event' in value:
                    if value!={'execution_scope':'operator_private_backup','event':'awaiting_final_snapshot_release'} or final_released:
                        raise ValueError('Unexpected final capture request')
                    if server.poll() is not None: raise ValueError('Server exited before coordinated shutdown')
                    stop_owned(server)
                    if server.poll() is None: raise ValueError('Server shutdown not confirmed')
                    print(json.dumps({'execution_scope':'managed_private_lifecycle','event':'server_stopped_before_final_snapshot'}),flush=True)
                    worker.stdin.write('FINAL_SNAPSHOT\n'); worker.stdin.flush()
                    final_released = True
                else:
                    print(json.dumps(value),flush=True)
            code = worker.poll()
            if code is not None and stream_closed:
                return code if code or final_released else 2
            if not final_released and server.poll() is not None:
                return server.returncode or 2
    except KeyboardInterrupt:
        return 0
    finally:
        for child in reversed(children): stop_owned(child)
        if worker is not None:
            for stream in (worker.stdin,worker.stdout):
                if stream is not None:
                    try: stream.close()
                    except (OSError,ValueError): pass
        if reader is not None: reader.join(timeout=1)


def run_restored_server(server_argv, server_env):
    """Keep a handle to the sole restored-server child and always reap it."""
    child = subprocess.Popen(server_argv, env=server_env, shell=False,
                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    try:
        return child.wait()
    except KeyboardInterrupt:
        return 0
    finally:
        stop_owned(child)


def termination_requested(signum, frame):
    # HF/Linux sends SIGTERM to the launcher; unwind through owned-child cleanup.
    raise KeyboardInterrupt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    checks = parser.add_mutually_exclusive_group()
    checks.add_argument('--check', action='store_true', help='Validate paths/roles/argv only; no credential or network')
    checks.add_argument('--check-initialization-baseline', action='store_true',
                        help='Read-only private Bucket inventory check with the dedicated token; no storage, backup or server')
    args = parser.parse_args()
    previous_termination_handler = None
    try:
        p = plan(args.config, os.environ)
        if args.check:
            import json
            print(json.dumps({'configuration_structurally_valid': True, 'mode': p['config']['mode'],
                              'server_argv': p['server_argv'], 'worker_argv': p['worker_argv'],
                              'dedicated_runtime_token_required': True, 'catalog_and_Bucket_validated': False,
                              'external_operations_performed': False}))
            return 0
        server_env, worker_env = child_environments(os.environ, restoring=p['config']['mode'] == 'restore')
        if args.check_initialization_baseline:
            check_initialization_baseline(p, worker_env['HF_TOKEN'])
            import json
            print(json.dumps({'initialization_baseline_matches': True,
                              'database_root_created_by_this_attempt': False,
                              'server_or_worker_spawned_by_this_attempt': False,
                              'remote_snapshot_writes': False}))
            return 0
        from koevd_eval.oauth import HFOAuthProvider
        HFOAuthProvider(server_env.get('OAUTH_CLIENT_ID', ''), server_env.get('OAUTH_CLIENT_SECRET', ''),
                       client_type=server_env.get('KOEVD_OAUTH_CLIENT_TYPE', 'confidential'))
        previous_termination_handler = signal.signal(signal.SIGTERM, termination_requested)
        prepare_storage(p, worker_env['HF_TOKEN'])
        # A pinned restore starts the existing app in recovery quarantine. Do
        # not turn an old restored state into a new active-backup claim.
        if p['config']['mode'] == 'restore':
            return run_restored_server(p['server_argv'], server_env)
        return supervise(p['server_argv'], p['worker_argv'], server_env, worker_env)
    except KeyboardInterrupt:
        return 0
    except (InitializationInventoryMismatch, InitializationRootAlreadyExists) as refused:
        import json
        print(json.dumps({'startup': 'refused', 'code': refused.code,
                          'database_root_created_by_this_attempt': False,
                          'server_or_worker_spawned_by_this_attempt': False}), file=sys.stderr)
        return 2
    except Exception:
        print('Managed startup failed; no successful operational acceptance is claimed.', file=sys.stderr)
        return 2  # Never print provider URLs, token values or uploaded text.
    finally:
        if previous_termination_handler is not None:
            signal.signal(signal.SIGTERM, previous_termination_handler)


if __name__ == '__main__':
    raise SystemExit(main())
