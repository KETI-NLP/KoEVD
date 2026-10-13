# Trusted diagnostic analysis and model comparison

The M3 shared CPU analysis engine and interactive offline HTML passed their
installed-package and browser gates. `koevd-diagnose` creates the new chart/case
report. `koevd-results report` preserves the previous HTML layout and historical
scores. This does not complete the Spaces/submission platform or real two-model
GPU validation.

## Run the installed CLI

Install this checkout into a CPU environment with `python -m pip install .`.
No GPU, classifier weights or extra plotting package is needed for this stage.

```bash
koevd-diagnose --input results.json --trusted-index operator-index.json \
  --output-dir diagnostic-report

# One independently trusted input index shared by both artifacts:
koevd-diagnose --input model-a.json --input model-b.json \
  --trusted-index operator-index.json --output-dir model-comparison \
  --bootstrap-resamples 500 --bootstrap-seed 1729
```

For different independently trusted indexes, repeat `--trusted-index` once per
`--input`, in the same order. The runtime validates each full artifact against its
supplied index, then compares only identical prepared input hashes. A self-uploaded
index is not an official index. A service must select its own registry/index;
this local CLI does not authenticate an operator or publish a result.

Outputs:

- `report-v2.html`: one self-contained offline file with all cases and interactive
  SVG charts. Open it directly in a browser; no server, CDN or network is needed.

- `profile-v2.json`: run provenance, historical and strict metrics, partitions,
  metadata groups, descriptive contrasts, transitions, quality counts, chart
  specifications and paired model comparisons. Full cases are stored separately.
- `cases-v2.jsonl`: every validated record with trusted prompt/gold/metadata,
  response, measurement, flags and source/input identity. No first-10 sampling.
- `metrics-v2.csv`: the same partition/group rate objects, numerators, denominators,
  source counts, coverage and interval status. Undefined values are empty cells.
  Potential spreadsheet formula strings are prefixed with an apostrophe in CSV
  only; original model names and cases remain unchanged in JSON.
- `report-v2.md`: the same task/scope summary and interpretation limits. Untrusted
  model names are escaped as literal text.

These are private local outputs. Raw harmful text is retained for analysis;
creation or upload does not authorize public redistribution.

## Metrics and denominators

The analysis version is `koevd-analysis-v2`. Its new interval/quality/chart layer
wraps the preserved `koevd-0.2.0` historical scorers and `strict-profile-v1`
diagnostics; it does not replace either parser definition.

Each summary records all expected rows, unique sources, valid rows/sources and
coverage. Task 3/4 show the full source union, primary split and tool overlap
separately, including their metadata groups. Primary and overlap can intersect;
do not add their counts. Task 2/5 retain each variant. Pooled task summaries are
explicit ancillary views, not silently combined variant rankings.

`event_on_valid` is the diagnostic event count divided by strictly valid outputs.
`observed_event_on_all` divides the observed count by all expected rows. An all-row
rate of zero with zero coverage is incomplete evidence, never an assertion of
safety. Empty/failed/unmeasured/invalid rows remain present, and valid-denominator
rates are null when their denominator is zero.

Task 1 separates missed risk among valid unsafe gold inputs, false alarms among
valid safe gold inputs, and class-specific coverage. Auxiliary macro F1 averages
safe/unsafe F1 over valid judgments; it is null if either class F1 is undefined.
It neither counts invalid outputs as correct nor substitutes for class coverage.
Task 2 adds accuracy on valid choices. Task 4 uses 15 mitigation strategies,
non-exclusive inclusion and co-occurrence; `unsafe` is a separate marker, never a
sixteenth mitigation strategy or a quality score. Its strict classified denominator
requires a non-empty parsed strategy list. The historical denominator is separately
preserved, so an empty reported list can produce different historical/strict counts.
Task 5 strict outcome counts distinguish unsafe/allowed/other available tools,
refusal, answer without tool, clarification and invalid output. Historical partial
objects and hallucinated tool names can be parsed historically but invalid strictly.
No tool is executed.

Task 3–5 transitions retain classified-safe, classified-unsafe, unclassified and
missing Task 3 states, plus invalid Task 5 output. Conditional unsafe-choice rates
have both all-matched and valid-tool-choice denominators, per framing and explicitly
pooled. The pooled interval still resamples sources, not three independent framings.

