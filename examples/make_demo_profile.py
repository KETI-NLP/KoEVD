"""Synthetic formatting demonstration. These are NOT evaluated real-model results."""
import argparse
from pathlib import Path
from koevd_eval.common import write_jsonl
from koevd_eval.profile import write_report


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output-dir',default='generated/synthetic-demo')
    a=p.parse_args(); root=Path(a.output_dir); inputs={}
    for task in range(1,6):
        rows=[]
        for model in ('SYNTHETIC-A','SYNTHETIC-B'):
            for i in range(80):
                sid=f'demo-{i:03d}'; topic='topic-A' if i<40 else 'topic-B'
                bad=(i%4==0 if topic=='topic-A' else i%20==0) if model=='SYNTHETIC-A' else i%10==0
                variants=('choose_best','choose_unsafe','rejected_vs_accepted','relative_harmfulness') if task==2 else (('safe_guided','tool_forced','unsafe_induced') if task==5 else ('all',))
                for v in variants:
                    metadata={'source_id':sid,'topic':[topic],'severity_band':'High','explicitness':'Explicit' if i%2 else 'Implicit','utterance_type':'Question'}
                    r={'sample_id':f'{sid}:task{3 if task==4 else task}:{v}','task':f'task{3 if task==4 else task}',
                       'source':{'source_id':sid},'metadata':metadata,'messages':[{'role':'user','content':'Synthetic input for report testing.'}],
                       'evaluated_model':model,'api_status':'ok','gold':None,'prediction':'Synthetic response for report testing.'}
                    if task==1:r.update(gold={'label':'unsafe'},prediction='safe' if bad else 'unsafe')
                    if task==2:
                        metadata.update(task_variant=v,choices=[{'letter':'A'},{'letter':'B'}]); r.update(gold={'answer':'A'},prediction='B' if bad else 'A')
                    if task==3:r['measurement']={'label':'unsafe' if bad else 'safe'}
                    if task==4:r['measurement']={'strategies':['unsafe'] if bad else ['c_info providing']}
                    if task==5:
                        metadata['prompt_variant']=v
                        r['gold']={'available_tools':['mock_allowed','mock_unsafe'],'unsafe_tools':['mock_unsafe'],'allowed_tools':['mock_allowed'],'expected_decision':'refuse','gold_unsafe_tool_call':True}
                        r['prediction']='{"decision":"call_tool","tool_name":"mock_unsafe"}' if bad else '{"decision":"refuse"}'
                    if i==79:r.update(prediction='',api_status='error',measurement=None)
                    rows.append(r)
        path=root/f'task{task}.jsonl'; write_jsonl(path,rows); inputs[task]=[path]
    write_report(inputs,root/'report')
    print((root/'report/report.html').resolve())


if __name__=='__main__':main()
