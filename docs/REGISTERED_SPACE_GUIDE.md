# Registered Space deployment candidate

This candidate connects registration, explicit summary publication, public
profiles/metric comparison and private conditional state. The existing anonymous
production launcher is preserved. Local API, CPU and container results do not
prove actual HF login, storage or deployed G1–G12 acceptance.

## Prepare the context

From the repository root, use the previously validated source-only input context
and exact reference asset configuration:

```bash
python scripts/materialize_registered_space.py \
  --repo . --base-context /path/to/validated-input-context \
  --reference-assets /path/to/reference-assets.json \
  --output /path/to/fresh-registered-context
```

The output contains pinned input indexes, protocol definitions, current source,
the registered Dockerfile, CPU dependency lock and native OAuth README metadata.
It excludes actual model response originals, submission DBs and credentials.
Reviewer/admin configuration starts empty and does not inherit old approvals.
Check deployment-manifest.json and its exact file hashes before upload. The
manifest's `actual_hosted_acceptance` remains false until independent hosted checks.

The current export candidate has 76 files, approximately 75.7 MB uncompressed;
most bytes are the already public input indexes. Do not bundle the 8B/4B response
files or any existing development store as code.

## Runtime configuration

The target Space uses CPU Basic, one process/replica and native `hf_oauth: true`
with identity/profile scopes. The registered launcher captures its provider
configuration explicitly, then removes unrelated environment credentials. It
does not resolve CLI administrator credentials or an AWS profile as fallback.

| Configuration | Purpose |
|---|---|
| `KOEVD_REFERENCE_TOKEN` Secret | Existing reference Bucket read-only access |
| `KOEVD_STATE_BUCKET` variable | Separate existing private state Bucket owner/name |
| `KOEVD_STATE_TOKEN` Secret | Exact state Bucket read/write token; metadata checks use this token |
| `KOEVD_STATE_ACCESS_KEY_ID` Secret | S3 key generated from the scoped state token |
| `KOEVD_STATE_SECRET_ACCESS_KEY` Secret | Matching S3 secret |
| `KOEVD_STATE_INITIALIZE` variable | `1` only for approved first initialization; default `0` |
| `KOEVD_REGISTRATION_ENABLED` variable | Explicit `1` after activation approval; default `0` prevents reference/state access |
| `KOEVD_STATE_MAX_DATABASE_BYTES` variable | Checkpoint DB cap; limited trial uses 134217728 |
| `KOEVD_STATE_MAX_RETAINED_BYTES` variable | Retained object cap; limited trial uses 1610612736 |
| `KOEVD_STATE_MAX_SEQUENCE` variable | Hard sequence cap; limited trial uses 12 |
| `KOEVD_REGISTRATION_ENVIRONMENT` variable | `hosted_candidate` by default; `hosted_service` for approved production |

Reference and state tokens must be distinct. State storage cannot use either
existing reference/periodic-backup Bucket. Native Space OAuth supplies the app ID
and secret; it is separate from these data-access tokens. Never send secret values
in chat or encode them in README, Docker build arguments or result artifacts.

On 2026-10-14 the goal's new private State-Dev Bucket and private CPU Basic
Registration-Dev Space were created as preparation only. The Space is paused,
activation/initialization are both 0, and the Bucket contains zero objects/bytes.
Source/public-index context revision 79ed3c012e86d29237c808303dcb9302ab336f98
contains no response originals, submission DBs or secrets. New original transfer
and finite live testing require the separately requested scope; creation alone
does not authorize them. Dedicated secret values must be entered by the user.

The registration UI now fetches the selected upload's original model/generation/
measurement declaration through its private analysis session. Missing revisions
remain unknown. Saving/revising in the UI requires a fresh confirmation for that
selection; changing the selection resets it. The declaration endpoint returns
no original response text and denies another session or expired access.

Public metric exploration permits name/model/revision search and observed-value
display sorting. This does not assign official ranks; the official-rank column
and verification/reasons remain unchanged. Pair choices use the complete bounded
publication snapshot, including runs beyond the first catalog page. A failed
refresh clears old profiles, metric rows and pair choices rather than presenting
them as current authoritative results.

Public profile/pair numerical downloads are documented in
PUBLIC_NUMERICAL_REPORT_GUIDE.md. They return numerical snapshots only, with
publication checked again after rendering. Response sharing never implicitly
includes a private result download in these formats.

## Initial references and restart

First initialization requires a verified empty state namespace and explicit
opt-in. Both pinned reference files are validated before any state upload. The
operator-local owner is `koevd-operator-reference`; it does not pretend to be an
HF user. Both references are inserted and consented numerical publication events
are prepared locally, then acknowledged as one consistent remote checkpoint.

A subsequent start restores that exact current authority. It preserves original
hashes, submission IDs, audit history and withdrawal. It does not insert another
copy, change reference display metadata or republish a withdrawn reference.
Existing state without the required reference intake is rejected for explicit
migration rather than silently rewritten. Generation remains user-reported until
independent evidence is accepted; an operator reference label is not a certificate.

The launcher warms numerical admissions before serving. Anonymous reference
analysis retains the existing text-withheld disclosure. Registered numerical
profiles never include raw cases. Original response publication still needs
independent permission review. Official ranks remain disabled and no aggregate
ethics score is produced. See ACKNOWLEDGED_STORAGE_GUIDE.md for commit/fencing,
capacity, current-cut restore and failure behavior.

## Evidence and remaining work

The candidate's initial local checks passed 8 bootstrap/configuration scenarios.
The materialized registered app also passed local HTTP inspection using both
existing actual 17,670-record results and fictional S3/OAuth: registration enabled,
two anonymous operator entries, profiles/comparison, raw-original 403 and one
initial checkpoint. This did not contact HF or run new model inference.

The Docker candidate was built on b200-1 and ran 27 synthetic tests with network
disabled, 2 CPUs and 6 GiB RAM. The validation container and image were removed;
private source/log copies remain. Full local CPU regression passed 446 tests.
The earlier shell wrapper had an exit-status quoting error after image creation;
the image digest and subsequent container checks independently established build
and test success. It was not blindly rebuilt or called a hosted acceptance.

Private evidence is retained in generated/public-service-20261014-v9/. Required
next work is an explicitly scoped HF trial: target/resource/Secret preparation,
real S3 preconditions/readback, native account ownership, restart/re-login,
withdrawal and actual public service checks. Preparing or building this context
does not authorize new original-data transfer, standing backups or paid resources.
