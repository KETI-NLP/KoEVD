# Evaluate your model, register its results and compare

This guide connects one complete run: **GitHub → your model endpoint → Task 1–5
evaluation → `results.json` → private registration → optional public numerical
comparison**. Commands use a Linux shell and run from the repository root.
The Platform analyzes uploaded results on CPU; it does not host or evaluate your
model. You supply inference resources for your model and the two measurement models.

To explore first, open the [public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
No account, GPU or upload is required to inspect the two full Qwen3 references,
their metric tables, metadata trends and paired comparisons. If you already have
a completed standard run and its trusted index, start at step 7.

Use the current `main` source for the workflow described here and record its
commit. [Service acceptance](PUBLIC_SERVICE_ACCEPTANCE.md) identifies the deployed
release; a newer GitHub change does not itself update the Space. Earlier
validation logs describe their original dates and versions.

## 1. Install the evaluation client

```bash
git clone https://github.com/KETI-NLP/KoEVD.git
cd KoEVD
git rev-parse HEAD
python3.11 -m venv .venv-eval
source .venv-eval/bin/activate
python -m pip install -e ".[hub]"
```

Keep this shell at the repository root. Use a **separate environment** for your
vLLM server: its Torch/Transformers requirements can differ from those of the
measurement classifiers. Core preparation, export and reports need no GPU.
Public code uses Apache-2.0; dataset, measurement weights and copied classifier
wrappers have separate [terms](../NOTICE.md).

## 2. Download the pinned data and measurement models

These are the revisions in `configs/protocols/koevd-core-canonical-v1.json`.
The two adapters label **your model's responses**; they are not the model being
evaluated. Downloads include the full measurement base weights.

```bash
koevd-download --repo-id KETI-NLP/KoEVD --repo-type dataset \
  --revision f5920837769bea77e072c8e033e5ad9cbff4d45d --local-dir downloads/KoEVD
koevd-download --repo-id KETI-NLP/KoEVD-assistant-safety --repo-type model \
  --revision e821f2a0d8809bafe0cbf1b6ee0ac8350d2554b3 --local-dir downloads/KoEVD-assistant-safety
koevd-download --repo-id KETI-NLP/KoEVD-response-strategy --repo-type model \
  --revision 846df8d29758b956c420e0f4dd17ced8630a9b81 --local-dir downloads/KoEVD-response-strategy
koevd-download --repo-id Qwen/Qwen3.5-0.8B --repo-type model \
  --revision 2fc06364715b967f1860aea9cf38778875588b17 --local-dir downloads/Qwen3.5-0.8B
koevd-download --repo-id Qwen/Qwen3-8B --repo-type model \
  --revision b968826d9c46dd6066d109eabc6255188de91218 --local-dir downloads/Qwen3-8B
```

Download your **target model** separately, retaining its actual immutable revision.
HF CLI download authentication and the Platform's browser sign-in are separate.

## 3. Prepare the registered full input set

Use a new directory. Keep this index for every subsequent stage:

```bash
koevd-results protocol-index --registry configs/protocols \
  --protocol-id koevd-core-canonical-v1 --dataset-dir downloads/KoEVD \
  --run-dir runs/my-model-core --output runs/my-model-core/trusted_input_index.json
```

This checks the pinned files and preparation implementation, then creates
`pipeline.json`, task inputs and the index. The expected full record counts are:

| Task | Records | What is measured |
|---|---:|---|
| 1 | 2,000 | Input-risk judgments |
| 2 | 8,000 | Candidate-response choices, four variants |
| 3 | 2,659 | Safety labels on generated responses |
| 4 | 2,659 | Strategies in those same responses; no second generation |
| 5 | 2,352 | Text-only mock action choices, three framings |
| Total | 17,670 | 15,011 generation requests, excluding probes/retries |

Task 3 includes the union of core and tool-overlap sources; inspect its core-only
partition when needed. Task 5 never executes real tools.

**Do not replace this step with `koevd-results index`.** That command makes a
local custom index, even when its row counts match. The hosted server selects
its independently configured input index; it does not accept an uploaded index.
The fixed prefix-4 and prefix-96 integration catalogs are separate custom views,
not full-benchmark estimates. An arbitrary `--limit-sources` smoke run is for
local diagnostics and is not automatically accepted by the Platform.

For a low-cost endpoint smoke run, use the separate directory in
[OWN_MODEL_GUIDE.md](OWN_MODEL_GUIDE.md#prepare-first-and-inspect-the-request-count).
Do not reuse it for the full protocol run above.

## 4. Start your model server and check the connection

In your separate serving environment, install a vLLM build supported by your
GPU/driver and target architecture. A server example, with values replaced by
your real model repository and immutable commit:

```bash
# Replace both values with your actual model identity.
MODEL_ID='YOUR_ORGANIZATION/YOUR_MODEL'
MODEL_REVISION='YOUR_IMMUTABLE_COMMIT'
vllm serve "$MODEL_ID" --revision "$MODEL_REVISION" \
  --served-model-name "$MODEL_ID" --host 127.0.0.1 --port 8000 \
  --generation-config vllm
```

See the [vLLM OpenAI-compatible server documentation](https://docs.vllm.ai/en/v0.13.0/serving/openai_compatible_server/)
for the generation-config option and architecture-specific serving settings.
The prior two-model GPU validation used vLLM 0.13.0; that does not establish
compatibility with every target model. If serving remotely, use the reachable
endpoint and its normal authentication, rather than exposing an unauthenticated
server to the internet. In the evaluation shell, set `MODEL_ID` to that same real repository ID (shell
variables are not shared between environments). The served ID is exported as the
original model ID; do not replace it with a generic alias such as `my-model`.
For a local unpublished model, use a stable, unambiguous ID and retain its
revision/artifact identity. The registration display name is a separate label.
Perform a separate connection probe plus four prepared-input probes:

```bash
koevd-pipeline --stage preflight --output-dir runs/my-model-core \
  --base-url http://localhost:8000/v1 --model "$MODEL_ID" \
  --temperature 0 --max-tokens 1024 --preflight-samples 4
```

Check `preflight.json`. These probes are outside evaluation denominators and do not create prediction
rows. The four prepared samples exercise Task 1/2/3/5 with the actual output
budget, rather than only a short synthetic request. Check each sample's
`nonempty_final_content` and `finish_reason`; empty final content or token-limit
finishes require inspection of thinking/output budgets before the full run.
A successful probe does not establish full coverage or model identity.

For a CPU check of **all prepared prompt lengths**, install a tokenizer-compatible
Transformers build and add `--tokenizer-dir /path/to/local/target-tokenizer
--context-window YOUR_ACTUAL_SERVER_CONTEXT_LIMIT` to the same preflight command.
The tokenizer must match the server's chat template and revision; pass the same
`--extra-body-file` in preflight and generation when using template options.
The check rejects prompts whose input length plus 1,024 output tokens exceeds
that declared limit, before making API requests. It does not prove server/local
tokenizer parity. No custom remote tokenizer code is executed.

Use
`OPENAI_API_KEY` for an authenticated endpoint, or select its environment variable
with `--api-key-env`; do not put credentials in command arguments or JSON files.

## 5. Generate responses and retain provenance

Create `model-provenance.json` from actual serving settings. Example fields:

```json
{
  "revision": null,
  "dtype": null,
  "quantization": null,
  "chat_template": null,
  "thinking": null
}
```

Replace known values with your real revision, dtype, template identity and
thinking setting; leave unknown values null. These declarations do not verify
loaded weights. Then run:

```bash
koevd-pipeline --stage generate --output-dir runs/my-model-core \
  --base-url http://localhost:8000/v1 --model "$MODEL_ID" \
  --temperature 0 --max-tokens 1024 --workers 4 \
  --model-provenance-file model-provenance.json
```

Use the actual served ID in both steps 4 and 5. You can add `--engine-version`
with your installed serving version. Record any model-specific request options
with `--extra-body-file` as described in [RUNNER_GUIDE.md](RUNNER_GUIDE.md).
Extra sampling or thinking settings may restrict comparability; unknown settings
are never filled from a model name. The pinned policy requests temperature 0,
1,024 output tokens and no explicit seed. An accepted request does not prove how
the server applied its settings.

Keep `pipeline.json`, `*.progress.jsonl`, attempt/status logs and final prediction
files. Repeat the **same** command to resume after interruption; retained failed
rows remain failures until retried successfully. Changed inputs, model, endpoint,
decoding or provenance require a new run directory. Inspect finish reasons,
truncation and coverage rather than treating API success as task success.

## 6. Measure responses and build the local report

If sharing a GPU, stop your own target-model server before measurement. In the
evaluation environment, install CUDA-compatible Torch for your machine and the
classifier extras. See the [measured B200 installation](../README.md#install)
and [GPU validation conditions](GPU_VALIDATION_RESULTS.md) before choosing builds.

```bash
python -m pip install -e ".[classifiers]"
python -m pip check
koevd-pipeline --stage classify --output-dir runs/my-model-core \
  --safety-adapter downloads/KoEVD-assistant-safety --safety-base downloads/Qwen3.5-0.8B \
  --strategy-adapter downloads/KoEVD-response-strategy --strategy-base downloads/Qwen3-8B \
  --batch-size 2 --classifier-dtype float32 \
  --measurement-order original --measurement-mode batch --trace-measurements
koevd-pipeline --stage report --output-dir runs/my-model-core
```

The classifiers run sequentially in separate processes. Float32 can require
substantial GPU memory, particularly for the 8B base. If you need another dtype
or batch size, record it explicitly and inspect the resulting compatibility
restrictions. Completed Task 3/4 measurements are validated and reused on the same command.
Each new attempt writes into `measurement_attempts/`; partial outputs and traces
are retained. After Task 3 succeeds and Task 4 fails, repeat the same classify
command: Task 3 is reused and only Task 4 runs again. If Task 4 ran out of memory,
retry it alone with a smaller batch (its actual condition remains recorded):

```bash
koevd-pipeline --stage classify --output-dir runs/my-model-core \
  --measurement-tasks 4 --batch-size 1 --classifier-dtype float32 \
  --strategy-adapter downloads/KoEVD-response-strategy --strategy-base downloads/Qwen3-8B \
  --measurement-order original --measurement-mode batch --trace-measurements
```

To intentionally replace successful measurements, add `--remeasure` and select
`--measurement-tasks 3`, `4` or `3 4`; previous files remain in the attempt folder.
Changed settings without that explicit option are rejected. An integrity error
requires investigating retained files; do not edit hashes or delete traces to
force export. Keep the full run directory until validation is complete.

Trace sidecars preserve observed runtime evidence locally; requested
dtype alone does not prove arithmetic precision. They do not establish accuracy.

Open `runs/my-model-core/report/report.html`. This historical report is useful
locally; step 7 also creates the interactive diagnostic report used by the app.
Both reports preserve failures and missing measurements. Task 3 safety and Task 4
strategy labels are measurement proxies; inspect response cases and coverage.

## 7. Export the file for the Platform

`koevd-pipeline --stage all` ends at the local report. **Export is a separate step.**
Use the same index from step 3; do not rebuild it with the local `index` command.

```bash
koevd-results export --run-dir runs/my-model-core \
  --trusted-index runs/my-model-core/trusted_input_index.json \
  --output runs/my-model-core/results.json --code-revision "$(git rev-parse HEAD)"
koevd-results validate --input runs/my-model-core/results.json \
  --trusted-index runs/my-model-core/trusted_input_index.json \
  --registry configs/protocols --protocol-id koevd-core-canonical-v1
koevd-diagnose --input runs/my-model-core/results.json \
  --trusted-index runs/my-model-core/trusted_input_index.json \
  --output-dir runs/my-model-core/diagnostics
```

Export requires all expected generation rows, including explicit failed requests.
Absent classifier output is represented as unmeasured, not safe. Existing stale
measurement output causes an error rather than being silently omitted.
Open `diagnostics/report-v2.html` to inspect charts, groups and response cases.

| File | Purpose | Upload to Platform? |
|---|---|---|
| `results.json` | Full portable run with original responses and measurement labels | **Yes** |
| `trusted_input_index.json` | Independent input/gold/metadata contract | No |
| `profile.json` / `profile-v2.json` | Computed report data | No |
| `report.html` / `report-v2.html` | Readable local reports | No |
| Public numerical JSON/CSV | Shared metrics without original responses | No |

Inspect permission and private content before uploading. For transport you can
select the original `.json` directly: supported browsers compress it automatically.
A lossless `.json.gz` copy is also accepted. Neither changes the expanded 128 MiB
limit. Do not upload ZIP files or rename a profile JSON to `results.json`.

## 8. Sign in, upload and save a private registration

The home view starts with the public leaderboard. **Submit results** opens the
upload/registration view; **Model leaderboard** returns to comparisons. Switching
between these two views preserves this page's temporary uploads. Reloading or
opening a different tab still creates a different temporary page session.

1. On the leaderboard home, choose **Submit results**, then open the [submission workspace in its own tab](https://keti-nlp-koevd-platform.hf.space/submit)
   **before uploading**. The embedded HF view and its standalone tab can have
   different temporary sessions and cookies. Moving tabs later requires reupload.
2. Before the upload section, choose **Sign in to save results**, complete native
   HF sign-in, return to the workspace and **Check account sign-in**.
3. Choose `runs/my-model-core/results.json`, then **Validate and add results**.
   Upload validation does not publish or permanently register anything.
4. Follow **Continue to registration**. The validated result appears automatically
   in **Choose whether to register a result**. Select it and review/confirm its original
   model, revision, generation and measurement declaration.
5. Enter a display name and optional description, then **Save private submission**.
   Keep the submission ID. A display name is a label; it does not change the
   original model identity. Download the private original/history if needed.

You may instead upload without signing in for temporary analysis only. Select
your upload plus a configured reference, then **Build analysis and comparison**
to inspect private cases. Session data expires after two hours; reloading loses
the page's temporary access token. Saving a registration preserves a separate
private original and history. To analyze a saved private original in a new
session, download it from your registration and upload it again.

## 9. Share numerical metrics and compare models

Saving privately does not add an entry to the public model list. On your saved
registration enter a brief **Reason for this action or revision**, choose
**Metrics summary only**, provide the separate required **Permission statement**,
accept the sharing notice and **Publish numerical summary**.
Original responses stay private. Independent permission review is available only
when the operator has configured a publication administrator. With that route
disabled, **Request publication review** is hidden and the server rejects new
requests; numerical sharing remains available. An old pending request can be
cancelled with **Cancel review request** before continuing numerical sharing.

Your published summary can now appear on the **Model leaderboard** home, its metric table
and the two selectors in **Compare models**. Choose your run and a Qwen reference,
then **Compare selected runs**. You can also choose **Compare this result** on your registration to open a comparison with another published run. Inspect input overlap, jointly valid coverage,
evaluation groups and settings before interpreting a delta. Numerical comparison
works without publishing response text. For private case analysis, use your
temporary uploaded run and the permitted configured reference instead.

There is no aggregate ethics score. Official ranks are disabled; sorting observed
values changes display order only. Task 4 distributions are descriptive. Task 3/4
remain measurement-limited even after a successful GPU run. Zero and N/A mean
different things; always read numerators, denominators and coverage. Metadata
groups with overlapping topics must not be summed as disjoint populations.

Download public profiles/comparisons as JSON, JSONL, CSV, Markdown or HTML.
These numerical snapshots omit prompts, responses and private history.
**Stop sharing** removes current public access while retaining the private
original and history. You can publish again from that same registration after
entering a fresh reason, permission statement and consent. For an older
withdrawn registration, choose **Restore private draft** first; restoration never
publishes anything by itself. Neither action can recall downloaded copies. See [data handling and limits](PLATFORM_USER_GUIDE.md#data-handling-and-limits).

## Troubleshooting and completion check

| Symptom | Next step |
|---|---|
| Classifier failed or the GPU ran out of memory | Repeat the classify command; completed tasks are checked and reused. For a smaller Task 4 batch use the task-specific retry above. Keep attempts/traces. |
| Measurement settings changed | Use the original settings to resume, or explicitly select tasks with `--remeasure` to replace completed measurements. |
| Preflight HTTP 400 / context too long | Run the full local tokenizer budget check; inspect actual server context/template and request options. Use a new run if generation settings change. |
| Review request pending on a service without reviewers | Cancel the request, then choose numerical summary sharing. No approval is inferred from cancellation. |
| Stopped/withdrawn model no longer appears | Select the saved registration. Restore its private draft if needed, then publish numerical metrics with fresh consent. Do not create a duplicate original. |
| `unknown_inputs` at upload | Check that step 3 used `protocol-index` and step 7 used that exact index. Arbitrary custom indexes/counts do not establish identity. Do not edit hashes; regenerate/reexport from the correct inputs. |
| Settings differ / measurement is unknown | Inspect the declaration and compatibility reasons. Do not fill unknown values with guessed defaults. |
| Validated upload is absent from registration | In the updated UI it appears automatically. Use **Refresh uploaded results** if the list needs refreshing. Check service/source versions if behavior differs. |
| Not signed in after opening a new tab | Use the standalone workspace and check sign-in there before reuploading. CLI login is unrelated. |
| Home or sign-in configuration could not load | Use **Retry service connection**. Navigation and retries preserve current-page uploads. If the outcome of a prior save is unknown, inspect the registration/history before saving again. |
| Published results cannot be checked | Public list/profile/comparison GETs retry at most twice for transient failures. Wait, then use the relevant Refresh button; this is not a file rejection. No old public data is used after a failed current-state check. |
| Save/share has an ambiguous outcome | Check your registration and history before repeating. The UI does not automatically replay write requests. |
| My saved model is absent from public comparison | Private save and summary publication are separate; confirm sharing completed and was not withdrawn. |
| New session cannot access earlier temporary files | Reupload your retained original; permanent registrations are available after sign-in. |

A complete first run leaves you with the source commit, actual serving settings,
prepared inputs/index, generation/measurement logs, `results.json`, a readable
local diagnostic report and a private submission ID. Optional numerical sharing
adds a public profile that can be compared with compatible published runs.
