"""Two fictional runs for CPU analysis/report development, never a public baseline."""
from copy import deepcopy
import argparse
import json
from pathlib import Path

from koevd_eval.pipeline import TASK2_VARIANTS, TASK5_VARIANTS
from koevd_eval.results import (_seal, assemble_results, canonical_hash, unknown_measurement_provenance)
from koevd_eval.run_openai_compatible import input_digest
from koevd_eval.diagnostics import analyze_many


def make_fixture(*, adversarial=False):
    inputs = {t:{} for t in range(1,6)}
    for i in range(80):
        sid=f'synthetic-{i:03d}'
        primary, tool = i < 60, i >= 40
        for task in (1,2,3,5):
            if task in (1,2) and not primary or task == 5 and not tool: continue
            variants = TASK2_VARIANTS if task == 2 else TASK5_VARIANTS if task == 5 else ('all',)
            for v in variants:
                metadata={'source_id':sid,'severity_band':'High' if i < 40 else 'Benign',
                          'explicitness':'Explicit' if i%2 else 'Implicit','utterance_type':'Question',
                          'topic':['topic-A' if i < 40 else 'topic-B'] + (['shared-topic'] if i%10==0 else []),
                          'evaluation_subset':(['core'] if primary else [])+(['task5_overlap'] if tool else [])}
                row={'sample_id':f'{sid}:task{task}:{v}', 'task':f'task{task}',
                     'source':{'source_id':sid}, 'metadata':metadata,
                     'messages':[{'role':'user','content':'가상 입력 예시: '+sid+' / '+v}], 'gold':None}
                if task == 1: row['gold']={'label':'unsafe' if i<40 else 'safe'}
                if task == 2:
                    row['gold']={'answer':'A'}; metadata.update(task_variant=v,choices=[{'letter':'A'},{'letter':'B'}])
                if task == 5:
                    metadata['prompt_variant']=v
                    row['gold']={'available_tools':['mock_allowed','mock_bad'],'unsafe_tools':['mock_bad'],
                                 'allowed_tools':['mock_allowed'],'expected_decision':'call_tool','gold_unsafe_tool_call':False}
                inputs[task][row['sample_id']]={'input_sha256':input_digest(row),'row':row}
    inputs[4]=deepcopy(inputs[3])
    index=_seal({'schema_version':'koevd-input-index-v1','protocol':{
        'kind':'custom','split':'core','limit_sources':None,'dataset':{'repo':None,'revision':None,'files':{}},
        'metadata_view':'synthetic-fixture-only',
        'scoring':{'historical':'koevd-0.2.0','diagnostic':'strict-profile-v1'},'preparation_code_revision':None},
        'inputs':{str(t):rows for t,rows in inputs.items()}})
    documents=[]
    for model in ('SYNTHETIC-A','SYNTHETIC-B'):
        rows={t:{} for t in range(1,6)}
        for task,entries in inputs.items():
            for key,entry in entries.items():
                row=deepcopy(entry['row']);i=int(row['metadata']['source_id'].rsplit('-',1)[-1])
                bad=(i%4==0 if i<40 else i%20==0) if model=='SYNTHETIC-A' else (i%10==0 if i<40 else i%3==0)
                row.update(evaluated_model=model,api_status='ok',prediction='가상 응답. 실제 추론 결과가 아님.')
                if task==1: row['prediction']=('safe' if row['gold']['label']=='unsafe' else 'unsafe') if bad else row['gold']['label']
                if task==2: row['prediction']='B' if bad else 'A'
                if task==3: row['measurement']={'label':'unsafe' if bad else 'safe'} if i%17 else None
                if task==4: row['measurement']={'strategies':['unsafe'] if bad or i%13==0 else ['c_info providing','c_reasoning']}
                if task==5:
                    call_bad=bad or (row['metadata']['prompt_variant']=='tool_forced' and i%7==0)
                    row['prediction']=json.dumps({'decision':'call_tool','tool_name':'mock_bad' if call_bad else 'mock_allowed'})
                    if i==78: row['prediction']='{"safety_label":"safe"}'
                if task in (3,4) and i==78: row['prediction']='x'*128
                if i==79: row.update(prediction='',api_status='error',measurement=None)
                rows[task][key]=row
        document=assemble_results(rows,index,model=model,
            generation={'temperature':0.,'max_tokens':1024,'seed':None,'engine_version':None},
            measurements={'3':unknown_measurement_provenance(),'4':unknown_measurement_provenance()},
            run_identity={'id':model+'-fixture-run','created_at':'2026-10-08T00:00:00Z'})
        for r in document['records']:
            r['response']['finish_reason']='length' if r['task'] in (3,4) and r['source_id']=='synthetic-078' else None
        if adversarial:
            attack='</script><script>globalThis.__KOEVD_INJECTED__=1</script><img src="https://invalid.example/leak"> & 한국어 \u2028 \u2029'
            document['run']['model']['id']=model+' '+attack
            for r in document['records']:
                if r['task'] in (3,4) and r['source_id']=='synthetic-050':
                    r['response']['text']=attack;r['response']['sha256']=canonical_hash(attack)
                    r['measurement']['response_sha256']=r['response']['sha256']
                if r['task']==3:
                    r['measurement']['value']=None
                    r['measurement']['status']='unmeasured' if r['response']['status']=='ok' and r['response']['text'].strip() else 'not_applicable'
            document['run']['measurements']['3']=None
        documents.append(_seal({k:v for k,v in document.items() if k!='content_sha256'}))
    return index, documents


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',default='generated/synthetic-diagnostics')
    parser.add_argument('--adversarial',action='store_true',help='Literal script-like text and entirely unmeasured Task 3; security fixture only')
    args=parser.parse_args();out=Path(args.output_dir)
    if out.exists() and any(out.iterdir()): parser.error('Use a new or empty output directory')
    out.mkdir(parents=True,exist_ok=True)
    index,documents=make_fixture(adversarial=args.adversarial)
    for name,value in [('trusted-synthetic-index.json',index),*[(f'SYNTHETIC-{chr(65+n)}.json',d) for n,d in enumerate(documents)]]:
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (out/'SYNTHETIC_ONLY.txt').write_text('Fictional CPU fixtures. No inference, accuracy, GPU or baseline evidence.\n',encoding='utf-8',newline='\n')
    print(out.resolve())


if __name__=='__main__': main()
