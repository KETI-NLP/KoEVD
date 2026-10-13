"""Transactional local persistence for immutable submissions and audit events.

This adapter is for operator-owned local disk. It does not make ephemeral Space
disk durable, authenticate an identity, or protect against a malicious DB owner.
"""
from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sqlite3

from .results import MAX_BYTES, canonical_hash

VERSION = 'koevd-submission-store-v1'


class StorageError(Exception):
    def __init__(self, code, message, status=400):
        self.code, self.status = code, status
        super().__init__(message)


def encode(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def token(value, name):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9:@._-]{0,255}', value):
        raise StorageError('invalid_identifier', 'Invalid ' + name)
    return value


class LocalSubmissionStore:
    """One atomic artifact/revision/event/state/request transaction per operation.

    Immutable SQL triggers are an application safeguard. Event hashes check
    consistency; neither is authentication against someone who controls disk.
    """
    def __init__(self, root, *, capacity_bytes=2 * 1024**3, busy_seconds=10):
        if type(capacity_bytes) is not int or capacity_bytes < 65536:
            raise ValueError('Invalid submission store capacity')
        if type(busy_seconds) not in (int, float) or not 0 < busy_seconds <= 60:
            raise ValueError('Invalid submission store busy timeout')
        path = Path(root).absolute()
        if any(p.is_symlink() for p in (path, *path.parents)):
            raise ValueError('Submission store root must not traverse symlinks')
        path.mkdir(parents=True, exist_ok=True)
        self.root, self.path = path.resolve(), path.resolve() / 'submissions.sqlite3'
        self.capacity_bytes, self.busy_seconds = capacity_bytes, busy_seconds
        if any(p.is_symlink() for p in self.root.iterdir()):
            raise ValueError('Submission store contains a symlink')
        allowed = {'submissions.sqlite3', 'submissions.sqlite3-journal'}
        if any(p.name not in allowed for p in self.root.iterdir()):
            raise ValueError('Submission storage requires a dedicated operator directory')
        if os.name != 'nt': os.chmod(self.root, 0o700)
        with self.connection() as db:
            existing = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if existing:
                row = db.execute("SELECT value FROM meta WHERE key='version'").fetchone()
                if row is None or row[0] != VERSION: raise StorageError('unsupported_store', 'Unknown submission store format')
                triggers = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='trigger'")}
                expected = {f'{table}_{action}' for table in ('meta','indexes','artifacts','revisions','events','requests') for action in ('update','delete')}
                if not expected <= triggers: raise StorageError('store_integrity', 'Immutable store triggers missing', 503)
            else:
                script = '''
                BEGIN IMMEDIATE;
                CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
                CREATE TABLE indexes(id TEXT PRIMARY KEY, digest TEXT NOT NULL);
                CREATE TABLE artifacts(digest TEXT PRIMARY KEY, byte_digest TEXT NOT NULL, data BLOB NOT NULL);
                CREATE TABLE submissions(id TEXT PRIMARY KEY, owner TEXT NOT NULL,
                  initial_artifact TEXT NOT NULL REFERENCES artifacts(digest), state TEXT NOT NULL,
                  UNIQUE(owner, initial_artifact));
                CREATE TABLE revisions(submission TEXT NOT NULL REFERENCES submissions(id),
                  number INTEGER NOT NULL, parent INTEGER, artifact TEXT NOT NULL REFERENCES artifacts(digest),
                  data TEXT NOT NULL, PRIMARY KEY(submission, number));
                CREATE TABLE events(submission TEXT NOT NULL REFERENCES submissions(id),
                  sequence INTEGER NOT NULL, digest TEXT NOT NULL, data TEXT NOT NULL,
                  PRIMARY KEY(submission, sequence));
                CREATE TABLE requests(actor TEXT NOT NULL, key TEXT NOT NULL,
                  fingerprint TEXT NOT NULL, response TEXT NOT NULL, PRIMARY KEY(actor, key));
                INSERT INTO meta VALUES('version', 'koevd-submission-store-v1');
                '''
                for table in ('meta', 'indexes', 'artifacts', 'revisions', 'events', 'requests'):
                    for action in ('UPDATE', 'DELETE'):
                        script += f"CREATE TRIGGER {table}_{action.lower()} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT, 'immutable record'); END;\n"
                db.executescript(script + 'COMMIT;')
        if os.name != 'nt': os.chmod(self.path, 0o600)

    @contextmanager
    def connection(self, *, write=False):
        if any(p.is_symlink() for p in (self.root, self.path, self.path.with_name(self.path.name + '-journal'))):
            raise StorageError('unsafe_store_path', 'Submission store path changed', 503)
        db = sqlite3.connect(self.path, timeout=self.busy_seconds, isolation_level=None)
        db.row_factory = sqlite3.Row
        try:
            db.execute('PRAGMA foreign_keys=ON')
            # Rollback journal avoids requiring a specific fixed WAL runtime or shared-memory FS.
            mode = db.execute('PRAGMA journal_mode=DELETE').fetchone()[0]
            if mode != 'delete': raise StorageError('unsupported_journal', 'Rollback journal is required', 503)
            db.execute('PRAGMA synchronous=EXTRA')
            page_size = db.execute('PRAGMA page_size').fetchone()[0]
            limit = self.capacity_bytes // page_size
            if db.execute(f'PRAGMA max_page_count={limit}').fetchone()[0] > limit:
                raise StorageError('store_capacity', 'Store exceeds configured database capacity', 507)
            if write: db.execute('BEGIN IMMEDIATE')
            else: db.execute('BEGIN')
            yield db
            if db.in_transaction: db.commit()
        except sqlite3.OperationalError as exc:
            if db.in_transaction: db.rollback()
            code = getattr(exc, 'sqlite_errorcode', 0) & 255
            if code in (sqlite3.SQLITE_BUSY, sqlite3.SQLITE_LOCKED):
                raise StorageError('store_busy', 'Store is busy; retry the same idempotency key', 503) from exc
            if code == sqlite3.SQLITE_FULL:
                raise StorageError('store_capacity', 'Submission database capacity reached', 507) from exc
            raise
        except BaseException:
            if db.in_transaction: db.rollback()
            raise
        finally:
            db.close()

    def register_indexes(self, indexes):
        with self.connection(write=True) as db:
            stored = dict(db.execute('SELECT id, digest FROM indexes'))
            if set(stored) - set(indexes): raise StorageError('missing_operator_index', 'Keep indexes referenced by the store')
            for name, digest in indexes.items():
                token(name, 'operator index ID')
                if name in stored and stored[name] != digest:
                    raise StorageError('changed_operator_index', 'An operator index ID changed contents')
                db.execute('INSERT OR IGNORE INTO indexes VALUES(?,?)', (name, digest))

    def apply(self, actor, key, request, operation):
        token(actor, 'actor'); token(key, 'idempotency key')
        fingerprint = canonical_hash(request)
        with self.connection(write=True) as db:
            from .recovery import require_ready
            require_ready(db)
            row = db.execute('SELECT fingerprint,response FROM requests WHERE actor=? AND key=?', (actor,key)).fetchone()
            if row is not None:
                if row['fingerprint'] != fingerprint:
                    raise StorageError('idempotency_conflict', 'Key already used for a different request', 409)
                return json.loads(row['response'])
            response = operation(db)
            db.execute('INSERT INTO requests VALUES(?,?,?,?)', (actor,key,fingerprint,encode(response).decode()))
            return response

    @staticmethod
    def put_artifact(db, document):
        raw, digest = encode(document), document['content_sha256']
        if len(raw) > MAX_BYTES: raise StorageError('artifact_too_large', 'Result exceeds upload size', 413)
        byte_digest = sha256(raw).hexdigest()
        existing = db.execute('SELECT byte_digest FROM artifacts WHERE digest=?', (digest,)).fetchone()
        if existing is not None and existing[0] != byte_digest:
            raise StorageError('artifact_conflict', 'Canonical artifact identity collision', 409)
        db.execute('INSERT OR IGNORE INTO artifacts VALUES(?,?,?)', (digest,byte_digest,raw))
        return digest

    @staticmethod
    def artifact(db, digest):
        row = db.execute('SELECT byte_digest,data FROM artifacts WHERE digest=?', (digest,)).fetchone()
        if row is None or sha256(row['data']).hexdigest() != row['byte_digest']:
            raise StorageError('store_integrity', 'Stored artifact missing or changed', 503)
        document = json.loads(row['data'])
        if document.get('content_sha256') != digest or canonical_hash({k:v for k,v in document.items() if k!='content_sha256'}) != digest:
            raise StorageError('store_integrity', 'Stored artifact seal changed', 503)
        return document

    @staticmethod
    def state(db, submission):
        token(submission, 'submission ID')
        row = db.execute('SELECT state,owner,initial_artifact FROM submissions WHERE id=?', (submission,)).fetchone()
        if row is None: raise StorageError('not_found', 'Submission not found', 404)
        state = json.loads(row[0])
        if state.get('id') != submission or state.get('owner') != row['owner']:
            raise StorageError('store_integrity', 'Submission ownership projection changed', 503)
        events = db.execute('SELECT sequence,digest,data FROM events WHERE submission=? ORDER BY sequence', (submission,)).fetchall()
        previous = None
        for sequence, event in enumerate(events, 1):
            value = json.loads(event['data'])
            if (event['sequence'] != sequence or value.get('sequence') != sequence or value.get('submission_id') != submission
                    or value.get('previous_sha256') != previous or canonical_hash(value) != event['digest']):
                raise StorageError('store_integrity', 'Submission audit chain changed', 503)
            previous = event['digest']
        if not events or value.get('state') != state or state.get('version') != len(events):
            raise StorageError('store_integrity', 'Submission state differs from audit history', 503)
        revisions = db.execute('SELECT number,parent,artifact,data FROM revisions WHERE submission=? ORDER BY number',(submission,)).fetchall()
        for number, revision in enumerate(revisions,1):
            data = json.loads(revision['data'])
            parent = None if number==1 else number-1
            if (revision['number'] != number or revision['parent'] != parent or data.get('number') != number
                    or data.get('parent') != parent or data.get('artifact_sha256') != revision['artifact']):
                raise StorageError('store_integrity','Revision lineage changed',503)
        if not revisions or state['head_revision'] != len(revisions) or revisions[0]['artifact'] != row['initial_artifact']:
            raise StorageError('store_integrity','Original or head revision changed',503)
        return state, [json.loads(event['data']) | {'content_sha256':event['digest']} for event in events]

    @staticmethod
    def event(db, state, *, action, actor, timestamp, details):
        sub = state['id']
        row = db.execute('SELECT digest FROM events WHERE submission=? ORDER BY sequence DESC LIMIT 1', (sub,)).fetchone()
        value = {'format':'koevd-submission-event-v1', 'submission_id':sub, 'sequence':state['version'],
                 'action':action, 'actor':actor, 'at':timestamp, 'details':details,
                 'previous_sha256':row[0] if row else None, 'state':state}
        db.execute('INSERT INTO events VALUES(?,?,?,?)', (sub,state['version'],canonical_hash(value),encode(value).decode()))
        db.execute('UPDATE submissions SET state=? WHERE id=?', (encode(state).decode(),sub))

    def backup(self, destination):
        """Consistent SQLite backup; never copy a live DB file as a backup."""
        path = Path(destination).absolute()
        if path.resolve().is_relative_to(self.root):
            raise StorageError('backup_location', 'Backup must be outside the dedicated live store directory')
        if path.exists() or any(p.is_symlink() for p in (path,*path.parents)):
            raise StorageError('backup_exists', 'Backup needs a new operator-owned path')
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb'): pass
        try:
            with self.connection() as db:
                target = sqlite3.connect(path)
                try:
                    db.backup(target)
                    if target.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                        raise StorageError('backup_integrity', 'Backup integrity check failed', 503)
                finally: target.close()
            if os.name != 'nt': os.chmod(path,0o600)
        except BaseException:
            # Preserve incomplete backup for operator inspection; do not call it successful.
            raise
        return {'sha256':sha256(path.read_bytes()).hexdigest(), 'bytes':path.stat().st_size}