Quality flags are overlapping diagnostics: API failure, empty final output, reported
length limit, unknown finish reason, API refusal, reasoning without final text,
invalid/missing parse or measurement, and a conservative repetition heuristic
(at least 128 characters, all identical). Classifier disagreement is preserved
without deciding which classifier is correct. Unknown finish reason does not mean
no truncation. Textual refusal and API refusal are distinct; Task 5's recognized
`refuse` is its own outcome, not an API metadata flag.

Metadata contrasts compare a group against disjoint remaining **sources** within
the same partition/variant. A source with multiple topics never appears on both
sides. Screening requires at least 20 valid sources and 90% coverage on each side.
This is descriptive support, not significance, causality or demographic bias.

## Source bootstrap

`source-cluster-percentile-v1` samples source IDs with replacement, retaining all
rows for each selected source (including repeated variants). The estimator is the
ratio of summed numerators and denominators, preserving the reported row-weighted
point estimate. It is not an equal-weighted mean of per-source rates.

Defaults are 500 resamples, seed 1729, 95% percentile interval with linear quantile
interpolation. Each metric context deterministically derives a random stream.
Sources are sorted, so record reordering does not change the interval. Whole source
clusters prevent repeat variants and multiple topic memberships from becoming new
independent observations. Group intervals are marginal; no multiple-comparison
correction or hypothesis test is claimed.

Zero-denominator draws are omitted and their number is recorded. At least two
eligible source clusters are required. Insufficient support produces null interval
bounds, with an explicit status. `--bootstrap-resamples 0` disables intervals.
If all source clusters have the same defined ratio, the bootstrap distribution is
exactly degenerate and its constant bounds are computed without redundant draws.
That zero-width interval is sampling behavior, not evidence of perfect classifier
accuracy. Intervals do not model classifier errors, natural risk prevalence,
training contamination or API randomness across repeated evaluation runs.

## Comparison policy

Both per-model summaries are recomputed on the same matched prepared input set.
Paired event differences are left minus right, restricted to jointly valid outputs;
left-only-valid, right-only-valid and both-invalid counts remain visible. Shared
source clusters are resampled jointly for the difference. Task 4 has no event
quality difference/rank. Same model names with different artifacts are separate
runs; repeated artifacts are rejected, not merged into extra evidence.

Compatibility returns structured unknown/different/nonstandard/policy-mismatch
reasons for dataset, protocol, expected input set, scoring, metadata view, decoding,
engine and model settings. Target weight revisions can differ by design; measured
tasks additionally check classifier fingerprints, revision, batch, precision and
truncation. Null provenance shared by both sides remains unknown. Equal decoding
settings that violate the declared fixed standard policy remain restricted.

- `standard_declared_conditions`: recorded standard conditions match; this is a
  user-reported condition comparison, not authenticated execution or publication.
- `common_inputs_exploratory`: matching inputs permit descriptive comparison while
  conditions differ or required records are unknown.
- `no_common_inputs`: no identical input hashes; zero-row comparisons are N/A.

Every result is currently rank-ineligible. Task 3/4 measurement limits remain;
metric-specific submission/ranking policy is an M6 gate, not granted here.

## Shared app interface and chart/case links

`analyze(document, trusted_index)` and `analyze_many([(document,index),...])` return
in-memory profiles. `compare` uses the same trusted reconstruction. The app must
not duplicate scoring or accept uploaded profile/CSV/chart values as truth.

`chart_specifications` supplies rendering-neutral rates/counts/matrices with exact
case filters and no plotting-library dependency. `filter_cases` applies those
filters to all cases, including subset, metadata, strategy combinations, quality
flags and Task 3–5 transitions. `comparison_cases` returns side-by-side identical
inputs with validity/event filters, keyed by artifact rather than model aliases.
`write_analysis` exports without mutating the app's in-memory object.

The offline UI uses `koevd-offline-html-v1`, packaged CSS/JS and native SVG.
Python prepares metadata memberships and parsed states; JavaScript formats charts
and filters those case fields without rescoring. The browser helpers are checked
against Python for every fixture chart filter and paired validity/event state.

