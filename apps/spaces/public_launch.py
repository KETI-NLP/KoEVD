"""Public anonymous CPU beta: pinned private references, projected public output.

No login, persistent submission, automatic backup, model inference or ranking.
The reference token is consumed during startup and never passed to the web app.
"""
from pathlib import Path
import hashlib
import json
import os
import tempfile


def pinned_reference_assets(config, destination, *, api):
    """Download exactly pinned objects from the private operator Bucket."""
    from koevd_eval.results import read_document
    config=read_document(config,max_bytes=1024*1024)
    if set(config)!={'format','bucket_id','references'} or config['format']!='koevd-reference-assets-v1':
        raise ValueError('Invalid reference asset configuration')
    bucket=config['bucket_id']
    if bucket!='KETI-NLP/KoEVD-Platform-Backups':raise ValueError('Unexpected reference Bucket')
    info=api.bucket_info(bucket)
    if info.id!=bucket or info.private is not True:raise ValueError('Reference Bucket must remain private')
    entries=config['references']
    if not isinstance(entries,list) or len(entries)!=2:raise ValueError('Two pinned references required')
    root=Path(destination);root.mkdir(mode=0o700,parents=True,exist_ok=True)
    result=[];total=0
    for entry in entries:
        if set(entry)!={'id','label','path','sha256','bytes'}:raise ValueError('Invalid reference entry')
        digest=entry['sha256']
        if len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):raise ValueError('Invalid digest')
        if entry['path']!='references/'+digest+'.json':raise ValueError('Unexpected object key')
        if type(entry['bytes']) is not int or not 0<entry['bytes']<=48*1024*1024:raise ValueError('Reference size limit')
        total+=entry['bytes']
        if total>90*1024*1024:raise ValueError('Combined reference size limit')
        dest=root/(digest+'.json')
        if not dest.exists():
            members=[]
            for number,item in enumerate(api.list_bucket_tree(bucket,prefix=entry['path'],recursive=False)):
                if number>=4:raise ValueError('Unexpected object listing')
                if item.path==entry['path']:members.append(item)
            if len(members)!=1 or members[0].size!=entry['bytes']:raise ValueError('Pinned object missing or changed')
            with tempfile.TemporaryDirectory(dir=root,prefix='.reference-') as temporary:
                staging=Path(temporary)/'download.json'
                api.download_bucket_files(bucket,files=[(members[0],staging)],raise_on_missing_files=True)
                if staging.is_symlink() or staging.stat().st_size!=entry['bytes'] or hashlib.sha256(staging.read_bytes()).hexdigest()!=digest:
                    raise ValueError('Pinned reference bytes differ')
                os.replace(staging,dest)
        if dest.is_symlink() or dest.stat().st_size!=entry['bytes'] or hashlib.sha256(dest.read_bytes()).hexdigest()!=digest:
            raise ValueError('Local reference bytes differ')
        result.append({**entry,'local_path':str(dest)})
    return result


def main():
    root=Path(__file__).resolve().parent
    host=os.environ.get('SPACE_HOST','').lower()
    if not host.endswith('.hf.space') or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-.' for c in host):
        raise ValueError('Expected provider SPACE_HOST')
    token=os.environ.pop('KOEVD_REFERENCE_TOKEN',None)
    if not token:raise ValueError('Set a read-only Bucket-scoped KOEVD_REFERENCE_TOKEN Secret')
    # Explicit token, no CLI cache or administrator credential fallback.
    from huggingface_hub import HfApi
    try:
        references=pinned_reference_assets(root/'operator-data/reference-assets.json',
                                           '/tmp/koevd-pinned-references',api=HfApi(token=token))
    except Exception as exc:
        # Report only the exception class and integer HTTP status; messages,
        # URLs, response bodies and credentials must never enter startup logs.
        status=getattr(getattr(exc,'response',None),'status_code',None)
        suffix=f'; HTTP {status}' if type(status) is int else ''
        raise ValueError(f'Pinned private reference initialization failed ({type(exc).__name__}{suffix})') from None
    finally:
        token=None
    for key in list(os.environ):
        if key.startswith(('HF_','HUGGING_FACE_','OAUTH_','KOEVD_')):os.environ.pop(key,None)
    from koevd_eval.results import read_document
    from koevd_eval.space_service import AnalysisService,InputCatalog
    from koevd_eval.spaces import create_app
    import uvicorn
    template=read_document(root/'operator-data/catalog.json')
    evidence=root/'operator-data/reference-permission.json'
    evidence_sha=hashlib.sha256(evidence.read_bytes()).hexdigest()
    template['baselines']=[{'id':e['id'],'label':e['label'],'index_id':'koevd-core',
        'path':e['local_path'],'sha256':e['sha256'],'scope':'actual_target_outputs',
        'publication_evidence':{'consent':'operator_confirmed_raw_publication',
        'rights':'Rights holder authorized research-use comparison; original reference text is not public in this beta.',
        'evidence_path':str(evidence),'evidence_sha256':evidence_sha}} for e in references]
    # Keep relative index/registry paths relative to the code-owned catalog dir.
    for entry in template['indexes']:
        for key in ('path','registry'):
            if key in entry:entry[key]=str((root/'operator-data'/entry[key]).resolve())
    catalog_path=Path('/tmp/koevd-pinned-references/catalog.json')
    catalog_path.write_text(json.dumps(template),encoding='utf-8')
    catalog=InputCatalog(catalog_path,public_reference_disclosure=True)
    service=AnalysisService(catalog,Path('/tmp/koevd-public-analysis-sessions'))
    origin='https://'+host
    app=create_app(service,origins=[origin],frame_ancestors=("'self'",'https://huggingface.co'),
        deployment_notice='Public research beta: personal uploads are temporary private analysis sessions. Reference text is withheld; all measured records and metrics are retained. No persistent submissions or official ranking. Keep your original results locally.')
    try:uvicorn.run(app,host='0.0.0.0',port=7860,workers=1,access_log=False)
    finally:service.close()


if __name__=='__main__':main()
