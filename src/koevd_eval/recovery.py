"""Offline restoration quarantine and independent operator checkpoint comparison.

An outside checkpoint is an operator assertion about the intended recovery cut,
not an authenticated proof of latest state. No HTTP reconciliation or approval.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re

from .eligibility import RankPolicy
from .results import canonical_hash, read_document
from .storage import StorageError, encode, token

CHECKPOINT_FORMAT = 'koevd-operator-checkpoint-v1'
GUARD_FORMAT = 'koevd-restore-guard-v1'
RELEASE_FORMAT = 'koevd-recovery-reconciliation-v1'
MAX_RECOVERIES, MAX_SUBMISSIONS, MAX_CHECKPOINT_BYTES, MAX_ROWS = 100, 10000, 8*1024**2, 1000000
KEY = re.compile(r'recovery\.(guard|release)\.([0-9]{6})')
GUARD_FIELDS = {'format','sequence','snapshot_sha256','recorded_at'}
RELEASE_FIELDS = {'format','sequence','guard_sha256','checkpoint_sha256','logical_sha256',
                  'policy_sha256','actor','statement','recorded_at','latest_state_authenticated'}
TABLE_COLUMNS = {
    'meta': ('key','value'), 'indexes': ('id','digest'),
    'artifacts': ('digest','byte_digest','data'),
    'submissions': ('id','owner','initial_artifact','state'),
    'revisions': ('submission','number','parent','artifact','data'),
    'events': ('submission','sequence','digest','data'),
    'requests': ('actor','key','fingerprint','response')}
ORDERS = {'meta':'key', 'indexes':'id', 'artifacts':'digest','submissions':'id',
          'revisions':'submission,number','events':'submission,sequence','requests':'actor,key'}


def _sha(value):
    return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None


def _time(value):
    try:
        return (isinstance(value,str) and datetime.strptime(value,'%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%dT%H:%M:%SZ')==value)
    except ValueError: return False


def now(): return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def inspect_recovery(db):
    rows=db.execute('SELECT key,value FROM meta ORDER BY key').fetchall()
    if len(rows)>1+2*MAX_RECOVERIES: raise StorageError('recovery_integrity','Recovery metadata limit exceeded',503)
    guards,releases={},{}
    for row in rows:
        key,raw=row['key'],row['value']
        if key=='version': continue
        match=KEY.fullmatch(key)
        if not match or len(raw.encode('utf-8'))>16384:
            raise StorageError('recovery_integrity','Unknown store metadata',503)
        kind,number=match[1],int(match[2])
        try: value=json.loads(raw)
        except (ValueError,TypeError): raise StorageError('recovery_integrity','Invalid recovery metadata',503) from None
        fields=GUARD_FIELDS if kind=='guard' else RELEASE_FIELDS
        if (not isinstance(value,dict) or set(value)!=fields or encode(value).decode('utf-8')!=raw
                or value['format']!=(GUARD_FORMAT if kind=='guard' else RELEASE_FORMAT)
                or type(value['sequence']) is not int or value['sequence']!=number or not _time(value['recorded_at'])):
            raise StorageError('recovery_integrity','Recovery metadata changed',503)
        if kind=='guard':
            if not _sha(value['snapshot_sha256']): raise StorageError('recovery_integrity','Restore digest missing',503)
            guards[number]=value
        else:
            if (any(not _sha(value[k]) for k in ('guard_sha256','checkpoint_sha256','logical_sha256','policy_sha256'))
                    or value['latest_state_authenticated'] is not False
                    or not isinstance(value['statement'],str) or not value['statement'].strip()
                    or len(value['statement'].encode('utf-8'))>4096):
                raise StorageError('recovery_integrity','Invalid recovery reconciliation',503)
            token(value['actor'],'local recovery actor'); releases[number]=value
    if set(guards)!=set(range(1,len(guards)+1)) or set(releases)-set(guards):
        raise StorageError('recovery_integrity','Recovery sequence changed',503)
    for number,release in releases.items():
        if release['guard_sha256']!=canonical_hash(guards[number]):
            raise StorageError('recovery_integrity','Reconciliation belongs to another restore',503)
    number=len(guards)
    return {'sequence':number,'guard':guards.get(number),'release':releases.get(number)}


def require_ready(db, *, policy_sha256=None):
    context=inspect_recovery(db)
    if context['guard'] is not None:
        release=context['release']
        if release is None:
            raise StorageError('recovery_required','Restored storage is offline until operator reconciliation.',503)
        if policy_sha256 is not None and release['policy_sha256']!=policy_sha256:
            raise StorageError('recovery_policy_changed','Restored storage requires reconciliation with the selected policy.',503)


def mark_restore(store,snapshot_sha256):
    if not _sha(snapshot_sha256): raise ValueError('Pin the restored snapshot byte digest')
    with store.connection(write=True) as db:
        number=inspect_recovery(db)['sequence']+1
        if number>MAX_RECOVERIES: raise ValueError('Recovery history limit reached')
        value={'format':GUARD_FORMAT,'sequence':number,'snapshot_sha256':snapshot_sha256,'recorded_at':now()}
        db.execute('INSERT INTO meta VALUES(?,?)',(f'recovery.guard.{number:06d}',encode(value).decode('utf-8')))
    return number


def checkpoint(db,indexes,*,registry=None,policy=None):
    from .snapshots import bindings
    from .storage import LocalSubmissionStore
    if policy is None: policy=RankPolicy()
    if not isinstance(policy,RankPolicy): raise ValueError('Typed outside operator policy required')
    inspect_recovery(db)
    outside=bindings(indexes,registry)
    if dict(db.execute('SELECT id,digest FROM indexes'))!=outside['indexes']:
        raise ValueError('Checkpoint catalog differs from database bindings')
    tables,total={},0
    for table,columns in TABLE_COLUMNS.items():
        h,count=sha256(),0
        where=" WHERE key='version'" if table=='meta' else ''
        for row in db.execute('SELECT '+','.join(columns)+' FROM '+table+where+' ORDER BY '+ORDERS[table]):
            # BLOB bytes influence the cut without copying responses into the checkpoint.
            values=[{'blob_sha256':sha256(v).hexdigest(),'bytes':len(v)} if isinstance(v,bytes) else v for v in row]
            h.update(encode(values)+b'\n'); count+=1; total+=1
            if total>MAX_ROWS: raise ValueError('Checkpoint row limit reached')
        tables[table]={'rows':count,'sha256':h.hexdigest()}
    if tables['submissions']['rows']>MAX_SUBMISSIONS: raise ValueError('Checkpoint submission limit reached')
    heads={}
    for row in db.execute('SELECT id FROM submissions ORDER BY id'):
        state,events=LocalSubmissionStore.state(db,row['id'])
        artifact=db.execute('SELECT artifact FROM revisions WHERE submission=? AND number=?',
                            (row['id'],state['head_revision'])).fetchone()[0]
        heads[row['id']]={'version':state['version'],'event_sha256':events[-1]['content_sha256'],
                         'head_revision':state['head_revision'],'artifact_sha256':artifact,
                         'workflow':state['workflow'],'publication':state['publication']}
    cut={'tables':tables,'bindings':outside,'policy_sha256':policy.sha256,'submissions':heads}
    document={'format':CHECKPOINT_FORMAT,'created_at':now(),**cut,
              'logical_sha256':canonical_hash(cut),'latest_state_authenticated':False}
    document['content_sha256']=canonical_hash(document)
    validate_checkpoint(document)
    return document


def validate_checkpoint(document,expected_sha256=None):
    fields={'format','created_at','tables','bindings','policy_sha256','submissions','logical_sha256',
            'latest_state_authenticated','content_sha256'}
    if (not isinstance(document,dict) or set(document)!=fields or document['format']!=CHECKPOINT_FORMAT
            or not _time(document['created_at']) or document['latest_state_authenticated'] is not False
            or any(not _sha(document[k]) for k in ('policy_sha256','logical_sha256','content_sha256'))
            or len(encode(document))>MAX_CHECKPOINT_BYTES): raise ValueError('Invalid bounded operator checkpoint')
    if document['content_sha256']!=canonical_hash({k:v for k,v in document.items() if k!='content_sha256'}):
        raise ValueError('Operator checkpoint content changed')
    if expected_sha256 is not None and (not _sha(expected_sha256) or document['content_sha256']!=expected_sha256):
        raise ValueError('Outside checkpoint differs from independently selected digest')
    tables=document['tables']
    if not isinstance(tables,dict) or set(tables)!=set(TABLE_COLUMNS): raise ValueError('Checkpoint tables missing')
    for value in tables.values():
        if (not isinstance(value,dict) or set(value)!={'rows','sha256'} or type(value['rows']) is not int
                or value['rows']<0 or not _sha(value['sha256'])): raise ValueError('Invalid checkpoint table')
    if sum(v['rows'] for v in tables.values())>MAX_ROWS: raise ValueError('Checkpoint row limit reached')
    outside=document['bindings']
    if not isinstance(outside,dict) or set(outside)!={'indexes','protocols'}: raise ValueError('Invalid checkpoint bindings')
    for kind,values in outside.items():
        if not isinstance(values,dict) or len(values)>1000: raise ValueError('Invalid checkpoint bindings')
        for name in values:
            if kind=='indexes': token(name,'index ID')
            elif not isinstance(name,str) or not 0<len(name)<=128: raise ValueError('Invalid protocol ID')
        if any(not _sha(v) for v in values.values()): raise ValueError('Invalid checkpoint binding digest')
    if not 1<=len(outside['indexes'])<=8: raise ValueError('Checkpoint index limit')
    heads=document['submissions']
    if (not isinstance(heads,dict) or len(heads)>MAX_SUBMISSIONS or len(heads)!=tables['submissions']['rows']):
        raise ValueError('Checkpoint submission count differs')
    for name,value in heads.items():
        token(name,'checkpoint submission')
        if (not isinstance(value,dict) or set(value)!={'version','event_sha256','head_revision','artifact_sha256','workflow','publication'}
                or type(value['version']) is not int or not 1<=value['version']<=1000
                or type(value['head_revision']) is not int or not 1<=value['head_revision']<=100
                or not _sha(value['event_sha256']) or not _sha(value['artifact_sha256'])
                or not isinstance(value['workflow'],str) or len(value['workflow'])>32
                or not isinstance(value['publication'],dict) or set(value['publication'])!={'status','revision','scope'}):
            raise ValueError('Invalid checkpoint submission head')
    cut={k:document[k] for k in ('tables','bindings','policy_sha256','submissions')}
    if canonical_hash(cut)!=document['logical_sha256']: raise ValueError('Checkpoint logical cut changed')
    return document


def compare(current,expected):
    validate_checkpoint(current); validate_checkpoint(expected)
    a,b=current['submissions'],expected['submissions']
    return {'matches':current['logical_sha256']==expected['logical_sha256'],
            'missing_submissions':sorted(set(b)-set(a)), 'extra_submissions':sorted(set(a)-set(b)),
            'changed_submissions':sorted(k for k in set(a)&set(b) if a[k]!=b[k]),
            'changed_tables':sorted(k for k in TABLE_COLUMNS if current['tables'][k]!=expected['tables'][k]),
            'bindings_match':current['bindings']==expected['bindings'],
            'policy_matches':current['policy_sha256']==expected['policy_sha256'],
            'latest_state_authenticated':False}


def reconcile(store,expected,expected_sha256,indexes,*,actor,administrators,statement,registry=None,policy=None):
    token(actor,'local recovery actor')
    if actor not in administrators: raise StorageError('admin_required','Independent local administrator required',403)
    if not isinstance(statement,str) or not statement.strip() or len(statement.encode('utf-8'))>4096:
        raise ValueError('Describe the actual outside recovery checkpoint and reviewed scope')
    validate_checkpoint(expected,expected_sha256)
    with store.connection(write=True) as db:
        context=inspect_recovery(db)
        if context['guard'] is None: raise ValueError('This is not a quarantined restoration')
        actual=checkpoint(db,indexes,registry=registry,policy=policy)
        report=compare(actual,expected)
        if not report['matches']: raise StorageError('recovery_mismatch','Restored data differs from the outside checkpoint; recover missing changes before release.',409)
        value={'format':RELEASE_FORMAT,'sequence':context['sequence'],'guard_sha256':canonical_hash(context['guard']),
               'checkpoint_sha256':expected_sha256,'logical_sha256':actual['logical_sha256'],'policy_sha256':actual['policy_sha256'],
               'actor':actor,'statement':statement,'recorded_at':now(),'latest_state_authenticated':False}
        prior=context['release']
        if prior is not None:
            if any(prior[k]!=value[k] for k in value if k!='recorded_at'):
                raise StorageError('recovery_release_conflict','Restore already has a different reconciliation',409)
            return prior
        db.execute('INSERT INTO meta VALUES(?,?)',(f"recovery.release.{context['sequence']:06d}",encode(value).decode('utf-8')))
    return value


def main():
    import argparse,sys
    from .common import configure_cli_stdio
    from .policy_decisions import configured_policy
    from .protocols import ProtocolRegistry
    from .space_service import InputCatalog
    from .storage import LocalSubmissionStore
    configure_cli_stdio()
    p=argparse.ArgumentParser(description='Offline operator recovery: checkpoint/compare/reconcile; no HTTP or automatic latest-state proof')
    for name in ('store-dir','catalog','roles-file','actor'): p.add_argument('--'+name,required=True)
    p.add_argument('--protocol-registry'); p.add_argument('--policy-root'); p.add_argument('--policy-head-sha256')
    p.add_argument('--demo',action='store_true')
    commands=p.add_subparsers(dest='command',required=True)
    commands.add_parser('status')
    cp=commands.add_parser('checkpoint'); cp.add_argument('--output',required=True)
    for name in ('compare','reconcile'):
        sub=commands.add_parser(name); sub.add_argument('--current-checkpoint',required=True); sub.add_argument('--checkpoint-sha256',required=True)
        if name=='reconcile': sub.add_argument('--statement',required=True)
    args=p.parse_args()
    try:
        from .snapshots import safe_path,fsync_dir
        roles=read_document(args.roles_file,max_bytes=1024*1024)
        if (set(roles)!={'reviewers','admins'} or any(not isinstance(v,list) or len(v)>1000
                or any(not isinstance(s,str) for s in v) for v in roles.values())): raise ValueError('Invalid independent roles')
        token(args.actor,'local recovery actor')
        if args.actor not in roles['admins']: raise StorageError('admin_required','Independent local administrator required',403)
        root=safe_path(args.store_dir)
        if not (root/'submissions.sqlite3').is_file(): raise ValueError('Existing operator store required')
        catalog=InputCatalog(args.catalog,allow_synthetic=args.demo)
        indexes={k:v['index'] for k,v in catalog.indexes.items()}
        registry=ProtocolRegistry(args.protocol_registry) if args.protocol_registry else None
        policy=configured_policy(args.policy_root,args.policy_head_sha256)
        store=LocalSubmissionStore(root)
        if args.command=='status':
            with store.connection() as db:
                context=inspect_recovery(db)
            result={'sequence':context['sequence'],'reconciliation_required':context['guard'] is not None and context['release'] is None,
                    'selected_policy_matches':context['release'] is None or context['release']['policy_sha256']==policy.sha256,
                    'latest_state_authenticated':False}
        else:
            with store.connection() as db: actual=checkpoint(db,indexes,registry=registry,policy=policy)
            if args.command=='checkpoint':
                path=safe_path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
                fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
                with os.fdopen(fd,'wb') as stream:
                    stream.write(encode(actual)+b'\n'); stream.flush(); os.fsync(stream.fileno())
                fsync_dir(path.parent)
                result={'checkpoint_sha256':actual['content_sha256'],'logical_sha256':actual['logical_sha256'],'submissions':len(actual['submissions'])}
            else:
                expected=read_document(args.current_checkpoint,max_bytes=MAX_CHECKPOINT_BYTES)
                validate_checkpoint(expected,args.checkpoint_sha256)
                if args.command=='compare': result=compare(actual,expected)
                else: result=reconcile(store,expected,args.checkpoint_sha256,indexes,actor=args.actor,administrators=roles['admins'],
                                       statement=args.statement,registry=registry,policy=policy)
        print(json.dumps({'execution_scope':'operator_offline_recovery','result':result,'published':False,'human_approval_authenticated':False},ensure_ascii=False))
    except (ValueError,StorageError,OSError) as exc:
        print(json.dumps({'error':getattr(exc,'code','recovery_failed'),'message':str(exc)},ensure_ascii=False),file=sys.stderr)
        raise SystemExit(2)


if __name__=='__main__': main()
