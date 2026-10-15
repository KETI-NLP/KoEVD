# Local upload and reference-comparison app (development candidate)

**Current public service (2026-10-15): v0.3.0-rc.1.** Actual HF-owned registration,
confirmed private storage/restart, consented summary sharing/withdrawal, two-model
public profiles/comparison and 15 numerical exports passed. Start with the
[user guide](PLATFORM_USER_GUIDE.md) and [current acceptance](PUBLIC_SERVICE_ACCEPTANCE.md).
Official ranks and original-response publication remain disabled. Earlier beta,
local-only and pending statements below retain their dated historical scope.

**Public beta v0.2.0-rc.1:** new disclosure projection and private pinned reference transport passed 374 CPU checks and full actual one-upload/reference browser acceptance. See [deployment scope](PUBLIC_BETA_DEPLOYMENT.md) and [local beta evidence](validation/platform_public_beta_local_v94.json). The earlier checkpoints below retain their dated scope.

An additional [Static candidate](STATIC_SPACES_GUIDE.md) runs the unchanged
Python analysis engine in a browser worker and keeps selected files local. It
preserves this server app and does not replace its identity/submission/storage
acceptance requirements. The Public Static preview and separate private CPU Docker
app have now been deployed; see [current operations](TEAM_SPACE_OPERATIONS.md).

The M5 CPU app now validates full result uploads, uses operator-selected trusted
inputs, runs the shared analysis engine, compares matching cases, previews the
same offline HTML and provides all report downloads. Two actual full target-model
results passed independent raw replay, local/node/HTTP profile agreement and
offline browser checks; see [the full two-model evidence](validation/platform_m4_m5_full_two_actual_20261009.json).
Submission/storage/ranking code is implemented with no official ranks granted by
the default policy. Actual private HF login/draft saving and all5 native report
downloads pass. Actual CPU_VALIDATION_NODE container analysis and bounded private HF backup/fixed
restore have also passed; continuous backup and production recovery release remain
inactive. Two rights-holder-approved actual research references are available in
the [local candidate](ACTUAL_REFERENCE_CANDIDATE.md), with no external posting.
See [the current checklist](PLATFORM_RELEASE_CANDIDATE.md) for dated scope.
The private Docker is a development app, not production.

For server report downloads, select a report button to prepare the file, then click
the visible **Save filename** link. Only one prepared link is retained; deleting or
replacing the analysis session removes it. See the [managed candidate guide](MANAGED_SPACE_GUIDE.md)
for the separate, unactivated server/backup startup profile.

## Try the explicit fictional demonstration

Run from the repository root in a CPU environment:

```bash
python -m pip install ".[serve]"
python examples/make_demo_space.py --output-dir generated/space-demo
koevd-space --catalog generated/space-demo/catalog.json --demo \
  --host 127.0.0.1 --port 7860
```

Use a new/empty demo directory. Open `http://127.0.0.1:7860`, select
`generated/space-demo/SYNTHETIC-A.json`, and click **Validate and add results**.
Select the explicitly fictional SYNTHETIC-B reference and click **Build analysis
and comparison**. Explore all report tabs/cases and download HTML, profile JSON,
full cases JSONL, metrics CSV or Markdown. Alternatively upload both fictional
result files and leave the reference unchecked. Selecting an identical uploaded
artifact and reference is rejected rather than counted twice.

These outputs are fabricated fixture behavior, not model inference or research
results. The demonstration has 80 union/60 primary/40 tool sources and 580 records
per run. A real user must generate and measure their model before portable export.

## Operator-controlled input catalog

The server matches a result's input-index checksum against its own loaded catalog
and reconstructs prompt, gold and metadata from that index. A client cannot upload
an index, source URL/path, publication state or summary score to configure the
service. Every matching full result still passes the existing strict contract,
seal/expected-ID/input/measurement checks. Hash consistency is not target-model
identity or generation authenticity.

Catalog `koevd-space-catalog-v1` contains `indexes` and `baselines`. Each index has
`id`, `label`, `mode`, `path`, `sha256`. Paths are operator-local files relative to
the catalog or explicit operator absolute paths; the service does not fetch URLs.
The byte checksum pins the file; the content seal and complete index are validated.

- `standard` additionally requires `registry` and `protocol_id`, and must pass
  `ProtocolRegistry.validate_index` against the fixed protocol/input set.
- `operator_custom` is an independently chosen local index and cannot assert a
  standard protocol; outputs stay exploratory.
- `synthetic_demo` requires explicit `--demo`, a nonstandard input set, and a visible
  fictional-reference notice. It cannot be promoted to actual target outputs.

An actual operator catalog for the pinned full dataset follows this shape (replace
all placeholders and compute file SHA-256 before use):

