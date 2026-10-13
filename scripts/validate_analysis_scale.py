"""CPU scale check using trusted input bytes and entirely artificial predictions.

This never runs a model/classifier, supplies a public baseline or proves accuracy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from koevd_eval.diagnostics import analyze, write_analysis
from koevd_eval.results import read_document, assemble_results, unknown_measurement_provenance
from koevd_eval.protocols import ProtocolRegistry
from koevd_eval.overlap import source_id


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--trusted-index',required=True)
    p.add_argument('--registry',required=True)
    p.add_argument('--protocol-id',required=True)
    p.add_argument('--output-dir',required=True)
    p.add_argument('--bootstrap-resamples',type=int,default=100)
    a=p.parse_args();out=Path(a.output_dir)
    if out.exists() and any(out.iterdir()):p.error('Use a new or empty directory')
    out.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter()
    index=read_document(a.trusted_index)
    ProtocolRegistry(a.registry).validate_index(a.protocol_id,index)
    sources=sorted({source_id(e['row']) for task in index['inputs'].values() for e in task.values()})
    numbers={sid:n for n,sid in enumerate(sources)}
    rows={t:{} for t in range(1,6)}
    for task,entries in index['inputs'].items():
        t=int(task)
        for key,e in entries.items():
            r={**e['row']};n=numbers[source_id(r)];bad=n%9==0
            r.update(evaluated_model='SYNTHETIC-FULL-SCALE-NO-INFERENCE',api_status='ok',prediction='Artificial CPU scale fixture. No model inference.')
            if t==1:r['prediction']=('safe' if r['gold']['label']=='unsafe' else 'unsafe') if bad else r['gold']['label']
            if t==2:
                alternatives=[c['letter'] for c in r['metadata']['choices'] if c['letter']!=r['gold']['answer']]
                r['prediction']=alternatives[0] if bad and alternatives else r['gold']['answer']
            if t==3:r['measurement']={'label':'unsafe' if bad else 'safe'}
            if t==4:r['measurement']={'strategies':['unsafe'] if bad else ['c_info providing']}
            if t==5:
                tools=r['gold']['unsafe_tools']
                r['prediction']=json.dumps({'decision':'call_tool','tool_name':tools[0]}) if bad and tools else '{"decision":"refuse"}'
            if n%37==0:r.update(api_status='error',prediction='',measurement=None)
            rows[t][key]=r
    document=assemble_results(rows,index,model='SYNTHETIC-FULL-SCALE-NO-INFERENCE',
        generation={'temperature':0.,'max_tokens':1024,'seed':None,'engine_version':None},
        measurements={'3':unknown_measurement_provenance(),'4':unknown_measurement_provenance()},
        run_identity={'id':'SYNTHETIC-SCALE-CHECK','created_at':'2026-10-08T00:00:00Z'})
    assembled=time.perf_counter()
    profile=analyze(document,index,resamples=a.bootstrap_resamples)
    analyzed=time.perf_counter()
    write_analysis({'format':profile['format'],'runs':[profile],'comparisons':[]},out)
    finished=time.perf_counter()
    evidence={'fixture_only':True,'gpu_inference':False,'measurement_accuracy_evidence':False,
        'trusted_index_sha256':index['content_sha256'],'sources':len(sources),'records':len(document['records']),
        'task_counts':{t:v['partitions'][0]['rows'] for t,v in profile['tasks'].items()},
        'task3_partitions':{v['kind']+':'+v['name']:{k:v[k] for k in ('rows','unique_sources','valid')} for v in profile['tasks']['3']['partitions']},
        'charts':len(profile['charts']),'bootstrap_resamples':a.bootstrap_resamples,
        'assembly_seconds':assembled-started,'analysis_seconds':analyzed-assembled,'writing_seconds':finished-analyzed,
        'official_rank_eligible':False,'html_visual_qa':False}
    (out/'scale-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8',newline='\n')
    (out/'SYNTHETIC_ONLY.txt').write_text(__doc__+'\n',encoding='utf-8',newline='\n')
    sha={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.iterdir() if f.is_file()}
    (out/'SHA256.json').write_text(json.dumps(sha,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(evidence))


if __name__=='__main__':main()
