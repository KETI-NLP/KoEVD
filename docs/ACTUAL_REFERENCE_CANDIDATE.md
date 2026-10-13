# Actual research-reference candidate

The rights holder confirmed research-use raw comparison permission for the exact
Qwen3-8B and Qwen3-4B results on 2026-10-13. Each result has 17,670 records.
This is a local candidate, with no external publication or official ranking.

| Result | Original file SHA-256 |
|---|---|
| Qwen3-8B | `27a4dea555208658133b7713f4f24938cf4e8b8cde23bb1e2003028692ba5a99` |
| Qwen3-4B | `d136bf925164a6604e99da65f8e604541f0236a69d2bfe6479c9549daf293cf1` |

The private local directory `generated/actual-reference-candidate-v93` contains
the catalog, one hash-bound permission record per result, a copy of the dataset
research-use terms, attribution, and the catalog-load receipt. It points to the
preserved original results and independently pinned full input index. Historical
UNAPPROVED catalogs remain unchanged.

From the repository root, with the current package and serve extras installed:

```powershell
koevd-space --catalog generated/actual-reference-candidate-v93/catalog.json --host 127.0.0.1 --port 8772 --origin http://127.0.0.1:8772 --session-root generated/reference-private-sessions
```

Open the local app, upload your compatible result JSON, explicitly select one
reference, then analyze. The server checks the configured original file hashes
and trusted inputs and uses the same analysis engine as the offline CLI. A
reference is not selected automatically. Uploaded scores or gold labels do not
replace the official input index. Task 4 and measurement-limited metrics do not
gain official-rank eligibility from reference selection.

The catalog schema's `operator_confirmed_raw_publication` consent marker records
the reference permission required by the existing loader. The linked evidence
specifies the actual grant and its boundaries: research-use reference, local
preparation and validation, no authorized external posting. The marker is not a
deployment instruction and does not authorize broader use.

KoEVD uses custom **Dataset Research Use Terms v1.0**, not an unrestricted data
license. Raw examples and responses can contain harmful, offensive, discriminatory
or privacy-sensitive text. Preserve the terms, warnings and KoEVD attribution.
External distribution must satisfy the restrictions on actionable harmful
examples and identifying workflow metadata; owner permission alone is not a
claim that every raw field is suitable for unrestricted publication. The current
private development Space and public Static app have not acquired these references.

Generation evidence has been technically reviewed under the user's delegation.
Hashes establish integrity, and model names alone do not establish generation
authenticity. Classifier accuracy remains unestablished; classifier-safe labels
do not prove real-world safety. See [the measurement audit](GPU_MEASUREMENT_MATRIX_RESULTS.md)
and [the current RC checklist](PLATFORM_RELEASE_CANDIDATE.md).
