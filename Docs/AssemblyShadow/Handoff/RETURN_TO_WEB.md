# Local Validation → Primary Implementation

## Blocker 1: fresh Unity `#-` assembly contains a real `MethodPtr` table

### Symptom

Fresh normal M07 passes the entire build, fixture, replay, linker-restoration, and outer success-restoration workflow at source anchor `68df00fe31a199491b313cc17f25575663b7452b`.

`run-r01-early-players.py` then fails before launching startup11. `prepare-h1-m07-control-capsules.py` fails at the same strict input gate:

```text
VerificationError: .../AssemblyShadowDemo.Bootstrap.dll: unsupported pointer tables
```

The fresh 567,296-byte assembly has SHA-256 `a937e18bcf5d8c4500f9b035c1fc3d61640f5af0c37e86529ccf173a21fd5e4b`, metadata stream `#-`, 469 `TypeDef` rows, 1,675 `MethodDef` rows, and 1,675 `MethodPtr` rows. The historical comparison assembly used `#~` and had no pointer rows.

### Reproduction and evidence

Run startup11 or the capsule generator using the fresh C fixture/build/replay receipts listed in `raw/V04/m07-normal/workflow.json` inside [the current checkpoint](../History/M07R/H1/local-validation-20260917-link-recovery/README.md). Both traces and `pointer-table-diagnosis.json` are members of its authenticated `raw-evidence.tar.gz`.

### Most likely root cause and impact

The current real Unity/IL-postprocessed Bootstrap output legitimately uses unoptimized `#-` metadata and a full `MethodPtr` indirection table. The verification model assumes direct `MethodDef` ordering and rejects all pointer tables before proving method bodies and raw-admission sites. Normal M07 build success therefore cannot produce authenticated early-control capsules.

Startup11, the M07 Player matrix, the provenance-bound diagnostic Player chain, capacity, lazy/dense, old-Player rejection, controlled performance, V05, and M08 remain blocked.

### Recommended direction

Primary should choose and test one explicit contract: either make the producer emit a deterministic optimized `#~` image before it is frozen, or extend the verifier to resolve the relevant ECMA-335 pointer indirections faithfully. Do not merely delete the guard. Add fixtures for reordered, duplicate, out-of-range, zero, truncated, and mixed pointer rows and prove raw-method lookup against the exact fresh Unity image before returning to Local.

### Uncertainty

Local has not established whether the `#-` form is caused by the current IL postprocessor output policy or another deterministic Unity compiler condition. The bytes repeat across the fresh A/B/C M07 attempts, so it is not a one-off corrupt build.

## Blocker 2: cleanup archive omitted the sealed dense adjunct DLLs

### Symptom and evidence

The recovered `workload-v3-dense-adjunct.json` requires:

- `AssemblyShadow.Workload.I0001.dll`, 1,048,576 bytes, SHA-256 `14f1fb323db1f1c1ca34840de5ef14eb3434c31e9e1608813ff4c1e398fd1273`;
- `AssemblyShadow.Workload.I0002.dll`, 1,048,576 bytes, SHA-256 `e5c88e875c43575b2a3087e466c745b9f8f57366d1247fc469820d53ef295bcf`.

Workspace and cleanup-archive searches found neither file. The archive contains the manifest and a historical raw PASS audit only. `dense-fixture-retention-audit.json` and the preserved parser failure are in the current checkpoint.

### Root cause and impact

Workspace consolidation classified these generated fixture bytes as regenerable without retaining the generator or an exact rebuild recipe capable of reproducing their sealed hashes. The manifest alone is insufficient. Fresh lazy/dense Player and native parser acceptance are unavailable.

### Recommended direction

Primary should publish either the exact authenticated fixture bytes through the external-artifact contract or a deterministic generator plus a new reviewed manifest and provenance contract. Historical PASS evidence must retain its old identity; replacement fixtures require fresh Player/native evidence.

### Uncertainty

Local cannot prove that a reconstructed assembly would match the old MVID, metadata layout, padding, and exact SHA-256. It therefore did not synthesize substitute bytes.

## Current gate state

H1 is `InProgress`. Whole-chain M08 is still `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. Return the two nontrivial issues to Primary and preserve the protected reproduction/performance pins. Do not begin R02.
