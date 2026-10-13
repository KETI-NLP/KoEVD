---
title: KoEVD Analysis Candidate
emoji: 📊
colorFrom: blue
colorTo: gray
sdk: docker
app_port: 7860
hf_oauth: true
hf_oauth_expiration_minutes: 60
---

# KoEVD CPU analysis deployment candidate

Current plan0.45: a separate private CPU Docker development app is deployed. Actual HF login/draft saving and all5 fresh native report downloads have scoped acceptance. The default store is ephemeral; the managed backup profile is an unactivated candidate. [Operations](../../docs/TEAM_SPACE_OPERATIONS.md), [managed guide](../../docs/MANAGED_SPACE_GUIDE.md).

This directory contains a Docker/FastAPI Spaces candidate using the same package,
analysis engine and interactive report as the local CLI. The default development
profile has actual HF build/run evidence; this does not validate the separate
managed backup profile or a production deployment. Submission registration is opt-in
with a configured store, operator roles and actual HF OAuth app credentials; it is
disabled by default. Local synthetic HTTP/browser evidence does not verify live HF login.
Actual target-model references are not bundled.

See [OAUTH_SUBMISSION_GUIDE.md](../../docs/OAUTH_SUBMISSION_GUIDE.md) for optional
`KOEVD_SUBMISSION_ROOT`, `KOEVD_ROLES_FILE`, `KOEVD_OAUTH_ORIGIN` and provider secrets.
The candidate YAML above requests identity/profile only, not repository write scopes.
The default confidential OAuth client requires both app ID and secret. For a
registered secretless public app, explicitly set `KOEVD_OAUTH_CLIENT_TYPE=public`
and `OAUTH_CLIENT_ID`, leaving `OAUTH_CLIENT_SECRET` unset or empty. Both modes
use server-side PKCE; neither accepts an HF CLI token as app configuration.
This does not enable shared submissions in the separate Static candidate or
change the organization's compute-hosting plan requirement.
An attached durable store still requires independent mount/restore verification;
ephemeral Space disk alone is not persistence evidence. Official ranks stay disabled.

Use [SPACES_GUIDE.md](../../docs/SPACES_GUIDE.md) for the tested local run,
operator-only input catalog, private sessions and limits. The Dockerfile requires
the dedicated context produced by `scripts/materialize_development_space.py`.
Run these commands from the KoEVD repository root, replacing the dataset/index
paths with independently verified inputs and choosing a fresh output directory:

```bash
python scripts/materialize_development_space.py \
  --repo . --dataset /path/to/KoEVD-dataset \
  --standard-index /path/to/trusted_input_index.json \
  --output generated/private-space-deployment
docker build -t koevd-space-candidate generated/private-space-deployment
```

The materializer supplies the Space card, Dockerfile, sources, licenses, pinned
web dependencies and operator catalog. Do not build with the repository root as
context: it lacks the required `operator-data` directory and contains files that
are not part of the deployment allowlist. These commands are preparation guidance;
an actual container build has not been verified on this Windows host. Keep pending
submissions and credentials out of the build context. No automatic push occurs.

At runtime provide `KOEVD_SPACE_CATALOG` (an operator-controlled catalog with pinned
index/reference file digests) and `KOEVD_APP_ORIGIN` (the exact HTTPS app origin).
The catalog and approved files must be present in the container/mounted storage.
Use one app worker. Temporary sessions are separate from future M6 persistent
submissions. No upload automatically becomes public.

Default Space disk is ephemeral; an attached Storage Bucket/dataset repository or
other persistence adapter is required for later accepted submissions. The previous
persistent-storage setting is not a working alternative. Confirm organization
plan, storage, authentication and costs before publishing this candidate.

