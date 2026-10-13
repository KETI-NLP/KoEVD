# Portable results: first implementation (v1)

This format packages one completed KoEVD pipeline generation into a single `results.json`. It retains all expected samples, including failed generation and unmeasured responses. Existing Task JSONL files and `pipeline.json` remain the source logs.

The checkout now contains an operator-controlled pinned core protocol candidate as well as local smoke/custom indexes. The format does not establish model authenticity, classifier accuracy, or public leaderboard registration. Task 3/4 measurements remain user-reported and measurement-limited. Public registration and protocol eligibility are not implemented in this milestone.

## Prepare, export, validate and report

Install the checkout with `pip install -e .` first. `python -m koevd_eval.results` can replace `koevd-results` in every command below.

Prepare inputs and generate responses using [OWN_MODEL_GUIDE.md](OWN_MODEL_GUIDE.md). Create an index from those prepared inputs. Where known, record immutable dataset and preparation-code revisions; omitted provenance is `null`, never inferred from the model name or current main branch.

```bash
koevd-results index --run-dir runs/my-model --output local_input_index.json \
  --dataset-repo KETI-NLP/KoEVD --dataset-revision EXACT_DATASET_COMMIT \
  --code-revision EXACT_PREPARATION_COMMIT
koevd-results export --run-dir runs/my-model --trusted-index local_input_index.json \
  --output runs/my-model/results.json --code-revision EXACT_GENERATION_COMMIT
koevd-results validate --input runs/my-model/results.json --trusted-index local_input_index.json
koevd-results report --input runs/my-model/results.json --trusted-index local_input_index.json \
  --output-dir runs/my-model/portable-report
```

Replace uppercase placeholders with actual revisions; do not leave them as claims. Classification may precede export. If either classifier output is absent, that task is explicitly unmeasured. If output files exist, their manifest checksums and preserved generation fields must match; stale files fail export rather than disappearing.

`export` requires a generation row for **every** expected Task 1/2/3/5 input. Failed requests must retain rows with `api_status: "error"`. Task 4 reuses the same Task 3 generation, including failures. A partial run cannot silently reduce its denominator. Complete or repair its generation logs before export.

The full core pipeline has 15,011 generation requests and 17,670 exported records (Task 4 adds its 2,659 measurement records). Actual counts come from the index, not a fixed number in the validator. Task 3 primary and tool-overlap membership remains in trusted metadata and is restored for the report.

## The trust boundary

A local index is convenient for your own run. Creating it does **not** make it an official index. A future hosted service must build and approve its index independently from pinned official data/code, keep it outside uploads, and select it through its own protocol registry. Never accept an uploader's index as proof of official inputs.

The upload contains no `gold`, `metadata`, prompt messages or aggregate score. For each task/sample the validator requires the independently supplied index checksum, input checksum, source and variant. It restores prompt, gold, metadata and source from that index. Rescoring uses the existing `profile.py` engine for the local JSONL and portable JSON paths.

Recomputing an uploaded file's hash cannot bypass a different trusted index. A user who supplies both the result and the supposedly trusted index can control both; the service must enforce this boundary. A checksum confirms content consistency, not which weights generated the response. Reported classifier labels can be fabricated while keeping hashes consistent; CPU validation cannot prove them correct or actually produced by a classifier. Verification/remeasurement is a later, separate requirement.

## Version 1 contract

The executable reference is [results.py](../src/koevd_eval/results.py), with adversarial tests in [test_results.py](../tests/test_results.py). Core analysis has no new dependencies. Draft 2020-12 schemas are packaged in [schemas/](../src/koevd_eval/schemas/). Run `koevd-results schema --kind results` (or `index` / `protocol`) to print them. Install `pip install -e ".[dev]"` for independent `jsonschema` validation. JSON Schema checks structure; runtime validation is still mandatory for expected IDs, canonical hashes, input restoration and measurement bindings.

| Field | Meaning |
|---|---|
| `schema_version`, `artifact_kind` | `koevd-results-v1`, `full_records`; summary-only results cannot be rescored |
| `run` | UUID, UTC creation time, optional code revision, migration source, target model, decoding settings, classifier fingerprints |
| `protocol_sha256` | Canonical digest of the separately supplied index's protocol |
| `input_index_sha256` | Digest identifying the full trusted expected input set |
| `publication` | Local artifact, response text included; an upload cannot assert publication |
| `records` | One row per expected task/sample, including failure/unmeasured rows |
| `content_sha256` | Canonical JSON digest excluding this field |

