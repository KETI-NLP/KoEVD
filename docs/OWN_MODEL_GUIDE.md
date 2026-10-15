# Diagnose your own model with KoEVD

The evaluated model is **your model**. The two KoEVD adapters are measurement models that label its generated responses. You can use any model exposed through the supported chat endpoint contract, or import outputs from your own inference code. The pipeline creates a source-linked Task 1–5 profile, not a single safety score.

**To evaluate a model and register it on the public Platform, follow the complete
[GETTING_STARTED.md](GETTING_STARTED.md) guide.** It prepares the registered
input index first and uses it again for export/validation. This page covers
custom local smoke runs, interpretation and importing other inference logs.
Its arbitrary local indexes are not automatically supported by the service.

Use current source and record `git rev-parse HEAD`. Historical 0.2.0 pipeline
evidence is retained in [PIPELINE_VALIDATION_RESULTS.md](PIPELINE_VALIDATION_RESULTS.md);
it is not the source version to select for the current registered workflow.

## What the results tell you

| Stage | Question | Main interpretation |
|---|---|---|
| Task 1 | Does the model recognize risky requests? | Missed unsafe requests and false alarms on benign requests, with confusion counts |
| Task 2 | Can it distinguish candidate response safety? | Choice error/accuracy separately for all four choice variants |
| Task 3 | Does its own response remain safe? | Classifier-measured unsafe generations, with valid-response and all-prompt denominators |
| Task 4 | How does it respond? | Multi-label strategy inclusion by severity, topic, explicitness and utterance type; descriptive, not a quality score |
| Task 5 | Does it choose an unsafe mock action? | Unsafe selection, over-refusal, allowed action selection and missing outputs by all three framings |
| Task 3→5 | Does safe direct generation coexist with unsafe action choice? | Source-matched transitions for the same model, separately by framing |

Groups include severity, explicitness, utterance type, topic, tool risk category, and severity × explicitness. Missing metadata is shown explicitly. Multi-topic memberships overlap and must not be summed.

## Installation and inputs

Clone the current source and install in a fresh environment as in the [README](../README.md). Run `python -m pip install -e .` for the CPU pipeline/report, plus the tested classifier dependencies from the README for the measurement stage. Download the dataset, both adapters and both base models using the README's **fixed revision** commands. The commands below assume those downloads are in `downloads/`.

Serve your model at an endpoint that accepts `POST /v1/chat/completions` with `model`, `messages`, `temperature`, and `max_tokens`, returning `choices[0].message.content`. The runner sends only the prompt messages and generation settings; it does not send the separate `gold` or `metadata` objects. A provider with a different API needs an adapter or the import route below. The pipeline does not start a model server or execute the mock tools.

## Prepare first and inspect the request count

```bash
koevd-pipeline --stage prepare \
  --dataset-dir downloads/KoEVD --split core \
  --limit-sources 4 --output-dir runs/my-model-smoke
```

Read `runs/my-model-smoke/pipeline.json` before generation. It records selected source counts, per-task row counts and input checksums. Task 2 preserves its four variants. Task 5 uses its released main source set and preserves all three framings. `--limit-sources` chooses a deterministic sorted prefix separately from the primary split and the tool set; this is an operational smoke sample, **not a representative estimate**.

The measured 4-source run made 40 generation requests; the 96-source run made 959 because its primary/tool union contained 191 sources. Calculate your own total from the prepared manifest:

```bash
python -c "import json; p=json.load(open('runs/my-model-smoke/pipeline.json')); print(sum(t['rows'] for t in p['inputs'].values()))"
```

Task 3 prepares the **union** of primary-split sources and Task 5 sources so that tool transitions have matching direct generations. `metadata.evaluation_subset` records primary split and/or `task5_overlap`. Task 3's overall number is the union; for a core-only result use the `evaluation_subset=core` group. Task 4 classifies those same generated responses without a second generation call.

## Generate using your model

Replace `YOUR_SERVED_MODEL_ID` and the endpoint with your server's values:

```bash
koevd-pipeline --stage generate --output-dir runs/my-model-smoke \
  --base-url http://localhost:8000/v1 --model YOUR_SERVED_MODEL_ID \
  --temperature 0 --max-tokens 1024
```

For authenticated endpoints, set the environment variable selected by `--api-key-env` (default `OPENAI_API_KEY`). Do not put secrets into flags or run manifests. Generation incurs the endpoint's normal compute/API cost. Match decoding budgets when comparing models; even 1,024 tokens can truncate reasoning-heavy models; inspect finish reasons.

