# B200 publication-package validation — 2026-09-14

Both classifiers passed actual GPU inference with the unmodified published code at `9aa38fa6d811fc61e26496d05e70abca17ec11f9`. The test used the revisions in [gpu_release_lock.json](../gpu_release_lock.json). The 12-candidate baseline is a subset of the 96-candidate expanded sample; they are not 108 independent examples. Candidates were the first available response from each tier for the first 4 or 32 source records.

For both models, single-example and batch-size-2/4 outputs had zero parsing failures, missing/duplicate IDs, raw-string differences, or final label/set differences on the tested comparisons. The actual offline classify→score CLI used the same 12 candidates plus two excluded rows: Task 3 `prompted=14`, Task 4 `generated_responses=14`, and both `classified=12`. Failed/empty generation rows retained null measurements and exclusion reasons. These were existing public candidates, not new LLM-generated benchmark responses.

## Tested environment

Ubuntu 22.04.5; NVIDIA B200; driver 580.178.04; Python 3.11.14; PyTorch 2.9.1+cu130; Transformers 5.8.1; PEFT 0.18.0; Accelerate 1.15.0; huggingface-hub 1.31.0; datasets 5.0.1. Both models were on `cuda:0`, without CPU offload or quantization. BF16 was requested, while actual parameters included both BF16 and FP32 (including FP32 LoRA parameters).

| Run | Model | Candidates | Batch size | Load seconds | Total seconds | Peak allocated GiB |
|---|---|---:|---:|---:|---:|---:|
| baseline_online_smoke_4 | assistant | 12 | 2 | 10.12 | 14.48 | 1.536 |
| baseline_online_smoke_4 | strategy | 12 | 2 | 6.56 | 28.32 | 17.583 |
| expanded_smoke_32 | assistant | 96 | 2 | 10.09 | 34.02 | 1.536 |
| expanded_smoke_32 | strategy | 96 | 2 | 6.61 | 102.31 | 17.584 |
| batch4_comparison | assistant | 96 | 4 | 8.12 | 23.93 | 1.645 |
| batch4_comparison | strategy | 96 | 4 | 4.37 | 79.87 | 17.583 |

Memory is `torch.cuda.max_memory_allocated()` after a per-model reset: peak active tensor allocation in this process. It is not total GPU usage, reserved memory, or a minimum VRAM requirement. Total time includes load, all single-example predictions, all batch predictions, and result saving; it excludes downloads and the other model. Cache state affects load time. These observations are not latency guarantees.

## Initial cache failure and successful recovery

The first offline attempt failed before sample selection because files cached with huggingface-hub 1.15.0 lacked tree metadata required by 1.31.0. The same code and fixed revisions passed after network access was allowed to populate metadata. The identical snapshot calls then succeeded offline. The actual classify CLI separately passed with local snapshot paths, `--local-files-only`, and `HF_HUB_OFFLINE=1`.

Prefetch pinned snapshots with the Hub version used for the run before taking the node offline. Existing weight files alone do not prove all metadata required by a different Hub version is cached. Do not change model revisions to work around this failure.

Optional Qwen3.5 fast kernels were absent, so the model used the PyTorch fallback. PEFT warned about additional adapter-config keys `lora_ga_config` and `use_bdlora`; both were null in the pinned configuration. These warnings did not cause failure in this test, and no runtime upgrade or code change was made to suppress them.

## Evidence and limits

The received result archive SHA-256 is `9e781bdf8004697abcb9d93399c63e5869f84cfe630b0e0f04add0e366f73150`. All 177 inner file checksums matched. Maintainer-side reanalysis confirmed hashes for 18 installed source files, the smoke script and lock, reparsed the saved raw outputs, recomputed the saved metrics, and compared single/batch/CLI results. A sanitized machine-readable summary is in [validation/b200_20260914.json](validation/b200_20260914.json). Internal node paths and GPU UUIDs are omitted.

CPU tests (19), all 13 dataset configurations, corpus counts, and seven aggregate plot outputs also passed. This validates operation in the stated environment and sample. It does not reproduce original held-out F1, establish full-benchmark accuracy, validate other GPUs/precisions, or establish FP32/FP16 inference equivalence. A live generation endpoint (`koevd-run`) was not exercised.