Each record has `task`, `sample_id`, `source_id`, `variant`, `input_sha256`, `response`, and `measurement`. The latter is tied to both response and input digests for Tasks 3/4. Task 3/4 response objects must be identical for a shared sample. Unknown raw classifier parsing remains `label: null` or empty strategy list; its coverage is not safe evidence. Task 4's separate `unsafe` marker is retained in the existing code format. No artificial confidence is added.

Response digest is SHA-256 of canonical JSON serialization of the text string, **not** SHA-256 of plain text bytes. Canonical JSON uses sorted object keys, UTF-8, no ASCII escaping, compact separators, and rejects nonfinite numbers. `input_sha256` preserves the existing runner's `input_digest` serialization to maintain compatibility with existing logs.

The migration preserves unrecorded model revision, dtype, quantization, template, thinking, seed, engine version, classifier precision and truncation as `null`. Older runner logs lack finish reason, usage and request ID; those fields remain `null`. The M2 runner now records them when returned by the server, with optional reasoning/refusal, IDs and an attempt ledger. See [RUNNER_GUIDE.md](RUNNER_GUIDE.md). It does not claim that decoding or classifier provenance is fully known.

Default limits: 128 MiB JSON, 100,000 records, 1 MiB per response/raw classifier text. UTF-8 errors, duplicate object keys, NaN/Infinity, unknown record fields, duplicate/missing/extra task/sample keys, stale response binding and unexpected verification assertions are rejected. No ZIP extraction is performed. Prepared input paths must stay in the run directory.

Endpoint URLs, credentials, raw API errors and local absolute model paths are not exported. **Response/raw classifier text is included**: inspect it for private data and redistribution permission before sharing. Export does not automatically redact content or publish anything. Summary/redacted export and large JSONL bundles are later work.

## Pinned core protocol candidate

[koevd-core-canonical-v1.json](../configs/protocols/koevd-core-canonical-v1.json) pins the dataset to `f5920837769bea77e072c8e033e5ad9cbff4d45d`, nine dataset-file checksums, preparation implementation identity, Task input sets, canonical metadata, parser versions, decoding policy and measurement revisions. The reference was built from previously downloaded HF files whose cache metadata identifies that immutable revision, with each consumed file checked against its release manifest. No new inference was used to establish these input sets.

```bash
koevd-results protocol-index --registry configs/protocols \
  --protocol-id koevd-core-canonical-v1 --dataset-dir downloads/KoEVD \
  --run-dir runs/core-protocol --output runs/core-protocol/trusted_input_index.json
```

This independently prepares the expected input contract, rejects changed dataset/code, and requires the pinned counts and input-set digests. `--run-dir` must be empty or already prepared with the same data/selection. Run target generation and measurement against those prepared inputs. Export using the generated trusted index. On an operator/service side, load the registry from the operator's checkout and use the operator's independently generated index:

```bash
koevd-results validate --input results.json --trusted-index operator/trusted_input_index.json \
  --registry configs/protocols --protocol-id koevd-core-canonical-v1
```

An upload's claimed protocol ID, a locally renamed file, or a recomputed uploader checksum cannot select an arbitrary registry definition. `ProtocolRegistry.validate_index` checks the stored definition and expected input-set digests, including gold and metadata. Do not point the operator's registry directory at uploaded files. Registered input identity does **not** automatically prove compliance of actual generation/measurement settings or make a result rank-eligible. The decoding/measurement policy is recorded for the later compatibility and registration checks. CLI validation currently reports `official_rank_eligible: false`. Task 3 official ranking remains disabled because of measurement concerns; Task 4 is descriptive and also has no official ranking. This protocol is a release candidate, not a published leaderboard standard.

The full trusted index currently occupies 69,541,861 bytes as pretty-printed JSON, below the 128 MiB reader cap. It belongs on the trusted operator side, not in a user result upload. Later hosted code can cache a validated index per process rather than duplicating it per session.

## Import original standalone JSONL logs

```bash
koevd-results migrate --task1 logs/task1_predictions.jsonl \
  --task2 logs/task2_predictions.jsonl --task3 logs/task3_safety.jsonl \
  --task4 logs/task3_strategies.jsonl --task5 logs/task5_predictions.jsonl \
  --trusted-index local_input_index.json --output migrated_results.json
```

