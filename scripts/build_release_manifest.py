"""Checksum the staged release files; ignored private outputs are not included."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess


def build(repo, version, *, git='git'):
    repo=Path(repo).resolve()
    command=[git,'-c','safe.directory='+repo.as_posix(),'-C',str(repo)]
    index=subprocess.check_output([*command,'ls-files','--stage','-z'])
    entries=[]
    for raw in index.split(b'\0'):
        if not raw:continue
        metadata,name=raw.split(b'\t',1);mode,blob,stage=metadata.split()
        name=name.decode('utf-8')
        if stage!=b'0' or mode not in (b'100644',b'100755'):raise ValueError('Unmerged/nonregular release file')
        if name=='manifest.json':continue
        if name.startswith(('generated/','.git/')) or Path(name).suffix in ('.safetensors','.sqlite3','.secret'):
            raise ValueError('Private artifact in release index')
        entries.append((name,blob))
    process=subprocess.run([*command,'cat-file','--batch'],input=b'\n'.join(blob for _,blob in entries)+b'\n',capture_output=True)
    if process.returncode:raise ValueError('Cannot read release index blobs')
    position=0;files=[]
    for name,blob in entries:
        end=process.stdout.index(b'\n',position);actual,kind,size=process.stdout[position:end].split()
        if actual!=blob or kind!=b'blob':raise ValueError('Unexpected Git blob')
        position=end+1;length=int(size);content=process.stdout[position:position+length];position+=length+1
        if re.search(rb'(?:hf_[A-Za-z0-9]{30,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{50,}|sk-(?:proj-)?[A-Za-z0-9_-]{32,})',content):
            raise ValueError('Credential-like literal in release')
        files.append({'path':name,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest()})
    return {'format':'sha256-file-manifest-v1','release_version':version,
            'basis':'exact staged Git blobs, excluding the manifest itself',
            'excludes':['manifest.json','.git','ignored build/cache/private artifacts'],'files':files}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',default='.');parser.add_argument('--version',required=True)
    parser.add_argument('--git',default='git');parser.add_argument('--output',default='manifest.json')
    args=parser.parse_args();manifest=build(args.repo,args.version,git=args.git)
    Path(args.output).write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(manifest['files']),'release_version':args.version,'private_outputs_included':False}))