Each response is durably appended to `*.progress.jsonl`. After a task completes it is compacted into a unique-row `taskN_predictions.jsonl`. Rerun the same command to resume successful requests and retry failed requests. Keep progress files after interruption. Changed input, model, endpoint or decoding settings require a new output directory. An API failure and a refusal expressed in a successful response remain different cases.

Inspect the progress/status files and server logs during a long task. Current prediction files retain observed finish reason and usage when the server returns them; older logs may not. The historical live test found nonempty repetitive/length-limited output that still satisfied classification eligibility. API success and task validity remain different checks.

## Measure the generated responses

If your target-model server occupies the same GPU, release its GPU allocation before this stage. Each KoEVD classifier runs in a separate process so one classifier is unloaded before the next loads.

```bash
koevd-pipeline --stage classify --output-dir runs/my-model-smoke \
  --safety-adapter downloads/KoEVD-assistant-safety \
  --safety-base downloads/Qwen3.5-0.8B \
  --strategy-adapter downloads/KoEVD-response-strategy \
  --strategy-base downloads/Qwen3-8B --batch-size 2
```

This stage runs offline from local weights and uses the existing classifier CLI's automatic dtype/device configuration. It hashes local model configuration and weight files for provenance. Failed/empty generations remain rows with null measurements. See [B200 conditions](GPU_VALIDATION_RESULTS.md) for the measured environment; other hardware needs its own verification.

## Build the diagnosis

```bash
koevd-pipeline --stage report --output-dir runs/my-model-smoke
```

Open `runs/my-model-smoke/report/report.html` in a browser. Reports do not need a server, network, GPU or plotting dependencies.

| File | Use |
|---|---|
| `report.html` | Read task summaries and descriptive contrasts; filter metadata groups and see rate bars |
| `report.md` | Share a readable analysis with counts, coverage and transitions |
| `profile.json` | Inspect complete metrics, confusion counts, variants, all groups and paired comparisons |
| `groups.csv` | Plot or further analyze group counts/rates |
| `strategies.csv` | Inspect Task 4 strategy inclusion by metadata group |
| `cases.jsonl` | Review up to 10 event and 10 missing cases per model/task/variant by default |

The pipeline rejects missing prediction rows and stale classifier outputs, rather than reporting a partially completed run as a full evaluation. Standalone reports can intentionally cover only selected tasks.

## Full evaluation in one command

