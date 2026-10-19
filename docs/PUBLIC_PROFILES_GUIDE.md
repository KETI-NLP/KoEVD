# Public numerical profiles

The public platform exposes numerical profiles for currently shared registrations.
Authentication, saving a private registration, numerical sharing and response
publication are separate actions. A local fixture is not proof of hosted identity
or durable preservation.

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

## Interactive model details (v0.3.0-rc.10)

Open a model from the leaderboard, then choose a Task in **Explore task behavior**.
These are live SVG charts, not screenshots. Hover or keyboard-focus a mark for
its exact values; click or press Enter/Space to pin its evidence. The numerical
table remains available beneath every chart. **SVG** exports the current graphic;
**Chart JSON** exports its observations, selected controls, model/public revision,
protocol, artifact and recorded generation/classifier conditions. These exports
are analysis snapshots, not portable result files for registration.

| Task | Default graphics and interpretation |
| --- | --- |
| 1 | Gold-to-prediction confusion matrix, including unparsed outputs; missed-risk and false-alarm rates with separate gold-label denominators. |
| 2 | Per-instruction accuracy bars and selected-variant coverage. Different variants repeat sources. |
| 3 | Core-source safety/coverage and question-type bars. Change the input scope and metadata axis to locate descriptive weaknesses; severity × explicitness is an exact joint heatmap. Core and tool-linked sets overlap. |
| 4 | All released strategy inclusion bars, a strategy × condition heatmap, optional co-occurrence matrix and a separate unsafe marker. Multi-label frequencies need not sum to 100%; none is a quality ranking. |
| 5 | Unsafe/valid rates by framing, seven-way strict outcome composition over all expected rows, condition × framing heatmap and response-label-to-tool-outcome transitions. Transition cells are row-normalized including invalid choices; original counts remain in the numerical table. |

**Input scope / framing** and **Analyze by** choose existing exact aggregate
partitions and groups. **Show condition** selects an exact group and updates its
summary, rates and strategy/outcome counts. Framing comparisons use that same
group in each variant where supplied; missing model/group combinations remain
unavailable. Conditional Task 3→5 transitions are not supplied, so that matrix is
hidden while a condition is selected. **Find chart
labels** hides marks without changing any denominator. Other arbitrary metadata
intersections are not offered: marginal percentages cannot establish them.
Small groups remain visible, with a warning when fewer than 20 valid sources are
reported. N/A is not zero. No confidence interval is estimated in the browser.
Task 3/4 include the recorded classifier settings beside the chart summary.

Public comparison uses one set of Task/scope/axis controls for both models and
fixed 0–100% rate scales. Each chart retains its own valid denominator; differences
between these marginal charts are not matched-case effects. Use the separately
reported matched-input comparison and its compatibility warnings for that purpose.

The historical twelve-model collection uses **only released per-model aggregates**.
Its Task 1 measures unsafe judgment frequency, Task 3 lacks per-model question
breakdowns, Task 4 includes selected strategy labels and Task 5 uses historical
all-row metrics/partial parsing. Unreleased labels are not filled with zeros;
pooled all-model breakdowns are not attributed to an individual model. Per-variant
counts and intervals are not reconstructed from rounded percentages.

Numerical chart selection never reveals prompts, responses or private history.
Response-case access remains a separate permission-aware workflow. Anonymous chart
interaction makes no registration/publication/server-state writes. Chart
controls are remembered in browser session storage for each public model/revision
or comparison; **Reset view** restores the task defaults.

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
