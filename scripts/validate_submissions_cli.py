"""Exercise installed operator CLI on an explicitly acknowledged synthetic fixture.

No HTTP, OAuth, GPU inference, remote storage or external publication is performed.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

from koevd_eval.results import read_document


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result',required=True);p.add_argument('--index',required=True)
    p.add_argument('--output-dir',required=True)
    p.add_argument('--synthetic-fixture',action='store_true',required=True)
    a=p.parse_args()
    out=Path(a.output_dir).resolve()
    if out.exists():raise ValueError('Use a new output directory; preserve previous receipts')
    out.mkdir(parents=True)
    roles=out/'roles.json';roles.write_text(json.dumps({'reviewers':['SYNTHETIC-reviewer'],'admins':['SYNTHETIC-admin']}),encoding='utf-8')
    consent=out/'consent.json';consent.write_text(json.dumps({'scope':'responses','accepted':True,'rights_statement':'SYNTHETIC validation fixture; no actual external publication'}),encoding='utf-8')
    executable=Path(sys.executable).with_name('koevd-submissions.exe' if sys.platform=='win32' else 'koevd-submissions')
    if not executable.is_file():raise RuntimeError('Install the wheel before running this console-CLI check')
    base=[str(executable),'--store-dir',str(out/'store'),'--trusted-index',str(Path(a.index).resolve()),'--index-id','fixture','--roles-file',str(roles)]
    commands=[]
    def run(arguments,*,expected=0,store=None):
        command=list(base)
        if store is not None:command[command.index('--store-dir')+1]=str(store)
        command+=arguments
        started=time.perf_counter()
        result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=180)
        number=len(commands)
        (out/f'command-{number}.log').write_text(result.stdout+result.stderr,encoding='utf-8')
        commands.append({'arguments':arguments,'exit_code':result.returncode,'expected_exit':expected,'seconds':time.perf_counter()-started,'log':f'command-{number}.log'})
        if result.returncode!=expected:raise RuntimeError('Unexpected CLI status; inspect command log '+str(number))
        return json.loads(result.stdout if expected==0 else result.stderr)
    create=['--actor','SYNTHETIC-author','create','--input',str(Path(a.result).resolve()),'--key','create-1']
    state=run(create)['result'];sid=state['id']
    assert run(create)['result']==state
    assert run(['public-list'])['result']==[]
    assert run(['--actor','SYNTHETIC-other','get','--id',sid],expected=2)['error']=='not_found'
    def action(name,actor,extras=()):
        nonlocal state
        state=run(['--actor',actor,'action','--id',sid,'--name',name,'--expected-version',str(state['version']),
                   '--reason','SYNTHETIC installed CLI validation','--key',name+'-1',*extras])['result']
    action('request_review','SYNTHETIC-author',['--consent-file',str(consent)])
    action('start_review','SYNTHETIC-reviewer')
    action('approve','SYNTHETIC-reviewer',['--rights-evidence','SYNTHETIC permission review; no human safety gold'])
    action('publish','SYNTHETIC-admin')
    assert state['publication']['status']=='published'
    summary=run(['public-summary','--id',sid])['result'];assert summary['official_rank_eligible'] is False
    assert summary['publication_environment']=='local_candidate'
    public=out/'public-candidate-original.json'
    run(['public-result','--id',sid,'--output',str(public)])
    assert read_document(public)==read_document(a.result)
    before=run(['--actor','SYNTHETIC-author','history','--id',sid])['result']
    assert len(before['events'])==5
    action('withdraw','SYNTHETIC-author')
    assert run(['public-result','--id',sid,'--output',str(out/'must-not-exist.json')],expected=2)['error']=='not_found'
    assert not (out/'must-not-exist.json').exists()
    assert run(['public-list'])['result']==[]
    after=run(['--actor','SYNTHETIC-author','get','--id',sid])['result'];assert after['workflow']=='withdrawn'
    original=out/'private-retained-original.json'
    run(['--actor','SYNTHETIC-author','result','--id',sid,'--revision','1','--output',str(original)])
    assert read_document(original)==read_document(a.result)
    restore=out/'restore';backup=restore/'submissions.sqlite3'
    receipt=run(['--actor','SYNTHETIC-admin','backup','--output',str(backup)])['result']
    assert run(['--actor','SYNTHETIC-author','get','--id',sid],store=restore)['result']==after
    assert run(['public-list'],store=restore)['result']==[]
    evidence={'scope':'Synthetic CPU operator CLI only; no network, OAuth or actual inference','commands':commands,
              'submission_id':sid,'all_expected_statuses':True,'private_original_preserved':True,
              'public_projection_withdrawn':True,'restart_and_backup_restored_withdrawal':True,'backup':receipt,
              'official_rank_eligible':False,'external_publication':False}
    (out/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'commands':len(commands),'all_expected_statuses':True,'scope':'synthetic CPU only'}))


if __name__=='__main__':main()
