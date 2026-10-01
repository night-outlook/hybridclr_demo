# Current Status — R03 batch-B blockers repaired; awaiting batch C

## Current state

R02 remains accepted as **PassedWithExplicitDeferredRisk** under its separately committed owner decision. R03 is in progress. The conservative product candidate remains implemented, but **R03Accepted=false; H2Passed=false**. PureInterpreter expansion remains disabled.

- Last Local return: `ec463b6dfbd91603ec0c539378af6dbbe6b9e651`.
- B executed demo `a261bdf0db3f1432226a6b6b69f6f56fbbc47d34` once.
- B remains **ReturnRequired: 12 Passed / 5 Failed / 19 Blocked**, focused seal Passed.
- Direct managed lifetime, both 9-case graph suites, 35 admission cases and fifteen-DLL generation passed in B.
- Four Unity builds and EditMode failed at compilation; Editor assertions, IL2CPP/native builds and all nineteen Players did not run.
- R03-LB-001: fixture-reference encoding **fixed and host compiler-validated; pinned Unity revalidation required**.
- R03-LB-002: Unity supervisor integration **implemented and real shared-compiler host-validated; actual Unity revalidation required**.
- Next cycle: **Local C requested; NotRun**.

Read the unchanged Local-owned `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for B facts. Read `History/M07R/R03/D_INPUT_REPAIR.md`, `D_HOST_EVIDENCE.json`, `D_VALIDATION_MATRIX.md` and the live `Handoff/WEB_TO_LOCAL.md` for the new repair/validation authority. Earlier preparation records do not authorize retrying A or B.

## Preserved evidence

B checkpoint: `History/M07R/R03/local-validation-20260930-batch-b-return-required/`.
Retained live B root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime`.
Local authenticated **407 indexed files / 408 archive members**. The seal establishes custody of the failed run, not native acceptance.

B result/index/archive SHA-256:
- `3c8646fa68556b987469467c473e7bff6b529abbd8df3b1693a0a49a20738870`
- `ec1feae707274098acfbce3f83696a0ce1d2aa734318254bb84d54878cb63887`
- `a09d5480508a6d40bf619f925b76144693faf5ed637dbf7ac1c7fed5cec86ebd`

A remains ReturnRequired, 4 Passed / 3 Failed / 29 Blocked, with its original seal and checkpoint untouched. Successful B managed execution does not backdate a PASS into A. B's exact dotnet survivor identity is not retroactively inferred from the new supervisor tests.

## New source authority

All four repositories use `codex/assembly-shadow-r01b-h1`.

| Repository | Exact authority |
| --- | --- |
| night-outlook/hybridclr_demo | tested executable/CI anchor `5c2932d5340728b16302b7cea8f20b64fcc9e7ce`; execute the final docs-only transport supplied in Primary's prompt and resolved by the live handoff |
| night-outlook/hybridclr | `041c0cbb42d3e64e54fe605673d99799b5d63893` — unchanged |
| night-outlook/hybridclr_unity | `120bb01be680cec0375002a0823552d66d34b84c` — unchanged |
| night-outlook/il2cpp_plus | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` — unchanged |

Implementation commit `c72893c0df9452aa46a45a1f723b71f62512a0e6` fixes the generator and integrates supervised Unity invocation plus compiler-consumer tests. Final source `5c2932...` corrects a new test consumer's static/instance calling shape; it does not change the value fixture or native expectation. Only documentation/evidence may differ after the final tested anchor.

The authoritative final demo transport is the latest commit touching WEB_TO_LOCAL.md, required to equal local HEAD, current remote HEAD and the exact Primary prompt. Do not use an arbitrary later HEAD or an old source/smoke/batch commit. The runner rechecks all four source authorities at entry and finish.

## Completed Primary checks

Final CI run **36805988857** at source **5c2932d5340728b16302b7cea8f20b64fcc9e7ce** passed on **Linux x86_64 and macOS 15.7.9 arm64**, SDK **8.0.318**. Each platform passed 57 Python contracts, both 9-case graph suites, 35 admission/method assertions, fifteen-DLL generation and the actual Runtime API compile. All 33 fixture metadata checks and actual compiler consumers passed. The separate invalid-key control produced the specific CS0009/Invalid public key failure with no emitted consumer.

Real SDK Roslyn `/shared` success/failure cases observed owned compiler children, authenticated and retired them using the same supervisor policy, retained original inner exits, and left an unrelated sentinel running. All 49 positive and 2 deliberately negative outer commands completed without surviving groups. Primary authenticated both final downloaded ZIPs: **620 indexed files / 621 ZIP files per platform**. `D_HOST_EVIDENCE.json` binds exact jobs, artifacts, platform, result hashes and command inventories.

These are host compiler/supervisor results, not Unity Editor or IL2CPP execution. Actual pinned Unity compiler consumption and valid/invalid Editor probes are implemented for Local C. The first Primary CI attempt failed on an incorrect consumer call shape; that failed attempt remains recorded, not relabeled.

## Next Local batch

Follow `Handoff/WEB_TO_LOCAL.md` for one invocation at the new prescribed root:

`/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001C-inputs`

Verify the root is unused. Use the recorded Unity 2022.3.62f2 and SDK 8.0.318 paths. Do not retry A/B, reuse an existing root, relax metadata/consumer/cleanup checks or perform non-trivial implementation locally.

All **36 cells / four native build roles / nineteen Player cases** remain. The fixture cell adds 33 pinned-Unity compiler consumers, an explicit invalid-key consumer control and two isolated Editor compiler/lifecycle probes. All normal Unity build and EditMode invocations use the supervisor while the outer no-survivor policy remains unchanged. Failed compiler controls remain visibly failed commands inside separate expected-negative assertions, not successful product builds.

All cells and the focused seal must pass for EvidenceReadyForPrimaryReview; otherwise return ReturnRequired. Local commits/pushes factual reports and a new immutable C checkpoint, then stops for Primary reconciliation.

## Remaining risks and gates

R02-D1 CPU residuals and the original H1 +18–19 MiB RSS risk remain visible through H2. R02 I result/index/archive remain `5f6df653b7338a88ad010027f0f031eb824fb11a63e0955a353656cd177c2e69`, `16f031acecbf0b10b37cf9b38c2f2f3e4c0183449e6df00cec3a9cf10562d926`, and `c94bbb2662e5506b0ed7da9b61a140430487114635b8946ef9b218753d073c1a`. No historical flags or acceptance decisions were rewritten.

Passing focused C does not complete full R03. Legacy/resource regressions, broader method/generic/interface/delegate/stack-trace coverage, startup/capacity/performance/memory, PureInterpreter qualification/experiments and independent full-stage review remain Primary-owned. H2 follows the documented R03 exits and is not approved by this repair or host CI.
