"""Private point-in-time DB + pinned policy-chain snapshots, never HTTP uploads.

Restoration requires an independently pinned ZIP digest and operator indexes.
No roles, credentials, server configuration or automatic publication is restored.
Bucket objects are mutable: content addressing is checked, not WORM or signing.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import tempfile
import zipfile

from .policy_decisions import PolicyArchive, MAX_HISTORY
from .protocols import ProtocolRegistry
from .results import MAX_BYTES, canonical_hash, read_document, validate_index, validate_results
from .storage import LocalSubmissionStore, encode, token

FORMAT = 'koevd-private-snapshot-v1'
MAX_SNAPSHOT_BYTES = 2 * 1024**3 + 8 * 1024**2
MAX_MANIFEST_BYTES = 256 * 1024
MAX_ROWS = 1000000
TABLES = ('meta', 'indexes', 'artifacts', 'submissions', 'revisions', 'events', 'requests')


def safe_path(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('Snapshot path must not traverse symlinks')
    return path


def require_digest(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('An independently selected SHA-256 is required')
    return value


def file_digest(path):
    h = sha256()
    with safe_path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()


def copy_bounded(source, destination, maximum):
    h, count = sha256(), 0
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as target:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            count += len(chunk)
            if count > maximum: raise ValueError('Snapshot file exceeds size limit')
            h.update(chunk); target.write(chunk)
        target.flush(); os.fsync(target.fileno())
    return {'sha256': h.hexdigest(), 'bytes': count}


def fsync_dir(path):
    if os.name != 'nt':
        fd = os.open(path, os.O_RDONLY)
        try: os.fsync(fd)
        finally: os.close(fd)


def bindings(indexes, registry=None):
    if not isinstance(indexes, dict) or not 1 <= len(indexes) <= 8:
        raise ValueError('Snapshot needs 1–8 independent operator indexes')
    if registry is not None and not isinstance(registry, ProtocolRegistry):
        raise ValueError('Independent protocol registry required')
    for name, index in indexes.items():
        token(name, 'operator index ID'); validate_index(index)
        if index['protocol'].get('kind') == 'standard':
            if registry is None: raise ValueError('Standard index requires an outside registry')
            registry.validate_index(index['protocol']['id'], index)
    return {'indexes': {k: v['content_sha256'] for k, v in sorted(indexes.items())},
            'protocols': {k: v['content_sha256'] for k, v in sorted(registry.definitions.items())}
                         if registry is not None else {}}


@contextmanager
def readonly_db(path):
    db = sqlite3.connect(safe_path(path).as_uri() + '?mode=ro&immutable=1', uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute('PRAGMA trusted_schema=OFF')
        yield db
    finally: db.close()


def schema(db):
    return [(r['type'], r['name'], r['tbl_name'], r['sql']) for r in db.execute(
        'SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name')]


def verify_database(path, indexes, expected_bindings):
    """Read-only validation, including exact known SQL schema before domain reads."""
    with tempfile.TemporaryDirectory(prefix='koevd-schema-') as temporary:
        fresh = LocalSubmissionStore(Path(temporary) / 'schema')
        with readonly_db(fresh.path) as trusted: expected_schema = schema(trusted)
    with readonly_db(path) as db:
        if schema(db) != expected_schema: raise ValueError('Snapshot DB SQL schema differs from the known store')
        if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchone():
            raise ValueError('Snapshot database integrity check failed')
        if db.execute("SELECT value FROM meta WHERE key='version'").fetchone()[0] != 'koevd-submission-store-v1':
            raise ValueError('Unknown snapshot database version')
        from .recovery import inspect_recovery
        inspect_recovery(db)
        if dict(db.execute('SELECT id,digest FROM indexes')) != expected_bindings['indexes']:
            raise ValueError('Snapshot DB operator bindings differ from outside catalog')
        counts = {name: db.execute('SELECT COUNT(*) FROM ' + name).fetchone()[0] for name in TABLES}
        if sum(counts.values()) > MAX_ROWS: raise ValueError('Snapshot row inspection limit reached')
        by_hash = {v['content_sha256']: v for v in indexes.values()}
        for row in db.execute('SELECT digest,length(data) AS size FROM artifacts'):
            if row['size'] > MAX_BYTES: raise ValueError('Snapshot artifact exceeds size limit')
            document = LocalSubmissionStore.artifact(db, row['digest'])
            index = by_hash.get(document.get('input_index_sha256'))
            if index is None: raise ValueError('Snapshot artifact lacks an outside input index')
            validate_results(document, index)
        if db.execute('SELECT digest FROM artifacts WHERE digest NOT IN (SELECT artifact FROM revisions)').fetchone():
            raise ValueError('Snapshot contains an orphan artifact')
        for row in db.execute('SELECT id FROM submissions'):
            state, events = LocalSubmissionStore.state(db, row['id'])
            if state.get('index_id') not in indexes: raise ValueError('Snapshot submission index missing')
            if len(events) > 1000 or state['head_revision'] > 100: raise ValueError('Snapshot submission history exceeds limit')
            for revision in db.execute('SELECT artifact FROM revisions WHERE submission=?', (row['id'],)):
                document = LocalSubmissionStore.artifact(db, revision['artifact'])
                if document['input_index_sha256'] != indexes[state['index_id']]['content_sha256']:
                    raise ValueError('Snapshot revision changed its bound input index')
        for row in db.execute('SELECT actor,key,fingerprint,response FROM requests'):
            token(row['actor'], 'request actor'); token(row['key'], 'request key'); require_digest(row['fingerprint'])
            value = json.loads(row['response'])
            if encode(value).decode('utf-8') != row['response']: raise ValueError('Noncanonical replay response')
    return counts


def create_snapshot(store, indexes, destination, *, registry=None, policy_root=None, policy_head=None):
    if not isinstance(store, LocalSubmissionStore): raise ValueError('Expected a local live store')
    if bool(policy_root) != bool(policy_head): raise ValueError('Policy root and explicit head must be supplied together')
    outside = bindings(indexes, registry)
    history = PolicyArchive(policy_root).history(policy_head) if policy_root else []
    dest = safe_path(destination)
    if dest.exists(): raise ValueError('Snapshot output already exists')
    if dest.is_relative_to(store.root) or (policy_root and dest.is_relative_to(safe_path(policy_root))):
        raise ValueError('Snapshot must be outside live stores')
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.koevd-snapshot-', dir=dest.parent) as temporary:
        stage = Path(temporary); database = stage / 'submissions.sqlite3'
        db_info = store.backup(database)
        counts = verify_database(database, indexes, outside)
        files = {'submissions.sqlite3': db_info}
        for entry in history:
            name = 'policy/' + entry['sha256'] + '.json'
            path = stage / name; path.parent.mkdir(exist_ok=True)
            raw = encode(entry['decision']) + b'\n'; path.write_bytes(raw)
            files[name] = {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}
        manifest = {'format': FORMAT, 'created_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'bindings': outside, 'policy_head_sha256': policy_head, 'counts': counts, 'files': files,
                    'scope': 'private_point_in_time', 'automatic_activation': False}
        pending = stage / 'snapshot.zip'
        with zipfile.ZipFile(pending, 'x', compression=zipfile.ZIP_STORED) as archive:
            archive.writestr('manifest.json', encode(manifest))
            for name in sorted(files): archive.write(stage / name, name)
        if os.name != 'nt': os.chmod(pending, 0o600)
        if pending.stat().st_size > MAX_SNAPSHOT_BYTES: raise ValueError('Snapshot exceeds configured limit')
        with pending.open('r+b') as stream: os.fsync(stream.fileno())
        digest = file_digest(pending)
        os.link(pending, dest); fsync_dir(dest.parent)
    return {'sha256': digest, 'bytes': dest.stat().st_size, 'counts': counts,
            'policy_decisions': len(history), 'policy_head_sha256': policy_head,
            'automatic_activation': False, 'remote_stored': False}


def unpack_verified(archive_path, expected_sha256, stage, indexes, registry=None):
    require_digest(expected_sha256)
    source = safe_path(archive_path)
    if source.stat().st_size > MAX_SNAPSHOT_BYTES: raise ValueError('Snapshot exceeds configured limit')
    copied = stage / 'input.zip'
    with source.open('rb') as stream: info = copy_bounded(stream, copied, MAX_SNAPSHOT_BYTES)
    if info['sha256'] != expected_sha256: raise ValueError('Snapshot differs from independently pinned byte digest')
    outside = bindings(indexes, registry)
    with zipfile.ZipFile(copied) as archive:
        members = archive.infolist()
        names = [m.filename for m in members]
        if len(members) > MAX_HISTORY + 2 or len(set(names)) != len(names): raise ValueError('Duplicate/too many snapshot members')
        for m in members:
            mode = m.external_attr >> 16
            if (m.compress_type != zipfile.ZIP_STORED or m.flag_bits & 1 or m.is_dir()
                    or stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0, stat.S_IFREG))
                    or m.file_size != m.compress_size):
                raise ValueError('Unsupported snapshot member type or compression')
        if 'manifest.json' not in names: raise ValueError('Snapshot manifest missing')
        with archive.open('manifest.json') as stream: copy_bounded(stream, stage / 'manifest.json', MAX_MANIFEST_BYTES)
        manifest = read_document(stage / 'manifest.json', max_bytes=MAX_MANIFEST_BYTES)
        if (set(manifest) != {'format','created_at','bindings','policy_head_sha256','counts','files','scope','automatic_activation'}
                or manifest['format'] != FORMAT or manifest['scope'] != 'private_point_in_time'
                or manifest['automatic_activation'] is not False or manifest['bindings'] != outside):
            raise ValueError('Unsupported snapshot or outside operator bindings mismatch')
        try:
            when = datetime.strptime(manifest['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            if when.strftime('%Y-%m-%dT%H:%M:%SZ') != manifest['created_at']: raise ValueError('Noncanonical time')
        except (ValueError, TypeError) as exc: raise ValueError('Invalid snapshot time') from exc
        files = manifest['files']
        if not isinstance(files, dict) or 'submissions.sqlite3' not in files or set(names) != set(files) | {'manifest.json'}:
            raise ValueError('Snapshot manifest file set mismatch')
        head = manifest['policy_head_sha256']
        if head is not None: require_digest(head)
        if head is None and len(files) != 1: raise ValueError('Unselected policy records in snapshot')
        for name, expected in files.items():
            if name != 'submissions.sqlite3' and not re.fullmatch(r'policy/[0-9a-f]{64}\.json', name):
                raise ValueError('Unexpected snapshot member path')
            if (not isinstance(expected, dict) or set(expected) != {'sha256','bytes'}
                    or type(expected['bytes']) is not int or not 0 < expected['bytes'] <= MAX_SNAPSHOT_BYTES):
                raise ValueError('Invalid snapshot member metadata')
            require_digest(expected['sha256'])
            maximum = 2 * 1024**3 if name == 'submissions.sqlite3' else 16384
            path = stage / name; path.parent.mkdir(exist_ok=True)
            with archive.open(name) as stream: actual = copy_bounded(stream, path, maximum)
            if actual != expected: raise ValueError('Snapshot member digest or size changed')
        counts = verify_database(stage / 'submissions.sqlite3', indexes, outside)
        if (not isinstance(manifest['counts'], dict) or any(type(v) is not int for v in manifest['counts'].values())
                or manifest['counts'] != counts): raise ValueError('Snapshot table counts changed')
        history = PolicyArchive(stage / 'policy').history(head) if head else []
        if set(files) != {'submissions.sqlite3'} | {'policy/' + v['sha256'] + '.json' for v in history}:
            raise ValueError('Snapshot policy chain differs from manifest')
    return manifest


def restore_snapshot(archive_path, expected_sha256, destination, indexes, *, registry=None):
    """Verify first; install into a fresh, offline operator directory only."""
    dest = safe_path(destination)
    if dest.exists(): raise ValueError('Restore requires a fresh directory')
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Cooperating restore commands serialize publication. Never overwrite a target.
    lock = dest.with_name('.' + dest.name + '.restore-lock')
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    try:
        with tempfile.TemporaryDirectory(prefix='.koevd-restore-', dir=dest.parent) as temporary:
            stage = Path(temporary)
            manifest = unpack_verified(archive_path, expected_sha256, stage, indexes, registry)
            ready = stage / 'ready'; ready.mkdir(mode=0o700)
            (ready / 'store').mkdir(mode=0o700)
            os.rename(stage / 'submissions.sqlite3', ready / 'store' / 'submissions.sqlite3')
            from .recovery import mark_restore
            recovery_sequence = mark_restore(LocalSubmissionStore(ready / 'store'), expected_sha256)
            if manifest['policy_head_sha256']: os.rename(stage / 'policy', ready / 'policy')
            receipt = {'format': 'koevd-snapshot-restore-v1', 'snapshot_sha256': expected_sha256,
                       'bindings': manifest['bindings'], 'snapshot_created_at': manifest['created_at'],
                       'counts': manifest['counts'], 'policy_head_sha256': manifest['policy_head_sha256'],
                       'automatic_activation': False, 'latest_state_verified': False,
                       'recovery_sequence': recovery_sequence, 'recovery_required': True,
                       'requires_withdrawal_reconciliation': True, 'public_server_started': False}
            with (ready / 'restore-receipt.json').open('xb') as stream:
                stream.write(encode(receipt) + b'\n'); stream.flush(); os.fsync(stream.fileno())
            if (ready / 'policy').exists(): fsync_dir(ready / 'policy')
            fsync_dir(ready / 'store'); fsync_dir(ready)
            if dest.exists(): raise ValueError('Restore destination appeared; preserve it')
            os.rename(ready, dest); fsync_dir(dest.parent)
        return receipt
    finally: lock.unlink()


class HFBucketSnapshots:
    """Single-object transport to an EXISTING private bucket. No creation/billing.

    Upload has no conditional-write/WORM guarantee. Verify by download and pin
    digests independently. A malicious bucket owner or visibility change after
    preflight cannot be prevented here. Never use this as a live SQLite mount.
    """
    def __init__(self, bucket_id, *, api=None):
        if not isinstance(bucket_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*/[A-Za-z0-9][A-Za-z0-9._-]*', bucket_id):
            raise ValueError('Explicit existing bucket owner/name required')
        if api is None:
            from huggingface_hub import HfApi
            api = HfApi()  # Standard local token resolution; never serialize it.
        self.bucket_id, self.api = bucket_id, api

    def call(self, method, *args, **kwargs):
        try: return getattr(self.api, method)(*args, **kwargs)
        except Exception:
            raise ValueError('Hugging Face bucket operation failed; no successful snapshot receipt') from None

    def private(self):
        info = self.call('bucket_info', self.bucket_id)
        if info.id != self.bucket_id or info.private is not True:
            raise ValueError('Snapshot transport requires the exact existing PRIVATE bucket')

    def key(self, digest): return 'koevd-snapshots/' + require_digest(digest) + '.zip'

    def metadata(self, digest):
        key = self.key(digest)
        items = iter(self.call('list_bucket_tree', self.bucket_id, prefix=key, recursive=False))
        for number in range(5):
            try: item = next(items)
            except StopIteration: break
            except Exception: raise ValueError('Hugging Face bucket listing failed') from None
            if number >= 4: raise ValueError('Unexpected bucket object listing')
            if item.path == key:
                if item.type != 'file' or type(item.size) is not int or not 0 < item.size <= MAX_SNAPSHOT_BYTES:
                    raise ValueError('Invalid/oversize bucket snapshot')
                return item
        return None

    def fetch(self, digest, destination):
        self.private(); item = self.metadata(digest)
        if item is None: raise ValueError('Pinned remote snapshot missing')
        dest = safe_path(destination)
        if dest.exists(): raise ValueError('Download requires a new file')
        dest.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.koevd-fetch-', dir=dest.parent) as temporary:
            downloaded = Path(temporary) / 'snapshot.zip'
            self.call('download_bucket_files', self.bucket_id, files=[(item, downloaded)], raise_on_missing_files=True)
            safe_path(downloaded)
            if downloaded.stat().st_size != item.size or downloaded.stat().st_size > MAX_SNAPSHOT_BYTES or file_digest(downloaded) != digest:
                raise ValueError('Remote snapshot bytes differ from pinned digest/metadata')
            if os.name != 'nt': os.chmod(downloaded, 0o600)
            with downloaded.open('r+b') as stream: os.fsync(stream.fileno())
            os.link(downloaded, dest); fsync_dir(dest.parent)
        return {'sha256': digest, 'bytes': dest.stat().st_size, 'download_verified': True}

    def put(self, archive_path, digest):
        require_digest(digest); source = safe_path(archive_path)
        self.private()
        with tempfile.TemporaryDirectory(prefix='koevd-bucket-put-') as temporary:
            frozen = Path(temporary) / 'snapshot.zip'
            with source.open('rb') as stream: info = copy_bounded(stream, frozen, MAX_SNAPSHOT_BYTES)
            if info['sha256'] != digest: raise ValueError('Local upload differs from pinned digest')
            existing = self.metadata(digest)
            if existing is None:
                self.call('batch_bucket_files', self.bucket_id, add=[(frozen, self.key(digest))])
            # Existing objects are not overwritten; verify them too. One object
            # avoids multi-file batch partiality; interrupted uploads need retry.
            self.fetch(digest, Path(temporary) / 'readback.zip')
        return {'sha256': digest, 'object_key': self.key(digest), 'readback_verified': True,
                'atomic_conditional_write': False, 'human_approval_authenticated': False}


def main():
    import argparse
    import sys
    from .common import configure_cli_stdio
    from .space_service import InputCatalog
    from .storage import StorageError
    configure_cli_stdio()
    p = argparse.ArgumentParser(description='Private operator snapshots; no HTTP restore, startup, roles or approval')
    p.add_argument('--catalog', required=True, help='Outside operator catalog, never obtained from a snapshot/upload')
    p.add_argument('--protocol-registry')
    p.add_argument('--roles-file', required=True); p.add_argument('--actor', required=True)
    p.add_argument('--demo', action='store_true', help='Explicit synthetic CPU test scope')
    commands = p.add_subparsers(dest='command', required=True)
    create = commands.add_parser('create'); create.add_argument('--store-dir', required=True); create.add_argument('--output', required=True)
    create.add_argument('--policy-root'); create.add_argument('--policy-head-sha256')
    restore = commands.add_parser('restore'); restore.add_argument('--input', required=True); restore.add_argument('--sha256', required=True); restore.add_argument('--destination', required=True)
    for name in ('put-hf', 'fetch-hf'):
        command = commands.add_parser(name); command.add_argument('--bucket', required=True); command.add_argument('--sha256', required=True)
        command.add_argument('--input' if name == 'put-hf' else '--output', required=True)
    args = p.parse_args()
    try:
        roles = read_document(args.roles_file, max_bytes=1024*1024)
        if (set(roles) != {'reviewers','admins'} or any(not isinstance(v,list) or len(v)>1000
                or any(not isinstance(s,str) for s in v) for v in roles.values())): raise ValueError('Invalid outside roles')
        token(args.actor, 'local snapshot administrator')
        if args.actor not in roles['admins']: raise ValueError('Independent local administrator required')
        catalog = InputCatalog(args.catalog, allow_synthetic=args.demo)
        indexes = {k: v['index'] for k,v in catalog.indexes.items()}
        registry = ProtocolRegistry(args.protocol_registry) if args.protocol_registry else None
        if args.command == 'create':
            store = safe_path(args.store_dir)
            if not (store / 'submissions.sqlite3').is_file(): raise ValueError('Existing live store required')
            result = create_snapshot(LocalSubmissionStore(store), indexes, args.output, registry=registry,
                                     policy_root=args.policy_root, policy_head=args.policy_head_sha256)
        elif args.command == 'restore':
            result = restore_snapshot(args.input, args.sha256, args.destination, indexes, registry=registry)
        elif args.command == 'put-hf':
            # Validate semantic contents before sending private originals remotely.
            with tempfile.TemporaryDirectory(prefix='koevd-preflight-') as temporary:
                unpack_verified(args.input, args.sha256, Path(temporary), indexes, registry)
            result = HFBucketSnapshots(args.bucket).put(args.input, args.sha256)
        else: result = HFBucketSnapshots(args.bucket).fetch(args.sha256, args.output)
        print(json.dumps({'execution_scope': 'operator_private_snapshot', 'result': result,
                          'published': False, 'synthetic_demo': args.demo}, ensure_ascii=False))
    except (ValueError, StorageError, OSError, sqlite3.Error, zipfile.BadZipFile, ImportError) as exc:
        # Provider exceptions may contain request details: do not dump tokens/URLs.
        print(json.dumps({'error': 'snapshot_failed', 'message': str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)


if __name__ == '__main__': main()
