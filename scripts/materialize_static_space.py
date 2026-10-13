"""Build an unpublished Static candidate using the exact common Python sources.

InputCatalog enforces independent inputs, registered standard sets and reference
publication rights before copying. No credentials, roles, private DB or actual
unapproved target outputs are included. Browser compute is not server acceptance.
"""
import argparse
import ast
import base64
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

RUNTIME_FILES = ('pyodide.js', 'pyodide.asm.js', 'pyodide.asm.wasm',
                 'python_stdlib.zip', 'pyodide-lock.json', 'LICENSE', 'PYTHON-LICENSE')
ASSETS = ('index.html', 'app.js', 'worker.js', 'style.css', 'README.md', 'DATA_LICENSE.md')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def engine_sources(repo):
    """Only the transitive Python imports of the analysis bridge, plus UI assets."""
    root = Path(repo) / 'src/koevd_eval'
    pending = ['browser_bridge']; modules = set()
    while pending:
        name = pending.pop()
        if name in modules: continue
        path = root / (name + '.py')
        if path.is_symlink(): raise ValueError('Engine symlink rejected')
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
        modules.add(name)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level == 1:
                imports = [node.module] if node.module else [a.name for a in node.names]
                pending.extend(n for n in imports if (root / (n + '.py')).is_file())
    paths = [root / '__init__.py', *[root / (n + '.py') for n in sorted(modules)],
             root / 'assets/report.js', root / 'assets/report.css']
    return {p.relative_to(root.parent).as_posix(): p for p in paths}


def build(repo, catalog_path, runtime_dir, output, *, allow_synthetic=False):
    from koevd_eval.space_service import InputCatalog
    repo = Path(repo).resolve(strict=True)
    catalog = InputCatalog(catalog_path, allow_synthetic=allow_synthetic)
    runtime = Path(runtime_dir).resolve(strict=True)
    receipt = json.loads((runtime / 'runtime-manifest.json').read_text(encoding='utf-8'))
    if receipt.get('version') != '0.29.3' or set(receipt['files']) != set(RUNTIME_FILES):
        raise ValueError('Require pinned Pyodide 0.29.3 runtime manifest')
    for name in RUNTIME_FILES:
        p = runtime / name
        if p.is_symlink() or sha(p) != receipt['files'][name]['sha256']:
            raise ValueError('Runtime file checksum mismatch')
    out = Path(output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    for name in ASSETS: shutil.copyfile(repo / 'apps/static' / name, out / name)
    # Blob frames inherit the parent's CSP. Permit only the same code-owned
    # report script/style hashes; uploaded strings never enter these hashes.
    page=(out/'index.html').read_text(encoding='utf-8')
    for marker,name in (('REPORT_SCRIPT_HASH','report.js'),('REPORT_STYLE_HASH','report.css')):
        raw=(repo/'src/koevd_eval/assets'/name).read_text(encoding='utf-8').encode('utf-8')
        page=page.replace(marker,base64.b64encode(hashlib.sha256(raw).digest()).decode('ascii'))
    (out/'index.html').write_text(page,encoding='utf-8',newline='\n')
    for name in ('LICENSE', 'NOTICE.md'): shutil.copyfile(repo / name, out / name)
    shutil.copytree(repo / 'LICENSES', out / 'LICENSES')
    (out / 'runtime').mkdir()
    # Copy only audited members; an unrelated operator file is never copied.
    for name in (*RUNTIME_FILES, 'runtime-manifest.json'):
        shutil.copyfile(runtime / name, out / 'runtime' / name)
        if name in RUNTIME_FILES and sha(out / 'runtime' / name) != receipt['files'][name]['sha256']:
            raise ValueError('Runtime changed while copying')
    sources = engine_sources(repo)
    with zipfile.ZipFile(out / 'engine.zip', 'x', zipfile.ZIP_DEFLATED) as z:
        for name, path in sorted(sources.items()):
            z.writestr(zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0)), path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
    config = {'format': 'koevd-static-candidate-v1', 'runtime_version': '0.29.3',
              'engine': {'path': 'engine.zip', 'sha256': sha(out / 'engine.zip')},
              'indexes': [], 'baselines': [], 'synthetic_demo_enabled': allow_synthetic,
              'official_rank_eligible': False, 'public_registration_enabled': False}
    data = out / 'data'; data.mkdir()
    raw_catalog = json.loads(Path(catalog_path).read_text(encoding='utf-8'))
    for n, item in enumerate(catalog.indexes.values()):
        original = next(e for e in raw_catalog['indexes'] if e['id'] == item['id'])
        source = Path(original['path'])
        if not source.is_absolute(): source = Path(catalog_path).resolve().parent / source
        dest = data / f'index-{n}.json'; shutil.copyfile(source, dest)
        if sha(dest) != original['sha256']: raise ValueError('Index changed while copying')
        config['indexes'].append({'path': dest.relative_to(out).as_posix(), 'sha256': sha(dest),
                                 'id': item['id'], 'label': item['label'], 'mode': item['mode']})
    for n, item in enumerate(catalog.baselines.values()):
        dest = data / f'reference-{n}.json'; shutil.copyfile(item['path'], dest)
        if sha(dest) != item['sha256']: raise ValueError('Reference changed while copying')
        config['baselines'].append({'path': dest.relative_to(out).as_posix(), 'sha256': sha(dest),
            **{k: item[k] for k in ('id', 'label', 'scope', 'index_id')}})
    (out / 'config.json').write_text(json.dumps(config, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    manifest = {'format': config['format'], 'deployed': False,
        'engine_sources': {n: {'sha256': sha(p), 'bytes': p.stat().st_size} for n,p in sources.items()},
        'files': {p.relative_to(out).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size}
                  for p in sorted(out.rglob('*')) if p.is_file()},
        'registration_backend': 'not_configured', 'official_rank_eligible': False}
    (out / 'deployment-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',default='.'); p.add_argument('--catalog',required=True)
    p.add_argument('--runtime-dir',required=True); p.add_argument('--output',required=True)
    p.add_argument('--demo',action='store_true')
    a=p.parse_args(); m=build(a.repo,a.catalog,a.runtime_dir,a.output,allow_synthetic=a.demo)
    print(json.dumps({'output':str(Path(a.output).resolve()),'files':len(m['files']), 'deployed':False}))
