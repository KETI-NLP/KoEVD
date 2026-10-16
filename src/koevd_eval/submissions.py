"""Explicit local submission workflow, independent of anonymous upload sessions.

Trusted application code supplies a Principal after authenticating the caller.
This module does not implement OAuth. Never construct a Principal from an HTTP
body, query parameter, uploaded username, or uploaded role.
"""
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import uuid

from .diagnostics import VERSION as ANALYSIS_VERSION, analyze, compare
from .profile_cache import NumericalProfileCache, numerical_profile, numerical_comparison
from .eligibility import VERSION as ADMISSION_VERSION, RankPolicy, evaluate_admission, _boards_from_admissions
from .generation_receipts import active_evidence, validate_receipt
from .results import canonical_hash, validate_index, validate_results
from .storage import LocalSubmissionStore, StorageError, encode, token

MAX_REVISIONS, MAX_EVENTS = 100, 1000
MAX_LEADERBOARD_ENTRIES, MAX_LEADERBOARD_BYTES = 512, 32 * 1024**2
MAX_PUBLIC_COMPARISON_BYTES = 128 * 1024**2
OPERATOR_REFERENCE_OWNER = 'koevd-operator-reference'


@dataclass(frozen=True)
class Principal:
    subject: str
    authentication_source: str


def _actor(actor):
    if not isinstance(actor, Principal) or actor.authentication_source not in ('operator_local', 'hf_oauth'):
        raise StorageError('identity_required', 'Trusted application identity required', 401)
    token(actor.subject, 'identity subject')
    return {'subject':actor.subject, 'authentication_source':actor.authentication_source}


def _text(value, name):
    if not isinstance(value, str) or not value.strip() or len(value.encode('utf-8')) > 4096:
        raise StorageError('invalid_text', 'A bounded nonempty ' + name + ' is required')
    return value


def _display(display_name, description, *, default_name=None):
    if display_name is None:
        display_name = default_name
        if isinstance(display_name, str) and len(display_name) > 200:
            display_name = display_name[:197]+'…'
    if (not isinstance(display_name, str) or not display_name.strip()
            or len(display_name) > 200 or len(display_name.encode('utf-8')) > 800):
        raise StorageError('invalid_display_name', 'Result display name must contain 1–200 characters')
    if not isinstance(description, str) or len(description) > 2000 or len(description.encode('utf-8')) > 8000:
        raise StorageError('invalid_description', 'Result description must contain at most 2000 characters')
    return {'display_name':display_name.strip(), 'description':description.strip()}


