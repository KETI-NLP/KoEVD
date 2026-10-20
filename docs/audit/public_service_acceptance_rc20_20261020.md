# Public service acceptance: Task 3 interpretation and exploration

Updated 2026-10-20. **[v0.3.0-rc.20](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.20)
is deployed** in the [public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
See the [first-user guide](GETTING_STARTED.md), [Task 3 chart guide](PUBLIC_PROFILES_GUIDE.md#task-3-type-analysis)
and [machine-readable acceptance receipt](audit/task3_clarity_rc20_receipt_20261020.json).
[Previous rc19 acceptance](audit/public_service_acceptance_rc19_20261020.md)
preserves the original four-axis aggregation and deployment evidence.

## What changed

- Grouping, input conditions and group/cross-chart display controls are separated,
  before the filtered summaries. Classification completion, unclassified counts
  and small source support remain explicit. Unsafe/classified is the primary
  observation; unsafe/all expected is supporting information, not a standalone
  safety score. Low completion and differences in completion are flagged.
- Multi-label topic/type selection retains the exact intersection: applying Taste
  inside Gender keeps Gender ∩ Taste rather than broadening to all Taste inputs.
  Required memberships have removable chips, survive reload and follow detail
  into model comparison. Per-scope condition undo remains local to the page.
- Safe heatmaps use teal and unsafe heatmaps red. Cross charts share domains/scales,
  align on wide screens and stack on narrow screens. A selected cross cell shows
  both models' classified denominators, completion and unclassified counts.
- The independent fixed-unsafe difference panel explicitly ignores Safe/count
  display switches while retaining input filters and label search. Symmetric axes
  adapt to ±5/10/20/50/100pp, with the full range selectable and labelled.
- Higher/lower screening candidates compare each group with disjoint remaining
  inputs in the same cohort. Both sides require 20 classified sources and 90%
  completion. Excluded groups retain concrete reasons; no candidate or a zero
  observed rate is not proof of safety. Semantic row ordering is explicit.

## Verified behavior and numerical evidence

**551 CPU tests passed** locally with the pinned production dependencies. Python
3.10 and 3.12 passed the complete suite in both source CI runs. A fresh GitHub
checkout and independent install passed **41 focused tests**, CLI checks, pip
check and the exact 443-file release manifest; the release tag matches the tested
application source. Renderer checks cover **9,636 marginal/cross cells** and
**516 independently summed disjoint contrasts** across all 12 historical models.

Actual anonymous public-browser checks covered the initial 12-model leaderboard,
co-topic selection, detail-to-comparison handoff, condition recovery, keyboard
cross-cell evidence, Safe/count heatmaps, fixed pp differences, screening reasons
and registered-model comparison. At a 390px viewport the paired chart stacked in
one column and the document did not overflow (375px document width).

Concrete observations (different cohorts must not be pooled):

| Cohort | Model 1 unsafe/classified | Model 2 unsafe/classified | Expected/model |
|---|---|---|---|
| Paper GPT-5.4 vs Apertus 8B: Gender ∩ Taste | 0/8 | 3/11 | 11 |
| Paper GPT-5.4 vs Apertus 8B: Gender, High, Implicit | 6/69 | 7/98 | 98 |
| Registered Qwen3-8B vs 4B: Core, Gender | 3/147 | 4/147 | 147 |

In the second row completion is 70.41% versus 100%; the observed unsafe-rate
difference is +1.55pp. A ±5pp axis makes it visible without changing the value.
Each model uses its own classified outputs; this is not a jointly valid paired
effect, significance test or causal bias finding.

**16 anonymous GET checks** verified health/readiness, policy, public catalog,
both registered profiles, their comparison, code assets, all 12 paper models and
page routes. The public leaderboard, published revisions and existing comparison
including paired statistics match the pre-update JSON exactly. Seven remote
repository files matched the candidate byte for byte; served text assets matched
the server's existing UTF-8/newline normalization. No original responses were
uploaded or disclosed during this acceptance.

## Source and deployment

- Application source `1ae7cd6218f7ae840a29687dcce19d8255f9af1a`; [PR #46](https://github.com/KETI-NLP/KoEVD/pull/46) merged.
- [Source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39414394257) and
  [PR CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39414402630) passed.
- Space revision `8f852f549b20f89bd690e16bc5ade45c72c79608` is RUNNING on CPU Basic, one replica.
- Seven code/metadata files, **173,534 bytes**, changed. One automatic
  build/start; no rollback. Operator inputs, LFS rules, State/Secret/resource
  policies and existing data were preserved. No new inference or raw-result upload.
- Registration and consent-based numerical sharing remain enabled. Official ranks,
  raw-response publication and continuous backup activation were not introduced.
