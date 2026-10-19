# Public registration service acceptance

Updated 2026-10-19. **Release v0.3.0-rc.4 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Follow the [pinned first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.4/docs/GETTING_STARTED.md).

- Application source: `6f786d2ea9a4a2c1992e50c20e3e007c6e72ad90`,
  [PR #14](https://github.com/KETI-NLP/KoEVD/pull/14), merged as
  `3d974840998963562615dccf3d5aae05ccbf8999`.
  [Release v0.3.0-rc.4](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.4)
  fixes that merge; package and module versions are `0.3.0rc4`.
- Actual running Space revision: `edb541e7ecb6f255b5cf298ab86c1dbe07420ce1`.
  Twelve changed files (395,692 bytes) match their remote bytes; all 77
  materialized source files match the application commit. CPU Basic, single
  replica, provider LFS, operator data, State and Secret configuration are
  preserved. One automatic start; no rollback.
- [Source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39188824731) and
  [merged CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39188982094) passed
  **509 tests each on Python 3.10 and 3.12**. Local full CPU validation passed
  509 tests; the final calculation checks passed five focused tests. Initial
  Python 3.10 checks found a last-digit floating-sum difference; source-decimal
  calculation now agrees with independent exact-rational tests across versions.
  A fresh public tag clone installed the hub extra in an isolated environment,
  passed dependency checks and 13 focused tests, and verified all 386 manifest
  entries against exact Git blobs. No PYTHONPATH source override was used.
- The default home is a searchable, sortable leaderboard of **all 12 paper
  models**, rather than a two-reference diagnostic overview. Every Task tab has
  12 rows. The 1,165-pixel table fits its 1,165-pixel desktop container. Model
  details, comparison and submission occupy separate screens, with direct
  links and back/forward navigation. No upload or comparison form appears on
  the default leaderboard. Display positions reflect the chosen metric and
  direction; they are not an official overall ethics rank.
- Twelve exact, checked-in aggregate CSV sources reproduce the model data.
  Task 1 retains all 12 models' coverage and 11 high-coverage models' judgment
  counts. Gemini 3.1 Pro's unavailable individual judgment counts stay N/A,
  with its 56.54% coverage retained. Judgments are not ethical-quality scores.
  Task 2 uses the same three common variants across open and commercial models;
  original four/three-variant means remain visible separately in details.
  Task 3 retains unsafe/classified rates and classified/expected counts.
  Task 4 is descriptive strategy inclusion, with selected heatmap columns
  explicitly distinguished from a complete strategy distribution. Task 5 uses
  the paper's unsafe calls/all expected rows, with three framing rows/model
  and parse coverage. Rounded percentages never imply invented counts.
- The two current Qwen3-8B/4B references remain in a separate registered
  input/configuration group. Their **94 metric rows, complete public board and
  entire public paired comparison response are exactly unchanged**. Paper
  comparisons are aggregate-only; registered comparisons still use checked
  matched inputs. Different collections cannot be selected together. No paper
  matched-case statistics, confidence intervals or significance are invented.
- The localhost browser verified config/session/public failure, independent
  paper discovery, retry without reload, synthetic sign-in/upload/private save,
  reload and saved-result reanalysis, explicit numerical consent/publication,
  own-group discovery and separate-screen comparison. Actual hosted browser
  checks passed the 12-model landing page, Task tabs, missing-value details,
  paper comparison, registered group and comparison, and submission isolation.
- This update performs **no actual hosted owner upload/write/sign-in retest or
  new GPU/accuracy experiment**. Earlier hosted persistence acceptance remains
  the evidence for native HF sign-in, durable owner writes and restart recovery.
  The local-only loader used the normal upload API; native file selection and
  mobile execution were not retested. Official ranks and raw reference-response
  publication remain disabled. Existing consent and private history are preserved.

[Full-leaderboard hosted receipt](validation/platform_full_leaderboard_hosted_20261019.json)
records exact revisions, remote hashes, numerical regression and test scope.

## Earlier Task overview release (2026-10-17; superseded)

Updated 2026-10-17. **Release v0.3.0-rc.3 is deployed** in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Start with the [pinned first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.3/docs/GETTING_STARTED.md).

- Application source: `ee6405fb18e2c7fbe4438a6fa81c9e9383c50b87`,
  [PR #12](https://github.com/KETI-NLP/KoEVD/pull/12), merged as
  `842e49aef73aea106f68e7229eee6db85f87f79a`.
  [Release v0.3.0-rc.3](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.3)
  fixes that merge; Python package/module version is `0.3.0rc3`.
- Running Space revision: `f7d26f3cc1117028975e5900e9b75f3ff1dbf38b`.
  The 16 changed files (218,098 bytes) match their remote bytes, and 75
  materialized source files match the application commit. CPU Basic, one replica,
  provider LFS attributes, operator data, State and Secret configuration are
  unchanged. One automatic start; no rollback.
- [Source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39016362176) and
  [merged CI](https://github.com/KETI-NLP/KoEVD/actions/runs/39016495253) passed
  **504 tests on each of Python 3.10 and 3.12**. Local CPU validation passed
  503 tests before the final recovery-order case and 35 final focused tests.
  A fresh public tag clone installed the `hub` extra in an isolated environment,
  passed dependency checks and eight focused tests, exposed `--stage status`,
  and verified all 369 manifest entries against exact Git blobs. The deeply
  nested initial Windows fixture exceeded the path limit; a shorter workspace
  clone installed successfully without a source or package change.
- The first screen shows both existing Qwen3-8B/4B references and representative
  Task 1–5 results. In the actual HF embedded app, model rows begin at 379.89
  and 488.06 pixels; the second ends at 596.23 within the 670-pixel app viewport.
  Task tabs expose denominators and coverage; Task 4 shows 15 multi-label
  strategy inclusion frequencies, with no quality direction. Existing **94
  metric rows and the entire public paired response remain exactly unchanged**.
- Paper results occupy a separate historical collection. Its five tables match
  the five existing public CSVs exactly: Task 1/2 pooled summaries (6/21 rows),
  Task 3/4 per-model tables (12 models each), and Task 5 pooled framing results
  (3 rows). The original 13,552 Task 3 prompts/model differ from current runs;
  missing per-model scores are not invented, and historical results never enter
  current-protocol ranking or paired comparison.
- The localhost browser completed synthetic upload, private save, analysis of an
  already-loaded saved result, page reload, saved-result import into a fresh
  private session, one-run analysis, explicit numerical consent/publication,
  own-model discovery and comparison with a different published artifact.
  Public startup also succeeded while account checks failed and private session
  creation was held. Actual hosted browser checks passed Task 1–5, all paper
  tabs, reference comparison and submission-entry instructions.
- `--stage status --output-dir RUN` reads retained generation/measurement state,
  reports failed/pending rows and recovery actions, and finishes pending
  measurement promotion before suggesting generation retry. It does not change
  model scores, hide failed denominators or claim export freshness.
- This update performs **no actual hosted owner upload/write/sign-in retest or
  new GPU/accuracy experiment**. The earlier full hosted acceptance remains the
  evidence for native HF sign-in, durable owner writes and restart recovery.
  A local-only loader exercised the normal upload API; native file selection and
  mobile execution were not retested. Official ranks and reference response
  publication remain disabled. Saved-result reanalysis is now implemented.

[Task-home hosted receipt](validation/platform_task_home_hosted_20261017.json)
records versions, remote file hashes, test scope and unchanged measurements.

## Earlier recovery/discovery release (2026-10-16; superseded)

Updated 2026-10-16. **Release v0.3.0-rc.2 and the recovery/discovery improvements
are deployed** in the [public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Use the [pinned first-user guide](https://github.com/KETI-NLP/KoEVD/blob/v0.3.0-rc.2/docs/GETTING_STARTED.md).

- Application source: `dfd32d34265835af4c6217447facfb8d38b551c3`,
  [PR #10](https://github.com/KETI-NLP/KoEVD/pull/10), normally merged as
  `2f480566cacdff7e1f5deebf55d3fae13de540af`.
- [Release v0.3.0-rc.2](https://github.com/KETI-NLP/KoEVD/releases/tag/v0.3.0-rc.2)
  points to that merge; Python package/module version is `0.3.0rc2`. A fresh clone
  of this tag and clean environment installed the `hub` extra, passed dependency
  checks and eight focused recovery tests, and exposed both `--measurement-tasks`
  and `--remeasure`. Historical rc.1 is preserved and lacks those recovery options.
- Actual running Space revision: `d6f863926557eb86c0a17ceb335084f753b634d5`.
  All 14 changed files (172,785 bytes) match the candidate at the remote revision;
  all 72 materialized source files match the application commit. CPU Basic,
  single replica, provider LFS attributes, operator data and existing State/Secret
  configuration are unchanged. One automatic start; no rollback.
- [Source CI](https://github.com/KETI-NLP/KoEVD/actions/runs/38854569046) and
  [merged CI](https://github.com/KETI-NLP/KoEVD/actions/runs/38854759633) passed
  **497 tests each on Python 3.10 and 3.12**. The initial local full CPU run
  passed 496 tests; final focused and fresh-release runs each passed eight.
- Generation retry after classification preserves validated prior predictions,
  measurements, traces and manifest before generation changes. Changed Task 3
  predictions invalidate Task 3/4 measurements. Interrupted invalidation resumes
  without another inference request; pending retries block classify/report/export.
  Canonical/archived tampering is rejected. Preparation identity stays unchanged.
- The actual localhost browser recovered combined configuration/session failure
  without reloading, then completed synthetic upload, private save, explicit
  numerical consent, own-model jump, global search, profile and paired comparison.
  A local-only loader sent synthetic JSON through the normal upload API; the
  native OS file chooser was not retested. JavaScript also verifies single-flight
  retries, valid-session/upload retention and cross-group duplicate mapping.
- Fifteen anonymous hosted HTTP reads passed. The two reference registrations,
  all **94 leaderboard metric rows**, and the entire public paired comparison
  response exactly match the predeployment values. Hosted browser checks cover
  the new global finder, metric direction and public comparison. Metrics use
  their existing denominators; Task 2 accuracy versus error is explained explicitly.
- This update makes **no actual owner upload/write/sign-in trial or new GPU/
  accuracy claim**. The earlier full hosted persistence acceptance remains the
  evidence for native HF sign-in, durable owner writes and restart recovery.
  Official ranks and reference response publication stay disabled. Saved private
  results can be downloaded and reuploaded for analysis; direct saved-result
  reanalysis is not implemented.

[Recovery/discovery hosted receipt](validation/platform_recovery_discovery_hosted_20261016.json)
records exact versions, file hashes, validation scope and unchanged metrics.

## Earlier recovery and leaderboard-first update (2026-10-16)

Earlier 2026-10-16 update (superseded above). **The recoverable workflow and leaderboard-first home were
deployed** in the [public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Follow [GETTING_STARTED.md](GETTING_STARTED.md) for evaluation, retries,
registration and comparison.

- Application source: `af6d25e8f024eae9d6751946dcd00bead40df6ce`, [PR #8](https://github.com/KETI-NLP/KoEVD/pull/8),
  merged as `8d0f71fdd590bc05986369ac645bab7b995351bb`.
- Actual running Space revision: `cf439ba7092dd2e4bb56f153fb5ca416925f61eb`.
  Eleven changed code/manifest files (208,816 bytes) match the pinned candidate;
  all 70 materialized source files match the application commit. CPU Basic,
  one replica, LFS attributes, operator inputs, Secret and State configuration
  are preserved. One automatic start; no rollback.
- [Linux CI](https://github.com/KETI-NLP/KoEVD/actions/runs/38840689534) passed
  489 tests each on Python 3.10 and 3.12. Local CPU tests and actual localhost
  browser tests use synthetic measurements, identities and results. A Windows
  replace-permission error observed in a full rerun was addressed using the
  existing fsync/bounded-retry checkpoint writer; 41 affected-module tests passed.
- Thirteen anonymous hosted HTTP checks passed: health/storage readiness,
  registration configuration, both reference profiles, leaderboard, paired
  comparison, assets and `/`/`/submit`. The actual HF embedded browser opened
  on the model leaderboard, switched to the account/upload view, returned to
  the model view and completed the two-reference comparison without console
  errors. Independent review is disabled; numerical sharing remains enabled.
- New owner-action writes retain local synthetic/CI validation scope: cancellation,
  reversible summary unsharing, fresh-consent resharing and recovery of an
  owner-withdrawn private draft. Administrator withdrawals cannot be bypassed.
  Measurement retries preserve attempts, validate successful tasks before reuse
  and reject export while file promotion is pending. The preparation identity
  and standard protocol inputs are unchanged.
- This update made no new result upload, registration/publication write, native
  HF sign-in, GPU run, classifier-accuracy claim, paid-resource change or tag
  change. Original-response publication and official ranks remain disabled.
  The earlier full persistence trial below is still the hosted evidence for
  owner registration, native sign-in and exact restart preservation.

[Aggregate hosted receipt](validation/platform_recovery_hosted_20261016.json)
records hashes, read checks and scope without originals or credentials.

## Earlier first-user workflow correction (2026-10-16)

The preceding first-user workflow correction was deployed in the
[public Platform](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform).
Start with the [complete evaluation-to-comparison guide](GETTING_STARTED.md).

- Application source: `39962e31d498ee9b0d0256b377c5e4837e915f6f`, PR #6,
  normally merged as `6d5b9fa5a1646148fd947d71b1c0013f83dd1667`.
- Actual running Space revision: `7cfd8d88099a28119d88c5f3a67852a43bfaf242`.
  Eight changed files (156,124 bytes) match the candidate byte-for-byte. CPU Basic,
  one replica, existing LFS attributes, Secret and State configuration are retained.
- Health and explicit storage readiness, registration configuration, both existing
  reference profiles, leaderboard and paired numerical comparison passed anonymous
  HTTP checks. The actual HF embedded browser displayed the new pre-upload account
  guidance, five-task profile charts and the completed two-reference comparison.
- One automatic start; no rollback, new result upload, registration/publication
  write, fresh native sign-in, GPU run or release/tag change. Registration writes
  retain the local synthetic scope of the correction tests. This update does not
  repeat the full persistence trial below or establish classifier accuracy.

[Hosted update receipt](validation/platform_first_user_hosted_20261016.json)
contains code hashes, read-check statuses and explicit scope. The earlier full
acceptance below remains the evidence for sign-in, registration and restart
preservation. Official ranks remain disabled.

## Initial full registration acceptance (2026-10-15)

On 2026-10-15, **the public research registration service passed its bounded
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

## First-user workflow correction (2026-10-16 implementation and local checks)

The [complete first-user guide](GETTING_STARTED.md) now connects registered input
preparation, generation, measurement, portable export, sign-in, private save,
optional numerical sharing and comparison. Custom local indexes are explicitly
separate. README and core guides no longer describe registration as unimplemented.

The accompanying UI candidate links uploaded results to registration automatically,
puts account guidance before upload, distinguishes temporary analysis from saving,
and retries only bounded public numerical reads. An explicit `/readyz` probes
storage/recovery without confirming a pending save; `/healthz` stays liveness.
A temporary public-read failure's underlying hosted cause has not been established.

[Local correction evidence](validation/platform_first_user_workflow_20261016.json)
records 477 passing tests, independent full-index preparation and validation of
both existing 17,670-record results, and a synthetic browser walkthrough through
private registration, numerical sharing and paired comparison. No new GPU run,
real HF login or raw-result upload was performed for those local checks.
The subsequent approved deployment and anonymous hosted checks are recorded at
the top of this document and in the separate hosted receipt. The local synthetic
registration test is not represented as a new hosted registration-write trial.

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