class SubmissionService:
    """Private original/revision/history, distinct review and publication axes.

    Roles come only from operator configuration. Generation and measurements
    remain user-reported. Local publication is a candidate projection, not an
    external publish or official ranking. Durable remote storage is still needed.
    """
    def __init__(self, store, indexes, *, reviewers=(), admins=(), clock=None,
                 registry=None, rank_policy=None, allow_self_reported_summaries=False,
                 publication_environment='local_candidate'):
        if not isinstance(store, LocalSubmissionStore): raise ValueError('Expected local persistence adapter')
        self.store = store
        self.indexes = deepcopy(indexes)
        if not isinstance(indexes, dict) or not indexes: raise ValueError('Operator indexes required')
        for name, index in self.indexes.items():
            token(name, 'index ID'); validate_index(index)
        self.reviewers, self.admins = frozenset(reviewers), frozenset(admins)
        for subject in self.reviewers | self.admins: token(subject, 'operator role subject')
        self.clock = clock or (lambda: datetime.now(timezone.utc).isoformat())
        from .protocols import ProtocolRegistry
        if registry is not None and not isinstance(registry, ProtocolRegistry):
            raise ValueError('Expected operator protocol registry')
        if rank_policy is not None and not isinstance(rank_policy, RankPolicy):
            raise ValueError('Expected operator rank policy, never an uploaded policy')
        self.registry, self.rank_policy = registry, rank_policy or RankPolicy()
        if type(allow_self_reported_summaries) is not bool:
            raise ValueError('Summary publication must be explicit operator configuration')
        self.allow_self_reported_summaries = allow_self_reported_summaries
        if publication_environment not in ('local_candidate','hosted_candidate','hosted_service'):
            raise ValueError('Explicit operator deployment environment required')
        self.publication_environment = publication_environment
        self.profile_cache = NumericalProfileCache()
        store.register_indexes({name:index['content_sha256'] for name,index in self.indexes.items()})

    @property
    def review_requests_enabled(self):
        # An independent admin can review and publish; no request is queued
        # when the deployment has nobody authorized to finish it.
        return bool(self.admins)

    def _index(self, name):
        token(name, 'index ID')
        if name not in self.indexes: raise StorageError('unknown_operator_index', 'Index is not selected by the operator')
        return self.indexes[name]

    def _document(self, document, name):
        from .results import MAX_BYTES
        value = deepcopy(document)
        if len(encode(value)) > MAX_BYTES: raise StorageError('artifact_too_large', 'Result exceeds upload size', 413)
        validate_results(value, self._index(name))
        return value

    def _visible(self, state, actor):
        _actor(actor)
        if actor.subject != state['owner'] and actor.subject not in self.reviewers | self.admins:
            raise StorageError('not_found', 'Submission not found', 404)

    def _own(self, state, actor):
        self._visible(state, actor)
        if state['owner'] != actor.subject: raise StorageError('owner_required', 'Only the submitter may change this revision', 403)

    def _review(self, state, actor, *, publish=False):
        self._visible(state, actor)
        roles = self.admins if publish else self.reviewers | self.admins
        if actor.subject not in roles or actor.subject == state['owner']:
            raise StorageError('independent_reviewer_required', 'An independent operator reviewer is required', 403)

    @staticmethod
    def _version(state, expected, *, allow_withdrawn=False):
        if type(expected) is not int or expected < 1: raise StorageError('version_required', 'Expected version is required')
        if state['version'] != expected: raise StorageError('stale_version', 'Submission changed; reload before retrying', 409)
        if state['workflow'] == 'withdrawn' and not allow_withdrawn: raise StorageError('withdrawn', 'Restore this withdrawn registration as a private draft before changing it', 409)

    def _event(self, db, state, action, actor, details):
        limit = MAX_EVENTS if action in ('withdraw','unpublish') else MAX_EVENTS - 1
        if state['version'] >= limit: raise StorageError('history_capacity', 'Submission history capacity reached', 409)
        state['version'] += 1
        state['updated_at'] = self.clock()
        self.store.event(db,state,action=action,actor=_actor(actor),timestamp=state['updated_at'],details=details)
        return deepcopy(state)

    def create(self, actor, document, index_id, *, key, display_name=None, description=''):
        _actor(actor)
        document = self._document(document, index_id)
        display = _display(display_name, description, default_name=document['run']['model']['id'])
        request = {'action':'create','artifact':document['content_sha256'],'index':index_id}
        if display_name is not None or description:
            request['display'] = display
        def operation(db):
            if db.execute('SELECT id FROM submissions WHERE owner=? AND initial_artifact=?', (actor.subject,document['content_sha256'])).fetchone():
                raise StorageError('duplicate_submission', 'This original already has a submission; use its ID or original idempotency key', 409)
            digest = self.store.put_artifact(db, document)
            now = self.clock(); sid = uuid.uuid4().hex
            state = {'format':'koevd-submission-v1','id':sid,'owner':actor.subject,'index_id':index_id,
                     'version':0,'head_revision':1,'workflow':'draft','created_at':now,'updated_at':now,
                     'consent':None,'approval':None,'publication':{'status':'unpublished','revision':None,'scope':None},
                     'verification':{'structure':'validated_against_operator_index','generation':'user_reported','measurement':'measurement_limited'},
                     'display':display}
            db.execute('INSERT INTO submissions VALUES(?,?,?,?)', (sid,actor.subject,digest,encode(state).decode()))
            revision = {'number':1,'parent':None,'kind':'original','artifact_sha256':digest,'created_at':now,'actor':_actor(actor)}
            db.execute('INSERT INTO revisions VALUES(?,?,?,?,?)',(sid,1,None,digest,encode(revision).decode()))
            return self._event(db,state,'create',actor,{'revision':1,'artifact_sha256':digest})
        return self.store.apply(actor.subject,key,request,operation)

    def update_display(self, actor, submission, *, display_name, description='', expected_version, key):
        """Owner metadata only; do not reseal or rewrite the original artifact."""
        _actor(actor)
        display = _display(display_name, description)
        current = self.get(actor, submission); self._own(current, actor)
        request = {'action':'update_display','id':submission,'expected_version':expected_version,'display':display}
        def operation(db):
            state, _ = self.store.state(db, submission)
            self._own(state, actor); self._version(state, expected_version)
            state['display'] = display
            return self._event(db, state, 'update_display', actor, {'display':display})
        return self.store.apply(actor.subject, key, request, operation)

    def publish_summary(self, actor, submission, *, consent, expected_version, reason, key):
        """Explicit owner-consented numerical publication, never response approval.

        This is a separate opt-in deployment policy. It does not create an
        operator review, generation receipt, accuracy claim or official rank.
        """
        _actor(actor); _text(reason, 'summary publication reason')
        if not self.allow_self_reported_summaries:
            raise StorageError('summary_publication_disabled', 'Self-reported summary publication is not enabled', 403)
        if (not isinstance(consent, dict) or set(consent) != {'scope','accepted','rights_statement'}
                or consent.get('accepted') is not True or consent.get('scope') != 'summary'):
            raise StorageError('summary_consent_required', 'Explicit summary-only publication consent required')
        _text(consent['rights_statement'], 'summary rights statement')
        consent = deepcopy(consent)
        current = self.get(actor, submission); self._own(current, actor)
        request = {'action':'publish_summary','id':submission,'expected_version':expected_version,
                   'reason':reason,'consent':consent}
        def operation(db):
            state, _ = self.store.state(db, submission)
            self._own(state, actor); self._version(state, expected_version)
            if state['workflow'] not in ('draft','rejected','registered'):
                raise StorageError('invalid_transition', 'Finish the current review before summary publication', 409)
            if state['publication']['status'] == 'published' and state['publication']['revision'] == state['head_revision']:
                raise StorageError('already_published', 'Current revision is already published', 409)
            state.update(workflow='registered', consent=consent, approval=None,
                         publication={'status':'published','revision':state['head_revision'],'scope':'summary'})
            return self._event(db, state, 'publish_summary', actor,
                               {'revision':state['head_revision'],'reason':reason,'consent':consent,
                                'permission_review':'not_operator_reviewed'})
        return self.store.apply(actor.subject, key, request, operation)

    def get(self, actor, submission):
        _actor(actor)
        with self.store.connection() as db:
            state, _ = self.store.state(db,submission); self._visible(state,actor)
            return deepcopy(state)

    def history(self, actor, submission):
        _actor(actor)
        with self.store.connection() as db:
            state, events = self.store.state(db,submission); self._visible(state,actor)
            revisions = [json.loads(row['data']) for row in db.execute('SELECT data FROM revisions WHERE submission=? ORDER BY number',(submission,))]
            return {'state':state,'events':events,'revisions':revisions}

    def result(self, actor, submission, *, revision=None):
        _actor(actor)
        with self.store.connection() as db:
            state,_ = self.store.state(db,submission); self._visible(state,actor)
            return self._result(db,state,state['head_revision'] if revision is None else revision)

    def _result(self, db, state, revision):
        if type(revision) is not int or revision < 1: raise StorageError('invalid_revision','Invalid revision')
        row = db.execute('SELECT artifact,data FROM revisions WHERE submission=? AND number=?',(state['id'],revision)).fetchone()
        if row is None: raise StorageError('not_found','Revision not found',404)
        document = self.store.artifact(db,row['artifact'])
        # Exact immutable bytes were already fully validated before their transaction.
        if document['input_index_sha256'] != self._index(state['index_id'])['content_sha256']:
            raise StorageError('store_integrity','Stored result index changed',503)
        return document

    def revise(self, actor, submission, document, *, expected_version, kind, reason, key):
        _actor(actor); _text(reason,'revision reason')
        if kind not in ('rerun','measurement_recheck'): raise StorageError('invalid_revision_kind','Unknown revision kind')
        initial = self.get(actor,submission); self._own(initial,actor)
        document = self._document(document,initial['index_id'])
        request = {'action':'revise','id':submission,'artifact':document['content_sha256'],
                   'expected_version':expected_version,'kind':kind,'reason':reason}
        def operation(db):
            state,_ = self.store.state(db,submission); self._own(state,actor); self._version(state,expected_version)
            number = state['head_revision'] + 1
            if number > MAX_REVISIONS: raise StorageError('revision_capacity','Revision capacity reached',409)
            previous = self._result(db,state,state['head_revision'])
            if previous['run']['model']['id'] != document['run']['model']['id']:
                raise StorageError('different_target','A different target model needs a separate submission',409)
            if previous['content_sha256'] == document['content_sha256']:
                raise StorageError('unchanged_revision','New revision must have different contents',409)
            if kind == 'measurement_recheck':
                def frozen(value):
                    records = sorted(({k:v for k,v in row.items() if k!='measurement'} for row in value['records']),key=lambda r:(r['task'],r['sample_id']))
                    return {'model':value['run']['model'],'generation':value['run']['generation'],'records':records}
                if frozen(previous) != frozen(document):
                    raise StorageError('generation_changed','Remeasurement must preserve every generation object and declaration',409)
            digest = self.store.put_artifact(db,document)
            revision = {'number':number,'parent':state['head_revision'],'kind':kind,'artifact_sha256':digest,'created_at':self.clock(),'actor':_actor(actor)}
            db.execute('INSERT INTO revisions VALUES(?,?,?,?,?)',(submission,number,state['head_revision'],digest,encode(revision).decode()))
            state.update(head_revision=number,workflow='draft',consent=None,approval=None)
            # An earlier published revision remains published until explicit replacement or withdrawal.
            return self._event(db,state,'revise',actor,{'revision':number,'parent':revision['parent'],'kind':kind,'reason':reason})
        return self.store.apply(actor.subject,key,request,operation)

    def action(self, actor, submission, action, *, expected_version, reason, key, consent=None, rights_evidence=None):
        _actor(actor); _text(reason,'action reason')
        if action not in ('request_review','start_review','approve','publish','reject','withdraw','cancel_review','unpublish','reopen'):
            raise StorageError('invalid_action','Unknown submission action')
        if action == 'request_review':
            if not self.review_requests_enabled:
                raise StorageError('review_unavailable','Independent publication review is not enabled; use numerical sharing instead',409)
            if not isinstance(consent,dict) or set(consent) != {'scope','rights_statement','accepted'} or consent.get('accepted') is not True or consent.get('scope') not in ('summary','responses'):
                raise StorageError('consent_required','Explicit summary/response publication consent required')
            _text(consent['rights_statement'],'rights statement')
            consent = deepcopy(consent)
        elif consent is not None: raise StorageError('unexpected_consent','Consent only belongs to a review request')
        if action == 'approve': _text(rights_evidence,'reviewed rights evidence')
        elif rights_evidence is not None: raise StorageError('unexpected_rights_evidence','Rights evidence belongs to approval')
        # Check current actor access before any cached response is replayed.
        current = self.get(actor,submission)
        if action == 'withdraw':
            if actor.subject != current['owner'] and actor.subject not in self.admins:
                raise StorageError('withdrawal_forbidden','Only the submitter or administrator may withdraw',403)
        elif action in ('request_review','cancel_review','unpublish','reopen'): self._own(current,actor)
        else: self._review(current,actor,publish=action=='publish')
        request = {'action':action,'id':submission,'expected_version':expected_version,'reason':reason,
                   'consent':consent,'rights_evidence':rights_evidence}
        def operation(db):
            state,events = self.store.state(db,submission)
            self._version(state,expected_version,allow_withdrawn=action=='reopen')
            workflow = state['workflow']
            if action == 'reopen':
                if workflow!='withdrawn': raise StorageError('invalid_transition','Only a withdrawn registration can be restored',409)
                state.update(workflow='draft',consent=None,approval=None,
                             publication={'status':'withdrawn','revision':None,'scope':None})
            elif action == 'unpublish':
                if state['publication']['status']!='published': raise StorageError('invalid_transition','This result is not publicly shared',409)
                state.update(workflow='draft',consent=None,approval=None,
                             publication={'status':'withdrawn','revision':None,'scope':None})
            elif action == 'cancel_review':
                if workflow not in ('pending','under_review'): raise StorageError('invalid_transition','There is no active review request',409)
                position=next((i for i in range(len(events)-1,-1,-1) if events[i]['action']=='request_review'),None)
                if position is None or position==0: raise StorageError('store_integrity','Review origin is missing',503)
                previous=events[position-1]['state']
                state.update(workflow=previous['workflow'],consent=deepcopy(previous['consent']),approval=deepcopy(previous['approval']))
            elif action == 'request_review':
                if workflow not in ('draft','rejected','registered'): raise StorageError('invalid_transition','Revision is already in review',409)
                state.update(workflow='pending',consent=consent,approval=None)
            elif action == 'start_review':
                if workflow!='pending': raise StorageError('invalid_transition','Review must begin from pending',409)
                state['workflow']='under_review'
            elif action == 'approve':
                if workflow!='under_review' or not state['consent']: raise StorageError('invalid_transition','Approval requires consent and active review',409)
                state.update(workflow='approved',approval={'revision':state['head_revision'],'reviewer':actor.subject,
                    'rights_evidence':rights_evidence,'scope':state['consent']['scope'],'approved_at':self.clock()})
            elif action == 'publish':
                if workflow!='approved' or state['approval']['revision']!=state['head_revision']:
                    raise StorageError('invalid_transition','Publication requires approval of the current revision',409)
                if (state['publication']['status']=='published' and state['publication']['revision']==state['head_revision']
                        and state['publication']['scope']==state['approval']['scope']):
                    raise StorageError('already_published','Current revision is already published',409)
                state['publication']={'status':'published','revision':state['head_revision'],'scope':state['approval']['scope']}
            elif action == 'reject':
                if workflow!='under_review': raise StorageError('invalid_transition','Rejection requires active review',409)
                state.update(workflow='rejected',approval=None)
            else:
                state.update(workflow='withdrawn',consent=None,approval=None,publication={'status':'withdrawn','revision':None,'scope':None})
            return self._event(db,state,action,actor,{'revision':state['head_revision'],'reason':reason,
                                                   'consent':consent,'rights_evidence':rights_evidence})
        return self.store.apply(actor.subject,key,request,operation)

    def _receipt_operator(self, state, actor):
        self._review(state, actor, publish=True)
        if actor.authentication_source != 'operator_local':
            raise StorageError('local_operator_required', 'Generation receipt intake is a local operator operation', 403)

    def accept_generation_receipt(self, actor, submission, receipt, *, revision,
                                  expected_version, reason, key):
        """Persist an independently reviewed operator assertion, not hash proof.

        Only local configured administrators may accept; no HTTP intake route is
        provided. The operator is responsible for reviewing the referenced files.
        Acceptance does not publish, approve rights, ratify policy or fix classifiers.
        """
        _actor(actor); _text(reason, 'receipt acceptance reason')
        initial = self.get(actor, submission); self._receipt_operator(initial, actor)
        with self.store.connection() as db:
            document = self._result(db, initial, revision)
        receipt, evidence = validate_receipt(receipt, document, self._index(initial['index_id']))
        request = {'action':'accept_generation_receipt', 'id':submission, 'revision':revision,
                   'receipt':receipt, 'expected_version':expected_version, 'reason':reason}
        def operation(db):
            state, events = self.store.state(db, submission)
            self._receipt_operator(state, actor); self._version(state, expected_version)
            current = self._result(db, state, revision)
            validate_receipt(receipt, current, self._index(state['index_id']))
            if active_evidence(events, revision, current, self._index(state['index_id'])) is not None:
                raise StorageError('receipt_already_active', 'Revoke the active receipt before replacing it', 409)
            return self._event(db, state, 'accept_generation_receipt', actor,
                               {'revision':revision, 'receipt':receipt,
                                'receipt_sha256':evidence.receipt_sha256, 'reason':reason})
        return self.store.apply(actor.subject, key, request, operation)

    def revoke_generation_receipt(self, actor, submission, *, revision, receipt_sha256,
                                  expected_version, reason, key):
        _actor(actor); _text(reason, 'receipt revocation reason')
        initial = self.get(actor, submission); self._receipt_operator(initial, actor)
        request = {'action':'revoke_generation_receipt', 'id':submission, 'revision':revision,
                   'receipt_sha256':receipt_sha256, 'expected_version':expected_version, 'reason':reason}
        def operation(db):
            state, events = self.store.state(db, submission)
            self._receipt_operator(state, actor); self._version(state, expected_version)
            document = self._result(db, state, revision)
            evidence = active_evidence(events, revision, document, self._index(state['index_id']))
            if evidence is None or evidence.receipt_sha256 != receipt_sha256:
                raise StorageError('active_receipt_not_found', 'The requested generation receipt is not active', 409)
            return self._event(db, state, 'revoke_generation_receipt', actor,
                               {'revision':revision, 'receipt_sha256':receipt_sha256, 'reason':reason})
        return self.store.apply(actor.subject, key, request, operation)

    @staticmethod
    def _public(state):
        if state['publication']['status']!='published' or state['workflow']=='withdrawn':
            raise StorageError('not_found','Published submission not found',404)

    def public_result(self, submission):
        with self.store.connection() as db:
            self._recovery_ready(db)
            state,_ = self.store.state(db,submission); self._public(state)
            if state['publication']['scope']!='responses': raise StorageError('responses_private','Original responses are not published',403)
            return self._result(db,state,state['publication']['revision'])

    def public_summary(self, submission):
        registry,policy=self.registry,self.rank_policy
        with self.store.connection() as db:
            self._recovery_ready(db,policy)
            state,events = self.store.state(db,submission); self._public(state)
            document = self._result(db,state,state['publication']['revision'])
            evidence = active_evidence(events,state['publication']['revision'],document,self._index(state['index_id']))
        # CPU analysis must not hold the DB read lock and delay a withdrawal commit.
        index = self._index(state['index_id'])
        registry_hash = canonical_hash(registry.definitions) if registry is not None else None
        identity = {'artifact':document['content_sha256'], 'index':index['content_sha256'],
                    'analysis':ANALYSIS_VERSION, 'admission':ADMISSION_VERSION, 'policy':policy.sha256,
                    'registry':registry_hash, 'evidence':evidence.receipt_sha256 if evidence else None,
                    'resamples':0, 'seed':1729}
        def compute():
            return {'profile':numerical_profile(analyze(document,index,resamples=0)),
                    'admission':evaluate_admission(document,index,evidence=evidence,
                                                   registry=registry,policy=policy)}
        cached = self.profile_cache.get_or_compute(identity,compute)
        profile, admission = cached['profile'], cached['admission']
        with self.store.connection() as db:
            current,_ = self.store.state(db,submission); self._public(current)
            self._recovery_ready(db,policy)
            if (current['publication'] != state['publication'] or current['version'] != state['version']
                    or self.rank_policy!=policy or self.registry is not registry
                    or self._index(state['index_id'])['content_sha256'] != index['content_sha256']
                    or (canonical_hash(registry.definitions) if registry is not None else None) != registry_hash):
                raise StorageError('publication_changed','Published revision changed; retry the summary',409)
        verification = deepcopy(state['verification'])
        if evidence is not None:
            verification['generation'] = 'operator_reproduced' if evidence.execution_scope == 'actual_gpu' else 'cpu_fixture_only'
        return {'format':'koevd-public-candidate-summary-v1','submission_id':submission,
                'origin':'operator_reference' if state['owner']==OPERATOR_REFERENCE_OWNER else 'submitted_run',
                'revision':state['publication']['revision'],'scope':state['publication']['scope'],
                'model':deepcopy(document['run']['model']),'display':deepcopy(state.get('display')),
                'protocol_sha256':canonical_hash(profile['protocol']),
                'tasks':profile['tasks'],'task3_task5':profile['task3_task5'],'statistics':profile['statistics'],
                'analysis':profile,'generation':deepcopy(document['run']['generation']),
                'verification':verification,'official_rank_eligible':bool(admission['eligible_metric_ids']),
                'rank_policy_status':admission['policy']['status'],'rank_admission':admission,
                'publication_environment':self.publication_environment}

    def public_profile(self, submission):
        """Current public numerical analysis; summary scope never returns cases."""
        # public_summary performs authoritative publication/recovery checks before
        # and after scoring, including cache hits. Use its checked result as the
        # response envelope rather than a second unchecked cache read.
        return self.public_summary(submission)

    def _board_states(self, db):
        """Complete bounded public membership, never a page labeled as a rank."""
        self._recovery_ready(db)
        rows=db.execute("SELECT id FROM submissions WHERE json_extract(state,'$.publication.status')='published' AND json_extract(state,'$.workflow')!='withdrawn' ORDER BY id LIMIT ?",
                        (MAX_LEADERBOARD_ENTRIES+1,)).fetchall()
        if len(rows)>MAX_LEADERBOARD_ENTRIES:
            raise StorageError('leaderboard_capacity','Publication set exceeds the current comparison capacity; no partial ranks were returned',503)
        states=[]
        for row in rows:
            state,events=self.store.state(db,row['id']);self._public(state)
            # Retain membership metadata only, not every publication's history.
            states.append((state,[]))
        return states

    def public_leaderboard(self):
        """Assemble all current publications from engine-computed admission.

        Operator-supplied policy/registry stay outside uploads. Raw responses,
        owners and private review evidence never enter this public projection.
        Default candidate policy returns exclusions and no official ranks.
        """
        entries,publications,total=[],[],0
        registry,policy=self.registry,self.rank_policy
        registry_hash=canonical_hash(registry.definitions) if registry is not None else None
        with self.store.connection() as db:
            snapshot=self._board_states(db)
        measured = {}
        for state,_ in sorted(snapshot,key=lambda item:(item[0]['created_at'],item[0]['id'])):
            try: summary=self.public_summary(state['id'])
            except StorageError as exc:
                if exc.code=='not_found':
                    raise StorageError('publication_changed','Public comparison changed; retry the complete comparison',409) from None
                raise
            report=summary['rank_admission']
            if report['policy_sha256']!=policy.sha256:
                raise StorageError('publication_changed','Operator policy changed; retry the complete comparison',409)
            artifact=report['artifact_sha256']
            duplicate_of=measured.get(artifact)
            if duplicate_of is None:
                measured[artifact]=state['id']
            total+=0 if duplicate_of else len(encode(report))
            if total>MAX_LEADERBOARD_BYTES:
                raise StorageError('leaderboard_capacity','Numerical admissions exceed comparison capacity; no partial ranks were returned',503)
            if duplicate_of is None:entries.append((state['id'],summary['model'],report))
            publications.append({'submission_id':state['id'],'revision':summary['revision'],
                'artifact_sha256':report['artifact_sha256'],'scope':summary['scope'],
                'model':summary['model'],'display':summary['display'],'verification':summary['verification'],
                'origin':summary['origin'],
                'duplicate_of':duplicate_of})
        # No all-original memory pool or repeated admission computation on hits.
        result=_boards_from_admissions(entries,policy=policy)
        expected=[(s['id'],s['version'],s['publication']) for s,_ in snapshot]
        with self.store.connection() as db:
            current=[(s['id'],s['version'],s['publication']) for s,_ in self._board_states(db)]
            if (current!=expected or self.rank_policy!=policy or self.registry is not registry
                    or (canonical_hash(registry.definitions) if registry is not None else None)!=registry_hash):
                raise StorageError('publication_changed','Public comparison changed; retry the complete comparison',409)
        return {**result,'publication_environment':self.publication_environment,
                'policy_status':policy.status,'official_ranking_enabled':policy.status=='ratified',
                'publication_count':len(publications),'publications':publications,
                'distinct_artifact_count':len(measured),
                'coverage':'complete_current_publication_snapshot','bootstrap_resamples':0}

    def public_comparison(self, left, right):
        """Paired original measurements, projected to numbers for any public scope."""
        token(left,'left submission');token(right,'right submission')
        if left==right:raise StorageError('distinct_runs_required','Select two different published runs')
        registry,policy=self.registry,self.rank_policy
        registry_hash=canonical_hash(registry.definitions) if registry is not None else None
        with self.store.connection() as db:
            self._recovery_ready(db,policy)
            states=[self.store.state(db,sid)[0] for sid in (left,right)]
            for state in states:self._public(state)
            original_bytes=0
            for state in states:
                row=db.execute('SELECT length(a.data) AS size FROM revisions r JOIN artifacts a ON r.artifact=a.digest WHERE r.submission=? AND r.number=?',
                               (state['id'],state['publication']['revision'])).fetchone()
                if row is None:raise StorageError('store_integrity','Published artifact missing',503)
                original_bytes+=row['size']
            if original_bytes>MAX_PUBLIC_COMPARISON_BYTES:
                raise StorageError('comparison_capacity','Paired originals exceed the current comparison limit',503)
        try: summaries=[self.public_summary(sid) for sid in (left,right)]
        except StorageError as exc:
            if exc.code=='not_found':
                raise StorageError('publication_changed','Comparison changed; retry with current publications',409) from None
            raise
        documents,indexes,total=[],[],0
        with self.store.connection() as db:
            self._recovery_ready(db,policy)
            for state in states:
                current,_=self.store.state(db,state['id'])
                if current!=state:
                    raise StorageError('publication_changed','Comparison changed; retry with current publications',409)
                revision=state['publication']['revision']
                row=db.execute('SELECT length(a.data) AS size FROM revisions r JOIN artifacts a ON r.artifact=a.digest WHERE r.submission=? AND r.number=?',
                               (state['id'],revision)).fetchone()
                if row is None:raise StorageError('store_integrity','Published artifact missing',503)
                total+=row['size']
                if total>MAX_PUBLIC_COMPARISON_BYTES:
                    raise StorageError('comparison_capacity','Paired originals exceed the current comparison limit',503)
                documents.append(self._result(db,state,revision));indexes.append(self._index(state['index_id']))
        if documents[0]['content_sha256']==documents[1]['content_sha256']:
            raise StorageError('duplicate_artifacts','These registrations contain the same original result')
        identity={'kind':'public_pair','analysis':ANALYSIS_VERSION,'policy':policy.sha256,
                  'registry':registry_hash,'left':documents[0]['content_sha256'],
                  'right':documents[1]['content_sha256'],'indexes':[i['content_sha256'] for i in indexes],
                  'resamples':0,'seed':1729}
        comparison=self.profile_cache.get_or_compute(identity,lambda:numerical_comparison(
            compare(documents[0],indexes[0],documents[1],indexes[1],resamples=0)))
        with self.store.connection() as db:
            self._recovery_ready(db,policy)
            changed=any(self.store.state(db,state['id'])[0]!=state for state in states)
            if (changed or self.rank_policy!=policy or self.registry is not registry
                    or (canonical_hash(registry.definitions) if registry is not None else None)!=registry_hash
                    or [self._index(s['index_id'])['content_sha256'] for s in states]!=identity['indexes']):
                raise StorageError('publication_changed','Comparison changed; retry with current publications',409)
        return {'format':'koevd-public-comparison-v1','left':summaries[0],'right':summaries[1],
                'comparison':comparison,'raw_cases_included':False,
                'approved_originals_available':all(s['scope']=='responses' for s in summaries),
                'bootstrap_resamples':0,'publication_environment':self.publication_environment}

    def visible_list(self, actor, *, after='', limit=50):
        """Bounded identity-filtered page; roles come only from operator config."""
        _actor(actor)
        if type(limit) is not int or not 1<=limit<=100:raise StorageError('page_limit','Select a page size from 1 to 100')
        if after:token(after,'submission cursor')
        with self.store.connection() as db:
            if actor.subject in self.reviewers | self.admins:
                rows=db.execute('SELECT id FROM submissions WHERE id>? ORDER BY id LIMIT ?', (after,limit+1)).fetchall()
            else:
                rows=db.execute('SELECT id FROM submissions WHERE owner=? AND id>? ORDER BY id LIMIT ?', (actor.subject,after,limit+1)).fetchall()
            states=[]
            for row in rows[:limit]:
                state,_=self.store.state(db,row['id']);self._visible(state,actor);states.append(state)
            return {'items':states,'next_cursor':states[-1]['id'] if len(rows)>limit else None}

    def public_list(self):
        policy=self.rank_policy
        with self.store.connection() as db:
            self._recovery_ready(db,policy)
            result=[]
            for row in db.execute('SELECT id FROM submissions ORDER BY id'):
                state,_ = self.store.state(db,row['id'])
                if state['publication']['status']=='published' and state['workflow']!='withdrawn':
                    result.append(self._publication_reference(state,policy))
            return result

    @staticmethod
    def _publication_reference(state,policy):
        # Listing metadata does not rescore metrics or inspect generation receipts.
        # A ratified policy cannot make a listing's uncomputed admission false.
        return {'submission_id':state['id'],'revision':state['publication']['revision'],
                'origin':'operator_reference' if state['owner']==OPERATOR_REFERENCE_OWNER else 'submitted_run',
                'display':deepcopy(state.get('display')),
                'scope':state['publication']['scope'],
                'official_rank_eligible':False if policy.status=='candidate' else None,
                'rank_policy_status':policy.status,
                'rank_eligibility_status':'policy_not_ratified' if policy.status=='candidate' else 'not_evaluated_in_listing'}

    def public_page(self, *, after='', limit=50):
        if type(limit) is not int or not 1<=limit<=100:raise StorageError('page_limit','Select a page size from 1 to 100')
        if after:token(after,'submission cursor')
        policy=self.rank_policy
        with self.store.connection() as db:
            self._recovery_ready(db,policy)
            rows=db.execute("SELECT id FROM submissions WHERE id>? AND json_extract(state,'$.publication.status')='published' AND json_extract(state,'$.workflow')!='withdrawn' ORDER BY id LIMIT ?",(after,limit+1)).fetchall()
            items=[]
            for row in rows[:limit]:
                state,_=self.store.state(db,row['id']);self._public(state)
                items.append(self._publication_reference(state,policy))
            return {'items':items,'next_cursor':items[-1]['submission_id'] if len(rows)>limit else None}

    def check_readiness(self):
        """Read storage/fencing/recovery state; never compute profiles or save."""
        connection = getattr(self.store, 'readiness_connection', self.store.connection)
        with connection() as db:
            self._recovery_ready(db)
            db.execute('SELECT 1').fetchone()

    def _recovery_ready(self, db, policy=None):
        from .recovery import require_ready
        require_ready(db,policy_sha256=(policy or self.rank_policy).sha256)


