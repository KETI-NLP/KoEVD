"""Explicit synthetic catalog for the local upload/reference demo; never a baseline."""
import argparse
import hashlib
import json
from pathlib import Path
from make_demo_diagnostics import make_fixture


def create_demo(output):
    output=Path(output)
    if output.exists() and any(output.iterdir()):raise ValueError('Use a new/empty demo output directory')
    output.mkdir(parents=True,exist_ok=True)
    index,docs=make_fixture()
    values={'trusted-synthetic-index.json':index,'SYNTHETIC-A.json':docs[0],'SYNTHETIC-B.json':docs[1]}
    for name,value in values.items():(output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    sha=lambda name:hashlib.sha256((output/name).read_bytes()).hexdigest()
    config={'schema_version':'koevd-space-catalog-v1',
        'indexes':[{'id':'synthetic-demo','label':'Fictional 80-source CPU demonstration','mode':'synthetic_demo','path':'trusted-synthetic-index.json','sha256':sha('trusted-synthetic-index.json')}],
        'baselines':[{'id':'synthetic-reference-b','label':'SYNTHETIC-B · fictional reference','index_id':'synthetic-demo','path':'SYNTHETIC-B.json','sha256':sha('SYNTHETIC-B.json'),'scope':'synthetic_demo','publication_evidence':None}]}
    (output/'catalog.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8',newline='\n')
    (output/'SYNTHETIC_ONLY.txt').write_text('Fictional outputs and reference. No inference, classifier accuracy, GPU or public baseline evidence.\n',encoding='utf-8',newline='\n')
    return output/'catalog.json'


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',default='generated/space-synthetic-demo');args=p.parse_args()
    print(create_demo(args.output_dir).resolve())
