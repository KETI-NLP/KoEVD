# KoEVD evaluation and analysis

Reference software for **KoEVD: A Korean Benchmark for Metadata-Conditioned Multi-Stage LLM Safety Evaluation**.

## Install

```bash
python -m pip install -e .
# Optional downloads, plots, or classifier inference:
python -m pip install -e ".[hub,analysis]"
python -m pip install -e ".[classifiers,serve]"
```

The core CLI uses Python's standard library. Classifier dependencies are loaded only when needed. No base model or adapter weights are stored in this GitHub repository. The dependency lower bounds are compatibility requirements, not a reconstruction of the original experiment environment; see docs/REPRODUCIBILITY.md.

## Data and models

Data and two LoRA adapters are publicly available on Hugging Face: [dataset](https://huggingface.co/datasets/KETI-NLP/KoEVD), [assistant safety](https://huggingface.co/KETI-NLP/KoEVD-assistant-safety), and [response strategy](https://huggingface.co/KETI-NLP/KoEVD-response-strategy). Download the pinned release commits:

```bash
koevd-download --repo-id KETI-NLP/KoEVD --revision f5920837769bea77e072c8e033e5ad9cbff4d45d --repo-type dataset --local-dir downloads/KoEVD
koevd-download --repo-id KETI-NLP/KoEVD-assistant-safety --revision e821f2a0d8809bafe0cbf1b6ee0ac8350d2554b3 --repo-type model --local-dir downloads/KoEVD-assistant-safety
koevd-download --repo-id KETI-NLP/KoEVD-response-strategy --revision 846df8d29758b956c420e0f4dd17ced8630a9b81 --repo-type model --local-dir downloads/KoEVD-response-strategy
```

## Evaluate

```bash
koevd-prepare --task 1 --corpus downloads/KoEVD/full_eval/koevd_full_eval.jsonl --split downloads/KoEVD/benchmark_splits/core.jsonl --output runs/task1.jsonl
koevd-prepare --task 3 --corpus downloads/KoEVD/full_eval/koevd_full_eval.jsonl --split downloads/KoEVD/benchmark_splits/core.jsonl --output runs/task3.jsonl
koevd-run --input runs/task1.jsonl --output runs/task1_predictions.jsonl --base-url http://localhost:8000/v1 --model MODEL_ID --max-tokens 512
koevd-score --task 1 --input runs/task1_predictions.jsonl --output runs/task1_metrics.json
```

Task 2 and Task 5 model-facing JSONL are already supplied by the dataset. Pass those files directly to `koevd-run`, then score with task 2 or 5. For remote providers, set the environment variable selected by `--api-key-env`. Secrets are never CLI arguments. The runner only sends chat requests; it never executes Task 5 tools. Running remote APIs may incur provider charges.

```bash
koevd-classify --task 3 --input runs/task3_predictions.jsonl --output runs/task3_safety.jsonl --adapter-path downloads/KoEVD-assistant-safety
koevd-classify --task 4 --input runs/task3_predictions.jsonl --output runs/task3_strategies.jsonl --adapter-path downloads/KoEVD-response-strategy
koevd-score --task 3 --input runs/task3_safety.jsonl
koevd-score --task 4 --input runs/task3_strategies.jsonl
```

The classifier requires successful nonempty generations (`api_status: ok`), preserving failed generation rows in the denominator. Use `--local-files-only` with a local base-model path for offline inference.

## Analyze

```bash
koevd-analyze stats --corpus downloads/KoEVD/full_eval/koevd_full_eval.jsonl --output generated/corpus_stats.json
koevd-analyze groups --task 1 --input runs/task1_predictions.jsonl --group-by evaluated_model metadata.severity_band --output generated/task1_by_model_severity.json
koevd-analyze overlap --task3 runs/task3_safety.jsonl --task5 runs/task5_predictions.jsonl --output generated/task3_task5.json
python analysis/plot_paper_tables.py --output-dir generated/figures
```

Group analysis keeps every prompted row in each group's applicable denominator. Task 4 uses distinct strategy-label inclusion. The overlap analysis joins on source and model and retains each framing and unparsed Task 5 rows. It does not turn a pooled share into evidence of individual vulnerability. Paper aggregate CSVs can generate diagnostic figures without private model outputs; this does not reproduce all API experiments or exact original image pixels.

See [metric definitions](docs/METRICS.md), [reproducibility scope](docs/REPRODUCIBILITY.md), [release map](docs/RELEASE.md), and [changes from the review software](CHANGELOG.md).

## Tests and terms

GPU inference has not yet been verified for this publication package. See [GPU validation](docs/GPU_VALIDATION.md) for a pinned-download smoke test, result collection, and the distinction from reproducing the paper's performance.

```bash
python -m unittest discover -s tests -v
```

The reference evaluation software uses the existing Apache-2.0 license. Copied classifier wrappers retain their original research-use terms under LICENSES/classifier-research-use.md; see NOTICE.md. Dataset and model weights have separate research-use terms. Metadata labels are operational labels under the project guidelines. Models are measurement proxies; Task 4 is descriptive and Task 5 measures mock action selection before execution.
