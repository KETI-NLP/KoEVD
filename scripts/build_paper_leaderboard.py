"""Build numerical paper references from checked-in, aggregate-only source CSVs."""
import csv
import hashlib
import json
from pathlib import Path

ALIASES = dict(zip(
    ['apertus-8b-instruct-vllm','claude-4.6-sonnet','claude-haiku-4-5','gemini-3.1-flash-lite-preview','gemma-4-e4b-it-vllm','gpt-5.4','gpt-5.4-nano','ministral-3-8b-reasoning-vllm','olmo-3-7b-think-vllm','qwen3.5-9b-vllm','qwen3.6-27b-fp8-vllm'],
    ['Apertus 8B','Claude 4.6 Sonnet','Claude Haiku 4.5','Gemini 3.1 Flash-Lite','Gemma 4 E4B','GPT-5.4','GPT-5.4 Nano','Ministral 3 8B','OLMo 3 7B','Qwen3.5 9B','Qwen3.6 27B']))


def build(root):
    root = Path(root)
    sources = []
    def read(name):
        path = 'paper_assets/tables/' + name + '.csv'
        raw = (root / path).read_bytes()
        rows = list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
        sources.append({'path': path, 'sha256': hashlib.sha256(raw).hexdigest(), 'rows': rows})
        return rows
    def indexed(name):
        rows = read(name)
        assert len({r['Model'] for r in rows}) == len(rows), name
        return {r['Model']: r for r in rows}
    coverage = indexed('appendix_f_task1_model_coverage')
    variants = {**indexed('appendix_g_task2_open_model_variant_accuracy'),
                **indexed('appendix_g_task2_commercial_model_variant_accuracy')}
    native_means = {**indexed('appendix_g_task2_open_model_summary'),
                    **indexed('appendix_g_task2_commercial_model_summary')}
    safety = indexed('appendix_h_task3_model_summary')
    strategy = indexed('appendix_i_task4_model_top_strategy_summary')
    strategy_counts = indexed('appendix_i_task4_model_summary')
    strategy_rates = indexed('appendix_i_task4_model_included_strategy_heatmap_values')
    tools = indexed('appendix_j_task5_model_summary')
    tool_variants = read('appendix_j_task5_model_variant_summary')
    judgments = read('task1_full_high_coverage_model_rates')
    assert len(coverage) == 12
    assert all(set(x) == set(coverage) for x in (variants,native_means,safety,strategy,strategy_counts,strategy_rates,tools))
    assert set(r['model'] for r in judgments) == set(ALIASES)
    assert len({(r['model'],r['utter_type'],r['toxicity']) for r in judgments}) == len(judgments)
    models = []
    for name, cov in coverage.items():
        rows = [r for r in judgments if ALIASES[r['model']] == name]
        n = sum(int(r['effective']) for r in rows)
        unsafe = sum(int(r['unsafe']) for r in rows)
        if rows: assert n == int(cov['Effective source judgments']), name
        bands = []
        for band in sorted({r['toxicity'] for r in rows}):
            subset = [r for r in rows if r['toxicity'] == band]
            bands.append({'severity_code':band,'judgments':sum(int(r['effective']) for r in subset),
                          'unsafe':sum(int(r['unsafe']) for r in subset)})
        common = ['Choose Best','Choose Unsafe','Relative Harmfulness']
        models.append({'name':name,'cohort':cov['Cohort'],
            'task1':{'coverage':cov,'judgments':n if rows else None,'unsafe':unsafe if rows else None,
                     'unsafe_rate':unsafe/n if n else None,'by_severity':bands},
            'task2':{'variants':variants[name],'common_three_mean_pct':sum(float(variants[name][v]) for v in common)/3,
                     'original_summary':native_means[name]},
            'task3':safety[name], 'task4':strategy[name], 'task4_measurements':strategy_counts[name],
            'task4_rates':strategy_rates[name], 'task5':tools[name],
            'task5_variants':[r for r in tool_variants if r['Model']==name]})
        assert len(models[-1]['task5_variants']) == 3
    return {'format':'koevd-paper-leaderboard-v1','scope':'historical_aggregate_only',
        'notes':{'task1':'Full-source unsafe judgments describe model judgments, not error or ethical quality. Per-model judgment counts are available for 11 high-coverage models; Gemini 3.1 Pro has coverage only.',
                 'task2':'Unweighted mean of Choose Best, Choose Unsafe and Relative Harmfulness. Original open-model means used four variants; original commercial means used three. No answer counts are inferred from rounded percentages.',
                 'task3':'Original 13,552 prompts/model; inspect classified/all rates and generation skips. Classifier proxy, not independent safety ground truth.',
                 'task4':'Descriptive strategy inclusion; no quality direction. Released heatmap contains selected strategies, not all 15 labels.',
                 'task5':'Unsafe calls / all expected rows, pooled across three simulated tool-choice framings, with separate framing rows. No real tools executed.',
                 'comparison':'Aggregate comparison only; no matched-case, significance or independent verification claim. Do not pool with current protocol registrations.'},
        'models':sorted(models,key=lambda m:m['name']), 'sources':sources}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    data = build(root)
    (root/'src/koevd_eval/assets/paper_models.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'models':len(data['models']),'sources':len(data['sources'])}))
