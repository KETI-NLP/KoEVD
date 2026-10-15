"""Synchronous checkpoint acknowledgement for the submission store.

A successful mutation must have a confirmed checkpoint before it is returned.
The file ledger below is a local adapter and test surface, not cloud storage.
Remote adapters must implement the same checked commit/head contract. Neither
hashes nor this adapter authenticate an operator or grant publication rights.
"""
from contextlib import closing, contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import threading
import uuid

from .recovery import TABLE_COLUMNS, ORDERS
from .results import canonical_hash, read_document
from .snapshots import file_digest, fsync_dir, require_digest, safe_path
from .storage import LocalSubmissionStore, StorageError, encode

FORMAT = 'koevd-acknowledged-checkpoint-v1'


def logical_digest(db):
    """Hash all persisted state, including actual artifact bytes, not DB headers."""
    tables = {}
    total = 0
    for table, columns in TABLE_COLUMNS.items():
        checksum = sha256()
        count = 0
        for row in db.execute('SELECT '+','.join(columns)+' FROM '+table+' ORDER BY '+ORDERS[table]):
            values = [{'bytes':len(v), 'sha256':sha256(v).hexdigest()} if isinstance(v, bytes) else v for v in row]
            checksum.update(encode(values)+b'\n')
            count += 1
            total += 1
            if total > 1000000:
                raise StorageError('checkpoint_capacity', 'Checkpoint row limit reached', 507)
        tables[table] = {'rows':count, 'sha256':checksum.hexdigest()}
    return canonical_hash(tables)


def checked_receipt(value, expected_logical=None):
    fields = {'format','sequence','parent_sha256','logical_sha256','database_sha256','database_bytes','content_sha256'}
    if (not isinstance(value, dict) or set(value) != fields or value['format'] != FORMAT
            or type(value['sequence']) is not int or not 1 <= value['sequence'] <= 1000000
            or type(value['database_bytes']) is not int or value['database_bytes'] < 4096):
        raise StorageError('checkpoint_integrity', 'Invalid checkpoint receipt', 503)
    try:
        for key in ('logical_sha256','database_sha256','content_sha256'):
            require_digest(value[key])
        if value['parent_sha256'] is not None:
            require_digest(value['parent_sha256'])
    except ValueError:
        raise StorageError('checkpoint_integrity', 'Invalid checkpoint identity', 503) from None
    if ((value['sequence'] == 1) != (value['parent_sha256'] is None)
            or canonical_hash({k:v for k,v in value.items() if k != 'content_sha256'}) != value['content_sha256']
            or (expected_logical is not None and value['logical_sha256'] != expected_logical)):
        raise StorageError('checkpoint_integrity', 'Checkpoint does not describe the committed state', 503)
    return value


