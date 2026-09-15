# Historical Task 1 analysis metadata, version 1

The paper's Task 1 metadata analyses used a retained correction view, while the canonical release retained its original source labels. This package makes the difference explicit. It does **not** relabel the canonical benchmark, change model-facing prompts, or rerun generation.

`overlay.json` records 35 changed sources relative to the original release: 30 severity changes, 14 utterance-type changes, and nine overlaps. The retained historical correction file inspected 36 sources. Only severity and utterance type were applied by the historical analysis script; other fields in that file are not adopted here. The private correction file's checksum and the historical script path are recorded for provenance, not as a claim that the private file is publicly downloadable.

## Materialize the view

From the GitHub repository root, using the original release file downloaded to `downloads/KoEVD`:

```bash
python reproduction/task1_metadata_v1/apply_overlay.py --corpus downloads/KoEVD/full_eval/koevd_full_eval.jsonl --output generated/task1_historical_metadata.jsonl
```

The script requires the exact base checksum in `overlay.json`, checks every patch's old labels, and refuses to overwrite an existing file. It uses only the Python standard library. Its output is a **metadata index**, not a corpus or model input file. Join it to existing Task 1 outputs by `source_id` and group by `analysis_severity_band` and `analysis_utterance_type`. Do not pass this index to `koevd-prepare` as a corpus or substitute it for Task 2–5 annotations. For a fresh benchmark evaluation, use the canonical metadata unless deliberately reproducing this historical view, and record the chosen version.

The index contains 13,552 sources, of which 13,430 are non-borderline. The unchanged canonical release has 13,429 non-borderline sources. Original request messages and predictions are unaffected by this metadata join.

## Figure 2 and aggregation

- `source_counts.csv` gives distinct source counts by type and severity, independent of model count.
- `high_coverage_models.csv` identifies the 11 models with effective Task 1 coverage of at least 95%; Gemini Pro is excluded (56.54% coverage).
- `task1_model_utter_type_by_severity_rates.csv` records per-model effective-response denominators and rates. Model-mean rates average these model-specific rates, rather than pooling all models' responses.
- `task1_utter_type_by_severity_model_mean.csv` records the Figure 2a aggregates; type alias `Biased Qs` means `Biased Questions`.
- `release_differences.csv` lists the normalized old/new metadata comparison.

Figure 2 retains all observed cells. Cells with fewer than 30 source utterances display their source count; 30 is a display flag, not an inferential cutoff or an exclusion rule. Four cells have one source each. Eleven models answering one source are not eleven independent source utterances. Small-cell results should not be generalized to an entire category.

The paper's High/Extreme means are 84.2369%/80.7137% with this historical grouping. Regrouping the same predictions with canonical labels gives 84.1424%/80.7045%. The broad direction is unchanged, but the exact historical aggregates require the documented view. Aggregate tables reproduce displayed summaries; private per-item historical model outputs are not included, and this package does not reproduce all original API runs.