Task 1/2/3/5 are required. Task 4 is optional; if absent it becomes an explicit unmeasured copy of the Task 3 generation. Supply original prepared-row fields, not aggregate CSVs. Input rows must exactly match the trusted expected set; retain failures. Changed gold/messages/source, incomplete files, mixed model IDs or conflicting recorded decoding settings fail import. Use `--model` only if an old file lacks its target identifier; the supplied ID remains user-reported. A legacy file without original input/provenance cannot be promoted to a full verified result. Aggregate-only paper artifacts remain separate references and cannot be converted into genuine per-case target outputs.

Classifier labels are preserved, but missing classifier identity, hashes, precision and batch size are explicitly `null` and measurement-limited. Missing generation settings remain `null`; they are not filled with current defaults. If every generation row records the same temperature/token limit, those fields are retained. Raw API errors, endpoints, run-config secrets and local paths are omitted. For pre-M2 imports, run IDs/timestamps identify the exported artifact. New pipeline exports preserve the durable evaluation-run identity. Old logs do not acquire fabricated past execution metadata.

## CPU-only example

```bash
python examples/make_demo_results.py --output-dir generated/synthetic-results
koevd-results validate --input generated/synthetic-results/results.json \
  --trusted-index generated/synthetic-results/local_input_index.json
koevd-results report --input generated/synthetic-results/results.json \
  --trusted-index generated/synthetic-results/local_input_index.json \
  --output-dir generated/synthetic-results/second-report
```

The output contains 12 records: Task counts 1/4/2/2/3. It uses a fictitious model, no inference or classifier, one failed generation and no measurements. These are formatting and denominator checks, not measured model performance. Use a new/empty output directory. Existing data is preserved.

## Remaining scope

Common compatibility and offline chart/case UI are implemented in the separate v2 diagnostic report. The local upload/session/reference-analysis flow now has CPU/browser evidence. Persistent submissions/leaderboard, actual raw baseline and two-target-model GPU integration evidence remain incomplete. The previous result reporter is preserved for historical use.

## Source-aware analysis

`koevd-diagnose` validates full results against independently trusted indexes,
then exports v2 partition/group metrics, intervals, chart data, full cases,
paired comparisons and `report-v2.html`. The HTML is self-contained and retains
all raw cases. It preserves historical scorer semantics. See
[DIAGNOSTICS_GUIDE.md](DIAGNOSTICS_GUIDE.md) for commands, browser evidence and
remaining GPU/Spaces/submission limits.


## Upload using the local app candidate

`koevd-space` accepts only full result JSON and resolves its input hash against an
operator-configured catalog. It does not take an uploader index/gold/score/path.
Use [SPACES_GUIDE.md](SPACES_GUIDE.md) for the private-session demo, supported
catalog modes, limits and actual verification scope. Structural validation and
recomputed scores do not authenticate model generation or grant public admission.

## Optional measurement conditions extension

New exports can add `run.measurements["3" or "4"].conditions`, versioned as `koevd-measurement-conditions-v1`. The current reader accepts the original evidence object without it. Older strict readers may reject this optional field and should be upgraded. The outer identity remains `koevd-results-v1`, following the existing optional response-provenance policy; unsupported extension versions and unknown fields are rejected.

Requested dtype, input order, single/batch mode and optional token-limit override are separate from `observation`. Untraced exports preserve only declarations recorded by the pipeline. A completed hash-bound sidecar adds allowlisted dtype counts, tokenizer/context/package versions, effective generate options and observation coverage/quality counts. Export rejects manifest/trace conflicts. Portable validation checks coverage against response statuses. Private paths, device details and complete per-record token observations remain in the separate sidecar.

Only Task 3/4 compatibility compares these conditions. Missing fields stay unknown. A null requested budget does not prove equal effective defaults. Trace hashes and response-dependent counts are evidence identifiers/statistics, not settings; they do not restrict compatibility. Existing scores and denominators are unchanged. Parameter dtype counts do not prove arithmetic precision; budget-without-EOS is a heuristic.

Uploaded compact observations cannot independently verify omitted sidecars, authenticate GPU inference, certify absence of truncation or establish accuracy. Provenance stays `user_reported`, accuracy stays `measurement_limited`, and all current comparisons stay rank-ineligible. See [MEASUREMENT_TRACE_GUIDE.md](MEASUREMENT_TRACE_GUIDE.md).
