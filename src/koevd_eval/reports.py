"""Self-contained offline renderer for the shared trusted diagnostic profile.

Only code-owned assets run. Responses/prompts/metadata are serialized as inert
JSON and displayed through textContent, never HTML, URL fetches or model calls.
"""
from __future__ import annotations

import base64
from copy import deepcopy
import hashlib
import html
from importlib.resources import files
import json
from pathlib import Path

from .profile import AXES, axis_values
from .diagnostics import VERSION, tool_outcome

RENDERER_VERSION='koevd-offline-html-v1'


def prepare_view(report):
    if report.get('format') != VERSION or not report.get('runs'):
        raise ValueError('Renderer requires a shared diagnostic analysis, not an uploaded result')
    view=deepcopy(report)
    view['renderer_version']=RENDERER_VERSION
    for profile in view['runs']:
        t3={c['source_id']:c for c in profile['cases'] if c['task']==3}
        for c in profile['cases']:
            previous=t3.get(c['source_id'])
            c['view']={'axis_values':{axis:axis_values(c,axis) for axis in (*AXES,'severity_band × explicitness')},
                'confusion':str((c['gold'] or {}).get('label','missing'))+'->'+str(c['parsed'] if c['valid'] else 'unparsed') if c['task']==1 else None,
                'tool_outcome':tool_outcome({'gold':c['gold']},(c['valid'],c['event'],c['parsed'])) if c['task']==5 else None,
                'paired_response_label':previous['parsed'] if previous and previous['valid'] else ('unclassified' if previous else 'missing')}
    return view


def inert_json(value):
    return json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e').replace('\u2028','\\u2028').replace('\u2029','\\u2029')


def _hash(value):
    return base64.b64encode(hashlib.sha256(value.encode('utf-8')).digest()).decode('ascii')


def render_html(report, title='KoEVD model diagnostics'):
    view=prepare_view(report)
    css=files('koevd_eval').joinpath('assets/report.css').read_text(encoding='utf-8')
    js=files('koevd_eval').joinpath('assets/report.js').read_text(encoding='utf-8')
    policy=f"default-src 'none'; script-src 'sha256-{_hash(js)}'; style-src 'sha256-{_hash(css)}'; img-src data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta http-equiv="Content-Security-Policy" content="'+html.escape(policy,quote=True)+'">'
        '<title>'+html.escape(title)+'</title><style>'+css+'</style></head><body>'
        '<a class="skip" href="#main">Skip to analysis</a><div id="app"></div>'
        '<noscript>This self-contained report needs JavaScript for charts and case exploration. '
        'The companion JSON, CSV and Markdown files retain all analysis values.</noscript>'
        '<script id="koevd-data" type="application/json">'+inert_json(view)+'</script>'
        '<script>'+js+'</script></body></html>\n')


def write_html(report,path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(render_html(report),encoding='utf-8',newline='\n')
    return path
