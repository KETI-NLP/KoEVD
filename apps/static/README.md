---
title: KoEVD Explorer · Static Candidate
emoji: 📊
colorFrom: blue
colorTo: gray
sdk: static
app_file: index.html
---

# KoEVD Explorer — Static development candidate

Select portable results JSON from your own KoEVD evaluation. The same Python
analysis engine runs in a browser Web Worker through pinned Pyodide 0.29.3.
Files stay in browser memory; there is no upload, inference, login, submission,
durable archive, publication or official ranking service in this candidate.

Compare up to four runs, including operator-approved references when configured.
Download the offline HTML, profile JSON, case JSONL, metrics CSV and Markdown.
Task/subset/variant denominators, N/A and measurement limitations are preserved.
Task 4 is descriptive; no combined ethics score is defined. Task 5 never executes
tools. Uploaded model identity and measurements remain user-reported.

Opening this page downloads runtime and independently configured input assets.
Run analysis starts only after selecting files. Clear cancels the worker and
releases report/file references; reload clears the session. Local files are not
sent to a model API or posted to the Hub. Analysis needs a modern WebAssembly
browser and adequate memory; initial runtime download is substantial.

This is an analysis preview; deployment visibility is controlled by the Space
settings. Synthetic catalogs are
explicit demonstrations, not actual model baselines. Actual reference files
require independent publication evidence. No public results are auto-registered.

## Benchmark data and permitted use

The configured input indexes are reformatted views of
[KoEVD](https://huggingface.co/datasets/KETI-NLP/KoEVD). Benchmark data and its
derivatives remain subject to the [KoEVD Dataset Research Use Terms](DATA_LICENSE.md),
separately from the Apache-2.0 software license. KoEVD contains harmful, offensive
and sensitive examples for research and safety evaluation. Use the data only for
purposes allowed by those terms; harmful operational use and misrepresenting
scores as deployment-safety certification are prohibited. This app executes no
mock tools. It does not publish the result files you select.

Paper: San Kim, Wonjung Kim, Heesoo Kwon and Jae Hee Yang (2026),
*KoEVD: A Korean Benchmark for Metadata-Conditioned Multi-Stage LLM Safety Evaluation*.
The source dataset revision is recorded in each input index's protocol.

Code: [KETI-NLP/KoEVD](https://github.com/KETI-NLP/KoEVD).
See LICENSE, DATA_LICENSE.md, LICENSES, NOTICE.md, runtime/LICENSE and runtime/PYTHON-LICENSE.
Unmodified runtime source: https://github.com/pyodide/pyodide/tree/0.29.3
and https://github.com/python/cpython/tree/v3.13.2 .
