# KoEVD Platform: evaluate, register and compare

The [Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform) connects
portable model evaluation results to owned registrations and shared numerical
profiles. Check [current acceptance](PUBLIC_SERVICE_ACCEPTANCE.md) for the actual
deployed release; a candidate branch alone does not activate the service.

## Explore without a file or account

1. **Model leaderboard** initially shows **Paper experiment · 12 models**.
   These are historical aggregates. Open **Score definitions, denominators and
   evaluation conditions** before interpreting scores. Select **Evaluation
   conditions → Registered results** for current protocol submissions and the
   two Qwen references; these collections do not form one ranking.
2. Select a model name to open **Model details**. Paper details contain source
   tables; registered details contain declared settings, measured ratios,
   valid/expected coverage and metadata charts. Task 3 is classifier-labeled;
   Task 4 is descriptive and Task 5 tools are simulated.
3. Choose **Compare this model**. The correct collection and left model follow
   you into the comparison screen. The global **Compare models** navigation link
   does the same when used from model details.
4. Choose the right model and press the relevant **Compare** button. Changing a
   selector invalidates the previous result and its downloads, including a
   response still in flight. Press Compare again to calculate the new pair.
   Paper comparisons are aggregate only; registered comparisons use identical
   inputs and jointly valid outputs, with explicit compatibility warnings.

