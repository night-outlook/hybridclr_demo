# Local Validation report

## Current run — 2026-09-17/18 authority `8b1298d` and fresh M07 chain

### Exit

**Local Validation → Primary Implementation: BLOCKED**

Validation ran in `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` from clean handoff checkout `dc64f250c1c47f260625fe60bac80fd26f0c7cdc` on branch `codex/assembly-shadow-r01b-h1`. The authoritative candidate source anchor is `8b1298d6a5979928bdfa30446e2d674d63999b76`.

Environment: macOS 26.5.2 (25F84), Unity 2022.3.62f2, StandaloneOSX arm64, Python 3.14.6, PowerShell 7.6.3, and Apple clang 21.0.0.

Repository state verified before validation:

| Repository | Path | Branch / commit | Result |
| --- | --- | --- | --- |
| Demo | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_demo` | `codex/assembly-shadow-r01b-h1` / `dc64f250c1c47f260625fe60bac80fd26f0c7cdc` | Clean; remote verified |
| HybridCLR | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr` | `codex/assembly-shadow-r01b-h1` / `1d2df7c36a3f9eb99ca8242f6c2bd4a5e054f0ad` | Clean; remote verified |
| HybridCLR Unity | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/hybridclr_unity` | `codex/assembly-shadow-r01b-h1` / `0ea633a2c5b936b5af69d944593c55bd2783fca9` | Clean; remote verified |
| IL2CPP | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/il2cpp_plus` | `codex/assembly-shadow-r01b-h1` / `6be7f38bec2fa4677d24efc1a4a1294240789933` | Clean; remote verified |
| Reproduction tooling | `/Users/ah/GitHub/hybridclr/assembly_shadow_h1r/reproduction_tooling` | detached exact commit `ba8fee33753a5ebc215b7a98739e343d8e05572e` | Clean; protected tooling ref exact |

Protected reproduction `352d7474dd7c2ffd9b9501d8fa42334a3b236e05`, tooling `ba8fee33753a5ebc215b7a98739e343d8e05572e`, and performance-reference `88508b59b7c4ef8c5023cbbe655d43ebfcf5304c` refs remained exact. The native checkout was temporarily detached at protected reproduction pin `99cdb1b67e4ed07b70732a2148cb69e079ca41cf` only for reproduction builds, then restored to `1d2df7c...`; the candidate runtime was reinstalled and reverified afterward.

### Results

| Step | Result | Evidence / limitation |
| --- | --- | --- |
| V00 candidate preflight | `Passed` | `SourceTargetVerifiedNotBuildAccepted`; `codeCommit=8b1298d...`; evidence `_temp/local-validation-20260917-authority8b/v00-candidate`. |
| V00 reproduction preflight | `Passed` | `BehaviorAndToolingSourcesVerifiedNotBuildAccepted`; evidence `_temp/local-validation-20260917-authority8b/v00-reproduction`. |
| V01 Python inventory | `Passed` with explicit skips | Broad: 963 passed / 28 skipped. H1-scoped: 462 passed / 27 skipped; all 27 require an unavailable count-coordination root and are not acceptance. |
| V01 Unity compilation | `Passed` | Candidate and reproduction projects compiled in Unity 2022.3.62f2 with zero errors. |
| V01 fixed-byte policy | `Passed` | `M07FixedByteBootstrapPolicyTests`: 2/2. |
| V02 candidate ON/Debug | `Passed` | Fresh receipt `a460318a...`; build GUID `686f015f...`; strict native and managed source graph passed. |
| V03 candidate modes | `Passed` | Fresh ON/Release, OFF/Debug, OFF/Release receipts; aggregate compiler verifier passed all four candidate modes. |
| V03 reproduction modes | `Passed` after retained first failure | First attempt retained: missing ignored M00 fixed input. Exact expected bytes (`9108a239...`) and `.meta` were restored; fresh ON/Debug and ON/Release then passed with tooling bindings. |
| Controlled M07 | `PassedExpectedFailure` | Post-validation authority succeeded, explicit controlled failure was reached, three guarded files restored exactly, restoration receipt SHA `8f75fa54...`, and fresh post-preflight passed. |
| Normal M07 | `Passed` | Baseline `M07-Baseline-H1-Authority8b-Normal-20260918A`; workflow SHA `1b3301d2...`; restoration receipt SHA `5236c4d6...`. |
| Control capsules | `Passed` | 13 capsule files plus `capsules.json` SHA `17625693...`. |
| Startup11 | `PassedBoundedProfile` | All 11 fresh modes completed with expected exit behavior; strict result SHA `cd322f08...`. |
| M07 Player matrix | `PassedGate3B14Of14` | Corrected invocation supplied `--early-capsule-root`; all 14 fresh processes passed, strict result SHA `ccf24653...`, no missing modes. The initial no-capsule refusal is retained separately. |
| Failure/publication matrix | `Failed` | Current launcher/verifier omit authenticated early-capsule arguments. `R01-Failure-P03-Control` was refused before host continuation; strict error: `exitCode: expected 0, got 1`. |
| Capacity / lazy-dense / retained M03–M07 / performance | `NotRun` | Stopped after the prerequisite failure/publication gate failed. Existing MethodPtr/dense checkpoint remains reusable only for its focused claims. |
| V05 / M08 | `NotRun` | V04 is incomplete. Historical M08 remains `FAIL`. |

