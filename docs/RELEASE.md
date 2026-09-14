# Repository map

Current source package: **0.2.0**, with the own-model pipeline and diagnostic reports. The downloadable `v0.1.0` release assets and GPU-tested tag are preserved; install the current source for new pipeline features. See [the guide](OWN_MODEL_GUIDE.md) for scope and verification.

| Repository | Contents |
|---|---|
| GitHub KoEVD | evaluation package, classifier wrappers, tests, analysis, aggregate paper tables |
| HF KoEVD | canonical corpus, source-ID views, Task 2/5 problems, schema, dataset card and terms |
| HF KoEVD-assistant-safety | Qwen3.5-0.8B LoRA adapter, tokenizer, recorded validation |
| HF KoEVD-response-strategy | original FP32 Qwen3-8B adapter; review_fp16/ holds the earlier compact submission |

The publisher is **KETI-NLP**. HF release `v0.1.0` is pinned by `gpu_release_lock.json`; it also records the upstream base-model revisions selected for the new GPU smoke test. These are not retroactive claims about the original experiments. Each repository has a SHA-256 manifest excluding itself and `.git`. B200 GPU inference and offline CLI validation passed; see [the measured scope](GPU_VALIDATION_RESULTS.md). The original `v0.1.0` tags and inference revisions remain unchanged.

| Artifact | Immutable HF commit |
|---|---|
| KoEVD | `f5920837769bea77e072c8e033e5ad9cbff4d45d` |
| KoEVD-assistant-safety | `e821f2a0d8809bafe0cbf1b6ee0ac8350d2554b3` |
| KoEVD-response-strategy | `846df8d29758b956c420e0f4dd17ced8630a9b81` |


HF dataset configurations are declared using the [official manual-configuration format](https://huggingface.co/docs/hub/datasets-manual-configuration). Adapter metadata follows the [official model-card format](https://huggingface.co/docs/hub/model-cards). Publication uses the [Hub upload API](https://huggingface.co/docs/huggingface_hub/guides/upload).
