# Changelog

## 0.3.0rc22 — 2026-10-21

- Fix individual Task 3 semantic ordering, separate filtered comparisons from whole-paper tables, and name the two rate-difference denominators.
- Dock selected evidence below its chart; show cell counts/completion and supported-contrast entry points.
- Add exact Task 4/5 condition buckets to the shared analysis engine and numerical profiles.
- Reconcile all twelve historical models with raw archives; release numerical-only per-model lazy assets, all 15 strategies, co-inclusion, seven outcomes and matched-input response/choice correspondence.
- Keep original paper scores, current strict diagnostics and publication policy unchanged; distinguish historical partial parsing and two missing-tool decisions.


## 0.3.0rc9

- Recover expired/missing temporary analysis sessions through an explicit
  connection check, preserving valid sessions on transient errors and never
  automatically replaying an upload. Stop remaining uploads on confirmed expiry.
- Read validated durable generation journals in pipeline status. Distinguish
  retained successes, known errors, interrupted unknown attempts and pending work;
  recommend resume/compaction before export without mutating the run.
- Recover stale selected registrations through a read without page reload.
  Preserve unsaved metadata/reasons, clear sharing consent and require explicit
  retry; Refresh submissions also updates the selected state.
- Show allowlisted Task 3/4 classifier declarations beside scores and in profiles/
  numerical exports, with Task-specific filters and left/right comparison values.
  Existing metric values, generation cohorts and official rank policy are unchanged.


## 0.3.0rc8

- Preserve successful files through partial batch upload failures, display file
  outcomes and skip acknowledged unchanged files on explicit retry. Reconcile
  exact duplicates through the current session without blocking later files.
- Distinguish latest private and current public revisions in owner guidance,
  profile/comparison buttons and numerical comparison headers. Publication still
  requires fresh explicit consent and never follows a private save automatically.
- Document revision replacement and separate transport/parse/truncation,
  measurement and stale-export recovery decisions. Metric calculations are unchanged.

## 0.3.0rc7

- Preserve an explicitly selected leaderboard collection across catalog refresh
  and URL reopening; selecting conditions clears an earlier model focus.
- Distinguish catalog loading from zero search matches and comparison settling
  from an actionable Compare prompt; discard obsolete results as before.
- Explain canonical Task 3/4 overlapping source sets with a diagram and counts.
- Add provenance field sources, resource planning and stage completion examples;
  consolidate repeated recovery instructions. Metrics and input sets are unchanged.

## 0.3.0rc6

- Search all public model collections and registration aliases from the home;
  use one navigation/focus path from search, details and the owner's registration.
- Show one row per exact original, retain alias discovery, and compare different
  originals consistently from every entry point.
- Correct model-name descending order and explain historical severity codes and
  percentage units without changing source measurements.
- Add read-only `koevd-results check-run` to detect stale exports after recovery
  or remeasurement while preserving failed/unmeasured observations.
- Pin the guide to this release and link deployment evidence to its living record.

## 0.3.0rc5

- Clear comparison results and downloads after selection changes; discard late network responses.
- Keep the model and paper/registered collection from details through comparison.
- Correct descriptive strategy labels and Task 1/4 alphabetical display order.
- Explain score denominators, coverage and evaluation groups next to the table.
- Align the beginner guide and private-save/public-sharing handoff with all four views.
- Preserve evaluation numbers, admission policy and original results.

## 0.3.0rc4

- Default model leaderboard includes all 12 paper models, with search, task tabs,
  metric sorting and separate registered evaluation groups.
- Model details, comparison and submission use separate navigation screens.
- Twelve exact aggregate source tables cover paper Tasks 1–5. Task 2 compares
  three common variants; Task 1 missing judgments stay N/A; Task 5 retains its
  all-expected denominator. Paper comparisons remain aggregate-only.
- Existing owner registration, recovery, consent and public paired API values
  are preserved. No GPU accuracy or official ranking activation is claimed.


- Public model loading no longer waits for account checks or a private analysis
  session. Private sessions start when the submission workspace is opened.
- A compact first-screen model table and Task 1–5 tabs expose counts, coverage,
  four choice variants, three tool framings and descriptive strategy frequencies.
- Historical paper tables are a separate aggregate-only collection with exact
  source provenance, distinct input counts and no fabricated current registrations.
- Saved originals can be imported into private analysis directly. Saving and
  numerical sharing have explicit, separate status messages.
- `koevd-pipeline --stage status` and final run summaries identify failed/pending
  generations and incomplete or invalid measurements without changing run data.