Official references checked 2026-10-08:
[Docker Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker),
[Spaces storage](https://huggingface.co/docs/hub/spaces-storage),
[Configuration](https://huggingface.co/docs/hub/spaces-config-reference).


## Organization development Space attempt — 2026-10-08

The user requested KETI-NLP organization hosting. `generated/private-space-deployment-20261008` contains an allowlisted 58-file/75,502,417-byte candidate with actual independently prepared full/prefix indexes, no model outputs/weights/credentials, empty reviewer/admin roles, native HF OAuth metadata and a visible temporary-storage warning. Related landing/upload/OAuth regression: 33 tests passed. The launcher selects the HF-provided canonical SPACE_HOST and temporary development storage; production durability and official ranks remain disabled.

Creating private Docker `KETI-NLP/KoEVD-Explorer` was rejected by HF with HTTP402: CPU Basic has no hourly hardware charge, but organization Docker/Gradio creation requires Team or Enterprise. An authenticated follow-up query returned404, so no Space was created and no files were uploaded. No subscription, billing or paid hardware was requested. This was the initial checkpoint; the user later confirmed KETI-NLP as the destination, as recorded below. See [creation receipt](../../docs/validation/platform_space_creation_20261008.json). A static-only shell is not substituted for the required server-side analysis/login workflow.


Hosting clarification (2026-10-08): official [Spaces Overview](https://huggingface.co/docs/hub/spaces-overview) states that Docker/Gradio compute Spaces require PRO for personal accounts or Team/Enterprise for organizations. CPU Basic has no hourly hardware cost; this does not waive the plan prerequisite. The current personal account returned `isPro: false`. The initially suggested free personal Docker fallback was corrected in chat and the pending hosting question. No personal Space or subscription was created. Static hosting alone does not satisfy the present server-side shared-engine/login/submission requirements.

The user subsequently confirmed KETI-NLP as the hosting destination. A second authenticated creation attempt at 2026-10-08T08:40:57Z verified organization admin membership and all 59 files in `generated/private-space-deployment-20261008-v16`, but again received HTTP402; a subsequent authenticated lookup returned404. The destination is decided, while the organization plan prerequisite remains outstanding. No upload, public visibility change, subscription or hardware upgrade occurred. See [recheck receipt](../../docs/validation/platform_space_org_recheck_20261008.json). Native Spaces OAuth is requested through `hf_oauth: true`; Hugging Face supplies its app credentials when provisioned, and these are separate from the local CLI token.

The later v18 candidate is `generated/private-space-deployment-20261008-v18`:59 allowlisted files/75,521,784bytes, all manifest bytes checked. A fresh noneditable package passed236 CPU tests with0skips. Actual prefix96 two-target integration and the separate seven-condition frozen-response GPU matrix were independently accepted; see [matrix results](../../docs/GPU_MEASUREMENT_MATRIX_RESULTS.md). Classifier accuracy, human/operator review and full standard baselines remain distinct. The candidate contains no actual outputs/weights/credentials/approved roles, and no actual plan activation, container/live Space or HF login is claimed. The public-list metadata fix leaves the prior UI assets unchanged; no additional v18 browser pass is claimed. [Candidate evidence](../../docs/validation/platform_m6_listing_metadata_cpu_20261008.json).

The latest v19 candidate is `generated/private-space-deployment-20261008-v19`:60files/75,531,813bytes, all manifest/source bytes checked. Its fresh noneditable package passed245 CPU tests and37 Python source/installed checks. Separate Linux policy-file checks exercised actual POSIX hard links, directory fsync, symlink rejection and tamper failure on fresh `/tmp`; they are not a full new-package Linux suite or cloud durability evidence. [Policy evidence](../../docs/validation/platform_m6_policy_decisions_cpu_20261008.json). Policy preservation/configuration is documented in [OPERATOR_POLICY_GUIDE.md](../../docs/OPERATOR_POLICY_GUIDE.md). The development launcher clears policy activation environment variables and keeps candidate/no-rank. No actual approval records, outputs, weights, credentials or configured reviewer/admin roles were bundled. Remote snapshot/restore and real hosted acceptance remain pending; no new browser or Space/container pass is claimed.


Latest v0.20 candidate: `generated/private-space-deployment-20261008-v20`,61files/75,555,401bytes, exact manifest/source bytes verified. Fresh noneditable final package passed258 CPU tests and38 Python byte comparisons. Combined private DB/selected-policy snapshots and HF Bucket transport candidate are described in [PRIVATE_SNAPSHOT_GUIDE.md](../../docs/PRIVATE_SNAPSHOT_GUIDE.md). Existing actual two-model originals (2300records) restored on Windows and a fresh Linux install; separate Linux file checks used SYNTHETIC policy records. [Snapshot evidence](../../docs/validation/platform_m6_snapshots_cpu_20261008.json). Real HF storage/automatic backup/RPO/operational restore, policy approval and hosted OAuth/container acceptance remain pending. No private snapshots/results/policies/credentials are bundled or uploaded. Launcher remains ephemeral candidate/no-rank; a manual backup feature does not make the running Space durable. Previous checkpoints above are historical.


Latest v0.21 candidate: `generated/private-space-deployment-20261008-v21`,62files/75,574,042bytes, manifest/source verified. Fresh installed package passed268 CPU tests and39 Python byte comparisons. Restored DBs now enforce a recovery guard on public projections and domain mutations until outside checkpoint reconciliation; private authorized originals remain available. Actual existing two-model2300records restored on Windows/Linux and stay quarantined. No actual operator release, HF cloud or hosted acceptance is implied. [Recovery guide](../../docs/RECOVERY_GUIDE.md), [evidence](../../docs/validation/platform_m6_recovery_cpu_20261008.json). Actual outputs/guards/checkpoints/roles/credentials are not bundled; launcher still uses ephemeral candidate/no-rank. Previous checkpoints above are historical.

Latest v0.22 candidate: `generated/private-space-deployment-20261008-v22`,63files/75,592,401bytes, exact manifest/source verified. Fresh installed package passed278 CPU tests and40 Python byte comparisons. The [private backup worker](../../docs/BACKUP_WORKER_GUIDE.md) derives checkpoints from frozen ZIP DBs, preserves failed/partial copies and previous successes, and distinguishes uncopied live changes. Actual existing2300records passed two periodic copies, a real configured-quota failure, a later uncopied event and stale-restore quarantine on Windows/Linux. [Evidence](../../docs/validation/platform_m6_backups_cpu_20261008.json). Remote contracts use a fake provider; no actual cloud storage, operator release or RPO guarantee. The worker is not automatically started by the launcher, which remains ephemeral candidate/no-rank. No actual backups/results/checkpoints/policy/credentials bundled or uploaded. KETI-NLP Docker hosting remains blocked by the previously observed402 plan requirement; no unchanged retry or paid activation. Previous checkpoints above are historical.

v0.23 changes GPU control/CPU token-budget/private replay intake tools only; package source/UI and the v22 deployment payload remain unchanged. The related22 CPU checks pass; the current entire suite was not rerun. Pinned full17670-record inputs and corrected actual input_ids budgets passed on B300, and full-core-v1/session90124 is now actually running. Full two-model results, app numeric acceptance and public-reference permissions remain pending. [Full run guide](../../docs/FULL_STANDARD_RUN_GUIDE.md), [preflight/live evidence](../../docs/validation/platform_m4_full_standard_preflight_20261008.json). No actual outputs/credentials or new cloud objects uploaded; no hosted login/container or official rank claim.


v0.24 adds a separate [Linux native-runtime check](../../docs/SPACES_RUNTIME_VALIDATION.md), not a new package or deployment payload. Exact14 web dependency versions/pip check and42 installed koevd_eval files passed. Existing actual prefix96 two-target uploads, three individual/comparison HTTP profiles and independent CLI values agreed under UID0 and UID/GID1000; the owned servers stopped. Context guard5 CPU tests passed. Build-context/venv-path and restricted NFS parent failures are preserved; no existing permissions were relaxed. [Evidence](../../docs/validation/platform_m5_native_runtime_20261008.json). Windows/node container engines are absent and actual user namespace creation returned EPERM, so image/live Space/OAuth acceptance remains pending. Current full-core-v1/session90124 is still running and has not been accepted. Candidatev22/source/UI, temporary storage/no-rank and external approval gates are unchanged. No cloud object, subscription or publication occurred. Previous checkpoints above are historical.


v0.25 verifies a separate full-input CPU capacity fixture, not actual full target inference. Two17670-record fixtures produced35340 cases, exact Task counts and303534808bytes of report files under the unchanged512MiB limit. Actual native HTTP upload/comparison/download passed with byte-identical independent CLI profile; both sessions and owned server closed. Validation-only --comparison-only avoids redundant individual reports; one-result misuse is rejected, with6 related CPU guards passing. [Evidence](../../docs/validation/platform_m5_full_comparison_capacity_20261008.json), [guide](../../docs/SPACES_RUNTIME_VALIDATION.md). Package/UI/candidatev22/limits unchanged; no new entire-suite/browser/container/provider/cloud pass. Same full GPU90124/controller56870 remains live. Actual full results and hosting/operator/public gates are pending.
