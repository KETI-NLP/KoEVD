# Public registration service acceptance

Updated 2026-10-20. **Release v0.3.0-rc.13 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Use the [pinned first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.13/docs/GETTING_STARTED.md)
and [chart interpretation guide](PUBLIC_PROFILES_GUIDE.md#interactive-model-details-v030-rc13).
The [previous rc.12 acceptance](audit/public_service_acceptance_rc12_20261020.md)
preserves the earlier ordering, denominator, handoff and registration/recovery evidence.

## Source and validation

- Application source `a70cf6b82e7561c51b44ed0c32a0acc35af4ef11`, [PR #32](https://github.com/KETI-NLP/KoEVD/pull/32),
  merged as `3d56910aa62368bcf62aaafa7e2ab00b845aa33d`.
  Immutable [v0.3.0-rc.13](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.13)
  fixes the tested application source; package/module version `0.3.0rc13`.
- Running HF revision `ddd0998fdc049fde9d932242e68997027748a787`. All 8 changed files
  (118,328 bytes) match remote bytes; 80 materialized source files match Git.
  CPU Basic, one replica, provider LFS, operator inputs, State and Secrets are
  unchanged. One code update; no manual restart or rollback.
- **535 local final CPU tests passed**. Python 3.10/3.12
  [source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39355197904),
  [PR CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39355282035),
  [merge CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39355438152) and
  [tag CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39355446096) passed.
- Fresh public-tag clone and isolated hub+serve installation passed pip check,
  versions, CLI commands, **37 focused tests** and **423 exact Git manifest entries**.
- Numerical checks passed **1,768 selections / 168,899 observations** over the
  two existing public references. No source measurements changed. Hosted health/configuration, profiles, comparison,
  assets and page checks passed. Public leaderboard and comparison JSON are fully
  equal to pre-update snapshots, including all 94 metric rows and public revisions.

## First-user analysis flow

1. Start at the twelve-model paper leaderboard or separately grouped registered
   results. Open details and choose a Task, scope and metadata condition.
2. Key measured rates precede plots. Task 4 shows a compact measurement-completeness
   badge explicitly separate from a performance score. Its canonical 15-strategy
   glossary gives definitions and newly written illustrative examples, not original
   responses or gold annotations. Historical parse coverage is labeled completeness. Every chart repeats its scope, condition,
   denominator basis and metric direction. Coverage describes completeness, not
   safety; Task 4 strategy frequencies have no quality direction.
3. Measured zero has an unfilled baseline marker and no positive-length bar.
   Unavailable values identify the known reason rather than implying measured
   zero or a confirmed classifier failure. Task-1 Benign missed risk, for example,
   is N/A with a zero eligible denominator, separately from its false-alarm rate.
4. Task-1 gold-class-specific charts follow the available selected axis. Task-2
   instruction overviews and Task-5 framing/composition overviews state that they
   span all available variants under the selected metadata condition. Scope-specific
   detail charts retain the selected scope. Arbitrary marginal intersections are
   never invented; absent conditional transitions remain unavailable.
5. Each Task independently retains scope, axis, condition, search, ordering and
   display settings through Task switching, reload and comparison handoff. Saved
   conditions unavailable for new models visibly reset; partial one-model
   availability is retained rather than inferred. Compare this model carries these
   Task views into shared controls.
   Matched-input statistics are in a separate collapsed section, explicitly
   unaffected by chart metadata filters. Each descriptive model rate keeps its
   own denominator; jointly valid paired effects retain their named partitions.
6. Long plots scroll with keyboard focus, preserving every row and column. Fixed
   rate scales, model/outcome legends and context stay beside plots. Select a mark
   to pin its evidence; Clear selection or Escape closes it. Scrolling clears
   stale hover evidence. Exact tables and full-plot SVG/JSON exports remain available.
7. A separate observed rate-difference summary precedes plots: Model 1 minus
   Model 2 in percentage points, with each numerator/denominator and source support.
   It covers rate-bar charts, excludes coverage, and exports all rows; matrices and
   outcome compositions remain in their charts. Strategies and historical judgment
   frequencies have no quality preference. These are descriptive marginal rates,
   not jointly valid paired effects, significance tests or causal findings.
8. Supported within-model group contrasts follow plots and start collapsed, as do detailed
   interpretation notes. Inspect group applies its condition to both model charts.
   Inspect group clears conflicting label search. A separate clear-search recovery
   action distinguishes hidden observations from unavailable measurements.
   Support/coverage requirements and descriptive limitations remain unchanged.

Actual public browser checks cover Task 1–5, zero/N/A, axis-specific charts,
accuracy versus answer-error direction, valid versus all-expected tool rates,
full per-Task state restoration, search-to-candidate recovery, canonical strategy
glossary, separate observed pp summary, grouped coverage, separated paired
statistics and readable outcome legends. Actual public numerical export generation
checks passed for 30 Task-4 observations and 16 difference rows with both contexts;
browser filesystem save completion is not claimed. The actual HF iframe layout was checked.
Registration, failed-upload recovery and revision/public-comparison workflows are
covered by regression tests; no new original upload or identity write was needed.

## Retained interpretation limits

Historical paper results contain only released per-model aggregates. Unreleased
counts, strategy labels, conditional distributions and matched cases are not
reconstructed. Task 3 is classifier-labeled and retains recorded measurement
conditions/limitations. Task 4 is multi-label; totals need not be 100%. Task 5 is
a simulation, with no real tools or robot execution. For example, unsafe/valid
140/783 = 17.88% differs from unsafe/all 140/784 = 17.86% because one output is
invalid. Both values keep their original denominators.

This release does not change response-publication permissions, official-rank
policy, registration storage, recurring backup, GPU execution or paid resources.
The [machine-readable receipt](audit/task_analysis_context_rc13_receipt_20261020.json)
records hosted, numerical, browser and fresh-install evidence. Immutable tags
retain their source-time acceptance; this living document is updated after hosting.
