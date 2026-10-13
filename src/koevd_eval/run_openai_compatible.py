"""Run model-facing KoEVD JSONL with durable attempts and bounded concurrency."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import http.client
import json
import math
import os
from pathlib import Path
import sys
import threading
import time
from typing import Any, Mapping
import urllib.error
import urllib.parse
import urllib.request
import uuid

from .common import read_jsonl, row_id, write_jsonl

MAX_API_BYTES = 8 * 1024 * 1024
EXTRA_FIELDS = {'seed','top_p','top_k','min_p','repetition_penalty','frequency_penalty',
                'presence_penalty','stop','chat_template_kwargs'}


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def endpoint(base_url: str) -> str:
    value = base_url.rstrip('/')
    value = value if value.endswith('/chat/completions') else value + '/chat/completions'
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Use an HTTP(S) endpoint without embedded credentials, query or fragment')
    return value


def validate_extra_body(value):
    if value is None:
        return {}
    if not isinstance(value,dict) or not set(value) <= EXTRA_FIELDS:
        raise ValueError('Unsupported extra request field; core fields, tools and credentials cannot be overridden')
    json.dumps(value,allow_nan=False)
    for key, item in value.items():
        if key in ('seed','top_k'):
            if type(item) is not int or (key == 'top_k' and item != -1 and item < 1):
                raise ValueError('Invalid integer extra request parameter')
        elif key in ('top_p','min_p'):
            if type(item) not in (int,float) or not math.isfinite(item) or not 0 <= item <= 1:
                raise ValueError('Invalid probability extra request parameter')
        elif key in ('repetition_penalty','frequency_penalty','presence_penalty'):
            if type(item) not in (int,float) or not math.isfinite(item) or (key=='repetition_penalty' and item<=0):
                raise ValueError('Invalid penalty extra request parameter')
        elif key == 'stop':
            if not (isinstance(item,str) or isinstance(item,list) and all(isinstance(v,str) for v in item)):
                raise ValueError('Stop must be a string or list of strings')
        elif key == 'chat_template_kwargs':
            if not isinstance(item,dict) or set(item) != {'enable_thinking'} or type(item['enable_thinking']) is not bool:
                raise ValueError('Only explicit boolean chat_template_kwargs.enable_thinking is supported')
    return deepcopy(value)


def validate_config(config):
    required={'endpoint','model','temperature','max_tokens'}
    optional={'extra_body','engine_version','model_provenance'}
    if not isinstance(config,dict) or not required <= set(config) or not set(config) <= required | optional:
        raise ValueError('Invalid runner configuration fields')
    endpoint(config['endpoint'])
    if not isinstance(config['model'],str) or not config['model'].strip():
        raise ValueError('Model ID is required')
    if type(config['temperature']) not in (int,float) or not math.isfinite(config['temperature']) or config['temperature']<0:
        raise ValueError('Temperature must be finite and nonnegative')
    if type(config['max_tokens']) is not int or config['max_tokens']<1:
        raise ValueError('max_tokens must be positive')
    validate_extra_body(config.get('extra_body'))
    if config.get('engine_version') is not None and not isinstance(config['engine_version'],str):
        raise ValueError('Engine version must be a declared string')
    claims=config.get('model_provenance')
    if claims is not None:
        allowed={'revision','chat_template','dtype','quantization','thinking'}
        if not isinstance(claims,dict) or not set(claims)<=allowed or any(v is not None and not isinstance(v,str) for v in claims.values()):
            raise ValueError('Invalid declared model provenance')
    return config


def make_config(base_url, model, temperature=0., max_tokens=1024, *, extra_body=None, engine_version=None, model_provenance=None):
    config={'endpoint':endpoint(base_url),'model':model,'temperature':temperature,'max_tokens':max_tokens}
    if extra_body: config['extra_body']=validate_extra_body(extra_body)
    if engine_version is not None: config['engine_version']=engine_version
    if model_provenance is not None: config['model_provenance']=deepcopy(model_provenance)
    return validate_config(config)


@dataclass(frozen=True)
class APIResponse:
    text: str
    finish_reason: str | None = None
    usage: dict | None = None
    request_id: str | None = None
    response_id: str | None = None
    server_model: str | None = None
    reasoning_content: str | None = None
    refusal: str | None = None
    http_status: int | None = None


def _optional_text(value):
    if value is not None and not isinstance(value,str):
        raise ValueError('Malformed optional response text')
    if value is not None: value.encode('utf-8')
    return value


def _parse_response(body, headers, http_status=None):
    if not isinstance(body,dict) or not isinstance(body.get('choices'),list) or len(body['choices'])!=1:
        raise ValueError('Expected exactly one chat completion choice')
    choice=body['choices'][0]
    message=choice.get('message')
    if not isinstance(message,dict): raise ValueError('Missing assistant message')
    content=message.get('content')
    if isinstance(content,list):
        if any(not isinstance(part,dict) or part.get('type')!='text' or not isinstance(part.get('text'),str) for part in content):
            raise ValueError('Unsupported assistant content part')
        content=''.join(part['text'] for part in content)
    content='' if content is None else _optional_text(content)
    usage=body.get('usage')
    if usage is not None:
        if not isinstance(usage,dict): raise ValueError('Malformed response usage')
        # Do not persist arbitrary server fields or headers.
        usage={key:value for key,value in usage.items() if key in ('prompt_tokens','completion_tokens','total_tokens')}
        if any(type(v) is not int or v<0 for v in usage.values()): raise ValueError('Malformed token counts')
    if message.get('tool_calls'):
        # KoEVD uses text-only mock tool decisions and never sends actual tool definitions.
        raise ValueError('Unexpected actual tool-call response')
    return APIResponse(content,_optional_text(choice.get('finish_reason')),usage,
                       _optional_text(headers.get('x-request-id')),
                       _optional_text(body.get('id')),_optional_text(body.get('model')),
                       _optional_text(message.get('reasoning_content',message.get('reasoning'))),
                       _optional_text(message.get('refusal')),http_status)


def call_api(url: str, api_key: str, model: str, messages: list[Mapping[str,Any]], temperature: float,
             max_tokens: int, timeout: float, *, extra_body=None, request_id=None, return_metadata=False):
    """The default text return preserves the old API; the runner opts into metadata."""
    payload={'model':model,'messages':messages,'temperature':temperature,'max_tokens':max_tokens,
             **validate_extra_body(extra_body)}
    headers={'Content-Type':'application/json'}
    if api_key: headers['Authorization']=f'Bearer {api_key}'
    if request_id: headers['X-Request-Id']=request_id
    request=urllib.request.Request(endpoint(url),data=json.dumps(payload,ensure_ascii=False,allow_nan=False).encode('utf-8'),headers=headers,method='POST')
    with urllib.request.urlopen(request,timeout=timeout) as response:
        raw=response.read(MAX_API_BYTES+1)
        if len(raw)>MAX_API_BYTES: raise ValueError('API response exceeds size limit')
        body=json.loads(raw.decode('utf-8'))
        parsed=_parse_response(body,response.headers,response.status)
    return parsed if return_metadata else parsed.text


def successful_ids(output_path: Path) -> set[str]:
    if not output_path.exists():return set()
    return {row_id(row) for row in read_jsonl(output_path) if row.get('api_status')=='ok'}


def unique_rows(rows):
    indexed={}
    for row in rows:
        key=row_id(row)
        if not key or key in indexed:raise ValueError(f'Input/output requires unique nonempty sample IDs: {key!r}')
        indexed[key]=row
    return indexed


def input_digest(row):
    return hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def _atomic_json(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    with temporary.open('w',encoding='utf-8',newline='\n') as handle:
        json.dump(value,handle,ensure_ascii=False,allow_nan=False,indent=2);handle.write('\n')
        handle.flush();os.fsync(handle.fileno())
    # A Windows reader or file scanner can briefly prevent replacement. Keep
    # both files intact; persistent access errors still fail after a short bound.
    for attempt in range(6):
        try:
            os.replace(temporary,path)
            break
        except OSError as error:
            if os.name!='nt' or getattr(error,'winerror',None) not in (5,32,33) or attempt==5:
                raise
            time.sleep(.02 * 2**attempt)


@contextmanager
def _output_lock(output):
    # OS locks release on process death. A leftover lock FILE is not a live lock.
    path=output.with_suffix(output.suffix+'.lock')
    with path.open('a+b') as handle:
        if handle.seek(0,os.SEEK_END)==0:handle.write(b'0');handle.flush()
        handle.seek(0)
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(handle.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError('Another runner holds this output lock') from exc
        try:yield
        finally:
            handle.seek(0)
            if os.name=='nt':msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(handle.fileno(),fcntl.LOCK_UN)


def _empty_result(row, config, run_id, attempts):
    result=deepcopy(row)
    result.update(prediction='',api_status='error',api_error=None,evaluated_model=config['model'],
                  run_config=deepcopy(config),input_sha256=input_digest(row),
                  generation={'run_id':run_id,'attempts':deepcopy(attempts),
                              'selection_policy':'first_accepted_api_response','selected_attempt_id':None,
                              **asdict(APIResponse(''))})
    result['generation'].pop('text')
    return result


def _previous(output, journal, inputs, config, run_id):
    previous=unique_rows(read_jsonl(output)) if output.exists() else {}
    pending={}
    if journal.exists():
        lines=journal.read_bytes().splitlines()
        for number,line in enumerate(lines):
            try:value=json.loads(line.decode('utf-8'))
            except (json.JSONDecodeError,UnicodeDecodeError):
                if number==len(lines)-1:break
                raise ValueError('Corrupt generation journal before final line')
            if not isinstance(value,dict):raise ValueError('Malformed generation journal entry')
            event=value.get('event')
            if event=='attempt_started':
                key=value.get('sample_id')
                if (key not in inputs or value.get('input_sha256')!=input_digest(inputs[key])
                        or value.get('config_sha256')!=input_digest(config) or value.get('run_id')!=run_id):
                    raise ValueError('Attempt journal does not match run/input/configuration')
                if key in pending:raise ValueError('Unfinished overlapping attempts for one sample')
                pending[key]=value['attempt']
            elif event=='attempt_finished':
                result=value.get('result')
                if not isinstance(result,dict):raise ValueError('Missing attempt result')
                key=row_id(result);previous[key]=result;pending.pop(key,None)
            elif event is None:
                previous[row_id(value)]=value  # compatible old row-only journal
            else:raise ValueError('Unknown generation journal event')
    for key,result in previous.items():
        if (key not in inputs or result.get('run_config')!=config or result.get('input_sha256')!=input_digest(inputs[key])
                or any(result.get(field)!=value for field,value in inputs[key].items())):
            raise ValueError('Resume requires the same input rows, model, endpoint and decoding settings; use a new output file.')
        recorded=(result.get('generation') or {}).get('run_id')
        if recorded is not None and recorded!=run_id:raise ValueError('Resume run identity mismatch')
    for key,attempt in pending.items():
        if previous.get(key,{}).get('api_status')=='ok':raise ValueError('Attempt started after a completed successful response')
        history=deepcopy((previous.get(key,{}).get('generation') or {}).get('attempts',[]))
        history.append({**attempt,'status':'interrupted_unknown','finished_at':None,'latency_seconds':None,'error_kind':None,'http_status':None})
        result=_empty_result(inputs[key],config,run_id,history)
        result['api_error']='interrupted_before_response_checkpoint'
        previous[key]=result
    return previous


def _safe_failure(exc):
    status=exc.code if isinstance(exc,urllib.error.HTTPError) else None
    kind=type(exc).__name__
    # Exception messages/server bodies can echo headers, tokens or URLs. Never persist them.
    retryable=status in (408,429,500,502,503,504) if status is not None else isinstance(exc,(urllib.error.URLError,TimeoutError,ConnectionError,http.client.HTTPException,KeyError,ValueError))
    if isinstance(exc,urllib.error.HTTPError):exc.close()
    return kind,status,retryable


def print_progress(value):
    print(f"[{value['state']}] {value['completed']}/{value['total']} checkpointed, {value['successful']} API-ok, {value['failed']} failed, {value['pending']} pending",file=sys.stderr,flush=True)


def run_rows(rows, output, config, *, api_key='', timeout=120, retries=2, retry_delay=2,
             resume=False, workers=1, progress=None, run_id=None):
    """Bound requests; fsync each attempt start/finish; compact in original input order.

    An interrupted transport may have reached the server. Resume records that
    ambiguity and tries again; it cannot guarantee exactly-once server inference.
    """
    validate_config(config)
    if type(workers) is not int or not 1<=workers<=64 or type(retries) is not int or retries<0:
        raise ValueError('Workers must be 1..64 and retries nonnegative')
    if not math.isfinite(timeout) or timeout<=0 or not math.isfinite(retry_delay) or retry_delay<0:
        raise ValueError('Invalid timeout or retry delay')
    inputs=unique_rows(rows)
    if any(not isinstance(row.get('messages'),list) for row in inputs.values()):
        raise ValueError('Prepared messages must be a list')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    with _output_lock(output):
        return _run_locked(inputs,output,deepcopy(config),api_key=api_key,timeout=timeout,
                           retries=retries,retry_delay=retry_delay,resume=resume,workers=workers,
                           progress=progress,run_id=run_id)


def _run_locked(inputs, output, config, *, api_key, timeout, retries, retry_delay, resume, workers, progress, run_id):
    journal=output.with_suffix(output.suffix+'.progress.jsonl')
    state_path=output.with_suffix(output.suffix+'.run.json')
    status_path=output.with_suffix(output.suffix+'.status.json')
    if not resume and any(p.exists() for p in (output,journal,state_path)):
        raise ValueError('Output already exists; use resume or a new output path')
    expected={'input_set_sha256':input_digest(list(inputs.values())),'config_sha256':input_digest(config)}
    if state_path.exists():
        state=json.loads(state_path.read_text(encoding='utf-8'))
        if any(state.get(k)!=v for k,v in expected.items()) or run_id is not None and state.get('run_id')!=run_id:
            raise ValueError('Resume run identity/input order/configuration changed')
    else:
        state={'format':'koevd-run-v2','run_id':run_id or str(uuid.uuid4()),'created_at':timestamp(),**expected}
        _atomic_json(state_path,state)
    run_id=state['run_id']
    results=_previous(output,journal,inputs,config,run_id) if resume else {}
    repaired=journal.with_suffix(journal.suffix+'.tmp')
    write_jsonl(repaired,results.values());os.replace(repaired,journal)
    checkpoint_lock=threading.Lock();stop=threading.Event()
    finished={key for key,row in results.items() if row.get('api_status')=='ok'}
    def checkpoint(value):
        with checkpoint_lock, journal.open('a',encoding='utf-8',newline='\n') as handle:
            handle.write(json.dumps(value,ensure_ascii=False,allow_nan=False)+'\n');handle.flush();os.fsync(handle.fileno())
    def emit(phase):
        done=len(finished);successful=sum(row.get('api_status')=='ok' for row in results.values())
        value={'format':'koevd-progress-v1','run_id':run_id,'state':phase,'updated_at':timestamp(),
               'total':len(inputs),'completed':done,'successful':successful,'failed':sum(key in finished and row.get('api_status')!='ok' for key,row in results.items()),
               'checkpointed':len(results),'pending':len(inputs)-successful if phase=='interrupted' else len(inputs)-done,
               'workers':workers}
        _atomic_json(status_path,value)
        if progress:progress(dict(value))
    def execute(key):
        row=inputs[key]
        history=deepcopy((results.get(key,{}).get('generation') or {}).get('attempts',[]))
        result=_empty_result(row,config,run_id,history)
        for attempt_number in range(retries+1):
            if stop.is_set():return None
            attempt={'id':str(uuid.uuid4()),'ordinal':len(history)+1,'started_at':timestamp(),
                     'client_controls':{'workers':workers,'timeout_seconds':timeout,
                                        'retries':retries,'retry_delay_seconds':retry_delay}}
            checkpoint({'event':'attempt_started','sample_id':key,'attempt':attempt,
                        'input_sha256':input_digest(row),'config_sha256':input_digest(config),'run_id':run_id})
            started=time.monotonic();retryable=False
            try:
                response=call_api(config['endpoint'],api_key,config['model'],row['messages'],config['temperature'],
                                  config['max_tokens'],timeout,extra_body=config.get('extra_body'),
                                  request_id=attempt['id'],return_metadata=True)
                # Existing custom callers/test doubles can still return a text string.
                if isinstance(response,str):response=APIResponse(response)
                if not isinstance(response,APIResponse):raise ValueError('Invalid chat response object')
                response.text.encode('utf-8')
                history.append({**attempt,'status':'ok','finished_at':timestamp(),
                                'latency_seconds':time.monotonic()-started,'error_kind':None,'http_status':response.http_status})
                result.update(prediction=response.text,api_status='ok',api_error=None)
                result['generation'].update(asdict(response),attempts=deepcopy(history),selected_attempt_id=attempt['id'],
                                            parameter_status='requested_unverified')
                result['generation'].pop('text',None)
            except (urllib.error.URLError,TimeoutError,ConnectionError,http.client.HTTPException,KeyError,ValueError) as exc:
                kind,status,retryable=_safe_failure(exc)
                history.append({**attempt,'status':'error','finished_at':timestamp(),
                                'latency_seconds':time.monotonic()-started,'error_kind':kind,'http_status':status})
                result['api_error']=kind+(f' HTTP {status}' if status is not None else '')
                result['generation']['attempts']=deepcopy(history)
            checkpoint({'event':'attempt_finished','sample_id':key,'result':result})
            if result['api_status']=='ok' or not retryable:break
            if attempt_number<retries and stop.wait(min(60,retry_delay*(2**attempt_number))):return result
        return result
    emit('running')
    pending=[key for key in inputs if results.get(key,{}).get('api_status')!='ok']
    pool=None
    try:
        if workers==1:
            for key in pending:
                result=execute(key)
                if result is not None:
                    results[key]=result;finished.add(key)
                emit('running')
        else:
            pool=ThreadPoolExecutor(max_workers=workers,thread_name_prefix='koevd-request')
            queue=iter(pending);futures={}
            def submit_one():
                key=next(queue,None)
                if key is not None:futures[pool.submit(execute,key)]=key
            for _ in range(workers):submit_one()
            while futures:
                ready,_=wait(futures,return_when=FIRST_COMPLETED)
                for future in ready:
                    key=futures.pop(future);result=future.result()
                    if result is not None:results[key]=result;finished.add(key)
                    emit('running');submit_one()
            pool.shutdown(wait=True);pool=None
        temporary=output.with_suffix(output.suffix+'.tmp')
        write_jsonl(temporary,(results[key] for key in inputs));os.replace(temporary,output)
        journal.unlink()
        emit('completed' if all(r.get('api_status')=='ok' for r in results.values()) else 'completed_with_errors')
        return results
    except BaseException:
        stop.set()
        if pool is not None:pool.shutdown(wait=True,cancel_futures=True)
        results=_previous(output,journal,inputs,config,run_id)
        finished.update(key for key,row in results.items() if row.get('api_status')=='ok')
        # A user callback can itself interrupt; the durable status update must still run.
        previous_callback=progress;progress=None
        emit('interrupted');progress=previous_callback
        raise


def load_options(path):
    if path is None:return None
    with Path(path).open('rb') as handle:raw=handle.read(32769)
    if len(raw)>32768:raise ValueError('Runner options JSON exceeds 32 KiB')
    from .results import _unique_object
    value=json.loads(raw.decode('utf-8'),object_pairs_hook=_unique_object)
    if not isinstance(value,dict):raise ValueError('Runner options must be an object')
    return value


def add_execution_arguments(parser):
    parser.add_argument('--workers',type=int,default=1)
    parser.add_argument('--retry-delay',type=float,default=2.)
    parser.add_argument('--extra-body-file')
    parser.add_argument('--model-provenance-file')
    parser.add_argument('--engine-version')
    parser.add_argument('--preflight',action='store_true',help='Run a separate synthetic connection probe')


def main():
    from .common import configure_cli_stdio
    configure_cli_stdio()
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True);parser.add_argument('--output',required=True)
    parser.add_argument('--base-url',required=True);parser.add_argument('--model',required=True)
    parser.add_argument('--api-key-env',default='OPENAI_API_KEY')
    parser.add_argument('--temperature',type=float,default=0.);parser.add_argument('--max-tokens',type=int,default=1024)
    parser.add_argument('--timeout',type=float,default=120.);parser.add_argument('--retries',type=int,default=2)
    parser.add_argument('--start',type=int,default=0);parser.add_argument('--limit',type=int)
    parser.add_argument('--resume',action='store_true');add_execution_arguments(parser)
    args=parser.parse_args()
    if args.start<0 or args.limit is not None and args.limit<0:parser.error('start and limit must be nonnegative')
    rows=list(read_jsonl(args.input))[args.start:]
    if args.limit is not None:rows=rows[:args.limit]
    config=make_config(args.base_url,args.model,args.temperature,args.max_tokens,
                       extra_body=load_options(args.extra_body_file),engine_version=args.engine_version,
                       model_provenance=load_options(args.model_provenance_file))
    key=os.environ.get(args.api_key_env,'')
    if args.preflight:
        from .preflight import preflight
        evidence=preflight(config,rows,api_key=key,timeout=args.timeout)
        _atomic_json(Path(args.output).with_suffix('.preflight.json'),evidence)
    run_rows(rows,Path(args.output),config,api_key=key,timeout=args.timeout,retries=args.retries,
             retry_delay=args.retry_delay,resume=args.resume,workers=args.workers,progress=print_progress)


if __name__=='__main__':main()
