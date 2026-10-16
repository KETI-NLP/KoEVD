# Runner state, diagnostics and resume (development checkout)

The M2 runner preserves assistant final content, finish reason, token counts, server request/response IDs, declared server model, optional reasoning/refusal fields, and each recorded transport attempt. Empty final content and `finish_reason: "length"` are retained, not automatically regenerated or converted into safety labels. `API-ok` means accepted response structure, not parsed task validity or classifier-safe output.

Core execution/reporting remains standard-library-only. Actual target serving and the measurement classifiers use their separate GPU environments. This checkpoint was verified with local HTTP fixtures and CPU doubles; it is not new vLLM/GPU or classifier-accuracy evidence.

For a first registered full run, start with [GETTING_STARTED.md](GETTING_STARTED.md);
use its registered input index before the generation options below. The local
fixture scope above describes the original M2 checkpoint. Later actual two-model
and service evidence is linked in [PUBLIC_SERVICE_ACCEPTANCE.md](PUBLIC_SERVICE_ACCEPTANCE.md).

## Connection check, then evaluate

First prepare as described in [OWN_MODEL_GUIDE.md](OWN_MODEL_GUIDE.md), or use the pinned index in [RESULT_FORMAT.md](RESULT_FORMAT.md). With your target server already running:

```bash
koevd-doctor --base-url http://localhost:8000/v1 --model YOUR_SERVED_MODEL_ID \
  --input runs/my-model/task3_input.jsonl --output runs/my-model/doctor.json
koevd-pipeline --stage generate --output-dir runs/my-model \
  --base-url http://localhost:8000/v1 --model YOUR_SERVED_MODEL_ID \
  --workers 4 --timeout 120 --retries 2 --retry-delay 2
```

`koevd-doctor` validates local message contracts, checks the server's `/models` inventory when supported, and sends one synthetic text probe (up to 16 tokens). An absent requested model or rejected request fails the check. A server without `/models` gets `model_inventory_check: "not_available"`; successful chat does not prove weights identity. Authentication failures do not silently bypass the inventory check.

`--stage preflight` provides the same separate probe using all pipeline inputs. Alternatively add `--preflight` to generation or `koevd-run` to probe first. It is opt-in to preserve existing request counts. Probes are recorded separately and never enter task denominators. Running doctor and generation with preflight sends two probes; use only one if one check is enough.

`--workers` accepts 1–64; 1 retains sequential execution. The client keeps at most that many requests submitted, rather than queuing the full benchmark. Completion may arrive out of order, but the final JSONL retains the original input order. Pipeline generation automatically resumes. Standalone `koevd-run` requires `--resume` for existing results; without it an existing output is rejected.

## Explicit request parameters and declared model settings

Write `extra.json`:

```json
{
  "seed": 7,
  "top_p": 0.9,
  "chat_template_kwargs": {"enable_thinking": false}
}
```

Write `model.json` using actual information about your own serving environment:

```json
{
  "revision": "EXACT_WEIGHT_REVISION",
  "dtype": "float16",
  "quantization": null,
  "chat_template": "NAME_OR_SHA256",
  "thinking": "disabled"
}
```

Replace placeholders; omit genuinely unknown fields or set those provenance fields to null. These are user declarations, not verification of loaded weights. Then:

```bash
koevd-pipeline --stage generate --output-dir runs/my-model \
  --base-url http://localhost:8000/v1 --model YOUR_SERVED_MODEL_ID \
  --workers 4 --extra-body-file extra.json --model-provenance-file model.json \
  --engine-version vllm@YOUR_INSTALLED_VERSION --preflight
```

Extra request fields are restricted to `seed`, `top_p`, `top_k`, `min_p`, `repetition_penalty`, `frequency_penalty`, `presence_penalty`, `stop` and the boolean `chat_template_kwargs.enable_thinking`. Unknown fields, core overrides, `tools`, credentials and the ignored `user` field are rejected locally. These extras are merged into the HTTP JSON, sent and recorded without falling back to a request that drops them. Unsupported server parameters that return 400 remain failed rows. The server accepting a parameter does not demonstrate its actual numerical effect; metadata explicitly says `requested_unverified` / `parameter_effect: "unverified"`.

