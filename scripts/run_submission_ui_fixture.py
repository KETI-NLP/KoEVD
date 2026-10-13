"""LOCAL SYNTHETIC UI server. No real HF identity, permission review or inference.

Run only for development acceptance. The production koevd-space CLI never loads
this provider. The authorization page is localhost-only; this server only accepts
four explicit SYNTHETIC fixture codes and never contacts HF for authentication.
"""
import argparse
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlsplit, urlencode

from koevd_eval.oauth import IdentitySessions
from koevd_eval.space_service import AnalysisService, InputCatalog, Limits
from koevd_eval.spaces import create_app
from koevd_eval.storage import LocalSubmissionStore, StorageError
from koevd_eval.submissions import SubmissionService
from koevd_eval.submission_web import RegistrationWeb


class SyntheticProvider:
    client_id='SYNTHETIC-ui-app'
    def exchange(self,code,verifier,redirect_uri):
        names={'SYNTHETIC-author','SYNTHETIC-other','SYNTHETIC-reviewer','SYNTHETIC-admin'}
        if code not in names or len(verifier)!=43:raise StorageError('synthetic_identity','Invalid fixture identity',401)
        name=code+(' <img src=x onerror="window.IDENTITY_ATTACK=true">' if code=='SYNTHETIC-author' else '')
        return {'sub':code,'preferred_username':name},3600


class SyntheticIdentitySessions(IdentitySessions):
    def begin(self, previous_binding=None):
        url,binding=super().begin(previous_binding)
        return self.origin+'/SYNTHETIC/authorize?'+urlsplit(url).query,binding


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog',required=True);parser.add_argument('--root',required=True)
    parser.add_argument('--persistent-root',help='Optional existing SYNTHETIC fixture store for explicit restart acceptance')
    parser.add_argument('--port',type=int,default=8770);parser.add_argument('--synthetic-fixture',required=True,action='store_true')
    args=parser.parse_args();root=Path(args.root)
    if root.exists():parser.error('Use a new directory; preserve prior evidence')
    root.mkdir(parents=True)
    catalog=InputCatalog(args.catalog,allow_synthetic=True)
    if any(item['mode']!='synthetic_demo' for item in catalog.indexes.values()):parser.error('Only explicit synthetic indexes are allowed')
    if any(item['scope']!='synthetic_demo' for item in catalog.baselines.values()):parser.error('Only synthetic references are allowed')
    role=lambda code:'hf:'+sha256(code.encode()).hexdigest()
    submissions=SubmissionService(LocalSubmissionStore(args.persistent_root or root/'persistent'),{k:v['index'] for k,v in catalog.indexes.items()},
        reviewers=[role('SYNTHETIC-reviewer')],admins=[role('SYNTHETIC-admin')])
    identity=SyntheticIdentitySessions(SyntheticProvider(),f'http://127.0.0.1:{args.port}')
    analysis=AnalysisService(catalog,root/'analysis',limits=Limits(bootstrap_resamples=0))
    app=create_app(analysis,origins=[identity.origin],registration=RegistrationWeb(submissions,identity))
    from fastapi import Request
    from fastapi.responses import Response
    @app.get('/SYNTHETIC/authorize')
    async def fake_authorize(request:Request):
        state=request.query_params.get('state','')
        if len(state)!=43 or request.query_params.get('code_challenge_method')!='S256':raise StorageError('synthetic_state','Invalid synthetic request',401)
        links=''.join('<p><a data-code="'+name+'" href="/auth/callback?'+urlencode({'state':state,'code':name}).replace('&','&amp;')+'">'+name+'</a></p>'
                      for name in ('SYNTHETIC-author','SYNTHETIC-other','SYNTHETIC-reviewer','SYNTHETIC-admin'))
        return Response('<!doctype html><html lang="en"><meta charset="utf-8"><title>SYNTHETIC login fixture</title><h1>SYNTHETIC identity provider</h1><p>Local CPU UI fixture. No real HF login, GPU or permission evidence.</p>'+links+'</html>',media_type='text/html')
    import uvicorn
    print('SYNTHETIC UI FIXTURE ONLY; NO REAL HF/GPU/PUBLICATION',flush=True)
    uvicorn.run(app,host='127.0.0.1',port=args.port,access_log=False,workers=1)


if __name__=='__main__':main()
