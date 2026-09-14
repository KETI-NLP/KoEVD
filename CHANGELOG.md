# 0.1.0 publication preparation

- Installable src package and separate parsers/metrics, preserving old score imports.
- Explicit local/pinned-HF adapter paths, with user-cache storage rather than writes into installed packages.
- Duplicate strategy labels count once per response.
- Resumable API output validates model/config/input identity and replaces failed attempts instead of double-counting them.
- Portable corpus statistics, grouped task metrics, matched Task 3/5 analysis, aggregate-table plotting and regression tests.
- Data, model weights and code staged in separate repositories; no upstream base weights or internal training pool included.
