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
