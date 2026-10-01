# Current Status — R03 count/API blocker repaired; awaiting Local batch D

## State and authority

R02 remains accepted as `PassedWithExplicitDeferredRisk`. R03 is in progress; neither R03 nor H2 is accepted. PureInterpreter structural expansion remains disabled.

- R02Accepted=true; mayEnterR03=true; R03Started=true.
- Latest Local return: **C, ReturnRequired**, published at `ed9afef29d17c64f15b281ea8b2176cb17d637b3`.
- C recorded **12 Passed / 5 Failed / 19 Blocked**, focused seal Passed, one invocation only.
- R03-LB-001/002: verified in C's focused compiler/Editor lifecycle scope, not full native/runtime acceptance.
- R03-LC-001: corrected in source and complete-helper compiler validation; integrated Local revalidation required.
- Next Local cycle: **D requested; NotRun**.
- R03Accepted=false; H2Passed=false; pureInterpreterExpansionEnabled=false.

Read the unchanged Local-owned reports and C checkpoint for execution facts. Read `History/M07R/R03/E_BUILD_API_REPAIR.md`, `E_HOST_EVIDENCE.json`, `E_VALIDATION_MATRIX.md`, and `Handoff/WEB_TO_LOCAL.md` for this repair and new execution authority. Earlier preparation records do not authorize retrying A/B/C.

## Preserved C facts

Executed demo `fdefb4f7133812f3b0593ae2257057c1bc57195e`; Local publication `ed9afef29d17c64f15b281ea8b2176cb17d637b3`.
Checkpoint: `History/M07R/R03/local-validation-20261001-batch-c-return-required/`.

Fixture/audit/consumer and actual valid/invalid Editor probes passed. All 55 command groups completed cleanly under the recorded lifetime policies. Four build attempts and EditMode failed C# compilation before their entrypoints, because receipt fields were uint and pinned Unity's BuildSummary getters return int. Native builds, Editor assertions and nineteen Players remain NotRun for C.

Local authenticated 677 indexed files and 678 archive members. Primary has not accessed the live macOS root or rewritten that custody evidence. Result/index/archive SHA-256 values remain:
- `f1dae2e7925f155dcb3eb4d6eff51705846c68366560e89506d6cbde631f5c6d`
- `477ad959a85db392a11fb0569fa313ee67ee4ad3e835a31821d37ebe2b790dec`
- `65537c0270229671214ae6c36633533d5f864484c00a2f6aa745e65399c20fe3`

A/B facts and uncertainty about B's original survivor identity remain historical. C's scoped successes do not retrospectively alter them.

## New source tuple

Branch for every repository: `codex/assembly-shadow-r01b-h1`.

| Repository | Source authority |
| --- | --- |
| night-outlook/hybridclr_demo | Tested source anchor `5931ada3c70958a7c6132219e059a42ee3cecbd0`; execute its final docs-only transport from the live handoff and exact Primary prompt |
| night-outlook/hybridclr | `041c0cbb42d3e64e54fe605673d99799b5d63893` — unchanged |
| night-outlook/hybridclr_unity | `120bb01be680cec0375002a0823552d66d34b84c` — unchanged |
| night-outlook/il2cpp_plus | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` — unchanged |

Implementation commit `24a5a25972afc2a91afb26e68f97984c6dd8af2b` changes only two helper field types plus compilation tooling/tests. `5931ada...` places Roslyn's /noconfig on the command line instead of inside the response file. No product guard, numeric JSON field/schema, native/package pin, fixture, Player expectation, deadline, lifetime rule or top-level ledger changed.

The final demo transport is the latest commit touching WEB_TO_LOCAL.md and must equal local HEAD, current remote HEAD, and Primary's exact prompt. Only Docs/AssemblyShadow evidence/documentation may differ after the tested anchor. The script repeats all four authorities before and after execution.

## Completed Primary validation

The new compile-only workflow uses the exact official Unity 2022.3.62f2 ARM64 package, extracted without installing/launching Unity. It compiles the full real HybridCLR.Runtime, CodeGen and Editor dependencies, then the complete repaired R03Build.cs, using Unity's actual compiler and DLLs. The decisive CoreModule bytes match C's exact SHA. The preserved complete C helper separately fails with exactly its two CS0266 errors and no DLL.

The same source's Linux/macOS host regressions pass 67 Python contracts, both 9-case graph suites, 35 admission cases, fifteen fixtures, 33 metadata audits/consumers, Runtime API compile and shared-compiler supervision. See E_HOST_EVIDENCE.json for exact workflow/job/artifact identities, diagnostics, output hashes and authenticated archive memberships. All reported compiler evidence has retained command receipts and stream hashes; package warnings are not hidden.

This is complete-source compiler coverage, not execution of Unity's import/ILPostProcessor/generation/IL2CPP pipeline. No new integrated Local batch or native Player is claimed by Primary.

## Next action

Run once under the exact live handoff in the unused root:

`/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001D-build-api`

The original **36 cells / four native build roles / nineteen Player cases** remain required. The existing verifier cell runs 67 tests; player-fixtures additionally performs the same full-helper/package compile and strict old-source negative control before native-role preparation. All cells plus the focused seal must pass for EvidenceReadyForPrimaryReview. Otherwise preserve ReturnRequired with exact failed/blocked evidence. Local writes its reports/new immutable D checkpoint, commits/pushes, and stops for Primary.

## Risks and remaining stage work

Installer/generation/IL2CPP/native/runtime behavior remains unvalidated for this candidate. Later failures may surface once compilation proceeds. Full R03 legacy/resource regressions, broader generic/delegate/interface/stack-trace coverage, startup/capacity/performance/memory, gated PureInterpreter qualification/experiments and independent full stage review remain Primary-owned.

R02-D1 CPU residuals and the original H1 +18–19 MiB RSS risk remain visible through H2. Historical R02 I result/index/archive are unchanged (`5f6df653b7338a88ad010027f0f031eb824fb11a63e0955a353656cd177c2e69`, `16f031acecbf0b10b37cf9b38c2f2f3e4c0183449e6df00cec3a9cf10562d926`, `c94bbb2662e5506b0ed7da9b61a140430487114635b8946ef9b218753d073c1a`). No prior execution-time flags or acceptance records are rewritten. D cannot approve R03, H2 or release.
