# KoEVD Platform: evaluate, register and compare

The [Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform) connects
portable model evaluation results to owned registrations and shared numerical
profiles. Check [current acceptance](PUBLIC_SERVICE_ACCEPTANCE.md) for the actual
deployed release; a candidate branch alone does not activate the service.

## Explore without a file or account

1. The home opens **Model leaderboard**. Select a model name to see its declared model,
   revision, generation settings, measured scores and metadata charts.
2. Use the metric table to select a metric/evaluation group and search or
   sort observed values. Official rank eligibility and exclusion reasons remain
   separate. There is no combined ethics score.
3. In **Compare models**, choose two runs and build the paired comparison.
   Compare the same inputs and jointly valid outputs; inspect coverage and
   differing evaluation conditions before interpreting a difference.

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

For a saved private result, download its private original and upload it to a new
analysis session when needed. Direct reanalysis from saved registrations is not
currently offered. Public numerical downloads are reports, not upload artifacts.
