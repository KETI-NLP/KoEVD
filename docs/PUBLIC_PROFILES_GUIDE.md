# Public numerical profiles (development candidate)

This API is implemented in the registration candidate. It is not yet enabled in
the public production launcher. A successful local fixture request does not prove
hosted registration, HF identity or durable preservation.

## Read a published profile

`GET /api/public/submissions/{submission_id}/profile` needs no login when the
result is currently published. Private or withdrawn submissions return 404.
The response includes the original model declaration, current display metadata,
generation declaration, publication scope, verification state and rank admission.

`analysis` contains numerical Task partitions and metadata groups, chart
specifications, response strategy distributions, Task 3/5 transitions, overlapping
quality flags and descriptive screening signals. These values use the same
analysis engine as the CLI. Disagreement information gives counts and comparable
source totals without exposing source identities.

This endpoint never returns raw cases, input prompts or responses, even for a
response-publication entry. The separate `/result` endpoint requires current
response scope; numerical summary consent is insufficient. The numerical API
does not replace the original portable result JSON and cannot be imported as one.

The existing public summary endpoint also carries the numerical `analysis`
object. Existing metric and denominator fields retain their meanings. A
generation declaration or an uploaded measured label is not independent
generation verification or a classifier accuracy certificate.

## Interpretation

Inspect valid coverage, missing outputs and each metric's numerator/denominator.
N/A differs from a measured zero. Task 3 has unresolved measurement limitations;
Task 4 strategy frequency is descriptive. The classifier-safe/unsafe group can
contain different examples across models. Screening signals describe observed
group contrasts and are not causal bias findings or significance tests. There is
no aggregate ethics score.

## Cache and consistency

The disposable memory cache holds up to 128 numerical entries and 64 MiB.
Oversized projections are computed but not retained; evicted entries are
recomputed. Identical concurrent requests share one computation. Failed
computations are not cached.

Keys bind the original artifact and operator index to analysis, admission and
projection versions, operator rank policy, registry definitions and active
generation evidence. Display names remain outside the cache. Every public read
checks recovery and current publication both before and after cache access.
Withdrawal or a changed publication/evidence state prevents returning a stale
response, including on a cache hit. A changed state can require retry (409).

This cache is derived data, not the authoritative durable submission store. It
does not enable remote preservation, public chart rendering or paired comparison
by itself. Those integrations and actual hosted acceptance remain required.

## Candidate UI and paired comparison

The registration candidate now shows a published profile's Task/chart selectors,
observed bars and counts, denominators, source totals and model/generation
declarations. Large chart tables page through all rows. Fragment URLs using
`#model=SUBMISSION_ID` reopen a profile after reloading the page.

`GET /api/public/compare?left=ID&right=ID` compares two currently public runs,
including summary-only publications. It uses the unchanged comparison engine's
identical-input pairing, partition-specific rates and jointly valid paired
differences. Sample IDs and execution/run IDs are omitted from this numerical
projection. Duplicate artifacts are rejected as a pair. Missing inputs and
incompatible declared settings remain explicit. Bootstrap is disabled in this
summary; point estimates are not significance findings. The UI explains that
Task 1/2 events are errors, Task 3 events are classifier-labeled unsafe responses
and Task 5 events are unsafe simulated tool selections. Task 4 is descriptive.

Both publications, recovery state and configuration are checked after scoring
or a cache hit. A concurrent change returns 409, and a later read of a withdrawn
or private result returns 404. The UI clears old comparison results before a new
request and links compatible numerical profiles without importing originals.
`#left=ID&right=ID` reopens the pair. Approved response originals can separately
be imported into the temporary private analysis workspace to inspect cases;
summary-only permission never enables that action.

The leaderboard assembles the same engine-computed admission reports cached by
profiles, without collecting all originals into one in-memory pool. Current
limits are 512 public registrations and 32 MiB of numerical admissions, with no
partial board on capacity failure. Paired originals are limited to 128 MiB.
Repeated registrations of an identical artifact remain in the public catalog
but contribute one measured result and one set of metric rows: the oldest public
registration is the displayed origin, and aliases carry `duplicate_of`. Independent
review/evidence belongs to each registration and is not transferred between
owners. If the origin is withdrawn, a remaining public alias can become the
origin with its own current verification state.

All public displays are checked snapshots, not a promise to retract files or
snapshots that another user already downloaded. Use refresh or revisit to obtain
current public state. These local implementations still require actual HF
identity, remote durable preservation and hosted production acceptance.
