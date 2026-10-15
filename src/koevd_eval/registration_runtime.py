"""Explicit registered-runtime bootstrap; no hosted resource or token creation."""
from pathlib import Path
import tempfile

from .durability import logical_digest
from .remote_durability import open_acknowledged_store
from .results import read_document, validate_results
from .storage import LocalSubmissionStore, StorageError
from .submissions import Principal, SubmissionService, OPERATOR_REFERENCE_OWNER
from .snapshots import file_digest

REFERENCE_OWNER=OPERATOR_REFERENCE_OWNER


def _documents(catalog):
    """Validate every reference before any first-state object is uploaded."""
    if len(catalog.baselines)!=2:raise ValueError('Two explicitly configured reference artifacts required')
    documents=[]
    for entry in catalog.baselines.values():
        if file_digest(entry['path'])!=entry['sha256']:
            raise StorageError('reference_changed','Pinned reference bytes changed',503)
        document=read_document(entry['path'])
        if document['content_sha256']!=entry['artifact_sha256']:
            raise StorageError('reference_changed','Pinned reference artifact changed',503)
        validate_results(document,catalog.indexes[entry['index_id']]['index'])
        documents.append((entry,document))
    if len({d['content_sha256'] for _,d in documents})!=2:
        raise ValueError('Reference artifacts must be distinct')
    return documents


def _references_present(store, catalog):
    """Check original reference bindings; never republish a withdrawn entry."""
    with store.connection() as db:
        for entry in catalog.baselines.values():
            rows=db.execute('SELECT id FROM submissions WHERE owner=? AND initial_artifact=?',
                            (REFERENCE_OWNER,entry['artifact_sha256'])).fetchall()
            if len(rows)!=1:
                raise StorageError('reference_intake_required','Existing state requires explicit reference intake; no automatic migration',503)
            state,_=store.state(db,rows[0]['id'])
            if state['index_id']!=entry['index_id']:
                raise StorageError('reference_changed','Stored reference index binding differs',503)


def bootstrap_registered_service(catalog, ledger, destination, *, roles, registry=None,
                                 publication_environment='hosted_candidate'):
    """Initial reference adoption is one acknowledged cut, then exact restore.

    The initialization flag is operator configuration. Existing state is only
    restored/validated; no automatic baseline reactivation or metadata rewriting.
    The seeded actor is explicitly operator-local, never a fictional HF account.
    """
    if (not isinstance(roles,dict) or set(roles)!={'reviewers','admins'}
            or any(not isinstance(v,list) for v in roles.values())):
        raise ValueError('Explicit operator roles required')
    head=ledger.head()
    if head is None:
        destination=Path(destination)
        if destination.exists():raise ValueError('Initial state adoption requires a fresh runtime destination')
        documents=_documents(catalog)
        indexes={name:entry['index'] for name,entry in catalog.indexes.items()}
        with tempfile.TemporaryDirectory(prefix='koevd-reference-adoption-') as temporary:
            store=LocalSubmissionStore(Path(temporary)/'prepared',capacity_bytes=ledger.max_database_bytes)
            service=SubmissionService(store,indexes,registry=registry,allow_self_reported_summaries=True,
                                      publication_environment=publication_environment,**roles)
            actor=Principal(REFERENCE_OWNER,'operator_local')
            for entry,document in documents:
                state=service.create(actor,document,entry['index_id'],key='reference-create-'+entry['id'],
                    display_name=entry['label'],description='Operator research reference. Numerical sharing only; generation and measurement limits remain explicit.')
                service.publish_summary(actor,state['id'],consent={'scope':'summary','accepted':True,
                    'rights_statement':'Operator-configured research numerical reference; original text remains private under the configured permission evidence.'},
                    expected_version=state['version'],reason='Initial operator numerical reference intake',key='reference-summary-'+entry['id'])
            with store.connection() as db:digest=logical_digest(db)
            ledger.commit(store,digest,None)
    store=open_acknowledged_store(destination,ledger)
    _references_present(store,catalog)
    return SubmissionService(store,{name:entry['index'] for name,entry in catalog.indexes.items()},
        registry=registry,allow_self_reported_summaries=True,publication_environment=publication_environment,**roles)
