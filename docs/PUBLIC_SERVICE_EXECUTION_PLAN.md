# Public registration service execution plan

Updated 2026-10-14. Goal: complete the public registered-result service, including
G1–G12, rather than extend the anonymous-analysis beta alone.

The original development checkout has 214 dirty entries and is preserved. Work
uses branch `feature/public-registration-service`, based on public main
`701140249ce69a3a4089e3a184d000bdde2cebb9`, in the isolated publishing checkout.

## Current state

The production Space is public, RUNNING, CPU Basic, one replica at
`a85e57c45cbe3943796543134e68805c389ae74d`. Registration remains disabled. Its
two exact references and anonymous-analysis acceptance remain intact.

## Decisions and sequence

1. A successful registration mutation must have a confirmed storage checkpoint
   before acknowledgement. A sink failure is a failed operation response; an
   unconfirmed cut is not exposed by subsequent reads. Retry uses the original
   idempotency key. The first file sink establishes this contract locally; it
   does not prove HF durability or authorize cloud transmission.
2. Preserve the current SQL schema, original artifacts, audit chain, request
   replay, independent response-publication review and rank exclusions. Add
   display metadata separately from the immutable result.
3. Add explicit user-consented summary publication without representing it as
   independent operator verification. Response publication retains its review
   path. Both publication paths remain distinct from official rank admission.
4. Cache numerical profiles by artifact/index/analysis version and select only
   the current public revision. Preserve withdrawal/revocation rechecks and
   raw-text scope in profile and comparison projections.
5. Wire OAuth, acknowledged private storage, two operator reference entries,
   public profiles/metrics/comparison and registration UI into the deployment
   candidate. Test local behavior, then approved HF staging and production.

## Work underway

`durability.py` now provides synchronous checkpoint confirmation, a separate
local ledger, exact-cut restore, interrupted-copy retry, retained quota and
conflict/error guards. Fourteen fixture tests passed. SQLite probe connections
are explicitly closed on Windows. Cross-filesystem restore stages objects at
the destination. Failed checkpoint writes never return successful mutation
acknowledgements; later reads/replay must confirm the pending cut first.

Registration now supports owner-controlled display name/description without
rewriting the model declaration or original artifact, including bounded HTTP
metadata updates. Legacy default-create request fingerprints are preserved.

An explicit `allow_self_reported_summaries` deployment option permits owners to
publish consented numerical summaries without fabricating permission review or
generation verification. Response scope still requires the existing independent
review/admin path. A reviewed summary-to-response scope upgrade is supported;
withdrawal continues to hide all current public projections. Eight new local
service/HTTP tests passed, along with twenty existing submission tests.

CLI options `--checkpoint-root` and `--self-reported-summaries` wire these
features into the opt-in registration candidate. Both remain off in the current
production launcher. HF transport, cached public profiles, operator reference
intake, actual OAuth, hosted restart/restore and final deployment remain required.

A first full run passed 397 CPU tests before the final ledger atomic-copy/quota
changes; it is not the final-source acceptance. Final-source tests are recorded
separately in `generated/public-service-20261014-v1/`. No earlier failed attempt
is relabeled as a pass.

No deployment, paid resource, token change or new original-result transmission
has occurred for this goal. Historical bounded test approvals are not reused.
