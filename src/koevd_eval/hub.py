"""Explicit, revision-pinned Hub downloads; importing this module is offline."""
import argparse
from pathlib import Path

def download(repo_id, revision, repo_type='model', local_dir=None, local_files_only=False):
    if not repo_id or not revision:
        raise ValueError('repo_id and revision are required; use a release tag or immutable commit.')
    from huggingface_hub import snapshot_download
    return Path(snapshot_download(repo_id=repo_id, repo_type=repo_type, revision=revision,
        local_dir=local_dir, local_files_only=local_files_only,
        ignore_patterns=['review_fp16/*'] if repo_type=='model' else None))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-id',required=True)
    p.add_argument('--revision',required=True)
    p.add_argument('--repo-type',choices=['model','dataset'],default='dataset')
    p.add_argument('--local-dir',required=True)
    p.add_argument('--local-files-only',action='store_true')
    a=p.parse_args()
    print(download(a.repo_id,a.revision,a.repo_type,a.local_dir,a.local_files_only))

if __name__=='__main__': main()
