# Public registration service acceptance

Updated 2026-10-19. **Release v0.3.0-rc.10 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Follow the [pinned complete first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.10/docs/GETTING_STARTED.md).
The [previous rc.9 acceptance](public_service_acceptance_rc9_20261019.md)
preserves recovery, measurement-condition and registration evidence.

## Deployed source and verification

- App source `d38a1c8fbf7958c3ebb2e9ccfd7fec0eb5ec92d7`, [PR #26](https://github.com/KETI-NLP/KoEVD/pull/26),
  normal merge `c4fec5af19dde113a0648adf92459537d407ff05`.
  Immutable [v0.3.0-rc.10](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.10)
  fixes that merge; package/module version is `0.3.0rc10`.
- Running HF revision `a5584e5cdfdda95947158ad0c4f61d024f186462`. All 11 changed files
  (168,350 bytes) match remote bytes; all 80 materialized source files match Git.
  CPU Basic, one replica, provider LFS, operator inputs, State and Secrets remain
  unchanged. One code update; no manual restart or rollback.
- Local final CPU suite: **530 tests passed**. An initial full run encountered
  one checkpoint-confirmation error in an unchanged durability test; the 35-test
  focused run and the subsequent full 530-test run passed without storage changes.
- [Source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39224389537),
  [PR CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39224396093),
  [merge CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39224662007) and
  [tag CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39224674374) passed on
  Python 3.10 and 3.12.
- Fresh public-tag clone / isolated hub+serve installation passed pip check,
  version/CLI checks, 32 focused tests and all 412 exact Git manifest entries.
- Anonymous hosted health/readiness, configuration, both reference profiles,
  full comparison, assets and page checks passed. Public leaderboard and paired
  numerical projections are **fully equal** to the pre-update snapshots. Existing
  94 public metric rows, public revisions and original records are unchanged.

## Interactive analysis

Details and comparison now use live SVG charts with keyboard/focus/hover evidence,
pinning, exact tables, SVG/JSON exports and per-public-revision session view
restoration. Task 1 shows confusion/error rates; Task 2 shows instruction accuracy;
Task 3 shows question/metadata risk; Task 4 shows multi-label strategies/heatmaps;
Task 5 shows framing, strict outcomes and row-normalized response-to-tool transitions.

Scope/condition selections use existing exact numerical partitions/groups. Two
models share Task/scope/axis controls and fixed rate scales while retaining their
own denominators. Missing model/group combinations are unavailable, never whole-
scope fallbacks. Severity × explicitness is an exact joint view; other arbitrary
multi-axis intersections are not inferred. Conditional Task 3→5 transitions are
hidden when the required aggregate is not supplied.

Both public references passed **1,844 chart selections / 171,815 observations**.
Actual browser checks covered Task 1–5 switching, Task 3 joint heatmap and
keyboard evidence, Task 4 High severity (426 valid/expected rows) with matching
15-strategy JSON export, Task 5 High severity (49 valid/expected tool-forced rows)
and explicit unavailable conditional transitions, synchronized comparison,
public-revision view restoration, and historical per-model limits. Hosted browser
checks confirmed the deployed charts and shared controls.

## Interpretation and retained boundaries

Historical twelve-model charts expose only released per-model aggregates. Pooled
all-model question tables are not attributed to an individual model; missing
strategy labels and unreleased counts/intervals are not reconstructed.

Task 3 is classifier-labeled and Task 4 frequency is descriptive; their recorded
measurement conditions and limitations remain visible. Invalid/unmeasured output
is never evidence of safety. Task 5 is a simulation; no tool or robot is executed.
Chart selection does not reveal prompts, responses or private history. Existing
publication permissions, raw-response restrictions, official-rank policy and
registration/recovery behavior are unchanged. No new result upload, HF identity
write, original publication, recurring backup, GPU job or paid resource change
was made for this release.

The [machine-readable receipt](interactive_charts_rc10_receipt_20261019.json)
records deployment, fresh installation, numerical parity and hosted read evidence.
Immutable release tags keep the evidence present when their source was frozen;
this living document is updated after hosted validation.