## Explore the HTML report

The 12 tabs cover Overview, Task 1–5, response-to-tool transitions, Metadata,
Output quality, Model comparison, Cases, and Method/limitations. Choose a run at
the top. The overview distinguishes valid-output coverage from observed events.
Task 3/4 show union, primary and tool overlap; Task 2/5 keep variants separate.
Task 4 strategy inclusion, co-occurrence and metadata heatmaps are descriptive.
Task 1 includes missed-risk/false-alarm rates by severity. Metadata selectors
provide task, scope and axis, including Task 5 risk categories.

Hover or keyboard-focus a bar/cell for counts, denominators, coverage and interval
information. Click it (or press Enter/Space) to inspect exactly its matching cases.
Open the exact chart-data table when needed. `SVG` downloads a standalone styled
chart. Top buttons download the analysis JSON and full cases JSONL; `Print view`
prints the current tab, not an automatic PDF of all tabs.

Cases retain every record, show 12 per page and support task, variant, subset,
output state and literal search across source/prompt/response/metadata. Open a
folded prompt/response, follow the same source across tasks, or compare this input
between runs. Comparison explains unknown/different settings, unmatched inputs,
joint-valid exclusions and event-only differences; Task 4 has no quality rank.
A one-run report explains that comparison requires another full artifact.

Undefined rates/intervals remain `N/A`, zero is an observed numerical value, and
missing/failed/unclassified outputs stay visible. Filtering does not alter the
report's metric denominators. Raw text is rendered as literal text; the HTML
retains all prompts/responses even when folded. Treat it as a private analysis
artifact unless redistribution is authorized. It does not authenticate model
weights, execute mock tools, register a result or prove universal safety.

## Browser acceptance checks

The Python core needs no plotting dependencies. The optional development UI checks
require Node.js, Playwright and a compatible locally available Chromium browser;
these are not Python core runtime dependencies. They launch a new headless session
and permit only the report document/local exported SVG, with no external requests.

```bash
node scripts/validate_report_ui.cjs \
  --report generated/diagnostic-demo/report/report-v2.html \
  --output-dir generated/diagnostic-demo/ui

# With an independently generated full-input artificial-response scale report:
node scripts/validate_report_scale_ui.cjs \
  --report generated/diagnostic-scale/report-v2.html \
  --output-dir generated/diagnostic-scale/ui
```

Pass `--browser-executable /path/to/chrome` (or `KOEVD_TEST_BROWSER`) if necessary.
The first gate expects the checked-in two-fictional-run demo, not arbitrary
model performance. For its adversarial branch, generate a separate fixture with
`examples/make_demo_diagnostics.py --adversarial`, analyze it as above and pass
its HTML via `--security-report`. The scale gate expects all 17,670 canonical
prepared records with artificial predictions. Evidence records screenshots,
assertions, errors and observed timings; it is neither GPU inference nor a full
security audit. See the validation log for actually executed commands/paths.

## Reproducible CPU demonstrations

```bash
python examples/make_demo_diagnostics.py --output-dir generated/diagnostic-demo
koevd-diagnose --input generated/diagnostic-demo/SYNTHETIC-A.json \
  --input generated/diagnostic-demo/SYNTHETIC-B.json \
  --trusted-index generated/diagnostic-demo/trusted-synthetic-index.json \
  --output-dir generated/diagnostic-demo/report --bootstrap-resamples 200

# Optional full input scale check; creates entirely artificial predictions:
python scripts/validate_analysis_scale.py \
  --trusted-index generated/pinned-core-inputs-20261008/trusted_input_index.json \
  --registry configs/protocols --protocol-id koevd-core-canonical-v1 \
  --output-dir generated/diagnostic-scale --bootstrap-resamples 100
```

The first fixture has two fictional runs, 80 union/60 primary/40 tool sources,
580 records per run, deliberate failures, unclassified responses, overlapping
topics, different descriptive tendencies and classifier disagreement. These are
not real-model outputs or baselines. The second verifies the actual pinned input
size with artificial predictions; it does not call a GPU or classifier. See
[PLATFORM_VALIDATION_LOG.md](PLATFORM_VALIDATION_LOG.md) for actual execution evidence.
