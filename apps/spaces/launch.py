"""Start a private, ephemeral CPU development Space with native HF OAuth.

No model inference, credentials printed, paid storage, automatic rank or external
publication. SPACE_HOST is provider configuration, never a request Host header.
"""
import os
from pathlib import Path
import sys


def main():
    root = Path(__file__).resolve().parent
    host = os.environ.get('SPACE_HOST')
    if not host or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-.' for c in host.lower()):
        raise ValueError('Expected HF-provided SPACE_HOST')
    if not host.lower().endswith('.hf.space'):
        raise ValueError('Expected a canonical HF Space host')
    origin = 'https://' + host.lower()
    os.environ['KOEVD_SPACE_CATALOG'] = str(root / 'operator-data/catalog.json')
    os.environ['KOEVD_APP_ORIGIN'] = origin
    os.environ['KOEVD_OAUTH_ORIGIN'] = origin
    os.environ['KOEVD_SUBMISSION_ROOT'] = '/tmp/koevd-development-submissions'
    os.environ['KOEVD_ROLES_FILE'] = str(root / 'operator-data/roles.json')
    os.environ['KOEVD_PROTOCOL_REGISTRY'] = str(root / 'configs/protocols')
    # This launcher is an ephemeral development candidate with ranks disabled.
    # Production operator policy activation uses separately reviewed configuration.
    os.environ.pop('KOEVD_POLICY_ROOT', None)
    os.environ.pop('KOEVD_POLICY_HEAD_SHA256', None)
    os.environ['KOEVD_DEPLOYMENT_NOTICE'] = (
        'Private development Space: analysis and saved submissions may disappear '
        'when this Space restarts or rebuilds. Keep your results JSON locally. '
        'Official ranking and verified model references are not enabled.')
    # Native metadata normally supplies confidential app credentials. An operator
    # can explicitly select a registered public app; no missing-secret fallback.
    # A CLI token never substitutes for either OAuth app configuration.
    from koevd_eval.oauth import HFOAuthProvider
    HFOAuthProvider(os.environ.get('OAUTH_CLIENT_ID',''),os.environ.get('OAUTH_CLIENT_SECRET',''),
                   client_type=os.environ.get('KOEVD_OAUTH_CLIENT_TYPE','confidential'))
    sys.argv = ['koevd-space', '--host', '0.0.0.0', '--port', '7860']
    from koevd_eval.spaces import main as serve
    serve()


if __name__ == '__main__':
    main()
