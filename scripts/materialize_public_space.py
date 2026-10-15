"""Allowlisted anonymous public-beta context, never raw reference originals."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def preserve_lfs_attributes(base, output):
    """Keep provider rules and declare large context assets before checkout."""
    source=Path(base)/'.gitattributes'
    if source.is_symlink():raise ValueError('Context attributes symlink rejected')
    inherited=source.read_bytes() if source.is_file() else b''
    if len(inherited)>65536:raise ValueError('Context attributes exceed supported size')
    lines=inherited.decode('utf-8').splitlines()
    additions=[]
    for path in sorted(Path(output).rglob('*')):
        if path.is_file() and path.stat().st_size>=10_000_000:
            name=path.relative_to(output).as_posix()
            pattern=json.dumps(name,ensure_ascii=False) if any(c.isspace() for c in name) else name
            rule=pattern+' filter=lfs diff=lfs merge=lfs -text'
            if rule not in lines:additions.append(rule)
    raw=inherited
    if additions:
        if raw and not raw.endswith(b'\n'):raw+=b'\n'
        raw+=('\n'.join(additions)+'\n').encode('utf-8')
    (Path(output)/'.gitattributes').write_bytes(raw)


def build(repo, base, references, output):
    from koevd_eval.results import read_document
    from koevd_eval.space_service import InputCatalog
    repo=Path(repo).resolve(strict=True);base=Path(base).resolve(strict=True)
    out=Path(output).resolve();out.mkdir(exist_ok=False)
    config=read_document(references,max_bytes=1024*1024)
    if config.get('format')!='koevd-reference-assets-v1' or config.get('bucket_id')!='KETI-NLP/KoEVD-Platform-Backups':
        raise ValueError('Expected explicitly configured production reference Bucket')
    if len(config['references'])!=2 or sum(e['bytes'] for e in config['references'])!=89396889:
        raise ValueError('Expected two exact verified reference originals')
    raw=read_document(base/'operator-data/catalog.json')
    if raw['baselines']:raise ValueError('Do not inherit raw baseline data from a development context')
    def copy(source, relative):
        source=Path(source)
        if source.is_symlink():raise ValueError('Context source symlink rejected')
        target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    for name in ('pyproject.toml','LICENSE','NOTICE.md','CITATION.cff'):copy(repo/name,name)
    copy(repo/'apps/static/DATA_LICENSE.md','DATA_LICENSE.md')
    for folder in ('src','LICENSES','configs/protocols'):
        for p in sorted((repo/folder).rglob('*')):
            if (p.is_file() and '__pycache__' not in p.parts and
                    not any(part.endswith(('.egg-info','.dist-info')) for part in p.parts) and
                    p.suffix in ('.py','.json','.js','.css','.html','.md')):
                copy(p,p.relative_to(repo))
    for name in ('public_launch.py','managed.requirements.lock.txt'):
        copy(repo/'apps/spaces'/name,Path('apps/spaces')/name)
    copy(repo/'apps/spaces/public.Dockerfile','Dockerfile')
    data=out/'operator-data';data.mkdir()
    for entry in raw['indexes']:
        source=(base/'operator-data'/entry['path']).resolve(strict=True)
        if source.parent!=(base/'operator-data').resolve() or source.is_symlink():
            raise ValueError('Index must be an exact local allowlisted file')
        if hashlib.sha256(source.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Index hash differs')
        copy(source,Path('operator-data')/source.name)
    (data/'catalog.json').write_text(json.dumps(raw,indent=2)+'\n',encoding='utf-8')
    InputCatalog(data/'catalog.json')
    (data/'reference-assets.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    permission={'format':'koevd-public-reference-permission-v1','date':'2026-10-13',
        'confirmed_by':'human rights holder','scope':'Approved research comparison of the two existing measured model results in the public beta',
        'originals_private':True,'raw_reference_text_public':False,
        'disclosure_policy':'koevd-public-reference-disclosure-v1',
        'originals':[{'id':e['id'],'file_sha256':e['sha256'],'records':17670} for e in config['references']],
        'terms':'KoEVD Dataset Research Use Terms v1.0; preserve attribution and harmful-content warning',
        'accuracy_or_official_rank_approval':False}
    (data/'reference-permission.json').write_text(json.dumps(permission,indent=2)+'\n',encoding='utf-8')
    (out/'README.md').write_text('''---
title: KoEVD Platform
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
license: apache-2.0
short_description: Multi-stage model diagnostics and research comparison
---

# KoEVD Platform — v0.2.0-rc.1 research beta

Upload your compatible results JSON, compare with the complete measured Qwen3-8B
and Qwen3-4B references, and download five analysis formats. Each reference has
17,670 records. No GPU inference runs in this Space.

Your uploads use isolated temporary analysis sessions (two-hour TTL); keep your
originals locally. Login, durable submissions, shared publication and official
ranking are not activated. Reference text is withheld in this beta, while every
measured record, numeric result and denominator is retained. Reports clearly mark
the disclosure projection; they are not portable original reference results.

KoEVD contains harmful and sensitive examples for research and safety evaluation.
The dataset and derivatives follow DATA_LICENSE.md, separate from Apache-2.0 code.
Classifier-safe is a proxy and does not establish real-world safety. Strategy
measurements are limited; Task 4 is descriptive. No combined ethics score.

Source and usage: https://github.com/KETI-NLP/KoEVD
Private analysis in your browser: https://huggingface.co/spaces/KETI-NLP/KoEVD-Explorer
Dataset: https://huggingface.co/datasets/KETI-NLP/KoEVD
''',encoding='utf-8')
    preserve_lfs_attributes(base,out)
    files={p.relative_to(out).as_posix():{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
           for p in sorted(out.rglob('*')) if p.is_file()}
    manifest={'format':'koevd-public-analysis-beta-context-v1','version':'0.2.0rc1','files':files,
              'raw_reference_originals_included':False,'credentials_included':False,
              'registration_enabled':False,'official_rank_eligible':False,'continuous_backup':False}
    (out/'deployment-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',default='.');parser.add_argument('--base-context',required=True)
    parser.add_argument('--reference-assets',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();m=build(args.repo,args.base_context,args.reference_assets,args.output)
    print(json.dumps({'files':len(m['files']),'bytes':sum(v['bytes'] for v in m['files'].values()),'uploaded':False}))
