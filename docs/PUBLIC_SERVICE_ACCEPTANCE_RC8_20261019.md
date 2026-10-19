# Public registration service acceptance

Updated 2026-10-19. **Release v0.3.0-rc.8 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Follow the [pinned complete first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.8/docs/GETTING_STARTED.md).
This living record is linked from the guide and the Space's **Deployment and version** link.
Immutable tags retain the evidence available when their source was frozen.

- App source `ff385d037500424cbb73f9fdc23a6f43bcce5b43`, [PR #22](https://github.com/KETI-NLP/KoEVD/pull/22),
  normal merge `8326b4d0154aca5da566bf0f36ec4afcc9a378a0`.
  Immutable [v0.3.0-rc.8](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.8)
  fixes that merge; module/package version is `0.3.0rc8`.
- Running HF Space revision `b53bb8a5ebbcbda79b6d29eaa4cb4b76763e7b4f`. All nine changed
  files (125,918 bytes) match remote bytes; all 78 materialized
  source files match Git. CPU Basic, one replica, provider LFS, operator inputs,
  State and Secrets are preserved. One code update; no manual restart or rollback.
- [Source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39209589017),
  [merge CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39209855628) and
  [tag CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39209961848) passed
  **520 tests each on Python 3.10 and 3.12**. The local full CPU suite passed
  520 tests. A fresh public-tag clone and isolated hub-extra installation passed
  dependency/version/CLI checks, 22 focused tests and all 399 manifest entries
  against exact Git blobs, without a source PYTHONPATH override.

## Partial-upload recovery

Each selected file receives its own outcome. An earlier failure does not prevent
later selected files from being attempted. Successful uploads remain available;
an explicit retry skips acknowledged File objects still retained in the session
and attempts the remaining files. Removing a retained run permits a new upload.
An exact duplicate reconciles the current server session with a read rather than
aborting the selection. No POST is retried automatically after a lost response.

Local filenames appear in the private analysis list and registration selector.
They do not replace public model identity or alter the original JSON. A corrected
file on disk must be selected again; changing contents under the same filename
does not incorrectly skip it. Existing quotas and upload limits remain enforced.

## Saved and public revision scopes

Owner progress, next action and buttons distinguish latest saved revision from
the public revision. Private analysis/download use the saved head; public profile,
leaderboard and comparison use the published revision. Saving a correction alone
does not publish it. Fresh permission and consent are required to replace the
public summary. Public profile and comparison identify their published revisions.

The guide distinguishes transport failures, accepted but unparseable/truncated
outputs, classifier failures and stale exports. It explains when to retry failed
work, when existing responses can be reused, and when a deliberate new run or
remeasurement and a fresh export are required. Failed outputs remain part of the
reported denominators; successful generations are not selectively regenerated.

## User journey evidence and limits

The localhost browser used fictional 12-record results and synthetic OAuth with
the shipped UI/API. File A succeeded and B failed; clicking retry on the same
selection sent only B (observed request sequence A, B, B). A was privately saved
as revision 1 and explicitly shared. B was saved as private revision 2 while public
revision 1 and its comparison remained unchanged. Fresh explicit consent published
revision 2 and the next comparison used revision 2. Reload restored both states.
Reselecting files showed their filenames. A further private save left saved
revision 3/public revision 2, with all three historical revisions preserved.

Additional shipped-JavaScript and backend tests cover continuing later files,
exact duplicate reconciliation, removed uploads, quota enforcement, changed content
with the same filename, lost acknowledgements without automatic POST replay,
and warm profile/comparison caches changing only after fresh publication consent.

Anonymous production checks passed health/readiness, registration configuration,
catalog, both profiles, full comparison, shipped assets and the four page paths.
**All 94 public metric rows and the entire paired response exactly match the
pre-deployment projections.** Browser checks verify default 12-model discovery,
real Qwen3-8B/4B profiles and comparison with revision labels, the submission
recovery guidance and the pinned rc.8 guide link.

No new real original upload or production owner mutation was performed. Owner
flows used localhost fictional data; hosted checks were anonymous reads. The
normal launch restored existing acknowledged state. Earlier actual OAuth/save/
restart evidence remains in the prior records. No GPU inference or held-out-F1
reproduction was repeated. Official ranks, original-response publication and
recurring backup remain off. Paper and registered conditions remain separate;
Task 3/4 measurements are classifier-limited, Task 4 is descriptive and Task 5
tools are simulated.

Machine-readable [current receipt](validation/public-registration-rc8-20261019.json).
The [rc.7 acceptance](PUBLIC_SERVICE_ACCEPTANCE_RC7_20261019.md) preserves its
original dates and scope; its runtime revision is superseded.
