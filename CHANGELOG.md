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
