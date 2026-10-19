# Public registration service acceptance

Updated 2026-10-19. **Release v0.3.0-rc.9 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Follow the [pinned complete first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.9/docs/GETTING_STARTED.md).
This living record is linked from the guide and the Space's Deployment and version link.
Immutable tags retain the evidence available when their source was frozen.

- App source `185d107674a22ef038d5620d48d95318e03a1e10`, [PR #24](https://github.com/KETI-NLP/KoEVD/pull/24),
  normal merge `76eb8f38061dab6190b09e10f66d3383d32e883a`.
  Immutable [v0.3.0-rc.9](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.9)
  fixes that merge; module/package version is `0.3.0rc9`.
- Running HF Space revision `17313aad0c939812ac7fcca52f970253899d025e`. All 14 changed
  files (214,445 bytes) match remote bytes; all 78 materialized
  source files match Git. CPU Basic, one replica, provider LFS, operator inputs,
  State and Secrets are preserved. One code update; no manual restart or rollback.
- [Source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39215486376),
  [PR CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39215513366) and
  [merge CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39215805700) passed
  **528 tests each on Python 3.10 and 3.12**. The local full CPU suite passed
  528 tests; the six shipped-JavaScript journeys also passed after final guards.
  A fresh public-tag clone/isolated hub-extra installation passed dependencies,
  versions and CLI checks, 30 focused tests and all 406 manifest entries against
  exact Git blobs, without a source PYTHONPATH override.

## Recovery corrections

Explicit Retry analysis connection checks a retained session, preserves it on
transient failure, and creates one replacement after confirmed expiry/missing
session. Only unavailable temporary files/reports are invalidated. The page
instructs explicit file reselection or saved-original import; uploads and owner
writes are never replayed automatically. Partial selections stop on expiry, and
a late response from an older session cannot invalidate a newly connected one.

Pipeline status reads validated durable journals using the resume parser. It
separates confirmed successes, known errors, interrupted unknown attempts and
pending inputs. An actual CPU runner interruption preserved one of four responses;
status reported that success and resume made three further calls. Status is
read-only, rejects corrupt/mismatched checkpoints, and recommends generation
compaction before export even when all responses have been checkpointed.

Reload selected registration and Refresh submissions read the selected latest
owner state without a page reload. They preserve unsaved names, descriptions and
reasons; permission statements and sharing consent are cleared for review.
Conflicting mutations remain disabled until the read, then require explicit retry.

## Measurement conditions

Generation cohorts and all numerical metric calculations remain unchanged.
Registered Task 3/4 scores show classifier batch/precision and expandable settings.
Task-specific filters retain their selection during catalog refresh; model focus
clears an obstructing filter. Task 1/2/5 tables do not inherit these filters.
Unknown declarations stay unknown. A declaration digest labels matching settings,
not verified inference or classifier accuracy, and confers no rank eligibility.

Profiles, public leaderboard publications and JSON numerical snapshots add
allowlisted per-Task measurement declarations. Their digests omit trace identity
and response-dependent counts. Comparison warnings show actual left/right values.
No prompt, original response, device identity or private audit note is added to
that declaration. Existing public metric rows and paired numerical outputs are
unchanged after omitting only the added measurement metadata from the envelopes.

## User journey evidence and limits

The actual localhost UI/API used fictional 12-record results and synthetic OAuth.
It passed A/B partial upload with explicit B-only retry, owner conflict/read
recovery/draft preservation/explicit save, real service-session expiry and
reconnection while the registration stayed preserved, saved-original import,
private revision 2/public revision 1 separation, fresh publication of revision 2,
reload recovery, Task 4 batch 2/4 display and filtering retained after refresh,
unaffected Task 2 discovery, and completed comparison of public revisions 2/1
showing left measurement batch 4/right batch 2.

Anonymous production checks passed health/readiness, public configuration,
catalog, both profiles, full comparison, assets and four page paths. All **94
public metric rows** and the previous paired numerical output were preserved;
only measurement metadata was added. Browser checks verify the default 12-model
paper table, cross-collection search, registered Task 3/4 declarations/filter,
unaffected other Tasks, real Qwen3-8B/4B comparison and pinned rc.9 guide links.

No new real original upload or production owner mutation was performed. Owner
flows used localhost fictional data; hosted checks were anonymous reads. Normal
launch restored existing acknowledged state. Earlier real OAuth/save/restart
evidence remains in previous records. No new GPU inference or held-out-F1
reproduction was performed. Official ranks, response publication and recurring
backup remain off. Paper conditions remain separate; Task 3/4 measurements are
classifier-limited, Task 4 is descriptive and Task 5 tools are simulated.

Machine-readable [current receipt](validation/public-registration-rc9-20261019.json).
The [rc.8 acceptance](PUBLIC_SERVICE_ACCEPTANCE_RC8_20261019.md) preserves its
original dates and scope; its runtime revision is superseded.
