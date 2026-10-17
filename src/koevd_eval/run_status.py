"""Read-only pipeline readiness. Does not infer accuracy or exported-file freshness."""
from pathlib import Path

from .common import read_jsonl
from .profile import identity
from .results import read_document, _measurement_evidence
from .run_openai_compatible import unique_rows


def status_run(output):
    from .pipeline import verify_prepared
    output=Path(output)
    manifest=read_document(output/'pipeline.json')
    verify_prepared(output,manifest)
    tasks={}
    for task in (1,2,3,5):
        inputs=unique_rows(read_jsonl(output/manifest['inputs'][str(task)]['file']))
        path=output/f'task{task}_predictions.jsonl'
        rows=unique_rows(read_jsonl(path)) if path.exists() else {}
        if not set(rows)<=set(inputs) or any(identity(row)!=identity(inputs[k]) or
                row.get('evaluated_model')!=manifest.get('generation',{}).get('model') or
                row.get('api_status') not in ('ok','error') for k,row in rows.items()):
            raise ValueError(f'Task {task}: predictions do not match this run; inspect retained files')
        tasks[str(task)]={'expected':len(inputs),'generated':len(rows),
            'api_ok':sum(r['api_status']=='ok' for r in rows.values()),
            'failed':sum(r['api_status']=='error' for r in rows.values()),'pending':len(inputs)-len(rows)}
    generation_pending=bool(manifest.get('generation_retry_pending'))
    measurement_pending=bool(manifest.get('measurement_pending'))
    measurements={}
    for task in (3,4):
        if generation_pending or measurement_pending:
            measurements[str(task)]={'status':'pending_promotion'}
        elif str(task) in manifest.get('measurements',{}) or (output/f'task{task}_measured.jsonl').exists():
            try:
                rows,_=_measurement_evidence(output,manifest,task,unique_rows(read_jsonl(output/'task3_predictions.jsonl')))
                measurements[str(task)]={'status':'complete','measured':sum(bool(r.get('measurement')) for r in rows.values()),'rows':len(rows)}
            except (ValueError,OSError):
                measurements[str(task)]={'status':'invalid','action':'Inspect retained measurement evidence; do not edit hashes or delete traces to bypass validation.'}
        else:measurements[str(task)]={'status':'not_measured'}
    failures=sum(t['failed'] for t in tasks.values())
    missing=sum(t['pending'] for t in tasks.values())
    if measurement_pending and not generation_pending:
        next_action='Repeat the original classify command with the same settings to finish pending promotion before retrying generation.'
    elif generation_pending or missing or failures:
        next_action='Repeat the original --stage generate command with the same model, endpoint, decoding and provenance settings. Successful rows are reused. Then classify/report/export again.'
    elif measurement_pending:
        next_action='Repeat the original classify command with the same settings to finish pending promotion.'
    elif any(m['status']=='invalid' for m in measurements.values()):
        next_action='Inspect measurement integrity errors before continuing; retain the run and attempt directories.'
    elif any(m['status']!='complete' for m in measurements.values()):
        selected=' '.join(t for t,m in measurements.items() if m['status']=='not_measured')
        next_action='Run --stage classify --measurement-tasks '+selected+' with the required local adapter/base paths and recorded settings.'
    else:next_action='Run --stage report, then koevd-results export and validate using the original trusted index. Reexport after any generation or measurement change.'
    return {'format':'koevd-run-status-v1','tasks':tasks,'measurements':measurements,
        'failed_generation_rows':failures,'pending_generation_rows':missing,
        'generation_retry_pending':generation_pending,'measurement_promotion_pending':measurement_pending,
        'all_generation_requests_succeeded':not (failures or missing or generation_pending),
        'next_action':next_action,'interpretation':'Readiness only; API success is not parsing success or model accuracy. Validation is structural. Exported-file freshness is not checked. Failed rows stay in denominators.'}
