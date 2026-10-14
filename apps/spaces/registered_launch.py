"""Registered CPU Space: native HF identity and acknowledged private state.

Requires explicit state configuration and dedicated secrets. No cached-token
fallback, bucket creation, paid-resource change or model inference. Existing
reference originals stay private; initial numerical intake requires opt-in.
"""
import json
import os
from pathlib import Path
import re
import tempfile


def captured_configuration(environ):
    if environ.get('KOEVD_REGISTRATION_ENABLED','0')!='1':
        raise ValueError('Registered runtime requires explicit activation; no reference/state access')
    host=environ.get('SPACE_HOST','').lower()
    if not host.endswith('.hf.space') or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-.' for c in host):
        raise ValueError('Canonical provider SPACE_HOST required')
    if environ.get('OPENID_PROVIDER_URL','https://huggingface.co').rstrip('/')!='https://huggingface.co':
        raise ValueError('Fixed HF identity provider required')
    initialize=environ.get('KOEVD_STATE_INITIALIZE','0')
    if initialize not in ('0','1'):raise ValueError('State initialization must be explicit 0 or 1')
    environment=environ.get('KOEVD_REGISTRATION_ENVIRONMENT','hosted_candidate')
    if environment not in ('hosted_candidate','hosted_service'):raise ValueError('Explicit hosted environment required')
    settings={'origin':'https://'+host,'initialize':initialize=='1','environment':environment}
    for key,default,upper in (('max_database_bytes',2*1024**3,2*1024**3),
                             ('max_retained_bytes',8*1024**3,8*1024**3),('max_sequence',10000,10000)):
        raw=environ.get('KOEVD_STATE_'+key.upper(),str(default))
        if not isinstance(raw,str) or not raw.isascii() or not raw.isdigit():raise ValueError('Bounded state limits required')
        value=int(raw)
        if not (1 if key=='max_sequence' else 65536)<=value<=upper:raise ValueError('State limit outside supported range')
        settings[key]=value
    for name in ('OAUTH_CLIENT_ID','OAUTH_CLIENT_SECRET','KOEVD_REFERENCE_TOKEN','KOEVD_STATE_TOKEN',
                 'KOEVD_STATE_ACCESS_KEY_ID','KOEVD_STATE_SECRET_ACCESS_KEY','KOEVD_STATE_BUCKET'):
        value=environ.get(name,'')
        if not isinstance(value,str) or not value.strip():raise ValueError('Dedicated registered runtime configuration incomplete')
        settings[name]=value
    if settings['KOEVD_STATE_BUCKET'] in ('KETI-NLP/KoEVD-Platform-Backups','KETI-NLP/KoEVD-Platform-Backups-Dev'):
        raise ValueError('State storage must be separate from references and periodic backups')
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*/[A-Za-z0-9][A-Za-z0-9._-]*',settings['KOEVD_STATE_BUCKET']):
        raise ValueError('Explicit state bucket owner/name required')
    if settings['KOEVD_STATE_TOKEN']==settings['KOEVD_REFERENCE_TOKEN']:
        raise ValueError('Reference and state credentials must be distinct')
    from koevd_eval.oauth import HFOAuthProvider
    settings['provider']=HFOAuthProvider(settings['OAUTH_CLIENT_ID'],settings.pop('OAUTH_CLIENT_SECRET'))
    return settings