class FileCheckpointLedger:
    """Content-addressed checkpoints with a single-writer local HEAD.

    The directory must be on a separately retained filesystem to survive loss
    of the live store. A leftover commit lock requires operator inspection; it
    is never silently stolen. Objects are mutable to the filesystem owner.
    """
    kind = 'local_files'

    def __init__(self, root, *, max_database_bytes=2*1024**3, max_retained_bytes=8*1024**3):
        self.root = safe_path(root)
        if type(max_database_bytes) is not int or max_database_bytes < 65536:
            raise ValueError('Invalid checkpoint size bound')
        if type(max_retained_bytes) is not int or max_retained_bytes < 65536:
            raise ValueError('Invalid retained checkpoint quota')
        self.max_database_bytes = max_database_bytes
        self.max_retained_bytes = max_retained_bytes
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        if any(p.is_symlink() for p in self.root.rglob('*')):
            raise ValueError('Checkpoint ledger contains a symlink')

    def _manifest(self, digest):
        require_digest(digest)
        value = read_document(safe_path(self.root/(digest+'.json')), max_bytes=8192)
        checked_receipt(value)
        if value['content_sha256'] != digest:
            raise StorageError('checkpoint_integrity', 'Checkpoint manifest address changed', 503)
        return value

    def head(self):
        path = safe_path(self.root/'HEAD.json')
        if not path.exists():
            # Orphaned objects can be an interrupted first commit, not proof of
            # an empty namespace. Do not initialize over that uncertainty.
            if any(p.name != '.commit-lock' for p in self.root.iterdir()):
                raise StorageError('checkpoint_initialization_required', 'Ledger has objects but no committed HEAD', 503)
            return None
        pointer = read_document(path, max_bytes=1024)
        if not isinstance(pointer, dict) or set(pointer) != {'checkpoint_sha256'}:
            raise StorageError('checkpoint_integrity', 'Invalid checkpoint HEAD', 503)
        value = self._manifest(pointer['checkpoint_sha256'])
        current = value
        for _ in range(10000):
            if current['parent_sha256'] is None:
                break
            parent = self._manifest(current['parent_sha256'])
            if parent['sequence'] != current['sequence']-1:
                raise StorageError('checkpoint_integrity', 'Checkpoint ancestry changed', 503)
            current = parent
        else:
            raise StorageError('checkpoint_capacity', 'Checkpoint ancestry inspection limit reached', 507)
        database = safe_path(self.root/(value['database_sha256']+'.sqlite3'))
        if (not database.is_file() or database.stat().st_size != value['database_bytes']
                or database.stat().st_size > self.max_database_bytes
                or file_digest(database) != value['database_sha256']):
            raise StorageError('checkpoint_integrity', 'Committed checkpoint database changed', 503)
        return value

    @contextmanager
    def _writer(self):
        lock = safe_path(self.root/'.commit-lock')
        try:
            fd = os.open(lock, os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o600)
        except FileExistsError:
            raise StorageError('checkpoint_busy', 'Checkpoint writer is active or needs inspection', 503) from None
        with os.fdopen(fd, 'wb') as stream:
            stream.write(encode({'pid':os.getpid()})); stream.flush(); os.fsync(stream.fileno())
        try:
            yield
        finally:
            lock.unlink()

    def _object(self, source, target):
        target = safe_path(target)
        if target.exists():
            if file_digest(source) != file_digest(target):
                raise StorageError('checkpoint_integrity', 'Addressed checkpoint object changed', 503)
            return
        # Never leave a partial object at its content address: exact replay
        # must be able to retry a failed copy without adopting corrupt bytes.
        # Restore may cross filesystems (retained volume -> ephemeral runtime).
        # Stage beside the destination so the final link stays on one volume.
        pending = safe_path(target.parent/('.object-'+uuid.uuid4().hex+'.pending'))
        try:
            with Path(source).open('rb') as original, pending.open('xb') as saved:
                shutil.copyfileobj(original, saved, length=1024*1024)
                saved.flush(); os.fsync(saved.fileno())
            os.link(pending, target); fsync_dir(target.parent)
        finally:
            if pending.exists(): pending.unlink()

    def commit(self, store, expected_logical, expected_parent):
        require_digest(expected_logical)
        if self.root.is_relative_to(store.root) or store.root.is_relative_to(self.root):
            raise ValueError('Live store and retained checkpoints must be separate')
        with self._writer():
            previous = self.head()
            # Also reconcile a commit whose HEAD succeeded but caller response
            # was lost; do not create a second checkpoint for an exact replay.
            if previous and previous['logical_sha256'] == expected_logical:
                return previous
            parent = previous['content_sha256'] if previous else None
            if parent != expected_parent:
                raise StorageError('checkpoint_conflict', 'Another writer changed the checkpoint HEAD', 409)
            if previous and previous['sequence'] >= 10000:
                raise StorageError('checkpoint_capacity', 'Retained checkpoint ancestry requires operator maintenance', 507)
            with tempfile.TemporaryDirectory(prefix='koevd-commit-') as temporary:
                stage = Path(temporary)
                raw = stage/'database.sqlite3'
                saved = store.backup(raw)
                if saved['bytes'] > self.max_database_bytes:
                    raise StorageError('checkpoint_capacity', 'Checkpoint database exceeds size bound', 507)
                with closing(sqlite3.connect(raw)) as db:
                    if logical_digest(db) != expected_logical:
                        raise StorageError('checkpoint_integrity', 'Backup cut changed during commit', 503)
                value = {'format':FORMAT, 'sequence':previous['sequence']+1 if previous else 1,
                         'parent_sha256':parent, 'logical_sha256':expected_logical,
                         'database_sha256':saved['sha256'], 'database_bytes':saved['bytes']}
                value['content_sha256'] = canonical_hash(value)
                checked_receipt(value, expected_logical)
                retained = sum(p.stat().st_size for p in self.root.iterdir() if p.is_file())
                if retained+saved['bytes']+8192 > self.max_retained_bytes:
                    raise StorageError('checkpoint_capacity', 'Retained checkpoint quota reached', 507)
                manifest = stage/'manifest.json'; manifest.write_bytes(encode(value)+b'\n')
                self._object(raw, self.root/(saved['sha256']+'.sqlite3'))
                self._object(manifest, self.root/(value['content_sha256']+'.json'))
                pending = safe_path(self.root/('.'+uuid.uuid4().hex+'.pending'))
                with pending.open('xb') as stream:
                    stream.write(encode({'checkpoint_sha256':value['content_sha256']})+b'\n')
                    stream.flush(); os.fsync(stream.fileno())
                os.replace(pending, self.root/'HEAD.json'); fsync_dir(self.root)
            return checked_receipt(self.head(), expected_logical)

    def restore(self, destination):
        head = self.head()
        if head is None:
            raise StorageError('checkpoint_missing', 'No acknowledged checkpoint to restore', 503)
        root = safe_path(destination)
        if root.exists() or root.is_relative_to(self.root) or self.root.is_relative_to(root):
            raise ValueError('Restore requires a fresh separate destination')
        root.mkdir(parents=True, mode=0o700)
        self._object(self.root/(head['database_sha256']+'.sqlite3'), root/'submissions.sqlite3')
        with closing(sqlite3.connect(root/'submissions.sqlite3')) as db:
            if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok' or logical_digest(db) != head['logical_sha256']:
                raise StorageError('checkpoint_integrity', 'Restored checkpoint differs', 503)
        fsync_dir(root)
        return head


