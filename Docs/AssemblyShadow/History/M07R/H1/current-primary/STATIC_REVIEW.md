# Static Review — V04 Failure/Lazy Repair + Protected Reference Coordination

## Verdict

**PASS for Primary → Local Validation handoff**, subject to fresh real-environment validation.

Reviewed candidate build-input source anchor:

`4fff4df26681ab3595bb241bbc972207d032831e`

This review does not claim real Unity/IL2CPP Player acceptance, performance acceptance, V05 completion, independent M08 PASS, or Human Review Gate approval.

## Finding A — late failure probe profile mismatch

### Previous defect

The earliest Baseline callback admitted each failure/publication process correctly, but `R01FailureProbe` then required `nativeBudgetCapabilityVersion == 1`.

Current patches are explicit profile 2.

### Repair

The late probe now delegates metadata contract admission to:

`ShadowPatchMetadataReservation.ValidateIfDeclared`

This is the same fail-closed validator used by the current M07 reservation path.

It verifies:

- declared capability;
- dormant legacy fields;
- complete profile-2 encoding contract;
- complete profile-2 capacity contract;
- load-order/closure equality;
- unique names;
- every declared DLL size against confined/hash-verified real bytes.

The returned profile must equal `M07Probe.RuntimeAbiVersion`.

Reservation uses the returned version rather than a hard-coded number.

### Preserved invariants

No changes were made to:

- earliest Baseline admission;
- Control/Q04/initializer operation ordering;
- Q04 byte transformation;
- initializer failure injection;
- raw diagnostic/recovery semantics;
- strict Python result oracle;
- native runtime implementation.

A simple `== 2` bypass was intentionally not used.

## Finding B — lazy dense-v2 NoCoverage

### Previous defect

`run-r01b-lazy-player.py` accepted only the historical sealed-v1 dense manifest, while the current supported generator emits deterministic-v2.

### Repair

The runner now explicitly supports two identities, not one loose superset.

#### Sealed-v1

Requires the exact old schema/kind/status, source-corpus bindings, parser identity and fixture envelope.

#### Deterministic-v2

Requires:

- schema 2;
- exact v2 kind/status/evidence identity;
- `historicalEvidenceReused=false`;
- old sealed hashes preserved only as `UnavailableDoNotRelabel`;
- exact shape contract;
- source/launcher/Mono/mcs/Cecil hashes;
- two-run reproducibility flags and command inventory;
- exact generated fixture-root confinement;
- exact 1 MiB fixture sizes;
- exact 4098 TypeDef / 4097 MethodDef rows;
- >64 KiB string heap;
- 4-byte TypeDef/MethodDef row widths;
- current parser-revalidated assembly identity, MVID and 4097-type inventory.

The runner normalizes only after successful admission.

### Player-side independent gate

`R01BLazyProbe` independently requires:

- recognized v1 or v2 header;
- no v2 historical-evidence relabelling;
- exactly fixture IDs 1 and 2;
- correct assembly names;
- current hash/size/row envelope;
- for v2: exact 1 MiB, exact 4098/4097 rows and >64 KiB strings heap.

It then executes the existing boundary methods at rows 4095/4096.

Lazy allocation/reservation semantics were not relaxed.

## Finding C/D — protected profile-1 old-Player/performance evidence unavailable

These were availability problems, not justification to reconstruct historical bytes.

Primary verified that the protected reference commit:

`88508b59b7c4ef8c5023cbbe655d43ebfcf5304c`

still contains:

- an explicit profile-1 reservation implementation;
- the M07 build workflow;
- the controlled R00 Development build producer;
- measurement probe/process-memory/witness bytes identical to the current candidate.

### New protected-reference verifier

`verify-h1-protected-reference.py` is read-only and requires exact:

- demo/reference head;
- HybridCLR, package and IL2CPP heads;
- Git origins;
- clean tracked state;
- protected source pins;
- profile-1 source contract;
- required producers;
- candidate/reference measurement-source parity.

It reports only `ProtectedReferenceInputsVerifiedNotBuilt`.

It does not install, build, or claim acceptance.

### New performance build-map freezer

`freeze-h1-performance-build-map.py` takes actual controlled build receipts/evidence from sides A/B.

It invokes the existing strict performance analyzer to authenticate:

- Development C++ Release configuration;
- build GUID/output/executable;
- native library/metadata;
- immutable input snapshot;
- source pins/provenance inventory;
- measurement source snapshots.

It derives comparability from those authenticated facts.

A build map is written only after `ComparabilityPassed`.

The tool does not accept hand-authored comparability claims and does not claim performance acceptance.

## Regression coverage

Primary regressions now cover:

- failure probe source bound to the shared profile-2 validator;
- no stale profile-1 equality;
- unchanged failure pipeline adversarial suite;
- deterministic-v2 manifest admission and normalization;
- v2 historical relabelling rejection;
- Player-side explicit v1/v2 contract;
- lazy ledger invariants;
- authenticated performance build-map derivation;
- controlled evidence tamper rejection;
- protected reference identity constants and expected runtime differences;
- committed live handoff preflight.

## Primary executable evidence

Workflow `35356780407` at source anchor `4fff4df...` and authority successor `5c57eb32c07ff5e2f716f41e27d006936ca42be8` passed:

- bounded Primary: **319/319**;
- committed handoff: **11/11**;
- early capsule: **7/7**;
- early results: **19/19**;
- failure pipeline: **17/17**;
- lazy contract: **8/8**.

Artifact ID:

`10551884431`

ZIP SHA-256:

`9e0629b135ee99962735f0667d81f167ce6dde07fe49a83dc2654f52746acb55`

## Source-authority review

Only `night-outlook/hybridclr_demo` changed.

Candidate native/package/IL2CPP pins remain:

- HybridCLR `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad`;
- HybridCLR Unity `0ea633a2c5b936b5af69d944593c55bd2783fca9`;
- IL2CPP `6be7f38bec2fa4677d24efc1a4a1294240789933`.

Candidate source anchor is `4fff4df...`.

The protected performance reference remains `88508b59...`; its branches/pins are not moved.

No source-verifier, metadata-only, H1 gate, M07 mutable-path, capacity, runtime ABI, performance-analysis or human-gate policy was weakened.

## Residual empirical requirements

Local must still prove in the real macOS/Unity environment:

1. current source/provenance builds at the new source anchor;
2. current controlled/normal M07;
3. repaired late failure Control/Q04/initializer behavior;
4. deterministic-v2 lazy Player execution;
5. isolated protected-reference installation integrity;
6. fresh reference profile-1 M07 graph;
7. fresh old-Player identity rejection;
8. fresh candidate/reference controlled Development builds;
9. build-map comparability;
10. preregistered pilot/formal performance sampling;
11. complete checkpoint retention;
12. V05 and genuine independent M08 only when eligible.

## Gate

H1 remains `InProgress`.

Historical M08 remains `FAIL`; it was not rerun.

`humanGatePassed=false`; `mayEnterR02=false`.

Do not begin R02.
