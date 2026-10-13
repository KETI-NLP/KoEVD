# Public beta deployment

Release candidate: **v0.2.0-rc.1**. The GPU generation/measurement evidence belongs
to its frozen execution source; new disclosure code does not rerun inference or
establish classifier accuracy. Default official ranking remains disabled.

| Surface | Function |
|---|---|
| KETI-NLP/KoEVD on GitHub | Evaluation, resume, measurement, export, offline report and app source |
| KETI-NLP/KoEVD-Explorer | Public Static personal analysis; uploaded files stay in the browser |
| KETI-NLP/KoEVD-Platform | Public CPU upload/analysis and comparison against two real full references |
| KoEVD-Platform-Dev | Separate private development environment |
| KoEVD-Platform-Backups | Private pinned reference objects; future operational backups remain off |

## Reference results

Qwen3-8B and Qwen3-4B each have 17,670 measured records and 15,011 generation
requests. Each Task 4 record reuses the corresponding Task 3 generation.
Numerical analyses, group denominators, quality flags, intervals and paired
comparisons are calculated from the unchanged, hash-pinned original results.

The exact original JSON files are private Bucket objects. The Space never puts
them in its public repository or serves them as raw original downloads. A
read-only, Bucket-scoped `KOEVD_REFERENCE_TOKEN` Secret initializes the two exact
objects; there is no administrator CLI-token fallback. The token is removed from
the app environment after initialization.

The beta's `koevd-public-reference-disclosure-v1` projection runs after analysis.
It withholds reference prompts, freeform responses, mock tool arguments and
execution/request identifiers while preserving all measured records, category
labels and numeric results. Original response hashes identify the undisclosed
original, not the placeholder text. Projected reports are not portable original
results and must not be reimported as such. Personal uploads retain their own
text inside their temporary isolated sessions. Classifier-safe labels do not
determine which raw examples may be published.

KoEVD's custom Research Use Terms, attribution and harmful-content warning apply.
Task 3 measurements remain limited, Task 4 is descriptive, response-conditioned
groups are diagnostic, and no combined ethics score or official rank is granted.
Later reviewed raw excerpts require a separate explicit disclosure policy.

## Initial public settings

- Docker SDK, CPU Basic, one replica, one analysis worker, no GPU or paid upgrade.
- Anonymous temporary upload sessions; source-cluster bootstrap 100, seed 1729.
- Up to 128 MiB per result and 256 MiB of uploads per session; two-hour session TTL.
- Shared login, persistent drafts, publication requests and continuous backups off.
- Five report downloads use the same analysis engine as the offline CLI; the
  reference display projection is explicitly indicated in HTML/JSON/JSONL.

`apps/spaces/public.Dockerfile` uses the pinned managed runtime dependency lock
for Bucket download support. The materialized context includes only source,
registered inputs, reference identities/hashes and research terms. It excludes
tokens, original reference responses, submission databases and backup history.

## Activation and verification

Create the production Bucket as private and store only the two pinned objects at
`references/<original-file-sha256>.json`. Set a fine-grained read-only token for
that Bucket in the new Space's `KOEVD_REFERENCE_TOKEN` Secret. The existing
development backup token is not reused or copied.

Validate the candidate before making the Space public: original/file hash checks,
complete CPU tests and GitHub CI, one-upload/reference analysis, numeric equality
to original native reports, all five projected downloads, isolation/deletion and
desktop/mobile visual checks. A failed reference initialization must refuse
startup; it must not present synthetic or missing references as actual results.

Operational persistence is a later stage: explicit retention/capacity bounds,
backup failure handling and independent restore/recovery acceptance are required
before saved submissions are advertised as durable. CPU hosting and reference
reads do not provide submission durability or a guaranteed recovery point.