### Fresh M07 launch contract

| Artifact | Path | SHA-256 |
| --- | --- | --- |
| Workflow | `_temp/AssemblyShadow/M02Validation-0ce1288da73d4d5581844f365060a7b6/m07-build-workflow.json` | `1b3301d22a2d30109f6ba1f57e00b53284873b71620bb80f2f43ce9b43282b8b` |
| Fixtures | same directory, `m07-fixtures.json` | `0e4036bc803504e9452dbb1881b7390df09f5e8bc7e8fef4db8d5c728ec465fd` |
| Native ON receipt | `_temp/AssemblyShadow/M07PlayerInputs-bff80fcb1e21489d859cd45adfab3b3b/m07-player-build.json` | `b5afad2b527d594f4e81ecda85fc673e0a0a888000673b54c14d58d9689dfc5f` |
| Native OFF receipt | `_temp/AssemblyShadow/M07PlayerInputs-a19c7c7b90bf49fb9e7f9c68516c786b/m07-player-build.json` | `e60aaf47a83fd5c8d85d7abf688234c98a27e1b92e3286b55970d27614fd271c` |
| Editor replay | M02 validation directory, `m07-editor-replay.json` | `f258aa16b83fe9b57f50b961c73feb268ab27eacb1393f8b9fefd5b4b26665ec` |
| Baseline manifest | `HybridCLRData/AssemblyShadow/Baselines/StandaloneOSX/M07-Baseline-H1-Authority8b-Normal-20260918A/baseline-manifest.json` | `fd4bc6d339d126456eccbe0bb324f1805c6c43f476a357da47f7849e07024164` |
| Failure fixtures | `_temp/local-validation-20260917-authority8b/v04-failure-fixtures/failure-fixtures.json` | `da9149fc89974e8c63108ebc1191cf61c0c8d315d4761618f11e6c9036a18f1f` |
| Q04 negative input | `_temp/local-validation-20260917-authority8b/v04-negative-input/q04-metadata-transform.json` | `147b636fb3653c6d475c75d6d4ab0bc3e84919ccbcfba4d9b34d57378bc23f63` |

The authenticated checkpoint is [local-validation-20260918-authority8b](../History/M07R/H1/local-validation-20260918-authority8b/README.md). `raw-evidence.tar.gz` contains 765 receipt/result/log/capsule/fixture files and has SHA-256 `ad5a67fce188b60a861e88e8d034c8f4385c8431472d849140040475440f252d`. Large Player, resource, and input-capture trees remain at their recorded workspace paths and are explicitly hash-bound by the archived ON/OFF and launch receipt input maps. The final post-run preflight again returned `SourceTargetVerifiedNotBuildAccepted` for `8b1298d...`. No cleanup was performed.

### Current gate state

H1 remains `InProgress`; M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`. R02 was not started. The actionable launcher/verifier defect is recorded in [RETURN_TO_WEB.md](RETURN_TO_WEB.md).
