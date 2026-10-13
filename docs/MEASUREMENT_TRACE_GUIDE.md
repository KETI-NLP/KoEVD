# Opt-in classifier token/dtype/order traces

The default classifier prompt, parser and batch path are preserved. `koevd-classify` and `koevd-pipeline` now offer an opt-in private sidecar to investigate batch sensitivity and frozen-response measurement differences. No observation is classifier accuracy certification or cryptographic inference authentication.

## Direct classifier CLI

```bash
koevd-classify --task 3 --input task3_predictions.jsonl \
  --output task3_measured.jsonl --adapter-path "$SAFETY_ADAPTER" \
  --base-model-name-or-path "$SAFETY_BASE" --local-files-only \
  --batch-size 2 --torch-dtype bfloat16 --input-order original \
  --inference-mode batch --trace-output task3_measurement_trace.json
```

Use Task 4 and the strategy adapter/base for strategy measurement. `--classifier-max-new-tokens` is optional; omitted means the existing wrapper defaults (safety 8, strategy 64). Do not change these budgets during a baseline audit without labeling a separate condition. `--torch-dtype` omitted preserves the wrapper's `auto` default. Requested dtype can differ from actual adapter/base parameter dtypes; the sidecar records the latter by element count.

The measurement output must differ from the input. A traced invocation requires new measurement and trace files. The sidecar is atomically published without replacement using a same-filesystem hard link; failure is reported if the filesystem cannot support that operation. Incomplete trace files are retained when prediction or output writing fails. They are rejected by successful-trace validation.

## Pipeline controls

```bash
koevd-pipeline --stage classify --output-dir "$NEW_VARIANT_RUN" \
  --safety-adapter "$SAFETY_ADAPTER" --safety-base "$SAFETY_BASE" \
  --strategy-adapter "$STRATEGY_ADAPTER" --strategy-base "$STRATEGY_BASE" \
  --batch-size 4 --classifier-dtype bfloat16 \
  --measurement-order reverse --measurement-mode batch --trace-measurements
```

Create each variant from identical prepared inputs, frozen predictions and generation metadata; do not copy prior measured outputs or traces. New flags are additive. Without them, original ordering, batch inference and wrapper dtype defaults remain in use. Reverse order changes processing but restores original file row order. `single` calls the existing direct-template `predict` path; `batch-size 1` still calls the existing render-then-tokenize `predict_batch` path. They are distinct checks.

Pipeline stores the trace file hash in each measurement manifest. Export validates that hash, the original/output file hashes, ordered record bindings, call/slot membership and observed raw output against recorded measurement raw output where present. Old results without traces keep unknown precision/truncation/revision. New traced exports can include a string beginning `reported_parameter_dtypes:`; it is reported observed parameter dtype evidence, not a certified uniform compute precision. No automatic no-truncation or accuracy claim is added.

## What the sidecar contains

- File and per-row input/response/measurement hashes; original positions and actual eligible generate call order.
- Nonpadding token count/hash, padded input width, padding count and single-template reference count/hash/parity.
- Formatted classifier prompt hash; the original source messages and responses remain in the frozen files.
- Existing generation call arguments: max new tokens, do_sample, pad/eos IDs.
- Generated suffix count/hash including batch padding; first EOS position, count through first EOS and a token-budget-without-EOS heuristic.
- Raw decoded classifier output, including outputs captured before a parser exception.
- Parameter dtype element counts, declared model context, tokenizer class/max length/padding side, package versions and available GPU memory observations.
- Completion/error type and elapsed time including tracing/token-reference work.

The observer passes the existing arguments through, calls original `generate` once and restores the original method even on exceptions. It does not change the released wrappers, regenerate responses, replace parser labels or treat failed calls as safe. Capturing token IDs adds CPU transfers/synchronization and reference tokenization; compare traced batch2 with an untraced frozen baseline to check observation effects. Elapsed time includes this overhead and is not pure model throughput.

`truncation_requested=false` describes the wrapper path, not proof that every upstream/downstream operation preserved all intended content. Model-config context exceedance is a diagnostic against a declared limit, not a complete rotary/context compatibility assessment. EOS/budget fields are derived token observations, not an API finish_reason. Unknown context or settings remain unknown. A failed batch parse can leave generated raw observations but no measured output; that condition remains incomplete.

Sidecars contain private sample identifiers and classifier raw outputs. They are local artifacts and are not automatically put into public results or Spaces. Auth tokens, all environment variables, model weights and local adapter/base paths are not collected by the observer.

## Validation and next GPU work

The final installed candidate passed 121 CPU tests, including 15 trace and 5 source-bundle tests. [Trace checkpoint](validation/platform_m4_trace_cpu_20261008.json). CPU tests use explicitly fake tensors/models, including the actual released wrapper methods running on those fake objects. They establish orchestration, unchanged arguments, restoration, token parity accounting and export binding, not GPU inference. See [GPU node request](GPU_PLATFORM_VALIDATION_PROMPT.md), [measurement audit](MEASUREMENT_AUDIT_GUIDE.md) and the latest [development progress](PLATFORM_DEVELOPMENT_PLAN.md).

The source-only bundle helper is `python scripts/gpu_source_bundle.py build --repo . --output generated/KoEVD_platform_GPU_source_20261008.zip`. Verify with `python scripts/gpu_source_bundle.py verify --zip ZIP --expected-sha256 EXTERNALLY_SUPPLIED_SHA256`. Verify the ZIP independently before running bundled code. Source archives have bounded expansion and reject noncanonical paths, duplicates/case collisions, symlinks and changed manifest file hashes; they do not extract files. Building excludes generated/credential directories and weights and rejects token-like source literals without printing their values.

## Portable conditions and compatibility

Export now retains optional versioned conditions and compact observations in `results.json`. Completed sidecars must match frozen predictions, measured output, batch size and recorded scheduling. Untraced pipeline measurements preserve only recorded declarations. Older files keep unknown conditions. Current readers accept both forms; older strict readers may require an upgrade.

The common local/Spaces engine reports order, single/batch mode, dtype, effective generate options, tokenizer and package differences for Task 3/4 only. Original scores, denominators, labels and Task 1/2/5 compatibility are preserved. Exact per-response token hashes and raw observations still require the full private sidecar. Uploaded conditions remain submitted evidence, not authenticated execution or accuracy. See [RESULT_FORMAT.md](RESULT_FORMAT.md).
