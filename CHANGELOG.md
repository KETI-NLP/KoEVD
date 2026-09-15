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
