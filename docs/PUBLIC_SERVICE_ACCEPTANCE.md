# Public registration service acceptance

Updated 2026-10-14. All G1–G12 are required. Existing anonymous beta receipts are
regression evidence; they do not prove registered-service completion.

| ID | Required evidence | Current goal status |
|---|---|---|
| G1 | Anonymous public model list and metrics, no upload required | Missing |
| G2 | Model/run metadata and separate display name | Owner display metadata API/UI implemented; model profile integration pending |
| G3 | Actual HF identity, persisted registration and URL | Missing in production |
| G4 | Explicit summary/response scope and publication state | Consented numerical summary path and reviewed response upgrade tested locally; hosted evidence missing |
| G5 | Re-login and restart preserve acknowledged originals/history | Local acknowledged checkpoint/restore tests passed; actual HF durability/re-login missing |
| G6 | Independent public reader; private data denied | Beta isolation only |
| G7 | Two actual-model public profiles and paired comparison | Private beta comparison only |
| G8 | CLI/profile/board/download numerical agreement | Existing beta regression; public path missing |
| G9 | Duplicate, invalid, incompatible, concurrent and failed writes | Local replay/failure/copy/quota/conflict checks passed; new hosted integration required |
| G10 | Withdrawal removes all current public projections | Consented-summary withdrawal and restored hidden state tested locally; public cache/hosted evidence missing |
| G11 | Actual retained storage, recovery, capacity, responsive UI | Incomplete |
| G12 | Matching public code/runtime and current user documentation | Beta release only |

Record commands, exact source/revision, fixture versus actual scope, exit codes
and artifact hashes here as evidence becomes available. Do not convert simulated
identity/transport evidence into actual HF acceptance or classifier accuracy.

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
