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

## Interactive model details (v0.3.0-rc.15)

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
hidden while a condition is selected. **Find chart labels** filters bars, highlights matrix cells and retains all
composition segments without changing any denominator. Other arbitrary metadata
intersections are not offered: marginal percentages cannot establish them.
Small groups remain visible, with a warning when fewer than 20 valid sources are
reported. N/A is not zero. No confidence interval is estimated in the browser.
Task 3/4 include the recorded classifier settings beside the chart summary.

Public comparison carries the selected Task, scope, axis, condition and display
settings from model details, including historical model details. Explicitly
carried settings take precedence over an older saved comparison view. Rebuilding
a pair after changing a model retains the current chart selection. Unsupported
model/condition combinations remain unavailable rather than falling back to a
whole-scope score.

Comparison bars place both models on the **same category rows** in one full-width
chart. Fixed order uses semantic domains; value order uses a shared maximum across
models, never independent per-model sorting. Severity follows Benign → Low →
Moderate → High → Extreme, with borderline/missing groups separate. Strategy rows
keep their canonical order when a condition changes. Matrices are paired by chart;
count matrices share their color maximum across models. On narrow screens, wide
matrices can scroll; exact data tables remain available.

Each model retains its own valid denominator. These marginal chart differences
are not matched-case effects. Metadata controls affect the charts only; the
separately reported matched-input tables retain their own named partitions and
are **not recomputed for a selected metadata condition**. Inspect their compatibility
warnings before drawing a paired comparison conclusion.

Task 1 offers counts or percentages within each gold-label row (including unparsed
predictions). Axis labels identify gold versus predicted labels; tooltip/table
denominators name their scope. Task 5 transition rates use the response-label row
total, while full-framing source support is explicitly separate. Variant bars
show valid/expected coverage beside the measured rate. Task 4 co-occurrence is a
count, not correlation or quality, and has a count-specific scale explanation.

Task 5 composition segments and the legend share one fixed outcome order. Label
search retains **all seven components**, including invalid outputs, without
renormalizing the composition. On matrices, search highlights matching cells and
retains the grid; on bars, it filters labels without changing their denominators.

Selected marks are highlighted and open a fixed, scrollable evidence panel with
a visible Clear selection control. Escape also closes the selection. JSON exports
of combined bars include both models' declarations and the shared view settings.

For current numerical profiles, within-model supported contrast candidates summarize higher
and lower observed error/unsafe rates against **disjoint remaining sources within
the same model**. The existing analysis engine requires at least 20 valid sources
and 90% coverage on both sides. Small/low-support groups stay in the charts but
are not promoted as supported candidates. These are descriptive review candidates,
not significance tests, confirmed weaknesses, causal bias or cross-model effects.
Task 4 has no quality direction and historical aggregates do not gain invented
conditional candidates.

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

## Task views, search recovery and strategy meaning

Each Task remembers its scope, axis, condition, label search, order, matrix mode
and co-occurrence selection. Returning to a Task restores its own view; values
are not blindly applied across different Tasks. Per-Task views survive session
reloads and detail-to-comparison handoff. If neither selected model supplies a
saved scope/axis/condition, the visible fallback is explained; a condition available
on only one model remains selected and the other remains unavailable.

**Inspect group** clears label search before applying its group. If a manually
chosen condition conflicts with a remaining search, the empty chart explains that
measured observations are hidden and offers **Clear label search**. Search does
not change denominators. Current strategy names follow the canonical
[released label crosswalk](STRATEGY_LABELS.md); earlier chart names remain searchable.
Task 4 includes short definitions and newly authored illustrative examples,
explicitly distinguished from benchmark text and gold annotations. Strategy
measurement completeness is a supporting badge, not a large performance score.
Per-model valid/expected counts remain beside comparison bars where supplied.

## Task 3: type analysis

Below the basic unsafe-rate chart, **Where does the model generate unsafe responses?**
shows every supplied question / utterance type in the selected input scope. Types
come from trusted input metadata, including new or missing categories; they are
not a fixed list or a taxonomy of the generated answer's harm.

- **Type chart measure** switches between unsafe / valid measurements and observed
  unsafe counts. A count is not a rate: common types can contribute more failures
  while having a lower failure rate. Count comparisons use a shared count scale;
  rate comparisons retain the fixed 0–100% scale.
- **Type row order** sorts by the highest displayed model value or by type name.
  Search question types filters labels only; it never changes denominators.
  All types remain available in Inspect question type, even when search hides a bar.
