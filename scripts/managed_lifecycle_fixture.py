"""Explicit local-only process fixture for validate_managed_space_lifecycle.py.

Not a production provider or login option. A fresh marker, scrubbed environment
and loopback-only connections are required; no actual HF credentials are used.
"""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import socket
import sys
from types import SimpleNamespace


def install():
    root = Path(os.environ['KOEVD_LIFECYCLE_FIXTURE_ROOT']).resolve(strict=True)
    marker = json.loads((root / 'fixture-scope.json').read_text(encoding='utf-8'))
    if marker != {'scope': 'local_CPU_process_integration', 'HF_and_OAuth_are_test_doubles': True}:
        raise ValueError('Explicit local fixture marker required')
    argv = ' '.join(sys.orig_argv)
    role = 'worker' if 'koevd_eval.backups' in argv else 'server' if 'koevd_eval.spaces' in argv else 'launcher'
    trace = root / ('process-' + str(os.getpid()) + '.json')
    trace.write_text(json.dumps({'pid': os.getpid(), 'role': role,
        'backup_token_present': bool(os.environ.get('KOEVD_BACKUP_TOKEN')),
        'HF_TOKEN_present': bool(os.environ.get('HF_TOKEN')),
        'OAuth_secret_present': bool(os.environ.get('OAUTH_CLIENT_SECRET'))}), encoding='utf-8')
    original_connect = socket.socket.connect
    def local_connect(sock, address):
        if isinstance(address, tuple) and address[0] not in ('127.0.0.1', '::1'):
            raise ValueError('Fixture refuses non-loopback network connections')
        return original_connect(sock, address)
    socket.socket.connect = local_connect

    class LocalBucketDouble:
        def __init__(self, **kwargs):
            token = kwargs.get('token') or os.environ.get('HF_TOKEN')
            if token != 'SYNTHETIC-LOCAL-BUCKET-TOKEN':
                raise ValueError('Only synthetic fixture token accepted')
        def bucket_info(self, bucket):
            if bucket != 'Fixture/Managed-Local-Only':
                raise ValueError('Fixture target only')
            return SimpleNamespace(id=bucket, private=True)
        def path(self, key):
            if not re.fullmatch(r'koevd-snapshots/[0-9a-f]{64}\.zip', key):
                raise ValueError('Fixture key invalid')
            return root / 'provider-double' / Path(key).name
        def list_bucket_tree(self, bucket, *, prefix, recursive):
            self.bucket_info(bucket)
            if prefix == 'koevd-snapshots/':
                return [SimpleNamespace(path='koevd-snapshots/' + p.name, type='file', size=p.stat().st_size)
                        for p in (root / 'provider-double').glob('*.zip')]
            path = self.path(prefix)
            return [SimpleNamespace(path=prefix, type='file', size=path.stat().st_size)] if path.exists() else []
        def batch_bucket_files(self, bucket, *, add):
            self.bucket_info(bucket)
            for source, key in add:
                path = self.path(key)
                path.parent.mkdir(exist_ok=True)
                with path.open('xb') as stream:
                    stream.write(Path(source).read_bytes())
        def download_bucket_files(self, bucket, *, files, raise_on_missing_files):
            self.bucket_info(bucket)
            for entry, destination in files:
                shutil.copyfile(self.path(entry.path), destination)

    import huggingface_hub
    huggingface_hub.HfApi = LocalBucketDouble
    from koevd_eval.oauth import HFOAuthProvider
    def synthetic_exchange(self, code, verifier, redirect_uri):
        if code != 'SYNTHETIC-managed-owner' or not redirect_uri.startswith('http://127.0.0.1:'):
            raise ValueError('Local synthetic login only')
        return {'sub': 'SYNTHETIC-managed-owner', 'preferred_username': 'SYNTHETIC managed fixture'}, 120
    HFOAuthProvider.exchange = synthetic_exchange
    from koevd_eval.storage import LocalSubmissionStore
    original_backup = LocalSubmissionStore.backup
    def capture_after_producer_stop(store, destination):
        if role == 'worker' and Path(destination).parent.parent.name.startswith('attempt-000003-'):
            servers = [json.loads(p.read_text(encoding='utf-8')) for p in root.glob('process-*.json')]
            servers = [entry for entry in servers if entry['role'] == 'server']
            if len(servers) != 1: raise ValueError('Expected the sole actual local HTTP producer')
            pid = servers[0]['pid']
            if os.name == 'nt':
                import ctypes
                kernel = ctypes.WinDLL('kernel32',use_last_error=True)
                kernel.OpenProcess.restype = ctypes.c_void_p
                kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p,ctypes.c_uint32]
                kernel.CloseHandle.argtypes = [ctypes.c_void_p]
                handle = kernel.OpenProcess(0x100000,False,pid)
                if not handle:
                    if ctypes.get_last_error() != 87: raise ValueError('Actual producer absence cannot be verified')
                    terminal = True
                else:
                    terminal = kernel.WaitForSingleObject(handle,0) == 0
                    kernel.CloseHandle(handle)
            else:
                try: os.kill(pid,0); terminal = False
                except ProcessLookupError: terminal = True
            if not terminal: raise ValueError('Actual HTTP producer is still live before final capture')
            (root / 'final-capture-producer-stopped.json').write_text(json.dumps({
                'actual_server_pid':pid,'actual_server_terminal_before_SQLite_capture':True}),encoding='utf-8')
        return original_backup(store,destination)
    LocalSubmissionStore.backup = capture_after_producer_stop


def run_launcher(config, launcher, root, port):
    """Only test binding/origin and watchdog differ from the actual main path."""
    import subprocess
    import threading
    spec = importlib.util.spec_from_file_location('managed_lifecycle_under_test', launcher)
    managed = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(managed)
    original_plan, original_popen = managed.plan, subprocess.Popen
    children = []
    def local_plan(*args):
        p = original_plan(*args)
        argv = p['server_argv']
        origin = 'http://127.0.0.1:' + str(port)
        for flag, value in (('--host', '127.0.0.1'), ('--port', str(port)),
                            ('--origin', origin), ('--oauth-origin', origin)):
            argv[argv.index(flag) + 1] = value
        return p
    def owned_start(*args, **kwargs):
        child = original_popen(*args, **kwargs)
        children.append(child)
        (root / 'children.json').write_text(json.dumps([p.pid for p in children]), encoding='utf-8')
        return child
    managed.plan = local_plan
    subprocess.Popen = owned_start
    expired = []
    def stop_when_requested():
        if (root / 'stop-owned-children').exists():
            for child in reversed(children):
                managed.stop_owned(child)
        elif not finished.is_set():
            timer = threading.Timer(.1, stop_when_requested)
            timer.daemon = True
            timer.start()
    def watchdog():
        expired.append(True)
        for child in reversed(children):
            managed.stop_owned(child)
    finished = threading.Event()
    timeout = threading.Timer(45, watchdog)
    timeout.daemon = True
    timeout.start()
    stop_when_requested()
    sys.argv = ['managed-lifecycle-fixture', '--config', str(config)]
    try:
        code = managed.main()
    finally:
        finished.set()
        timeout.cancel()
        for child in reversed(children):
            managed.stop_owned(child)
        subprocess.Popen = original_popen
    (root / 'exit-receipt.json').write_text(json.dumps({'managed_exit_code': code,
        'watchdog_expired': bool(expired), 'all_owned_children_terminal': all(p.poll() is not None for p in children),
        'children': [{'pid': p.pid, 'exit_code': p.poll()} for p in children]}), encoding='utf-8')
    return 2 if expired else code
