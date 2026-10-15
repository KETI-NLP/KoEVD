# Public numerical reports (registered-service candidate)

The registered candidate provides report downloads from each public model profile
and public two-run comparison. These routes are pending registered-service
deployment; their presence in this branch does not mean production registration
is enabled. Check PUBLIC_SERVICE_ACCEPTANCE.md for current hosted status.

## What is included

Choose **Download public numerical report** after opening a profile or completing
a two-run comparison. Public reads and downloads do not require login or a result
upload. Each request checks both the public analysis and current publication state;
a withdrawal or changed publication during rendering discards the file response.
Downloads use no-store responses and a 32 MiB/file limit. An unavailable or
oversized export fails explicitly instead of returning a truncated report.

| File | Contents |
|---|---|
| JSON | Complete public numerical profile or paired comparison, model/generation declarations, verification, policy/eligibility, counts and denominators |
| JSONL | One numerical metric, chart observation or paired difference per line; `koevd-public-numerical-row-v1` |
| CSV | The same numerical rows with explicit units and coverage; strings that could become spreadsheet formulas receive a leading apostrophe |
| Markdown | Numerical table and interpretation limits; untrusted metadata is escaped |
| HTML | Standalone report with numerical tables, observed-value bars and recorded settings; no scripts or external assets |

These files never contain original prompts, response cases, tool arguments,
private review evidence or ownership/history records. Summary permission is
sufficient for public numerical exports; independent response permission does not
change these exports into original-result downloads. The full private report and
portable result artifact remain separate features of your own analysis workspace.
Numerical report JSON/JSONL is not a file to register as a new measured run.

JSON preserves the existing public API object and uses compact serialization so
the two full model profiles fit within the bounded download size. Whitespace has
no effect on decoded values. JSONL/CSV/Markdown/HTML flatten the public observation
rows; they preserve every represented metric numerator/denominator without
claiming to flatten all model declarations into those tabular rows. Use JSON or
HTML settings for complete generation and verification metadata.

## Reading units and comparisons

- `proportion` is a ratio, for example 0.1 means 10%. A ratio with no observations
  remains JSON null, a blank CSV numeric cell or N/A in the text report.
- `count` is a chart observation count. Count bars scale within their chart;
  length does not indicate model quality. Overlapping groups must not be summed.
- `proportion_difference` is left minus right on jointly valid outputs.
  Multiply by 100 for percentage points. Its numerator/denominator and matched
  coverage remain visible.
- Task 4 has no paired quality/event direction; no such difference row is created.
  Its strategy distributions remain descriptive observations.
- Classifier-based observations and model-dependent conditional groups retain
  their measurement limitations. Tool selections are simulated, not robot actions.
- Eligibility is metric-specific. Downloading, sorting or HF account login does
  not prove target-model generation, classifier accuracy or official rank.

Reports are snapshots. After a result is withdrawn the service denies new
downloads; it cannot recall copies already saved by other people. Use the public
registration ID, publication revision and artifact hash to identify the snapshot.
The target model's immutable revision is a separate model declaration.
Tabular rows call these `submission_revision` and `model_revision` explicitly;
an unknown model revision stays blank/null/N/A rather than becoming revision 1.

## API examples

The public registered app origin is `https://keti-nlp-koevd-platform.hf.space`.
Replace the example origin below with it, and use actual published IDs from the
current catalog. See [public acceptance](PUBLIC_SERVICE_ACCEPTANCE.md) for deployed
versions. A paused development candidate is separate from that public service. Do not put OAuth cookies or private bearer tokens in
these public URLs.

```text
GET https://<registered-app-origin>/api/public/submissions/<id>/profile/download?format=json
GET https://<registered-app-origin>/api/public/submissions/<id>/profile/download?format=html
GET https://<registered-app-origin>/api/public/compare/download?left=<left-id>&right=<right-id>&format=csv
```

Supported `format` values: `json`, `jsonl`, `csv`, `markdown`, `html`.
Attachments use fixed `koevd-public-profile.*` or `koevd-public-comparison.*`
filenames; uploader-controlled names never become file paths or response headers.

KoEVD attribution, DATA_LICENSE.md research-use terms for benchmark data, and
model-output permissions remain distinct from the Apache-2.0 code license.
Consult the linked source/data terms before redistributing benchmark material.
