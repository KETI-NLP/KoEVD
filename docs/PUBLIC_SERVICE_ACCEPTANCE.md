# Public registration service acceptance

Updated 2026-10-15. **The public research registration service passed its bounded
acceptance trial.** [Open the Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform)
or follow the [user guide](PLATFORM_USER_GUIDE.md). Numerical comparison is active;
official ranks and original-response publication remain disabled.

- Application source: `064a013d2f8e558acdb217a57d20e4f653121677`, PR #4,
  normally merged as `ee7b5e32584954b023533061ddee6439ad66e95e`.
- Actual Space revision: `1bc4cbdf552a9999ca91c87d4cb2af81927ec44b`.
  Its 69 code/license/protocol files match the committed source blobs. Provider
  LFS attributes and every deployed Git/LFS file were verified before start.
- Distribution: `v0.3.0-rc.1` / Python package `0.3.0rc1`. Accompanying documentation
  changes do not change deployed application files or require another restart.
- [Main CI](https://github.com/KETI-NLP/KoEVD/actions/runs/38722314566): Python 3.10
  and 3.12 each passed 471 tests. [Aggregate hosted receipt](validation/platform_public_registration_hosted_20261015.json)
  contains hashes, counts and scope, without private originals or credentials.

| ID | Acceptance evidence | Scope |
|---|---|---|
| G1 | Independent anonymous browser lists two actual references and metric values | No upload/sign-in required |
| G2 | Full 17,670-record gzip upload; immutable model/generation/measurement declaration and separate display name | Same existing 8B artifact; no new generation |
| G3 | Actual native HF sign-in, private save, owner list and public summary URL | Account ownership does not verify generation |
| G4 | Explicit metrics-only rights/consent; public summary; private original returns 403 to public reader | No response-publication approval fabricated |
| G5 | Server restart and native re-login; private original and four-event history byte-identical before/after | One production restart, in addition to earlier dated private trials |
| G6 | Independent browser and anonymous HTTP reads; private history 401 | No administrative token impersonates app identity |
| G7 | Both profiles, metadata/framing/strategy controls and exact-input paired comparison render | Task counts 2000/8000/2659/2659/2352; raw cases withheld |
| G8 | Offline point values/denominators agree; all 94 board rows exact; all 15 numerical exports match renderer bytes | Bootstrap intervals excluded from oracle comparison |
| G9 | Actual duplicate counts once; full CI covers invalid/partial/configuration/conflict/fault handling | Fault injection remains local/CI; earlier private hosted duplicate evidence retained |
| G10 | Withdrawal removes catalog/profile/pair/downloads, including after restart; private history retained | Previously downloaded copies cannot be recalled |
| G11 | Actual CPU Basic/single replica, four confirmed checkpoints, restored owner state, desktop/mobile widths and zero console errors | Korean/untrusted-name checks retain earlier local scope; no availability SLA inferred |
| G12 | Versioned public source, exact runtime mapping, user guide and aggregate receipt accompany the new release | Historical tags preserved; docs-only updates do not alter runtime |

The validation upload was 6,022,832 compressed bytes and reconstructed the existing
44,779,573-byte original. Owner downloads use canonical JSON: the entire decoded
object equals the upload; their 33,589,402 bytes and the 8,086-byte history were
also exactly equal before and after restart. Events were create, display update,
summary publication and withdrawal, with one immutable result revision.

The 15 numerical exports total 63,796,419 decoded bytes and 3,465,141 wire bytes.
They contain no original prompts/responses or private history. Observed values
remain descriptive: Task 3 uses limited classifier measurements, Task 4 is not a
quality score, Task 5 selects simulated tools, and no combined ethics score exists.

Two starts were used. Four new checkpoints retained 268,703,380 bytes; total State
was 335,866,272 bytes. Initialization stayed disabled. DB/retained caps remain
2 GiB/8 GiB; no recurring backup worker, new paid resources or GPU work was enabled.
The test duplicate was withdrawn, leaving the two reference summaries public.
Registrations and audit copies are retained privately; withdrawal is not erasure.

The earlier LFS omission and incomplete plain-transfer trial remain failures in
their own scope. They were followed by the corrected compressed trial above.
The build manifest retains its pre-acceptance flag as an immutable build fact;
the separate dated receipt records later hosted acceptance.

## Historical checkpoints

The sections below are dated development records, not current pending gates.

## First implementation checkpoint

Final frozen source passed **400 CPU tests** in 154.216 seconds. Source hashes,
command outcome and local fixture scope are retained in
`generated/public-service-20261014-v1/full-cpu-receipt.json`. This includes
14 acknowledged-store/restore tests and 8 display/summary-publication tests.
The actual HF login, remote checkpoint adapter, cached public profiles, reference
intake, hosted recovery and production deployment remain unverified or missing.
The full goal remains active and incomplete.

## Numerical profile checkpoint

Nine local CPU tests passed for bounded numerical caching, shared-engine metric
preservation, display refresh, policy invalidation and withdrawal on a warm cache
(including a withdrawal during a cache hit). The prior 20 submission and 8
registration contract tests also passed before the final HTTP profile assertion
and admission-version key additions. These are fixture/API evidence only.
Public profile chart rendering and two-model paired comparison are still pending;
G7, G8, G10 and G11 have not been proven on the hosted registered service.

Final frozen source passed **410 CPU tests** in 160.489 seconds. The receipt,
command and unchanged source hashes are retained in
generated/public-service-20261014-v3/full-cpu-receipt.json.
The earlier 409-test run had one obsolete race-injection failure and remains
separately preserved in v2. Receipt revocation is now checked during both first
analysis and a warm-cache read; neither check weakens rank or privacy rules.
Read-only production probing still shows registration disabled at the original
production revision. No registered-service hosted acceptance is claimed.

## Public comparison candidate

The final frozen candidate passed **419 CPU tests** in 169.160 seconds. Eight
new tests cover public numerical pairs, exact engine agreement, warm profile/board
reuse, incompatible settings, duplicate artifacts, capacity and withdrawal races.
The anonymous HTTP fixture covers summary permission and post-withdrawal refusal.
Prior leaderboard race tests now inject changes at cached-admission assembly;
the authoritative membership/policy recheck is preserved.

Local Chrome QA at 1440/390 pixels passed public profile charts, Task 4 context,
literal Korean/untrusted names, summary-only paired comparison, link revisiting
and page-width checks. It recorded zero page errors and external requests.
Hashes and browser screenshots are in generated/public-service-20261014-v5/.
The goal still lacks actual HF registration, remote durability/restart,
production public catalog and full hosted G1–G12 acceptance.

Existing actual Qwen3-8B/4B artifacts (17,670 records each) passed local operator
summary registration, profiles, complete metric board and paired comparison in
87.406 seconds. Original byte/content hashes were preserved. Numerical Task,
metadata-group, transition, strategy/quality/chart and signal point values and
denominators matched the prior independent native report (SHA-256
58d68fc772681c5ec0de3e7da72ce11e7fe26f233e9bea8ce6db38fdd9b6526e).
Matched Task 1–5 input counts were 2000/8000/2659/2659/2352. The 94 stored board
metric rows matched the registered profiles' engine admissions exactly.

The older report used 100 source-cluster resamples; this public numerical
candidate uses zero. Intervals were explicitly excluded from the point-value
comparison, not relabeled as matching. No official rank, raw case publication,
new GPU inference, HF transfer, hosted identity or remote durability was claimed.
See actual-reference-receipt.json and actual-reference-board-receipt.json in the
same private evidence directory. Operator-local test ownership is not HF login.

## Conditional state adapter checkpoint

Sixteen conditional-object fixture tests and three CLI assembly scenarios passed.
They verify confirmed originals/history, exact retry after lost response,
withdrawal fencing of an older instance, corruption/refusal, quota/initialization
guards and explicit dedicated credentials. The optional local boto3 SDK model
supports If-Match/If-None-Match; no real request was sent. This is not actual HF
durability, OAuth login or a deployed registered runtime. Frozen regression
receipts are retained separately in generated/public-service-20261014-v6/.

Final frozen source passed **438 CPU tests** in 175.546 seconds. The receipt and
source hashes are in generated/public-service-20261014-v7/. The HF metadata
endpoint is fixed independently of HF_ENDPOINT; S3 uses the fixed HF namespace
gateway and explicit dedicated credentials. The earlier v6 run passed 438 tests
before that endpoint guard and remains earlier-scope evidence. G1–G12 hosted
acceptance is still incomplete; no source-only success is a durability certificate.

## Registered deployment candidate

Registered launcher/bootstrap checks passed 8 fictional CPU scenarios: atomic
two-reference first cut, same IDs/history after restart, withdrawn reference
remaining hidden, input mutation preflight, explicit migration/initialization and
dedicated native/provider configuration. Local materialized-app HTTP checks with
both actual full references passed in 116.422 seconds. Storage and OAuth were
doubles; the two references' original bytes remained local.

The final local suite passed **446 CPU tests** in 179.512 seconds. A source-only
Docker context plus synthetic QA was transferred to the user-selected b200-1:
6,849,703 bytes, SHA-256 a36c383056f2eeceaf47776e9141918c69de942ace679da34aea1846dfde7f5c.
The image digest was
sha256:485f018f5d57515c4e22dcf59a8a4cc1c26a3c6ad83691c9ca425cf9174cacc6;
27 container tests passed with networking disabled, 2 CPUs and 6 GiB RAM.
The post-build shell wrapper's quoting error remains distinguished from verified
image/container success. Validation containers/image were cleaned up.

No HF state/Space changes, original model-result transmission, actual hosted
OAuth, conditional storage or restart acceptance occurred. G1–G12 remain open
for actual production evidence. Candidate/log/source hashes are in
generated/public-service-20261014-v9/.

After the frozen CPU/container checks, the footer's environment wording alone
was corrected. Final JS syntax and localhost Chrome desktop/mobile QA passed;
the rebuilt v10 context differs from the Docker-tested v9 context in registration.js
only. Backend/dependency files are identical. Final frontend hashes/screenshots
and the source-only context are in generated/public-service-20261014-v10/.

## Actual HF preparation, no state activation

The new private registration test Space exists at
79ed3c012e86d29237c808303dcb9302ab336f98 with source/index files only. It is
PAUSED; activation and first-state initialization are 0. The exact new private
state Bucket has 0 bytes/0 objects. Resource creation and source preparation do
not prove actual OAuth, S3, registration or restart. Original-transfer/trial
approval and dedicated user-entered Secrets are pending. Existing production
remains a85e57c45cbe3943796543134e68805c389ae74d.

Local declaration checks prove model/generation/measurement values are shown
without response text or fabricated verification; session isolation, expiration
and changed-byte refusal remain enforced. Mobile UI checks prove confirmation
is required before saving and is reset after selection changes. The first browser
harness failure remains separate from the corrected pass. Full v11 had one
temporary-file PermissionError; targeted report rerun passed. Final source tests
are recorded in v12 and are not inferred from either earlier outcome.

The final frozen v12 source passed **452 CPU tests** in 216.222 seconds with
terminal exit code 0. Ten source/test hashes were rechecked before writing
generated/public-service-20261014-v12/full-cpu-receipt.json. This proves the
local declaration/activation/bounded-checkpoint regression only. Actual HF OAuth,
conditional state writes, hosted restart and the public G1–G12 gates remain open.

Frontend-only exploration checks subsequently passed with 53 synthetic published
runs at 1440/390 pixels: observed-value sorting/search leaves official ranks
unchanged, undefined values stay last, all 53 runs appear in pair choices despite
a 50-entry catalog page, and failed refresh clears previous views/options.
G1/G7/G9/G10 local UI evidence is in v13; actual production gates remain open.
The 452-test backend regression is earlier-source evidence, with the later JS/CSS
changes verified separately by syntax and these browser checks.

Read-only HF metadata subsequently confirmed the four required user-entered
Secrets absent, State-Dev private/empty (0 bytes), the test Space paused and
production unchanged at a85e57c45cbe3943796543134e68805c389ae74d. The exact
five changed code files and checksum manifest (98,430 bytes) were prepared at
4bdf0cda2bb36a95033451cbdb827f34a5727d16 in the private test Space. Its observed
revision matches the commit; PAUSED and activation/initialization 0 are confirmed.
No original results, state snapshots, new input files or Secret values were sent.
This is actual source preparation only, not actual hosted G1–G12 acceptance.
Receipts are in v13; user setup is documented in HF_REGISTRATION_TRIAL_SETUP_KO.md.

## Public numerical downloads

The candidate now exports current public profiles and paired comparisons in
JSON/JSONL/CSV/Markdown/HTML without original cases. Rendering is bounded to
32 MiB and rechecks current publication after rendering; withdrawal or changed
metadata discards the attachment. All routes use the existing bounded CPU gate.
CSV formula protection, scriptless HTML, explicit units and separate submission/
model revisions are covered. Task 4 has no quality/event difference row.

The compact-JSON source passed **459 CPU tests** in 228.072 seconds with frozen
source hashes (v15). The subsequent export column names/HTML minimum widths and
their assertions passed **7 focused tests** in 11.914 seconds (v16); these two
file changes are kept distinct from the earlier full-regression source scope.
Final localhost Chrome checks saved all five profile and five comparison formats
at desktop/mobile widths, byte-matched each to the current API and opened the
scriptless offline HTML with readable scrolling columns and literal Korean names.

Serializer replay of the two previously validated actual numerical snapshots
(17,670 records/model) passed all 15 outputs, exact decoded JSON/JSONL/CSV numbers,
oracle point values and denominators. The largest file is 18,922,174 bytes. The
earlier pretty-JSON capacity failure remains a separate receipt; whitespace was
removed without increasing the cap. Historical origin metadata was derived from
read-only retained local SQL, not invented HF ownership. Bootstrap intervals were
not compared. This is serializer/CPU evidence, not new inference, actual hosted
registration, HF storage or public G1–G12 acceptance. See v14/v15/v16 receipts and
PUBLIC_NUMERICAL_REPORT_GUIDE.md. Actual native identity/state/restart gates remain
pending manual scoped Secrets and the separately requested finite trial approval.

Final source-only preparation is at private revision
71c010860056b6f80d13f8e1da7a4b92a3bbca4a, matching implementation commit
01e5d7edd3f7c718f1e046ac7ff2e6ca323dd16a for materialized code. Only three source
files and checksum manifest (68,382 bytes) changed. The Space remains PAUSED,
private, activation/initialization 0. The metadata-only readiness probe before
preparation showed all four required data Secrets absent and production unchanged.
No original data, state writes or native HF login occurred. See v16's prepared
context, final-validation-receipt.json and hf-code-update-receipt.json.
