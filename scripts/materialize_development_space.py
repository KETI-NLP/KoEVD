"""Build a reviewable, allowlisted CPU Space deployment folder; no upload."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil


def main():
    from koevd_eval.pipeline import prepare_run, save_json
    from koevd_eval.results import build_index, read_document
    from koevd_eval.space_service import InputCatalog
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',default='.')
    parser.add_argument('--dataset',required=True)
    parser.add_argument('--standard-index',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    repo=Path(args.repo).resolve(strict=True)
    out=Path(args.output).resolve()
    out.mkdir(exist_ok=False)
    def copy(relative):
        source=repo/relative
        if source.is_symlink():raise ValueError('Deployment source symlink rejected')
        dest=out/relative
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
    for name in ('pyproject.toml','LICENSE','NOTICE.md'):
        copy(name)
    # The fixed benchmark indexes are dataset derivatives, not Apache-2.0 code.
    shutil.copyfile(repo/'apps/static/DATA_LICENSE.md',out/'DATA_LICENSE.md')
    for folder in ('src','LICENSES','configs/protocols'):
        for path in sorted((repo/folder).rglob('*')):
            if path.is_file() and path.suffix in ('.py','.json','.js','.css','.html','.md'):
                copy(path.relative_to(repo))
    for name in ('launch.py','requirements.lock.txt'):
        copy(Path('apps/spaces')/name)
    shutil.copyfile(repo/'apps/spaces/Dockerfile',out/'Dockerfile')
    shutil.copyfile(repo/'apps/spaces/DEVELOPMENT_SPACE_README.md',out/'README.md')
    data=out/'operator-data';data.mkdir()
    # Actual dataset inputs; no generated responses, synthetic model baseline,
    # source upload directory or uploader-controlled gold is accepted here.
    full=data/'core-index.json'
    shutil.copyfile(args.standard_index,full)
    digest=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
    entries=[{'id':'koevd-core','label':'KoEVD full core · 17,670 records','mode':'standard',
              'path':'core-index.json','sha256':digest(full),'registry':'../configs/protocols',
              'protocol_id':'koevd-core-canonical-v1'}]
    dataset=read_document(repo/'configs/validation/platform-gpu-candidate-v1.json')['release_artifacts']['dataset']
    for count in (4,96):
        run=out.parent/(out.name+'-prepared-'+str(count))
        prepare_run(args.dataset,run,'core',count)
        index=build_index(run,dataset_repo=dataset['repo_id'],dataset_revision=dataset['revision'])
        filename='prefix-'+str(count)+'-index.json'
        save_json(data/filename,index)
        entries.append({'id':'koevd-prefix-'+str(count),'label':'KoEVD prefix '+str(count)+' · integration only',
                        'mode':'operator_custom','path':filename,'sha256':digest(data/filename)})
    save_json(data/'catalog.json',{'schema_version':'koevd-space-catalog-v1','indexes':entries,'baselines':[]})
    save_json(data/'roles.json',{'reviewers':[],'admins':[]})
    catalog=InputCatalog(data/'catalog.json')
    files={}
    for path in sorted(out.rglob('*')):
        if path.is_file():
            if path.is_symlink():raise ValueError('Deployment symlink rejected')
            files[str(path.relative_to(out)).replace('\\','/')]= {'bytes':path.stat().st_size,'sha256':digest(path)}
    save_json(out/'deployment-manifest.json',{'format':'koevd-private-development-space-v1','files':files,
        'storage':'ephemeral_development','official_rank_eligible':False,'catalog':catalog.public(),
        'credentials_included':False,'actual_target_outputs_included':False})
    print(json.dumps({'deployment_root':str(out),'files':len(files),'bytes':sum(v['bytes'] for v in files.values()),
                      'catalog':catalog.public(),'uploaded':False}))


if __name__=='__main__':main()
