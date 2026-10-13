"""Download fixed public Pyodide runtime to a fresh candidate folder; no publish."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

VERSION='0.29.3'
BASE=f'https://cdn.jsdelivr.net/pyodide/v{VERSION}/full/'
FILES=('pyodide.js','pyodide.asm.js','pyodide.asm.wasm','python_stdlib.zip','pyodide-lock.json','LICENSE','PYTHON-LICENSE')


def fetch(output):
    out=Path(output); out.mkdir(parents=True,exist_ok=False)
    receipt={'version':VERSION,'files':{},'scope':'runtime integrity, not deployment or analysis evidence'}
    for name in FILES:
        url=BASE+name
        if name=='LICENSE': url=f'https://raw.githubusercontent.com/pyodide/pyodide/{VERSION}/LICENSE'
        if name=='PYTHON-LICENSE': url='https://raw.githubusercontent.com/python/cpython/v3.13.2/LICENSE'
        with urllib.request.urlopen(url,timeout=60) as response:
            raw=response.read(64*1024*1024+1)
        if len(raw)>64*1024*1024: raise ValueError('Runtime download exceeds bound')
        (out/name).write_bytes(raw)
        receipt['files'][name]={'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
        print(name,len(raw),flush=True)
    (out/'runtime-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True)
    fetch(p.parse_args().output)
