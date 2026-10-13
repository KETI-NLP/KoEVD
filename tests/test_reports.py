from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import tempfile
import unittest
import hashlib
import base64
import os
import shutil
import subprocess
from importlib.resources import files

from koevd_eval.diagnostics import analyze_many, filter_cases, comparison_cases, write_analysis
from koevd_eval.reports import render_html, prepare_view, inert_json
from koevd_eval.results import _seal, canonical_hash
import test_results


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False);self.scripts=[];self.styles=[];self.active=None;self.policy=None
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='meta' and attrs.get('http-equiv')=='Content-Security-Policy':self.policy=attrs['content']
        if tag in ('script','style'):
            self.active={'tag':tag,'attrs':attrs,'text':''}
            (self.scripts if tag=='script' else self.styles).append(self.active)
    def handle_data(self,data):
        if self.active:self.active['text']+=data
    def handle_endtag(self,tag):
        if self.active and tag==self.active['tag']:self.active=None


class OfflineReportTests(unittest.TestCase):
    def setUp(self):
        f=test_results.ResultContractTests('test_roundtrip_preserves_union_variants_failures_unknowns_and_privacy');f.setUp()
        self.addCleanup(f.temp.cleanup);self.document=f.document;self.index=f.index

    def test_untrusted_text_cannot_end_json_script_or_create_active_markup(self):
        d=deepcopy(self.document)
        attack='</script><script>globalThis.__KOEVD_INJECTED__=1</script><img src="https://invalid.example/x"> & 한국어 \u2028 \u2029'
        d['run']['model']['id']='SYNTHETIC-'+attack
        for r in d['records']:
            if r['task'] in (3,4) and r['response']['status']=='ok':
                r['response']['text']=attack;r['response']['sha256']=canonical_hash(attack)
                r['measurement']['response_sha256']=r['response']['sha256']
        d=_seal({k:v for k,v in d.items() if k!='content_sha256'})
        analysis=analyze_many([(d,self.index)],resamples=0)
        before=deepcopy(analysis);text=render_html(analysis,title=attack)
        parsed=Scripts();parsed.feed(text)
        self.assertEqual(len(parsed.scripts),2)
        self.assertEqual(len(parsed.styles),1)
        self.assertNotIn('<img',text)
        self.assertNotIn('<script>globalThis',text)
        raw=json.loads(parsed.scripts[0]['text'])
        self.assertEqual(raw['runs'][0]['run']['model']['id'],'SYNTHETIC-'+attack)
        self.assertEqual(next(c for c in raw['runs'][0]['cases'] if c['task']==3 and c['response']['status']=='ok')['response']['text'],attack)
        self.assertEqual(analysis,before)
        self.assertEqual(json.loads(inert_json({'x':attack}))['x'],attack)

    def test_csp_matches_embedded_code_and_disallows_external_sources(self):
        analysis=analyze_many([(self.document,self.index)],resamples=0)
        p=Scripts();p.feed(render_html(analysis))
        script_hash=base64.b64encode(hashlib.sha256(p.scripts[1]['text'].encode()).digest()).decode()
        style_hash=base64.b64encode(hashlib.sha256(p.styles[0]['text'].encode()).digest()).decode()
        self.assertIn("script-src 'sha256-"+script_hash+"'",p.policy)
        self.assertIn("style-src 'sha256-"+style_hash+"'",p.policy)
        self.assertIn("connect-src 'none'",p.policy)
        self.assertIn("default-src 'none'",p.policy)
        self.assertNotIn('unsafe-inline',p.policy)
        self.assertNotIn('unsafe-eval',p.policy)
        self.assertTrue(all('src' not in s['attrs'] for s in p.scripts))
        for forbidden in ('innerHTML','eval(', 'fetch(', 'XMLHttpRequest', 'document.write('):
            self.assertNotIn(forbidden,p.scripts[1]['text'])

    @unittest.skipUnless(os.environ.get('KOEVD_TEST_NODE') or shutil.which('node'),'Optional Node presentation-helper parity check')
    def test_browser_helpers_match_python_case_filters_and_pair_states(self):
        a,b=deepcopy(self.document),deepcopy(self.document)
        b['run']['id']='other-run';b['run']['model']['id']='other-model'
        record=next(r for r in b['records'] if r['task']==1)
        record['response'].update(text='',status='error');record['response']['sha256']=canonical_hash('')
        record['measurement']['status']='not_applicable'
        b=_seal({k:v for k,v in b.items() if k!='content_sha256'})
        analysis=analyze_many([(a,self.index),(b,self.index)],resamples=0);view=prepare_view(analysis)
        tests=[]
        for p in analysis['runs']:
            for chart in p['charts']:
                for datum in chart['data']:
                    if 'case_filter' in datum:
                        filt=datum['case_filter'];expected=filter_cases(analysis['runs'],filt)
                        tests.append({'filter':filt,'expected':[[c['artifact_sha256'],c['task'],c['sample_id']] for c in expected]})
        pairs=[]
        for task in range(1,6):
            for state in ('all','both_valid','left_only_valid','right_only_valid','both_invalid','left_event_only','right_event_only'):
                expected=comparison_cases(analysis['comparisons'][0],analysis['runs'],task,state=state)
                pairs.append({'task':task,'state':state,'expected':[p['left']['sample_id'] for p in expected]})
        with tempfile.TemporaryDirectory() as folder:
            request=Path(folder)/'parity.json';request.write_text(json.dumps({'data':view,'filters':tests,'pairs':pairs}),encoding='utf-8')
            js="""const fs=require('node:fs'),assert=require('node:assert/strict');
const api=require(process.argv[1]),req=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const all=req.data.runs.flatMap(p=>p.cases);
for(const t of req.filters)assert.deepEqual(all.filter(c=>api.matches(c,t.filter)).map(c=>[c.artifact_sha256,c.task,c.sample_id]),t.expected);
for(const t of req.pairs)assert.deepEqual(api.pairedCases(req.data,req.data.comparisons[0],t.task,'all','all',t.state).map(p=>p.left.sample_id),t.expected);
assert.equal(api.percent(null),'N/A');assert.equal(api.percent(0),'0.0%');
console.log(JSON.stringify({filters:req.filters.length,pair_states:req.pairs.length,status:'passed'}));"""
            node=os.environ.get('KOEVD_TEST_NODE') or shutil.which('node')
            result=subprocess.run([node,'-e',js,str(files('koevd_eval').joinpath('assets/report.js')),str(request)],capture_output=True,text=True,encoding='utf-8',check=True,timeout=30)
            self.assertEqual(json.loads(result.stdout)['status'],'passed')
            self.assertGreater(json.loads(result.stdout)['filters'],100)

    def test_view_fields_use_trusted_python_filter_semantics_and_keep_undefined(self):
        analysis=analyze_many([(self.document,self.index)],resamples=0)
        view=prepare_view(analysis);self.assertEqual(view['runs'][0]['charts'],analysis['runs'][0]['charts'])
        for c in view['runs'][0]['cases']:
            self.assertIn('evaluation_subset',c['view']['axis_values'])
            if c['task']==5:self.assertEqual(c['view']['paired_response_label'],'unclassified')
        self.assertIsNone(view['runs'][0]['tasks']['3']['partitions'][0]['rates']['event_on_valid']['value'])
        with tempfile.TemporaryDirectory() as folder:
            write_analysis(analysis,folder)
            html=(Path(folder)/'report-v2.html').read_text(encoding='utf-8')
            parser=Scripts();parser.feed(html)
            self.assertEqual(json.loads(parser.scripts[0]['text'])['runs'][0]['tasks'],analysis['runs'][0]['tasks'])
            self.assertEqual(len(json.loads(parser.scripts[0]['text'])['runs'][0]['cases']),12)
        with self.assertRaises(ValueError):render_html({'format':'summary-only','runs':[]})


if __name__=='__main__':unittest.main()
