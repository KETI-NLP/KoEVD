# Public registration service acceptance

Updated 2026-10-19. **Release v0.3.0-rc.5 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Use the [pinned first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.5/docs/GETTING_STARTED.md).

- Application source: `d7a4cb45a5dc8918006526d852ab8e96f4a79164`,
  [PR #16](https://github.com/KETI-NLP/KoEVD/pull/16), merged as
  `8a2f59ac37c9bf2e5098ed330c28a4f338c9ff99`.
  The immutable [v0.3.0-rc.5 tag](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.5)
  fixes that merge; package and module versions are `0.3.0rc5`.
- Actual running Space revision: `8821bc5cecdc94b2c023284abe5a51906feb7576`.
  Nine changed files (104,080 bytes) match their remote bytes;
  all 77 materialized source files match the application commit. CPU Basic,
  single replica, provider LFS, operator inputs, State and Secret configuration
  are preserved. One automatic start; no rollback.
- [Source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39200857351) and
  [merge CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39201010193) passed
  **510 tests each on Python 3.10 and 3.12**. Local full CPU validation passed
  510 tests; the final public tag passed 14 focused tests in a fresh clone and
  isolated installation with the hub extra, dependency/CLI checks and all
  **388 manifest entries** verified against Git blobs. No source PYTHONPATH
  override was used for that installation.

## Newcomer flow and comparison correctness

The first screen shows all 12 historical paper models with Task-specific scores.
Registered results remain in separate recorded evaluation groups. The table's
definitions panel and the guide explain the different primary metrics and
denominators before users run inference. Task 1/4 tabs start in name order;
their paper frequencies are descriptive, not quality ranks. Missing historical
judgment counts are explained as N/A, distinct from zero events.

Model details contain a **Compare this model** action. The global Compare link
also retains the selected model and its paper/registered collection, including
when the registered profile is still loading. Changing either comparison model
removes the old result and downloads. Late responses after selection, collection
or view changes are discarded. Unavailable publication links show recovery
guidance. Task 4 comparison shows actual strategy labels and distinguishes the
same versus different most frequent strategies without a quality delta.

The guide covers evaluate → export/validate → sign in → upload → confirm settings
→ save privately → explicitly share numerical metrics → find the registered group
→ compare. Save/share confirmations name the next actions. A model-specific chat
template can create a separate group even with the canonical input set; this is
not an upload error. Cross-group matched-input analysis is exploratory and retains
compatibility warnings. Eligibility and cohort policy were not relaxed.

The localhost browser journey used only fictional 12-record data and a synthetic
account. It passed initial connection failure/retry, login/account check, validated
upload, declaration confirmation, private save, numerical consent/publication,
Show my model, profile-to-comparison context, comparison invalidation, reload,
saved-original reimport and a completed CPU report with five output formats.
The shipped-JavaScript integration separately tests a selection change while a
comparison response is pending and navigation before that response arrives.

## Actual production checks and limits

Anonymous production GETs passed health/readiness, current configuration, catalog,
both registered profiles, full paired comparison, shipped assets and all four
page paths. **All 94 registered metric rows and the complete paired response
exactly match the pre-deployment projections.** Paper tables/source numbers are
unchanged. Actual browser checks cover the 12-model home, definitions, descriptive
ordering, paper strategy wording, selector invalidation, registered model detail
and comparison context, and the pinned guide link.

No real original was uploaded, no production owner registration/publication was
mutated, and no GPU inference was repeated in this release. The owner flow was
validated locally; earlier real HF sign-in/storage/restart evidence remains in
the prior acceptance record. This is not a new accuracy or held-out-F1 reproduction.
Task 3 remains classifier-limited, Task 4 descriptive and Task 5 simulated.
Official ranks, original response publication and recurring backup remain off.

Machine-readable [current receipt](validation/public-registration-rc5-20261019.json).
The [previous rc.4 acceptance](validation/public-registration-rc4-20261019.md)
preserves historical evidence and its dates; its deployed revision is superseded.
