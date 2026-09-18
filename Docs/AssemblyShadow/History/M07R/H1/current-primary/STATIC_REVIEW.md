# Static Review — R01 Failure/Publication Early Admission Repair

## Verdict

**PASS for Primary → Local Validation handoff.**

This review covers the source/tool repair returned by Local Validation at `af0d345ce3aa7257e301926d0da652709c09cf54`. It does not establish real Unity/IL2CPP Player acceptance, V04/V05 completion, M08 PASS, or Human Review Gate readiness.

Reviewed build-input anchor:

`50c79913096961636a776ee8254b6631002cdfe5`

## Finding closure

### F1 — earliest-startup capsule omission

**Closed in source/tooling; real Player validation required.**

The previous failure launcher invoked the Player without the mandatory `-shadowEarlyCapsule` transport. Native startup correctly refused before managed host continuation.

The repaired launcher always provides:

- `-shadowEarlyCapsule`;
- `-shadowEarlyCapsuleSha256`;
- `-shadowEarlyResult`.

No bypass or disable path was added.

### F2 — direct verifier zero-work invocation

**Closed.**

`r01_failure_results.py` now has a direct `__main__` entrypoint. The public wrapper remains valid as well.

## Design invariants

### Early phase authenticates; later probe owns the transaction

The selected early mode is `Baseline`.

The early callback reads and hashes the P03 closure and all prerequisites but performs no Shadow Configure/Begin/Reserve/Stage/Validate/Commit sequence.

This is required because:

- early `Control` would consume/commit the world before `R01FailureProbe`;
- early `MetadataFailure` or `InitializerFailure` intentionally returns a non-zero callback and stops before host continuation.

The existing C#/native failure transaction implementation is unchanged.

### Capsules are mode-bound

Each failure mode has an immutable `R01FailureEarlyAdmissionBinding` prerequisite. Therefore the three admission capsules differ even though their early execution mode is Baseline.

A capsule from another failure mode cannot pass strict reconstruction.

### Complete failure inputs are authenticated

The capsule prerequisite set includes verified failure-fixture and Q04 negative-input files in addition to the ordinary M07 prerequisite graph.

If an extra prerequisite is already present as a closure DLL/PDB input it is omitted from the prerequisite list, preserving the early callback's no-duplicate-path invariant without dropping byte authentication.

### Immutable inventory freezes after admission materialization

Bindings and capsules are generated before `inputHashesBefore`.

The launch receipt records the same full immutable input graph before and after all three processes. The verifier independently recomputes the inventory.

### Same-process chain is mandatory

For each mode, strict verification requires:

1. exact expected binding bytes;
2. exact reconstructed capsule bytes/hash;
3. early Baseline receipt from the launch PID;
4. early result `Passed`, callback code 0;
5. exact executed command;
6. later failure/publication result from the same PID;
7. existing strict raw diagnostics/capacity/recovery/publication oracle.

Rebinding hashes after tampering does not bypass semantic verification.

### Existing runtime safety is unchanged

No C#, HybridCLR, IL2CPP, native transaction, recovery, capacity, MethodPtr, dense-fixture, M07 workflow-authority, or performance behavior changed in this repair.

Protected reproduction/native/package/IL2CPP/performance pins remain unchanged.

## Adversarial regression coverage

The source tests cover:

- missing capsule;
- stale/hash-mismatched capsule;
- capsule substitution across failure modes;
- wrong early mode;
- early result PID mismatch;
- early receipt capsule-hash mismatch;
- duplicate closure/extra-prerequisite overlap;
- exact command binding;
- late result PID and build binding;
- rebound raw diagnostic/capacity/recovery tampering;
- transaction identity/MVID tampering;
- initializer completion mislabelling;
- profile-contract validation;
- direct verifier entrypoint execution.

## Primary executable evidence

GitHub Actions workflow `35330989089`, commit `50c79913096961636a776ee8254b6631002cdfe5`:

- exact bounded Primary suite: **311/311 Passed**;
- early capsule: **7/7 Passed**;
- early results: **19/19 Passed**;
- failure pipeline: **16/16 Passed**.

Artifact ID `10540898558`, ZIP SHA-256:

`52861f7bca634fa007e4e5fba7cd3774ab8f9dfbf1b39de0c6ca80fba047d139`

The CI workflow itself is part of the reviewed source anchor.

## Source authority review

Candidate source authority is advanced to `50c79913...` because the repair modifies non-metadata Python tooling/tests/workflow files.

The reproduction validation-tool anchor is advanced to the same candidate source anchor. Every declared tooling blob remains byte-identical there and both authenticated deletion paths remain absent.

`shadow_tools.metadata_only()`, `verify_demo()`, and protected refs are unchanged.

All commits after the build-input anchor must remain metadata-only until another explicit Primary source-authority advance.

## Residual empirical requirements

Local must still prove:

- candidate/reproduction preflight under the new source pin;
- real Unity compilation/provenance required by H1;
- fresh controlled and normal M07 chain under the new source pin;
- real earliest Baseline admission for each failure process;
- later Control/Q04/initializer failure/publication semantics in those same processes;
- remaining capacity/lazy/dense/retained/performance matrix;
- evidence retention and V05 successor closure.

## Gate

H1 remains `InProgress`; M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`.

Do not begin R02.
