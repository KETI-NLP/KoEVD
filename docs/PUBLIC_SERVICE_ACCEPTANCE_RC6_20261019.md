# Public registration service acceptance

Updated 2026-10-19. **Release v0.3.0-rc.6 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Use the [pinned first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.6/docs/GETTING_STARTED.md).
Both its deployment-evidence link and the Space's **Deployment and version** link
point to this living record; immutable release tags retain their original evidence.

- Source `ab8fc860a36970f521ba4ef071028f46ac7b6741`, [PR #18](https://github.com/KETI-NLP/KoEVD/pull/18),
  merged as `f0ed34905e03002c8039020fa93af3147ff98993`. The immutable
  [rc.6 tag](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.6) fixes that
  merge; package/module versions are `0.3.0rc6`.
- Actual running Space revision: `45e91bad9be833e9499fb0030e72c08cbde7fc9d`.
  Fourteen changed files (167,874 bytes) match remote bytes;
  all 78 materialized source files match the application commit. CPU Basic,
  one replica, provider LFS, operator inputs and State/Secret configuration are
  preserved. One automatic start; no rollback or new paid resource.
- [Source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39203180115) and
  [merge CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39203442606) passed
  **516 tests each on Python 3.10 and 3.12**. Local full CPU validation passed
  516 tests. A fresh public-tag clone and isolated hub-extra installation passed
  dependency/version/CLI checks, 20 focused tests and all 392 manifest entries
  against exact Git blobs, without a source PYTHONPATH override.

## Discovery, condition tables and duplicate originals

The home still starts with all 12 historical paper models. **Search all models**
finds paper results and every public registered condition group, including aliases,
display names, revisions and submission IDs. **Show on leaderboard**, the advanced
finder and owner actions share the same condition-selection, navigation and
highlight path. An owner's focus URL restores the correct registered row after
reload. Scores from different groups are not mixed into one order.

Multiple registrations of the same exact original occupy one labeled result row;
their aliases remain discoverable and private originals/history remain separate.
All automatic comparison entry points choose a different original, and alias-to-
alias comparison is explained rather than sent to the server. The actual two
production reference originals remain distinct. Model-name order supports both
directions. Historical detail percentages use readable precision and explicit
units; severity codes are decoded using the verified historical plotting mapping.
The source rows, corrected metadata view and current canonical labels remain distinct.

## Latest-export and recovery checks

`koevd-results check-run` compares the exported responses, measurements, model and
settings with the retained pipeline, including stable run identity when available.
It is read-only and checks contents rather than modification dates. `stale_export`
and invalid/pending-recovery cases exit 2; current exports can retain explicit
failed-generation and unmeasured-response warnings. Legacy runs without stable IDs
compare contents/settings and disclose that limit. Ordering records or updating
export code metadata alone does not create a false stale result.

The actual CLI was exercised against a tiny synthetic registered protocol: current
export → changed prediction detected → re-export → current again. It retained the
failed request and correctly reported registered input scope. Unit tests also cover
measurement completion, invalid JSON, identity/settings changes, concurrent source
changes, read-only behavior and exit codes. This is not a model authenticity,
parsing-accuracy, classifier-quality or GPU-performance attestation.

The localhost browser used fictional 12-record outputs and synthetic OAuth. It
passed initial session failure/retry, cross-group model search, advanced-finder
navigation, private save, explicit summary sharing, duplicate alias discovery,
single-row display, owner comparison to a different original, reload/reimport,
completed CPU report outputs, stop-sharing removal, fresh-consent reshare and
focus-link reload. Shipped-JavaScript tests separately retain the pending-response
and navigation guards introduced in rc.5.

## Actual production verification and limits

Anonymous production health/readiness, configuration, catalog, both profiles,
full paired comparison, shipped assets and all four page paths passed.
**All 94 metric rows and the complete paired response exactly match the
pre-deployment projections.** The paper source CSVs and numerical bundle are unchanged.
Actual browser checks cover the default 12-model home, global Qwen lookup, correct
condition table/highlight, advanced-finder navigation, name descending order,
decoded percentages/severity, registered model comparison and guide/version links.

No real original upload or production owner mutation was repeated. Owner/recovery
and duplicate scenarios used localhost synthetic data; production checks were
anonymous reads. Existing stored originals and history were restored by the normal
service launch. Earlier real HF sign-in/storage/restart evidence remains in the
prior acceptance. No new GPU inference or held-out-F1 reproduction was performed.
Official ranks and original-response publication remain off; Task 3 is classifier-
limited, Task 4 descriptive and Task 5 simulated. Recurring backup remains off.

Machine-readable [current receipt](validation/public-registration-rc6-20261019.json).
The [rc.5 acceptance](PUBLIC_SERVICE_ACCEPTANCE_RC5_20261019.md) preserves prior
evidence with its dates and scope; its runtime revision is superseded.
