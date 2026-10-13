"""Resolve pinned public GPU artifacts and verify cache bytes against HF metadata.

Uses previous cache snapshots read-only; missing snapshots go in the new root.
This checks artifact bytes, not inference authenticity or classifier accuracy.
"""

import argparse
import fnmatch
import hashlib
import json
from pathlib import Path


def digests(path):
    sha256 = hashlib.sha256()
    blob = hashlib.sha1(b'blob ' + str(path.stat().st_size).encode() + b'\0')
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            sha256.update(block)
            blob.update(block)
    return sha256.hexdigest(), blob.hexdigest()


def pinned_resources(lock):
    """Normalize the documented release repo_id and target id fields eagerly."""
    resources = dict(lock['release_artifacts'])
    resources.update({'target-' + item['id'].split('/')[-1]: item
                      for item in lock['target_models']})
    normalized = {}
    for key, item in resources.items():
        repo = item.get('repo_id', item.get('id'))
        if not isinstance(repo, str) or not repo or len(repo.split('/')) != 2:
            raise ValueError('Expected an owner/repository identifier: ' + key)
        if 'repo_id' in item and 'id' in item and item['repo_id'] != item['id']:
            raise ValueError('Conflicting repository identifiers: ' + key)
        revision = item['revision']
        if not isinstance(revision, str) or len(revision) != 40 or any(c not in '0123456789abcdef' for c in revision):
            raise ValueError('Immutable revision required: ' + key)
        normalized[key] = {**item, 'repo_id': repo}
    return normalized


def main():
    from huggingface_hub import HfApi, snapshot_download
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--previous-cache', required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve(strict=True)
    previous = Path(args.previous_cache).resolve(strict=True)
    lock = json.loads((root / 'source/configs/validation/platform-gpu-candidate-v1.json').read_text())
    resources = pinned_resources(lock)
    api = HfApi(token=False)
    receipt = {'scope': 'pinned_public_artifact_integrity_not_inference', 'artifacts': {}, 'status': 'running'}
    out = root / 'environment/artifact-receipt.json'
    checked_paths = {}

    def save():
        tmp = out.with_suffix('.tmp')
        tmp.write_text(json.dumps(receipt, indent=2))
        tmp.replace(out)

    save()
    def prepare():
        for key, item in resources.items():
            repo, revision = item['repo_id'], item['revision']
            if len(revision) != 40 or any(c not in '0123456789abcdef' for c in revision):
                raise ValueError('Immutable revision required')
            kind = 'dataset' if key == 'dataset' else 'model'
            info = api.repo_info(repo, repo_type=kind, revision=revision, files_metadata=True)
            if info.sha != revision:
                raise ValueError('Resolved revision differs from lock')
            prefix = 'datasets--' if kind == 'dataset' else 'models--'
            snapshot = previous / (prefix + repo.replace('/', '--')) / 'snapshots' / revision
            patterns = ['*.json', '*.safetensors', '*.jinja', '*.txt', '*.md']
            required = [s.rfilename for s in info.siblings
                        if kind == 'dataset' or any(fnmatch.fnmatch(s.rfilename, p) for p in patterns)]
            unavailable = [name for name in required if not (snapshot / name).is_file()]
            # A directory can exist while pointing at another node's absent /root
            # blobs. Never repair its symlinks or count its existence as a cache hit.
            reused = snapshot.is_dir() and not unavailable
            if not reused:
                print('DOWNLOAD ' + key + ' ' + repo + '@' + revision, flush=True)
                snapshot = Path(snapshot_download(repo, repo_type=kind, revision=revision,
                    cache_dir=str(root / 'hf-cache'), token=False,
                    allow_patterns=None if kind == 'dataset' else patterns))
            if any(not (snapshot / name).is_file() for name in required):
                raise ValueError('Required snapshot files remain unavailable')
            files = {}
            total = 0
            for sibling in info.siblings:
                name = sibling.rfilename
                relative = Path(name)
                if relative.is_absolute() or '..' in relative.parts:
                    raise ValueError('Unsafe Hub path')
                path = snapshot / relative
                if not path.is_file():
                    continue
                # Reused base/target may refer to exactly the same cached file.
                fingerprint = (str(path.resolve()), path.stat().st_size)
                if fingerprint not in checked_paths:
                    checked_paths[fingerprint] = digests(path)
                sha256, blob = checked_paths[fingerprint]
                lfs = sibling.lfs
                expected = getattr(lfs, 'sha256', None) if lfs else sibling.blob_id
                actual = sha256 if lfs else blob
                if not expected or actual != expected:
                    raise ValueError('Hub metadata checksum mismatch: ' + key + '/' + name)
                if sibling.size is not None and path.stat().st_size != sibling.size:
                    raise ValueError('Hub metadata byte count mismatch')
                files[name] = {'bytes': path.stat().st_size, 'sha256': sha256,
                               'hub_checksum_kind': 'lfs_sha256' if lfs else 'git_blob_sha1'}
                total += path.stat().st_size
            if not files or (kind == 'model' and not any(n.endswith('.safetensors') for n in files)):
                raise ValueError('Missing required model/data files')
            if kind == 'model':
                index_path = snapshot / 'model.safetensors.index.json'
                if index_path.is_file():
                    needed = set(json.loads(index_path.read_text())['weight_map'].values())
                    if not needed <= set(files):
                        raise ValueError('Missing model shard')
            receipt['artifacts'][key] = {'repo_id': repo, 'revision': revision, 'snapshot': str(snapshot),
                                         'reused_previous_cache': reused, 'verified_files': files,
                                         'previous_cache_unavailable_files': unavailable,
                                         'bytes': total}
            save()
            print('VERIFIED ' + key + ' files=' + str(len(files)), flush=True)

    try:
        prepare()
    except BaseException as exc:
        receipt.update(status='failed', error_type=type(exc).__name__, error=str(exc))
        save()
        raise
    receipt['status'] = 'passed'
    save()
    print(json.dumps({'artifact_integrity': 'passed', 'receipt': str(out), 'gpu_inference_verified': False}), flush=True)


if __name__ == '__main__':
    main()
