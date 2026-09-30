# Current Status — R03 batch-A failure repaired; awaiting batch B

## Current authority and state

R02 remains accepted as **`PassedWithExplicitDeferredRisk`** under the separately committed owner decision. R03 is in progress; its conservative candidate remains implemented, but R03 and H2 are not accepted.

- `R02Accepted=true`; `mayEnterR03=true`; `R03Started=true`.
- Last Local return: **batch A, `ReturnRequired`**, committed at `2a9fdec813592fd79db511d5db96a6dcf1dea620`.
- Batch A completed its one authorized invocation: **4 Passed / 3 Failed / 29 Blocked**, focused seal Passed.
- `R03-LA-001`: **repaired in source and host-validated; Local revalidation required**.
- Next Local cycle: **batch B requested; NotRun**.
- `R03Accepted=false`; `H2Passed=false`.
- PureInterpreter structural expansion: **disabled**.

Read `Handoff/LOCAL_VALIDATION.md` and `Handoff/RETURN_TO_WEB.md` for the unchanged batch-A execution facts. Read `History/M07R/R03/C_LIFETIME_REPAIR.md`, `C_HOST_EVIDENCE.json`, `C_VALIDATION_MATRIX.md`, and the live `Handoff/WEB_TO_LOCAL.md` for the repair and new execution authority. Earlier A/B handoff records are historical and do not authorize retrying A.

## Preserved batch-A result

Executed demo: `25a7c5ada06c97574bf218e74cf38c811445d13c`.
Local publication: `2a9fdec813592fd79db511d5db96a6dcf1dea620`.
Checkpoint: `History/M07R/R03/local-validation-20260930-batch-a-return-required/`.

Three managed builds exited 0 but left surviving process groups. The runner rejected each before its host assertion program ran. Fixture generation, four Unity builds, EditMode tests and nineteen Player cases remain **Blocked/NotRun**. The exact survivor executable was not captured; the proposed compiler/build-server explanation is not a directly observed child identity.

Local authenticated 58 indexed files and 59 archive members. The seal proves custody of the failed run, not runtime acceptance. Preserve the live A root and its excluded compiled outputs/intermediates/reference worktrees unchanged.

- A result SHA-256: `a03a2b2cc2f493ca92f782eed0a2b03d040c45a826333581818c96200c4a9173`.
- A index SHA-256: `a14717414c030ac734fc2e9543118b507df4465b55cbbeb4a9af0bf5a0756181`.
- A archive SHA-256: `13cf7407447d7952aae6429bbf8e5aae3fc11a030ae139651a09142324450c6c`.

## New source tuple

Branch in all four repositories: `codex/assembly-shadow-r01b-h1`.

| Repository | Exact source authority |
| --- | --- |
| night-outlook/hybridclr_demo | Tested executable/CI anchor `7e2852fcd6c5bd9ebc82f2b3f97516742b772dc2`; execute the final documentation-only transport HEAD identified by the current handoff and Primary prompt. |
| night-outlook/hybridclr | `041c0cbb42d3e64e54fe605673d99799b5d63893` — unchanged |
| night-outlook/hybridclr_unity | `120bb01be680cec0375002a0823552d66d34b84c` — unchanged |
| night-outlook/il2cpp_plus | `1abb6bcaa85226f08c67f9da65edb3c58e8cb399` — unchanged |

Repair implementation commit: `94f2612a6c64c341ac38efcaf01952cb594f47d8`. Final source anchor `7e2852...` adds complete hidden compiler-file retention in host CI artifacts. Only documentation/evidence may differ after that new anchor. The previous `f5f571...` host anchor remains historical, not the source authority for batch B.

The live handoff resolves the demo transport as the latest commit touching `WEB_TO_LOCAL.md`, and requires it to match local HEAD, current remote HEAD and Primary's exact prompt. The runner independently verifies all four owning repository identities before and after execution.

## Primary repair and completed host checks

Managed builds now explicitly disable build servers/shared compilation/node reuse per invocation, using a child-scoped environment. The common command wrapper retains fail-closed survivor rejection and adds bounded pre-cleanup PID/PGID diagnostics. It never globally shuts down unrelated workers or converts successful cleanup into a passed command. New command receipts use schema version 2, `R03OwnedCommandV1`.

Final workflow **36739214352** executed anchor `7e2852fcd6c5bd9ebc82f2b3f97516742b772dc2` successfully on **Linux x86_64 and macOS 15.7.9 arm64**, both with .NET SDK **8.0.318**. Each platform passed 43 Python contracts, both 9-case graph suites, 35 admission/method assertions, exact 15-DLL generation, five managed builds including the actual Runtime API compile, and twelve owned command completions with no surviving process group. Primary downloaded and authenticated both final ZIPs: **308 indexed files / 309 archive files per platform**. See `C_HOST_EVIDENCE.json` for job/artifact IDs, hashes and individual command bindings.

This evidence exercises the production `Batch.command`/`Batch.managed` path, not only direct dotnet shell builds. It is not execution of Local batch B, Local's macOS 26.5 environment, Unity Editor, or IL2CPP Player. The first source-94f host archive had a hidden-file membership defect; it is explicitly recorded as incomplete and superseded by the authenticated final source-7e artifacts.

## Next action and stop

Follow `Handoff/WEB_TO_LOCAL.md` to run exactly one new batch at:

`/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20260930B-lifetime`

Use the existing verified SDK 8.0.318 and Unity 2022.3.62f2 paths recorded there. The batch root must be unused. Do not retry A, reuse an existing root, relax flags/timeouts/expectations or perform non-trivial implementation locally.

The batch retains **36 cells / four isolated Unity builds / nineteen fresh-process Player cases**. The existing verifier cell now runs 43 tests. All cells and the focused seal must pass for `EvidenceReadyForPrimaryReview`; otherwise return `ReturnRequired` with the original failure classifications. Local commits/pushes its factual reports and immutable B checkpoint, then stops for Primary reconciliation.

## Preserved risks and remaining R03 work

R02-D1 CPU residuals and the original H1 +18–19 MiB RSS risk remain deferred through H2. R02 I result/index/archive remain `5f6df653b7338a88ad010027f0f031eb824fb11a63e0955a353656cd177c2e69`, `16f031acecbf0b10b37cf9b38c2f2f3e4c0183449e6df00cec3a9cf10562d926`, and `c94bbb2662e5506b0ed7da9b61a140430487114635b8946ef9b218753d073c1a`. No historical acceptance or execution-time flags have been rewritten.

A successful focused B batch does not complete full R03. Legacy/resource regressions, broader method/generic/delegate/interface/stack-trace coverage, startup/capacity/performance/memory, gated PureInterpreter qualification/experiments and independent full stage review remain Primary-owned. H2 follows completion of the documented R03 exit conditions; it is not authorized by this repair or host evidence.
