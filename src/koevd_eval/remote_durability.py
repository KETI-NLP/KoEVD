"""Acknowledged checkpoints in an explicitly configured existing private Bucket.

Immutable objects precede a conditional S3 HEAD write. No bucket creation,
credential fallback, automatic publication, retention deletion or billing action.
Provider credentials authorize storage; hashes do not authenticate an operator.
"""
from contextlib import closing
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile

from .durability import checked_receipt, logical_digest, FORMAT
from .results import canonical_hash, _unique_object
from .snapshots import file_digest, fsync_dir, require_digest, safe_path
from .storage import StorageError, encode


def _failure(code='durability_unavailable'):
    return StorageError(code, 'Private checkpoint storage was not confirmed; no successful acknowledgement', 503)


class HFS3StateObjects:
    """Explicit HF metadata identity plus scoped S3 conditional object access.

    Construct the clients from dedicated server secrets. Never resolve ordinary
    HF/CLI/AWS credentials implicitly. Bucket privacy is checked by the ledger
    before each operation; an owner changing visibility later cannot be prevented.
    """
    def __init__(self, bucket_id, *, api, client):
        if (not isinstance(bucket_id, str) or not re.fullmatch(
                r'[A-Za-z0-9][A-Za-z0-9_-]*/[A-Za-z0-9][A-Za-z0-9._-]*', bucket_id)):
            raise ValueError('Explicit private state bucket owner/name required')
        self.bucket_id, self.api, self.client = bucket_id, api, client
        self.namespace, self.bucket = bucket_id.split('/')

    @classmethod
    def from_secrets(cls, bucket_id, *, hf_token, access_key_id, secret_access_key):
        if any(not isinstance(v,str) or not v.strip() for v in (hf_token,access_key_id,secret_access_key)):
            raise ValueError('Dedicated state token and S3 secrets required; no cached fallback')
        if (not isinstance(bucket_id,str) or not re.fullmatch(
                r'[A-Za-z0-9][A-Za-z0-9_-]*/[A-Za-z0-9][A-Za-z0-9._-]*',bucket_id)):
            raise ValueError('Explicit state bucket required')
        namespace=bucket_id.split('/')[0]
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*',namespace):
            raise ValueError('Invalid state bucket namespace')
        import boto3
        from botocore.config import Config
        from huggingface_hub import HfApi
        client=boto3.client('s3',endpoint_url='https://s3.hf.co/'+namespace,
            aws_access_key_id=access_key_id,aws_secret_access_key=secret_access_key,
            config=Config(region_name='us-east-1',s3={'addressing_style':'path'},
                request_checksum_calculation='when_required',response_checksum_validation='when_required',
                connect_timeout=10,read_timeout=120,retries={'total_max_attempts':1}))
        return cls(bucket_id,api=HfApi(token=hf_token,endpoint='https://huggingface.co'),client=client)

    def private(self):
        try:info=self.api.bucket_info(self.bucket_id)
        except Exception:raise _failure() from None
        if info.id!=self.bucket_id or info.private is not True:
            raise _failure('checkpoint_target_not_private')

    @staticmethod
    def _error(exc):
        response=getattr(exc,'response',{})
        return response.get('Error',{}).get('Code') if isinstance(response,dict) else None

    def read(self, key, limit):
        try:response=self.client.get_object(Bucket=self.bucket,Key=key)
        except Exception as exc:
            if self._error(exc) in ('NoSuchKey','404'):return None
            raise _failure() from None
        body=response['Body']
        try:
            if type(response.get('ContentLength')) is not int or not 0<=response['ContentLength']<=limit:
                raise _failure('checkpoint_integrity')
            raw=body.read(limit+1)
            if len(raw)!=response['ContentLength']:raise _failure('checkpoint_integrity')
            etag=response.get('ETag')
            if not isinstance(etag,str) or not etag or len(etag)>256:raise _failure('checkpoint_integrity')
            return raw,etag
        finally:body.close()

    def fetch(self, key, target, expected_size, expected_sha):
        try:response=self.client.get_object(Bucket=self.bucket,Key=key)
        except Exception:raise _failure() from None
        body=response['Body'];digest=sha256();count=0
        try:
            if response.get('ContentLength')!=expected_size:raise _failure('checkpoint_integrity')
            with safe_path(target).open('xb') as stream:
                while chunk:=body.read(1024*1024):
                    count+=len(chunk)
                    if count>expected_size:raise _failure('checkpoint_integrity')
                    digest.update(chunk);stream.write(chunk)
                stream.flush();os.fsync(stream.fileno())
            if count!=expected_size or digest.hexdigest()!=expected_sha:
                raise _failure('checkpoint_integrity')
        finally:body.close()

    def put(self, key, source, *, absent=False, etag=None):
        if absent==bool(etag):raise ValueError('One explicit conditional write precondition required')
        condition={'IfNoneMatch':'*'} if absent else {'IfMatch':etag}
        def send(body):
            try:self.client.put_object(Bucket=self.bucket,Key=key,Body=body,**condition)
            except Exception as exc:
                if self._error(exc) in ('PreconditionFailed','412','ConditionalRequestConflict','409'):
                    return False
                raise _failure() from None
            return True
        if isinstance(source,bytes):return send(source)
        with safe_path(source).open('rb') as stream:return send(stream)

    def usage(self, prefix):
        total=count=0;continuation=None
        while True:
            kwargs={'Bucket':self.bucket,'Prefix':prefix+'/','MaxKeys':1000}
            if continuation:kwargs['ContinuationToken']=continuation
            try:response=self.client.list_objects_v2(**kwargs)
            except Exception:raise _failure() from None
            for item in response.get('Contents',[]):
                if (not isinstance(item.get('Key'),str) or not item['Key'].startswith(prefix+'/')
                        or type(item.get('Size')) is not int or item['Size']<0):
                    raise _failure('checkpoint_integrity')
                total+=item['Size'];count+=1
                if count>20000:raise _failure('checkpoint_capacity')
            if not response.get('IsTruncated'):return total,count
            next_token=response.get('NextContinuationToken')
            if not isinstance(next_token,str) or not next_token or next_token==continuation:
                raise _failure('checkpoint_integrity')
            continuation=next_token


