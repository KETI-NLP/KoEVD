# Public registration service acceptance

Updated 2026-10-20. **Release v0.3.0-rc.18 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Use the [pinned first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.18/docs/GETTING_STARTED.md)
and [original paper data guide](PAPER_TASK3_TYPE_AGGREGATION.md).
[Previous rc.16 acceptance](audit/public_service_acceptance_rc16_20261020.md)
preserves the registered-model safe/unsafe chart correction and earlier service evidence.

## Original paper models now support type analysis

The prior public app included only summary tables for the twelve paper models.
The project's original predictions and input metadata were available. They have
now been audited and reaggregated: **12 models × 13,552 sources = 162,624 original
model/source records**. Input/prediction metadata and complete source inventories
match, with duplicate/missing records rejected. Total/classified/unsafe counts
match the paper summary for every model. All earlier Task 1–5 model values are unchanged.

The public numeric source contains 132 model/type groups and 2,148 exact
type/topic, type/severity and type/explicitness cells. An independent SQL scan
checked all 2,280 cells against the original rows. Data files record original
input hashes and sizes. Historical metadata is retained without applying later
corpus overlays. No prompts, responses, rationales, source IDs or per-case
predictions are published, and no generation or classifier was rerun.

On the initial **Paper experiment · 12 models** leaderboard, open any model's
**Details → Task 3 → Safe and unsafe responses by user-input type**. The default
stacked bars show classifier-safe and classifier-unsafe, with rate/count and
safe-only/unsafe-only views. Type search, exact conditional drilldown and
**Compare selected type with another model** preserve analysis controls.
All 66 paper-model pairs are available in the separate paper comparison collection.

Safety rates divide by classified responses, and completion divides by all
expected original sources. Missing outputs never become safe. For example,
GPT-5.4 retains 10,819/13,552 classified responses and 2,733 unclassified records.
In Proverb/Term Meaning, it has safe 46 and unsafe 15 out of 61 classified / 64
expected, compared with Apertus 8B's safe 30 and unsafe 34 out of 64/64.
Displayed percentages can differ slightly from 100% after rounding.

## Verified source and deployment

- Application source `e4b0f5ac572e2ac04a1f695fa7a8e43bbf67137f`, [PR #39](https://github.com/KETI-NLP/KoEVD/pull/39),
  and [Windows-checkout PR #40](https://github.com/KETI-NLP/KoEVD/pull/40),
  merged as `918c2d7254ca9421af66294c435000bd9c38e148`. Immutable
  [v0.3.0-rc.18](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.18), package/module `0.3.0rc18`.
- Running HF revision `8a52997955b25517dddf7d182ac9c40e3ea48a01`.
  All 7 changed files (65,673 bytes) match remote bytes;
  80 materialized source files match Git. Data/JS URLs include version/content hashes.
  Two code deployments, including the Windows packaging follow-up; no manual restart or rollback.
  The first transferred 9 code/numeric files (1,370,784 bytes); the final version
  update transferred 7 files (65,673 bytes) and kept the paper data byte-identical. CPU Basic, one replica,
  provider LFS, operator inputs, State, Secrets and resource settings are unchanged.
- **545 local CPU tests passed**, plus final-source Python 3.10/3.12
  [final source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39373465435) and
  [final PR CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39373471297).
- The first rc17 Windows installation exposed Git newline conversion of the numeric
  source file: the data values were unchanged, but the recorded raw-byte hash did
  not reproduce. A scoped byte-preserving Git attribute fixes that issue without
  changing numeric data or the HF provider LFS rules. The failing receipt is
  retained; rc17 was not retagged.
- Fresh public-source clone at the exact immutable tagged commit and isolated hub+serve install passed pip check, versions,
  CLI commands, **47 focused tests** and **436 exact Git manifest entries**.
- Shipped-renderer checks cover **13,680 chart observations** across all twelve
  models and **396 comparison views / 66 distinct model pairs**. Builder tests
  reject duplicates, missing sources, metadata mismatches, contradictory labels
  and changed paper totals. Incomplete coverage, overlapping topics and old
  profiles without type data retain explicit behavior.
- The real public browser flow passed initial paper leaderboard → GPT-5.4 details
  → type selection → input-severity breakdown → Apertus comparison, including
  rate/count and safe/unsafe switching. JSON export generation passed for 22
  overview observations and the exact selected-type breakdown. Browser filesystem
  download completion is not claimed.
- Hosted health/configuration, profiles, comparison, assets and pages passed
  **24 anonymous GET checks**. The served paper data exactly matches
  the locally audited 12-model asset. Existing registered leaderboard, public
  revisions and paired statistics equal the pre-update snapshot. No upload,
  sign-in, registration write or raw-response publication was needed.

Historical paper and current-protocol registered models remain separate
collections. Cross-model type-rate differences use each model's own classified
denominator; they are not jointly valid paired effects or significance tests.
Small groups remain visible and flagged. Classifier-safe is a measurement proxy,
Task 4 is descriptive, and Task 5 is simulated. No combined ethics score,
official ranking or new storage/retention policy was enabled.
