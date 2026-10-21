# Analyze input conditions, response strategies and simulated choices

Start at the [Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Choose an evaluation collection, open a model, and select a task. Historical paper
experiments and current-protocol registrations have different inputs and measurement
definitions. They remain separate collections; there is no combined ethics score.

## Read the analysis screen

Choose a grouping attribute first. **Input condition filters** opens the four
metadata filters (plus tool-risk category in Task 5); the summary shows the number
of active requirements. Active conditions remain visible as removable chips.
Optional display controls and framing explanations are collapsed initially.
The original paper summary remains separate and does not follow chart filters.

Registered comparison has two distinct outputs: task charts subtract/compare each
model's observed rates using its own valid measurements, while the separate
matched-input statistics use jointly valid observations on identical inputs.
Chart conditions do not recompute the separate matched-input statistics.
Evidence panels distinguish the unique input inventory, valid measurements, and
the conditional row denominator. These numbers can legitimately differ.

### Select evidence and continue an analysis

Hover or keyboard-focus shows a concise tooltip positioned using its actual size.
Click or press Enter on a mark to reveal the complete evidence panel; **Back to
selected mark** returns to that chart position. Task 4/5 comparison evidence also
shows the matching observation for both models, each with its own fraction and
completion. **Expand chart height** removes that chart's internal vertical scroll;
**Collapse chart height** restores the compact view. These controls do not change
measurements or exports.

Open **Analyze this input condition in another task** to preview the target input
scope and expected source counts for each model. Select **Analyze this condition
in Task 4/5/3** to copy metadata requirements explicitly. A compatible current
scope is retained; otherwise the displayed target scope is used. Moving from
Task 5 to Task 3/4 prefers the Task-5-linked scope when supplied. Tool risk category
is omitted outside Task 5 with a visible notice. Conditions absent from the target
metadata are explained and transfer is disabled; an empty intersection is warned
before applying. Target Task 3 display evidence thresholds and label search reset
to show all groups. Regular task tabs still restore each task independently.
Equal metadata conditions do not establish identical input inventories, sequential
tool execution or a causal comparison.

## Task 3: where are unsafe generated responses observed?

Choose question/utterance type, topic, input severity or explicitness as the grouping
attribute. Input filters combine with AND. Applying a topic cell retains existing
topic memberships: Gender and Taste means their intersection, not all Taste inputs.
Topic totals overlap and must not be added. Input severity is input metadata, not
the severity of the generated answer.

Read unsafe/classified together with classified/expected completion. Failed,
empty and unclassified outputs are unknown, never safe. Cells display event counts
and their classified denominators; `C valid/expected` below a cell is completion.
Dashed borders flag fewer than 20 sources; amber borders flag completion below 90%.
Zero events with a positive denominator differ from no inputs or no classifications.
Severity and explicitness retain semantic order in both individual and comparison
views. Label search does not change the input cohort.

Open **Chart display and evidence filters** to set **Minimum classified sources**
(all, 20, 50, 100) and **Minimum classification completion** (all, 90%, 95%, 100%).
These are display thresholds, not record filters: all cohort totals, rates and
denominators stay unchanged. Bars and difference rows omit groups below either
threshold; cross cells retain their position and say **Filtered**, distinct from
no inputs or unclassified outputs. The status states groups shown/hidden before
label search. In comparison, every selected model must meet the thresholds.
The overall unsafe card/overview and supported-contrast screening are unaffected.
Clear evidence filters or reset the Task 3 view to show all groups again.
Thresholds survive task switching, detail-to-comparison handoff and local reload.
They do not establish statistical significance or confirmed strengths/weaknesses.

Chart JSON describes the displayed chart. Analysis JSON retains the complete
condition aggregates and the selected display thresholds for reproducibility.

Screening candidates use their own fixed support/completion policy. If a candidate
is hidden by the current display thresholds, its card says so and offers separate
actions to inspect it **and clear evidence filters**, or apply the condition **and
keep evidence filters**. The latter can legitimately produce an empty display;
clear evidence filters in the chart to recover without changing its cohort.

The supported-contrast preview compares a group with disjoint remaining inputs
inside the current cohort. Each side needs at least 20 classified sources and 90%
completion. This is descriptive screening, not significance, causal bias or a
confirmed strength/weakness. No candidate does not establish safety.

Model differences subtract each model's unsafe/classified rate. There is no single
fraction for the difference: inspect the two separate fractions and completion.
The minimum model support is not a jointly valid paired sample count. Full-paper
summary tables are collapsed separately and do not follow chart filters. Existing
registered matched-input statistics also retain their own partitions.

## Task 4: how does the model respond?

1. Inspect inclusion of all 15 strategy labels. Multiple strategies can occur in
   one response, so their percentages may sum to more than 100%. They describe
   behavior; more frequent inclusion is not a higher quality score.
2. Narrow the same four input attributes. Choose **Focus strategy** to see where
   that strategy appears; optionally open the full strategy-by-group matrix.
   Definitions and newly written illustrations are available separately. These
   illustrations are not benchmark examples or gold response annotations.
3. Inspect the selected strategy by Task 3 response classification. Its denominator
   is strategy-classified responses in each response-label group. These groups may
   contain different inputs across models; no causal benefit is established.
4. Open co-occurrence as counts or `P(column strategy | row strategy)`. The latter
   divides the joint count by the row-strategy inclusion count. It is directional,
   not correlation or quality. The live grid keeps row and column headings fixed during horizontal/vertical
   scrolling. Cell evidence also shows full-input completion. The two-model
   strategy overview uses compact paired dots with both exact fractions, preserving
   all fifteen labels and the same 0–100% scale. The diagonal is 100% only when that strategy occurs;
   an absent row has no denominator. Count colors share a maximum in comparison.
5. Use **Compare this cohort with another model** to retain conditions and strategy
   selection. Numerical chart and analysis JSON exports retain scope and denominators.

The separate **Unsafe strategy marker** is not a sixteenth strategy or the Task 3
response-safety label. Completion shows both classified/strategy-eligible responses
and classified/full input inventory. In the paper, outputs not classified in Task 3
could be absent from Task 4 eligibility. This explains how conditional strategy
completion can be 100% while full-input completion is lower.

The displayed mean includes only the 15 strategy labels. The original paper's
reported density included the separate Unsafe marker. Original tables and scores
are preserved; the two density definitions must not be conflated.

## Task 5: when are unsafe simulated tool choices observed?

The overview compares Safety-guided, Tool-forced and Unsafe-induced instructions
under the same input filters. Their summaries explain the instructions, not literal
benchmark prompts. Select a framing overview mark and **View this framing** to update detail
charts; **Back one condition** restores the preceding framing and input conditions.
Other detail charts use the selected framing, labelled above
each chart. Filters additionally include the trusted tool-risk category; this is
distinct from topic and severity and is not taken from a model's self-report.

- **Unsafe/valid choices** excludes invalid choices. Inspect valid/expected
  completion beside every rate. Unsafe/all expected is supporting information;
  invalid outputs can lower it and are not safe.
- **Seven outcomes** places the two models' stacked bars together under each
  framing in comparison. The outcome colors are shared; model rows and exact
  denominators remain distinct. **Seven outcomes** divides unsafe tool, allowed tool, other available tool,
  refusal, answer without tool, clarification and invalid by all expected inputs.
  These exclusive outcomes sum to 100% when the denominator exists. Allowed tool
  selection is not proof of correct or safe execution; no tool is actually executed.
- **Input group × framing** locates conditions associated with unsafe selection.
  Select a cell to pin counts, apply its input condition and framing, or compare
  that condition with another model. Clear filters or use Back one condition to
  recover. Task-specific conditions survive switching tasks and returning.
- **Unsafe choice by Task 3 response label** directly compares classifier-safe
  and classifier-unsafe groups for each framing. Use **Response-group denominator**, immediately above these bars (also included when using the Response safety
  correspondence section shortcut), to switch
  between valid choices and all matched inputs. This switch affects only those
  bars: the seven-outcome composition and correspondence matrices always include
  invalid outputs in their expected-input/row denominators. The detailed correspondence matrix includes unclassified,
  missing and invalid observations instead of silently discarding them.

Task 3 responses and Task 5 choices are separate measurements matched by original
input identity. The correspondence is not a sequential tool-execution trace or a
causal effect. Each framing has one observation per input; 784 inputs across three
framings produce 2,352 observations, not 2,352 independent sources.

### Historical parsing and measurement limits

For the twelve archived paper models, original `Parsed rows` counts nonempty
archived parsed objects, including some without a decision. The new seven-outcome
view requires successful status, a recognized archived decision, and an available
tool for a call. It does not rerun the parser. Two historical call decisions had
no tool name and are now explicitly invalid in this view. The archive's parse
counts, original unsafe/all scores and published correspondence counts reconcile
separately; they are not replaced by the normalized-choice completion.

Current-protocol registrations continue to use their existing strict diagnostics.
Historical normalization is not evidence of identical prompts, parsers, classifiers
or generation conditions between collections. Neither collection has official ranks.

## Provenance and implementation

`paper_assets/data/behavior_aggregates.json` contains numerical metadata buckets
for all twelve historical models. The builder checks Task 3/4 identities and
metadata, duplicate sources, the same 784 Task 5 sources per framing, exact original
strategy counts and selected rates, framing counts and original Task 3/5 overlap.
Source hashes are recorded; prompts, responses, rationales and source IDs are omitted.
Per-model assets load only when opening detail/comparison, keeping the initial
leaderboard independent of large strategy/tool aggregates. Failed detail loading
offers an explicit retry while retaining original tables.

Operators retaining the canonical original archive can reproduce numerical assets:

```powershell
$env:PYTHONPATH = 'src;scripts'
python scripts/build_paper_behavior.py --archive-root /path/to/original/workspace
python scripts/build_paper_leaderboard.py
```

Current-protocol offline diagnostics and public profiles share the same
`behavior_facets` projection in Task 4/5. The public projection contains numerical
buckets, not original responses or individual source identities. All model scores,
publication revisions and matched-input statistical definitions remain unchanged.
