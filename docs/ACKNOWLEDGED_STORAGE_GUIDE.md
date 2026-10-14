# Acknowledged registration storage (candidate)

This is the synchronous conditional storage candidate. It is distinct from the
existing periodic backup manager and fixed-snapshot transport. Local doubles and
CLI assembly tests do not establish actual HF persistence. Production registration
is not enabled by adding this module or installing its dependencies.

## Storage contract

1. A registration mutation commits original artifacts, revisions, events, consent,
   publication state and its idempotent response in the local SQL transaction.
2. Before returning success, the store creates a consistent SQLite checkpoint
   and validates its logical digest against the pending cut.
3. The private Bucket receives content-addressed database and manifest objects
   with `If-None-Match: *`. Both are downloaded and verified, including when an
   existing object caused a precondition response. Existing addressed objects
   are never silently overwritten by the application.
4. Only then is `PREFIX/HEAD.json` written: initially with `If-None-Match: *`,
   otherwise with `If-Match` against the previously read ETag. The HEAD receipt
   is read back before acknowledgement.
5. A write failure or conflict returns no successful registration acknowledgement.
   The unconfirmed local cut stays private; retry uses the same request key.
   If HEAD succeeded but its response was lost, retry reconciles the same cut
   without creating another logical checkpoint.
6. Each live read is fenced against the current remote HEAD. An older instance
   stops serving state after another writer advances the authority. It cannot
   keep exposing a result withdrawn by a newer instance.

Ordinary HF batch uploads are non-transactional. The adapter uses the documented
S3 conditional PUT contract instead. ETags are write preconditions, not content
checksums; SHA-256 verifies database bytes and canonical receipts. A digest does
not prove the identity or approval of an operator.

## Restore and failure handling

A fresh runtime downloads the current acknowledged database into a staging
directory. Size, bytes, SQLite `quick_check` and the logical digest must match.
HEAD is checked again before the staged directory becomes the live store.
The opening store also verifies its local state against the current HEAD.

Existing divergent working directories are preserved and rejected. They are not
deleted, overwritten, merged or implicitly adopted. Missing HEAD with orphaned
objects is an inspection condition, not evidence of an empty store. Access denial
is never treated as an empty namespace. Initializing a genuinely empty namespace
requires the explicit `--initialize-state` flag.

This restores the current application authority, including terminal withdrawal
and audit history. The separate arbitrary ZIP-snapshot recovery/quarantine path
is unchanged; old snapshots do not become automatically publishable. Operator
input indexes, roles and rank policy still require their configured validation.

## Configure the CLI candidate

Install the `serve` and `storage` extras. Supply the normal trusted catalog,
operator roles and HF OAuth application configuration. The following command is
a template for a future approved target, not authorization to create it:

```bash
koevd-space --catalog /operator/catalog.json \
  --submission-root /tmp/koevd-live-state \
  --roles-file /operator/roles.json \
  --origin https://YOUR-SPACE.hf.space \
  --state-bucket KETI-NLP/KoEVD-Platform-State-Dev \
  --state-prefix koevd-state-v1 \
  --self-reported-summaries
```

Use `--initialize-state` only for a verified empty, approved namespace. An existing
acknowledged HEAD is restored without that flag. A filesystem `--checkpoint-root`
and remote `--state-bucket` are mutually exclusive. The default public anonymous
launcher remains unchanged and does not enable this configuration.

The proposed state Bucket is separate from reference and periodic-backup Buckets.
It must already exist and remain private. The adapter never creates Buckets,
changes visibility, configures a paid resource or deletes retained objects.

Dedicated server Secrets:

| Name | Purpose |
|---|---|
| `KOEVD_STATE_TOKEN` | Fine-grained read/write token for the exact state Bucket; the HF client uses it for metadata checks |
| `KOEVD_STATE_ACCESS_KEY_ID` | S3 access key generated from the same scoped token |
| `KOEVD_STATE_SECRET_ACCESS_KEY` | Matching S3 secret key |

Generate S3 credentials through the scoped token's settings dropdown. They inherit
its permissions; allow read/write for the intended private state Bucket only.
Never use `KOEVD_REFERENCE_TOKEN`, a development backup token, a CLI administrator
token or ordinary AWS credential lookup as a substitute. Do not send Secret
values in chat. Native Space OAuth is separate: `hf_oauth: true` supplies the
application variables, with identity/profile scopes sufficient for account
ownership. A registered launcher must preserve/use them explicitly before
clearing unrelated environment credentials.

## Bounds and remaining acceptance

Defaults limit a live checkpoint to 2 GiB, conservatively counted retained objects
to 8 GiB, inspected namespace objects to 20,000 and sequence to at most 10,000.
Actual namespace/size capacity can stop earlier. There is no automatic deletion,
garbage collection or quota purchase. Retained object sizes are counted rather
than assumed Xet savings. The SDK disables automatic request retries; confirmation
and exact-request retry are application decisions. A single process/replica remains
the intended operating profile; conditional writes and read fencing additionally
reject conflicting/stale instances rather than merging their edits.

The Bucket owner and scoped writers control storage. Application conditional
writes do not supply WORM storage or prevent a privileged operator from deleting
objects, rewinding HEAD or changing visibility. Those changes require operator
procedures; they are not supported online recovery actions.

Required next steps are registered launcher/Docker assembly, actual scoped S3
precondition/readback tests, native HF sign-in, full-state restart/restore and
public service G1–G12 acceptance. No raw upload, new state Bucket, S3 key, Space
Secret or production deployment was made by the local implementation checks.

References: [HF Bucket API](https://huggingface.co/docs/huggingface_hub/main/guides/buckets),
[HF S3 conditional writes and credentials](https://huggingface.co/docs/hub/storage-buckets-s3),
[native Space OAuth](https://huggingface.co/docs/hub/spaces-oauth).
