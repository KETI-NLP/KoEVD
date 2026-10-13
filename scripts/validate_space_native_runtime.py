"""Check an installed development candidate over loopback HTTP, not a container/HF.

Uses independently supplied, previously accepted private results. No HF request,
human approval, inference, public registration or durable-storage claim is made.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import socket
import subprocess
import time
import urllib.error
import urllib.request


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def checked_context(root):
    manifest = json.loads((root / 'deployment-manifest.json').read_text(encoding='utf-8'))
    if manifest['format'] != 'koevd-private-development-space-v1':
        raise ValueError('Expected a development deployment manifest')
    files = manifest['files']
    inventory = list(root.rglob('*'))
    if root.is_symlink() or any(p.is_symlink() for p in inventory):
        raise ValueError('Deployment symlink rejected')
    actual = {p.relative_to(root).as_posix() for p in inventory if p.is_file()}
    if actual != set(files) | {'deployment-manifest.json'}:
        raise ValueError('Deployment context file set differs from manifest')
    for name, item in files.items():
        relative = PurePosixPath(name)
        if relative.is_absolute() or relative.as_posix() != name or '..' in relative.parts or '\\' in name or ':' in name:
            raise ValueError('Unsafe deployment path')
        path = root / name
        if any(p.is_symlink() for p in (path, *path.parents)) or not path.resolve().is_relative_to(root):
            raise ValueError('Deployment symlink or escape')
        if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            raise ValueError('Deployment file hash mismatch: ' + name)
    if manifest['credentials_included'] or manifest['actual_target_outputs_included'] or manifest['official_rank_eligible']:
        raise ValueError('Expected the unpublished, no-rank development candidate')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--python', required=True, help='Fresh, noneditable runtime with the candidate and exact web lock installed')
    parser.add_argument('--result', action='append', required=True)
    parser.add_argument('--result-sha256', action='append', required=True, help='Outside previously accepted byte hash, in result order')
    parser.add_argument('--comparison-only', action='store_true',
                        help='Check one combined comparison, useful for full-size fixtures; default also checks individual reports')
    parser.add_argument('--existing-loopback-port', type=int,
                        help='Validate an externally owned server on 127.0.0.1; never stop it or claim container ownership')
    parser.add_argument('--output', required=True, help='Fresh private directory; contains actual response reports')
    args = parser.parse_args()
    if not 1 <= len(args.result) <= 4 or len(args.result) != len(args.result_sha256):
        parser.error('Provide one to four results and an independent byte hash for each')
    if args.comparison_only and len(args.result) < 2:
        parser.error('Comparison-only check requires two or more results')
    if args.existing_loopback_port is not None and not 1 <= args.existing_loopback_port <= 65535:
        parser.error('Existing loopback port must be in 1..65535')
    root = Path(args.candidate).resolve(strict=True)
    # Linux venv Python is normally a symlink to the base interpreter. Resolving
    # it before execution discards the venv and its installed dependencies.
    python = os.path.abspath(args.python)
    if not Path(python).is_file():
        parser.error('Runtime Python does not exist')
    out = Path(args.output).resolve()
    out.mkdir(mode=0o700, exist_ok=False)
    receipt = {'format': 'koevd-native-space-runtime-check-v1', 'status': 'running',
               'container_verified': False, 'hosted_space_verified': False, 'provider_login_verified': False,
               'new_inference_performed': False, 'public_outputs_created': False,
               'durability_verified': False, 'human_or_operator_approval_created': False,
               'synthetic_oauth_configuration_only': True, 'checks': []}
    receipt['uid'] = os.getuid() if hasattr(os, 'getuid') else None
    receipt['gid'] = os.getgid() if hasattr(os, 'getgid') else None
    receipt['comparison_only'] = args.comparison_only
    receipt['server_owned_by_external_caller'] = args.existing_loopback_port is not None
    process = None
    log = None
    env = {k: v for k, v in os.environ.items() if k not in (
        'PYTHONPATH', 'PYTHONHOME', 'HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN', 'OAUTH_CLIENT_ID',
        'OAUTH_CLIENT_SECRET') and not k.startswith('KOEVD_')}
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1',
               OAUTH_CLIENT_ID='synthetic-runtime-client', OAUTH_CLIENT_SECRET='synthetic-runtime-secret')
    try:
        manifest = checked_context(root)
        receipt['manifest_sha256'] = digest(root / 'deployment-manifest.json')
        receipt['candidate_files'] = len(manifest['files'])
        receipt['checks'].append('exact_deployment_manifest')
        installed = json.loads(subprocess.check_output([python, '-c',
            "import koevd_eval,json,sys,importlib.metadata as m; from pathlib import Path; "
            "print(json.dumps({'package':str(Path(koevd_eval.__file__).parent),"
            "'python':sys.version,'versions':{d.metadata['Name'].lower().replace('_','-'):d.version for d in m.distributions()}}))"],
            env=env, text=True, cwd=out))
        package = Path(installed['package']).resolve(strict=True)
        if package.is_relative_to(root) or 'site-packages' not in package.parts:
            raise ValueError('Expected a noneditable installed package, not context/source imports')
        if not installed['python'].startswith('3.12.'):
            raise ValueError('Docker candidate specifies Python 3.12; use the same minor version')
        source_files = {p.relative_to(root / 'src/koevd_eval').as_posix(): p
                        for p in (root / 'src/koevd_eval').rglob('*') if p.is_file()}
        installed_files = {p.relative_to(package).as_posix(): p for p in package.rglob('*')
                           if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
        if set(source_files) != set(installed_files):
            raise ValueError('Installed package file set differs from candidate')
        for name, source in source_files.items():
            if digest(source) != digest(installed_files[name]):
                raise ValueError('Installed package bytes differ: ' + name)
        locked = {}
        for line in (root / 'apps/spaces/requirements.lock.txt').read_text().splitlines():
            if not line.strip() or line.startswith('#'):
                continue
            match = re.fullmatch(r'([A-Za-z0-9_-]+)==([A-Za-z0-9.+_-]+)', line)
            if not match:
                raise ValueError('Expected an exact version in the web lock')
            name, version = match.groups()
            name = name.lower().replace('_', '-')
            if name in locked or installed['versions'].get(name) != version:
                raise ValueError('Web runtime dependency version mismatch: ' + name)
            locked[name] = version
        receipt.update(python=installed['python'], installed_package=installed['package'],
                       installed_files=len(installed_files), locked_versions=locked)
        receipt['checks'].extend(['noneditable_package_exact_bytes', 'exact_web_dependency_versions'])
        results = []
        catalog = json.loads((root / 'operator-data/catalog.json').read_text(encoding='utf-8'))
        indexes = {}
        for entry in catalog['indexes']:
            path = (root / 'operator-data' / entry['path']).resolve(strict=True)
            index = json.loads(path.read_text(encoding='utf-8'))
            indexes[index['content_sha256']] = path
        for filename, expected in zip(args.result, args.result_sha256):
            path = Path(filename).resolve(strict=True)
            if path.is_relative_to(root) or not re.fullmatch('[0-9a-f]{64}', expected) or digest(path) != expected:
                raise ValueError('Private result requires an outside accepted byte hash and path')
            document = json.loads(path.read_text(encoding='utf-8'))
            index = indexes[document['input_index_sha256']]
            results.append((path, index))
        receipt['result_byte_sha256'] = args.result_sha256
        if args.existing_loopback_port is None:
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
        else:
            port = args.existing_loopback_port
        origin = 'https://keti-nlp-koevd-explorer.hf.space'
        env['KOEVD_DEPLOYMENT_NOTICE'] = 'Native CPU runtime check; temporary private data; no official ranks.'
        argv = [python, '-m', 'koevd_eval.spaces', '--host', '127.0.0.1', '--port', str(port),
                '--origin', origin, '--oauth-origin', origin, '--catalog', str(root / 'operator-data/catalog.json'),
                '--roles-file', str(root / 'operator-data/roles.json'),
                '--protocol-registry', str(root / 'configs/protocols'),
                '--session-root', str(out / 'sessions'), '--submission-root', str(out / 'submissions')]
        if args.existing_loopback_port is None:
            log = (out / 'server.log').open('w', encoding='utf-8')
            process = subprocess.Popen(argv, cwd=out, env=env, stdout=log, stderr=subprocess.STDOUT)
            receipt['server_pid'] = process.pid
        base = 'http://127.0.0.1:' + str(port)

        def request(method, path, *, body=None, headers=None):
            defaults = {'Host': 'keti-nlp-koevd-explorer.hf.space', 'Origin': origin}
            defaults.update(headers or {})
            req = urllib.request.Request(base + path, data=body, headers=defaults, method=method)
            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    return response.status, {k.lower(): v for k, v in response.headers.items()}, response.read()
            except urllib.error.HTTPError as exc:
                return exc.code, {k.lower(): v for k, v in exc.headers.items()}, exc.read()

        deadline = time.monotonic() + 90
        while True:
            if process is not None and process.poll() is not None:
                raise RuntimeError('Owned server exited before readiness')
            try:
                code, _, raw = request('GET', '/healthz')
                if code == 200:
                    assert json.loads(raw) == {'status': 'ready', 'registration_enabled': True}
                    break
            except (urllib.error.URLError, ConnectionError):
                pass
            if time.monotonic() > deadline:
                raise TimeoutError('Owned server readiness timeout')
            time.sleep(.2)
        code, headers, raw = request('GET', '/')
        expected_notice = (b'Native CPU runtime check' if args.existing_loopback_port is None
                           else b'Private development Space')
        assert code == 200 and expected_notice in raw
        assert headers['cache-control'] == 'no-store' and 'unsafe-inline' not in headers['content-security-policy']
        code, _, raw = request('GET', '/api/catalog')
        public = json.loads(raw)
        assert code == 200 and not public['official_rank_eligible'] and public['baselines'] == []
        code, _, raw = request('GET', '/api/identity')
        assert code == 200 and json.loads(raw) == {'signed_in': False}
        assert request('POST', '/api/session', headers={'Origin': 'https://attacker.invalid'})[0] == 403
        assert request('GET', '/api/session')[0] == 401
        receipt['checks'].append('actual_loopback_http_readiness_no_rank_and_boundaries')

        def session():
            code, _, raw = request('POST', '/api/session')
            assert code == 201
            data = json.loads(raw)
            return {'Authorization': 'Bearer ' + data['session_token'], 'X-Koevd-CSRF': data['csrf_token']}

        auth = session()
        other = session()
        uploads = []
        for result, _ in results:
            code, _, raw = request('POST', '/api/uploads', body=result.read_bytes(),
                                   headers={**auth, 'Content-Type': 'application/json'})
            assert code == 201
            uploads.append(json.loads(raw)['id'])
        code, _, raw = request('GET', '/api/session', headers=other)
        assert code == 200 and json.loads(raw)['uploads'] == []
        receipt['checks'].append('actual_private_results_upload_and_session_isolation')
        profiles = []
        selections = [list(range(len(results)))] if args.comparison_only else [[i] for i in range(len(results))]
        if len(results) > 1 and not args.comparison_only:
            selections.append(list(range(len(results))))
        for n, selection in enumerate(selections):
            code, _, raw = request('POST', '/api/analyses', body=json.dumps({
                'upload_ids': [uploads[i] for i in selection], 'baseline_ids': []}).encode(),
                headers={**auth, 'Content-Type': 'application/json'})
            assert code == 202
            job = json.loads(raw)['id']
            deadline = time.monotonic() + 300
            while True:
                code, _, raw = request('GET', '/api/analyses/' + job, headers=auth)
                status = json.loads(raw)
                assert code == 200 and status['status'] != 'failed'
                if status['status'] == 'complete':
                    break
                if time.monotonic() > deadline:
                    raise TimeoutError('Private report generation timeout')
                time.sleep(.2)
            code, _, profile = request('GET', '/api/reports/' + job + '/profile', headers=auth)
            assert code == 200
            assert request('GET', '/api/reports/' + job + '/profile', headers=other)[0] != 200
            code, report_headers, html = request('GET', '/api/reports/' + job + '/html', headers=auth)
            assert code == 200 and 'attachment' in report_headers['content-disposition']
            (out / ('http-profile-' + str(n) + '.json')).write_bytes(profile)
            (out / ('http-report-' + str(n) + '.html')).write_bytes(html)
            cli = out / ('cli-' + str(n))
            command = [python, '-m', 'koevd_eval.diagnostics', '--output-dir', str(cli),
                       '--bootstrap-resamples', str(public['limits']['bootstrap_resamples']),
                       '--bootstrap-seed', str(public['limits']['bootstrap_seed'])]
            for i in selection:
                command.extend(['--input', str(results[i][0]), '--trusted-index', str(results[i][1])])
            with (out / ('cli-' + str(n) + '.log')).open('w', encoding='utf-8') as stream:
                subprocess.run(command, cwd=out, env=env, stdout=stream, stderr=subprocess.STDOUT, check=True, timeout=300)
            assert json.loads(profile) == json.loads((cli / 'profile-v2.json').read_text(encoding='utf-8'))
            downloads = {}
            for kind, filename in {'profile':'profile-v2.json', 'html':'report-v2.html',
                                   'cases':'cases-v2.jsonl', 'csv':'metrics-v2.csv', 'markdown':'report-v2.md'}.items():
                if kind == 'profile':
                    payload = profile
                elif kind == 'html':
                    payload = html
                else:
                    code, file_headers, payload = request('GET', '/api/reports/' + job + '/' + kind, headers=auth)
                    assert code == 200 and 'attachment' in file_headers['content-disposition']
                assert payload == (cli / filename).read_bytes(), 'HTTP/CLI download bytes differ: ' + kind
                downloads[kind] = {'bytes':len(payload), 'sha256':hashlib.sha256(payload).hexdigest(),
                                   'http_equals_cli_bytes':True}
            profiles.append({'selection': selection, 'profile_sha256': hashlib.sha256(profile).hexdigest(),
                             'http_equals_cli': True, 'html_bytes': len(html), 'downloads': downloads})
        receipt['profiles'] = profiles
        receipt['checks'].append('actual_model_and_comparison_http_cli_profile_equality')
        assert request('DELETE', '/api/session', headers=auth)[0] == 200
        assert request('GET', '/api/session', headers=auth)[0] == 401
        assert request('DELETE', '/api/session', headers=other)[0] == 200
        receipt['checks'].append('private_session_deletion')
        receipt['status'] = 'passed'
    except Exception as exc:
        receipt.update(status='failed', failure_type=type(exc).__name__)
        raise
    finally:
        if process is not None:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=15)
            receipt['owned_server_exit_code'] = process.returncode
            receipt['owned_server_stopped'] = process.poll() is not None
        if log is not None:
            log.close()
        (out / 'receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': receipt['status'], 'checks': len(receipt['checks']), 'output': str(out),
                      'container_verified': False, 'hosted_space_verified': False}))


if __name__ == '__main__':
    main()
