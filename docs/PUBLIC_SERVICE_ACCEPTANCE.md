# Public registration service acceptance

Updated 2026-10-20. **Release v0.3.0-rc.15 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Use the [pinned first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.15/docs/GETTING_STARTED.md)
and [Task 3 type-analysis guide](PUBLIC_PROFILES_GUIDE.md#task-3-type-analysis).
[Previous rc.13 acceptance](audit/public_service_acceptance_rc13_20261020.md)
preserves the prior full-Task charts, search, handoff and registration/recovery evidence.

## Source and validation

- Application source `aa229622bd767c47fe2dbc62f6475a1c71602ff5`, [feature PR #34](https://github.com/KETI-NLP/KoEVD/pull/34) and
  [axis-order PR #35](https://github.com/KETI-NLP/KoEVD/pull/35),
  merged as `a6e2f7831a1aada8dda565a56f585b96bc32b667`. Immutable [v0.3.0-rc.15](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.15);
  module/package version `0.3.0rc15`.
- Running HF revision `96af2c11dad4ddb86fe5e704c06819aea9d9bc3e`. All 7 changed files
  (119,457 bytes) match remote bytes; 80 materialized source files match Git.
  CPU Basic, one replica, provider LFS, operator inputs, State and Secrets are unchanged.
  Two code updates including the final axis-order fix; no manual restart or rollback. Asset URLs include content hashes.
- **540 local CPU tests passed**; final chart refinements also passed all eight
  targeted chart tests and final-source CI. An initial local durability test reported
  checkpoint sequence 1 instead of 2; its isolated rerun and the full final rerun passed.
  Storage code was not changed. The receipt retains that observation.
  Python 3.10/3.12 [source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39358717896),
  [PR CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39358723745),
  [merge CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39358906516) and
  [tag CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39358915557) passed.
- Fresh public-tag clone and isolated hub+serve install passed pip check, versions,
  CLI commands, **42 focused tests** and **427 exact Git manifest entries**.
- For each existing 17,670-record Qwen reference, **33 type slices / 389 exact
  conditional cells** match an independent row-level oracle. No inference or raw
  result upload was required. Existing analysis values are equal after removing
  the additive type slices and accounting for the analysis-format version.
- Existing charts: **1,768 selections / 168,899 observations**. New type charts:
  **408 selections / 1,688 observations**. Export generation passed for 22 overview
  observations and a two-model Copyright breakdown with counts 5/4 and denominators
  118/118. Browser filesystem save completion is not claimed.
- Hosted health/configuration, profiles, comparison, assets and pages passed
  **24 anonymous GET checks**. Leaderboard and paired statistics equal pre-update
  snapshots; hosted analysis matches the local oracle, including the new type cells. The initial rc14 analysis-format marker changed
  from v2 to v3; paired statistical values were unchanged.
  All 94 leaderboard metric rows and public revisions retain their values.

## First-user Task 3 flow

1. The initial paper leaderboard retains 12 models; separately grouped registered
   results include the two full references. Open registered Model details → Task 3.
2. A basic unsafe-rate chart precedes **Where does the model generate unsafe responses?**
   Its valid-output and all-expected denominators are explicitly distinguished.
3. Type chart measure switches rate/count; Type row order sorts a shared row order;
   Search question types retains input focus while filtering labels. Counts use a
   common integer scale. Types are read from metadata, including arbitrary or missing
   categories; no fixed type vocabulary silently drops a category.
4. Inspect unsafe/valid, valid/expected completion and valid-source support. Groups
   below 20 valid sources remain visible and flagged. Invalid or missing measurements
   are not safe. Observed zero counts and undefined rates remain different states.
5. Select a type by bar, keyboard or dropdown. The page moves to exact Topic,
   Input severity or Explicitness slices within that type and input scope. This
   does not infer a cross-tab from marginal totals or intersect unrelated filters.
6. Compare selected type with another model retains type, metric, search, order and
   breakdown axis. Both models keep their own denominator and completion; missing
   type/cross-tab data is explicit. The selected-type pp difference is descriptive,
   separate from jointly valid paired effects and within-model contrasts.
7. Topic detail rows follow the selected value/name order. Severity and explicitness
   retain fixed semantic order in both model details and comparison.
8. General metadata controls apply to the basic/additional metadata charts. The
   type section has dedicated controls and repeats its scope. The additional
   metadata chart is collapsed below type analysis. Task switching/reload preserve
   the dedicated type view; a scope without the selected type visibly resets it.

Actual HF browser checks cover the type overview, rate/count switching, live
search, inspection, three breakdown axes, comparison handoff, other Task views
and Task switching. Historical limits, registration, failed-upload recovery and revision/public
comparison remain covered by regression tests; no new owner write was needed.
The [broader chart guide](PUBLIC_PROFILES_GUIDE.md) covers Tasks 1–5 and exports.

## Interpretation and retained policies

Analysis `koevd-analysis-v3` adds numeric Task-3 type slices. Existing metrics,
partitions, groups, signals, charts and paired effects keep their definitions.
Topics and multi-valued type memberships can overlap, so their counts need not
sum to independent samples. Counts depend on group sizes; high rates from small
samples do not establish a weakness. Task 3 is classifier-labeled and retains
recorded measurement limitations. Task 4 is multi-label and descriptive; Task 5
is simulated, with no real tool or robot execution. Historical per-model type
breakdowns are not reconstructed from pooled tables.

Original prompts/responses remain outside numerical profiles. This release does
not change response-publication permissions, official ranking, durable state,
recurring backup, GPU execution or paid resources.
The [machine-readable receipt](audit/task3_types_rc15_receipt_20261020.json)
records revisions and evidence. Immutable tags retain source-time acceptance;
this living document is updated after verified hosting.
