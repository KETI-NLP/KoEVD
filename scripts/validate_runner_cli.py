"""Installed CLI validation using synthetic local HTTP, never real inference."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import sysconfig
import os


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-dir',required=True)
    a=p.parse_args();root=Path(a.output_dir)
    if root.exists() and any(root.iterdir()):p.error('Use an empty/new output directory')
    root.mkdir(parents=True,exist_ok=True)
    checkout=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(checkout/'tests'))
    from test_runner_v2 import server
    from test_own_model_pipeline import dataset_fixture
    from koevd_eval.results import read_document,validate_results
    from koevd_eval.protocols import preparation_identity
    import koevd_eval
    dataset_fixture(root/'synthetic-data')
    (root/'SYNTHETIC_ONLY.txt').write_text('No model, vLLM or classifier inference. Local HTTP contracts only.\n',encoding='utf-8')
    (root/'extra.json').write_text(json.dumps({'seed':23,'top_p':.8,'chat_template_kwargs':{'enable_thinking':False}}),encoding='utf-8')
    (root/'model.json').write_text(json.dumps({'revision':'SYNTHETIC-DECLARED-REVISION','dtype':'SYNTHETIC-DTYPE'}),encoding='utf-8')
    commands=[]
    def command(name,*args):
        executable=Path(sysconfig.get_path('scripts'))/(name+('.exe' if os.name=='nt' else ''))
        if not executable.exists():raise ValueError('Install this checkout in the active Python environment')
        result=subprocess.run([str(executable),*map(str,args)],capture_output=True,text=True,encoding='utf-8',timeout=40)
        if result.stdout is None or result.stderr is None:raise AssertionError('Missing decoded CLI output')
        commands.append({'cli':name,'arguments':[str(v) for v in args],'exit_code':result.returncode,
                         'stdout':result.stdout,'stderr':result.stderr})
        if result.returncode:raise AssertionError(result.stderr)
    with server(responses={'hello core-a':{'content':'Synthetic length-limited final',
                         'reasoning_content':'Synthetic reasoning','_finish':'length'}}) as (base,state):
        command('koevd-pipeline','--stage','prepare','--dataset-dir',root/'synthetic-data','--output-dir',root/'run')
        command('koevd-doctor','--base-url',base,'--model','cpu-http-target','--input',root/'run/task3_input.jsonl',
                '--extra-body-file',root/'extra.json','--output',root/'doctor.json')
        common=['--stage','generate','--output-dir',root/'run','--base-url',base,'--model','cpu-http-target',
                '--extra-body-file',root/'extra.json','--model-provenance-file',root/'model.json',
                '--engine-version','SYNTHETIC-HTTP-ENGINE']
        command('koevd-pipeline',*common,'--workers','2','--preflight')
        count=len(state['requests'])
        command('koevd-pipeline',*common,'--workers','1')
        assert len(state['requests'])==count==12
    command('koevd-results','index','--run-dir',root/'run','--output',root/'index.json')
    command('koevd-results','export','--run-dir',root/'run','--trusted-index',root/'index.json','--output',root/'results.json')
    command('koevd-results','validate','--input',root/'results.json','--trusted-index',root/'index.json')
    command('koevd-results','report','--input',root/'results.json','--trusted-index',root/'index.json','--output-dir',root/'report')
    result=read_document(root/'results.json');index=read_document(root/'index.json');validate_results(result,index)
    assert any(r['response']['finish_reason']=='length' for r in result['records'] if r['task']==3)
    assert all(r['response']['execution']['attempts'][0]['client_controls']['workers']==2 for r in result['records'])
    definition=read_document(checkout/'configs/protocols/koevd-core-canonical-v1.json')
    assert preparation_identity()==definition['preparation_sha256']
    evidence={'scope':'SYNTHETIC_LOCAL_HTTP_ONLY','commands':commands,'http_requests':12,'benchmark_requests':10,
              'probe_requests':2,'exported_records':12,'resume_extra_requests':0,
              'peak_concurrent_requests':state['peak'],'installed_package':str(Path(koevd_eval.__file__).resolve()),
              'length_metadata_preserved':True,'client_controls_preserved':True,
              'pinned_preparation_unchanged':True,'utf8_log_capture':True}
    (root/'cli-evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    names=['results.json','index.json','doctor.json','cli-evidence.json','report/profile.json']
    (root/'SHA256.json').write_text(json.dumps({n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in names},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in evidence.items() if k not in ('commands','installed_package')},indent=2))


if __name__=='__main__':main()
