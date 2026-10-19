# Public registration service acceptance

Updated 2026-10-19. **Release v0.3.0-rc.7 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Follow the [pinned complete first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.7/docs/GETTING_STARTED.md).
Its deployment link and the Space's **Deployment and version** link point to
this living record; immutable tags retain their original historical evidence.

- App source `97509cb93b58a8011fa6a8b0d6aaa722e899f97f`, [PR #20](https://github.com/KETI-NLP/KoEVD/pull/20),
  normal merge `b499e04d65f887e15da07664996b172322c78ca1`.
  Immutable [v0.3.0-rc.7](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.7)
  fixes that merge; module/package version is `0.3.0rc7`.
- Running HF Space revision `883261b7d449b3c237a62ea6816ddd38c8492010`. All ten changed
  files (122,829 bytes) match remote bytes; all 78 materialized
  source files match Git. CPU Basic, one replica, provider LFS, operator inputs,
  State and Secrets are preserved. Two bounded code/introduction updates; no manual restart, rollback or new resource.
- [Source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39206367426) and
  [merge CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39206587252) passed
  **516 tests each on Python 3.10 and 3.12**. The local full CPU suite passed
  516 tests. A fresh public-tag clone/isolated hub-extra installation passed
  dependency/version/CLI checks, 20 focused tests and all 394 manifest entries
  against exact Git blobs, without a source PYTHONPATH override.

## Selection, loading and interpretation corrections

Following a focused model, explicitly choosing another evaluation collection,
refreshing and reopening the condition URL now retain the chosen table. Explicit
collection changes remove the old focus; focused model links still restore their
group until another condition is selected. Paper and registered scores remain
separate. Cross-collection search, duplicate aliases and one-row-per-original
behavior remain intact.

Search says in progress while registered results load, then updates automatically;
it does not report a completed zero-match search. Changing a comparison selector
clears obsolete results and explains the wait while its prior request settles.
The actionable instruction and Compare button return together afterwards.

Canonical Task 3/4 diagrams explain core 2,000 + Task-5-linked 784 - common 125 =
union 2,659 (1,875 core-only, 125 shared, 659 tool-linked-only). The 659 additional
sources are not the full tool-linked subset. Custom subsets and valid measurement
denominators can differ. No inputs, numerical calculations or paper tables changed.

The guide adds actual provenance field sources, an explicitly fictional filled
example, resource planning and stage completion examples. A current export can
retain failed generation or unmeasured responses. Run readiness, export freshness,
task usability, private saving and optional numerical sharing have separate checks.
Repeated recovery instructions are consolidated. The Space introduction also pins
the rc.7 guide; the generation helper now derives that link from the package version.
A separate local regression checks current and future prerelease links. This helper
correction is retained on main; the immutable rc.7 app tag remains unchanged.

## User journey evidence and limits

The localhost browser used fictional 12-record results and synthetic OAuth. It
passed held-catalog loading, initial session failure/retry, private save and explicit
summary sharing, model discovery, collection refresh/reload, in-flight comparison
selection changes, completed comparison, saved-original recovery after reload,
five-format CPU report generation, withdrawal and fresh-consent reshare.
The shipped-JavaScript test exercises the corrected URL/loading/waiting paths.

Anonymous production checks passed health/readiness, registration configuration,
catalog, both profiles, full comparison, shipped assets and the four page paths.
**All 94 public metric rows and the entire paired response exactly match the
pre-deployment projections.** Browser checks verify default 12-model discovery,
condition preservation after refresh/reload, subset diagrams, real Qwen3-8B/4B
comparison and pinned guide/version links.

No new real original upload or production owner mutation was performed. Browser
owner flows used localhost fictional data; actual hosted checks were anonymous
reads. The normal launch restored current acknowledged state. Earlier actual
OAuth/save/restart evidence remains in the prior records. No GPU inference or
held-out-F1 reproduction was repeated. Official ranks, original-response publication
and recurring backup remain off. Task 3/4 measurements remain classifier-limited;
Task 4 is descriptive and Task 5 tools are simulated.

Machine-readable [current receipt](validation/public-registration-rc7-20261019.json).
The [rc.6 acceptance](PUBLIC_SERVICE_ACCEPTANCE_RC6_20261019.md) preserves its
original dates and scope; its runtime revision is superseded.
