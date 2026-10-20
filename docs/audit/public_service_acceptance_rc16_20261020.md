# Public registration service acceptance

Updated 2026-10-20. **Release v0.3.0-rc.16 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Use the [pinned first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.16/docs/GETTING_STARTED.md)
and [Task 3 chart guide](PUBLIC_PROFILES_GUIDE.md#task-3-type-analysis).
[Previous rc.15 acceptance](audit/public_service_acceptance_rc15_20261020.md)
preserves the earlier type aggregation and full registration/recovery evidence.

## What was missing and what changed

The earlier type explorer displayed unsafe rates/counts only. Task 3 now defaults
to **Safe + unsafe** in one stacked bar per user-input type and model. Teal means
classifier-safe and red means classifier-unsafe; these colors retain the same
meaning across models. Model identity is labeled separately. Safe-only and
unsafe-only views remain available, with rate/count switching and shared axes.

Safe count = valid minus unsafe, because Task 3 valid measurements have binary
safe/unsafe labels. Both rates divide by valid measurements. Their sum is 100%
only when valid is nonzero. Failed, missing and unclassified outputs never become
safe: valid/expected completion remains visible separately. Missing model/type
data differs from an observed zero. Small support stays visible and flagged.
Exact evidence and exported chart JSON include both classifications.

## Verified source and public deployment

- Application source `1c20b89e34f9faaff5425a6a33e2552c2de114a6`, [PR #37](https://github.com/KETI-NLP/KoEVD/pull/37),
  merged as `acca154c7a099e6439e1c7f28681b5ab5d338274`.
  Immutable [v0.3.0-rc.16](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.16),
  package/module `0.3.0rc16`.
- Running HF revision `598325b5a1cd901cd1bf5d74beda9c8fd63e9710`.
  All 7 changed files (123,874 bytes) match remote bytes;
  80 materialized source files match Git. Asset URLs include version/content hashes.
  One code update; no manual restart or rollback. CPU Basic, one replica, provider
  LFS, operator inputs, State and Secrets are unchanged. No result upload or new GPU run.
- **540 local CPU tests passed**. Python 3.10/3.12
  [source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39370978953),
  [PR CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39370984422),
  [merge CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39371169522) and
  [tag CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39371176561) passed.
- Fresh public-tag clone and isolated hub+serve install passed pip check, versions,
  CLI commands, **42 focused tests** and **429 exact Git manifest entries**.
- Both existing full reference profiles passed **5,064 chart observation checks**
  across input scopes, rates/counts, both/safe/unsafe views and exact conditional
  topic/severity/explicitness cells. Browser playback and the hosted UI verified
  the default distribution, classification switching, count switching, type
  selection and model comparison. Renderer tests also cover invalid/zero/missing
  counts and retained Task/reload/handoff state.
- Chart JSON generation passed for 22 overview observations and a two-model
  Copyright breakdown: safe counts 113/114, unsafe counts 5/4, denominators 118/118.
  Browser filesystem download completion is not claimed.
- Hosted health/configuration, profiles, comparison, assets and pages passed
  **24 anonymous GET checks**. The leaderboard, public revisions,
  numerical profiles and paired statistics equal the pre-update snapshot.
  Existing model measurements and historical paper values are unchanged.

## Where to find the chart

1. On the leaderboard, choose **Evaluation conditions → Registered results**.
   Open a registered model's Details → Task 3, or compare the two registered runs.
2. Below the basic unsafe-rate chart, find **Safe and unsafe responses by user-input type**.
   **Response safety shown → Safe + unsafe** is the default, including when an
   earlier rc.15 view had stored its rate/count preference without a safety choice.
3. Read safe/valid, unsafe/valid, completion and support together. Select a type,
   then inspect its exact topic, input-severity or explicitness breakdown. The
   same controls and safety colors apply in the two-model comparison.
4. Dedicated type controls share input scope, while general Analyze by and Show
   condition apply to the basic/additional metadata chart. Search hides labels
   only; it never changes denominators. Severity and explicitness retain semantic order.
5. The initial paper leaderboard still contains 12 models. Its released aggregates
   do not provide per-model type breakdowns, so those missing distributions are
   not reconstructed. Full type charts currently use the two registered references
   or newly registered results with validated measurements.

Classifier-safe is a proxy label, not a guarantee of safe behavior. Task 4 remains
descriptive; Task 5 remains simulated tool selection. No combined ethics score,
official ranking, original-response publication, new state retention policy or
registration workflow was enabled by this display correction.
