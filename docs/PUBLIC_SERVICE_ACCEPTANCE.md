# Public registration service acceptance

Updated 2026-10-19. **Release v0.3.0-rc.11 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Follow the [pinned first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.11/docs/GETTING_STARTED.md).
The [previous rc.10 acceptance](audit/public_service_acceptance_rc10_20261019.md)
preserves the initial interactive-chart and earlier registration/recovery evidence.

## Deployed source and verification

- Source `f8fb607998e6832550d639b7c383d5139520df9b`, [PR #28](https://github.com/KETI-NLP/KoEVD/pull/28),
  merged as `bf5e95f7e1c495185554d5671368ef4987e6b58d`.
  Immutable [v0.3.0-rc.11](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.11)
  fixes the tested application source; module/package version `0.3.0rc11`.
- Running HF revision `10d70564fe1cb936e996305e9c19317fab3cef5b`. All 10 changed files
  (167,189 bytes) match remote bytes; 80 materialized source files match Git.
  CPU Basic, one replica, provider LFS, operator inputs, State and Secrets are
  unchanged. One code update, no manual restart or rollback.
- **532 local CPU tests passed**, including shipped JavaScript controls,
  registration/recovery, first-user workflow and chart handoff regressions.
- Python 3.10/3.12 [source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39236940568),
  [PR CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39236947254),
  [merge CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39237363712) and
  [tag CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39237398113) passed.
- Fresh public-tag clone, isolated hub+serve installation, pip check,
  module/metadata versions, CLI commands, **34 focused tests** and all **416**
  exact Git manifest entries passed.
- **1,768 chart selections / 168,979 observations** passed numerical checks
  against existing public aggregates. Hosted anonymous health/configuration,
  profile, comparison, page and asset checks passed. Public leaderboard and
  comparison JSON are fully equal to pre-update snapshots; all 94 metric rows,
  public revisions and underlying results remain unchanged.

## Analysis flow and interpretation

1. Start with the twelve-model paper leaderboard or the separately grouped
   registered references. Open model details and inspect a Task.
2. Severity/explicitness use semantic orders. Task 5 segments and legend share
   one outcome order. Task 1 confusion defaults to gold-row percentages with
   a separate count view; row totals include unparsed predictions.
3. Choose scope, metadata axis and condition. Moving from details to comparison
   retains the view. Rebuilding a pair retains comparison conditions. Both
   models use identical category rows and rate scales; value ordering uses a
   shared maximum. Missing cells remain unavailable, distinct from zero.
4. Comparison bars use the full width with two model bars per category.
   Matrices are grouped by chart with aligned domains and shared count scales.
   Select a mark to pin its evidence in an on-screen panel; clear or Escape
   closes it. Counts, valid/expected coverage and source support are explicit.
5. Task 3/5 candidate summaries compare a metadata group against disjoint
   remaining sources within that model and scope. Both sides require at least
   20 valid sources and 90% coverage. Inspect group applies the condition to
   both model charts. Small/low/unknown-support groups remain in plots but do
   not become supported candidates. These contrasts are descriptive, not
   significance tests, causal bias findings or confirmed strengths/weaknesses.

Actual hosted browser checks covered paper detail-to-Task-4 comparison, registered
Task-4 High severity (426/426 for each model), detail-to-comparison handoff,
shared ordering, pinned evidence/clear, Task-5 canonical compositions and the
3/18 transition row versus 784 full-framing sources, candidate inspection and
comparison rebuild. The fixed panel was checked inside the actual HF iframe.
Regression tests cover registration, partial-upload recovery and revision/public
comparison flows; this release did not perform a new identity or original upload.

Task 2/5 overview charts include all available variants/framings for the selected
metadata condition; scope-specific detail charts use the selected scope. Label
search filters bars, highlights complete matrices and retains all composition
segments, without changing denominators. Task-5 transitions use their response-
label row totals including invalid choices; full-framing source support is
separately labeled. Metadata chart filters do not recalculate matched-input
comparison tables above. Severity x explicitness uses an exact precomputed joint
view; unsupported arbitrary multi-axis intersections are never inferred.

Historical paper models have only released per-model aggregates: no fabricated
metadata filters, supported candidates, matched-case comparisons, counts or
missing strategy labels. Task 4 is multi-label/descriptive; its percentages need
not total 100% and have no quality direction. Task 3 is classifier-labeled;
measurement settings and limitations remain visible. Task 5 is a simulation.

No original-response publication, official ranking, recurring backup, GPU job,
paid resource change or publication-permission change was introduced. Existing
registration storage and recovery behavior remain enabled.
The [machine-readable receipt](audit/chart_analysis_ux_rc11_receipt_20261019.json)
records deployment, installation, numerical and hosted checks. Immutable tags
retain their source-time evidence; this living document is updated after hosting.
