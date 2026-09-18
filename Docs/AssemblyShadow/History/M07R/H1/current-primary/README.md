# R01B H1 — Current Primary Implementation

## Status

Local Validation returned the fresh source-anchor-`8b1298d` cycle at:

`af0d345ce3aa7257e301926d0da652709c09cf54`

That cycle passed authority, provenance, controlled and normal M07, control capsules, startup11, and the 14-mode M07 Player matrix. It then exposed one remaining Primary-owned integration defect: the separate R01 failure/publication launcher did not supply the mandatory earliest-startup capsule arguments, so the Player correctly refused before host continuation.

Current reviewed candidate build-input source anchor:

`50c79913096961636a776ee8254b6631002cdfe5`

H1 remains `InProgress`; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

## Failure/publication repair

### Design choice

The failure/publication matrix must satisfy two constraints simultaneously:

1. authenticate its complete input graph in the native earliest-startup callback;
2. leave the Shadow transaction unused so `R01FailureProbe` remains the sole owner of the Control, Q04 metadata-failure, and initializer-failure transaction.

Therefore the launcher uses an **early Baseline capsule** for all three processes.

`Baseline` is admission-only: the early callback reads and hashes closure/prerequisite bytes, records the source-bound receipt, returns success, and performs no Shadow transaction.

Using early `Control` would commit too early. Using early `MetadataFailure` or `InitializerFailure` would intentionally return failure and terminate before the host failure probe. Neither is compatible with the required later transaction oracle.

### Per-mode binding

Three plain Baseline capsules could otherwise be interchangeable. Each process now gets a deterministic `R01FailureEarlyAdmissionBinding` JSON containing:

- failure mode;
- early mode;
- baseline/runtime identity;
- fixture manifest path/hash;
- Native-ON build receipt path/hash;
- failure-fixture path/hash;
- Q04 negative-input path/hash;
- exact source pins.

That binding file is a capsule prerequisite. Its different failure-mode value makes the three capsule bytes/hashes distinct.

The capsule also authenticates the complete verified failure-fixture and negative-input file set. Extra prerequisites that are already closure DLL/PDB inputs are deduplicated, preserving the early callback's unique-path invariant.

### Launch and verification

`run-r01-failure-players.py` now:

- materializes all three bindings/capsules before freezing the immutable-input hash inventory;
- launches every mode in a fresh process with `-shadowEarlyCapsule`, `-shadowEarlyCapsuleSha256`, and `-shadowEarlyResult`;
- requires the early Baseline receipt to be `Passed`, callback code 0, same PID, and exact capsule path/hash;
- then requires the existing late failure/publication result from that same PID;
- records binding/capsule/early-result/late-result/log/console hashes in launch schema v2.

`r01_failure_results.py` independently reconstructs each expected binding and capsule from the verified current inputs, verifies the complete immutable inventory, runs the existing strict early receipt verifier, checks the exact executed command and same process identity, then runs the unchanged failure/publication runtime oracle.

The verifier also has a direct `__main__` entrypoint; direct script invocation can no longer succeed without executing verification.

## Primary tests

GitHub Actions workflow `35330989089` at source anchor `50c79913096961636a776ee8254b6631002cdfe5` passed:

- bounded Primary suite: **311/311**;
- R01 early-capsule tests: **7/7**;
- R01 early-results tests: **19/19**;
- R01 failure-pipeline tests: **16/16**.

Artifact:

- ID: `10540898558`
- ZIP SHA-256: `52861f7bca634fa007e4e5fba7cd3774ab8f9dfbf1b39de0c6ca80fba047d139`

The failure-pipeline suite includes missing/stale/substituted/mode-mismatched capsule rejection, same-PID early receipt binding, duplicate-prerequisite handling, exact-command binding, raw/runtime tamper checks, and the direct verifier entrypoint.

This is source/tool contract evidence only. It is not real Unity/IL2CPP Player acceptance.

## Preserved Local evidence

The previous Local checkpoint remains immutable:

`Docs/AssemblyShadow/History/M07R/H1/local-validation-20260918-authority8b/`

It proves the prior `8b1298d...` chain through startup11 and M07 14/14, and records the failure/publication pre-startup refusal. It is historical comparison after the source anchor advances to `50c79913...`; it must not be relabelled as current-anchor V04/V05 acceptance.

Earlier MethodPtr/dense evidence also remains under its original identity.

## Next Local cycle

Because the committed source pin advances to `50c79913...`, regenerate a fresh provenance-bound candidate chain. After normal M07 succeeds:

1. generate control capsules;
2. run startup11;
3. run M07 14/14;
4. run the repaired three-mode failure/publication matrix and strict verifier;
5. regardless of an isolated downstream functional failure, continue other independent V04 cells when source/runtime provenance remains intact;
6. run capacity/lazy-dense/generic/array/reflection/FieldRVA/old-Player/retained coverage/performance;
7. retain the complete current-anchor artifact graph before cleanup;
8. only if acceptance prerequisites are complete, build V05 successor evidence and commission genuine independent whole-chain M08.

Authority/provenance/source-integrity failures still stop the batch immediately.

## Gate

H1 remains `InProgress`. Only genuine independent whole-chain M08 PASS can make it Ready for Human Review Gate. Human H1 approval must then be explicit.

Do not begin R02.
