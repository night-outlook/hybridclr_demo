# R03 E — Local batch D validation matrix

Status: ready for source-bound Local revalidation of R03-LC-001 after Primary's complete-source compile checks. This is not R03/H2 acceptance.

## Authority

Branch for all four repositories: `codex/assembly-shadow-r01b-h1`.
Demo tested source anchor: `5931ada3c70958a7c6132219e059a42ee3cecbd0`.
Execute the final docs-only transport SHA containing the live `Handoff/WEB_TO_LOCAL.md`, as supplied by Primary's final prompt and checked against local/remote HEAD.

Unchanged external source tuple:
- HybridCLR `041c0cbb42d3e64e54fe605673d99799b5d63893`
- package `120bb01be680cec0375002a0823552d66d34b84c`
- IL2CPP `1abb6bcaa85226f08c67f9da65edb3c58e8cb399`

Unity 2022.3.62f2, StandaloneOSX arm64. Direct managed SDK 8.0.318. The build-helper check uses the selected Unity installation's own NetCoreRuntime/dotnet and DotNetSdkRoslyn/csc.dll, not the direct managed SDK's compiler.

New root: `/Users/ah/GitHub/hybridclr/r03-local-validation/R03LocalBatch-20261001D-build-api`.
Preserve C and all previous roots. No retry, reuse, deletion, relaxation or Local source correction is authorized.

## Unchanged 36-cell ledger

The same `run_local.py` ledger and `player-cases.json` remain authoritative. No cell is removed or renamed:

| Group | Cells | Required scope |
| --- | ---: | --- |
| Entry authority, verifier contracts, reference sources | 3 | Four exact clean owning repositories/current remote heads; 67 Python contracts; detached pinned references |
| Reference/candidate graph and admission | 3 | 9 assertions in each graph suite; all 35 admission/method cases |
| Player fixtures and prerequisite subchecks | 1 | All original checks plus complete helper compilation described below |
| Four role prepare/build pairs | 8 | candidate-release, reference-release, candidate-debug, candidate-off |
| Actual EditMode | 1 | Real XML with all mandatory R03 IDs and target-cycle regression |
| Fresh-process Player cases | 19 | Exactly C01–C10, R01–R05, D01–D03 and O01 with unchanged runtime expectations |
| Final authority | 1 | Repeat source/branch/clean/remote checks |

Total: **36**. Any failed prerequisite blocks only its scheduled dependents; unrelated cells retain the runner's existing continuation behavior.

## Extended player-fixtures cell

The existing fifteen Player DLLs, 33 metadata audits, 33 pinned-Unity compiler consumers, exact invalid-public-key consumer, and valid/invalid Editor lifecycle probes remain mandatory. Their classifications and supervision rules are unchanged.

The added `build_api.validate_build_api` subcheck runs after those probes and before native-role preparation. It requires:

1. Exact UnityEditor.CoreModule SHA-256 `e22a829a8022d30c6b2b11fe764d12a2383cf882b63a954641e3cd41ea56af6e`, matching C's read-only API record.
2. Actual package asmdef-owned source compilation in dependency order: HybridCLR.Runtime, Unity.HybridCLR.AssemblyShadow.CodeGen, HybridCLR.Editor. No substituted API/package stubs.
3. The **complete current R03Build.cs** compiled with actual pinned Unity references/macOS defines, clean exit 0 and a real emitted DLL.
4. The **complete preserved C R03Build.cs** (blob `7b54381bc96b4be133ebed5f7b7173fcc0a57849`) compiled separately, with clean exit 1, exactly two CS0266 int-to-uint errors and no emitted DLL. Reading this snapshot is not rerunning C or modifying its evidence.
5. Source/asmdef/plugin/compiler/runtime/API input hashes unchanged before and after all five compiler invocations. `/noconfig` remains a direct command-line option; other arguments are in retained response files.

Only the named negative control may accept the specific nonzero exit as an expected-negative observation. It never changes a failed build into success. Unknown compiler errors, missing references, survivor/timeout/launch failures or missing output fail the subcheck. Compile-only success does not establish installer, ILPostProcessor, generation, native build, Editor assertions or Player behavior.

## Additional evidence

Preserve the original batch result/ledger/index/archive/seal, all cells, command streams, host/fixtures/consumers/lifecycle/build/Editor/Player evidence and excluded live-root inventories. Also retain:

- `build-api/inputs.json` and `build-api/results.json`;
- `build-api/*/compiler.rsp`;
- emitted package assemblies and complete `build-api/R03Build/R03Build.dll`;
- exact original-helper negative stdout/stderr and command receipt;
- all five additional outer schema-v2 `R03OwnedCommandV1` command receipts.

The `build-api` directory is inside the existing focused seal selection. No new exclusions or evidence schema relaxation are introduced. The original source lives in the immutable checkpoint, and its input hash is bound again; do not mutate or duplicate an altered version in C.

## Verdict and return

All 36 cells plus the focused seal must pass for `EvidenceReadyForPrimaryReview`; otherwise return `ReturnRequired`. Preserve all failing and Blocked/NotRun statuses, including the original inner exit codes of supervised Unity commands. A compilation artifact alone is not an Editor/native verdict.

Local updates only `Handoff/LOCAL_VALIDATION.md`, `Handoff/RETURN_TO_WEB.md`, and a new immutable `History/M07R/R03/local-validation-<date>-batch-d-<result>/` checkpoint; commit/push these demo evidence/docs and stop. Source/expectation/timeout/pin changes return to Primary.

`R03Accepted=false`, `H2Passed=false`, `pureInterpreterExpansionEnabled=false`, and `fullLegacyRegressionAcceptance=false` stay mandatory. Broader R03 regressions, measurement, gated PureInterpreter qualification and independent stage review remain Primary-owned and are not waived by D.
