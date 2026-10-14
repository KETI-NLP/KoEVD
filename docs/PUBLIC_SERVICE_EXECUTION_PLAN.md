# Public registration service execution plan

Updated 2026-10-14. Goal: complete the public registered-result service, including
G1–G12, rather than extend the anonymous-analysis beta alone.

The original development checkout has 214 dirty entries and is preserved. Work
uses branch `feature/public-registration-service`, based on public main
`701140249ce69a3a4089e3a184d000bdde2cebb9`, in the isolated publishing checkout.

## Current state

The production Space is public, RUNNING, CPU Basic, one replica at
`a85e57c45cbe3943796543134e68805c389ae74d`. Registration remains disabled. Its
two exact references and anonymous-analysis acceptance remain intact.

The registered candidate's implementation commit is
`01e5d7edd3f7c718f1e046ac7ff2e6ca323dd16a`. Its source-only private test preparation
is `71c010860056b6f80d13f8e1da7a4b92a3bbca4a`, PAUSED with activation/initialization
0. Four required user-entered Secret names were absent on the latest read-only
probe; scope approval and manual credential setup remain pending. Local backend
regression reached 459 tests; final export formatting has separate seven-test
and browser follow-up evidence. Search/pair choices passed with 53 synthetic
publications, and retained actual numerical snapshots passed 15 exports.
No actual HF login, state cut,
restart acceptance or public registration deployment is claimed.

## Decisions and sequence

1. A successful registration mutation must have a confirmed storage checkpoint
   before acknowledgement. A sink failure is a failed operation response; an
   unconfirmed cut is not exposed by subsequent reads. Retry uses the original
   idempotency key. The first file sink establishes this contract locally; it
   does not prove HF durability or authorize cloud transmission.
2. Preserve the current SQL schema, original artifacts, audit chain, request
   replay, independent response-publication review and rank exclusions. Add
   display metadata separately from the immutable result.
3. Add explicit user-consented summary publication without representing it as
   independent operator verification. Response publication retains its review
   path. Both publication paths remain distinct from official rank admission.
4. Cache numerical profiles by artifact/index/analysis version and select only
   the current public revision. Preserve withdrawal/revocation rechecks and
   raw-text scope in profile and comparison projections.
5. Wire OAuth, acknowledged private storage, two operator reference entries,
   public profiles/metrics/comparison and registration UI into the deployment
   candidate. Test local behavior, then approved HF staging and production.

## Work underway

`durability.py` now provides synchronous checkpoint confirmation, a separate
local ledger, exact-cut restore, interrupted-copy retry, retained quota and
conflict/error guards. Fourteen fixture tests passed. SQLite probe connections
are explicitly closed on Windows. Cross-filesystem restore stages objects at
the destination. Failed checkpoint writes never return successful mutation
acknowledgements; later reads/replay must confirm the pending cut first.

Registration now supports owner-controlled display name/description without
rewriting the model declaration or original artifact, including bounded HTTP
metadata updates. Legacy default-create request fingerprints are preserved.

An explicit `allow_self_reported_summaries` deployment option permits owners to
publish consented numerical summaries without fabricating permission review or
generation verification. Response scope still requires the existing independent
review/admin path. A reviewed summary-to-response scope upgrade is supported;
withdrawal continues to hide all current public projections. Eight new local
service/HTTP tests passed, along with twenty existing submission tests.

CLI options `--checkpoint-root` and `--self-reported-summaries` wire these
features into the opt-in registration candidate. Both remain off in the current
production launcher. HF transport, cached public profiles, operator reference
intake, actual OAuth, hosted restart/restore and final deployment remain required.

A first full run passed 397 CPU tests before the final ledger atomic-copy/quota
changes; it is not the final-source acceptance. Final-source tests are recorded
separately in `generated/public-service-20261014-v1/`. No earlier failed attempt
is relabeled as a pass.

No deployment, paid resource, token change or new original-result transmission
has occurred for this goal. Historical bounded test approvals are not reused.

## Numerical profile implementation

Public summaries and `/api/public/submissions/{id}/profile` now expose the shared
engine's numerical partitions, metadata groups, charts, strategy distributions,
quality counts and signals. A bounded disposable memory cache binds artifact,
index, analysis/admission/projection versions, rank policy, registry definitions
and active evidence. Current publication, version, recovery and policy checks
still run before and after cache access. Display metadata is read from current
state rather than cached. Cached projections contain no raw cases, prompts,
responses, run/request identifiers or disagreement source identities.

