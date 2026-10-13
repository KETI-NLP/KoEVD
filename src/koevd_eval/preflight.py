"""Separate connection/model/shape probe; never included in benchmark denominators."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import urllib.error
import urllib.request
import uuid

from .common import read_jsonl
from .run_openai_compatible import (APIResponse,MAX_API_BYTES,call_api,validate_config,unique_rows,
                                    make_config,load_options,timestamp,_atomic_json)


def preflight(config, rows=(), *, api_key='', timeout=30):
    validate_config(config)
    if not math.isfinite(timeout) or timeout<=0:raise ValueError('Preflight timeout must be positive and finite')
    inputs=unique_rows(rows)
    for row in inputs.values():
        messages=row.get('messages')
        if not isinstance(messages,list) or not messages:
            raise ValueError('Preflight requires nonempty prepared message lists')
        if any(not isinstance(m,dict) or m.get('role') not in ('system','user','assistant') or not isinstance(m.get('content'),str) for m in messages):
            raise ValueError('Unsupported prepared text-message contract')
    headers={}
    if api_key:headers['Authorization']=f'Bearer {api_key}'
    models_url=config['endpoint'].removesuffix('/chat/completions')+'/models'
    listed=None;model_check='not_available'
    try:
        request=urllib.request.Request(models_url,headers=headers)
        with urllib.request.urlopen(request,timeout=timeout) as response:
            raw=response.read(MAX_API_BYTES+1)
            if len(raw)>MAX_API_BYTES:raise ValueError('Model inventory exceeds size limit')
            inventory=json.loads(raw.decode('utf-8'))
        if not isinstance(inventory,dict) or not isinstance(inventory.get('data'),list):
            raise ValueError('Malformed model inventory')
        listed=[v.get('id') for v in inventory['data'] if isinstance(v,dict) and isinstance(v.get('id'),str)]
        if config['model'] not in listed:raise ValueError('Requested model is absent from server model inventory')
        model_check='listed_by_server'
    except urllib.error.HTTPError as exc:
        status=exc.code;exc.close()
        if status not in (404,405,501):raise ValueError(f'Model inventory HTTP {status}') from None
    except urllib.error.URLError as exc:
        raise ValueError('Model inventory connection failed') from None
    probe_id=str(uuid.uuid4())
    try:
        response=call_api(config['endpoint'],api_key,config['model'],
                          [{'role':'user','content':'Connection check only: reply with OK.'}],
                          config['temperature'],min(config['max_tokens'],16),timeout,
                          extra_body=config.get('extra_body'),request_id=probe_id,return_metadata=True)
    except (urllib.error.URLError,TimeoutError,KeyError,ValueError) as exc:
        status=exc.code if isinstance(exc,urllib.error.HTTPError) else None
        if isinstance(exc,urllib.error.HTTPError):exc.close()
        raise ValueError('Chat probe rejected or failed'+(f' HTTP {status}' if status else '')) from None
    if not isinstance(response,APIResponse):raise ValueError('Malformed preflight response object')
    return {'format':'koevd-preflight-v1','checked_at':timestamp(),'model':config['model'],
            'model_inventory_check':model_check,'expected_rows':len(inputs),
            'probe_in_benchmark':False,'probe_max_tokens':min(config['max_tokens'],16),
            'probe_client_request_id':probe_id,'response_id':response.response_id,
            'server_model':response.server_model,'finish_reason':response.finish_reason,
            'usage':response.usage,'nonempty_final_content':bool(response.text.strip()),
            'request_contract':'accepted_by_server','parameter_effect':'unverified',
            'model_weights_identity':'user_reported'}


def main():
    from .common import configure_cli_stdio
    configure_cli_stdio()
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-url',required=True);p.add_argument('--model',required=True)
    p.add_argument('--input');p.add_argument('--output',required=True)
    p.add_argument('--api-key-env',default='OPENAI_API_KEY');p.add_argument('--timeout',type=float,default=30.)
    p.add_argument('--temperature',type=float,default=0.);p.add_argument('--max-tokens',type=int,default=1024)
    p.add_argument('--extra-body-file')
    a=p.parse_args()
    import os
    config=make_config(a.base_url,a.model,a.temperature,a.max_tokens,extra_body=load_options(a.extra_body_file))
    rows=list(read_jsonl(a.input)) if a.input else []
    evidence=preflight(config,rows,api_key=os.environ.get(a.api_key_env,''),timeout=a.timeout)
    _atomic_json(Path(a.output),evidence)
    print(json.dumps(evidence,ensure_ascii=False))


if __name__=='__main__':main()