class AcknowledgedSubmissionStore(LocalSubmissionStore):
    """Serialize reads/writes with checkpoint confirmation before success.

    A sink failure leaves a local, unacknowledged cut. All subsequent access
    retries confirmation before exposing it. Exact request replay remains in
    the same SQLite transaction history. Reopening a divergent local cut is
    refused; restore the authoritative checkpoint rather than erase it.
    """
    def __init__(self, root, sink, **kwargs):
        if not callable(getattr(sink, 'head', None)) or not callable(getattr(sink, 'commit', None)):
            raise ValueError('Explicit checkpoint sink required')
        self.sink = sink
        self._lock = threading.RLock()
        self._ready = self._dirty = self._checkpointing = False
        self.last_checkpoint = sink.head()
        if self.last_checkpoint and not (Path(root)/'submissions.sqlite3').exists():
            raise StorageError('checkpoint_restore_required', 'Restore the acknowledged store before opening it', 503)
        super().__init__(root, **kwargs)
        with super().connection() as db:
            digest = logical_digest(db)
            if self.last_checkpoint:
                checked_receipt(self.last_checkpoint, digest)
            elif db.execute('SELECT count(*) FROM submissions').fetchone()[0]:
                raise StorageError('checkpoint_initialization_required', 'Existing data needs explicit checkpoint adoption', 503)
        self._ready = True

    @contextmanager
    def readiness_connection(self):
        """Check the acknowledged cut without confirming or writing a dirty cut."""
        with self._lock:
            if not self._ready or self._dirty or self._checkpointing:
                raise StorageError('durability_unavailable', 'Acknowledged storage is not ready', 503)
            fence = getattr(self.sink, 'check_current', None)
            if callable(fence):
                fence(self.last_checkpoint)
            with super().connection() as db:
                yield db

    def _confirm(self):
        if not self._dirty:
            return
        self._checkpointing = True
        try:
            with super().connection() as db:
                digest = logical_digest(db)
            parent = self.last_checkpoint['content_sha256'] if self.last_checkpoint else None
            receipt = self.sink.commit(self, digest, parent)
            self.last_checkpoint = checked_receipt(receipt, digest)
            self._dirty = False
        except StorageError:
            raise
        except Exception:
            # Exceptions from remote adapters can contain credentials/URLs.
            raise StorageError('durability_unavailable', 'Submission checkpoint was not confirmed; retry the same request', 503) from None
        finally:
            self._checkpointing = False

    @contextmanager
    def connection(self, *, write=False):
        with self._lock:
            if self._ready and not self._checkpointing:
                self._confirm()
                fence = getattr(self.sink, 'check_current', None)
                if callable(fence):
                    # A second server must not expose an older publication cut.
                    fence(self.last_checkpoint)
            with super().connection(write=write) as db:
                before = db.total_changes
                yield db
                changed = write and db.total_changes != before
            if self._ready and changed and not self._checkpointing:
                self._dirty = True
                self._confirm()
