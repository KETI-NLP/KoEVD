# Frozen measurement matrix returns

`scripts/measurement_matrix_bundle.py` packages a **terminal passed** matrix and independently accepts it against previously accepted baseline generations and an operator input index outside the new ZIP. It does not run ZIP code, create human labels, authenticate generation, certify accuracy, publish results or enable ranks.

The default intake requires both target models and all seven conditions: repeat traced batch2, untraced batch2, batch1, batch4, reverse batch2, single and float32-request batch2. An explicit `--required-variant` subset is allowed only with a receipt that says the full seven-condition matrix was not checked. A subset must never be called the complete precision/batch audit.

## Node packaging after completion

The current GPU controller remains `incoming/validate_frozen_measurements_v1.py`, independently hashed and separate from the original131-file core. Do not restart it while live or copy changing status into a fabricated completed bundle. The packaging helper copied to `incoming/matrix_return_v1` has SHA256 `fea2a3be2a8ff450758ed396ea81b1647559c45e91ee870a7832ada75624112e`; its local path helper has SHA256 `1d20900d209d2b4eab0fb4d008824b9252fa66adce13c5b1f95f5c0448a06a1c`. These are the node packer's bytes, not a claim that the later local intake revision is identical.

After the actual controller exits0 and `checks/status.json` is `passed_frozen_measurement_matrix`, use a fresh archive path:

```bash
ROOT=[private-node-path]
"$ROOT/envs/core/bin/python" "$ROOT/incoming/matrix_return_v1/measurement_matrix_bundle.py" pack \
  --matrix "$ROOT/measurement-matrix-expanded-v1" \
  --output "$ROOT/returns/KoEVD_measurement_matrix_expanded_20261008_v1.zip"
```

This command was subsequently executed after session46297 exited0. The resulting archive has221 files/27,223,907bytes/SHA256 `695b2e25fb853726a8e37b63c2d38ff12b03484ccbc8b749f96fb56b0505b95b`, and independent local intake passed. Do not rerun packaging into this existing path. It preserves the matrix, refuses an existing ZIP, scans for credential-like literals and returns the archive SHA256/size. Do not include weights, environment directories, auth caches or unrelated node outputs. Packaging is consistency evidence, not inference authentication.

## Independent local intake

Copy the ZIP and obtain its SHA256 separately. Use the local current source script and an installed KoEVD package; the accepted expanded baseline and independent index already exist locally. The following records the successful v18 intake. Its output now exists; a future recheck must use a fresh private output path.

```powershell
& 'generated/matrix-return-install-20261008-v18/Scripts/python.exe' scripts/measurement_matrix_bundle.py accept `
  --zip generated/KoEVD_measurement_matrix_expanded_20261008_v1.zip `
  --expected-sha256 695b2e25fb853726a8e37b63c2d38ff12b03484ccbc8b749f96fb56b0505b95b `
  --baseline generated/gpu-expanded-intake-20261008-v1/expanded-v3 `
  --trusted-index generated/private-space-deployment-20261008-v16/operator-data/prefix-96-index.json `
  --output generated/measurement-matrix-intake-20261008-v1
```

The same bounded byte snapshot is used for verification and extraction. Paths, links, case collisions, expansion limits and manifest checksums are checked before extraction. The intake refuses an archived `intake-receipt.json` or other files outside `matrix/`. After extraction it recomputes baseline and variant exports, verifies eight frozen input/prediction file hashes per target, independently recalculates comparison values and binds trace observations to measured outputs, call order and requested settings. Returned aggregate counts are not trusted. An error preserves the partial folder without an accepted receipt. The intake neither changes original measurements nor runs the archived classifier/controller.

## Requested dtype and observed dtype

`traced-fp32-b2` identifies a **float32 request**. It is not proof that both wrappers actually loaded every parameter in FP32. The receipt includes `parameter_dtype_realization` per classifier and a `requested_fp32_not_fully_realized` caveat when observed parameters remain mixed. Presence of some FP32 parameters is insufficient. Even uniformly FP32 parameter storage does not certify kernel arithmetic or explain a changed label causally.

At the partial8B observation on2026-10-08, the safety classifier under the float32 request still had752,393,024 BF16 and6,389,760 FP32 parameter elements, while the strategy classifier had8,234,382,336 FP32 elements. Safety precision sensitivity therefore remained untested by that request. The original wrappers and running controller were preserved; no weights or labels were cast/overwritten to manufacture a passing result.

CPU fixture tests verify the archive and recomputation boundaries, including mixed-dtype caveats. They do not substitute for actual returned matrix acceptance. The later actual return was independently accepted for both targets/all7conditions; [final evidence](validation/platform_m4_gpu_measurement_matrix_20261008.json) and [result interpretation](GPU_MEASUREMENT_MATRIX_RESULTS.md) supersede the partial8B checkpoint above. Human review, policy ratification, a full standard baseline and actual Space deployment remain separate requirements.
