"""Redraw selected paper aggregates; no raw model responses are required."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

def bars(frame,label,value,title,out):
    frame=frame.copy()
    fig,ax=plt.subplots(figsize=(9,max(3.5,len(frame)*.36+1.8)),layout='constrained')
    ax.barh(frame[label].astype(str),frame[value],color='#39698a')
    ax.invert_yaxis(); ax.set_xlabel(value); ax.set_title(title)
    ax.spines[['top','right']].set_visible(False)
    ax.bar_label(ax.containers[0],fmt='%.2f',padding=4,fontsize=8)
    ax.margins(x=.18)
    for extension in ['png','svg']: fig.savefig(out.with_suffix('.'+extension),dpi=180)
    plt.close(fig)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--tables-dir',type=Path,default=Path(__file__).resolve().parents[1]/'paper_assets/tables')
    p.add_argument('--output-dir',type=Path,required=True); a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    specs=[
        ('appendix_f_task1_full_severity_summary.csv','Severity band','Model-mean unsafe judgment rate (%)','Task 1: full-corpus severity view','task1_severity'),
        ('appendix_h_task3_model_summary.csv','Model','Unsafe/classified (%)','Task 3: unsafe generations among classified responses','task3_models'),
        ('appendix_i_task4_model_strategy_clusters.csv','Model','Dominant included rate (%)','Task 4: dominant strategy inclusion (descriptive)','task4_dominant_strategy'),
        ('appendix_j_task5_variant_summary.csv','Variant','Unsafe tool-call rate (%)','Task 5: unsafe mock calls / all prompted rows','task5_framing'),
        ('appendix_k_single_label_reliability.csv','field','krippendorff_alpha','IAA: nominal Krippendorff alpha','iaa_nominal'),
    ]
    for filename,label,value,title,name in specs:
        frame=pd.read_csv(a.tables_dir/filename,encoding='utf-8-sig')
        if name=='task4_dominant_strategy':
            frame[label]=frame[label]+' / '+frame['Dominant included strategy']
        bars(frame,label,value,title,a.output_dir/name)
    t2=pd.read_csv(a.tables_dir/'appendix_g_task2_metadata_accuracy_summary.csv',encoding='utf-8-sig')
    bars(t2[t2['Axis']=='Severity band'],'Value','Accuracy on answered items (%)','Task 2: severity aggregates (answered denominator)',a.output_dir/'task2_severity')
    overlap=pd.read_csv(a.tables_dir/'task3_task5_overlap_verified.csv',encoding='utf-8-sig')
    fig,ax=plt.subplots(figsize=(10,5),layout='constrained')
    xs=list(range(len(overlap))); width=.34
    ax.bar([x-width/2 for x in xs],overlap['p_task5_unsafe_given_task3_safe_all_matched_pct'],width,label='Task 3 safe',color='#39698a')
    ax.bar([x+width/2 for x in xs],overlap['p_task5_unsafe_given_task3_unsafe_all_matched_pct'],width,label='Task 3 unsafe',color='#ba683e')
    ax.set_xticks(xs,overlap['variant']); ax.set_ylabel('Unsafe mock calls / all matched rows (%)')
    ax.set_title('Task 3 / Task 5: conditional rates by framing'); ax.legend(); ax.spines[['top','right']].set_visible(False)
    for extension in ['png','svg']: fig.savefig(a.output_dir/('task3_task5_conditional.'+extension),dpi=180)
    plt.close(fig)
    print('Wrote seven aggregate redraws as PNG and SVG:',a.output_dir)

if __name__=='__main__': main()
