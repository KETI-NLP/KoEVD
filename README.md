# KoEVD evaluation and analysis

**Evaluation client: v0.3.0-rc.23 (package 0.3.0rc23).** Evaluate your own model, export
portable JSON, build offline reports, and register results in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Anonymous visitors start with the 12-model historical paper leaderboard. Each
paper model supports direct Task 3 type/topic/input-severity/explicitness views,
exact condition filters, completion-aware cards, cross heatmaps and model differences from its original
predictions; see the
[archived-data guide](docs/PAPER_TASK3_TYPE_AGGREGATION.md). Search
across paper and registered collections, or switch conditions for the two full
Qwen3 references, model profiles, metadata trends and paired comparisons without
uploading a file. Current source
opens with a task-specific **Model leaderboard** and a separate **Submit results**
view. Use the [runtime acceptance record](docs/PUBLIC_SERVICE_ACCEPTANCE.md) to
check whether a source correction has reached the hosted app.

Sign in with Hugging Face to preserve a private original, give the run a display
name, and optionally share its numerical summary. Uploading alone stays temporary.
Summary sharing does not publish original responses or grant an official rank.

Actual public acceptance on 2026-10-15 passed the full 17,670-record gzip upload,
registration, rename, summary sharing/withdrawal, native re-login after server
restart, exact original/history preservation, 94 metric rows and 15 numerical
downloads. The public app uses CPU Basic and one replica. This is research-service
acceptance, with no new inference or classifier-accuracy claim. Prior beta and
failed activation evidence retain their dated scope.

Start with the **[complete first-user guide](docs/GETTING_STARTED.md)**: pinned
inputs → model generation → measurement → `results.json` → sign-in → private
registration → optional shared numerical comparison. The guide includes failed
generation/measurement retries, service reconnection, cross-group model discovery,
metric interpretation, latest-export checks, local prompt-budget checks, review-request cancellation and
reversible summary sharing. Use
[Platform controls and data handling](docs/PLATFORM_USER_GUIDE.md) as a reference.
See [current acceptance and source/runtime versions](docs/PUBLIC_SERVICE_ACCEPTANCE.md),
[deployment and recovery](docs/REGISTERED_SPACE_GUIDE.md),
[public profile definitions](docs/PUBLIC_PROFILES_GUIDE.md), and
[numerical report formats](docs/PUBLIC_NUMERICAL_REPORT_GUIDE.md).

Reference software for **KoEVD: A Korean Benchmark for Metadata-Conditioned Multi-Stage LLM Safety Evaluation**.

