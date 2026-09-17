# Local Validation report

## Current run — 2026-09-17 M07 recovery and downstream validation

### Exit

**Local Validation → Primary Implementation**

Candidate checkout `65d8b25b0d98ef47f63d2a3df8c94ed97eedbe4c` on `codex/assembly-shadow-r01b-h1` was validated against source anchor `68df00fe31a199491b313cc17f25575663b7452b`. Unity was 2022.3.62f2 targeting StandaloneOSX arm64. Protected reproduction, native, package, IL2CPP, and performance-reference pins remained unchanged.

The bounded Local repairs are committed. Native ON and OFF Player generation now snapshot, authenticate, and restore tracked `Assets/HybridCLRGenerate/link.xml`. The outer M07 wrapper now restores its exact three guarded workflow inputs on successful and failed exits. Focused policy tests pass 5/5, the authoritative Python inventory passes 986 with 28 skips, and `M07FixedByteBootstrapPolicyTests` passes 2/2 in Unity.

Fresh normal M07 baseline `M07-Baseline-Consolidation-Recovery-Normal-20260917C` passes compiler-input validation, post-validation authority, baseline resources, Native ON, Native OFF, structural prepare/compile/restore, fixture finalization, and Editor replay. Both generated linker restorations pass. The success-path outer receipt is `M07OuterSuccessRestoration / ExactBytesRestored`, and post-run source preflight returns `SourceTargetVerifiedNotBuildAccepted` with a clean tracked checkout.

Downstream validation found a new nontrivial blocker before startup11 launches a Player. The fresh frozen `AssemblyShadowDemo.Bootstrap.dll` is a real Unity `#-` metadata image containing 1,675 `MethodPtr` rows. `m05_types.CliTables` rejects every nonempty pointer table. The same failure prevents generation of authenticated M07 early-control capsules. Local did not remove that guard or reinterpret the tables because the handoff prohibits broadening acceptance semantics locally.

The 8,192-entry capacity corpus was recovered from the verified cleanup archive plus deterministic regeneration of its nine absent tail members. All 8,192 hashes match the sealed manifest and total 536,870,912 bytes. The separate overflow fixture also passes. Capacity cannot run until the current M07 capsule chain verifies. The cleanup archive retained the dense adjunct manifest and historical PASS audit but omitted its two sealed 1 MiB DLLs, so lazy/dense acceptance is `Unavailable`, not reused or passed.

Independent retained native checks pass for M03, corrected M03 visibility (18,988 checks), M04, M05, M06, R01B attribute batch, constraints, index range, index runtime, type cache, live capability, and codec kernel. The initial M03 visibility invocation with the wrong generated-root depth and the dense-parser failure were preserved. No result is promoted to Player acceptance.

### Validation results

| Step | Result | Empirical result |
| --- | --- | --- |
| V00–V03 | `Pass` | Prior current-chain preflight, Unity/NUnit, six-build provenance, retention, candidate count, and reproduction evidence remain authenticated under their original identities. |
| V04 controlled M07 | `PassExpectedFailure` | Exact controlled throw, post-validation authority, mutation proof, three-file recovery, and post-recovery preflight pass. |
| V04 normal M07 | `Pass` | Resources, Native ON/OFF, linker restoration, structural fixtures, finalization, Editor replay, and exact success restoration pass. |
| startup11 | `BlockedPreLaunch` | Strict verifier rejects 1,675 `MethodPtr` rows in the fresh `#-` Bootstrap assembly. |
| M07 Player matrix | `BlockedPreLaunch` | Authenticated control capsules cannot be produced for the same verifier reason. A capsule-free launch was retained as diagnostic-only and is not an M07 behavioral failure. |
| capacity 8192/8193 | `InputsRecovered / Blocked` | 8,192 files and 512 MiB verify exactly; fresh diagnostic/capsule chain remains blocked. |
| retained native coverage | `Pass`, except dense parser `Unavailable` | M03–M06 and listed R01B native checks pass; dense DLL bytes are absent. |
| lazy/dense / old Player / performance | `Blocked / NotRun` | No valid fresh current-anchor capsule chain; dense inputs also unavailable. |
| V05 / M08 | `Blocked / NotRun` | No complete fresh chain; independent whole-chain M08 was not commissioned. |

Portable evidence is under [local-validation-20260917-link-recovery](../History/M07R/H1/local-validation-20260917-link-recovery/README.md). Earlier evidence remains under its original identity. Actionable issues are in [RETURN_TO_WEB.md](RETURN_TO_WEB.md).

H1 remains `InProgress`; last independent whole-chain M08 remains `FAIL`; `humanGatePassed=false`; `mayEnterR02=false`; R02 was not started.
