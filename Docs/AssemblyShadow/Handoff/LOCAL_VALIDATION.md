# Local Validation report

## Current run — 2026-09-18 authority `af56b841`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED after V04**

The clean candidate checkout was fast-forwarded to exact requested commit `66b4b86570bce92e65e99ba795eb9c4f72582c8c` on `codex/assembly-shadow-r01b-h1`. Fresh V00 established `SourceTargetVerifiedNotBuildAccepted` for exact candidate source anchor `af56b841e9ae80be0b1748e546338f9b68da2717`; no receipt from blocked attempt `f8a2766d...` was reused or relabelled.

V00–V03, controlled M07, normal M07, startup11, and the strict M07 14-mode matrix passed. The repaired failure/publication launcher successfully created three mode-bound Baseline capsules and obtained successful earliest-admission receipts from the same three Player PIDs, but every late probe failed before its intended Control/Q04/initializer oracle. The public strict verifier therefore returned `Failed`.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | `SourceTargetVerifiedNotBuildAccepted`; checkout `66b4b865...`, source `af56b841...` |
| V00 reproduction/protected refs | `Passed` | Tooling `ba8fee33...`; protected reproduction `352d7474...`; performance `88508b59...` |
| V01 Python inventory | `PassedWithSkips` | Broad 969 passed / 28 skipped; H1 463 passed / 27 skipped; bounded Primary 312/312; Unity compile clean; fixed-byte tests 2/2 |
| V02 candidate smoke | `Passed` | Fresh On/Debug build after stale installed-runtime receipt was corrected by a fresh candidate install |
| V03 candidate/reproduction | `Passed` | Four candidate modes and two reproduction modes; strict compiler/provenance verification passed |
| V04 controlled M07 | `PassedExpectedFailureAndExactRestoration` | Deliberate post-validation failure; three guarded files exact-byte restored |
| V04 normal M07 | `Passed` | Baseline `M07-Baseline-H1-AuthorityAf56-Normal-20260918A`; exact outer restoration |
| V04 startup11 | `PassedBoundedProfile` | 11 fresh processes; expected positive/rejection exits; inputs unchanged |
| V04 M07 Player matrix | `PassedGate3B14Of14` | 14 distinct PIDs; strict verifier `resultPassed=true`, no missing modes |
| V04 failure/publication | `Failed` | Earliest admission passed in all three same-PID processes; all late probes failed `Selected patch is not the complete baseline-bound budgeted closure`; strict verifier failed on Control exit 1 |
| V04 8192/8193 capacity | `Passed` | Ordinary envelope Player passed; complete before/after hashes unchanged |
| V04 mixed boundary | `Passed` | Exact 512 MiB mixed workload and Player passed; inputs unchanged |
| V04 dense / FieldRVA / parser | `Passed` | 8,192 files, 8,196 FieldRVA rows, both deterministic dense-v2 fixtures, bounded BlobReader and sanitizer checks passed |
| V04 lazy Player | `Failed / NoCoverage` | Fresh dense generator emits schema v2; lazy runner requires unavailable sealed-v1 manifest inventory and rejected it before launch |
| V04 generic/index/cache/capability | `Passed` | Constraint 34, index range 49, index runtime 157, type cache 77, attribute 4,197+4,197, live capability 16,396 per native feature state plus managed tests |
| V04 retained M03–M06/R01 native | `Passed` | Fresh M03–M06, visibility, budget/contention/recovery/startup gateway/startup/transaction and codec suites passed with stable inputs |
| V04 old-Player rejection | `Unavailable / NotRun` | No immutable profile-1 fixture/ON/OFF/replay/Player graph exists in the listed checkout; not reconstructed |
| V04 controlled performance | `Unavailable / NotRun` | Protected ref is exact, but no protected-reference Development Player/build map exists in the listed checkout; not reconstructed |
| V05 / M08 | `Blocked / NotRun` | Mandatory failure matrix, lazy, old-Player, and performance prerequisites are incomplete |

### Failure root cause

The early-admission repair works: each mode has a schema-v2 binding, distinct Baseline capsule, successful early receipt, exact command/PID binding, late result from the same PID, complete logs, and identical before/after hashes across 17,275 inputs.

The late Player probe still hard-codes `patch.nativeBudgetCapabilityVersion == 1` in `R01FailureProbe.cs`. The fresh normal M07 baseline and all selected patches use capability profile 2. Consequently every mode is rejected by the shared pre-oracle closure guard before Control, Q04, or initializer-specific behavior can execute. This is the direct failure and the reason the Primary-tested early-path repair is not Local-accepted.

The lazy-path tooling has a second independent contract mismatch: `create-r01b-dense-fixtures.py` produces `R01BDenseAdjunctManifest` schema 2, while `run-r01b-lazy-player.py` accepts only the historical `R01BWorkloadV3DenseMetadataAdjunct` schema 1 inventory. The strict native parser does accept and pass the fresh deterministic schema-2 fixtures; the lazy Player has `NoCoverage`.

### Retention checkpoint

The pre-cleanup checkpoint is [local-validation-20260918-authorityaf56](../History/M07R/H1/local-validation-20260918-authorityaf56/README.md). `MANIFEST.sha256` authenticates its report, summary, artifact index, and 49 MiB archive. The archive contains 901 files, including V00–V03 receipts, controlled/normal restoration, the complete current M07 receipt set, control capsules, startup11, 14-mode results/logs, failure binding/capsule/early/late/log evidence, capacity results, dense/lazy inputs, and retained native receipts. Large live Players, compiler snapshots, resources, and 512 MiB corpora were not copied into Git; their complete file hashes remain bound by the archived strict receipts and before/after input maps. No cleanup was performed.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. `WEB_TO_LOCAL.md`, source verification, protected pins, and R02 were not changed.
