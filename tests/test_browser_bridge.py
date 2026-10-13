"""Trust/parity boundaries of the file bridge; browser execution is separate QA."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'examples'))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from make_demo_diagnostics import make_fixture
from make_demo_space import create_demo
from materialize_static_space import build, engine_sources, RUNTIME_FILES
from koevd_eval.browser_bridge import analyze_files
from koevd_eval.diagnostics import analyze_many, write_analysis
from koevd_eval.results import _seal


class BrowserBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.index,self.docs=make_fixture()
        self.index_path=self.root/'index.json';self.save(self.index_path,self.index)
        self.paths=[]
        for n,d in enumerate(self.docs):
            p=self.root/f'result-{n}.json';self.save(p,d);self.paths.append(p)

    def save(self,path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    def test_all_outputs_exact_common_engine_with_float_originals_and_intervals(self):
        expected=self.root/'expected';write_analysis(analyze_many([(d,self.index) for d in self.docs],resamples=20,seed=1729),expected)
        receipt=analyze_files(self.paths,[self.index_path],self.root/'actual',resamples=20)
        for name in receipt['files']:self.assertEqual((expected/name).read_bytes(),(self.root/'actual'/name).read_bytes())
        self.assertFalse(receipt['official_rank_eligible']);self.assertFalse(receipt['publication_performed'])

    def test_scores_missing_stale_and_unconfigured_index_rejected(self):
        for change in ('scores','missing','stale','index','publication'):
            d=deepcopy(self.docs[0])
            if change=='scores':d['scores']={'safety':1}
            if change=='missing':d['records'].pop()
            if change=='stale':next(r for r in d['records'] if r['task']==3)['measurement']['response_sha256']='0'*64
            if change=='index':d['input_index_sha256']='0'*64
            if change=='publication':d['publication']['status']='published'
            p=self.root/(change+'.json');self.save(p,_seal({k:v for k,v in d.items() if k!='content_sha256'}))
            with self.subTest(change=change),self.assertRaises(ValueError):analyze_files([p],[self.index_path],self.root/('out-'+change),resamples=0)

    def test_duplicate_results_and_empty_selection_rejected(self):
        for paths in ([],self.paths[:1]*2,self.paths*3):
            with self.assertRaises(ValueError):analyze_files(paths,[self.index_path],self.root/'bad',resamples=0)

    def test_materializer_copies_only_audited_sources_and_runtime(self):
        repo=Path(__file__).resolve().parents[1];catalog=create_demo(self.root/'demo')
        runtime=self.root/'runtime';runtime.mkdir()
        import hashlib
        for name in RUNTIME_FILES:(runtime/name).write_bytes(b'CPU packaging fixture, not actual runtime')
        self.save(runtime/'runtime-manifest.json',{'version':'0.29.3','files':{n:{'sha256':hashlib.sha256((runtime/n).read_bytes()).hexdigest()} for n in RUNTIME_FILES}})
        (runtime/'private-credential.txt').write_text('must not be copied')
        out=self.root/'candidate';m=build(repo,catalog,runtime,out,allow_synthetic=True)
        self.assertEqual((out/'DATA_LICENSE.md').read_bytes(),(repo/'apps/static/DATA_LICENSE.md').read_bytes())
        self.assertIn('DATA_LICENSE.md',m['files'])
        self.assertFalse((out/'runtime/private-credential.txt').exists())
        import zipfile
        with zipfile.ZipFile(out/'engine.zip') as z:
            for name,p in engine_sources(repo).items():self.assertEqual(z.read(name),p.read_bytes())
            self.assertFalse(any('classif' in n or 'storage.py' in n for n in z.namelist()))
        self.assertFalse(m['deployed']);self.assertFalse(m['official_rank_eligible'])

    def test_actual_unapproved_reference_is_rejected_before_candidate_creation(self):
        catalog=create_demo(self.root/'demo');d=json.loads(catalog.read_text())
        d['baselines'][0]['scope']='actual_target_outputs'
        d['baselines'][0]['publication_evidence']={'consent':None,'rights':None,'evidence_path':None,'evidence_sha256':None}
        self.save(catalog,d);out=self.root/'rejected'
        with self.assertRaises(ValueError):build(Path(__file__).resolve().parents[1],catalog,self.root/'no-runtime',out,allow_synthetic=True)
        self.assertFalse(out.exists())
