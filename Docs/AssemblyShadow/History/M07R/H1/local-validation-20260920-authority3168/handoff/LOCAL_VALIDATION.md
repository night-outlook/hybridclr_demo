# Local Validation report

## Current run — 2026-09-20 authority `316894a8`

### Exit

**Local Validation → Primary Implementation: RETURN REQUIRED after V04**

Fresh V00 authenticated candidate checkout `9b4eccd0159b41b5172f7b192130eb4d4c380445` and exact source anchor `316894a83873c46ffd3eefa57222311ae03da214`. Candidate authority returned `SourceTargetVerifiedNotBuildAccepted`; reproduction tooling, the exact protected family, and both installed runtimes passed. The candidate runtime receipt was refreshed through `AssemblyShadowBaseline.Editor.BaselineBuild.InstallRepeatability` before verification.

The direct PowerShell binder repair passed and both real controlled workflows entered `native-on-controlled`, so the prior parameter-binding defect is fixed. Neither workflow completed: protected profile-1 built Native ON but failed the next exact-source guard after Unity changed `ProjectSettings.asset`; current profile-2 failed inside Native ON provenance capture because its nested `--skip-demo-source` verification inherited the outer M07 authority context. Both projects were restored to clean pinned tracked bytes and their installed runtimes re-verified.

### Results

| Cell | Result | Evidence / disposition |
| --- | --- | --- |
| V00 candidate authority | `Passed` | Exact checkout and `SourceTargetVerifiedNotBuildAccepted` for `316894a8...` |
| V00 reproduction/protected refs | `Passed` | Reproduction tooling bound to current anchor; protected demo/native/package/IL2CPP commits exact |
| V00 installed runtimes | `PassedAfterCandidateReceiptRefresh` | Candidate and protected runtime source/inventory verification passed with Shadow ON |
| V01 complete Python inventory | `PassedWithExplicitSkips` | 1,016 discovered/executed: 988 passed, 28 explicit skips, no failures |
| V01 bounded Primary | `Passed` | 324/324 |
| V01 direct PowerShell binder | `Passed` | Four valid labels accepted; invalid rejected; `unityInvoked=false` |
| V01 direct handoff/R01/lazy | `Passed` | 11/11, 7/7, 20/20, 20/20, 16/16, and 10/10 |
| V01 broad Unity EditMode | `Passed` | 1,076/1,076, no failures or skips |
| V01A source-scope audit | `PassedExactExpectedScope` | Exactly four non-metadata CI/tool/test paths; no runtime/native/performance-protocol input changed |
| V02/V03 six compiler cells | `ReusedAuditedFrom925e` | Original checkpoint remains authoritative; not relabelled current-anchor PASS |
| V04 unaffected runtime matrix | `ReusedAuditedFrom925e` | Normal M07, startup11, 14/14, failure, dense, capacity, parser/native/index/generic/cache/capability retained under original hashes only |
| V04 profile-1 controlled performance | `FailedAfterNativeOnControlledSuccessBeforeNativeOff` | Native ON Player/evidence passed; `link.xml` restored; next guard rejected changed `ProjectSettings.asset`; Native OFF not run |
| V04 profile-2 controlled performance | `FailedDuringNativeOnControlledBeforePlayerCompletion` | Nested verifier rejected inherited M07 context plus `--skip-demo-source`; no successful controlled Player |
| V04 exact restoration | `PassedWithPreservedManualRecoveryForUndeclaredPath` | Declared outer paths and `link.xml` restored by workflow; both failed `ProjectSettings.asset` bytes preserved then exactly restored; runtimes reverified |
| V04 old-Player | `Blocked / NotRun` | Two complete fresh performance graphs do not exist |
| V04 map / preregistration | `Blocked / NotRun` | Four controlled Player receipt/evidence pairs do not exist; `ComparabilityPassed` not claimed |
| V04 pilots / formal / analysis | `Blocked / NotRun` | Strict frozen-map prerequisite absent; no performance sample launched |
| V05 / independent M08 | `Blocked / NotRun` | Mandatory V04 evidence incomplete |

### Source-scope audit and audited reuse

The full `git diff --name-status` from `925e84d7b653bc7434482e6f4fbde39a4d9fcd0e` to `316894a83873c46ffd3eefa57222311ae03da214` is retained. The only non-metadata paths are `.github/workflows/h1-bee-primary.yml`, `Invoke-M07Build.Core.ps1`, its authority test, and the new PowerShell binder test. The production change is exactly the four-label `ValidateSet` expansion.

The original `925e84d7...` checkpoint is therefore referenced only as `ReusedAuditedFrom925e`. Its receipt and archive hashes are recorded in `reused-audit-catalog.json`; no historical result is labelled fresh current-anchor PASS.

### Controlled-workflow failures

Profile-1 proves the label fix works in real Unity: `native-on-controlled` produced build GUID `1f1591b62163402d9ff1db23a84340eb`, executable SHA-256 `e3d12892d9d4649bc89725f7ad8205d5797307219f7a9ee0848d264751807b8e`, native library SHA-256 `e7ebb313aecc24eda259cd2fd11a87b3f6528fbcc7d93ac4381f319a1c69f24e`, and passed controlled evidence. The next authority guard found the semantically restored but byte-different `ProjectSettings.asset` serialization and stopped before Native OFF.

Profile-2 failed earlier. `H1BuildInputProvenance` invoked the current verifier with `--skip-demo-source` while the outer M07 authority environment remained active. The verifier correctly rejected that unsupported combination. The failure evidence is provenance-incomplete and no Player receipt was accepted.

The root causes and concrete Primary directions are in `RETURN_TO_WEB.md`.

### Commands

```text
pwsh -NoProfile -File Tools/AssemblyShadow/tests/test_m07_generated_input_recovery_labels.ps1
python3 Tools/AssemblyShadow/h1_test_inventory.py python ...
python3 Tools/AssemblyShadow/h1_bee_primary_tests.py ...
pwsh -NoProfile -File Tools/AssemblyShadow/Invoke-ShadowEditorTests.ps1 -TestFilter 'HybridCLR.Editor.AssemblyShadow.Tests;AssemblyShadowDemo.EditorTests'
pwsh -NoProfile -File <candidate>/Tools/AssemblyShadow/Invoke-M07Build.ps1 -ProjectPath <protected> -BaselineId M07-Baseline-H1-Perf-Reference-3168-20260920A -TimeoutSec 28800 -BuildTarget StandaloneOSX -ControlledPerformanceBuilds
pwsh -NoProfile -File <candidate>/Tools/AssemblyShadow/Invoke-M07Build.ps1 -ProjectPath <candidate> -BaselineId M07-Baseline-H1-Perf-Current-3168-20260920A -TimeoutSec 28800 -BuildTarget StandaloneOSX -ControlledPerformanceBuilds
```

### Retention checkpoint

The authenticated pre-cleanup checkpoint is `Docs/AssemblyShadow/History/M07R/H1/local-validation-20260920-authority3168/`. It contains fresh V00/V01, the scope audit, exact reuse catalog, both full workflow logs, successful profile-1 Native ON receipt/evidence, both failure transactions, restoration evidence, mutated-byte snapshots, final runtime verification, an artifact index, raw archive, and manifest. No cleanup was performed.

H1 remains `InProgress`; the last independent M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. `WEB_TO_LOCAL.md`, source/preflight verification, protected pins, and R02 were not modified.
