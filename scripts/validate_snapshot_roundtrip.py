"""Private CPU roundtrip of independently supplied results; no review/approval.

May create a new draft store and snapshot, or restore a separately pinned input.
Does not publish, invoke models, select rank policies, or create cloud resources.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from koevd_eval.results import read_document, validate_index, validate_results
from koevd_eval.snapshots import create_snapshot, restore_snapshot, file_digest
from koevd_eval.storage import LocalSubmissionStore, StorageError, encode
from koevd_eval.submissions import Principal, SubmissionService


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--index', required=True); p.add_argument('--result', action='append', required=True)
    p.add_argument('--output-dir', required=True)
    p.add_argument('--snapshot', help='Existing private snapshot to restore')
    p.add_argument('--snapshot-sha256', help='Outside pinned byte digest; required with --snapshot')
    args = p.parse_args()
    if bool(args.snapshot) != bool(args.snapshot_sha256): p.error('Pin the existing snapshot digest explicitly')
    out = Path(args.output_dir).absolute()
    if out.exists(): raise ValueError('Use a fresh owned validation directory')
    out.mkdir(parents=True, mode=0o700)
    index = read_document(args.index); validate_index(index)
    documents = [read_document(path) for path in args.result]
    for document in documents: validate_results(document, index)
    indexes = {'roundtrip-input': index}
    if not args.snapshot:
        store = LocalSubmissionStore(out / 'source-store')
        service = SubmissionService(store, indexes)
        states = [service.create(Principal('roundtrip-' + str(i), 'operator_local'), document,
                                 'roundtrip-input', key='original-' + str(i)) for i, document in enumerate(documents)]
        saved = create_snapshot(store, indexes, out / 'private-snapshot.zip')
        snapshot, digest = out / 'private-snapshot.zip', saved['sha256']
    else:
        snapshot, digest = Path(args.snapshot), args.snapshot_sha256
        states, saved = None, None
    receipt = restore_snapshot(snapshot, digest, out / 'restored', indexes)
    restored = SubmissionService(LocalSubmissionStore(out / 'restored' / 'store'), indexes)
    if states is None:
        with restored.store.connection() as db:
            states = [restored.store.state(db, row['id'])[0] for row in db.execute('SELECT id FROM submissions ORDER BY owner')]
    if len(states) != len(documents): raise ValueError('Restored submission count differs from independent originals')
    comparisons = []
    for state, document in zip(states, documents):
        owner = Principal(state['owner'], 'operator_local')
        actual = restored.result(owner, state['id'])
        if actual != document or restored.get(owner, state['id']) != state:
            raise ValueError('Restored immutable original or state differs')
        if state['workflow'] != 'draft' or state['publication']['status'] != 'unpublished':
            raise ValueError('Roundtrip validation must remain private and unreviewed')
        if saved is not None:
            if restored.history(owner, state['id']) != service.history(owner, state['id']):
                raise ValueError('Original event history differs')
            with restored.store.connection() as after, store.connection() as before:
                if list(map(tuple,after.execute('SELECT * FROM requests ORDER BY actor,key'))) != list(map(tuple,before.execute('SELECT * FROM requests ORDER BY actor,key'))):
                    raise ValueError('Original idempotency receipt differs')
        comparisons.append({'artifact_sha256': document['content_sha256'], 'records': len(document['records']),
                            'original_exact': True, 'private_draft': True})
    try: restored.public_list()
    except StorageError as error:
        if error.code!='recovery_required': raise
    else: raise ValueError('Restored public lookup was not quarantined')
    if restored.rank_policy.status != 'candidate': raise ValueError('Restore unexpectedly activated rank policy')
    evidence = {'scope': 'private_cpu_snapshot_roundtrip', 'snapshot_sha256': digest,
                'snapshot_bytes': Path(snapshot).stat().st_size, 'index_byte_sha256':file_digest(args.index),
                'restore_receipt': receipt, 'source_snapshot_receipt': saved, 'comparisons': comparisons,
                'new_inference': False, 'human_review': False, 'policy_approved': False,
                'restored_public_lookup_quarantined': True,
                'cloud_provider_verified': False, 'published': False,
                'module_file': __import__('koevd_eval.snapshots',fromlist=['__file__']).__file__}
    (out / 'evidence.json').write_bytes(encode(evidence) + b'\n')
    print(json.dumps({'snapshot_sha256':digest,'models':len(documents),'records':sum(c['records'] for c in comparisons),
                      'private_roundtrip_passed':True,'evidence':str(out/'evidence.json')}))


if __name__ == '__main__': main()