For a registered full run, use [steps 3–7 of the first-user guide](GETTING_STARTED.md#3-prepare-the-registered-full-input-set).
The following is an alternative **local custom** all-in-one run in a new directory;
it does not create the registered input index or portable JSON automatically:

```bash
koevd-pipeline --dataset-dir downloads/KoEVD --split core \
  --output-dir runs/my-model-core \
  --base-url http://localhost:8000/v1 --model YOUR_SERVED_MODEL_ID \
  --temperature 0 --max-tokens 1024 \
  --safety-adapter downloads/KoEVD-assistant-safety \
  --safety-base downloads/Qwen3.5-0.8B \
  --strategy-adapter downloads/KoEVD-response-strategy \
  --strategy-base downloads/Qwen3-8B --batch-size 2
```

The single-command route assumes enough resources for the target server and measurement models. Use the staged route when they share a GPU. Other released split names, such as `hard` or `core_severity_explicitness_balanced_768`, can be passed via `--split`. Hard is an empirically selected stress view; it does not estimate natural prevalence.

## Bring outputs from another inference framework

Use the prepared `taskN_input.jsonl` as the contract. For **every** input row preserve `sample_id`, `task`, `messages`, `metadata`, `source`, and `gold`; add:

```json
{
  "evaluated_model": "my-model@exact-revision",
  "prediction": "the model's assistant content",
  "api_status": "ok"
}
```

For failures retain the row with `prediction: ""`, `api_status: "error"` and optionally `api_error`. Do not put choice labels, classifier labels or reference answers into `prediction` in a real run. Missing rows cannot be inferred by the standalone reporter, so first compare IDs/counts against the prepared input. One generation per source is required for Task 3→5 matching; analyze repeated seeds in separate runs.

Apply the existing `koevd-classify --task 3` and `--task 4` commands to your Task 3 predictions, then:

```bash
koevd-analyze report \
  --task1 my/task1_predictions.jsonl --task2 my/task2_predictions.jsonl \
  --task3 my/task3_safety.jsonl --task4 my/task3_strategies.jsonl \
  --task5 my/task5_predictions.jsonl --output-dir my/report
```

To compare two models, give both files after each `--taskN` argument. Use distinct `evaluated_model` IDs. The report compares only shared IDs with identical prepared inputs and records unmatched or changed-input rows. It preserves per-model coverage and does not silently merge model aliases. Task 3 and Task 4 must contain the same response for a shared sample.

## Read strengths and weaknesses responsibly

`higher_observed_risk` and `lower_observed_risk` compare a group to **remaining sources within the same task variant**. Both sides require at least 20 valid unique sources and 90% diagnostic coverage by default (`--min-sources`, `--min-coverage`). These thresholds are screening rules, not confidence intervals or significance tests. Repeated sources do not satisfy the source threshold. A lower observed rate with adequate coverage is a candidate strength under these conditions; a higher rate identifies cases to investigate.

- Task 1 judgment errors include both missed risks and benign false alarms: inspect the confusion counts.
- Task 3 all-prompt risk can look low because of missing responses: inspect coverage and valid-response risk together.
- Task 4 information-giving/refusal frequencies alone do not establish helpfulness or correctness.
- Task 5 partial JSON may satisfy the historical parser but not a usable action decision. Diagnostic coverage requires a recognized decision, and an available tool when calling one; historical metrics are retained separately.
- Severity, topic and utterance type can be confounded. Group differences do not establish a causal weakness or superiority over other models.
- This pipeline uses classifier proxies. Inspect `cases.jsonl` and conduct human review of important findings. It does not establish production safety or reproduce the paper's held-out classifier F1.

## CPU-only demonstration and verification

```bash
python examples/make_demo_profile.py --output-dir generated/synthetic-demo
python -m unittest discover -s tests -v
```

The demo uses explicitly synthetic predictions for two fictitious models; its values are not research results. Automated integration tests exercise a real local HTTP request through generation, classification CLI glue using CPU test doubles, resume, denominator handling and report generation. The [live B200 run](PIPELINE_VALIDATION_RESULTS.md) separately verified real target-model generation, GPU measurement and reporting. Its batch differences and suspicious safety judgments remain unresolved. Preserve `pipeline.json`, prediction/measurement files, `report/`, environment versions and server/terminal logs when returning a new validation result.


## Portable result JSON (local diagnostic format)

The development checkout adds `koevd-results index/export/validate/report`. Follow [RESULT_FORMAT.md](RESULT_FORMAT.md) to export the existing pipeline as one JSON, validate against a separately trusted prepared-input index, and rescore with the same report engine. It retains failures and unmeasured responses. Private app upload and comparison use this same JSON. Export alone does not publish a result, verify model authenticity or register an official leaderboard result.


## Recorded execution and bounded requests

The development runner adds `koevd-doctor`, optional separate preflight, `--workers`, durable attempt/run/status files, observed response metadata and explicit extra request controls. See [RUNNER_GUIDE.md](RUNNER_GUIDE.md) for commands, retry/resume semantics and interpretation. API success is not parsed task success or a safety label.


## Interactive offline diagnostics and paired comparison

After portable export, run `koevd-diagnose --input results.json
--trusted-index operator-index.json --output-dir diagnostics` on one command line.
Open `diagnostics/report-v2.html` for Task 1–5 charts, metadata groups, quality
flags, full prompt/response cases and method limitations. Repeat `--input` to
compare two full artifacts on identical prepared inputs. The trusted index must
be selected independently; an uploaded index is not an official source.
See [DIAGNOSTICS_GUIDE.md](DIAGNOSTICS_GUIDE.md) for reproducible commands and
source-cluster intervals. The HTML keeps all raw text locally and does not
register a result. Actual Qwen3-8B and Qwen3-4B prefix96 generation, measurement,
export and app/CLI/node parity have passed; see [the scoped evidence](validation/platform_m4_gpu_expanded_20261008.json).
This is a custom integration subset, not full standard evaluation or classifier
accuracy evidence. Current full-run and hosted evidence is listed in
[PUBLIC_SERVICE_ACCEPTANCE.md](PUBLIC_SERVICE_ACCEPTANCE.md).
Generation authenticity and classifier accuracy are separate from execution success. Artificial
demonstrations are not model performance evidence.


## Private upload, registration and comparison

The [public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform) supports
temporary analysis, account-owned private originals, optional numerical sharing,
profiles and paired comparison. Use the [first-user guide](GETTING_STARTED.md)
and [Platform guide](PLATFORM_USER_GUIDE.md). Open the workspace in its own tab
and sign in before uploading if you intend to save a registration. The registered
service has superseded the earlier HTTP402/undeployed status; dated validation
documents preserve that history. Official ranks remain disabled and Task 3/4
remain measurement-limited.

For operator catalog and session configuration, use [SPACES_GUIDE.md](SPACES_GUIDE.md)
and [REGISTERED_SPACE_GUIDE.md](REGISTERED_SPACE_GUIDE.md). Local synthetic demo
references are fictional; they do not replace the actual published Qwen references.
