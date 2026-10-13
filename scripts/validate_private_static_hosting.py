"""Read-only private Static check with credentials confined to memory/stdin.

Requires the hub/dev extras plus Node/Playwright/Chrome. Never publishes a Space,
uploads result bytes, changes visibility or verifies KoEVD submitter OAuth.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import urlparse


def checked_host(value):
    if not value.startswith('https://'):
        value = 'https://' + value
    parsed = urlparse(value)
    if (parsed.scheme != 'https' or parsed.username or parsed.password
            or parsed.query or parsed.fragment or parsed.path not in ('', '/')
            or parsed.port is not None
            or not re.fullmatch(r'[a-z0-9-]+\.static\.hf\.space', parsed.hostname or '')):
        raise ValueError('Require API-verified HTTPS Static origin')
    return value.rstrip('/')


def normalized_index(content):
    """Accept only the observed provider-added creator variable, then byte-check.

    New OAuth variables or provider markup need explicit review before this
    development validator accepts them; no arbitrary injected script is removed.
    """
    pattern = rb'<script>window\.huggingface=\{variables:(\{[^\n]*\})\};</script>'
    matches = list(re.finditer(pattern, content))
    if len(matches) != 1:
        raise ValueError('Unexpected HF variables injection')
    match = matches[0]
    variables = json.loads(match.group(1))
    if (set(variables) != {'SPACE_CREATOR_USER_ID'}
            or not isinstance(variables['SPACE_CREATOR_USER_ID'], str)
            or not re.fullmatch(r'[a-f0-9]{24}', variables['SPACE_CREATOR_USER_ID'])):
        raise ValueError('Unexpected HF provider variable set')
    return content[:match.start()] + content[match.end():]


def redirect_index(host, response):
    # Deliberately never follow a service redirect with credentials automatically.
    from urllib.parse import urljoin
    if response.status_code != 302:
        raise ValueError('Expected signed access redirect')
    target = urljoin(host + '/', response.headers.get('location', ''))
    if target != host + '/index.html':
        raise ValueError('Unexpected signed redirect destination')
    return target


def access_cookies(jar, host):
    cookies = []
    for item in jar:
        if not item.name.startswith('hf_jwt_'):
            continue
        if (item.domain != urlparse(host).hostname or item.path != '/'
                or not item.secure or 'HttpOnly' not in item._rest
                or not re.fullmatch(r'hf_jwt_[a-f0-9]+', item.name)):
            raise ValueError('Unexpected private access cookie boundary')
        cookies.append({'name': item.name, 'value': item.value, 'domain': item.domain,
                        'path': '/', 'secure': True, 'httpOnly': True})
    if len(cookies) != 1:
        raise ValueError('Expected exactly one private Space access cookie')
    return cookies


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-id', required=True)
    parser.add_argument('--revision', required=True, help='Outside approved candidate commit SHA')
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--node')
    parser.add_argument('--browser-executable')
    parser.add_argument('--result', action='append', default=[])
    parser.add_argument('--expected', help='Native profile; all five native outputs must be in this folder')
    parser.add_argument('--output', help='Fresh private directory: contains actual response reports')
    parser.add_argument('--resamples', type=int, default=100)
    args = parser.parse_args()
    if (not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+', args.repo_id)
            or not re.fullmatch(r'[a-f0-9]{40}', args.revision)):
        parser.error('Require a namespace/name and outside forty-character commit SHA')
    if not args.preflight_only and (not args.node or not args.browser_executable
            or not 1 <= len(args.result) <= 4 or not args.expected or not args.output):
        parser.error('Full check requires node, browser, one to four results, native profile and fresh private output')
    import httpx
    from huggingface_hub import HfApi, get_token
    candidate = Path(args.candidate).resolve(strict=True)
    from validate_static_inventory import checked_inventory
    checked_inventory(candidate)
    info = HfApi().space_info(args.repo_id)
    if not info.private or info.sdk != 'static' or info.sha != args.revision:
        raise ValueError('Space differs from the independently supplied private candidate revision')
    host = checked_host(info.host)
    with httpx.Client(follow_redirects=False, timeout=60) as client:
        response = client.get('https://huggingface.co/api/spaces/' + args.repo_id + '/jwt',
                              headers={'Authorization': 'Bearer ' + get_token()})
        if response.status_code != 200:
            raise ValueError('Private Space JWT request denied')
        jwt = response.json()['token']
        response = client.get(host + '/', params={'__sign': jwt})
        target = redirect_index(host, response)
        response = client.get(target)
        if response.status_code != 200 or normalized_index(response.content) != (candidate / 'index.html').read_bytes():
            raise ValueError('Hosted index differs from the local candidate')
        access = {'origin': host, 'revision': args.revision,
                  'cookies': access_cookies(client.cookies.jar, host)}
        summary = {'scope': 'read-only owner development access; not submitter OAuth',
                   'repo_id': args.repo_id, 'revision': args.revision, 'private': True,
                   'index_exact_after_HF_variables_injection': True,
                   'credentials_persisted': False, 'actual_results_transmitted': False}
        if args.preflight_only:
            print(json.dumps(summary))
            return
        env = {key: value for key, value in os.environ.items() if key not in (
            'HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN', 'OAUTH_CLIENT_ID', 'OAUTH_CLIENT_SECRET')}
        command = [args.node, str(Path(__file__).with_name('validate_hosted_static_space_ui.cjs')),
                   '--space', str(candidate), '--output', args.output, '--files', json.dumps(args.result),
                   '--expected', args.expected, '--resamples', str(args.resamples),
                   '--browser-executable', args.browser_executable]
        # No cookie/HF token appears in argv/environment or any saved receipt.
        process = subprocess.run(command, input=json.dumps(access), text=True, env=env)
        summary['browser_exit_code'] = process.returncode
        print(json.dumps(summary))
        raise SystemExit(process.returncode)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Do not serialize service exceptions, whose messages can contain URLs.
        print(json.dumps({'status': 'private_static_check_failed', 'error_type': type(error).__name__,
                          'credentials_persisted': False}))
        raise SystemExit(1)