**Static analysis candidate:** A browser-only option runs the same Python
validation/analysis engine through Pyodide. Select results JSON, compare runs and
download the offline report without sending your files to a server. See the
[Static candidate guide](docs/STATIC_SPACES_GUIDE.md). The public
[KoEVD Explorer preview](https://huggingface.co/spaces/KETI-NLP/KoEVD-Explorer)
provides personal analysis. Shared submission/storage and official ranking remain
separate, and the platform beta is released separately from the historical paper software.

**GPU status:** Both classifiers and offline classify→score passed on NVIDIA B200 with the published code unchanged. See [tested conditions and results](docs/GPU_VALIDATION_RESULTS.md); this is an operational smoke test, not held-out F1 reproduction.

**Evaluate your own model:** The 0.2.0 `koevd-pipeline` (prepare → generate → classify → report) completed live Qwen3-8B evaluation on B200 without source changes: 40 smoke and 959 expanded generation requests. See the [complete guide](docs/OWN_MODEL_GUIDE.md) and [live validation findings](docs/PIPELINE_VALIDATION_RESULTS.md). **Measurement limits remain:** strategy outputs differed at batch 2/4 in 5/191 cases; all-safe Task 3 labels included concerning outputs on qualitative review. Execution success does not establish measurement accuracy or target-model safety.

## Choose a workflow

- **Evaluate and register your own model:** follow [GETTING_STARTED.md](docs/GETTING_STARTED.md)
  from a new run directory. Use `protocol-index`, then export with that same index.
- **Explore without GPU or uploads:** open the [public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
- **Run custom local diagnostics or reproduce historical components:** use the
  component commands below. Their input selection is separate from the registered
  full protocol; arbitrary local indexes are not accepted by the service.

## Install

Start from a clone in a fresh environment (Linux shell example):

```bash
git clone https://github.com/KETI-NLP/KoEVD.git
cd KoEVD
python3.11 -m venv .venv
source .venv/bin/activate
```

For the current registered workflow, keep the current source and follow
[GETTING_STARTED.md](docs/GETTING_STARTED.md). The standalone commands below are
component examples, not the full registered workflow. For the historical code
exercised on B200, check out `9aa38fa6d811fc61e26496d05e70abca17ec11f9` before installation. To use the new own-model pipeline, install the current source on `main` and record its commit; the pipeline is not in the old `v0.1.0` tag. Install the components needed for your use:

```bash
python -m pip install -e .
# Optional downloads, plots, or classifier inference:
python -m pip install -e ".[hub,analysis]"
python -m pip install -e ".[classifiers,serve]"
```

For the measured B200 environment, install CUDA-compatible PyTorch first and pin the tested classifier dependencies:

```bash
python -m pip install torch==2.9.1 --index-url https://download.pytorch.org/whl/cu130
python -m pip install ".[classifiers,analysis]" "transformers==5.8.1" "peft==0.18.0" datasets
python -m pip check
```

This CUDA 13.0 recipe was tested with driver 580.178.04; select an appropriate PyTorch build for a different driver. Core scoring does not require CUDA. The core CLI uses Python's standard library. Classifier dependencies are loaded only when needed. No base model or adapter weights are stored in this GitHub repository. The dependency lower bounds are compatibility requirements, not a reconstruction of the original experiment environment; see docs/REPRODUCIBILITY.md.

## Data and models

Data and two LoRA adapters are publicly available on Hugging Face: [dataset](https://huggingface.co/datasets/KETI-NLP/KoEVD), [assistant safety](https://huggingface.co/KETI-NLP/KoEVD-assistant-safety), and [response strategy](https://huggingface.co/KETI-NLP/KoEVD-response-strategy). Download the pinned release commits:

```bash
koevd-download --repo-id KETI-NLP/KoEVD --revision f5920837769bea77e072c8e033e5ad9cbff4d45d --repo-type dataset --local-dir downloads/KoEVD
koevd-download --repo-id KETI-NLP/KoEVD-assistant-safety --revision e821f2a0d8809bafe0cbf1b6ee0ac8350d2554b3 --repo-type model --local-dir downloads/KoEVD-assistant-safety
koevd-download --repo-id KETI-NLP/KoEVD-response-strategy --revision 846df8d29758b956c420e0f4dd17ced8630a9b81 --repo-type model --local-dir downloads/KoEVD-response-strategy
```

The adapters also require their separately distributed base-model weights. Download the GPU-tested base commits before running the classifier examples:

```bash
koevd-download --repo-id Qwen/Qwen3.5-0.8B --revision 2fc06364715b967f1860aea9cf38778875588b17 --repo-type model --local-dir downloads/Qwen3.5-0.8B
koevd-download --repo-id Qwen/Qwen3-8B --revision b968826d9c46dd6066d109eabc6255188de91218 --repo-type model --local-dir downloads/Qwen3-8B
```

## Evaluate

```bash
koevd-prepare --task 1 --corpus downloads/KoEVD/full_eval/koevd_full_eval.jsonl --split downloads/KoEVD/benchmark_splits/core.jsonl --output runs/task1.jsonl
koevd-prepare --task 3 --corpus downloads/KoEVD/full_eval/koevd_full_eval.jsonl --split downloads/KoEVD/benchmark_splits/core.jsonl --output runs/task3.jsonl
koevd-run --input runs/task1.jsonl --output runs/task1_predictions.jsonl --base-url http://localhost:8000/v1 --model MODEL_ID --max-tokens 512
koevd-score --task 1 --input runs/task1_predictions.jsonl --output runs/task1_metrics.json
koevd-run --input runs/task3.jsonl --output runs/task3_predictions.jsonl --base-url http://localhost:8000/v1 --model MODEL_ID --max-tokens 512
```

The `koevd-run` examples require an available endpoint and its actual `MODEL_ID`. The earlier candidate-based B200 test used existing corpus responses. The subsequent [live pipeline test](docs/PIPELINE_VALIDATION_RESULTS.md) exercised real Qwen3-8B generation and documented its measurement limitations.

Task 2 and Task 5 model-facing JSONL are already supplied by the dataset. Pass those files directly to `koevd-run`, then score with task 2 or 5. For remote providers, set the environment variable selected by `--api-key-env`. Secrets are never CLI arguments. The runner only sends chat requests; it never executes Task 5 tools. Running remote APIs may incur provider charges.

```bash
koevd-classify --task 3 --input runs/task3_predictions.jsonl --output runs/task3_safety.jsonl --adapter-path downloads/KoEVD-assistant-safety --base-model-name-or-path downloads/Qwen3.5-0.8B --local-files-only --batch-size 2
koevd-classify --task 4 --input runs/task3_predictions.jsonl --output runs/task3_strategies.jsonl --adapter-path downloads/KoEVD-response-strategy --base-model-name-or-path downloads/Qwen3-8B --local-files-only --batch-size 2
koevd-score --task 3 --input runs/task3_safety.jsonl
koevd-score --task 4 --input runs/task3_strategies.jsonl
```

For revision-pinned offline inference, also download the two base-model commits in `gpu_release_lock.json`, pass their local snapshots through `--base-model-name-or-path`, and use `--local-files-only`. See [the full procedure](docs/GPU_VALIDATION.md). The current classify CLI accepts `--torch-dtype auto|float16|bfloat16|float32`; without that option it keeps the wrapper's default settings. Device placement uses the wrapper's automatic mapping. `--trace-output` records the observed measurement runtime, so a requested dtype must not be assumed to describe every parameter or operation. See [measurement traces](docs/MEASUREMENT_TRACE_GUIDE.md) and [the GPU audit findings](docs/GPU_MEASUREMENT_MATRIX_RESULTS.md).

The classifier requires successful nonempty generations (`api_status: ok`), preserving failed generation rows in the denominator. Use `--local-files-only` with a local base-model path for offline inference.

## Analyze

For a complete report from your own results, follow [OWN_MODEL_GUIDE.md](docs/OWN_MODEL_GUIDE.md). The commands below are also available as individual analysis operations. `analysis/plot_paper_tables.py` plots the supplied paper aggregates; use the new report's `groups.csv` and `strategies.csv` for your own model's figures.

```bash
koevd-analyze stats --corpus downloads/KoEVD/full_eval/koevd_full_eval.jsonl --output generated/corpus_stats.json
koevd-analyze groups --task 1 --input runs/task1_predictions.jsonl --group-by evaluated_model metadata.severity_band --output generated/task1_by_model_severity.json
koevd-analyze overlap --task3 runs/task3_safety.jsonl --task5 runs/task5_predictions.jsonl --output generated/task3_task5.json
python analysis/plot_paper_tables.py --output-dir generated/figures
```

Group analysis keeps every prompted row in each group's applicable denominator. Task 4 uses distinct strategy-label inclusion. The overlap analysis joins on source and model and retains each framing and unparsed Task 5 rows. It does not turn a pooled share into evidence of individual vulnerability. Paper aggregate CSVs can generate diagnostic figures without private model outputs; this does not reproduce all API experiments or exact original image pixels.

The classifier API returns a wrapper object whose `result` becomes the CLI row’s `measurement`. See [output fields and actual examples](docs/CLASSIFIER_OUTPUTS.md) and the [strategy code/display-label crosswalk](docs/STRATEGY_LABELS.md).

See [metric definitions](docs/METRICS.md), [reproducibility scope](docs/REPRODUCIBILITY.md), [release map](docs/RELEASE.md), and [changes from the review software](CHANGELOG.md).

## Tests and terms

### Evaluation platform development checkout

The local development candidate supports portable results JSON, interactive
offline diagnostics, a private upload/comparison app, and opt-in submission
history with metric-specific candidate comparisons. Start with
[the own-model guide](docs/OWN_MODEL_GUIDE.md),
[result format](docs/RESULT_FORMAT.md),
[interactive diagnostics](docs/DIAGNOSTICS_GUIDE.md) and
[the app guide](docs/SPACES_GUIDE.md). These additions are provided in the platform beta; shared production submission
and official ranking are separate. The old v0.1.0 tag does not contain them.

The subsequent full registered Qwen3-8B and Qwen3-4B runs completed15,011
generation requests and17,670 portable records per model. Both raw reexports
match the independently checked results. Node, local CLI and native HTTP analysis
profiles agree, and the actual35,340-record comparison HTML passed browser checks.
See [full two-model evidence](docs/validation/platform_m4_m5_full_two_actual_20261009.json)
and [the release checklist](docs/PLATFORM_RELEASE_CANDIDATE.md) for current
acceptance evidence and the separate production conditions. Full-size private HF
analysis and actual b200-1 Docker analysis passed with all five report formats
matching the independent CLI. Research-reference permission for both results is
recorded in a [separate local candidate](docs/ACTUAL_REFERENCE_CANDIDATE.md).

The earlier Qwen3-8B and Qwen3-4B pipelines passed on B300 using a custom prefix96
integration subset, with 959 API-ok generations and 1150 exported records per
model. Local app, CLI and node analysis profiles agree. See
[expanded GPU evidence](docs/validation/platform_m4_gpu_expanded_20261008.json).
This does not reproduce held-out F1 or establish classifier accuracy. Safety
and strategy measurements remain limited and excluded from official ranks;
Task4 frequencies are descriptive. The organization Team plan enabled the
private CPU development Space; native HF login, private draft saving and bounded
backup/fixed restore have been tested. Its default disk remains ephemeral and
continuous backup is off. The initial HTTP402 attempt is historical. The shared production registration service is now active; see
[current public acceptance](docs/PUBLIC_SERVICE_ACCEPTANCE.md). Official ranking
remains disabled. Earlier development gates above describe their dated scope.

B200 GPU inference and offline CLI validation passed on the fixed 12/96-candidate samples. See [GPU validation](docs/GPU_VALIDATION.md) for a pinned-download smoke test, result collection, and the distinction from reproducing the paper's performance.

```bash
python -m unittest discover -s tests -v
```

The reference evaluation software uses the existing Apache-2.0 license. Copied classifier wrappers retain their original research-use terms under LICENSES/classifier-research-use.md; see NOTICE.md. Dataset and model weights have separate research-use terms. Metadata labels are operational labels under the project guidelines. Models are measurement proxies; Task 4 is descriptive and Task 5 measures mock action selection before execution.

## Paper reproduction clarification

See [the camera-ready reproduction notes](docs/REPRODUCIBILITY.md#camera-ready-reproducibility-clarification--2026-09-15) for the separate 532-input safety reproduction, unresolved new-response measurement limits, exact Task 2 contracts, and [historical Task 1 metadata overlay](reproduction/task1_metadata_v1/README.md). The overlay preserves canonical data and makes the paper-specific grouping explicit.

See [the camera-ready supplement and pinned documentation revisions](docs/CAMERA_READY_RELEASE.md) for the historical Task 1 view and latest reproduction evidence.

### Analyze strategies and simulated choices

Task 4/5 now support exact input-condition filters and synchronized model comparison
for the 12 archived paper models and current-protocol registrations. Focus a strategy,
inspect directional co-inclusion, compare framing-specific outcome distributions,
and relate Task 3 response labels to Task 5 simulated choices.
Read the [task analysis guide](docs/TASK_ANALYSIS_GUIDE.md) for denominators,
completion, historical parsing differences and interpretation limits.
