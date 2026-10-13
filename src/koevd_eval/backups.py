"""Private periodic snapshot/checkpoint pairs and honest backup-lag observation.

Local completion is not cloud durability. Periodic copies are not synchronous
commit/RPO guarantees. No recovery release, publication, bucket creation or GC.
"""
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import tempfile
import time
import uuid

from .policy_decisions import configured_policy
from .recovery import checkpoint, compare, validate_checkpoint
from .results import canonical_hash, read_document
from .snapshots import (HFBucketSnapshots, create_snapshot, unpack_verified,
                        readonly_db, safe_path, file_digest, fsync_dir, bindings)
from .storage import LocalSubmissionStore, StorageError, encode, token

FORMAT = 'koevd-backup-attempt-v1'
COMPLETE = 'koevd-backup-completion-v1'
MAX_ATTEMPTS = 1000
ATTEMPT_NAME = re.compile(r'attempt-([0-9]{6})-([0-9a-f]{32})')


def atomic_json(path, value):
    """Publish a complete addressed operator record, preserving prior files."""
    path=safe_path(path); pending=path.with_name('.'+uuid.uuid4().hex+'.pending')
    linked=False
    try:
        fd=os.open(pending,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as stream:
            stream.write(encode(value)+b'\n'); stream.flush(); os.fsync(stream.fileno())
        os.link(pending,path); linked=True; fsync_dir(path.parent)
    except BaseException:
        if linked: path.unlink()  # Only this newly published record, never an existing one.
        raise
    finally:
        if pending.exists(): pending.unlink()


def derive_checkpoint(snapshot, digest, indexes, *, registry=None):
    """Derive the checkpoint from the FROZEN backup, never from a later live DB."""
    with tempfile.TemporaryDirectory(prefix='koevd-backup-cut-') as temporary:
        stage=Path(temporary)
        manifest=unpack_verified(snapshot,digest,stage,indexes,registry)
        head=manifest['policy_head_sha256']
        policy=configured_policy(stage/'policy',head) if head else configured_policy()
        with readonly_db(stage/'submissions.sqlite3') as db:
            result=checkpoint(db,indexes,registry=registry,policy=policy)
        # Deterministic derivation also works after downloading the single ZIP.
        result['created_at']=manifest['created_at']
        result['content_sha256']=canonical_hash({k:v for k,v in result.items() if k!='content_sha256'})
        validate_checkpoint(result)
        return result


class BackupManager:
    def __init__(self,store,indexes,root,*,actor,registry=None,policy_root=None,policy_head=None,
                 transport=None,max_bytes=8*1024**3,clock=None):
        if not isinstance(store,LocalSubmissionStore): raise ValueError('Existing local submission store required')
        token(actor,'local backup administrator')
        if type(max_bytes) is not int or max_bytes<65536: raise ValueError('Invalid retained backup quota')
        if transport is not None and not isinstance(transport,HFBucketSnapshots): raise ValueError('Expected private HF Bucket adapter')
        if bool(policy_root)!=bool(policy_head): raise ValueError('Pin policy root and selected head together')
        self.store,self.indexes,self.root=store,deepcopy(indexes),safe_path(root)
        if self.root.is_relative_to(store.root) or (policy_root and self.root.is_relative_to(safe_path(policy_root))):
            raise ValueError('Backups require a separate dedicated directory')
        bindings(self.indexes,registry); configured_policy(policy_root,policy_head)
        self.root.mkdir(parents=True,exist_ok=True)
        if os.name!='nt': os.chmod(self.root,0o700)
        self.actor,self.registry,self.policy_root,self.policy_head=actor,registry,policy_root,policy_head
        self.transport,self.max_bytes=transport,max_bytes
        self.clock=clock or (lambda:datetime.now(timezone.utc))
        self.target={'kind':'hf_private_bucket','bucket_id':transport.bucket_id} if transport else {'kind':'local_only'}

    def timestamp(self):
        value=self.clock()
        if not isinstance(value,datetime) or value.tzinfo is None: raise ValueError('Use an aware UTC clock')
        return value.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    @contextmanager
    def worker_lock(self):
        lock=safe_path(self.root/'.worker-lock')
        fd=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'wb') as stream:
            stream.write(encode({'pid':os.getpid(),'actor':self.actor})+b'\n');stream.flush();os.fsync(stream.fileno())
        try: yield
        finally: lock.unlink()

    def attempts(self):
        result=[]
        for path in self.root.iterdir():
            safe_path(path)
            if path.name=='.worker-lock':continue
            match=ATTEMPT_NAME.fullmatch(path.name)
            if not match or not path.is_dir():raise ValueError('Unexpected backup directory entry')
            result.append((int(match[1]),path))
        result.sort()
        if len(result)>MAX_ATTEMPTS or len({n for n,p in result})!=len(result):raise ValueError('Backup sequence/attempt limit')
        return result

    def retained_bytes(self):
        total,files=0,0
        for path in self.root.rglob('*'):
            safe_path(path)
            if path.is_file():
                total+=path.stat().st_size;files+=1
                if files>100000:raise ValueError('Backup file inspection limit')
        return total

    def _cycle(self):
        attempts=self.attempts()
        if len(attempts)>=MAX_ATTEMPTS: raise ValueError('Backup attempt history full; operator retention required')
        number=(attempts[-1][0]+1) if attempts else 1
        path=self.root/(f'attempt-{number:06d}-'+uuid.uuid4().hex);path.mkdir(mode=0o700)
        attempt={'format':FORMAT,'sequence':number,'actor':self.actor,'started_at':self.timestamp(),'target':self.target}
        atomic_json(path/'attempt.json',attempt)
        try:
            # This is a conservative retained-file reservation, not a quota for
            # SQLite journals or temporary extraction on the working filesystem.
            reserve=self.store.path.stat().st_size+16*1024**2
            if self.retained_bytes()+reserve>self.max_bytes:raise StorageError('backup_capacity','Retained backup quota reached',507)
            saved=create_snapshot(self.store,self.indexes,path/'snapshot.zip',registry=self.registry,
                                  policy_root=self.policy_root,policy_head=self.policy_head)
            cp=derive_checkpoint(path/'snapshot.zip',saved['sha256'],self.indexes,registry=self.registry)
            atomic_json(path/'checkpoint.json',cp)
            if self.retained_bytes()>self.max_bytes:raise StorageError('backup_capacity','Retained backup quota reached',507)
            remote=None
            if self.transport is not None:
                remote=self.transport.put(path/'snapshot.zip',saved['sha256'])
                if (not isinstance(remote,dict) or remote.get('sha256')!=saved['sha256']
                        or remote.get('readback_verified') is not True):raise ValueError('Remote readback not verified')
            receipt={'format':COMPLETE,'sequence':number,'target':self.target,'started_at':attempt['started_at'],
                     'completed_at':self.timestamp(),'snapshot_sha256':saved['sha256'],'snapshot_bytes':saved['bytes'],
                     'checkpoint_sha256':cp['content_sha256'],'checkpoint_byte_sha256':file_digest(path/'checkpoint.json'),
                     'logical_sha256':cp['logical_sha256'],'remote_readback_verified':remote is not None,
                     'latest_state_authenticated':False,'rpo_guaranteed_seconds':None}
            atomic_json(path/'COMPLETED.json',receipt)
            return {'sequence':number,'success':True,'target':self.target,'snapshot_sha256':saved['sha256'],
                    'checkpoint_sha256':cp['content_sha256'],'remote_readback_verified':remote is not None}
        except Exception as exc:
            # Preserve partial files and older successes. Never serialize remote
            # exception strings (URLs/tokens) or private model text into failure logs.
            failure={'format':'koevd-backup-failure-v1','sequence':number,'failed_at':self.timestamp(),
                     'error_code':getattr(exc,'code','backup_failed'),'completed':False}
            atomic_json(path/'FAILURE.json',failure)
            return {'sequence':number,'success':False,'error_code':failure['error_code'],'target':self.target}

    def cycle(self):
        with self.worker_lock():return self._cycle()

    def _verified_pair(self,number,path):
        attempt=read_document(path/'attempt.json',max_bytes=4096)
        receipt=read_document(path/'COMPLETED.json',max_bytes=8192)
        fields={'format','sequence','target','started_at','completed_at','snapshot_sha256','snapshot_bytes',
                'checkpoint_sha256','checkpoint_byte_sha256','logical_sha256','remote_readback_verified',
                'latest_state_authenticated','rpo_guaranteed_seconds'}
        target=receipt.get('target')
        if not isinstance(target,dict) or target.get('kind') not in ('local_only','hf_private_bucket'):
            raise ValueError('Invalid backup target')
        if ((target['kind']=='local_only' and set(target)!={'kind'}) or
                (target['kind']=='hf_private_bucket' and (set(target)!={'kind','bucket_id'} or
                 not isinstance(target['bucket_id'],str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*/[A-Za-z0-9][A-Za-z0-9._-]*',target['bucket_id'])))):
            raise ValueError('Invalid backup target')
        if (set(receipt)!=fields or receipt['format']!=COMPLETE or type(receipt['sequence']) is not int or receipt['sequence']!=number
                or attempt.get('format')!=FORMAT or attempt.get('sequence')!=number
                or receipt['target']!=attempt.get('target') or receipt['started_at']!=attempt.get('started_at')
                or receipt['latest_state_authenticated'] is not False or receipt['rpo_guaranteed_seconds'] is not None
                or type(receipt['remote_readback_verified']) is not bool
                or receipt['remote_readback_verified']!=(receipt['target'].get('kind')=='hf_private_bucket')):
            raise ValueError('Backup completion receipt changed')
        if ((path/'snapshot.zip').stat().st_size!=receipt['snapshot_bytes']
                or file_digest(path/'snapshot.zip')!=receipt['snapshot_sha256']
                or file_digest(path/'checkpoint.json')!=receipt['checkpoint_byte_sha256']):raise ValueError('Backup pair bytes changed')
        cp=read_document(path/'checkpoint.json',max_bytes=8*1024**2)
        validate_checkpoint(cp,receipt['checkpoint_sha256'])
        derived=derive_checkpoint(path/'snapshot.zip',receipt['snapshot_sha256'],self.indexes,registry=self.registry)
        if cp!=derived or cp['logical_sha256']!=receipt['logical_sha256']:raise ValueError('Checkpoint does not describe the frozen snapshot')
        return receipt,cp

    def status(self):
        attempts=self.attempts(); successes=[];failed=[];pending=[]
        for number,path in attempts:
            if (path/'FAILURE.json').exists():failed.append(number)
            elif (path/'COMPLETED.json').exists():
                receipt=read_document(path/'COMPLETED.json',max_bytes=8192)
                attempt=read_document(path/'attempt.json',max_bytes=4096)
                if (receipt.get('format')!=COMPLETE or receipt.get('sequence')!=number
                        or receipt.get('target')!=attempt.get('target')):raise ValueError('Backup completion target/sequence changed')
                if receipt.get('target')==self.target:successes.append((number,path))
            else:pending.append(number)
        result={'configured_target':self.target,'attempts':len(attempts),'failed_attempts':failed,'incomplete_attempts':pending,
                'last_verified_sequence':None,'changes_pending':None,'events_since_verified_backup':None,
                'seconds_since_backup_started':None,'clock_valid':None,'remote_readback_verified':False,
                'rpo_guaranteed_seconds':None,'latest_state_authenticated':False,'observed_at':self.timestamp(),
                'retained_bytes':self.retained_bytes(),'retained_quota_bytes':self.max_bytes}
        if not successes:return result
        number,path=successes[-1]
        # Tamper/corruption of the selected success fails closed; do not silently
        # claim an earlier copy is the latest verified state.
        receipt,cp=self._verified_pair(number,path)
        with self.store.connection() as db:
            live=checkpoint(db,self.indexes,registry=self.registry,
                            policy=configured_policy(self.policy_root,self.policy_head))
        difference=compare(live,cp)
        age=(datetime.strptime(result['observed_at'],'%Y-%m-%dT%H:%M:%SZ')-
             datetime.strptime(receipt['started_at'],'%Y-%m-%dT%H:%M:%SZ')).total_seconds()
        delta=live['tables']['events']['rows']-cp['tables']['events']['rows']
        regression=bool(difference['missing_submissions']) or any(live['tables'][k]['rows']<v['rows'] for k,v in cp['tables'].items()) or any(
            live['submissions'][k]['version']<v['version'] for k,v in cp['submissions'].items() if k in live['submissions'])
        result.update(last_verified_sequence=number,changes_pending=not difference['matches'],comparison=difference,
                      events_since_verified_backup=None if regression else delta,
                      state_regressed=regression,seconds_since_backup_started=age if age>=0 else None,
                      clock_valid=age>=0,remote_readback_verified=receipt['remote_readback_verified'],
                      checkpoint_sha256=cp['content_sha256'],snapshot_sha256=receipt['snapshot_sha256'])
        if (path/'FAILURE.json').exists() or not (path/'COMPLETED.json').is_file():
            raise StorageError('backup_state_changed','Backup publication changed during observation; retry status',503)
        return result

    def run(self,*,interval_seconds=300,cycles=1,wait=time.sleep,emit=lambda value:None,before_final_cycle=None):
        if type(interval_seconds) not in (int,float) or not 1<=interval_seconds<=86400:raise ValueError('Use backup interval1–86400 seconds')
        if type(cycles) is not int or cycles<0 or cycles>MAX_ATTEMPTS:raise ValueError('Invalid cycle count;0 explicitly runs until interrupted')
        if before_final_cycle is not None and (not callable(before_final_cycle) or cycles==0):
            raise ValueError('Final-cycle coordination requires a finite run and a callable gate')
        count,failures=0,0
        with self.worker_lock():
            while cycles==0 or count<cycles:
                if before_final_cycle is not None and count==cycles-1:
                    before_final_cycle()  # No capture starts before server shutdown is confirmed.
                result=self._cycle();emit(result);count+=1;failures+=not result['success']
                if cycles and count>=cycles:break
                remaining=interval_seconds
                while remaining>0:
                    step=min(1,remaining);wait(step);remaining-=step
        return {'cycles':count,'failures':failures,'rpo_guaranteed_seconds':None}


def await_final_snapshot_release():
    """Private launcher pipe protocol; EOF/invalid release never permits capture."""
    import json,sys
    print(json.dumps({'execution_scope':'operator_private_backup','event':'awaiting_final_snapshot_release'}),flush=True)
    if sys.stdin.readline(64) != 'FINAL_SNAPSHOT\n':
        raise ValueError('Final snapshot release missing or invalid; server shutdown is not confirmed')


def main():
    import argparse,json,sys
    from .common import configure_cli_stdio
    from .space_service import InputCatalog
    from .protocols import ProtocolRegistry
    configure_cli_stdio()
    p=argparse.ArgumentParser(description='Private snapshot/checkpoint backup worker; no synchronous remote commit/RPO guarantee')
    for name in ('store-dir','backup-root','catalog','roles-file','actor'):p.add_argument('--'+name,required=True)
    p.add_argument('--protocol-registry');p.add_argument('--policy-root');p.add_argument('--policy-head-sha256')
    p.add_argument('--bucket');p.add_argument('--enable-remote-backup',action='store_true',help='Explicitly authorize this configured existing private target')
    p.add_argument('--retained-quota-bytes',type=int,default=8*1024**3);p.add_argument('--demo',action='store_true')
    sub=p.add_subparsers(dest='command',required=True);sub.add_parser('status')
    run=sub.add_parser('run');run.add_argument('--interval-seconds',type=float,default=300);run.add_argument('--cycles',type=int,default=1)
    run.add_argument('--await-final-snapshot-release',action='store_true',help='Launcher pipe only: wait for server shutdown before the final finite capture')
    args=p.parse_args()
    try:
        if args.command=='run' and args.await_final_snapshot_release and args.cycles<=0:
            raise ValueError('Final snapshot coordination requires finite positive cycles')
        roles=read_document(args.roles_file,max_bytes=1024*1024)
        if (set(roles)!={'reviewers','admins'} or any(not isinstance(v,list) or len(v)>1000 or any(not isinstance(s,str) for s in v) for v in roles.values())):
            raise ValueError('Invalid independent operator roles')
        token(args.actor,'local backup administrator')
        if args.actor not in roles['admins']:raise StorageError('admin_required','Independent local administrator required',403)
        if bool(args.bucket)!=args.enable_remote_backup:raise ValueError('Remote backup requires both an existing bucket and explicit enable flag')
        root=safe_path(args.store_dir)
        if not (root/'submissions.sqlite3').is_file():raise ValueError('Existing source store required')
        catalog=InputCatalog(args.catalog,allow_synthetic=args.demo)
        manager=BackupManager(LocalSubmissionStore(root),{k:v['index'] for k,v in catalog.indexes.items()},args.backup_root,
                              actor=args.actor,registry=ProtocolRegistry(args.protocol_registry) if args.protocol_registry else None,
                              policy_root=args.policy_root,policy_head=args.policy_head_sha256,
                              transport=HFBucketSnapshots(args.bucket) if args.bucket else None,max_bytes=args.retained_quota_bytes)
        if args.command=='status':result=manager.status()
        else:
            result=manager.run(interval_seconds=args.interval_seconds,cycles=args.cycles,
                before_final_cycle=await_final_snapshot_release if args.await_final_snapshot_release else None,
                emit=lambda value:print(json.dumps({'execution_scope':'operator_private_backup','cycle':value}),flush=True))
        print(json.dumps({'execution_scope':'operator_private_backup','result':result,'published':False}))
        if args.command=='run' and result['failures']:raise SystemExit(2)
    except (ValueError,StorageError,OSError) as exc:
        print(json.dumps({'error':getattr(exc,'code','backup_failed'),'message':str(exc)}),file=sys.stderr)
        raise SystemExit(2)
    except KeyboardInterrupt:
        print(json.dumps({'stopped':True,'reason':'operator_interrupt','published':False}),file=sys.stderr)
        raise SystemExit(130)


if __name__=='__main__':main()
