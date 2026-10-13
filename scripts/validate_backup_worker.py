"""CPU private-backup acceptance with outside existing originals; no inference.

Creates isolated validation drafts, two periodic copies, declared private
withdrawals and a real configured-quota failure. Never reviews/publishes/releases.
"""
import argparse
import json
from pathlib import Path

from koevd_eval.backups import BackupManager
from koevd_eval.recovery import checkpoint,compare,reconcile
from koevd_eval.results import read_document,validate_index,validate_results
from koevd_eval.snapshots import restore_snapshot,file_digest
from koevd_eval.storage import LocalSubmissionStore,StorageError,encode
from koevd_eval.submissions import SubmissionService,Principal


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--index',required=True);p.add_argument('--result',action='append',required=True)
    p.add_argument('--output-dir',required=True);args=p.parse_args()
    if len(args.result)!=2:p.error('Supply exactly two independent existing originals for this acceptance scenario')
    out=Path(args.output_dir).absolute()
    if out.exists():raise ValueError('Use a fresh private validation root')
    out.mkdir(parents=True,mode=0o700)
    index=read_document(args.index);validate_index(index);indexes={'backup-input':index}
    documents=[read_document(path) for path in args.result]
    for document in documents:validate_results(document,index)
    store=LocalSubmissionStore(out/'source-store');service=SubmissionService(store,indexes)
    owners=[Principal('backup-validation-'+str(i),'operator_local') for i in range(2)]
    states=[service.create(owners[i],document,'backup-input',key='create-'+str(i)) for i,document in enumerate(documents)]
    manager=BackupManager(store,indexes,out/'copies',actor='backup-validator')
    observations=[];cycles=[]
    def emit(value):
        cycles.append(value)
        if not value['success']:raise ValueError('Baseline backup cycle failed')
        if len(cycles)==1:
            states[0]=service.action(owners[0],states[0]['id'],'withdraw',expected_version=states[0]['version'],
                reason='CPU backup validation: withdraw an isolated private draft, not a content review',key='withdraw-0')
            status=manager.status()
            if status['changes_pending'] is not True or status['events_since_verified_backup']!=1:
                raise ValueError('Change after first snapshot was incorrectly reported as covered')
            observations.append(status)
    loop=manager.run(cycles=2,interval_seconds=1,emit=emit)
    covered=manager.status()
    if covered['changes_pending'] or covered['events_since_verified_backup']!=0:raise ValueError('Second same-cut pair did not cover the private change')
    manager.max_bytes=65536  # Actual configured quota rejection, no provider double.
    failed=manager.cycle()
    if failed['success'] or failed.get('error_code')!='backup_capacity':raise ValueError('Quota failure was incorrectly completed')
    states[1]=service.action(owners[1],states[1]['id'],'withdraw',expected_version=states[1]['version'],
        reason='CPU backup validation: private draft withdrawal after configured quota failure',key='withdraw-1')
    after_failure=manager.status()
    if after_failure['last_verified_sequence']!=2 or after_failure['changes_pending'] is not True or after_failure['events_since_verified_backup']!=1:
        raise ValueError('Last successful backup/uncopied change was hidden after failure')
    latest=manager.attempts()[1][1]
    receipt=read_document(latest/'COMPLETED.json')
    restored_receipt=restore_snapshot(latest/'snapshot.zip',receipt['snapshot_sha256'],out/'restored',indexes)
    restored=SubmissionService(LocalSubmissionStore(out/'restored/store'),indexes)
    for state,owner,document in zip(states,owners,documents):
        if restored.result(owner,state['id'])!=document:raise ValueError('Backup restore changed an original result')
    with store.connection() as db:current=checkpoint(db,indexes)
    with restored.store.connection() as db:old=checkpoint(db,indexes)
    difference=compare(old,current)
    if difference['matches'] or difference['changed_submissions']!=[states[1]['id']]:raise ValueError('Missed withdrawal not detected in recovered copy')
    try:reconcile(restored.store,current,current['content_sha256'],indexes,actor='backup-validator',administrators=['backup-validator'],
                  statement='CPU rejection test only; no actual operator reconciliation or approval')
    except StorageError as exc:
        if exc.code!='recovery_mismatch':raise
    else:raise ValueError('A stale copy was released')
    try:restored.public_list()
    except StorageError as exc:
        if exc.code!='recovery_required':raise
    else:raise ValueError('Recovered stale copy became public')
    evidence={'scope':'CPU automatic local backup over existing two-model originals with isolated private workflow changes',
              'models':2,'records':sum(len(d['records']) for d in documents),'original_artifact_sha256':[d['content_sha256'] for d in documents],
              'outside_index_byte_sha256':file_digest(args.index),'cycles':cycles,'loop':loop,'after_first_change':observations[0],
              'covered_after_second':covered,'quota_failure':failed,'after_quota_failure_and_new_change':after_failure,
              'restored_receipt':restored_receipt,'recovery_difference':difference,'current_checkpoint_sha256':current['content_sha256'],
              'stale_reconciliation_rejected':True,'private_originals_exact':True,'rpo_guaranteed_seconds':None,
              'new_inference':False,'actual_cloud_storage':False,'actual_operator_reconciliation':False,'human_review':False,'published':False,
              'module_file':__import__('koevd_eval.backups',fromlist=['__file__']).__file__}
    (out/'evidence.json').write_bytes(encode(evidence)+b'\n')
    print(json.dumps({'models':2,'records':evidence['records'],'periodic_successes':2,'quota_failure_preserved':True,
                      'uncopied_events_after_failure':1,'stale_restore_still_quarantined':True,'evidence':str(out/'evidence.json')}))


if __name__=='__main__':main()
