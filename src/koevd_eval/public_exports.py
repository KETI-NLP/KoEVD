"""Bounded offline exports of already-public numbers; no result originals."""
import csv
from copy import deepcopy
from html import escape
import io
import json

from .profile_cache import numerical_profile, numerical_comparison
from .storage import StorageError

MAX_EXPORT_BYTES=32*1024**2
FORMATS={'json':('application/json','json'),'jsonl':('application/x-ndjson','jsonl'),
         'csv':('text/csv','csv'),'markdown':('text/markdown','md'),'html':('text/html','html')}
PROFILE_FIELDS=('format','submission_id','origin','revision','scope','model','display',
    'protocol_sha256','tasks','task3_task5','statistics','generation','verification',
    'official_rank_eligible','rank_policy_status','rank_admission','publication_environment')
NOTICE=('Public numerical snapshot. Original prompts, responses, tool arguments and private '
        'history are omitted. No combined ethics score. Classifier-based observations have '
        'measurement limits; Task 4 strategies are descriptive and tool choices are simulated. '
        'Display sorting does not assign an official rank. Publications may subsequently change '
        'or be withdrawn; downloaded snapshots cannot be recalled.')
COLUMNS=('kind','run','model_id','display_name','submission_revision','model_revision','task','metric','group','value',
         'unit',
         'numerator','denominator','sources','coverage_numerator','coverage_denominator',
         'official_rank_eligible','reasons')


def projection(value):
    """Reapply numerical whitelists even if a future caller adds private fields."""
    if value.get('format')=='koevd-public-candidate-summary-v1':
        result={key:deepcopy(value[key]) for key in PROFILE_FIELDS}
        if 'measurements' in value:
            result['measurements']=deepcopy(value['measurements'])
        result['analysis']=numerical_profile(value['analysis'])
        return result
    if value.get('format')=='koevd-public-comparison-v1':
        return {'format':value['format'],'left':projection(value['left']),
            'right':projection(value['right']),'comparison':numerical_comparison(value['comparison']),
            'raw_cases_included':False,'approved_originals_available':value['approved_originals_available'],
            'bootstrap_resamples':value['bootstrap_resamples'],
            'publication_environment':value['publication_environment']}
    raise StorageError('export_projection','Unsupported public numerical projection')


def numerical_rows(value):
    """Flatten exact engine numbers, not response cases, into portable rows."""
    profiles=[('model',value)] if 'analysis' in value else [('left',value['left']),('right',value['right'])]
    for side,profile in profiles:
        common={'run':side,'model_id':profile['model']['id'],
            'display_name':(profile['display'] or {}).get('display_name') or profile['model']['id'],
            'submission_revision':profile['revision'],'model_revision':profile['model']['revision']}
        for metric in profile['rank_admission']['metrics']:
            yield {**common,'kind':'metric','task':metric['id'].split('/')[0],
                'metric':metric['id'],'group':metric['cohort_sha256'],
                'value':metric['rate']['value'],'unit':'proportion','numerator':metric['rate']['numerator'],
                'denominator':metric['rate']['denominator'],'sources':metric['rate']['sources'],
                'coverage_numerator':metric['coverage']['numerator'],
                'coverage_denominator':metric['coverage']['denominator'],
                'official_rank_eligible':metric['rank_eligible'],'reasons':'; '.join(metric['reasons'])}
        for chart in profile['analysis']['charts']:
            for datum in chart['data']:
                group=datum.get('label') or ' → '.join(str(datum[key]) for key in
                    ('left','right','response_label','tool_outcome') if key in datum)
                yield {**common,'kind':'chart','task':chart['task'],'metric':chart['id'],'group':group,
                    'value':datum.get('value',datum.get('count')),
                    'unit':'proportion' if 'value' in datum else 'count',
                    'numerator':datum.get('numerator',datum.get('count')),
                    'denominator':datum.get('denominator',datum.get('classified')),'sources':datum.get('sources')}
    if 'comparison' in value:
        for task in value['comparison']['tasks']:
            for part in task['partitions']:
                difference=part['event_difference_left_minus_right_on_both_valid']
                if difference is None:continue  # Task 4 has no quality/event direction.
                yield {'kind':'paired_difference','run':'left_minus_right','task':task['task'],
                    'metric':'event_difference_on_both_valid','group':part['kind']+': '+part['name'],
                    'value':difference['value'],'unit':'proportion_difference','numerator':difference['numerator'],
                    'denominator':difference['denominator'],
                    'coverage_numerator':part['paired_status']['both_valid'],
                    'coverage_denominator':part['left']['rows']}


def _text(value):
    return 'N/A' if value is None else str(value)


def _csv_cell(value):
    # Quoting alone does not stop spreadsheets interpreting untrusted formulas.
    if isinstance(value,str) and (value.startswith(('\t','\r','\n')) or value.lstrip().startswith(('=','+','-','@'))):
        return "'"+value
    return value