- Bars, evidence and the exact table report unsafe / valid, valid / expected,
  completion and source support. Fewer than 20 valid sources is flagged, not hidden.
  No valid measurements gives an undefined rate; observed count zero does not
  establish safety. Missing model/type data is not a measured zero.
- Select a bar (click, Enter or Space) or use **Inspect question type**. Choose
  Topic, Input severity or Explicitness to inspect an **exact type × metadata**
  breakdown computed from validated rows. Topics and multi-valued types can overlap;
  their totals need not add to the overall sample size. No other metadata
  intersection is inferred from marginal tables. Topic breakdowns use the chosen
  value/name ordering; severity and explicitness retain fixed semantic order in
  both single-model and comparison views.
- These dedicated controls use the current **input scope**. General Analyze by,
  Show condition, Bar order and Find chart labels apply to the basic/additional
  metadata charts separately. The additional metadata chart is collapsed below
  type analysis. Changing scope refreshes type support.
- **Compare selected type with another model** carries the type, metric, search,
  order and breakdown axis to synchronized model comparison. Each model keeps its
  own numerator/denominator. The selected-type pp difference is descriptive,
  not a jointly valid paired effect or significance test. Missing conditional
  data is explicitly unavailable; model declarations still require inspection.

Only numerical aggregates are exposed. These charts do not publish prompts or
responses. Paper experiments have no released per-model type breakdown here;
use registered results. Older profiles without exact type slices can show the
known type overview, but cannot invent a selected-type breakdown. Analysis format
`koevd-analysis-v3` adds numeric `tasks["3"].type_details`; existing scores,
partitions, groups, signals, charts and paired statistics retain their definitions.
Client Chart JSON exports preserve the current type view and model contexts.

## Between-model observed differences versus within-model contrasts

The separate **Between-model observed rate differences** panel subtracts Model 2's
observed rate from Model 1's rate, in percentage points, for the displayed chart
and named condition. Each model retains its own numerator and denominator. These
are marginal observed differences, not jointly valid paired effects, confidence
intervals, significance tests or causal effects. Groups and valid outputs can
differ. Check generation/measurement declarations and the separate matched-input
statistics before making a paired inference.

Rows with at least 20 reported sources per model precede small/unknown-support
rows; within each set, the largest absolute differences appear first. The first
eight are displayed and **Difference summary JSON** exports all rows, both model
contexts and current controls. Missing rates stay unavailable, measured zero is
retained, and no counts are reconstructed for historical percentages. Coverage
rows are excluded from this error/behavior summary. Task 4 and historical Task 1
judgment frequencies have no quality preference. Descriptive difference alone
does not establish a model's strength or weakness.

The **Within-model group contrasts** below the plots compare a group to disjoint
remaining sources of the same model. They retain their existing source/coverage
requirements. Neither panel replaces the unchanged paired comparison engine or
introduces an overall ethics rank.

## Reading conditions, denominators and availability

Every chart card repeats its input scope, selected condition and denominator
basis. Task 2 overview uses all instruction variants; Task 5 framing/composition
overview uses all framings under the selected metadata condition. Other detail
charts use the selected scope. Matched-input tables live in a separate collapsed
section and are never recalculated by these chart filters.

Task 1 gold-class-specific breakdowns are shown only when **Analyze by** matches
their released axis (currently input severity); they no longer remain under an
unrelated question/topic view. Select Input severity to inspect those charts.

Task 2 accuracy points up; answer-error points down. Strategy frequency has no
quality direction. Coverage describes completeness, not safety. Direction and
denominator labels also appear in exact tables and evidence. Task 5 can show
140/783 = 17.88% on valid choices and 140/784 = 17.86% on all expected rows;
the extra row is invalid, so these are different denominators for the same event.

A measured zero uses an unfilled baseline marker, with no positive-length fill.
Unavailable values state the known reason: no eligible denominator, no valid
outputs, condition not supplied, measurement not supplied, or historical value
not released. Absence alone is not relabeled as a confirmed measurement failure.

Key measured rates precede charts. Supported contrast candidates and detailed
interpretation follow the plots and start collapsed. Plot regions support keyboard
focus and scrolling; rate scales, conditions and legends remain beside the plot.
Dark outcome colors retain readable white labels. Exports preserve full plots and
exact observations; chart viewport scrolling does not discard data.

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
