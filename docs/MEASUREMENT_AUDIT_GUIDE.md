# Measurement audit and separate human review

`koevd-audit` is CPU tooling for frozen-response comparisons and review preparation. It runs no target model or classifier and does not establish classifier accuracy, verify generation authenticity, modify measurements, or grant leaderboard eligibility.

## Audit an existing result

Use a full-record `results.json` and an independently prepared trusted input index. The index must come from the operator/data preparation path; a submitter-provided index is not official validation. Use the actual guideline ID/version and provide that document to reviewers.

```bash
koevd-audit create \
  --results runs/model-A/results.json \
  --trusted-index inputs/trusted_input_index.json \
  --guideline-id YOUR_ACTUAL_GUIDELINE_ID \
  --guideline-version YOUR_ACTUAL_GUIDELINE_VERSION \
  --limit 100 --seed 1729 \
  --output-dir audits/model-A
```

The output directory must be new or empty. Files are private by default and contain original messages and potentially harmful generated text. This command has no network upload or publication step. Select storage and sharing permissions accordingly.

- `audit.json`: original classifier labels, metadata, quality flags, selected cases, universe counts and measurement comparisons. Keep this apart from blinded reviewer materials.
- `blinded-cases.jsonl`: input messages and generated final text, generation status and opaque bound case IDs. Model name, metadata/gold, classifier labels and selection reasons are omitted. Text itself may still contain identifying clues; this is field blinding, not a guarantee of complete blinding.
- `review-template.json`: guideline ID/version, empty reported reviewer identity and explicit `not_reviewed` decisions.
- `README.md`: scope and interpretation reminders.

Selection is deterministic: named suspect sources first, then classifier disagreement, length/repetition, invalid or missing measurement, other quality flags, then metadata coverage. Within each priority, cases rotate across metadata combinations with seed-bound ordering. Topics can overlap and are not independent statistical rows. Each selected case is one Task 3 generation and its corresponding Task 4 measurement.

The default named sources are the historical safety suspects `new_template3_1st_13794`, `new_template3_1st_05843` and strategy batch mismatch `new_template3_1st_05104`. Additional sources use repeatable `--suspect-source ID`. `suspects_present`/`suspects_missing` describe the entire input universe, not a promise that every source was selected when the limit is small. Selected IDs and reasons are in `cases`.

The review sample is deliberately enriched for issues. Its counts do not estimate natural risk prevalence or held-out classifier performance. Severity describes benchmark inputs; it is not human gold for newly generated answers.

## Compare frozen measurements

Supply variants made by remeasuring **the same generations**. Preserve the baseline and each variant separately; changing the generated text is not a measurement-condition comparison.

```bash
koevd-audit create \
  --results runs/model-A/results.json \
  --trusted-index inputs/trusted_input_index.json \
  --guideline-id YOUR_ACTUAL_GUIDELINE_ID \
  --guideline-version YOUR_ACTUAL_GUIDELINE_VERSION \
  --variant batch2=runs/model-A-batch2/results.json \
  --variant batch4=runs/model-A-batch4/results.json \
  --output-dir audits/model-A-batch-check
```

At most 16 variants are accepted, with unique IDs. Target model and generation declarations, every prepared input and every response object must match the baseline. Response status, termination metadata and other preserved generation fields also belong to that frozen object. An identical artifact is accepted as a zero-change repeat; this differs from target-model comparison, where duplicate artifacts are rejected.

For each Task 3/4 comparison, the audit separates:

- semantic label changes among jointly valid classifications;
- valid-to-invalid and invalid-to-valid transitions;
- recorded raw-output changes among pairs with both raw outputs present;
- raw-output presence changes, where a log exists on only one side;
- changes in the whole reported measurement value and measurement provenance.

A zero denominator has a null rate. Missing raw logs do not prove output equality. Task 4 label ordering is not a semantic strategy change. Batch, precision and revision differences are reported when recorded; unknown fields remain unknown. Results-v1 does not record observed classifier input order, so the variant name is a reported description, not evidence of that order. The new opt-in [trace sidecars](MEASUREMENT_TRACE_GUIDE.md) observe tokenization, parameter dtype and eligible call order. Results-v1 alone still lacks those detailed observations. Actual GPU audit logs and interpretation remain required in M4. Differences are not automatically attributed to batch or hardware.

## Fill and import an independent review

Give reviewers `blinded-cases.jsonl`, `review-template.json` and the actual guideline. Keep a separate filled file for each reviewer. Fill the reviewer ID/role and provide a rationale for any reviewed judgment.

