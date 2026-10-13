"""Derive an unactivated managed candidate from an independently checked context.

No token, real operator roles, managed.json, original responses or upload included.
The operator must complete configuration and approve live backup before use.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from validate_space_native_runtime import checked_context


def checked_base(repo, base):
    """Reject internally valid but stale source and operationally configured bases."""
    previous = checked_context(base)
    if previous.get('storage') != 'ephemeral_development':
        raise ValueError('Start from an unactivated ephemeral development context')
    for name in ('operator-data/managed.json', 'operator-data/backup-roles.json'):
        if name in previous['files']:
            raise ValueError('Do not inherit actual managed configuration or backup roles')
    from koevd_eval.results import read_document
    roles = read_document(base / 'operator-data/roles.json')
    if roles != {'reviewers': [], 'admins': []}:
        raise ValueError('Candidate must not inherit approved web roles')
    if read_document(base / 'operator-data/catalog.json').get('baselines') != []:
        raise ValueError('Candidate must not inherit actual reference outputs')
    sources = {}
    for folder in ('src/koevd_eval', 'src/koevd_classifiers', 'configs/protocols'):
        root = repo / folder
        if not root.is_dir():
            raise ValueError('Current repository source or protocol directory missing')
        for path in root.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                if path.is_symlink():
                    raise ValueError('Current repository source symlink rejected')
                sources[path.relative_to(repo).as_posix()] = path
    sources['pyproject.toml'] = repo / 'pyproject.toml'
    inherited = {name for name in previous['files'] if name == 'pyproject.toml' or
                 name.startswith(('src/', 'configs/protocols/'))}
    if inherited != set(sources):
        raise ValueError('Base source inventory differs from the current repository')
    for name, path in sources.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != previous['files'][name]['sha256']:
            raise ValueError('Base source bytes differ from the current repository: ' + name)
    return previous


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', default='.')
    p.add_argument('--base-candidate', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    repo = Path(a.repo).resolve(strict=True)
    base = Path(a.base_candidate).resolve(strict=True)
    previous = checked_base(repo, base)
    out = Path(a.output).resolve()
    out.mkdir(exist_ok=False)
    for name in previous['files']:
        dest = out / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(base / name, dest)
    for name in ('managed_launch.py', 'managed.requirements.lock.txt'):
        shutil.copyfile(repo / 'apps/spaces' / name, out / 'apps/spaces' / name)
    shutil.copyfile(repo / 'apps/spaces/managed.Dockerfile', out / 'Dockerfile')
    shutil.copyfile(repo / 'apps/spaces/managed.example.json', out / 'operator-data/managed.example.json')
    with (out / 'README.md').open('a', encoding='utf-8') as f:
        f.write('\n## Unactivated managed runtime candidate\n\n'
                'This context requires independently supplied operator-data/managed.json, '
                'backup-roles.json and a dedicated KOEVD_BACKUP_TOKEN secret. The example '
                'config is a template, not an approved operator role or continuous-upload '
                'decision. It cannot start with these missing settings. The default running '
                'private Space has not been switched to this profile. Restored stores remain '
                'quarantined; initial remote backup failure prevents new server startup. '
                'Periodic copies do not guarantee remote commit or RPO.\n')
    files = {p.relative_to(out).as_posix(): {'bytes': p.stat().st_size,
             'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
             for p in sorted(out.rglob('*')) if p.is_file()}
    manifest = dict(previous, files=files, storage='local_database_with_opt_in_remote_snapshot_candidate',
                    operator_configuration_included=False, managed_profile_activated=False)
    (out / 'deployment-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    checked_context(out)
    print(json.dumps({'files': len(files), 'candidate': str(out), 'uploaded': False,
                      'managed_profile_activated': False, 'operator_configuration_included': False}))


if __name__ == '__main__':
    main()
