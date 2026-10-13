"""Read-only anonymous hosted Static validation; never changes visibility.

Uses no HF token, private-access JWT, stored cookies or user browser profile.
The existing common browser validator checks the actual analysis and downloads.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from validate_private_static_hosting import checked_host, normalized_index
from validate_static_inventory import checked_inventory


def anonymous_access(info, revision):
    if info.private or info.sdk != 'static' or info.sha != revision:
        raise ValueError('Require the exact public Static revision')
    return {'origin': checked_host(info.host), 'revision': revision,
            'mode': 'anonymous', 'cookies': []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-id', required=True)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--node')
    parser.add_argument('--browser-executable')
    parser.add_argument('--result', action='append', default=[])
    parser.add_argument('--expected')
    parser.add_argument('--output')
    parser.add_argument('--resamples', type=int, default=100)
    args = parser.parse_args()
    if (not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+', args.repo_id)
            or not re.fullmatch(r'[a-f0-9]{40}', args.revision)):
        parser.error('Require namespace/name and outside commit SHA')
    if not args.preflight_only and (not args.node or not args.browser_executable
            or not 1 <= len(args.result) <= 4 or not args.expected or not args.output):
        parser.error('Full check requires Node/browser/results/native outputs/fresh private output')
    import httpx
    from huggingface_hub import HfApi
    candidate = Path(args.candidate).resolve(strict=True)
    checked_inventory(candidate)
    # Explicit False suppresses any locally cached CLI token on every API call.
    info = HfApi(token=False).space_info(args.repo_id, token=False)
    access = anonymous_access(info, args.revision)
    with httpx.Client(follow_redirects=False, timeout=60) as client:
        response = client.get(access['origin'] + '/index.html')
        if (response.status_code != 200 or client.cookies
                or 'authorization' in response.request.headers
                or 'cookie' in response.request.headers
                or normalized_index(response.content) != (candidate / 'index.html').read_bytes()):
            raise ValueError('Anonymous hosted index access/parity failed')
        parent = client.get('https://huggingface.co/spaces/' + args.repo_id)
        if parent.status_code != 200 or 'authorization' in parent.request.headers:
            raise ValueError('Public Hub parent not anonymously accessible')
    summary = {'scope': 'Anonymous public API, Hub parent HTTP and direct Static index; parent file flow is separate',
               'repo_id': args.repo_id, 'revision': info.sha, 'private': info.private,
               'anonymous_access': True, 'credentials_used': False,
               'index_exact_after_HF_variables_injection': True, 'Hub_parent_HTTP_status': 200,
               'actual_result_transmitted': False}
    if args.preflight_only:
        print(json.dumps(summary))
        return
    # The browser receives no provider credential and never uses a user profile.
    env = {key: value for key, value in os.environ.items() if key not in (
        'HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN', 'OAUTH_CLIENT_ID', 'OAUTH_CLIENT_SECRET')}
    command = [args.node, str(Path(__file__).with_name('validate_hosted_static_space_ui.cjs')),
               '--anonymous', '--space', str(candidate), '--output', args.output,
               '--files', json.dumps(args.result), '--expected', args.expected,
               '--resamples', str(args.resamples), '--browser-executable', args.browser_executable]
    completed = subprocess.run(command, input=json.dumps(access), text=True, env=env)
    summary['browser_exit_code'] = completed.returncode
    summary['candidate_manifest_sha256'] = hashlib.sha256((candidate / 'deployment-manifest.json').read_bytes()).hexdigest()
    (Path(args.output) / 'anonymous-access.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary))
    raise SystemExit(completed.returncode)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(json.dumps({'status': 'public_static_check_failed', 'error_type': type(error).__name__,
                          'credentials_used': False}))
        raise SystemExit(1)