def build_app(root, runtime, settings):
    from huggingface_hub import HfApi
    from public_launch import pinned_reference_assets
    from koevd_eval.results import read_document
    from koevd_eval.space_service import InputCatalog,AnalysisService
    from koevd_eval.oauth import IdentitySessions
    from koevd_eval.protocols import ProtocolRegistry
    from koevd_eval.registration_runtime import bootstrap_registered_service
    from koevd_eval.remote_durability import HFS3StateObjects,RemoteCheckpointLedger
    from koevd_eval.submission_web import RegistrationWeb
    from koevd_eval.spaces import create_app
    from koevd_eval.snapshots import file_digest
    root=Path(root);runtime=Path(runtime)
    references=pinned_reference_assets(root/'operator-data/reference-assets.json',runtime/'references',
        api=HfApi(token=settings['KOEVD_REFERENCE_TOKEN'],endpoint='https://huggingface.co'))
    template=read_document(root/'operator-data/catalog.json')
    if template['baselines']:raise ValueError('Do not inherit raw baseline paths in code context')
    for entry in template['indexes']:
        for key in ('path','registry'):
            if key in entry:entry[key]=str((root/'operator-data'/entry[key]).resolve())
    permission=root/'operator-data/reference-permission.json'
    evidence={'consent':'operator_confirmed_raw_publication',
        'rights':'Rights-holder-approved numerical research references; raw originals are not public.',
        'evidence_path':str(permission),'evidence_sha256':file_digest(permission)}
    template['baselines']=[{'id':e['id'],'label':e['label'],'index_id':'koevd-core','path':e['local_path'],
        'sha256':e['sha256'],'scope':'actual_target_outputs','publication_evidence':evidence} for e in references]
    catalog_file=runtime/'catalog.json';catalog_file.write_text(json.dumps(template),encoding='utf-8')
    catalog=InputCatalog(catalog_file,public_reference_disclosure=True)
    roles=read_document(root/'operator-data/roles.json',max_bytes=1024*1024)
    objects=HFS3StateObjects.from_secrets(settings['KOEVD_STATE_BUCKET'],hf_token=settings['KOEVD_STATE_TOKEN'],
        access_key_id=settings['KOEVD_STATE_ACCESS_KEY_ID'],secret_access_key=settings['KOEVD_STATE_SECRET_ACCESS_KEY'])
    ledger=RemoteCheckpointLedger(objects,initialize_empty=settings['initialize'],
        max_database_bytes=settings['max_database_bytes'],max_retained_bytes=settings['max_retained_bytes'],
        max_sequence=settings['max_sequence'])
    submissions=bootstrap_registered_service(catalog,ledger,runtime/'state',roles=roles,
        registry=ProtocolRegistry(root/'configs/protocols'),publication_environment=settings['environment'])
    identities=IdentitySessions(settings['provider'],settings['origin'])
    analysis=AnalysisService(catalog,runtime/'analysis')
    try:
        # Warm numerical admission once before serving; subsequent board/profile
        # requests reuse it and still perform current publication fencing.
        submissions.public_leaderboard()
        return create_app(analysis,origins=[settings['origin']],frame_ancestors=("'self'",'https://huggingface.co'),
            registration=RegistrationWeb(submissions,identities),deployment_notice=(
                'Registered research candidate: explicit summary consent preserves results in private acknowledged state. '
                'Raw responses require independent permission review. Reference originals remain private. '
                'Generation is self-reported unless independently reviewed; official ranks stay disabled.'))
    except Exception:
        identities.close();analysis.close();raise


def main():
    settings=captured_configuration(os.environ)
    # Keep only explicitly captured client objects/values; no incidental admin
    # or old backup token can become a runtime credential fallback.
    for key in list(os.environ):
        if key.startswith(('HF_','HUGGING_FACE_','OAUTH_','KOEVD_')):os.environ.pop(key,None)
    import uvicorn
    with tempfile.TemporaryDirectory(prefix='koevd-registered-runtime-') as temporary:
        app=build_app(Path(__file__).resolve().parent,Path(temporary),settings)
        settings.clear()
        try:uvicorn.run(app,host='0.0.0.0',port=7860,workers=1,access_log=False)
        finally:
            app.state.service.close()
            app.state.registration.close()


if __name__=='__main__':
    try:main()
    except Exception as exc:
        # Provider messages may contain signed URLs or credentials.
        print(json.dumps({'error':'registered_startup_failed','class':type(exc).__name__}),flush=True)
        raise SystemExit(2) from None