Nine new CPU tests cover metric preservation, cache concurrency/failure/size,
metadata refresh, policy invalidation and withdrawal including a warm-cache
race. Public profile HTTP checks were added to the existing registration fixture.
Cache entries can be regenerated after restart; they are not the durable store.
Board aggregation still needs conversion from repeated raw analysis, and public
profile rendering, public paired comparisons and hosted acceptance remain open.

## Public comparison and rendering checkpoint

Board aggregation now consumes the same cached engine admissions as numerical
profiles. It retains only public membership states between reads and does not
pool every raw original. Capacity is bounded by 512 registrations and 32 MiB
of numerical admissions. Duplicate artifacts contribute one measurement row;
catalog aliases and registration counts remain visible separately.

The public pair API computes identical-input matched partitions and jointly
valid differences, projects away run/sample identities and rechecks both current
publications after cold scoring or a warm cache read. Summary scope enables
numbers and metadata trends, while original case access remains independent.

The UI now has public profile chart selectors, paginated numerical chart rows,
recorded model/generation declarations, anonymous two-run comparison and stable
fragment links. Approved originals can be explored in the existing private
analysis workspace. User-controlled names remain literal text. Summary consent
and reviewed response-scope upgrades have distinct UI paths.

Eight new CPU comparison tests and an additional anonymous HTTP scenario passed.
The frozen candidate passed 419 CPU tests in 169.160 seconds. Final localhost
Chrome QA at 1440 and 390 pixels passed profile/Task 4 exploration, literal
untrusted Korean names, anonymous summary comparisons, revisiting pair links and
no page overflow, with zero page errors or external requests. Evidence is in
generated/public-service-20261014-v5/. This is fixture/browser evidence, not
hosted HF login, remote preservation or public deployment acceptance.

Both existing actual full references also passed the local registered path in
87.406 seconds: 17,670 records each, original hashes unchanged, all numerical
point values and denominators matched the independent native report, and 94
stored board metric rows matched registered admission reports. Public summaries
use zero bootstrap resamples versus the oracle's 100; intervals were excluded
explicitly from the point comparison. This proves local actual-data integration,
not hosted HF identity/durability, new generation or classifier accuracy.

## Conditional remote state candidate

`remote_durability.py` adds dedicated private HF/S3 object access and a conditional
HEAD ledger. Objects are read back before HEAD, exact replay reconciles a lost
HEAD response, live reads are fenced against newer authority, and a fresh runtime
restores the acknowledged SQL cut while preserving divergent existing directories.
The `koevd-space` CLI can select this sink with explicit state/initialization flags
and dedicated server Secrets. Old filesystem and periodic-backup paths are intact.

Sixteen local object-store tests and three CLI assembly checks passed, covering
checkpoint failure/replay, stale reads/writes after withdrawal, byte corruption,
private target checks, quota, orphan initialization and no cached administrator
credential fallback. Local boto3 1.43.113 exposes both conditional PUT fields;
that SDK model check sent no requests. Full frozen-source CPU regression is
recorded in generated/public-service-20261014-v6/.

The production launcher still runs the anonymous beta. Registered launcher/
Docker assembly, actual scoped S3 tests, native hosted OAuth and restart/restore
must still be completed. No Bucket/Secret creation or actual HF/S3 state transfer
occurred. Follow ACKNOWLEDGED_STORAGE_GUIDE.md for the candidate contract and
future concrete approval/credential scope.

## Registered launcher and Docker assembly

The registered launcher now combines native OAuth configuration, pinned private
references, conditional acknowledged state, operator reference intake, warmed
public numerical profiles and the existing private analysis service. The first
two references are one acknowledged SQL cut; later starts preserve IDs/history
and never reactivate withdrawn references. Public responses distinguish operator
references and user runs without fabricating HF identities or GPU verification.

The new allowlisted materializer emits a source-only 75-file registered context
with OAuth metadata, empty operator roles and observed CPU/S3 dependencies.
The 6,849,703-byte compressed code/public-input/synthetic-QA package went to the
previously specified b200-1 private folder. It contained no model response
originals, DB or credentials. Docker build was independently confirmed by image
digest and 27 passing network-disabled synthetic tests (2 CPUs/6 GiB). Its
container/image were removed; source/log evidence remains private.