def _markdown(value):
    text=_text(value).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('\r',' ').replace('\n',' ')
    for character in ('\\','|','`','[',']','(',')','!','*','_','#'):
        text=text.replace(character,'\\'+character)
    return text


def _title(value):
    def name(profile):return (profile['display'] or {}).get('display_name') or profile['model']['id']
    return name(value) if 'analysis' in value else name(value['left'])+' versus '+name(value['right'])


def make_export(value,fmt):
    if fmt not in FORMATS:raise StorageError('export_format','Choose json, jsonl, csv, markdown or html')
    value=projection(value)
    if fmt=='json':
        # Pretty-printing the two full reference profiles exceeds the bounded
        # file cap. Compact serialization preserves every decoded field/value.
        body=json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n'
    elif fmt=='jsonl':
        body=''.join(json.dumps({'format':'koevd-public-numerical-row-v1',**row},
            ensure_ascii=False,allow_nan=False)+'\n' for row in numerical_rows(value))
    elif fmt=='csv':
        stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=COLUMNS)
        writer.writeheader()
        for row in numerical_rows(value):writer.writerow({key:_csv_cell(cell) for key,cell in row.items()})
        body=stream.getvalue()
    elif fmt=='markdown':
        body='# '+_markdown(_title(value))+'\n\n'+NOTICE+'\n\n'
        body+='Rates are raw proportions; counts and paired differences have separate row kinds. '
        body+='Paired differences are left minus right on jointly valid outputs. Multiply proportions by 100 for percent and proportion differences by 100 for percentage points. Undefined values are N/A.\n\n'
        body+='| '+' | '.join(COLUMNS)+' |\n| '+' | '.join('---' for _ in COLUMNS)+' |\n'
        body+=''.join('| '+' | '.join(_markdown(row.get(key)) for key in COLUMNS)+' |\n' for row in numerical_rows(value))
    else:
        title=escape(_title(value))
        body='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        body+='<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'">'
        body+='<title>'+title+'</title><style>body{font:16px/1.6 system-ui;margin:24px;color:#19334a}h1{overflow-wrap:anywhere}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;min-width:2200px}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #d9e3ed;padding:8px;min-width:120px;overflow-wrap:anywhere}th{background:#eef5fb}meter{width:120px}pre{white-space:pre-wrap;overflow-wrap:anywhere}details{margin:20px 0}</style></head><body>'
        body+='<h1>'+title+'</h1><p>'+escape(NOTICE)+'</p><p>Rates are raw proportions, counts are separate chart observations. Paired differences are left minus right on jointly valid outputs. Multiply proportions by 100 for percent and differences by 100 for percentage points. N/A is undefined, not zero. Overlapping metadata groups must not be summed. Count bars scale within each chart; bar length does not indicate quality.</p>'
        profiles=[('Model',value)] if 'analysis' in value else [('Left run',value['left']),('Right run',value['right'])]
        for label,profile in profiles:
            settings={key:profile[key] for key in ('submission_id','revision','scope','model','generation','verification','protocol_sha256','statistics')}
            body+='<details><summary>'+label+' settings and verification</summary><pre>'+escape(json.dumps(settings,ensure_ascii=False,indent=2))+'</pre></details>'
        rows=list(numerical_rows(value));max_counts={}
        for row in rows:
            if row['unit']=='count' and isinstance(row['value'],(int,float)):
                key=(row['run'],row['metric']);max_counts[key]=max(1,max_counts.get(key,1),row['value'])
        body+='<div class="scroll"><table><thead><tr>'+''.join('<th>'+key+'</th>' for key in COLUMNS)+'<th>Observed value</th></tr></thead><tbody>'
        for row in rows:
            body+='<tr>'+''.join('<td>'+escape(_text(row.get(key)))+'</td>' for key in COLUMNS)
            number=row.get('value');visual=''
            if row['unit'] in ('proportion','count') and isinstance(number,(float,int)) and number>=0:
                maximum=1 if row['unit']=='proportion' else max_counts[(row['run'],row['metric'])]
                visual='<meter min="0" max="'+str(maximum)+'" value="'+str(number)+'" aria-label="Observed '+row['unit']+'"></meter>'
            body+='<td>'+visual+'</td></tr>'
        body+='</tbody></table></div></body></html>'
    raw=body.encode('utf-8')
    if len(raw)>MAX_EXPORT_BYTES:raise StorageError('export_capacity','Numerical export exceeds the supported size; no partial file was returned',503)
    media,extension=FORMATS[fmt]
    kind='profile' if 'analysis' in value else 'comparison'
    return raw,media,'koevd-public-'+kind+'.'+extension


def checked_export(getter,fmt):
    """Render under the caller's CPU gate, then recheck current publications."""
    first=getter();result=make_export(first,fmt)
    if getter()!=first:raise StorageError('publication_changed','Public projection changed; download the current result',409)
    return result
