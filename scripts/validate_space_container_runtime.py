"""Check a prebuilt local Docker image using its default development launcher.

No image build/pull/push, HF request, real OAuth credentials, public endpoint,
GPU inference or managed backup activation. Uses private disposable copies.
The inner HTTP checker deliberately does not claim container ownership; this
driver inspects and stops only its uniquely labelled container.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

from validate_space_native_runtime import checked_context, digest

SCOPE = 'koevd.runtime.validation'

def single_inspection(raw):
    values = json.loads(raw)
    if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], dict):
        raise ValueError('Expected exactly one inspect object for the supplied ID')
    return values[0]


def image_state(raw):
    value = single_inspection(raw)
    config = value['Config']
    if not isinstance(config, dict):
        raise ValueError('Image config unavailable')
    environment = config.get('Env') or []
    if not isinstance(environment, list) or not all(isinstance(v, str) for v in environment):
        raise ValueError('Image environment metadata malformed')
    # Docker can omit an unset Entrypoint. Go templates treating it as a
    # required map key fail before the default CMD can be inspected.
    # Environment values remain in memory and are never serialized/logged.
    return {'id': value['Id'], 'user': config.get('User', ''), 'cmd': config.get('Cmd'),
            'entrypoint': config.get('Entrypoint'), 'env': environment}


def container_state(raw):
    value = single_inspection(raw)
    config, host, state = value['Config'], value['HostConfig'], value['State']
    if not all(isinstance(v, dict) for v in (config, host, state)):
        raise ValueError('Container inspection metadata unavailable')
    if type(state.get('Running')) is not bool or type(state.get('ExitCode')) is not int:
        raise ValueError('Container terminal metadata malformed')
    return {'id': value['Id'], 'image': value['Image'], 'user': config.get('User', ''),
            'label': (config.get('Labels') or {}).get(SCOPE),
            'running': state['Running'], 'exit_code': state['ExitCode'],
            'network': host.get('NetworkMode'), 'restart': (host.get('RestartPolicy') or {}).get('Name'),
            'ports': host.get('PortBindings')}


def checked_image(value):
    if not re.fullmatch(r'sha256:[0-9a-f]{64}', value or ''):
        raise ValueError('Use the independently supplied exact local image ID')
    return value


def mount(source, target, *, readonly=True):
    value = str(Path(source).resolve())
    if any(c in value for c in (',', '\n', '\r', '\x00')):
        raise ValueError('Bind mount path cannot contain comma or control characters')
    if not target.startswith('/') or ',' in target:
        raise ValueError('Fixed absolute container mount target required')
    return 'type=bind,source=' + value + ',target=' + target + (',readonly' if readonly else '')


def checked_local_endpoint(endpoint):
    if not (isinstance(endpoint, str) and
            (re.fullmatch(r'unix:///[^\r\n\x00]+', endpoint) or
             endpoint == 'npipe:////./pipe/docker_engine')):
        raise ValueError('Use a local Unix/named-pipe Docker endpoint; remote daemons are not allowed')
    return endpoint


def checked_owner(state, cid, image, label):
    if (state.get('id') != cid or state.get('image') != image or state.get('label') != label
            or state.get('user') != '1000:1000' or state.get('network') != 'none'
            or state.get('restart') != 'no' or state.get('ports') not in (None, {})):
        raise ValueError('Owned container identity or isolation differs; no cleanup by name')
    return state


def own_private_copy_tree(root):
    """Only fresh disposable copies; never change original ownership/modes."""
    paths = list(root.rglob('*'))
    if root.is_symlink() or any(p.is_symlink() for p in paths):
        raise ValueError('Disposable validation copies contain a symlink')
    for path in [*paths, root]:
        if os.name == 'posix':
            if os.getuid() == 0:
                os.chown(path, 1000, 1000)
            elif os.getuid() != 1000:
                raise ValueError('Run staging as UID1000 or root; existing files are never chmod/chowned')
        path.chmod(0o700 if path.is_dir() else 0o600)


def create_argv(docker, image, label, context, tools, results, output):
    return [docker, 'create', '--pull=never', '--name', 'koevd-runtime-' + label,
        '--label', SCOPE + '=' + label, '--user', '1000:1000', '--network', 'none',
        '--restart', 'no', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
        '--read-only', '--tmpfs', '/tmp:rw,nosuid,nodev,size=2147483648',
        '--env', 'SPACE_HOST=keti-nlp-koevd-explorer.hf.space',
        '--env', 'OAUTH_CLIENT_ID=SYNTHETIC-container-runtime',
        '--env', 'OAUTH_CLIENT_SECRET=SYNTHETIC-container-runtime',
        '--mount', mount(context, '/validation-context'),
        '--mount', mount(tools, '/validation-tools'),
        '--mount', mount(results, '/validation-results'),
        '--mount', mount(output, '/validation-output', readonly=False), image]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', required=True)
    p.add_argument('--image-id', required=True)
    p.add_argument('--docker', default='docker')
    p.add_argument('--result', action='append', required=True)
    p.add_argument('--result-sha256', action='append', required=True)
    p.add_argument('--comparison-only', action='store_true')
    p.add_argument('--prepare-only', action='store_true', help='Hash/plan only; no Docker or private result copying')
    p.add_argument('--output', required=True, help='Fresh private directory; actual execution includes raw reports')
    a = p.parse_args()
    image = checked_image(a.image_id)
    if not 1 <= len(a.result) <= 4 or len(a.result) != len(a.result_sha256):
        p.error('Require one to four results and independent byte hashes')
    if a.comparison_only and len(a.result) < 2:
        p.error('Comparison-only check requires at least two results')
    candidate = Path(a.candidate).resolve(strict=True)
    manifest = checked_context(candidate)
    if manifest.get('storage') != 'ephemeral_development' or 'operator-data/managed.json' in manifest['files']:
        raise ValueError('Only the unactivated default development profile is allowed')
    results = [Path(name).resolve(strict=True) for name in a.result]
    for path, expected in zip(results, a.result_sha256):
        if path.is_relative_to(candidate) or not re.fullmatch(r'[0-9a-f]{64}', expected) or digest(path) != expected:
            raise ValueError('Require an outside original and independently accepted SHA-256')
    out = Path(a.output).resolve()
    for path in (candidate, *results, out):
        mount(path, '/validation-path-check')
    if out.is_relative_to(candidate) or candidate.is_relative_to(out) or any(out == r or r.is_relative_to(out) for r in results):
        raise ValueError('Output must be a fresh independent path')
    out.mkdir(mode=0o700, parents=True, exist_ok=False)
    receipt = {'format':'koevd-local-container-runtime-v1', 'status':'preparing',
        'container_verified':False, 'hosted_HF_verified':False, 'actual_OAuth_verified':False,
        'new_inference':False, 'managed_backup_activated':False, 'public_outputs':False,
        'image_id':image, 'candidate_manifest_sha256':digest(candidate/'deployment-manifest.json'),
        'candidate_payload_files':len(manifest['files']), 'result_byte_sha256':a.result_sha256,
        'comparison_only':a.comparison_only, 'actual_container_started':False}
    cid = None
    label = uuid.uuid4().hex
    env = dict(os.environ)
    # Docker CLI needs its own config/context. No HF app/backup credential is passed.
    for key in list(env):
        if key.startswith(('HF_', 'HUGGING_FACE_', 'OAUTH_', 'KOEVD_')):
            env.pop(key)
    def run(args, *, timeout=60, check=True):
        result = subprocess.run(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding='utf-8', timeout=timeout, shell=False)
        if check and result.returncode:
            raise RuntimeError('Docker operation failed; raw provider/config output is not serialized')
        return result
    def inspect_owned():
        state=container_state(run([a.docker,'container','inspect',cid]).stdout)
        return checked_owner(state,cid,image,label)
    try:
        if a.prepare_only:
            receipt.update(status='prepared_only', default_launcher_required=True, inside_UID_required=1000,
                network_required='none', port_publication_required=False,
                Docker_operations=0, raw_result_copies_created=False)
            return
        if os.environ.get('DOCKER_HOST'):
            raise ValueError('Unset DOCKER_HOST and use an inspected local Docker context')
        context_name=run([a.docker,'context','show']).stdout.strip()
        context=json.loads(run([a.docker,'context','inspect',context_name]).stdout)
        endpoint=checked_local_endpoint(context[0]['Endpoints']['docker']['Host'])
        receipt['local_endpoint_verified']=True
        info=image_state(run([a.docker,'image','inspect',image]).stdout)
        if (info['id']!=image or info['user'] not in ('appuser','1000','1000:1000')
                or info['cmd']!=['python','launch.py'] or info['entrypoint'] not in (None,[])
                or any(v.split('=',1)[0].startswith(('HF_','HUGGING_FACE_','OAUTH_','KOEVD_')) for v in info['env'])):
            raise ValueError('Default image command/user or credential environment differs')
        staged=out/'disposable'
        staged.mkdir()
        context_copy=staged/'context'
        shutil.copytree(candidate,context_copy)
        checked_context(context_copy)
        tools=staged/'tools';tools.mkdir()
        shutil.copyfile(Path(__file__).with_name('validate_space_native_runtime.py'),tools/'validate_space_native_runtime.py')
        copies=staged/'results';copies.mkdir()
        for i,path in enumerate(results):
            shutil.copyfile(path,copies/(str(i)+'.json'))
            assert digest(copies/(str(i)+'.json'))==a.result_sha256[i]
        outputs=staged/'output';outputs.mkdir()
        own_private_copy_tree(staged)
        command=create_argv(a.docker,image,label,context_copy,tools,copies,outputs)
        cid=run(command).stdout.strip()
        if not re.fullmatch('[0-9a-f]{64}',cid):
            cid=None
            raise ValueError('Docker create returned no exact owned container ID; inspect unique label manually')
        inspect_owned()
        run([a.docker,'container','start',cid])
        receipt['actual_container_started']=True
        state=inspect_owned()
        if not state['running']:
            raise RuntimeError('Default container launcher did not remain live')
        receipt.update(container_id=cid, default_image_CMD_used=True, network='none',
            inside_user='1000:1000', published_ports=0, restart_policy='no')
        checker=[a.docker,'exec',cid,'python','/validation-tools/validate_space_native_runtime.py',
            '--candidate','/validation-context','--python','/usr/local/bin/python',
            '--existing-loopback-port','7860','--output','/validation-output/http']
        for i,expected in enumerate(a.result_sha256):
            checker.extend(['--result','/validation-results/'+str(i)+'.json','--result-sha256',expected])
        if a.comparison_only:
            checker.append('--comparison-only')
        run(checker,timeout=2400)
        inner=json.loads((outputs/'http/receipt.json').read_text(encoding='utf-8'))
        if (inner['status']!='passed' or inner['uid']!=1000 or inner['gid']!=1000
                or not inner['server_owned_by_external_caller']
                or inner['result_byte_sha256']!=a.result_sha256
                or inner['manifest_sha256']!=receipt['candidate_manifest_sha256']):
            raise ValueError('Container HTTP/CLI result does not match outside ownership and hashes')
        receipt.update(status='checks_passed_cleanup_pending', inner_receipt_sha256=digest(outputs/'http/receipt.json'),
            profiles=inner['profiles'], installed_koevd_eval_files=inner['installed_files'],
            locked_versions=inner['locked_versions'])
    except Exception as error:
        receipt.update(status='failed',failure_type=type(error).__name__)
        raise
    finally:
        if cid is not None:
            try:
                state=inspect_owned()
                if state['running']:
                    run([a.docker,'container','stop','--time','15',cid])
                state=inspect_owned()
                if state['running']:
                    raise ValueError('Owned container still live; do not claim cleanup')
                receipt.update(owned_container_terminal=True, container_exit_code=state['exit_code'])
                run([a.docker,'container','rm',cid])
                receipt['owned_container_removed']=True
                if receipt['status']=='checks_passed_cleanup_pending':
                    receipt.update(status='passed',container_verified=True)
            except Exception as error:
                receipt.update(status='failed',cleanup_failure_type=type(error).__name__,container_verified=False)
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':receipt['status'],'container_verified':receipt['container_verified'],
            'hosted_HF_verified':False,'actual_OAuth_verified':False}))
    if receipt['status']!='passed':
        raise SystemExit(1)


if __name__=='__main__':
    main()
