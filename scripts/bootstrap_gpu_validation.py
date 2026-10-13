"""Prepare isolated environments under an explicit new validation root.

Does not launch GPU inference or change the previous validation environment.
Measurement dependency reuse is explicit and recorded, never an installation
claim for those inherited packages. Run on the operator-selected Linux node.
"""

import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--measurement-dependencies', required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve(strict=True)
    inherited = Path(args.measurement_dependencies).resolve(strict=True)
    source = root / 'source'
    if not (source / 'pyproject.toml').is_file() or not (root / 'environment/source-receipt.json').is_file():
        parser.error('Expected independently verified source and receipt')
    if inherited == root or root in inherited.parents:
        parser.error('Inherited dependencies must be an existing external environment')
    env = dict(os.environ)
    env.update(UV_CACHE_DIR=str(root / 'environment/uv-cache'),
               UV_PYTHON_INSTALL_DIR=str(root / 'environment/python-runtime'),
               PYTHONDONTWRITEBYTECODE='1', UV_NO_PROGRESS='1')
    evidence = {'scope': 'environment_setup_not_gpu_validation',
                'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'root': str(root), 'measurement_dependency_path': str(inherited),
                'source_sha256': json.loads((root / 'environment/source-receipt.json').read_text())['zip_sha256'],
                'commands': [], 'status': 'running'}
    state = root / 'environment/bootstrap-status.json'

    def save():
        temporary = state.with_suffix('.tmp')
        temporary.write_text(json.dumps(evidence, indent=2))
        temporary.replace(state)

    def run(name, command):
        item = {'name': name, 'argv': command, 'status': 'running'}
        evidence['commands'].append(item)
        save()
        print('START ' + name, flush=True)
        with (root / 'environment' / (name + '.log')).open('x') as log:
            result = subprocess.run(command, env=env, cwd=source, stdout=log, stderr=subprocess.STDOUT)
        item.update(exit_code=result.returncode, status='passed' if result.returncode == 0 else 'failed')
        save()
        print('END ' + name + ' exit=' + str(result.returncode), flush=True)
        if result.returncode:
            evidence['status'] = 'failed'
            save()
            raise SystemExit(result.returncode)

    for name in ('core', 'measure', 'serve'):
        if (root / 'envs' / name).exists():
            parser.error('Refusing to overwrite existing environment: ' + name)
    save()
    for name in ('core', 'measure', 'serve'):
        run('venv-' + name, ['uv', 'venv', '--python', '3.11.14', '--seed', str(root / 'envs' / name)])
    run('install-core', ['uv', 'pip', 'install', '--python', str(root / 'envs/core/bin/python'),
                         str(source) + '[dev,hub,serve]'])
    # Only a new .pth file is written. Existing dependency files stay unchanged.
    site = root / 'envs/measure/lib/python3.11/site-packages'
    (site / 'koevd-measurement-dependencies.pth').write_text(str(inherited) + '\n')
    run('install-measure', ['uv', 'pip', 'install', '--python', str(root / 'envs/measure/bin/python'),
                            '--no-deps', str(source)])
    wheel = ('https://github.com/vllm-project/vllm/releases/download/v0.13.0/'
             'vllm-0.13.0%2Bcu130-cp38-abi3-manylinux_2_35_x86_64.whl')
    run('install-serve', ['uv', 'pip', 'install', '--python', str(root / 'envs/serve/bin/python'),
                          wheel, '--torch-backend=cu130'])
    run('serve-dependency-check', [str(root / 'envs/serve/bin/python'), '-m', 'pip', 'check'])
    run('core-dependency-check', [str(root / 'envs/core/bin/python'), '-m', 'pip', 'check'])
    evidence.update(status='passed', finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    save()
    print(json.dumps({'bootstrap': evidence['status'], 'evidence': str(state),
                      'gpu_inference_verified': False}), flush=True)


if __name__ == '__main__':
    main()