- See current service acceptance for actual deployment and validation scope.

# 0.3.0rc2 recovery and model discovery

- Preserve validated measurements before retrying failed generation; changed
  Task 3 responses require new Task 3/4 measurements. Interrupted retries remain
  blocked and resumable. Existing integrity checks remain enforced.
- Retry service connection also reconnects private analysis, preserving valid
  sessions and uploads. Concurrent retries share one session request.
- Find published models across evaluation groups and jump to your shared model.
- Explain metric direction and accuracy/error rates; pin the first-user guide
  to this release and mark private analysis as optional before registration.
- See current service acceptance for tested source/runtime versions and limits.

# 0.3.0rc1 public registered research service

- HF-owned submission metadata, original-declaration confirmation and explicit
  consent for numerical summary publication, separate from reviewed originals.
- Acknowledged checkpoints with conditional private HF/S3 state, restore and
  stale-instance/withdrawal fencing; activation and initialization remain opt-in.
- Cached public profiles, metric search/display sorting, complete published-run
  pair choices and exact-input comparisons without fabricating official ranks.
- Five bounded public numerical export formats, current-publication rechecks,
  explicit units and scriptless offline reports. No original cases are exported.
- Actual private HF OAuth registration, scoped state writes, original/history
  restore, numerical consent, duplicate accounting and withdrawal survived two
  restarts. Hosted points/denominators matched the retained offline oracle.
- Public-first model exploration, direct section navigation, explicit embedded
  sign-in guidance and environment-specific registration notices.
- Lossless browser gzip uploads and negotiated report downloads, with separate
  wire/expanded bounds, damaged-stream rejection and unchanged original bytes.
  Identity/session responses are excluded; ranged downloads stay uncompressed.
- Materialized contexts preserve provider LFS attributes and declare large assets.
- Actual public HF acceptance passed full gzip upload, owned registration, rename,
  metrics-only consent, withdrawal, re-login after server restart, exact private
  original/history recovery, 94 board values and all 15 numerical downloads.
- Main CI passed 471 checks on each of Python 3.10 and 3.12. CPU Basic/single
  replica, official-rank exclusions and existing tags remain unchanged.
- See the dated hosted acceptance receipt for exact runtime and scope; no new
  inference, raw-response publication or classifier-accuracy claim.

# 0.2.0rc1 platform public beta

- Portable validated results, resumable execution and shared offline/CPU/browser analysis.
- Full two-target GPU evidence, measurement audit, paired comparisons, metadata charts and complete case coverage.
- Pinned private reference originals with an explicit post-analysis public display projection; metrics and denominators remain unchanged.
- Anonymous temporary analysis beta; persistent publication, official ranking and continuous backups remain inactive.
- Python 3.10 SQLite full/busy failure compatibility and atomic rollback; unrelated errors are preserved.
- Current local CPU and full-reference browser validation; actual GitHub Python 3.10/3.12 CI passed after the compatibility fix.
- Public documentation removes internal validation paths; original evidence and historical v0.1.0 remain preserved.

# 0.2.0 own-model analysis pipeline

- Prepare, generate, classify and report Task 1–5 with `koevd-pipeline`; preserve source joins, all framings and failed rows.
- Generate HTML/Markdown/JSON/CSV diagnostics, metadata contrasts with coverage/source thresholds, strategy distributions, error cases and exact-input model comparisons.
- Task 3 source union supports Task 5 transitions and explicitly labels split membership.
- Durable response journals replace repeated full-file rewrites; resume compacts one result per sample and detects changed configurations.
- CPU tests cover real local HTTP integration with classifier doubles, missing/stale outputs, interrupted resume and report invariants. A subsequent [live pipeline test](docs/PIPELINE_VALIDATION_RESULTS.md) completed with the original source; batch sensitivity and concerning safety judgments remain unresolved.
- Correct package `__version__` to match distribution metadata. Prior classifier wrappers, parsers and scorer formulas are unchanged; the `v0.1.0` tag/assets remain immutable.

# 0.1.0 publication preparation

- Installable src package and separate parsers/metrics, preserving old score imports.
- Explicit local/pinned-HF adapter paths, with user-cache storage rather than writes into installed packages.
- Duplicate strategy labels count once per response.
- Resumable API output validates model/config/input identity and replaces failed attempts instead of double-counting them.
- Portable corpus statistics, grouped task metrics, matched Task 3/5 analysis, aggregate-table plotting and regression tests.
- Data, model weights and code staged in separate repositories; no upstream base weights or internal training pool included.
