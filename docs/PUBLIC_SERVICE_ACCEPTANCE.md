# Public service acceptance: Task 3 input-condition analysis

Updated 2026-10-20. **[v0.3.0-rc.19](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.19)
is deployed** in the [public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
The [first-user guide](GETTING_STARTED.md), [chart controls](PUBLIC_PROFILES_GUIDE.md#task-3-type-analysis)
and [paper-data provenance](PAPER_TASK3_TYPE_AGGREGATION.md) describe the current flow.
[Previous rc18 acceptance](audit/public_service_acceptance_rc18_20261020.md)
retains the original type-analysis deployment evidence.

## What is available

Task 3 now offers **utterance type, topic, input risk severity and explicitness**
as independent analysis axes. Four coordinated single-value filters combine with
AND and update all Task 3 cohort cards, overall rates, group bars and heatmaps.
Every pair of input attributes can form a cross heatmap. Select a mark with click,
Enter or Space, inspect its evidence and apply its exact condition. A separate
Compare action carries the same cohort and display settings to model comparison.
Rate/count, safe/unsafe views, source support and classification completion remain
explicit. Label search changes the display, never the cohort or denominator.

Two-model views share domains/scales and show observed unsafe-rate differences
in pp (Model 1 minus Model 2). Each model retains its own classified denominator.
Matched-input statistics elsewhere remain separate. Analysis JSON and Chart JSON
retain conditions/counts; these exports are not result-upload files.

## Data and denominator verification

- **12 historical models × 13,552 inputs = 162,624 original model/source records**
  were reaggregated without generating or classifying responses again.
  Independent SQL grouping matched **10,896 disjoint joint metadata buckets**.
  Complete topic memberships remain inside each bucket, so filtering counts each
  input once even when topics overlap. Existing 132 type groups, 2,148 type-specific
  cells and all earlier Task 1–5 model values are unchanged.
- Shipped-renderer tests checked **9,636 marginal/cross cells**, exact selected
  intersections, rates/counts, undefined rates, keyboard selection, reset,
  Task/reload persistence, model handoff and pp direction, with exact integer tick positions in count mode. Existing type adapters
  also retain 13,680 observations and 396 views across all 66 paper-model pairs.
- All **246 existing metadata groups** in the two current-protocol references
  match the new bucket-derived group counts, valid-source support and completion.
  Registered leaderboard, public revisions and paired statistics match the
  pre-update snapshot exactly. The layout-only follow-up also leaves the complete
  numerical profiles and comparisons unchanged.
- Safe/unsafe rates divide by classified outputs; completion divides by expected
  outputs. Failed, empty and unclassified outputs never count as safe. No-input,
  unclassified-only, measured-zero and unavailable cells remain distinct.
  Input severity is input toxicity metadata, not generated-response toxicity.
  Paper source codes 1/2 still merge into Low; HD remains separate.

## Verified source and runtime

- Application source `3901ab27a61026cd7447c36dd5a7980b7de10e29`; [feature PR #42](https://github.com/KETI-NLP/KoEVD/pull/42),
  [selection-panel correction #43](https://github.com/KETI-NLP/KoEVD/pull/43),
  and [integer count ticks #44](https://github.com/KETI-NLP/KoEVD/pull/44) are merged.
  Package/module `0.3.0rc19`, analysis `koevd-analysis-v4`. The immutable tag binds
  the final application source. Deployment evidence on main is updated separately.
- **550 local CPU tests passed**. The final layout change passed 14 targeted tests
  and final-source Python 3.10/3.12 [source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39381484519)
  and [PR CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39381490876).
- A fresh public clone and isolated CPU install passed pip check, CLI commands,
  40 focused tests and all **440 exact Git manifest entries**. That environment
  was updated to the final source and reinstalled/retested; the release tag resolves
  to that exact source. No source PYTHONPATH override was used for the install tests.
- Running HF revision `1ca009ff7402f9a8bfef856f4579e30bb840a370`. The initial 12-file update
  transferred 3,850,589 bytes; the four-file layout correction transferred 157,125
  bytes; the final three-file integer-tick correction transferred 141,614 bytes.
  All changed remote files match local candidate bytes, and 81 materialized
  source files match Git. CPU Basic, one replica, provider LFS, trusted indexes,
  State configuration, Secrets and resource settings are unchanged. Three code
  deployments; no manual restart or rollback. No new result upload was performed.
- Hosted acceptance passed **16 anonymous GET checks**:
  health/readiness, registration configuration, both numerical profiles, comparison,
  paper models, assets and separate navigation routes. Existing registration and
  numerical-summary sharing remain enabled; official ranking remains disabled.
- Actual browser acceptance covers initial twelve-model leaderboard → paper
  details → independent topic/severity analysis → joint condition → Apply without
  navigation → explicit Compare with retained filters. The floating selection
  action overlap found on the first deployment was corrected and rechecked.
  The private registration/upload workflow is covered by regression tests;
  no new login, upload, publication or withdrawal mutation was needed for this update.
- Numeric export generation passed for two models, five chart JSONs and an analysis
  JSON, including empty heatmap cells. Browser filesystem save completion is not claimed.

Historical paper inputs/metadata and current registrations stay in separate
evaluation collections. Small samples and low completion require care; screening
conditions are not confirmed weaknesses. Classifier labels are measurement proxies,
not independently verified safety or causal bias findings. No prompt/response text,
case IDs, new official ranks or changed storage/retention policy are published.
