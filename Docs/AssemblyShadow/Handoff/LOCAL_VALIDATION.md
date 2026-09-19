# Local Validation report

## Current run — 2026-09-19 authority `99ef65db`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED after V04**

Fresh V00 validated candidate checkout `fe441e3e73f68bd1f237fe1264c93fb358004cbd` and exact source anchor `99ef65db13341f54cf610e18453dddf197ee86e4`. Candidate authority returned `SourceTargetVerifiedNotBuildAccepted`; reproduction tooling, protected refs, and freshly verified installed runtimes passed strict checks. No earlier attempt was reused or relabelled.

V00–V03, controlled and normal M07, startup11, the M07 14-mode matrix, ordinary and exact-mixed capacity execution, deterministic dense-v2 generation, parser/FieldRVA/native coverage, the protected profile-1 M07 graph, and old-Player rejection passed. Four controlled Development Players also passed provenance capture, and the A/B freezer returned `ComparabilityPassed`. Three independent V04 contracts nevertheless failed: strict failure/publication verification rejected Q04 history, the lazy Player threw before dense execution, and the first performance pilot found that both controlled Player baselines differ from their supplied fixture graphs. V05/M08 therefore did not run.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | `SourceTargetVerifiedNotBuildAccepted`; candidate `fe441e3e...`, source `99ef65db...` |
| V00 reproduction/protected refs | `Passed` | `BehaviorAndToolingSourcesVerifiedNotBuildAccepted`; exact protected refs; candidate and protected installed runtimes verified with Shadow ON |
| V01 Python and direct suites | `PassedWithIsolatedStaleExpectation` | Full Python 1008/1009 passed with 28 skips; the lone failure expects the pre-repair 11-mode inventory. Bounded Primary 320/320 and all requested direct suites passed |
| V01 Unity compile | `Passed` | Fresh Unity 2022.3.62f2 batch compile clean |
| V01 broad EditMode | `FailedIsolatedBroadTest` | 1074/1075; one stale temp-root literal expectation; focused affected coverage passed separately |
| V02/V03 provenance builds | `Passed` | Fresh current-anchor and reproduction-tooling builds passed with exact restoration; wrong-pwsh failure retained |
| V04 controlled M07 | `PassedExpectedFailureAndExactRestoration` | Deliberate recovery failure reached only after authority checks; workflow-owned bytes restored exactly |
| V04 normal M07 | `Passed` | Baseline `M07-Baseline-H1-Authority99ef-Normal-20260919A`; fresh fixture/ON/OFF/replay graph and exact outer restoration |
| V04 control capsules | `Passed` | 13 current capsules; `capsules.json` SHA-256 `9ce3dbb9...` |
| V04 startup11 | `PassedBoundedProfile` | 11 fresh processes; strict result SHA-256 `9242101c...` |
| V04 M07 Player matrix | `PassedGate3B14Of14` | Strict 14/14; result SHA-256 `a0364af3...` |
| V04 failure/publication | `Failed` | All three earliest-owned transactions launched with bound capsule/PID/log/hash evidence; strict verifier rejected Q04 `firstUseHistory` for selected-closure or non-candidate baseline use |
| V04 ordinary capacity | `Passed` | 8192-entry / 536,870,912-byte Player passed in 530 seconds; 8193 refusal and exact accounting verified |
| V04 exact mixed boundary | `Passed` | 536,733,184 ordinary + 137,728 shadow = 536,870,912 bytes; Player exit 0 in 596.7 seconds; strict receipt retained |
| V04 dense-v2 producer | `Passed` | Deterministic IDs 1 and 2; each generator command has the corrected four-field contract |
| V04 lazy Player | `FailedRuntimeNoDenseCoverage` | Diagnostic Player launched and 51 preconditions passed, then dense boundary type lookup resolved against `mscorlib` and threw `TypeLoadException`; `denseFixtures=0` |
| V04 parser / FieldRVA | `Passed` | 8,192-file corpus, 8,196 FieldRVA rows, both dense IDs, bounded readers, and sanitizer checks passed |
| V04 capacity/index/generic/cache | `Passed` | Fresh index-range/runtime, generic constraint, type-cache, capability, attribute, codec, overflow, and live-capability coverage passed |
| V04 retained M03–M06/R01 native | `Passed` | Fresh M03–M06, budget, contention, recovery, startup, transaction, attribute, constraint, and count suites passed |
| V04 protected profile-1 install | `Passed` | Isolated exact reference family; source and installed-runtime verification passed before and after workflow/builds |
| V04 protected profile-1 M07 | `Passed` | Current candidate coordinator ran with `-ProjectPath <reference-demo>` and produced a fresh profile-1 fixture/ON/OFF/replay graph with exact outer restoration |
| V04 old-Player rejection | `PassedExpectedRejection` | Profile-1 Baseline admitted early; profile-2 inputs were refused before Configure; verification result `Passed` |
| V04 controlled Development builds | `PassedFourOfFour` | Current and reference ON/OFF builds each passed provenance capture, Release native compilation, Low stripping, OptimizeSpeed, no debugger/profiler |
| V04 frozen build map | `ComparabilityPassed` | Common measurement and witness hashes matched; expected ABI/source-pin differences were authenticated |
| V04 preregistration | `Passed` | Protocol bytes unchanged, schedule semantic fields unchanged, 44 pairs retained |
| V04 performance pilot | `FailedBeforePlayerLaunch` | Pilot 1 failed closed on both sides: controlled Player baseline IDs differ from the supplied fresh M07 fixture baseline IDs; no performance sample was taken |
| V04 formal performance | `Blocked / NotRun` | Four successful pilots are mandatory; formal sampling correctly refused to begin |
| V05 / M08 | `Blocked / NotRun` | Mandatory failure, lazy, and performance prerequisites are incomplete |

### Failure analysis

The failure/publication repair moved transaction ownership to the earliest callback as intended, and the late probe is persistence-only evidence. Control and initializer evidence remained coherent, but strict Q04 verification found a selected-closure or non-candidate baseline use in `postHost.firstUseHistory`. That is an isolated runtime-oracle failure, not an authority or shared-input failure.

The corrected dense-v2 contract reached the diagnostic Player. The runner authenticated 51 setup/input checks, but the Player attempted to resolve `AssemblyShadow.Workload.DenseType_0001_4095_MetadataBoundary_...` from `mscorlib`, raised `TypeLoadException`, and executed zero dense fixtures. This is a real runtime failure, not `NoCoverage` from a prelaunch schema guard.

The protected-reference M07 sequencing repair worked: the current candidate wrapper drove the protected project and restored it exactly. All four later controlled Development builds also passed. The strict freezer, however, accepted the normal-M07 fixture/replay graphs alongside controlled Players built under new immutable performance baseline IDs. Pilot 1 independently reconstructed the inputs and rejected both sides before launch: profile 1 expected `M07-Baseline-H1-ProtectedProfile1-20260919A` but received `M07-Baseline-H1-Perf-Reference-20260919A`; profile 2 expected `M07-Baseline-H1-Authority99ef-Normal-20260919A` but received `M07-Baseline-H1-Perf-Current-20260919A`. Formal sampling did not begin.

### Retention checkpoint

The authenticated pre-cleanup checkpoint is [local-validation-20260919-authority99ef](../History/M07R/H1/local-validation-20260919-authority99ef/README.md). `MANIFEST.sha256` binds this report, the summary, artifact index, and raw-evidence archive. The archive retains the complete bounded launch contract and failed states; large reproducible payloads remain live and receipt-bound. No cleanup was performed.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. `WEB_TO_LOCAL.md`, source/preflight verification, protected pins, and R02 were not modified.
