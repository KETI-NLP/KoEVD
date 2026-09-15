# Camera-ready reproduction supplement — 2026-09-15

KoEVD is accepted to the main conference of AACL-IJCNLP 2026. Proceedings identifiers are pending.

This documentation update adds the [historical Task 1 metadata view](../reproduction/task1_metadata_v1/README.md) and records the later 532-input safety reproduction check. It does not change canonical data, classifier weights, parsers, scoring formulas, or model-facing prompts. The 0.1.0 release and GPU-tested 0.2.0 code remain separately pinned.

## Immutable documentation and supplement revisions

| Repository | Revision |
|---|---|
| [KoEVD](https://huggingface.co/datasets/KETI-NLP/KoEVD/tree/192a2972f4e7830163fc57c62161d53ccb4c2a92) | `192a2972f4e7830163fc57c62161d53ccb4c2a92` |
| [KoEVD-assistant-safety](https://huggingface.co/KETI-NLP/KoEVD-assistant-safety/tree/b87c9520c4ac4025a6cd69ea38e4ea5f3345f1d3) | `b87c9520c4ac4025a6cd69ea38e4ea5f3345f1d3` |
| [KoEVD-response-strategy](https://huggingface.co/KETI-NLP/KoEVD-response-strategy/tree/0ec5aa8659e34cd41ee97e31c1dddb1681aa098f) | `0ec5aa8659e34cd41ee97e31c1dddb1681aa098f` |

The historical metadata supplement is present at the dataset revision above; the original dataset revision `f5920837769bea77e072c8e033e5ad9cbff4d45d` does not contain it. Both versions contain the same canonical corpus. Model usage examples keep the original tested adapter revisions.

Download just the supplement without re-downloading the corpus:

```python
from huggingface_hub import snapshot_download
snapshot_download("KETI-NLP/KoEVD", repo_type="dataset",
    revision="192a2972f4e7830163fc57c62161d53ccb4c2a92",
    allow_patterns=["reproduction/task1_metadata_v1/*"],
    local_dir="downloads/KoEVD-camera-ready")
```

Then follow its README with the pinned canonical corpus already downloaded. The output is a separate metadata index; do not replace model inputs or silently mix canonical and historical grouping.

## Validation boundaries

The original 12/96-candidate B200 smoke test, the 40-request smoke/959-request expanded live pipeline, and the later 532-input safety reproduction are separate checks. On the latter, all historical safety outputs and labels matched at batch sizes 2, 4, and 32; macro/micro F1 remained 0.9981/0.9981 with the same unsafe-to-safe error. This does not establish accuracy on the 191 new generations, reproduce strategy validation F1, or resolve the 5/191 batch-dependent strategy label sets. See [reproducibility scope](REPRODUCIBILITY.md).