class RemoteCheckpointLedger:
    """Conditional HEAD authority and disposable local staging, no mounted SQL.

    HEAD contains the full checked receipt. Every live read is fenced against
    another writer's newer HEAD. Restore downloads only the acknowledged cut;
    it never adopts an orphan, scans for the newest filename or erases live data.
    """
    kind='hf_private_bucket_conditional'

    def __init__(self, objects, *, prefix='koevd-state-v1', initialize_empty=False,
                 max_database_bytes=2*1024**3, max_retained_bytes=8*1024**3,max_sequence=10000):
        if not isinstance(prefix,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',prefix):
            raise ValueError('Explicit simple state namespace required')
        if type(initialize_empty) is not bool:raise ValueError('Explicit initialization flag required')
        if any(type(v) is not int or v<65536 for v in (max_database_bytes,max_retained_bytes)):
            raise ValueError('Positive bounded remote capacity required')
        if type(max_sequence) is not int or not 1<=max_sequence<=10000:
            raise ValueError('Explicit bounded checkpoint sequence required')
        self.objects,self.prefix,self.initialize_empty=objects,prefix,initialize_empty
        self.max_database_bytes,self.max_retained_bytes=max_database_bytes,max_retained_bytes
        self.max_sequence=max_sequence

    def _call(self, name, *args, **kwargs):
        try:return getattr(self.objects,name)(*args,**kwargs)
        except StorageError:raise
        except Exception:raise _failure() from None

    def _key(self, digest, suffix):
        return self.prefix+'/objects/'+require_digest(digest)+suffix

    def _head(self):
        self._call('private')
        result=self._call('read',self.prefix+'/HEAD.json',8192)
        if result is None:
            _,count=self._call('usage',self.prefix)
            if count or not self.initialize_empty:
                raise _failure('checkpoint_initialization_required')
            return None,None
        raw,etag=result
        try:value=json.loads(raw.decode('utf-8'),object_pairs_hook=_unique_object)
        except (ValueError,UnicodeError):raise _failure('checkpoint_integrity') from None
        checked_receipt(value)
        if value['database_bytes']>self.max_database_bytes or value['sequence']>self.max_sequence:raise _failure('checkpoint_capacity')
        manifest=self._call('read',self._key(value['content_sha256'],'.json'),8192)
        if manifest is None or manifest[0]!=encode(value)+b'\n':raise _failure('checkpoint_integrity')
        return value,etag

    def head(self):return self._head()[0]

    def check_current(self, expected):
        current,_=self._head()
        if current!=expected:raise _failure('checkpoint_stale')

    def _immutable(self, key, source, size, digest, stage):
        self._call('put',key,source,absent=True)
        # Verify both fresh uploads and a pre-existing object after HTTP 412.
        target=stage/'readback'
        if target.exists():target.unlink()
        self._call('fetch',key,target,size,digest)
        target.unlink()

    def commit(self, store, expected_logical, expected_parent):
        require_digest(expected_logical)
        previous,etag=self._head()
        if previous and previous['logical_sha256']==expected_logical:return previous
        parent=previous['content_sha256'] if previous else None
        if parent!=expected_parent:
            raise StorageError('checkpoint_conflict','Another writer changed the acknowledged checkpoint',409)
        if previous and previous['sequence']>=self.max_sequence:raise _failure('checkpoint_capacity')
        with tempfile.TemporaryDirectory(prefix='koevd-remote-cut-') as temporary:
            stage=Path(temporary);raw=stage/'database.sqlite3';saved=store.backup(raw)
            if saved['bytes']>self.max_database_bytes:raise _failure('checkpoint_capacity')
            with closing(sqlite3.connect(raw)) as db:
                if logical_digest(db)!=expected_logical:raise _failure('checkpoint_integrity')
            value={'format':FORMAT,'sequence':previous['sequence']+1 if previous else 1,
                   'parent_sha256':parent,'logical_sha256':expected_logical,
                   'database_sha256':saved['sha256'],'database_bytes':saved['bytes']}
            value['content_sha256']=canonical_hash(value);checked_receipt(value,expected_logical)
            manifest=encode(value)+b'\n'
            used,count=self._call('usage',self.prefix)
            if count+3>20000 or used+saved['bytes']+2*len(manifest)>self.max_retained_bytes:
                raise _failure('checkpoint_capacity')
            self._immutable(self._key(saved['sha256'],'.sqlite3'),raw,saved['bytes'],saved['sha256'],stage)
            self._immutable(self._key(value['content_sha256'],'.json'),manifest,len(manifest),sha256(manifest).hexdigest(),stage)
            success=self._call('put',self.prefix+'/HEAD.json',manifest,absent=etag is None,etag=etag)
            if not success:raise StorageError('checkpoint_conflict','Another writer changed the acknowledged checkpoint',409)
            current,_=self._head()
            if current!=value:raise _failure('checkpoint_stale')
            return checked_receipt(current,expected_logical)

    def restore(self, destination):
        value=self.head()
        if value is None:raise _failure('checkpoint_missing')
        root=safe_path(destination)
        if root.exists():raise ValueError('Remote restore requires a fresh destination')
        root.parent.mkdir(parents=True,exist_ok=True)
        # Complete staging is moved into place only after bytes and SQL match.
        with tempfile.TemporaryDirectory(prefix='.koevd-remote-restore-',dir=root.parent) as temporary:
            stage=Path(temporary);database=stage/'submissions.sqlite3'
            self._call('fetch',self._key(value['database_sha256'],'.sqlite3'),database,
                       value['database_bytes'],value['database_sha256'])
            with closing(sqlite3.connect(database)) as db:
                if db.execute('PRAGMA quick_check').fetchone()[0]!='ok' or logical_digest(db)!=value['logical_sha256']:
                    raise _failure('checkpoint_integrity')
            self.check_current(value)
            fsync_dir(stage);os.rename(stage,root);fsync_dir(root.parent)
        return value


def open_acknowledged_store(destination, ledger):
    """Restore authoritative HEAD for a fresh runtime; preserve divergent disk.

    Empty initialization still requires the explicit ledger flag and namespace
    inspection. Caller must register its operator indexes before serving users.
    Existing nonempty state is never implicitly adopted or overwritten.
    """
    from .durability import AcknowledgedSubmissionStore
    if not isinstance(ledger,RemoteCheckpointLedger):raise ValueError('Explicit remote ledger required')
    root=safe_path(destination)
    head=ledger.head()
    if not root.exists() and head is not None:ledger.restore(root)
    return AcknowledgedSubmissionStore(root,ledger,capacity_bytes=ledger.max_database_bytes)