```json
{
  "schema_version": "koevd-space-catalog-v1",
  "indexes": [{
    "id": "koevd-core",
    "label": "KoEVD registered core inputs",
    "mode": "standard",
    "path": "/operator/trusted_input_index.json",
    "sha256": "<SHA-256 of the index file bytes>",
    "registry": "/operator/protocols",
    "protocol_id": "koevd-core-canonical-v1"
  }],
  "baselines": []
}
```

The actual pinned 17,670-record index was loaded and registered-validated on this
Windows host; see the validation checkpoint. This does not prove GPU performance.
Select catalog/index independently; never copy an uploader's index into it without
operator verification. Registry version and preparation digest remain fixed.

## Reference files and publication scope

A reference entry has `id`, `label`, `index_id`, `path`, `sha256`, `scope` and
`publication_evidence`. Synthetic references require demo mode, the synthetic
index and `publication_evidence: null`. Actual target outputs require a separate
operator attestation: `consent: operator_confirmed_raw_publication`, a nonempty
`rights` explanation, and a pinned `evidence_path`/`evidence_sha256` local document.
That attestation confirms the operator's publication decision; it is not an
automatic GPU reproduction or identity-verification badge. The separate local
research-reference candidate records the rights holder's permission for two
actual results and retains KoEVD research terms and content warnings. It does not
change the default deployed catalog or authorize external posting. No old corpus
response is relabeled as a new model baseline. Bytes are rechecked before each
analysis to detect reference edits.

## Sessions, request boundaries and retention

A random session bearer and request token are generated per page, held in browser
memory only and sent in request headers. They are never placed in URLs, cookies,
localStorage or exported report files. The server stores a hash of the bearer.
This supports the HF embedded app without depending on third-party cookies; actual
HF iframe behavior remains a deployment verification gate. Reloading loses that
page's session access. No identity/authenticated public submission is inferred.

API requests require the correct session, mutation token and configured same
origin. Cross-site API requests and unexpected hosts are rejected. Main document
navigation can be embedded under the configured frame-ancestor policy; it does not
carry private data. Non-local listening requires an explicit HTTPS `--origin` or
`KOEVD_APP_ORIGIN`; trusted public origin is operator configuration, not inferred
from client/proxy headers. No wildcard CORS, secrets input or arbitrary file route
is enabled. Uvicorn access logging is disabled. Production reverse-proxy/TLS/access
policy and external abuse defenses still require deployment review.

Uploaded JSON is streamed with both Content-Length precheck and actual-byte limit,
including unknown/chunked lengths. Non-JSON HTML/ZIP/pickle is not accepted. Files
use server UUID names; original filenames are not filesystem paths. Ambiguous JSON,
unknown fields, uploaded gold/scores and unsupported result forms are rejected.
Partial/failed uploads release their reservation and do not become selectable runs.

Defaults: 128 MiB/file, 4 uploads, 256 MiB total uploads/session, 32 live sessions,
2 GiB service temporary capacity, 512 MiB reserved report capacity/job, one analysis
worker and at most two running/queued jobs. Because capacity is reserved up front,
an otherwise small upload can be refused when remaining reserved capacity is low.
A session allows one active upload/analysis. Computation runs outside the request
loop; job states queued/running/complete/failed are polled. Unknown or incompatible
conditions remain in the completed report's comparison reasons rather than being
silently declared comparable. Client stack traces/operator paths/raw error details
are not exposed.

Sessions expire after 120 minutes from creation. The service sweeps every 30 s;
busy work is cleaned when it finishes, and expired access is rejected immediately.
Use **Delete session data** to remove uploads/reports and revoke access; active work
must finish first. Removing an upload also invalidates its generated report. The
single-process directory is ephemeral, requires a new/empty owned root and is
cleaned at graceful shutdown. Abrupt process/host failure can leave disk remnants
until the operator cleans/replaces that temporary root; it is not restart-persistent
private submission storage. Never point it at a shared/preexisting data directory.

Report preview is a sandboxed Blob iframe with no same-origin permission; parent
credentials stay outside it. Only packaged, hashed report code/style may run.
Prompt/response/model text uses inert JSON and DOM text nodes. Exact profiles are
downloaded through the same session authorization. Filtering changes the view,
not the scoring denominator. No actual tool, model or remote source fetch is run
by this app. Session upload is separate from future public registration.

## Tests and browser evidence

```bash
python -m pip install ".[serve,dev]"
python -m unittest discover -s tests -v

# Optional Node/Playwright developer check; start the app first:
node scripts/validate_space_ui.cjs --origin http://127.0.0.1:7860 \
  --fixture-dir generated/space-demo --output-dir generated/space-ui \
  --security-result /path/to/explicit-adversarial-result.json \
  --browser-executable /path/to/chrome
```

The UI gate specifically expects the checked-in fictional demonstration. Generate
its adversarial input with `examples/make_demo_diagnostics.py --adversarial`, in a
separate empty directory. Add `--expected-profile /path/to/profile-v2.json` from an
independent `koevd-diagnose` call using the same A/B files/index and 100 resamples,
seed 1729, to check complete app/local JSON equality. Tests launch fresh browser
contexts and use a real local HTTP server; they never inspect the user's browser.

