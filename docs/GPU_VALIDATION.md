# Validation on a GPU node

The release has passed CPU packaging/data checks. Actual classifier inference remains unverified until a GPU report is collected. Use a pinned public commit for the first remote smoke test, fix any failures, then run a larger evaluation. A smoke-test pass does not reproduce the paper's reported F1.

## Install and pin artifacts

On the GPU node, use a fresh Python environment with a CUDA-compatible PyTorch installation. Install this repository at an explicit Git commit and run:

```bash
python -m pip install '.[classifiers]'
python -m unittest discover -s tests -v
git rev-parse HEAD
```

Record the Git commit with the result bundle. The included `gpu_release_lock.json` pins the published dataset, adapters and two upstream base models to full 40-character commit SHAs. Use it unchanged for the first test. For a different release, use `scripts/gpu_release_lock.example.json` and explicitly fill every revision. No `main` or floating tag is accepted. The base-model commits selected for this test describe this run; they cannot retroactively recover missing revisions from the original experiment.

The script downloads the dataset, both adapters and both base models into the standard Hugging Face cache. Reserve storage for those complete repositories. It runs one classifier at a time on the first visible CUDA GPU, without CPU offloading or quantization. The GPU must hold the 8B model, adapter and inference activations; actual peak allocation is reported. Start with four sources and batch size two; BF16 is the default. Unsupported BF16 hardware requires an explicit `--dtype float16`, recorded as a different test condition. Set `CUDA_VISIBLE_DEVICES` before starting to choose a GPU.

## Run

```bash
python scripts/gpu_smoke.py --lock gpu_release_lock.json --output runs/gpu-smoke-001 --sources 4 --batch-size 2
```

Use a new output directory for each run. Exit code 0 plus `status: passed` in `summary.json` means the smoke checks passed. A failed import, model-load/inference error, empty/unparsed output, single/batch label disagreement, or denominator mismatch requires review. Single/batch differences can result from numerical effects and do not alone prove a parser bug.

Checks include pinned downloads, SHA-256 verification of published artifact manifests, loading both adapters, single and batch inference on the first candidate of each available tier for the selected sources, output parsing, and Task 3/4 scoring with a missing-measurement row retained in the denominator. Candidate content is not printed or copied into the result bundle. GPU model wrappers are exercised directly; remote provider APIs and every CLI combination are outside this smoke test.

Return the entire result directory, the lock file and the Git commit. The report includes dependency versions, GPU/CUDA details, script and corpus hashes, sample IDs, raw classifier outputs, parsed results, metrics, elapsed times, peak allocated GPU memory, and failure tracebacks. These allow analysis of missing outputs, batching changes, environment mismatches and loading failures. On failure, the second classifier is still attempted where possible.

## Interpret and extend

This sample is deterministic and small. It is not held out from classifier training and has no representative performance claim. The test checks operation, not a target accuracy threshold. The saved outputs support manual diagnosis but must not be presented as a new held-out F1.

Once the smoke test passes, run a broader fixed benchmark or the original authorized source-disjoint validation set on the GPU node. Compare labels and metrics with the original results only when examples, prompts, parser, denominator, model revision and precision are aligned. Keep FP32-versus-review-FP16 experiments separate. The original held-out training/validation materials are not part of the public dataset package.

For a CPU-only check of case selection and report writing:

```bash
python scripts/gpu_smoke.py --prepare-only downloads/KoEVD/full_eval/koevd_full_eval.jsonl --output runs/prepare-only
```

This deliberately reports `prepared_only_gpu_not_tested` and does not validate model loading or inference.