The materialized app passed local HTTP checks with both existing actual full
references and fictional state/identity in 116.422 seconds. Full local CPU
regression passed 446 tests in 179.512 seconds. No HF Space or state Bucket was
created or changed, and actual HF OAuth/S3 durability remains unverified.
See REGISTERED_SPACE_GUIDE.md and generated/public-service-20261014-v9/.

## HF preparation and pending finite trial

New private resources KETI-NLP/KoEVD-Platform-State-Dev and
KETI-NLP/KoEVD-Platform-Registration-Dev were created under the active service
goal. Only source and already public input indexes were committed to the new
Space at 79ed3c012e86d29237c808303dcb9302ab336f98. It is paused, the state Bucket
is empty, and activation/initialization remain 0. New hard guards support 12 cuts,
128 MiB per DB and 1.5 GiB retained for the requested limited trial. No original
responses, state snapshots or secret values were transferred.

The user has been asked to approve the exact original-reference/finite-trial
scope and to set resource-scoped state/S3 and read-only reference Secrets. Neither
pending intent nor elapsed time counts as approval/configuration. Continue local
independent work while these inputs are pending; production stays unchanged.

Independent G2 work adds a private declaration endpoint and confirmation UI
before saving/revising selected upload metadata. Four CPU/HTTP checks and local
mobile browser QA passed. The initial browser harness omitted navigation from
the sign-in completion page back to the workspace; its failed receipt is kept.

The v11 448-test run had one Windows temporary-file replacement PermissionError
in an unchanged report fixture. Targeted report tests passed on rerun; this does
not establish a root cause or reclassify the failure as success. Frozen full
regression uses a task-owned temporary directory and separate v12 evidence.

That final frozen regression completed with 452 tests passing in 216.222 seconds,
exit code 0. Source hashes and the full log are retained in the v12 receipt.
The earlier failed v11 run is still a separate failure with unproven root cause.
Remote activation remains pending; no local pass changes the approval boundary.

## Observed-value exploration and complete pair choices

The public metric table now searches original model IDs, display names and
revisions, sorts observed values without assigning or changing official ranks,
keeps undefined rates last and links rows to their numerical profiles. Origin
and generation/measurement verification are visible alongside denominators.
Pair selectors use the complete bounded board publication snapshot rather than
the first 50-entry catalog page. Failed refresh clears profiles, previous pair
results/options and metric rows before showing the error.

Local desktop/mobile Chrome checks passed against 53 fictional engine-computed
runs, including a contrasting classification and an invalid-output denominator.
They prove pagination boundaries, both sort directions, N/A handling, literal
untrusted Korean names, no fabricated ranks, profile links and clearing on a
failed authoritative refresh. There were no page errors or external requests.
The two fixture-setup mistakes and sandbox/no-listener browser attempts remain
separate failed receipts; the corrected owned localhost server was explicitly
confirmed running before the successful checks. This is not hosted HF evidence.
See generated/public-service-20261014-v13/board-browser-receipt.json.

Read-only HF readiness found all four required data Secret names absent; the
state Bucket remains private/empty and production remains the existing beta.
The private paused test Space now has the five tested code updates plus checksum
manifest at 4bdf0cda2bb36a95033451cbdb827f34a5727d16 (98,430 bytes, no originals or
new input files). Activation/initialization remain 0. Scope approval and dedicated
Secret setup are still pending; follow HF_REGISTRATION_TRIAL_SETUP_KO.md.

## Public numerical report downloads

Profiles and pairs now have five numerical download formats, with public-state
recheck after rendering, existing bounded CPU admission, no-store attachments,
no originals and a 32 MiB cap. The compact serializer passed 459 frozen CPU tests;
final revision-label/HTML-width follow-ups passed seven focused tests and actual
desktop/mobile download/byte checks. Both actual historical numerical profiles
and their pair passed 15 exports against the prior independent point-value
oracle, including CSV/JSONL denominators. The initial pretty JSON exceeded the
cap for the pair; compact JSON fixed it without truncation or a larger quota.
No live HF identity, data write/restore or production registration is claimed.
Usage/units are in PUBLIC_NUMERICAL_REPORT_GUIDE.md; detailed scope is in v14–v16.

The final export implementation's three code files plus checksum manifest
(68,382 bytes) are prepared at private revision
71c010860056b6f80d13f8e1da7a4b92a3bbca4a. Source parent/current revision, PAUSED,
private and activation/initialization 0 were checked. No originals, snapshots,
new inputs or credentials were transmitted. The latest metadata-only readiness
probe still found all four required data Secret names absent; manual setup and
finite-trial approval remain pending.