def main():
    """Operator-only local CLI. --actor is an OS/operator assertion, not login."""
    import argparse
    import os
    from pathlib import Path
    import sys
    from .common import configure_cli_stdio
    from .results import read_document
    configure_cli_stdio()
    parser=argparse.ArgumentParser(description='Local submission candidate operations; no OAuth, HTTP registration or remote publication')
    parser.add_argument('--store-dir',required=True)
    parser.add_argument('--trusted-index',required=True,help='Operator-selected file, never an uploader-selected index')
    parser.add_argument('--index-id',default='local')
    parser.add_argument('--roles-file',required=True,help='Operator-owned reviewer/admin subject configuration')
    parser.add_argument('--protocol-registry',help='Operator protocol directory, never an uploaded registry')
    parser.add_argument('--policy-root',help='Independent local operator decision archive')
    parser.add_argument('--policy-head-sha256',help='Explicit operator-selected decision digest; never an upload field')
    parser.add_argument('--actor',help='Local operator assertion only; do not expose this flag in HTTP')
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('public-leaderboard')
    create=commands.add_parser('create');create.add_argument('--input',required=True);create.add_argument('--key',required=True)
    revise=commands.add_parser('revise');revise.add_argument('--id',required=True);revise.add_argument('--input',required=True)
    revise.add_argument('--kind',choices=('rerun','measurement_recheck'),required=True)
    for sub in (revise,):
        sub.add_argument('--expected-version',type=int,required=True);sub.add_argument('--reason',required=True);sub.add_argument('--key',required=True)
    action=commands.add_parser('action');action.add_argument('--id',required=True)
    action.add_argument('--name',choices=('request_review','start_review','approve','publish','reject','withdraw','cancel_review','unpublish','reopen'),required=True)
    action.add_argument('--expected-version',type=int,required=True);action.add_argument('--reason',required=True);action.add_argument('--key',required=True)
    action.add_argument('--consent-file');action.add_argument('--rights-evidence')
    accept=commands.add_parser('accept-generation');accept.add_argument('--receipt-file',required=True)
    revoke=commands.add_parser('revoke-generation');revoke.add_argument('--receipt-sha256',required=True)
    for sub in (accept,revoke):
        sub.add_argument('--id',required=True);sub.add_argument('--revision',type=int,required=True)
        sub.add_argument('--expected-version',type=int,required=True);sub.add_argument('--reason',required=True);sub.add_argument('--key',required=True)
    for name in ('get','history','result','public-summary','public-result'):
        sub=commands.add_parser(name);sub.add_argument('--id',required=True)
        if name in ('result','public-result'):sub.add_argument('--output',required=True)
        if name=='result':sub.add_argument('--revision',type=int)
    commands.add_parser('public-list')
    backup=commands.add_parser('backup');backup.add_argument('--output',required=True)
    args=parser.parse_args()
    try:
        roles=read_document(args.roles_file,max_bytes=1024*1024)
        if set(roles)!= {'reviewers','admins'} or any(not isinstance(roles[name],list) or len(roles[name])>1000 or any(not isinstance(x,str) for x in roles[name]) for name in roles):
            raise ValueError('Invalid operator roles configuration')
        store=LocalSubmissionStore(args.store_dir)
        from .protocols import ProtocolRegistry
        registry=ProtocolRegistry(args.protocol_registry) if args.protocol_registry else None
        from .policy_decisions import configured_policy
        policy=configured_policy(args.policy_root,args.policy_head_sha256)
        service=SubmissionService(store,{args.index_id:read_document(args.trusted_index)},registry=registry,rank_policy=policy,**roles)
        actor=Principal(args.actor,'operator_local') if args.actor else None
        if args.command=='create':response=service.create(actor,read_document(args.input),args.index_id,key=args.key)
        elif args.command=='revise':response=service.revise(actor,args.id,read_document(args.input),expected_version=args.expected_version,kind=args.kind,reason=args.reason,key=args.key)
        elif args.command=='action':response=service.action(actor,args.id,args.name,expected_version=args.expected_version,reason=args.reason,key=args.key,consent=read_document(args.consent_file,max_bytes=16384) if args.consent_file else None,rights_evidence=args.rights_evidence)
        elif args.command=='accept-generation':response=service.accept_generation_receipt(actor,args.id,read_document(args.receipt_file,max_bytes=32768),revision=args.revision,expected_version=args.expected_version,reason=args.reason,key=args.key)
        elif args.command=='revoke-generation':response=service.revoke_generation_receipt(actor,args.id,revision=args.revision,receipt_sha256=args.receipt_sha256,expected_version=args.expected_version,reason=args.reason,key=args.key)
        elif args.command=='get':response=service.get(actor,args.id)
        elif args.command=='history':response=service.history(actor,args.id)
        elif args.command=='public-list':response=service.public_list()
        elif args.command=='public-leaderboard':response=service.public_leaderboard()
        elif args.command=='public-summary':response=service.public_summary(args.id)
        elif args.command=='backup':
            _actor(actor)
            if actor.subject not in service.admins:raise StorageError('admin_required','Administrator required for a private backup',403)
            response=store.backup(args.output)
        else:
            document=service.result(actor,args.id,revision=args.revision) if args.command=='result' else service.public_result(args.id)
            path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(fd,'wb') as stream:
                stream.write(encode(document)+b'\n');stream.flush();os.fsync(stream.fileno())
            response={'artifact_sha256':document['content_sha256'],'output':str(path)}
        print(json.dumps({'execution_scope':'operator_local_candidate','result':response},ensure_ascii=False))
    except (StorageError,ValueError,OSError) as exc:
        print(json.dumps({'error':getattr(exc,'code','invalid_request'),'message':str(exc)},ensure_ascii=False),file=sys.stderr)
        raise SystemExit(2)


if __name__=='__main__':main()