Details now open interactive Task charts. Use **Input scope / framing**,
**Analyze by** and **Show condition** to inspect exact conditional aggregates;
hover/focus or select a mark for counts, denominators and source support. Task 4
uses multi-label bars and heatmaps; Task 5 includes framing, outcome composition
and response-to-tool transitions. Comparison controls synchronize both models.
Export with **SVG** / **Chart JSON**. These are analysis snapshots, not files to
submit as results. Historical data supports only its released aggregates; see the
[chart interpretation guide](PUBLIC_PROFILES_GUIDE.md#interactive-model-details-v030-rc10).

The Qwen3-8B/4B references each contain 17,670 previously measured records.
They are operator references, not independent generation verification. Their
original responses remain private; numerical comparisons retain their counts.

## Evaluate your model and prepare JSON

Follow **[GETTING_STARTED.md](GETTING_STARTED.md)** from installation through
the standard input index, generation, measurement and portable export. It uses
`protocol-index` before generation and the same index for export/validation.
The Platform does not run inference. Keep your `results.json` original, source
commit, model revision and inference/measurement settings. Report/profile JSON
files are not upload artifacts. [RESULT_FORMAT.md](RESULT_FORMAT.md) is the format
reference; [OWN_MODEL_GUIDE.md](OWN_MODEL_GUIDE.md) covers custom local workflows.

Upload full records, not a hand-written score table. The server validates against
its configured input index and recomputes metrics. A different input set or
protocol requires an explicitly supported index rather than relabeling results.

## Analyze and register

1. Choose **Submit results**, then open the standalone `/submit` workspace before uploading. In the pre-upload
   account section choose **Sign in to save results**, then **Check account sign-in**.
   Older deployed versions put **Sign in with Hugging Face** / **Check sign-in**
   in the registration section instead; the order is still sign-in, then upload. Embedded and standalone cookies can differ; open the own-tab
   workspace before uploading to avoid losing access to an anonymous session.
2. In **Choose your result JSON**, select the result and **Validate and add results**.
   Temporary analysis is available without sign-in and does not publish data.
   In browsers supporting compression, large JSON files are compressed only for
   transport when this reduces their size. Choose the same original `.json`; the
   server restores and validates its exact bytes. The file on your device, model
   identity and recorded measurements are unchanged. Older clients can send plain
   JSON. You may also choose a losslessly compressed `.json.gz` copy of the same
   result. The server applies the same expanded-size and JSON validation limits.
   Compression does not increase the expanded 128 MiB limit.
3. Optionally build an analysis with another uploaded run or configured reference.
   The interactive report contains charts, groups and permitted response cases.
4. Follow **Continue to registration**. The validated upload is added to the
   **Private analysis result to preserve** selector automatically; select it. Older clients
   have **Refresh uploaded results** if the selector has not updated. Inspect the
   original model/generation/measurement declaration and confirm it. Unknown
   fields remain unknown; account sign-in does not verify model generation.
5. Set a display name/description and **Save private submission**. This preserves
   a separate original and event/revision history. Save the returned submission
   ID. Signing in again restores access to your registrations after a restart.

Editing the display name does not change the original model or result. A new
generation and a measurement recheck are distinct revision operations. An
identical original must not be presented as an additional independent model.

## Choose a sharing scope

For numerical sharing, enter a brief **Reason for this action or revision**,
select **Metrics summary only**, provide the separate **Permission statement**,
accept the sharing/retention notice and **Publish numerical summary**.
This exposes numerical profiles and declared model settings, without original
response text. A shared summary can be listed/compared while official ranks remain
disabled. Duplicate originals are counted once in metric comparisons.

Original-response sharing requires the separate independent permission review
and operator publication path; checking a box does not publish responses.
When both runs have approved response sharing, their public comparison offers
an import into your temporary analysis workspace to inspect response cases.
Otherwise numerical and metadata comparison remains available.

Profile and pair numerical reports support JSON, JSONL, CSV, Markdown and HTML.
These numerical downloads exclude prompts, responses, private review notes and
case identifiers. Compatible clients negotiate HTTP compression for numerical
and personal report downloads; saved files remain normal JSON/JSONL/CSV/Markdown/HTML.
Temporary personal analysis reports follow their separate
session scope and can contain your uploaded response text.

## Data handling and limits

- Analysis sessions expire after two hours. Reloading discards the page's access
  token; deleting session data removes that temporary session, not a separately
  saved registration. Keep your local original and downloaded reports.
- Registration originals, revisions, sharing consent and audit events are stored
  privately. A successful mutation confirms its durable checkpoint first. No
  successful registration acknowledgement is given for an unconfirmed save.
- **Stop sharing** removes current public catalog/profile/comparison
  access. It does not erase private originals, audit history or prior checkpoint
  copies. Previously downloaded shared copies cannot be recalled.
- The beta has no automatic erasure schedule. Private registration/audit copies
  remain until an operator-reviewed removal procedure; **Stop sharing** is the immediate public-removal action. Do not interpret withdrawal as permanent
  deletion of every retained copy. Request retention/removal guidance through
  the [project issue tracker](https://github.com/KETI-NLP/KoEVD/issues) without
  posting private outputs or credentials there.
- The upload limit is 128 MiB per file and four results per temporary session.
  Numerical exports are bounded to 32 MiB. CPU queue or state capacity can reject
  work explicitly; keep the same operation request for supported retries and
  check saved state before resubmitting. Storage is bounded, not unlimited.

Read [ACKNOWLEDGED_STORAGE_GUIDE.md](ACKNOWLEDGED_STORAGE_GUIDE.md) for the operator
storage/restore contract. Dataset research-use terms are separate from the code
license. Task 3 labels are classifier measurements, Task 4 strategy frequencies
are descriptive, and Task 5 tool selections are simulated. None establishes
universal model safety or a controlled demographic discrimination finding.

## Leaderboard home and recoverable submission

The public home opens the **Model leaderboard**. Choose a task-specific metric,
inspect coverage and evaluation groups, and compare two published runs. There is
no aggregate ethics score and official ranking remains disabled. **Submit
results** opens a separate upload/login/registration view. The navigation links
preserve temporary uploads within the same page; browser reloads/new tabs do not.
Open the standalone `/submit` workspace before login/upload when using the HF
embedded view.

Saving privately and publishing a numerical summary are separate. A saved
registration offers **Compare this result** after summary publication. Original
response text is not included in public numerical profiles or comparisons.

* **Cancel review request** returns an active request to its prior workflow and
  consent state. This remains possible if the operator later disables review.
* **Stop sharing** removes the public projection and clears current consent and
  approval. The original/history remain private; fresh consent is required to
  publish again.
* **Restore private draft** recovers a legacy registration you withdrew yourself without
  making it public. Use this instead of creating a duplicate original, then
  provide fresh consent for numerical sharing. Administrator withdrawals remain blocked.

When no publication administrator is configured, the independent review request
button is hidden and new requests are rejected by the server. Numerical sharing
still works. No action automatically retries an ambiguous write: refresh the
registration/history before repeating it. See the concrete
[retry and troubleshooting commands](GETTING_STARTED.md#troubleshooting-and-completion-check).

## Recover, find your model and interpret its metrics

- If generation fails, rerun the same `--stage generate` command with the same
  directory and generation settings. Successful rows are reused. If Task 3 had
  already been measured, validated predictions, measurements, traces and the old
  manifest are preserved under `generation_retries/` before resuming. A changed
  generation invalidates its Task 3/4 measurements; repeat classify, report and
  export. Do not upload the earlier export as the recovered run. An interrupted
  retry must finish with generate before measurement/export can continue.
- If only classification failed, repeat classify. Completed unchanged tasks are
  reused; use `--measurement-tasks 4 --batch-size 1` to retry only strategy
  measurement with a smaller batch. To replace completed measurements explicitly,
  use `--remeasure`. Integrity failures are rejected; they are not overwritten.
- If startup fails, use **Retry service connection**. It retries a missing
  analysis session as well as service configuration. A valid session and its
  uploads are retained; reloading the page instead loses the temporary token.
- After saving privately, numerical sharing still requires fresh permission and
  consent. After sharing, use **Show my model on leaderboard**, **View my public
  profile** or **Compare this result**. Private registrations are not public rows.
- **Find any published model** searches names, model IDs, revisions and submission
  IDs across every evaluation group. **Show model on leaderboard** switches to
  that run's group. The separate row filter searches only the current group.
  Different groups reflect different conditions; they are not one ranking.
- Task 2 leaderboard values are **accuracy (higher is better)**. Paired Task 2
  comparisons display **answer error rate (lower is better)**: within the same
  partition and valid outputs, accuracy = 100% minus error. Thus 81.55% accuracy
  corresponds to 18.45% error. Paired differences use jointly valid outputs;
  individual displayed rates may have different valid denominators.
- Task 1 missed risk and false alarms are separate conditional rates; its paired
  overall judgment error is a different denominator. Task 3 uses classifier-based
  unsafe response rates, and Task 5 uses unsafe **simulated** tool selections.
  Lower is better for these rates; measurement limitations still apply. Task 4
  strategy frequencies describe behavior and do not measure quality. N/A means
  an undefined denominator, not zero. There is no aggregate ethics score.

For a saved private result, sign in, select the registration and choose
**Analyze saved result**. Select a reference or second uploaded run and build
analysis. Your original and history stay unchanged. Public numerical downloads
are reports, not upload artifacts.

## Leaderboard, model details, comparison and submission (v0.3.0-rc.9)

The landing page is a searchable, sortable **model leaderboard**, defaulting to
all 12 models in the paper experiment. Choose Task tabs or All tasks. Display
positions follow the selected metric and order; they are descriptive, not an
official overall ethics rank. Task 1 judgments and Task 4 strategies do not have
a quality direction and are not offered as quality-ranking metrics.

Use **Evaluation conditions** to switch to registered results. Each recorded
input/configuration group has its own table; paper results and current-protocol
submissions never share a sorted order. The two existing Qwen3-8B/4B references
remain in the registered group. After publishing your summary, **Show my model
on leaderboard** selects your group and clears the search filter.

Paper Task 1 shows unsafe judgment rates for 11 high-coverage models and coverage
for all 12. Gemini 3.1 Pro has no released per-model judgment counts in that
source, so its judgment rate is N/A, with its 56.54% coverage retained. This is
not a judgment error rate. Paper Task 2 uses the unweighted mean of Choose Best,
Choose Unsafe and Relative Harmfulness. Open-model original summaries used four
variants and commercial summaries used three; details preserve those original
summaries separately. Counts cannot be recovered from rounded percentages.
Paper Task 3 uses unsafe/classified responses, with classified/expected counts.
Paper Task 4 shows descriptive strategies and measurement coverage. Paper Task 5
uses unsafe calls/all expected rows, pooled over three simulated framings; its
separate framing rates and parse coverage are available in details. These
populations differ from the current registered metrics shown in the other group.

**Details** opens a separate model screen with Task 1–5 measurements and source
CSV links. **Compare models** opens a separate comparison screen: paper models
use aggregate comparisons with coverage, without matched-case statistics;
registered results use the existing checked, matched-input comparison. Different
collections cannot be selected together. No new paired statistics are inferred
from paper aggregate tables. Back/forward navigation and model links retain the
selected screen.

**Submit results** opens its own screen. Sign in before selecting your file if
you want to preserve it, validate the exported results.json, confirm its model
settings, save privately, then optionally share numerical metrics. Saving is
separate from publication. Saved private results can be reopened with **Analyze
saved result** without manually downloading and reuploading. Existing retry,
consent, withdrawal and run-status instructions below still apply.

Public model results load independently of account checks and private analysis.
If account lookup fails, use **Check account sign-in**; the model list remains
available. For temporary analysis use **Retry analysis connection**. Neither
button automatically repeats an ambiguous save/share write.

After generation or measurement, inspect the printed overall status summary.
A command can finish with retained failed rows; successful exit does not mean
all API requests or task parses succeeded. Check again at any time:

```bash
koevd-pipeline --stage status --output-dir runs/my-model-core
```

This read-only check shows expected/generated/failed/pending rows for each task,
measurement readiness or integrity problems, and the next stage to run. It
requires no model endpoint, adapter or GPU. It does not verify model accuracy or
the freshness of an older exported JSON. Repeat your original generation command
when failures remain, preserving every model/decoding/provenance setting. After
changes, rebuild the report, reexport and validate against the same trusted index.
A status recommendation never authorizes editing hashes or discarding failures.

If a command stops before printing its status summary, run `koevd-pipeline --stage status --output-dir <the-same-run-directory>` to inspect retained progress and the next recovery step.

## Find your result after submission

**Save private submission** preserves your original and history; it does not add
a public leaderboard entry. Provide a reason, a permission statement and fresh
numerical-summary consent, then **Publish numerical summary**. The confirmation
explains the next actions: **Show my model on leaderboard** selects your group,
**View my public profile** gives a linkable profile, and **Compare this result**
opens a registered comparison. Your run does not enter the historical paper table.

Registered groups require identical recorded protocol, trusted input index,
generation settings, chat template, dtype, quantization and thinking settings.
The model ID/revision itself is excluded from the group key. Different native
templates can therefore separate otherwise standard runs. Inspect the readable
settings in the table's definitions panel and profile; group IDs are identifiers,
not scores. Cross-group matched-input comparisons remain available as exploratory
analyses with compatibility warnings. Unknown conditions remain unknown.

For the exact primary values used in the two collections, see the Task mapping
at the start of [GETTING_STARTED.md](GETTING_STARTED.md). Coverage is valid /
expected, whereas the displayed score uses its own event denominator. N/A can
mean unavailable historical counts, an unmeasured metric or no eligible outputs;
it never means measured zero. Task 1/4 tabs start in alphabetical order because
their paper values describe behavior rather than a quality ranking.

## Search, duplicate registrations and submission readiness

Use **Search all models** on the home to find paper results and registered runs
across condition groups. Matching names/aliases are listed with their collection;
**Show on leaderboard** opens that table and highlights the result. The advanced
**Find any published model** control leads to the same home. Scores remain in
their original condition groups. Model-name ordering supports A–Z and Z–A.

Multiple registrations of the same exact original occupy one distinct result row
with a registration count. Their names and submission IDs remain searchable, and
each owner's private history and public profile remain separate. The automatic
comparison action selects a different original. Two aliases of the same file
cannot provide an independent model comparison.

Before upload, run `koevd-results check-run` with `--run-dir`, `--input` and the
original `--trusted-index`, adding the registered protocol arguments from step 7
of GETTING_STARTED. It compares content and settings with the retained pipeline;
`stale_export` requires re-export, and `check_failed` requires investigation or
completion of pending recovery. `current_with_warnings` preserves failed requests
and missing measurements. It does not verify model identity, classifier accuracy
or universal safety; the Space cannot inspect your local files.

The **Deployment and version** link always opens the current service acceptance
record. Evaluation commands remain pinned to an immutable release tag. Historical
validation documents describe their own dates and releases, not today's runtime.


## Loading, selection and completion cues

Changing **Evaluation conditions** clears the prior model focus and retains the
chosen collection in its URL, including after a public-catalog refresh. A focused
model link still restores its group until you explicitly choose another collection.
Search says **in progress** while registered results load and updates automatically;
this is not a completed zero-match search. If you change models during comparison,
wait for the previous request to finish before the Compare button becomes available.
The old response is discarded, not attached to the new selection.

Task 3/4 canonical inputs overlap: core 2,000 + Task-5-linked 784 - common 125 =
union 2,659. There are 659 additional sources outside core. The diagrams in score
definitions, profiles and comparisons explain why subset counts are not additive.
Custom subsets and valid measurement denominators can differ from these totals.

Before selecting a JSON, use the [stage completion examples](GETTING_STARTED.md#decide-whether-each-stage-is-complete).
`current_with_warnings` means consistency with local records, not all-success,
parse accuracy or safety. Private save and public numerical sharing have separate
completion signals; neither account login nor a display name verifies model weights.


## Partial uploads and public revision scope

Multiple selected files receive individual outcomes. A successful file remains
available if another fails, and unchanged acknowledged files are skipped on an
explicit retry. Editing a file on disk requires selecting the corrected file again.
An exact duplicate response is reconciled through a read of current session uploads
before processing later files. Uploads are never automatically retried. The four
result/session and expanded 128 MiB/file limits are unchanged; remove a result when
the session is full. A removed result can be uploaded again.

The latest saved revision and current public revision can differ. Saving revision 2
privately leaves published revision 1 visible until explicit replacement or stopping
sharing. Owner buttons name the public revision they open/compare; private analysis
and original downloads use the latest saved revision. Confirm the new declaration,
select the correct revision kind, save privately, then provide fresh permission and
consent to publish its numerical summary. See the [revision walkthrough](GETTING_STARTED.md#update-a-saved-result-without-confusing-its-public-revision)
and [recovery decision table](GETTING_STARTED.md#decide-whether-each-stage-is-complete).


## Expired sessions, owner conflicts and measurement conditions

**Retry analysis connection** checks the current temporary session. A transient
connection failure preserves its token and validated uploads. Confirmed expiry
or a missing server session invalidates only temporary uploads/reports; explicit
reconnection creates a new session. Reselect local files or use **Analyze saved
result** to import a preserved registration. No upload/save/share is replayed.

For a registration version conflict, use **Reload selected registration** or
**Refresh submissions**. This reads the selected latest state without a page
reload, preserves unsaved name/description/reason, and clears sharing consent and
its permission statement. Review the new state before explicitly retrying.

Generation groups do not include every classifier measurement condition. Task
3/4 cells show declared batch/precision and expandable settings; choose that
Task to filter matching declarations. Unknown settings remain unknown. Filters
do not change Task 1/2/5 groups or create rank eligibility. Public profiles and
numerical JSON exports retain the added settings declaration. That declaration omits
trace identities, raw responses, device names and response-dependent measurement counts. Comparison
warnings show both sides' declared values. Matching declarations do not certify
generation authenticity, classifier accuracy or universal model safety.
