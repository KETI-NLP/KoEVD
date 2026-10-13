"""Private CPU upload/analysis service. No registration or model authentication."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from hashlib import sha256
import json
from pathlib import Path
import secrets
import shutil
import threading
import time
import uuid

from .diagnostics import analyze_many, write_analysis
from .protocols import ProtocolRegistry
from .results import MAX_BYTES, _keys, read_document, validate_index, validate_results


class ServiceError(Exception):
    def __init__(self, code, message, status=400):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)


def digest(path):
    h=sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def _id(value):
    return isinstance(value,str) and 0<len(value)<=128 and all(c.isascii() and (c.isalnum() or c in '_-') for c in value)


class InputCatalog:
    """Loaded only from an operator-selected file, never from an HTTP upload."""
    def __init__(self, config_path, *, allow_synthetic=False, public_reference_disclosure=False):
        config_path=Path(config_path).resolve()
        config=read_document(config_path,max_bytes=1024*1024)
        _keys(config,('schema_version','indexes','baselines'),'Space catalog')
        if config['schema_version']!='koevd-space-catalog-v1':raise ValueError('Unsupported space catalog')
        if not isinstance(config['indexes'],list) or not 1<=len(config['indexes'])<=8:raise ValueError('Catalog needs 1–8 trusted indexes')
        if not isinstance(config['baselines'],list) or len(config['baselines'])>8:raise ValueError('Too many baseline entries')
        self.indexes={};self.by_hash={};self.baselines={};self.synthetic=allow_synthetic
        if type(public_reference_disclosure) is not bool:raise ValueError('Disclosure flag must be boolean')
        self.public_reference_disclosure=public_reference_disclosure
        def local_path(value):
            if not isinstance(value,str) or not value:raise ValueError('Operator path required')
            p=Path(value)
            p=(config_path.parent/p).resolve() if not p.is_absolute() else p.resolve()
            if not p.is_file():raise ValueError('Operator catalog file missing')
            return p
        for entry in config['indexes']:
            _keys(entry,('id','label','mode','path','sha256'),'Trusted catalog index',optional=('registry','protocol_id'))
            if not _id(entry['id']) or entry['id'] in self.indexes:raise ValueError('Invalid/duplicate catalog ID')
            if not isinstance(entry['label'],str) or not entry['label'] or len(entry['label'])>256:raise ValueError('Invalid catalog label')
            p=local_path(entry['path'])
            if digest(p)!=entry['sha256']:raise ValueError('Operator index file checksum mismatch')
            index=read_document(p);validate_index(index)
            if entry['mode']=='standard':
                if set(entry)-{'id','label','mode','path','sha256'}!={'registry','protocol_id'}:raise ValueError('Standard catalog needs registry and protocol ID')
                registry=Path(entry['registry']);registry=(config_path.parent/registry).resolve() if not registry.is_absolute() else registry.resolve()
                ProtocolRegistry(registry).validate_index(entry['protocol_id'],index)
            elif entry['mode']=='synthetic_demo':
                if not allow_synthetic or index['protocol'].get('kind')=='standard':raise ValueError('Synthetic index needs explicit demo mode and nonstandard protocol')
            elif entry['mode']=='operator_custom':
                if index['protocol'].get('kind')=='standard':raise ValueError('A standard index must pass registered validation')
            else:raise ValueError('Unknown catalog mode')
            if index['content_sha256'] in self.by_hash:raise ValueError('Duplicate trusted input hash')
            item={'id':entry['id'],'label':entry['label'],'mode':entry['mode'],'index':index}
            self.indexes[entry['id']]=item;self.by_hash[index['content_sha256']]=item
        for entry in config['baselines']:
            _keys(entry,('id','label','index_id','path','sha256','scope','publication_evidence'),'Baseline')
            if not _id(entry['id']) or entry['id'] in self.baselines or entry['index_id'] not in self.indexes:raise ValueError('Invalid baseline catalog ID')
            if not isinstance(entry['label'],str) or not entry['label'] or len(entry['label'])>256:raise ValueError('Invalid baseline label')
            if entry['scope']=='synthetic_demo':
                if not allow_synthetic or self.indexes[entry['index_id']]['mode']!='synthetic_demo' or entry['publication_evidence'] is not None:raise ValueError('Synthetic baseline only in explicit demo mode')
            elif entry['scope']=='actual_target_outputs':
                if self.indexes[entry['index_id']]['mode']=='synthetic_demo':raise ValueError('Synthetic reference cannot assert actual target outputs')
                # Operator attestation is distinct from GPU/model authenticity verification.
                e=entry['publication_evidence']
                _keys(e,('consent','rights','evidence_path','evidence_sha256'),'Raw publication evidence')
                if e['consent']!='operator_confirmed_raw_publication' or not isinstance(e['rights'],str) or not e['rights'].strip():raise ValueError('Raw baseline publication rights required')
                if digest(local_path(e['evidence_path']))!=e['evidence_sha256']:raise ValueError('Publication evidence hash mismatch')
            else:raise ValueError('Baseline must identify actual outputs or explicit synthetic demo')
            p=local_path(entry['path'])
            if digest(p)!=entry['sha256']:raise ValueError('Baseline file checksum mismatch')
            d=read_document(p);validate_results(d,self.indexes[entry['index_id']]['index'])
            self.baselines[entry['id']]={**entry,'path':p,'model':d['run']['model']['id'],'artifact_sha256':d['content_sha256']}

    def resolve(self, document):
        item=self.by_hash.get(document.get('input_index_sha256'))
        if item is None:raise ServiceError('unknown_inputs','No server-configured trusted input set matches this result.',422)
        return item

    def public(self):
        return {'indexes':[{'id':v['id'],'label':v['label'],'mode':v['mode'],'expected_records':sum(len(e) for e in v['index']['inputs'].values())} for v in self.indexes.values()],
                'baselines':[{k:v[k] for k in ('id','label','model','scope','index_id')} for v in self.baselines.values()],
                'synthetic_demo_enabled':self.synthetic,'public_registration_enabled':False,'official_rank_eligible':False,
                'reference_disclosure': 'koevd-public-reference-disclosure-v1' if self.public_reference_disclosure else None}


@dataclass(frozen=True)
class Limits:
    upload_bytes:int=MAX_BYTES
    session_upload_bytes:int=256*1024*1024
    global_bytes:int=2*1024*1024*1024
    report_bytes:int=512*1024*1024
    max_uploads:int=4
    max_sessions:int=32
    ttl_seconds:int=7200
    max_jobs:int=2
    bootstrap_resamples:int=100
    bootstrap_seed:int=1729


@dataclass
class Session:
    directory:Path
    csrf:str
    expires:float
    uploads:dict=field(default_factory=dict)
    jobs:dict=field(default_factory=dict)
    report:dict|None=None
    busy:bool=False


class AnalysisService:
    """Single-process bounded ephemeral store; separate M6 persistence is required."""
    FILES={'html':'report-v2.html','profile':'profile-v2.json','cases':'cases-v2.jsonl','csv':'metrics-v2.csv','markdown':'report-v2.md'}
    def __init__(self,catalog,root,*,limits=None,clock=time.monotonic):
        self.catalog=catalog;self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True)
        if any(self.root.iterdir()):raise ValueError('Session storage must be a new/empty operator directory')
        self.limits=limits or Limits();self.clock=clock;self.lock=threading.RLock();self.sessions={};self.reserved=0;self.closed=False
        if not (0<self.limits.upload_bytes<=MAX_BYTES and self.limits.max_uploads<=8 and self.limits.max_sessions>=1 and self.limits.ttl_seconds>0 and 0<=self.limits.bootstrap_resamples<=500):raise ValueError('Invalid service limits')
        self.executor=ThreadPoolExecutor(max_workers=1,thread_name_prefix='koevd-analysis')
        self.job_slots=threading.BoundedSemaphore(self.limits.max_jobs)

    def _remove(self,path):
        path=Path(path).resolve()
        if not path.is_relative_to(self.root) or path==self.root:raise RuntimeError('Refusing cleanup outside owned service root')
        if path.is_dir():shutil.rmtree(path)
        elif path.exists():path.unlink()

    def _size(self):
        return sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file())

    def _lookup(self,token,csrf=None):
        if not isinstance(token,str) or len(token)>256:raise ServiceError('session_required','Create a private session first.',401)
        session=self.sessions.get(sha256(token.encode()).hexdigest())
        if session is None or session.expires<=self.clock():raise ServiceError('session_expired','Session is missing or expired. Create a new one.',401)
        if csrf is not None and (not isinstance(csrf,str) or not secrets.compare_digest(csrf,session.csrf)):raise ServiceError('csrf_rejected','Session request token mismatch.',403)
        return session

    def cleanup(self):
        with self.lock:
            for key,s in list(self.sessions.items()):
                if s.expires<=self.clock() and not s.busy:
                    self._remove(s.directory);del self.sessions[key]

    def create_session(self):
        with self.lock:
            self.cleanup()
            if self.closed:raise ServiceError('closed','Service is closed.',503)
            if len(self.sessions)>=self.limits.max_sessions:raise ServiceError('session_capacity','Session capacity reached. Try later.',429)
            token=secrets.token_urlsafe(32);directory=self.root/uuid.uuid4().hex;directory.mkdir()
            s=Session(directory,secrets.token_urlsafe(32),self.clock()+self.limits.ttl_seconds)
            self.sessions[sha256(token.encode()).hexdigest()]=s
            return token,{'csrf_token':s.csrf,'expires_in_seconds':self.limits.ttl_seconds,'uploads':[],'report':None}

    def _invalidate(self,s):
        if s.report:self._remove(s.report['directory']);s.report=None

    def describe(self,token):
        with self.lock:
            s=self._lookup(token)
            return {'csrf_token':s.csrf,'expires_in_seconds':max(0,int(s.expires-self.clock())),
                    'uploads':[{k:v for k,v in entry.items() if k!='path'} for entry in s.uploads.values()],
                    'busy':s.busy,'jobs':[dict(v) for v in s.jobs.values()],
                    'report':None if s.report is None else {'job_id':s.report['job_id'],'files':list(self.FILES)},'publication':'private_ephemeral_session'}

    def delete_session(self,token,csrf):
        with self.lock:
            s=self._lookup(token,csrf)
            if s.busy:raise ServiceError('session_busy','Wait for the active upload or analysis before deleting.',409)
            self._remove(s.directory);del self.sessions[sha256(token.encode()).hexdigest()]

    def begin_upload(self,token,csrf):
        with self.lock:
            self.cleanup();s=self._lookup(token,csrf)
            if s.busy:raise ServiceError('session_busy','Another upload or analysis is active.',409)
            if len(s.uploads)>=self.limits.max_uploads:raise ServiceError('upload_capacity','Session upload count limit reached.',413)
            if sum(e['bytes'] for e in s.uploads.values())+self.limits.upload_bytes>self.limits.session_upload_bytes:raise ServiceError('session_quota','Session upload byte capacity reached.',413)
            if self._size()+self.reserved+self.limits.upload_bytes>self.limits.global_bytes:raise ServiceError('storage_capacity','Temporary storage capacity reached.',503)
            s.busy=True;self.reserved+=self.limits.upload_bytes
            return s,s.directory/(uuid.uuid4().hex+'.upload')

    def abort_upload(self,s,path):
        with self.lock:
            self._remove(path);s.busy=False;self.reserved-=self.limits.upload_bytes;self.cleanup()

    def finish_upload(self,token,s,path):
        try:
            if path.stat().st_size>self.limits.upload_bytes:raise ServiceError('upload_size','Result exceeds the upload limit.',413)
            document=read_document(path,max_bytes=self.limits.upload_bytes)
            item=self.catalog.resolve(document);validate_results(document,item['index'])
            with self.lock:
                if self._lookup(token) is not s:raise ServiceError('session_expired','Session expired during upload.',401)
                if any(e['artifact_sha256']==document['content_sha256'] for e in s.uploads.values()):raise ServiceError('duplicate_artifact','This exact result is already uploaded.',409)
                upload_id=uuid.uuid4().hex;new_path=s.directory/(upload_id+'.json');path.replace(new_path)
                entry={'id':upload_id,'path':new_path,'model':document['run']['model']['id'],'run_id':document['run']['id'],
                       'artifact_sha256':document['content_sha256'],'index_id':item['id'],'scope':item['mode'],'records':len(document['records']),'bytes':new_path.stat().st_size,'file_sha256':digest(new_path),'verification':'structurally_validated_user_reported','publication':'private_ephemeral_session'}
                self._invalidate(s);s.uploads[upload_id]=entry
                return {k:v for k,v in entry.items() if k!='path'}
        except ServiceError:raise
        except (ValueError,TypeError,KeyError,RecursionError):raise ServiceError('invalid_result','Invalid result contract, checksum or trusted input binding.',422) from None
        finally:self.abort_upload(s,path)

    def submission_source(self,token,csrf,upload_id):
        """Copy a session-owned original for an explicit authenticated submission.

        The server resolves the index; the browser supplies no gold, score, path
        or identity. Hold the short read against session deletion/file replacement.
        """
        if not _id(upload_id):raise ServiceError('upload_id','Select a valid private upload ID.')
        with self.lock:
            s=self._lookup(token,csrf)
            if s.busy:raise ServiceError('session_busy','Wait for active work before creating a submission.',409)
            entry=s.uploads.get(upload_id)
            if entry is None:raise ServiceError('not_found','Session upload not found.',404)
            if digest(entry['path'])!=entry['file_sha256']:raise ServiceError('artifact_changed','Stored session result changed.',409)
            document=read_document(entry['path'],max_bytes=self.limits.upload_bytes)
            item=self.catalog.resolve(document)
            if item['id']!=entry['index_id']:raise ServiceError('artifact_changed','Stored index binding changed.',409)
            return document,item['id']

    def delete_upload(self,token,csrf,upload_id):
        with self.lock:
            s=self._lookup(token,csrf)
            if s.busy:raise ServiceError('session_busy','Wait for active work before removing uploads.',409)
            entry=s.uploads.get(upload_id)
            if entry is None:raise ServiceError('not_found','Upload not found in this session.',404)
            self._remove(entry['path']);del s.uploads[upload_id];self._invalidate(s)

    def submit_analysis(self,token,csrf,upload_ids,baseline_ids):
        if not isinstance(upload_ids,list) or not 1<=len(upload_ids)<=4 or not all(_id(x) for x in upload_ids) or len(set(upload_ids))!=len(upload_ids):raise ServiceError('selection','Select 1–4 distinct session results.')
        if not isinstance(baseline_ids,list) or len(baseline_ids)>2 or not all(_id(x) for x in baseline_ids) or len(set(baseline_ids))!=len(baseline_ids):raise ServiceError('selection','Select at most two distinct configured references.')
        with self.lock:
            self.cleanup();s=self._lookup(token,csrf)
            if s.busy:raise ServiceError('session_busy','Another upload or analysis is active.',409)
            if any(x not in s.uploads for x in upload_ids):raise ServiceError('not_found','A selected result is not in this session.',404)
            if any(x not in self.catalog.baselines for x in baseline_ids):raise ServiceError('not_found','Unknown configured reference.',404)
            entries=[s.uploads[x] for x in upload_ids]+[self.catalog.baselines[x] for x in baseline_ids]
            if len({e['artifact_sha256'] for e in entries})!=len(entries):raise ServiceError('duplicate_artifact','Selected references duplicate an uploaded artifact.',409)
            if self._size()+self.reserved+self.limits.report_bytes>self.limits.global_bytes:raise ServiceError('storage_capacity','Not enough temporary analysis capacity.',503)
            if not self.job_slots.acquire(blocking=False):raise ServiceError('analysis_capacity','Analysis queue is full. Try later.',429)
            s.busy=True;self.reserved+=self.limits.report_bytes
            job_id=uuid.uuid4().hex;s.jobs={job_id:{'id':job_id,'status':'queued','error':None}};self._invalidate(s)
            try:self.executor.submit(self._analyze,token,s,job_id,entries)
            except RuntimeError:
                s.busy=False;self.reserved-=self.limits.report_bytes;self.job_slots.release();raise ServiceError('closed','Analysis service is closing.',503) from None
            return dict(s.jobs[job_id])

    def _analyze(self,token,s,job_id,entries):
        out=s.directory/job_id
        try:
            with self.lock:s.jobs[job_id]['status']='running'
            pairs=[]
            for e in entries:
                if digest(e['path'])!=e.get('file_sha256',e.get('sha256')):raise ServiceError('artifact_changed','Stored artifact changed; remove and upload again.',422)
                pairs.append((read_document(e['path']),self.catalog.indexes[e.get('index_id')]['index']))
            report=analyze_many(pairs,resamples=self.limits.bootstrap_resamples,seed=self.limits.bootstrap_seed)
            if self.catalog.public_reference_disclosure:
                from .public_disclosure import disclose_references
                report=disclose_references(report,[e['artifact_sha256'] for e in entries
                                                   if e.get('scope')=='actual_target_outputs'])
            write_analysis(report,out)
            size=sum(p.stat().st_size for p in out.iterdir() if p.is_file())
            if size>self.limits.report_bytes:raise ServiceError('report_size','Analysis output exceeds the temporary report limit.',413)
            with self.lock:
                self._lookup(token)
                s.report={'job_id':job_id,'directory':out};s.jobs[job_id]['status']='complete'
        except Exception:
            # Never expose a stack, raw response, endpoint or operator path to clients/logs.
            with self.lock:
                s.jobs[job_id].update(status='failed',error='Analysis could not complete. Check result compatibility or service capacity.')
                if out.exists():self._remove(out)
        finally:
            with self.lock:s.busy=False;self.reserved-=self.limits.report_bytes;self.job_slots.release();self.cleanup()

    def job(self,token,job_id):
        with self.lock:
            s=self._lookup(token)
            if job_id not in s.jobs:raise ServiceError('not_found','Job not found in this session.',404)
            return dict(s.jobs[job_id])

    def report_file(self,token,job_id,kind):
        with self.lock:
            s=self._lookup(token)
            if kind not in self.FILES or s.report is None or s.report['job_id']!=job_id:raise ServiceError('not_found','Report not found in this session.',404)
            return s.report['directory']/self.FILES[kind]

    def close(self):
        with self.lock:self.closed=True
        self.executor.shutdown(wait=True,cancel_futures=False)
        with self.lock:
            for s in self.sessions.values():self._remove(s.directory)
            self.sessions.clear()
