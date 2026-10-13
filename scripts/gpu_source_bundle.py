"""Prepare/verify a bounded source-only bundle for a GPU node (no extraction)."""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
import stat
import subprocess
import zipfile

FORMAT='koevd-gpu-source-bundle-v1'
MAX_TOTAL=64*1024*1024
MAX_FILE=16*1024*1024
MAX_FILES=2000
ROOTS=('src','tests','configs','apps','examples','scripts','docs','LICENSES')
TOP=('pyproject.toml','README.md','LICENSE','NOTICE.md','CITATION.cff','gpu_release_lock.json')
PUBLIC_CONFIGS=('.github/workflows/test.yml',)
BUILD_RECIPES=('apps/spaces/Dockerfile','apps/spaces/managed.Dockerfile','apps/spaces/public.Dockerfile')
EXTENSIONS={'.py','.json','.css','.js','.html','.toml','.md','.txt','.yml','.yaml','.cjs','.sh','.ps1'}
BUILD_METADATA_SUFFIXES=('.egg-info','.dist-info')


def sha(value): return hashlib.sha256(value).hexdigest()


def safe_name(name):
    p=PurePosixPath(name)
    if (not name or p.is_absolute() or p.as_posix()!=name or '..' in p.parts
            or '\\' in name or ':' in name or '\x00' in name):
        raise ValueError('Noncanonical or unsafe archive path')
    return name


def collect_sources(repo):
    repo=Path(repo).resolve()
    files={}
    candidates=[repo/name for name in (*TOP,*PUBLIC_CONFIGS) if (repo/name).is_file()]
    for root in ROOTS:
        if (repo/root).exists(): candidates.extend((repo/root).rglob('*'))
    for p in sorted(candidates):
        if not p.is_file():continue
        relative=p.relative_to(repo)
        # Wheel/editable builds can leave generated metadata under src/. Its
        # SOURCES.txt changes on every build and is not executable source.
        if any(part.lower().endswith(BUILD_METADATA_SUFFIXES) for part in relative.parts):continue
        if (relative.as_posix() not in PUBLIC_CONFIGS
                and any(part.startswith('.') or part=='__pycache__' for part in relative.parts)):continue
        if p.name not in TOP and relative.as_posix() not in BUILD_RECIPES and p.suffix.lower() not in EXTENSIONS:continue
        if p.is_symlink() or not p.resolve().is_relative_to(repo):
            raise ValueError('Source symlink or path outside repository')
        if any(parent.is_symlink() for parent in p.parents if parent!=repo):
            raise ValueError('Symlink in source path')
        if p.stat().st_size>MAX_FILE:raise ValueError('Source file exceeds size limit')
        name=safe_name(relative.as_posix())
        raw=p.read_bytes()
        if re.search(rb'(?:hf_[A-Za-z0-9]{30,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|sk-(?:proj-)?[A-Za-z0-9_-]{32,})',raw):
            raise ValueError('Credential-like literal found in source file: '+name)
        files[name]=raw
    if len(files)>MAX_FILES or sum(map(len,files.values()))>MAX_TOTAL:
        raise ValueError('Source bundle exceeds size/count limits')
    return files


def build_source_zip(repo,output,*,head):
    if len(head)!=40 or any(c not in '0123456789abcdef' for c in head):
        raise ValueError('Expected actual forty-character Git HEAD')
    files=collect_sources(repo)
    if 'pyproject.toml' not in files or 'src/koevd_eval/classify_responses.py' not in files:
        raise ValueError('Not a KoEVD source checkout')
    manifest={'format':FORMAT,'head':head,'source_state':'local candidate including uncommitted source',
              'files':{name:{'sha256':sha(raw),'bytes':len(raw)} for name,raw in sorted(files.items())},
              'limitations':['Source integrity only, not GPU inference or accuracy evidence.',
               'No Git/build metadata, generated directories, environment credential files or model/data artifacts are included. Source docs can contain small validation summaries.',
               'Verify the externally supplied ZIP SHA-256 before running any bundled code.']}
    path=Path(output)
    path.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        archive.writestr('bundle-manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        for name,raw in sorted(files.items()):archive.writestr(name,raw)
    verified=verify_source_zip(path)
    assert verified==manifest
    return manifest


def verify_source_zip(path,expected_sha256=None):
    path=Path(path)
    if path.stat().st_size>MAX_TOTAL:raise ValueError('ZIP exceeds size limit')
    raw=path.read_bytes()
    if expected_sha256 is not None and sha(raw)!=expected_sha256:
        raise ValueError('ZIP checksum differs from independent expected checksum')
    with zipfile.ZipFile(path) as archive:
        entries=archive.infolist()
        if len(entries)>MAX_FILES+1 or sum(e.file_size for e in entries)>MAX_TOTAL:
            raise ValueError('Archive expansion/count exceeds limit')
        names=[]
        for entry in entries:
            safe_name(entry.filename)
            if entry.is_dir() or entry.file_size>MAX_FILE or entry.flag_bits&1:
                raise ValueError('Unsupported archive entry')
            if stat.S_ISLNK(entry.external_attr>>16):raise ValueError('Archive symlink rejected')
            names.append(entry.filename)
        if len(set(names))!=len(names) or len({n.casefold() for n in names})!=len(names):
            raise ValueError('Duplicate/case-colliding archive names')
        def unique(pairs):
            value={}
            for k,v in pairs:
                if k in value:raise ValueError('Duplicate manifest JSON key')
                value[k]=v
            return value
        manifest=json.loads(archive.read('bundle-manifest.json').decode('utf-8'),object_pairs_hook=unique)
        if not isinstance(manifest,dict) or manifest.get('format')!=FORMAT or not isinstance(manifest.get('files'),dict):
            raise ValueError('Unsupported source manifest')
        head=manifest.get('head')
        if not isinstance(head,str) or len(head)!=40 or any(c not in '0123456789abcdef' for c in head):
            raise ValueError('Invalid manifest HEAD')
        if set(names)!={'bundle-manifest.json',*manifest['files']}:
            raise ValueError('Archive and manifest file sets differ')
        for name,evidence in manifest['files'].items():
            content=archive.read(name)
            if not isinstance(evidence,dict) or evidence.get('bytes')!=len(content) or evidence.get('sha256')!=sha(content):
                raise ValueError('Source checksum/size mismatch')
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    build=sub.add_parser('build');build.add_argument('--repo',default='.');build.add_argument('--output',required=True)
    build.add_argument('--git',default='git')
    verify=sub.add_parser('verify');verify.add_argument('--zip',required=True);verify.add_argument('--expected-sha256')
    args=parser.parse_args()
    try:
        if args.command=='build':
            repo=Path(args.repo).resolve()
            head=subprocess.check_output([args.git,'-c','safe.directory='+str(repo),'-C',str(repo),
                                          'rev-parse','HEAD'],text=True).strip()
            manifest=build_source_zip(repo,args.output,head=head)
            print(json.dumps({'path':str(Path(args.output).resolve()),'sha256':sha(Path(args.output).read_bytes()),
                              'source_files':len(manifest['files']),'head':head}))
        else:
            manifest=verify_source_zip(args.zip,args.expected_sha256)
            print(json.dumps({'verified_source_integrity':True,'source_files':len(manifest['files']),
                              'head':manifest['head'],'gpu_inference_verified':False}))
    except (ValueError,OSError,KeyError,zipfile.BadZipFile,subprocess.CalledProcessError) as exc:
        parser.error(str(exc))


if __name__=='__main__':main()