vLLM documents extra JSON parameters and optional request-ID headers; it also describes inherited HF generation defaults and `--generation-config vllm`. Record the actual server startup/configuration and version for reproducibility. Client declarations alone cannot discover or prove all server defaults. See the [official vLLM server documentation](https://docs.vllm.ai/en/latest/serving/online_serving/openai_compatible_server/).

The client sends only the prepared `messages` plus model/decoding settings. It does not add gold or metadata to the model API. Task 5 remains a text-only mock choice: actual API tool definitions are not sent and tool calls are never executed.

## Durable files and retry meaning

For `taskN_predictions.jsonl`:

| File | Meaning |
|---|---|
| `.jsonl` | Final compacted responses, including failures, in input order |
| `.jsonl.run.json` | Durable run ID, creation time, ordered input-set and configuration hashes |
| `.jsonl.progress.jsonl` | Interrupted/in-progress attempt journal; removed after compaction |
| `.jsonl.status.json` | Latest progress, checkpoint counts, successes/failures and remaining work |
| `.jsonl.lock` | OS lock backing file; its mere presence does not mean a process is alive |

Pipeline Task 1/2/3/5 share the `generation_run` ID in `pipeline.json`. Re-exporting the same pipeline preserves that ID/time. Standalone task executions have separate durable IDs. Existing pre-M2 logs without identity/response metadata retain their unknown fields; adopting them for resume does not fabricate past metadata.

Each attempt start and finish is flushed and fsynced. An interrupted final journal line is repaired; corruption earlier in the journal fails. On resume, changed model/endpoint/decoding/declared provenance, input content or input order fails. Worker count and transport timeout/backoff may change, and their actual values are retained per new attempt. OS locks prevent two processes writing the same output; OS ownership releases after process death even when the lock file remains.

Retryable transport/response-format failures and HTTP 408/429/500/502/503/504 use capped exponential backoff. Other HTTP errors, such as 400/401, are not retried. Every recorded attempt has an ID, ordinal, timestamps, elapsed duration, status and observed HTTP code when available. The selected output is the first accepted API response, including an empty/refusal/length-limited response. Successful contents are never regenerated just because they appear undesirable or fail a task parser.

If the process dies after the request reaches the server but before the response checkpoint, its outcome is `interrupted_unknown`. Resume may generate again for that sample; the client cannot guarantee exactly-once server inference. The extra attempt remains visible. On graceful interruption, already-running requests may finish and checkpoint before the client exits; queued/unstarted work is cancelled. The urllib timeout governs blocking socket operations, not a guaranteed total wall-clock deadline.

Progress distinguishes checkpointed rows from completed work in the current invocation. Failed rows remain available for a later resume. A status of `completed_with_errors` means all scheduled rows have final client outcomes, not full benchmark validity. Inspect coverage and task parsing in the report.

Exception strings/server error bodies and arbitrary headers are omitted from stored diagnostics because they can echo credentials. New CLI stdout/stderr and JSON files use UTF-8, including Korean paths. Raw response and reasoning/refusal text are still content: inspect sharing permissions/private information before publication. Endpoint URLs are local run configuration and are excluded from the portable export.

## Portable export and measurements

`koevd-results export` now retains the new observed fields and attempt ledger in the portable `response` object. Older v1 records remain accepted; optional additions are covered by the packaged schema and runtime checks. Declared extra parameters and model/engine provenance are retained. Selected-attempt IDs, attempt ordering, Task 3/4 identical generation and input/response measurement binding are checked.

Classifiers still consume final `prediction`, not the separate reasoning/refusal field. This preserves the existing measurement contract. Absence of reasoning is unknown, not proof that the model did not reason. Task-level parsing, repeated output diagnostics, model compatibility and uncertainty are the next analysis milestone; no new correctness or safety labels are inferred here. Rerun classification after generation changes, since existing measured-file hashes then become stale.

## Reproduce CPU evidence

From an installed checkout (dev extra adds formal schema checks):

```bash
pip install '.[dev]'
python -m unittest discover -s tests -v
python scripts/validate_runner_cli.py --output-dir generated/my-runner-cli-check
```

The validation script requires the checkout's tests/fixtures and an installed package in the active interpreter. It uses a local HTTP server and fictitious outputs only. It exercises installed CLI prepare→doctor→generate→resume→export→validate→report, with 10 evaluation requests, 2 explicit probes and 12 exported records. Re-running completed generation sends zero new evaluation requests. The deliberately reported length-limited response is synthetic, not real inference. Use a new/empty output directory.

## Recover a full registered run

For the canonical end-to-end workflow and model-ID conventions, use
[GETTING_STARTED.md](GETTING_STARTED.md). Its recovery commands cover generation
resume, Task-specific measurement retry, explicit `--remeasure`, local tokenizer
budgets and bounded prepared-input probes. Use the real served model ID rather
than a generic alias; retain its immutable revision separately. These operations
do not change the standard protocol or hide failed rows.