```json
{
  "case_id": "COPY_FROM_TEMPLATE",
  "input_sha256": "COPY_FROM_TEMPLATE",
  "response_sha256": "COPY_FROM_TEMPLATE",
  "safety_label": "uncertain",
  "strategies": null,
  "rationale": "Explain the uncertainty against the supplied guideline."
}
```

Safety decisions are `safe`, `unsafe`, `uncertain`, `abstain`, or `not_reviewed`. The last is the default and never becomes safe. Strategy labels are the existing KoEVD vocabulary, optionally including its separate `unsafe` marker. `null` means no strategy judgment was returned; `[]` means the reviewer explicitly judged no listed strategy applicable. Duplicate or unknown strategy labels are rejected. Failed/empty generations cannot receive safe/unsafe response labels or strategy judgments; use abstain/not_reviewed as appropriate.

```bash
koevd-audit import-review \
  --review audits/model-A/reviewer-1.json \
  --audit audits/model-A/audit.json \
  --results runs/model-A/results.json \
  --trusted-index inputs/trusted_input_index.json \
  --output audits/model-A/imported-reviewer-1.json
```

The output file must not exist. Import revalidates the results and independently reconstructs the deterministic audit selection, universe and case snapshots. It rejects changed input/response hashes, duplicate or unknown cases, changed guideline identifiers and stale baseline/audit bindings. Partial returns are allowed and counted as `unreturned_cases`; unreturned or unreviewed cases are not negative or safe judgments.

The imported file retains original review decisions separately. Reported reviewer identity is not authenticated. `reported_classifier_agrees` is defined only for a definite human safe/unsafe decision and a valid original safety classification; otherwise it is null. No global F1, accuracy certification or automatic relabeling is produced. Import currently supports independent reviews only. Multiple reviewers can return separate files, but conflict resolution and adjudicated-gold import are not implemented yet. An unsupported adjudication stage is rejected.

## Current validation scope

The first audit candidate passed 101 CPU tests, including 13 audit tests. The subsequent trace/source candidate passed 121; see the trace checkpoint for its separate scope. Installed console CLI checks exercised export, filled **synthetic** review import and stale rejection. A registered full-size input index with 17,670 artificial result records was used for scale validation; this is not actual target inference or human annotation.

See [initial validation evidence](validation/platform_m4_audit_cpu_20261008.json) and [the development plan](PLATFORM_DEVELOPMENT_PLAN.md). Those CPU checks did not establish actual target inference or human adjudication. Official rank remains disabled.

The later actual B300 checkpoint independently accepted two target models at prefix96: each generated959 responses and exported1150records, with Task4 reusing the191 Task3 responses. The actual two-result app, CLI and node profiles agree. See [expanded integration evidence](validation/platform_m4_gpu_expanded_20261008.json). This is a custom integration prefix, not a representative/full standard baseline or accuracy reproduction.

Private review queues were prepared for current Qwen3-8B, current Qwen3-4B and the preserved historical B200 run. Each selects100 of191 response sources; all three historical suspect IDs are present and selected in each queue. The historical run was reexported without modifying source files. Its missing finish reasons remain unknown. All review judgments remain `not_reviewed`; no adjudicated gold or accuracy estimate has been produced. Queue preparation and guideline file binding are recorded in [the scoped return/audit evidence](validation/platform_m4_matrix_return_cpu_20261008.json).

The seven-condition frozen-response GPU matrix is still running at the v0.17 checkpoint. For Qwen3-8B, safety labels stayed unchanged across the completed seven conditions, while strategy labels changed on0–10 of191 jointly valid cases depending on condition. In the FP32-request condition, safety parameter storage still contains752,393,024 BF16 and6,389,760 FP32 elements; strategy storage is fully FP32. Therefore the request label must not be interpreted as a completed full-FP32 safety comparison. Parameter storage does not certify kernel arithmetic or identify the cause of label changes. Preserve the original logs and precision caveat. Final result acceptance uses the independently supplied baseline/index and the [matrix return guide](MEASUREMENT_MATRIX_RETURN_GUIDE.md); local CPU return-tool checks do not replace completion of the actual GPU job.

The v0.18 terminal result supersedes that partial checkpoint: both targets/all7conditions were independently accepted. [Final evidence](validation/platform_m4_gpu_measurement_matrix_20261008.json) and [interpretation](GPU_MEASUREMENT_MATRIX_RESULTS.md) preserve the precision caveat. The private unblinded change union contains11 sources for8B and15 for4B,26 cases in `generated/measurement-matrix-changed-cases-20261008-v2`. It includes original/variant measurements and frozen responses, with no human judgments. Do not use its classifier outputs as human gold or mistake the selected instability cases for a representative prevalence sample. Existing blinded human review materials remain separate and unreviewed. Classifiers remain rank-excluded.
