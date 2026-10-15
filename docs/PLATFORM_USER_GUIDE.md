# KoEVD Platform: evaluate, register and compare

The [Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform) connects
portable model evaluation results to owned registrations and shared numerical
profiles. Check [current acceptance](PUBLIC_SERVICE_ACCEPTANCE.md) for the actual
deployed release; a candidate branch alone does not activate the service.

## Explore without a file or account

1. Open **Explore models**. Select a published run to see its declared model,
   revision, generation settings, measured scores and metadata charts.
2. Use **Metric leaderboard** to select a metric/evaluation group and search or
   sort observed values. Official rank eligibility and exclusion reasons remain
   separate. There is no combined ethics score.
3. In **Compare models**, choose two runs and build the paired comparison.
   Compare the same inputs and jointly valid outputs; inspect coverage and
   differing evaluation conditions before interpreting a difference.

The Qwen3-8B/4B references each contain 17,670 previously measured records.
They are operator references, not independent generation verification. Their
original responses remain private; numerical comparisons retain their counts.

## Evaluate your model and prepare JSON

Use [OWN_MODEL_GUIDE.md](OWN_MODEL_GUIDE.md) to run the existing Task 1–5 pipeline
against your own vLLM-compatible endpoint. The Platform does not run inference.
Use [RESULT_FORMAT.md](RESULT_FORMAT.md) to export and validate one portable
full-record JSON and create local reports. Keep this original and record your
source commit, model revision and inference/measurement settings.

Upload full records, not a hand-written score table. The server validates against
its configured input index and recomputes metrics. A different input set or
protocol requires an explicitly supported index rather than relabeling results.

## Analyze and register

1. Open the workspace in its own tab, then **Sign in with Hugging Face** and
   **Check sign-in**. Embedded and standalone cookies can differ; open the own-tab
   workspace before uploading to avoid losing access to an anonymous session.
2. In **Analyze your JSON**, select the result and **Validate and add results**.
   Temporary analysis is available without sign-in and does not publish data.
3. Optionally build an analysis with another uploaded run or configured reference.
   The interactive report contains charts, groups and permitted response cases.
4. In **Register or manage results**, select the validated upload. Inspect the
   original model/generation/measurement declaration and confirm it. Unknown
   fields remain unknown; account sign-in does not verify model generation.
5. Set a display name/description and **Save private submission**. This preserves
   a separate original and event/revision history. Save the returned submission
   ID. Signing in again restores access to your registrations after a restart.

Editing the display name does not change the original model or result. A new
generation and a measurement recheck are distinct revision operations. An
identical original must not be presented as an additional independent model.

## Choose a sharing scope

For numerical sharing, select **Metrics summary only**, provide your permission
statement, accept the sharing/retention notice and **Publish numerical summary**.
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
case identifiers. Temporary personal analysis reports follow their separate
session scope and can contain your uploaded response text.

## Data handling and limits

- Analysis sessions expire after two hours. Reloading discards the page's access
  token; deleting session data removes that temporary session, not a separately
  saved registration. Keep your local original and downloaded reports.
- Registration originals, revisions, sharing consent and audit events are stored
  privately. A successful mutation confirms its durable checkpoint first. No
  successful registration acknowledgement is given for an unconfirmed save.
- **Withdraw publication** removes current public catalog/profile/comparison
  access. It does not erase private originals, audit history or prior checkpoint
  copies. Previously downloaded shared copies cannot be recalled.
- The beta has no automatic erasure schedule. Private registration/audit copies
  remain until an operator-reviewed removal procedure; withdrawal is the supported
  immediate public-removal action. Do not interpret withdrawal as permanent
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
