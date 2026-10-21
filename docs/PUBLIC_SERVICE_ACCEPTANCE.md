# Public service acceptance: exact task-condition analysis

Updated 2026-10-21. **[v0.3.0-rc.22](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.22)**
provides Task 3 interpretation fixes and Task 4/5 condition analysis in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Use the [first-user guide](GETTING_STARTED.md) and [task analysis guide](TASK_ANALYSIS_GUIDE.md).
The release attachment [task_behavior_acceptance_20261021.json](https://github.com/KETI-NLP/KoEVD/releases/download/v0.3.0-rc.22/task_behavior_acceptance_20261021.json)
records the final application source, active Space revision, CI and browser acceptance.

## User-visible changes

- Task 3 individual and comparison severity rows use semantic order. Filtered
  charts are separated from collapsed full-paper tables. Rate differences name
  both models' denominators, not an unavailable single fraction. Exact cells show
  counts and completion, and a supported-contrast preview provides an entry point.
- Selected evidence follows its chart in normal flow rather than covering cells.
  Comparison layouts stack on narrow screens. Missing, zero, small support and
  low completion remain distinct.
- Task 4 includes all 15 strategies, focused strategy-by-condition views, an
  optional full matrix, response-label groups and count/directional co-inclusion.
  Strategy eligibility and full-input completion are separate. The displayed
  mean excludes the Unsafe marker; the original paper density remains unchanged.
- Task 5 connects three instruction framings, seven exclusive outcomes, input
  condition heatmaps and same-input Task 3 response-label/choice correspondence.
  Valid-choice and all-matched denominators are selectable for the correspondence
  bars. Outcomes include invalid and unclassified/missing response groups.
- Four input attributes combine exactly with AND; Task 5 also supports tool-risk
  category. Topic intersections retain required memberships. Detail-to-comparison
  handoff keeps the task, condition, strategy or response-group denominator.
  Conditions are task-specific; reset and condition undo are explicit.
- Historical per-model detail assets load separately from the initial leaderboard.
  Failed loads retain the original tables and offer retry. Late success or failure
  cannot overwrite a changed model, model pair, invalid pair or evaluation collection.

## Numerical integrity and interpretation

All twelve historical models were reaggregated from canonical archived records,
with 44 source-file/table hashes. Exact published Task 4 strategy counts and selected
frequencies, Task 5 framing counts and original Task 3/5 correspondence reconcile.
Metadata and source inventories are consistent across models/framings. No generation,
classifier or parser inference was rerun; no prompts, responses or source IDs are
included in the new public numerical assets.

Historical Parsed rows include partial parsed objects without a decision. The
new outcome view requires successful status, a recognized decision and an available
tool for calls. Two archived call decisions without a tool are explicitly invalid
in this view. Original unsafe/all scores, parse counts and correspondence are
preserved and reconciled separately. Historical and registered definitions are
not merged into one ranking.

Task 4 is descriptive. Task 3 safety labels and Task 5 choices are parallel
measurements on matched inputs, not an executed tool sequence or a causal effect.
Different models can have different valid denominators and response-label groups.
No combined ethics score, significance claim or official ranking is introduced.

## Validation and operation

The feature passed all 556 local CPU tests and Python 3.10/3.12 push/PR CI. A fresh
GitHub checkout and isolated install passed focused tests, CLI checks, pip check
and the exact release manifest. Renderer checks independently sum 1,992 historical
metadata groups and test four-way intersections, co-inclusion denominators, outcome
conservation, same-input correspondence and task-specific recovery. Existing Task 3
checks cover 9,636 marginal/cross cells and 516 disjoint contrasts. Delayed success
and error fixtures verify that changed selections cannot receive stale results.

Both complete Qwen references (17,670 records each) retain every previous diagnostic
value after excluding additive condition buckets. Hosted numerical profiles match
the offline engine exactly. The existing public leaderboard, publication revisions
and paired statistics remain unchanged. Numerical assets for all twelve paper models
and remote code hashes are checked separately from browser behavior.

Actual browser acceptance covers historical and registered model detail/comparison,
condition and strategy handoff, Task 4/5 condition isolation, reset/undo, explicit
completion and separate full-paper summaries. A 390px viewport stacks comparison
charts and retains a 375px document width without page overflow.

The service stays public on CPU Basic with one replica. Registration and explicit
numerical sharing remain enabled; original responses stay private. Existing operator
inputs, provider LFS rules, State/Secret settings and resource/backup policy are
preserved. The update does not run GPU inference or upload raw result files.

The [initial deployment receipt](audit/task_behavior_initial_rc22_receipt_20261021.json)
retains numerical acceptance before the small lazy-load selection follow-up. The
release attachment linked above identifies the final deployed source and receipt.
[Previous rc21 acceptance](audit/public_service_acceptance_rc21_20261020.md) preserves
prior Task 3 evidence.