See [PLATFORM_VALIDATION_LOG.md](PLATFORM_VALIDATION_LOG.md) and the M5 CPU checkpoint
for actually executed commands/results. HTTP tests need optional serve/dev packages
and otherwise skip; the current installed test environment ran them. CPU fixtures
are not GPU classifier/target inference or a complete security audit.

## Docker and future publication

[apps/spaces](../apps/spaces/README.md) contains the candidate Dockerfile and exact
observed web dependency lock. The actual CPU_VALIDATION_NODE CPU container passed individual
analysis for both full results and their paired comparison; all 15 downloaded
files matched the CLI. See [container evidence](validation/platform_m5_actual_b200_container_v92.json).
FastAPI/Docker is supported by HF Spaces; default disk is ephemeral,
and a Storage Bucket/dataset repository/other adapter is needed for persistent
accepted submissions. The previous persistent-storage YAML setting is no longer
supported. Organization plan, exact host/origin, storage mount, OAuth identity,
raw-reference rights and costs must be verified before public deployment.
No production push/Space creation/paid activation was performed.

Official sources checked 2026-10-08:
[Docker Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker),
[Spaces storage](https://huggingface.co/docs/hub/spaces-storage),
[Spaces configuration](https://huggingface.co/docs/hub/spaces-config-reference),
[FastAPI direct requests](https://fastapi.tiangolo.com/advanced/using-request-directly/).

## Separate local submission storage candidate

M6 has a separate local original/revision/event store, operator CLI and opt-in authenticated submission HTTP/UI; see [SUBMISSIONS_GUIDE.md](SUBMISSIONS_GUIDE.md). These do not make anonymous uploads public or Space disk durable. Operator CLI actor assertions are not OAuth. Metric-specific admission and a complete current-publication comparison are implemented; the default candidate policy grants no official rank. Actual private HF login and bounded cloud backup/fixed restore passed. Production policy activation and continuous durability remain separate operating conditions.

## Optional HF identity and submission candidate

The anonymous app remains the default. Opt-in consent/review/scope, candidate publication, withdrawal, metric comparison and response reimport have synthetic HTTP/browser/restart evidence. [OAUTH_SUBMISSION_GUIDE.md](OAUTH_SUBMISSION_GUIDE.md) describes OAuth app credentials, roles, origin and storage. Actual two-target full GPU evaluation, private HF login/draft saving, full analysis/download and CPU container execution passed with their dated receipts. Synthetic publication tests are not evidence that actual user results have been publicly posted. Default official ranking is disabled.

The registration UI provides **Compare published metrics** with a metric/evaluation-group selector. It recalculates only current approved revisions and displays numerator/denominator, source count, coverage and eligibility reasons. Excluded entries have no provisional rank. `/api/public/leaderboard` fails rather than returning stale withdrawn/revoked entries or silently ranking a partial page. See [rank admission](RANK_ADMISSION_GUIDE.md) for current limits and operator-registry configuration.


## Historical private HF deployment preparation — 2026-10-08

The following records describe the initial preparation and plan rejection.
Subsequent Team-plan deployment, login, full analysis and container validation are
recorded in the current RC checklist; the initial pending states are historical.

`materialize_development_space.py` creates an independent allowlisted upload root, copies the registered core index, prepares prefix4/prefix96 indexes from actual pinned data, validates the full operator catalog and writes a file checksum manifest. Generated responses/weights/auth caches are excluded. Native hf_oauth metadata provides app credentials at runtime; `launch.py` derives origin only from SPACE_HOST. Temporary submission retention is explicitly shown in the landing page through escaped, bounded operator text; no extra script or relaxed CSP is introduced.

The Dockerfile requires this materialized root as its context. Use `docker build -t koevd-space-development generated/private-space-deployment-20261008` once the folder is prepared; this command has not been executed here. Actual container build/login/UI acceptance remain pending.

User-authorized private KETI-NLP/KoEVD-Explorer creation returned HF402 requiring an organization Team/Enterprise plan for Docker/Gradio cpu-basic hosting. The follow-up repo query returned404. No Space/upload/billing/paid resource exists from this attempt. The user was asked whether to arrange organization hosting, use a personal development Space or defer deployment. The prepared candidate is kept for the selected hosting route. See [service receipt](validation/platform_space_creation_20261008.json).


Hosting clarification (2026-10-08): official [Spaces Overview](https://huggingface.co/docs/hub/spaces-overview) states that Docker/Gradio compute Spaces require PRO for personal accounts or Team/Enterprise for organizations. CPU Basic has no hourly hardware cost; this does not waive the plan prerequisite. The current personal account returned `isPro: false`. The initially suggested free personal Docker fallback was corrected in chat and the pending hosting question. No personal Space or subscription was created. Static hosting alone does not satisfy the present server-side shared-engine/login/submission requirements.
