# Local Validation report

## Current run — 2026-09-18 authority `4fff4df2`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED after V04**

Fresh V00 validated candidate checkout `f480d3a6cccbbc4d3728dc0cf46ad8723f99fb53` and exact source anchor `4fff4df26681ab3595bb241bbc972207d032831e`. Candidate authority returned `SourceTargetVerifiedNotBuildAccepted`; reproduction tooling, protected refs, and a freshly installed candidate runtime passed strict checks. No historical attempt was relabelled.

V00–V03, controlled and normal M07, startup11, the M07 14-mode matrix, current capacity/parser/index/native coverage, and the fresh deterministic dense-v2 producer passed. Two independent V04 contracts failed: all three failure/publication late probes returned `BaselineAlreadyUsed` after successful same-PID early admission, and the lazy verifier rejected the producer's four-element `generator.generateCommands` entries because it requires three elements. The protected profile-1 runtime was installed and verified, but its own M07 workflow modified the protected tracked scene before invoking strict source verification and therefore failed closed. Old-Player and performance work remain `Unavailable / NotRun`.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | `SourceTargetVerifiedNotBuildAccepted`; candidate `f480d3a6...`, source `4fff4df2...` |
| V00 reproduction/protected refs | `Passed` | `BehaviorAndToolingSourcesVerifiedNotBuildAccepted`; exact protected refs; fresh installed-runtime receipt SHA-256 `12a118df...` |
| V01 Python and direct suites | `PassedWithSkips` | Full Python 1008 passed / 28 skipped; bounded Primary 319/319; handoff 11/11; capsule 7/7; early results 19/19; failure pipeline 17/17; lazy contract 8/8 |
| V01 Unity compile | `Passed` | Fresh batch compile clean |
| V01 broad EditMode | `FailedIsolatedBroadTest` | 1074/1075; stale expected temp-root literal in `WorkflowRestoresExactProjectSettingsBytesAcrossFreshEditors`; affected focused suite subsequently passed 24/24 |
| V02/V03 candidate builds | `Passed` | Candidate ON/OFF Debug/Release all passed with exact restoration |
| V02/V03 reproduction builds | `PassedAfterFreshProtectedInput` | Initial missing/generated M00 attempts retained as failed; exact protected fixed input restored; ON Debug/Release passed |
| V04 controlled M07 | `PassedExpectedFailureAndExactRestoration` | Baseline `M07-Baseline-H1-Authority4fff-Controlled-20260918A`; deliberate failure after compiler inputs; `ExactBytesRestored` |
| V04 normal M07 | `Passed` | Baseline `M07-Baseline-H1-Authority4fff-Normal-20260918A`; fresh fixture/ON/OFF/replay graph and exact outer restoration |
| V04 control capsules | `Passed` | 13 current capsules; `capsules.json` SHA-256 `8aeff837...` |
| V04 startup11 | `PassedBoundedProfile` | 11 fresh processes with expected success/rejection results; inputs unchanged |
| V04 M07 Player matrix | `PassedGate3B14Of14` | Strict 14/14, no missing modes; result SHA-256 `818d52a4...` |
| V04 failure/publication | `Failed` | Three mode-bound capsules and successful same-PID early receipts; every late result was `BaselineAlreadyUsed`; strict verifier failed on Control's exit 1 |
| V04 ordinary capacity | `Passed` | 8192/8193-envelope Player passed in 521 seconds; before/after hashes unchanged |
| V04 exact mixed boundary | `Passed` | 536,733,184 ordinary + 137,728 shadow = 536,870,912 bytes; Player passed in 540 seconds; inputs unchanged |
| V04 dense-v2 producer | `Passed` | Deterministic IDs 1 and 2; manifest SHA-256 `f7c5cc9f...` |
| V04 lazy Player | `Failed / NoCoverage` | Fresh current-baseline diagnostic Player built; runner rejected dense-v2 command inventory before Player launch: producer emits four fields, verifier requires three |
| V04 parser / FieldRVA | `Passed` | 8,192-file corpus, 8,196 FieldRVA rows, both dense IDs, bounded reader, and sanitizer checks passed |
| V04 capacity/index/generic/cache | `Passed` | Index range 49; index runtime 157; generic constraint 34; type cache 77 |
| V04 capability/attribute | `Passed` | 16,396 checks per native feature state plus managed coverage; attribute 4,197 Release + 4,197 ASan |
| V04 retained M03–M06/R01 native | `Passed` | Fresh M03–M06, budget 2,684, recovery 498, contention 35,328, startup gateway, startup, and transaction suites passed |
| V04 protected profile-1 install | `Passed` | Isolated exact reference worktrees; protected source and installed-runtime verification passed, installed receipt SHA-256 `54bfe84c...` |
| V04 protected profile-1 M07 | `Failed` | Workflow generated the new baseline into protected tracked `M07Bootstrap.unity`, then its strict source verifier correctly rejected the changed bytes; tracked bytes restored and protected verification passed again |
| V04 old-Player rejection | `Unavailable / NotRun` | Fresh protected profile-1 M07/Player graph was not established |
| V04 controlled performance | `Unavailable / NotRun` | Four authenticated Development builds, frozen build map, and preregistration binding could not be created without the profile-1 M07 graph |
| V05 / M08 | `Blocked / NotRun` | Mandatory failure, lazy, old-Player, and performance prerequisites are incomplete |

### Failure analysis

The failure/publication repair proves the new earliest-admission layer: each mode has a mode-bound schema-v2 binding, Baseline capsule, successful early receipt, exact command/PID binding, late result from the same PID, logs, and immutable before/after hashes. The late phase nevertheless attempts a transaction after early Baseline admission has consumed the one-use baseline state, so all three modes terminate as `BaselineAlreadyUsed` before their Control/Q04/initializer oracle. The strict verifier correctly rejects the matrix.

The lazy path has an independent producer/verifier schema mismatch. The fresh dense-v2 manifest records each generation command as four values (`mono`, generator executable, fixture ID, output DLL), while the lazy verifier requires exactly three. It fails closed before starting the otherwise valid current-baseline diagnostic Player; this is `NoCoverage`, not a runtime pass or failure.

The protected profile-1 workflow also fails closed for a separate sequencing defect: it writes the requested new baseline ID to the protected tracked scene before running its source-integrity verifier. The verifier detects that mutation as designed. After exact restoration, both protected-ref and installed-runtime verification pass again, but no reference M07 graph exists, so old-Player and A/B performance evidence cannot be generated.

### Retention checkpoint

The authenticated pre-cleanup checkpoint is [local-validation-20260918-authority4fff](../History/M07R/H1/local-validation-20260918-authority4fff/README.md). `MANIFEST.sha256` binds the report, summary, artifact index, and 46 MiB raw-evidence archive. The archive contains 5,060 entries covering V00–V03 and the current M07 fixture/build/replay/capsule/startup contract, failure evidence, dense/lazy evidence, capacity receipts, native coverage, and protected-reference receipts. Large reproducible compiler snapshots, copied assembly/reference trees, resource payloads, Player bundles, and the 512 MiB corpus remain in the live validation workspaces and are hash-bound by retained receipts; no cleanup was performed.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. `WEB_TO_LOCAL.md`, source/preflight verification, protected pins, and R02 were not modified.
