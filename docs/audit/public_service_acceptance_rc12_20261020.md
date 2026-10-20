# Public registration service acceptance

Updated 2026-10-19. **Release v0.3.0-rc.12 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Use the [pinned first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.12/docs/GETTING_STARTED.md)
and [chart interpretation guide](../PUBLIC_PROFILES_GUIDE.md#interactive-model-details-v030-rc12).
The [previous rc.11 acceptance](public_service_acceptance_rc11_20261019.md)
preserves the earlier ordering, denominator, handoff and registration/recovery evidence.

## Source and validation

- Application source `95cf6c734a6ee54494991cae493470892fabe76b`, [PR #30](https://github.com/KETI-NLP/KoEVD/pull/30),
  merged as `4361afa4e576a5c43133202b49b2893bac746b9f`.
  Immutable [v0.3.0-rc.12](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.12)
  fixes the tested application source; package/module version `0.3.0rc12`.
- Running HF revision `8ea27130097c546288de2c7a7e3a4d44e1c05300`. All 10 changed files
  (163,045 bytes) match remote bytes; 80 materialized source files match Git.
  CPU Basic, one replica, provider LFS, operator inputs, State and Secrets are
  unchanged. One code update; no manual restart or rollback.
- **533 local final CPU tests passed**. Python 3.10/3.12
  [source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39264609347),
  [PR CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39264616478),
  [merge CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39264962632) and
  [tag CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39264980960) passed.
- Fresh public-tag clone and isolated hub+serve installation passed pip check,
  versions, CLI commands, **35 focused tests** and **419 exact Git manifest entries**.
- Numerical checks passed **1,768 selections / 168,899 observations** over the
  two existing public references. The lower observation count than rc.11 reflects
  hiding fixed severity-only Task-1 charts under unrelated selected axes, not a
  change to source measurements. Hosted health/configuration, profiles, comparison,
  assets and page checks passed. Public leaderboard and comparison JSON are fully
  equal to pre-update snapshots, including all 94 metric rows and public revisions.

## First-user analysis flow

1. Start at the twelve-model paper leaderboard or separately grouped registered
   results. Open details and choose a Task, scope and metadata condition.
2. Key measured rates precede plots. Every chart repeats its scope, condition,
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
5. Compare this model carries Task/scope/axis/condition into shared controls.
   Matched-input statistics are in a separate collapsed section, explicitly
   unaffected by chart metadata filters. Each descriptive model rate keeps its
   own denominator; jointly valid paired effects retain their named partitions.
6. Long plots scroll with keyboard focus, preserving every row and column. Fixed
   rate scales, model/outcome legends and context stay beside plots. Select a mark
   to pin its evidence; Clear selection or Escape closes it. Scrolling clears
   stale hover evidence. Exact tables and full-plot SVG/JSON exports remain available.
7. Supported contrast candidates follow plots and start collapsed, as do detailed
   interpretation notes. Inspect group applies its condition to both model charts.
   Support/coverage requirements and descriptive limitations remain unchanged.

Actual public browser checks cover Task 1–5, zero/N/A, axis-specific charts,
accuracy versus answer-error direction, valid versus all-expected tool rates,
condition handoff, bounded plot scrolling, candidate inspection, separated paired
statistics and readable outcome legends. The actual HF iframe layout was checked.
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
The [machine-readable receipt](chart_clarity_design_rc12_receipt_20261019.json)
records hosted, numerical, browser and fresh-install evidence. Immutable tags
retain their source-time acceptance; this living document is updated after hosting.
