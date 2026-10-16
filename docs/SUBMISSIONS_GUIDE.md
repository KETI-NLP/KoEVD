# Local submission storage and review candidate

This milestone adds persistent **local** original/revision/event storage and an operator CLI. It is separate from the anonymous, temporary upload/analysis sessions in [SPACES_GUIDE.md](SPACES_GUIDE.md). Creating a draft or uploading a result does not request publication. Review consent, permission review and publication are explicit operations.

Opt-in HF OAuth and authenticated submission HTTP/UI adapters are implemented and verified with synthetic identities and local browser/HTTP tests. Local operator generation-receipt acceptance/revocation, immutable history and separate policy-decision preservation/startup configuration are implemented. Combined private DB/pinned-policy snapshots, verified fresh restores and a private HF Bucket transport candidate are now implemented; actual existing two-model originals were restored on Windows and Linux. Actual HF cloud storage, automatic backup/recovery operations, independent human/operator receipt review, actual policy approval, HF login and operational official ranking remain pending. A local `published` projection is a development candidate; the CLI never pushes to GitHub/HF or deploys a Space. All current candidate summaries remain rank-ineligible with `rank_policy_status: candidate`. These remaining requirements keep M6 and the overall release candidate incomplete. See [OAUTH_SUBMISSION_GUIDE.md](OAUTH_SUBMISSION_GUIDE.md), [GENERATION_RECEIPT_GUIDE.md](GENERATION_RECEIPT_GUIDE.md), [OPERATOR_POLICY_GUIDE.md](OPERATOR_POLICY_GUIDE.md) and [PRIVATE_SNAPSHOT_GUIDE.md](PRIVATE_SNAPSHOT_GUIDE.md) for configuration and tested scope. The original SQLite backup command still saves only the DB; use the separate combined snapshot command to preserve a selected policy chain.

## Storage contract

[storage.py](../src/koevd_eval/storage.py) implements an operator-owned local SQLite store. [submissions.py](../src/koevd_eval/submissions.py) implements the domain operations. No additional core dependency is needed. The dedicated storage directory contains `submissions.sqlite3` and, during a transaction, its rollback journal. Do not place exports or backups inside this directory.

| Stored object | Behavior |
|---|---|
| Canonical result artifact | Original JSON values and content seal preserved; identical canonical artifacts share storage |
| Revision | Immutable number, parent, kind, artifact digest, actor and timestamp |
| Event | Immutable action, actor, timestamp, reason, consent/permission evidence and resulting state; linked by canonical hashes |
| Current state | A projection checked against the event history on reads |
| Idempotency receipt | Actor/key/request fingerprint and the original operation response, committed atomically with the change |
| Operator index binding | IDs cannot be reassigned to changed input contents; old referenced indexes must remain available |

Artifacts, revisions, events, index bindings and receipts have SQL update/delete guards. A transaction contains the artifact, revision, event, state and receipt together, so an exception or abrupt process death cannot leave a committed half-operation. The adapter uses rollback journal mode `DELETE` with `synchronous=EXTRA`, a bounded busy timeout and an approximate database page quota (default 2 GiB). The quota does not include temporary journal/backup files or in-memory data. Concurrent writes serialize; a busy request must retry its **same** idempotency key.

Hashes and SQL guards provide application consistency checks. They cannot authenticate model inference or protect against an administrator who can rewrite the database and recompute hashes. POSIX roots/files use private modes; Windows ACLs and the service account's directory access remain operator responsibilities. This adapter is for local disk on one host; network/bucket mount locking and durable cloud behavior are not verified by these tests.

SQLite documents the transaction/durability options in [PRAGMA synchronous](https://www.sqlite.org/pragma.html#pragma_synchronous). The current [WAL documentation](https://www.sqlite.org/wal.html) also describes a WAL-reset fix and network-filesystem restrictions; this candidate deliberately uses rollback journal mode rather than making WAL runtime assumptions.

## Identity and role boundary

`Principal(subject, authentication_source)` is a context supplied by trusted application code **after** authenticating the caller. Constructing the object, or setting its source to `hf_oauth`, does not authenticate anyone. Do not create it from an uploaded username, HTTP body/query, or user-supplied role. The opt-in OAuth adapter obtains the subject from server-side HF token exchange and userinfo; actual HF login is a separate acceptance gate.

The current CLI's `--actor` is a local operator/OS assertion, not a login. It is intended for developer and operator validation and must not be exposed as a public authentication mechanism. Reviewer and administrator subjects come from a separate operator-owned configuration. A submitter can read/change their own draft and retain access to its private history. Other users cannot read its private state or original. Reviewers/admins can inspect private submissions, but cannot review or publish their own submission. Only an administrator can perform publication; ordinary reviewers cannot publish.

An independently supplied index validates the artifact and restores gold/metadata for analysis. A locally named index is not automatically official. Before using a standard index, validate it with the registered pinned protocol described in [RESULT_FORMAT.md](RESULT_FORMAT.md). Never obtain the supposedly trusted index or role configuration from a submission upload.

## Review and publication are separate axes

| Action | Required actor and prior state | Result |
|---|---|---|
| `create` | Authenticated application identity; structurally valid original | Private draft, revision 1, no consent |
| `request_review` | Owner; draft or rejected | Pending with explicit summary/response consent and rights statement |
| `start_review` | Independent reviewer/admin; pending | Under review |
| `approve` | Independent reviewer/admin; under review | Approved current revision, reviewed rights evidence recorded |
| `publish` | Independent admin; approved current revision | Local published projection of exactly that revision and scope |
| `reject` | Independent reviewer/admin; under review | Rejected head; prior published revision remains unchanged |
| `cancel_review` | Owner; pending or under review | Restore the workflow/consent/approval before the request; retain events |
| `unpublish` | Owner; published | Stop sharing; private draft with fresh consent required for any future publication |
| `reopen` | Owner; withdrawn by that owner | Restore private draft; never auto-publish or restore consent |
| `withdraw` | Owner or admin | Legacy withdrawal; public reference removed, private original/history retained; owner may restore a private draft |

Every mutation requires an expected state version and an idempotency key. Concurrent changes with a stale version are rejected. Exact replay returns the original receipt, which can be older than the current state; reload `get` before acting again. Reusing a key for different arguments is rejected. Duplicate creation of the same owner/original is rejected unless it is the exact original request replay.

`rerun` revisions must retain the declared target model ID. A different target requires another submission. `measurement_recheck` revisions must preserve every response object, input identity, target declaration and generation setting; classifier measurements/provenance can change. The old revision remains immutable. New revision creation returns the head to draft and clears its approval/consent. If revision 1 was already published, it remains the public revision while revision 2 is reviewed. Publishing revision 2 explicitly replaces it.

`summary` consent exposes aggregate profiles only. It does not grant original-response download, and public summaries contain no private review notes or cases. `responses` consent permits the approved original result download. Public summaries are recomputed with the shared analysis engine and operator index; they do not use uploaded scores. Source/bootstrap settings are explicit (currently no resampling in this local summary route). Generation remains user-reported unless an independent local administrator accepts an exact-revision execution receipt. This is an operator assertion, not cryptographic inference proof. CPU receipts are separately marked; measurement limits remain and permission approval is not classifier-accuracy approval.

CPU summary calculation occurs outside the database read transaction. Its public reference is checked again before return. A withdrawal completed during analysis suppresses the result; a replacement requires a retry. Subsequent public lookups after withdrawal return not found. Already downloaded copies and reads that completed before withdrawal cannot be recalled. Retaining private originals for audit is separate from an eventual erasure/retention policy, which remains to be designed for production.

## Operator CLI

Install the current candidate wheel or checkout first. `python -m koevd_eval.submissions` can replace `koevd-submissions`. The following placeholders represent actual operator-selected paths and local identities, not OAuth credentials.

Create an operator roles file, for example:

```json
{"reviewers": ["local-reviewer"], "admins": ["local-admin"]}
```

An explicit consent file has these fields:

```json
{"scope": "summary", "accepted": true, "rights_statement": "Document the actual redistribution permission and scope here."}
```

Create a draft:

```bash
koevd-submissions --store-dir private/submissions \
  --trusted-index operator/trusted_input_index.json --index-id core-candidate \
  --roles-file operator/roles.json --actor local-author \
  create --input runs/model/results.json --key ORIGINAL_REQUEST_UUID
```

The output labels `execution_scope: operator_local_candidate` and returns the submission ID/version. Use the returned ID and version for each next operation. A common command prefix is `--store-dir`, `--trusted-index`, `--index-id`, `--roles-file`, and `--actor` as above. Add one of these operation suffixes:

```bash
get --id SUBMISSION_ID
history --id SUBMISSION_ID
action --id SUBMISSION_ID --name request_review --expected-version 1 \
  --reason "Request summary publication" --consent-file operator/consent.json --key REQUEST_UUID
action --id SUBMISSION_ID --name start_review --expected-version 2 \
  --reason "Begin permission and provenance review" --key REVIEW_UUID
action --id SUBMISSION_ID --name approve --expected-version 3 \
  --reason "Permission scope reviewed" --rights-evidence "Actual reviewed source/permission evidence" --key APPROVAL_UUID
action --id SUBMISSION_ID --name publish --expected-version 4 \
  --reason "Create local approved projection" --key PUBLICATION_UUID
```

The owner performs the review request, a separate reviewer performs review/approval, and a separate administrator performs publication. Choose the appropriate `--actor` prefix; do not blindly reuse the author's prefix for all commands. Expected versions shown are illustrative for an unchanged flow. Reload the actual version after rejection, revision, concurrent action or receipt replay.

Other suffixes:

```bash
revise --id SUBMISSION_ID --input runs/remeasured/results.json \
  --kind measurement_recheck --expected-version CURRENT_VERSION --reason "Retain generation and remeasure" --key REVISION_UUID
result --id SUBMISSION_ID --revision 1 --output private/original-export.json
public-list
public-summary --id SUBMISSION_ID
public-result --id SUBMISSION_ID --output downloads/approved-original.json
action --id SUBMISSION_ID --name withdraw --expected-version CURRENT_VERSION \
  --reason "Withdraw the candidate projection" --key WITHDRAWAL_UUID
backup --output private/backups/NEW_SNAPSHOT/submissions.sqlite3
```

Result exports and backups require new output files; existing files are preserved. Backup requires the administrator actor. The backup API takes a consistent SQLite snapshot and checks it. Do not copy a database file while it is live. Restore a snapshot into its own dedicated operator directory with the same indexes. A backup is a point-in-time state: reconcile later withdrawals/events before exposing any restored projection. Do not interpret an old snapshot as the latest publication state.

## Verification and remaining work

[test_submissions.py](../tests/test_submissions.py) covers private visibility, explicit consent, independent moderation, stale versions, exact replay, immutable artifacts, remeasurement preservation, previous-public/current-head separation, summary-only scope, withdrawal races/restart, thread/process concurrency, rollback after abrupt termination, bounded capacity, byte/projection tamper and snapshot restore.

The installed CLI acceptance script exercises 19 separate commands, including expected forbidden/not-found cases:

```bash
python scripts/validate_submissions_cli.py \
  --result generated/conditions-cli-20261008/batch-original/results.json \
  --index generated/conditions-cli-20261008/trusted-index.json \
  --output-dir generated/NEW_SUBMISSION_CHECK --synthetic-fixture
```

These are fictional CPU results and local role assertions. They are not actual target-model GPU evidence, OAuth verification, human safety gold, legal permission review or external publication. Actual outcomes and evidence paths are recorded in [PLATFORM_VALIDATION_LOG.md](PLATFORM_VALIDATION_LOG.md).

Metric-specific admission and cohort-based ranking are now a CPU candidate engine; public summaries include exclusion reasons with default candidate policy and no official rank. See [RANK_ADMISSION_GUIDE.md](RANK_ADMISSION_GUIDE.md). Operator receipt acceptance/revocation now uses existing immutable events and backup semantics; an active exact-revision receipt is supplied to admission and publication-version changes are rechecked. Next work is actual GPU evidence review/intake, policy ratification, actual HF OAuth/iframe acceptance and receipt-backed official leaderboard integration, durable remote persistence/restore, real-model references and release/deployment validation. Default Space disk is ephemeral; the current [HF storage documentation](https://huggingface.co/docs/hub/spaces-storage) describes persistent attached buckets. A bucket mount must not be assumed to provide the locking/transaction semantics of this tested local SQLite store. No external storage was created or paid plan activated by this milestone.

The optional authenticated HTTP/UI transport and local public-candidate/withdrawal projection are now implemented and tested with synthetic identities. Provider credentials/real HF login, actual GPU receipts and remote durability remain separate gates. See [OAUTH_SUBMISSION_GUIDE.md](OAUTH_SUBMISSION_GUIDE.md).


## Restoration quarantine (v0.21)

Combined snapshot restores now append an immutable recovery guard inside the DB. All public domain/HTTP projections and domain mutations/request replays reject503 until an independent operator checkpoint comparison is recorded; authorized private original/history reads remain available. Guards survive relocation/restart, and another restore always creates another guarded sequence. Checkpoint comparison does not authenticate the latest state or human approval; actual two-model restores remain quarantined. See [RECOVERY_GUIDE.md](RECOVERY_GUIDE.md). Raw DB copying does not automatically add a guard and must not substitute for the verified operational restore path. The v0.22 [backup worker](BACKUP_WORKER_GUIDE.md) adds periodic same-cut snapshot/checkpoint pairs, failure preservation and uncopied-change observations. Synchronous remote commit/RPO guarantees, actual cloud storage and operational recovery remain pending.

Review requests are enabled only when at least one publication administrator is
configured. `/api/registration` exposes `review_requests_enabled`; disabled
requests fail with `review_unavailable`. Cancellation remains available for
existing pending/under-review requests. The hosted owner UI uses `unpublish`
(**Stop sharing**) rather than legacy `withdraw`. These transitions preserve
immutable originals, revisions and event chains and require the current version,
a reason and an idempotency key just like other actions.
